"""Scriptorium: a local browser for bible.duckdb.

    python scriptorium.py            # http://127.0.0.1:8770  (opens your browser)
    python scriptorium.py --port 9000 --no-browser

Read-only: the database is opened read-only and external file/network access is switched off,
so the SQL console can query every table but cannot change the database or touch other files.
The Reference Rainbow is served alongside at /rainbow/.
"""
import argparse, collections, json, mimetypes, os, re, subprocess, sys, threading, time, webbrowser
from datetime import date, datetime
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import duckdb

HERE = Path(__file__).resolve().parent
DB = HERE / "bible.duckdb"
WEB = HERE / "web"
RAINBOW = HERE.parent / "rainbow"
ROOT = HERE.parent
SHAREABLE = HERE / "bible-shareable.duckdb"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").exists() else ""
MAX_ROWS = 2000
URL = ""

con = None
GEN = 0                      # bumps whenever the database is (re)opened, so threads fetch fresh cursors
_local = threading.local()
_swap_lock = threading.Lock()


def cur():
    if getattr(_local, "gen", -1) != GEN:
        _local.c = con.cursor()
        _local.gen = GEN
    return _local.c


def open_db():
    global con, GEN
    c = duckdb.connect(str(DB), read_only=True)
    c.execute("SET GLOBAL enable_external_access = false")
    c.execute("SET GLOBAL lock_configuration = true")
    con = c
    GEN += 1
    books = []
    for b in rows("SELECT book_id, osis, name, testament, chapters FROM books WHERE book_id <= 66 ORDER BY book_id"):
        b["key"] = re.sub(r"[^a-z0-9]", "", b["name"].lower())
        books.append(b)
    BOOKS[:] = books


def rows(sql, params=()):
    c = cur().execute(sql, params)
    cols = [d[0] for d in c.description]
    return [dict(zip(cols, r)) for r in c.fetchall()]


def jsonable(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()
    if isinstance(o, Decimal):
        return float(o)
    if isinstance(o, (bytes, bytearray)):
        return o.hex()
    return str(o)


# ------------------------------------------------------------------ reference parsing
BOOKS = []
ALIASES = {"psalm": "Ps", "psa": "Ps", "pss": "Ps", "jn": "John", "mt": "Matt", "mk": "Mark", "lk": "Luke", "sos": "Song", "songofsongs": "Song",
           "canticles": "Song", "phm": "Phlm", "jas": "Jas", "rv": "Rev", "revelations": "Rev", "ezk": "Ezek", "jdg": "Judg",
           # STEPBible abbreviations used in lexicon cross-links
           "mrk": "Mark", "jhn": "John", "php": "Phil", "1jn": "1John", "2jn": "2John", "3jn": "3John", "jol": "Joel", "nam": "Nah", "sng": "Song"}


def find_book(q):
    key = re.sub(r"[^a-z0-9]", "", q.lower())
    if not key:
        return None
    if key in ALIASES:
        key = ALIASES[key].lower()
    for b in BOOKS:
        if b["key"] == key or b["osis"].lower() == key:
            return b
    for b in BOOKS:
        if b["key"].startswith(key) or b["osis"].lower().startswith(key):
            return b
    return None


def parse_ref(q):
    """'John 3', 'Jn 3:16', 'Gen.1.1', 'Ps 23:1-4' -> (book, chapter, v_from, v_to)."""
    q = q.strip().replace(".", " ")
    m = re.match(r"^((?:[1-3]\s*)?[A-Za-z][A-Za-z ]*?)\s*(\d+)?(?:\s*[: ]\s*(\d+)(?:\s*[-–]\s*(\d+))?)?\s*$", q)
    if not m:
        return None
    b = find_book(m.group(1))
    if not b:
        return None
    ch = min(max(int(m.group(2) or 1), 1), b["chapters"])
    vf = int(m.group(3)) if m.group(3) else None
    vt = int(m.group(4)) if m.group(4) else vf
    return b, ch, vf, vt


# ------------------------------------------------------------------ API
def api_meta(_):
    return dict(
        books=BOOKS,
        translations=rows("SELECT translation_id, title, language, language_code, category, has_ot, has_nt, has_deuterocanon, has_strongs FROM translations ORDER BY category DESC, language, translation_id"),
        counts=rows("""SELECT (SELECT count(*) FROM translations) translations, (SELECT count(DISTINCT language) FROM translations) languages,
                       (SELECT count(*) FROM verse_text) verse_rows, (SELECT count(*) FROM original_words) original_words,
                       (SELECT count(*) FROM strongs) strongs, (SELECT count(*) FROM cross_references) cross_references,
                       (SELECT count(*) FROM translation_words) tagged_words, (SELECT count(*) FROM phrase_repeats) repeated_phrases,
                       (SELECT count(*) FILTER (words_of_jesus) FROM verses) jesus_verses, (SELECT count(*) FILTER (words_of_god_detected) FROM verses) god_verses""")[0],
    )


def api_passage(qs):
    ref = parse_ref(qs.get("ref", ["John 1"])[0])
    if not ref:
        return dict(error="No book matches that reference. Try John 3, Ps 23:1-6 or Gen.1.1.")
    b, ch, vf, vt = ref
    trs = [t for t in qs.get("tr", ["KJV,BSB,ORIG"])[0].split(",") if t][:12]
    orig = "TAHOT" if b["book_id"] <= 39 else "TAGNT"
    trs = [orig if t == "ORIG" else t for t in trs]
    known = {r["translation_id"] for r in rows("SELECT translation_id FROM translations")}
    trs = [t for t in dict.fromkeys(trs) if t in known]
    params = [b["book_id"], ch]
    vfilter = ""
    if vf:
        vfilter = " AND verse BETWEEN ? AND ?"
        params += [vf, vt or vf]
    verses = rows(f"SELECT verse_id, chapter, verse, words_of_jesus, words_of_god_detected, god_detection_method FROM verses WHERE book_id = ? AND chapter = ?{vfilter} ORDER BY verse", params)
    texts, red = {}, {}
    if trs:
        ph = ",".join("?" * len(trs))
        for r in rows(f"SELECT translation_id, verse, text FROM verse_text WHERE book_id = ? AND chapter = ?{vfilter} AND translation_id IN ({ph})", params + trs):
            texts.setdefault(r["verse"], {})[r["translation_id"]] = r["text"]
        for r in rows(f"SELECT translation_id, verse, start_char, end_char, speaker, method FROM speech_spans WHERE book_id = ? AND chapter = ?{vfilter} AND translation_id IN ({ph}) ORDER BY start_char", params + trs):
            red.setdefault(r["verse"], {}).setdefault(r["translation_id"], []).append([r["start_char"], r["end_char"], r["speaker"], r["method"]])
    words = {}
    if qs.get("interlinear", ["0"])[0] == "1":
        for w in rows(f"""SELECT verse, word_pos, language, text, transliteration, english, strongs, morphology, gloss
                         FROM original_words WHERE source = ? AND book_id = ? AND chapter = ?{vfilter}
                         AND (source = 'TAHOT' AND word_type <> 'K' OR source = 'TAGNT' AND word_type LIKE 'N%') ORDER BY verse, word_pos""", [orig] + params):
            words.setdefault(w["verse"], []).append(w)
    meta = {r["translation_id"]: r for r in rows(f"SELECT translation_id, title, language, language_code, category FROM translations WHERE translation_id IN ({','.join('?' * len(trs))})", trs)} if trs else {}
    idx = next(i for i, x in enumerate(BOOKS) if x["book_id"] == b["book_id"])
    prev = (b, ch - 1) if ch > 1 else ((BOOKS[idx - 1], BOOKS[idx - 1]["chapters"]) if idx > 0 else None)
    nxt = (b, ch + 1) if ch < b["chapters"] else ((BOOKS[idx + 1], 1) if idx + 1 < len(BOOKS) else None)
    return dict(book=b, chapter=ch, verse_from=vf, verse_to=vt, translations=[meta[t] for t in trs if t in meta], original=orig,
                verses=[dict(v, texts=texts.get(v["verse"], {}), red=red.get(v["verse"], {}), words=words.get(v["verse"], [])) for v in verses],
                prev=f"{prev[0]['name']} {prev[1]}" if prev else None, next=f"{nxt[0]['name']} {nxt[1]}" if nxt else None)


def api_strongs_search(qs):
    q = qs.get("q", [""])[0].strip()
    if not q:
        return dict(results=rows("SELECT strongs_id, language, lemma, transliteration, left(definition, 90) AS definition FROM strongs WHERE strongs_id IN ('H0430','H3068','H7225','H1254','G0026','G3056','G5485','G4102','H2617','H7965') ORDER BY strongs_id"))
    m = re.match(r"^([HGhg])\s*0*(\d{1,4})[A-Za-z]?$", q)
    if m:
        sid = f"{m.group(1).upper()}{int(m.group(2)):04d}"
        return dict(results=rows("SELECT strongs_id, language, lemma, transliteration, left(definition, 90) AS definition FROM strongs WHERE strongs_id = ?", [sid]))
    like = f"%{q}%"
    return dict(results=rows("""SELECT strongs_id, language, lemma, transliteration, left(definition, 90) AS definition FROM strongs
        WHERE lemma = ? OR strip_accents(transliteration) ILIKE strip_accents(?) OR kjv_usage ILIKE ? OR definition ILIKE ?
        ORDER BY (lemma = ?) DESC, (kjv_usage ILIKE ?) DESC, strongs_id LIMIT 60""", [q, like, like, like, q, like]))


def api_strongs(sid):
    m = re.match(r"^([HG])0*(\d{1,4})$", sid.upper())
    if not m:
        return dict(error="Strong's numbers look like H430 or G26.")
    sid = f"{m.group(1)}{int(m.group(2)):04d}"
    entry = rows("SELECT * FROM strongs WHERE strongs_id = ?", [sid])
    if not entry:
        return dict(error=f"{sid} is not in Strong's dictionary.")
    return dict(
        entry=entry[0],
        senses=rows("SELECT extended_id, relation, lemma, transliteration, language, part_of_speech, gloss, definition_html FROM lexicon_extended WHERE strongs_id = ? ORDER BY extended_id", [sid]),
        counts=rows("""SELECT (SELECT count(*) FROM original_words WHERE strongs = ?) AS occurrences,
                              (SELECT count(DISTINCT verse_id) FROM verse_strongs WHERE strongs = ?) AS verses,
                              (SELECT count(DISTINCT book_id) FROM original_words WHERE strongs = ?) AS books""", [sid, sid, sid])[0],
        forms=rows("SELECT text, transliteration, count(*) n FROM original_words WHERE strongs = ? GROUP BY ALL ORDER BY n DESC LIMIT 12", [sid]),
        renderings=rows("""SELECT translation_id, rendering, n FROM (
                               SELECT translation_id, lower(trim(word)) AS rendering, count(*) AS n FROM translation_words
                               WHERE strongs = ? AND word IS NOT NULL GROUP BY translation_id, lower(trim(word)))
                           QUALIFY row_number() OVER (PARTITION BY translation_id ORDER BY n DESC) <= 12
                           ORDER BY translation_id, n DESC""", [sid]),
        by_book=rows("""SELECT b.book_id, b.name, count(*) n FROM original_words w JOIN books b USING (book_id) WHERE w.strongs = ? GROUP BY ALL ORDER BY b.book_id""", [sid]),
        verses=rows("""SELECT v.reference, v.osis_ref, vt.text AS kjv,
                              (SELECT string_agg(DISTINCT tw.word, ', ') FROM translation_words tw WHERE tw.verse_id = v.verse_id AND tw.translation_id = 'KJV' AND tw.strongs = ?) AS kjv_words
                       FROM verse_strongs s JOIN verses v USING (verse_id) LEFT JOIN verse_text vt ON vt.verse_id = v.verse_id AND vt.translation_id = 'KJV'
                       WHERE s.strongs = ? ORDER BY v.verse_id LIMIT 80""", [sid, sid]),
    )


def api_books(_):
    books = rows("""SELECT b.book_id, b.osis, b.name, b.testament, b.genre, b.original_language, b.chapters, b.verses,
                           d.consensus, d.consensus_note, d.traditional_year, d.critical_year
                    FROM books b JOIN book_dating d USING (book_id) ORDER BY b.book_id""")
    views = rows("""SELECT a.*, p.name AS place_name, p.latitude, p.longitude, p.precision FROM book_authorship a LEFT JOIN places p USING (place_id) ORDER BY authorship_id""")
    cites = rows("""SELECT x.authorship_id, x.locator, s.* FROM book_authorship_sources x JOIN scholarly_sources s USING (source_id)""")
    by_view = {}
    for c in cites:
        by_view.setdefault(c["authorship_id"], []).append(c)
    by_book = {}
    for v in views:
        v["sources"] = by_view.get(v["authorship_id"], [])
        by_book.setdefault(v["book_id"], []).append(v)
    for b in books:
        b["views"] = by_book.get(b["book_id"], [])
    return dict(books=books)


def api_translations(qs):
    if qs.get("catalog", [""])[0] == "ebible":
        return dict(rows=rows("SELECT * FROM ebible_catalog ORDER BY imported DESC, language, title"))
    return dict(rows=rows("SELECT * FROM translations ORDER BY category DESC, language, translation_id"))


def api_tables(_):
    t = rows("""SELECT table_name AS name, 'table' AS kind, estimated_size AS rows, comment FROM duckdb_tables() WHERE schema_name = 'main'
                UNION ALL SELECT view_name, 'view', NULL, comment FROM duckdb_views() WHERE schema_name = 'main' AND NOT internal
                ORDER BY kind, name""")
    cols = rows("SELECT table_name, column_name, data_type, comment, column_index FROM duckdb_columns() WHERE schema_name = 'main' ORDER BY table_name, column_index")
    by = {}
    for c in cols:
        by.setdefault(c["table_name"], []).append(dict(name=c["column_name"], type=c["data_type"], comment=c["comment"]))
    for x in t:
        x["columns"] = by.get(x["name"], [])
    return dict(tables=t)


def api_table(name, qs):
    names = {r["name"]: r for r in api_tables(None)["tables"]}
    if name not in names:
        return dict(error=f"No table or view named {name}.")
    colnames = [c["name"] for c in names[name]["columns"]]
    limit = min(max(int(qs.get("limit", ["50"])[0]), 1), 500)
    offset = max(int(qs.get("offset", ["0"])[0]), 0)
    where, params = "", []
    col, op, val = qs.get("col", [""])[0], qs.get("op", ["contains"])[0], qs.get("val", [""])[0]
    if col in colnames and val != "":
        if op == "equals":
            where, params = f' WHERE CAST("{col}" AS VARCHAR) = ?', [val]
        elif op == "starts":
            where, params = f' WHERE CAST("{col}" AS VARCHAR) ILIKE ?', [val + "%"]
        else:
            where, params = f' WHERE CAST("{col}" AS VARCHAR) ILIKE ?', [f"%{val}%"]
    order = ""
    ocol = qs.get("order", [""])[0]
    if ocol in colnames:
        order = f' ORDER BY "{ocol}" {"DESC" if qs.get("dir", ["asc"])[0] == "desc" else "ASC"} NULLS LAST'
    t0 = time.time()
    total = cur().execute(f'SELECT count(*) FROM "{name}"{where}', params).fetchone()[0]
    c = cur().execute(f'SELECT * FROM "{name}"{where}{order} LIMIT {limit} OFFSET {offset}', params)
    return dict(columns=[d[0] for d in c.description], rows=c.fetchall(), total=total, limit=limit, offset=offset, ms=round((time.time() - t0) * 1000))


def api_sql(body):
    sql = (body.get("sql") or "").strip()
    if not sql:
        return dict(error="Write a query first, e.g. SELECT * FROM books LIMIT 10.")
    t0 = time.time()
    try:
        c = cur().execute(sql)
        if c.description is None:
            return dict(columns=[], rows=[], ms=round((time.time() - t0) * 1000), truncated=False)
        data = c.fetchmany(MAX_ROWS + 1)
        return dict(columns=[d[0] for d in c.description], rows=data[:MAX_ROWS], truncated=len(data) > MAX_ROWS, ms=round((time.time() - t0) * 1000))
    except duckdb.Error as e:
        return dict(error=str(e))


# ------------------------------------------------------------------ setup: status and background jobs
RESTRICTED = ("Non-commercial only", "No derivatives", "Copyrighted, free distribution", "Not stated")
PAGE_FILES = [("Rainbow", "rainbow/data.js"), ("Echoes", "rainbow/echoes-data.js"), ("Translations", "rainbow/texts/manifest.js"), ("Word study", "rainbow/study/concordance.js")]
PAGE_STEPS = [["Refreshing the Rainbow's data", "rainbow/build_data.py"], ["Refreshing Echoes", "rainbow/build_echoes.py"],
              ["Refreshing the translations", "rainbow/build_texts.py"], ["Refreshing the reader's word study", "rainbow/build_study.py"]]
BUILD_NEW = ["Building the database (about 2 minutes)", "bibledb/build.py", "--output", "bibledb/bible.new.duckdb"]
SWAP = ["Switching to the new database", "@swap"]
JOBS = {
    "pages": dict(title="Refresh the pages' data", steps=PAGE_STEPS),
    "rebuild": dict(title="Rebuild the database", steps=[BUILD_NEW, SWAP, *PAGE_STEPS]),
    "update": dict(title="Get the latest data and rebuild", steps=[["Downloading (anything missing, plus the latest cross-references)", "bibledb/download.py", "--refresh"], BUILD_NEW, SWAP, *PAGE_STEPS]),
    "shareable": dict(title="Make a shareable copy", steps=[["Building bible-shareable.duckdb without the restricted texts", "bibledb/build.py", "--open-only", "--output", "bibledb/bible-shareable.duckdb"]]),
}
JOB = dict(name="", title="", running=False, ok=None, started=None, finished=None, step="", log=collections.deque(maxlen=800))


def job_state(with_log=True):
    d = {k: v for k, v in JOB.items() if k != "log"}
    if with_log:
        d["log"] = list(JOB["log"])
    return d


def file_info(p):
    p = Path(p)
    if not p.exists():
        return dict(path=str(p), exists=False)
    st = p.stat()
    return dict(path=str(p), exists=True, size=st.st_size, modified=datetime.fromtimestamp(st.st_mtime).isoformat(timespec="minutes"))


def swap_database(new_file):
    global con
    with _swap_lock:
        old, con = con, None
        old.close()
        os.replace(new_file, DB)
        wal = Path(str(DB) + ".wal")
        if wal.exists():
            wal.unlink()
        open_db()


def run_job(name):
    spec = JOBS[name]
    JOB["log"].clear()
    JOB.update(name=name, title=spec["title"], running=True, ok=None, started=datetime.now().isoformat(timespec="seconds"), finished=None, step="Starting")
    ok = True
    try:
        for title, *cmd in spec["steps"]:
            JOB["step"] = title
            JOB["log"].append(f"── {title}")
            if cmd == ["@swap"]:
                swap_database(HERE / "bible.new.duckdb")
                JOB["log"].append("Now using the new database.")
                continue
            env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
            proc = subprocess.Popen([sys.executable, "-u", *cmd], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, encoding="utf-8", errors="replace", env=env)
            for line in proc.stdout:
                JOB["log"].append(line.rstrip())
            if proc.wait() != 0:
                JOB["log"].append(f"This step failed (exit code {proc.returncode}).")
                ok = False
                break
    except Exception as e:  # noqa: BLE001 - report anything to the page
        JOB["log"].append(f"Stopped: {e}")
        ok = False
        if con is None:
            try:
                open_db()
            except Exception:  # noqa: BLE001
                pass
    JOB.update(running=False, ok=ok, finished=datetime.now().isoformat(timespec="seconds"), step="Finished" if ok else JOB["step"])


def api_setup(_):
    restricted = rows(f"SELECT translation_id, title, license FROM translations WHERE license_class IN ({','.join('?' * len(RESTRICTED))}) ORDER BY translation_id", RESTRICTED)
    return dict(
        root=str(ROOT), url=URL, version=VERSION, python=sys.version.split()[0],
        launchers=["Start Scriptorium (Windows).bat", "Start Scriptorium (Mac).command"],
        db=file_info(DB), shareable=file_info(SHAREABLE),
        pages=[dict(name=n, **file_info(ROOT / p)) for n, p in PAGE_FILES],
        counts=api_meta(None)["counts"], restricted=restricted,
        classes=rows("SELECT license_class, count(*) AS texts FROM translations GROUP BY 1 ORDER BY texts DESC"),
        sources=rows("SELECT dataset, provider, license, used_for, url FROM data_sources"),
        job=job_state(),
    )


# ------------------------------------------------------------------ HTTP
class Handler(BaseHTTPRequestHandler):
    server_version = "Scriptorium/1.0"

    def log_message(self, fmt, *args):
        pass

    def send_json(self, obj, status=200, cors=False):
        data = json.dumps(obj, default=jsonable, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        if cors:  # only the harmless status check may be read by pages opened from disk
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Private-Network", "true")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        if urlparse(self.path).path != "/api/ping":
            return self.send_error(404)
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.end_headers()

    def send_file(self, path: Path):
        if not path.is_file():
            self.send_error(404)
            return
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript", "application/json"):
            ctype += "; charset=utf-8"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        qs = parse_qs(u.query)
        p = unquote(u.path)
        try:
            if p == "/api/ping":
                return self.send_json(dict(ok=True, app="Scriptorium", version=VERSION, url=URL), cors=True)
            if p == "/api/jobs":
                return self.send_json(job_state())
            if con is None:
                return self.send_json(dict(error="Scriptorium is switching to the new database. Try again in a moment."), 503)
            if p == "/api/setup":
                return self.send_json(api_setup(qs))
            if p == "/api/meta":
                return self.send_json(api_meta(qs))
            if p == "/api/passage":
                return self.send_json(api_passage(qs))
            if p == "/api/strongs":
                return self.send_json(api_strongs_search(qs))
            if p.startswith("/api/strongs/"):
                return self.send_json(api_strongs(p.rsplit("/", 1)[1]))
            if p == "/api/books":
                return self.send_json(api_books(qs))
            if p == "/api/translations":
                return self.send_json(api_translations(qs))
            if p == "/api/tables":
                return self.send_json(api_tables(qs))
            if p.startswith("/api/table/"):
                return self.send_json(api_table(p.rsplit("/", 1)[1], qs))
        except (duckdb.Error, ValueError) as e:
            return self.send_json(dict(error=str(e)), 400)
        if p == "/rainbow":
            self.send_response(301)
            self.send_header("Location", "/rainbow/")
            self.end_headers()
            return
        if p.startswith("/rainbow/"):
            rel = p[len("/rainbow/"):] or "index.html"
            target = (RAINBOW / rel).resolve()
            return self.send_file(target) if RAINBOW.resolve() in target.parents or target == RAINBOW.resolve() else self.send_error(404)
        rel = p.lstrip("/") or "index.html"
        target = (WEB / rel).resolve()
        if WEB.resolve() not in target.parents:
            return self.send_error(404)
        return self.send_file(target)

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ("/api/sql", "/api/jobs"):
            return self.send_error(404)
        n = int(self.headers.get("Content-Length", "0"))
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            return self.send_json(dict(error="Request body must be JSON."), 400)
        if path == "/api/jobs":
            # the custom header keeps other websites from starting jobs (it forces a CORS preflight we never allow)
            if self.headers.get("X-Scriptorium") != "1":
                return self.send_json(dict(error="Jobs can only be started from Scriptorium's own page."), 403)
            name = body.get("job")
            if name not in JOBS:
                return self.send_json(dict(error="Unknown job."), 400)
            if JOB["running"]:
                return self.send_json(dict(error=f"“{JOB['title']}” is still running. Wait for it to finish."), 409)
            JOB["running"] = True
            threading.Thread(target=run_job, args=(name,), daemon=True).start()
            return self.send_json(dict(ok=True))
        if con is None:
            return self.send_json(dict(error="Scriptorium is switching to the new database. Try again in a moment."), 503)
        return self.send_json(api_sql(body))


def main():
    global URL
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8770)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()
    if not DB.exists():
        raise SystemExit(f"{DB} not found. Double-click 'Start Scriptorium' in the project folder, or run: python bibledb/download.py && python bibledb/build.py")
    open_db()
    url = URL = f"http://127.0.0.1:{args.port}/"
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Scriptorium is running at {url}\n  Keep this window open while you use it; close it (or press Ctrl+C) to stop.\n  Reference Rainbow: {url}rainbow/   Read: {url}rainbow/read.html")
    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

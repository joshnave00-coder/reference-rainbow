"""Build bible.duckdb from the raw sources fetched by download.py.

    python download.py     # once; ~350 MB of source files into raw/
    python build.py        # writes bible.duckdb (rebuilds from scratch)

Every table and column is documented with COMMENT ON, which the Scriptorium browser (scriptorium.py)
shows next to the data.
"""
import csv, json, re, sys, time
from datetime import date
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import book_origins as BO  # noqa: E402
import phrases  # noqa: E402
import red_letter  # noqa: E402
from english_texts import EBIBLE_ENGLISH  # noqa: E402

RAW = HERE / "raw"
STAGE = RAW / "_staging"
DB = HERE / "bible.duckdb"
T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:6.1f}s] {msg}", flush=True)


# --------------------------------------------------------------------------- canon
# osis, name, scrollmapper name, USFM code, genre
CANON = [
    ("Gen", "Genesis", "Genesis", "GEN", "Law"), ("Exod", "Exodus", "Exodus", "EXO", "Law"),
    ("Lev", "Leviticus", "Leviticus", "LEV", "Law"), ("Num", "Numbers", "Numbers", "NUM", "Law"),
    ("Deut", "Deuteronomy", "Deuteronomy", "DEU", "Law"), ("Josh", "Joshua", "Joshua", "JOS", "History"),
    ("Judg", "Judges", "Judges", "JDG", "History"), ("Ruth", "Ruth", "Ruth", "RUT", "History"),
    ("1Sam", "1 Samuel", "I Samuel", "1SA", "History"), ("2Sam", "2 Samuel", "II Samuel", "2SA", "History"),
    ("1Kgs", "1 Kings", "I Kings", "1KI", "History"), ("2Kgs", "2 Kings", "II Kings", "2KI", "History"),
    ("1Chr", "1 Chronicles", "I Chronicles", "1CH", "History"), ("2Chr", "2 Chronicles", "II Chronicles", "2CH", "History"),
    ("Ezra", "Ezra", "Ezra", "EZR", "History"), ("Neh", "Nehemiah", "Nehemiah", "NEH", "History"),
    ("Esth", "Esther", "Esther", "EST", "History"), ("Job", "Job", "Job", "JOB", "Wisdom / Poetry"),
    ("Ps", "Psalms", "Psalms", "PSA", "Wisdom / Poetry"), ("Prov", "Proverbs", "Proverbs", "PRO", "Wisdom / Poetry"),
    ("Eccl", "Ecclesiastes", "Ecclesiastes", "ECC", "Wisdom / Poetry"), ("Song", "Song of Solomon", "Song of Solomon", "SNG", "Wisdom / Poetry"),
    ("Isa", "Isaiah", "Isaiah", "ISA", "Major Prophets"), ("Jer", "Jeremiah", "Jeremiah", "JER", "Major Prophets"),
    ("Lam", "Lamentations", "Lamentations", "LAM", "Major Prophets"), ("Ezek", "Ezekiel", "Ezekiel", "EZK", "Major Prophets"),
    ("Dan", "Daniel", "Daniel", "DAN", "Major Prophets"), ("Hos", "Hosea", "Hosea", "HOS", "Minor Prophets"),
    ("Joel", "Joel", "Joel", "JOL", "Minor Prophets"), ("Amos", "Amos", "Amos", "AMO", "Minor Prophets"),
    ("Obad", "Obadiah", "Obadiah", "OBA", "Minor Prophets"), ("Jonah", "Jonah", "Jonah", "JON", "Minor Prophets"),
    ("Mic", "Micah", "Micah", "MIC", "Minor Prophets"), ("Nah", "Nahum", "Nahum", "NAM", "Minor Prophets"),
    ("Hab", "Habakkuk", "Habakkuk", "HAB", "Minor Prophets"), ("Zeph", "Zephaniah", "Zephaniah", "ZEP", "Minor Prophets"),
    ("Hag", "Haggai", "Haggai", "HAG", "Minor Prophets"), ("Zech", "Zechariah", "Zechariah", "ZEC", "Minor Prophets"),
    ("Mal", "Malachi", "Malachi", "MAL", "Minor Prophets"),
    ("Matt", "Matthew", "Matthew", "MAT", "Gospels"), ("Mark", "Mark", "Mark", "MRK", "Gospels"),
    ("Luke", "Luke", "Luke", "LUK", "Gospels"), ("John", "John", "John", "JHN", "Gospels"),
    ("Acts", "Acts", "Acts", "ACT", "Early Church History"), ("Rom", "Romans", "Romans", "ROM", "Paul's Letters"),
    ("1Cor", "1 Corinthians", "I Corinthians", "1CO", "Paul's Letters"), ("2Cor", "2 Corinthians", "II Corinthians", "2CO", "Paul's Letters"),
    ("Gal", "Galatians", "Galatians", "GAL", "Paul's Letters"), ("Eph", "Ephesians", "Ephesians", "EPH", "Paul's Letters"),
    ("Phil", "Philippians", "Philippians", "PHP", "Paul's Letters"), ("Col", "Colossians", "Colossians", "COL", "Paul's Letters"),
    ("1Thess", "1 Thessalonians", "I Thessalonians", "1TH", "Paul's Letters"), ("2Thess", "2 Thessalonians", "II Thessalonians", "2TH", "Paul's Letters"),
    ("1Tim", "1 Timothy", "I Timothy", "1TI", "Paul's Letters"), ("2Tim", "2 Timothy", "II Timothy", "2TI", "Paul's Letters"),
    ("Titus", "Titus", "Titus", "TIT", "Paul's Letters"), ("Phlm", "Philemon", "Philemon", "PHM", "Paul's Letters"),
    ("Heb", "Hebrews", "Hebrews", "HEB", "General Letters"), ("Jas", "James", "James", "JAS", "General Letters"),
    ("1Pet", "1 Peter", "I Peter", "1PE", "General Letters"), ("2Pet", "2 Peter", "II Peter", "2PE", "General Letters"),
    ("1John", "1 John", "I John", "1JN", "General Letters"), ("2John", "2 John", "II John", "2JN", "General Letters"),
    ("3John", "3 John", "III John", "3JN", "General Letters"), ("Jude", "Jude", "Jude", "JUD", "General Letters"),
    ("Rev", "Revelation", "Revelation of John", "REV", "Prophecy"),
]
ORIG_LANG = {"Gen": "Hebrew (two Aramaic words in 31:47)", "Jer": "Hebrew (one Aramaic verse, 10:11)",
             "Ezra": "Hebrew and Aramaic (4:8–6:18; 7:12–26)", "Dan": "Hebrew and Aramaic (2:4b–7:28)"}
# Books outside the 66-book Protestant canon, as named by scrollmapper, with their USFM codes.
EXTRA_BOOKS = [
    ("Tob", "Tobit", "Tobit", "TOB"), ("Jdt", "Judith", "Judith", "JDT"), ("EsthGr", "Esther (Greek)", "Esther (Greek)", "ESG"),
    ("AddEsth", "Additions to Esther", "Additions to Esther", "ADE"), ("Wis", "Wisdom of Solomon", "Wisdom", "WIS"),
    ("Sir", "Sirach", "Sirach", "SIR"), ("Bar", "Baruch", "Baruch", "BAR"), ("EpJer", "Epistle of Jeremiah", "Epistle of Jeremiah", "LJE"),
    ("PrAzar", "Prayer of Azariah", "Prayer of Azariah", "S3Y"), ("Sus", "Susanna", "Susanna", "SUS"),
    ("Bel", "Bel and the Dragon", "Bel and the Dragon", "BEL"), ("AddDan", "Additions to Daniel", "Additions to Daniel", "DAG"),
    ("1Macc", "1 Maccabees", "I Maccabees", "1MA"), ("2Macc", "2 Maccabees", "II Maccabees", "2MA"),
    ("3Macc", "3 Maccabees", "III Maccabees", "3MA"), ("4Macc", "4 Maccabees", "IV Maccabees", "4MA"),
    ("1Esd", "1 Esdras", "I Esdras", "1ES"), ("2Esd", "2 Esdras", "II Esdras", "2ES"), ("PrMan", "Prayer of Manasseh", "Prayer of Manasses", "MAN"),
    ("AddPs", "Psalm 151", "Additional Psalm", "PS2"), ("PssSol", "Psalms of Solomon", "Psalms of Solomon", "PSS"),
    ("Odes", "Odes", "Odes", "ODA"), ("1En", "1 Enoch", "I Enoch", "ENO"), ("EpLao", "Epistle to the Laodiceans", "Laodiceans", "LAO"),
]

LANGUAGES = {
    "en": "English", "enm": "Middle English", "hbo": "Ancient Hebrew", "grc": "Koine Greek", "syr": "Classical Syriac (Aramaic)",
    "la": "Latin", "cop-sa": "Sahidic Coptic", "got": "Gothic", "cu": "Church Slavonic", "de": "German", "fr": "French",
    "es": "Spanish", "pt": "Portuguese", "it": "Italian", "nl": "Dutch", "da": "Danish", "sv": "Swedish", "nb": "Norwegian Bokmål",
    "nn": "Norwegian Nynorsk", "fi": "Finnish", "et": "Estonian", "lv": "Latvian", "cs": "Czech", "sl": "Slovenian", "pl": "Polish",
    "hr": "Croatian", "sr": "Serbian", "hu": "Hungarian", "ru": "Russian", "uk": "Ukrainian", "el": "Modern Greek", "he": "Modern Hebrew",
    "sq": "Albanian", "hy": "Armenian", "ja": "Japanese", "ko": "Korean", "zh-hant": "Chinese (Traditional)", "lzh": "Classical Chinese",
    "vi": "Vietnamese", "th": "Thai", "tl": "Tagalog", "ceb": "Cebuano", "my": "Burmese", "ml": "Malayalam", "mg": "Malagasy",
    "mi": "Māori", "ht": "Haitian Creole", "eo": "Esperanto", "gv": "Manx Gaelic", "chr": "Cherokee", "bea": "Beaver (Dane-zaa)",
    "pon": "Pohnpeian", "sml": "Central Sama", "tsg": "Tausug", "tpi": "Tok Pisin", "tlh": "Klingon", "vls": "West Flemish",
}
ORIGINAL_LANGUAGE_TEXTS = {"WLC", "MapM", "SP", "Byz", "TR", "StatResGNT"}
# Catholic Bibles are left out of this project on purpose.
EXCLUDED_TRANSLATIONS = {"DRC", "CPDV", "FreCrampon"}
ANCIENT_VERSIONS = {"Peshitta", "Vulgate", "VulgClementine", "VulgConte", "VulgHetzenauer", "VulgSistine", "CopSahBible2", "Wulfila", "LXX"}


class Stage:
    """Tab-separated staging file, loaded into DuckDB with read_csv."""

    def __init__(self, name, cols):
        STAGE.mkdir(parents=True, exist_ok=True)
        self.name, self.cols = name, cols
        self.path = STAGE / f"{name}.tsv"
        self.f = open(self.path, "w", newline="", encoding="utf-8")
        self.w = csv.writer(self.f, delimiter="\t", lineterminator="\n")
        self.w.writerow([c for c, _ in cols])
        self.n = 0

    def add(self, *row):
        self.w.writerow(["" if x is None else x for x in row])
        self.n += 1

    def load(self, con, table, order_by=None):
        self.f.close()
        cols = "{" + ", ".join(f"'{c}': '{t}'" for c, t in self.cols) + "}"
        order = f" ORDER BY {order_by}" if order_by else ""
        con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv('{self.path.as_posix()}', delim='\t', header=true, "
                    f"quote='\"', escape='\"', nullstr='', columns={cols}, max_line_size=10000000){order}")
        return self.n


def norm_strongs(s):
    """'H430' / 'H0430G' / '{H0430G}' -> ('H0430', 'H0430G'); anything unparseable -> (None, None)."""
    m = re.search(r"([HG])0*(\d{1,4})([A-Za-z]?)", s or "")
    if not m:
        return None, None
    base = f"{m.group(1)}{int(m.group(2)):04d}"
    return base, base + m.group(3).upper() if m.group(3) else base


# --------------------------------------------------------------------------- USFM
USFM_SKIP_LINE = re.compile(r"^\\(id|ide|h|toc\d?|mt\d?|ms\d?|mr|s\d?|sr|r|d|sp|cl|rem|sts|is\d?|ip|imt\d?|io\d?|iot|ie|cp|periph)\b")
W_TAG = re.compile(r"\\\+?w\s+([^|\\]*?)\|([^\\]*?)\\\+?w\*")
NOTE = re.compile(r"\\(f|fe|x|ef|ex)\s.*?\\\1\*", re.S)
MARKER = re.compile(r"\\\+?[a-z]+\d*\*?")


def parse_usfm(path):
    """Yield (usfm_book_code, chapter, verse, plain_text, [(word, strongs), ...])."""
    book, chap, verse, buf = None, 0, 0, []
    text = NOTE.sub("", path.read_text(encoding="utf-8-sig"))

    def flush():
        if book and verse:
            raw = " ".join(buf)
            words = []
            for w, attrs in W_TAG.findall(raw):
                m = re.search(r'strong="([^"]+)"', attrs)
                for code in (m.group(1).replace(",", " ").split() if m else [None]):
                    words.append((w.strip(), code))
            plain = W_TAG.sub(lambda m: m.group(1), raw)
            plain = MARKER.sub(" ", plain)
            plain = re.sub(r"\s+([,.;:!?’”)])", r"\1", re.sub(r"\s+", " ", plain)).strip()
            if plain:
                yield (book, chap, verse, plain, words)

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("\\id "):
            book = line.split()[1]
            continue
        if USFM_SKIP_LINE.match(line):
            continue
        m = re.match(r"^\\c\s+(\d+)", line)
        if m:
            yield from flush()
            chap, verse, buf = int(m.group(1)), 0, []
            continue
        for part in re.split(r"(\\v\s+\d+[a-z]?(?:-\d+)?\s)", line):
            mv = re.match(r"\\v\s+(\d+)", part)
            if mv:
                yield from flush()
                verse, buf = int(mv.group(1)), []
            elif verse:
                buf.append(part)
    yield from flush()


# --------------------------------------------------------------------------- build
def main():
    import argparse
    ap = argparse.ArgumentParser(description="Build bible.duckdb from bibledb/raw.")
    ap.add_argument("--open-only", action="store_true",
                    help="leave out texts whose licence forbids commercial use or derivatives, is copyrighted, or is not stated "
                         "(use this before sharing the built database with others)")
    ap.add_argument("--output", help="write the database to this file instead of bibledb/bible.duckdb")
    args = ap.parse_args()
    global DB
    if args.output:
        DB = Path(args.output).resolve()
    if DB.exists():
        DB.unlink()
    wal = Path(str(DB) + ".wal")
    if wal.exists():
        wal.unlink()
    con = duckdb.connect(str(DB))
    con.execute("SET preserve_insertion_order=false")

    # ---- books & verses -----------------------------------------------------
    bookid = {}
    rows = []
    for i, (osis, name, sname, usfm, genre) in enumerate(CANON, 1):
        rows.append((i, osis, name, "OT" if i <= 39 else "NT", genre, "Protestant canon", ORIG_LANG.get(osis, "Hebrew" if i <= 39 else "Greek"), usfm, sname))
    for j, (osis, name, sname, usfm) in enumerate(EXTRA_BOOKS, 67):
        rows.append((j, osis, name, "Deuterocanon / Apocrypha", "Deuterocanonical & other", "Outside the Protestant canon", "Greek (some Hebrew/Aramaic originals)", usfm, sname))
    for r in rows:
        bookid[r[1]] = r[0]
    usfm_to_book = {r[7]: r[0] for r in rows}
    scroll_to_book = {r[8]: r[0] for r in rows}
    con.execute("CREATE TABLE books (book_id SMALLINT PRIMARY KEY, osis VARCHAR, name VARCHAR, testament VARCHAR, genre VARCHAR, canon VARCHAR, original_language VARCHAR, usfm_code VARCHAR, source_name VARCHAR)")
    con.executemany("INSERT INTO books VALUES (?,?,?,?,?,?,?,?,?)", rows)

    kjv = (RAW / "scrollmapper" / "parquet" / "KJV.parquet").as_posix()
    con.execute("CREATE TEMP TABLE bookmap AS SELECT book_id, osis, name, source_name FROM books")
    con.execute(f"""
        CREATE TABLE verses AS
        SELECT row_number() OVER (ORDER BY b.book_id, p.chapter, p.verse)::INTEGER AS verse_id,
               b.book_id, p.chapter::SMALLINT AS chapter, p.verse::SMALLINT AS verse,
               b.osis || '.' || p.chapter || '.' || p.verse AS osis_ref,
               b.name || ' ' || p.chapter || ':' || p.verse AS reference
        FROM read_parquet('{kjv}') p JOIN bookmap b ON b.source_name = p.book_name
        WHERE b.book_id <= 66 AND trim(coalesce(p.text, '')) <> ''
        ORDER BY 1""")
    con.execute("""ALTER TABLE books ADD COLUMN chapters SMALLINT; ALTER TABLE books ADD COLUMN verses SMALLINT;
        UPDATE books SET chapters = s.c, verses = s.v FROM (SELECT book_id, max(chapter) c, count(*) v FROM verses GROUP BY 1) s WHERE s.book_id = books.book_id""")
    nverses = con.execute("SELECT count(*) FROM verses").fetchone()[0]
    assert nverses == 31102, nverses
    vid = {(b, c, v): i for i, b, c, v in con.execute("SELECT verse_id, book_id, chapter, verse FROM verses").fetchall()}
    log(f"books and {nverses} verses")

    # ---- translations (scrollmapper) -----------------------------------------
    tr_rows = []
    for md in sorted((RAW / "scrollmapper" / "readme").glob("*.md")):
        lang, tid = md.stem.split("__")
        if tid in EXCLUDED_TRANSLATIONS:
            continue
        txt = md.read_text(encoding="utf-8")
        m = re.match(r"#\s*([^:]+):\s*(.+)", txt)
        title = m.group(2).strip() if m else tid
        lic = re.search(r"\*\*License:\*\*\s*(.+)", txt)
        license_ = lic.group(1).strip() if lic else (txt.split("\n", 2)[2].strip() if txt.count("\n") >= 2 else "Not stated")
        license_ = re.sub(r"^\*\*License\*\*:\s*", "", license_)
        if license_.lower() in ("null", "none", ""):
            license_ = "Not stated"
        year = re.search(r"\b(1[3-9]\d\d|20[0-2]\d)\b", title)
        cat = "Original-language text" if tid in ORIGINAL_LANGUAGE_TEXTS else "Ancient version" if tid in ANCIENT_VERSIONS else "Translation"
        tr_rows.append(dict(translation_id=tid, title=title, language_code=lang, language=LANGUAGES.get(lang, lang), category=cat,
                            year=int(year.group(1)) if year else None, license=license_, source="scrollmapper/bible_databases (from CrossWire SWORD modules)",
                            source_url=f"https://github.com/scrollmapper/bible_databases/tree/master/sources/{lang}/{tid}",
                            has_strongs=False, strongs_source=None))
    for r in tr_rows:
        r["stem"] = r["translation_id"]
        if r["translation_id"] == "KJV":  # "KJV" is the eBible.org edition below (with Strong's and red letters)
            r.update(translation_id="KJV1769", title="King James Version (1769), CrossWire SWORD edition")
    con.execute("CREATE TEMP TABLE tmap (translation_id VARCHAR, stem VARCHAR)")
    con.executemany("INSERT INTO tmap VALUES (?, ?)", [(r["translation_id"], r["stem"]) for r in tr_rows])
    # unknown book names get new ids so nothing is dropped
    names = [r[0] for r in con.execute(f"SELECT DISTINCT book_name FROM read_parquet('{(RAW / 'scrollmapper' / 'parquet').as_posix()}/*.parquet')").fetchall()]
    for n in names:
        if n not in scroll_to_book:
            new_id = max(r[0] for r in rows) + 1
            rows.append((new_id, re.sub(r"\W", "", n), n, "Deuterocanon / Apocrypha", "Deuterocanonical & other", "Outside the Protestant canon", None, None, n))
            con.execute("INSERT INTO books (book_id, osis, name, testament, genre, canon, source_name) VALUES (?,?,?,?,?,?,?)", rows[-1][:6] + (n,))
            scroll_to_book[n] = new_id
    con.execute("CREATE OR REPLACE TEMP TABLE bookmap AS SELECT book_id, source_name FROM books")
    con.execute(f"""
        CREATE TABLE verse_text AS
        SELECT t.translation_id, b.book_id::SMALLINT AS book_id, p.chapter::SMALLINT AS chapter, p.verse::SMALLINT AS verse,
               v.verse_id, trim(p.text) AS text
        FROM read_parquet('{(RAW / 'scrollmapper' / 'parquet').as_posix()}/*.parquet', filename=true) p
        JOIN tmap t ON t.stem = parse_filename(p.filename, true)
        JOIN bookmap b ON b.source_name = p.book_name
        LEFT JOIN verses v ON v.book_id = b.book_id AND v.chapter = p.chapter AND v.verse = p.verse
        WHERE trim(coalesce(p.text, '')) <> ''""")
    log(f"scrollmapper: {len(tr_rows)} translations, {con.execute('SELECT count(*) FROM verse_text').fetchone()[0]:,} verse rows")

    # ---- eBible USFM: WEB and KJV (Strong's tags + red letters), Septuagint ------
    ebible = {r["translationId"]: r for r in csv.DictReader(open(RAW / "ebible_translations.csv", encoding="utf-8-sig"))}
    vt = Stage("verse_text_ebible", [("translation_id", "VARCHAR"), ("book_id", "SMALLINT"), ("chapter", "SMALLINT"), ("verse", "SMALLINT"), ("verse_id", "INTEGER"), ("text", "VARCHAR")])
    tw = Stage("translation_words", [("translation_id", "VARCHAR"), ("verse_id", "INTEGER"), ("book_id", "SMALLINT"), ("chapter", "SMALLINT"), ("verse", "SMALLINT"),
                                     ("word_seq", "SMALLINT"), ("word", "VARCHAR"), ("strongs", "VARCHAR"), ("strongs_extended", "VARCHAR"),
                                     ("original_text", "VARCHAR"), ("transliteration", "VARCHAR"), ("parsing", "VARCHAR"), ("language", "VARCHAR"),
                                     ("start_char", "SMALLINT"), ("end_char", "SMALLINT"), ("red_letter", "VARCHAR")])
    ss = Stage("speech_spans", [("translation_id", "VARCHAR"), ("verse_id", "INTEGER"), ("book_id", "SMALLINT"), ("chapter", "SMALLINT"), ("verse", "SMALLINT"),
                                ("start_char", "SMALLINT"), ("end_char", "SMALLINT"), ("speaker", "VARCHAR"), ("method", "VARCHAR"), ("text", "VARCHAR")])
    log("finding words of Jesus and of God (red letters)…")
    RL = red_letter.build(RAW)
    for tid in ("WEB", "KJV"):
        n = 0
        for (code, c, v), d in RL[tid].items():
            b = usfm_to_book.get(code)
            if b is None:
                continue
            verse_id = vid.get((b, c, v)) if b <= 66 else None
            vt.add(tid, b, c, v, verse_id, d["text"])
            n += 1
            for s0, e0, speaker, method in d["spans"]:
                ss.add(tid, verse_id, b, c, v, s0, e0, speaker, method, d["text"][s0:e0])
            if verse_id:
                for seq, (s0, e0, code_s) in enumerate(d["words"], 1):
                    base, ext = norm_strongs(code_s)
                    red = next((sp[2] for sp in d["spans"] if sp[0] <= s0 < sp[1]), None)
                    tw.add(tid, verse_id, b, c, v, seq, d["text"][s0:e0], base, ext, None, None, None,
                           "Hebrew" if (base or "").startswith("H") else "Greek" if base else None, s0, e0, red)
        log(f"eBible {tid}: {n:,} verses")
    tr_rows.append(dict(translation_id="WEB", title="World English Bible (Protestant edition)", language_code="en", language="English", category="Translation",
                        year=None, license="Public Domain", source="eBible.org USFM (engwebp)", source_url="https://ebible.org/engwebp/", has_strongs=True,
                        strongs_source="eBible.org USFM word tags (machine-assisted alignment)"))
    tr_rows.append(dict(translation_id="KJV", title="King James Version (eBible.org edition, with Strong's numbers and words of Jesus marked)", language_code="en", language="English",
                        category="Translation", year=1769, license="Public Domain", source="eBible.org USFM (eng-kjv2006)", source_url="https://ebible.org/eng-kjv2006/", has_strongs=True,
                        strongs_source="eBible.org KJV (eng-kjv2006) USFM word tags, from the CrossWire KJV Strong's module"))
    n = 0
    for f in sorted((RAW / "lxx_usfm").glob("*.usfm")):
        for code, c, v, plain, _ in parse_usfm(f):
            b = usfm_to_book.get(code)
            if b is None:
                continue
            if code == "DAG":
                b = bookid["Dan"]   # the Septuagint's Daniel (with the Greek additions)
            if code == "ESG":
                b = bookid["Esth"]  # the Septuagint's Esther (with the Greek additions)
            vt.add("LXX", b, c, v, vid.get((b, c, v)) if b <= 66 else None, plain)
            n += 1
    e = ebible["grclxx"]
    tr_rows.append(dict(translation_id="LXX", title="Septuagint (Greek Old Testament)", language_code="grc", language="Koine Greek", category="Ancient version",
                        year=None, license=e["Copyright"].strip().title() or "Public Domain", source="eBible.org USFM (grclxx)", source_url="https://ebible.org/grclxx/",
                        has_strongs=False, strongs_source=None))
    log(f"eBible LXX: {n:,} verses")
    for et in EBIBLE_ENGLISH:  # more English translations from eBible.org
        folder = RAW / "ebible" / et["ebible"]
        if not folder.exists():
            log(f"  {et['id']} not downloaded (run download.py); skipped")
            continue
        n = 0
        for f in sorted(folder.glob("*.usfm")):
            for code, c, v, plain, _ in parse_usfm(f):
                b = usfm_to_book.get(code)
                if b is None:
                    continue
                vt.add(et["id"], b, c, v, vid.get((b, c, v)) if b <= 66 else None, plain)
                n += 1
        tr_rows.append(dict(translation_id=et["id"], title=et["title"], language_code="en", language="English", category="Translation",
                            year=et["year"], license=et["license"], source=f"eBible.org USFM ({et['ebible']}) — {et['attribution']}",
                            source_url=f"https://ebible.org/{et['ebible']}/", has_strongs=False, strongs_source=None))
        log(f"eBible {et['id']}: {n:,} verses")
    ss.load(con, "speech_spans", "translation_id, verse_id, start_char")
    vt.load(con, "verse_text_ebible")
    con.execute("INSERT INTO verse_text SELECT * FROM verse_text_ebible; DROP TABLE verse_text_ebible")

    # ---- BSB interlinear (Berean tables) ---------------------------------------
    log("reading Berean interlinear workbook (slow)…")
    con.execute("INSTALL excel; LOAD excel")
    con.execute(f"CREATE TEMP TABLE bsb_raw AS SELECT * FROM read_xlsx('{(RAW / 'bsb_tables.xlsx').as_posix()}', sheet='biblosinterlinear96', header=true, all_varchar=true, stop_at_empty=false)")
    cols = [r[0] for r in con.execute("DESCRIBE bsb_raw").fetchall()]
    col = lambda prefix: next(c for c in cols if c.strip().lower().startswith(prefix.lower()))
    c_sort, c_verse, c_lang, c_orig, c_tr, c_pars, c_sh, c_sg, c_vid, c_eng = (col("BSB Sort"), col("Verse"), col("Language"), col("WLC / Nestle Base TR"), col("Translit"),
                                                                             [c for c in cols if c.lower().startswith("parsing")][-1], col("Str Heb"), col("Str Grk"), col("VerseId"), col("BSB version"))
    bsb = con.execute(f'SELECT "{c_sort}", "{c_verse}", "{c_lang}", "{c_orig}", "{c_tr}", "{c_pars}", "{c_sh}", "{c_sg}", "{c_vid}", "{c_eng}" FROM bsb_raw').fetchall()
    name_to_book = {r[2].lower(): r[0] for r in rows}
    name_to_book.update({"psalm": bookid["Ps"], "song of songs": bookid["Song"]})
    verse_label = {}
    for r in bsb:
        if r[8] and r[1]:
            verse_label[r[1]] = r[8]
    bsb.sort(key=lambda r: int(float(r[0])) if r[0] else 0)
    seqs, nb = {}, 0
    for sort, vnum, lang, orig, tr, pars, sh, sg, _, eng in bsb:
        lab = verse_label.get(vnum)
        m = re.match(r"(.+?)\s+(\d+):(\d+)$", (lab or "").strip())
        if not m:
            continue
        b = name_to_book.get(m.group(1).lower())
        verse_id = vid.get((b, int(m.group(2)), int(m.group(3)))) if b else None
        if not verse_id:
            continue
        num = sh if (lang or "").startswith(("Hebrew", "Aramaic")) else sg
        base, ext = norm_strongs(("H" if (lang or "").startswith(("Hebrew", "Aramaic")) else "G") + str(int(float(num)))) if num and re.match(r"^\d+(\.0)?$", num.strip()) else (None, None)
        word = (eng or "").strip()
        if not base and word in ("-", ""):
            continue  # layout-only rows in the workbook
        seqs[verse_id] = seqs.get(verse_id, 0) + 1
        tw.add("BSB", verse_id, b, int(m.group(2)), int(m.group(3)), seqs[verse_id], word if word not in ("-", "") else None, base, ext, orig, tr, pars, lang, None, None, None)
        nb += 1
    con.execute("DROP TABLE bsb_raw")
    tw.load(con, "translation_words", "translation_id, verse_id, word_seq")
    for r in tr_rows:
        if r["translation_id"] == "BSB":
            r.update(has_strongs=True, strongs_source="Berean Bible interlinear tables (bereanbible.com), BSB rendering aligned to each Hebrew/Greek word")
    log(f"translation_words: {con.execute('SELECT count(*) FROM translation_words').fetchone()[0]:,} rows (BSB {nb:,})")

    # ---- original-language words (STEPBible TAHOT / TAGNT) ----------------------
    ow = Stage("original_words", [("source", "VARCHAR"), ("verse_id", "INTEGER"), ("book_id", "SMALLINT"), ("chapter", "SMALLINT"), ("verse", "SMALLINT"),
                                  ("word_pos", "SMALLINT"), ("word_type", "VARCHAR"), ("language", "VARCHAR"), ("text", "VARCHAR"), ("segmented", "VARCHAR"),
                                  ("transliteration", "VARCHAR"), ("english", "VARCHAR"), ("strongs", "VARCHAR"), ("strongs_extended", "VARCHAR"),
                                  ("all_strongs", "VARCHAR"), ("morphology", "VARCHAR"), ("lemma", "VARCHAR"), ("gloss", "VARCHAR"), ("editions", "VARCHAR"), ("source_ref", "VARCHAR")])
    ref_re = re.compile(r"^([1-3]?[A-Za-z]+)\.(\d+)\.(\d+)(?:\([^)]*\))?(?:[a-z])?#(\d+)=(\S+)$")
    for kind, pattern, first_book in [("TAHOT", "TAHOT*.txt", 1), ("TAGNT", "TAGNT*.txt", 40)]:
        files = sorted((RAW / "stepbible").glob(pattern), key=lambda p: ["Gen", "Jos", "Job", "Isa", "Mat", "Act"].index(p.name.split()[1][:3]))
        codes, n = {}, 0
        for f in files:
            with open(f, encoding="utf-8-sig") as fh:
                for line in fh:
                    cells = line.rstrip("\n").split("\t")
                    m = ref_re.match(cells[0].strip())
                    if not m or len(cells) < 6:
                        continue
                    code = m.group(1)
                    if code not in codes:
                        codes[code] = first_book + len(codes)
                    b, c, v, pos, typ = codes[code], int(m.group(2)), int(m.group(3)), int(m.group(4)), m.group(5)
                    verse_id = vid.get((b, c, v))
                    if kind == "TAHOT":
                        heb, translit, eng, dstr, gram = cells[1], cells[2], cells[3], cells[4], cells[5]
                        main = re.search(r"\{([^}]+)\}", dstr)
                        base, ext = norm_strongs(main.group(1) if main else dstr)
                        lang = "Aramaic" if gram.startswith("A") else "Hebrew"
                        lemma = gloss = None
                        if len(cells) > 11:
                            mm = re.search(r"\{H\d+[A-Za-z]?=([^=]+)=([^}]+)\}", cells[11])
                            if mm:
                                lemma, gloss = mm.group(1), mm.group(2).split("»")[0].lstrip(": ")
                        ow.add(kind, verse_id, b, c, v, pos, typ, lang, heb.replace("/", "").replace("\\", ""), heb, translit, eng, base, ext, dstr, gram, lemma, gloss, None, cells[0])
                    else:
                        gm = re.match(r"(.*?)\s*\((.*)\)\s*$", cells[1])
                        greek, translit = (gm.group(1), gm.group(2)) if gm else (cells[1], None)
                        sg, _, gram = cells[3].partition("=")
                        base, ext = norm_strongs(sg)
                        lemma, _, gloss = cells[4].partition("=")
                        ow.add(kind, verse_id, b, c, v, pos, typ, "Greek", greek.strip(), None, translit, cells[2], base, ext, sg, gram, lemma or None, gloss or None,
                               cells[5] if len(cells) > 5 else None, cells[0])
                    n += 1
        assert len(codes) == (39 if kind == "TAHOT" else 27), (kind, len(codes))
        log(f"{kind}: {n:,} words")
    ow.load(con, "original_words", "book_id, chapter, verse, word_pos")
    tr_rows += [
        dict(translation_id="TAHOT", title="Translators Amalgamated Hebrew OT (Leningrad Codex base, word-tagged)", language_code="hbo", language="Ancient Hebrew & Aramaic",
             category="Original-language text", year=None, license="CC BY 4.0", source="STEPBible.org / Tyndale House Cambridge", source_url="https://github.com/STEPBible/STEPBible-Data",
             has_strongs=True, strongs_source="STEPBible extended Strong's tags (every word)"),
        dict(translation_id="TAGNT", title="Translators Amalgamated Greek NT (NA27/28, SBL, TR, Byzantine and others, word-tagged)", language_code="grc", language="Koine Greek",
             category="Original-language text", year=None, license="CC BY 4.0", source="STEPBible.org / Tyndale House Cambridge", source_url="https://github.com/STEPBible/STEPBible-Data",
             has_strongs=True, strongs_source="STEPBible extended Strong's tags (every word)"),
    ]
    # TAHOT/TAGNT also as plain verse text (words joined) so they appear in parallel views
    con.execute("""INSERT INTO verse_text
        SELECT source, book_id, chapter, verse, verse_id, string_agg(text, ' ' ORDER BY word_pos)
        FROM original_words WHERE verse_id IS NOT NULL AND (source = 'TAGNT' AND word_type LIKE 'N%' OR source = 'TAHOT' AND word_type NOT IN ('K'))
        GROUP BY ALL""")

    # ---- Strong's dictionaries & extended lexicons ----------------------------
    st = Stage("strongs", [("strongs_id", "VARCHAR"), ("number", "SMALLINT"), ("testament_language", "VARCHAR"), ("language", "VARCHAR"), ("lemma", "VARCHAR"),
                           ("transliteration", "VARCHAR"), ("pronunciation", "VARCHAR"), ("derivation", "VARCHAR"), ("definition", "VARCHAR"), ("kjv_usage", "VARCHAR")])
    for fname, prefix in [("strongs-hebrew-dictionary.js", "H"), ("strongs-greek-dictionary.js", "G")]:
        raw = (RAW / fname).read_text(encoding="utf-8")
        d = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
        for k, e in d.items():
            base, _ = norm_strongs(k)
            deriv = e.get("derivation") or ""
            lang = ("Aramaic" if re.search(r"Aramaic|Chald", deriv) else "Hebrew") if prefix == "H" else "Greek"
            st.add(base, int(base[1:]), "Old Testament" if prefix == "H" else "New Testament", lang, e.get("lemma"), e.get("xlit") or e.get("translit"),
                   e.get("pron"), deriv or None, e.get("strongs_def"), e.get("kjv_def"))
    st.load(con, "strongs", "strongs_id")
    lx = Stage("lexicon_extended", [("extended_id", "VARCHAR"), ("strongs_id", "VARCHAR"), ("relation", "VARCHAR"), ("unified_strongs", "VARCHAR"), ("lemma", "VARCHAR"),
                                    ("transliteration", "VARCHAR"), ("language", "VARCHAR"), ("part_of_speech", "VARCHAR"), ("gloss", "VARCHAR"), ("definition_html", "VARCHAR")])
    langcode = {"H": "Hebrew", "A": "Aramaic", "G": "Greek", "N": "Proper name"}
    for fname in ["TBESH - Translators Brief lexicon of Extended Strongs for Hebrew - STEPBible.org CC BY.txt", "TBESG - Translators Brief lexicon of Extended Strongs for Greek - STEPBible.org CC BY.txt"]:
        with open(RAW / "stepbible" / fname, encoding="utf-8-sig") as fh:
            for line in fh:
                cells = line.rstrip("\n").split("\t")
                if len(cells) < 8 or not re.match(r"^[HG]\d{4}", cells[0]):
                    continue
                ext_id, _, relation = cells[1].partition(" =")
                base, _ = norm_strongs(cells[0])
                morph_lang, _, pos = cells[5].partition(":")
                lx.add(ext_id.strip(), base, relation.strip() or None, cells[2].strip() or None, cells[3], cells[4], langcode.get(morph_lang, morph_lang), pos, cells[6], cells[7].strip())
    lx.load(con, "lexicon_extended", "extended_id")
    con.execute("""CREATE TABLE verse_strongs AS
        SELECT DISTINCT verse_id, strongs, language FROM original_words
        WHERE verse_id IS NOT NULL AND strongs IS NOT NULL AND NOT regexp_matches(strongs, '^H9[0-9]{3}$')
        ORDER BY verse_id, strongs""")
    log(f"strongs {con.execute('SELECT count(*) FROM strongs').fetchone()[0]:,}, lexicon_extended {con.execute('SELECT count(*) FROM lexicon_extended').fetchone()[0]:,}")

    # ---- red-letter flags on verses ----------------------------------------------
    con.execute("""
        ALTER TABLE verses ADD COLUMN words_of_jesus BOOLEAN DEFAULT false;
        ALTER TABLE verses ADD COLUMN words_of_god_detected BOOLEAN DEFAULT false;
        ALTER TABLE verses ADD COLUMN god_detection_method VARCHAR;
        ALTER TABLE verses ADD COLUMN red_letter VARCHAR;
        UPDATE verses SET words_of_jesus = true WHERE verse_id IN (SELECT verse_id FROM speech_spans WHERE speaker = 'Jesus' AND verse_id IS NOT NULL);
        UPDATE verses SET words_of_god_detected = true, god_detection_method = s.m
        FROM (SELECT verse_id, CASE WHEN bool_or(method = 'quotation heuristic') THEN 'quotation heuristic' ELSE 'dialogue heuristic' END m
              FROM speech_spans WHERE translation_id = 'WEB' AND speaker = 'God' AND verse_id IS NOT NULL GROUP BY 1) s
        WHERE s.verse_id = verses.verse_id;
        UPDATE verses SET red_letter = CASE WHEN words_of_jesus AND words_of_god_detected THEN 'Jesus + God (detected)'
                                            WHEN words_of_jesus THEN 'Jesus' WHEN words_of_god_detected THEN 'God (detected)' END""")
    log(f"red letters: {con.execute('SELECT count(*) FILTER (words_of_jesus), count(*) FILTER (words_of_god_detected) FROM verses').fetchone()} verses (Jesus, God)")

    # ---- repeated phrases ("echoes") in the original languages ----------------------
    log("finding repeated phrases…")
    bname = dict(con.execute("SELECT book_id, name FROM books").fetchall())
    corpora = {}
    corpora["ot"] = [dict(norm=phrases.norm_hebrew(t), lemma=s, book_id=b, chapter=c, verse=v, verse_id=vi, text=t, gloss=g,
                          translit=phrases.clean_step_translit(tr) or "-")
                     for t, s, b, c, v, vi, g, tr in con.execute(
                         """SELECT text, strongs, book_id, chapter, verse, verse_id, english, transliteration FROM original_words
                            WHERE source = 'TAHOT' AND word_type NOT LIKE 'K%' AND word_type NOT LIKE 'X%' AND text NOT IN ('ס', 'פ', '׆')
                            ORDER BY book_id, chapter, verse, word_pos""").fetchall()]
    corpora["nt"] = [dict(norm=phrases.norm_greek(t), lemma=s, book_id=b, chapter=c, verse=v, verse_id=vi, text=t.replace("¶", ""), gloss=g,
                          translit=(tr or phrases.translit_greek(t)).replace(" ", "") or "-")
                     for t, s, b, c, v, vi, g, tr in con.execute(
                         """SELECT text, strongs, book_id, chapter, verse, verse_id, english, transliteration FROM original_words
                            WHERE source = 'TAGNT' AND word_type LIKE 'N%' ORDER BY book_id, chapter, verse, word_pos""").fetchall()]
    gk = []
    for text, b, c, v, vi in con.execute("SELECT text, book_id, chapter, verse, verse_id FROM verse_text WHERE translation_id = 'LXX' ORDER BY book_id, chapter, verse").fetchall():
        for w in text.split():
            gk.append(dict(norm=phrases.norm_greek(w), lemma=None, book_id=b, chapter=c, verse=v, verse_id=vi, text=w, gloss=None,
                           translit=phrases.translit_greek(w) or "-"))
    gk += [dict(t, book_id=t["book_id"]) for t in corpora["nt"]]
    corpora["gk"] = gk
    for k in corpora:
        corpora[k] = [t for t in corpora[k] if t["norm"]]
    pst = Stage("phrase_length_stats", [("corpus", "VARCHAR"), ("match_mode", "VARCHAR"), ("length_words", "SMALLINT"), ("distinct_phrases", "INTEGER"), ("occurrences", "INTEGER")])
    prp = Stage("phrase_repeats", [("repeat_id", "INTEGER"), ("corpus", "VARCHAR"), ("match_mode", "VARCHAR"), ("length_words", "SMALLINT"), ("occurrence_count", "SMALLINT"),
                                   ("book_count", "SMALLINT"), ("phrase_text", "VARCHAR"), ("phrase_gloss", "VARCHAR"), ("phrase_transliteration", "VARCHAR")])
    poc = Stage("phrase_occurrences", [("repeat_id", "INTEGER"), ("occurrence_no", "SMALLINT"), ("book_id", "SMALLINT"), ("start_chapter", "SMALLINT"), ("start_verse", "SMALLINT"),
                                       ("end_chapter", "SMALLINT"), ("end_verse", "SMALLINT"), ("start_verse_id", "INTEGER"), ("end_verse_id", "INTEGER"),
                                       ("reference", "VARCHAR"), ("text", "VARCHAR"), ("transliteration", "VARCHAR"), ("strongs", "VARCHAR")])
    rid = 0
    for corpus, modes in [("ot", ["exact", "lemma"]), ("nt", ["exact", "lemma"]), ("gk", ["exact"])]:
        toks = corpora[corpus]
        for mode in modes:
            stats, reps = phrases.run_corpus(toks, mode)
            for n, distinct, occ in stats:
                pst.add(corpus, mode, n, distinct, occ)
            for n, starts_ in sorted(reps, key=lambda r: (-r[0], r[1][0])):
                rid += 1
                first = toks[starts_[0]:starts_[0] + n]
                glosses = [t["gloss"] for t in first if t["gloss"]]
                prp.add(rid, corpus, mode, n, len(starts_), len({toks[p]["book_id"] for p in starts_}), " ".join(t["text"] for t in first),
                        " ".join(glosses).replace("/ ", " ").replace("/", " ") if glosses else None, " ".join(t["translit"] for t in first))
                for k, p in enumerate(sorted(starts_), 1):
                    a, z = toks[p], toks[p + n - 1]
                    ref = f"{bname.get(a['book_id'], a['book_id'])} {a['chapter']}:{a['verse']}" + (
                        "" if (a["chapter"], a["verse"]) == (z["chapter"], z["verse"]) else (f"–{z['verse']}" if a["chapter"] == z["chapter"] else f"–{z['chapter']}:{z['verse']}"))
                    poc.add(rid, k, a["book_id"], a["chapter"], a["verse"], z["chapter"], z["verse"], a["verse_id"], z["verse_id"], ref, " ".join(t["text"] for t in toks[p:p + n]),
                            " ".join(t["translit"] for t in toks[p:p + n]), " ".join(t["lemma"] or "-" for t in toks[p:p + n]))
            log(f"  {corpus}/{mode}: lengths {stats[0][0] if stats else '-'}–{stats[-1][0] if stats else '-'}, {len(reps):,} repeated phrases")
    pst.load(con, "phrase_length_stats", "corpus, match_mode, length_words")
    prp.load(con, "phrase_repeats", "repeat_id")
    poc.load(con, "phrase_occurrences", "repeat_id, occurrence_no")
    del corpora, gk

    # ---- cross references -----------------------------------------------------
    osis_to_book = {r[1]: r[0] for r in rows}
    maxc = dict(con.execute("SELECT book_id, max(chapter) FROM verses GROUP BY 1").fetchall())
    maxv = {(b, c): n for b, c, n in con.execute("SELECT book_id, chapter, max(verse) FROM verses GROUP BY 1, 2").fetchall()}

    def gid(tok):
        bk, ch, vs = tok.split(".")
        b = osis_to_book[bk]
        c = min(int(ch), maxc[b])
        return vid[(b, c, min(int(vs), maxv[(b, c)]))]

    xr = Stage("cross_references", [("from_verse_id", "INTEGER"), ("to_verse_start_id", "INTEGER"), ("to_verse_end_id", "INTEGER"), ("votes", "INTEGER"),
                                    ("from_osis", "VARCHAR"), ("to_osis", "VARCHAR")])
    with open(RAW / "cross_references" / "cross_references.txt", encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 3:
                continue
            s, _, e = p[1].partition("-")
            a, ts = gid(p[0]), gid(s)
            xr.add(a, ts, max(ts, gid(e)) if e else ts, int(p[2]), p[0], p[1])
    xr.load(con, "cross_references", "from_verse_id, votes DESC")
    log(f"cross_references {xr.n:,}")

    # ---- book origins -----------------------------------------------------------
    con.execute("CREATE TABLE scholarly_sources (source_id VARCHAR PRIMARY KEY, kind VARCHAR, author VARCHAR, title VARCHAR, date VARCHAR, url VARCHAR)")
    con.executemany("INSERT INTO scholarly_sources VALUES (?,?,?,?,?,?)", [(k, s["kind"], s["author"], s["title"], s["date"], s["url"]) for k, s in BO.SOURCES.items()])
    con.execute("CREATE TABLE places (place_id VARCHAR PRIMARY KEY, name VARCHAR, latitude DOUBLE, longitude DOUBLE, precision VARCHAR)")
    con.executemany("INSERT INTO places VALUES (?,?,?,?,?)", [(k, *p) for k, p in BO.PLACES.items()])
    con.execute("""CREATE TABLE book_authorship (authorship_id INTEGER PRIMARY KEY, book_id SMALLINT, view VARCHAR, section VARCHAR, author VARCHAR,
        date_from INTEGER, date_to INTEGER, date_display VARCHAR, place_id VARCHAR, place_display VARCHAR, held_by VARCHAR, note VARCHAR)""")
    con.execute("CREATE TABLE book_authorship_sources (authorship_id INTEGER, source_id VARCHAR, locator VARCHAR)")
    con.execute("CREATE TABLE book_dating (book_id SMALLINT PRIMARY KEY, consensus VARCHAR, consensus_note VARCHAR, traditional_year DOUBLE, critical_year DOUBLE)")
    aid = 0
    for osis, info in BO.ORIGINS.items():
        b = bookid[osis]
        for vw in info["views"]:
            aid += 1
            con.execute("INSERT INTO book_authorship VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (aid, b, vw["view"], vw["section"], vw["author"], vw["date_from"], vw["date_to"],
                        vw["date_display"], vw["place_id"], vw["place_display"], vw["held_by"], vw["note"]))
            for sid, loc in vw["sources"]:
                assert sid in BO.SOURCES, sid
                con.execute("INSERT INTO book_authorship_sources VALUES (?,?,?)", (aid, sid, loc))
        con.execute("INSERT INTO book_dating VALUES (?,?,?,?,?)", (b, info["consensus"], BO.CONSENSUS_NOTE[info["consensus"]],
                    BO.representative_year(osis, "traditional"), BO.representative_year(osis, "critical")))
    assert len(BO.ORIGINS) == 66
    log(f"book_authorship {aid} views")

    # ---- repair double-encoded characters in source texts (UTF-8 read as Windows-1252) ----
    moji = re.compile(r"[ÂÃ][-¿]|â€[-¿ŒœŠšŸŽžƒˆ˜–-›™]")

    def unmojibake(m):
        try:
            return m.group(0).encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return m.group(0)

    fixed = 0
    for tid, b, c, v, text in con.execute("SELECT translation_id, book_id, chapter, verse, text FROM verse_text WHERE regexp_matches(text, '[ÂÃ][-¿]|â€')").fetchall():
        new = moji.sub(unmojibake, text)
        if new != text:
            con.execute("UPDATE verse_text SET text = ? WHERE translation_id = ? AND book_id = ? AND chapter = ? AND verse = ?", (new, tid, b, c, v))
            fixed += 1
    log(f"repaired double-encoded characters in {fixed} verses")

    # ---- translations table + versification -------------------------------------
    con.execute("""CREATE TABLE translations (translation_id VARCHAR PRIMARY KEY, title VARCHAR, language_code VARCHAR, language VARCHAR, category VARCHAR,
        year SMALLINT, license VARCHAR, source VARCHAR, source_url VARCHAR, has_strongs BOOLEAN, strongs_source VARCHAR)""")
    con.executemany("INSERT INTO translations VALUES (?,?,?,?,?,?,?,?,?,?,?)", [tuple(r[k] for k in ["translation_id", "title", "language_code", "language", "category", "year", "license",
                                                                                                  "source", "source_url", "has_strongs", "strongs_source"]) for r in tr_rows])
    con.execute("""
        ALTER TABLE translations ADD COLUMN verse_count INTEGER; ALTER TABLE translations ADD COLUMN book_count SMALLINT;
        ALTER TABLE translations ADD COLUMN has_ot BOOLEAN; ALTER TABLE translations ADD COLUMN has_nt BOOLEAN;
        ALTER TABLE translations ADD COLUMN has_deuterocanon BOOLEAN; ALTER TABLE translations ADD COLUMN versification VARCHAR;
        ALTER TABLE translations ADD COLUMN unmatched_verses INTEGER;
        ALTER TABLE translations ADD COLUMN damaged_verses INTEGER; ALTER TABLE translations ADD COLUMN paragraph_marks BOOLEAN;
        UPDATE translations SET verse_count = s.n, book_count = s.nb, has_ot = s.ot > 0, has_nt = s.nt > 0, has_deuterocanon = s.dc > 0, unmatched_verses = s.um,
               damaged_verses = s.dmg, paragraph_marks = s.pil > 0
        FROM (SELECT translation_id, count(*) n, count(DISTINCT book_id) nb, count(*) FILTER (book_id <= 39) ot, count(*) FILTER (book_id BETWEEN 40 AND 66) nt,
                     count(*) FILTER (book_id > 66) dc, count(*) FILTER (book_id <= 66 AND verse_id IS NULL) um,
                     count(*) FILTER (text LIKE '%�%') dmg, count(*) FILTER (text LIKE '%¶%') pil
              FROM verse_text GROUP BY 1) s WHERE s.translation_id = translations.translation_id;
        UPDATE translations SET versification = s.vs FROM (
            SELECT translation_id,
                   CASE WHEN max(chapter) FILTER (book_id = 39) = 3 AND max(chapter) FILTER (book_id = 29) = 4 THEN 'Hebrew (Masoretic)'
                        WHEN count(*) FILTER (book_id = 19 AND chapter = 9) >= 38 THEN 'Greek/Latin (Septuagint–Vulgate Psalms)'
                        WHEN max(chapter) FILTER (book_id = 39) = 4 OR count(*) FILTER (book_id <= 39) = 0 THEN 'English (KJV)'
                        ELSE 'Mixed / other' END vs
            FROM verse_text GROUP BY 1) s WHERE s.translation_id = translations.translation_id""")

    # ---- licence classes (and the --open-only build) ------------------------------------
    con.execute(r"""
        ALTER TABLE translations ADD COLUMN license_class VARCHAR;
        UPDATE translations SET license_class = CASE
            WHEN license ILIKE '%public domain%' OR license ILIKE '%cc0%' THEN 'Public domain'
            WHEN regexp_matches(lower(license), '\bnc\b|non-commercial') THEN 'Non-commercial only'
            WHEN regexp_matches(lower(license), '\bnd\b') THEN 'No derivatives'
            WHEN license ILIKE '%gpl%' THEN 'Copyleft (GPL)'
            WHEN regexp_matches(lower(license), '\bsa\b') THEN 'Share-alike'
            WHEN license ILIKE '%copyright%' THEN 'Copyrighted, free distribution'
            WHEN license ILIKE '%by%' OR license ILIKE '%attribution%' THEN 'Attribution'
            ELSE 'Not stated' END""")
    if args.open_only:
        dropped = [r[0] for r in con.execute("""SELECT translation_id FROM translations
            WHERE license_class IN ('Non-commercial only', 'No derivatives', 'Copyrighted, free distribution', 'Not stated') ORDER BY 1""").fetchall()]
        con.execute("""DELETE FROM verse_text WHERE translation_id IN (SELECT translation_id FROM translations
            WHERE license_class IN ('Non-commercial only', 'No derivatives', 'Copyrighted, free distribution', 'Not stated'))""")
        con.execute("DELETE FROM translations WHERE translation_id IN (SELECT unnest(?))", [dropped])
        log(f"--open-only: left out {len(dropped)} restricted texts: {', '.join(dropped)}")

    # ---- eBible catalogue & provenance ---------------------------------------------
    con.execute(f"""CREATE TABLE ebible_catalog AS SELECT translationId AS ebible_id, languageCode AS language_code, languageNameInEnglish AS language,
        title, shortTitle AS short_title, description, Redistributable::BOOLEAN AS redistributable, Copyright AS copyright,
        OTbooks::INT AS ot_books, NTbooks::INT AS nt_books, DCbooks::INT AS dc_books, OTverses::INT AS ot_verses, NTverses::INT AS nt_verses,
        UpdateDate AS updated, 'https://ebible.org/' || translationId || '/' AS url,
        translationId IN ('engwebp', 'eng-kjv2006', 'grclxx', {', '.join(repr(t['ebible']) for t in EBIBLE_ENGLISH)}) AS imported
        FROM read_csv('{(RAW / 'ebible_translations.csv').as_posix()}', header=true, all_varchar=true)""")
    con.execute("CREATE TABLE data_sources (dataset VARCHAR, provider VARCHAR, url VARCHAR, license VARCHAR, used_for VARCHAR, retrieved DATE)")
    today = date.today().isoformat()
    con.executemany("INSERT INTO data_sources VALUES (?,?,?,?,?,?)", [
        ("Bible texts in 137 translations", "scrollmapper/bible_databases", "https://github.com/scrollmapper/bible_databases", "MIT (repository); each translation has its own licence — see translations.license", "verse_text, translations", today),
        ("World English Bible, KJV with Strong's tags and words of Jesus, Septuagint", "eBible.org", "https://ebible.org/", "Public domain", "verse_text (WEB, KJV, LXX), translation_words (KJV, WEB), speech_spans (Jesus)", today),
        ("Words of God (detected)", "Computed for this database (red_letter.py) from WEB quotation punctuation", None, "Heuristic output", "speech_spans (God), verses.words_of_god_detected", today),
        ("Repeated phrases", "Computed for this database (phrases.py) from TAHOT, TAGNT and the Septuagint", None, "Derived data", "phrase_length_stats, phrase_repeats, phrase_occurrences", today),
        ("eBible.org translation catalogue", "eBible.org", "https://ebible.org/Scriptures/translations.csv", "Catalogue data", "ebible_catalog", today),
        ("TAHOT & TAGNT tagged Hebrew/Aramaic OT and Greek NT", "STEPBible.org / Tyndale House Cambridge", "https://github.com/STEPBible/STEPBible-Data", "CC BY 4.0", "original_words, verse_text (TAHOT, TAGNT), verse_strongs", today),
        ("TBESH & TBESG brief lexicons of extended Strong's", "STEPBible.org / Tyndale House Cambridge", "https://github.com/STEPBible/STEPBible-Data", "CC BY 4.0", "lexicon_extended", today),
        ("Strong's Hebrew and Greek dictionaries (1890/1894)", "Open Scriptures", "https://github.com/openscriptures/strongs", "Text public domain; JSON edition CC BY-SA", "strongs", today),
        ("Berean Standard Bible interlinear tables", "Berean Bible / bereanbible.com", "https://bereanbible.com/bsb_tables.xlsx", "Public domain (BSB dedicated to the public domain, 2023)", "translation_words (BSB)", today),
        ("Bible cross-references (Treasury of Scripture Knowledge based)", "OpenBible.info", "https://www.openbible.info/labs/cross-references/", "CC BY 4.0", "cross_references", today),
        ("Authorship, dating and place of writing", "Compiled for this database from the works in scholarly_sources", None, "Summaries; cite the underlying works", "book_authorship, book_dating, places, scholarly_sources", today),
    ])

    # ---- views ------------------------------------------------------------------
    con.execute("""
    CREATE VIEW v_passage AS
        SELECT v.verse_id, v.reference, v.osis_ref, t.translation_id, t.title AS translation, t.language, vt.text
        FROM verse_text vt JOIN verses v USING (verse_id) JOIN translations t USING (translation_id);
    CREATE VIEW v_interlinear AS
        SELECT v.reference, w.verse_id, w.word_pos, w.language, w.text, w.transliteration, w.english, w.strongs, w.strongs_extended, w.morphology,
               s.lemma AS strongs_lemma, s.definition AS strongs_definition, s.kjv_usage
        FROM original_words w LEFT JOIN verses v USING (verse_id) LEFT JOIN strongs s ON s.strongs_id = w.strongs;
    CREATE VIEW v_strongs_renderings AS
        SELECT strongs, translation_id, lower(word) AS rendering, count(*) AS occurrences
        FROM translation_words WHERE strongs IS NOT NULL AND word IS NOT NULL GROUP BY ALL;
    CREATE VIEW v_strongs_usage AS
        SELECT s.strongs_id, s.language, s.lemma, s.transliteration, s.definition,
               (SELECT count(*) FROM original_words w WHERE w.strongs = s.strongs_id) AS original_occurrences,
               (SELECT count(DISTINCT verse_id) FROM verse_strongs vs WHERE vs.strongs = s.strongs_id) AS verses
        FROM strongs s;
    CREATE VIEW v_book_authorship AS
        SELECT b.name AS book, a.view, a.section, a.author, a.date_display, a.date_from, a.date_to, a.place_display, p.latitude, p.longitude, a.held_by,
               d.consensus,
               (SELECT string_agg(ss.author || ', ' || ss.title || coalesce(' ' || x.locator, ''), '; ')
                  FROM book_authorship_sources x JOIN scholarly_sources ss USING (source_id) WHERE x.authorship_id = a.authorship_id) AS sources
        FROM book_authorship a JOIN books b USING (book_id) JOIN book_dating d USING (book_id) LEFT JOIN places p USING (place_id)
        ORDER BY a.book_id, a.authorship_id;
    """)

    # ---- documentation ------------------------------------------------------------
    DOCS = {
        "books": ("The 66 books of the Protestant canon (book_id 1–66) plus deuterocanonical/apocryphal books found in some translations (67+).", {
            "book_id": "Canonical order; 1 = Genesis, 66 = Revelation; 67+ = books outside the Protestant canon", "osis": "OSIS abbreviation (Gen, 1Sam, Rev…)",
            "testament": "OT, NT, or Deuterocanon / Apocrypha", "genre": "Category: Law, History, Wisdom / Poetry, Major Prophets, Minor Prophets, Gospels, Early Church History, Paul's Letters, General Letters, Prophecy",
            "original_language": "Language(s) the book was written in", "usfm_code": "Three-letter USFM book code", "source_name": "Book name used by scrollmapper",
            "chapters": "Number of chapters (KJV versification)", "verses": "Number of verses (KJV versification)"}),
        "verses": ("Canonical verse list in KJV (English) versification: 31,102 verses. verse_id is the key used by every other table.", {
            "verse_id": "1 = Genesis 1:1 … 31102 = Revelation 22:21", "osis_ref": "OSIS reference, e.g. John.3.16", "reference": "Readable reference, e.g. John 3:16",
            "words_of_jesus": "Red letter: the verse contains words of Jesus, from the red-letter markup (\\wj) in the eBible.org WEB/KJV editions — the standard editorial marking",
            "words_of_god_detected": "Dark red: the verse contains words spoken by God, DETECTED from quotation marks and speech formulas in the WEB (see speech_spans.method). Heuristic — not an editorial marking",
            "god_detection_method": "quotation heuristic (explicit attribution such as “God said”, “Thus says the LORD”) or dialogue heuristic (“He said” answering a person who replied to God)",
            "red_letter": "Summary: Jesus | God (detected) | Jesus + God (detected) | NULL"}),
        "translations": ("Every text in verse_text: modern translations, ancient versions (Septuagint, Vulgate, Peshitta…) and original-language texts.", {
            "translation_id": "Short code used in verse_text / translation_words", "category": "Translation, Ancient version, or Original-language text",
            "year": "Year taken from the title when it contains one", "license": "Licence as stated by the source", "has_strongs": "True when word-level Strong's numbers exist in translation_words or original_words",
            "strongs_source": "Where the Strong's tagging comes from",
            "license_class": "Public domain | Attribution | Share-alike | Copyleft (GPL) | No derivatives | Non-commercial only | Copyrighted, free distribution | Not stated. Build with --open-only to leave out the restrictive classes", "versification": "Verse-numbering system detected from the data (English/KJV, Hebrew/Masoretic, Greek/Latin Psalms)",
            "unmatched_verses": "Verses in books 1–66 whose number does not exist in KJV versification (verse_id is NULL for them)",
            "damaged_verses": "Verses containing the replacement character (U+FFFD) — characters already lost in the source file and not recoverable",
            "paragraph_marks": "True when the text keeps the pilcrow (¶) paragraph marks of its printed edition (common in KJV-family texts)"}),
        "verse_text": ("One row per verse per translation (≈4.8 million rows).", {
            "verse_id": "Joins to verses when the book/chapter/verse numbers exist in KJV versification. Hebrew- or Septuagint-numbered texts can align to a neighbouring verse in some chapters (see translations.versification)",
            "book_id": "Joins to books (67+ for deuterocanonical books)", "text": "Verse text as published by the source"}),
        "original_words": ("Every word of the Hebrew/Aramaic Old Testament (TAHOT) and Greek New Testament (TAGNT), tagged with Strong's numbers, morphology and glosses.", {
            "source": "TAHOT (Hebrew/Aramaic OT) or TAGNT (Greek NT)", "verse_id": "English (KJV) versification verse; the Hebrew/Greek reference is kept in source_ref",
            "word_pos": "Word position within the verse", "word_type": "STEPBible word type: L = Leningrad text; Q/K = qere/ketiv; for Greek, letters show which editions have the word (N = Nestle-Aland, K = KJV/TR, O = other)",
            "language": "Hebrew, Aramaic or Greek (Aramaic from the morphology code)", "text": "Word as written (Hebrew with vowels and accents; Greek with accents)",
            "segmented": "Hebrew word split into prefixes/suffixes with '/'", "english": "STEPBible's English translation of the word",
            "strongs": "Strong's number normalised to H0000/G0000 (joins strongs.strongs_id)", "strongs_extended": "STEPBible extended Strong's (e.g. H0430G), joins lexicon_extended.extended_id",
            "all_strongs": "All Strong's tags on the word, including prefix codes H9001–H9016", "morphology": "Morphology/parsing code (TAHOT: OSHB codes starting H or A; TAGNT: Robinson-style codes)",
            "lemma": "Dictionary form", "gloss": "Short English gloss", "editions": "Greek editions containing the word (NA28, SBL, TR, Byz…)", "source_ref": "Original STEPBible reference"}),
        "translation_words": ("English words tagged with Strong's numbers: KJV and WEB (eBible.org word tags) and BSB (Berean interlinear). The link from each Strong's number into translations.", {
            "translation_id": "KJV, WEB or BSB", "word_seq": "Order within the verse (KJV/WEB: tagged words; BSB: English word order)", "word": "The English word or phrase",
            "strongs": "Strong's number (H0000/G0000)", "original_text": "BSB only: the Hebrew/Greek word it renders", "transliteration": "BSB only", "parsing": "BSB only: parsing description",
            "language": "Hebrew, Aramaic or Greek", "start_char": "KJV/WEB: character offset of the word in verse_text.text", "end_char": "KJV/WEB: end offset (exclusive)",
            "red_letter": "KJV/WEB: Jesus or God when the word lies inside a speech_spans range"}),
        "speech_spans": ("Red letters at character level in the WEB and KJV: where Jesus speaks (red) and where God speaks (dark red). Offsets index verse_text.text for the same translation.", {
            "speaker": "Jesus or God", "method": "red-letter markup (Jesus; exact editorial marking) | quotation heuristic | dialogue heuristic | aligned from WEB (…) — how the span was found",
            "start_char": "Offset of the first character", "end_char": "Offset after the last character", "text": "The spoken words"}),
        "phrase_length_stats": ("Repeated-phrase chunk counts: for each length (7 words and up) how many distinct word sequences occur at least twice, and at how many places. Counts every run, including runs inside longer repeats.", {
            "corpus": "ot = Hebrew & Aramaic OT (TAHOT); nt = Greek NT (TAGNT); gk = Septuagint OT + Greek NT together (finds NT quotations of the Septuagint)",
            "match_mode": "exact = same words ignoring vowel points/accents/case/punctuation; lemma = same Strong's numbers (different inflections match)",
            "length_words": "Phrase length in original-language words", "distinct_phrases": "Distinct sequences of this length that repeat", "occurrences": "Places where those sequences occur"}),
        "phrase_repeats": ("Repeated phrases of 7+ original-language words, each listed once at its full length (a 20-word repeat is not listed again as its shorter sub-runs; a shorter part that repeats in extra places gets its own row).", {
            "length_words": "Number of words in the phrase", "occurrence_count": "Number of places it occurs", "book_count": "Number of different books it occurs in",
            "phrase_text": "The phrase as written at its first occurrence", "phrase_gloss": "Word-by-word English gloss (STEPBible), OT/NT corpora only",
            "phrase_transliteration": "The phrase in Latin letters, word for word (STEPBible transliteration; Septuagint words romanized by phrases.translit_greek)"}),
        "phrase_occurrences": ("Every place each repeated phrase occurs.", {
            "reference": "Readable range, e.g. Psalms 18:3–4", "start_verse_id": "Joins verses (NULL for Septuagint verses outside KJV numbering or books)", "text": "The phrase as written at this place",
            "transliteration": "Space-separated transliteration, one entry per word of text", "strongs": "Space-separated Strong's numbers, one per word of text (- when untagged, e.g. Septuagint)"}),
        "verse_strongs": ("Which Strong's numbers occur in each verse (from original_words). Join on verse_id to find a word's verses in ANY translation.", {}),
        "strongs": ("James Strong's Hebrew (1894) and Greek (1890) dictionaries.", {
            "strongs_id": "H0001–H8674, G0001–G5624", "language": "Hebrew, Aramaic (Hebrew-dictionary entries marked Aramaic/Chaldee) or Greek",
            "definition": "Strong's definition", "kjv_usage": "How the KJV renders the word", "derivation": "Strong's note on the word's origin"}),
        "lexicon_extended": ("STEPBible brief lexicons (TBESH/TBESG): extended Strong's numbers that split homonyms and names, with modern glosses and definitions.", {
            "extended_id": "Extended Strong's (e.g. H0430G)", "strongs_id": "Plain Strong's number", "relation": "How the extended number relates to the plain one",
            "definition_html": "Definition (HTML markup from the source; Greek definitions abridged from Abbott-Smith)"}),
        "cross_references": ("OpenBible.info cross-references (≈344,800), mainly from the Treasury of Scripture Knowledge. Same data as the Reference Rainbow.", {
            "from_verse_id": "Verse the reference is listed under", "to_verse_start_id": "First verse of the referenced passage", "to_verse_end_id": "Last verse (same as start for single verses)",
            "votes": "OpenBible.info relevance votes (can be negative)"}),
        "book_authorship": ("Who wrote each book, when and where — one row per view (traditional, critical, consensus, alternative), with sources in book_authorship_sources.", {
            "view": "consensus | traditional | critical | alternative", "section": "Part of the book the row covers, when views differ by section (e.g. Isaiah 40–55)",
            "date_from": "Earliest year (negative = BC)", "date_to": "Latest year (negative = BC)", "date_display": "Date as it should be read", "held_by": "Who holds this view",
            "place_id": "Joins places (coordinates)"}),
        "book_authorship_sources": ("Citations for each authorship view. Ancient sources carry passage locators.", {"locator": "Book.chapter.section or folio in the cited work"}),
        "book_dating": ("One row per book: how settled the question is and a representative year for each dating tradition (midpoint of its range). Used for the Rainbow's 'Years apart' colouring.", {
            "consensus": "broad | divided | open", "traditional_year": "Midpoint year under traditional dating", "critical_year": "Midpoint year under critical dating"}),
        "scholarly_sources": ("Ancient and modern works cited in book_authorship_sources.", {}),
        "places": ("Places of writing with approximate coordinates.", {"precision": "site = a specific city/site; region = approximate centre of a region"}),
        "ebible_catalog": ("eBible.org's catalogue of 1,500+ Bible translations and their licences — documents what else is available beyond the imported texts.", {
            "imported": "True when the text is imported into verse_text"}),
        "data_sources": ("Where every dataset in this database came from, and its licence.", {}),
    }
    for t, (tc, cc) in DOCS.items():
        con.execute(f"COMMENT ON TABLE {t} IS '{tc.replace(chr(39), chr(39) * 2)}'")
        for c, txt in cc.items():
            con.execute(f"COMMENT ON COLUMN {t}.{c} IS '{txt.replace(chr(39), chr(39) * 2)}'")
    VDOCS = {"v_passage": "Verse text joined with references and translation names — filter by osis_ref or reference.",
             "v_interlinear": "Original-language words with Strong's lemma, definition and KJV usage.",
             "v_strongs_renderings": "How KJV, WEB and BSB render each Strong's number, with counts.",
             "v_strongs_usage": "Occurrence counts for each Strong's number (slow over all rows; filter by strongs_id).",
             "v_book_authorship": "Readable authorship/dating/place table with sources joined in."}
    for vname, txt in VDOCS.items():
        con.execute(f"COMMENT ON VIEW {vname} IS '{txt.replace(chr(39), chr(39) * 2)}'")

    con.execute("CHECKPOINT")
    con.close()
    size = DB.stat().st_size / 1e6
    log(f"done: {DB.name} {size:,.0f} MB")


if __name__ == "__main__":
    main()

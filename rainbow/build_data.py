"""Build compact data for the Reference Rainbow page.

Inputs (downloaded):
  cross_references.txt  - OpenBible.info cross references (CC BY 4.0)
  t_kjv.csv             - KJV text, scrollmapper/bible_databases (public domain)

  ../bibledb/book_origins.py - authorship, dating and place of writing (with sources)

Output: data.js defining window.RAINBOW_DATA with gzip+base64 columnar arrays.

    python build_data.py                      # reads ../bibledb/raw (run ../bibledb/download.py first)
    python build_data.py <src_dir> <out.js>
"""
import base64, csv, gzip, json, sys
from array import array
from pathlib import Path

from buildutil import write_text

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "bibledb"))
import book_origins as BO  # noqa: E402

src = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "bibledb" / "raw"
out = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "data.js"
xref_file = next(p for p in [src / "cross_references.txt", src / "cross_references" / "cross_references.txt"] if p.exists())

BOOKS = [
    ("Gen", "Genesis"), ("Exod", "Exodus"), ("Lev", "Leviticus"), ("Num", "Numbers"),
    ("Deut", "Deuteronomy"), ("Josh", "Joshua"), ("Judg", "Judges"), ("Ruth", "Ruth"),
    ("1Sam", "1 Samuel"), ("2Sam", "2 Samuel"), ("1Kgs", "1 Kings"), ("2Kgs", "2 Kings"),
    ("1Chr", "1 Chronicles"), ("2Chr", "2 Chronicles"), ("Ezra", "Ezra"), ("Neh", "Nehemiah"),
    ("Esth", "Esther"), ("Job", "Job"), ("Ps", "Psalms"), ("Prov", "Proverbs"),
    ("Eccl", "Ecclesiastes"), ("Song", "Song of Solomon"), ("Isa", "Isaiah"), ("Jer", "Jeremiah"),
    ("Lam", "Lamentations"), ("Ezek", "Ezekiel"), ("Dan", "Daniel"), ("Hos", "Hosea"),
    ("Joel", "Joel"), ("Amos", "Amos"), ("Obad", "Obadiah"), ("Jonah", "Jonah"),
    ("Mic", "Micah"), ("Nah", "Nahum"), ("Hab", "Habakkuk"), ("Zeph", "Zephaniah"),
    ("Hag", "Haggai"), ("Zech", "Zechariah"), ("Mal", "Malachi"),
    ("Matt", "Matthew"), ("Mark", "Mark"), ("Luke", "Luke"), ("John", "John"),
    ("Acts", "Acts"), ("Rom", "Romans"), ("1Cor", "1 Corinthians"), ("2Cor", "2 Corinthians"),
    ("Gal", "Galatians"), ("Eph", "Ephesians"), ("Phil", "Philippians"), ("Col", "Colossians"),
    ("1Thess", "1 Thessalonians"), ("2Thess", "2 Thessalonians"), ("1Tim", "1 Timothy"),
    ("2Tim", "2 Timothy"), ("Titus", "Titus"), ("Phlm", "Philemon"), ("Heb", "Hebrews"),
    ("Jas", "James"), ("1Pet", "1 Peter"), ("2Pet", "2 Peter"), ("1John", "1 John"),
    ("2John", "2 John"), ("3John", "3 John"), ("Jude", "Jude"), ("Rev", "Revelation"),
]
OSIS = {abbr: i for i, (abbr, _) in enumerate(BOOKS)}

# --- verse structure + text from KJV ---------------------------------------
verses = {}  # (book, chap) -> max verse
texts = []
with open(src / "t_kjv.csv", newline="", encoding="utf-8") as f:
    rows = sorted(csv.DictReader(f), key=lambda r: int(r["id"]))
rows = [r for r in rows if r["t"].strip() not in ("", "[]")]  # e.g. empty placeholder 3 John 1:15
for r in rows:
    b, c, v = int(r["b"]) - 1, int(r["c"]), int(r["v"])
    verses[(b, c)] = max(verses.get((b, c), 0), v)
    texts.append(r["t"].strip().replace("\n", " "))

chapters = []  # per book list of verse counts
for b in range(66):
    counts, c = [], 1
    while (b, c) in verses:
        counts.append(verses[(b, c)])
        c += 1
    chapters.append(counts)

n_ch = sum(len(c) for c in chapters)
n_vs = sum(sum(c) for c in chapters)
assert n_ch == 1189 and n_vs == 31102 == len(texts), (n_ch, n_vs, len(texts))

offset = {}  # (book, chap) -> global verse index of verse 1
g = 0
for b, counts in enumerate(chapters):
    for c, n in enumerate(counts, 1):
        offset[(b, c)] = g
        g += n

clamped = 0
def gid(tok):
    global clamped
    book, chap, verse = tok.split(".")
    b, c, v = OSIS[book], int(chap), int(verse)
    if c > len(chapters[b]):  # versification differences (e.g. Mal 4 / Joel 3)
        c = len(chapters[b]); clamped += 1
    n = chapters[b][c - 1]
    if v > n:
        v = n; clamped += 1
    return offset[(b, c)] + v - 1

# --- cross references ------------------------------------------------------
refs = []
with open(xref_file, encoding="utf-8") as f:
    next(f)
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 3:
            continue
        a, to, votes = parts[0], parts[1], int(parts[2])
        s, _, e = to.partition("-")
        fa, ts = gid(a), gid(s)
        te = gid(e) if e else ts
        if te < ts:
            te = ts
        refs.append((fa, ts, te, votes))

refs.sort()
N = len(refs)
from_delta = array("H")
to_diff = array("h")
span = array("H")
votes = array("h")
prev = 0
for fa, ts, te, v in refs:
    from_delta.append(fa - prev); prev = fa
    to_diff.append(ts - fa)
    span.append(min(te - ts, 65535))
    votes.append(max(-32768, min(32767, v)))

def pack(arr):
    if sys.byteorder != "little":
        arr.byteswap()
    return base64.b64encode(gzip.compress(arr.tobytes(), 9, mtime=0)).decode()

# --- red letters: eBible.org KJV text with words of Jesus (markup) and of God (detected) ----------
import red_letter  # noqa: E402
from build import CANON  # noqa: E402

RED_KIND = {"red-letter markup": 1, "quotation heuristic": 2, "dialogue heuristic": 3}
red = red_letter.build(HERE.parent / "bibledb" / "raw")["KJV"]
sp_gid, sp_start, sp_end, sp_kind = array("H"), array("H"), array("H"), array("B")
replaced = 0
for b, (_, _, _, usfm, _) in enumerate(CANON):
    for c, n in enumerate(chapters[b], 1):
        for v in range(1, n + 1):
            d = red.get((usfm, c, v))
            if not d:
                continue
            g = offset[(b, c)] + v - 1
            texts[g] = d["text"]
            replaced += 1
            for s, e, speaker, method in d["spans"]:
                kind = 1 if speaker == "Jesus" else (3 if "dialogue" in method else 2)
                sp_gid.append(g); sp_start.append(s); sp_end.append(e); sp_kind.append(kind)
print(f"KJV text from eBible for {replaced} verses; {len(sp_gid)} red-letter spans")

text_blob = base64.b64encode(gzip.compress("\n".join(texts).encode("utf-8"), 9, mtime=0)).decode()

data = {
    "books": [{"osis": a, "name": n, "chapters": chapters[i]} for i, (a, n) in enumerate(BOOKS)],
    "count": N,
    "fromDelta": pack(from_delta),
    "toDiff": pack(to_diff),
    "span": pack(span),
    "votes": pack(votes),
    "text": text_blob,
    "red": {"gid": pack(sp_gid), "start": pack(sp_start), "end": pack(sp_end), "kind": pack(sp_kind), "count": len(sp_gid)},
    "origins": [dict(
        consensus=BO.ORIGINS[a]["consensus"],
        trad=BO.representative_year(a, "traditional"),
        crit=BO.representative_year(a, "critical"),
        views=[dict(view=w["view"], section=w["section"], author=w["author"], date=w["date_display"],
                    place=w["place_display"], held=w["held_by"], src=[[s, loc] for s, loc in w["sources"]])
               for w in BO.ORIGINS[a]["views"]],
    ) for a, _ in BOOKS],
    "sources": {k: f"{s['author']}, {s['title']} ({s['date']})" for k, s in BO.SOURCES.items()},
}
write_text(out, "window.RAINBOW_DATA=" + json.dumps(data, separators=(",", ":")) + ";\n")
vs = sorted(v for *_, v in refs)
print(f"refs={N} clamped={clamped} votes min={vs[0]} median={vs[N//2]} max={vs[-1]}")
for t in (0, 1, 5, 10, 20, 30, 50):
    print(f"  votes>={t}: {sum(1 for v in vs if v >= t)}")
print(f"data.js {out.stat().st_size/1e6:.2f} MB")

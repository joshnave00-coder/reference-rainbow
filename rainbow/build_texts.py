"""Export the English translations offered in the Rainbow and Echoes from ../bibledb/bible.duckdb.

    python build_texts.py      # writes texts/manifest.js and texts/<ID>.js (run ../bibledb/build.py first)

Only translations that may be freely shared (public domain, CC0, CC BY, CC BY-SA) are exported, because these
files ship with the project. The King James Version is already inside data.js, so it gets no separate file.
Verses are placed by King James chapter and verse numbers; a verse a translation doesn't have is an empty line.
"""
import base64, gzip, json, re, sys
from array import array
from pathlib import Path

from buildutil import write_text

import duckdb

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "bibledb"))
from english_texts import EBIBLE_ENGLISH  # noqa: E402

DB = HERE.parent / "bibledb" / "bible.duckdb"
OUT = HERE / "texts"
NV, OT_VERSES = 31102, 23145
OPEN_CLASSES = {"Public domain", "Attribution", "Share-alike"}

VULGATE = "Psalms and a few other chapters are numbered as in the Latin Vulgate, so some verses there sit one number away from the KJV."
# (group, id, name shown, one-line description, extra note)
CURATED = [
    ("Modern English", "BSB", "Berean Standard Bible", "A modern, readable translation made directly from the Hebrew and Greek (2016–2023).", None),
    ("Modern English", "WEB", "World English Bible", "A modern update of the 1901 American Standard Version. Words of Jesus in red.", None),
    ("Modern English", "WEBU", "World English Bible Updated", "A later revision of the World English Bible.", None),
    ("Modern English", "MSB", "Majority Standard Bible", "The Berean Standard Bible, following the Majority Text in the New Testament.", None),
    ("Modern English", "NHEB", "New Heart English Bible", "A modern public-domain revision of the World English Bible.", None),
    ("Modern English", "LSV", "Literal Standard Version", "A modern, word-for-word literal translation (2020).", None),
    ("Modern English", "FBV", "Free Bible Version", "Contemporary, easy-to-read English (2018).", None),
    ("Modern English", "T4T", "Translation for Translators", "Very plain English that spells out meaning the original leaves implied.", None),
    ("Modern English", "ULB", "Unlocked Literal Bible", "A literal, open update of the American Standard Version (2017).", None),
    ("Modern English", "BBE", "Bible in Basic English", "Written with a vocabulary of about 1,000 everyday words (1949/1964).", None),
    ("Modern English", "OEB", "Open English Bible", "Modern English; a work in progress, so many books are not yet included.", None),
    ("Modern English", "TCENT", "Text-Critical English New Testament", "A modern New Testament following the Byzantine Greek text (2022).", None),
    ("King James tradition", "KJV", "King James Version", "The Authorized Version of 1611 (1769 text). Words of Jesus in red.", None),
    ("King James tradition", "KJVPCE", "King James Version, Pure Cambridge Edition", "The Cambridge text of the KJV as printed around 1900.", None),
    ("King James tradition", "UKJV", "Updated King James Version", "The KJV with old words and grammar brought up to date.", None),
    ("King James tradition", "Webster", "Webster Bible", "Noah Webster's 1833 revision of the KJV.", None),
    ("King James tradition", "RNKJV", "Restored Name King James Version", "The KJV using Hebrew names for God.", None),
    ("King James tradition", "ACV", "A Conservative Version", "A close, conservative update of the KJV's wording.", None),
    ("Classic English", "ASV", "American Standard Version (1901)", "The American edition of the Revised Version, known for its literal style.", None),
    ("Classic English", "RV", "Revised Version (1881–1885)", "The first official revision of the KJV, made in Britain.", None),
    ("Classic English", "YLT", "Young's Literal Translation", "Robert Young's very literal translation (1898).", None),
    ("Classic English", "Darby", "Darby Bible", "John Nelson Darby's literal translation (1890).", None),
    ("Classic English", "Rotherham", "Rotherham's Emphasized Bible", "J. B. Rotherham's literal translation marking emphasis (1902).", None),
    ("Historic English", "Geneva1599", "Geneva Bible (1599)", "The Bible of Shakespeare, the Puritans and the Mayflower.", None),
    ("Historic English", "Tyndale", "Tyndale Bible (1525–1530)", "William Tyndale's pioneering translation; he completed only part of the Old Testament.", None),
    ("Historic English", "Wycliffe", "Wycliffe Bible (c. 1395)", "The first complete English Bible, in Middle English, translated from the Latin.", VULGATE),
    ("Jewish and Messianic", "JPS", "JPS Tanakh (1917)", "The Jewish Publication Society's translation of the Hebrew Bible.", "A few chapters follow Hebrew verse numbering, so some verses there sit one number away from the KJV."),
    ("Jewish and Messianic", "OJB", "Orthodox Jewish Bible", "Hebrew Bible and New Testament in English with many Hebrew and Yiddish terms.", None),
    ("Jewish and Messianic", "WMB", "World Messianic Bible", "The World English Bible using Hebrew names and terms.", None),
]
ATTRIBUTION = {t["id"]: t["attribution"] for t in EBIBLE_ENGLISH}
SHORT = {"Geneva1599": "Geneva", "Rotherham": "Rotherham", "Webster": "Webster", "Darby": "Darby", "Tyndale": "Tyndale", "Wycliffe": "Wycliffe"}


def pack(arr):
    if sys.byteorder != "little":
        arr.byteswap()
    return base64.b64encode(gzip.compress(arr.tobytes(), 9, mtime=0)).decode()


def clean(text):
    text = (text or "").replace("¶", " ")
    return re.sub(r"\s+", " ", text).strip()


def main():
    con = duckdb.connect(str(DB), read_only=True)
    OUT.mkdir(exist_ok=True)
    meta = {r[0]: r for r in con.execute("SELECT translation_id, title, license, license_class, source_url FROM translations").fetchall()}
    manifest, written, total = [], set(), 0
    for group, tid, name, blurb, note in CURATED:
        if tid not in meta:
            print(f"  {tid}: not in the database, skipped")
            continue
        _, title, license_, lclass, url = meta[tid]
        if lclass not in OPEN_CLASSES:
            print(f"  {tid}: licence '{license_}' is not open, skipped")
            continue
        lines = [""] * NV
        for verse_id, text in con.execute("SELECT verse_id, text FROM verse_text WHERE translation_id = ? AND verse_id IS NOT NULL", [tid]).fetchall():
            lines[verse_id - 1] = clean(text)
        ot = sum(1 for g in range(OT_VERSES) if lines[g])
        nt = sum(1 for g in range(OT_VERSES, NV) if lines[g])
        if ot > 0.9 * OT_VERSES and nt > 0.9 * (NV - OT_VERSES):
            coverage = "Old and New Testaments"
        elif ot > 0.9 * OT_VERSES and nt == 0:
            coverage = "Old Testament only"
        elif nt > 0.9 * (NV - OT_VERSES) and ot == 0:
            coverage = "New Testament only"
        else:
            coverage = f"partial, {round((ot + nt) / NV * 100)}% of verses"
        red = None
        if tid == "WEB":
            gid, st, en, kind = array("H"), array("H"), array("H"), array("B")
            for vi, s0, e0, speaker, method in con.execute(
                    "SELECT verse_id, start_char, end_char, speaker, method FROM speech_spans WHERE translation_id = 'WEB' AND verse_id IS NOT NULL ORDER BY verse_id, start_char").fetchall():
                gid.append(vi - 1); st.append(s0); en.append(e0); kind.append(1 if speaker == "Jesus" else (3 if "dialogue" in method else 2))
            red = {"gid": pack(gid), "start": pack(st), "end": pack(en), "kind": pack(kind), "count": len(gid)}
        entry = dict(id=tid, name=name, short=SHORT.get(tid, tid), group=group, blurb=blurb, note=note, coverage=coverage,
                     license={"Public domain": "Public domain", "Attribution": "CC BY", "Share-alike": "CC BY-SA"}[lclass] + ("" if lclass == "Public domain" else f" ({license_})"),
                     attribution=ATTRIBUTION.get(tid) or title, url=url, red=tid in ("KJV", "WEB"), builtin=tid == "KJV")
        manifest.append(entry)
        if tid == "KJV":
            continue  # already in data.js
        payload = {"text": base64.b64encode(gzip.compress("\n".join(lines).encode("utf-8"), 9, mtime=0)).decode(), "red": red}
        path = OUT / f"{tid}.js"
        write_text(path, f"(window.RAINBOW_TEXTS = window.RAINBOW_TEXTS || {{}})[{json.dumps(tid)}] = " + json.dumps(payload) + ";\n")
        written.add(path.name)
        total += path.stat().st_size
        print(f"  {tid:<10} {coverage:<26} {path.stat().st_size / 1e6:.2f} MB")
    for old in OUT.glob("*.js"):
        if old.name not in written and old.name != "manifest.js":
            old.unlink()
    write_text((OUT / "manifest.js"), "window.RAINBOW_TRANSLATIONS = " + json.dumps(manifest, ensure_ascii=False, indent=1) + ";\n")
    print(f"{len(manifest)} translations ({len(written)} files, {total / 1e6:.1f} MB) + manifest.js")


if __name__ == "__main__":
    main()

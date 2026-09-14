"""Fetch every raw source used to build bible.duckdb into bibledb/raw/.

Safe to re-run: files that already exist are skipped. Run:  python download.py
"""
import json, sys, urllib.parse, urllib.request, zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from english_texts import EBIBLE_ENGLISH  # noqa: E402

RAW = Path(__file__).resolve().parent / "raw"
UA = {"User-Agent": "bibledb-builder/1.0"}

STEP = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/master/"
STEP_FILES = [
    "Translators Amalgamated OT+NT/TAHOT Gen-Deu - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt",
    "Translators Amalgamated OT+NT/TAHOT Jos-Est - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt",
    "Translators Amalgamated OT+NT/TAHOT Job-Sng - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt",
    "Translators Amalgamated OT+NT/TAHOT Isa-Mal - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt",
    "Translators Amalgamated OT+NT/TAGNT Mat-Jhn - Translators Amalgamated Greek NT - STEPBible.org CC-BY.txt",
    "Translators Amalgamated OT+NT/TAGNT Act-Rev - Translators Amalgamated Greek NT - STEPBible.org CC-BY.txt",
    "Lexicons/TBESH - Translators Brief lexicon of Extended Strongs for Hebrew - STEPBible.org CC BY.txt",
    "Lexicons/TBESG - Translators Brief lexicon of Extended Strongs for Greek - STEPBible.org CC BY.txt",
]
SCROLL = "https://raw.githubusercontent.com/scrollmapper/bible_databases/master/"

SINGLE = {
    "cross_references.zip": "https://a.openbible.info/data/cross-references.zip",
    "kjv_usfm.zip": "https://ebible.org/Scriptures/eng-kjv2006_usfm.zip",
    "web_usfm.zip": "https://ebible.org/Scriptures/engwebp_usfm.zip",
    "lxx_usfm.zip": "https://ebible.org/Scriptures/grclxx_usfm.zip",
    "ebible_translations.csv": "https://ebible.org/Scriptures/translations.csv",
    "t_kjv.csv": "https://raw.githubusercontent.com/scrollmapper/bible_databases/2024/csv/t_kjv.csv",
    "strongs-hebrew-dictionary.js": "https://raw.githubusercontent.com/openscriptures/strongs/master/hebrew/strongs-hebrew-dictionary.js",
    "strongs-greek-dictionary.js": "https://raw.githubusercontent.com/openscriptures/strongs/master/greek/strongs-greek-dictionary.js",
    "bsb_tables.xlsx": "https://bereanbible.com/bsb_tables.xlsx",
    "scrollmapper_tree.json": "https://api.github.com/repos/scrollmapper/bible_databases/git/trees/master?recursive=1",
}


def fetch(url, dest: Path):
    if dest.exists() and dest.stat().st_size > 0:
        return f"skip  {dest.name}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=300) as r, open(str(dest) + ".part", "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    Path(str(dest) + ".part").replace(dest)
    return f"got   {dest.name} ({dest.stat().st_size/1e6:.1f} MB)"


def main():
    import argparse
    import shutil
    ap = argparse.ArgumentParser(description="Fetch the raw sources for bible.duckdb into bibledb/raw.")
    ap.add_argument("--refresh", action="store_true",
                    help="re-download the files that change over time: OpenBible.info cross-references (vote counts) and eBible.org's catalogue")
    args = ap.parse_args()
    RAW.mkdir(exist_ok=True)
    if args.refresh:
        for name in ("cross_references.zip", "ebible_translations.csv"):
            (RAW / name).unlink(missing_ok=True)
        shutil.rmtree(RAW / "cross_references", ignore_errors=True)
        print("refreshing cross-references and the eBible.org catalogue")
    jobs = [(u, RAW / n) for n, u in SINGLE.items()]
    jobs += [(STEP + urllib.parse.quote(f), RAW / "stepbible" / Path(f).name) for f in STEP_FILES]
    with ThreadPoolExecutor(8) as ex:
        for msg in ex.map(lambda j: fetch(*j), jobs):
            print(msg)

    tree = json.loads((RAW / "scrollmapper_tree.json").read_text(encoding="utf-8"))["tree"]
    paths = [t["path"] for t in tree]
    parquet = [p for p in paths if p.startswith("formats/parquet/") and p.endswith(".parquet")]
    readmes = [p for p in paths if p.startswith("sources/") and p.endswith("/README.md") and p.count("/") == 3]
    jobs = [(SCROLL + urllib.parse.quote(p), RAW / "scrollmapper" / "parquet" / Path(p).name) for p in parquet]
    jobs += [(SCROLL + urllib.parse.quote(p), RAW / "scrollmapper" / "readme" / f"{p.split('/')[1]}__{p.split('/')[2]}.md") for p in readmes]
    with ThreadPoolExecutor(12) as ex:
        for msg in ex.map(lambda j: fetch(*j), jobs):
            if not msg.startswith("skip"):
                print(msg)

    for z, d in [("kjv_usfm.zip", "kjv_usfm"), ("web_usfm.zip", "web_usfm"), ("lxx_usfm.zip", "lxx_usfm"), ("cross_references.zip", "cross_references")]:
        if not (RAW / d).exists():
            zipfile.ZipFile(RAW / z).extractall(RAW / d)

    # more English translations (see english_texts.py for their licences)
    jobs = [(f"https://ebible.org/Scriptures/{t['ebible']}_usfm.zip", RAW / "ebible" / f"{t['ebible']}_usfm.zip") for t in EBIBLE_ENGLISH]
    with ThreadPoolExecutor(6) as ex:
        for msg in ex.map(lambda j: fetch(*j), jobs):
            if not msg.startswith("skip"):
                print(msg)
    for t in EBIBLE_ENGLISH:
        d = RAW / "ebible" / t["ebible"]
        if not d.exists():
            zipfile.ZipFile(RAW / "ebible" / f"{t['ebible']}_usfm.zip").extractall(d)
    print(f"{len(parquet)} parquet translations, {len(readmes)} translation READMEs")


if __name__ == "__main__":
    sys.exit(main())

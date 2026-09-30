"""Build chrono.js: every verse of the Bible in the order its events happened, for the Order control.

    python build_chrono.py              # downloads the Theographic CSVs into ../bibledb/raw/theographic/ if missing
    python build_chrono.py --report     # also print the order as a list of passages, to check it by eye

Source: Theographic Bible Metadata (Robert Rouse, https://github.com/robertrouse/theographic-bible-metadata),
CC BY-SA 4.0. Its events list the verses that tell them, from every book that does, with a fine-grained
sort key; its verses carry an estimated year.

The order:
  1. A verse that belongs to an event sorts by that event's sort key. Parallel accounts share an event, so the
     Gospels' feeding of the five thousand, or a story told in both Kings and Isaiah, end up side by side.
     A verse in several events (a parallel told inside a larger story) takes the most specific one: the event
     with the fewest verses. Events count only in books told event by event (a quarter or more of their verses in
     an event), so a letter's passing mention of Enoch or Abraham stays in the letter.
  2. A verse with no event sorts by its estimated year, after that year's events: Chronicles beside the reigns
     it retells, a letter at the year it was written.
  3. A verse with neither follows the verse before it in its book (so an undated psalm stays with its neighbours).
Ties keep Bible order, so each account stays in one piece.

Writes chrono.js defining window.RAINBOW_CHRONO = {count, order, source}, where order is the gzip+base64 of
Uint16 verse indices (0 = Genesis 1:1 … 31101 = Revelation 22:21) in chronological order.
"""
import base64, csv, gzip, json, os, shutil, sys, urllib.request
from array import array
from pathlib import Path

from buildutil import write_text

HERE = Path(__file__).resolve().parent
RAW = HERE.parent / "bibledb" / "raw" / "theographic"
BASE = "https://raw.githubusercontent.com/robertrouse/theographic-bible-metadata/master/CSV/"
SOURCE = ("Theographic Bible Metadata, Robert Rouse (CC BY-SA 4.0), "
          "https://github.com/robertrouse/theographic-bible-metadata")


def fetch(name):
    path = RAW / name
    if not path.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        part = path.with_suffix(".part")
        if part.exists():
            part.unlink()
        print("downloading", name)
        # download beside the final name and move it into place only once complete, so a broken download is never reused
        with urllib.request.urlopen(BASE + name, timeout=60) as response, open(part, "wb") as f:
            shutil.copyfileobj(response, f)
        os.replace(part, path)
    return list(csv.DictReader(open(path, encoding="utf-8-sig", newline="")))


def main():
    verses = fetch("Verses.csv")
    events = fetch("Events.csv")
    # sort verses by verseID (format BBCCCVVV) to ensure canonical order
    verses.sort(key=lambda v: int(v["verseID"]))
    refs = [v["osisRef"] for v in verses]
    index = {r: i for i, r in enumerate(refs)}
    # the pages count verses in KJV order, Genesis 1:1 = 0; Theographic uses the same versification
    data = HERE / "data.js"
    if data.exists():
        d = json.loads(data.read_text(encoding="utf-8").split("=", 1)[1].rstrip().rstrip(";"))
        # build expected list of references from data.js and compare to sorted Theographic refs
        expected_refs = []
        for book in d["books"]:
            osis = book["osis"]
            for chapter_idx, chapter_verses in enumerate(book["chapters"], 1):
                for verse in range(1, chapter_verses + 1):
                    expected_refs.append(f"{osis}.{chapter_idx}.{verse}")
        if expected_refs != refs:
            # find first mismatch
            for pos, (exp, got) in enumerate(zip(expected_refs, refs)):
                if exp != got:
                    sys.exit(f"verse {pos}: data.js has {exp} but Theographic has {got}")
            # also check if lengths differ
            if len(expected_refs) != len(refs):
                sys.exit(f"verse count differs: data.js has {len(expected_refs)}, Theographic {len(refs)}")

    # most specific event per verse (fewest verses), with its sort key; only for books told event by event
    in_event = {i for e in events for i in (index.get(r) for r in (e["verses"] or "").split(",")) if i is not None}
    per_book, told = {}, {}
    for i, v in enumerate(verses):
        per_book[v["book"]] = per_book.get(v["book"], 0) + 1
        told[v["book"]] = told.get(v["book"], 0) + (i in in_event)
    narrated = {b for b in per_book if told[b] >= per_book[b] / 4}
    best = {}
    for e in events:
        vs = [index[r] for r in (e["verses"] or "").split(",") if r in index]
        if not vs or not e["sortKey"]:
            continue
        key = float(e["sortKey"])
        for i in vs:
            if verses[i]["book"] not in narrated:
                continue
            if i not in best or len(vs) < best[i][0]:
                best[i] = (len(vs), key)

    def year(v):
        y = v["yearNum"].strip()
        if not y:
            return None
        y = int(float(y))
        return y + 1 if y < 0 else y    # event keys count 1 BC as year 0; verse years count it as -1

    keys = [None] * len(refs)
    for i, v in enumerate(verses):
        if i in best:
            keys[i] = best[i][1]
        elif year(v) is not None:
            keys[i] = year(v) + 0.999
    # undated verses follow the verse before them in the same book (or, at a book's start, the one after)
    for i in range(len(keys)):
        if keys[i] is None and i and verses[i - 1]["book"] == verses[i]["book"]:
            keys[i] = keys[i - 1]
    for i in range(len(keys) - 1, -1, -1):
        if keys[i] is None:
            keys[i] = keys[i + 1] if i + 1 < len(keys) and verses[i + 1]["book"] == verses[i]["book"] else 0.0

    order = sorted(range(len(refs)), key=lambda i: (keys[i], i))
    arr = array("H", order)
    if sys.byteorder != "little":
        arr.byteswap()
    blob = base64.b64encode(gzip.compress(arr.tobytes(), 9, mtime=0)).decode()
    out = HERE / "chrono.js"
    write_text(out, "window.RAINBOW_CHRONO=" + json.dumps({"count": len(order), "order": blob, "source": SOURCE},
                                                          separators=(",", ":")) + ";\n")
    runs = sum(1 for k in range(len(order)) if k == 0 or order[k] != order[k - 1] + 1)
    print(f"chrono.js {out.stat().st_size / 1e3:.0f} kB · {len(order)} verses in {runs} passages")

    if "--report" in sys.argv:
        k = 0
        while k < len(order):
            e = k
            while e + 1 < len(order) and order[e + 1] == order[e] + 1:
                e += 1
            print(f"{keys[order[k]]:>12.3f}  {refs[order[k]]} – {refs[order[e]]}  ({e - k + 1})")
            k = e + 1


if __name__ == "__main__":
    main()

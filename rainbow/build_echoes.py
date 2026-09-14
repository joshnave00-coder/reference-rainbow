"""Export repeated phrases from ../bibledb/bible.duckdb for the Echoes page.

    python build_echoes.py            # writes echoes-data.js (run ../bibledb/build.py first)

Output: window.ECHOES_DATA = {z: base64(gzip(JSON))}, where the JSON is
  sets:  {"ot/exact": {stats: [[length, distinct, places]], repeats: [[length, books, text, gloss, occurrences, transliteration]]}, …}
         occurrence = [book, ch1, v1, ch2, v2, verse_index1, verse_index2, text|null, transliteration|null, strongs|null]
         (text/transliteration are null when identical to the phrase's; strongs is null when identical to the first occurrence's)
  books: {id: name}
  lex:   {strongs: [lemma, transliteration, language, definition, kjv_usage, derivation, pronunciation, gloss]}
"""
import base64, gzip, json, re
from pathlib import Path

from buildutil import write_text

import duckdb

HERE = Path(__file__).resolve().parent
DB = HERE.parent / "bibledb" / "bible.duckdb"
OUT = HERE / "echoes-data.js"

con = duckdb.connect(str(DB), read_only=True)
books = {b: n for b, n in con.execute("SELECT book_id, name FROM books").fetchall()}
sets = {}
for corpus, mode, n, distinct, occ in con.execute("SELECT corpus, match_mode, length_words, distinct_phrases, occurrences FROM phrase_length_stats ORDER BY 1, 2, 3").fetchall():
    sets.setdefault(f"{corpus}/{mode}", {"stats": [], "repeats": []})["stats"].append([n, distinct, occ])

occ_by, used = {}, set()
for rid, b, c1, v1, c2, v2, g1, g2, text, tr, strongs in con.execute(
        """SELECT repeat_id, book_id, start_chapter, start_verse, end_chapter, end_verse, start_verse_id, end_verse_id, text, transliteration, strongs
           FROM phrase_occurrences ORDER BY repeat_id, occurrence_no""").fetchall():
    occ_by.setdefault(rid, []).append([b, c1, v1, c2, v2, (g1 - 1) if g1 else -1, (g2 - 1) if g2 else -1, text, tr, strongs])
    used.update(s for s in (strongs or "").split() if s != "-")

n_rep = 0
for rid, corpus, mode, n, count, nbooks, text, gloss, tr in con.execute(
        """SELECT repeat_id, corpus, match_mode, length_words, occurrence_count, book_count, phrase_text, phrase_gloss, phrase_transliteration
           FROM phrase_repeats ORDER BY repeat_id""").fetchall():
    occs = occ_by[rid]
    first_strongs = occs[0][9]
    for k, o in enumerate(occs):
        if o[7] == text:
            o[7] = None
        if o[8] == tr:
            o[8] = None
        if k and o[9] == first_strongs:
            o[9] = None
    sets[f"{corpus}/{mode}"]["repeats"].append([n, nbooks, text, gloss, occs, tr])
    n_rep += 1

lex = {}
if used:
    rows = con.execute("""
        SELECT s.strongs_id, s.lemma, s.transliteration, s.language, s.definition, s.kjv_usage, s.derivation, s.pronunciation,
               (SELECT gloss FROM lexicon_extended l WHERE l.strongs_id = s.strongs_id ORDER BY (l.extended_id = s.strongs_id) DESC, l.extended_id LIMIT 1)
        FROM strongs s WHERE s.strongs_id IN (SELECT unnest(?))""", [sorted(used)]).fetchall()
    lex = {r[0]: [x.strip() if isinstance(x, str) else x for x in r[1:]] for r in rows}

# ---- word links: which English words translate each Strong's number, for the verses Echoes shows ----
#   KJV and WEB: Strong's-tagged words with character positions (eBible.org word tags)
#   BSB: the Berean interlinear's English rendering of each Hebrew/Greek word, located in the verse text in order
need = set()
for occs in occ_by.values():
    for o in occs:
        if o[5] >= 0:
            need.update(range(o[5], min(o[6] if o[6] >= 0 else o[5], o[5] + 8) + 1))
need_ids = sorted(g + 1 for g in need)
clean = lambda t: re.sub(r"\s+", " ", (t or "").replace("¶", " ")).strip()
sid_index, align = {}, {}


def add(tid, g, s0, e0, sid):
    align.setdefault(tid, []).append((g, s0, e0, sid_index.setdefault(sid, len(sid_index))))


for tid in ("KJV", "WEB"):
    texts = {vi: clean(t) for vi, t in con.execute(
        "SELECT verse_id, text FROM verse_text WHERE translation_id = ? AND verse_id IN (SELECT unnest(?))", [tid, need_ids]).fetchall()}
    for vi, s0, e0, sid, word in con.execute(
            """SELECT verse_id, start_char, end_char, strongs, word FROM translation_words
               WHERE translation_id = ? AND strongs IS NOT NULL AND start_char IS NOT NULL AND verse_id IN (SELECT unnest(?))""", [tid, need_ids]).fetchall():
        if texts.get(vi, "")[s0:e0] == word:
            add(tid, vi - 1, s0, e0, sid)

texts = {vi: clean(t) for vi, t in con.execute(
    "SELECT verse_id, text FROM verse_text WHERE translation_id = 'BSB' AND verse_id IN (SELECT unnest(?))", [need_ids]).fetchall()}
cur, pos, bsb_found, bsb_total = None, 0, 0, 0
for vi, word, sid in con.execute(
        """SELECT verse_id, word, strongs FROM translation_words
           WHERE translation_id = 'BSB' AND word IS NOT NULL AND verse_id IN (SELECT unnest(?)) ORDER BY verse_id, word_seq""", [need_ids]).fetchall():
    if vi != cur:
        cur, pos = vi, 0
    t, w = texts.get(vi, ""), re.sub(r"[\[\]]", "", word).strip()
    if not w or not t:
        continue
    bsb_total += 1
    i = t.find(w, pos)
    if i < 0:
        i = t.lower().find(w.lower(), pos)
    if i < 0:
        continue
    bsb_found += 1
    if sid:
        add("BSB", vi - 1, i, i + len(w), sid)
    pos = i + len(w)

align_out = {}
for tid, rows in align.items():
    rows.sort()
    prev, G, S, L, K = 0, [], [], [], []
    for g, s0, e0, k in rows:
        G.append(g - prev); prev = g; S.append(s0); L.append(e0 - s0); K.append(k)
    align_out[tid] = {"g": G, "s": S, "l": L, "k": K}
align_ids = [None] * len(sid_index)
for sid, k in sid_index.items():
    align_ids[k] = sid
print(f"word links for {len(need_ids):,} verses: " + ", ".join(f"{t} {len(r):,}" for t, r in align.items()) + f" (BSB words located {bsb_found:,}/{bsb_total:,})")

payload = json.dumps({"sets": sets, "books": books, "lex": lex, "align": align_out, "alignIds": align_ids},
                     ensure_ascii=False, separators=(",", ":")).encode("utf-8")
write_text(OUT, "window.ECHOES_DATA=" + json.dumps({"z": base64.b64encode(gzip.compress(payload, 9, mtime=0)).decode()}) + ";\n")
print(f"{n_rep} repeated phrases in {len(sets)} sets; {len(lex)} Strong's entries; echoes-data.js {OUT.stat().st_size / 1e6:.2f} MB (raw JSON {len(payload) / 1e6:.1f} MB)")

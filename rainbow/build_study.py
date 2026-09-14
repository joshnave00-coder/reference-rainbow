"""Export word-study data for the Bible reader (read.html) from ../bibledb/bible.duckdb.

    python build_study.py      # run ../bibledb/build.py first

Writes:
  study/books/B01.js … B66.js   every Hebrew, Aramaic and Greek word of the book, in order, per verse:
                                [text, transliteration, English gloss, Strong's, grammar code, flag]
                                flag: q = read as the margin reading (qere); t = in the KJV's Greek text only;
                                      n = in modern critical editions only; '' otherwise
                                plus word links for the KJV and BSB: [start, end, Strong's] per verse
  study/lexicon.js              Strong's dictionary + STEPBible short meanings and senses
  study/concordance.js          for every Strong's number: the verses it occurs in and how the KJV and BSB render it there
"""
import base64, gzip, json, re, sys
from pathlib import Path

from buildutil import write_text

import duckdb

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "bibledb"))
import phrases  # noqa: E402

DB = HERE.parent / "bibledb" / "bible.duckdb"
OUT = HERE / "study"
WORD_FILTER = """((source = 'TAHOT' AND (word_type LIKE 'L%' OR word_type LIKE 'Q%' OR word_type = 'R'))
                 OR (source = 'TAGNT' AND regexp_matches(word_type, '[NK]')))"""


def pack(obj):
    return base64.b64encode(gzip.compress(json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), 9, mtime=0)).decode()


def clean(t):
    return re.sub(r"\s+", " ", (t or "").replace("¶", " ")).strip()


def write(path, js):
    path.parent.mkdir(parents=True, exist_ok=True)
    write_text(path, js)
    return path.stat().st_size


def main():
    con = duckdb.connect(str(DB), read_only=True)
    total = 0

    # ---- words per book ------------------------------------------------------------
    books = {}
    for b, vi, src, wtype, text, tr, eng, sid, morph in con.execute(f"""
            SELECT book_id, verse_id, source, word_type, text, transliteration, english, strongs, morphology
            FROM original_words WHERE verse_id IS NOT NULL AND {WORD_FILTER} ORDER BY verse_id, word_pos""").fetchall():
        if src == "TAHOT":
            tr = phrases.clean_step_translit(tr)
            flag = "q" if wtype.startswith("Q") else ""
        else:
            n, k = "N" in wtype, "K" in wtype
            flag = "" if n and k else ("n" if n else "t")
        gloss = re.sub(r"/\s*", " ", eng or "").strip()
        books.setdefault(b, {"v": {}, "a": {}})["v"].setdefault(str(vi - 1), []).append(
            [(text or "").replace("¶", ""), tr or "", gloss, sid or "", morph or "", flag])

    # ---- word links: KJV (Strong's tags with positions) and BSB (interlinear renderings located in order) ----
    kjv_text = {vi: clean(t) for vi, t in con.execute("SELECT verse_id, text FROM verse_text WHERE translation_id = 'KJV' AND verse_id IS NOT NULL").fetchall()}
    for b, vi, s0, e0, sid, word in con.execute(
            """SELECT book_id, verse_id, start_char, end_char, strongs, word FROM translation_words
               WHERE translation_id = 'KJV' AND strongs IS NOT NULL AND start_char IS NOT NULL ORDER BY verse_id, start_char""").fetchall():
        if kjv_text.get(vi, "")[s0:e0] == word and b in books:
            books[b]["a"].setdefault("KJV", {}).setdefault(str(vi - 1), []).append([s0, e0, sid])
    bsb_text = {vi: clean(t) for vi, t in con.execute("SELECT verse_id, text FROM verse_text WHERE translation_id = 'BSB' AND verse_id IS NOT NULL").fetchall()}
    cur, pos = None, 0
    for b, vi, word, sid in con.execute(
            """SELECT book_id, verse_id, word, strongs FROM translation_words
               WHERE translation_id = 'BSB' AND word IS NOT NULL ORDER BY verse_id, word_seq""").fetchall():
        if vi != cur:
            cur, pos = vi, 0
        t, w = bsb_text.get(vi, ""), re.sub(r"[\[\]]", "", word).strip()
        if not w or not t:
            continue
        i = t.find(w, pos)
        if i < 0:
            i = t.lower().find(w.lower(), pos)
        if i < 0:
            continue
        if sid and b in books:
            books[b]["a"].setdefault("BSB", {}).setdefault(str(vi - 1), []).append([i, i + len(w), sid])
        pos = i + len(w)

    for b in range(1, 67):
        size = write(OUT / "books" / f"B{b:02d}.js", f"(window.STUDY_BOOKS = window.STUDY_BOOKS || {{}})[{b}] = {{\"z\": \"{pack(books.get(b, {'v': {}, 'a': {}}))}\"}};\n")
        total += size
    print(f"books: 66 files, {total / 1e6:.1f} MB")

    # ---- lexicon ----------------------------------------------------------------------
    senses = {}
    for sid, ext, gloss in con.execute("SELECT strongs_id, extended_id, gloss FROM lexicon_extended ORDER BY extended_id").fetchall():
        senses.setdefault(sid, []).append([ext, gloss])
    lex = {}
    for sid, lemma, tr, pron, lang, definition, kjv, deriv in con.execute(
            "SELECT strongs_id, lemma, transliteration, pronunciation, language, definition, kjv_usage, derivation FROM strongs").fetchall():
        ss = senses.get(sid, [])
        main = next((g for e, g in ss if e == sid), ss[0][1] if ss else "")
        lex[sid] = [lemma, tr, pron, lang, (definition or "").strip(), (kjv or "").strip(), (deriv or "").strip(), main or "", ss if len(ss) > 1 else None]
    size = write(OUT / "lexicon.js", f"window.STUDY_LEX = {{\"z\": \"{pack(lex)}\"}};\n")
    total += size
    print(f"lexicon: {len(lex):,} entries, {size / 1e6:.2f} MB")

    # ---- concordance -------------------------------------------------------------------------
    rows = con.execute(f"""
        WITH o AS (SELECT DISTINCT strongs, verse_id FROM original_words
                   WHERE verse_id IS NOT NULL AND strongs IS NOT NULL AND NOT regexp_matches(strongs, '^H9') AND {WORD_FILTER}),
             k AS (SELECT strongs, verse_id, array_to_string(list_sort(list_distinct(list(trim(word)))), ' / ') w
                   FROM translation_words WHERE translation_id = 'KJV' AND strongs IS NOT NULL AND word IS NOT NULL GROUP BY 1, 2),
             b AS (SELECT strongs, verse_id, array_to_string(list_sort(list_distinct(list(trim(regexp_replace(word, '[\\[\\]]', '', 'g'))))), ' / ') w
                   FROM translation_words WHERE translation_id = 'BSB' AND strongs IS NOT NULL AND word IS NOT NULL GROUP BY 1, 2)
        SELECT o.strongs, o.verse_id, k.w, b.w FROM o LEFT JOIN k USING (strongs, verse_id) LEFT JOIN b USING (strongs, verse_id)
        ORDER BY 1, 2""").fetchall()
    strings, conc = {"": 0}, {}
    for sid, vi, kw, bw in rows:
        entry = conc.setdefault(sid, [[], [], [], 0])  # [verse deltas, KJV rendering ids, BSB rendering ids, previous verse]
        g = vi - 1
        entry[0].append(g - entry[3])
        entry[3] = g
        entry[1].append(strings.setdefault(kw or "", len(strings)))
        entry[2].append(strings.setdefault(bw or "", len(strings)))
    conc = {sid: e[:3] for sid, e in conc.items()}
    table = [None] * len(strings)
    for s, i in strings.items():
        table[i] = s
    size = write(OUT / "concordance.js", f"window.STUDY_CONC = {{\"z\": \"{pack({'r': table, 's': conc})}\"}};\n")
    total += size
    print(f"concordance: {len(conc):,} Strong's numbers, {len(rows):,} verse occurrences, {size / 1e6:.2f} MB")
    print(f"total {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()

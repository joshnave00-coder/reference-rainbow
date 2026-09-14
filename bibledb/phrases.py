"""Repeated phrases ("echoes"): runs of 7 or more words that occur more than once in the original-language text.

Corpora
  ot  - Hebrew & Aramaic Old Testament (STEPBible TAHOT; one reading per word: ketiv and added words skipped)
  nt  - Greek New Testament (STEPBible TAGNT; words printed in Nestle-Aland)
  gk  - the Greek Bible: Septuagint Old Testament (eBible grclxx) followed by the Greek New Testament, so that
        New Testament quotations of the Septuagint show up as repeats

Match modes
  exact - the same words in the same order, ignoring vowel points, cantillation, accents, case and punctuation
  lemma - the same dictionary words (Strong's numbers) in the same order, so different inflections still match
          (ot and nt only; the Septuagint text has no Strong's tagging)

For every length n >= MIN_WORDS the stats count how many distinct n-word sequences occur at least twice and at
how many places. The repeats list keeps only maximal phrases: a phrase is reported at its full length, not again
as each of its shorter sub-runs. Phrases never cross a book boundary.
"""
import re
import unicodedata
from collections import defaultdict

MIN_WORDS = 7

_HEB_KEEP = re.compile(r"[^א-ת]")
_FINALS = str.maketrans("ךםןףץ", "כמנפצ")
_GRK_KEEP = re.compile(r"[^α-ω]")


_GRK_ROMAN = {"α": "a", "β": "b", "γ": "g", "δ": "d", "ε": "e", "ζ": "z", "η": "ē", "θ": "th", "ι": "i", "κ": "k", "λ": "l", "μ": "m",
              "ν": "n", "ξ": "x", "ο": "o", "π": "p", "ρ": "r", "σ": "s", "ς": "s", "ϲ": "s", "τ": "t", "υ": "y", "φ": "ph", "χ": "ch",
              "ψ": "ps", "ω": "ō"}


def translit_greek(word):
    """Romanize a Greek word (SBL-style): ἁμαρτία -> hamartia, Χριστοῦ -> Christou, εὐαγγέλιον -> euangelion."""
    letters = []  # [base letter, has rough breathing]
    for ch in unicodedata.normalize("NFD", word or ""):
        if unicodedata.combining(ch):
            if ch == "̔" and letters:
                letters[-1][1] = True
        elif ch.isalpha():
            letters.append([ch, False])
    out, rough_done = [], False
    for i, (ch, rough) in enumerate(letters):
        low = ch.lower()
        nxt = letters[i + 1][0].lower() if i + 1 < len(letters) else ""
        prev = letters[i - 1][0].lower() if i else ""
        if low == "γ" and nxt and nxt in "γκξχ":
            t = "n"
        elif low == "υ" and prev and prev in "αεηο":
            t = "u"
        else:
            t = _GRK_ROMAN.get(low, low)
        if rough and not rough_done:
            if low == "ρ":
                t = "rh"
            else:
                out.insert(0, "h")  # rough breathing belongs at the front of the word, even when it sits on a diphthong's second vowel
            rough_done = True
        out.append(t[:1].upper() + t[1:] if ch != low else t)
    s = "".join(out)
    if len(s) > 1 and s[0] == "h" and s[1].isupper():
        s = "H" + s[1].lower() + s[2:]
    return s


def clean_step_translit(t):
    """STEPBible Hebrew transliteration ('be./re.Shit', "'E.lo.Him") -> readable ('bereshit', "'elohim")."""
    return re.sub(r"[./\\]", "", t or "").lower().strip()


def norm_hebrew(word):
    return _HEB_KEEP.sub("", word or "").translate(_FINALS)


def norm_greek(word):
    w = unicodedata.normalize("NFD", word or "")
    w = "".join(ch for ch in w if not unicodedata.combining(ch)).lower().replace("ς", "σ").replace("ϲ", "σ")
    return _GRK_KEEP.sub("", w)


def find_repeats(keys, books, min_words=MIN_WORDS):
    """keys: list of hashable tokens; books: parallel list of book ids.
    Returns (stats [(n, distinct_phrases, occurrences)], repeats [(n, [start positions])])."""
    N = len(keys)
    ids, vocab = [], {}
    for k in keys:
        ids.append(vocab.setdefault(k, len(vocab)))
    groups = defaultdict(list)
    for i in range(N - min_words + 1):
        if books[i] == books[i + min_words - 1]:
            groups[tuple(ids[i:i + min_words])].append(i)
    level = [g for g in groups.values() if len(g) > 1]
    del groups
    stats, repeats = [], []
    n = min_words
    while level:
        stats.append((n, len(level), sum(len(g) for g in level)))
        nxt = []
        for g in level:
            sub = defaultdict(list)
            for p in g:
                q = p + n
                if q < N and books[q] == books[p]:
                    sub[ids[q]].append(p)
            extends_as_one = len(sub) == 1 and len(next(iter(sub.values()))) == len(g)
            if not extends_as_one:
                before = {ids[p - 1] if p > 0 and books[p - 1] == books[p] else -1 - p for p in g}
                if len(before) > 1:
                    repeats.append((n, g))
            nxt.extend(s for s in sub.values() if len(s) > 1)
        level = nxt
        n += 1
    return stats, repeats


def run_corpus(tokens, mode):
    """tokens: list of dicts with keys norm, lemma, book_id. Returns (stats, repeats)."""
    if mode == "lemma":
        keys = [t["lemma"] or ("~" + t["norm"]) for t in tokens]
    else:
        keys = [t["norm"] for t in tokens]
    return find_repeats(keys, [t["book_id"] for t in tokens])

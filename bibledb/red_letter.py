"""Red letters: words spoken by Jesus and by God in the WEB and KJV (eBible.org USFM editions).

* Jesus - from the \\wj ... \\wj* ("words of Jesus") markup in eBible.org's WEB and KJV files, which
          follow the red-letter-edition tradition. Exact for those two texts.
* God   - detected in the WEB, whose modern punctuation marks every quotation, including quotations
          nested inside quotations. Each quotation is attributed from the words that introduce or follow
          it: "God said", "the LORD spoke to Moses, saying", "Thus says the LORD", "the LORD's word came
          to me", "a voice out of the sky", "“…,” says the LORD". A quotation nested inside God's speech
          (a prophet relaying "The LORD says, '…'") keeps God as speaker, and so does a quotation that
          resumes right after "says the LORD". This is a heuristic: expect misses and some
          over-inclusion. Such spans carry method = 'quotation heuristic'.
* KJV God spans are carried over from the WEB verse by verse by matching Strong's numbers
  (method = 'aligned from WEB').

Offsets are character offsets into the plain verse text returned here, which is the text the database
stores for WEB and KJV.
"""
import re
from pathlib import Path

NOTE = re.compile(r"\\(f|fe|x|ef|ex)\s.*?\\\1\*", re.S)
SKIP_LINE = re.compile(r"^\\(id|ide|h|toc\d?|mt\d?|ms\d?|mr|s\d?|sr|r|d|sp|cl|rem|sts|is\d?|ip|imt\d?|io\d?|iot|ie|cp|periph)\b")
PARA = re.compile(r"^\\(p|m|pi\d?|mi|nb|q\d?|qc|qr|qm\d?|li\d?|b|pc|pr|pm|pmo|pmc|pmr|ph\d?|lh|lf|lim\d?)(?=\s|$)\s?")
TOK = re.compile(
    r"\\v\s+(?P<v>\d+)[a-z]?(?:-\d+)?\s?"
    r"|\\\+?w\s+(?P<w>[^|\\]*?)\|(?P<attrs>[^\\]*?)\\\+?w\*"
    r"|\\(?P<plus>\+?)(?P<mk>[a-z]+\d*)(?:(?P<close>\*)|\s?)"
    r"|(?P<t>[^\\]+)")
WS = re.compile(r"\s+")


class Verse:
    __slots__ = ("chapter", "verse", "text", "jesus", "words", "para", "pending_para", "god")

    def __init__(self, chapter, verse, para):
        self.chapter, self.verse, self.text = chapter, verse, ""
        self.jesus, self.words, self.para, self.pending_para, self.god = [], [], [], para, []

    def add(self, s, jesus=False, strongs=None):
        s = WS.sub(" ", s.replace("¶", " "))
        if not self.text or self.text.endswith(" "):
            s = s.lstrip(" ")
        if not s:
            return
        start = len(self.text)
        if self.pending_para:
            self.para.append(start)
            self.pending_para = False
        self.text += s
        if jesus:
            self.jesus.append([start, len(self.text)])
        if strongs is not None:
            m = re.search(r'strong="([^"]+)"', strongs)
            for code in (m.group(1).replace(",", " ").split() if m else []):
                self.words.append([start, len(self.text), code])

    def finish(self):
        t = self.text.rstrip()
        self.text, n = t, len(t)
        spans = []
        for s, e in self.jesus:
            s, e = min(s, n), min(e, n)
            while s < e and t[s] == " ":
                s += 1
            while e > s and t[e - 1] == " ":
                e -= 1
            if e <= s:
                continue
            if spans and re.fullmatch(r"[\s\W]*", t[spans[-1][1]:s]):
                spans[-1][1] = e
            else:
                spans.append([s, e])
        self.jesus = spans
        self.words = [w for w in self.words if w[0] < n]


def parse_book(path: Path):
    """-> (usfm_code, [Verse, ...]) with plain text, Jesus spans, Strong's-tagged word offsets, paragraph starts."""
    raw = NOTE.sub("", path.read_text(encoding="utf-8-sig"))
    code, chap, cur, out = None, 0, None, []
    jesus, para = False, True
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("\\id "):
            code = line.split()[1]
            continue
        if SKIP_LINE.match(line):
            continue
        m = re.match(r"^\\c\s+(\d+)", line)
        if m:
            chap, cur, para = int(m.group(1)), None, True
            continue
        pm = PARA.match(line)
        if pm:
            line = line[pm.end():]
            para = True
            if cur is not None:
                cur.pending_para = True
                if cur.text and not cur.text.endswith(" "):
                    cur.text += " "
        for m in TOK.finditer(line):
            if m.group("v"):
                cur = Verse(chap, int(m.group("v")), para)
                para = False
                out.append(cur)
            elif m.group("w") is not None:
                if cur is not None:
                    cur.add(m.group("w"), jesus, m.group("attrs"))
            elif m.group("mk"):
                if m.group("mk") == "wj":
                    jesus = not m.group("close")
            elif m.group("t") and cur is not None:
                cur.add(m.group("t"), jesus)
        if cur is not None and not cur.text.endswith(" "):
            cur.text += " "
    for v in out:
        v.finish()
    return code, [v for v in out if v.text]


# ------------------------------------------------------------------------------ God's speech
GODN = (r"(?:the\s+)?(?:LORD(?:\s+(?:God|of\s+Armies|your\s+God|their\s+God|his\s+God|our\s+God|my\s+God))?"
        r"|Lord\s+GOD|Lord\s+LORD|God\s+Almighty|God|GOD|Holy\s+Spirit|Almighty|Most\s+High|Holy\s+One\s+of\s+Israel)")
VERBS = r"(?:said|says|spoke|spoken|speaks|answered|called|commanded|swore|sworn|declared|declares|replied|proclaimed)"
INTRO = [
    (re.compile(rf"\b{GODN}\s+(?:[a-z]+\s+){{0,3}}?{VERBS}\b"), 50),
    (re.compile(rf"\b(?:word\s+of\s+{GODN}|{GODN}’s\s+word)\s+(?:came|was|which\s+came)\b"), 90),
    (re.compile(rf"\b(?:[Tt]hus|[Ss]o|[Tt]his\s+is\s+what)\s+(?:says|said)\s+{GODN}"), 30),
    (re.compile(r"\bvoice\s+(?:came\s+)?(?:out\s+of|from)\s+(?:the\s+)?(?:heavens?|sky|cloud|throne|temple)"), 50),
    (re.compile(rf"\b(?:voice\s+of\s+(?:{GODN}|the\s+Lord)|(?:{GODN}|the\s+Lord)’s\s+voice)\b"), 40),
    (re.compile(rf"\b{GODN}\b[^.!?;“”‘’]{{0,140}}?\b(?:and\s+said|saying|and\s+spoke|and\s+called)\b"), 25),
]
SUBJECT_PATTERNS = (INTRO[0][0], INTRO[5][0])
AFTER = re.compile(rf"^\s*,?\s*(?:says|declares|said|has\s+said|has\s+spoken)\s+{GODN}")
PREP_BEFORE = re.compile(r"\b(?:to|unto|before|of|from|with|by|against|in|on|upon|about|than|like)\s+$")


def _intro_is_god(pre):
    for rx, maxgap in INTRO:
        last = None
        for m in rx.finditer(pre):
            last = m
        if last is None:
            continue
        gap = pre[last.end():]
        if len(gap) > maxgap or re.search(r"[.!?;]", gap) or "”" in gap:
            continue
        if rx in SUBJECT_PATTERNS and PREP_BEFORE.search(pre[max(0, last.start() - 12):last.start()]):
            continue
        return True
    return False


PRONOUN_INTRO = re.compile(r"\b[Hh]e\s+(?:said|answered|called|replied)(?:\s+to\s+(?:him|her|them|me|us))?,?\s*$")
RESUME_GAP = re.compile(rf"[\s,.;:—–-]*(?:(?:says|declares|said|has\s+said|has\s+spoken)\s+{GODN}[\s,.;:—–-]*)?")
QUOTE_METHOD = "quotation heuristic"
DIALOGUE_METHOD = "dialogue heuristic"


def detect_god(verses, trace=None):
    """verses: WEB Verse objects of one book (in order).
    Returns {verse index: [[start, end, method], ...]} of God's speech."""
    starts, parts, pos = [], [], 0
    para_starts = set()
    for v in verses:
        starts.append(pos)
        for p in v.para:
            para_starts.add(pos + p)
        parts.append(v.text)
        pos += len(v.text) + 1
    S = " ".join(parts)
    stack, spans = [], []
    history = []  # top-level quotations: (end offset, speaker or None)

    def at_para(i):
        j = i
        while j > 0 and S[j - 1] == " " and j not in para_starts:
            j -= 1
        return j in para_starts or j == 0

    def push(kind, i):
        pre = S[max(0, i - 240):i]
        who = None
        if _intro_is_god(pre):
            who = ("God", QUOTE_METHOD)
        elif stack:
            who = stack[-1]["who"]
        elif history and history[-1][1] and history[-1][1][0] == "God" and i - history[-1][0] <= 60 \
                and RESUME_GAP.fullmatch(S[history[-1][0] + 1:i]):
            who = history[-1][1]  # the same oracle resuming after "…,” says the LORD."
        elif PRONOUN_INTRO.search(pre) and len(history) >= 2 and history[-1][1] is None \
                and history[-2][1] and history[-2][1][0] == "God" and i - history[-2][0] <= 700:
            who = ("God", DIALOGUE_METHOD)  # "He said" answering a human reply to God
        if trace is not None:
            trace.append((i, kind, who, pre[-70:], [q["who"] for q in stack]))
        stack.append(dict(kind=kind, start=i + 1, who=who))

    def close(q, i):
        who = q["who"]
        if who is None and AFTER.match(S[i + 1:i + 60]):
            who = ("God", QUOTE_METHOD)
        if who:
            spans.append([q["start"], i, who[1]])
        if not stack:
            history.append((i, who))

    def close_all(i):
        while stack:
            close(stack.pop(), i)

    chapter_starts = {}
    for idx, v in enumerate(verses):
        if v.verse == 1:
            chapter_starts[starts[idx]] = idx

    for i, ch in enumerate(S):
        if i in chapter_starts and stack:
            first = S[i:i + 3].lstrip()
            if not first.startswith(("“", "‘")):
                close_all(i)  # quotations do not run on into a chapter that does not continue them
        if ch == "“":
            if stack and any(q["kind"] == "d" for q in stack) and at_para(i):
                while stack[-1]["kind"] != "d":
                    close(stack.pop(), i)  # inner quotations must have ended before the new paragraph
                continue  # a new paragraph re-opening the same quotation
            if stack and stack[-1]["kind"] == "d":
                cut = max([p for p in para_starts if stack[0]["start"] < p <= i] or [0])
                if not cut:
                    m = None
                    for m in re.finditer(r"[.!?]\s", S[stack[0]["start"]:i]):
                        pass
                    cut = stack[0]["start"] + m.end() if m else i
                close_all(cut)  # a quotation that was never closed: end it before this new attribution
            push("d", i)
        elif ch == "‘":
            if stack and stack[-1]["kind"] == "s" and at_para(i):
                continue
            push("s", i)
        elif ch == "”":
            while stack:
                q = stack.pop()
                close(q, i)
                if q["kind"] == "d":
                    break
        elif ch == "’" and stack and stack[-1]["kind"] == "s":
            prev = S[i - 1] if i else " "
            nxt = S[i + 1] if i + 1 < len(S) else " "
            if not prev.isalnum() or nxt in "”’?!.,;:" or (nxt in " \n" and prev in ".,!?;:"):
                close(stack.pop(), i)
    close_all(len(S))

    out = {}
    for s, e, method in spans:
        for idx, vs in enumerate(starts):
            ve = vs + len(verses[idx].text)
            a, b = max(s, vs), min(e, ve)
            if a < b:
                out.setdefault(idx, []).append([a - vs, b - vs, method])
    for idx, lst in out.items():
        t = verses[idx].text
        merged = []
        for a, b, m in sorted(lst):
            while a < b and not t[a].isalnum() and t[a] not in "‘“(":
                a += 1
            while b > a and t[b - 1] in " ,;:":
                b -= 1
            if b <= a:
                continue
            if merged and a <= merged[-1][1] + 1:
                merged[-1][1] = max(merged[-1][1], b)
                if m == QUOTE_METHOD:
                    merged[-1][2] = m
            else:
                merged.append([a, b, m])
        out[idx] = merged
    return out


def subtract(spans, holes):
    """Remove hole ranges from spans."""
    res = []
    for s, e in spans:
        cur = [[s, e]]
        for hs, he in holes:
            nxt = []
            for a, b in cur:
                if he <= a or hs >= b:
                    nxt.append([a, b])
                else:
                    if a < hs:
                        nxt.append([a, hs])
                    if he < b:
                        nxt.append([he, b])
            cur = nxt
        res.extend(x for x in cur if x[1] - x[0] > 1)
    return res


SPEECH_LEAD = re.compile(r"^(?:(?:and\s+)?(?:said|saith|saying|spake|spoke|answered|called|say|says)\b[,:]?\s*|(?:unto|to)\s+(?:him|her|them|me|us|[A-Z]\w+)[,:]\s*)+", re.I)


FULL_LEAD = re.compile(r"^(?:And\s+|Then\s+|So\s+)?(?:(?:he|she|they|I|God|the\s+LORD(?:\s+God)?|[A-Z][a-z]+)\s+)?(?:said|saith|spake|answered|called)(?:\s+(?:unto|to)\s+(?:him|her|them|me|us|[A-Z][a-z]+))?[,:]\s*")


def carry_to(web_v, spans, kjv_v):
    """Map God spans from a WEB verse onto the KJV verse: proportional position snapped to KJV words,
    widened to matching Strong's-number anchors, with leading speech formulas ("said unto him,") trimmed."""
    kt = kjv_v.text
    lw, lk = max(1, len(web_v.text)), max(1, len(kt))
    if sum(e - s for s, e in spans) / lw > 0.85:
        lead = FULL_LEAD.match(kt)
        return [[lead.end() if lead else 0, len(kt)]]
    words = [(m.start(), m.end()) for m in re.finditer(r"\S+", kt)]
    out = []
    for s, e in spans:
        ps, pe = s / lw * lk, e / lw * lk
        inside = [w for w in words if ps <= (w[0] + w[1]) / 2 <= pe]
        if not inside:
            continue
        a, b = inside[0][0], inside[-1][1]
        codes_in = {w[2] for w in web_v.words if s <= w[0] < e}
        codes_out = {w[2] for w in web_v.words if not (s <= w[0] < e)}
        anchors = [k for k in kjv_v.words if k[2] in codes_in and k[2] not in codes_out and abs(k[0] / lk - s / lw) < 0.35]
        if anchors:
            a, b = min(a, min(k[0] for k in anchors)), max(b, max(k[1] for k in anchors))
        lead = SPEECH_LEAD.match(kt[a:b])
        if lead:
            a += lead.end()
        if re.search(r"\b(?:unto|to)\s+$", kt[max(0, a - 6):a]):
            obj = re.match(r"(?:me|him|her|them|us|thee|[A-Z]\w+)[,:]\s*", kt[a:b])
            if obj:
                a += obj.end()
        while b > a and kt[b - 1] in " ,;:":
            b -= 1
        if b > a:
            out.append([a, b])
    out.sort()
    merged = []
    for a, b in out:
        if merged and a <= merged[-1][1] + 2:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return merged


def build(raw: Path):
    """Parse WEB and KJV, detect speech. Returns {tid: {(usfm, chapter, verse): dict(text, words, spans)}},
    spans = [(start, end, speaker, method)]."""
    books = {}
    for tid, folder in [("WEB", "web_usfm"), ("KJV", "kjv_usfm")]:
        for f in sorted((raw / folder).glob("*.usfm")):
            code, vs = parse_book(f)
            books.setdefault(tid, {})[code] = vs
    result = {"WEB": {}, "KJV": {}}
    for code, wvs in books["WEB"].items():
        god = detect_god(wvs)
        kmap = {(v.chapter, v.verse): v for v in books["KJV"].get(code, [])}
        for i, v in enumerate(wvs):
            g = []
            for s0, e0, m in god.get(i, []):
                g += [(a, b, m) for a, b in subtract([[s0, e0]], v.jesus)]
            spans = [(s0, e0, "Jesus", "red-letter markup") for s0, e0 in v.jesus] + [(s0, e0, "God", m) for s0, e0, m in g]
            result["WEB"][(code, v.chapter, v.verse)] = dict(text=v.text, words=v.words, spans=sorted(spans))
            kv = kmap.get((v.chapter, v.verse))
            if kv is not None and g:
                method = QUOTE_METHOD if any(m == QUOTE_METHOD for _, _, m in g) else DIALOGUE_METHOD
                kv.god = [(a, b, f"aligned from WEB ({method})") for a, b in subtract(carry_to(v, [[a, b] for a, b, _ in g], kv), kv.jesus)]
    for code, kvs in books["KJV"].items():
        for v in kvs:
            god = v.god
            spans = [(s, e, "Jesus", "red-letter markup") for s, e in v.jesus] + [(s, e, "God", m) for s, e, m in god]
            result["KJV"][(code, v.chapter, v.verse)] = dict(text=v.text, words=v.words, spans=sorted(spans))
    return result


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    res = build(Path(__file__).resolve().parent / "raw")
    for tid in ("WEB", "KJV"):
        n = {"Jesus": 0, "God": 0}
        for d in res[tid].values():
            for sp in {x[2] for x in d["spans"]}:
                n[sp] += 1
        print(tid, "verses with Jesus:", n["Jesus"], "with God:", n["God"])
    show = [("GEN", 1, 3), ("GEN", 3, 9), ("GEN", 3, 11), ("EXO", 3, 5), ("EXO", 20, 2), ("EXO", 20, 3), ("EXO", 4, 1), ("ISA", 1, 2), ("ISA", 1, 18),
            ("JER", 2, 2), ("HOS", 11, 1), ("MAT", 3, 17), ("MAT", 5, 3), ("JHN", 3, 16), ("HEB", 1, 5), ("ACT", 7, 3), ("REV", 21, 5), ("NUM", 12, 6), ("PSA", 2, 7), ("MAT", 22, 32),
            ("EXO", 3, 4), ("ACT", 7, 2), ("GEN", 22, 2), ("1SA", 3, 11), ("ISA", 6, 8), ("LUK", 3, 22), ("2KI", 20, 5), ("EXO", 14, 15), ("GEN", 4, 6), ("NUM", 22, 38)]
    for key in show:
        for tid in ("WEB", "KJV"):
            d = res[tid].get(key)
            if not d:
                continue
            t, out, last = d["text"], "", 0
            for s, e, sp, _ in d["spans"]:
                out += t[last:s] + ("[J:" if sp == "Jesus" else "[G:") + t[s:e] + "]"
                last = e
            print(f"{tid} {key}: {out + t[last:]}")

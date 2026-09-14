/* Plain-English descriptions of the grammar codes in STEPBible's tagged texts.
 *   Morph.describe('HC/Td/Ncfsa', 'OT')  -> "Conjunction + Definite article + Noun: feminine singular absolute"
 *   Morph.describe('V-AAI-3S', 'NT')     -> "Verb: aorist active indicative, 3rd person singular"
 * Hebrew/Aramaic codes follow the Open Scriptures Hebrew Bible scheme; Greek codes follow Robinson's scheme.
 * Unknown codes are returned unchanged. */
(function () {
  'use strict';
  const GEN = { m: 'masculine', f: 'feminine', b: 'masculine or feminine', c: 'common', n: 'neuter' };
  const NUM = { s: 'singular', p: 'plural', d: 'dual' };
  const STATE = { a: 'absolute', c: 'construct', d: 'determined' };
  const PER = { 1: '1st person', 2: '2nd person', 3: '3rd person' };
  const HEB_STEM = { q: 'Qal', N: 'Niphal', p: 'Piel', P: 'Pual', h: 'Hiphil', H: 'Hophal', t: 'Hithpael', o: 'Polel', O: 'Polal', r: 'Hithpolel', m: 'Poel', M: 'Poal', k: 'Palel', K: 'Pulal', Q: 'Qal passive', l: 'Pilpel', L: 'Polpal', f: 'Hithpalpel', D: 'Nithpael', j: 'Pealal', i: 'Pilel', u: 'Hothpaal', c: 'Tiphil', v: 'Hishtaphel', w: 'Nithpalel', y: 'Nithpoel', z: 'Hithpoel' };
  const ARAM_STEM = { q: 'Peal', Q: 'Peil', u: 'Hithpeel', p: 'Pael', P: 'Ithpaal', M: 'Hithpaal', a: 'Aphel', h: 'Haphel', s: 'Saphel', e: 'Shaphel', H: 'Hophal', i: 'Ithpeel', t: 'Hishtaphel', v: 'Ishtaphel', w: 'Hithaphel', o: 'Polel', z: 'Ithpoel', r: 'Hithpolel', f: 'Hithpalpel', b: 'Hephal', c: 'Tiphel', m: 'Poel', l: 'Palpel', L: 'Ithpalpel', O: 'Ithpolel', G: 'Ittaphal' };
  const ASPECT = { p: 'perfect', q: 'sequential perfect', i: 'imperfect', w: 'sequential imperfect', h: 'cohortative', j: 'jussive', v: 'imperative', r: 'active participle', s: 'passive participle', a: 'infinitive absolute', c: 'infinitive construct' };
  const ADJ = { a: 'Adjective', c: 'Number', g: 'Gentilic adjective', o: 'Ordinal number' };
  const PRON = { d: 'Demonstrative pronoun', f: 'Indefinite pronoun', i: 'Interrogative pronoun', p: 'Personal pronoun', r: 'Relative pronoun' };
  const PART = { a: 'Particle of affirmation', d: 'Definite article', e: 'Particle of exhortation', i: 'Interrogative particle', j: 'Interjection', m: 'Demonstrative particle', n: 'Negative particle', o: 'Direct object marker', r: 'Relative particle', c: 'Conjunctive particle' };
  const PROPER = { m: 'a man', f: 'a woman', l: 'a place', t: 'a title or group', g: 'a people group' };
  const join = (name, bits) => { const d = bits.filter(Boolean).join(' '); return d ? `${name}: ${d}` : name; };
  const pgn = r => [PER[r[0]], [GEN[r[1]], NUM[r[2]]].filter(Boolean).join(' ')].filter(Boolean).join(', ');

  function hebPart(p, aram) {
    const k = p[0], r = p.slice(1);
    switch (k) {
      case 'A': return join(ADJ[r[0]] || 'Adjective', [GEN[r[1]], NUM[r[2]], STATE[r[3]]]);
      case 'C': return 'Conjunction';
      case 'c': return 'Conjunction (sequential “and”)';
      case 'D': return 'Adverb';
      case 'N':
        if (r[0] === 'p') return PROPER[r[1]] ? `Proper name of ${PROPER[r[1]]}` : 'Proper name';
        return join(r[0] === 'g' ? 'Gentilic noun' : 'Noun', [GEN[r[1]], NUM[r[2]], STATE[r[3]]]);
      case 'P': return [PRON[r[0]] || 'Pronoun', pgn(r.slice(1))].filter(Boolean).join(': ');
      case 'R': return r[0] === 'd' ? 'Preposition with definite article' : 'Preposition';
      case 'S':
        if (r[0] === 'p') return `Pronoun suffix: ${pgn(r.slice(1))}`;
        return { d: 'Directional ending (“toward”)', h: 'Paragogic he', n: 'Paragogic nun' }[r[0]] || 'Suffix';
      case 'T': return PART[r[0]] || 'Particle';
      case 'V': {
        const stem = (aram ? ARAM_STEM : HEB_STEM)[r[0]], asp = ASPECT[r[1]], rest = r.slice(2);
        const head = ['Verb', [stem, asp].filter(Boolean).join(' ')].filter(Boolean).join(': ');
        if (!rest) return head;
        if (r[1] === 'r' || r[1] === 's') return `${head}, ${[GEN[rest[0]], NUM[rest[1]], STATE[rest[2]]].filter(Boolean).join(' ')}`;
        return `${head}, ${pgn(rest)}`;
      }
      default: return p;
    }
  }
  function hebrew(code) {
    const lang = code[0], parts = code.slice(1).split('/').filter(Boolean);
    if (!parts.length) return code;
    return (lang === 'A' ? 'Aramaic. ' : '') + parts.map(p => hebPart(p, lang === 'A')).join(' + ');
  }

  const CASE = { N: 'nominative', G: 'genitive', D: 'dative', A: 'accusative', V: 'vocative' };
  const GNUM = { S: 'singular', P: 'plural' };
  const GGEN = { M: 'masculine', F: 'feminine', N: 'neuter' };
  const TENSE = { P: 'present', I: 'imperfect', F: 'future', A: 'aorist', R: 'perfect', L: 'pluperfect' };
  const VOICE = { A: 'active', M: 'middle', P: 'passive', E: 'middle or passive', D: 'middle', O: 'passive', N: 'middle or passive', Q: 'impersonal active', X: '' };
  const MOOD = { I: 'indicative', S: 'subjunctive', O: 'optative', M: 'imperative', N: 'infinitive', P: 'participle', R: 'participle with imperative sense' };
  const WORD = { ADV: 'Adverb', CONJ: 'Conjunction', PREP: 'Preposition', PRT: 'Particle', INJ: 'Interjection', COND: 'Conditional particle', HEB: 'Hebrew word', ARAM: 'Aramaic word' };
  const SUF = { N: 'negative', I: 'interrogative', P: 'proper name', T: 'title', L: 'place', G: 'gentilic', C: 'contracted form', ATT: 'Attic form', S: 'superlative', K: 'crasis', ABB: 'abbreviated', LI: 'letter', PRI: 'proper name, indeclinable', NUI: 'number, indeclinable', OI: 'indeclinable' };
  const PRONOUN = { R: 'Relative pronoun', D: 'Demonstrative pronoun', C: 'Reciprocal pronoun', K: 'Correlative pronoun', I: 'Interrogative pronoun', X: 'Indefinite pronoun', Q: 'Correlative or interrogative pronoun' };
  const cng = s => [CASE[s[0]], GNUM[s[1]], GGEN[s[2]]].filter(Boolean).join(' ');

  function greek(code) {
    if (code.includes(' + ')) return code.split(' + ').map(p => greek(p.includes('=') ? p.split('=').pop() : p)).join(' + ');
    const [h, a = '', b = ''] = code.split('-');
    const tail = s => (SUF[s] ? ` (${SUF[s]})` : '');
    if (WORD[h]) return WORD[h] + tail(a);
    switch (h) {
      case 'N': return SUF[a] ? `Noun${tail(a)}` : join('Noun', [cng(a)]) + tail(b);
      case 'A': return SUF[a] ? `Adjective${tail(a)}` : join('Adjective', [cng(a)]) + tail(b);
      case 'T': return join('Definite article', [cng(a)]);
      case 'P': return /^\d/.test(a) ? `Personal pronoun: ${PER[a[0]]}, ${[CASE[a[1]], GNUM[a[2]]].filter(Boolean).join(' ')}` : join('Pronoun (he, she, it)', [cng(a)]) + tail(b);
      case 'F': return /^\d/.test(a) ? `Reflexive pronoun: ${PER[a[0]]}, ${cng(a.slice(1))}` : join('Reflexive pronoun', [cng(a)]);
      case 'S': return /^\d/.test(a) ? `Possessive pronoun (${PER[a[0]]} ${GNUM[a[1]] || ''}): ${cng(a.slice(2))}` : join('Possessive pronoun', [cng(a)]);
      case 'V': {
        const m = a.match(/^(2?)([PIFARL])([AMPEDONQX])([ISOMNPR])$/);
        if (!m) return `Verb${a ? ' ' + a : ''}`;
        const desc = [(m[1] ? 'second ' : '') + TENSE[m[2]], VOICE[m[3]], MOOD[m[4]]].filter(Boolean).join(' ');
        if (m[4] === 'N') return `Verb: ${desc}`;
        if (m[4] === 'P' || m[4] === 'R') return `Verb: ${desc}, ${cng(b)}`;
        return `Verb: ${desc}${b ? `, ${PER[b[0]] || ''} ${GNUM[b[1]] || ''}`.trimEnd() : ''}`;
      }
      default:
        if (PRONOUN[h]) return join(PRONOUN[h], [cng(a)]) + tail(b);
        return code;
    }
  }

  window.Morph = {
    describe(code, testament) {
      if (!code) return '';
      try { return testament === 'OT' ? hebrew(code) : greek(code); } catch (_) { return code; }
    },
  };
})();

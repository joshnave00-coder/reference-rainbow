"""Fast checks that need no downloaded data: python -m unittest discover -s tests -v"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bibledb"))

import book_origins  # noqa: E402
import phrases  # noqa: E402
import red_letter  # noqa: E402


class PhraseTests(unittest.TestCase):
    def test_repeated_run_is_found_once_at_full_length(self):
        keys = list("abcdefg") + ["x", "y", "z"] + list("abcdefg") + ["q"]
        stats, repeats = phrases.find_repeats(keys, [1] * len(keys))
        self.assertEqual(stats, [(7, 1, 2)])
        self.assertEqual(repeats, [(7, [0, 10])])

    def test_phrases_do_not_cross_books(self):
        keys = list("abcdefg") * 2
        books = [1] * 10 + [2] * 4
        stats, repeats = phrases.find_repeats(keys, books)
        self.assertEqual(repeats, [])

    def test_normalisation_ignores_points_and_accents(self):
        self.assertEqual(phrases.norm_hebrew("בְּרֵאשִׁ֖ית"), phrases.norm_hebrew("בראשית"))
        self.assertEqual(phrases.norm_greek("Χριστοῦ,"), phrases.norm_greek("χριστου"))

    def test_greek_transliteration(self):
        for greek, roman in [("Χριστοῦ", "Christou"), ("ἁμαρτία", "hamartia"), ("εὐαγγέλιον", "euangelion"),
                             ("Ἰησοῦ", "Iēsou"), ("οὗτος", "houtos"), ("ῥῆμα", "rhēma"), ("Ἁβραάμ", "Habraam")]:
            self.assertEqual(phrases.translit_greek(greek), roman)

    def test_stepbible_transliteration_cleanup(self):
        self.assertEqual(phrases.clean_step_translit("be./re.Shit"), "bereshit")


class RedLetterTests(unittest.TestCase):
    @staticmethod
    def verses(*texts):
        out = []
        for i, t in enumerate(texts, 1):
            v = red_letter.Verse(1, i, True)
            v.add(t)
            v.finish()
            out.append(v)
        return out

    def test_god_said_is_detected(self):
        vs = self.verses("God said, “Let there be light,” and there was light.")
        spans = red_letter.detect_god(vs)[0]
        self.assertEqual([vs[0].text[s:e] for s, e, _ in spans], ["Let there be light"])

    def test_human_speech_is_not_marked(self):
        vs = self.verses("Moses said to the people, “Don’t be afraid.”")
        self.assertEqual(red_letter.detect_god(vs), {})


class EnglishTextTests(unittest.TestCase):
    def test_extra_translations_are_openly_licensed(self):
        import english_texts
        ids = [t["id"] for t in english_texts.EBIBLE_ENGLISH]
        self.assertEqual(len(ids), len(set(ids)))
        for t in english_texts.EBIBLE_ENGLISH:
            self.assertIn(t["license"], {"Public Domain", "CC BY 4.0", "CC BY-SA 4.0"}, t["id"])
            self.assertTrue(t["attribution"], t["id"])


class BookOriginTests(unittest.TestCase):
    def test_all_books_have_cited_views(self):
        self.assertEqual(len(book_origins.ORIGINS), 66)
        for osis, info in book_origins.ORIGINS.items():
            self.assertIn(info["consensus"], book_origins.CONSENSUS_NOTE, osis)
            self.assertTrue(info["views"], osis)
            for view in info["views"]:
                self.assertLessEqual(view["date_from"], view["date_to"], osis)
                for source_id, _ in view["sources"]:
                    self.assertIn(source_id, book_origins.SOURCES, osis)


if __name__ == "__main__":
    unittest.main()

import unittest

from normalization_engine import normalize_text, normalize_word


class NormalizationEngineTests(unittest.TestCase):
    def test_glosses_known_romanized_words(self):
        self.assertEqual(normalize_text("Aaje mara project ma problem che"), "today my project in problem is")

    def test_unknown_words_are_lowercased(self):
        self.assertEqual(normalize_word("Python,"), "python")


if __name__ == "__main__":
    unittest.main()

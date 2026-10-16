import unittest

from codemix_engine import analyze_text, calculate_cmis, detect_language


class CodeMixEngineTests(unittest.TestCase):
    def test_detects_romanized_languages_and_switches(self):
        result = analyze_text("Aaje lecture boring che but sir explained it")

        self.assertEqual(result["total_words"], 8)
        self.assertEqual(result["distribution"]["Gujarati"], 25.0)
        self.assertEqual(result["distribution"]["English"], 75.0)
        self.assertEqual(result["switching_count"], 3)
        self.assertEqual(result["transliterated_words"], ["aaje", "che"])

    def test_hindi_detection_and_empty_input(self):
        self.assertEqual(detect_language("Mujhe,"), "Hindi")
        self.assertIn("error", analyze_text(" \n "))

    def test_cmis_is_bounded_and_zero_for_empty_text(self):
        self.assertEqual(calculate_cmis({}, 0, 0, 0), 0.0)
        result = analyze_text("Mujhe Python project banana hai.")
        self.assertGreaterEqual(result["cmis"], 0)
        self.assertLessEqual(result["cmis"], 100)


if __name__ == "__main__":
    unittest.main()

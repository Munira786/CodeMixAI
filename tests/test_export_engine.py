import csv
import io
import json
import unittest

from codemix_engine import analyze_text
from export_engine import (
    analysis_to_csv,
    analysis_to_json,
    analyses_to_csv,
    evaluation_to_csv,
)


class ExportEngineTests(unittest.TestCase):
    def setUp(self):
        self.analysis = analyze_text("Aaje Python project che.")

    def test_json_export_contains_analysis_without_credentials(self):
        payload = json.loads(analysis_to_json(self.analysis))
        self.assertEqual(payload["text"], self.analysis["text"])
        self.assertNotIn("GOOGLE_API_KEY", analysis_to_json(self.analysis))

    def test_csv_export_has_expected_values(self):
        rows = list(csv.DictReader(io.StringIO(analysis_to_csv(self.analysis))))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["total_words"], "4")
        self.assertEqual(rows[0]["cmis"], str(self.analysis["cmis"]))

    def test_history_csv_exports_each_result(self):
        result = analyze_text("Mujhe help chahiye.")
        rows = list(
            csv.DictReader(io.StringIO(analyses_to_csv([self.analysis, result])))
        )
        self.assertEqual(len(rows), 2)

    def test_evaluation_csv_exports_reference_and_prediction(self):
        records = [
            {
                "id": 1,
                "text": "Aaje test che",
                "expected": "English, Gujarati",
                "detected": "English, Gujarati",
                "exact_match": True,
                "cmis": 50.0,
                "switches": 2,
                "english_percentage": 50.0,
                "gujarati_percentage": 50.0,
                "hindi_percentage": 0.0,
            }
        ]
        row = next(csv.DictReader(io.StringIO(evaluation_to_csv(records))))
        self.assertEqual(row["expected"], "English, Gujarati")
        self.assertEqual(row["detected"], "English, Gujarati")
        self.assertEqual(row["exact_match"], "True")


if __name__ == "__main__":
    unittest.main()

import unittest

from evaluation_engine import evaluate_dataset


class EvaluationEngineTests(unittest.TestCase):
    def test_dataset_metrics_use_sentence_level_reference_labels(self):
        result = evaluate_dataset()

        self.assertEqual(len(result["records"]), 8)
        for metric in (
            "exact_match_accuracy",
            "precision",
            "recall",
            "f1",
        ):
            self.assertGreaterEqual(result[metric], 0)
            self.assertLessEqual(result[metric], 1)
        self.assertEqual(
            set(result["confusion_matrices"]),
            {"English", "Gujarati", "Hindi"},
        )
        self.assertTrue(
            all(
                matrix.shape == (2, 2)
                for matrix in result["confusion_matrices"].values()
            )
        )


if __name__ == "__main__":
    unittest.main()

import unittest

from security_engine import MAX_TEXT_LENGTH, validate_input


class SecurityEngineTests(unittest.TestCase):
    def test_rejects_empty_and_non_text_input(self):
        self.assertFalse(validate_input("  ")["valid"])
        self.assertFalse(validate_input(None)["valid"])
        self.assertFalse(validate_input(42)["valid"])

    def test_accepts_limit_and_rejects_above_limit(self):
        self.assertTrue(validate_input("a" * MAX_TEXT_LENGTH)["valid"])
        result = validate_input("a" * (MAX_TEXT_LENGTH + 1))
        self.assertFalse(result["valid"])
        self.assertIn(str(MAX_TEXT_LENGTH), result["message"])


if __name__ == "__main__":
    unittest.main()

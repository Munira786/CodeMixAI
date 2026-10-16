import unittest
from unittest.mock import patch

from ai_engine import generate_response


class AIEngineTests(unittest.TestCase):
    def test_missing_api_key_returns_useful_message_without_client_creation(self):
        with (
            patch("ai_engine.get_google_api_key", return_value=None),
            patch("ai_engine._create_model") as create_model,
        ):
            result = generate_response("Hello")

        self.assertFalse(result["success"])
        self.assertIn("GOOGLE_API_KEY", result["response"])
        create_model.assert_not_called()


if __name__ == "__main__":
    unittest.main()

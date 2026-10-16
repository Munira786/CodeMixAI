import unittest
from unittest.mock import patch

from ngrok_engine import start_ngrok, stop_ngrok


class NgrokEngineTests(unittest.TestCase):
    def test_missing_token_does_not_start_a_tunnel(self):
        with patch("ngrok_engine.get_ngrok_auth_token", return_value=None):
            with self.assertRaisesRegex(ValueError, "NGROK_AUTHTOKEN"):
                start_ngrok()

    def test_stopping_when_no_tunnel_is_active_is_safe(self):
        stop_ngrok()


if __name__ == "__main__":
    unittest.main()

"""Local environment configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parent
ENV_FILE = PROJECT_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=False)


def get_google_api_key() -> str | None:
    value = os.getenv("GOOGLE_API_KEY", "").strip()
    if not value or value.lower().startswith("your_"):
        return None
    return value


def get_ngrok_auth_token() -> str | None:
    value = os.getenv("NGROK_AUTHTOKEN", "").strip()
    if not value or value.lower().startswith("your_"):
        return None
    return value


def get_gemini_model() -> str:
    value = os.getenv("GEMINI_MODEL", "").strip()
    return value or "gemini-3.8-flash"

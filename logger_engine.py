"""Lazy file logging that never records message contents or credentials."""

import logging
from pathlib import Path

from config import PROJECT_DIR


LOG_FILE = PROJECT_DIR / "codemixai.log"
_LOGGER = logging.getLogger("CodeMixAI")
_LOGGER.setLevel(logging.INFO)
_LOGGER.propagate = False


def _get_logger() -> logging.Logger:
    if not _LOGGER.handlers:
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        _LOGGER.addHandler(handler)
    return _LOGGER


def log_analysis(text: str) -> None:
    _get_logger().info("Text analyzed. Length=%d", len(text))


def log_error(error: BaseException) -> None:
    _get_logger().error("Application error: %s", type(error).__name__)

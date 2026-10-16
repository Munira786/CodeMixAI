"""Explicit user-triggered conversation export."""

import json
from collections.abc import Sequence
from typing import Any


def export_chat(messages: Sequence[dict[str, Any]]) -> str:
    """Serialize only the supplied chat messages as UTF-8-friendly JSON."""
    return json.dumps(list(messages), indent=2, ensure_ascii=False)

"""Orchestration that keeps local NLP independent from Gemini availability."""

from typing import Any

from ai_engine import generate_response
from codemix_engine import analyze_text


def smart_analyze(
    text: str,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    analysis = analyze_text(text)
    if "error" in analysis:
        return {
            "analysis": analysis,
            "ai_response": analysis["error"],
            "ai_available": False,
        }

    ai_result = generate_response(text, history)
    return {
        "analysis": analysis,
        "ai_response": ai_result["response"],
        "ai_available": ai_result["success"],
    }

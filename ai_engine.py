"""Lazy LangChain integration for Gemini chat and structured analysis."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from config import get_gemini_model, get_google_api_key
from error_handler import safe_error_message
from logger_engine import log_error


SYSTEM_PROMPT = """You are CodeMixAI, a conversational assistant specialized in code-mixed Indian languages.
Understand Gujarati-English, Hindi-English, Hinglish, Romanized Gujarati,
Romanized Hindi, and normal English. Do not assume every Roman-script word is
English. Respond naturally, maintain conversation context, and give practical
examples for technical questions. Do not unnecessarily translate the user's
message."""

STRUCTURED_SYSTEM_PROMPT = """You are CodeMixAI, a specialized system for
understanding code-mixed Indian languages, especially Gujarati-English,
Hindi-English, Hinglish, and Romanized Gujarati or Hindi. Use the surrounding
context; do not assume every Roman-script token is English. Analyze only what
the text supports. Estimate language distributions and switching points,
provide approximate English glosses, sentiment, intent, emotion, and a short
explanation. Be explicit in the explanation when the local evidence is
uncertain. Return the requested structured format."""


class GeminiConfigurationError(RuntimeError):
    """Raised when a requested Gemini feature has no local API key."""


@lru_cache(maxsize=2)
def _create_model(api_key: str, model_name: str) -> Any:
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.7,
        timeout=30,
        max_retries=1,
    )


def _get_model() -> Any:
    api_key = get_google_api_key()
    if not api_key:
        raise GeminiConfigurationError(
            "Gemini is not configured. Add GOOGLE_API_KEY to your local .env file."
        )
    return _create_model(api_key, get_gemini_model())


@lru_cache(maxsize=1)
def _structured_schema() -> type:
    from pydantic import BaseModel, Field

    class WordAnalysis(BaseModel):
        word: str = Field(description="Original word from the input text")
        language: str = Field(
            description="English, Gujarati, Hindi, or Other"
        )
        normalized: str = Field(description="Approximate English meaning")

    class CodeMixAnalysis(BaseModel):
        original_text: str
        detected_languages: list[str]
        language_distribution: dict[str, float]
        code_mixing_level: str
        switching_points: int
        word_analysis: list[WordAnalysis]
        normalized_text: str
        sentiment: str
        intent: str
        emotion: str
        explanation: str

    return CodeMixAnalysis


def _response_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
        if parts:
            return "\n".join(parts)
    return str(content)


def generate_response(
    user_message: str,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Generate a Gemini chat response, retaining history only in the caller."""
    if not user_message or not user_message.strip():
        return {"success": False, "response": "Please enter a message."}
    if not get_google_api_key():
        return {
            "success": False,
            "response": (
                "Gemini is not configured. Add GOOGLE_API_KEY to your local "
                ".env file."
            ),
        }

    try:
        from langchain_core.messages import AIMessage, HumanMessage
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        past_messages = []
        for item in history or []:
            if item.get("role") == "user":
                past_messages.append(HumanMessage(content=item["content"]))
            elif item.get("role") == "assistant":
                past_messages.append(AIMessage(content=item["content"]))

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )
        response = (prompt | _get_model()).invoke(
            {"history": past_messages, "input": user_message}
        )
        return {"success": True, "response": _response_text(response.content)}
    except Exception as error:
        log_error(error)
        return {"success": False, "response": safe_error_message(error)}


def analyze_code_mixed_text(text: str) -> Any:
    """Request the notebook's optional Pydantic-structured Gemini analysis."""
    if not text or not text.strip():
        raise ValueError("Please enter some text.")
    if not get_google_api_key():
        raise GeminiConfigurationError(
            "Gemini is not configured. Add GOOGLE_API_KEY to your local .env file."
        )

    try:
        from langchain_core.prompts import ChatPromptTemplate

        structured_schema = _structured_schema()
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", STRUCTURED_SYSTEM_PROMPT),
                ("human", "Analyze this text:\n\n{text}"),
            ]
        )
        chain = prompt | _get_model().with_structured_output(structured_schema)
        return chain.invoke({"text": text})
    except GeminiConfigurationError:
        raise
    except Exception as error:
        log_error(error)
        raise RuntimeError(safe_error_message(error)) from error

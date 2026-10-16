"""Helpers for short, per-session conversational histories."""

MAX_MESSAGES = 20


def add_message(messages: list[dict[str, str]], role: str, content: str) -> list[dict[str, str]]:
    if role not in {"user", "assistant"}:
        raise ValueError("role must be 'user' or 'assistant'")
    messages.append({"role": role, "content": content})
    if len(messages) > MAX_MESSAGES:
        del messages[: len(messages) - MAX_MESSAGES]
    return messages


def clear_memory() -> list[dict[str, str]]:
    return []

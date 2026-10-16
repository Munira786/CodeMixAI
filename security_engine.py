"""Validation for user-provided text."""

MAX_TEXT_LENGTH = 5000


def validate_input(text: object) -> dict[str, object]:
    if text is None or not isinstance(text, str):
        return {"valid": False, "message": "Input must be text."}
    if not text.strip():
        return {"valid": False, "message": "Please enter some text."}
    if len(text) > MAX_TEXT_LENGTH:
        return {
            "valid": False,
            "message": (
                f"Text is too long. Maximum allowed length is "
                f"{MAX_TEXT_LENGTH} characters."
            ),
        }
    return {"valid": True, "message": "Input is valid."}

"""Safe, user-facing error messages for optional external services."""


def safe_error_message(error: BaseException) -> str:
    error_text = str(error).lower()
    if "429" in error_text or "resource_exhausted" in error_text or "quota" in error_text:
        return "Gemini quota is currently exhausted. Please try again later."
    if "401" in error_text or "unauthorized" in error_text:
        return "Gemini authentication failed. Check GOOGLE_API_KEY in your .env file."
    if "403" in error_text or "permission" in error_text:
        return "Gemini access was denied. Check your API key and API access."
    if "timeout" in error_text or "timed out" in error_text:
        return "The Gemini request timed out. Please try again."
    return f"The AI service request failed ({type(error).__name__})."

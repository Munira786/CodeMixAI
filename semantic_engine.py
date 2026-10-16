"""Small local word-list heuristics for sentiment and intent."""


def _clean_word(word: str) -> str:
    return word.lower().strip(".,!?;:'\"()[]{}<>|/\\")


POSITIVE_WORDS = {
    "good", "great", "awesome", "nice", "excellent", "happy", "love",
    "like", "saras", "accha", "achha", "mast",
}
NEGATIVE_WORDS = {
    "bad", "boring", "sad", "angry", "hate", "problem", "error", "fail",
    "nathi", "bored",
}
QUESTION_WORDS = {
    "what", "why", "how", "when", "where", "kya", "kyun", "kaise", "shu",
    "kem",
}


def detect_sentiment(text: str) -> str:
    words = [_clean_word(word) for word in text.split()]
    positive = sum(word in POSITIVE_WORDS for word in words)
    negative = sum(word in NEGATIVE_WORDS for word in words)
    if positive > negative:
        return "Positive"
    if negative > positive:
        return "Negative"
    return "Neutral"


def detect_intent(text: str) -> str:
    words = {_clean_word(word) for word in text.split()}
    if words.intersection(QUESTION_WORDS):
        return "Question"
    if "help" in words:
        return "Help Request"
    if "error" in words:
        return "Technical Problem"
    if "project" in words:
        return "Project Related"
    return "General Conversation"

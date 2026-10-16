"""Rule-based analysis for Romanized Gujarati/Hindi and English text."""

from __future__ import annotations

from typing import Any

from semantic_engine import detect_intent, detect_sentiment


GUJARATI_WORDS = {
    "aaje", "aavse", "aavya", "aavyu", "che", "chhe", "chu", "hato",
    "hati", "hatu", "bahu", "saru", "saras", "nathi", "mane", "mari",
    "mara", "maru", "tame", "tamne", "tamaro", "tamari", "shu", "su",
    "kem", "kya", "ane", "pan", "ma", "thi", "mate", "karvu", "karvanu",
    "karo", "kari", "javu", "javanu", "jaavu", "game", "gamtu", "gamy",
    "thayu", "thase", "hase", "hoy", "karyu", "kare", "karta", "karine",
    "levu", "levanu", "aavvu", "aavanu", "college", "assignment", "submit",
    "joiye", "joiye", "aave", "aavse",
}

HINDI_WORDS = {
    "mujhe", "mujhko", "mujh", "mera", "meri", "mere", "hum", "hamara",
    "tum", "tumhara", "tumhari", "aap", "aapka", "aapki", "kya", "kyun",
    "kyunki", "nahi", "nahin", "hai", "hain", "tha", "thi", "the",
    "bahut", "accha", "achha", "aaj", "kal", "kaise", "karna", "karni",
    "karo", "jaana", "jana", "jao", "raha", "rahi", "rahe", "chahiye",
    "lagta", "lagti", "ho", "hona", "hoga", "ka", "ki", "ke", "ko", "se",
    "par", "liye", "phir", "abhi", "sab", "kuch", "mera", "meri",
}

LANGUAGES = ("English", "Gujarati", "Hindi")
_PUNCTUATION = ".,!?;:'\"()[]{}<>|/\\"


def clean_word(word: str) -> str:
    """Lowercase a token and remove punctuation around its edges."""
    return word.lower().strip(_PUNCTUATION)


def detect_language(word: str) -> str:
    """Classify a token using the notebook's local vocabulary lists."""
    cleaned = clean_word(word)
    if cleaned in GUJARATI_WORDS:
        return "Gujarati"
    if cleaned in HINDI_WORDS:
        return "Hindi"
    return "English"


def calculate_cmis(
    language_distribution: dict[str, float],
    switching_points: int,
    total_words: int,
    transliterated_words: int,
) -> float:
    """Calculate the notebook's proposed 0-100 CMIS score."""
    if total_words <= 0:
        return 0.0

    active_languages = sum(
        percentage > 0 for percentage in language_distribution.values()
    )
    diversity_score = min(active_languages / 3, 1) * 30
    switching_ratio = switching_points / max(total_words - 1, 1)
    switching_score = min(switching_ratio, 1) * 30
    transliteration_ratio = transliterated_words / total_words
    transliteration_score = min(transliteration_ratio, 1) * 20

    percentages = [
        percentage
        for percentage in language_distribution.values()
        if percentage > 0
    ]
    balance_score = 0.0
    if len(percentages) >= 2:
        maximum = max(percentages)
        if maximum > 0:
            balance_score = min(percentages) / maximum * 20

    return round(
        min(
            diversity_score
            + switching_score
            + transliteration_score
            + balance_score,
            100,
        ),
        2,
    )


def analyze_text(text: str) -> dict[str, Any]:
    """Return local word, distribution, switching, and CMIS analysis."""
    if not isinstance(text, str) or not text.strip():
        return {"error": "Please enter some text."}

    words = text.split()
    languages = [detect_language(word) for word in words]
    counts = {language: 0 for language in LANGUAGES}
    transliterated: list[str] = []

    for word, language in zip(words, languages):
        counts[language] += 1
        if language in {"Gujarati", "Hindi"}:
            transliterated.append(clean_word(word))

    total_words = len(words)
    distribution = {
        language: round(count / total_words * 100, 2)
        for language, count in counts.items()
    }
    switches = [
        {
            "position": index + 1,
            "from": languages[index - 1],
            "to": languages[index],
            "word": words[index],
        }
        for index in range(1, total_words)
        if languages[index] != languages[index - 1]
    ]
    clean_words = [clean_word(word) for word in words]
    unique_words = len(set(clean_words))
    cmis = calculate_cmis(
        language_distribution=distribution,
        switching_points=len(switches),
        total_words=total_words,
        transliterated_words=len(transliterated),
    )
    if cmis < 25:
        cmis_level = "Low"
    elif cmis < 50:
        cmis_level = "Moderate"
    elif cmis < 75:
        cmis_level = "High"
    else:
        cmis_level = "Very High"

    return {
        "text": text,
        "words": words,
        "total_words": total_words,
        "characters": len(text),
        "unique_words": unique_words,
        "average_word_length": round(
            sum(len(word) for word in clean_words) / total_words, 2
        ),
        "distribution": distribution,
        "language_sequence": languages,
        "transliterated_words": transliterated,
        "switches": switches,
        "switching_count": len(switches),
        "switching_density": round(
            len(switches) / max(total_words - 1, 1), 3
        ),
        "lexical_diversity": round(unique_words / total_words, 3),
        "dominant_language": max(counts, key=counts.get),
        "mixing_score": round(
            (counts["Gujarati"] + counts["Hindi"]) / total_words * 100, 2
        ),
        "cmis": cmis,
        "cmis_level": cmis_level,
        "sentiment": detect_sentiment(text),
        "intent": detect_intent(text),
    }

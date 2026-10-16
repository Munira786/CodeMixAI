"""Dictionary-based glosses for Romanized Gujarati and Hindi tokens."""

from codemix_engine import clean_word


GUJARATI_NORMALIZATION = {
    "aaje": "today",
    "mane": "I",
    "mara": "my",
    "mari": "my",
    "maru": "my",
    "tame": "you",
    "tamne": "you",
    "tamaro": "your",
    "tamari": "your",
    "che": "is",
    "chhe": "is",
    "chu": "am",
    "bahu": "very",
    "saru": "good",
    "saras": "good",
    "nathi": "not",
    "ane": "and",
    "pan": "but",
    "ma": "in",
    "thi": "from",
    "mate": "for",
    "kem": "why",
    "shu": "what",
    "su": "what",
    "karvu": "to do",
    "karvanu": "to do",
    "karo": "do",
    "kari": "did",
    "javu": "to go",
    "javanu": "to go",
    "game": "like",
    "thayu": "happened",
    "thase": "will happen",
}

HINDI_NORMALIZATION = {
    "mujhe": "I",
    "mujhko": "I",
    "mujh": "me",
    "mera": "my",
    "meri": "my",
    "mere": "my",
    "tum": "you",
    "tumhara": "your",
    "tumhari": "your",
    "aap": "you",
    "aapka": "your",
    "aapki": "your",
    "kya": "what",
    "kyun": "why",
    "kyunki": "because",
    "nahi": "not",
    "nahin": "not",
    "hai": "is",
    "hain": "are",
    "bahut": "very",
    "accha": "good",
    "achha": "good",
    "aaj": "today",
    "kal": "tomorrow",
    "kaise": "how",
    "karna": "to do",
    "karni": "to do",
    "karo": "do",
    "jaana": "go",
    "jana": "go",
    "jao": "go",
    "raha": "doing",
    "rahi": "doing",
    "rahe": "doing",
    "chahiye": "need",
    "lagta": "seems",
    "lagti": "seems",
    "ka": "of",
    "ki": "of",
    "ke": "of",
    "ko": "to",
    "se": "from",
    "par": "on",
    "liye": "for",
    "phir": "then",
    "abhi": "now",
}


def normalize_word(word: str) -> str:
    """Return a dictionary gloss or the lowercased token."""
    cleaned = clean_word(word)
    return GUJARATI_NORMALIZATION.get(
        cleaned,
        HINDI_NORMALIZATION.get(cleaned, cleaned),
    )


def normalize_text(text: str) -> str:
    """Produce the notebook's simple token-by-token English gloss."""
    return " ".join(normalize_word(word) for word in text.split())

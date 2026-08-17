"""
Language filter — keeps English and Hinglish (Hindi-English code-mixed),
drops pure Hindi (Devanagari), and other non-Latin scripts.
"""

import re
from typing import Optional


# Devanagari unicode range
DEVANAGARI_RE = re.compile(r'[\u0900-\u097F]')

# Latin characters (English + romanized Hindi)
LATIN_RE = re.compile(r'[a-zA-Z]')

# Common Hinglish words (romanized Hindi frequently used in reviews)
HINGLISH_MARKERS = {
    "accha", "bahut", "koi", "nahi", "hai", "nhi", "hota", "kya",
    "acha", "bhi", "toh", "tha", "mein", "mera", "mere", "bohot",
    "sab", "kuch", "karo", "karega", "wala", "wali", "yaar", "bhai",
    "didi", "arrey", "arre", "dekho", "dekha", "paisa", "liya", "diya",
    "karke", "hogaya", "hogya", "milta", "milti", "gaya", "gayi",
    "sahi", "galat", "bakwas", "mazaa", "maza", "jaldi", "abhi",
    "lekin", "kyunki", "isliye", "waise", "achha", "theek", "thik",
    "pehle", "baad", "zyada", "kam", "pasand", "bekar", "ghatiya",
    "kapda", "kapde", "size", "fitting", "chhota", "bada",
    "ye", "wo", "yeh", "woh", "aur", "par", "pe", "se", "ka", "ki", "ke",
    "haan", "nahin", "mat", "saste", "mehnga", "achhi", "bura",
}


def detect_language(text: str) -> str:
    """
    Classify text language as 'english', 'hinglish', 'hindi', or 'other'.
    
    Hinglish = Roman script containing Hindi-origin words.
    Hindi = predominantly Devanagari script.
    """
    if not text or len(text.strip()) < 3:
        return "unknown"

    text_lower = text.lower()
    words = text_lower.split()

    # Count script types
    devanagari_chars = len(DEVANAGARI_RE.findall(text))
    latin_chars = len(LATIN_RE.findall(text))
    total_alpha = devanagari_chars + latin_chars

    if total_alpha == 0:
        return "unknown"

    devanagari_ratio = devanagari_chars / total_alpha

    # If >50% Devanagari, it's Hindi
    if devanagari_ratio > 0.5:
        return "hindi"

    # If predominantly Latin, check for Hinglish markers
    if latin_chars > 0:
        hinglish_count = sum(1 for w in words if w in HINGLISH_MARKERS)
        hinglish_ratio = hinglish_count / max(len(words), 1)

        if hinglish_ratio > 0.1:
            return "hinglish"

        # Also check with langdetect for non-English Latin scripts
        try:
            from langdetect import detect
            detected = detect(text)
            if detected == "hi":
                return "hinglish"  # Romanized Hindi detected by langdetect
            elif detected in ("en", "id", "ms"):
                # langdetect sometimes misclassifies Hinglish as Indonesian/Malay
                # If it has Hinglish markers, keep it
                if hinglish_count > 0:
                    return "hinglish"
                return "english"
            elif detected in ("fr", "de", "es", "pt", "it", "nl"):
                return "other"
            else:
                return "english"  # Default to English for ambiguous Latin
        except Exception:
            return "english"  # Default if langdetect fails

    return "unknown"


def should_keep(text: str) -> bool:
    """Return True if the text should be kept (English or Hinglish)."""
    lang = detect_language(text)
    return lang in ("english", "hinglish")


def filter_documents(docs: list) -> tuple:
    """
    Filter a list of document dicts, keeping English and Hinglish.
    
    Returns:
        (kept_docs, dropped_count)
    """
    kept = []
    dropped = 0

    for doc in docs:
        content = doc.get("content", "")
        if should_keep(content):
            kept.append(doc)
        else:
            dropped += 1

    return kept, dropped

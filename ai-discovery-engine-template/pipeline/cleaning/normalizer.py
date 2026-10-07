"""
Text normalization utilities.
Cleans raw text into a standardized format for downstream classification.
"""

import re
import unicodedata

import emoji


def normalize_text(text: str) -> str:
    """
    Full normalization pipeline for a single text string.
    
    Steps:
    1. Unicode normalization (NFKC)
    2. Convert emojis to text labels
    3. Strip URLs
    4. Strip email addresses
    5. Normalize whitespace
    6. Strip HTML tags
    7. Remove excessive punctuation
    """
    if not text:
        return ""

    # 1. Unicode normalization
    text = unicodedata.normalize("NFKC", text)

    # 2. Convert emojis to text (e.g., 👍 → :thumbs_up:)
    text = emoji.demojize(text, delimiters=(" ", " "))

    # 3. Strip URLs
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)

    # 4. Strip email addresses
    text = re.sub(r'\S+@\S+\.\S+', '', text)

    # 5. Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # 6. Remove excessive punctuation (3+ of the same character)
    text = re.sub(r'([!?.]){3,}', r'\1\1', text)
    text = re.sub(r'([*#_~]){2,}', '', text)

    # 7. Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def normalize_document(doc: dict) -> dict:
    """Normalize the text fields of a document dict."""
    doc = doc.copy()
    if "content" in doc:
        doc["content"] = normalize_text(doc["content"])
    if "title" in doc and doc["title"]:
        doc["title"] = normalize_text(doc["title"])
    return doc

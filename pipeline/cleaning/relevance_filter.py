"""
Relevance filter — keeps documents that contain fashion/shopping/Myntra signals.
Drops pure noise (tech support, unrelated topics).
"""

import re
from typing import List, Tuple


# Keywords that indicate fashion/shopping relevance
FASHION_KEYWORDS = {
    # Brand & platform
    "myntra", "ajio", "meesho", "nykaa", "flipkart", "amazon", "h&m",
    "zara", "shein", "tatacliq", "jabong",
    
    # Clothing & fashion terms
    "dress", "shirt", "tshirt", "t-shirt", "kurti", "kurta", "saree",
    "sari", "jeans", "trouser", "pant", "legging", "jacket", "hoodie",
    "sweater", "top", "blouse", "skirt", "shorts", "lehenga", "suit",
    "ethnic", "western", "casual", "formal", "party", "wedding",
    "outfit", "wear", "clothing", "clothes", "apparel", "garment",
    "fashion", "style", "trend", "collection", "brand", "designer",
    "footwear", "shoes", "sneaker", "heels", "sandal", "slipper",
    "watch", "accessory", "accessories", "bag", "handbag", "sunglasses",
    "jewellery", "jewelry", "earring", "necklace", "bracelet",
    
    # Shopping terms
    "wishlist", "cart", "order", "buy", "purchase", "shop", "shopping",
    "sale", "discount", "offer", "coupon", "code", "deal", "price",
    "delivery", "shipping", "return", "refund", "exchange", "cod",
    "payment", "emi", "upi",
    
    # Quality & sizing
    "size", "sizing", "fit", "fitting", "quality", "fabric", "material",
    "color", "colour", "stitching", "cotton", "polyester", "silk",
    "small", "medium", "large", "xl", "xxl",
    
    # Review terms
    "review", "rating", "star", "recommend", "worth", "value",
    "genuine", "fake", "original", "authentic", "counterfeit", "copy",
    
    # Hinglish fashion terms
    "kapda", "kapde", "pehna", "pehan", "kharida", "khareed", "pasand",
    "accha", "bekar", "ghatiya", "sasta", "mehnga", "mazboot",
}

# Terms that indicate noise (pure tech support, unrelated)
NOISE_PATTERNS = [
    r"^\s*(good|nice|bad|worst|best|ok|okay|fine|great|excellent|awesome|terrible|horrible|amazing)\s*[.!]*\s*$",
    r"^[⭐★☆✩✪]+\s*$",
    r"^\s*\d+\s*$",
]

NOISE_REGEXES = [re.compile(p, re.IGNORECASE) for p in NOISE_PATTERNS]


# Minimum word count for a useful review
MIN_WORD_COUNT = 4


def is_relevant(text: str) -> bool:
    """
    Check if a text is relevant to fashion/shopping/Myntra.
    Returns True if the text should be kept.
    """
    if not text:
        return False

    text_lower = text.lower()
    words = text_lower.split()

    # Too short — not useful for analysis
    if len(words) < MIN_WORD_COUNT:
        return False

    # Check for noise patterns (ultra-short reviews like "Good", "Nice app")
    for regex in NOISE_REGEXES:
        if regex.match(text):
            return False

    # Check for fashion/shopping keywords
    for keyword in FASHION_KEYWORDS:
        if keyword in text_lower:
            return True

    # If from a Myntra-specific source (Play Store, App Store), it's inherently
    # relevant even without keyword match — it's about the Myntra app
    # This check is handled at the pipeline level using doc source metadata.
    
    return False


def is_relevant_with_source(text: str, source: str) -> bool:
    """
    Check relevance with source context.
    App store reviews are inherently Myntra-relevant.
    Reddit/YouTube need keyword signals.
    """
    if not text or len(text.split()) < MIN_WORD_COUNT:
        return False
    
    # Check noise patterns
    for regex in NOISE_REGEXES:
        if regex.match(text):
            return False

    # App store reviews are about the Myntra app by definition
    if source in ("playstore", "appstore", "trustpilot", "pissedconsumer", "reviewsio"):
        return True

    # Reddit and YouTube need keyword signals
    return is_relevant(text)


def filter_documents(docs: List[dict]) -> Tuple[List[dict], int]:
    """
    Filter documents for relevance.
    
    Returns:
        (relevant_docs, dropped_count)
    """
    kept = []
    dropped = 0

    for doc in docs:
        content = doc.get("content", "")
        source = doc.get("source", "")

        if is_relevant_with_source(content, source):
            kept.append(doc)
        else:
            dropped += 1

    return kept, dropped

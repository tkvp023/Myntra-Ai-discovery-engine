"""
Deduplication engine.
Two-stage: exact hash dedup → fuzzy MinHash dedup (Jaccard > 0.85).
"""

import hashlib
from typing import List, Tuple

from datasketch import MinHash, MinHashLSH


def _content_hash(text: str) -> str:
    """Generate a SHA-256 hash of normalized text for exact dedup."""
    normalized = text.lower().strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _build_minhash(text: str, num_perm: int = 128) -> MinHash:
    """Build a MinHash signature for fuzzy dedup."""
    m = MinHash(num_perm=num_perm)
    # Use word-level shingles (3-grams)
    words = text.lower().split()
    for i in range(len(words) - 2):
        shingle = " ".join(words[i:i + 3])
        m.update(shingle.encode("utf-8"))
    return m


def deduplicate_exact(docs: List[dict]) -> Tuple[List[dict], int]:
    """
    Remove exact duplicates based on content hash.
    
    Returns:
        (unique_docs, duplicate_count)
    """
    seen_hashes = set()
    unique = []
    dupes = 0

    for doc in docs:
        content = doc.get("content", "")
        h = _content_hash(content)
        if h not in seen_hashes:
            seen_hashes.add(h)
            unique.append(doc)
        else:
            dupes += 1

    return unique, dupes


def deduplicate_fuzzy(
    docs: List[dict],
    threshold: float = 0.85,
    num_perm: int = 128,
) -> Tuple[List[dict], int]:
    """
    Remove near-duplicate documents using MinHash LSH.
    Documents with Jaccard similarity > threshold are considered duplicates.
    
    Returns:
        (unique_docs, duplicate_count)
    """
    if not docs:
        return docs, 0

    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    unique = []
    dupes = 0

    for i, doc in enumerate(docs):
        content = doc.get("content", "")

        # Skip very short texts (not enough for meaningful MinHash)
        if len(content.split()) < 5:
            unique.append(doc)
            continue

        mh = _build_minhash(content, num_perm=num_perm)
        key = f"doc_{i}"

        try:
            # Check if similar document already exists
            result = lsh.query(mh)
            if result:
                dupes += 1
            else:
                lsh.insert(key, mh)
                unique.append(doc)
        except Exception:
            # If LSH fails (e.g., empty MinHash), keep the document
            unique.append(doc)

    return unique, dupes


def deduplicate(
    docs: List[dict],
    fuzzy_threshold: float = 0.85,
) -> Tuple[List[dict], dict]:
    """
    Full deduplication pipeline: exact → fuzzy.
    
    Returns:
        (unique_docs, stats_dict)
    """
    # Stage 1: Exact dedup
    after_exact, exact_dupes = deduplicate_exact(docs)

    # Stage 2: Fuzzy dedup (only if we have enough docs — skip for tiny sets)
    if len(after_exact) > 10:
        after_fuzzy, fuzzy_dupes = deduplicate_fuzzy(after_exact, threshold=fuzzy_threshold)
    else:
        after_fuzzy = after_exact
        fuzzy_dupes = 0

    stats = {
        "input_count": len(docs),
        "exact_duplicates": exact_dupes,
        "fuzzy_duplicates": fuzzy_dupes,
        "total_removed": exact_dupes + fuzzy_dupes,
        "output_count": len(after_fuzzy),
        "dedup_rate": round((exact_dupes + fuzzy_dupes) / max(len(docs), 1) * 100, 2),
    }

    return after_fuzzy, stats

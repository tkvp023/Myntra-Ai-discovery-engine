"""
Post-classification validator.
Validates LLM output against the schema, fixes recoverable errors, logs failures.
Matches llm_prompts.md §5 validation rules.
"""

from typing import List, Dict, Tuple

from pipeline.classification.schema import (
    VALID_HESITATION_REASONS, VALID_WISHLIST_INTENTS, VALID_AGE_GROUPS,
    VALID_PRICE_SENSITIVITY, VALID_FASHION_ENGAGEMENT, VALID_GENDER_SIGNALS,
    VALID_SENTIMENTS, VALID_PLATFORMS, VALID_COMPARISON_CRITERIA,
    VALID_INFO_TYPES, FACTOR_NAMES,
)


# ──────────────────────────────────────────────────────────
# Validation Config
# ──────────────────────────────────────────────────────────

VALIDATION_CONFIG = {
    "min_confidence": 0.4,
    "max_hesitation_reasons": 6,
    "max_unmet_needs": 5,
    "evidence_quote_min_length": 5,
    "evidence_must_be_substring": True,
}


# ──────────────────────────────────────────────────────────
# Core Validator
# ──────────────────────────────────────────────────────────

def validate_classification(doc_content: str, classification: dict) -> Tuple[dict, List[str]]:
    """
    Validate and fix a single classification result.
    
    Args:
        doc_content: Original document content (for evidence quote checking).
        classification: Raw classification dict from LLM.
    
    Returns:
        (fixed_classification, errors) — the fixed dict and list of error messages.
    """
    errors = []
    c = classification.copy() if isinstance(classification, dict) else {}

    # ── 1. Validate hesitation_reasons ──
    valid_reasons = []
    for reason in c.get("hesitation_reasons", []):
        if not isinstance(reason, dict):
            errors.append(f"Invalid hesitation reason format: {reason}")
            continue

        # Check reason enum
        r = reason.get("reason", "")
        if r not in VALID_HESITATION_REASONS:
            errors.append(f"Invalid hesitation reason: '{r}'")
            continue

        # Check confidence
        conf = reason.get("confidence", 0.5)
        try:
            conf = float(conf)
        except (ValueError, TypeError):
            conf = 0.5
        conf = max(0.0, min(1.0, conf))  # Clamp to [0, 1]

        # Drop below threshold
        if conf < VALIDATION_CONFIG["min_confidence"]:
            continue

        # Check evidence quote
        quote = reason.get("evidence_quote", "")
        if len(quote) < VALIDATION_CONFIG["evidence_quote_min_length"]:
            errors.append(f"Evidence quote too short for '{r}': '{quote}'")
            # Keep the reason but note the issue

        if VALIDATION_CONFIG["evidence_must_be_substring"] and quote and doc_content:
            if quote.lower() not in doc_content.lower():
                errors.append(f"Evidence quote not found in source for '{r}': '{quote[:60]}'")
                # Keep the reason — LLM may have slightly paraphrased

        valid_reasons.append({
            "reason": r,
            "confidence": round(conf, 2),
            "evidence_quote": quote,
        })

    # Cap at max
    c["hesitation_reasons"] = valid_reasons[:VALIDATION_CONFIG["max_hesitation_reasons"]]

    # ── 2. Validate wishlist_intent ──
    intent = c.get("wishlist_intent", "unknown")
    if intent not in VALID_WISHLIST_INTENTS:
        errors.append(f"Invalid wishlist_intent: '{intent}' → defaulting to 'unknown'")
        c["wishlist_intent"] = "unknown"

    # ── 3. Validate user_segment_signals ──
    signals = c.get("user_segment_signals", {})
    if not isinstance(signals, dict):
        signals = {}
    
    if signals.get("inferred_age_group", "unknown") not in VALID_AGE_GROUPS:
        errors.append(f"Invalid age_group: '{signals.get('inferred_age_group')}'")
        signals["inferred_age_group"] = "unknown"
    if signals.get("price_sensitivity", "unknown") not in VALID_PRICE_SENSITIVITY:
        signals["price_sensitivity"] = "unknown"
    if signals.get("fashion_engagement", "unknown") not in VALID_FASHION_ENGAGEMENT:
        signals["fashion_engagement"] = "unknown"
    if signals.get("gender_signal", "unknown") not in VALID_GENDER_SIGNALS:
        signals["gender_signal"] = "unknown"
    c["user_segment_signals"] = signals

    # ── 4. Validate comparison_behavior ──
    comp = c.get("comparison_behavior", {})
    if not isinstance(comp, dict):
        comp = {}
    comp["compares_across_platforms"] = bool(comp.get("compares_across_platforms", False))
    comp["platforms_mentioned"] = [
        p for p in comp.get("platforms_mentioned", []) if p in VALID_PLATFORMS
    ]
    comp["comparison_criteria"] = [
        cr for cr in comp.get("comparison_criteria", []) if cr in VALID_COMPARISON_CRITERIA
    ]
    c["comparison_behavior"] = comp

    # ── 5. Validate external_info_seeking ──
    ext = c.get("external_info_seeking", {})
    if not isinstance(ext, dict):
        ext = {}
    ext["seeks_external_info"] = bool(ext.get("seeks_external_info", False))
    ext["info_types"] = [
        t for t in ext.get("info_types", []) if t in VALID_INFO_TYPES
    ]
    c["external_info_seeking"] = ext

    # ── 6. Validate factor_mentions ──
    factors = c.get("factor_mentions", {})
    if not isinstance(factors, dict):
        factors = {}
    
    validated_factors = {}
    for factor_name in FACTOR_NAMES:
        f = factors.get(factor_name, {})
        if not isinstance(f, dict):
            f = {}
        validated_factors[factor_name] = {
            "mentioned": bool(f.get("mentioned", False)),
            "sentiment": f.get("sentiment", "neutral") if f.get("sentiment", "neutral") in VALID_SENTIMENTS else "neutral",
        }
    c["factor_mentions"] = validated_factors

    # ── 7. Validate unmet_needs ──
    needs = c.get("unmet_needs", [])
    if not isinstance(needs, list):
        needs = []
    needs = [str(n) for n in needs if n and len(str(n).strip()) > 2]
    c["unmet_needs"] = needs[:VALIDATION_CONFIG["max_unmet_needs"]]

    # ── 8. Validate question_mapping ──
    q_map = c.get("brief_question_mapping", [])
    if not isinstance(q_map, list):
        q_map = []
    c["brief_question_mapping"] = [int(q) for q in q_map if isinstance(q, (int, float)) and 1 <= q <= 10]

    # ── 9. Validate is_primary_signal ──
    c["is_primary_signal"] = bool(c.get("is_primary_signal", False))

    return c, errors


def validate_batch(documents: list, classifications: list) -> Tuple[list, dict]:
    """
    Validate a batch of classifications.
    
    Args:
        documents: List of document dicts with 'doc_id' and 'content'.
        classifications: List of classification result dicts.
    
    Returns:
        (validated_classifications, stats)
    """
    doc_map = {d["doc_id"]: d.get("content", "") for d in documents}
    validated = []
    total_errors = 0
    error_types = {}

    for cls in classifications:
        doc_id = cls.get("doc_id", "")
        content = doc_map.get(doc_id, "")
        raw_cls = cls.get("classification", cls)

        fixed, errors = validate_classification(content, raw_cls)
        
        validated.append({
            "doc_id": doc_id,
            "classification": fixed,
        })
        
        total_errors += len(errors)
        for e in errors:
            error_type = e.split(":")[0] if ":" in e else e
            error_types[error_type] = error_types.get(error_type, 0) + 1

    stats = {
        "total_docs": len(classifications),
        "total_errors": total_errors,
        "error_rate": round(total_errors / max(len(classifications), 1), 2),
        "error_types": error_types,
    }

    return validated, stats

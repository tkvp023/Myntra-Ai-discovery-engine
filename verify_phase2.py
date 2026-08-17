"""Phase 2 verification script — tests all classification module imports and logic."""
import sys
import os
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).resolve().parent))

print("[1] Testing schema imports...")
from pipeline.classification.schema import (
    DocumentClassification, ClassificationResult, Classification,
    HesitationReason, UserSegmentSignals, FactorMentions,
    VALID_HESITATION_REASONS, VALID_WISHLIST_INTENTS, empty_classification
)
assert len(VALID_HESITATION_REASONS) == 12
assert len(VALID_WISHLIST_INTENTS) == 6
ec = empty_classification("test_doc")
assert ec.doc_id == "test_doc"
assert ec.classification.wishlist_intent == "unknown"
print("    [OK] Schema imports and empty_classification work")

print("[2] Testing prompt templates...")
from pipeline.classification.prompts import (
    SYSTEM_PROMPT, FEW_SHOT_EXAMPLES, format_batch_prompt, build_few_shot_messages
)
assert "sizing_uncertainty" in SYSTEM_PROMPT
assert len(FEW_SHOT_EXAMPLES) == 3
test_docs = [{"doc_id": "d1", "content": "Great jacket but size is wrong"}, {"doc_id": "d2", "content": "Too expensive"}]
prompt = format_batch_prompt(test_docs)
assert "[Document d1]" in prompt
assert "[Document d2]" in prompt
msgs = build_few_shot_messages()
assert len(msgs) == 6  # 3 examples * 2 (user + model)
print("    [OK] Prompts and batch formatter work")

print("[3] Testing validator...")
from pipeline.classification.validator import validate_classification, validate_batch
# Valid classification
valid_cls = {
    "hesitation_reasons": [{"reason": "sizing_uncertainty", "confidence": 0.9, "evidence_quote": "size is wrong"}],
    "wishlist_intent": "genuine_purchase_intent",
    "user_segment_signals": {"inferred_age_group": "gen_z", "price_sensitivity": "high", "fashion_engagement": "high", "gender_signal": "female"},
    "comparison_behavior": {"compares_across_platforms": False, "platforms_mentioned": [], "comparison_criteria": []},
    "external_info_seeking": {"seeks_external_info": False, "info_types": []},
    "factor_mentions": {"fit_size": {"mentioned": True, "sentiment": "negative"}, "price": {"mentioned": False, "sentiment": "neutral"}, "reviews_ratings": {"mentioned": False, "sentiment": "neutral"}, "styling": {"mentioned": False, "sentiment": "neutral"}, "occasion": {"mentioned": False, "sentiment": "neutral"}, "social_validation": {"mentioned": False, "sentiment": "neutral"}, "brand_trust": {"mentioned": False, "sentiment": "neutral"}, "delivery_returns": {"mentioned": False, "sentiment": "neutral"}},
    "unmet_needs": ["better size guide"],
    "brief_question_mapping": [2, 3],
    "is_primary_signal": True
}
fixed, errors = validate_classification("Great jacket but size is wrong", valid_cls)
assert fixed["wishlist_intent"] == "genuine_purchase_intent"
assert len(fixed["hesitation_reasons"]) == 1
# Invalid reason should be dropped
invalid_cls = {"hesitation_reasons": [{"reason": "INVALID_REASON", "confidence": 0.9, "evidence_quote": "test"}], "wishlist_intent": "bad_intent"}
fixed2, errors2 = validate_classification("test", invalid_cls)
assert fixed2["wishlist_intent"] == "unknown"
assert len(fixed2["hesitation_reasons"]) == 0
# Low confidence should be dropped
low_conf = {"hesitation_reasons": [{"reason": "price_sensitivity", "confidence": 0.2, "evidence_quote": "cheap"}], "wishlist_intent": "unknown"}
fixed3, errors3 = validate_classification("cheap product", low_conf)
assert len(fixed3["hesitation_reasons"]) == 0
print("    [OK] Validator correctly handles valid, invalid, and low-confidence cases")

print("[4] Testing keyword tagger...")
from pipeline.classification.keyword_tagger import classify_with_keywords
result = classify_with_keywords("test_doc", "The size is too small and price is very expensive, not worth it")
cls = result["classification"]
reasons = [r["reason"] for r in cls["hesitation_reasons"]]
assert "sizing_uncertainty" in reasons or "price_sensitivity" in reasons
assert cls["factor_mentions"]["fit_size"]["mentioned"] == True
assert cls["factor_mentions"]["price"]["mentioned"] == True
# Non-fashion text
result2 = classify_with_keywords("other_doc", "I love sunny weather today")
assert not result2["classification"]["is_primary_signal"]
print("    [OK] Keyword tagger detects sizing and price signals correctly")

print("[5] Testing classifier imports (LLM clients)...")
from pipeline.classification.classifier import TieredClassifier, GeminiClassifier, GroqClassifier, KeywordClassifier
# Keyword classifier is always available
kc = KeywordClassifier()
assert kc.available == True
results, _ = kc.classify([{"doc_id": "k1", "content": "Myntra sizing chart is useless"}])
assert len(results) == 1
assert results[0]["doc_id"] == "k1"
print("    [OK] Classifier imports OK, keyword tier always available")

print("[6] Testing batch processor imports...")
from pipeline.classification.batch_processor import BatchProcessor
bp = BatchProcessor(batch_size=5, rate_limit_rpm=20)
assert bp.batch_size == 5
assert bp.seconds_per_request == 3.0
print("    [OK] BatchProcessor instantiates correctly")

print()
print("=== ALL PHASE 2 VERIFICATION PASSED ===")

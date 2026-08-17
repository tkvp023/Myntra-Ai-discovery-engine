"""
Pydantic models for the classification schema.
Matches llm_prompts.md §1 exactly.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────
# Valid Enum Constants
# ──────────────────────────────────────────────────────────

VALID_HESITATION_REASONS = [
    "sizing_uncertainty", "price_sensitivity", "style_uncertainty",
    "quality_doubt", "waiting_for_sale", "social_validation_needed",
    "occasion_mismatch", "comparison_paralysis", "trust_deficit",
    "information_gap", "return_policy_concern", "other",
]

VALID_WISHLIST_INTENTS = [
    "genuine_purchase_intent", "bookmarking", "aspiration",
    "comparison_shortlist", "gift_idea", "unknown",
]

VALID_AGE_GROUPS = ["gen_z", "millennial", "gen_x", "unknown"]

VALID_PRICE_SENSITIVITY = ["high", "medium", "low", "unknown"]

VALID_FASHION_ENGAGEMENT = ["high", "casual", "unknown"]

VALID_GENDER_SIGNALS = ["male", "female", "non_binary", "unknown"]

VALID_SENTIMENTS = ["positive", "negative", "neutral", "mixed"]

VALID_PLATFORMS = [
    "amazon", "ajio", "meesho", "flipkart", "offline_store",
    "nykaa_fashion", "other",
]

VALID_COMPARISON_CRITERIA = [
    "price", "quality", "delivery", "return_policy", "variety",
    "authenticity", "other",
]

VALID_INFO_TYPES = [
    "youtube_reviews", "instagram_styling", "google_search",
    "ask_friends", "offline_trial", "brand_website", "other",
]

FACTOR_NAMES = [
    "fit_size", "price", "reviews_ratings", "styling",
    "occasion", "social_validation", "brand_trust", "delivery_returns",
]


# ──────────────────────────────────────────────────────────
# Pydantic Models
# ──────────────────────────────────────────────────────────

class HesitationReason(BaseModel):
    """A single hesitation reason with confidence and evidence."""
    reason: str = "other"
    confidence: float = 0.5
    evidence_quote: str = ""


class UserSegmentSignals(BaseModel):
    """Inferred user segment signals."""
    inferred_age_group: str = "unknown"
    price_sensitivity: str = "unknown"
    fashion_engagement: str = "unknown"
    gender_signal: str = "unknown"


class ComparisonBehavior(BaseModel):
    """Cross-platform comparison behavior."""
    compares_across_platforms: bool = False
    platforms_mentioned: List[str] = Field(default_factory=list)
    comparison_criteria: List[str] = Field(default_factory=list)


class ExternalInfoSeeking(BaseModel):
    """External information seeking behavior."""
    seeks_external_info: bool = False
    info_types: List[str] = Field(default_factory=list)


class FactorMentionItem(BaseModel):
    """A single factor mention."""
    mentioned: bool = False
    sentiment: str = "neutral"


class FactorMentions(BaseModel):
    """All 8 factor mentions."""
    fit_size: FactorMentionItem = Field(default_factory=FactorMentionItem)
    price: FactorMentionItem = Field(default_factory=FactorMentionItem)
    reviews_ratings: FactorMentionItem = Field(default_factory=FactorMentionItem)
    styling: FactorMentionItem = Field(default_factory=FactorMentionItem)
    occasion: FactorMentionItem = Field(default_factory=FactorMentionItem)
    social_validation: FactorMentionItem = Field(default_factory=FactorMentionItem)
    brand_trust: FactorMentionItem = Field(default_factory=FactorMentionItem)
    delivery_returns: FactorMentionItem = Field(default_factory=FactorMentionItem)


class Classification(BaseModel):
    """Full classification output for a single document."""
    hesitation_reasons: List[HesitationReason] = Field(default_factory=list)
    wishlist_intent: str = "unknown"
    user_segment_signals: UserSegmentSignals = Field(default_factory=UserSegmentSignals)
    comparison_behavior: ComparisonBehavior = Field(default_factory=ComparisonBehavior)
    external_info_seeking: ExternalInfoSeeking = Field(default_factory=ExternalInfoSeeking)
    factor_mentions: FactorMentions = Field(default_factory=FactorMentions)
    unmet_needs: List[str] = Field(default_factory=list)
    brief_question_mapping: List[int] = Field(default_factory=list)
    is_primary_signal: bool = False


class DocumentClassification(BaseModel):
    """Classification result for a single document (doc_id + classification)."""
    doc_id: str
    classification: Classification = Field(default_factory=Classification)


class ClassificationResult(BaseModel):
    """Wrapper for a batch of classification results."""
    results: List[DocumentClassification] = Field(default_factory=list)
    model_used: str = ""
    tier_used: str = ""
    errors: List[str] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────
# Helper: Build default empty classification
# ──────────────────────────────────────────────────────────

def empty_classification(doc_id: str) -> DocumentClassification:
    """Return a default empty classification for a document."""
    return DocumentClassification(
        doc_id=doc_id,
        classification=Classification(
            hesitation_reasons=[],
            wishlist_intent="unknown",
            user_segment_signals=UserSegmentSignals(),
            comparison_behavior=ComparisonBehavior(),
            external_info_seeking=ExternalInfoSeeking(),
            factor_mentions=FactorMentions(),
            unmet_needs=[],
            brief_question_mapping=[],
            is_primary_signal=False,
        ),
    )

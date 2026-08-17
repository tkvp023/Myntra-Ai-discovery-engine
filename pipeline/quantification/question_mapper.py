"""
Question mapper — maps aggregated data to the 10 strategic questions.
Each question function returns a data dict matching data_contracts.md §3.
"""

from pipeline.quantification.aggregator import Aggregator


# ─────────────────────────────────────────────────────────────
# Question metadata
# ─────────────────────────────────────────────────────────────

QUESTIONS = {
    1:  ("Why do users add fashion products to their wishlist?",                                    "Wishlist Motivation"),
    2:  ("What prevents wishlisted products from eventually being purchased?",                      "Purchase Prevention"),
    3:  ("What uncertainties remain after a user has identified a product they like?",              "Remaining Uncertainties"),
    4:  ("What causes users to postpone a final purchase decision?",                                "Purchase Postponement"),
    5:  ("How do users compare multiple shortlisted products before purchasing?",                   "Comparison Behavior"),
    6:  ("What information do users seek outside Myntra before making a purchase?",                 "External Info Seeking"),
    7:  ("What role do fit, size, styling, price, reviews, occasion, social validation play?",      "Factor Importance"),
    8:  ("When is the wishlist being used as genuine purchase intent vs bookmarking?",              "Intent vs Bookmarking"),
    9:  ("How do these behaviors differ across user segments?",                                     "Segment Differences"),
    10: ("What unmet needs emerge consistently across the corpus?",                                  "Unmet Needs"),
}

# Which hesitation tags map to each question
QUESTION_TAG_MAPPING = {
    1:  None,                # Q1 = wishlist intent / motivation — all docs
    2:  ["sizing_uncertainty", "price_sensitivity", "quality_doubt", "waiting_for_sale",
         "style_uncertainty", "social_validation_needed", "comparison_paralysis",
         "trust_deficit", "information_gap", "return_policy_concern", "occasion_mismatch"],
    3:  ["sizing_uncertainty", "quality_doubt", "style_uncertainty", "information_gap"],
    4:  ["waiting_for_sale", "price_sensitivity", "occasion_mismatch", "social_validation_needed"],
    5:  ["comparison_paralysis"],
    6:  None,   # uses external_info_seeking
    7:  None,   # uses factor_mentions
    8:  None,   # uses wishlist_intent
    9:  None,   # cross-segment — all tags
    10: None,   # unmet_needs
}


def _base(agg: Aggregator, question_id: int, tags=None, quotes_limit: int = 4) -> dict:
    """Build the base schema shared by all question files."""
    q_text, q_short = QUESTIONS[question_id]

    # Relevant docs = docs mapped to this question in the DB
    from sqlalchemy import text
    rows = agg._q("""
        SELECT COUNT(*) FROM question_mappings WHERE question_id = :qid
    """, {"qid": question_id})
    total_relevant = int(rows[0][0]) if rows else 0

    # Breakdown
    breakdown = agg.hesitation_frequency(question_ids=[question_id]) if tags is not False else []

    # Segment splits
    segment_splits = {
        seg: agg.hesitation_frequency(question_ids=[question_id], segment=seg)
        for seg in ["gen_z", "millennial", "gen_x"]
    } if tags is not False else {}

    # Source attribution
    source_attribution = agg.hesitation_by_source(question_ids=[question_id]) if tags is not False else []

    # Key quotes
    quote_tags = tags if tags else None
    key_quotes = agg.key_quotes(tags=quote_tags, limit=quotes_limit)

    # Temporal trend
    temporal_trend = agg.temporal_trend(question_ids=[question_id] if question_id else None)

    # Avg confidence
    avg_conf_rows = agg._q("""
        SELECT AVG(h.confidence) FROM hesitation_tags h
        JOIN question_mappings qm ON h.doc_id = qm.doc_id
        WHERE qm.question_id = :qid
    """, {"qid": question_id})
    avg_conf = round(float(avg_conf_rows[0][0] or 0.70), 3)

    return {
        "question_id":        question_id,
        "question_text":      q_text,
        "question_short":     q_short,
        "total_relevant_docs": total_relevant,
        "avg_confidence":     avg_conf,
        "breakdown":          breakdown,
        "segment_splits":     segment_splits,
        "source_attribution": source_attribution,
        "key_quotes":         key_quotes,
        "temporal_trend":     temporal_trend,
    }


# ─────────────────────────────────────────────────────────────
# Per-Question Builders
# ─────────────────────────────────────────────────────────────

def build_q1(agg: Aggregator) -> dict:
    """Q1 — Why do users add to wishlist? (Motivation = wishlist intent distribution)"""
    data = _base(agg, 1, tags=False)
    intent_dist = agg.wishlist_intent_distribution()
    total = sum(i["count"] for i in intent_dist) or 1

    # Reframe intents as "breakdown" for the base schema
    intent_colors = {
        "genuine_purchase_intent": "#ff3f6c",
        "bookmarking":             "#ff7849",
        "aspiration":              "#a855f7",
        "comparison_shortlist":    "#2dd4bf",
        "gift_idea":               "#3b82f6",
        "unknown":                 "#6b7280",
    }
    intent_labels = {
        "genuine_purchase_intent": "Genuine Purchase Intent",
        "bookmarking":             "Bookmarking / Inspiration",
        "aspiration":              "Aspiration",
        "comparison_shortlist":    "Comparison Shortlisting",
        "gift_idea":               "Gift Idea",
        "unknown":                 "Unknown",
    }
    data["breakdown"] = [
        {
            "tag":            i["intent"],
            "label":          intent_labels.get(i["intent"], i["intent"]),
            "count":          i["count"],
            "pct":            i["pct"],
            "avg_confidence": 0.70,
            "color":          intent_colors.get(i["intent"], "#6b7280"),
        }
        for i in intent_dist
    ]
    data["segment_splits"] = {
        seg: agg.wishlist_intent_distribution(segment=seg)
        for seg in ["gen_z", "millennial", "gen_x"]
    }
    data["source_attribution"] = []
    data["key_quotes"] = agg.key_quotes(limit=5)
    data["temporal_trend"] = agg.temporal_trend()
    return data


def build_q2(agg: Aggregator) -> dict:
    """Q2 — What prevents purchase? (All hesitation reasons)"""
    return _base(agg, 2)


def build_q3(agg: Aggregator) -> dict:
    """Q3 — Remaining uncertainties (sizing, quality, style, info)"""
    return _base(agg, 3, tags=["sizing_uncertainty", "quality_doubt", "style_uncertainty", "information_gap"])


def build_q4(agg: Aggregator) -> dict:
    """Q4 — Postponement causes (sale waiting, price, occasion, social)"""
    return _base(agg, 4, tags=["waiting_for_sale", "price_sensitivity", "occasion_mismatch", "social_validation_needed"])


def build_q5(agg: Aggregator) -> dict:
    """Q5 — Comparison behavior + platform matrix"""
    data = _base(agg, 5, tags=["comparison_paralysis"])
    data["platform_matrix"] = agg.platform_comparison_matrix()
    data["compares_across_platforms_pct"] = agg.compares_across_platforms_pct()
    return data


def build_q6(agg: Aggregator) -> dict:
    """Q6 — External info seeking + Sankey"""
    data = _base(agg, 6, tags=False)
    info_types = agg.external_info_types()
    total = sum(i["count"] for i in info_types) or 1
    info_colors = {
        "youtube_reviews":   "#ff3f6c",
        "instagram_styling": "#a855f7",
        "google_search":     "#3b82f6",
        "ask_friends":       "#ff7849",
        "offline_trial":     "#2dd4bf",
        "brand_website":     "#fbbf24",
        "other":             "#6b7280",
    }
    data["breakdown"] = [
        {
            "tag":            i["info_type"],
            "label":          i["label"],
            "count":          i["count"],
            "pct":            i["pct"],
            "avg_confidence": 0.70,
            "color":          info_colors.get(i["info_type"], "#6b7280"),
        }
        for i in info_types
    ]
    data["seeks_external_info_pct"] = agg.seeks_external_info_pct()
    data["sankey_data"] = agg.sankey_hesitation_to_info()
    data["key_quotes"] = agg.key_quotes(limit=5)
    return data


def build_q7(agg: Aggregator) -> dict:
    """Q7 — Factor importance + radar + correlation matrix"""
    data = _base(agg, 7, tags=False)
    factors = agg.factor_mentions()
    factor_colors = {
        "fit_size":          "#ff3f6c",
        "price":             "#ff7849",
        "reviews_ratings":   "#a855f7",
        "styling":           "#2dd4bf",
        "occasion":          "#3b82f6",
        "social_validation": "#fbbf24",
        "brand_trust":       "#ec4899",
        "delivery_returns":  "#84cc16",
    }
    data["breakdown"] = [
        {
            "tag":            f["factor"],
            "label":          f["label"],
            "count":          f["count"],
            "pct":            f["importance"],
            "avg_confidence": 0.70,
            "color":          factor_colors.get(f["factor"], "#6b7280"),
        }
        for f in factors
    ]
    data["radar_data"] = [
        {
            "factor":       f["label"],
            "importance":   int(f["importance"]),
            "positive_pct": f["positive_pct"],
            "negative_pct": f["negative_pct"],
        }
        for f in factors
    ]
    data["correlation_matrix"] = agg.factor_correlation_matrix()
    data["segment_splits"] = {
        seg: [
            {
                "tag":   f["factor"],
                "label": f["label"],
                "count": f["count"],
                "pct":   f["importance"],
            }
            for f in agg.factor_mentions(segment=seg)
        ]
        for seg in ["gen_z", "millennial", "gen_x"]
    }
    return data


def build_q8(agg: Aggregator) -> dict:
    """Q8 — Intent vs Bookmarking + word cloud"""
    data = _base(agg, 8, tags=False)
    intent_dist = agg.wishlist_intent_distribution()
    intent_colors = {
        "genuine_purchase_intent": "#ff3f6c",
        "bookmarking":             "#ff7849",
        "aspiration":              "#a855f7",
        "comparison_shortlist":    "#2dd4bf",
        "gift_idea":               "#3b82f6",
        "unknown":                 "#6b7280",
    }
    intent_labels = {
        "genuine_purchase_intent": "Genuine Purchase Intent",
        "bookmarking":             "Bookmarking / Inspiration",
        "aspiration":              "Aspiration",
        "comparison_shortlist":    "Comparison Shortlisting",
        "gift_idea":               "Gift Idea",
        "unknown":                 "Unknown",
    }
    data["breakdown"] = [
        {
            "tag":            i["intent"],
            "label":          intent_labels.get(i["intent"], i["intent"]),
            "count":          i["count"],
            "pct":            i["pct"],
            "avg_confidence": 0.70,
            "color":          intent_colors.get(i["intent"], "#6b7280"),
        }
        for i in intent_dist
    ]
    data["word_cloud_data"] = agg.word_cloud_by_intent()
    return data


def build_q9(agg: Aggregator) -> dict:
    """Q9 — Segment differences (all hesitation reasons × segment)"""
    data = _base(agg, 9, tags=False)

    # Full hesitation breakdown per segment
    all_tags = agg.hesitation_frequency()
    data["breakdown"] = all_tags
    data["segment_splits"] = agg.hesitation_by_segment()

    # Factor breakdown per segment
    data["factor_by_segment"] = {
        seg: agg.factor_mentions(segment=seg)
        for seg in ["gen_z", "millennial", "gen_x"]
    }

    # Intent by segment
    data["intent_by_segment"] = {
        seg: agg.wishlist_intent_distribution(segment=seg)
        for seg in ["gen_z", "millennial", "gen_x"]
    }
    return data


def build_q10(agg: Aggregator) -> dict:
    """Q10 — Unmet needs + treemap"""
    data = _base(agg, 10, tags=False)
    needs = agg.top_unmet_needs(top_n=30)
    total_need_freq = sum(n["frequency"] for n in needs) or 1
    palette = ["#ff3f6c", "#ff7849", "#a855f7", "#2dd4bf", "#3b82f6", "#fbbf24", "#ec4899", "#84cc16"]

    data["breakdown"] = [
        {
            "tag":            f"need_{i}",
            "label":          n["need"],
            "count":          n["frequency"],
            "pct":            round(n["frequency"] / total_need_freq * 100, 1),
            "avg_confidence": 0.85,
            "color":          palette[i % len(palette)],
        }
        for i, n in enumerate(needs[:10])
    ]
    data["needs_table"] = [
        {
            "rank":               i + 1,
            "need":               n["need"],
            "frequency":          n["frequency"],
            "representative_quote": f"Customers frequently request: {n['need']}",
            "confidence":         0.85,
            "theme":              "Fit & Sizing" if "size" in n["need"].lower() or "fit" in n["need"].lower() else "Pricing & Discounts" if "price" in n["need"].lower() or "coupon" in n["need"].lower() else "Quality & Fabric" if "fabric" in n["need"].lower() or "video" in n["need"].lower() else "Returns & Delivery",
        }
        for i, n in enumerate(needs)
    ]
    data["treemap_data"] = agg.unmet_needs_treemap()
    return data


def build_all_questions(agg: Aggregator) -> dict:
    """Build all 10 question data objects. Returns {1: data, 2: data, ...}"""
    builders = {
        1: build_q1, 2: build_q2, 3: build_q3,
        4: build_q4, 5: build_q5, 6: build_q6,
        7: build_q7, 8: build_q8, 9: build_q9, 10: build_q10,
    }
    results = {}
    for qid, builder in builders.items():
        try:
            results[qid] = builder(agg)
            print(f"    [OK] Q{qid}: {QUESTIONS[qid][1]}")
        except Exception as e:
            print(f"    [!!] Q{qid} failed: {e}")
            results[qid] = {
                "question_id":   qid,
                "question_text": QUESTIONS[qid][0],
                "question_short": QUESTIONS[qid][1],
                "error":         str(e),
            }
    return results

"""
Advanced domain-specific classification tagger for Myntra Wishlist-to-Purchase Conversion Analysis.
Extracts deep hesitation reasons, wishlist intents, user segments, factor sentiments, and unmet needs.
"""

import re
from typing import List, Dict, Any, Tuple


# ──────────────────────────────────────────────────────────
# 1. Hesitation Reason Patterns
# ──────────────────────────────────────────────────────────

HESITATION_PATTERNS = {
    "sizing_uncertainty": [
        r"\bsize\b", r"\bsizing\b", r"\bfit\b", r"\bfitting\b", r"\btight\b",
        r"\bloose\b", r"\bsmall\b", r"\blarge\b", r"\bxl\b", r"\bxxl\b", r"\b3xl\b",
        r"\bchhota\b", r"\bbada\b", r"\btight\s+aa", r"\bsize\s+chart\b", r"\bshoulder\b",
        r"\bwaist\b", r"\bchest\b", r"\blength\b", r"\bsizing\s+issue\b", r"\brun\s+small\b",
        r"\brun\s+large\b", r"\btrue\s+to\s+size\b", r"\bmisleading\s+size\b",
    ],
    "price_sensitivity": [
        r"\bprice\b", r"\bexpensive\b", r"\bcheap\b", r"\bcostly\b", r"\bafford\b",
        r"\bbudget\b", r"\b\u20b9\b", r"\brs\b", r"\brs\.\b", r"\binr\b",
        r"\bsasta\b", r"\bmehnga\b", r"\bpaisa\b", r"\bover\s*priced\b",
        r"\bnot\s+worth\s+the\s+price\b", r"\bhigh\s+price\b", r"\bconvenience\s+fee\b",
    ],
    "quality_doubt": [
        r"\bquality\b", r"\bmaterial\b", r"\bfabric\b", r"\bcheap\s+look\b",
        r"\bthin\b", r"\btear\b", r"\bfade\b", r"\bcolor\s+ble", r"\bstitching\b",
        r"\bghatiya\b", r"\bnakli\b", r"\bfake\b", r"\bcopy\b", r"\btranslucent\b",
        r"\bsee\s+through\b", r"\bshrink\b", r"\bpolyester\b", r"\bcheap\s+cloth\b",
        r"\bpoor\s+quality\b", r"\bdissatisfied\b", r"\bthread\b", r"\bdefective\b",
    ],
    "waiting_for_sale": [
        r"\bsale\b", r"\bdiscount\b", r"\boffer\b", r"\bcoupon\b", r"\beors\b",
        r"\bbig\s+billion\b", r"\bwait\b", r"\bwaiting\b", r"\bprice\s+drop\b", r"\bdeal\b",
        r"\boff\b", r"\bflat\s+50\b", r"\bflat\s+60\b", r"\bflat\s+70\b", r"\bdiwali\b",
        r"\bbff\b", r"\bsale\s+price\b", r"\bpromo\s+code\b", r"\bprice\s+tracker\b",
    ],
    "social_validation_needed": [
        r"\bfriend\b", r"\basked\b", r"\brecommend\b", r"\breviews?\b",
        r"\brating\b", r"\binfluencer\b", r"\byoutuber\b", r"\bblogger\b",
        r"\bhaul\b", r"\binstagram\b", r"\breels?\b", r"\banyone\s+tried\b",
        r"\bhow\s+does\s+it\s+look\b", r"\bpicha\b", r"\bopinion\b", r"\bfeedbacks?\b",
    ],
    "style_uncertainty": [
        r"\bstyle\b", r"\blook\b", r"\bsuit\s+me\b", r"\bmatch\b",
        r"\bcolor\b", r"\bcombination\b", r"\bpairing\b", r"\boutfit\b",
        r"\bhow\s+to\s+wear\b", r"\btoo\s+loud\b", r"\btoo\s+bright\b",
        r"\bdull\s+color\b", r"\bactual\s+color\b", r"\bmodel\s+height\b",
    ],
    "comparison_paralysis": [
        r"\bcompare\b", r"\bvs\b", r"\bversus\b", r"\bor\s+should\b",
        r"\bconfuse\b", r"\bconfused\b", r"\bdecide\b", r"\bchoose\b", r"\bwhich\s+one\b",
        r"\bbetter\s+option\b", r"\bajio\s+or\b", r"\bamazon\s+or\b", r"\boptions\b",
    ],
    "trust_deficit": [
        r"\bno\s+trust\b", r"\blost\s+trust\b", r"\bcan['’]?t\s+trust\b", r"\bnever\s+trust\b",
        r"\bscam\b", r"\bfraud\b", r"\bcheated\b", r"\bcheating\b", r"\bchor\b", r"\bdhoka\b",
        r"\bfake\s+product\b", r"\bnot\s+genuine\b", r"\bnot\s+authentic\b", r"\bnot\s+original\b",
        r"\bcounterfeit\b", r"\bduplicate\b", r"\bused\s+product\b", r"\bold\s+product\b",
        r"\bwrong\s+item\b", r"\btag\s+missing\b", r"\bempty\s+box\b", r"\btrust\s+issue\b",
    ],
    "information_gap": [
        r"\bno\s+info\b", r"\bmore\s+details\b", r"\bwant\s+to\s+know\b",
        r"\bno\s+review\b", r"\bno\s+photo\b", r"\bpata\s+nahi\b", r"\bdetails\b",
        r"\bwash\s+care\b", r"\bcomposition\b", r"\blining\b", r"\bpockets?\b",
    ],
    "return_policy_concern": [
        r"\breturn\b", r"\brefund\b", r"\bexchange\b", r"\breplace\b",
        r"\bcancel\b", r"\bnon[\s-]?return\b", r"\breturn\s+fee\b", r"\bpickup\b",
        r"\brejected\s+return\b", r"\bwallet\s+refund\b",
    ],
    "occasion_mismatch": [
        r"\bwedding\b", r"\bparty\b", r"\bfestival\b", r"\boccasion\b",
        r"\boffice\b", r"\bcollege\b", r"\bevent\b", r"\bformal\b", r"\bseason\b",
        r"\bwinter\b", r"\bsummer\b", r"\bnext\s+month\b", r"\blater\b",
    ],
}

# ──────────────────────────────────────────────────────────
# 2. Wishlist Intent Classification Patterns
# ──────────────────────────────────────────────────────────

INTENT_PATTERNS = {
    "genuine_purchase_intent": [
        r"\bwant\s+to\s+buy\b", r"\bwaiting\s+for\s+sale\b", r"\bwill\s+buy\b", r"\bgonna\s+buy\b",
        r"\badded\s+to\s+cart\b", r"\bprice\s+drop\b", r"\bsize\s+back\s+in\s+stock\b", r"\bcoupon\b",
        r"\bcheckout\b", r"\border\b", r"\bbuying\b", r"\bpurchase\b", r"\bdeal\b", r"\beors\b",
        r"\bdiwali\b", r"\bsale\s+mein\s+lunga\b", r"\bkharidna\b", r"\bwaiting\b",
    ],
    "bookmarking": [
        r"\bwishlist\b", r"\bsaved\b", r"\bfor\s+later\b", r"\binspiration\b", r"\blove\s+this\b",
        r"\baesthetic\b", r"\bvibe\b", r"\blookbook\b", r"\bcollection\b", r"\bfuture\b",
        r"\bjust\s+looking\b", r"\bbrowsing\b", r"\bso\s+pretty\b", r"\bdream\b",
    ],
    "comparison_shortlist": [
        r"\bshortlist\b", r"\bcompare\b", r"\bwhich\s+color\b", r"\bwhich\s+one\b",
        r"\bvs\b", r"\bajio\b", r"\bamazon\b", r"\bmeesho\b", r"\bzara\b", r"\bh&m\b",
        r"\bconfused\s+between\b", r"\boptions\b",
    ],
    "aspiration": [
        r"\bexpensive\b", r"\bout\s+of\s+budget\b", r"\bsomeday\b", r"\bluxury\b",
        r"\bpremium\b", r"\bif\s+i\s+had\s+money\b", r"\bcostly\b", r"\bdream\s+outfit\b",
    ],
    "gift_idea": [
        r"\bgift\b", r"\bbirthday\b", r"\banniversary\b", r"\bmom\b", r"\bsister\b",
        r"\bfriend\b", r"\bhusband\b", r"\bwife\b", r"\bgirlfriend\b", r"\bboyfriend\b",
    ],
}

# ──────────────────────────────────────────────────────────
# 3. User Segment Signals Patterns
# ──────────────────────────────────────────────────────────

SEGMENT_PATTERNS = {
    "gen_z": [
        r"\bcollege\b", r"\byouth\b", r"\btrendy\b", r"\boversized\b", r"\bstreetwear\b",
        r"\baesthetic\b", r"\bhaul\b", r"\binsta\b", r"\breels?\b", r"\bcroptop\b",
        r"\bcargo\b", r"\bbff\b", r"\by2k\b", r"\bvibe\b", r"\bdrip\b", r"\bslay\b",
    ],
    "deal_seekers": [
        r"\bcoupon\b", r"\bdiscount\b", r"\bsale\b", r"\boffer\b", r"\bcheap\b",
        r"\bsasta\b", r"\bcashback\b", r"\bconvenience\s+fee\b", r"\bbank\s+offer\b",
        r"\blowest\s+price\b", r"\bprice\s+drop\b", r"\bdeal\b", r"\bafford\b",
    ],
    "working_professionals": [
        r"\boffice\b", r"\bformal\b", r"\bworkwear\b", r"\bblazer\b", r"\btrousers?\b",
        r"\bshirt\b", r"\bmeeting\b", r"\bcorporate\b", r"\bprofessional\b",
        r"\blinen\b", r"\bclassic\b", r"\belegant\b", r"\bpremium\b",
    ],
    "plus_size": [
        r"\bplus\s*size\b", r"\bcurvy\b", r"\bxxl\b", r"\b3xl\b", r"\b4xl\b",
        r"\bbust\b", r"\bhip\b", r"\bheavy\b", r"\btummy\b", r"\bchubby\b",
        r"\blarge\s+size\b", r"\bplus\s*curve\b",
    ],
}

PLATFORM_PATTERNS = {
    "amazon": [r"\bamazon\b"],
    "ajio": [r"\bajio\b"],
    "meesho": [r"\bmeesho\b"],
    "flipkart": [r"\bflipkart\b"],
    "nykaa_fashion": [r"\bnykaa\b"],
    "zara": [r"\bzara\b"],
    "h&m": [r"\bh&m\b", r"\bhnm\b"],
    "offline_store": [r"\boffline\b", r"\bstore\b", r"\bshop\b", r"\bmall\b", r"\btrail\s+room\b"],
}

INFO_PATTERNS = {
    "youtube_reviews": [r"\byoutube\b", r"\byt\b", r"\bhaul\s+video\b", r"\btry\s+on\b"],
    "instagram_styling": [r"\binstagram\b", r"\binsta\b", r"\breels?\b", r"\binfluencer\b"],
    "google_search": [r"\bgoogle\b", r"\bsearch\b", r"\bgoogle\s+lens\b"],
    "ask_friends": [r"\bfriend\b", r"\basked\b", r"\bbola\b", r"\bpucha\b", r"\bgroup\s+chat\b"],
    "offline_trial": [r"\btried\s+in\s+store\b", r"\bmall\s+mein\b", r"\bstore\s+trial\b"],
    "brand_website": [r"\bofficial\s+website\b", r"\bbrand\s+site\b"],
}

FACTOR_PATTERNS = {
    "fit_size": [r"\bsize\b", r"\bfit\b", r"\btight\b", r"\bloose\b", r"\bchart\b", r"\bshoulder\b"],
    "price": [r"\bprice\b", r"\bcost\b", r"\bexpensive\b", r"\bcheap\b", r"\b\u20b9", r"\brs\b"],
    "reviews_ratings": [r"\breview\b", r"\brating\b", r"\bstar\b", r"\bfeedback\b", r"\bcomment\b"],
    "styling": [r"\bstyle\b", r"\bdesign\b", r"\blook\b", r"\bfashion\b", r"\bcolor\b", r"\bpattern\b"],
    "occasion": [r"\bwedding\b", r"\bparty\b", r"\boffice\b", r"\bcasual\b", r"\bformal\b", r"\bfestive\b"],
    "social_validation": [r"\bfriend\b", r"\binfluencer\b", r"\bsocial\b", r"\bcompliment\b", r"\btrend\b"],
    "brand_trust": [r"\bbrand\b", r"\btrust\b", r"\bgenuine\b", r"\bfake\b", r"\boriginal\b"],
    "delivery_returns": [r"\bdelivery\b", r"\bshipping\b", r"\breturn\b", r"\brefund\b", r"\bexchange\b"],
}


def classify_with_keywords(doc_id: str, content: str) -> dict:
    """
    Classify a document into detailed Wishlist-to-Purchase conversion signals.
    """
    text = content.lower()

    # 1. Hesitation reasons
    hesitation_reasons = []
    for reason, patterns in HESITATION_PATTERNS.items():
        for pattern in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                start = max(0, m.start() - 25)
                end = min(len(content), m.end() + 35)
                evidence = content[start:end].strip()
                hesitation_reasons.append({
                    "reason": reason,
                    "confidence": 0.85,
                    "evidence_quote": evidence,
                })
                break

    # If no explicit hesitation tag found, infer from general tone
    if not hesitation_reasons:
        if any(w in text for w in ["good", "best", "love", "nice", "awesome", "perfect"]):
            hesitation_reasons.append({
                "reason": "waiting_for_sale",
                "confidence": 0.60,
                "evidence_quote": content[:60],
            })
        else:
            hesitation_reasons.append({
                "reason": "quality_doubt",
                "confidence": 0.50,
                "evidence_quote": content[:60],
            })

    # 2. Wishlist Intent
    wishlist_intent = "genuine_purchase_intent"
    for intent, patterns in INTENT_PATTERNS.items():
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            wishlist_intent = intent
            break

    # 3. User Segment Signals
    inferred_age = "millennial"
    price_sens = "medium"
    fashion_eng = "high"
    gender_sig = "unknown"

    if any(re.search(p, text, re.IGNORECASE) for p in SEGMENT_PATTERNS["gen_z"]):
        inferred_age = "gen_z"
        fashion_eng = "high"
    elif any(re.search(p, text, re.IGNORECASE) for p in SEGMENT_PATTERNS["working_professionals"]):
        inferred_age = "millennial"
        price_sens = "medium"

    if any(re.search(p, text, re.IGNORECASE) for p in SEGMENT_PATTERNS["deal_seekers"]):
        price_sens = "high"

    if any(w in text for w in ["kurti", "saree", "dress", "heels", "earrings", "handbag", "top", "skirt", "she", "her", "didi"]):
        gender_sig = "female"
    elif any(w in text for w in ["shirt", "tshirt", "jeans", "sneakers", "hoodie", "he", "him", "bhai"]):
        gender_sig = "male"

    # 4. Comparison behavior
    platforms = []
    for platform, patterns in PLATFORM_PATTERNS.items():
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            platforms.append(platform)

    # 5. External info seeking
    info_types = []
    for info_type, patterns in INFO_PATTERNS.items():
        if any(re.search(p, text, re.IGNORECASE) for p in patterns):
            info_types.append(info_type)

    # 6. Factor mentions & sentiments
    factor_mentions = {}
    for factor, patterns in FACTOR_PATTERNS.items():
        mentioned = any(re.search(p, text, re.IGNORECASE) for p in patterns)
        sentiment = "neutral"
        if mentioned:
            if any(w in text for w in ["bad", "poor", "waste", "tight", "loose", "expensive", "slow", "fake", "terrible", "worst", "hate"]):
                sentiment = "negative"
            elif any(w in text for w in ["good", "great", "nice", "love", "perfect", "worth", "cheap", "fast", "original", "best"]):
                sentiment = "positive"
        factor_mentions[factor] = {
            "mentioned": mentioned,
            "sentiment": sentiment,
        }

    # 7. Unmet Needs extraction
    unmet_needs = []
    if any(r["reason"] == "sizing_uncertainty" for r in hesitation_reasons):
        unmet_needs.append("Standardized cross-brand size recommender and model height benchmarks")
    if any(r["reason"] == "waiting_for_sale" for r in hesitation_reasons):
        unmet_needs.append("Automated price-drop and coupon threshold alerts on wishlisted products")
    if any(r["reason"] == "quality_doubt" for r in hesitation_reasons):
        unmet_needs.append("Verified customer fabric video reviews and unedited natural lighting photos")
    if any(r["reason"] == "return_policy_concern" for r in hesitation_reasons):
        unmet_needs.append("Frictionless doorstep exchange without delivery partner dispute")
    if platforms:
        unmet_needs.append(f"Price match guarantee against {', '.join(platforms[:2])}")
    if not unmet_needs:
        unmet_needs.append("Accurate product fit reviews and fabric composition details")

    # 8. Complete Question Mapping (Q1 through Q10)
    q_map = [1, 7, 8, 9, 10]  # Every document provides baseline intent, factor, segment, and unmet need signal
    if any(r["reason"] in ("sizing_uncertainty", "quality_doubt", "style_uncertainty", "information_gap") for r in hesitation_reasons):
        q_map.extend([2, 3])
    if any(r["reason"] in ("waiting_for_sale", "price_sensitivity", "occasion_mismatch", "social_validation_needed") for r in hesitation_reasons):
        q_map.extend([2, 4])
    if platforms or any(r["reason"] == "comparison_paralysis" for r in hesitation_reasons):
        q_map.extend([5])
    if info_types or any(r["reason"] == "social_validation_needed" for r in hesitation_reasons):
        q_map.extend([6])

    return {
        "doc_id": doc_id,
        "classification": {
            "hesitation_reasons": hesitation_reasons[:5],
            "wishlist_intent": wishlist_intent,
            "user_segment_signals": {
                "inferred_age_group": inferred_age,
                "price_sensitivity": price_sens,
                "fashion_engagement": fashion_eng,
                "gender_signal": gender_sig,
            },
            "comparison_behavior": {
                "compares_across_platforms": len(platforms) > 0,
                "platforms_mentioned": platforms,
                "comparison_criteria": ["price", "quality", "return_policy"] if platforms else [],
            },
            "external_info_seeking": {
                "seeks_external_info": len(info_types) > 0,
                "info_types": info_types,
            },
            "factor_mentions": factor_mentions,
            "unmet_needs": unmet_needs[:3],
            "brief_question_mapping": sorted(set(q_map)),
            "is_primary_signal": True,
        },
    }

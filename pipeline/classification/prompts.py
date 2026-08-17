"""
Prompt templates for LLM classification.
System prompt, few-shot examples, and batch formatter.
Matches llm_prompts.md §1–3 exactly.
"""

# ──────────────────────────────────────────────────────────
# System Prompt
# ──────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert analyst classifying user feedback about Myntra, India's largest online fashion retailer.

Your task: For each review/comment provided, extract structured classification tags using the JSON schema below. These tags will be aggregated to answer strategic business questions about why users add fashion products to their wishlist but don't purchase them.

CRITICAL RULES:
1. Respond ONLY with valid JSON. No markdown, no explanations, no extra text.
2. Many reviews are in Hinglish (Hindi-English code-mixed). Classify these with the same schema — do NOT skip them.
3. A single review can have MULTIPLE hesitation reasons, factor mentions, and unmet needs. Extract ALL that apply.
4. Only assign tags you are confident about. Use the "confidence" field (0.0–1.0) to express certainty.
5. Always include an "evidence_quote" — the exact substring from the review supporting each tag.
6. If a review has NO relevant signal for a field, use the default/empty value (e.g., "unknown", empty array).
7. Do NOT hallucinate or infer information not present in the text.
8. For "unmet_needs", extract the user's own words about what they wish existed — do not rephrase.

SCHEMA:
{
  "doc_id": "string — pass through from input",
  "classification": {
    "hesitation_reasons": [
      {
        "reason": "sizing_uncertainty | price_sensitivity | style_uncertainty | quality_doubt | waiting_for_sale | social_validation_needed | occasion_mismatch | comparison_paralysis | trust_deficit | information_gap | return_policy_concern | other",
        "confidence": 0.0-1.0,
        "evidence_quote": "exact substring from the review"
      }
    ],
    "wishlist_intent": "genuine_purchase_intent | bookmarking | aspiration | comparison_shortlist | gift_idea | unknown",
    "user_segment_signals": {
      "inferred_age_group": "gen_z | millennial | gen_x | unknown",
      "price_sensitivity": "high | medium | low | unknown",
      "fashion_engagement": "high | casual | unknown",
      "gender_signal": "male | female | non_binary | unknown"
    },
    "comparison_behavior": {
      "compares_across_platforms": true | false,
      "platforms_mentioned": ["amazon", "ajio", "meesho", "flipkart", "offline_store", "nykaa_fashion", "other"],
      "comparison_criteria": ["price", "quality", "delivery", "return_policy", "variety", "authenticity", "other"]
    },
    "external_info_seeking": {
      "seeks_external_info": true | false,
      "info_types": ["youtube_reviews", "instagram_styling", "google_search", "ask_friends", "offline_trial", "brand_website", "other"]
    },
    "factor_mentions": {
      "fit_size": { "mentioned": true | false, "sentiment": "positive | negative | neutral | mixed" },
      "price": { "mentioned": true | false, "sentiment": "positive | negative | neutral | mixed" },
      "reviews_ratings": { "mentioned": true | false, "sentiment": "positive | negative | neutral | mixed" },
      "styling": { "mentioned": true | false, "sentiment": "positive | negative | neutral | mixed" },
      "occasion": { "mentioned": true | false, "sentiment": "positive | negative | neutral | mixed" },
      "social_validation": { "mentioned": true | false, "sentiment": "positive | negative | neutral | mixed" },
      "brand_trust": { "mentioned": true | false, "sentiment": "positive | negative | neutral | mixed" },
      "delivery_returns": { "mentioned": true | false, "sentiment": "positive | negative | neutral | mixed" }
    },
    "unmet_needs": ["free-text strings — extracted from the user's own words"],
    "brief_question_mapping": [1, 2, 7],
    "is_primary_signal": true | false
  }
}

QUESTION MAPPING REFERENCE:
Map each review to the relevant questions it helps answer (by number):
  1. Why do users add fashion products to their wishlist?
  2. What prevents wishlisted products from being purchased?
  3. What uncertainties remain after identifying a liked product?
  4. What causes users to postpone a purchase?
  5. How do users compare multiple shortlisted products?
  6. What information do users seek outside Myntra before purchasing?
  7. What role do fit, size, styling, price, reviews, occasion and social validation play?
  8. When is the wishlist genuine purchase intent vs bookmarking?
  9. How do these behaviors differ across user segments?
  10. What unmet needs emerge consistently?"""


# ──────────────────────────────────────────────────────────
# Few-Shot Examples
# ──────────────────────────────────────────────────────────

FEW_SHOT_EXAMPLES = [
    # Example 1: English — Price Sensitivity + External Info
    {
        "input": '[Document doc_001]: "I\'ve had this jacket in my wishlist for 2 months now. Love the design but \\u20b93,499 feels steep for the brand. Checked Amazon and it\'s \\u20b9500 cheaper there but out of stock. Might wait for EORS sale. Saw a YouTube review saying the material is thinner than it looks in photos."',
        "output": '{"doc_id":"doc_001","classification":{"hesitation_reasons":[{"reason":"price_sensitivity","confidence":0.92,"evidence_quote":"\\u20b93,499 feels steep for the brand"},{"reason":"waiting_for_sale","confidence":0.88,"evidence_quote":"Might wait for EORS sale"},{"reason":"quality_doubt","confidence":0.75,"evidence_quote":"the material is thinner than it looks in photos"}],"wishlist_intent":"genuine_purchase_intent","user_segment_signals":{"inferred_age_group":"millennial","price_sensitivity":"high","fashion_engagement":"high","gender_signal":"unknown"},"comparison_behavior":{"compares_across_platforms":true,"platforms_mentioned":["amazon"],"comparison_criteria":["price"]},"external_info_seeking":{"seeks_external_info":true,"info_types":["youtube_reviews"]},"factor_mentions":{"fit_size":{"mentioned":false,"sentiment":"neutral"},"price":{"mentioned":true,"sentiment":"negative"},"reviews_ratings":{"mentioned":false,"sentiment":"neutral"},"styling":{"mentioned":true,"sentiment":"positive"},"occasion":{"mentioned":false,"sentiment":"neutral"},"social_validation":{"mentioned":false,"sentiment":"neutral"},"brand_trust":{"mentioned":true,"sentiment":"negative"},"delivery_returns":{"mentioned":false,"sentiment":"neutral"}},"unmet_needs":["price match with other platforms","accurate material/fabric photos"],"brief_question_mapping":[2,4,5,6,7],"is_primary_signal":true}}',
    },
    # Example 2: Hinglish — Sizing + Social Validation
    {
        "input": '[Document doc_002]: "Ye dress bahut acchi hai but size ka pata nahi chalra. Reviews mein koi sizing info nahi hai. Mere friend ne bola ki Myntra ka S bahut tight aata hai. Wishlist mein daala hai, sale ka wait kar rahi hoon. Instagram pe dekha tha styling ideas but brand ka koi page nahi mila."',
        "output": '{"doc_id":"doc_002","classification":{"hesitation_reasons":[{"reason":"sizing_uncertainty","confidence":0.95,"evidence_quote":"size ka pata nahi chalra"},{"reason":"information_gap","confidence":0.82,"evidence_quote":"Reviews mein koi sizing info nahi hai"},{"reason":"waiting_for_sale","confidence":0.85,"evidence_quote":"sale ka wait kar rahi hoon"},{"reason":"social_validation_needed","confidence":0.70,"evidence_quote":"Mere friend ne bola ki Myntra ka S bahut tight aata hai"}],"wishlist_intent":"genuine_purchase_intent","user_segment_signals":{"inferred_age_group":"gen_z","price_sensitivity":"high","fashion_engagement":"high","gender_signal":"female"},"comparison_behavior":{"compares_across_platforms":false,"platforms_mentioned":[],"comparison_criteria":[]},"external_info_seeking":{"seeks_external_info":true,"info_types":["instagram_styling","ask_friends"]},"factor_mentions":{"fit_size":{"mentioned":true,"sentiment":"negative"},"price":{"mentioned":true,"sentiment":"negative"},"reviews_ratings":{"mentioned":true,"sentiment":"negative"},"styling":{"mentioned":true,"sentiment":"positive"},"occasion":{"mentioned":false,"sentiment":"neutral"},"social_validation":{"mentioned":true,"sentiment":"negative"},"brand_trust":{"mentioned":false,"sentiment":"neutral"},"delivery_returns":{"mentioned":false,"sentiment":"neutral"}},"unmet_needs":["sizing information in reviews","brand styling page on Instagram"],"brief_question_mapping":[1,2,3,4,6,7,8],"is_primary_signal":true}}',
    },
    # Example 3: Low-Signal (App crash complaint)
    {
        "input": '[Document doc_003]: "App crashes every time I open it. Worst experience. Fix your app!!"',
        "output": '{"doc_id":"doc_003","classification":{"hesitation_reasons":[],"wishlist_intent":"unknown","user_segment_signals":{"inferred_age_group":"unknown","price_sensitivity":"unknown","fashion_engagement":"unknown","gender_signal":"unknown"},"comparison_behavior":{"compares_across_platforms":false,"platforms_mentioned":[],"comparison_criteria":[]},"external_info_seeking":{"seeks_external_info":false,"info_types":[]},"factor_mentions":{"fit_size":{"mentioned":false,"sentiment":"neutral"},"price":{"mentioned":false,"sentiment":"neutral"},"reviews_ratings":{"mentioned":false,"sentiment":"neutral"},"styling":{"mentioned":false,"sentiment":"neutral"},"occasion":{"mentioned":false,"sentiment":"neutral"},"social_validation":{"mentioned":false,"sentiment":"neutral"},"brand_trust":{"mentioned":true,"sentiment":"negative"},"delivery_returns":{"mentioned":false,"sentiment":"neutral"}},"unmet_needs":["stable app that doesn\'t crash"],"brief_question_mapping":[],"is_primary_signal":false}}',
    },
]


# ──────────────────────────────────────────────────────────
# Batch Request Formatter
# ──────────────────────────────────────────────────────────

def format_batch_prompt(documents: list) -> str:
    """
    Format a batch of documents into the user prompt.
    
    Args:
        documents: List of dicts with 'doc_id' and 'content' keys.
    
    Returns:
        Formatted prompt string.
    """
    parts = ["Classify the following reviews. Return a JSON array with one classification object per document.\n"]

    for doc in documents:
        doc_id = doc.get("doc_id", "unknown")
        content = doc.get("content", "")
        # Truncate very long content to ~500 words
        words = content.split()
        if len(words) > 500:
            content = " ".join(words[:500]) + " [truncated]"
        parts.append(f'[Document {doc_id}]: "{content}"')

    return "\n\n".join(parts)


def build_few_shot_messages() -> list:
    """
    Build the few-shot message history for chat-based APIs.
    Returns list of {"role": "user"/"model", "content": "..."} dicts.
    """
    messages = []
    for example in FEW_SHOT_EXAMPLES:
        messages.append({"role": "user", "content": example["input"]})
        messages.append({"role": "model", "content": example["output"]})
    return messages


def estimate_tokens(text: str) -> int:
    """Rough token estimate — ~4 chars per token for English."""
    return len(text) // 4

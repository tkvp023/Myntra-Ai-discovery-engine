# LLM Prompts & Classification Guide
### AI Discovery Engine — Myntra

---

## 1. Classification System Prompt

This is the **system prompt** sent with every classification API call. It does not change between batches.

```
You are an expert analyst classifying user feedback about Myntra, India's largest online fashion retailer.

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
  10. What unmet needs emerge consistently?
```

---

## 2. Few-Shot Examples

### Example 1: English — Price Sensitivity + External Info Seeking

**Input:**
```
[Document doc_001]: "I've had this jacket in my wishlist for 2 months now. Love the design but ₹3,499 feels steep for the brand. Checked Amazon and it's ₹500 cheaper there but out of stock. Might wait for EORS sale. Saw a YouTube review saying the material is thinner than it looks in photos."
```

**Output:**
```json
{
  "doc_id": "doc_001",
  "classification": {
    "hesitation_reasons": [
      {
        "reason": "price_sensitivity",
        "confidence": 0.92,
        "evidence_quote": "₹3,499 feels steep for the brand"
      },
      {
        "reason": "waiting_for_sale",
        "confidence": 0.88,
        "evidence_quote": "Might wait for EORS sale"
      },
      {
        "reason": "quality_doubt",
        "confidence": 0.75,
        "evidence_quote": "the material is thinner than it looks in photos"
      }
    ],
    "wishlist_intent": "genuine_purchase_intent",
    "user_segment_signals": {
      "inferred_age_group": "millennial",
      "price_sensitivity": "high",
      "fashion_engagement": "high",
      "gender_signal": "unknown"
    },
    "comparison_behavior": {
      "compares_across_platforms": true,
      "platforms_mentioned": ["amazon"],
      "comparison_criteria": ["price"]
    },
    "external_info_seeking": {
      "seeks_external_info": true,
      "info_types": ["youtube_reviews"]
    },
    "factor_mentions": {
      "fit_size": { "mentioned": false, "sentiment": "neutral" },
      "price": { "mentioned": true, "sentiment": "negative" },
      "reviews_ratings": { "mentioned": false, "sentiment": "neutral" },
      "styling": { "mentioned": true, "sentiment": "positive" },
      "occasion": { "mentioned": false, "sentiment": "neutral" },
      "social_validation": { "mentioned": false, "sentiment": "neutral" },
      "brand_trust": { "mentioned": true, "sentiment": "negative" },
      "delivery_returns": { "mentioned": false, "sentiment": "neutral" }
    },
    "unmet_needs": ["price match with other platforms", "accurate material/fabric photos"],
    "brief_question_mapping": [2, 4, 5, 6, 7],
    "is_primary_signal": true
  }
}
```

---

### Example 2: Hinglish — Sizing Uncertainty + Social Validation

**Input:**
```
[Document doc_002]: "Ye dress bahut acchi hai but size ka pata nahi chalra. Reviews mein koi sizing info nahi hai. Mere friend ne bola ki Myntra ka S bahut tight aata hai. Wishlist mein daala hai, sale ka wait kar rahi hoon. Instagram pe dekha tha styling ideas but brand ka koi page nahi mila."
```

**Output:**
```json
{
  "doc_id": "doc_002",
  "classification": {
    "hesitation_reasons": [
      {
        "reason": "sizing_uncertainty",
        "confidence": 0.95,
        "evidence_quote": "size ka pata nahi chalra"
      },
      {
        "reason": "information_gap",
        "confidence": 0.82,
        "evidence_quote": "Reviews mein koi sizing info nahi hai"
      },
      {
        "reason": "waiting_for_sale",
        "confidence": 0.85,
        "evidence_quote": "sale ka wait kar rahi hoon"
      },
      {
        "reason": "social_validation_needed",
        "confidence": 0.70,
        "evidence_quote": "Mere friend ne bola ki Myntra ka S bahut tight aata hai"
      }
    ],
    "wishlist_intent": "genuine_purchase_intent",
    "user_segment_signals": {
      "inferred_age_group": "gen_z",
      "price_sensitivity": "high",
      "fashion_engagement": "high",
      "gender_signal": "female"
    },
    "comparison_behavior": {
      "compares_across_platforms": false,
      "platforms_mentioned": [],
      "comparison_criteria": []
    },
    "external_info_seeking": {
      "seeks_external_info": true,
      "info_types": ["instagram_styling", "ask_friends"]
    },
    "factor_mentions": {
      "fit_size": { "mentioned": true, "sentiment": "negative" },
      "price": { "mentioned": true, "sentiment": "negative" },
      "reviews_ratings": { "mentioned": true, "sentiment": "negative" },
      "styling": { "mentioned": true, "sentiment": "positive" },
      "occasion": { "mentioned": false, "sentiment": "neutral" },
      "social_validation": { "mentioned": true, "sentiment": "negative" },
      "brand_trust": { "mentioned": false, "sentiment": "neutral" },
      "delivery_returns": { "mentioned": false, "sentiment": "neutral" }
    },
    "unmet_needs": ["sizing information in reviews", "brand styling page on Instagram"],
    "brief_question_mapping": [1, 2, 3, 4, 6, 7, 8],
    "is_primary_signal": true
  }
}
```

---

### Example 3: Low-Signal Review (App Store complaint)

**Input:**
```
[Document doc_003]: "App crashes every time I open it. Worst experience. Fix your app!!"
```

**Output:**
```json
{
  "doc_id": "doc_003",
  "classification": {
    "hesitation_reasons": [],
    "wishlist_intent": "unknown",
    "user_segment_signals": {
      "inferred_age_group": "unknown",
      "price_sensitivity": "unknown",
      "fashion_engagement": "unknown",
      "gender_signal": "unknown"
    },
    "comparison_behavior": {
      "compares_across_platforms": false,
      "platforms_mentioned": [],
      "comparison_criteria": []
    },
    "external_info_seeking": {
      "seeks_external_info": false,
      "info_types": []
    },
    "factor_mentions": {
      "fit_size": { "mentioned": false, "sentiment": "neutral" },
      "price": { "mentioned": false, "sentiment": "neutral" },
      "reviews_ratings": { "mentioned": false, "sentiment": "neutral" },
      "styling": { "mentioned": false, "sentiment": "neutral" },
      "occasion": { "mentioned": false, "sentiment": "neutral" },
      "social_validation": { "mentioned": false, "sentiment": "neutral" },
      "brand_trust": { "mentioned": true, "sentiment": "negative" },
      "delivery_returns": { "mentioned": false, "sentiment": "neutral" }
    },
    "unmet_needs": ["stable app that doesn't crash"],
    "brief_question_mapping": [],
    "is_primary_signal": false
  }
}
```

---

### Example 4: Comparison + Bookmarking Behavior

**Input:**
```
[Document doc_004]: "I use Myntra wishlist more like a Pinterest board lol. I'll add 50 items then never buy any of them. Sometimes I compare prices on AJIO and Meesho for the same brands. If the quality reviews are good and price is lower, I'll buy from there. Myntra's return policy is better though so for expensive stuff I still prefer Myntra."
```

**Output:**
```json
{
  "doc_id": "doc_004",
  "classification": {
    "hesitation_reasons": [
      {
        "reason": "comparison_paralysis",
        "confidence": 0.80,
        "evidence_quote": "I compare prices on AJIO and Meesho for the same brands"
      },
      {
        "reason": "price_sensitivity",
        "confidence": 0.78,
        "evidence_quote": "If the quality reviews are good and price is lower, I'll buy from there"
      }
    ],
    "wishlist_intent": "bookmarking",
    "user_segment_signals": {
      "inferred_age_group": "gen_z",
      "price_sensitivity": "high",
      "fashion_engagement": "high",
      "gender_signal": "unknown"
    },
    "comparison_behavior": {
      "compares_across_platforms": true,
      "platforms_mentioned": ["ajio", "meesho"],
      "comparison_criteria": ["price", "quality", "return_policy"]
    },
    "external_info_seeking": {
      "seeks_external_info": false,
      "info_types": []
    },
    "factor_mentions": {
      "fit_size": { "mentioned": false, "sentiment": "neutral" },
      "price": { "mentioned": true, "sentiment": "negative" },
      "reviews_ratings": { "mentioned": true, "sentiment": "positive" },
      "styling": { "mentioned": false, "sentiment": "neutral" },
      "occasion": { "mentioned": false, "sentiment": "neutral" },
      "social_validation": { "mentioned": false, "sentiment": "neutral" },
      "brand_trust": { "mentioned": false, "sentiment": "neutral" },
      "delivery_returns": { "mentioned": true, "sentiment": "positive" }
    },
    "unmet_needs": ["price parity with competitor platforms"],
    "brief_question_mapping": [1, 2, 5, 7, 8],
    "is_primary_signal": true
  }
}
```

---

### Example 5: Aspiration / Gift Idea

**Input:**
```
[Document doc_005]: "Added a Levi's denim jacket for my boyfriend's birthday. ₹4,999 is way over my budget rn but maybe next month. Hope they have a sale before October."
```

**Output:**
```json
{
  "doc_id": "doc_005",
  "classification": {
    "hesitation_reasons": [
      {
        "reason": "price_sensitivity",
        "confidence": 0.90,
        "evidence_quote": "₹4,999 is way over my budget rn"
      },
      {
        "reason": "waiting_for_sale",
        "confidence": 0.85,
        "evidence_quote": "Hope they have a sale before October"
      }
    ],
    "wishlist_intent": "gift_idea",
    "user_segment_signals": {
      "inferred_age_group": "gen_z",
      "price_sensitivity": "high",
      "fashion_engagement": "casual",
      "gender_signal": "female"
    },
    "comparison_behavior": {
      "compares_across_platforms": false,
      "platforms_mentioned": [],
      "comparison_criteria": []
    },
    "external_info_seeking": {
      "seeks_external_info": false,
      "info_types": []
    },
    "factor_mentions": {
      "fit_size": { "mentioned": false, "sentiment": "neutral" },
      "price": { "mentioned": true, "sentiment": "negative" },
      "reviews_ratings": { "mentioned": false, "sentiment": "neutral" },
      "styling": { "mentioned": false, "sentiment": "neutral" },
      "occasion": { "mentioned": true, "sentiment": "positive" },
      "social_validation": { "mentioned": false, "sentiment": "neutral" },
      "brand_trust": { "mentioned": true, "sentiment": "positive" },
      "delivery_returns": { "mentioned": false, "sentiment": "neutral" }
    },
    "unmet_needs": ["price drop notifications", "wishlist sale alerts"],
    "brief_question_mapping": [1, 2, 4, 7, 8],
    "is_primary_signal": true
  }
}
```

---

## 3. Batch Request Format

The user prompt for each classification batch:

```
Classify the following reviews. Return a JSON array with one classification object per document.

[Document {doc_id_1}]: "{content_1}"

[Document {doc_id_2}]: "{content_2}"

...

[Document {doc_id_N}]: "{content_N}"
```

### Batch Configuration

| Parameter | Value | Rationale |
|---|---|---|
| Batch size | 10 documents | Fits well within token limits for all model tiers |
| Max input tokens per batch | ~8,000 | Leaves room for the schema + few-shot in system prompt |
| Max output tokens per batch | ~12,000 | 10 detailed classifications at ~1,200 tokens each |
| Temperature | 0.1 | Low temperature for consistent, deterministic output |
| Top-p | 0.95 | Standard |
| Response format | `application/json` (Gemini) / JSON mode (Groq) | Enforces valid JSON |

---

## 4. RAG Answer Generation Prompt

Used when a user asks a question via the "Ask the Data" chat interface:

```
You are the AI Discovery Engine assistant for Myntra wishlist intelligence.
You answer questions based ONLY on the retrieved evidence provided below.

RULES:
1. Base your answer ONLY on the retrieved documents. Do NOT use external knowledge.
2. Cite sources using [Source: {source}, {date}] format after each claim.
3. Include quantitative data where available (counts, percentages).
4. If the retrieved evidence doesn't contain enough information to answer, say so explicitly.
5. Keep answers concise but data-rich. Use bullet points.
6. If the user asks about a specific segment (Gen-Z, Millennial, etc.), filter your answer accordingly.

RETRIEVED EVIDENCE:
{retrieved_documents}

USER QUESTION:
{user_query}

FILTERS APPLIED:
- Segment: {segment_filter or "all"}
- Source: {source_filter or "all"}
- Question category: {question_filter or "all"}
```

---

## 5. Validation Rules

### Post-Classification Validation

After receiving LLM output, validate each classification:

```python
VALIDATION_RULES = {
    # Drop tags below confidence threshold
    "min_confidence": 0.4,
    
    # Valid enum values
    "valid_hesitation_reasons": [
        "sizing_uncertainty", "price_sensitivity", "style_uncertainty",
        "quality_doubt", "waiting_for_sale", "social_validation_needed",
        "occasion_mismatch", "comparison_paralysis", "trust_deficit",
        "information_gap", "return_policy_concern", "other"
    ],
    "valid_wishlist_intents": [
        "genuine_purchase_intent", "bookmarking", "aspiration",
        "comparison_shortlist", "gift_idea", "unknown"
    ],
    "valid_age_groups": ["gen_z", "millennial", "gen_x", "unknown"],
    "valid_sentiments": ["positive", "negative", "neutral", "mixed"],
    
    # Structural checks
    "max_hesitation_reasons": 6,       # Unlikely to have more than 6
    "max_unmet_needs": 5,              # Cap at 5 per review
    "evidence_quote_min_length": 5,    # Must be at least 5 chars
    "evidence_must_be_substring": True, # Quote must exist in original content
}
```

### Validation Pipeline

```python
def validate_classification(doc_content, classification):
    errors = []
    
    # 1. Check JSON structure
    if not isinstance(classification, dict):
        errors.append("Not a valid JSON object")
        return errors
    
    # 2. Validate hesitation reasons
    for reason in classification.get("hesitation_reasons", []):
        if reason["reason"] not in VALID_HESITATION_REASONS:
            errors.append(f"Invalid reason: {reason['reason']}")
        if reason["confidence"] < MIN_CONFIDENCE:
            # Don't error — just drop silently
            pass
        if reason["evidence_quote"] not in doc_content:
            errors.append(f"Evidence quote not found in source: {reason['evidence_quote'][:50]}")
    
    # 3. Validate enums
    if classification.get("wishlist_intent") not in VALID_WISHLIST_INTENTS:
        classification["wishlist_intent"] = "unknown"
    
    # 4. Cap array lengths
    classification["unmet_needs"] = classification.get("unmet_needs", [])[:5]
    
    return errors  # Empty = valid
```

---

## 6. Edge Cases & Handling

| Edge Case | How to Handle |
|---|---|
| Review is entirely in Hindi (Devanagari script) | Mark as `is_primary_signal: false`, skip classification (our cleaning pipeline filters these out first) |
| Review is just "Good app" or "Nice" | Classify with empty arrays/unknown. `is_primary_signal: false`. |
| Review mentions Myntra but is about a different topic | Set `is_primary_signal: false`. Still extract any relevant factor mentions. |
| Review has profanity/anger | Classify normally. Anger often contains strong signal about hesitation reasons. |
| Review is a reply/conversation fragment | Use `metadata.parent_id` context if available. Classify the standalone text as-is. |
| LLM returns invalid JSON | Retry once with stricter prompt. If still invalid, log and skip document. |
| LLM returns empty classification | Accept it — some reviews genuinely have no relevant signal. |
| Review mentions multiple products | Extract all signals — they represent general shopping behavior patterns. |

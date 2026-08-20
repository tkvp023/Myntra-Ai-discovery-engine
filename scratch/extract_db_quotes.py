import sqlite3
import json

conn = sqlite3.connect('data/db.sqlite')
conn.row_factory = sqlite3.Row
c = conn.cursor()

def get_quotes_by_intent(intent, limit=2):
    query = """
    SELECT d.doc_id, d.source, d.source_id, d.content, d.title, c.wishlist_intent, c.inferred_age_group
    FROM documents d
    JOIN classifications c ON d.doc_id = c.doc_id
    WHERE c.wishlist_intent = ? AND length(d.content) BETWEEN 40 AND 350
    LIMIT ?
    """
    rows = c.execute(query, (intent, limit)).fetchall()
    return [dict(r) for r in rows]

def get_quotes_by_hesitation(reason, limit=2):
    query = """
    SELECT d.doc_id, d.source, d.source_id, d.content, h.reason, h.confidence, h.evidence_quote, c.inferred_age_group
    FROM documents d
    JOIN hesitation_tags h ON d.doc_id = h.doc_id
    JOIN classifications c ON d.doc_id = c.doc_id
    WHERE h.reason = ? AND length(d.content) BETWEEN 40 AND 350
    LIMIT ?
    """
    rows = c.execute(query, (reason, limit)).fetchall()
    return [dict(r) for r in rows]

def get_quotes_by_factor(factor, sentiment=None, limit=2):
    query = """
    SELECT d.doc_id, d.source, d.source_id, d.content, f.factor, f.sentiment
    FROM documents d
    JOIN factor_mentions f ON d.doc_id = f.doc_id
    WHERE f.factor = ? AND (? IS NULL OR f.sentiment = ?) AND length(d.content) BETWEEN 40 AND 350
    LIMIT ?
    """
    rows = c.execute(query, (factor, sentiment, sentiment, limit)).fetchall()
    return [dict(r) for r in rows]

def get_quotes_by_segment_and_reason(segment, reason, limit=2):
    query = """
    SELECT d.doc_id, d.source, d.source_id, d.content, c.inferred_age_group, h.reason, h.evidence_quote
    FROM documents d
    JOIN classifications c ON d.doc_id = c.doc_id
    JOIN hesitation_tags h ON d.doc_id = h.doc_id
    WHERE c.inferred_age_group = ? AND h.reason = ? AND length(d.content) BETWEEN 40 AND 350
    LIMIT ?
    """
    rows = c.execute(query, (segment, reason, limit)).fetchall()
    return [dict(r) for r in rows]

def search_text_quotes(keywords, limit=2):
    where_clauses = " AND ".join(["LOWER(d.content) LIKE ?" for _ in keywords])
    params = [f"%{k.lower()}%" for k in keywords] + [limit]
    query = f"""
    SELECT d.doc_id, d.source, d.source_id, d.content, c.inferred_age_group
    FROM documents d
    JOIN classifications c ON d.doc_id = c.doc_id
    WHERE {where_clauses} AND length(d.content) BETWEEN 40 AND 350
    LIMIT ?
    """
    rows = c.execute(query, params).fetchall()
    return [dict(r) for r in rows]

print("=== WISHLIST INTENTS ===")
for intent in ['genuine_purchase_intent', 'comparison_shortlist', 'bookmarking', 'gift_idea', 'aspiration']:
    print(f"\n--- Intent: {intent} ---")
    for q in get_quotes_by_intent(intent, 2):
        print(f"[{q['source']} | ID: {q['doc_id'][:8]}] {q['content']}")

print("\n=== HESITATION REASONS ===")
for reason in ['quality_doubt', 'waiting_for_sale', 'social_validation_needed', 'price_sensitivity', 'sizing_uncertainty', 'style_uncertainty', 'return_policy_concern', 'occasion_mismatch', 'trust_deficit', 'comparison_paralysis', 'information_gap']:
    print(f"\n--- Reason: {reason} ---")
    for q in get_quotes_by_hesitation(reason, 2):
        print(f"[{q['source']} | ID: {q['doc_id'][:8]}] {q['content']}")

print("\n=== SEGMENT SAMPLES ===")
print("Gen Z + Social Validation:")
for q in get_quotes_by_segment_and_reason('gen_z', 'social_validation_needed', 2):
    print(f"[{q['source']} | ID: {q['doc_id'][:8]}] {q['content']}")

print("\nMillennial + Quality Doubt:")
for q in get_quotes_by_segment_and_reason('millennial', 'quality_doubt', 2):
    print(f"[{q['source']} | ID: {q['doc_id'][:8]}] {q['content']}")

print("\n=== FACTOR SAMPLES ===")
for factor in ['delivery_returns', 'price', 'brand_trust', 'reviews_ratings', 'styling', 'fit_size']:
    print(f"\n--- Factor: {factor} ---")
    for q in get_quotes_by_factor(factor, None, 1):
        print(f"[{q['source']} | ID: {q['doc_id'][:8]} | Sentiment: {q['sentiment']}] {q['content']}")

print("\n=== COMPETITOR SEARCH ===")
for comp in ['meesho', 'ajio', 'flipkart']:
    print(f"\n--- Mentioning {comp} ---")
    for q in search_text_quotes([comp], 2):
        print(f"[{q['source']} | ID: {q['doc_id'][:8]}] {q['content']}")


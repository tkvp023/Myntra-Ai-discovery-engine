import sqlite3
import json

conn = sqlite3.connect('data/db.sqlite')
conn.row_factory = sqlite3.Row
c = conn.cursor()

def search_best(sql_where, params=(), limit=1):
    sql = f"""
    SELECT d.doc_id, d.source, d.source_id, d.content, d.title, d.author
    FROM documents d
    WHERE {sql_where}
    LIMIT ?
    """
    rows = c.execute(sql, params + (limit,)).fetchall()
    return [dict(r) for r in rows]

# 1. Wishlist Intent Quotes
q_intent_genuine = search_best("content LIKE '%wishlist%' AND (content LIKE '%buy%' OR content LIKE '%cart%' OR content LIKE '%limit%')", limit=2)
q_intent_compare = search_best("(content LIKE '%choose between%' OR content LIKE '%compare%') AND (content LIKE '%size%' OR content LIKE '%brand%' OR content LIKE '%shoe%')", limit=2)
q_intent_bookmark = search_best("content LIKE '%collection%' AND (content LIKE '%browse%' OR content LIKE '%view%' OR content LIKE '%save%')", limit=2)

# 2. Quality & Fabric
q_quality = search_best("(content LIKE '%fabric%' OR content LIKE '%material%') AND (content LIKE '%bad%' OR content LIKE '%thin%' OR content LIKE '%cheap%' OR content LIKE '%different%')", limit=2)
q_quality_positive = search_best("(content LIKE '%fabric%' OR content LIKE '%material%') AND (content LIKE '%comfortable%' OR content LIKE '%good%' OR content LIKE '%soft%')", limit=2)

# 3. Waiting for Sale / Pricing
q_sale_waiting = search_best("(content LIKE '%sale%' OR content LIKE '%eors%') AND (content LIKE '%price%' OR content LIKE '%discount%' OR content LIKE '%cart%')", limit=2)
q_price_sensitivity = search_best("(content LIKE '%convenience fee%' OR content LIKE '%delivery fee%' OR content LIKE '%expensive%')", limit=2)

# 4. Sizing & Fit
q_sizing = search_best("content LIKE '%size%' AND (content LIKE '%tight%' OR content LIKE '%fitting%' OR content LIKE '%chart%' OR content LIKE '%exchange%')", limit=2)

# 5. Social Validation & Peer opinion
q_social = search_best("(content LIKE '%haul%' OR content LIKE '%review%' OR content LIKE '%suggest%' OR content LIKE '%recommend%') AND length(content) BETWEEN 60 AND 250", limit=2)

# 6. Returns & Delivery Friction
q_returns = search_best("(content LIKE '%refund%' OR content LIKE '%return%') AND (content LIKE '%tag%' OR content LIKE '%delivery%' OR content LIKE '%pickup%' OR content LIKE '%cancel%')", limit=2)

# 7. Competitor comparisons
q_meesho = search_best("content LIKE '%meesho%'", limit=2)
q_ajio = search_best("content LIKE '%ajio%'", limit=2)
q_flipkart = search_best("content LIKE '%flipkart%'", limit=2)

# 8. Unmet Needs
q_video_need = search_best("(content LIKE '%video%' OR content LIKE '%photo%') AND (content LIKE '%dress%' OR content LIKE '%fabric%' OR content LIKE '%try%')", limit=2)

print("INTENT GENUINE:", q_intent_genuine)
print("INTENT COMPARE:", q_intent_compare)
print("QUALITY:", q_quality)
print("SALE WAITING:", q_sale_waiting)
print("PRICE SENSITIVITY:", q_price_sensitivity)
print("SIZING:", q_sizing)
print("SOCIAL:", q_social)
print("RETURNS:", q_returns)
print("MEESHO:", q_meesho)
print("AJIO:", q_ajio)
print("FLIPKART:", q_flipkart)

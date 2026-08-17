# Testing Plan
### AI Discovery Engine — Myntra

---

## 1. Testing Strategy Overview

| Layer | Testing Type | Tools |
|---|---|---|
| Scrapers | Unit + Integration | pytest, manual spot-check |
| Cleaning Pipeline | Unit + Validation | pytest, statistical checks |
| LLM Classification | Quality Sampling + Validation | Manual review, automated schema validation |
| Quantification | Unit + Consistency | pytest, cross-validation |
| Dashboard | Visual + Functional | Browser testing, Lighthouse |
| RAG | Quality + Accuracy | Manual query testing, relevance scoring |
| End-to-End | Integration | Full pipeline run + dashboard verification |

---

## 2. Scraper Testing

### 2.1 Unit Tests (per scraper)

```python
# tests/test_scrapers.py

def test_playstore_scraper_returns_documents():
    """Fetch 10 reviews and verify unified schema."""
    scraper = PlayStoreScraper(config=TEST_CONFIG)
    docs = scraper.scrape(limit=10)
    assert len(docs) == 10
    for doc in docs:
        assert_valid_unified_schema(doc)

def test_reddit_scraper_auth():
    """Verify Reddit OAuth works."""
    scraper = RedditScraper(config=TEST_CONFIG)
    assert scraper.authenticate() is True

def test_checkpoint_resume():
    """Scraper resumes from last checkpoint, not from scratch."""
    scraper = PlayStoreScraper(config=TEST_CONFIG)
    scraper.scrape(limit=100)
    checkpoint = scraper.get_checkpoint()
    assert checkpoint["docs_scraped"] == 100
    
    # Resume — should not re-scrape existing docs
    scraper2 = PlayStoreScraper(config=TEST_CONFIG)
    scraper2.load_checkpoint(checkpoint)
    new_docs = scraper2.scrape(limit=50)
    assert all(d["doc_id"] not in existing_ids for d in new_docs)
```

### 2.2 Schema Validation

```python
def assert_valid_unified_schema(doc):
    """Validate a document matches the unified schema."""
    required_fields = ["doc_id", "source", "source_type", "content", "scraped_at"]
    for field in required_fields:
        assert field in doc, f"Missing required field: {field}"
    
    assert doc["source"] in VALID_SOURCES
    assert doc["source_type"] in ["primary", "secondary"]
    assert len(doc["content"]) > 0
    assert doc["doc_id"] is not None
```

### 2.3 Integration Test

| Check | Expected | Pass Criteria |
|---|---|---|
| Play Store returns reviews | 50K+ | Count > 40,000 |
| App Store returns reviews | 5K+ | Count > 3,000 |
| Reddit returns posts+comments | 10K+ | Count > 8,000 |
| YouTube returns comments | 5K+ | Count > 4,000 |
| Trustpilot returns reviews | 2K+ | Count > 1,500 |
| PissedConsumer returns reviews | 1K+ | Count > 800 |
| Reviews.io returns reviews | 500+ | Count > 300 |
| All docs in unified schema | 100% | Zero schema violations |
| No duplicate doc_ids | 0 | Zero duplicates within a source |

### 2.4 Manual Spot-Check (per source)

- [ ] Read 20 random documents per source
- [ ] Verify content is actual Myntra-related feedback (not spam/noise)
- [ ] Verify timestamps are reasonable (not all the same date)
- [ ] Verify ratings match content sentiment (quick sanity check)

---

## 3. Cleaning Pipeline Testing

### 3.1 Unit Tests

```python
def test_language_filter():
    """Keeps English and Hinglish, drops others."""
    assert language_filter("This product is great") == True       # English
    assert language_filter("Ye bahut accha hai") == True           # Hinglish
    assert language_filter("यह बहुत अच्छा है") == False           # Pure Hindi
    assert language_filter("") == False                            # Empty

def test_deduplication():
    """Near-duplicates are removed."""
    docs = [
        {"content": "The quality is really bad, fabric is thin"},
        {"content": "The quality is really bad, the fabric is thin"},  # Near-dup
        {"content": "Great app, love the collection!"},
    ]
    result = deduplicate(docs, threshold=0.85)
    assert len(result) == 2

def test_relevance_filter():
    """Non-fashion content is filtered out."""
    assert relevance_filter("Myntra dress sizing is terrible") == True
    assert relevance_filter("I love cooking pasta") == False
    assert relevance_filter("Great app for fashion shopping") == True
```

### 3.2 Statistical Checks

After running the full cleaning pipeline, verify:

| Metric | Expected Range | Action if Out of Range |
|---|---|---|
| Dedup removal rate | 3–8% | If >15%, check for scraper duplication bug |
| Language filter removal rate | 2–5% | If >10%, filter is too aggressive (check Hinglish handling) |
| Relevance filter removal rate | 5–15% | If >25%, filter is too strict; if <2%, filter is too loose |
| Length filter removal rate | 5–10% | Expected — many short reviews |
| Overall retention rate | 70–90% | If <60%, investigate which filter is dropping too much |

---

## 4. LLM Classification Testing

### 4.1 Prompt Validation (before full run)

**Test batch:** 50 diverse documents (mix of English, Hinglish, short, long, high-signal, low-signal)

| Check | Method | Pass Criteria |
|---|---|---|
| Valid JSON output | Parse each response | 100% valid JSON |
| Schema compliance | Validate against Pydantic models | 100% compliant |
| Evidence quotes exist in source | Substring match | >95% match |
| Confidence scores reasonable | Distribution check | Mean between 0.5–0.85 |
| No hallucinated tags | Manual review | <5% hallucination rate |
| Hinglish handled correctly | Review Hinglish subset | >80% correct tags |
| Low-signal reviews handled | Check "unknown"/empty | Should be empty, not forced tags |

### 4.2 Classification Quality Benchmark

After full corpus classification, sample 100 random documents and manually grade:

```
Grading rubric per document:
- Hesitation reasons: Correct (+1), Partially correct (+0.5), Wrong (-1), Missing (-0.5)
- Wishlist intent: Correct (+1), Wrong (-1)
- Factor mentions: Correct (+1), Missing (-0.5), Hallucinated (-1)
- Overall: Grade as A (perfect), B (minor issues), C (significant issues), F (wrong)

Target: >80% A or B grades
```

### 4.3 Automated Validation (post-classification)

```python
def test_classification_validation():
    """Run validation rules from llm_prompts.md."""
    classifications = load_all_classifications()
    
    errors_by_type = Counter()
    for cls in classifications:
        errors = validate_classification(cls)
        for e in errors:
            errors_by_type[e.type] += 1
    
    total = len(classifications)
    assert errors_by_type["invalid_enum"] / total < 0.02      # <2% invalid enums
    assert errors_by_type["quote_not_found"] / total < 0.10    # <10% quote mismatches
    assert errors_by_type["invalid_json"] / total < 0.01       # <1% JSON errors
```

### 4.4 Distribution Sanity Checks

| Distribution | Expected | Red Flag |
|---|---|---|
| Top hesitation reason | 20–40% of docs | If >60%, model is over-tagging one category |
| "unknown" wishlist intent | 20–40% | If >60%, model isn't classifying properly |
| Documents with 0 hesitation reasons | 30–50% | If <10%, model is hallucinating reasons |
| Documents with >4 hesitation reasons | <5% | If >15%, model is over-tagging |
| Confidence score mean | 0.60–0.80 | If >0.90, model is over-confident (suspicious) |

---

## 5. Quantification Testing

### 5.1 Consistency Checks

```python
def test_percentages_sum():
    """Breakdown percentages should approximately sum to 100% (or less, for multi-tag)."""
    for q in range(1, 11):
        data = load_json(f"q{q}.json")
        # For single-tag fields (like wishlist_intent), should sum to ~100%
        if q in [1, 8]:  # Intent distribution
            total_pct = sum(item["pct"] for item in data["breakdown"])
            assert 95 <= total_pct <= 105

def test_counts_match_total():
    """Sum of breakdown counts should not exceed total_relevant_docs."""
    for q in range(1, 11):
        data = load_json(f"q{q}.json")
        total_counts = sum(item["count"] for item in data["breakdown"])
        # Multi-tag: total can exceed total_relevant_docs (one doc → multiple tags)
        # But shouldn't be >3x
        assert total_counts <= data["total_relevant_docs"] * 3

def test_segment_splits_consistent():
    """Segment split counts should roughly sum to the main breakdown count."""
    for q in range(1, 11):
        data = load_json(f"q{q}.json")
        for item in data["breakdown"]:
            tag = item["tag"]
            segment_total = sum(
                seg_item["count"]
                for segment in data["segment_splits"].values()
                for seg_item in segment
                if seg_item["tag"] == tag
            )
            # Allow 10% tolerance (some docs have "unknown" segment)
            assert segment_total <= item["count"] * 1.1
```

### 5.2 Cross-Validation

| Check | Method |
|---|---|
| `summary.json` totals match sum of q1–q10 | Compare total_relevant_docs |
| Source distribution matches DB query | Run `SELECT source, COUNT(*) FROM documents GROUP BY source` |
| KPI card values match corresponding question data | Cross-reference |

---

## 6. Dashboard Testing

### 6.1 Visual Testing

| Page | Checks |
|---|---|
| Summary | All 4 stat cards render; sparklines animate; source bar chart loads; top 5 bars render |
| Q1–Q10 | All charts render with data; segment toggle works; quote cards expand; confidence badges colored correctly |
| Systemic Gaps | Issue bars render; source split chart loads; scatter plot renders |
| Ask the Data | Chat UI renders; suggested queries clickable; input field functional |

### 6.2 Functional Testing

| Test | Steps | Expected |
|---|---|---|
| Segment toggle | Click "Gen-Z" toggle on Q2 | All charts in Q2 update to show Gen-Z data only |
| Chart hover | Hover over a bar in horizontal bar chart | Tooltip shows label, count, pct, confidence |
| Quote expand | Click "Read more" on a quote card | Card expands to show full text |
| Navigation | Click Q5 in nav | Page scrolls/routes to Q5 section |
| RAG chat | Type "What causes sizing issues?" and submit | Returns answer with citations |
| Filter chat | Select "Gen-Z" segment filter, then ask a question | Answer is filtered to Gen-Z data |
| Empty state | Load a question with no data | Shows "No data available" message |
| Responsive | Resize browser to 768px | Layout switches to 2-column |

### 6.3 Performance Testing

```bash
# Run Lighthouse audit
npx lighthouse http://localhost:3000 --output json --output-path lighthouse.json

# Targets:
# Performance: > 90
# Accessibility: > 90
# Best Practices: > 90
# SEO: > 90
```

---

## 7. RAG Testing

### 7.1 Quality Test Queries

| Query | Expected Answer Contains | Checks |
|---|---|---|
| "What is the top hesitation reason?" | Sizing uncertainty, ~34% | Matches quantification data |
| "What do Gen-Z users say about pricing?" | Price sensitivity mentions, sale waiting | Segment filter works |
| "How does Reddit differ from Play Store?" | Different signal distributions | Source-aware |
| "What are the main unmet needs?" | Size charts, styling help, price alerts | Matches Q10 data |
| "Do users compare Myntra with AJIO?" | Yes, comparison mentions + criteria | Matches Q5 data |

### 7.2 Accuracy Scoring

For each test query:
1. Rate answer relevance: 1 (irrelevant) to 5 (perfectly relevant)
2. Rate citation accuracy: Are cited sources real and relevant?
3. Rate factual consistency: Does answer match quantified data?

**Target: Average score > 3.5 across all test queries**

### 7.3 Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| Empty query | "Please enter a question" message |
| Very long query (500+ chars) | Truncate and process |
| Query about non-Myntra topic | "I can only answer questions about Myntra user feedback" |
| Profanity in query | Process normally, ignore profanity |
| Query in Hindi | Best-effort answer (may be lower quality) |

---

## 8. End-to-End Pipeline Test

Run the complete pipeline from scratch on a small subset:

```bash
# 1. Scrape 100 docs per source (test mode)
python run_pipeline.py --mode scrape --test-limit 100

# 2. Clean
python run_pipeline.py --mode clean

# 3. Classify
python run_pipeline.py --mode classify

# 4. Quantify + export
python run_pipeline.py --mode quantify

# 5. Verify JSON output
python run_pipeline.py --mode validate

# 6. Start dashboard
cd dashboard && npm run dev

# 7. Verify all pages render with data
```

**Pass criteria:** All pages render, all charts show data, no console errors, RAG returns answers.

---

## 9. Pre-Deployment Checklist

- [ ] All unit tests pass
- [ ] All JSON files validate against schemas
- [ ] Dashboard Lighthouse score > 90
- [ ] RAG quality score > 3.5 average
- [ ] No console errors in browser
- [ ] Responsive layout works at all breakpoints
- [ ] All environment variables set in Vercel
- [ ] Production build completes without errors (`npm run build`)
- [ ] Deployed URL accessible and functional

# Evaluation Framework
### AI Discovery Engine — Myntra
### Metrics, Benchmarks & Scoring Rubrics

---

> **Purpose:** This document defines how to measure the quality, accuracy, and performance of every component in the pipeline — from scraped data to final dashboard. Each eval has a metric, benchmark, measurement method, and pass/fail criteria.

---

## 1. Scraper Evaluation

### 1.1 Volume Metrics

| Metric | Definition | Target | Fail Threshold | Measurement |
|---|---|---|---|---|
| **Total corpus size** | Sum of all scraped documents | >50,000 | <20,000 | `SELECT COUNT(*) FROM documents` |
| **Play Store volume** | Reviews from Google Play | >40,000 | <20,000 | Count in `data/raw/playstore/` |
| **Reddit volume** | Posts + comments from Reddit | >8,000 | <3,000 | Count in `data/raw/reddit/` |
| **YouTube volume** | Comments from YouTube | >4,000 | <1,500 | Count in `data/raw/youtube/` |
| **App Store volume** | Reviews from Apple App Store | >3,000 | <500 | Count in `data/raw/appstore/` |
| **Secondary volume** | Trustpilot + PissedConsumer + Reviews.io | >1,500 | <300 | Count in secondary source dirs |
| **Source diversity** | No single source >70% of total | ≤70% | >85% | `source_distribution` in summary.json |

### 1.2 Quality Metrics

| Metric | Definition | Target | Measurement |
|---|---|---|---|
| **Schema compliance** | % of docs matching unified schema | 100% | Pydantic validation on all docs |
| **Non-empty content** | % of docs with `len(content) > 0` | 100% | `sum(1 for d in docs if d.content)` |
| **Dedup within source** | 0 duplicate `source_id` per source | 0 dupes | `len(ids) == len(set(ids))` per source |
| **Timestamp validity** | % of docs with parseable timestamp | >90% | ISO-8601 parse attempt |
| **Content readability** | Spot-check: % of 50 random docs that are actual user reviews | >95% | Manual review |

### 1.3 Scraper Health Eval

```python
def eval_scraper_health(data_dir):
    """Run after scraping. Returns pass/fail report."""
    results = {}
    for source in VALID_SOURCES:
        docs = load_docs(data_dir / "raw" / source)
        results[source] = {
            "count": len(docs),
            "schema_valid": all(validate_schema(d) for d in docs),
            "unique_ids": len(set(d["source_id"] for d in docs)) == len(docs),
            "non_empty": all(len(d["content"].strip()) > 0 for d in docs),
        }
    return results
```

---

## 2. Cleaning Pipeline Evaluation

### 2.1 Pipeline Metrics

| Metric | Definition | Target Range | Red Flag |
|---|---|---|---|
| **Retention rate** | `clean_count / raw_count * 100` | 70–90% | <60% (over-filtering) or >95% (under-filtering) |
| **Language filter drop rate** | % dropped by language filter | 2–8% | >15% (filter too aggressive on Hinglish) |
| **Relevance filter drop rate** | % dropped by relevance filter | 5–15% | >25% (filter too strict) or <2% (filter too loose) |
| **Dedup rate** | % removed by deduplication | 3–10% | >20% (scraper has bug) or <1% (dedup not working) |
| **Length filter drop rate** | % dropped for being too short | 5–15% | >30% (many junk reviews in corpus) |

### 2.2 Language Detection Accuracy

**Eval set:** 100 manually labeled documents (25 English, 25 Hinglish, 25 Hindi, 25 Other)

| Metric | Target | Method |
|---|---|---|
| **English precision** | >95% | `correctly_labeled_english / total_labeled_english` |
| **English recall** | >95% | `correctly_labeled_english / total_actual_english` |
| **Hinglish precision** | >80% | Hinglish is inherently fuzzy; 80% is acceptable |
| **Hinglish recall** | >85% | Must not drop too many Hinglish reviews |
| **Hindi filter precision** | >90% | Should drop pure Hindi without false-positiving Hinglish |
| **False positive rate** | <5% | English/Hinglish incorrectly dropped |

### 2.3 Deduplication Accuracy

| Metric | Target | Method |
|---|---|---|
| **True positive rate** | >90% | Sample 50 removed docs — verify they ARE duplicates |
| **False positive rate** | <5% | Sample 50 removed docs — verify none are unique reviews |
| **Threshold calibration** | Jaccard=0.85 optimal | Test at 0.80, 0.85, 0.90 — check false positive rates |

### 2.4 Relevance Filter Accuracy

| Metric | Target | Method |
|---|---|---|
| **Precision** | >85% | Sample 100 kept docs — verify they ARE fashion/Myntra relevant |
| **Recall** | >90% | Sample 100 dropped docs — verify none are fashion-relevant |
| **Source-aware accuracy** | >95% for app stores | App store reviews should almost never be dropped |

---

## 3. LLM Classification Evaluation

### 3.1 Manual Quality Grading

**Protocol:** Randomly sample 100 classified documents. Two evaluators independently grade each.

#### Grading Rubric

| Grade | Criteria | Score |
|---|---|---|
| **A (Excellent)** | All tags correct, evidence quotes valid, confidence reasonable, no hallucination | 4 |
| **B (Good)** | Minor issues: 1 missing tag or 1 slightly off confidence score | 3 |
| **C (Acceptable)** | Significant issues: wrong tag present OR 2+ missing tags, but overall direction correct | 2 |
| **D (Poor)** | Major errors: multiple wrong tags, hallucinated evidence, wrong intent | 1 |
| **F (Fail)** | Completely wrong classification or invalid output | 0 |

#### Targets

| Metric | Target | Calculation |
|---|---|---|
| **Mean quality score** | ≥3.0 / 4.0 | Average of all 100 grades |
| **A+B rate** | ≥80% | % of docs graded A or B |
| **F rate** | <3% | % of docs graded F |
| **Inter-rater agreement** | Cohen's κ ≥ 0.7 | Agreement between two evaluators |

### 3.2 Per-Tag Precision & Recall

For each hesitation reason tag, measure against manual labels:

| Tag | Target Precision | Target Recall |
|---|---|---|
| `sizing_uncertainty` | >85% | >80% |
| `price_sensitivity` | >85% | >80% |
| `quality_doubt` | >80% | >75% |
| `waiting_for_sale` | >85% | >80% |
| `social_validation_needed` | >75% | >70% |
| `style_uncertainty` | >75% | >70% |
| `comparison_paralysis` | >75% | >70% |
| `trust_deficit` | >80% | >75% |
| `information_gap` | >75% | >70% |
| `occasion_mismatch` | >70% | >65% |
| `return_policy_concern` | >80% | >75% |

**Measurement:** Against a manually labeled eval set of 200 documents.

### 3.3 Wishlist Intent Accuracy

| Metric | Target | Method |
|---|---|---|
| **Intent classification accuracy** | >75% | Compare to manual labels on 100 docs |
| **"unknown" rate** | 20–40% | If <10%, model is guessing. If >60%, model isn't classifying. |
| **Bookmarking detection** | >70% precision | Key insight — must be reliable |

### 3.4 Evidence Quality

| Metric | Target | Method |
|---|---|---|
| **Quote substring match** | >90% | `evidence_quote in original_content` for all tags |
| **Quote relevance** | >85% | Manual check: does the quote actually support the tag? |
| **Non-empty quotes** | >95% | Percentage of tags with non-empty evidence_quote |

### 3.5 Confidence Calibration

| Metric | Target | Method |
|---|---|---|
| **Mean confidence** | 0.60–0.80 | Average across all tags |
| **Confidence-accuracy correlation** | Positive (r > 0.3) | Higher confidence tags should be more accurate |
| **Over-confidence rate** | <10% of docs at >0.95 | If many docs at 0.95+, model is poorly calibrated |
| **Under-confidence rate** | <5% of correct tags below 0.4 | Correct tags shouldn't be low-confidence |

### 3.6 Distribution Sanity

| Check | Expected | Red Flag |
|---|---|---|
| Top hesitation reason | 20–40% of docs | >60% (over-tagging one category) |
| Docs with 0 hesitation reasons | 30–50% | <10% (hallucinating reasons) |
| Docs with >4 reasons | <5% | >15% (over-tagging) |
| "unknown" wishlist intent | 20–40% | >60% (not classifying) |
| Primary signal docs | 50–70% | <30% (prompt too conservative) |

### 3.7 Hinglish-Specific Eval

| Metric | Target | Method |
|---|---|---|
| **Hinglish classification quality** | A+B ≥75% | Grade 50 Hinglish-only documents |
| **Hinglish evidence quote accuracy** | >80% | Substring match on Hinglish content |
| **Tag distribution parity** | Within 15% of English distribution | Hinglish shouldn't systematically differ unless real |

### 3.8 LLM Tier Comparison

When using multiple LLM tiers, compare quality:

| Comparison | Method | Acceptable Degradation |
|---|---|---|
| Gemini vs Groq (Llama 3.3) | Grade 50 docs from each | Groq quality ≥80% of Gemini quality |
| Gemini vs Ollama (Llama 3.1 8B) | Grade 50 docs from each | Ollama quality ≥60% of Gemini quality |
| Gemini vs Keyword tagger | Grade 50 docs from each | Keyword ≥40% of Gemini quality |

---

## 4. Quantification Evaluation

### 4.1 Internal Consistency

| Check | Method | Pass Criteria |
|---|---|---|
| **Summary totals match DB** | `summary.primary_signal_docs == SELECT COUNT(*) WHERE is_primary_signal=true` | Exact match |
| **Source distribution matches** | Compare `source_distribution` with `GROUP BY source` query | Within 1% |
| **Breakdown sums reasonable** | For single-tag fields: sum ≈ 100% | 95–105% |
| **Segment splits sum to breakdown** | `sum(segment_counts) ≤ breakdown_count * 1.1` | Within 10% (some "unknown" segment) |
| **Temporal trend sums match total** | `sum(monthly_counts) ≈ total_relevant_docs` | Within 5% |

### 4.2 Cross-Question Consistency

| Check | Method | Pass Criteria |
|---|---|---|
| **Docs mapped to ≥1 question** | `count(docs with question_mappings) / total_primary` | >80% of primary signal docs |
| **No question has 0 docs** | All q1–q10 have `total_relevant_docs > 0` | All > 0 |
| **Factor importance sums** | Q7 factor mention rates don't exceed 100% individually | Each factor ≤ 100% |

### 4.3 Statistical Validity

| Metric | Target | Method |
|---|---|---|
| **Confidence interval width** | <±5% for top tags | Bootstrap resampling (n=1000) |
| **Sample size adequacy** | N ≥ 30 per segment per question | Direct count |
| **Effect size** | Cohen's d > 0.3 for segment differences claimed | Standard effect size calculation |

---

## 5. Dashboard Evaluation

### 5.1 Performance (Lighthouse)

| Metric | Target | Measurement |
|---|---|---|
| **Performance score** | >90 | Lighthouse audit |
| **First Contentful Paint (FCP)** | <1.2s | Lighthouse |
| **Largest Contentful Paint (LCP)** | <2.0s | Lighthouse |
| **Total Blocking Time (TBT)** | <200ms | Lighthouse |
| **Cumulative Layout Shift (CLS)** | <0.1 | Lighthouse |
| **Bundle size (gzipped)** | <500KB | `next build` output |

### 5.2 Accessibility

| Metric | Target | Measurement |
|---|---|---|
| **Lighthouse accessibility** | >90 | Lighthouse audit |
| **Color contrast (WCAG AA)** | 4.5:1 minimum | axe-core or manual check |
| **Keyboard navigable** | All interactive elements reachable via Tab | Manual test |
| **Screen reader compatible** | Charts have `aria-label` descriptions | Manual test |
| **`prefers-reduced-motion` respected** | Animations disabled | Toggle OS setting, verify |

### 5.3 Functional Completeness

| Feature | Test | Pass Criteria |
|---|---|---|
| **All 10 question pages render** | Navigate to each | Charts visible, no console errors |
| **Segment toggle works** | Click Gen-Z, Millennial, Gen-X, All | Charts update with filtered data |
| **Chart hover tooltips** | Hover on each chart type | Tooltip shows label + count + pct |
| **Quote cards expand** | Click "Read more" | Full text visible |
| **Navigation works** | Click all nav items | Correct page loads |
| **Responsive layout** | Resize to 768px, 1024px, 1440px | Layout adapts correctly |
| **Loading states** | Throttle network in DevTools | Skeleton shimmer visible |
| **Error states** | Rename a JSON file to simulate missing data | Error message shown, no crash |
| **Chat UI functional** | Type query, submit | Response rendered (or "not configured" message) |

### 5.4 Visual Quality

| Criteria | Score (1-5) | Evaluator Notes |
|---|---|---|
| **First impression** | — | Does the dashboard look premium and professional? |
| **Color consistency** | — | Are colors harmonious? No clashing palettes? |
| **Typography** | — | Are fonts readable? Hierarchy clear? |
| **Animation quality** | — | Smooth? Not janky? Not excessive? |
| **Data density** | — | Is every pixel earning its place? No wasted space? |
| **Dark mode quality** | — | Comfortable to read? Good contrast? |

**Target: Average ≥4.0 / 5.0**

---

## 6. RAG Evaluation

### 6.1 Retrieval Quality

| Metric | Target | Method |
|---|---|---|
| **Recall@10** | >70% | For 20 test queries with known relevant docs: what % are in top-10 retrieved? |
| **Precision@10** | >50% | What % of top-10 retrieved docs are actually relevant? |
| **MRR (Mean Reciprocal Rank)** | >0.5 | Average of `1/rank_of_first_relevant_result` |
| **Segment filter accuracy** | >90% | When filtering by Gen-Z, are all retrieved docs from Gen-Z? |
| **Source filter accuracy** | >95% | When filtering by Reddit, are all retrieved docs from Reddit? |

### 6.2 Answer Quality

**Protocol:** 20 test queries, each graded by evaluator on 3 dimensions:

| Dimension | Score Range | Criteria |
|---|---|---|
| **Relevance** | 1–5 | Does the answer address the question? |
| **Accuracy** | 1–5 | Are the facts correct? Do they match quantified data? |
| **Citation quality** | 1–5 | Are citations present, relevant, and from real sources? |

#### Targets

| Metric | Target |
|---|---|
| **Mean relevance** | ≥4.0 / 5.0 |
| **Mean accuracy** | ≥3.5 / 5.0 |
| **Mean citation quality** | ≥3.5 / 5.0 |
| **Overall mean** | ≥3.7 / 5.0 |
| **No hallucination rate** | <10% of answers contain hallucinated facts |

### 6.3 Test Query Bank

| # | Query | Expected Answer Contains | Eval Focus |
|---|---|---|---|
| 1 | "What is the top hesitation reason?" | Sizing uncertainty, ~34% | Accuracy vs quantified data |
| 2 | "Why don't users buy from their wishlist?" | Multiple reasons with percentages | Comprehensive answer |
| 3 | "What do Gen-Z users care about most?" | Segment-specific insights | Segment filter |
| 4 | "How does Myntra compare to AJIO?" | Platform comparison criteria | Q5 data accuracy |
| 5 | "What external info do users seek?" | YouTube, Instagram, friends | Q6 data accuracy |
| 6 | "What are the main unmet needs?" | Size charts, styling tools, price alerts | Q10 data |
| 7 | "Is the wishlist used for bookmarking or buying?" | Intent distribution with % | Q8 data |
| 8 | "What role does pricing play in hesitation?" | Price sensitivity data with context | Factor analysis |
| 9 | "What are the top complaints on Trustpilot?" | Delivery, refunds, service | Systemic gaps data |
| 10 | "How has sizing uncertainty changed over time?" | Temporal trend | Time-series awareness |
| 11 | "Tell me about social validation" | Social validation mentions + examples | Niche tag retrieval |
| 12 | "What do Reddit users say vs Play Store users?" | Source comparison | Source awareness |
| 13 | "Are men and women equally hesitant about sizing?" | Gender-based analysis | Cross-segment |
| 14 | "What's the weather today?" | Polite refusal | Out-of-scope handling |
| 15 | "Show me everything you know" | Structured summary, not data dump | Boundary handling |
| 16 | "Myntra pe return kaise karte hain?" (Hinglish) | Return policy concerns | Hinglish query handling |
| 17 | "What percentage of reviews mention quality issues?" | Quality doubt %, with count | Quantitative accuracy |
| 18 | "Which age group uses wishlist as Pinterest?" | Bookmarking behavior by segment | Specific insight |
| 19 | "What should Myntra fix first?" | Top opportunity with evidence | Actionable recommendation |
| 20 | "Summarize the key findings in 3 bullet points" | Concise, accurate summary | Synthesis ability |

### 6.4 Response Time

| Metric | Target | Measurement |
|---|---|---|
| **P50 latency** | <3s | Median response time across 20 queries |
| **P95 latency** | <8s | 95th percentile |
| **P99 latency** | <15s | Max acceptable |

---

## 7. End-to-End System Evaluation

### 7.1 Pipeline Success Criteria

| Criterion | Target | Measured By |
|---|---|---|
| Total reviews analyzed | >50,000 | `corpus_meta.json → total_after_cleaning` |
| Classification accuracy | >80% A+B rate | Manual grading of 100 samples |
| Dashboard charts working | 38+ interactive charts | Visual verification |
| RAG answer quality | >3.5/5 average | Test query bank evaluation |
| Lighthouse performance | >90 | Lighthouse audit |
| Total LLM cost | $0 | API billing dashboard |
| Total calendar time | ≤13 days | Project timeline |
| Testable public URL | Working | Browser access |

### 7.2 Business Value Metrics

| Insight Quality Check | Method | Target |
|---|---|---|
| **Are the top 3 hesitation reasons actionable?** | Product team review | Team agrees insights are actionable |
| **Do segment differences reveal real patterns?** | Statistical significance test | At least 2 significant segment differences |
| **Are unmet needs genuinely unmet?** | Cross-reference with Myntra features | >50% of needs not addressed by current app |
| **Does the comparison data match market knowledge?** | Compare with published market data | Directionally consistent |

### 7.3 Reproducibility

| Check | Method | Target |
|---|---|---|
| **Pipeline determinism** | Run twice with same inputs | >95% identical classifications |
| **Cross-machine reproducibility** | Run on different machine | Same results (modulo scraping variations) |
| **Version pinning** | All dependencies pinned in requirements.txt | `pip freeze` matches requirements.txt |

---

## 8. Evaluation Schedule

| Phase | Eval Type | When | Who |
|---|---|---|---|
| Phase 1 | Scraper health + cleaning stats | After Phase 1 | Automated |
| Phase 2 | Classification quality (100 sample grading) | After Phase 2 | Manual |
| Phase 2 | Per-tag precision/recall (200 eval set) | After Phase 2 | Manual |
| Phase 3 | Consistency checks | After Phase 3 | Automated |
| Phase 4 | Lighthouse + visual quality | After Phase 4 | Automated + Manual |
| Phase 5 | RAG test query bank (20 queries) | After Phase 5 | Manual |
| Phase 6 | Full end-to-end eval | Before deployment | All |

---

## 9. Eval Data Artifacts

All evaluation results should be saved to `data/evals/`:

```
data/evals/
├── scraper_health.json           ← Automated scraper metrics
├── cleaning_stats.json           ← Pipeline retention rates
├── classification_grades.csv     ← Manual grading of 100 samples
├── per_tag_metrics.json          ← Precision/recall per tag
├── consistency_checks.json       ← Quantification consistency
├── lighthouse_report.json        ← Lighthouse audit results
├── rag_eval_results.csv          ← Test query bank results
└── final_scorecard.json          ← End-to-end summary
```

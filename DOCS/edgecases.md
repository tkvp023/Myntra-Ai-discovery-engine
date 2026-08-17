# Edge Cases
### AI Discovery Engine — Myntra
### Comprehensive Edge Case Catalog

---

> **Purpose:** This document catalogs every known edge case across the full pipeline — scraping, cleaning, classification, quantification, dashboard, and RAG. Each case includes the scenario, expected behavior, mitigation strategy, and severity.

---

## Severity Legend

| Level | Meaning |
|---|---|
| 🔴 **Critical** | System crash, data corruption, or fundamentally wrong output |
| 🟡 **Major** | Significant data loss or degraded quality, but system continues |
| 🟢 **Minor** | Cosmetic issue or negligible impact on final results |

---

## 1. Scraping Edge Cases

### 1.1 Rate Limiting & Blocking

| # | Edge Case | Severity | Expected Behavior | Mitigation |
|---|---|---|---|---|
| S-01 | Google Play API returns 429 (rate limit) | 🟡 Major | Pause, retry with exponential backoff | `tenacity` retry decorator: 2s → 4s → 8s → max 60s. Save checkpoint before pausing. |
| S-02 | Reddit PRAW returns 403 (auth failure) | 🔴 Critical | Stop Reddit scraper, continue others | Validate credentials at startup. Log clear error: "Check REDDIT_CLIENT_ID/SECRET in .env" |
| S-03 | YouTube quota exhausted (10K units/day) | 🟡 Major | Stop YouTube scraper gracefully | Track API units consumed. Save checkpoint with video IDs collected. Resume next day for comments. |
| S-04 | Trustpilot blocks IP (anti-bot) | 🟢 Minor | Skip blocked pages, continue | User-agent rotation, random delays (2-4s). If 3 consecutive 403s, stop gracefully. |
| S-05 | PissedConsumer/Reviews.io changes HTML structure | 🟡 Major | Scraper returns 0 reviews | Flexible CSS selectors with fallbacks. Log "0 reviews parsed" warning. Manual review needed. |
| S-06 | App Store RSS feed returns empty (Apple outage) | 🟢 Minor | 0 App Store reviews scraped | Retry 3x over 30 min. If still empty, mark as "unavailable" in checkpoint. |

### 1.2 Data Quality During Scraping

| # | Edge Case | Severity | Expected Behavior | Mitigation |
|---|---|---|---|---|
| S-07 | Review text is empty string `""` | 🟢 Minor | Skip document, don't add to corpus | Check `len(content.strip()) > 0` before creating `ScrapedDocument`. |
| S-08 | Review text is just emojis `"👍👍👍"` | 🟢 Minor | Keep — normalizer converts to text labels | `emoji.demojize()` converts to `:thumbs_up: :thumbs_up: :thumbs_up:`. Short, but may carry sentiment signal. |
| S-09 | Review has HTML entities (`&amp;`, `&lt;`) | 🟢 Minor | Normalizer strips HTML | `re.sub(r'<[^>]+>', '', text)` + `html.unescape()` in normalizer. |
| S-10 | Reddit post is a link post (no selftext) | 🟢 Minor | Use title only if selftext is empty | `full_content = title` when `selftext` is None or empty. |
| S-11 | Reddit comment is `[deleted]` or `[removed]` | 🟢 Minor | Skip — no useful signal | Check for these strings explicitly before creating doc. |
| S-12 | YouTube comment has HTML formatting (`<b>`, `<a>`) | 🟢 Minor | Strip HTML, keep plain text | Use `textFormat="plainText"` in API call. Normalizer strips any remaining tags. |
| S-13 | Play Store review has `None` timestamp | 🟢 Minor | Set timestamp to `None` in doc | Timestamp is optional in unified schema. Null is acceptable. |
| S-14 | Author username contains unicode/special chars | 🟢 Minor | Anonymize normalizes to hash | `anonymize_username()` uses SHA-256 hash — handles any character. |
| S-15 | Play Store returns duplicate `reviewId` across pages | 🟡 Major | Deduplicate during scraping | Track `existing_ids` set. Skip any `reviewId` already seen. |
| S-16 | Reddit API returns paginated results that loop | 🟡 Major | Infinite scraping loop | Track seen post IDs. Break if >80% of a page's posts are already seen. |

### 1.3 Network & Infrastructure

| # | Edge Case | Severity | Expected Behavior | Mitigation |
|---|---|---|---|---|
| S-17 | Network disconnects mid-scrape | 🟡 Major | Resume from last checkpoint | Checkpoint saved every N docs. `scraper.run()` catches exceptions, saves progress. |
| S-18 | Machine runs out of disk space | 🔴 Critical | Crash with clear error | Check available disk before starting. Warn if <1GB free. |
| S-19 | Scraper process killed by user (Ctrl+C) | 🟡 Major | Partial data saved | `try/finally` in `BaseScraper.run()` saves whatever docs exist. |
| S-20 | SSL certificate errors on secondary sources | 🟢 Minor | Skip source, continue others | `verify=True` in requests. If fails, log warning. Don't use `verify=False`. |

---

## 2. Cleaning Pipeline Edge Cases

### 2.1 Language Detection

| # | Edge Case | Severity | Expected Behavior | Mitigation |
|---|---|---|---|---|
| C-01 | Pure Devanagari Hindi review (no Latin chars) | 🟢 Minor | Filter out (we can't classify it reliably) | `devanagari_ratio > 0.5` → mark as "hindi" → drop. |
| C-02 | Hinglish with Devanagari mixed in (`"ye bahut अच्छा hai"`) | 🟡 Major | Keep if >50% Latin chars | Classify as "hinglish" if latin_ratio > 0.5 AND hinglish markers present. |
| C-03 | Tamil/Telugu/Kannada script reviews | 🟢 Minor | Filter out | Non-Latin, non-Devanagari → classified as "other" → dropped. |
| C-04 | Review in French/German (misclassified as English) | 🟢 Minor | `langdetect` catches it | Fall back to `langdetect.detect()` for ambiguous Latin-script texts. |
| C-05 | Very short text (`"bad"`, `"ok"`) | 🟢 Minor | Dropped by relevance filter | `MIN_WORD_COUNT = 4` — anything shorter is noise. |
| C-06 | Code-mixed English + Hindi + another language | 🟢 Minor | Keep if has Hinglish markers | The Hinglish marker word list catches common code-mixing patterns. |
| C-07 | `langdetect` library non-deterministic results | 🟢 Minor | Inconsistent language labels | `langdetect` can vary on short texts. Our Hinglish marker check runs first, more reliable. |
| C-08 | Review is entirely URLs or promotional links | 🟢 Minor | Normalizer strips URLs, relevance filter drops empty result | URLs removed → remaining text too short → dropped by length filter. |

### 2.2 Deduplication

| # | Edge Case | Severity | Expected Behavior | Mitigation |
|---|---|---|---|---|
| C-09 | Exact duplicate (same user, same review, different scrape time) | 🟢 Minor | Removed by exact hash dedup | SHA-256 on normalized lowercase text catches exact dupes. |
| C-10 | Near-duplicate (same content with minor typo fix) | 🟢 Minor | Removed by MinHash fuzzy dedup | Jaccard threshold 0.85 catches near-dupes. |
| C-11 | Same user posts same complaint on Reddit and Play Store | 🟡 Major | Both kept (cross-source dedup is risky) | We intentionally don't cross-source dedup — same user on different platforms = valid signal amplification. |
| C-12 | Very short reviews all hash similarly (`"good app"`, `"great app"`) | 🟡 Major | MinHash may false-positive merge different reviews | MinHash skips texts with <5 words (too few shingles for reliable similarity). |
| C-13 | Templated/spammed reviews (bot-generated) | 🟡 Major | Some caught by dedup, rest slip through | Exact hash catches identical spam. Remaining spam is low-signal → `is_primary_signal: false` in classification. |
| C-14 | Scraper re-run adds duplicates to raw/ | 🟢 Minor | Dedup removes them during cleaning | The cleaning pipeline always runs on the full raw corpus, catching any scraper-introduced dupes. |

### 2.3 Relevance Filtering

| # | Edge Case | Severity | Expected Behavior | Mitigation |
|---|---|---|---|---|
| C-15 | Play Store review about app crashes (not fashion-related) | 🟢 Minor | Kept — it's from the Myntra app | App store reviews are auto-relevant by source. These become `is_primary_signal: false` in classification. |
| C-16 | Reddit post mentions "myntra" in passing but is about cooking | 🟢 Minor | Kept (has keyword match) but classified as low-signal | Relevance filter is intentionally loose — classification stage handles nuance. |
| C-17 | YouTube comment is just `"🔥🔥🔥"` (3 emojis, no keywords) | 🟢 Minor | Dropped — no fashion keywords, <4 words after emoji conversion | Emoji → text conversion gives ~3 words. Below MIN_WORD_COUNT threshold. |
| C-18 | Review about Myntra's competitor with no Myntra mention | 🟢 Minor | Depends on source | If from Reddit/YouTube without any keywords → dropped. If from Myntra app stores → kept. |

---

## 3. LLM Classification Edge Cases

### 3.1 Input-Side

| # | Edge Case | Severity | Expected Behavior | Mitigation |
|---|---|---|---|---|
| L-01 | Review is in pure Hinglish, no English words | 🟡 Major | LLM must still classify correctly | Few-shot examples include Hinglish (Example 2 in `llm_prompts.md`). Gemini 3.7 Flash has strong Hinglish understanding. |
| L-02 | Review contains profanity/slang | 🟢 Minor | Classify normally — anger carries strong signal | Prompt explicitly says: "Anger often contains strong signal about hesitation reasons." |
| L-03 | Review is extremely long (1000+ words, Reddit essay) | 🟡 Major | May exceed per-doc token budget in batch | Long docs processed solo (not in batch). Or truncate to first 500 tokens with `[truncated]` note. |
| L-04 | Review mentions multiple products/brands | 🟢 Minor | Extract all relevant signals | Prompt says: "Review mentions multiple products → extract all signals — they represent general shopping behavior." |
| L-05 | Review is sarcastic (`"Oh yes, Myntra's sizing is PERFECT"`) | 🟡 Major | LLM may misclassify sentiment | Few-shot examples should include sarcasm case. Gemini 3.7 Flash handles sarcasm reasonably well. |
| L-06 | Review is a conversation fragment (Reddit reply to deleted parent) | 🟢 Minor | Missing context → classify what's visible | Classify standalone text as-is. `is_primary_signal: false` if too ambiguous. |
| L-07 | Review contains prices in ₹ (rupee symbol) | 🟢 Minor | LLM should parse correctly | Gemini handles ₹ natively. Few-shot examples include ₹ prices. |
| L-08 | Review has zero relevant signal (just "Nice app 5 stars") | 🟢 Minor | Return empty arrays, `is_primary_signal: false` | Prompt explicitly handles this: "If a review has NO relevant signal, use defaults." |

### 3.2 LLM Output-Side

| # | Edge Case | Severity | Expected Behavior | Mitigation |
|---|---|---|---|---|
| L-09 | LLM returns invalid JSON (broken syntax) | 🔴 Critical | Retry once. If still invalid, skip doc. | Use `response_mime_type="application/json"` + `response_schema` in Gemini for guaranteed valid JSON. |
| L-10 | LLM returns valid JSON but wrong schema (missing fields) | 🟡 Major | Pydantic validation catches it | `Classification` Pydantic model validates all required fields. Missing fields → default values. |
| L-11 | LLM hallucinate tags not in valid enum list | 🟡 Major | Validation drops invalid tags | Post-classification validator checks against `VALID_HESITATION_REASONS`, etc. Invalid values → dropped. |
| L-12 | LLM fabricates evidence_quote not in source text | 🟡 Major | Validation flags it | `evidence_must_be_substring: True` — quotes verified as substrings of original content. Non-matches logged. |
| L-13 | LLM returns confidence = 1.0 for everything | 🟡 Major | Suspiciously over-confident | Distribution check: if mean confidence > 0.90, flag for review. May need prompt adjustment. |
| L-14 | LLM assigns 6+ hesitation reasons to a single review | 🟢 Minor | Likely over-tagging | Cap at `max_hesitation_reasons: 6`. If consistently high, prompt may need "be selective" guidance. |
| L-15 | LLM returns completely empty classification (all null/empty) | 🟢 Minor | Accept — some reviews genuinely have no signal | Set `is_primary_signal: false`. Don't re-classify. |
| L-16 | LLM output exceeds max_output_tokens (truncated JSON) | 🔴 Critical | Invalid JSON → parse error | Increase `max_output_tokens`. Reduce batch size to 5 if tokens are tight. |

### 3.3 LLM Infrastructure

| # | Edge Case | Severity | Expected Behavior | Mitigation |
|---|---|---|---|---|
| L-17 | Gemini free tier quota exhausted | 🟡 Major | Auto-failover to Groq | Tiered failover: Gemini → Groq → Ollama → keyword tagger. |
| L-18 | Groq free tier also exhausted | 🟡 Major | Fall to Ollama (local) | Ollama runs unlimited on local machine. Quality drop (~10-15%) but functional. |
| L-19 | All LLM APIs down simultaneously | 🟡 Major | Keyword-based fallback tagger | Rule-based tagger uses regex/keyword matching for basic categorization. Lower quality but $0 and always available. |
| L-20 | Gemini returns 500 (server error) | 🟢 Minor | Retry 3x, then failover to Groq | `tenacity` retry decorator handles transient errors. |
| L-21 | Ollama model not downloaded yet | 🟢 Minor | Skip Ollama tier, fall to keyword tagger | Check `ollama list` at startup. Log warning: "Run `ollama pull llama3.1:8b` to enable local fallback." |
| L-22 | Google requires billing account for API (new policy) | 🔴 Critical | API calls fail with 403 | Link a billing account (no charges on free tier). Document this in env_setup_guide.md. |

---

## 4. Quantification Edge Cases

| # | Edge Case | Severity | Expected Behavior | Mitigation |
|---|---|---|---|---|
| Q-01 | A question has <50 relevant documents | 🟡 Major | Thin data → unreliable percentages | Show "Low confidence — insufficient data" warning in dashboard. Set minimum threshold of 30 docs. |
| Q-02 | One hesitation reason dominates (>60% of all tags) | 🟢 Minor | May indicate real signal OR over-tagging | Cross-reference with manual spot-check. If real → great insight. If over-tagging → fix prompt. |
| Q-03 | A segment (e.g., Gen-X) has very few documents | 🟡 Major | Segment splits unreliable for that group | Show "N=42" sample size in dashboard. Don't show segment if N < 20. |
| Q-04 | Temporal trend has gaps (no data for some months) | 🟢 Minor | Missing data points in timeline | Interpolate or show gaps explicitly. Don't fill with zeros (misleading). |
| Q-05 | Percentages don't sum to 100% (multi-tag docs) | 🟢 Minor | Expected for multi-label classification | Add tooltip: "Percentages exceed 100% because reviews can have multiple tags." |
| Q-06 | Summary totals don't match sum of q1-q10 | 🔴 Critical | Consistency error in export | Run `test_counts_match_total()` validation. Fix export logic if mismatch. |
| Q-07 | Zero documents classified for a specific tag | 🟢 Minor | Tag shows 0% in breakdown | Include it in the breakdown with count=0. Don't hide it. |
| Q-08 | All documents are `is_primary_signal: false` | 🔴 Critical | No data for any question | Indicates prompt is too conservative. Lower signal detection threshold. Re-classify. |

---

## 5. Dashboard Edge Cases

| # | Edge Case | Severity | Expected Behavior | Mitigation |
|---|---|---|---|---|
| D-01 | JSON data file not found (e.g., `q3.json` missing) | 🟡 Major | Page shows error state, not crash | `try/catch` on `fetch()`. Show "Data unavailable" error card with retry button. |
| D-02 | JSON file is empty `{}` or malformed | 🟡 Major | Charts render empty, no crash | Validate JSON at load time. Show empty state component. |
| D-03 | User toggles segment with 0 matching documents | 🟢 Minor | Charts show "No data" state | Check filtered data length. If 0, show empty state instead of broken chart. |
| D-04 | Word cloud has <3 words | 🟢 Minor | Word cloud looks sparse | Hide word cloud if <5 words. Show "Insufficient data for word cloud" message. |
| D-05 | Sankey diagram has no links | 🟢 Minor | Blank Sankey area | Hide Sankey if no links. Show table fallback. |
| D-06 | Heatmap row/column has all zeros | 🟢 Minor | Row/column appears blank | Keep it visible (zero is informative). Use consistent color scale. |
| D-07 | Browser doesn't support `backdrop-filter` (old Firefox) | 🟢 Minor | Glassmorphism degrades to opaque background | CSS fallback: `background: rgba(15,15,26,0.95)` for non-supporting browsers. |
| D-08 | User is on mobile with small screen | 🟢 Minor | Charts may be cramped | Single-column layout at <768px. Simplify complex charts (Sankey → table). |
| D-09 | Page takes >3s to load (large JSON files) | 🟢 Minor | User sees blank page | Add skeleton loading states. Lazy-load chart libraries. Code-split per page. |
| D-10 | `prefers-reduced-motion` is set | 🟢 Minor | Animations should be disabled | Check media query. Disable all chart animations and transitions. |

---

## 6. RAG & Chat Edge Cases

| # | Edge Case | Severity | Expected Behavior | Mitigation |
|---|---|---|---|---|
| R-01 | User asks question unrelated to Myntra ("What's the weather?") | 🟢 Minor | Polite refusal | System prompt: "I can only answer questions about Myntra user feedback." |
| R-02 | User sends empty query | 🟢 Minor | Show "Please enter a question" message | Frontend validation — don't send empty strings to API. |
| R-03 | User sends very long query (1000+ chars) | 🟢 Minor | Truncate to 500 chars, process | Frontend cap at 500 chars. Show remaining character count. |
| R-04 | Retrieved documents have 0 relevance to query | 🟡 Major | Answer says "I don't have enough information" | Set minimum similarity threshold (0.3). If all results below threshold, return "insufficient data" response. |
| R-05 | RAG API times out (>30s response) | 🟡 Major | Show timeout error to user | Set 30s timeout on API call. Show "Request timed out, please try again" message. |
| R-06 | Gemini API key not set in production | 🔴 Critical | RAG completely non-functional | Check API key at startup. Show "Chat feature unavailable — API key not configured" if missing. |
| R-07 | User asks in Hindi (Devanagari) | 🟢 Minor | Best-effort answer (may be lower quality) | Retrieval uses embeddings which handle Hindi. Answer quality may vary. |
| R-08 | User asks about a specific product/SKU | 🟢 Minor | No product-level data in corpus | Answer: "Our analysis covers aggregate patterns across categories. We don't have product-level data." |
| R-09 | User sends adversarial/prompt injection | 🟡 Major | System prompt should resist | Strong system prompt boundaries. Don't expose raw corpus data in responses. |
| R-10 | ChromaDB vector store not initialized | 🔴 Critical | RAG returns error | Check vector store at startup. Show "Search index not available" if missing. |
| R-11 | User rapidly sends 10+ queries (spam) | 🟢 Minor | API overloaded | Rate limit: max 10 queries/minute per session. Show "Please wait" message. |
| R-12 | LLM hallucinates information not in retrieved docs | 🟡 Major | Answer contains false claims | System prompt: "Base your answer ONLY on retrieved documents." Citation requirement forces grounding. |

---

## 7. End-to-End Edge Cases

| # | Edge Case | Severity | Expected Behavior | Mitigation |
|---|---|---|---|---|
| E-01 | Entire pipeline re-run produces different results | 🟢 Minor | Expected — LLMs are non-deterministic | Set temperature=0.1 for high consistency. Accept ~5% variation across runs. |
| E-02 | Scraping returns <10K total documents (all sources combined) | 🔴 Critical | Insufficient data for meaningful analysis | Expand search queries. Add more subreddits. Extend date range. Show "data collection insufficient" warning. |
| E-03 | Pipeline runs fine but dashboard shows no insights | 🔴 Critical | Classification didn't extract meaningful tags | Manual review of 20 random classifications. Likely prompt issue — needs calibration. |
| E-04 | Source distribution is extremely skewed (95% Play Store) | 🟡 Major | Analysis dominated by one source type | Show source-weighted results. Add source breakdown to every chart. Caveat in methodology notes. |
| E-05 | Pipeline takes >5 days to complete classification (free tier limits) | 🟢 Minor | Slow but expected | Use all 3 tiers simultaneously. Gemini for batch 1-1500, Groq for 1501-2500, etc. |
| E-06 | User runs pipeline on different OS (Linux/Mac) | 🟢 Minor | Path separators, encoding may differ | Use `pathlib.Path` everywhere (cross-platform). UTF-8 encoding explicit in all file operations. |

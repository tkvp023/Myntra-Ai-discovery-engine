# AI-Powered Discovery Engine — Working Spec
### Product chosen: Myntra
### Build tool: Antigravity

---

## 1. Original Brief (unchanged)

Build an AI-powered system that analyzes user feedback at scale to help answer:

- Why do users add fashion products to their wishlist?
- What prevents wishlisted products from eventually being purchased?
- What uncertainties remain after users have identified a product they like?
- What causes users to postpone a purchase?
- How do users compare multiple shortlisted products?
- What information do users seek outside Myntra/AJIO before purchasing?
- What role do fit, size, styling, price, reviews, occasion and social validation play?
- When do users use the wishlist as genuine purchase intent versus simply as a bookmarking mechanism?
- How do these behaviors differ across user segments?
- What unmet needs emerge consistently across user conversations?

**Constraint:** must go beyond summarizing reviews or sentiment analysis — must identify, quantify (where possible), and compare opportunity areas that could influence the business metric (Wishlist → Purchase conversion within 30 days).

---

## 2. Decisions Made So Far

### 2.1 Product
**Myntra** — chosen over AJIO and Nykaa Fashion based on:
- Largest review/discussion volume (best raw material for the discovery engine)
- Profitable, mature unit economics (₹548 Cr profit FY25)
- Cleanest, least-diluted signal (AJIO's data is noisier/mixed with Reliance; Nykaa's fashion vertical data is diluted by beauty-dominant discussions and is itself a known loss center)

### 2.2 Data Sources — Shortlisted

**Primary sources** (used to directly answer the 10 discovery questions — wishlist-to-purchase hesitation):
| Source | Access method | Notes |
|---|---|---|
| Play Store reviews | `google-play-scraper` (unofficial, no auth) | Highest volume, best starting point |
| App Store reviews | Apple RSS feed / scraping | Lower volume for India, still useful supplement |
| Reddit | Official API (PRAW) | High signal depth — r/IndianFashionAddicts, r/india, r/twoxindia etc. |
| YouTube comments | YouTube Data API | Pull comments from Myntra haul/review-style videos |

**Secondary sources** (used to understand overall systemic gaps — trust, service, returns friction — that may indirectly explain wishlist hesitation, not the primary evidence base):
| Source | Notes |
|---|---|
| Trustpilot | Skews toward complaint-driven reviews (delivery, refunds, service) |
| PissedConsumer | Same complaint-skew, even more extreme |
| Reviews.io | Thin Myntra presence, low volume, similar skew |

**Explicitly excluded / deprioritized:**
- On-site Myntra product reviews (Q&A) — excluded from primary set because reviews only exist for *purchased* products, so they structurally can't explain why wishlisted-but-unpurchased items stayed unpurchased (survivorship bias). May be referenced only as an indirect proxy signal (e.g., poor fit/quality reviews in a category correlating with low wishlist conversion in that category).
- Dedicated fashion/shopping forums — mostly inactive; discussion has migrated to Reddit/Instagram.
- Twitter/X — API access friction (paid/restricted), deprioritized versus better ROI sources.

### 2.3 Engine Format
**Hybrid: Structured dashboard + lightweight query layer**, deployed as a single testable link (satisfies the "link where the workflow can be tested" deliverable requirement).

- **Core layer (primary deliverable):**
  - One-time batch pipeline: scrape all primary + secondary sources → clean/dedupe → run LLM classification pass → organize output into dashboard sections mapped 1:1 to the 10 brief questions.
  - Each section must show **quantified breakdowns** (e.g., "34% of hesitation mentions cite sizing uncertainty," "22% cite price-drop waiting behavior") — not just a text summary. This satisfies the "beyond summarizing/sentiment analysis" requirement by identifying, quantifying, and comparing opportunity areas.
  - Secondary-source data (Trustpilot/PissedConsumer/Reviews.io) feeds a separate "systemic gaps" section — used for broader context on what Myntra is lacking overall (service/trust/logistics issues), not treated as primary evidence for wishlist hesitation specifically.

- **Optional top layer (added interactivity, not re-scraping):**
  - A simple chat/query box that runs retrieval (RAG-style) over the already-processed corpus — e.g., "What do Gen-Z users say about styling uncertainty?" — without needing to re-scrape live data.
  - Justification: sources don't change fast enough to require real-time freshness; this keeps the build simple while still making the deliverable feel interactive and "AI-powered" for testing purposes.

### 2.4 Build Stack
- **Antigravity** (Google's agentic coding/IDE tool) chosen as the build environment — suited for a coding-heavy pipeline (scraping + LLM classification + dashboard), more control than no-code tools like n8n/Zapier for this use case.
- Known constraints to plan around:
  - Reddit & YouTube have official, clean APIs — straightforward to wire up.
  - Play Store has no official bulk review API — relies on unofficial scraper libraries (acceptable for this academic/fellowship context, but semi-fragile/technically against ToS at scale).
  - App Store review access is also non-official (RSS feed / scraping), and India-specific volume is typically low.
  - Deliverable must be an actual deployed, testable artifact (not just a script) — plan for a lightweight hosted dashboard/app (e.g., Flask/Next.js on Vercel/Render or similar).

---

## 3. Open / Next Steps
- [ ] Design the LLM classification schema (tags/categories to extract per review — e.g., hesitation reason, fit/size mention, price sensitivity, social validation, segment inference, etc.)
- [ ] Define how quantification will work (tagging + frequency counts, confidence thresholds, etc.)
- [ ] Decide final tech stack for hosting/deployment
- [ ] Build scraping scripts per source
- [ ] Build dashboard UI mapped to the 10 questions
- [ ] Wire up the RAG query layer on top of the processed corpus
- [ ] Deploy and test the public link
- [ ] Move to Part 2: Business Metric Decomposition (Wishlist → Purchase), to be used alongside discovery engine findings to identify highest-potential opportunity areas

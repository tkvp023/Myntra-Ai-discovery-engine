# Task Board
### AI Discovery Engine — Myntra

---

> **Legend:** `[ ]` = Not started | `[/]` = In progress | `[x]` = Complete

---

## Phase 1: Foundation & Scraping (Days 1–3)

### 1.1 Environment Setup
- [ ] Create project directory structure (as defined in `architecture.md`)
- [ ] Set up Python virtual environment + install dependencies
- [ ] Initialize Next.js dashboard project
- [ ] Register all API keys (Gemini, Groq, Reddit, YouTube)
- [ ] Create `.env` file with all credentials
- [ ] Run verification checklist from `env_setup_guide.md`
- [ ] Initialize Git repo + `.gitignore`

### 1.2 Database Setup
- [ ] Create SQLAlchemy models matching schema in `architecture.md`
- [ ] Create `connection.py` with SQLite connection
- [ ] Run `Base.metadata.create_all()` to initialize tables
- [ ] Test: insert a dummy document and query it back

### 1.3 Scraper Framework
- [ ] Build `BaseScraper` abstract class (common interface)
- [ ] Implement unified document schema (dataclass/Pydantic model)
- [ ] Build checkpoint/resume system (JSON checkpoint files)
- [ ] Build retry + exponential backoff utility

### 1.4 Individual Scrapers
- [ ] **Play Store scraper** — test with 100 reviews, then run full 50K
- [ ] **App Store scraper** — RSS feed parser + scraping fallback
- [ ] **Reddit scraper** — PRAW setup, all subreddits + queries from `scraper_config.md`
- [ ] **YouTube scraper** — video search → comment extraction pipeline
- [ ] **Trustpilot scraper** — Playwright-based, with anti-bot mitigation
- [ ] **PissedConsumer scraper** — BeautifulSoup parser
- [ ] **Reviews.io scraper** — BeautifulSoup parser

### 1.5 Scraper Orchestrator
- [ ] Build `orchestrator.py` — runs all scrapers with parallel execution
- [ ] Implement error handling (partial success mode)
- [ ] Test full pipeline run (all 7 scrapers)
- [ ] Verify output in `data/raw/` — spot-check 50 random docs per source

### 1.6 Cleaning Pipeline
- [ ] Language filter (English + Hinglish; drop non-Latin)
- [ ] Text normalizer (lowercase, URL strip, unicode normalize, emoji-as-text)
- [ ] Deduplicator (exact hash + MinHash, Jaccard > 0.85)
- [ ] Relevance filter (must contain fashion/Myntra signals)
- [ ] Length filter (drop < 10 words)
- [ ] Run full cleaning pipeline on scraped data
- [ ] Verify: check dedup rate, language filter rate, output quality

**Phase 1 Exit Criteria:**
- All 7 scrapers produce output in `data/raw/`
- Cleaning pipeline produces `data/clean/` with dedup + filtered corpus
- All documents in unified schema
- Checkpoint files exist for all scrapers

---

## Phase 2: LLM Classification (Days 4–6)

### 2.1 Classification Framework
- [ ] Build `schema.py` — Pydantic models for classification output
- [ ] Build `prompts.py` — system prompt + few-shot examples from `llm_prompts.md`
- [ ] Build Gemini API client with JSON-mode response
- [ ] Build Groq API client with JSON-mode response
- [ ] Build Ollama client (local fallback)
- [ ] Implement tiered failover logic (Gemini → Groq → Ollama)

### 2.2 Batch Processor
- [ ] Build `batch_processor.py` — chunked batch classification
- [ ] Implement batching (10 docs per API call)
- [ ] Implement rate limiting (10 RPM for Gemini, 25 RPM for Groq)
- [ ] Implement checkpoint/resume (save after each batch)
- [ ] Implement caching (hash each doc, skip re-classification)

### 2.3 Validation Pipeline
- [ ] Implement post-classification validation (from `llm_prompts.md` Section 5)
- [ ] Confidence threshold filtering (drop < 0.4)
- [ ] Enum validation (check all tags are valid values)
- [ ] Evidence quote substring check
- [ ] Log validation failures for review

### 2.4 Run Classification
- [ ] Run small test batch (50 docs) — manually review output quality
- [ ] Calibrate prompts if needed (adjust few-shot examples)
- [ ] Run full corpus classification (~50K+ docs)
- [ ] Monitor: track API calls, tokens used, errors, failover events
- [ ] Store results in `classifications` + tag tables in SQLite

### 2.5 Quality Check
- [ ] Sample 100 random classified docs — manually verify accuracy
- [ ] Check for systematic errors (always tagging "unknown", hallucinated quotes, etc.)
- [ ] Verify Hinglish docs are classified correctly
- [ ] Calculate per-tag confidence distribution
- [ ] Adjust prompts + re-classify if quality is below threshold

**Phase 2 Exit Criteria:**
- All clean corpus documents classified and stored in DB
- Manual spot-check shows >80% accuracy on sampled classifications
- Validation failure rate < 5%
- All API costs = $0

---

## Phase 3: Quantification + Data Export (Days 7–8)

### 3.1 Aggregation Engine
- [ ] Build `aggregator.py` — SQL queries for tag frequency counts
- [ ] Implement cross-tabulation (hesitation × segment, factor × source)
- [ ] Implement confidence-weighted counts
- [ ] Implement source-weighted roll-up (primary 1.0, secondary 0.5)
- [ ] Implement temporal trends (group by month)

### 3.2 Question Mapper
- [ ] Build `question_mapper.py` — maps aggregates to 10 questions
- [ ] Generate breakdown arrays for each question
- [ ] Generate segment splits for each question
- [ ] Generate source attribution for each question
- [ ] Extract top quotes per question (sorted by confidence)

### 3.3 JSON Export
- [ ] Build `export.py` — generates all JSON files per `data_contracts.md`
- [ ] Export `summary.json`
- [ ] Export `q1.json` through `q10.json` (with question-specific extras)
- [ ] Export `systemic_gaps.json`
- [ ] Export `corpus_meta.json`
- [ ] Copy all JSON to `dashboard/public/data/`
- [ ] Validate all JSON against TypeScript interfaces from data contracts

**Phase 3 Exit Criteria:**
- All 14 JSON files generated and valid
- Numbers are internally consistent (totals add up, pcts sum to ~100%)
- JSON passes schema validation

---

## Phase 4: Dashboard Build (Days 8–11)

### 4.1 Design System
- [ ] Create `globals.css` with all design tokens from `dashboard_ui_spec.md`
- [ ] Set up Google Fonts (Inter + Outfit)
- [ ] Create glassmorphism card component (`ChartWrapper.js`)
- [ ] Create loading skeleton component
- [ ] Create error state component

### 4.2 Layout & Navigation
- [ ] Build fixed top navbar with glassmorphism
- [ ] Build nav items with active state (pink underline + glow)
- [ ] Build responsive layout (breakpoints from UI spec)
- [ ] Build page transition animations (fade-in + slide-up)
- [ ] Build sidebar nav for mobile

### 4.3 Chart Components (reusable)
- [ ] `StatCard.js` — KPI card with sparkline + counter animation
- [ ] `HorizontalBar.js` — gradient bars with confidence badges
- [ ] `StackedBar.js` — stacked bar with legend
- [ ] `GroupedBar.js` — grouped bar for segment comparisons
- [ ] `DonutChart.js` — animated donut/pie chart
- [ ] `RadarChart.js` — spider/radar for factor importance
- [ ] `AreaTimeline.js` — area chart for temporal trends
- [ ] `TreemapChart.js` — treemap for hierarchical data
- [ ] `HeatmapChart.js` — Nivo heatmap wrapper
- [ ] `SankeyDiagram.js` — Nivo Sankey for flow visualization
- [ ] `ScatterPlot.js` — scatter for correlation analysis
- [ ] `WordCloud.js` — word cloud wrapper

### 4.4 UI Components
- [ ] `ConfidenceBadge.js` — circular confidence indicator
- [ ] `SourceBadge.js` — colored pill showing data source
- [ ] `QuoteCard.js` — expandable quote with metadata
- [ ] `QuoteCarousel.js` — scrollable quote carousel
- [ ] `SegmentToggle.js` — Gen-Z / Millennial / Gen-X toggle
- [ ] `FilterBar.js` — source + segment + date filters

### 4.5 Pages
- [ ] **Summary page** (`page.js`) — stat cards + source distribution + top opportunities
- [ ] **Question pages** (`questions/[id]/page.js`) — dynamic, loads q{id}.json
- [ ] **Systemic Gaps page** (`systemic-gaps/page.js`)
- [ ] **Ask the Data page** (`ask/page.js`) — chat interface (UI only, wire RAG later)

### 4.6 Data Integration
- [ ] Build `lib/api.js` — data fetching from static JSON files
- [ ] Build `lib/constants.js` — 10 questions text, color tokens
- [ ] Wire all charts to real data from JSON
- [ ] Verify: all 38+ charts render with real data
- [ ] Segment toggle actually filters chart data

**Phase 4 Exit Criteria:**
- All pages render with real data
- All 38+ charts are interactive (hover, tooltips, filters)
- Responsive across desktop/tablet breakpoints
- No console errors
- Visual quality matches mockup aesthetic

---

## Phase 5: RAG & Chat (Days 11–12)

### 5.1 Embedding Pipeline
- [ ] Build `embedder.py` — embed clean corpus using Gemini/sentence-transformers
- [ ] Build `indexer.py` — store embeddings in ChromaDB
- [ ] Run full embedding pipeline on clean corpus
- [ ] Verify: test similarity search with sample queries

### 5.2 Query Engine
- [ ] Build `query_engine.py` — retrieval + answer generation
- [ ] Implement top-k retrieval (k=10) with metadata filtering
- [ ] Implement answer generation using Gemini Flash (free tier)
- [ ] Implement citation extraction + formatting
- [ ] Test with 10 diverse queries — verify answer quality

### 5.3 RAG API
- [ ] Build `/api/ask` endpoint (Next.js API route or Flask)
- [ ] Accept query + filters (segment, source, question)
- [ ] Return structured answer with citations
- [ ] Implement error handling + rate limiting

### 5.4 Wire Chat UI
- [ ] Connect ChatInterface to RAG API
- [ ] Implement suggested queries (pre-populated chips)
- [ ] Implement filter dropdowns (segment, source)
- [ ] Implement loading state (typing indicator)
- [ ] Test end-to-end: type query → see answer with citations

**Phase 5 Exit Criteria:**
- Chat interface returns accurate, cited answers
- Filters (segment, source) correctly narrow retrieval
- Response time < 5 seconds
- No hallucinated information

---

## Phase 6: Polish & Deploy (Days 12–13)

### 6.1 Polish
- [ ] Review all pages for visual consistency
- [ ] Verify all animations work (entrance, hover, filter transitions)
- [ ] Test loading states (skeleton shimmer)
- [ ] Test empty states (for any questions with thin data)
- [ ] Test error states (simulate API failure)
- [ ] Verify accessibility (keyboard nav, focus indicators, color contrast)
- [ ] Performance audit (Lighthouse score > 90)

### 6.2 Deployment
- [ ] Configure Vercel project
- [ ] Set environment variables in Vercel dashboard
- [ ] Deploy dashboard (`vercel deploy`)
- [ ] Verify all pages work on deployed URL
- [ ] Verify RAG chat works on deployed URL
- [ ] Test on different browsers (Chrome, Firefox, Safari)

### 6.3 Documentation
- [ ] Update README.md with project overview + setup instructions
- [ ] Create walkthrough artifact summarizing what was built
- [ ] Screenshot key dashboard views for documentation

### 6.4 Handoff
- [ ] Share testable link
- [ ] Document any known limitations or data gaps
- [ ] Note areas for future improvement

**Phase 6 Exit Criteria:**
- Dashboard live on public URL
- All features working end-to-end
- README complete
- Testable link shared

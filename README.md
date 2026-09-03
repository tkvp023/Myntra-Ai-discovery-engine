# 🔍 AI Discovery Engine — Myntra Wishlist Insights

> **Quantified analysis of 87,000+ user reviews revealing why shoppers add to wishlist but hesitate to buy on Myntra.**

A full-stack consumer insights platform that ingests, classifies, quantifies, and visualizes public user feedback from multiple sources — powered by LLMs and presented through a premium dark-mode analytics dashboard.

---

## 🎯 Problem Statement

Myntra users add millions of products to their wishlist but hesitate to purchase. This project answers **10 strategic discovery questions** about that hesitation gap:

| # | Question |
|---|---|
| Q1 | Why do users add fashion products to their wishlist? |
| Q2 | What prevents wishlist items from being purchased? |
| Q3 | What uncertainties remain after finding a liked product? |
| Q4 | What causes users to postpone a purchase? |
| Q5 | How do users compare products across platforms? |
| Q6 | What information do users seek outside Myntra? |
| Q7 | What factors influence the purchase decision most? |
| Q8 | When is the wishlist genuine intent vs bookmarking? |
| Q9 | How do behaviors differ across Gen-Z, Millennial, Gen-X? |
| Q10 | What unmet needs emerge consistently? |

Plus a **Systemic Gaps** analysis from secondary sources (Trustpilot, PissedConsumer, Reviews.io) and an **interactive "Ask the Data" chat interface**.

---

## ✨ Dashboard Features

- **38+ interactive visualizations** — Horizontal bars, grouped/stacked bars, donut charts, radar, Sankey, heatmaps, treemaps, word clouds, scatter plots, area timelines
- **Premium dark-mode glassmorphism** — Custom design system with Inter + Outfit fonts, CSS glass effects, gradient accents
- **Segment toggle** — Filter all charts by Gen-Z, Millennial, or Gen-X in real time
- **Entrance animations** — IntersectionObserver-driven staggered chart animations
- **Responsive design** — Desktop, tablet, and mobile with hamburger navigation
- **Ask the Data** — Interactive chat with topic-aware demo responses, citation badges, and filter dropdowns
- **Loading skeletons** — Shimmer animations during route transitions
- **Error boundaries** — Glassmorphic error pages with retry and navigation

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Pipeline (Python)                   │
│  Scrapers → Cleaning → LLM Classification → Quantification │
│              (5 sources)    (Gemini/Groq)      (Export JSON) │
└──────────────────────────┬──────────────────────────────────┘
                           │ JSON files
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Dashboard (Next.js 16)                     │
│  Summary → 10 Question Pages → Systemic Gaps → Ask the Data │
│  (StatCards, Charts, Filters, Animations, Glassmorphism)    │
└─────────────────────────────────────────────────────────────┘
```

### Data Sources (5 platforms)

| Source | Type | Volume (Raw) | Classified in DB |
|---|---|---|---|
| YouTube (haul/try-on/review comments) | Primary | 17,470 comments | 5,319 docs |
| Google Play Store (`com.myntra.android`) | Primary | 2,600 reviews | 1,180 docs |
| Reddit (`r/IndianFashionAddicts`, `r/MyntraSucks`, etc.) | Primary | 1,234 posts/threads | 1,039 docs |
| PissedConsumer (dispute & complaint forum) | Secondary | 511 complaints | 507 docs |
| Apple App Store (iTunes RSS) | Primary | 250 reviews | 137 docs |
| **Total** | | **22,065 raw** | **8,182 classified** |

> *Note: Scrapers for Trustpilot and Reviews.io were developed and tested, but yielded 0 records due to Cloudflare anti-bot blocks and negligible presence for Myntra India. The corpus is solidly grounded in the 5 high-yield platforms above.*

### Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, TypeScript |
| Charts | Recharts, Nivo (Sankey) |
| Styling | Vanilla CSS (glassmorphism design system) |
| Pipeline | Python 3.14, SQLAlchemy, SQLite |
| LLMs | Gemini Flash (free), Groq Llama 3.3 (free) |
| Embedding | sentence-transformers (local, free) |
| Vector Store | ChromaDB (local) |
| Deployment | Vercel (static + serverless) |

---

## 🚀 Quickstart

### Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.10 (for pipeline only)

### Run the Dashboard

```bash
cd dashboard
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) — the dashboard runs with mock data out of the box.

### Production Build

```bash
cd dashboard
npm run build    # or: node node_modules/next/dist/bin/next build
```

### Deploy to Vercel

```bash
cd dashboard
vercel deploy --prod
```

---

## 📁 Project Structure

```
ai-discovery-engine/
├── DOCS/                              # Specifications & documentation
│   ├── architecture.md                # System architecture & data flow
│   ├── dashboard_ui_spec.md           # UI component specifications
│   ├── data_contracts.md              # JSON schema contracts
│   ├── phase_wise_implementation_plan.md
│   ├── llm_prompts.md                 # Classification prompt templates
│   └── ...
│
├── pipeline/                          # Python data pipeline
│   ├── scrapers/                      # Platform scrapers (5 active data sources)
│   ├── cleaning/                      # Dedup, normalization
│   ├── classification/                # LLM-powered tagging
│   ├── quantification/                # Aggregation & JSON export
│   ├── db/                            # SQLAlchemy models
│   └── run_pipeline.py                # Orchestrator
│
├── dashboard/                         # Next.js frontend
│   ├── app/
│   │   ├── page.tsx                   # Summary dashboard
│   │   ├── questions/[id]/page.tsx    # 10 question detail pages
│   │   ├── gaps/page.tsx              # Systemic gaps analysis
│   │   ├── ask/page.tsx               # Ask the Data chat
│   │   ├── loading.tsx                # Loading skeletons
│   │   ├── error.tsx                  # Error boundary
│   │   ├── not-found.tsx              # Custom 404
│   │   └── globals.css                # Full design system
│   ├── components/                    # 22 reusable components
│   │   ├── StatCard.tsx               # KPI with sparkline
│   │   ├── HorizontalBar.tsx          # Animated horizontal bars
│   │   ├── DonutChart.tsx             # Animated donut chart
│   │   ├── GroupedBar.tsx             # Segment comparison bars
│   │   ├── StackedBar.tsx             # Stacked bar chart
│   │   ├── RadarChartComponent.tsx    # Spider/radar chart
│   │   ├── SankeyDiagram.tsx          # Flow visualization
│   │   ├── HeatmapChart.tsx           # Cross-comparison heatmap
│   │   ├── TreemapChart.tsx           # Hierarchical treemap
│   │   ├── ScatterPlot.tsx            # Scatter/bubble chart
│   │   ├── WordCloudChart.tsx         # CSS word cloud
│   │   ├── AreaTimeline.tsx           # Temporal trend chart
│   │   ├── QuoteCarousel.tsx          # Quote display + navigation
│   │   ├── Skeleton.tsx               # Loading skeletons
│   │   ├── Navbar.tsx                 # Glassmorphism nav
│   │   └── ...
│   ├── lib/
│   │   ├── api.ts                     # Data loading (fs + mock fallback)
│   │   ├── mockData.ts                # Development mock data
│   │   └── constants.ts               # Colors, labels, metadata
│   └── public/data/                   # Pipeline-exported JSON files
│
└── data/                              # SQLite DB + pipeline outputs
```

---

## 📊 Data Contracts

The pipeline exports JSON files consumed by the dashboard:

| File | Contents |
|---|---|
| `summary.json` | KPI cards, source distribution, top opportunities |
| `q1.json` – `q10.json` | Per-question breakdowns, segment splits, quotes, temporal trends |
| `systemic_gaps.json` | Secondary-source issue analysis, correlations |
| `corpus_meta.json` | Corpus-level metadata |

See [data_contracts.md](DOCS/data_contracts.md) for full schemas.

---

## 🎨 Design System

The dashboard uses a custom dark-mode glassmorphism design system:

- **Colors:** Pink (#ff3f6c), Orange (#ff7849), Purple (#a855f7), Teal (#2dd4bf), Blue (#3b82f6), Yellow (#fbbf24)
- **Fonts:** Inter (body), Outfit (numbers/headings)
- **Glass:** `rgba(255,255,255,0.04)` background + `blur(20px)` backdrop
- **Animations:** fadeSlideUp entrance, shimmer loading, counter animation, chart draw

See [dashboard_ui_spec.md](DOCS/dashboard_ui_spec.md) for full specifications.

---

## 📄 Documentation

| Document | Purpose |
|---|---|
| [architecture.md](DOCS/architecture.md) | System architecture, data flow, deployment |
| [dashboard_ui_spec.md](DOCS/dashboard_ui_spec.md) | UI component specs, design tokens |
| [data_contracts.md](DOCS/data_contracts.md) | JSON schemas (pipeline ↔ dashboard) |
| [phase_wise_implementation_plan.md](DOCS/phase_wise_implementation_plan.md) | 13-day build roadmap |
| [llm_prompts.md](DOCS/llm_prompts.md) | Classification prompt templates |
| [testing_plan.md](DOCS/testing_plan.md) | Test strategy & acceptance criteria |
| [deployment_runbook.md](DOCS/deployment_runbook.md) | Deploy procedures |

---

## 💰 Cost

**$0 total.** The entire stack uses free-tier services:
- Gemini Flash (free via AI Studio)
- Groq Llama 3.3 (free tier)
- sentence-transformers (local)
- ChromaDB (local)
- Vercel (free tier for deployment)

---

## 📜 License

This project is built as an academic/research deliverable for the AI Discovery Engine initiative.

# Quick Start Guide

Build your own AI Discovery Engine in 5 minutes. No coding required — just context.

## Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **API Keys** (all free tier):
  - [Google Gemini API](https://aistudio.google.com/apikey) (classification)
  - [Groq API](https://console.groq.com/) (fallback LLM)
  - [YouTube Data API](https://console.cloud.google.com/) (if using YouTube source)
  - [Apify](https://apify.com/) or Reddit API credentials (if using Reddit source)

## Step 1: Configure Your Domain

Edit `discovery_config.yaml` — this is the **only file you need to change**.

```yaml
project:
  name: "My Product Discovery Engine"
  slug: "myproduct"
  description: "Analyzing user friction for MyProduct"

domain:
  brand_name: "MyProduct"
  industry: "E-Commerce"
  competitors: ["CompetitorA", "CompetitorB"]

# ... configure sources, questions, classification schema
```

See [CONFIG_REFERENCE.md](CONFIG_REFERENCE.md) for the full reference.

## Step 2: Generate Your Engine

```bash
# Install PyYAML (needed for the generator)
pip install pyyaml

# Validate your config first
python setup_engine.py --validate

# Generate all domain-specific code
python setup_engine.py
```

This creates/updates:
- `pipeline/scrapers/config.py` — scraper configurations
- `pipeline/classification/prompts.py` — LLM system prompt
- `pipeline/classification/schema.py` — classification schema
- `pipeline/classification/keyword_tagger.py` — keyword patterns
- `pipeline/cleaning/relevance_filter.py` — relevance keywords
- `pipeline/quantification/question_mapper.py` — question mappings
- `dashboard/lib/constants.ts` — dashboard metadata
- `dashboard/lib/mockData.ts` — development mock data
- `dashboard/app/layout.tsx` — dashboard branding
- `.env.example` — environment template
- `README.md` — project documentation

## Step 3: Set Up Environment

```bash
# Copy and fill in your API keys
cp .env.example .env

# Install Python dependencies
pip install -r requirements.txt

# Install dashboard dependencies
cd dashboard
npm install
cd ..
```

## Step 4: Run the Pipeline

```bash
cd pipeline

# Test with a small batch first
python run_pipeline.py --mode full --limit 50

# Or run each step individually:
python run_pipeline.py --mode init-db       # Create database
python run_pipeline.py --mode scrape --limit 100   # Scrape data
python run_pipeline.py --mode clean          # Clean & filter
python run_pipeline.py --mode classify       # LLM classification
python run_pipeline.py --mode export         # Generate dashboard JSON
```

## Step 5: Launch the Dashboard

```bash
cd dashboard
npm run dev
# Open http://localhost:3000
```

## Step 6: Ask Questions (RAG)

```bash
cd pipeline
python run_pipeline.py --mode embed         # Build vector index
python run_pipeline.py --mode rag-server    # Start RAG API on :8000
```

Then visit the "Ask" page on the dashboard to query your corpus.

---

## Pipeline Modes Reference

| Mode | What it does |
|------|-------------|
| `init-db` | Create SQLite database tables |
| `scrape` | Scrape data from configured sources |
| `clean` | Normalize → language filter → relevance filter → deduplicate |
| `insert-db` | Insert clean documents into database |
| `classify` | Run LLM classification (Gemini → Groq → Ollama → Keywords) |
| `classify-stats` | Show classification progress |
| `export` | Generate JSON files for the dashboard |
| `embed` | Build vector index for RAG |
| `rag-server` | Start FastAPI RAG server |
| `full` | Run everything: scrape → clean → classify → export |
| `stats` | Show data statistics |

## Useful Options

```bash
# Scrape specific sources only
python run_pipeline.py --mode scrape --sources playstore,reddit

# Use a specific LLM tier
python run_pipeline.py --mode classify --tier gemini

# Adjust batch size and rate limit
python run_pipeline.py --mode classify --batch-size 5 --rpm 5

# Export to custom directory
python run_pipeline.py --mode export --output-dir ./custom_output
```

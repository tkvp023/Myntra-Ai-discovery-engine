# Environment Setup Guide
### AI Discovery Engine — Myntra

---

## Prerequisites

| Tool | Version | Check Command |
|---|---|---|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Git | 2.30+ | `git --version` |
| pip | 22+ | `pip --version` |

---

## 1. Clone & Project Structure

```bash
# Navigate to project root
cd "AI discovery engine(GP)"

# Create the full directory structure
mkdir -p pipeline/scrapers
mkdir -p pipeline/cleaning
mkdir -p pipeline/classification
mkdir -p pipeline/quantification
mkdir -p pipeline/rag
mkdir -p pipeline/db/migrations
mkdir -p dashboard
mkdir -p data/raw
mkdir -p data/clean
mkdir -p data/classified
```

---

## 2. Python Environment (Pipeline)

```bash
# Create virtual environment
cd pipeline
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### `requirements.txt`

```txt
# Scrapers
google-play-scraper==1.2.7
praw==7.7.1
google-api-python-client==2.131.0
beautifulsoup4==4.12.3
playwright==1.44.0
requests==2.32.3
feedparser==6.0.11

# Cleaning
langdetect==1.0.9
datasketch==1.6.4
emoji==2.12.1
regex==2024.5.15

# LLM Classification
google-generativeai==0.8.5
groq==0.9.0

# Database
sqlalchemy==2.0.30
alembic==1.13.1

# RAG
chromadb==0.5.5
sentence-transformers==3.0.1

# Utilities
python-dotenv==1.0.1
tqdm==4.66.4
tenacity==8.3.0
uuid==1.30
```

### Post-install: Playwright browsers

```bash
# Required for Trustpilot/PissedConsumer scraping
playwright install chromium
```

---

## 3. API Keys — Registration Guide

All keys are **free**. No credit card required for any of these.

### 3.1 Google AI Studio (Gemini API)

1. Go to [https://aistudio.google.com](https://aistudio.google.com)
2. Sign in with your Google account
3. Click **"Get API Key"** → **"Create API key"**
4. Select or create a Google Cloud project
5. Copy the key → save as `GEMINI_API_KEY`

**Free limits:** ~15 RPM, ~1M TPM, ~1500 RPD (check your AI Studio quota page for exact numbers)

### 3.2 Groq (Llama API)

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up with email or Google account
3. Navigate to **API Keys** → **Create API Key**
4. Copy the key → save as `GROQ_API_KEY`

**Free limits:** 30 RPM, 1000 RPD (for Llama 3.3 70B), 14400 RPD (for Llama 3.1 8B)

### 3.3 Reddit (PRAW OAuth)

1. Go to [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Scroll down → click **"create another app..."**
3. Fill in:
   - Name: `myntra-discovery-engine`
   - Type: **script**
   - Redirect URI: `http://localhost:8080`
4. Click **"create app"**
5. Note:
   - **Client ID** = the string under the app name
   - **Client Secret** = the "secret" field
6. Save as `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`

### 3.4 YouTube Data API v3

1. Go to [https://console.cloud.google.com](https://console.cloud.google.com)
2. Create or select a project
3. Navigate to **APIs & Services** → **Library**
4. Search for **"YouTube Data API v3"** → **Enable**
5. Go to **Credentials** → **Create Credentials** → **API key**
6. Copy the key → save as `YOUTUBE_API_KEY`

**Free limits:** 10,000 units/day (each commentThread.list call = ~3 units)

### 3.5 Ollama (Local — Optional Fallback)

```bash
# Windows (via installer)
# Download from https://ollama.com/download

# After install, pull the model
ollama pull llama3.1:8b

# Start the server (runs on http://localhost:11434)
ollama serve
```

**No API key needed.** Runs entirely on your machine. Requires ~8GB RAM.

---

## 4. Environment Variables

Create a `.env` file in the project root:

```env
# === LLM APIs (all free) ===
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# === Reddit API ===
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=myntra-discovery-engine/1.0 by u/YOUR_USERNAME
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# === YouTube API ===
YOUTUBE_API_KEY=your_youtube_api_key_here

# === Database ===
DATABASE_URL=sqlite:///data/db.sqlite

# === Ollama (local, no key) ===
OLLAMA_BASE_URL=http://localhost:11434

# === Pipeline Config ===
BATCH_SIZE=10
CONFIDENCE_THRESHOLD=0.4
MAX_RPM_GEMINI=10
MAX_RPM_GROQ=25
```

Create a `.env.example` with the same keys but placeholder values, and commit this to Git.

---

## 5. Node.js Environment (Dashboard)

```bash
cd dashboard

# Initialize Next.js project (if not yet created)
npx -y create-next-app@latest ./ --js --no-tailwind --eslint --app --src-dir --no-turbopack --import-alias "@/*"

# Install additional dependencies
npm install recharts @nivo/heatmap @nivo/sankey framer-motion react-wordcloud

# Create data directory for static JSON
mkdir -p public/data
```

---

## 6. Database Initialization

```bash
cd pipeline

# Activate venv
.\venv\Scripts\activate

# Initialize the SQLite database
python -c "
from db.connection import engine
from db.models import Base
Base.metadata.create_all(engine)
print('Database initialized at data/db.sqlite')
"
```

---

## 7. Git Configuration

### `.gitignore`

```gitignore
# Python
pipeline/venv/
__pycache__/
*.pyc
*.pyo

# Node
dashboard/node_modules/
dashboard/.next/
dashboard/out/

# Data (large files)
data/raw/
data/clean/
data/classified/
data/db.sqlite

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
```

---

## 8. Verification Checklist

Run these checks after setup to confirm everything works:

```bash
# 1. Python environment
cd pipeline
.\venv\Scripts\activate
python -c "import google.generativeai; print('✅ Gemini SDK installed')"
python -c "import groq; print('✅ Groq SDK installed')"
python -c "import praw; print('✅ PRAW installed')"
python -c "import chromadb; print('✅ ChromaDB installed')"

# 2. API connectivity
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
assert os.getenv('GEMINI_API_KEY'), '❌ GEMINI_API_KEY not set'
assert os.getenv('GROQ_API_KEY'), '❌ GROQ_API_KEY not set'
assert os.getenv('REDDIT_CLIENT_ID'), '❌ REDDIT_CLIENT_ID not set'
assert os.getenv('YOUTUBE_API_KEY'), '❌ YOUTUBE_API_KEY not set'
print('✅ All API keys configured')
"

# 3. Gemini test call
python -c "
import google.generativeai as genai
from dotenv import load_dotenv
import os
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-3.7-flash')
response = model.generate_content('Say hello in one word')
print(f'✅ Gemini working: {response.text}')
"

# 4. Node/Dashboard
cd ../dashboard
npm run dev
# Should start on http://localhost:3000
```

---

## 9. IDE Recommendations

| Tool | Purpose |
|---|---|
| VS Code / Antigravity IDE | Primary editor |
| Python extension | Linting, IntelliSense for pipeline |
| ESLint extension | JavaScript linting for dashboard |
| SQLite Viewer extension | Inspect database contents |
| Thunder Client / Postman | Test API endpoints |

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `pip install` fails on `playwright` | Run `pip install playwright` separately, then `playwright install chromium` |
| Gemini returns `429 Resource Exhausted` | You've hit rate limits. Wait 60s or switch to Groq tier. |
| Reddit PRAW auth fails | Double-check client ID/secret. Ensure app type is "script". Try re-creating the app. |
| YouTube quota exceeded | 10K units/day limit. Spread scraping across days or reduce video count. |
| Ollama model download slow | `llama3.1:8b` is ~4.7GB. Use a stable connection. |
| `chromadb` install fails on Windows | Install Visual C++ Build Tools first: `pip install chromadb --no-binary :all:` or use `pip install chromadb-client` |
| Next.js won't start | Ensure Node 18+. Delete `node_modules` and `package-lock.json`, then `npm install` again. |

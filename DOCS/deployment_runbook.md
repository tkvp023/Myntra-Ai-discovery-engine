# Deployment Runbook
### AI Discovery Engine — Myntra

---

## 1. Deployment Architecture

```
Local Machine (Pipeline)         →    Vercel (Dashboard)
┌──────────────────────┐              ┌──────────────────┐
│ Python scrapers      │              │ Next.js app      │
│ LLM classification   │──export──→   │ Static JSON data │
│ Quantification       │   JSON       │ RAG API (serverless)│
│ Vector embedding     │              │ ChromaDB (bundled)│
│ SQLite DB            │              └──────────────────┘
└──────────────────────┘                    │
                                            ↓
                                    Public testable URL
```

---

## 2. Pre-Deployment Checklist

### 2.1 Pipeline Output Verification

```bash
# Verify all JSON files exist and are valid
cd dashboard/public/data/

# Check files exist
ls -la summary.json q1.json q2.json q3.json q4.json q5.json q6.json q7.json q8.json q9.json q10.json systemic_gaps.json corpus_meta.json

# Validate JSON syntax
for f in *.json; do python -m json.tool "$f" > /dev/null && echo "✅ $f valid" || echo "❌ $f INVALID"; done

# Check file sizes (should not be empty)
for f in *.json; do
    size=$(wc -c < "$f")
    if [ "$size" -lt 100 ]; then
        echo "❌ $f is suspiciously small ($size bytes)"
    else
        echo "✅ $f ($size bytes)"
    fi
done
```

### 2.2 Dashboard Build Verification

```bash
cd dashboard

# Clean install
rm -rf node_modules .next
npm install

# Build production bundle
npm run build

# Expected output:
# ✓ Compiled successfully
# Route sizes should be reasonable (< 500KB per page)

# Test production build locally
npm run start
# Visit http://localhost:3000 — verify all pages work
```

### 2.3 Environment Variables for Production

| Variable | Where Set | Notes |
|---|---|---|
| `GEMINI_API_KEY` | Vercel Dashboard → Environment Variables | For RAG answer generation |
| `GROQ_API_KEY` | Vercel Dashboard → Environment Variables | RAG fallback |
| `NEXT_PUBLIC_API_URL` | Vercel Dashboard | Leave empty (uses relative paths) |

**Note:** Reddit, YouTube, Play Store API keys are NOT needed in production — scraping is done locally. Only LLM keys for RAG are needed in production.

---

## 3. Vercel Deployment Steps

### 3.1 First-Time Setup

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Navigate to dashboard directory
cd dashboard

# 4. Link to Vercel project
vercel link
# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? [your account]
# - Link to existing project? No (first time)
# - Project name? ai-discovery-engine
# - Directory? ./
# - Override settings? No

# 5. Set environment variables
vercel env add GEMINI_API_KEY production
# Paste your API key when prompted

vercel env add GROQ_API_KEY production
# Paste your API key when prompted
```

### 3.2 Deploy

```bash
# Deploy to production
vercel --prod

# Expected output:
# ✅ Production: https://ai-discovery-engine-xxxxx.vercel.app
```

### 3.3 Custom Domain (Optional)

```bash
# Add a custom domain
vercel domains add your-domain.com

# Or use the Vercel dashboard:
# Project → Settings → Domains → Add
```

---

## 4. Post-Deployment Verification

### 4.1 Smoke Test

Visit the deployed URL and verify each page:

| Page | URL | Checks |
|---|---|---|
| Summary | `/` | Stat cards load, source chart renders, top opportunities render |
| Q1 | `/questions/1` | Charts load, segment toggle works |
| Q2 | `/questions/2` | Horizontal bars render, hover tooltips work |
| Q5 | `/questions/5` | Heatmap renders, radar chart renders |
| Q7 | `/questions/7` | Radar chart shows 8 axes, stacked bars render |
| Q10 | `/questions/10` | Word cloud renders, treemap renders, table sorts |
| Systemic Gaps | `/systemic-gaps` | Issue bars render, scatter plot renders |
| Ask the Data | `/ask` | Chat UI loads, suggested queries clickable |

### 4.2 RAG Smoke Test

Send these test queries through the chat interface:

```
1. "What is the top hesitation reason for Myntra users?"
   → Should return: Sizing uncertainty, ~34%, with citations

2. "What do Gen-Z users think about pricing?"
   → Should return: Price sensitivity data for Gen-Z segment

3. "Tell me about unmet needs"
   → Should return: List of unmet needs with frequencies
```

### 4.3 Performance Check

```bash
# Run Lighthouse on deployed URL
npx lighthouse https://your-deployed-url.vercel.app --output json

# Key metrics to check:
# - Performance: > 90
# - First Contentful Paint: < 1.5s
# - Largest Contentful Paint: < 2.5s
# - Total Blocking Time: < 200ms
```

### 4.4 Cross-Browser Check

| Browser | Version | Check |
|---|---|---|
| Chrome | Latest | All charts render, animations work |
| Firefox | Latest | All charts render, hover works |
| Safari | Latest | Glass effects work, charts render |
| Edge | Latest | All features work |

---

## 5. Rollback Procedure

If the deployment has issues:

```bash
# List recent deployments
vercel ls

# Roll back to previous deployment
vercel rollback [deployment-url]

# Or redeploy from a known-good commit
git checkout [known-good-commit]
cd dashboard
vercel --prod
```

---

## 6. Monitoring

### 6.1 Vercel Analytics (Free)

Enable in Vercel Dashboard → Project → Analytics:
- Page views per route
- Web Vitals (LCP, FID, CLS)
- Error rates

### 6.2 RAG API Monitoring

Monitor in Vercel Dashboard → Project → Functions:
- `/api/ask` invocation count
- Response times
- Error logs

### 6.3 Free Tier Limits

| Service | Free Limit | Action if Exceeded |
|---|---|---|
| Vercel | 100GB bandwidth/month, 100K function invocations | More than enough for a demo/fellowship project |
| Gemini API (RAG) | ~1500 RPD | Add rate limiting to `/api/ask` — max 100 queries/day |
| Groq API (RAG fallback) | 1000 RPD | Automatic fallback from Gemini |

---

## 7. Updating Data

If you re-run the pipeline with new data:

```bash
# 1. Re-run pipeline
cd pipeline
python run_pipeline.py --mode full

# 2. Export new JSON
python run_pipeline.py --mode export

# 3. Copy to dashboard
cp -r data/export/* ../dashboard/public/data/

# 4. Rebuild and deploy
cd ../dashboard
npm run build
vercel --prod
```

---

## 8. Sharing the Testable Link

### For Fellowship/Academic Submission

```
Project: AI-Powered Discovery Engine — Myntra Wishlist Intelligence
Live Demo: https://ai-discovery-engine-xxxxx.vercel.app

Features:
- Executive summary with quantified insights from 87,000+ user reviews
- 10 discovery questions, each with interactive visualizations
- Segment comparison (Gen-Z vs Millennial vs Gen-X)
- AI-powered Q&A over the processed corpus
- Data sourced from Play Store, Reddit, YouTube, App Store + secondary sources

Source Code: [GitHub link if applicable]
```

---

## 9. Troubleshooting — Production

| Issue | Diagnosis | Fix |
|---|---|---|
| Charts not rendering | Check browser console for JS errors | Likely a data format issue — validate JSON files |
| RAG not responding | Check Vercel Functions logs | API key might not be set — check env vars |
| Slow page load | Run Lighthouse | Enable Next.js image optimization; check bundle size |
| 404 on question pages | Check routing config | Ensure `questions/[id]/page.js` exists and handles all IDs 1–10 |
| CORS error on RAG API | Check API route headers | Add CORS headers to `/api/ask` |
| Vercel build fails | Check build logs in Vercel dashboard | Usually a missing dependency — run `npm install` and commit `package-lock.json` |
| Data looks stale | JSON files not updated | Re-run export and redeploy |

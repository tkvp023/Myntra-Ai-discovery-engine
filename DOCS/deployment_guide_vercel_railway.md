# 🚀 Production Deployment Guide: Vercel (Frontend) + Railway (Backend)

This guide walks you through deploying the **AI Discovery Engine** with:
- **Frontend (Dashboard)**: Hosted on **Vercel** (Free Next.js hosting, Edge CDN)
- **Backend (RAG API)**: Hosted on **Railway** (Python FastAPI with 8,182 vector index)

---

## 🏗️ Architecture

```
                                  HTTPS
     User Browser  ───────────►  Vercel (Next.js Dashboard)
                                        │
                                        │  Proxy /api/ask (or direct)
                                        ▼
                                 Railway (FastAPI RAG Server)
                                        │
                                ┌───────┴───────┐
                                │               │
                          Gemini 2.0 Flash    VectorStore
                          (Free LLM Tier)   (8,182 reviews)
```

---

## 📦 STEP 1: Push Repository to GitHub

Make sure your repository has the latest code and data files committed:

```bash
git add .
git commit -m "feat: complete AI Discovery Engine with Phase 5 RAG and deployment configs"
git push origin main
```

> **Files included for production:**
> - `dashboard/public/data/*.json` (13 quantified data contracts)
> - `data/vector_model.joblib` & `data/vector_meta.json` (8,182 embedded reviews)
> - `requirements.txt` & `railway.toml` & `Procfile` (Railway deployment configs)
> - `pipeline/` & `dashboard/`

---

## 🚂 STEP 2: Deploy Backend to Railway

1. Go to [railway.app](https://railway.app) and sign in with your GitHub account.
2. Click **"+ New Project"** $\rightarrow$ **"Deploy from GitHub repo"**.
3. Select your repository (`AI discovery engine(GP)`).
4. Railway will automatically detect the Python environment via `requirements.txt` and `railway.toml`.
5. **Set Environment Variables**:
   - Go to your Railway service $\rightarrow$ **Variables** tab $\rightarrow$ Click **"New Variable"**:
   
   | Variable Name | Value |
   |---|---|
   | `GEMINI_API_KEY` | `Your Gemini API Key` |
   | `GROQ_API_KEY` | `Your Groq API Key` (optional fallback) |

6. **Generate Public Domain**:
   - Go to the **Settings** tab $\rightarrow$ scroll to **Networking** $\rightarrow$ Click **"Generate Domain"**.
   - You will get a URL like: `https://ai-discovery-engine-production.up.railway.app`
7. **Verify Deployment**:
   - Open `https://YOUR_RAILWAY_URL/health` in your browser.
   - It should return:
     ```json
     {
       "status": "ok",
       "vectors": 8182,
       "model": "gemini-embedding-001 + gemini-2.0-flash"
     }
     ```

---

## ⚡ STEP 3: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) and log in.
2. Click **"Add New..."** $\rightarrow$ **"Project"**.
3. Import your GitHub repository.
4. **Configure Project Settings**:
   - **Framework Preset**: `Next.js`
   - **Root Directory**: Click **Edit** $\rightarrow$ Select `dashboard` $\rightarrow$ Click **Continue**.
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
5. **Set Environment Variables**:
   - Expand the **Environment Variables** section:
   
   | Name | Value |
   |---|---|
   | `RAG_API_URL` | `https://YOUR_RAILWAY_URL` (from Step 2) |
   | `NEXT_PUBLIC_RAG_API_URL` | `https://YOUR_RAILWAY_URL` (from Step 2) |

6. Click **"Deploy"**.
   - Vercel will build the Next.js application in ~60 seconds and assign you a production URL (e.g. `https://myntra-ai-discovery.vercel.app`).

---

## 🧪 STEP 4: Post-Deployment Smoke Test

Visit your live Vercel URL and verify:

1. **Dashboard Home (`/`)**: All 4 KPI stat cards and top opportunity bars load instantly.
2. **Questions Q1–Q10 (`/questions/1` through `/questions/10`)**: Segment toggles (`Gen-Z`, `Millennials`, `Gen-X`) update charts smoothly.
3. **Systemic Gaps (`/gaps`)**: Real representative customer complaints load with orange accent cards.
4. **Ask the Data (`/ask`)**:
   - Status badge shows: `Live RAG Engine (Gemini 2.0 Flash)` with green pulsing indicator.
   - Click a suggested query chip (e.g., *"Why do users hesitate to buy ethnic wear?"*).
   - Verify that the cited answer with grounding badges loads in ~2-3 seconds.

---

## ⚙️ Maintenance & Updates

- **Updating Data**: To refresh data or add new reviews, run the scraper & quantification pipeline locally, then push the updated `dashboard/public/data/*.json` and `data/vector_model.joblib` to GitHub. Vercel and Railway will auto-redeploy!
- **Zero Cost**: Both Vercel Hobby and Railway Starter free tiers comfortably cover this architecture at $0/month.

# API Keys Setup Guide
### AI Discovery Engine — Myntra
### Step-by-step guide to get every API key needed

---

> **Time needed:** ~20 minutes total  
> **Cost:** $0 — all keys have a free tier sufficient for this project

---

## Quick Summary

| Key | Service | Required For | Free Limit | Time to Get |
|---|---|---|---|---|
| `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` | Reddit API | Reddit scraper | 100 req/min | 2 min |
| `YOUTUBE_API_KEY` | YouTube Data API v3 | YouTube scraper | 10,000 units/day | 5 min |
| `GEMINI_API_KEY` | Google AI Studio | LLM Classification (primary) | 1,500 req/day | 3 min |
| `GROQ_API_KEY` | Groq Cloud | LLM Classification (fallback) | ~14,400 req/day | 2 min |

> **No keys needed for:** Play Store, App Store, Trustpilot, PissedConsumer, Reviews.io

---

## Step 1 — Reddit API (2 minutes)

Reddit is one of our richest sources of Hinglish fashion opinions.

### 1.1 Create a Reddit Account (if you don't have one)
Go to **[reddit.com](https://www.reddit.com)** → Sign Up

### 1.2 Create an App
1. Go to **[reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)**
2. Scroll to the bottom → Click **"Create App"** or **"Create Another App"**
3. Fill in the form:
   - **Name:** `MyntraDiscoveryEngine` (any name)
   - **App type:** Select **"script"** ← Important!
   - **Description:** `Research scraper for Myntra user reviews`
   - **About URL:** leave blank
   - **Redirect URI:** `http://localhost:8080` (required but not used)
4. Click **"Create app"**

### 1.3 Copy your credentials
After creation you'll see:

```
[App name]
personal use script
[CLIENT_ID]          ← This is a 14-character string under the app name
secret: [CLIENT_SECRET]  ← Click "edit" to reveal if hidden
```

### 1.4 Add to .env
```env
REDDIT_CLIENT_ID=your_14_char_id_here
REDDIT_CLIENT_SECRET=your_secret_here
REDDIT_USER_AGENT=MyntraDiscoveryEngine/1.0 by u/your_reddit_username
```

> **Tip:** The `REDDIT_USER_AGENT` must follow Reddit's format. Replace `your_reddit_username` with your actual Reddit username.

---

## Step 2 — YouTube Data API v3 (5 minutes)

YouTube comments give us rich qualitative data — unboxings, haul videos, reviews.

### 2.1 Go to Google Cloud Console
Go to **[console.cloud.google.com](https://console.cloud.google.com)**  
Sign in with your Google account.

### 2.2 Create a New Project
1. Click the **project dropdown** at the top (next to "Google Cloud")
2. Click **"New Project"**
3. Name it: `MyntraDiscoveryEngine`
4. Click **"Create"**
5. Wait ~30 seconds, then select the new project from the dropdown

### 2.3 Enable the YouTube Data API
1. In the left sidebar → **"APIs & Services"** → **"Library"**
2. Search for **"YouTube Data API v3"**
3. Click on it → Click **"Enable"**

### 2.4 Create an API Key
1. In the left sidebar → **"APIs & Services"** → **"Credentials"**
2. Click **"+ Create Credentials"** → **"API Key"**
3. Your key appears immediately — copy it!
4. (Optional) Click **"Restrict Key"**:
   - Under "API restrictions" → select "YouTube Data API v3"
   - This prevents misuse if the key leaks

### 2.5 Add to .env
```env
YOUTUBE_API_KEY=AIzaSy_your_key_here
```

> **Free quota:** 10,000 units/day. A search costs 100 units, fetching comments costs 1 unit each. You get ~100 searches/day free — more than enough for this project.

---

## Step 3 — Gemini API Key (3 minutes)

This is the primary LLM for classifying all 50K+ reviews.

### 3.1 Go to Google AI Studio
Go to **[aistudio.google.com](https://aistudio.google.com)**  
Sign in with your Google account.

### 3.2 Get API Key
1. Click **"Get API Key"** in the left sidebar (or top right)
2. Click **"Create API Key"**
3. Select your Google Cloud project (the one you created above, or create new)
4. Copy the key immediately!

### 3.3 Add to .env
```env
GEMINI_API_KEY=AIzaSy_your_gemini_key_here
```

> **Free limits (Gemini 2.0 Flash / 2.5 Flash):**
> - 1,500 requests/day
> - 1 million tokens/minute
> - **$0 cost** as long as you stay within limits

> **Important:** If you get `429 Resource Exhausted` errors, it means you've hit the daily limit. The pipeline will auto-failover to Groq (Step 4).

---

## Step 4 — Groq API Key (2 minutes)

Groq is the fallback LLM — extremely fast, free, and runs Llama 3.3 70B.

### 4.1 Sign Up for Groq
Go to **[console.groq.com](https://console.groq.com)**  
Click **"Sign Up"** → use Google or GitHub login (faster)

### 4.2 Create an API Key
1. In the left sidebar → **"API Keys"**
2. Click **"Create API Key"**
3. Name it: `MyntraDiscovery`
4. Copy the key (starts with `gsk_...`)

### 4.3 Add to .env
```env
GROQ_API_KEY=gsk_your_groq_key_here
```

> **Free limits (Llama 3.3 70B):**
> - 6,000 tokens/minute
> - 500 requests/day (generous for overflow classification)
> - **$0 cost**

---

## Step 5 — Configure Your .env File

Now put it all together. In the project root:

```bash
# Copy the template
copy .env.example .env
```

Then open `.env` and fill it in:

```env
# ─────────────────────────────────────────────
# Reddit API
# ─────────────────────────────────────────────
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=MyntraDiscoveryEngine/1.0 by u/your_username

# ─────────────────────────────────────────────
# YouTube Data API v3
# ─────────────────────────────────────────────
YOUTUBE_API_KEY=AIzaSy_your_youtube_key_here

# ─────────────────────────────────────────────
# Gemini (Primary LLM)
# ─────────────────────────────────────────────
GEMINI_API_KEY=AIzaSy_your_gemini_key_here

# ─────────────────────────────────────────────
# Groq (Fallback LLM)
# ─────────────────────────────────────────────
GROQ_API_KEY=gsk_your_groq_key_here
```

---

## Step 6 — Verify Keys Work

Run this quick test to check all keys are valid:

```bash
cd "AI discovery engine(GP)"
.\pipeline\venv\Scripts\python.exe pipeline\run_pipeline.py --mode scrape --sources playstore --limit 10
```

If Play Store returns 10 reviews → scraper works ✅

Then test Reddit (needs key):
```bash
.\pipeline\venv\Scripts\python.exe pipeline\run_pipeline.py --mode scrape --sources reddit --limit 5
```

---

## Troubleshooting

### Reddit: `ResponseException: received 401 HTTP response`
→ Wrong `REDDIT_CLIENT_ID` or `REDDIT_CLIENT_SECRET`. Double-check from [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps).

### Reddit: `prawcore.exceptions.OAuthException`
→ Make sure app type is **"script"** not "web app".

### YouTube: `HttpError 403 quotaExceeded`
→ Daily 10,000 unit quota hit. Resets at midnight Pacific Time. Scraper will resume next day.

### YouTube: `HttpError 400 keyInvalid`
→ API key is wrong OR YouTube Data API v3 is not enabled in Cloud Console.

### Gemini: `429 Resource Exhausted`
→ Free tier daily limit hit. Pipeline auto-failovers to Groq. No action needed.

### Gemini: `403 API key not valid`
→ Key copied incorrectly. Regenerate from [aistudio.google.com](https://aistudio.google.com).

### Groq: `AuthenticationError`
→ Key must start with `gsk_`. Regenerate from [console.groq.com](https://console.groq.com).

---

## Optional: Ollama (Local Fallback — No Key Needed)

If you want a fully-offline LLM fallback:

```bash
# 1. Download Ollama from:
#    https://ollama.com/download (Windows installer)

# 2. After install, pull the model:
ollama pull llama3.1:8b

# 3. Start Ollama server:
ollama serve

# 4. No .env key needed — pipeline auto-detects it
```

> Ollama runs Llama 3.1 8B locally. Requires ~5GB disk + 8GB RAM. Quality is good but slightly lower than Gemini/Groq.

---

## Security Reminders

> [!CAUTION]
> - **Never commit `.env` to Git.** It's already in `.gitignore`.
> - **Never share your keys** in screenshots, Slack, or Discord.
> - If a key is accidentally exposed, **regenerate it immediately** from the respective console.
> - YouTube and Gemini keys share the same Google Cloud project — you can restrict the YouTube key to only the YouTube API for extra safety.

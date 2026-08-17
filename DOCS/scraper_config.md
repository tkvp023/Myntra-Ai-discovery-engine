# Scraper Configuration
### AI Discovery Engine — Myntra

---

## 1. Play Store Reviews

### Target App
| Field | Value |
|---|---|
| App Name | Myntra: Fashion Shopping App |
| Package ID | `com.myntra.android` |
| Library | `google-play-scraper` (Python) |

### Scraping Parameters

```python
PLAYSTORE_CONFIG = {
    "app_id": "com.myntra.android",
    "lang": "en",               # Primary language
    "country": "in",            # India
    "sort": "NEWEST",           # Most recent first
    "count": 50000,             # Target: 50K reviews
    "filter_score_with": None,  # All ratings (1-5)
}
```

### Pagination Strategy
- `google-play-scraper` uses continuation tokens internally
- Fetch in batches of 200 (library default)
- Estimated time: ~30–60 minutes for 50K reviews
- Save checkpoint every 5K reviews

### Fields to Extract
| Field | Maps To |
|---|---|
| `reviewId` | `source_id` |
| `content` | `content` |
| `score` | `rating` |
| `at` | `timestamp` |
| `userName` | `author` (will be anonymized) |
| `replyContent` | `metadata.developer_reply` |
| `appVersion` | `metadata.app_version` |

---

## 2. App Store Reviews

### Target App
| Field | Value |
|---|---|
| App Name | Myntra - Fashion Shopping |
| App ID | `907394059` |
| Method | Apple RSS Feed + web scraping fallback |

### RSS Feed URL
```
https://itunes.apple.com/in/rss/customerreviews/id=907394059/sortBy=mostRecent/json
```

### Scraping Parameters

```python
APPSTORE_CONFIG = {
    "app_id": "907394059",
    "country": "in",
    "max_pages": 50,          # RSS returns 50 per page
    "sort_by": "mostRecent",
    "target_count": 10000,    # Expect ~5K-10K (India volume is low)
}
```

### Fields to Extract
| RSS Field | Maps To |
|---|---|
| `id.label` | `source_id` |
| `content.label` | `content` |
| `im:rating.label` | `rating` |
| `updated.label` | `timestamp` |
| `author.name.label` | `author` (anonymized) |
| `im:version.label` | `metadata.app_version` |
| `title.label` | `title` |

---

## 3. Reddit (PRAW)

### Target Subreddits

| Subreddit | Relevance | Expected Volume |
|---|---|---|
| `r/IndianFashionAddicts` | **Primary** — dedicated fashion discussion | High |
| `r/india` | General — large community, Myntra mentions scattered | Medium |
| `r/twoxindia` | Women's perspective — fashion/shopping discussions | Medium |
| `r/IndianSkincareAddicts` | Crossover — beauty + fashion overlap | Low |
| `r/Frugal_India` | Price sensitivity signals | Low |
| `r/bangalore` / `r/mumbai` / `r/delhi` | Metro city shopping behavior | Low |

### Search Queries

```python
REDDIT_CONFIG = {
    "subreddits": [
        "IndianFashionAddicts",
        "india",
        "twoxindia",
        "IndianSkincareAddicts",
        "Frugal_India",
        "bangalore",
        "mumbai",
        "delhi",
    ],
    "search_queries": [
        "myntra",
        "myntra wishlist",
        "myntra review",
        "myntra quality",
        "myntra sale",
        "myntra vs ajio",
        "myntra vs amazon",
        "myntra sizing",
        "myntra return",
        "online fashion shopping india",
        "myntra haul",
        "myntra order",
        "myntra delivery",
        "fashion app india",
    ],
    "sort": "relevance",        # Sort search results by relevance
    "time_filter": "all",       # All time (maximize volume)
    "limit_per_query": 500,     # Posts per search query
    "include_comments": True,   # Scrape comment threads too
    "comment_depth": 5,         # Max comment tree depth
    "min_upvotes": 1,           # Skip 0-vote posts
}
```

### Rate Limits
- PRAW handles rate limiting automatically (60 req/min)
- Use `time.sleep(1)` between search queries as a safety buffer
- Estimated time: ~2–4 hours for all subreddits + queries

### Fields to Extract

**Posts:**
| PRAW Field | Maps To |
|---|---|
| `id` | `source_id` |
| `title` | `title` |
| `selftext` | `content` |
| `score` | `metadata.upvotes` |
| `created_utc` | `timestamp` |
| `author.name` | `author` (anonymized) |
| `subreddit.display_name` | `metadata.subreddit` |
| `permalink` | `url` |
| `num_comments` | `metadata.comment_count` |

**Comments:**
| PRAW Field | Maps To |
|---|---|
| `id` | `source_id` |
| `body` | `content` |
| `score` | `metadata.upvotes` |
| `created_utc` | `timestamp` |
| `author.name` | `author` (anonymized) |
| `parent_id` | `metadata.parent_id` |
| `link_id` | `metadata.post_id` |

---

## 4. YouTube Comments

### Search Strategy

Search for Myntra-related videos, extract video IDs, then pull comment threads.

### Video Search Queries

```python
YOUTUBE_CONFIG = {
    "search_queries": [
        "myntra haul",
        "myntra review",
        "myntra shopping haul",
        "myntra wishlist",
        "myntra try on haul",
        "myntra sale haul",
        "myntra fashion haul",
        "myntra vs ajio haul",
        "myntra clothing review",
        "myntra online shopping experience",
        "myntra best products",
        "is myntra worth it",
    ],
    "max_videos_per_query": 30,     # Top 30 videos per search
    "max_comments_per_video": 200,  # Top 200 comments per video
    "order": "relevance",           # Video search sort
    "published_after": "2022-01-01T00:00:00Z",  # Last ~4 years
    "region_code": "IN",
    "relevance_language": "en",
    "comment_order": "relevance",   # Comment sort within each video
}
```

### API Quota Management
- **Budget:** 10,000 units/day
- `search.list` = 100 units per call (returns 50 results)
- `commentThreads.list` = 1 unit per call (returns 20 comments)
- **Estimated daily capacity:** ~80 video searches + ~9,000 comment fetches
- Strategy: scrape video IDs on Day 1, comments on Day 1–2

### Fields to Extract

**From Comments:**
| API Field | Maps To |
|---|---|
| `id` | `source_id` |
| `snippet.textDisplay` | `content` |
| `snippet.likeCount` | `metadata.upvotes` |
| `snippet.publishedAt` | `timestamp` |
| `snippet.authorDisplayName` | `author` (anonymized) |
| `snippet.videoId` | `metadata.video_id` |
| `snippet.parentId` | `metadata.parent_id` (for replies) |

**Video metadata (stored separately):**
| Field | Purpose |
|---|---|
| `video_id` | Link comments back to video |
| `title` | Context for comments (stored as `title` in unified doc) |
| `channel_title` | Creator attribution |
| `view_count` | Signal of reach |
| `published_at` | Video date |

---

## 5. Trustpilot (Secondary)

### Target Page
| Field | Value |
|---|---|
| URL | `https://www.trustpilot.com/review/www.myntra.com` |
| Method | Playwright (headless browser) — needed for JavaScript-rendered content |

### Scraping Parameters

```python
TRUSTPILOT_CONFIG = {
    "base_url": "https://www.trustpilot.com/review/www.myntra.com",
    "max_pages": 100,            # ~20 reviews per page
    "target_count": 5000,
    "sort_by": "recency",
    "wait_between_pages": 2,     # seconds — avoid anti-bot
    "headless": True,
}
```

### Anti-Bot Mitigation
- Use Playwright with random user-agent rotation
- Add random delays (1–3s) between page loads
- Respect robots.txt rate suggestions
- If blocked, fall back to manual export or reduce speed

### Fields to Extract
| Selector | Maps To |
|---|---|
| Review text body | `content` |
| Star rating | `rating` |
| Review date | `timestamp` |
| Reviewer name | `author` (anonymized) |
| Review title | `title` |
| Review URL | `url` |

---

## 6. PissedConsumer (Secondary)

### Target Page
| Field | Value |
|---|---|
| URL | `https://www.pissedconsumer.com/company/myntra/reviews.html` |
| Method | BeautifulSoup + requests (mostly static HTML) |

### Scraping Parameters

```python
PISSEDCONSUMER_CONFIG = {
    "base_url": "https://www.pissedconsumer.com/company/myntra/reviews.html",
    "max_pages": 50,
    "target_count": 3000,
    "wait_between_pages": 3,    # Conservative delay
}
```

### Fields to Extract
| Element | Maps To |
|---|---|
| Review body text | `content` |
| Star rating | `rating` |
| Date posted | `timestamp` |
| Review title | `title` |
| Complaint category | `metadata.category` |

---

## 7. Reviews.io (Secondary)

### Target Page
| Field | Value |
|---|---|
| URL | `https://www.reviews.io/company-reviews/store/myntra.com` |
| Method | BeautifulSoup + requests |

### Scraping Parameters

```python
REVIEWSIO_CONFIG = {
    "base_url": "https://www.reviews.io/company-reviews/store/myntra.com",
    "max_pages": 20,          # Very thin presence
    "target_count": 1000,
    "wait_between_pages": 2,
}
```

---

## 8. Orchestration Strategy

### Execution Order

```
Phase 1 (Parallel — no dependencies):
  ├── Play Store scraper     (~50K reviews, ~45 min)
  ├── App Store scraper      (~5K reviews, ~10 min)
  └── Reddit scraper         (~15K posts+comments, ~3 hrs)

Phase 2 (After Phase 1 video IDs collected):
  └── YouTube comments       (~10K comments, ~2 hrs)

Phase 3 (Parallel — secondary, lower priority):
  ├── Trustpilot scraper     (~3K reviews, ~30 min)
  ├── PissedConsumer scraper (~2K reviews, ~20 min)
  └── Reviews.io scraper     (~500 reviews, ~10 min)
```

### Error Handling

| Scenario | Response |
|---|---|
| Scraper crashes mid-run | Resume from last checkpoint (save progress every 500 docs) |
| Rate limit hit (429) | Exponential backoff: 1s → 2s → 4s → 8s → max 60s |
| Anti-bot block (403) | Log warning, skip page, continue. Retry with different user-agent later. |
| Network timeout | Retry 3x with 5s delay. If still failing, mark source as partial. |
| Empty/malformed response | Log and skip. Don't add to corpus. |

### Checkpoint Format

```json
{
  "scraper": "playstore",
  "last_checkpoint": "2026-08-15T12:00:00Z",
  "docs_scraped": 23500,
  "continuation_token": "abc123...",
  "status": "in_progress",
  "errors": []
}
```

---

## 9. Output Format

All scrapers output to `data/raw/{source_name}/` as JSON files:

```
data/raw/
├── playstore/
│   ├── batch_001.json    (500 docs per file)
│   ├── batch_002.json
│   └── ...
├── appstore/
│   └── batch_001.json
├── reddit/
│   ├── posts_batch_001.json
│   └── comments_batch_001.json
├── youtube/
│   ├── videos_metadata.json
│   └── comments_batch_001.json
├── trustpilot/
│   └── batch_001.json
├── pissedconsumer/
│   └── batch_001.json
└── reviewsio/
    └── batch_001.json
```

Each batch file contains an array of documents in the **Unified Document Schema** (defined in `architecture.md`).

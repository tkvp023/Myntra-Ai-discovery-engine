"""
Scraper configurations for all 7 data sources.
Matches scraper_config.md specifications.
"""

# ──────────────────────────────────────────────────────────
# 1. Play Store
# ──────────────────────────────────────────────────────────
PLAYSTORE_CONFIG = {
    "app_id": "com.myntra.android",
    "lang": "en",
    "country": "in",
    "sort": 1,                  # NEWEST
    "count": 50000,
    "batch_size": 200,
    "checkpoint_every": 5000,
}

# ──────────────────────────────────────────────────────────
# 2. App Store
# ──────────────────────────────────────────────────────────
APPSTORE_CONFIG = {
    "app_id": "907394059",
    "country": "in",
    "rss_url": "https://itunes.apple.com/in/rss/customerreviews/id=907394059/sortBy=mostRecent/json",
    "max_pages": 50,
    "target_count": 10000,
}

# ──────────────────────────────────────────────────────────
# 3. Reddit
# ──────────────────────────────────────────────────────────
REDDIT_CONFIG = {
    "subreddits": [
        "MyntraSucks",
        "dealsforindia",
        "IndianGlamDeals",
        "IndianBeautyDeals",
        "IndianFashionAddicts",
        "india",
        "twoxindia",
        "IndianSkincareAddicts",
        "Frugal_India",
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
    "sort": "relevance",
    "time_filter": "all",
    "limit_per_query": 500,
    "include_comments": True,
    "comment_depth": 5,
    "min_upvotes": 1,
}

# ──────────────────────────────────────────────────────────
# 4. YouTube
# ──────────────────────────────────────────────────────────
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
    "max_videos_per_query": 30,
    "max_comments_per_video": 200,
    "order": "relevance",
    "published_after": "2022-01-01T00:00:00Z",
    "region_code": "IN",
    "relevance_language": "en",
    "comment_order": "relevance",
}

# ──────────────────────────────────────────────────────────
# 5. Trustpilot (Secondary)
# ──────────────────────────────────────────────────────────
TRUSTPILOT_CONFIG = {
    "base_url": "https://www.trustpilot.com/review/www.myntra.com",
    "max_pages": 100,
    "target_count": 5000,
    "wait_between_pages": 2,
}

# ──────────────────────────────────────────────────────────
# 6. PissedConsumer (Secondary)
# ──────────────────────────────────────────────────────────
PISSEDCONSUMER_CONFIG = {
    "base_url": "https://myntra.pissedconsumer.com/review.html",
    "max_pages": 50,
    "target_count": 3000,
    "wait_between_pages": 2,
}

# ──────────────────────────────────────────────────────────
# 7. Reviews.io (Secondary)
# ──────────────────────────────────────────────────────────
REVIEWSIO_CONFIG = {
    "base_url": "https://www.reviews.io/company-reviews/store/myntra.com",
    "max_pages": 20,
    "target_count": 1000,
    "wait_between_pages": 2,
}

# ──────────────────────────────────────────────────────────
# Aggregate config
# ──────────────────────────────────────────────────────────
SCRAPER_CONFIGS = {
    "playstore": PLAYSTORE_CONFIG,
    "appstore": APPSTORE_CONFIG,
    "reddit": REDDIT_CONFIG,
    "youtube": YOUTUBE_CONFIG,
    "trustpilot": TRUSTPILOT_CONFIG,
    "pissedconsumer": PISSEDCONSUMER_CONFIG,
    "reviewsio": REVIEWSIO_CONFIG,
}

# Valid source names and types
VALID_SOURCES = {"playstore", "appstore", "reddit", "youtube", "trustpilot", "pissedconsumer", "reviewsio"}
PRIMARY_SOURCES = {"playstore", "appstore", "reddit", "youtube"}
SECONDARY_SOURCES = {"trustpilot", "pissedconsumer", "reviewsio"}

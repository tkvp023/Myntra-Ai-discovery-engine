"""
Reddit scraper supporting:
1. Apify Reddit Scraper (`trudax/reddit-scraper-lite` or `apify/reddit-scraper`) via APIFY_API_TOKEN
2. Public Reddit JSON search (No API key needed fallback)
3. PRAW (Python Reddit API Wrapper) if OAuth credentials are provided

Target subreddits include:
- r/MyntraSucks (Systemic gaps & complaints)
- r/dealsforindia (Price sensitivity, deals, sales)
- r/IndianGlamDeals (Fashion deals & wishlist drops)
- r/IndianBeautyDeals (Coupons, sales, comparisons)
- r/IndianFashionAddicts (Fit, sizing, quality, styling)
"""

import os
import sys
import json
import urllib.parse
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import requests
from pipeline.scrapers.base_scraper import BaseScraper, ScrapedDocument, anonymize_username
from pipeline.scrapers.config import REDDIT_CONFIG


class RedditScraper(BaseScraper):

    @property
    def source_name(self) -> str:
        return "reddit"

    # ──────────────────────────────────────────────────────────
    # 1. Apify Scraper Implementation (Primary)
    # ──────────────────────────────────────────────────────────
    def _scrape_via_apify(self, limit: Optional[int] = None) -> List[ScrapedDocument]:
        """Scrape Reddit using Apify actor (trudax/reddit-scraper-lite or apify/reddit-scraper)."""
        apify_token = os.getenv("APIFY_API_TOKEN")
        if not apify_token:
            return []

        print("  🚀 Using Apify Reddit Scraper Actor...")
        try:
            from apify_client import ApifyClient
            client = ApifyClient(apify_token)
        except ImportError:
            print("  ⚠️ apify-client not installed. Run: pip install apify-client")
            return []

        subreddits = self.config.get("subreddits", REDDIT_CONFIG["subreddits"])
        queries = self.config.get("search_queries", REDDIT_CONFIG["search_queries"])
        max_items = limit or 5000

        # Build start URLs for targeted subreddits + search keywords
        start_urls = []
        for sub in subreddits:
            # Add subreddit home / top feed
            start_urls.append({"url": f"https://www.reddit.com/r/{sub}/"})
            for q in queries[:4]:  # Top high-signal search queries per sub
                encoded_q = urllib.parse.quote(q)
                start_urls.append({"url": f"https://www.reddit.com/r/{sub}/search/?q={encoded_q}&restrict_sr=1"})

        run_input = {
            "startUrls": start_urls,
            "maxItems": max_items,
            "includeComments": self.config.get("include_comments", True),
            "maxComments": self.config.get("comment_depth", 5),
            "sort": self.config.get("sort", "relevance"),
            "time": self.config.get("time_filter", "all"),
        }

        actor_id = os.getenv("APIFY_REDDIT_ACTOR", "trudax/reddit-scraper-lite")
        print(f"  📡 Calling Apify Actor `{actor_id}` with {len(start_urls)} target URLs (max {max_items} items)...")

        run = client.actor(actor_id).call(run_input=run_input)
        if not run:
            print("  ⚠️ Apify run did not return results.")
            return []

        documents: List[ScrapedDocument] = []
        dataset_id = getattr(run, "default_dataset_id", None) or (run.get("defaultDatasetId") if isinstance(run, dict) else None)
        if not dataset_id:
            print("  ⚠️ Could not find defaultDatasetId on Apify run.")
            return []

        dataset_client = client.dataset(dataset_id)
        existing_ids = self.get_existing_source_ids()
        seen_ids = set(existing_ids)

        for item in dataset_client.iterate_items():
            doc = self._apify_item_to_doc(item)
            if doc and doc.source_id not in seen_ids:
                documents.append(doc)
                seen_ids.add(doc.source_id)

            # Process nested comments if present in output
            comments = item.get("comments") or item.get("commentList") or []
            if isinstance(comments, list):
                for comment in comments:
                    cdoc = self._apify_comment_to_doc(comment, item.get("subreddit") or "unknown")
                    if cdoc and cdoc.source_id not in seen_ids:
                        documents.append(cdoc)
                        seen_ids.add(cdoc.source_id)

            if limit and len(documents) >= limit:
                break

        print(f"  ✅ Apify scraping completed. Extracted {len(documents)} documents.")
        return documents

    def _apify_item_to_doc(self, item: Dict[str, Any]) -> Optional[ScrapedDocument]:
        """Convert Apify raw item (post or comment) to ScrapedDocument."""
        try:
            data_type = item.get("dataType", "post")
            if data_type == "community":
                return None

            content = item.get("body") or item.get("text") or item.get("selftext") or ""
            title = item.get("title") or ""
            full_content = f"{title}\n\n{content}".strip() if (title and content) else (content or title)
            if not full_content or full_content in ("[deleted]", "[removed]"):
                return None

            raw_id = item.get("id") or item.get("postId") or item.get("commentId") or str(hash(full_content))[:12]
            raw_time = item.get("createdAt") or item.get("parsedTime") or datetime.now(timezone.utc).isoformat()
            subreddit = item.get("subreddit") or item.get("communityName") or "unknown"
            author = item.get("author") or item.get("username") or "[deleted]"

            return ScrapedDocument(
                source="reddit",
                source_type="primary",
                source_id=f"reddit_{raw_id}",
                author=anonymize_username(author),
                content=full_content,
                title=title if title else None,
                rating=None,
                timestamp=raw_time,
                url=item.get("url") or item.get("link"),
                metadata={
                    "subreddit": str(subreddit).replace("r/", ""),
                    "upvotes": item.get("upVotes") or item.get("score") or 0,
                    "comment_count": item.get("numberOfComments") or item.get("numComments") or 0,
                    "post_type": "submission" if data_type == "post" else "comment",
                    "scraper_engine": "apify",
                },
            )
        except Exception:
            return None

    def _apify_comment_to_doc(self, comment: Dict[str, Any], subreddit: str) -> Optional[ScrapedDocument]:
        """Convert an Apify comment to ScrapedDocument."""
        try:
            body = comment.get("body") or comment.get("text") or ""
            if not body.strip() or body in ("[deleted]", "[removed]"):
                return None

            cid = comment.get("id") or comment.get("commentId") or str(hash(body))[:10]
            raw_time = comment.get("createdAt") or datetime.now(timezone.utc).isoformat()

            return ScrapedDocument(
                source="reddit",
                source_type="primary",
                source_id=f"reddit_comment_{cid}",
                author=anonymize_username(comment.get("author") or "[deleted]"),
                content=body.strip(),
                title=None,
                rating=None,
                timestamp=raw_time,
                url=comment.get("url") or comment.get("link"),
                metadata={
                    "subreddit": str(subreddit).replace("r/", ""),
                    "upvotes": comment.get("upVotes") or comment.get("score") or 0,
                    "post_type": "comment",
                    "scraper_engine": "apify",
                },
            )
        except Exception:
            return None

    # ──────────────────────────────────────────────────────────
    # 2. Public JSON Fallback (No Keys Needed)
    # ──────────────────────────────────────────────────────────
    def _scrape_via_public_json(self, limit: Optional[int] = None) -> List[ScrapedDocument]:
        """Scrape Reddit public search endpoints (.json) with polite rate limits."""
        print("  🌐 Using Public Reddit JSON endpoints...")
        subreddits = self.config.get("subreddits", REDDIT_CONFIG["subreddits"])
        queries = self.config.get("search_queries", REDDIT_CONFIG["search_queries"])

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        documents = []
        existing_ids = self.get_existing_source_ids()
        seen_ids = set(existing_ids)

        for sub in subreddits:
            for q in queries[:3]:
                try:
                    url = f"https://www.reddit.com/r/{sub}/search.json?q={urllib.parse.quote(q)}&restrict_sr=1&sort=relevance&limit=50"
                    resp = requests.get(url, headers=headers, timeout=10)
                    if resp.status_code == 429:
                        print("  ⚠️ Reddit public JSON rate limited. Sleeping 5s...")
                        self.rate_limit_sleep(5.0)
                        continue
                    if resp.status_code != 200:
                        continue

                    data = resp.json()
                    children = data.get("data", {}).get("children", [])

                    for child in children:
                        post = child.get("data", {})
                        pid = post.get("id")
                        if not pid or pid in seen_ids:
                            continue

                        title = post.get("title", "")
                        selftext = post.get("selftext", "")
                        full_content = f"{title}\n\n{selftext}".strip() if selftext else title

                        if full_content:
                            doc = ScrapedDocument(
                                source="reddit",
                                source_type="primary",
                                source_id=f"reddit_{pid}",
                                author=anonymize_username(post.get("author", "[deleted]")),
                                content=full_content,
                                title=title,
                                rating=None,
                                timestamp=datetime.fromtimestamp(post.get("created_utc", 0), tz=timezone.utc).isoformat(),
                                url=f"https://reddit.com{post.get('permalink', '')}",
                                metadata={
                                    "subreddit": sub,
                                    "upvotes": post.get("score", 0),
                                    "comment_count": post.get("num_comments", 0),
                                    "post_type": "submission",
                                    "scraper_engine": "public_json",
                                },
                            )
                            documents.append(doc)
                            seen_ids.add(pid)

                        if limit and len(documents) >= limit:
                            return documents

                    self.rate_limit_sleep(2.0)
                except Exception as e:
                    print(f"  ⚠️ Error scraping r/{sub} via public JSON: {e}")

        return documents

    # ──────────────────────────────────────────────────────────
    # 3. Main Scrape Entrypoint
    # ──────────────────────────────────────────────────────────
    def scrape(self, limit: Optional[int] = None) -> List[ScrapedDocument]:
        """Scrape Reddit using Apify (preferred), falling back to public JSON endpoints or PRAW."""
        # 1. Try Apify if token available
        if os.getenv("APIFY_API_TOKEN"):
            docs = self._scrape_via_apify(limit)
            if docs:
                return docs

        # 2. Try PRAW if OAuth credentials exist
        if os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET"):
            print("  🔑 Found Reddit OAuth keys. Attempting PRAW...")
            try:
                import praw
                reddit = praw.Reddit(
                    client_id=os.getenv("REDDIT_CLIENT_ID"),
                    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                    user_agent=os.getenv("REDDIT_USER_AGENT", "myntra-discovery/1.0"),
                )
                # Test credentials
                _ = reddit.read_only
                print("  ✅ PRAW initialized successfully.")
            except Exception as e:
                print(f"  ⚠️ PRAW init failed: {e}. Falling back to public JSON...")

        # 3. Fallback to public JSON endpoints
        return self._scrape_via_public_json(limit)

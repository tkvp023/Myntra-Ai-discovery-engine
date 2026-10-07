"""
Apple App Store scraper for Myntra app reviews.
Uses Apple RSS feed (no auth required). India volume is typically low.
"""

import json
from typing import List, Optional
from datetime import datetime, timezone

import requests
import feedparser

from pipeline.scrapers.base_scraper import BaseScraper, ScrapedDocument, anonymize_username, with_retry
from pipeline.scrapers.config import APPSTORE_CONFIG


class AppStoreScraper(BaseScraper):

    @property
    def source_name(self) -> str:
        return "appstore"

    @with_retry
    def _fetch_rss_page(self, page: int = 1) -> list:
        """Fetch a page of reviews from the Apple RSS feed."""
        url = f"https://itunes.apple.com/in/rss/customerreviews/page={page}/id={self.config['app_id']}/json"

        response = requests.get(url, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "application/json",
        })
        response.raise_for_status()

        data = response.json()
        entries = data.get("feed", {}).get("entry", [])

        # First entry is usually the app metadata, skip it
        if entries and isinstance(entries, list) and "im:name" in entries[0]:
            entries = entries[1:]

        return entries if isinstance(entries, list) else []

    def _parse_entry(self, entry: dict) -> Optional[ScrapedDocument]:
        """Parse a single RSS entry into a ScrapedDocument."""
        try:
            content = entry.get("content", {}).get("label", "")
            if not content:
                return None

            review_id = entry.get("id", {}).get("label", "")
            author_name = entry.get("author", {}).get("name", {}).get("label", "")
            rating_str = entry.get("im:rating", {}).get("label", "")
            title = entry.get("title", {}).get("label", "")
            updated = entry.get("updated", {}).get("label", "")
            version = entry.get("im:version", {}).get("label", "")
            link = entry.get("link", {}).get("attributes", {}).get("href", "")

            return ScrapedDocument(
                source="appstore",
                source_type="primary",
                source_id=review_id,
                author=anonymize_username(author_name),
                content=content,
                title=title,
                rating=float(rating_str) if rating_str else None,
                timestamp=updated if updated else datetime.now(timezone.utc).isoformat(),
                url=link if link else None,
                metadata={
                    "app_version": version,
                    "store": "apple_in",
                },
            )
        except Exception as e:
            return None

    def scrape(self, limit: Optional[int] = None) -> List[ScrapedDocument]:
        max_pages = self.config.get("max_pages", 20)
        target = limit or self.config.get("target_count", 5000)

        existing_ids = self.get_existing_source_ids()
        documents = []

        from tqdm import tqdm
        pbar = tqdm(total=target, desc="  App Store", unit="reviews")

        empty_streak = 0
        for page in range(1, max_pages + 1):
            try:
                entries = self._fetch_rss_page(page=page)

                if not entries:
                    empty_streak += 1
                    if empty_streak >= 5:
                        break
                    continue

                empty_streak = 0
                for entry in entries:
                    doc = self._parse_entry(entry)
                    if doc and doc.source_id not in existing_ids:
                        documents.append(doc)
                        existing_ids.add(doc.source_id)
                        pbar.update(1)

                if len(documents) >= target:
                    break

                self.rate_limit_sleep(0.5)

            except Exception as e:
                continue

        pbar.close()
        return documents

"""
PissedConsumer scraper for Myntra reviews (secondary source).
Complaint-heavy — essential for systemic gap analysis.
"""

import sys
import time
import random
from typing import List, Optional
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import requests
from bs4 import BeautifulSoup

from pipeline.scrapers.base_scraper import BaseScraper, ScrapedDocument, anonymize_username, with_retry
from pipeline.scrapers.config import PISSEDCONSUMER_CONFIG


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
]


class PissedConsumerScraper(BaseScraper):

    @property
    def source_name(self) -> str:
        return "pissedconsumer"

    @with_retry
    def _fetch_page(self, page: int) -> Optional[BeautifulSoup]:
        """Fetch a page of PissedConsumer reviews."""
        url = self.config.get("base_url", "https://myntra.pissedconsumer.com/review.html")
        if page > 1:
            url = f"{url}?page={page}"

        response = requests.get(url, timeout=30, headers={
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        })

        if response.status_code == 403:
            print(f"  ⚠️ Blocked at page {page}")
            return None
        if response.status_code == 404:
            return None

        response.raise_for_status()
        return BeautifulSoup(response.text, "lxml")

    def _parse_reviews(self, soup: BeautifulSoup, page: int) -> List[dict]:
        """Extract reviews from a PissedConsumer page."""
        reviews = []

        # Find review item containers
        review_items = soup.find_all("div", class_=lambda c: c and "review-item" in str(c).lower())
        if not review_items:
            review_items = soup.find_all("div", class_=lambda c: c and "f-component-item" in str(c).lower())

        for item in review_items:
            try:
                # Text content
                text_elem = item.find("div", class_=lambda c: c and "review_text_container" in str(c).lower()) or item.find("p")
                content = text_elem.get_text(strip=True) if text_elem else ""
                if not content or len(content) < 15:
                    continue

                # Title
                title_elem = item.find(["h2", "h3", "h4"]) or item.find("a", class_=lambda c: c and "title" in str(c).lower())
                title = title_elem.get_text(strip=True) if title_elem else ""

                # Rating / Score
                rating_elem = item.find("span", class_=lambda c: c and "rating" in str(c).lower())
                rating = 1.0  # PissedConsumer defaults to 1 star complaints
                if rating_elem:
                    try:
                        rating = float(rating_elem.get_text(strip=True).split("/")[0])
                    except (ValueError, IndexError):
                        rating = 1.0

                # Author / ID
                author_elem = item.find("span", class_=lambda c: c and "author" in str(c).lower()) or item.find("a", class_=lambda c: c and "user" in str(c).lower())
                author_name = author_elem.get_text(strip=True) if author_elem else "Anonymous"

                # Review ID
                review_id = f"pc_p{page}_{abs(hash(content)) % 10000000}"

                reviews.append({
                    "id": review_id,
                    "author": author_name,
                    "title": title if title else None,
                    "content": content,
                    "rating": rating,
                    "date": datetime.now(timezone.utc).isoformat()[:10],
                    "url": f"https://myntra.pissedconsumer.com/review.html#review-{review_id}",
                    "metadata": {
                        "platform": "pissedconsumer",
                        "page": page,
                        "category": "complaint",
                    },
                })
            except Exception:
                continue

        return reviews

    def scrape(self, limit: Optional[int] = None) -> List[ScrapedDocument]:
        max_pages = self.config.get("max_pages", 50)
        target = limit or self.config.get("target_count", 3000)
        wait_time = self.config.get("wait_between_pages", 2)

        existing_ids = self.get_existing_source_ids()
        documents = []
        seen_ids = set(existing_ids)

        from tqdm import tqdm
        pbar = tqdm(total=min(target, max_pages * 20), desc="  PissedConsumer", unit="reviews")

        for page in range(1, max_pages + 1):
            if len(documents) >= target:
                break

            try:
                soup = self._fetch_page(page)
                if not soup:
                    break

                raw_reviews = self._parse_reviews(soup, page)
                if not raw_reviews:
                    break

                new_count = 0
                for r in raw_reviews:
                    if r["id"] not in seen_ids:
                        doc = ScrapedDocument(
                            source="pissedconsumer",
                            source_type="secondary",
                            source_id=r["id"],
                            author=anonymize_username(r["author"]),
                            content=r["content"],
                            title=r["title"],
                            rating=r["rating"],
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            url=r["url"],
                            metadata=r["metadata"],
                        )
                        documents.append(doc)
                        seen_ids.add(r["id"])
                        new_count += 1

                pbar.update(new_count)
                self.rate_limit_sleep(wait_time)

            except Exception as e:
                print(f"  ⚠️ Error on page {page}: {e}")
                break

        pbar.close()
        return documents

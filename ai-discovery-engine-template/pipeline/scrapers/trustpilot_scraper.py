"""
Trustpilot scraper for Myntra reviews (secondary source).
Uses requests + BeautifulSoup. Complaint-skewed but useful for systemic gap analysis.
"""

import time
import random
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from pipeline.scrapers.base_scraper import BaseScraper, ScrapedDocument, anonymize_username, with_retry
from pipeline.scrapers.config import TRUSTPILOT_CONFIG


# User-Agent rotation to mitigate anti-bot detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
]


class TrustpilotScraper(BaseScraper):

    @property
    def source_name(self) -> str:
        return "trustpilot"

    @with_retry
    def _fetch_page(self, page: int) -> Optional[BeautifulSoup]:
        """Fetch and parse a single page of Trustpilot reviews."""
        url = f"{self.config['base_url']}?page={page}"

        response = requests.get(url, timeout=30, headers={
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        })

        if response.status_code == 403:
            print(f"  ⚠️  Blocked by Trustpilot at page {page}")
            return None

        response.raise_for_status()
        return BeautifulSoup(response.text, "lxml")

    def _parse_reviews(self, soup: BeautifulSoup) -> List[dict]:
        """Extract reviews from a parsed Trustpilot page."""
        reviews = []

        # Trustpilot review cards
        review_cards = soup.find_all("article", {"data-service-review-card-paper": True})
        if not review_cards:
            review_cards = soup.find_all("div", class_=lambda c: c and "reviewCard" in c)

        for card in review_cards:
            try:
                # Extract rating from star image
                rating_elem = card.find("div", {"data-service-review-rating": True})
                rating = None
                if rating_elem:
                    rating_val = rating_elem.get("data-service-review-rating")
                    rating = float(rating_val) if rating_val else None

                # Extract title
                title_elem = card.find("h2") or card.find("a", {"data-review-title-typography": True})
                title = title_elem.get_text(strip=True) if title_elem else None

                # Extract body
                body_elem = card.find("p", {"data-service-review-text-typography": True})
                if not body_elem:
                    body_elem = card.find("div", class_=lambda c: c and "reviewBody" in str(c))
                content = body_elem.get_text(strip=True) if body_elem else ""

                # Extract date
                time_elem = card.find("time")
                timestamp = time_elem.get("datetime", "") if time_elem else ""

                # Extract author
                author_elem = card.find("span", {"data-consumer-name-typography": True})
                author = author_elem.get_text(strip=True) if author_elem else ""

                if content:
                    reviews.append({
                        "content": f"{title}\n\n{content}".strip() if title else content,
                        "title": title,
                        "rating": rating,
                        "timestamp": timestamp,
                        "author": author,
                    })

            except Exception as e:
                continue

        return reviews

    def scrape(self, limit: Optional[int] = None) -> List[ScrapedDocument]:
        max_pages = self.config.get("max_pages", 100)
        target = limit or self.config.get("target_count", 5000)
        wait_time = self.config.get("wait_between_pages", 2)

        existing_ids = self.get_existing_source_ids()
        documents = []

        from tqdm import tqdm
        pbar = tqdm(total=target, desc="  Trustpilot", unit="reviews")

        consecutive_empty = 0
        for page in range(1, max_pages + 1):
            soup = self._fetch_page(page)
            if soup is None:
                break

            reviews = self._parse_reviews(soup)

            if not reviews:
                consecutive_empty += 1
                if consecutive_empty >= 3:
                    print(f"  ℹ️  3 consecutive empty pages — stopping")
                    break
                continue
            else:
                consecutive_empty = 0

            for i, review in enumerate(reviews):
                source_id = f"tp_p{page}_r{i}"
                if source_id in existing_ids:
                    continue

                doc = ScrapedDocument(
                    source="trustpilot",
                    source_type="secondary",
                    source_id=source_id,
                    author=anonymize_username(review["author"]),
                    content=review["content"],
                    title=review.get("title"),
                    rating=review.get("rating"),
                    timestamp=review.get("timestamp"),
                    url=f"{self.config['base_url']}?page={page}",
                    metadata={},
                )
                documents.append(doc)
                pbar.update(1)

            if len(documents) >= target:
                break

            # Random delay to avoid detection
            time.sleep(wait_time + random.uniform(0, 1))

        pbar.close()
        return documents

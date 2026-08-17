"""
Reviews.io scraper for Myntra reviews (secondary source).
Very thin presence — expected <1K reviews.
"""

import time
import random
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from pipeline.scrapers.base_scraper import BaseScraper, ScrapedDocument, anonymize_username, with_retry


class ReviewsIOScraper(BaseScraper):

    @property
    def source_name(self) -> str:
        return "reviewsio"

    @with_retry
    def _fetch_page(self, page: int) -> Optional[BeautifulSoup]:
        """Fetch a page of Reviews.io reviews."""
        url = self.config["base_url"]
        if page > 1:
            url = f"{url}?page={page}"

        response = requests.get(url, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
        })

        if response.status_code in (403, 404):
            return None

        response.raise_for_status()
        return BeautifulSoup(response.text, "lxml")

    def _parse_reviews(self, soup: BeautifulSoup, page: int) -> List[dict]:
        """Extract reviews from a Reviews.io page."""
        reviews = []

        # Try various selectors for review containers
        review_items = soup.find_all("div", class_=lambda c: c and "review" in str(c).lower())

        for item in review_items:
            try:
                # Body
                body_elem = item.find("p") or item.find("div", class_=lambda c: c and ("body" in str(c).lower() or "text" in str(c).lower()))
                content = body_elem.get_text(strip=True) if body_elem else ""

                if not content or len(content) < 10:
                    continue

                # Title
                title_elem = item.find("h3") or item.find("h4")
                title = title_elem.get_text(strip=True) if title_elem else None

                # Rating
                rating = None
                star_elem = item.find("div", class_=lambda c: c and "star" in str(c).lower())
                if star_elem:
                    try:
                        rating_text = star_elem.get("data-rating") or star_elem.get_text(strip=True)
                        rating = float(rating_text) if rating_text else None
                    except (ValueError, TypeError):
                        pass

                # Date
                date_elem = item.find("time") or item.find("span", class_=lambda c: c and "date" in str(c).lower())
                timestamp = date_elem.get("datetime", "") if date_elem else ""

                # Author
                author_elem = item.find("span", class_=lambda c: c and ("author" in str(c).lower() or "name" in str(c).lower()))
                author = author_elem.get_text(strip=True) if author_elem else ""

                reviews.append({
                    "content": f"{title}\n\n{content}".strip() if title else content,
                    "title": title,
                    "rating": rating,
                    "timestamp": timestamp,
                    "author": author,
                })

            except Exception:
                continue

        return reviews

    def scrape(self, limit: Optional[int] = None) -> List[ScrapedDocument]:
        max_pages = self.config.get("max_pages", 20)
        target = limit or self.config.get("target_count", 1000)
        wait_time = self.config.get("wait_between_pages", 2)

        documents = []

        from tqdm import tqdm
        pbar = tqdm(total=target, desc="  Reviews.io", unit="reviews")

        consecutive_empty = 0
        for page in range(1, max_pages + 1):
            soup = self._fetch_page(page)
            if soup is None:
                break

            reviews = self._parse_reviews(soup, page)

            if not reviews:
                consecutive_empty += 1
                if consecutive_empty >= 3:
                    break
                continue
            else:
                consecutive_empty = 0

            for i, review in enumerate(reviews):
                doc = ScrapedDocument(
                    source="reviewsio",
                    source_type="secondary",
                    source_id=f"rio_p{page}_r{i}",
                    author=anonymize_username(review.get("author", "")),
                    content=review["content"],
                    title=review.get("title"),
                    rating=review.get("rating"),
                    timestamp=review.get("timestamp"),
                    url=self.config["base_url"],
                    metadata={"page": page},
                )
                documents.append(doc)
                pbar.update(1)

            if len(documents) >= target:
                break

            time.sleep(wait_time + random.uniform(0, 1))

        pbar.close()
        return documents

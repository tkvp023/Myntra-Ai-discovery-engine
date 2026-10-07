"""
Google Play Store scraper for Myntra app reviews.
Uses google-play-scraper library (unofficial, no auth required).
"""

from typing import List, Optional

from pipeline.scrapers.base_scraper import BaseScraper, ScrapedDocument, anonymize_username, with_retry
from pipeline.scrapers.config import PLAYSTORE_CONFIG


class PlayStoreScraper(BaseScraper):

    @property
    def source_name(self) -> str:
        return "playstore"

    @with_retry
    def _fetch_reviews(self, continuation_token=None, count=200):
        """Fetch a batch of reviews from Google Play Store."""
        from google_play_scraper import reviews, Sort

        result, token = reviews(
            self.config["app_id"],
            lang=self.config.get("lang", "en"),
            country=self.config.get("country", "in"),
            sort=Sort.NEWEST,
            count=count,
            continuation_token=continuation_token,
        )
        return result, token

    def scrape(self, limit: Optional[int] = None) -> List[ScrapedDocument]:
        target = limit or self.config.get("count", 50000)
        batch_size = self.config.get("batch_size", 200)
        checkpoint_every = self.config.get("checkpoint_every", 5000)

        # Load existing source IDs to avoid re-scraping
        existing_ids = self.get_existing_source_ids()
        print(f"  📦 Found {len(existing_ids)} existing docs on disk")

        documents = []
        continuation_token = self.checkpoint.continuation_token
        batch_num = 0

        from tqdm import tqdm
        pbar = tqdm(total=target, desc=f"  Play Store", unit="reviews")
        pbar.update(len(existing_ids))

        while len(documents) + len(existing_ids) < target:
            try:
                result, continuation_token = self._fetch_reviews(
                    continuation_token=continuation_token,
                    count=min(batch_size, target - len(documents) - len(existing_ids)),
                )

                if not result:
                    print(f"  ℹ️  No more reviews available")
                    break

                for review in result:
                    review_id = review.get("reviewId", "")
                    if review_id in existing_ids:
                        continue

                    doc = ScrapedDocument(
                        source="playstore",
                        source_type="primary",
                        source_id=review_id,
                        author=anonymize_username(review.get("userName", "")),
                        content=review.get("content", ""),
                        title=None,
                        rating=review.get("score"),
                        timestamp=review.get("at", "").isoformat() if review.get("at") else None,
                        url=f"https://play.google.com/store/apps/details?id={self.config['app_id']}&reviewId={review_id}",
                        metadata={
                            "app_version": review.get("appVersion"),
                            "thumbs_up": review.get("thumbsUpCount", 0),
                            "reply_content": review.get("replyContent"),
                            "replied_at": review.get("repliedAt", "").isoformat() if review.get("repliedAt") else None,
                        },
                    )
                    documents.append(doc)
                    existing_ids.add(review_id)

                pbar.update(len(result))
                batch_num += 1

                # Save checkpoint periodically
                token_str = str(continuation_token.token) if hasattr(continuation_token, "token") else (str(continuation_token) if continuation_token else None)
                if len(documents) % checkpoint_every < batch_size:
                    self.save_checkpoint(
                        docs_scraped=len(documents) + len(existing_ids),
                        continuation_token=token_str,
                    )
                    # Save intermediate batch
                    if documents:
                        self.save_batch(documents[-checkpoint_every:], batch_num)

                if continuation_token is None:
                    print(f"  ℹ️  Reached end of reviews")
                    break

                self.rate_limit_sleep(0.5)

            except Exception as e:
                print(f"  ⚠️  Error fetching batch: {e}")
                token_str = str(continuation_token.token) if hasattr(continuation_token, "token") else (str(continuation_token) if continuation_token else None)
                self.save_checkpoint(
                    docs_scraped=len(documents),
                    continuation_token=token_str,
                    errors=self.checkpoint.errors + [str(e)],
                )
                break

        pbar.close()
        return documents

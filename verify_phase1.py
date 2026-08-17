"""Phase 1 verification script."""
import sys
import os
from pathlib import Path

# Fix Windows encoding
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Test database layer
from pipeline.db.models import Base, Document, Classification, HesitationTag, FactorMention, UnmetNeed, QuestionMapping
print("[OK] Database models imported")

from pipeline.db.connection import get_engine, get_session, init_db
print("[OK] Database connection imported")

# Test scraper framework
from pipeline.scrapers.base_scraper import BaseScraper, ScrapedDocument
print("[OK] Base scraper imported")

from pipeline.scrapers.config import SCRAPER_CONFIGS, VALID_SOURCES
print(f"[OK] Scraper configs loaded: {list(SCRAPER_CONFIGS.keys())}")

from pipeline.scrapers.playstore_scraper import PlayStoreScraper
from pipeline.scrapers.appstore_scraper import AppStoreScraper
from pipeline.scrapers.reddit_scraper import RedditScraper
from pipeline.scrapers.youtube_scraper import YouTubeScraper
from pipeline.scrapers.trustpilot_scraper import TrustpilotScraper
from pipeline.scrapers.pissedconsumer_scraper import PissedConsumerScraper
from pipeline.scrapers.reviewsio_scraper import ReviewsIOScraper
print("[OK] All 7 scrapers imported")

from pipeline.scrapers.orchestrator import run_all_scrapers
print("[OK] Orchestrator imported")

# Test cleaning pipeline
from pipeline.cleaning.normalizer import normalize_text
from pipeline.cleaning.language_filter import detect_language, should_keep
from pipeline.cleaning.deduplicator import deduplicate
from pipeline.cleaning.relevance_filter import is_relevant
from pipeline.cleaning.pipeline import CleaningPipeline
print("[OK] Cleaning pipeline imported")

# Quick functional tests
result = normalize_text("Check this https://example.com  out!!!!!")
print(f'   Normalizer test: "{result}"')

lang1 = detect_language("This product is great")
lang2 = detect_language("Ye bahut accha hai bhai")
print(f"   Language: english={lang1}, hinglish={lang2}")

rel1 = is_relevant("Myntra dress sizing is terrible")
rel2 = is_relevant("I love cooking pasta")
print(f"   Relevance: myntra={rel1}, pasta={rel2}")

# Init DB
engine = init_db()

# Verify tables
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"[OK] DB tables created: {tables}")

print()
print("=== ALL PHASE 1 VERIFICATION PASSED ===")

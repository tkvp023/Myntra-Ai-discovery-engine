"""
Abstract base class for all scrapers.
Provides: unified document schema, checkpoint/resume, retry logic, and file I/O.
"""

import json
import sys
import hashlib
import uuid
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from tqdm import tqdm

from pipeline.scrapers.config import PRIMARY_SOURCES


# ──────────────────────────────────────────────────────────
# Unified Document Schema
# ──────────────────────────────────────────────────────────

class ScrapedDocument(BaseModel):
    """Unified document schema — every scraped item is normalized into this format."""
    doc_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str                           # playstore, appstore, reddit, youtube, etc.
    source_type: str                      # primary or secondary
    source_id: Optional[str] = None       # original platform ID
    author: Optional[str] = None          # anonymized username
    content: str                          # raw text body
    title: Optional[str] = None           # reddit post title, video title, etc.
    rating: Optional[float] = None        # 1-5 for app stores, None for reddit/youtube
    timestamp: Optional[str] = None       # ISO-8601
    url: Optional[str] = None             # permalink to original
    metadata: Dict[str, Any] = Field(default_factory=dict)
    scraped_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return self.model_dump()


# ──────────────────────────────────────────────────────────
# Checkpoint System
# ──────────────────────────────────────────────────────────

class Checkpoint(BaseModel):
    """Checkpoint state for resumable scraping."""
    scraper: str
    last_checkpoint: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    docs_scraped: int = 0
    continuation_token: Optional[str] = None
    status: str = "not_started"           # not_started, in_progress, completed, failed
    errors: List[str] = Field(default_factory=list)
    extra: Dict[str, Any] = Field(default_factory=dict)


# ──────────────────────────────────────────────────────────
# Retry Decorator
# ──────────────────────────────────────────────────────────

def with_retry(func):
    """Decorator: retry with exponential backoff on network/rate-limit errors."""
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, OSError)),
        reraise=True,
    )(func)


# ──────────────────────────────────────────────────────────
# Anonymization
# ──────────────────────────────────────────────────────────

def anonymize_username(username: str) -> str:
    """Hash username for privacy — deterministic so same user maps to same anon ID."""
    if not username or username == "[deleted]":
        return "anon_deleted"
    return f"anon_{hashlib.sha256(username.encode()).hexdigest()[:12]}"


# ──────────────────────────────────────────────────────────
# Base Scraper
# ──────────────────────────────────────────────────────────

class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.
    
    Subclasses must implement:
        - scrape(limit) -> List[ScrapedDocument]
        - source_name (property)
    """

    def __init__(self, config: dict, data_dir: Path = None):
        self.config = config
        self.data_dir = data_dir or Path(__file__).resolve().parent.parent.parent / "data"
        self.raw_dir = self.data_dir / "raw" / self.source_name
        self.checkpoint_dir = self.data_dir / "checkpoints"
        self.documents: List[ScrapedDocument] = []
        self._checkpoint: Optional[Checkpoint] = None

        # Ensure directories exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the source name (e.g., 'playstore', 'reddit')."""
        ...

    @property
    def source_type(self) -> str:
        """Return 'primary' or 'secondary' based on source name."""
        return "primary" if self.source_name in PRIMARY_SOURCES else "secondary"

    @abstractmethod
    def scrape(self, limit: Optional[int] = None) -> List[ScrapedDocument]:
        """
        Scrape documents from the source.
        
        Args:
            limit: Optional max number of documents to scrape (for testing).
                   If None, scrapes up to config target.
        
        Returns:
            List of ScrapedDocument objects.
        """
        ...

    # ── Checkpoint Management ──

    def load_checkpoint(self) -> Optional[Checkpoint]:
        """Load checkpoint from disk if it exists."""
        path = self.checkpoint_dir / f"{self.source_name}_checkpoint.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                self._checkpoint = Checkpoint(**json.load(f))
                return self._checkpoint
        return None

    def save_checkpoint(self, **kwargs):
        """Save current checkpoint to disk."""
        if self._checkpoint is None:
            self._checkpoint = Checkpoint(scraper=self.source_name)
        
        for key, value in kwargs.items():
            if hasattr(self._checkpoint, key):
                setattr(self._checkpoint, key, value)
        
        self._checkpoint.last_checkpoint = datetime.now(timezone.utc).isoformat()
        
        path = self.checkpoint_dir / f"{self.source_name}_checkpoint.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._checkpoint.model_dump(), f, indent=2)

    @property
    def checkpoint(self) -> Checkpoint:
        """Get current checkpoint, loading from disk if needed."""
        if self._checkpoint is None:
            loaded = self.load_checkpoint()
            if loaded is None:
                self._checkpoint = Checkpoint(scraper=self.source_name)
        return self._checkpoint

    # ── File I/O ──

    def save_batch(self, docs: List[ScrapedDocument], batch_num: int):
        """Save a batch of documents to a JSON file."""
        path = self.raw_dir / f"batch_{batch_num:04d}.json"
        data = [doc.to_dict() for doc in docs]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return path

    def save_csv(self):
        """Save all documents to a human-readable CSV file in the source directory."""
        import csv
        csv_path = self.raw_dir / f"{self.source_name}_reviews.csv"
        all_docs = self.load_existing_docs()
        if not all_docs:
            all_docs = self.documents
            
        fieldnames = ["source", "source_type", "date", "rating", "author", "title", "content", "url", "metadata"]
        try:
            with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
                writer.writeheader()
                for doc in all_docs:
                    writer.writerow({
                        "source": doc.source,
                        "source_type": doc.source_type,
                        "date": doc.timestamp[:10] if doc.timestamp else "",
                        "rating": doc.rating if doc.rating is not None else "",
                        "author": doc.author or "",
                        "title": doc.title or "",
                        "content": doc.content,
                        "url": doc.url or "",
                        "metadata": json.dumps(doc.metadata) if doc.metadata else "",
                    })
            print(f"  📄 Human-readable CSV saved to {csv_path}")
        except Exception as e:
            print(f"  ⚠️ CSV export error: {e}")

    def save_all(self):
        """Save all collected documents in batches of 500 and export human-readable CSV."""
        batch_size = 500
        for i in range(0, len(self.documents), batch_size):
            batch = self.documents[i:i + batch_size]
            batch_num = i // batch_size + 1
            self.save_batch(batch, batch_num)
        
        print(f"  💾 Saved {len(self.documents)} documents to {self.raw_dir}")
        self.save_csv()

    def load_existing_docs(self) -> List[ScrapedDocument]:
        """Load all previously scraped documents from disk."""
        docs = []
        for path in sorted(self.raw_dir.glob("batch_*.json")):
            with open(path, "r", encoding="utf-8") as f:
                batch = json.load(f)
                docs.extend([ScrapedDocument(**d) for d in batch])
        return docs

    def get_existing_source_ids(self) -> set:
        """Get set of already-scraped source IDs (for dedup during scraping)."""
        existing = self.load_existing_docs()
        return {d.source_id for d in existing if d.source_id}

    # ── Utilities ──

    def rate_limit_sleep(self, seconds: float = 1.0):
        """Sleep to respect rate limits."""
        time.sleep(seconds)

    def run(self, limit: Optional[int] = None) -> List[ScrapedDocument]:
        """
        Full scrape pipeline: load checkpoint → scrape → save → update checkpoint.
        """
        print(f"\n{'='*60}")
        print(f"🔍 Starting {self.source_name} scraper ({self.source_type})")
        print(f"{'='*60}")

        # Load checkpoint
        self.load_checkpoint()
        if self.checkpoint.status == "completed":
            existing = self.load_existing_docs()
            print(f"  ✅ Already completed — {len(existing)} docs on disk. Skipping.")
            return existing

        try:
            # Scrape
            self.checkpoint.status = "in_progress"
            self.save_checkpoint(status="in_progress")
            
            docs = self.scrape(limit=limit)
            self.documents = docs

            # Save
            if docs:
                self.save_all()

            # Update checkpoint
            self.save_checkpoint(
                status="completed",
                docs_scraped=len(docs),
            )

            print(f"  ✅ Completed: {len(docs)} documents scraped")
            return docs

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"  ❌ Error: {error_msg}")
            self.save_checkpoint(
                status="failed",
                errors=self.checkpoint.errors + [error_msg],
            )
            # Save whatever we have so far
            if self.documents:
                self.save_all()
                print(f"  💾 Saved {len(self.documents)} docs before failure")
            return self.documents

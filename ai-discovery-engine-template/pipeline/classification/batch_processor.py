"""
Batch processor — loads clean docs, classifies in batches of 10,
stores results in SQLite DB, supports checkpoint/resume.
"""

import json
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict

from tqdm import tqdm

from pipeline.classification.classifier import TieredClassifier
from pipeline.classification.validator import validate_batch
from pipeline.classification.schema import empty_classification


# ──────────────────────────────────────────────────────────
# Batch Processor
# ──────────────────────────────────────────────────────────

class BatchProcessor:
    """
    Loads clean documents → classifies in batches → validates → stores in DB.
    Supports checkpoint/resume, rate limiting, and per-tier stats.
    """

    def __init__(
        self,
        data_dir: Path = None,
        batch_size: int = 10,
        rate_limit_rpm: int = 10,       # Requests per minute (conservative for free tier)
        preferred_tier: Optional[str] = None,
        checkpoint_every: int = 100,    # Save checkpoint every N docs
    ):
        self.data_dir = data_dir or Path(__file__).resolve().parent.parent.parent / "data"
        self.clean_dir = self.data_dir / "clean"
        self.classified_dir = self.data_dir / "classified"
        self.checkpoint_dir = self.data_dir / "checkpoints"
        self.classified_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.batch_size = batch_size
        self.rate_limit_rpm = rate_limit_rpm
        self.seconds_per_request = 60.0 / rate_limit_rpm
        self.preferred_tier = preferred_tier
        self.checkpoint_every = checkpoint_every

        self.classifier = TieredClassifier()
        self.stats = {
            "total_docs": 0,
            "classified": 0,
            "skipped": 0,
            "errors": 0,
            "validation_errors": 0,
            "started_at": None,
            "elapsed_seconds": 0,
        }

    # ── Data Loading ──

    def load_clean_docs(self, sources: Optional[List[str]] = None) -> List[dict]:
        """Load all clean documents from data/clean/."""
        docs = []
        if not self.clean_dir.exists():
            print("  [!] No clean data found. Run cleaning pipeline first.")
            return docs

        for batch_file in sorted(self.clean_dir.glob("clean_batch_*.json")):
            try:
                with open(batch_file, "r", encoding="utf-8") as f:
                    batch = json.load(f)
                    if sources:
                        batch = [d for d in batch if d.get("source") in sources]
                    docs.extend(batch)
            except Exception as e:
                print(f"  [!] Error reading {batch_file.name}: {e}")
        return docs

    def load_from_db(self, sources: Optional[List[str]] = None) -> List[dict]:
        """Load clean documents from SQLite DB."""
        from pipeline.db.connection import get_session
        from pipeline.db.models import Document

        session = get_session()
        try:
            query = session.query(Document)
            if sources:
                query = query.filter(Document.source.in_(sources))
            docs = [
                {
                    "doc_id": d.doc_id,
                    "content": d.content,
                    "source": d.source,
                    "source_type": d.source_type,
                }
                for d in query.all()
            ]
            return docs
        finally:
            session.close()

    # ── Checkpoint Management ──

    def _checkpoint_path(self) -> Path:
        return self.checkpoint_dir / "classification_checkpoint.json"

    def load_checkpoint(self) -> set:
        """Load set of already-classified doc IDs."""
        path = self._checkpoint_path()
        if path.exists():
            with open(path, "r") as f:
                data = json.load(f)
                return set(data.get("classified_ids", []))
        return set()

    def save_checkpoint(self, classified_ids: set):
        """Save checkpoint of classified doc IDs."""
        path = self._checkpoint_path()
        with open(path, "w") as f:
            json.dump({
                "classified_ids": list(classified_ids),
                "count": len(classified_ids),
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "stats": self.stats,
            }, f, indent=2)

    # ── DB Storage ──

    def store_classifications(self, results: List[dict]):
        """Store classification results in SQLite DB."""
        from pipeline.db.connection import get_session, init_db
        from pipeline.db.models import (
            Classification as DBClassification,
            HesitationTag, FactorMention, UnmetNeed, QuestionMapping,
        )

        init_db()
        session = get_session()

        try:
            for result in results:
                doc_id = result.get("doc_id", "")
                cls = result.get("classification", {})
                if not cls or not doc_id:
                    continue

                now = datetime.now(timezone.utc).isoformat()
                seg = cls.get("user_segment_signals", {})
                comp = cls.get("comparison_behavior", {})
                ext = cls.get("external_info_seeking", {})

                # Upsert Classification row
                existing = session.query(DBClassification).filter_by(doc_id=doc_id).first()
                if existing:
                    session.delete(existing)

                db_cls = DBClassification(
                    doc_id=doc_id,
                    wishlist_intent=cls.get("wishlist_intent", "unknown"),
                    inferred_age_group=seg.get("inferred_age_group", "unknown"),
                    price_sensitivity=seg.get("price_sensitivity", "unknown"),
                    fashion_engagement=seg.get("fashion_engagement", "unknown"),
                    gender_signal=seg.get("gender_signal", "unknown"),
                    compares_across=comp.get("compares_across_platforms", False),
                    seeks_external_info=ext.get("seeks_external_info", False),
                    is_primary_signal=cls.get("is_primary_signal", False),
                    raw_classification=json.dumps(cls),
                    classified_at=now,
                )
                session.add(db_cls)

                # Delete existing child rows
                session.query(HesitationTag).filter_by(doc_id=doc_id).delete()
                session.query(FactorMention).filter_by(doc_id=doc_id).delete()
                session.query(UnmetNeed).filter_by(doc_id=doc_id).delete()
                session.query(QuestionMapping).filter_by(doc_id=doc_id).delete()

                # Add hesitation tags
                for reason in cls.get("hesitation_reasons", []):
                    session.add(HesitationTag(
                        doc_id=doc_id,
                        reason=reason.get("reason", "other"),
                        confidence=reason.get("confidence", 0.5),
                        evidence_quote=reason.get("evidence_quote", ""),
                    ))

                # Add factor mentions
                for factor_name, factor_data in cls.get("factor_mentions", {}).items():
                    if factor_data.get("mentioned", False):
                        session.add(FactorMention(
                            doc_id=doc_id,
                            factor=factor_name,
                            mentioned=True,
                            sentiment=factor_data.get("sentiment", "neutral"),
                        ))

                # Add unmet needs
                for need in cls.get("unmet_needs", []):
                    if need:
                        session.add(UnmetNeed(doc_id=doc_id, need_text=str(need)))

                # Add question mappings
                for q_id in cls.get("brief_question_mapping", []):
                    session.add(QuestionMapping(doc_id=doc_id, question_id=int(q_id)))

            session.commit()

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def save_classified_batch(self, results: List[dict], batch_num: int):
        """Save classified results to JSON for backup."""
        path = self.classified_dir / f"classified_batch_{batch_num:04d}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    # ── Main Processing ──

    def run(
        self,
        sources: Optional[List[str]] = None,
        limit: Optional[int] = None,
        use_db: bool = True,
    ) -> dict:
        """
        Run the full classification batch processing pipeline.

        Args:
            sources: Optional source filter.
            limit: Max docs to classify (for testing).
            use_db: Whether to load from/store to DB (True) or use JSON files.

        Returns:
            Final stats dict.
        """
        print(f"\n{'='*60}")
        print(f"[*] Phase 2 — LLM Classification Pipeline")
        print(f"{'='*60}")
        print(f"  Batch size:      {self.batch_size} docs")
        print(f"  Rate limit:      {self.rate_limit_rpm} RPM ({self.seconds_per_request:.1f}s/batch)")
        print(f"  Preferred tier:  {self.preferred_tier or 'auto'}")

        # Load documents
        print(f"\n  Loading clean documents...")
        if use_db:
            docs = self.load_from_db(sources=sources)
        else:
            docs = self.load_clean_docs(sources=sources)

        if not docs:
            print("  [!] No documents found.")
            return self.stats

        if limit:
            docs = docs[:limit]

        print(f"  Loaded {len(docs):,} documents")

        # Load checkpoint
        classified_ids = self.load_checkpoint()
        docs_to_classify = [d for d in docs if d.get("doc_id") not in classified_ids]
        print(f"  Already classified: {len(classified_ids):,}")
        print(f"  Remaining:          {len(docs_to_classify):,}")

        if not docs_to_classify:
            print("  [*] All documents already classified!")
            return self.stats

        # Show available tiers
        available = self.classifier.get_available_tiers()
        print(f"  Available tiers: {available}")
        print(f"{'='*60}\n")

        self.stats["total_docs"] = len(docs_to_classify)
        self.stats["started_at"] = datetime.now(timezone.utc).isoformat()
        start_time = time.time()

        batch_num = 0
        pbar = tqdm(total=len(docs_to_classify), desc="  Classifying", unit="docs")

        for i in range(0, len(docs_to_classify), self.batch_size):
            batch = docs_to_classify[i:i + self.batch_size]
            batch_num += 1

            try:
                # Classify
                batch_start = time.time()
                raw_results, tier_used, error = self.classifier.classify_batch(
                    batch, preferred_tier=self.preferred_tier
                )

                if error and not raw_results:
                    print(f"\n  [!] Batch {batch_num} failed: {error}")
                    self.stats["errors"] += len(batch)
                    pbar.update(len(batch))
                    continue

                # Validate
                validated, val_stats = validate_batch(batch, raw_results)
                self.stats["validation_errors"] += val_stats.get("total_errors", 0)

                # Store in DB
                if use_db and validated:
                    self.store_classifications(validated)

                # Save JSON backup
                self.save_classified_batch(validated, batch_num)

                # Update classified IDs
                for doc in batch:
                    classified_ids.add(doc.get("doc_id", ""))

                self.stats["classified"] += len(validated)
                pbar.update(len(batch))

                # Save checkpoint periodically
                if len(classified_ids) % self.checkpoint_every < self.batch_size:
                    self.save_checkpoint(classified_ids)

                # Rate limiting
                elapsed_this_batch = time.time() - batch_start
                sleep_time = max(0, self.seconds_per_request - elapsed_this_batch)
                if sleep_time > 0:
                    time.sleep(sleep_time)

            except Exception as e:
                print(f"\n  [!] Batch {batch_num} error: {e}")
                traceback.print_exc()
                self.stats["errors"] += len(batch)
                pbar.update(len(batch))
                self.save_checkpoint(classified_ids)
                continue

        pbar.close()

        # Final checkpoint
        self.save_checkpoint(classified_ids)

        # Final stats
        self.stats["elapsed_seconds"] = round(time.time() - start_time, 1)
        self.stats.update(self.classifier.get_stats())

        self._print_summary()
        return self.stats

    def _print_summary(self):
        s = self.stats
        print(f"\n{'='*60}")
        print(f"[*] Classification Complete")
        print(f"{'='*60}")
        print(f"  Total docs:          {s['total_docs']:>8,}")
        print(f"  Classified:          {s['classified']:>8,}")
        print(f"  Errors:              {s['errors']:>8,}")
        print(f"  Validation errors:   {s['validation_errors']:>8,}")
        print(f"  Gemini calls:        {s.get('gemini_calls', 0):>8,}")
        print(f"  Groq calls:          {s.get('groq_calls', 0):>8,}")
        print(f"  Ollama calls:        {s.get('ollama_calls', 0):>8,}")
        print(f"  Keyword calls:       {s.get('keyword_calls', 0):>8,}")
        print(f"  Failovers:           {s.get('failovers', 0):>8,}")
        print(f"  Elapsed:             {s['elapsed_seconds']}s")
        print(f"{'='*60}\n")

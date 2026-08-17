"""
Embedder & Indexer — indexes all 8,182 clean documents from SQLite into VectorStore.

Usage:
    python -m pipeline.rag.embedder
"""

import sys
import os
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.db.connection import get_session, init_db
from pipeline.db.models import Document, Classification, HesitationTag, QuestionMapping
from pipeline.rag.vector_store import VectorStore


def build_index(reset: bool = False):
    """Index all clean documents from the database into VectorStore."""
    print("=" * 60)
    print("🧠 Phase 5.1 — Indexing Clean Corpus into VectorStore")
    print("=" * 60)

    # 1. Load documents from DB
    init_db()
    session = get_session()
    docs = session.query(Document).all()
    print(f"  📄 Loaded {len(docs):,} documents from database")

    # 2. Load classifications for metadata
    print("  🏷️  Loading classification metadata...")
    classifications = {}
    for cls in session.query(Classification).all():
        classifications[cls.doc_id] = cls

    hesitation_map = {}
    for ht in session.query(HesitationTag).all():
        hesitation_map.setdefault(ht.doc_id, []).append(ht.reason)

    question_map = {}
    for qm in session.query(QuestionMapping).all():
        question_map.setdefault(qm.doc_id, []).append(qm.question_id)

    # 3. Assemble documents & metadata
    doc_ids = []
    documents = []
    metadatas = []

    for d in docs:
        cls = classifications.get(d.doc_id)
        tags = hesitation_map.get(d.doc_id, [])
        questions = question_map.get(d.doc_id, [])

        meta = {
            "source": d.source or "unknown",
            "source_id": str(d.source_id or ""),
            "timestamp": str(d.timestamp or "")[:10],
            "rating": float(d.rating) if d.rating else 0.0,
            "content_preview": (d.content or "")[:500],
            "hesitation_tags": ",".join(tags[:5]) if tags else "",
            "question_ids": ",".join(str(q) for q in sorted(set(questions))) if questions else "",
        }
        if cls:
            meta["segment"] = cls.inferred_age_group or "unknown"
            meta["wishlist_intent"] = cls.wishlist_intent or "unknown"
            meta["price_sensitivity"] = cls.price_sensitivity or "unknown"
            meta["is_primary_signal"] = str(cls.is_primary_signal or False)
        else:
            meta["segment"] = "unknown"
            meta["wishlist_intent"] = "unknown"
            meta["price_sensitivity"] = "unknown"
            meta["is_primary_signal"] = "False"

        doc_ids.append(d.doc_id)
        documents.append(d.content or "No content")
        metadatas.append(meta)

    session.close()

    # 4. Build and save index
    store = VectorStore()
    store.build_and_save(doc_ids, documents, metadatas)

    print(f"\n  ✅ Indexing complete!")
    print(f"  📊 VectorStore contains {store.count():,} indexed documents with full metadata.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Index clean corpus into VectorStore")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    build_index(reset=args.reset)

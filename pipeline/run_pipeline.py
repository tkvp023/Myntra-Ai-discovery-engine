"""
AI Discovery Engine — Pipeline Entry Point

Usage:
    python run_pipeline.py --mode scrape [--sources playstore,reddit] [--limit 100]
    python run_pipeline.py --mode clean [--sources playstore,reddit]
    python run_pipeline.py --mode classify [--limit 100] [--tier gemini]
    python run_pipeline.py --mode full [--limit 100]
    python run_pipeline.py --mode stats
    python run_pipeline.py --mode init-db
"""

import argparse
import sys
import json
from pathlib import Path

# Fix Windows console encoding for emojis and multilingual text
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")


def cmd_init_db():
    """Initialize the database — create all tables."""
    from pipeline.db.connection import init_db
    init_db()


def cmd_scrape(sources=None, limit=None, parallel=True):
    """Run scrapers."""
    from pipeline.scrapers.orchestrator import run_all_scrapers

    report = run_all_scrapers(
        sources=sources,
        limit=limit,
        parallel=parallel,
    )
    return report


def cmd_clean(sources=None):
    """Run the cleaning pipeline."""
    from pipeline.cleaning.pipeline import CleaningPipeline

    pipeline = CleaningPipeline()
    clean_docs = pipeline.run(sources=sources)
    return clean_docs


def cmd_insert_to_db():
    """Insert clean documents into the SQLite database."""
    from pipeline.db.connection import get_session, init_db
    from pipeline.db.models import Document

    # Ensure tables exist
    init_db()

    session = get_session()
    data_dir = PROJECT_ROOT / "data" / "clean"

    if not data_dir.exists():
        print("❌ No clean data found. Run 'clean' mode first.")
        return

    total = 0
    skipped = 0

    for batch_file in sorted(data_dir.glob("clean_batch_*.json")):
        with open(batch_file, "r", encoding="utf-8") as f:
            batch = json.load(f)

        for doc_data in batch:
            doc_id = doc_data.get("doc_id")

            # Check if already exists
            existing = session.query(Document).filter_by(doc_id=doc_id).first()
            if existing:
                skipped += 1
                continue

            doc = Document(
                doc_id=doc_id,
                source=doc_data.get("source"),
                source_type=doc_data.get("source_type"),
                source_id=doc_data.get("source_id"),
                content=doc_data.get("content"),
                title=doc_data.get("title"),
                rating=doc_data.get("rating"),
                timestamp=doc_data.get("timestamp"),
                url=doc_data.get("url"),
                metadata_json=json.dumps(doc_data.get("metadata", {})),
                scraped_at=doc_data.get("scraped_at"),
                author=doc_data.get("author"),
            )
            session.add(doc)
            total += 1

        # Commit per batch file
        session.commit()

    session.close()
    print(f"\n✅ Inserted {total:,} documents into database (skipped {skipped:,} existing)")


def cmd_stats():
    """Show current data statistics."""
    data_dir = PROJECT_ROOT / "data"

    print(f"\n{'='*60}")
    print(f"📊 Data Statistics")
    print(f"{'='*60}")

    # Raw data
    raw_dir = data_dir / "raw"
    if raw_dir.exists():
        print(f"\n  📂 Raw Data ({raw_dir}):")
        for source_dir in sorted(raw_dir.iterdir()):
            if source_dir.is_dir():
                count = 0
                for batch_file in source_dir.glob("batch_*.json"):
                    try:
                        with open(batch_file) as f:
                            count += len(json.load(f))
                    except Exception:
                        pass
                print(f"     {source_dir.name:20s} → {count:>8,} docs")
    else:
        print(f"\n  ⚠️  No raw data found")

    # Clean data
    clean_dir = data_dir / "clean"
    if clean_dir.exists():
        clean_count = 0
        for batch_file in clean_dir.glob("clean_batch_*.json"):
            try:
                with open(batch_file) as f:
                    clean_count += len(json.load(f))
            except Exception:
                pass
        print(f"\n  🧹 Clean Data: {clean_count:,} documents")
    else:
        print(f"\n  ⚠️  No clean data found")

    # Cleaning stats
    stats_file = data_dir / "cleaning_stats.json"
    if stats_file.exists():
        with open(stats_file) as f:
            stats = json.load(f)
        print(f"\n  📈 Cleaning Stats:")
        print(f"     Retention rate: {stats.get('retention_rate', 'N/A')}%")
        print(f"     Language dropped: {stats.get('language_dropped', 'N/A')}")
        print(f"     Relevance dropped: {stats.get('relevance_dropped', 'N/A')}")
        print(f"     Dedup removed: {stats.get('dedup_stats', {}).get('total_removed', 'N/A')}")

    # Database
    db_path = data_dir / "db.sqlite"
    if db_path.exists():
        from pipeline.db.connection import get_session
        from pipeline.db.models import Document
        session = get_session()
        db_count = session.query(Document).count()
        session.close()
        print(f"\n  🗄️  Database: {db_count:,} documents")
    else:
        print(f"\n  ⚠️  Database not initialized")

    # Checkpoints
    checkpoint_dir = data_dir / "checkpoints"
    if checkpoint_dir.exists():
        print(f"\n  🔖 Checkpoints:")
        for cp_file in sorted(checkpoint_dir.glob("*_checkpoint.json")):
            try:
                with open(cp_file) as f:
                    cp = json.load(f)
                name = cp_file.stem.replace("_checkpoint", "")
                print(f"     {name:20s} → {cp.get('status', 'unknown'):12s} ({cp.get('docs_scraped', 0):,} docs)")
            except Exception:
                pass

    print(f"\n{'='*60}\n")


def cmd_classify(sources=None, limit=None, tier=None, batch_size=10, rpm=10):
    """Run Phase 2 — LLM classification on clean corpus."""
    from pipeline.classification.batch_processor import BatchProcessor

    processor = BatchProcessor(
        batch_size=batch_size,
        rate_limit_rpm=rpm,
        preferred_tier=tier,
    )
    return processor.run(sources=sources, limit=limit, use_db=True)


def cmd_classify_stats():
    """Show classification progress stats."""
    from pipeline.db.connection import get_session
    from pipeline.db.models import Classification, Document, HesitationTag

    session = get_session()
    try:
        total_docs = session.query(Document).count()
        classified = session.query(Classification).count()
        primary_signal = session.query(Classification).filter_by(is_primary_signal=True).count()
        total_tags = session.query(HesitationTag).count()

        print(f"\n{'='*60}")
        print(f"[*] Classification Stats")
        print(f"{'='*60}")
        print(f"  Total documents:   {total_docs:>8,}")
        print(f"  Classified:        {classified:>8,}")
        print(f"  Unclassified:      {total_docs - classified:>8,}")
        print(f"  Primary signal:    {primary_signal:>8,}")
        print(f"  Total tags:        {total_tags:>8,}")
        if classified > 0:
            print(f"  Progress:          {classified/total_docs*100:.1f}%")
        print(f"{'='*60}\n")
    finally:
        session.close()


def cmd_full(sources=None, limit=None):
    """Run full pipeline: scrape → clean → classify → insert to DB."""
    print("\n[*] Running full pipeline: scrape -> clean -> classify\n")

    # Step 1: Scrape
    cmd_scrape(sources=sources, limit=limit)

    # Step 2: Clean
    cmd_clean(sources=sources)

    # Step 3: Insert to DB
    cmd_insert_to_db()

    # Step 4: Classify
    cmd_classify(sources=sources, limit=limit)

    # Step 5: Show stats
    cmd_stats()

    # Step 6: Export JSON
    cmd_export()

    print("[*] Full pipeline complete!")


def cmd_export(output_dir=None, no_dashboard_copy=False):
    """Run Phase 3 — quantification & JSON export."""
    from pathlib import Path
    from pipeline.quantification.export import run_export
    out = Path(output_dir) if output_dir else None
    run_export(output_dir=out, copy_to_dashboard=not no_dashboard_copy)


def main():
    parser = argparse.ArgumentParser(
        description="AI Discovery Engine — Pipeline CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py --mode init-db
  python run_pipeline.py --mode scrape --sources playstore --limit 100
  python run_pipeline.py --mode scrape --sources playstore,appstore,reddit
  python run_pipeline.py --mode clean
  python run_pipeline.py --mode full --limit 50
  python run_pipeline.py --mode stats
        """,
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["scrape", "clean", "classify", "classify-stats", "export", "embed", "rag-server", "full", "stats", "init-db", "insert-db"],
        help="Pipeline mode to run",
    )
    parser.add_argument("--reset", action="store_true", help="Reset/rebuild vector index during embedding")
    parser.add_argument("--output-dir", type=str, default=None, help="Custom output directory for JSON export")
    parser.add_argument("--no-dashboard-copy", action="store_true", help="Skip copying exports to dashboard/public/data/")
    parser.add_argument(
        "--tier",
        type=str,
        default=None,
        choices=["gemini", "groq", "ollama", "keyword"],
        help="Preferred LLM tier for classification (default: auto-failover)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Docs per classification batch (default: 10)",
    )
    parser.add_argument(
        "--rpm",
        type=int,
        default=10,
        help="Max API requests per minute (default: 10)",
    )
    parser.add_argument(
        "--sources",
        type=str,
        default=None,
        help="Comma-separated list of sources (e.g., playstore,reddit). Default: all",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max documents per scraper (for testing). Default: full scrape",
    )
    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Run scrapers sequentially instead of in parallel",
    )

    args = parser.parse_args()

    # Parse sources
    sources = None
    if args.sources:
        sources = [s.strip() for s in args.sources.split(",")]

    # Run the requested mode
    if args.mode == "init-db":
        cmd_init_db()
    elif args.mode == "scrape":
        cmd_scrape(sources=sources, limit=args.limit, parallel=not args.no_parallel)
    elif args.mode == "clean":
        cmd_clean(sources=sources)
    elif args.mode == "insert-db":
        cmd_insert_to_db()
    elif args.mode == "classify":
        cmd_classify(
            sources=sources,
            limit=args.limit,
            tier=args.tier,
            batch_size=args.batch_size,
            rpm=args.rpm,
        )
    elif args.mode == "classify-stats":
        cmd_classify_stats()
    elif args.mode == "export":
        cmd_export(
            output_dir=getattr(args, 'output_dir', None),
            no_dashboard_copy=getattr(args, 'no_dashboard_copy', False),
        )
    elif args.mode == "embed":
        from pipeline.rag.embedder import build_index
        build_index(reset=getattr(args, 'reset', False))
    elif args.mode == "rag-server":
        import uvicorn
        uvicorn.run("pipeline.rag.server:app", host="0.0.0.0", port=8000, reload=False)
    elif args.mode == "full":
        cmd_full(sources=sources, limit=args.limit)
    elif args.mode == "stats":
        cmd_stats()


if __name__ == "__main__":
    main()

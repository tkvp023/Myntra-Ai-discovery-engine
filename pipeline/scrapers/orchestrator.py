"""
Scraper orchestrator — runs all scrapers with parallel execution,
error handling, and aggregate statistics.
"""

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from pipeline.scrapers.base_scraper import BaseScraper, ScrapedDocument
from pipeline.scrapers.config import (
    SCRAPER_CONFIGS, PRIMARY_SOURCES, SECONDARY_SOURCES,
    PLAYSTORE_CONFIG, APPSTORE_CONFIG, REDDIT_CONFIG, YOUTUBE_CONFIG,
    TRUSTPILOT_CONFIG, PISSEDCONSUMER_CONFIG, REVIEWSIO_CONFIG,
)
from pipeline.scrapers.playstore_scraper import PlayStoreScraper
from pipeline.scrapers.appstore_scraper import AppStoreScraper
from pipeline.scrapers.reddit_scraper import RedditScraper
from pipeline.scrapers.youtube_scraper import YouTubeScraper
from pipeline.scrapers.trustpilot_scraper import TrustpilotScraper
from pipeline.scrapers.pissedconsumer_scraper import PissedConsumerScraper
from pipeline.scrapers.reviewsio_scraper import ReviewsIOScraper


# Map source names to scraper classes and configs
SCRAPER_REGISTRY = {
    "playstore":       (PlayStoreScraper,       PLAYSTORE_CONFIG),
    "appstore":        (AppStoreScraper,        APPSTORE_CONFIG),
    "reddit":          (RedditScraper,          REDDIT_CONFIG),
    "youtube":         (YouTubeScraper,         YOUTUBE_CONFIG),
    "trustpilot":      (TrustpilotScraper,      TRUSTPILOT_CONFIG),
    "pissedconsumer":  (PissedConsumerScraper,   PISSEDCONSUMER_CONFIG),
    "reviewsio":       (ReviewsIOScraper,       REVIEWSIO_CONFIG),
}


def run_scraper(
    source_name: str,
    limit: Optional[int] = None,
    data_dir: Path = None,
) -> Dict:
    """Run a single scraper and return results summary."""
    if source_name not in SCRAPER_REGISTRY:
        return {"source": source_name, "status": "error", "error": f"Unknown source: {source_name}", "count": 0}

    ScraperClass, config = SCRAPER_REGISTRY[source_name]

    try:
        scraper = ScraperClass(config=config, data_dir=data_dir)
        docs = scraper.run(limit=limit)
        return {
            "source": source_name,
            "status": "completed",
            "count": len(docs),
            "error": None,
        }
    except Exception as e:
        return {
            "source": source_name,
            "status": "failed",
            "count": 0,
            "error": f"{type(e).__name__}: {str(e)}",
        }


def run_all_scrapers(
    sources: Optional[List[str]] = None,
    limit: Optional[int] = None,
    parallel: bool = True,
    max_workers: int = 3,
    data_dir: Path = None,
) -> Dict:
    """
    Run multiple scrapers.
    
    Args:
        sources: List of source names to run. If None, runs all.
        limit: Optional per-scraper document limit (for testing).
        parallel: Whether to run scrapers in parallel (True) or sequential.
        max_workers: Max parallel threads.
        data_dir: Override data directory.
    
    Returns:
        Aggregate results dict with per-source statistics.
    """
    if sources is None:
        sources = list(SCRAPER_REGISTRY.keys())

    print(f"\n{'='*60}")
    print(f"🚀 AI Discovery Engine — Scraping Orchestrator")
    print(f"{'='*60}")
    print(f"  Sources: {', '.join(sources)}")
    print(f"  Mode: {'parallel' if parallel else 'sequential'} (limit={limit or 'full'})")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    start_time = time.time()
    results = []

    if parallel and len(sources) > 1:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(run_scraper, source, limit, data_dir): source
                for source in sources
            }
            for future in as_completed(futures):
                source = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        "source": source,
                        "status": "failed",
                        "count": 0,
                        "error": str(e),
                    })
    else:
        for source in sources:
            result = run_scraper(source, limit, data_dir)
            results.append(result)

    elapsed = time.time() - start_time

    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 Scraping Complete — Summary")
    print(f"{'='*60}")

    total_docs = 0
    for r in sorted(results, key=lambda x: x["source"]):
        status_icon = "✅" if r["status"] == "completed" else "❌"
        print(f"  {status_icon} {r['source']:20s} → {r['count']:>6,} docs  [{r['status']}]")
        if r.get("error"):
            print(f"     └─ Error: {r['error'][:80]}")
        total_docs += r["count"]

    print(f"{'─'*60}")
    print(f"  Total: {total_docs:,} documents in {elapsed:.1f}s")
    print(f"{'='*60}\n")

    # Save orchestration report
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed, 1),
        "total_documents": total_docs,
        "results": results,
    }

    report_dir = (data_dir or Path(__file__).resolve().parent.parent.parent / "data")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "scrape_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Export master consolidated CSV and markdown summary for easy viewing
    export_master_csv(report_dir, results)

    return report


def export_master_csv(data_dir: Path, results: list):
    """Combine all scraped source batches into one unified, human-readable CSV."""
    import csv
    raw_dir = data_dir / "raw"
    if not raw_dir.exists():
        return

    master_csv_path = data_dir / "all_scraped_reviews.csv"
    summary_md_path = data_dir / "scraped_data_summary.md"
    fieldnames = ["source", "source_type", "date", "rating", "author", "title", "content", "url"]

    total_rows = 0
    source_counts = {}

    try:
        with open(master_csv_path, "w", encoding="utf-8-sig", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()

            for source_folder in sorted(raw_dir.iterdir()):
                if not source_folder.is_dir():
                    continue
                source_name = source_folder.name
                count = 0

                for batch_file in sorted(source_folder.glob("batch_*.json")):
                    with open(batch_file, "r", encoding="utf-8") as f_in:
                        batch = json.load(f_in)
                        for doc in batch:
                            writer.writerow({
                                "source": doc.get("source", source_name),
                                "source_type": doc.get("source_type", ""),
                                "date": (doc.get("timestamp") or "")[:10],
                                "rating": doc.get("rating", ""),
                                "author": doc.get("author", ""),
                                "title": doc.get("title", ""),
                                "content": doc.get("content", ""),
                                "url": doc.get("url", ""),
                            })
                            count += 1

                source_counts[source_name] = count
                total_rows += count

        print(f"\n  📄 Master spreadsheet exported to: {master_csv_path} ({total_rows:,} rows)")

        # Create quick markdown summary in data/ folder
        with open(summary_md_path, "w", encoding="utf-8") as f_md:
            f_md.write(f"# 📦 Scraped Data Summary\n\n")
            f_md.write(f"**Total Documents Scraped:** {total_rows:,}\n\n")
            f_md.write(f"| Source | Category | Documents Scraped | CSV File Link |\n")
            f_md.write(f"|---|---|---|---|\n")
            for s_name, s_count in source_counts.items():
                f_md.write(f"| **{s_name}** | Primary/Secondary | {s_count:,} | [`raw/{s_name}/{s_name}_reviews.csv`](raw/{s_name}/{s_name}_reviews.csv) |\n")
            f_md.write(f"\n> **Master Dataset:** [`all_scraped_reviews.csv`](all_scraped_reviews.csv) contains all {total_rows:,} reviews.\n")

    except Exception as e:
        print(f"  ⚠️ Master CSV export error: {e}")


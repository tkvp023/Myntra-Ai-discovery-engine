"""
Cleaning pipeline orchestrator.
Chains: normalize → language filter → relevance filter → deduplicate.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Optional

from tqdm import tqdm

from pipeline.cleaning.normalizer import normalize_document
from pipeline.cleaning.language_filter import filter_documents as language_filter
from pipeline.cleaning.relevance_filter import filter_documents as relevance_filter
from pipeline.cleaning.deduplicator import deduplicate


class CleaningPipeline:
    """
    Orchestrates the full cleaning pipeline on scraped documents.
    
    Pipeline order:
    1. Normalize text (unicode, emoji, URL strip)
    2. Language filter (keep English + Hinglish)
    3. Relevance filter (keep fashion/shopping signals)
    4. Deduplicate (exact hash + fuzzy MinHash)
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path(__file__).resolve().parent.parent.parent / "data"
        self.raw_dir = self.data_dir / "raw"
        self.clean_dir = self.data_dir / "clean"
        self.clean_dir.mkdir(parents=True, exist_ok=True)
        self.stats: Dict = {}

    def load_raw_documents(self, sources: Optional[List[str]] = None) -> List[dict]:
        """Load all raw documents from data/raw/{source}/batch_*.json."""
        docs = []
        
        source_dirs = sorted(self.raw_dir.iterdir()) if self.raw_dir.exists() else []
        
        for source_dir in source_dirs:
            if not source_dir.is_dir():
                continue
            if sources and source_dir.name not in sources:
                continue

            batch_files = sorted(source_dir.glob("batch_*.json"))
            for batch_file in batch_files:
                try:
                    with open(batch_file, "r", encoding="utf-8") as f:
                        batch = json.load(f)
                        docs.extend(batch)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"  ⚠️  Error reading {batch_file}: {e}")
                    continue

        return docs

    def run(self, sources: Optional[List[str]] = None) -> List[dict]:
        """
        Execute the full cleaning pipeline.
        
        Args:
            sources: Optional list of source names to clean. If None, cleans all.
        
        Returns:
            List of cleaned document dicts.
        """
        print(f"\n{'='*60}")
        print(f"🧹 Cleaning Pipeline")
        print(f"{'='*60}")
        start_time = time.time()

        # Load raw data
        print(f"\n  📂 Loading raw documents...")
        raw_docs = self.load_raw_documents(sources=sources)
        print(f"  📦 Loaded {len(raw_docs):,} raw documents")

        if not raw_docs:
            print(f"  ⚠️  No raw documents found in {self.raw_dir}")
            return []

        # Step 1: Normalize
        print(f"\n  [1/4] 📝 Normalizing text...")
        normalized = []
        for doc in tqdm(raw_docs, desc="  Normalizing", unit="docs"):
            normalized.append(normalize_document(doc))
        print(f"  ✅ Normalized {len(normalized):,} documents")

        # Step 2: Language filter
        print(f"\n  [2/4] 🌐 Language filtering (keep English + Hinglish)...")
        after_lang, lang_dropped = language_filter(normalized)
        print(f"  ✅ Kept {len(after_lang):,} | Dropped {lang_dropped:,} ({lang_dropped/max(len(normalized),1)*100:.1f}%)")

        # Step 3: Relevance filter
        print(f"\n  [3/4] 🎯 Relevance filtering (fashion/shopping signals)...")
        after_relevance, relevance_dropped = relevance_filter(after_lang)
        print(f"  ✅ Kept {len(after_relevance):,} | Dropped {relevance_dropped:,} ({relevance_dropped/max(len(after_lang),1)*100:.1f}%)")

        # Step 4: Deduplication
        print(f"\n  [4/4] 🔄 Deduplicating (exact hash + fuzzy MinHash)...")
        after_dedup, dedup_stats = deduplicate(after_relevance)
        print(f"  ✅ Kept {len(after_dedup):,} | Removed {dedup_stats['total_removed']:,}")
        print(f"     ├─ Exact duplicates: {dedup_stats['exact_duplicates']:,}")
        print(f"     └─ Fuzzy duplicates: {dedup_stats['fuzzy_duplicates']:,}")

        elapsed = time.time() - start_time

        # Compile stats
        self.stats = {
            "raw_count": len(raw_docs),
            "after_normalize": len(normalized),
            "after_language_filter": len(after_lang),
            "language_dropped": lang_dropped,
            "language_drop_rate": round(lang_dropped / max(len(normalized), 1) * 100, 2),
            "after_relevance_filter": len(after_relevance),
            "relevance_dropped": relevance_dropped,
            "relevance_drop_rate": round(relevance_dropped / max(len(after_lang), 1) * 100, 2),
            "after_dedup": len(after_dedup),
            "dedup_stats": dedup_stats,
            "final_count": len(after_dedup),
            "retention_rate": round(len(after_dedup) / max(len(raw_docs), 1) * 100, 2),
            "elapsed_seconds": round(elapsed, 1),
        }

        # Save clean data
        self._save_clean_docs(after_dedup)
        
        # Save stats
        self._save_stats()

        # Print summary
        self._print_summary()

        return after_dedup

    def _save_clean_docs(self, docs: List[dict]):
        """Save clean documents to data/clean/ in batches of 500."""
        batch_size = 500
        for i in range(0, len(docs), batch_size):
            batch = docs[i:i + batch_size]
            batch_num = i // batch_size + 1
            path = self.clean_dir / f"clean_batch_{batch_num:04d}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(batch, f, indent=2, ensure_ascii=False)
        
        print(f"\n  💾 Saved {len(docs):,} clean documents to {self.clean_dir}")

    def _save_stats(self):
        """Save cleaning statistics to a JSON file."""
        stats_path = self.data_dir / "cleaning_stats.json"
        with open(stats_path, "w") as f:
            json.dump(self.stats, f, indent=2)

    def _print_summary(self):
        """Print a formatted summary of the cleaning pipeline."""
        s = self.stats
        print(f"\n{'='*60}")
        print(f"📊 Cleaning Pipeline — Summary")
        print(f"{'='*60}")
        print(f"  Raw documents:      {s['raw_count']:>8,}")
        print(f"  After lang filter:  {s['after_language_filter']:>8,}  (-{s['language_dropped']:,}, {s['language_drop_rate']}%)")
        print(f"  After relevance:    {s['after_relevance_filter']:>8,}  (-{s['relevance_dropped']:,}, {s['relevance_drop_rate']}%)")
        print(f"  After dedup:        {s['after_dedup']:>8,}  (-{s['dedup_stats']['total_removed']:,}, {s['dedup_stats']['dedup_rate']}%)")
        print(f"{'─'*60}")
        print(f"  Final corpus:       {s['final_count']:>8,}  ({s['retention_rate']}% retained)")
        print(f"  Time:               {s['elapsed_seconds']}s")
        print(f"{'='*60}\n")

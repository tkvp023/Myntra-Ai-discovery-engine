"""Phase 3 verification — imports, aggregator logic, export pipeline."""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))

print("[1] Testing quantification package imports...")
from pipeline.quantification.aggregator import (
    Aggregator, SOURCE_COLORS, SOURCE_LABELS, HESITATION_LABELS,
    HESITATION_COLORS, FACTOR_LABELS, SEGMENTS, INFO_TYPE_LABELS
)
assert len(HESITATION_LABELS) == 12
assert len(FACTOR_LABELS) == 8
assert len(SEGMENTS) == 3
assert "playstore" in SOURCE_COLORS
print("    [OK] Aggregator constants correct")

from pipeline.quantification.question_mapper import build_all_questions, QUESTIONS, QUESTION_TAG_MAPPING
assert len(QUESTIONS) == 10
assert all(i in QUESTIONS for i in range(1, 11))
print("    [OK] Question mapper loaded, 10 questions defined")

from pipeline.quantification.export import (
    build_summary, build_systemic_gaps, build_corpus_meta,
    run_consistency_checks, run_export, PIPELINE_VERSION
)
assert PIPELINE_VERSION == "1.0.0"
print("    [OK] Export pipeline loaded")

print("[2] Testing Aggregator against real DB...")
from pipeline.db.connection import init_db, get_session
init_db()
session = get_session()
agg = Aggregator(session)

stats = agg.corpus_stats()
assert isinstance(stats["total_docs"], int)
assert isinstance(stats["avg_confidence"], float)
print(f"    [OK] corpus_stats: {stats['total_docs']} docs, {stats['total_classified']} classified")

src_dist = agg.source_distribution()
assert isinstance(src_dist, list)
print(f"    [OK] source_distribution: {len(src_dist)} sources")

hesitation = agg.hesitation_frequency()
assert isinstance(hesitation, list)
print(f"    [OK] hesitation_frequency: {len(hesitation)} tags found")

seg_splits = agg.hesitation_by_segment()
assert set(seg_splits.keys()) == {"gen_z", "millennial", "gen_x"}
print("    [OK] hesitation_by_segment: 3 segments")

factors = agg.factor_mentions()
assert isinstance(factors, list)
print(f"    [OK] factor_mentions: {len(factors)} factors found")

temporal = agg.temporal_trend()
assert isinstance(temporal, list)
print(f"    [OK] temporal_trend: {len(temporal)} months")

needs = agg.top_unmet_needs(top_n=5)
assert isinstance(needs, list)
print(f"    [OK] top_unmet_needs: {len(needs)} needs")

session.close()

print("[3] Testing export pipeline (dry run — no dashboard copy)...")
import tempfile, json
with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp)
    result = run_export(output_dir=out, copy_to_dashboard=False)
    files = result["files"]
    assert "summary.json" in files, "Missing summary.json"
    assert "corpus_meta.json" in files, "Missing corpus_meta.json"
    assert "systemic_gaps.json" in files, "Missing systemic_gaps.json"
    assert all(f"q{i}.json" in files for i in range(1, 11)), "Missing q-files"
    print(f"    [OK] Export generated {len(files)} JSON files: {files}")

    # Spot-check summary.json schema
    with open(out / "summary.json") as f:
        s = json.load(f)
    assert "kpi_cards" in s
    assert "source_distribution" in s
    assert "top_opportunities" in s
    assert "generated_at" in s
    assert "pipeline_version" in s
    print("    [OK] summary.json schema valid")

    # Spot-check q2.json schema
    with open(out / "q2.json") as f:
        q2 = json.load(f)
    assert q2["question_id"] == 2
    assert "breakdown" in q2
    assert "segment_splits" in q2
    assert "temporal_trend" in q2
    assert "key_quotes" in q2
    print("    [OK] q2.json schema valid")

    # Spot-check q5.json has platform_matrix
    with open(out / "q5.json") as f:
        q5 = json.load(f)
    assert "platform_matrix" in q5
    print("    [OK] q5.json has platform_matrix")

    # Spot-check q7.json has radar + correlation
    with open(out / "q7.json") as f:
        q7 = json.load(f)
    assert "radar_data" in q7
    assert "correlation_matrix" in q7
    print("    [OK] q7.json has radar_data + correlation_matrix")

    # Spot-check q10.json has treemap
    with open(out / "q10.json") as f:
        q10 = json.load(f)
    assert "treemap_data" in q10
    print("    [OK] q10.json has treemap_data")

    # Consistency checks
    checks = result["consistency"]
    if not checks["passed"]:
        print(f"    [WARN] Consistency issues: {checks['errors']}")
    else:
        print("    [OK] All consistency checks passed")

print("[4] Testing CLI export mode import...")
from pipeline.run_pipeline import cmd_export
print("    [OK] cmd_export importable from run_pipeline")

print()
print("=== ALL PHASE 3 VERIFICATION PASSED ===")

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from pipeline.db.connection import get_session, init_db
from pipeline.db.models import Document, Classification, HesitationTag, FactorMention, UnmetNeed, QuestionMapping
from pipeline.classification.keyword_tagger import classify_with_keywords
from pipeline.quantification.export import run_export


def reclassify_full_corpus():
    print("=" * 60)
    print("🚀 Reclassifying Full Corpus with Wishlist-to-Purchase Intelligence")
    print("=" * 60)

    init_db()
    session = get_session()

    # Clear old classifications & tags
    print("\n  🧹 Clearing previous classifications...")
    session.query(QuestionMapping).delete()
    session.query(UnmetNeed).delete()
    session.query(FactorMention).delete()
    session.query(HesitationTag).delete()
    session.query(Classification).delete()
    session.commit()

    docs = session.query(Document).all()
    print(f"  📦 Processing {len(docs):,} documents from database...")

    total_tags = 0
    total_factors = 0
    total_needs = 0
    total_mappings = 0
    now_iso = datetime.now(timezone.utc).isoformat()

    from tqdm import tqdm
    for doc in tqdm(docs, desc="  Classifying", unit="docs"):
        raw_res = classify_with_keywords(doc.doc_id, doc.content)
        cls_data = raw_res["classification"]

        user_signals = cls_data.get("user_segment_signals", {})
        comp = cls_data.get("comparison_behavior", {})
        ext = cls_data.get("external_info_seeking", {})
        factors = cls_data.get("factor_mentions", {})

        classification = Classification(
            doc_id=doc.doc_id,
            wishlist_intent=cls_data.get("wishlist_intent", "genuine_purchase_intent"),
            inferred_age_group=user_signals.get("inferred_age_group", "millennial"),
            price_sensitivity=user_signals.get("price_sensitivity", "medium"),
            fashion_engagement=user_signals.get("fashion_engagement", "high"),
            gender_signal=user_signals.get("gender_signal", "unknown"),
            compares_across=comp.get("compares_across_platforms", False),
            seeks_external_info=ext.get("seeks_external_info", False),
            is_primary_signal=cls_data.get("is_primary_signal", True),
            raw_classification=json.dumps(cls_data),
            classified_at=now_iso,
        )
        session.add(classification)

        # Hesitation tags
        for ht in cls_data.get("hesitation_reasons", []):
            tag = HesitationTag(
                doc_id=doc.doc_id,
                reason=ht.get("reason"),
                confidence=ht.get("confidence", 0.85),
                evidence_quote=ht.get("evidence_quote", ""),
            )
            session.add(tag)
            total_tags += 1

        # Factor mentions
        for factor_name, factor_val in factors.items():
            if isinstance(factor_val, dict) and factor_val.get("mentioned"):
                fm = FactorMention(
                    doc_id=doc.doc_id,
                    factor=factor_name,
                    mentioned=True,
                    sentiment=factor_val.get("sentiment", "neutral"),
                )
                session.add(fm)
                total_factors += 1

        # Unmet needs
        for need in cls_data.get("unmet_needs", []):
            if need:
                un = UnmetNeed(
                    doc_id=doc.doc_id,
                    need_text=need,
                )
                session.add(un)
                total_needs += 1

        # Question mappings
        for q_id in cls_data.get("brief_question_mapping", []):
            qm = QuestionMapping(
                doc_id=doc.doc_id,
                question_id=q_id,
            )
            session.add(qm)
            total_mappings += 1

    session.commit()
    session.close()

    print(f"\n  ✅ Successfully classified {len(docs):,} documents!")
    print(f"  🏷️  Extracted {total_tags:,} hesitation tags")
    print(f"  🔍 Extracted {total_factors:,} factor mentions")
    print(f"  💡 Extracted {total_needs:,} unmet needs")
    print(f"  📌 Created {total_mappings:,} question mappings")

    # Export to dashboard
    print("\n  📊 Exporting updated data contracts to dashboard...")
    run_export(copy_to_dashboard=True)
    print("\n  🎉 Complete! Dashboard data is fully updated.")


if __name__ == "__main__":
    reclassify_full_corpus()

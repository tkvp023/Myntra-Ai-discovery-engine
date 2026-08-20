"""
LLM Key Quote Curator — Uses Gemini 3.6 Flash / 3.5 Flash to analyze candidate reviews
and curate the top 5 most meaningful, representative, and articulate quotes for each of the 10 discovery questions.
"""

import os
import sys
import json
import time
import re
import html
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

import google.generativeai as genai
from pipeline.db.connection import get_session
from pipeline.quantification.aggregator import Aggregator, SOURCE_LABELS

QUESTIONS_CONFIG = {
    1: {
        "title": "Why do users add to wishlist? (Motivation & Intent)",
        "focus": "Why shoppers bookmark items, save for price drops, plan future purchases, or build moodboards/aspirational lists instead of immediate checkout.",
        "sql": """
            SELECT d.doc_id, d.content, d.source, d.source_id, d.timestamp, c.inferred_age_group
            FROM documents d
            JOIN classifications c ON d.doc_id = c.doc_id
            WHERE LENGTH(d.content) BETWEEN 40 AND 450
              AND (d.content LIKE '%wishlist%' OR d.content LIKE '%save%' OR d.content LIKE '%bookmark%' OR d.content LIKE '%cart%' OR d.content LIKE '%buy later%' OR d.content LIKE '%shortlist%' OR c.wishlist_intent != 'unknown')
            ORDER BY (CASE WHEN d.content LIKE '%wishlist%' THEN 0 ELSE 1 END), LENGTH(d.content) DESC
            LIMIT 25
        """
    },
    2: {
        "title": "What prevents purchase? (Core Purchase Blockers)",
        "focus": "The primary reasons and friction points that stop shoppers from converting items in their wishlist to completed orders (e.g. sizing confusion, sudden delivery charges, return hassles, doubts on authenticity/quality).",
        "sql": """
            SELECT d.doc_id, d.content, d.source, d.source_id, d.timestamp, c.inferred_age_group
            FROM documents d
            JOIN classifications c ON d.doc_id = c.doc_id
            WHERE LENGTH(d.content) BETWEEN 45 AND 450
              AND (d.content LIKE '%return%' OR d.content LIKE '%refund%' OR d.content LIKE '%size%' OR d.content LIKE '%price%' OR d.content LIKE '%quality%' OR d.content LIKE '%delivery%' OR d.content LIKE '%fake%' OR d.content LIKE '%hesitat%')
            ORDER BY (CASE WHEN d.rating <= 2 THEN 0 ELSE 1 END), LENGTH(d.content) DESC
            LIMIT 25
        """
    },
    3: {
        "title": "What remaining uncertainties do users face? (Fit, Fabric, Style, Information)",
        "focus": "Specific product uncertainties before buying: uncertainty about size/fit chart accuracy, fabric transparency/feel, exact color/shade vs photos, and missing product specs.",
        "sql": """
            SELECT d.doc_id, d.content, d.source, d.source_id, d.timestamp, c.inferred_age_group
            FROM documents d
            JOIN classifications c ON d.doc_id = c.doc_id
            WHERE LENGTH(d.content) BETWEEN 45 AND 450
              AND (d.content LIKE '%size%' OR d.content LIKE '%fit%' OR d.content LIKE '%fabric%' OR d.content LIKE '%cloth%' OR d.content LIKE '%material%' OR d.content LIKE '%color%' OR d.content LIKE '%look%' OR d.content LIKE '%photo%' OR d.content LIKE '%transparent%')
            ORDER BY LENGTH(d.content) DESC
            LIMIT 25
        """
    },
    4: {
        "title": "Why do users postpone their purchases? (Sale Waiting & Timing)",
        "focus": "Postponing purchase to wait for upcoming End of Reason Sale (EORS), festive discount coupons, payday timing, or price drops on wishlisted items.",
        "sql": """
            SELECT d.doc_id, d.content, d.source, d.source_id, d.timestamp, c.inferred_age_group
            FROM documents d
            JOIN classifications c ON d.doc_id = c.doc_id
            WHERE LENGTH(d.content) BETWEEN 45 AND 450
              AND (d.content LIKE '%sale%' OR d.content LIKE '%discount%' OR d.content LIKE '%coupon%' OR d.content LIKE '%price drop%' OR d.content LIKE '%offer%' OR d.content LIKE '%expensive%' OR d.content LIKE '%wait%')
            ORDER BY LENGTH(d.content) DESC
            LIMIT 25
        """
    },
    5: {
        "title": "How do users compare wishlist items across products & platforms?",
        "focus": "Comparison behavior: checking the same garment on Amazon, Flipkart, Ajio, Meesho, Zara, or H&M, finding cheaper alternatives, or suffering from choice overload.",
        "sql": """
            SELECT d.doc_id, d.content, d.source, d.source_id, d.timestamp, c.inferred_age_group
            FROM documents d
            JOIN classifications c ON d.doc_id = c.doc_id
            WHERE LENGTH(d.content) BETWEEN 45 AND 450
              AND (d.content LIKE '%amazon%' OR d.content LIKE '%ajio%' OR d.content LIKE '%flipkart%' OR d.content LIKE '%meesho%' OR d.content LIKE '%zara%' OR d.content LIKE '%compare%' OR d.content LIKE '%other app%' OR d.content LIKE '%cheaper%')
            ORDER BY LENGTH(d.content) DESC
            LIMIT 25
        """
    },
    6: {
        "title": "What external information do users seek to resolve hesitation?",
        "focus": "External channels consulted before buying: YouTube try-on haul videos, Instagram influencer reels/styling, asking friends on WhatsApp/Reddit, or trying similar sizes in offline stores.",
        "sql": """
            SELECT d.doc_id, d.content, d.source, d.source_id, d.timestamp, c.inferred_age_group
            FROM documents d
            JOIN classifications c ON d.doc_id = c.doc_id
            WHERE LENGTH(d.content) BETWEEN 45 AND 450
              AND (d.content LIKE '%youtube%' OR d.content LIKE '%instagram%' OR d.content LIKE '%video%' OR d.content LIKE '%haul%' OR d.content LIKE '%review%' OR d.content LIKE '%try on%' OR d.content LIKE '%influencer%' OR d.content LIKE '%friend%')
            ORDER BY LENGTH(d.content) DESC
            LIMIT 25
        """
    },
    7: {
        "title": "How do price, fit, reviews, styling, and validation rank in importance?",
        "focus": "The relative hierarchy of buying factors: fit & size accuracy, transparent pricing, authentic customer photo reviews, styling versatility, and easy doorstep returns.",
        "sql": """
            SELECT d.doc_id, d.content, d.source, d.source_id, d.timestamp, c.inferred_age_group
            FROM documents d
            JOIN classifications c ON d.doc_id = c.doc_id
            WHERE LENGTH(d.content) BETWEEN 45 AND 450
              AND (d.content LIKE '%fit%' OR d.content LIKE '%price%' OR d.content LIKE '%review%' OR d.content LIKE '%quality%' OR d.content LIKE '%return%' OR d.content LIKE '%brand%')
            ORDER BY LENGTH(d.content) DESC
            LIMIT 25
        """
    },
    8: {
        "title": "Is wishlist used more for purchase intent or bookmarking/inspiration?",
        "focus": "Contrasting behavior between high purchase intent (adding items to buy on payday) vs recreational moodboarding/hoarding (saving hundreds of aspirational luxury items with no intention to buy).",
        "sql": """
            SELECT d.doc_id, d.content, d.source, d.source_id, d.timestamp, c.inferred_age_group
            FROM documents d
            JOIN classifications c ON d.doc_id = c.doc_id
            WHERE LENGTH(d.content) BETWEEN 40 AND 450
              AND (d.content LIKE '%wishlist%' OR d.content LIKE '%save%' OR d.content LIKE '%bookmark%' OR d.content LIKE '%hoard%' OR d.content LIKE '%inspire%' OR d.content LIKE '%aesthetic%' OR d.content LIKE '%buy%')
            ORDER BY LENGTH(d.content) DESC
            LIMIT 25
        """
    },
    9: {
        "title": "How do wishlist behaviors differ across demographics (Gen-Z vs Millennials)?",
        "focus": "Segment-specific behaviors: Gen-Z seeking trendy streetwear, aesthetic reels & instant gratification vs Millennials focused on workwear, fabric durability, and value-for-money.",
        "sql": """
            SELECT d.doc_id, d.content, d.source, d.source_id, d.timestamp, c.inferred_age_group
            FROM documents d
            JOIN classifications c ON d.doc_id = c.doc_id
            WHERE LENGTH(d.content) BETWEEN 45 AND 450
              AND c.inferred_age_group IN ('gen_z', 'millennial', 'gen_x')
            ORDER BY LENGTH(d.content) DESC
            LIMIT 25
        """
    },
    10: {
        "title": "What unmet needs or feature gaps exist in wishlist experiences?",
        "focus": "Specific feature requests from shoppers: automatic price drop notifications, back-in-stock size alerts, virtual 3D try-on, wishlist folder categorization, sharing wishlists with friends, and fabric video reviews.",
        "sql": """
            SELECT d.doc_id, d.content, d.source, d.source_id, d.timestamp, c.inferred_age_group
            FROM documents d
            JOIN classifications c ON d.doc_id = c.doc_id
            WHERE LENGTH(d.content) BETWEEN 45 AND 450
              AND (d.content LIKE '%feature%' OR d.content LIKE '%wishlist%' OR d.content LIKE '%notify%' OR d.content LIKE '%alert%' OR d.content LIKE '%option%' OR d.content LIKE '%add%' OR d.content LIKE '%share%' OR d.content LIKE '%video%' OR d.content LIKE '%size chart%' OR d.content LIKE '%suggest%')
            ORDER BY LENGTH(d.content) DESC
            LIMIT 25
        """
    }
}

MODELS_FALLBACK = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]


def curate_quotes_for_question(qid: int, config: dict, agg: Aggregator) -> List[Dict[str, Any]]:
    """Fetch candidate reviews and have Gemini select & format the top 5 quotes with model failover."""
    rows = agg._q(config["sql"])
    if not rows:
        print(f"  [!] No candidate rows found for Q{qid}", flush=True)
        return []

    candidates = []
    for r in rows:
        text_clean = html.unescape(str(r[1] or "")).strip()
        text_clean = re.sub(r"^/u/[^\s]+\s+on\s+[^:\n]+[:\n\-]*", "", text_clean)
        text_clean = re.sub(r"^Updated by user [A-Za-z]+ \d+, \d+\s*(?:Company fixed the issue and)?\s*", "", text_clean, flags=re.IGNORECASE)
        text_clean = " ".join(text_clean.split())
        if len(text_clean) < 35:
            continue
        candidates.append({
            "text": text_clean,
            "source": SOURCE_LABELS.get(r[2] or "", r[2] or ""),
            "source_id": str(r[3] or ""),
            "date": str(r[4] or "")[:10],
            "segment": str(r[5] or "millennial")
        })

    prompt = f"""You are an expert consumer insights analyst for Myntra's Wishlist Intelligence Engine.
Select the top 5 most poignant, articulate, and insightful real customer quotes from the candidate pool below that directly answer or provide real evidence for this specific research question:

Question #{qid}: {config['title']}
Focus: {config['focus']}

Candidate Customer Reviews:
{json.dumps(candidates[:18], indent=2)}

Instructions:
1. Select 5 distinct candidate reviews that BEST answer or illustrate Question #{qid}.
2. For each selected review, return:
   - "text": Clean customer quote (between 60 and 260 characters).
   - "source": Source name from candidate ("Play Store", "Reddit", "YouTube", "App Store", "Trustpilot", "PissedConsumer").
   - "source_id": The candidate source_id.
   - "date": Date (YYYY-MM-DD).
   - "confidence": Float between 0.85 and 0.95.
   - "tags": Array with 1 descriptive snake_case tag (e.g. ["sizing_uncertainty"], ["price_drop_waiting"], ["bookmarking_inspiration"], ["cross_platform_comparison"], ["try_on_haul_seeking"], ["size_chart_gap"], etc.).
   - "segment": "gen_z", "millennial", or "gen_x".

Respond ONLY with a valid JSON array of 5 quote objects. No markdown wrap, no commentary."""

    for model_name in MODELS_FALLBACK:
        try:
            model = genai.GenerativeModel(
                model_name,
                generation_config={"temperature": 0.2, "response_mime_type": "application/json"}
            )
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()

            quotes = json.loads(raw_text)
            if isinstance(quotes, list) and len(quotes) >= 3:
                return quotes[:5]
        except Exception as e:
            print(f"  [!] {model_name} failed for Q{qid}: {str(e)[:100]}, trying next model...", flush=True)
            time.sleep(0.5)

    return []


def run_llm_quote_curation():
    """Run LLM curation across all 10 questions and persist results."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[-] GEMINI_API_KEY not found in environment", flush=True)
        return

    genai.configure(api_key=api_key)

    session = get_session()
    agg = Aggregator(session)

    all_curated_quotes = {}
    print("=" * 60, flush=True)
    print("[*] Starting LLM Quote Curation with Gemini 3.6 / 3.5 Flash...", flush=True)
    print("=" * 60, flush=True)

    for qid in range(1, 11):
        config = QUESTIONS_CONFIG[qid]
        print(f"[*] Curating Q{qid}: {config['title']}...", flush=True)
        quotes = curate_quotes_for_question(qid, config, agg)
        if quotes:
            all_curated_quotes[str(qid)] = quotes
            print(f"  [OK] Successfully curated {len(quotes)} high-signal quotes for Q{qid}", flush=True)
            for i, q in enumerate(quotes[:2], 1):
                print(f"    - Quote {i} [{q.get('tags', [''])[0]}]: {q.get('text', '')[:80]}...", flush=True)
        else:
            print(f"  [!] Fallback needed for Q{qid}", flush=True)
        time.sleep(0.5)

    out_file = PROJECT_ROOT / "data" / "exports" / "llm_curated_quotes.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_curated_quotes, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] Saved all curated quotes to {out_file}", flush=True)

    # Also copy to dashboard/public/data
    dashboard_out = PROJECT_ROOT / "dashboard" / "public" / "data" / "llm_curated_quotes.json"
    dashboard_out.parent.mkdir(parents=True, exist_ok=True)
    with open(dashboard_out, "w", encoding="utf-8") as f:
        json.dump(all_curated_quotes, f, indent=2, ensure_ascii=False)

    return all_curated_quotes


if __name__ == "__main__":
    run_llm_quote_curation()

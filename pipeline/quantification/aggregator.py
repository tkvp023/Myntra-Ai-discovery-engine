"""
Aggregator — SQL-based aggregation of classification tags.
Produces tag frequencies, cross-tabs, weighted roll-ups, temporal trends.
All queries run directly against the SQLite DB built in Phase 1 & 2.
"""

from __future__ import annotations
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Optional

from sqlalchemy import text


# ─────────────────────────────────────────────────────────────
# Source color palette (matches data_contracts.md)
# ─────────────────────────────────────────────────────────────
SOURCE_COLORS = {
    "playstore":      "#ff3f6c",
    "appstore":       "#2dd4bf",
    "reddit":         "#ff7849",
    "youtube":        "#a855f7",
    "trustpilot":     "#3b82f6",
    "pissedconsumer": "#fbbf24",
    "reviewsio":      "#6b7280",
}

SOURCE_LABELS = {
    "playstore":      "Play Store",
    "appstore":       "App Store",
    "reddit":         "Reddit",
    "youtube":        "YouTube",
    "trustpilot":     "Trustpilot",
    "pissedconsumer": "PissedConsumer",
    "reviewsio":      "Reviews.io",
}

HESITATION_LABELS = {
    "sizing_uncertainty":     "Sizing Uncertainty",
    "price_sensitivity":      "Price Sensitivity",
    "style_uncertainty":      "Style Uncertainty",
    "quality_doubt":          "Quality Doubt",
    "waiting_for_sale":       "Waiting for Sale",
    "social_validation_needed": "Social Validation Needed",
    "occasion_mismatch":      "Occasion Mismatch",
    "comparison_paralysis":   "Comparison Paralysis",
    "trust_deficit":          "Trust Deficit",
    "information_gap":        "Information Gap",
    "return_policy_concern":  "Return Policy Concern",
    "other":                  "Other",
}

HESITATION_COLORS = {
    "sizing_uncertainty":     "#ff3f6c",
    "price_sensitivity":      "#ff7849",
    "quality_doubt":          "#a855f7",
    "waiting_for_sale":       "#2dd4bf",
    "style_uncertainty":      "#3b82f6",
    "social_validation_needed": "#fbbf24",
    "comparison_paralysis":   "#ec4899",
    "trust_deficit":          "#f97316",
    "information_gap":        "#84cc16",
    "return_policy_concern":  "#06b6d4",
    "occasion_mismatch":      "#8b5cf6",
    "other":                  "#6b7280",
}

FACTOR_LABELS = {
    "fit_size":        "Fit/Size",
    "price":           "Price",
    "reviews_ratings": "Reviews & Ratings",
    "styling":         "Styling",
    "occasion":        "Occasion",
    "social_validation": "Social Validation",
    "brand_trust":     "Brand Trust",
    "delivery_returns": "Delivery & Returns",
}

SEGMENTS = ["gen_z", "millennial", "gen_x"]

INFO_TYPE_LABELS = {
    "youtube_reviews":   "YouTube Reviews",
    "instagram_styling": "Instagram Styling",
    "google_search":     "Google Search",
    "ask_friends":       "Ask Friends",
    "offline_trial":     "Offline Trial",
    "brand_website":     "Brand Website",
    "other":             "Other",
}


class Aggregator:
    """Runs all aggregation queries against the SQLite database."""

    def __init__(self, session):
        self.session = session

    def _q(self, sql: str, params: dict = None) -> list:
        """Execute raw SQL and return list of Row objects."""
        result = self.session.execute(text(sql), params or {})
        return result.fetchall()

    # ─────────────────────────────────────────────────────────
    # Corpus-Level Stats
    # ─────────────────────────────────────────────────────────

    def corpus_stats(self) -> dict:
        """Overall corpus counts."""
        rows = self._q("""
            SELECT
                (SELECT COUNT(*) FROM documents)                                        AS total_docs,
                (SELECT COUNT(*) FROM classifications)                                  AS total_classified,
                (SELECT COUNT(*) FROM classifications WHERE is_primary_signal = 1)      AS primary_signal,
                (SELECT COUNT(*) FROM classifications WHERE is_primary_signal = 0)      AS no_signal,
                (SELECT COUNT(*) FROM hesitation_tags)                                  AS total_tags,
                (SELECT AVG(confidence) FROM hesitation_tags)                           AS avg_confidence
        """)
        r = rows[0]
        return {
            "total_docs":       int(r[0] or 0),
            "total_classified": int(r[1] or 0),
            "primary_signal":   int(r[2] or 0),
            "no_signal":        int(r[3] or 0),
            "total_tags":       int(r[4] or 0),
            "avg_confidence":   round(float(r[5] or 0), 3),
        }

    def source_distribution(self) -> List[dict]:
        """Count and percentage per source."""
        rows = self._q("""
            SELECT source, COUNT(*) as cnt
            FROM documents
            GROUP BY source
            ORDER BY cnt DESC
        """)
        total = sum(r[1] for r in rows)
        result = []
        for r in rows:
            src = r[0]
            cnt = int(r[1])
            result.append({
                "source": SOURCE_LABELS.get(src, src),
                "source_key": src,
                "count": cnt,
                "pct": round(cnt / total * 100, 1) if total else 0,
                "color": SOURCE_COLORS.get(src, "#6b7280"),
            })
        return result

    def date_range(self) -> dict:
        """Earliest and latest review timestamps."""
        rows = self._q("""
            SELECT MIN(timestamp), MAX(timestamp)
            FROM documents
            WHERE timestamp IS NOT NULL
        """)
        r = rows[0]
        return {"earliest": r[0] or "", "latest": r[1] or ""}

    # ─────────────────────────────────────────────────────────
    # Hesitation Tag Aggregations
    # ─────────────────────────────────────────────────────────

    def hesitation_frequency(
        self,
        question_ids: Optional[List[int]] = None,
        segment: Optional[str] = None,
        source: Optional[str] = None,
    ) -> List[dict]:
        """
        Count hesitation tags, optionally filtered.
        Returns list sorted by count desc.
        """
        filters = ["1=1"]
        params = {}

        if question_ids:
            placeholders = ", ".join(f":q{i}" for i, _ in enumerate(question_ids))
            filters.append(f"""
                h.doc_id IN (
                    SELECT doc_id FROM question_mappings
                    WHERE question_id IN ({placeholders})
                )
            """)
            for i, qid in enumerate(question_ids):
                params[f"q{i}"] = qid

        if segment:
            filters.append("c.inferred_age_group = :segment")
            params["segment"] = segment

        if source:
            filters.append("d.source = :source")
            params["source"] = source

        where = " AND ".join(filters)
        rows = self._q(f"""
            SELECT h.reason,
                   COUNT(*) as cnt,
                   AVG(h.confidence) as avg_conf
            FROM hesitation_tags h
            JOIN classifications c ON h.doc_id = c.doc_id
            JOIN documents d ON h.doc_id = d.doc_id
            WHERE {where}
            GROUP BY h.reason
            ORDER BY cnt DESC
        """, params)

        total = sum(int(r[1]) for r in rows)
        result = []
        for r in rows:
            tag = r[0]
            cnt = int(r[1])
            result.append({
                "tag":            tag,
                "label":          HESITATION_LABELS.get(tag, tag),
                "count":          cnt,
                "pct":            round(cnt / total * 100, 1) if total else 0,
                "avg_confidence": round(float(r[2] or 0), 3),
                "color":          HESITATION_COLORS.get(tag, "#6b7280"),
            })
        return result

    def hesitation_by_segment(
        self,
        question_ids: Optional[List[int]] = None,
    ) -> Dict[str, List[dict]]:
        """Hesitation breakdown per segment (gen_z, millennial, gen_x)."""
        return {
            seg: self.hesitation_frequency(question_ids=question_ids, segment=seg)
            for seg in SEGMENTS
        }

    def hesitation_by_source(
        self,
        question_ids: Optional[List[int]] = None,
    ) -> List[dict]:
        """For each hesitation tag, show count per source."""
        overall = self.hesitation_frequency(question_ids=question_ids)
        result = []
        for item in overall:
            tag = item["tag"]
            sources = []
            rows = self._q("""
                SELECT d.source, COUNT(*) as cnt
                FROM hesitation_tags h
                JOIN documents d ON h.doc_id = d.doc_id
                WHERE h.reason = :tag
                GROUP BY d.source
                ORDER BY cnt DESC
            """, {"tag": tag})
            tag_total = sum(int(r[1]) for r in rows)
            for r in rows:
                src = r[0]
                cnt = int(r[1])
                sources.append({
                    "source": SOURCE_LABELS.get(src, src),
                    "count":  cnt,
                    "pct":    round(cnt / tag_total * 100, 1) if tag_total else 0,
                })
            result.append({
                "label":   item["label"],
                "tag":     tag,
                "sources": sources,
            })
        return result

    # ─────────────────────────────────────────────────────────
    # Factor Mention Aggregations
    # ─────────────────────────────────────────────────────────

    def factor_mentions(
        self,
        segment: Optional[str] = None,
    ) -> List[dict]:
        """Count each factor mention, with sentiment breakdown."""
        params = {}
        seg_join = ""
        seg_filter = ""
        if segment:
            seg_join = "JOIN classifications c ON fm.doc_id = c.doc_id"
            seg_filter = "AND c.inferred_age_group = :segment"
            params["segment"] = segment

        rows = self._q(f"""
            SELECT fm.factor,
                   COUNT(*) as total,
                   SUM(CASE WHEN fm.sentiment = 'positive' THEN 1 ELSE 0 END) as pos,
                   SUM(CASE WHEN fm.sentiment = 'negative' THEN 1 ELSE 0 END) as neg,
                   SUM(CASE WHEN fm.sentiment = 'neutral'  THEN 1 ELSE 0 END) as neu,
                   SUM(CASE WHEN fm.sentiment = 'mixed'    THEN 1 ELSE 0 END) as mix
            FROM factor_mentions fm
            {seg_join}
            WHERE fm.mentioned = 1 {seg_filter}
            GROUP BY fm.factor
            ORDER BY total DESC
        """, params)

        all_total = sum(int(r[1]) for r in rows) or 1
        result = []
        for r in rows:
            factor = r[0]
            total = int(r[1])
            pos = int(r[2] or 0)
            neg = int(r[3] or 0)
            neu = int(r[4] or 0)
            mix = int(r[5] or 0)
            result.append({
                "factor":        factor,
                "label":         FACTOR_LABELS.get(factor, factor),
                "count":         total,
                "importance":    round(total / all_total * 100, 1),
                "positive_pct":  round(pos / total * 100, 1) if total else 0,
                "negative_pct":  round(neg / total * 100, 1) if total else 0,
                "neutral_pct":   round(neu / total * 100, 1) if total else 0,
                "mixed_pct":     round(mix / total * 100, 1) if total else 0,
            })
        return result

    def factor_correlation_matrix(self) -> dict:
        """Simple co-occurrence matrix between factors."""
        factors = list(FACTOR_LABELS.keys())
        n = len(factors)
        # Build co-occurrence counts
        matrix = [[0.0] * n for _ in range(n)]
        for i, f1 in enumerate(factors):
            for j, f2 in enumerate(factors):
                if i == j:
                    matrix[i][j] = 1.0
                    continue
                if j < i:
                    matrix[i][j] = matrix[j][i]
                    continue
                rows = self._q("""
                    SELECT COUNT(*) FROM factor_mentions fm1
                    JOIN factor_mentions fm2 ON fm1.doc_id = fm2.doc_id
                    WHERE fm1.factor = :f1 AND fm1.mentioned = 1
                      AND fm2.factor = :f2 AND fm2.mentioned = 1
                """, {"f1": f1, "f2": f2})
                co_count = int(rows[0][0]) if rows else 0
                # Normalise: co_count / max(count_f1, count_f2)
                r1 = self._q("SELECT COUNT(*) FROM factor_mentions WHERE factor=:f AND mentioned=1", {"f": f1})
                r2 = self._q("SELECT COUNT(*) FROM factor_mentions WHERE factor=:f AND mentioned=1", {"f": f2})
                c1 = int(r1[0][0]) if r1 else 1
                c2 = int(r2[0][0]) if r2 else 1
                matrix[i][j] = round(co_count / max(c1, c2), 2) if max(c1, c2) else 0.0

        return {"factors": factors, "values": matrix}

    # ─────────────────────────────────────────────────────────
    # Wishlist Intent
    # ─────────────────────────────────────────────────────────

    def wishlist_intent_distribution(
        self,
        segment: Optional[str] = None,
    ) -> List[dict]:
        params = {}
        seg_filter = ""
        if segment:
            seg_filter = "AND inferred_age_group = :segment"
            params["segment"] = segment

        rows = self._q(f"""
            SELECT wishlist_intent, COUNT(*) as cnt
            FROM classifications
            WHERE 1=1 {seg_filter}
            GROUP BY wishlist_intent
            ORDER BY cnt DESC
        """, params)
        total = sum(int(r[1]) for r in rows) or 1
        return [
            {"intent": r[0], "count": int(r[1]), "pct": round(int(r[1]) / total * 100, 1)}
            for r in rows
        ]

    # ─────────────────────────────────────────────────────────
    # Comparison Behavior
    # ─────────────────────────────────────────────────────────

    def platform_comparison_matrix(self) -> dict:
        """Criterion × Platform co-mention counts from raw JSON."""
        platforms = ["amazon", "ajio", "meesho", "flipkart", "offline_store"]
        criteria = ["price", "quality", "delivery", "return_policy", "variety"]
        # Query raw classification JSON for platforms_mentioned + comparison_criteria
        rows = self._q("""
            SELECT raw_classification FROM classifications
            WHERE raw_classification IS NOT NULL
        """)
        import json
        matrix = defaultdict(lambda: defaultdict(int))
        for row in rows:
            try:
                cls = json.loads(row[0])
                cb = cls.get("comparison_behavior", {})
                plats = cb.get("platforms_mentioned", [])
                crits = cb.get("comparison_criteria", [])
                for p in plats:
                    if p in platforms:
                        for c in crits:
                            if c in criteria:
                                matrix[c][p] += 1
            except Exception:
                continue

        platform_labels = {
            "amazon": "Amazon", "ajio": "AJIO", "meesho": "Meesho",
            "flipkart": "Flipkart", "offline_store": "Offline",
        }
        return {
            "rows":    criteria,
            "columns": [platform_labels.get(p, p) for p in platforms],
            "values":  [[matrix[c][p] for p in platforms] for c in criteria],
        }

    def compares_across_platforms_pct(self) -> float:
        rows = self._q("""
            SELECT
                SUM(CASE WHEN compares_across = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
            FROM classifications
        """)
        return round(float(rows[0][0] or 0), 1)

    # ─────────────────────────────────────────────────────────
    # External Info Seeking
    # ─────────────────────────────────────────────────────────

    def external_info_types(self) -> List[dict]:
        """Which info types are sought, and how often."""
        rows = self._q("""
            SELECT raw_classification FROM classifications
            WHERE seeks_external_info = 1 AND raw_classification IS NOT NULL
        """)
        import json
        counts = defaultdict(int)
        for row in rows:
            try:
                cls = json.loads(row[0])
                for info_type in cls.get("external_info_seeking", {}).get("info_types", []):
                    counts[info_type] += 1
            except Exception:
                continue
        total = sum(counts.values()) or 1
        return sorted([
            {
                "info_type": k,
                "label":     INFO_TYPE_LABELS.get(k, k),
                "count":     v,
                "pct":       round(v / total * 100, 1),
            }
            for k, v in counts.items()
        ], key=lambda x: -x["count"])

    def seeks_external_info_pct(self) -> float:
        rows = self._q("""
            SELECT
                SUM(CASE WHEN seeks_external_info = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
            FROM classifications
        """)
        return round(float(rows[0][0] or 0), 1)

    def sankey_hesitation_to_info(self) -> dict:
        """Build hesitation -> info_type Sankey links."""
        import json
        rows = self._q("""
            SELECT d.doc_id, d.raw_classification
            FROM classifications d
            WHERE d.seeks_external_info = 1 AND d.raw_classification IS NOT NULL
        """)
        link_counts = defaultdict(int)
        for row in rows:
            try:
                cls = json.loads(row[1])
                reasons = [r["reason"] for r in cls.get("hesitation_reasons", [])]
                info_types = cls.get("external_info_seeking", {}).get("info_types", [])
                for reason in reasons:
                    for info_type in info_types:
                        link_counts[(reason, info_type)] += 1
            except Exception:
                continue

        nodes_set = set()
        links = []
        for (src, tgt), val in sorted(link_counts.items(), key=lambda x: -x[1])[:20]:
            nodes_set.add(src)
            nodes_set.add(tgt)
            links.append({"source": src, "target": tgt, "value": val})

        return {
            "nodes": [{"id": n} for n in sorted(nodes_set)],
            "links": links,
        }

    # ─────────────────────────────────────────────────────────
    # Unmet Needs
    # ─────────────────────────────────────────────────────────

    def top_unmet_needs(self, top_n: int = 20) -> List[dict]:
        """Most frequent unmet needs (by exact text)."""
        rows = self._q("""
            SELECT need_text, COUNT(*) as cnt
            FROM unmet_needs
            GROUP BY need_text
            ORDER BY cnt DESC
            LIMIT :top_n
        """, {"top_n": top_n})
        return [
            {"need": r[0], "frequency": int(r[1])}
            for r in rows
        ]

    def unmet_needs_treemap(self) -> List[dict]:
        """Group unmet needs by theme keywords for treemap."""
        themes = {
            "Fit & Sizing Tools": ["size", "sizing", "fit", "chart", "measurement", "try-on"],
            "Styling Assistance": ["style", "styling", "outfit", "combination", "occasion"],
            "Price & Offers":    ["price", "discount", "sale", "offer", "alert", "notify"],
            "Product Info":      ["photo", "material", "fabric", "quality", "detail", "accurate"],
            "Social Proof":      ["review", "rating", "feedback", "social", "friend"],
            "Delivery & Returns": ["delivery", "return", "refund", "exchange", "shipping"],
        }
        rows = self._q("""SELECT need_text, COUNT(*) as cnt FROM unmet_needs GROUP BY need_text""")
        theme_data = defaultdict(list)
        for row in rows:
            need = row[0].lower()
            cnt = int(row[1])
            matched = False
            for theme, keywords in themes.items():
                if any(kw in need for kw in keywords):
                    theme_data[theme].append({"name": row[0], "value": cnt})
                    matched = True
                    break
            if not matched:
                theme_data["Other"].append({"name": row[0], "value": cnt})

        return [
            {"theme": theme, "children": sorted(children, key=lambda x: -x["value"])[:5]}
            for theme, children in theme_data.items()
            if children
        ]

    # ─────────────────────────────────────────────────────────
    # Temporal Trends
    # ─────────────────────────────────────────────────────────

    def temporal_trend(
        self,
        tag: Optional[str] = None,
        question_ids: Optional[List[int]] = None,
    ) -> List[dict]:
        """Monthly trend of a hesitation tag or all primary-signal docs."""
        if tag:
            rows = self._q("""
                SELECT SUBSTR(d.timestamp, 1, 7) as month, COUNT(*) as cnt
                FROM hesitation_tags h
                JOIN documents d ON h.doc_id = d.doc_id
                WHERE h.reason = :tag AND d.timestamp IS NOT NULL
                GROUP BY month
                ORDER BY month
            """, {"tag": tag})
        else:
            rows = self._q("""
                SELECT SUBSTR(d.timestamp, 1, 7) as month, COUNT(*) as cnt
                FROM classifications c
                JOIN documents d ON c.doc_id = d.doc_id
                WHERE c.is_primary_signal = 1 AND d.timestamp IS NOT NULL
                GROUP BY month
                ORDER BY month
            """)

        total_by_month = {}
        all_rows = self._q("""
            SELECT SUBSTR(timestamp, 1, 7) as month, COUNT(*) as cnt
            FROM documents WHERE timestamp IS NOT NULL GROUP BY month
        """)
        for r in all_rows:
            if r[0]:
                total_by_month[r[0]] = int(r[1])

        result = []
        for r in rows:
            month = r[0]
            cnt = int(r[1])
            total = total_by_month.get(month, cnt) or 1
            result.append({
                "month": month,
                "count": cnt,
                "pct":   round(cnt / total * 100, 1),
            })
        return result

    # ─────────────────────────────────────────────────────────
    # Key Quotes
    # ─────────────────────────────────────────────────────────

    def key_quotes(
        self,
        tags: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        max_rating: Optional[float] = None,
        limit: int = 5,
        min_confidence: float = 0.7,
    ) -> List[dict]:
        """Fetch top representative quotes for given tags and optional source/rating filters."""
        where_clauses = ["h.confidence >= :min_conf"]
        params: dict = {"min_conf": min_confidence, "limit": limit}

        if tags:
            tag_placeholders = ", ".join(f":t{i}" for i, _ in enumerate(tags))
            where_clauses.append(f"h.reason IN ({tag_placeholders})")
            for i, t in enumerate(tags):
                params[f"t{i}"] = t

        if sources:
            src_placeholders = ", ".join(f":s{i}" for i, _ in enumerate(sources))
            where_clauses.append(f"d.source IN ({src_placeholders})")
            for i, s in enumerate(sources):
                params[f"s{i}"] = s

        if max_rating is not None:
            where_clauses.append("(d.rating IS NULL OR d.rating <= :max_rating)")
            params["max_rating"] = max_rating

        where_sql = " AND ".join(where_clauses)

        rows = self._q(f"""
            SELECT d.content, d.source, d.source_id, d.timestamp,
                   h.confidence, h.reason, c.inferred_age_group, d.rating
            FROM hesitation_tags h
            JOIN documents d ON h.doc_id = d.doc_id
            JOIN classifications c ON h.doc_id = c.doc_id
            WHERE {where_sql}
            ORDER BY h.confidence DESC, d.rating ASC
            LIMIT :limit
        """, params)

        result = []
        for r in rows:
            content = str(r[0] or "")
            result.append({
                "text":       content[:300] + ("..." if len(content) > 300 else ""),
                "source":     SOURCE_LABELS.get(r[1] or "", r[1] or ""),
                "source_id":  str(r[2] or ""),
                "date":       str(r[3] or "")[:10],
                "confidence": round(float(r[4] or 0), 2),
                "tags":       [r[5]] if r[5] else [],
                "segment":    str(r[6] or "unknown"),
            })
        return result

    def systemic_complaint_quotes(self, limit: int = 6) -> List[dict]:
        """Fetch unique representative negative complaints specifically from secondary sources and low-rated reviews."""
        rows = self._q("""
            SELECT DISTINCT d.doc_id, d.content, d.source, d.source_id, d.timestamp,
                   c.inferred_age_group, d.rating
            FROM documents d
            LEFT JOIN classifications c ON d.doc_id = c.doc_id
            WHERE d.source IN ('pissedconsumer', 'trustpilot', 'reviewsio')
               OR (d.rating IS NOT NULL AND d.rating <= 2.0)
            ORDER BY (CASE WHEN d.source IN ('pissedconsumer', 'trustpilot', 'reviewsio') THEN 0 ELSE 1 END),
                     COALESCE(d.rating, 1.0) ASC,
                     LENGTH(d.content) DESC
            LIMIT 50
        """)

        positive_markers = ["love", "best", "great", "excellent", "amazing", "smooth", "happy with", "good app", "5 star", "5/5", "awesome"]
        seen_contents = set()
        filtered = []

        for r in rows:
            content = str(r[1] or "").strip()
            if len(content) < 30:
                continue

            lower = content.lower()

            # Exclude reviews where other platforms are the primary subject
            if "meesho customer" in lower or ("meesho" in lower and "myntra" not in lower):
                continue

            # Skip duplicates by first 80 chars
            short_prefix = content[:80].lower()
            if short_prefix in seen_contents:
                continue
            seen_contents.add(short_prefix)

            if any(p in lower for p in positive_markers) and (r[6] is None or r[6] > 2.0):
                continue

            # Get tags for this doc
            tag_rows = self._q("SELECT reason, confidence FROM hesitation_tags WHERE doc_id = :did LIMIT 1", {"did": r[0]})
            tag_name = tag_rows[0][0] if tag_rows else "systemic_friction"
            conf = float(tag_rows[0][1]) if tag_rows else 0.85

            filtered.append({
                "text":       content[:300] + ("..." if len(content) > 300 else ""),
                "source":     SOURCE_LABELS.get(r[2] or "", r[2] or ""),
                "source_id":  str(r[3] or ""),
                "date":       str(r[4] or "")[:10],
                "confidence": round(conf, 2),
                "tags":       [tag_name],
                "segment":    str(r[5] or "unknown"),
            })
            if len(filtered) >= limit:
                break

        return filtered

    # ─────────────────────────────────────────────────────────
    # Systemic Gaps (Secondary Sources)
    # ─────────────────────────────────────────────────────────

    def systemic_gap_breakdown(self) -> List[dict]:
        """
        For secondary sources (Trustpilot, PissedConsumer, Reviews.io),
        group the return_policy_concern + trust_deficit + other tags as systemic gaps.
        """
        secondary_sources = ["trustpilot", "pissedconsumer", "reviewsio"]
        placeholders = ", ".join(f":s{i}" for i, _ in enumerate(secondary_sources))
        params = {f"s{i}": s for i, s in enumerate(secondary_sources)}

        rows = self._q(f"""
            SELECT h.reason, COUNT(*) as cnt
            FROM hesitation_tags h
            JOIN documents d ON h.doc_id = d.doc_id
            WHERE d.source IN ({placeholders})
            GROUP BY h.reason
            ORDER BY cnt DESC
        """, params)

        # Map to systemic gap categories
        gap_map = {
            "return_policy_concern": ("Refund/Return Friction", "refund_return", "#ff7849"),
            "trust_deficit":         ("Product Authenticity",   "authenticity_concern", "#2dd4bf"),
            "quality_doubt":         ("Product Quality Issues", "quality_issues", "#a855f7"),
            "information_gap":       ("App/Website Bugs",       "technical_issues", "#3b82f6"),
            "price_sensitivity":     ("Pricing Complaints",     "pricing", "#fbbf24"),
        }

        result = []
        total = sum(int(r[1]) for r in rows) or 1
        for r in rows:
            tag = r[0]
            cnt = int(r[1])
            if tag in gap_map:
                label, gap_tag, color = gap_map[tag]
            else:
                label, gap_tag, color = HESITATION_LABELS.get(tag, tag), tag, "#6b7280"
            result.append({
                "label": label,
                "tag":   gap_tag,
                "count": cnt,
                "pct":   round(cnt / total * 100, 1),
                "color": color,
            })
        return result

    def systemic_source_split(self) -> List[dict]:
        """Breakdown of systemic issues by secondary source."""
        secondary_sources = ["trustpilot", "pissedconsumer", "reviewsio"]
        rows = self._q("""
            SELECT d.source, h.reason, COUNT(*) as cnt
            FROM hesitation_tags h
            JOIN documents d ON h.doc_id = d.doc_id
            WHERE d.source IN ('trustpilot', 'pissedconsumer', 'reviewsio')
            GROUP BY d.source, h.reason
            ORDER BY cnt DESC
        """)

        result = defaultdict(lambda: {"trustpilot": 0, "pissedconsumer": 0, "reviewsio": 0})
        for r in rows:
            src = r[0]
            reason = r[1]
            cnt = int(r[2])
            result[reason][src] = cnt

        return [
            {"issue": HESITATION_LABELS.get(k, k), **v}
            for k, v in result.items()
        ]

    def hesitation_to_systemic_correlation(self) -> List[dict]:
        """Pair each major systemic issue with its correlated hesitation reason."""
        pairs = [
            ("trust_deficit",          "Trust Deficit",           "trustpilot"),
            ("return_policy_concern",  "Return Policy Concern",   "pissedconsumer"),
            ("quality_doubt",          "Quality Doubt",           "reviewsio"),
        ]
        result = []
        for hesitation_tag, label, sec_source in pairs:
            # Count in secondary sources
            r1 = self._q("""
                SELECT COUNT(*) FROM hesitation_tags h
                JOIN documents d ON h.doc_id = d.doc_id
                WHERE h.reason = :tag AND d.source = :src
            """, {"tag": hesitation_tag, "src": sec_source})
            systemic_freq = int(r1[0][0]) if r1 else 0

            # Count in primary sources
            r2 = self._q("""
                SELECT COUNT(*) FROM hesitation_tags WHERE reason = :tag
            """, {"tag": hesitation_tag})
            hesitation_freq = int(r2[0][0]) if r2 else 0

            if hesitation_freq > 0:
                correlation = round(systemic_freq / hesitation_freq, 2)
            else:
                correlation = 0.0

            result.append({
                "systemic_issue":       label,
                "systemic_frequency":   systemic_freq,
                "related_hesitation":   hesitation_tag,
                "hesitation_frequency": hesitation_freq,
                "correlation_hint":     min(correlation, 1.0),
            })
        return result

    def word_cloud_by_intent(self) -> dict:
        """Extract frequent phrases from content for each wishlist intent."""
        import json, re
        intents = ["genuine_purchase_intent", "bookmarking"]
        result = {}
        for intent in intents:
            rows = self._q("""
                SELECT d.content FROM documents d
                JOIN classifications c ON d.doc_id = c.doc_id
                WHERE c.wishlist_intent = :intent
                LIMIT 500
            """, {"intent": intent})

            word_counts = defaultdict(int)
            phrases = [
                "planning to buy", "need this", "saving up", "next paycheck",
                "waiting for sale", "love this", "want it", "will buy",
                "just browsing", "window shopping", "like a pinterest",
                "maybe someday", "never buy", "just saving", "bookmarking",
                "inspiration", "someday", "aspiration",
            ]
            for row in rows:
                content = (row[0] or "").lower()
                for phrase in phrases:
                    if phrase in content:
                        word_counts[phrase] += 1

            result[intent] = sorted(
                [{"text": k, "value": v} for k, v in word_counts.items() if v > 0],
                key=lambda x: -x["value"],
            )[:10]
        return result

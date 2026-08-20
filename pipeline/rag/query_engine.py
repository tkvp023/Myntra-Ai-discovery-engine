"""
Query Engine — retrieves relevant documents from VectorStore and generates
structured answers using Gemini Flash with inline citations and Groq fallback.

Can be used as a library or run directly for CLI testing:
    python -m pipeline.rag.query_engine "Why do users hesitate to buy?"
"""

import sys
import os
import json
from pathlib import Path
from typing import Optional, Dict, List, Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

import google.generativeai as genai
from pipeline.rag.vector_store import VectorStore

TOP_K = 12

SOURCE_DISPLAY = {
    "playstore": ("Play Store", "#ff3f6c"),
    "appstore": ("App Store", "#2dd4bf"),
    "reddit": ("Reddit", "#ff7849"),
    "youtube": ("YouTube", "#a855f7"),
    "pissedconsumer": ("PissedConsumer", "#fbbf24"),
    "trustpilot": ("Trustpilot", "#3b82f6"),
    "reviewsio": ("Reviews.io", "#10b981"),
}


class RAGQueryEngine:
    """Retrieval-Augmented Generation engine for the Myntra corpus with Hybrid SQL + Vector intelligence."""

    def __init__(self):
        self.store = VectorStore()
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        if self.api_key:
            genai.configure(api_key=self.api_key)

    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K,
        segment: Optional[str] = None,
        source: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve top-k documents from VectorStore matching query and filters."""
        return self.store.query(
            query_text=query,
            top_k=top_k,
            segment=segment,
            source=source,
        )

    def _get_quantitative_context(self, query: str, segment: Optional[str] = None) -> str:
        """Fetch real-time quantitative metrics from SQLite to supplement semantic retrieval."""
        try:
            from pipeline.db.connection import get_session
            from pipeline.quantification.aggregator import Aggregator
            session = get_session()
            agg = Aggregator(session)
            
            # Check hesitation tag frequency
            tag_freq = agg.hesitation_frequency(segment=segment if segment != "all" else None)[:6]
            intent_dist = agg.wishlist_intent_distribution(segment=segment if segment != "all" else None)
            
            lines = [
                "QUANTITATIVE AGGREGATES FROM 8,182 CLASSIFIED REVIEWS:",
                f"- Top Friction / Hesitation Drivers: " + ", ".join([f"{t['label']} ({t['pct']}% of issues, {t['count']} docs)" for t in tag_freq]),
                f"- Wishlist Intent Breakdown: " + ", ".join([f"{i['intent'].replace('_', ' ').title()} ({i['pct']}%, {i['count']} docs)" for i in intent_dist[:4]])
            ]
            return "\n".join(lines)
        except Exception as e:
            return ""

    def generate_answer(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        segment: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a structured answer using Gemini Flash with retrieved context and strict guardrails."""

        if not retrieved_docs:
            return {
                "answer": "I couldn't find any relevant reviews matching your query with the current filters. Try relaxing the demographic/source filters or rephrasing your question.",
                "citations": [],
                "filters_applied": {"segment": segment or "all", "source": source or "all"},
                "docs_retrieved": 0,
                "retrieved_docs": [],
                "suggestions": ["Why do users add items to wishlist?", "What causes fit and sizing uncertainty?", "How does Myntra compare to Ajio and Amazon?"],
                "is_out_of_scope": False,
            }

        # Build context from retrieved documents
        context_parts = []
        for i, doc in enumerate(retrieved_docs[:10]):
            src_display = SOURCE_DISPLAY.get(doc["source"], (doc["source"], "#6b7280"))[0]
            tags = doc.get("hesitation_tags", "")
            context_parts.append(
                f"[Review {i+1}] Source: {src_display} | Demographic: {doc['segment']} | "
                f"Tags: {tags or 'none'} | Relevance: {doc['similarity']:.0%}\n"
                f"\"{doc['content_preview'] or doc['content']}\""
            )

        context_block = "\n\n---\n\n".join(context_parts)
        quant_block = self._get_quantitative_context(query, segment)

        # Build source summary for citations
        source_counts: Dict[str, int] = {}
        source_similarities: Dict[str, List[float]] = {}
        for doc in retrieved_docs:
            src = doc["source"]
            source_counts[src] = source_counts.get(src, 0) + 1
            source_similarities.setdefault(src, []).append(doc["similarity"])

        filter_context = ""
        if segment and segment != "all":
            filter_context += f"\nThe user has filtered specifically for the **{segment.replace('_', ' ').title()}** demographic."
        if source and source != "all":
            filter_context += f"\nThe user has filtered for **{source}** reviews only."

        system_prompt = f"""You are an executive consumer intelligence analyst for Myntra's AI Discovery Engine (India's premier fashion e-commerce platform).
You analyze grounded customer feedback across 8,182 reviews (YouTube, Play Store, Reddit, App Store, PissedConsumer, Trustpilot) regarding wishlist habits, cart abandonment, sizing doubts, pricing, return fees, and platform comparisons (Ajio, Amazon, Meesho, Zara).

STRICT SCOPE GUARDRAILS:
1. You MUST answer ONLY questions related to fashion e-commerce, consumer shopping behavior, Myntra features/policies, product uncertainties (fit, fabric, style), returns/refunds, pricing/sales, and platform comparisons.
2. If the user asks an OUT-OF-SCOPE question (e.g. general programming/coding, mathematics, non-fashion trivia, cooking recipes, weather, politics, sports, general assistant chat), you MUST output exactly:
[OUT_OF_SCOPE]
This question is out of scope. I am specifically designed to analyze Myntra customer research, wishlist behavior, sizing/fit uncertainty, return friction, and fashion e-commerce insights across our 8,182 review corpus. Please ask a question related to consumer purchase intent, platform comparisons, or product experience on Myntra.

INSTRUCTIONS FOR IN-SCOPE QUESTIONS:
1. Provide a crisp executive summary followed by numbered analytical findings.
2. Cite exact quantitative metrics from the database (e.g. percentages, counts) in **bold**.
3. Quote authentic customer verbatims with their source using markdown blockquotes: `> "quote" — [Review X] (Source)`.
4. Provide actionable product/UX recommendations for Myntra (e.g. size guides, video reviews, return fee clarity).
5. At the very end of your response, ALWAYS provide 2 to 3 concise, highly relevant follow-up questions formatted exactly like this:
[FOLLOW_UP_SUGGESTIONS]
- Question 1?
- Question 2?
- Question 3?

{filter_context}

{quant_block}

RETRIEVED VOICE-OF-CUSTOMER EVIDENCE ({len(retrieved_docs)} reviews):
{context_block}"""

        user_prompt = f"Question: {query}\n\nSynthesize an actionable analysis based strictly on the voice-of-customer reviews and quantitative evidence above:"

        # Attempt answer generation via Gemini (trying candidate models)
        candidate_gemini_models = [
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-3.7-flash",
            "gemini-flash-latest",
        ]
        answer_text = ""
        for g_model_name in candidate_gemini_models:
            try:
                model = genai.GenerativeModel(g_model_name)
                response = model.generate_content(
                    [{"role": "user", "parts": [system_prompt + "\n\n" + user_prompt]}],
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2,
                        max_output_tokens=1600,
                    ),
                )
                answer_text = response.text.strip()
                if answer_text:
                    break
            except Exception as e:
                print(f"⚠️ Gemini model '{g_model_name}' failed: {type(e).__name__}: {e}", flush=True)

        # If Gemini didn't produce an answer, fallback to Groq
        if not answer_text:
            answer_text = self._fallback_groq(system_prompt, user_prompt)

        # Parse OUT_OF_SCOPE and FOLLOW_UP_SUGGESTIONS
        is_out_of_scope = False
        suggestions = []

        if "[OUT_OF_SCOPE]" in answer_text:
            is_out_of_scope = True
            answer_text = answer_text.replace("[OUT_OF_SCOPE]", "").strip()
            suggestions = [
                "Why do users add items to their wishlist?",
                "What are the main causes of sizing uncertainty?",
                "How do shoppers compare Myntra with Amazon and Ajio?"
            ]
        else:
            if "[FOLLOW_UP_SUGGESTIONS]" in answer_text:
                parts = answer_text.split("[FOLLOW_UP_SUGGESTIONS]")
                answer_text = parts[0].strip()
                suggestion_lines = parts[1].strip().split("\n")
                for s in suggestion_lines:
                    clean_s = s.strip().lstrip("-*•1234567890. ").strip()
                    if clean_s and len(clean_s) > 5:
                        suggestions.append(clean_s)

        if not suggestions:
            suggestions = [
                "How do return processing fees affect cart conversion?",
                "What differences exist between Gen-Z and Millennials?",
                "What are the top unmet customer feature requests?"
            ]

        # Build citations
        citations = []
        for src, count in sorted(source_counts.items(), key=lambda x: -x[1]):
            display_name, color = SOURCE_DISPLAY.get(src, (src, "#6b7280"))
            avg_sim = sum(source_similarities[src]) / len(source_similarities[src])
            citations.append({
                "source": display_name,
                "confidence": round(avg_sim, 2),
                "color": color,
                "count": count,
            })

        # Format full retrieved docs payload for frontend inspector
        formatted_retrieved_docs = []
        for i, doc in enumerate(retrieved_docs):
            src_display = SOURCE_DISPLAY.get(doc["source"], (doc["source"], "#6b7280"))[0]
            formatted_retrieved_docs.append({
                "index": i + 1,
                "doc_id": doc.get("doc_id", ""),
                "source": src_display,
                "raw_source": doc.get("source", ""),
                "source_id": doc.get("source_id", ""),
                "date": doc.get("timestamp", "")[:10] if doc.get("timestamp") else "2026",
                "segment": doc.get("segment", "unknown"),
                "similarity": round(float(doc.get("similarity", 0.8)), 2),
                "tags": [t.strip() for t in doc.get("hesitation_tags", "").split(",") if t.strip()],
                "content": doc.get("content", doc.get("content_preview", "")),
            })

        return {
            "answer": answer_text,
            "citations": citations,
            "filters_applied": {"segment": segment or "all", "source": source or "all"},
            "docs_retrieved": len(retrieved_docs),
            "retrieved_docs": formatted_retrieved_docs,
            "suggestions": suggestions[:3],
            "is_out_of_scope": is_out_of_scope,
        }

    def _fallback_groq(self, system_prompt: str, user_prompt: str) -> str:
        """Attempt answer generation via Groq as fallback with model cascade."""
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not groq_key:
            print("⚠️ Groq fallback skipped — GROQ_API_KEY not set", flush=True)
            return ""

        candidate_groq_models = [
            os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "llama3-70b-8192",
            "llama3-8b-8192",
            "mixtral-8x7b-32768",
        ]

        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            for m in candidate_groq_models:
                try:
                    response = client.chat.completions.create(
                        model=m,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=0.2,
                        max_tokens=1200,
                    )
                    text = response.choices[0].message.content.strip()
                    if text:
                        print(f"✅ Groq fallback succeeded with model: {m}", flush=True)
                        return text
                except Exception as model_err:
                    print(f"⚠️ Groq model '{m}' failed: {model_err}", flush=True)
            return ""
        except Exception as e:
            print(f"⚠️ Groq client initialization error: {type(e).__name__}: {e}", flush=True)
            return ""

    def ask(
        self,
        query: str,
        segment: Optional[str] = None,
        source: Optional[str] = None,
        top_k: int = TOP_K,
    ) -> Dict[str, Any]:
        """Full RAG pipeline: retrieve -> generate -> return structured answer."""
        retrieved = self.retrieve(query, top_k=top_k, segment=segment, source=source)
        return self.generate_answer(query, retrieved, segment=segment, source=source)


_engine: Optional[RAGQueryEngine] = None

def get_engine() -> RAGQueryEngine:
    global _engine
    if _engine is None:
        _engine = RAGQueryEngine()
        _engine.store.load()
    return _engine


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="RAG Query Engine CLI")
    parser.add_argument("query", type=str, help="Question to ask")
    parser.add_argument("--segment", type=str, default=None)
    parser.add_argument("--source", type=str, default=None)
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    engine = get_engine()
    result = engine.ask(args.query, segment=args.segment, source=args.source)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*60}")
        print(f"Query: {args.query}")
        print(f"Docs retrieved: {result['docs_retrieved']}")
        print(f"{'='*60}\n")
        print(result["answer"])
        print(f"\n{'─'*40}")
        print("Sources:")
        for c in result["citations"]:
            print(f"  • {c['source']} ({c['count']} docs, {c['confidence']:.0%} avg relevance)")

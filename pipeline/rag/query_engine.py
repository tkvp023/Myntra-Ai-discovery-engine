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
    """Retrieval-Augmented Generation engine for the Myntra corpus."""

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

    def generate_answer(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        segment: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a structured answer using Gemini Flash with retrieved context."""

        if not retrieved_docs:
            return {
                "answer": "I couldn't find any relevant reviews matching your query with the current filters. Try relaxing the demographic/source filters or rephrasing your question.",
                "citations": [],
                "filters_applied": {"segment": segment or "all", "source": source or "all"},
                "docs_retrieved": 0,
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

        system_prompt = f"""You are an executive consumer intelligence analyst for Myntra (India's premier fashion e-commerce platform).
You provide grounded, executive-grade answers about customer behavior, wishlist-to-purchase hesitation, sizing issues, returns, and pricing.

All your answers MUST be synthesized directly from the retrieved customer reviews provided below.

INSTRUCTIONS:
1. Provide a crisp executive summary followed by numbered findings highlighting core drivers.
2. Quote authentic customer verbatims with their source using markdown blockquotes: `> "quote" — Source`.
3. Highlight metrics, proportions, and recurring tag themes in **bold**.
4. Frame findings with actionable product & UX recommendations (e.g. Fit tools, return policy transparency, dynamic pricing).
5. If the evidence shows sharp demographic splits (Gen-Z vs Millennials vs Gen-X), call them out explicitly.
{filter_context}

RETRIEVED VOICE-OF-CUSTOMER EVIDENCE ({len(retrieved_docs)} reviews):
{context_block}"""

        user_prompt = f"Question: {query}\n\nSynthesize an actionable analysis based strictly on the voice-of-customer reviews above:"

        # Attempt answer generation via Gemini (trying candidate models)
        candidate_gemini_models = [
            os.getenv("GEMINI_MODEL", "gemini-3.7-flash"),
            "gemini-3.6-flash",
            "gemini-2.5-flash",
            "gemini-1.5-flash",
        ]
        answer_text = ""
        for g_model_name in candidate_gemini_models:
            try:
                model = genai.GenerativeModel(g_model_name)
                response = model.generate_content(
                    [{"role": "user", "parts": [system_prompt + "\n\n" + user_prompt]}],
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2,
                        max_output_tokens=1500,
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

        # If all LLMs fail, return raw reviews
        if not answer_text:
            print("⚠️ All LLM fallbacks failed — returning raw reviews", flush=True)
            answer_text = f"Analyzed {len(retrieved_docs)} relevant reviews from the corpus:\n\n"
            for i, doc in enumerate(retrieved_docs[:5]):
                src_display = SOURCE_DISPLAY.get(doc["source"], (doc["source"],))[0]
                answer_text += f"{i+1}. **{src_display}**:\n> \"{(doc['content_preview'] or doc['content'])[:180]}...\"\n\n"

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

        return {
            "answer": answer_text,
            "citations": citations,
            "filters_applied": {"segment": segment or "all", "source": source or "all"},
            "docs_retrieved": len(retrieved_docs),
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

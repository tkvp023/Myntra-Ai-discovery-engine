"""
FastAPI sidecar server for the RAG query engine.

Runs on port 8000 alongside the Next.js dashboard (port 3000).
Loads VectorStore once on startup for sub-millisecond retrieval.

Usage:
    python -m pipeline.rag.server
    # or
    uvicorn pipeline.rag.server:app --host 0.0.0.0 --port 8000
"""

import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager

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

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import time

from pipeline.rag.query_engine import get_engine

# ─────────────────────────────────────────────────────────────
# Lifespan — warm-load VectorStore on startup
# ─────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-load VectorStore on server start."""
    print("🚀 Initializing RAG engine (VectorStore + Gemini embeddings)...")
    engine = get_engine()
    count = engine.store.count()
    print(f"✅ RAG engine ready — {count:,} vectors in VectorStore")
    yield
    # Shutdown cleanup (if needed in the future)

# ─────────────────────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Discovery Engine — RAG API",
    description="Retrieval-Augmented Generation over 8,182 classified Myntra reviews",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# Request / Response Models
# ─────────────────────────────────────────────────────────────

class AskFilters(BaseModel):
    segment: Optional[str] = Field(None, description="User segment filter: gen_z, millennial, gen_x, or all")
    source: Optional[str] = Field(None, description="Source filter: Play Store, Reddit, YouTube, App Store, PissedConsumer, or all")

class AskRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500, description="Natural-language question")
    filters: Optional[AskFilters] = None

class RetrievedDoc(BaseModel):
    index: int
    doc_id: str
    source: str
    raw_source: str
    source_id: str
    date: str
    segment: str
    similarity: float
    tags: List[str]
    content: str

class AskResponse(BaseModel):
    answer: str
    citations: List[Citation]
    filters_applied: dict
    docs_retrieved: int
    retrieved_docs: List[RetrievedDoc] = []
    suggestions: List[str] = []
    is_out_of_scope: bool = False
    latency_ms: int


# ─────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────

@app.post("/api/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """Answer a natural-language question using RAG over the Myntra corpus."""
    start = time.time()

    engine = get_engine()

    segment = request.filters.segment if request.filters else None
    source = request.filters.source if request.filters else None

    try:
        result = engine.ask(
            query=request.query,
            segment=segment,
            source=source,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

    elapsed_ms = int((time.time() - start) * 1000)

    return AskResponse(
        answer=result["answer"],
        citations=[Citation(**c) for c in result["citations"]],
        filters_applied=result["filters_applied"],
        docs_retrieved=result["docs_retrieved"],
        retrieved_docs=[RetrievedDoc(**d) for d in result.get("retrieved_docs", [])],
        suggestions=result.get("suggestions", []),
        is_out_of_scope=result.get("is_out_of_scope", False),
        latency_ms=elapsed_ms,
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    engine = get_engine()
    count = engine.store.count()
    return {
        "status": "ok",
        "vectors": count,
        "model": "gemini-embedding-001 + gemini-3.7-flash",
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "pipeline.rag.server:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
    )

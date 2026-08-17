import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { query, filters } = body;

    if (!query || typeof query !== 'string' || query.trim().length === 0) {
      return NextResponse.json({ error: 'Query is required' }, { status: 400 });
    }

    // Proxy request to Python RAG FastAPI backend
    const ragBackendUrl = process.env.RAG_API_URL || process.env.NEXT_PUBLIC_RAG_API_URL || 'http://localhost:8000';
    try {
      const pyResp = await fetch(`${ragBackendUrl}/api/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, filters }),
        signal: AbortSignal.timeout(15000),
      });

      if (pyResp.ok) {
        const data = await pyResp.json();
        return NextResponse.json(data);
      }
    } catch (fetchErr) {
      // FastAPI server not reachable or timed out
      console.warn('FastAPI backend not reachable at', ragBackendUrl, ':', fetchErr);
    }

    return NextResponse.json(
      {
        error: 'RAG service temporarily unavailable. Please make sure the backend server is running.',
      },
      { status: 503 }
    );
  } catch (err: any) {
    return NextResponse.json({ error: err.message || 'Internal server error' }, { status: 500 });
  }
}

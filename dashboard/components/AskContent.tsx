'use client';
import { useState, useRef, useEffect } from 'react';

const SUGGESTED = [
  'Why do users hesitate to buy after wishlisting?',
  'What is the top sizing issue Gen-Z faces in ethnic wear?',
  'Which platform do users compare Myntra with most?',
  'What are the top unmet needs in fashion discovery?',
  'How does price sensitivity differ by demographic segment?',
  'What systemic issues appear in customer complaint forums?',
];

interface Citation {
  source: string;
  confidence: number;
  color: string;
  count: number;
}

interface Message {
  role: 'user' | 'ai';
  content: string;
  citations?: Citation[];
  latencyMs?: number;
  docsRetrieved?: number;
}

function MarkdownText({ text }: { text: string }) {
  // Convert standard markdown structures into styled HTML elements
  const html = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^> (.+)$/gm, '<blockquote style="border-left:3px solid var(--pink);padding-left:12px;margin:10px 0;color:var(--text-secondary);font-style:italic;background:rgba(255,63,108,0.04);padding:8px 12px;border-radius:0 8px 8px 0;">$1</blockquote>')
    .replace(/^(\d+)\. (.+)$/gm, '<div style="padding:3px 0"><span style="color:var(--pink);font-weight:700;margin-right:6px;">$1.</span> $2</div>')
    .replace(/^- (.+)$/gm, '<div style="padding:2px 0;padding-left:12px;position:relative"><span style="position:absolute;left:0;color:var(--teal)">•</span> $1</div>')
    .replace(/\n\n/g, '<br/><br/>');
  return <span dangerouslySetInnerHTML={{ __html: html }} />;
}

function CitationBadges({ citations, latencyMs, docsRetrieved }: { citations: Citation[]; latencyMs?: number; docsRetrieved?: number }) {
  return (
    <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid var(--border)', display: 'flex', flexDirection: 'column', gap: 6 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Grounding Citations ({docsRetrieved || citations.reduce((acc, c) => acc + (c.count || 1), 0)} evidence docs retrieved)
        </span>
        {latencyMs !== undefined && (
          <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>
            ⚡ {latencyMs}ms
          </span>
        )}
      </div>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {citations.map((c, i) => (
          <span
            key={`${c.source}-${i}`}
            style={{
              background: `${c.color}15`,
              border: `1px solid ${c.color}40`,
              color: c.color,
              borderRadius: 14,
              padding: '3px 10px',
              fontSize: 11,
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: c.color }} />
            {c.source}
            {c.count > 0 && <span style={{ opacity: 0.7, fontSize: 10 }}>({c.count})</span>}
            <span style={{ opacity: 0.85, fontSize: 10, background: 'rgba(0,0,0,0.2)', padding: '1px 5px', borderRadius: 6 }}>
              {(c.confidence * 100).toFixed(0)}% relevance
            </span>
          </span>
        ))}
      </div>
    </div>
  );
}

export default function AskContent() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [segment, setSegment] = useState('all');
  const [source, setSource] = useState('all');
  const [copied, setCopied] = useState<number | null>(null);
  const [isLive, setIsLive] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;
    const q = text.trim();
    setInput('');
    setMessages((m) => [...m, { role: 'user', content: q }]);
    setLoading(true);

    try {
      // First attempt direct call to FastAPI backend
      const directUrl = process.env.NEXT_PUBLIC_RAG_API_URL || 'http://localhost:8000';
      let res = await fetch(`${directUrl}/api/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: q,
          filters: { segment, source },
        }),
      }).catch(() => null);

      // If direct call fails, try Next.js proxy route
      if (!res || !res.ok) {
        res = await fetch('/api/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: q,
            filters: { segment, source },
          }),
        }).catch(() => null);
      }

      if (res && res.ok) {
        const data = await res.json();
        setIsLive(true);
        setMessages((m) => [
          ...m,
          {
            role: 'ai',
            content: data.answer,
            citations: data.citations,
            latencyMs: data.latency_ms,
            docsRetrieved: data.docs_retrieved,
          },
        ]);
      } else {
        throw new Error('RAG backend not responding');
      }
    } catch (err: any) {
      setIsLive(false);
      setMessages((m) => [
        ...m,
        {
          role: 'ai',
          content: `⚠️ **RAG Server Notice**: The Python intelligence backend (FastAPI on port 8000) is currently initializing or offline. To start it, run \`python -m pipeline.rag.server\` in the terminal.`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const copyResponse = (idx: number, text: string) => {
    navigator.clipboard.writeText(text.replace(/\*\*/g, '').replace(/\*/g, ''));
    setCopied(idx);
    setTimeout(() => setCopied(null), 1500);
  };

  return (
    <div className="container" style={{ paddingTop: 32, paddingBottom: 64 }}>
      <div className="page-header">
        <h1>
          <span style={{ background: 'var(--gradient-brand)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Ask
          </span>{' '}
          the Data
        </h1>
        <p style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
          <span>Natural-language RAG over 8,182 classified voice-of-customer reviews</span>
          <span
            style={{
              background: isLive ? 'rgba(16,185,129,0.1)' : 'rgba(251,191,36,0.1)',
              border: `1px solid ${isLive ? 'rgba(16,185,129,0.3)' : 'rgba(251,191,36,0.3)'}`,
              borderRadius: 12,
              padding: '2px 10px',
              fontSize: 12,
              color: isLive ? 'var(--green)' : 'var(--yellow)',
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
            }}
          >
            <span
              style={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                background: isLive ? 'var(--green)' : 'var(--yellow)',
                animation: isLive ? 'pulse 2s infinite' : 'none',
              }}
            />
            {isLive ? 'Live RAG Engine (Gemini 2.0 Flash)' : 'RAG Standby'}
          </span>
        </p>
      </div>

      <div className="card" style={{ maxWidth: 900, margin: '0 auto', backdropFilter: 'blur(16px)' }}>
        {/* Suggested queries */}
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
            <p style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Suggested executive queries
            </p>
            {messages.length > 0 && (
              <button
                onClick={clearChat}
                style={{
                  background: 'none',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--text-muted)',
                  fontSize: 11,
                  padding: '3px 10px',
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                }}
              >
                Clear chat
              </button>
            )}
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {SUGGESTED.map((q) => (
              <button
                key={q}
                onClick={() => sendMessage(q)}
                disabled={loading}
                style={{
                  background: 'var(--glass-bg)',
                  border: '1px solid var(--border)',
                  borderRadius: 20,
                  padding: '6px 14px',
                  fontSize: 12,
                  color: 'var(--text-secondary)',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  transition: 'all 0.15s',
                  opacity: loading ? 0.5 : 1,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                }}
                onMouseEnter={(e) => {
                  if (!loading) (e.currentTarget.style.borderColor = 'var(--pink)');
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget.style.borderColor = 'var(--border)');
                }}
              >
                <span>💡</span> {q}
              </button>
            ))}
          </div>
        </div>

        {/* Message history */}
        <div style={{ minHeight: 360, maxHeight: 560, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: 18 }}>
          {messages.length === 0 && (
            <div className="empty-state" style={{ opacity: 0.7, padding: '40px 20px' }}>
              <div className="empty-state-icon" style={{ fontSize: 44 }}>🧠</div>
              <div className="empty-state-text" style={{ fontSize: 16, fontWeight: 600 }}>Query the Myntra Consumer Knowledge Graph</div>
              <div style={{ fontSize: 13, color: 'var(--text-muted)', maxWidth: 440, marginTop: 6, lineHeight: 1.5 }}>
                Ask questions about wishlist hesitation, sizing uncertainties, cross-platform pricing, return friction, or unmet needs. Every response is synthesized with exact grounded citations.
              </div>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
              {msg.role === 'user' ? (
                <div className="chat-bubble-user" style={{ maxWidth: '80%', padding: '10px 16px', fontSize: 14 }}>
                  {msg.content}
                </div>
              ) : (
                <div
                  className="chat-bubble-ai"
                  style={{
                    maxWidth: '92%',
                    padding: '16px 20px',
                    fontSize: 13.5,
                    lineHeight: 1.6,
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius-md)',
                  }}
                >
                  <MarkdownText text={msg.content} />
                  {msg.citations && msg.citations.length > 0 && (
                    <CitationBadges
                      citations={msg.citations}
                      latencyMs={msg.latencyMs}
                      docsRetrieved={msg.docsRetrieved}
                    />
                  )}
                  <div style={{ marginTop: 10, display: 'flex', justifyContent: 'flex-end' }}>
                    <button
                      className="copy-btn"
                      onClick={() => copyResponse(i, msg.content)}
                      style={{
                        background: 'rgba(255,255,255,0.04)',
                        border: '1px solid var(--border)',
                        borderRadius: 6,
                        color: 'var(--text-muted)',
                        padding: '3px 10px',
                        fontSize: 11,
                        cursor: 'pointer',
                      }}
                    >
                      {copied === i ? '✓ Copied' : '📋 Copy Analysis'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
              <div
                className="chat-bubble-ai"
                style={{
                  display: 'flex',
                  gap: 8,
                  alignItems: 'center',
                  padding: '14px 20px',
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius-md)',
                }}
              >
                <div style={{ display: 'flex', gap: 4 }}>
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                </div>
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  Searching 8,182 vector embeddings & synthesizing insights with Gemini Flash...
                </span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input + Filters */}
        <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border)', background: 'rgba(0,0,0,0.1)' }}>
          <div style={{ display: 'flex', gap: 10 }}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage(input);
                }
              }}
              placeholder="Ask anything about wishlist drops, fit issues, Gen-Z vs Millennial patterns..."
              style={{
                flex: 1,
                background: 'var(--glass-bg)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-md)',
                padding: '12px 16px',
                color: 'var(--text-primary)',
                fontSize: 14,
                outline: 'none',
                transition: 'border-color 0.15s',
              }}
              onFocus={(e) => {
                (e.target as HTMLInputElement).style.borderColor = 'var(--pink)';
              }}
              onBlur={(e) => {
                (e.target as HTMLInputElement).style.borderColor = 'var(--border)';
              }}
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || loading}
              style={{
                background: loading ? 'var(--glass-bg)' : 'var(--gradient-brand)',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                color: '#fff',
                padding: '12px 24px',
                fontSize: 14,
                fontWeight: 700,
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: !input.trim() ? 0.5 : 1,
                transition: 'opacity 0.15s',
                minWidth: 90,
              }}
            >
              {loading ? '···' : 'Ask →'}
            </button>
          </div>

          {/* Filter row */}
          <div style={{ display: 'flex', gap: 12, marginTop: 12, alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Vector Filter:
            </span>
            <select
              className="chat-filter-select"
              value={segment}
              onChange={(e) => setSegment(e.target.value)}
              aria-label="Filter by demographic segment"
              style={{
                background: 'var(--glass-bg)',
                border: '1px solid var(--border)',
                color: 'var(--text-secondary)',
                borderRadius: 8,
                padding: '4px 10px',
                fontSize: 12,
              }}
            >
              <option value="all">All Demographics</option>
              <option value="gen_z">Gen-Z Only</option>
              <option value="millennial">Millennial Only</option>
              <option value="gen_x">Gen-X Only</option>
            </select>
            <select
              className="chat-filter-select"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              aria-label="Filter by review source"
              style={{
                background: 'var(--glass-bg)',
                border: '1px solid var(--border)',
                color: 'var(--text-secondary)',
                borderRadius: 8,
                padding: '4px 10px',
                fontSize: 12,
              }}
            >
              <option value="all">All Sources (7 Platforms)</option>
              <option value="Play Store">Play Store</option>
              <option value="Reddit">Reddit</option>
              <option value="YouTube">YouTube</option>
              <option value="App Store">App Store</option>
              <option value="PissedConsumer">PissedConsumer</option>
              <option value="Trustpilot">Trustpilot</option>
              <option value="Reviews.io">Reviews.io</option>
            </select>
            <span
              style={{
                marginLeft: 'auto',
                fontSize: 11,
                color: 'var(--text-muted)',
                display: 'flex',
                alignItems: 'center',
                gap: 4,
              }}
            >
              Grounding: 8,182 Clean Docs
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

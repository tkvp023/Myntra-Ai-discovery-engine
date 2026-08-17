'use client';
import { useState } from 'react';

interface Quote {
  text: string; source: string; source_id?: string;
  date: string; confidence: number; tags: string[]; segment: string;
}

const SOURCE_COLORS: Record<string, string> = {
  'Play Store': '#ff3f6c', 'Reddit': '#ff7849', 'YouTube': '#a855f7',
  'App Store': '#2dd4bf', 'Trustpilot': '#3b82f6', 'PissedConsumer': '#fbbf24', 'Reviews.io': '#6b7280',
};
const SEGMENT_COLORS: Record<string, string> = {
  gen_z: '#a855f7', millennial: '#3b82f6', gen_x: '#2dd4bf', unknown: '#6b7280',
};

function ConfBadge({ conf }: { conf: number }) {
  const cls = conf >= 0.8 ? 'badge-conf-high' : conf >= 0.6 ? 'badge-conf-mid' : 'badge-conf-low';
  return <span className={`badge ${cls}`}>{(conf * 100).toFixed(0)}%</span>;
}

function QuoteCard({ quote, accent }: { quote: Quote; accent?: string }) {
  const [expanded, setExpanded] = useState(false);
  const isLong = quote.text.length > 180;
  const display = (!expanded && isLong) ? quote.text.slice(0, 180) + '…' : quote.text;

  return (
    <div className="quote-card" style={{ borderLeftColor: accent || SOURCE_COLORS[quote.source] || 'var(--pink)' }}>
      <p className="quote-text">"{display}"</p>
      {isLong && (
        <button
          onClick={() => setExpanded(!expanded)}
          style={{ background: 'none', border: 'none', color: 'var(--pink)', fontSize: 11, cursor: 'pointer', marginBottom: 8 }}
        >
          {expanded ? 'Show less' : 'Read more'}
        </button>
      )}
      <div className="quote-meta">
        <span className="badge badge-source" style={{ background: `${SOURCE_COLORS[quote.source]}22`, color: SOURCE_COLORS[quote.source] || 'var(--text-secondary)' }}>
          {quote.source}
        </span>
        {quote.segment !== 'unknown' && (
          <span className="badge" style={{ background: `${SEGMENT_COLORS[quote.segment]}22`, color: SEGMENT_COLORS[quote.segment] }}>
            {quote.segment.replace('_', ' ')}
          </span>
        )}
        <ConfBadge conf={quote.confidence} />
        <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 'auto' }}>{quote.date}</span>
      </div>
    </div>
  );
}

export default function QuoteCarousel({ quotes }: { quotes: Quote[] }) {
  const [idx, setIdx] = useState(0);
  if (!quotes || quotes.length === 0) return (
    <div className="empty-state"><div className="empty-state-icon">💬</div><div className="empty-state-text">No quotes available</div></div>
  );

  return (
    <div>
      <QuoteCard quote={quotes[idx]} />
      {quotes.length > 1 && (
        <div style={{ display: 'flex', gap: 8, marginTop: 12, justifyContent: 'center', alignItems: 'center' }}>
          <button
            onClick={() => setIdx((i) => Math.max(0, i - 1))}
            disabled={idx === 0}
            style={{ background: 'var(--glass-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text-secondary)', width: 32, height: 32, cursor: 'pointer', fontSize: 14, opacity: idx === 0 ? 0.3 : 1 }}
          >←</button>
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{idx + 1} / {quotes.length}</span>
          <button
            onClick={() => setIdx((i) => Math.min(quotes.length - 1, i + 1))}
            disabled={idx === quotes.length - 1}
            style={{ background: 'var(--glass-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text-secondary)', width: 32, height: 32, cursor: 'pointer', fontSize: 14, opacity: idx === quotes.length - 1 ? 0.3 : 1 }}
          >→</button>
        </div>
      )}
    </div>
  );
}

export { QuoteCard };

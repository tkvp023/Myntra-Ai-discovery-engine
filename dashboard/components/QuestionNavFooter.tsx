'use client';
import Link from 'next/link';
import { QUESTION_META } from '@/lib/constants';

interface QuestionNavFooterProps {
  currentId: number;
}

export default function QuestionNavFooter({ currentId }: QuestionNavFooterProps) {
  const prevId = currentId > 1 ? currentId - 1 : null;
  const nextId = currentId < 10 ? currentId + 1 : null;

  const currentMeta = QUESTION_META[currentId];
  const prevMeta = prevId ? QUESTION_META[prevId] : null;
  const nextMeta = nextId ? QUESTION_META[nextId] : null;

  return (
    <div
      style={{
        marginTop: 40,
        paddingTop: 24,
        borderTop: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
      }}
    >
      {/* Ask AI Banner Bar */}
      <div
        className="card"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '16px 22px',
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-md)',
          flexWrap: 'wrap',
          gap: 12,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontSize: 24 }}>🤖</span>
          <div>
            <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>
              Explore Grounded Evidence with AI Assistant
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
              Ask custom follow-ups regarding {currentMeta?.short || `Question ${currentId}`} and inspect source citations.
            </div>
          </div>
        </div>

        <Link
          href={`/ask?q=${encodeURIComponent(currentMeta?.text || '')}`}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            padding: '8px 18px',
            borderRadius: 'var(--radius-sm)',
            background: 'var(--gradient-brand)',
            color: '#fff',
            fontWeight: 700,
            fontSize: 13,
            textDecoration: 'none',
            transition: 'opacity 0.15s ease',
          }}
        >
          <span>Deep-Dive in AI Chat</span>
          <span>→</span>
        </Link>
      </div>

      {/* Prev / Next Navigation Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: prevMeta && nextMeta ? '1fr 1fr' : '1fr',
          gap: 16,
        }}
      >
        {prevMeta && prevId && (
          <Link
            href={`/questions/${prevId}`}
            className="card"
            style={{
              padding: '16px 20px',
              textDecoration: 'none',
              display: 'flex',
              flexDirection: 'column',
              gap: 4,
              transition: 'border-color var(--t-fast), background var(--t-fast)',
            }}
          >
            <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              ← Previous Inquiry (Q{prevId})
            </div>
            <div style={{ fontSize: 14.5, fontWeight: 700, color: 'var(--text-primary)' }}>
              {prevMeta.short}
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              {prevMeta.text}
            </div>
          </Link>
        )}

        {nextMeta && nextId && (
          <Link
            href={`/questions/${nextId}`}
            className="card"
            style={{
              padding: '16px 20px',
              textDecoration: 'none',
              display: 'flex',
              flexDirection: 'column',
              gap: 4,
              textAlign: prevMeta ? 'right' : 'left',
              transition: 'border-color var(--t-fast), background var(--t-fast)',
            }}
          >
            <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Next Inquiry (Q{nextId}) →
            </div>
            <div style={{ fontSize: 14.5, fontWeight: 700, color: 'var(--text-primary)' }}>
              {nextMeta.short}
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              {nextMeta.text}
            </div>
          </Link>
        )}
      </div>
    </div>
  );
}

'use client';
import Link from 'next/link';
import { QUESTION_META } from '@/lib/constants';

export default function QuestionGrid() {
  const questions = Object.entries(QUESTION_META).map(([idStr, meta]) => ({
    id: parseInt(idStr),
    ...meta,
  }));

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12 }}>
      {questions.map((q) => {
        const isBoth = q.sourceType === 'both';
        return (
          <Link
            key={q.id}
            href={`/questions/${q.id}`}
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: 8,
              padding: '14px 16px',
              background: 'var(--glass-bg)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)',
              textDecoration: 'none',
              transition: 'background var(--t-fast), border-color var(--t-fast), transform 0.15s ease',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.background = 'var(--bg-card-hover)';
              (e.currentTarget as HTMLElement).style.borderColor = q.color;
              (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.background = 'var(--glass-bg)';
              (e.currentTarget as HTMLElement).style.borderColor = 'var(--border)';
              (e.currentTarget as HTMLElement).style.transform = 'translateY(0)';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: 8,
                    background: `${q.color}22`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 13,
                    fontWeight: 800,
                    color: q.color,
                    fontFamily: 'Outfit',
                    flexShrink: 0,
                  }}
                >
                  Q{q.id}
                </span>
                <span style={{ fontSize: 13.5, color: 'var(--text-primary)', fontWeight: 600 }}>
                  {q.short}
                </span>
              </div>
            </div>

            {/* Source derivation indicator */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 2 }}>
              <span
                style={{
                  fontSize: 10.5,
                  fontWeight: 600,
                  padding: '2px 8px',
                  borderRadius: 12,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 4,
                  background: isBoth ? 'rgba(6, 182, 212, 0.12)' : 'rgba(168, 85, 247, 0.12)',
                  border: `1px solid ${isBoth ? 'rgba(6, 182, 212, 0.3)' : 'rgba(168, 85, 247, 0.3)'}`,
                  color: isBoth ? '#06b6d4' : '#c084fc',
                }}
              >
                <span>{isBoth ? '🔄' : '⚡'}</span>
                {isBoth ? 'Both Sources (4 Primary + 1 Secondary)' : '4 Primary Sources'}
              </span>
            </div>
          </Link>
        );
      })}
    </div>
  );
}

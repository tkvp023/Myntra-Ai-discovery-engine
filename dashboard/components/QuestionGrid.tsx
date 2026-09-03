'use client';
import Link from 'next/link';
import { QUESTION_META } from '@/lib/constants';

const Q_ICONS: Record<number, string> = {
  1: '🎯',
  2: '🛑',
  3: '🔍',
  4: '⏳',
  5: '⚖️',
  6: '🌐',
  7: '📊',
  8: '🛒',
  9: '📱',
  10: '💡',
};

const Q_SUBTITLES: Record<number, string> = {
  1: 'Why users shortlist vs purchase items immediately',
  2: 'Core friction points & root causes blocking checkout',
  3: 'Fabric, sizing, and quality doubts before buying',
  4: 'Price drops, flash sales, and timing hesitations',
  5: 'How users benchmark vs Ajio, Meesho, and Amazon',
  6: 'YouTube try-ons, Instagram reels, and peer validation',
  7: 'Relative weights of fit, price, style, and returns',
  8: 'Active conversion funnel vs passive bookmarking',
  9: 'Side-by-side platform friction & behavior breakdown',
  10: 'High-frequency customer feature requests & gaps',
};

export default function QuestionGrid() {
  const questions = Object.entries(QUESTION_META).map(([idStr, meta]) => ({
    id: parseInt(idStr),
    ...meta,
    icon: Q_ICONS[parseInt(idStr)] || '📌',
    subtitle: Q_SUBTITLES[parseInt(idStr)] || meta.text,
  }));

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        gap: 14,
      }}
    >
      {questions.map((q) => {
        const isBoth = q.sourceType === 'both';
        return (
          <Link
            key={q.id}
            href={`/questions/${q.id}`}
            style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              padding: '16px 18px',
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderTop: '1px solid var(--border-highlight)',
              borderRadius: 'var(--radius-md)',
              textDecoration: 'none',
              transition: 'transform var(--t-fast), border-color var(--t-fast), box-shadow var(--t-fast)',
              position: 'relative',
              overflow: 'hidden',
              minHeight: 140,
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.background = 'var(--bg-card-hover)';
              (e.currentTarget as HTMLElement).style.borderColor = q.color;
              (e.currentTarget as HTMLElement).style.boxShadow = `0 12px 28px -6px rgba(0, 0, 0, 0.45), 0 0 16px ${q.color}22`;
              (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.background = 'var(--bg-card)';
              (e.currentTarget as HTMLElement).style.borderColor = 'var(--border)';
              (e.currentTarget as HTMLElement).style.boxShadow = 'none';
              (e.currentTarget as HTMLElement).style.transform = 'translateY(0)';
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span
                    style={{
                      width: 28,
                      height: 28,
                      borderRadius: 8,
                      background: `${q.color}20`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: 12,
                      fontWeight: 800,
                      color: q.color,
                      fontFamily: 'Outfit',
                      flexShrink: 0,
                    }}
                  >
                    Q{q.id}
                  </span>
                  <span style={{ fontSize: 14.5, color: 'var(--text-primary)', fontWeight: 700, letterSpacing: '-0.01em' }}>
                    {q.short}
                  </span>
                </div>
                <span style={{ fontSize: 16 }}>{q.icon}</span>
              </div>

              <p
                style={{
                  fontSize: 12,
                  color: 'var(--text-secondary)',
                  lineHeight: 1.45,
                  margin: 0,
                  marginBottom: 12,
                }}
              >
                {q.subtitle}
              </p>
            </div>

            {/* Source derivation chip */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: 8, borderTop: '1px solid var(--border)' }}>
              <span
                style={{
                  fontSize: 11,
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
                {isBoth ? 'Both Sources (Primary + Secondary)' : '4 Primary Sources'}
              </span>

              <span style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 700 }}>
                →
              </span>
            </div>
          </Link>
        );
      })}
    </div>
  );
}

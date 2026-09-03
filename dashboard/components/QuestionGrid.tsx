'use client';
import { useState } from 'react';
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

const Q_CATEGORIES: Record<number, { name: string; tag: string; color: string }> = {
  1: { name: 'Funnel Dynamics', tag: 'Motivation', color: '#ff3f6c' },
  2: { name: 'Funnel Dynamics', tag: 'Conversion Blocker', color: '#ff7849' },
  3: { name: 'Funnel Dynamics', tag: 'Product Uncertainty', color: '#a855f7' },
  4: { name: 'Funnel Dynamics', tag: 'Price & Timing', color: '#2dd4bf' },
  5: { name: 'Funnel Dynamics', tag: 'Competitor Benchmark', color: '#3b82f6' },
  6: { name: 'Signal Dynamics', tag: 'External Discovery', color: '#fbbf24' },
  7: { name: 'Signal Dynamics', tag: 'Factor Weighting', color: '#ec4899' },
  8: { name: 'Signal Dynamics', tag: 'Purchase Intent', color: '#84cc16' },
  9: { name: 'Signal Dynamics', tag: 'Cross-Platform', color: '#f97316' },
  10: { name: 'Signal Dynamics', tag: 'Unmet Opportunities', color: '#8b5cf6' },
};

export default function QuestionGrid() {
  const [filter, setFilter] = useState<'all' | 'funnel' | 'signal'>('all');

  const questions = Object.entries(QUESTION_META).map(([idStr, meta]) => {
    const id = parseInt(idStr);
    const cat = Q_CATEGORIES[id] || { name: 'Strategic', tag: 'Intelligence', color: meta.color };
    return {
      id,
      ...meta,
      icon: Q_ICONS[id] || '📌',
      subtitle: Q_SUBTITLES[id] || meta.text,
      category: cat.name,
      categoryTag: cat.tag,
      categoryColor: cat.color,
    };
  });

  const filteredQuestions = questions.filter((q) => {
    if (filter === 'funnel') return q.category === 'Funnel Dynamics';
    if (filter === 'signal') return q.category === 'Signal Dynamics';
    return true;
  });

  return (
    <div>
      {/* Category Tab Filters */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 12,
          marginBottom: 16,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button
            onClick={() => setFilter('all')}
            style={{
              padding: '6px 14px',
              borderRadius: 20,
              fontSize: 12,
              fontWeight: 700,
              cursor: 'pointer',
              border: `1px solid ${filter === 'all' ? 'var(--brand-primary)' : 'var(--border)'}`,
              background: filter === 'all' ? 'var(--theme-accent-bg)' : 'transparent',
              color: filter === 'all' ? 'var(--brand-primary)' : 'var(--text-secondary)',
              transition: 'all 0.15s ease',
            }}
          >
            All 10 Inquiries (10)
          </button>
          <button
            onClick={() => setFilter('funnel')}
            style={{
              padding: '6px 14px',
              borderRadius: 20,
              fontSize: 12,
              fontWeight: 700,
              cursor: 'pointer',
              border: `1px solid ${filter === 'funnel' ? '#ff7849' : 'var(--border)'}`,
              background: filter === 'funnel' ? 'rgba(255, 120, 73, 0.12)' : 'transparent',
              color: filter === 'funnel' ? '#ff7849' : 'var(--text-secondary)',
              transition: 'all 0.15s ease',
            }}
          >
            🎯 Conversion Funnel Dynamics (Q1–Q5)
          </button>
          <button
            onClick={() => setFilter('signal')}
            style={{
              padding: '6px 14px',
              borderRadius: 20,
              fontSize: 12,
              fontWeight: 700,
              cursor: 'pointer',
              border: `1px solid ${filter === 'signal' ? '#06b6d4' : 'var(--border)'}`,
              background: filter === 'signal' ? 'rgba(6, 182, 212, 0.12)' : 'transparent',
              color: filter === 'signal' ? '#06b6d4' : 'var(--text-secondary)',
              transition: 'all 0.15s ease',
            }}
          >
            🌐 Signal & Ecosystem Dynamics (Q6–Q10)
          </button>
        </div>

        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
          Showing {filteredQuestions.length} of 10 Inquiries
        </span>
      </div>

      {/* Grid of Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: 14,
        }}
      >
        {filteredQuestions.map((q) => {
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
                transition: 'transform var(--t-fast), border-color var(--t-fast), background var(--t-fast)',
                position: 'relative',
                overflow: 'hidden',
                minHeight: 155,
              }}
              className="question-card"
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.background = 'var(--bg-card-hover)';
                (e.currentTarget as HTMLElement).style.borderColor = q.color;
                (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.background = 'var(--bg-card)';
                (e.currentTarget as HTMLElement).style.borderColor = 'var(--border)';
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

                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
                  <span
                    style={{
                      fontSize: 10.5,
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      letterSpacing: '0.04em',
                      color: q.categoryColor,
                      background: `${q.categoryColor}15`,
                      padding: '2px 8px',
                      borderRadius: 10,
                    }}
                  >
                    {q.categoryTag}
                  </span>
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
                  {isBoth ? 'Primary + Secondary' : '4 Primary Sources'}
                </span>

                <span style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 700 }}>
                  →
                </span>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

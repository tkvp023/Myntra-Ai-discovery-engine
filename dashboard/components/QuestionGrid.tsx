'use client';

const QUESTIONS = [
  [1,  'Wishlist Motivation',     '#ff3f6c'],
  [2,  'Purchase Prevention',     '#ff7849'],
  [3,  'Remaining Uncertainties', '#a855f7'],
  [4,  'Purchase Postponement',   '#2dd4bf'],
  [5,  'Comparison Behavior',     '#3b82f6'],
  [6,  'External Info Seeking',   '#fbbf24'],
  [7,  'Factor Importance',       '#ec4899'],
  [8,  'Intent vs Bookmarking',   '#84cc16'],
  [9,  'Segment Differences',     '#f97316'],
  [10, 'Unmet Needs',             '#8b5cf6'],
] as const;

export default function QuestionGrid() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 10 }}>
      {QUESTIONS.map(([id, label, color]) => (
        <a
          key={id}
          href={`/questions/${id}`}
          style={{
            display: 'flex', alignItems: 'center', gap: 12,
            padding: '12px 16px',
            background: 'var(--glass-bg)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-md)',
            textDecoration: 'none',
            transition: 'background var(--t-fast), border-color var(--t-fast)',
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLElement).style.background = 'var(--bg-card-hover)';
            (e.currentTarget as HTMLElement).style.borderColor = color;
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLElement).style.background = 'var(--glass-bg)';
            (e.currentTarget as HTMLElement).style.borderColor = 'var(--border)';
          }}
        >
          <span style={{
            width: 32, height: 32, borderRadius: 8, background: `${color}22`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 13, fontWeight: 800, color, fontFamily: 'Outfit',
            flexShrink: 0,
          }}>
            Q{id}
          </span>
          <span style={{ fontSize: 13, color: 'var(--text-secondary)', fontWeight: 500 }}>
            {label}
          </span>
        </a>
      ))}
    </div>
  );
}

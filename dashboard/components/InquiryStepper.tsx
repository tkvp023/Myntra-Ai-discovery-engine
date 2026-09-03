'use client';
import Link from 'next/link';
import { QUESTION_META } from '@/lib/constants';

interface InquiryStepperProps {
  activeId: number;
}

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

export default function InquiryStepper({ activeId }: InquiryStepperProps) {
  return (
    <div
      style={{
        marginBottom: 24,
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '10px 14px',
        overflowX: 'auto',
      }}
      className="inquiry-stepper-container"
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          minWidth: 'max-content',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, paddingRight: 8, borderRight: '1px solid var(--border)' }}>
          <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>
            Inquiries
          </span>
          <span style={{ fontSize: 11, background: 'rgba(255,255,255,0.06)', padding: '2px 6px', borderRadius: 8, color: 'var(--text-secondary)', fontWeight: 600 }}>
            {activeId}/10
          </span>
        </div>

        {Object.entries(QUESTION_META).map(([idStr, meta]) => {
          const id = parseInt(idStr);
          const isActive = id === activeId;
          const icon = Q_ICONS[id] || '📌';

          return (
            <Link
              key={id}
              href={`/questions/${id}`}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '6px 12px',
                borderRadius: 'var(--radius-sm)',
                textDecoration: 'none',
                fontSize: 12.5,
                fontWeight: isActive ? 700 : 500,
                color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                background: isActive ? `${meta.color}18` : 'transparent',
                border: `1px solid ${isActive ? meta.color : 'transparent'}`,
                transition: 'all 0.15s ease',
                whiteSpace: 'nowrap',
              }}
              className={`inquiry-step-pill ${isActive ? 'active' : ''}`}
            >
              <span
                style={{
                  width: 20,
                  height: 20,
                  borderRadius: 6,
                  background: isActive ? meta.color : `${meta.color}25`,
                  color: isActive ? '#fff' : meta.color,
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 10.5,
                  fontWeight: 800,
                  fontFamily: 'Outfit',
                }}
              >
                {id}
              </span>
              <span>{meta.short}</span>
              <span style={{ fontSize: 13, opacity: isActive ? 1 : 0.6 }}>{icon}</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

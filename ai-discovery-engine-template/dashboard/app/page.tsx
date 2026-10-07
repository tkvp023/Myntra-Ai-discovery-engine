import { getSummary } from '@/lib/api';
import StatCard from '@/components/StatCard';
import SummaryAnimations from '@/components/SummaryAnimations';
import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Executive Intelligence Summary | Myntra AI Discovery Engine',
  description: 'Executive summary of 8,182 grounded Myntra customer reviews: root causes of hesitation, 5-source breakdown, and opportunity rankings.',
};

export default async function SummaryPage() {
  const data = await getSummary();
  const totalDocs = (data.primary_signal_docs || 7675) + (data.secondary_signal_docs || 507);

  return (
    <div className="container" style={{ paddingTop: 36, paddingBottom: 64 }}>
      {/* Executive Hero Section */}
      <div className="page-header" style={{ marginBottom: 36 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14, flexWrap: 'wrap' }}>
          <span
            style={{
              background: 'rgba(16, 185, 129, 0.12)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: 20,
              padding: '4px 12px',
              fontSize: 12,
              fontWeight: 700,
              color: '#10b981',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              letterSpacing: '0.03em',
            }}
          >
            <span className="beacon-dot" />
            LIVE CORPUS INTELLIGENCE
          </span>

          <span
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: 20,
              padding: '4px 12px',
              fontSize: 12,
              color: 'var(--text-secondary)',
              fontWeight: 600,
            }}
          >
            {totalDocs.toLocaleString()} Classified Reviews
          </span>

          <span
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: 20,
              padding: '4px 12px',
              fontSize: 12,
              color: 'var(--text-secondary)',
              fontWeight: 500,
            }}
          >
            Gemini 3.7 Flash · Confidence {((data.overall_confidence || 0.69) * 100).toFixed(0)}%
          </span>
        </div>

        <h1
          style={{
            fontSize: 'clamp(30px, 3.8vw, 46px)',
            fontWeight: 900,
            lineHeight: 1.15,
            letterSpacing: '-0.035em',
            marginBottom: 14,
            maxWidth: 1000,
          }}
        >
          Diagnosing{' '}
          <span
            style={{
              background: 'var(--gradient-brand)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Wishlist Drop-Offs
          </span>{' '}
          & Conversion Gaps
        </h1>

        <p
          style={{
            fontSize: 15.5,
            lineHeight: 1.65,
            color: 'var(--text-secondary)',
            maxWidth: 860,
            marginBottom: 20,
          }}
        >
          Mining 22k+ customer conversations across <strong>4 Primary Discovery Sources</strong> (YouTube, Play Store, Reddit, App Store) and <strong>1 Secondary Source</strong> (PissedConsumer) to quantify root causes of hesitation and close the Wishlist → Purchase conversion gap.
        </p>

        {/* Action Quicklinks */}
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <Link
            href="/ask"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              background: 'var(--gradient-brand)',
              color: '#fff',
              fontWeight: 700,
              fontSize: 13.5,
              padding: '10px 18px',
              borderRadius: 'var(--radius-md)',
              textDecoration: 'none',
              boxShadow: '0 4px 16px rgba(255, 45, 85, 0.3)',
              transition: 'transform 0.15s ease, opacity 0.15s ease',
            }}
          >
            <span>🤖</span>
            Ask the AI Assistant →
          </Link>
          <Link
            href="/gaps"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              color: 'var(--text-primary)',
              fontWeight: 600,
              fontSize: 13.5,
              padding: '10px 18px',
              borderRadius: 'var(--radius-md)',
              textDecoration: 'none',
              transition: 'border-color 0.15s ease, background 0.15s ease',
            }}
          >
            <span>⚠️</span>
            Systemic Gaps & Friction
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid-3" style={{ marginBottom: 32 }}>
        {data.kpi_cards.map((card, i) => (
          <StatCard key={card.id} {...card as any} delay={i * 80} />
        ))}
      </div>

      {/* Summary Charts and 10 Strategic Inquiries */}
      <SummaryAnimations data={data} />
    </div>
  );
}

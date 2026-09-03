import { getSummary } from '@/lib/api';
import StatCard from '@/components/StatCard';
import DonutChart from '@/components/DonutChart';
import HorizontalBar from '@/components/HorizontalBar';
import QuestionGrid from '@/components/QuestionGrid';
import SummaryAnimations from '@/components/SummaryAnimations';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Summary',
  description: 'Executive summary of 8,182+ Myntra reviews: top hesitation drivers, 5-source breakdown, KPI snapshot.',
};

export default async function SummaryPage() {
  const data = await getSummary();

  return (
    <div className="container" style={{ paddingTop: 32, paddingBottom: 64 }}>
      {/* Header */}
      <div className="page-header">
        <h1>
          <span style={{ background: 'var(--gradient-brand)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Myntra Wishlist
          </span>{' '}
          Discovery Engine
        </h1>
        <p>
          {data.primary_signal_docs.toLocaleString()} primary-signal documents across{' '}
          {data.source_distribution.length} sources · Overall confidence{' '}
          <span style={{ color: 'var(--teal)', fontWeight: 600 }}>
            {(data.overall_confidence * 100).toFixed(0)}%
          </span>
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid-4" style={{ marginBottom: 32 }}>
        {data.kpi_cards.map((card, i) => (
          <StatCard key={card.id} {...card as any} delay={i * 100} />
        ))}
      </div>

      <SummaryAnimations data={data} />
    </div>
  );
}

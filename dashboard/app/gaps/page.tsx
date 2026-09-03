import { getSystemicGaps } from '@/lib/api';
import GapsContent from '@/components/GapsContent';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Systemic Gaps',
  description: 'Secondary-source analysis: delivery issues, return friction, authenticity concerns and trust deficits from customer complaint and dispute forums (PissedConsumer).',
};

export default async function GapsPage() {
  const data = await getSystemicGaps();

  return (
    <div className="container" style={{ paddingTop: 32, paddingBottom: 64 }}>
      <div className="page-header">
        <h1>
          <span style={{ background: 'var(--gradient-brand)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Systemic
          </span>{' '}
          Gaps
        </h1>
        <p>
          Secondary-source analysis from {data.total_secondary_docs.toLocaleString()} reviews across
          customer dispute forums (PissedConsumer) — systemic issues that amplify hesitation
        </p>
      </div>

      <GapsContent data={data} />
    </div>
  );
}

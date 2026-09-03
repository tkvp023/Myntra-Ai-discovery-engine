'use client';
import { useInView } from 'react-intersection-observer';
import DonutChart from './DonutChart';
import HorizontalBar from './HorizontalBar';
import QuestionGrid from './QuestionGrid';

function AnimatedCard({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  const { ref, inView } = useInView({ threshold: 0.1, triggerOnce: true });
  return (
    <div
      ref={ref}
      className="card animate-enter"
      style={{
        animationDelay: `${delay}ms`,
        opacity: inView ? 1 : 0,
        transition: 'opacity 0.4s ease',
      }}
    >
      {children}
    </div>
  );
}

function AnimatedSection({ children, delay = 0, className, style }: { children: React.ReactNode; delay?: number; className?: string; style?: React.CSSProperties }) {
  const { ref, inView } = useInView({ threshold: 0.1, triggerOnce: true });
  return (
    <div
      ref={ref}
      className={`animate-enter ${className || ''}`}
      style={{
        animationDelay: `${delay}ms`,
        opacity: inView ? 1 : 0,
        transition: 'opacity 0.4s ease',
        ...style,
      }}
    >
      {children}
    </div>
  );
}

interface SummaryAnimationsProps {
  data: any;
}

export default function SummaryAnimations({ data }: SummaryAnimationsProps) {
  return (
    <>
      {/* Source distribution + Top Opportunities */}
      <div className="grid-2" style={{ marginBottom: 32 }}>
        <AnimatedCard delay={100}>
          <div className="card-header">
            <span className="card-title">Source Distribution</span>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              {data.source_distribution.reduce((s: number, d: any) => s + d.count, 0).toLocaleString()} total
            </span>
          </div>
          <div className="card-body">
            <DonutChart
              data={data.source_distribution.map((s: any) => ({ ...s, label: s.source }))}
              centerLabel="reviews"
            />
          </div>
        </AnimatedCard>

        <AnimatedCard delay={200}>
          <div className="card-header">
            <span className="card-title">Top Opportunities</span>
            <span className="badge badge-conf-high">Ranked by impact</span>
          </div>
          <div className="card-body">
            <HorizontalBar
              data={data.top_opportunities.map((op: any) => ({
                label: op.label,
                tag: `opp_${op.rank}`,
                count: op.count,
                pct: op.pct,
                avg_confidence: op.avg_confidence,
                color: ['#ff3f6c','#ff7849','#a855f7','#2dd4bf','#3b82f6'][op.rank - 1] || '#6b7280',
                href: `/questions/${op.question_id || 2}`,
              }))}
            />
          </div>
        </AnimatedCard>
      </div>

      {/* Signal breakdown */}
      <AnimatedCard delay={300}>
        <div className="card-header">
          <span className="card-title">Corpus Signal Quality</span>
        </div>
        <div className="card-body">
          <div className="grid-3">
            {[
              { label: 'Primary Signal', value: data.primary_signal_docs, color: '#84cc16', desc: 'Contains clear hesitation or wishlist intent signals' },
              { label: 'Secondary Signal', value: data.secondary_signal_docs, color: '#fbbf24', desc: 'Partial signal — systemic issues, complaints' },
              { label: 'No Signal', value: data.no_signal_docs, color: '#6b7280', desc: 'Off-topic, spam, or non-relevant content' },
            ].map((item) => {
              const total = data.primary_signal_docs + data.secondary_signal_docs + data.no_signal_docs;
              const pct = ((item.value / total) * 100).toFixed(1);
              return (
                <div key={item.label} style={{ textAlign: 'center', padding: '16px 12px' }}>
                  <div style={{ fontSize: 28, fontFamily: 'Outfit, sans-serif', fontWeight: 800, color: item.color }}>
                    {pct}%
                  </div>
                  <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', margin: '4px 0' }}>
                    {item.label}
                  </div>
                  <div style={{ fontSize: 20, fontFamily: 'Outfit', fontWeight: 700, color: 'var(--text-secondary)' }}>
                    {item.value.toLocaleString()}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
                    {item.desc}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </AnimatedCard>

      {/* Quick links to all 10 questions */}
      <AnimatedSection delay={400} style={{ marginTop: 32 }}>
        <div className="card">
          <div className="card-header">
            <span className="card-title">10 Strategic Questions</span>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Click to explore →</span>
          </div>
          <div className="card-body">
            <QuestionGrid />
          </div>
        </div>
      </AnimatedSection>
    </>
  );
}

'use client';
import { useInView } from 'react-intersection-observer';
import HorizontalBar from './HorizontalBar';
import { QuoteCard } from './QuoteCarousel';

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

interface GapsContentProps {
  data: {
    total_secondary_docs: number;
    issue_breakdown: any[];
    correlation_with_hesitation: any[];
    key_quotes: any[];
  };
}

export default function GapsContent({ data }: GapsContentProps) {
  return (
    <>
      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Issue breakdown */}
        <AnimatedCard delay={0}>
          <div className="card-header">
            <span className="card-title">Issue Breakdown</span>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{data.total_secondary_docs.toLocaleString()} secondary docs</span>
          </div>
          <div className="card-body">
            <HorizontalBar data={data.issue_breakdown} />
          </div>
        </AnimatedCard>

        {/* Impact on hesitation */}
        <AnimatedCard delay={100}>
          <div className="card-header">
            <span className="card-title">Correlation with Hesitation</span>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {(data.correlation_with_hesitation || []).map((item: any) => (
                <div key={item.systemic_issue} style={{
                  padding: '14px 16px',
                  background: 'rgba(255,255,255,0.03)',
                  borderRadius: 'var(--radius-md)',
                  borderLeft: '3px solid var(--orange)',
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                    <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{item.systemic_issue}</span>
                    <span style={{
                      fontSize: 13, fontWeight: 800, fontFamily: 'Outfit',
                      color: item.correlation_hint > 0.6 ? 'var(--pink)' : 'var(--yellow)',
                    }}>
                      r = {item.correlation_hint.toFixed(2)}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: 16, fontSize: 12, color: 'var(--text-muted)' }}>
                    <span>Systemic: {item.systemic_frequency.toLocaleString()}</span>
                    <span>Hesitation: {item.hesitation_frequency.toLocaleString()}</span>
                    <span style={{ color: 'var(--text-secondary)' }}>→ {item.related_hesitation.replace(/_/g, ' ')}</span>
                  </div>
                </div>
              ))}
              {(!data.correlation_with_hesitation || data.correlation_with_hesitation.length === 0) && (
                <div className="empty-state">
                  <div className="empty-state-icon">🔗</div>
                  <div className="empty-state-text">Run pipeline to see correlations</div>
                </div>
              )}
            </div>
          </div>
        </AnimatedCard>
      </div>

      {/* Key quotes */}
      {data.key_quotes && data.key_quotes.length > 0 && (
        <AnimatedCard delay={200}>
          <div className="card-header">
            <span className="card-title">Representative Complaints</span>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{data.key_quotes.length} quotes</span>
          </div>
          <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {data.key_quotes.map((q: any, i: number) => (
              <QuoteCard
                key={i}
                quote={{ ...q, tags: [q.issue || ''], source_id: '', confidence: 0.8 }}
                accent="var(--orange)"
              />
            ))}
          </div>
        </AnimatedCard>
      )}
    </>
  );
}

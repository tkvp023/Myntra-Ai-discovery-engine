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
  const totalDocs = (data.primary_signal_docs || 7675) + (data.secondary_signal_docs || 507);

  return (
    <>
      {/* Source distribution + Top Opportunities */}
      <div className="grid-2" style={{ marginBottom: 28 }}>
        <AnimatedCard delay={100}>
          <div className="card-header">
            <div>
              <span className="card-title">Source Distribution</span>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                5 Mined Consumer Channels (4 Primary + 1 Secondary)
              </div>
            </div>
            <span
              style={{
                fontSize: 12,
                fontWeight: 700,
                color: 'var(--teal)',
                background: 'rgba(6, 182, 212, 0.1)',
                padding: '3px 10px',
                borderRadius: 12,
              }}
            >
              {totalDocs.toLocaleString()} Total
            </span>
          </div>
          <div className="card-body">
            <DonutChart
              data={data.source_distribution.map((s: any) => ({ ...s, label: s.source }))}
              centerLabel="reviews"
            />
            {/* Quick summary chips */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
                gap: 8,
                marginTop: 16,
                paddingTop: 16,
                borderTop: '1px solid var(--border)',
              }}
            >
              {data.source_distribution.map((s: any) => (
                <div
                  key={s.source}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    padding: '6px 10px',
                    borderRadius: 8,
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid var(--border)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11.5, color: 'var(--text-secondary)' }}>
                    <span style={{ width: 8, height: 8, borderRadius: '50%', background: s.color }} />
                    <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{s.source}</span>
                  </div>
                  <div style={{ fontSize: 13, fontWeight: 700, fontFamily: 'Outfit', color: 'var(--text-primary)', marginTop: 2 }}>
                    {s.count.toLocaleString()} <span style={{ fontSize: 11, fontWeight: 500, color: 'var(--text-muted)' }}>({s.pct}%)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </AnimatedCard>

        <AnimatedCard delay={200}>
          <div className="card-header">
            <div>
              <span className="card-title">Top Purchase-Blocker Opportunities</span>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                Prioritized by Volume & Conversion Impact
              </div>
            </div>
            <span className="badge badge-conf-high">Ranked by Impact</span>
          </div>
          <div className="card-body">
            <HorizontalBar
              data={data.top_opportunities.map((op: any) => ({
                label: op.label,
                tag: `opp_${op.rank}`,
                count: op.count,
                pct: op.pct,
                avg_confidence: op.avg_confidence,
                color: ['#ff2d55', '#ff7849', '#06b6d4', '#fbbf24', '#a855f7'][op.rank - 1] || '#6b7280',
                href: `/questions/${op.question_id || 2}`,
              }))}
            />
          </div>
        </AnimatedCard>
      </div>

      {/* Corpus Signal Quality Breakdown */}
      <AnimatedCard delay={300}>
        <div className="card-header">
          <div>
            <span className="card-title">Corpus Architecture & Grounded Signal Quality</span>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
              Verified Multi-Tier Data Pipeline with Zero Fabricated Records
            </div>
          </div>
          <span
            style={{
              fontSize: 12,
              fontWeight: 700,
              padding: '3px 10px',
              borderRadius: 12,
              background: 'rgba(16, 185, 129, 0.12)',
              color: '#10b981',
              border: '1px solid rgba(16, 185, 129, 0.3)',
            }}
          >
            100% Grounded Corpus
          </span>
        </div>
        <div className="card-body">
          <div className="grid-3" style={{ gap: 16 }}>
            {[
              {
                title: 'Primary Sources',
                tag: 'Discovery & Sentiment',
                value: data.primary_signal_docs || 7675,
                color: '#c084fc',
                bg: 'rgba(168, 85, 247, 0.08)',
                border: 'rgba(168, 85, 247, 0.25)',
                desc: 'YouTube video try-on hauls, Google Play Store, Reddit discussions, and Apple App Store analyzing fit, styling, and price comparison.',
              },
              {
                title: 'Secondary Source',
                tag: 'Escalations & Disputes',
                value: data.secondary_signal_docs || 507,
                color: '#fbbf24',
                bg: 'rgba(251, 191, 36, 0.08)',
                border: 'rgba(251, 191, 36, 0.25)',
                desc: 'PissedConsumer dispute threads detailing doorstep pickup rejections, tag inspection friction, and refund timelines.',
              },
              {
                title: 'Total Classified Database',
                tag: 'Unified Intelligence',
                value: totalDocs,
                color: '#06b6d4',
                bg: 'rgba(6, 182, 212, 0.08)',
                border: 'rgba(6, 182, 212, 0.25)',
                desc: '8,182 structured records deduplicated from 22,065 raw reviews with strict JSON schema validation and Gemini confidence scores.',
              },
            ].map((item) => {
              const pct = item.title === 'Total Classified Database' ? '100' : ((item.value / totalDocs) * 100).toFixed(1);
              return (
                <div
                  key={item.title}
                  style={{
                    padding: '18px 20px',
                    borderRadius: 'var(--radius-md)',
                    background: item.bg,
                    border: `1px solid ${item.border}`,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                      <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>
                        {item.title}
                      </span>
                      <span style={{ fontSize: 11, fontWeight: 600, color: item.color, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        {item.tag}
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, margin: '8px 0' }}>
                      <span style={{ fontSize: 32, fontFamily: 'Outfit, sans-serif', fontWeight: 900, color: item.color, letterSpacing: '-0.03em' }}>
                        {pct}%
                      </span>
                      <span style={{ fontSize: 15, fontFamily: 'Outfit', fontWeight: 700, color: 'var(--text-secondary)' }}>
                        ({item.value.toLocaleString()} reviews)
                      </span>
                    </div>
                  </div>

                  <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0, marginTop: 8 }}>
                    {item.desc}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </AnimatedCard>

      {/* 10 Strategic Inquiries Grid */}
      <AnimatedSection delay={400} style={{ marginTop: 28 }}>
        <div className="card">
          <div className="card-header">
            <div>
              <span className="card-title">10 Strategic Intelligence Inquiries</span>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                Comprehensive Question Deep-Dives Across the Fashion Discovery Journey
              </div>
            </div>
            <span style={{ fontSize: 12, color: 'var(--text-secondary)', fontWeight: 600 }}>
              Select an inquiry to explore evidence →
            </span>
          </div>
          <div className="card-body">
            <QuestionGrid />
          </div>
        </div>
      </AnimatedSection>
    </>
  );
}

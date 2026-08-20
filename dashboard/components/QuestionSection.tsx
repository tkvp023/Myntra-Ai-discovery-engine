'use client';
import { useState } from 'react';
import HorizontalBar from './HorizontalBar';
import DonutChart from './DonutChart';
import AreaTimeline from './AreaTimeline';
import QuoteCarousel from './QuoteCarousel';
import RadarChartComponent from './RadarChartComponent';
import HeatmapChart from './HeatmapChart';
import WordCloudChart from './WordCloudChart';
import TreemapChart from './TreemapChart';
import SankeyDiagram from './SankeyDiagram';
import GroupedBar from './GroupedBar';
import { useInView } from 'react-intersection-observer';

interface QuestionSectionProps {
  data: any;
  questionId: number;
}

function ChartCard({ title, children, delay = 0 }: { title: string; children: React.ReactNode; delay?: number }) {
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
      <div className="card-header">
        <span className="card-title">{title}</span>
      </div>
      <div className="card-body">{children}</div>
    </div>
  );
}

export default function QuestionSection({ data, questionId }: QuestionSectionProps) {
  const [source, setSource] = useState('all');

  const breakdown = data.breakdown || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

      {/* Stat strip */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div style={{ display: 'flex', gap: 20 }}>
          <div>
            <div style={{ fontSize: 22, fontFamily: 'Outfit', fontWeight: 800 }}>{data.total_relevant_docs.toLocaleString()}</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>relevant docs</div>
          </div>
          <div>
            <div style={{ fontSize: 22, fontFamily: 'Outfit', fontWeight: 800, color: 'var(--teal)' }}>
              {(data.avg_confidence * 100).toFixed(0)}%
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>avg confidence</div>
          </div>
          {/* Source filter pills */}
          {data.source_attribution && data.source_attribution.length > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
              {['all', 'Play Store', 'Reddit', 'YouTube', 'App Store'].map((src) => {
                const active = src === source;
                const color = ({ 'Play Store': '#ff3f6c', Reddit: '#ff7849', YouTube: '#a855f7', 'App Store': '#2dd4bf', all: 'var(--teal)' } as Record<string, string>)[src] || '#6b7280';
                return (
                  <button
                    key={src}
                    onClick={() => setSource(src)}
                    style={{
                      padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 600, cursor: 'pointer',
                      border: `1px solid ${active ? color : 'var(--border)'}`,
                      background: active ? `${color}22` : 'transparent',
                      color: active ? color : 'var(--text-muted)',
                      transition: 'all 0.15s',
                    }}
                  >{src === 'all' ? 'All Sources' : src}</button>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Main breakdown + donut */}
      <div className="grid-2">
        <ChartCard title="Breakdown" delay={0}>
          {breakdown.length > 0
            ? <HorizontalBar data={breakdown} />
            : <div className="empty-state"><div className="empty-state-icon">📊</div><div className="empty-state-text">No data available</div></div>
          }
        </ChartCard>

        <ChartCard title="Distribution" delay={100}>
          {breakdown.length > 0
            ? <DonutChart data={breakdown} centerLabel="signals" />
            : <div className="empty-state"><div className="empty-state-icon">🍩</div><div className="empty-state-text">No data</div></div>
          }
        </ChartCard>
      </div>

      {/* Q5: Platform comparison heatmap */}
      {questionId === 5 && data.platform_matrix && (
        <ChartCard title="Platform × Criterion Co-mention Matrix" delay={150}>
          <HeatmapChart matrix={data.platform_matrix} />
        </ChartCard>
      )}

      {/* Q6: External info-seeking Sankey */}
      {questionId === 6 && data.sankey_data && (
        <ChartCard title="Information-Seeking Flow — Where Users Go Before Buying" delay={150}>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 12 }}>
            From Myntra listing → external research platform → purchase outcome
          </p>
          <SankeyDiagram
            nodes={data.sankey_data.nodes}
            links={data.sankey_data.links}
            height={380}
          />
        </ChartCard>
      )}

      {/* Q7: Radar chart */}
      {questionId === 7 && data.radar_data && (
        <ChartCard title="Factor Importance Radar" delay={150}>
          <RadarChartComponent data={data.radar_data} />
        </ChartCard>
      )}

      {/* Q8: Word cloud */}
      {questionId === 8 && data.word_cloud_data && (
        <div className="grid-2">
          <ChartCard title="Genuine Purchase Intent — Common Phrases" delay={150}>
            <WordCloudChart words={data.word_cloud_data.genuine_purchase_intent || []} color="#ff3f6c" />
          </ChartCard>
          <ChartCard title="Bookmarking / Aspiration — Common Phrases" delay={200}>
            <WordCloudChart words={data.word_cloud_data.bookmarking || []} color="#a855f7" />
          </ChartCard>
        </div>
      )}

      {/* Q10: Treemap */}
      {questionId === 10 && data.treemap_data && (
        <ChartCard title="Unmet Needs Treemap" delay={150}>
          <TreemapChart data={data.treemap_data} />
        </ChartCard>
      )}

      {/* Q9: Segment × factor GroupedBar */}
      {questionId === 9 && data.segment_grouped_data && (
        <ChartCard title="Hesitation Factor by Inferred Segment" delay={150}>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 12 }}>
            % of inferred segment mentioning each hesitation factor
          </p>
          <GroupedBar
            data={data.segment_grouped_data}
            categoryKey="factor"
            seriesKeys={['gen_z', 'millennial', 'gen_x']}
            seriesLabels={{ gen_z: 'Gen-Z', millennial: 'Millennial', gen_x: 'Gen-X' }}
            colors={['#a855f7', '#3b82f6', '#2dd4bf']}
            unit="%"
            height={300}
          />
        </ChartCard>
      )}

      {/* Temporal trend */}
      {data.temporal_trend && data.temporal_trend.length > 0 && (
        <ChartCard title="Signal Trend Over Time" delay={200}>
          <AreaTimeline data={data.temporal_trend} />
        </ChartCard>
      )}

      {/* Source attribution */}
      {data.source_attribution && data.source_attribution.length > 0 && (
        <ChartCard title="Source Attribution" delay={250}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {data.source_attribution.slice(0, 3).map((item: any, i: number) => (
              <div key={`${item.tag || item.label || 'attr'}-${i}`}>
                <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8 }}>{item.label}</p>
                <HorizontalBar
                  data={item.sources.map((s: any, si: number) => ({
                    label: s.source, tag: `${s.source}-${si}`, count: s.count, pct: s.pct,
                    color: ({ 'Play Store': '#ff3f6c', Reddit: '#ff7849', YouTube: '#a855f7', 'App Store': '#2dd4bf' } as Record<string, string>)[s.source] || '#6b7280',
                  }))}
                  showCount={true}
                />
              </div>
            ))}
          </div>
        </ChartCard>
      )}

      {/* Q9: Inferred segment comparison table */}
      {questionId === 9 && data.segment_splits && (
        <ChartCard title="Inferred Segment Comparison" delay={300}>
          <div className="grid-3" style={{ gap: 16 }}>
            {(['gen_z', 'millennial', 'gen_x'] as const).map((seg) => {
              const splits = data.segment_splits[seg] || [];
              const label = seg === 'gen_z' ? 'Gen-Z' : seg === 'millennial' ? 'Millennial' : 'Gen-X';
              const color = seg === 'gen_z' ? '#a855f7' : seg === 'millennial' ? '#3b82f6' : '#2dd4bf';
              return (
                <div key={seg}>
                  <div style={{ fontSize: 13, fontWeight: 700, color, marginBottom: 10 }}>{label}</div>
                  <HorizontalBar data={splits.slice(0, 4).map((s: any, i: number) => ({
                    ...s,
                    tag: s.tag || s.intent || s.label || `${seg}-${i}`,
                    color: ['#ff3f6c','#ff7849','#a855f7','#2dd4bf'][i] || '#6b7280',
                    avg_confidence: undefined,
                  }))} showCount={false} />
                </div>
              );
            })}
          </div>
        </ChartCard>
      )}

      {/* Q9: Inference methodology disclaimer */}
      {questionId === 9 && (
        <div style={{
          background: 'var(--glass-bg)',
          border: '1px solid var(--border)',
          borderLeft: '3px solid #fbbf24',
          borderRadius: 10,
          padding: '16px 20px',
          fontSize: 13,
          lineHeight: 1.6,
          color: 'var(--text-secondary)',
        }}>
          <div style={{ fontWeight: 700, color: '#fbbf24', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>⚠️</span> Inferred Segments — Not Actual User Ages
          </div>
          <p style={{ margin: '0 0 8px 0' }}>
            These generational segments (<strong>Gen-Z</strong>, <strong>Millennial</strong>, <strong>Gen-X</strong>) are
            <em> inferred from review text</em>, not from verified user profile data. No review platform provides actual age information.
          </p>
          <p style={{ margin: '0 0 8px 0', fontWeight: 600, color: 'var(--text-primary)' }}>
            How we infer segments:
          </p>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            <li><strong>LLM Analysis:</strong> Each review is analyzed by Gemini for language cues — slang, vocabulary, lifestyle references, and cultural context.</li>
            <li><strong>Keyword Patterns:</strong> As a fallback, regex patterns detect generational signals:
              <span style={{ color: '#a855f7', fontWeight: 600 }}> Gen-Z</span> → &quot;aesthetic&quot;, &quot;y2k&quot;, &quot;vibe&quot;, &quot;drip&quot;, &quot;reels&quot;, &quot;streetwear&quot; |
              <span style={{ color: '#3b82f6', fontWeight: 600 }}> Millennial</span> → &quot;office&quot;, &quot;formal&quot;, &quot;premium&quot;, &quot;corporate&quot;, &quot;classic&quot;
            </li>
            <li><strong>Default:</strong> Reviews without clear signals default to &quot;Millennial&quot;.</li>
          </ul>
          <p style={{ margin: '8px 0 0 0', fontStyle: 'italic', fontSize: 12, color: 'var(--text-muted)' }}>
            Treat these as behavioral proxies, not demographic facts. They reflect language style and topic patterns, not confirmed ages.
          </p>
        </div>
      )}

      {/* Key quotes */}
      {data.key_quotes && data.key_quotes.length > 0 && (
        <ChartCard title="Key Quotes" delay={350}>
          <QuoteCarousel quotes={data.key_quotes} />
        </ChartCard>
      )}
    </div>
  );
}

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

  // Compute active breakdown based on source filter
  let activeBreakdown = data.breakdown || [];
  let activeDocsCount = data.total_relevant_docs;
  let activeQuotes = data.key_quotes || [];

  if (source !== 'all' && data.source_attribution && data.source_attribution.length > 0) {
    const computedItems: any[] = [];
    data.source_attribution.forEach((attr: any, i: number) => {
      const match = attr.sources?.find((s: any) => s.source.toLowerCase() === source.toLowerCase());
      if (match && match.count > 0) {
        computedItems.push({
          label: attr.label,
          tag: attr.tag,
          count: match.count,
          pct: match.pct || 0,
          avg_confidence: attr.avg_confidence || data.avg_confidence,
          color: attr.color || ['#ff3f6c', '#ff7849', '#a855f7', '#2dd4bf', '#3b82f6', '#fbbf24'][i % 6],
        });
      }
    });

    if (computedItems.length > 0) {
      const totalCount = computedItems.reduce((acc, it) => acc + it.count, 0) || 1;
      activeBreakdown = computedItems
        .map((it) => ({
          ...it,
          pct: Number(((it.count / totalCount) * 100).toFixed(1)),
        }))
        .sort((a, b) => b.count - a.count);
      activeDocsCount = totalCount;
    }
  }

  // Filter quotes by active source
  if (data.key_quotes && data.key_quotes.length > 0) {
    let filtered = [...data.key_quotes];
    if (source !== 'all') {
      const match = filtered.filter((q: any) => q.source?.toLowerCase() === source.toLowerCase());
      if (match.length > 0) filtered = match;
    }
    activeQuotes = filtered;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

      {/* Interactive Filter and Stat strip */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 16,
          padding: '14px 18px',
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-md)',
        }}
      >
        <div style={{ display: 'flex', gap: 20, alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: 22, fontFamily: 'Outfit', fontWeight: 800 }}>
              {activeDocsCount?.toLocaleString() || data.total_relevant_docs?.toLocaleString()}
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              {source !== 'all' ? `${source} reviews` : 'verified reviews'}
            </div>
          </div>
          <div>
            <div style={{ fontSize: 22, fontFamily: 'Outfit', fontWeight: 800, color: 'var(--teal)' }}>
              {(data.avg_confidence * 100).toFixed(0)}%
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              avg confidence
            </div>
          </div>
        </div>

        {/* Source filter pills */}
        {data.source_attribution && data.source_attribution.length > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginRight: 2 }}>
              Platform Filter:
            </span>
            {['all', 'YouTube', 'Play Store', 'Reddit', 'PissedConsumer', 'App Store'].map((src) => {
              const active = src === source;
              const color = ({ 'Play Store': '#ff3f6c', Reddit: '#ff7849', YouTube: '#a855f7', 'App Store': '#2dd4bf', PissedConsumer: '#fbbf24', all: 'var(--teal)' } as Record<string, string>)[src] || '#6b7280';
              return (
                <button
                  key={src}
                  onClick={() => setSource(src)}
                  style={{
                    padding: '4px 12px',
                    borderRadius: 20,
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: 'pointer',
                    border: `1px solid ${active ? color : 'var(--border)'}`,
                    background: active ? `${color}22` : 'transparent',
                    color: active ? color : 'var(--text-muted)',
                    transition: 'all 0.15s',
                  }}
                >
                  {src === 'all' ? 'All Sources' : src}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Main breakdown + donut */}
      <div className="grid-2">
        <ChartCard
          title={`Breakdown ${source !== 'all' ? `— ${source}` : ''}`}
          delay={0}
        >
          {activeBreakdown.length > 0
            ? <HorizontalBar data={activeBreakdown} />
            : <div className="empty-state"><div className="empty-state-icon">📊</div><div className="empty-state-text">No data available for this filter</div></div>
          }
        </ChartCard>

        <ChartCard
          title={`Distribution ${source !== 'all' ? `— ${source}` : ''}`}
          delay={50}
        >
          {activeBreakdown.length > 0
            ? <DonutChart data={activeBreakdown} centerLabel={source !== 'all' ? source : 'Total Reviews'} />
            : <div className="empty-state"><div className="empty-state-icon">🍩</div><div className="empty-state-text">No distribution data</div></div>
          }
        </ChartCard>
      </div>

      {/* Q5: Heatmap */}
      {questionId === 5 && data.comparison_matrix && (
        <ChartCard title="Brand vs Platform Comparison Heatmap" delay={100}>
          <HeatmapChart matrix={data.comparison_matrix} />
        </ChartCard>
      )}

      {/* Q6: Sankey Flow Diagram */}
      {questionId === 6 && data.sankey_nodes && data.sankey_links && (
        <ChartCard title="Information Seeking Flow (External Discovery → Impact)" delay={100}>
          <SankeyDiagram nodes={data.sankey_nodes} links={data.sankey_links} />
        </ChartCard>
      )}

      {/* Q6: Word cloud */}
      {questionId === 6 && data.word_cloud && (
        <ChartCard title="Common External Discovery Search Phrases" delay={150}>
          <WordCloudChart words={data.word_cloud} />
        </ChartCard>
      )}

      {/* Q7: Radar chart */}
      {questionId === 7 && data.radar_data && (
        <ChartCard title="Factor Importance Radar" delay={100}>
          <RadarChartComponent data={data.radar_data} />
        </ChartCard>
      )}

      {/* Q10: Treemap */}
      {questionId === 10 && data.treemap_data && (
        <ChartCard title="Unmet Needs Treemap" delay={150}>
          <TreemapChart data={data.treemap_data} />
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
        <ChartCard title="Cross-Platform Attribution" delay={250}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {data.source_attribution.slice(0, 4).map((item: any, i: number) => (
              <div key={`${item.tag || item.label || 'attr'}-${i}`}>
                <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8 }}>{item.label}</p>
                <HorizontalBar
                  data={item.sources.map((s: any, si: number) => ({
                    label: s.source, tag: `${s.source}-${si}`, count: s.count, pct: s.pct,
                    color: ({ 'Play Store': '#ff3f6c', Reddit: '#ff7849', YouTube: '#a855f7', 'App Store': '#2dd4bf', PissedConsumer: '#fbbf24' } as Record<string, string>)[s.source] || '#6b7280',
                  }))}
                  showCount={true}
                />
              </div>
            ))}
          </div>
        </ChartCard>
      )}

      {/* Key quotes */}
      {activeQuotes && activeQuotes.length > 0 && (
        <ChartCard title={`Key Customer Quotes ${source !== 'all' ? `(${source})` : ''}`} delay={300}>
          <QuoteCarousel quotes={activeQuotes} />
        </ChartCard>
      )}
    </div>
  );
}

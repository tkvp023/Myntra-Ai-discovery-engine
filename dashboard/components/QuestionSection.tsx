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
import SegmentToggle from './SegmentToggle';
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
  const [segment, setSegment] = useState('all');

  // Compute active breakdown based on source and demographic filters
  let activeBreakdown = data.breakdown || [];
  let activeDocsCount = data.total_relevant_docs;
  let activeQuotes = data.key_quotes || [];

  if (segment !== 'all' && data.segment_splits?.[segment]?.length > 0) {
    const rawSplits = data.segment_splits[segment];
    const totalSegCount = rawSplits.reduce((acc: number, it: any) => acc + (it.count || 0), 0) || 1;
    activeBreakdown = rawSplits.map((item: any, i: number) => ({
      ...item,
      pct: item.pct || Number(((item.count / totalSegCount) * 100).toFixed(1)),
      color: item.color || ['#a855f7', '#3b82f6', '#2dd4bf', '#fbbf24', '#ff7849', '#ff3f6c'][i % 6],
    }));
    activeDocsCount = totalSegCount;
  } else if (source !== 'all' && data.source_attribution && data.source_attribution.length > 0) {
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

  // Filter quotes by active source & segment
  if (data.key_quotes && data.key_quotes.length > 0) {
    let filtered = [...data.key_quotes];
    if (source !== 'all') {
      const match = filtered.filter((q: any) => q.source?.toLowerCase() === source.toLowerCase());
      if (match.length > 0) filtered = match;
    }
    if (segment !== 'all') {
      const match = filtered.filter((q: any) => q.segment?.toLowerCase() === segment.toLowerCase());
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
              {source !== 'all' ? `${source} docs` : segment !== 'all' ? `${segment.replace('_', ' ')} docs` : 'relevant docs'}
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

        {/* Demographic segment filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Demographic:
          </span>
          <SegmentToggle
            value={segment}
            onChange={(v) => {
              setSegment(v);
              if (v !== 'all') setSource('all'); // prioritize segment
            }}
          />
        </div>

        {/* Source filter pills */}
        {data.source_attribution && data.source_attribution.length > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginRight: 2 }}>
              Platform:
            </span>
            {['all', 'YouTube', 'Play Store', 'Reddit', 'PissedConsumer', 'App Store'].map((src) => {
              const active = src === source;
              const color = ({ 'Play Store': '#ff3f6c', Reddit: '#ff7849', YouTube: '#a855f7', 'App Store': '#2dd4bf', PissedConsumer: '#fbbf24', all: 'var(--teal)' } as Record<string, string>)[src] || '#6b7280';
              return (
                <button
                  key={src}
                  onClick={() => {
                    setSource(src);
                    if (src !== 'all') setSegment('all'); // prioritize source
                  }}
                  style={{
                    padding: '3px 10px',
                    borderRadius: 20,
                    fontSize: 11,
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
          title={`Breakdown ${source !== 'all' ? `— ${source}` : segment !== 'all' ? `— ${segment.replace('_', ' ').toUpperCase()}` : ''}`}
          delay={0}
        >
          {activeBreakdown.length > 0
            ? <HorizontalBar data={activeBreakdown} />
            : <div className="empty-state"><div className="empty-state-icon">📊</div><div className="empty-state-text">No data available for this filter</div></div>
          }
        </ChartCard>

        <ChartCard
          title={`Distribution ${source !== 'all' ? `— ${source}` : segment !== 'all' ? `— ${segment.replace('_', ' ').toUpperCase()}` : ''}`}
          delay={100}
        >
          {activeBreakdown.length > 0
            ? <DonutChart data={activeBreakdown} centerLabel="signals" />
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
        <ChartCard title="Hesitation Factor by Implied Demographic Segment" delay={150}>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 12 }}>
            % of implied demographic cohort mentioning each hesitation factor
          </p>
          <GroupedBar
            data={data.segment_grouped_data}
            categoryKey="factor"
            seriesKeys={['gen_z', 'millennial', 'gen_x']}
            seriesLabels={{ gen_z: 'Implied Gen-Z', millennial: 'Implied Millennial', gen_x: 'Implied Gen-X' }}
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
                    color: ({ 'Play Store': '#ff3f6c', Reddit: '#ff7849', YouTube: '#a855f7', 'App Store': '#2dd4bf', PissedConsumer: '#fbbf24' } as Record<string, string>)[s.source] || '#6b7280',
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
        <ChartCard title="Implied Segment Comparison" delay={300}>
          <div className="grid-3" style={{ gap: 16 }}>
            {(['gen_z', 'millennial', 'gen_x'] as const).map((seg) => {
              const splits = data.segment_splits[seg] || [];
              const label = seg === 'gen_z' ? 'Implied Gen-Z' : seg === 'millennial' ? 'Implied Millennial' : 'Implied Gen-X';
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
            <span>⚠️</span> Implied / Inferred Cohorts — Behavioral Proxies (No Age Data Provided)
          </div>
          <p style={{ margin: '0 0 8px 0' }}>
            All generational cohorts (<strong>Implied Gen-Z</strong>, <strong>Implied Millennial</strong>, <strong>Implied Gen-X</strong>) are
            <em> inferred from textual signals and linguistic context</em>. E-commerce review and video platforms do not collect or expose user ages or birth years.
          </p>
          <p style={{ margin: '0 0 8px 0', fontWeight: 600, color: 'var(--text-primary)' }}>
            Categorization Methodology & Justification:
          </p>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            <li><strong>LLM Semantic Cue Analysis:</strong> Reviews are classified using Gemini for generational language cues, slang, lifestyle themes, and contextual markers.</li>
            <li><strong>Linguistic Signal Markers:</strong>
              <span style={{ color: '#a855f7', fontWeight: 600 }}> Implied Gen-Z</span> → &quot;aesthetic&quot;, &quot;y2k&quot;, &quot;vibe&quot;, &quot;drip&quot;, &quot;reels&quot;, &quot;streetwear&quot;, &quot;college&quot; |
              <span style={{ color: '#3b82f6', fontWeight: 600 }}> Implied Millennial</span> → &quot;office&quot;, &quot;formal&quot;, &quot;workwear&quot;, &quot;premium&quot;, &quot;corporate&quot;, &quot;classic&quot; |
              <span style={{ color: '#2dd4bf', fontWeight: 600 }}> Implied Gen-X</span> → &quot;family&quot;, &quot;kids&quot;, &quot;traditional&quot;, &quot;comfort&quot;, &quot;practical&quot;
            </li>
            <li><strong>Baseline Default:</strong> Unlabeled general reviews default to &quot;Implied Millennial&quot; as the baseline consumer majority.</li>
          </ul>
          <p style={{ margin: '8px 0 0 0', fontStyle: 'italic', fontSize: 12, color: 'var(--text-muted)' }}>
            These segments represent behavioral and stylistic patterns across customer discussions, not verified demographic data.
          </p>
        </div>
      )}

      {/* Key quotes */}
      {activeQuotes && activeQuotes.length > 0 && (
        <ChartCard title={`Key Quotes ${source !== 'all' ? `(${source})` : segment !== 'all' ? `(${segment.replace('_', ' ').toUpperCase()})` : ''}`} delay={350}>
          <QuoteCarousel quotes={activeQuotes} />
        </ChartCard>
      )}
    </div>
  );
}

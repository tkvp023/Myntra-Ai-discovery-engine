'use client';
import { SOURCE_COLORS, SEGMENT_COLORS, SEGMENT_LABELS } from '@/lib/constants';

interface FilterBarProps {
  /** Available data sources — pass empty array to hide source filter */
  sources?: string[];
  selectedSource: string;
  onSourceChange: (source: string) => void;
  /** Available segments — pass empty array to hide segment filter */
  segments?: string[];
  selectedSegment: string;
  onSegmentChange: (segment: string) => void;
  /** Total doc count to display */
  totalDocs?: number;
}

/**
 * FilterBar — horizontal row of source + segment filter pills.
 * Used at the top of chart sections that support cross-filtering.
 */
export default function FilterBar({
  sources = [],
  selectedSource,
  onSourceChange,
  segments = ['all', 'gen_z', 'millennial', 'gen_x'],
  selectedSegment,
  onSegmentChange,
  totalDocs,
}: FilterBarProps) {
  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: 12,
        padding: '12px 0',
        borderBottom: '1px solid var(--border)',
        marginBottom: 20,
      }}
    >
      {/* Doc count */}
      {totalDocs !== undefined && (
        <span style={{ fontSize: 13, color: 'var(--text-muted)', marginRight: 4 }}>
          {totalDocs.toLocaleString()} docs
        </span>
      )}

      {/* Segment pills */}
      {segments.length > 0 && (
        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
          {segments.map((seg) => {
            const active = seg === selectedSegment;
            const color = seg === 'all' ? 'var(--pink)' : (SEGMENT_COLORS[seg] || '#6b7280');
            return (
              <button
                key={seg}
                onClick={() => onSegmentChange(seg)}
                style={{
                  padding: '4px 12px',
                  borderRadius: 20,
                  border: `1px solid ${active ? color : 'var(--border)'}`,
                  background: active ? `${color}22` : 'transparent',
                  color: active ? color : 'var(--text-muted)',
                  fontSize: 12,
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                }}
              >
                {SEGMENT_LABELS[seg] || seg}
              </button>
            );
          })}
        </div>
      )}

      {/* Source pills */}
      {sources.length > 0 && (
        <>
          <div style={{ width: 1, height: 20, background: 'var(--border)' }} />
          <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
            {['all', ...sources].map((src) => {
              const active = src === selectedSource;
              const color = src === 'all' ? 'var(--teal)' : (SOURCE_COLORS[src] || '#6b7280');
              return (
                <button
                  key={src}
                  onClick={() => onSourceChange(src)}
                  style={{
                    padding: '4px 12px',
                    borderRadius: 20,
                    border: `1px solid ${active ? color : 'var(--border)'}`,
                    background: active ? `${color}22` : 'transparent',
                    color: active ? color : 'var(--text-muted)',
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: 'pointer',
                    transition: 'all 0.15s',
                  }}
                >
                  {src === 'all' ? 'All Sources' : src}
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

'use client';
import { useInView } from 'react-intersection-observer';

interface BreakdownItem {
  label: string;
  tag: string;
  count: number;
  pct: number;
  avg_confidence?: number;
  color: string;
}

interface HorizontalBarProps {
  data: BreakdownItem[];
  title?: string;
  maxBars?: number;
  showCount?: boolean;
}

function ConfidenceDot({ conf }: { conf?: number }) {
  if (conf === undefined) return null;
  const color = conf >= 0.8 ? '#84cc16' : conf >= 0.6 ? '#fbbf24' : '#ef4444';
  return (
    <span
      title={`Confidence: ${(conf * 100).toFixed(0)}%`}
      style={{
        display: 'inline-block',
        width: 8, height: 8,
        borderRadius: '50%',
        background: color,
        marginLeft: 6,
        verticalAlign: 'middle',
        flexShrink: 0,
      }}
    />
  );
}

export default function HorizontalBar({ data, title, maxBars = 8, showCount = true }: HorizontalBarProps) {
  const { ref, inView } = useInView({ threshold: 0.2, triggerOnce: true });
  const visible = data.slice(0, maxBars);

  return (
    <div ref={ref}>
      {title && (
        <p style={{ fontSize: 13, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 16 }}>
          {title}
        </p>
      )}
      <div className="bar-row">
        {visible.map((item, i) => (
          <div key={`${item.tag || item.label || 'bar'}-${i}`} className="bar-item" style={{ animationDelay: `${i * 60}ms` }}>
            <div className="bar-meta">
              <span className="bar-label" style={{ display: 'flex', alignItems: 'center' }}>
                {item.label}
                <ConfidenceDot conf={item.avg_confidence} />
              </span>
              <span className="bar-value">
                {item.pct.toFixed(1)}%
                {showCount && <span style={{ marginLeft: 6, opacity: 0.5 }}>({item.count.toLocaleString()})</span>}
              </span>
            </div>
            <div className="bar-track">
              <div
                className="bar-fill"
                style={{
                  width: inView ? `${item.pct}%` : '0%',
                  background: `linear-gradient(90deg, ${item.color}cc, ${item.color})`,
                  transition: `width ${500 + i * 80}ms ${i * 60}ms ease-out`,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

'use client';
import { useEffect, useRef, useState, useId } from 'react';
import { useInView } from 'react-intersection-observer';
import { AreaChart, Area, ResponsiveContainer, Tooltip } from 'recharts';

interface StatCardProps {
  label: string;
  value: number;
  unit: 'count' | 'percent';
  sparkline: number[];
  trend?: 'up' | 'down' | 'stable';
  trend_pct?: number;
  delay?: number;
}

const KPI_CONFIG: Record<string, { color: string; icon: string; desc: string }> = {
  'Reviews Analyzed': { color: '#ff2d55', icon: '📊', desc: '4 Primary + 1 Secondary' },
  'Quality Doubt': { color: '#a855f7', icon: '🧵', desc: 'Fabric & texture uncertainty' },
  'Waiting for Sale': { color: '#2dd4bf', icon: '🏷️', desc: 'Price drop / flash deals' },
  'Return Policy Concern': { color: '#06b6d4', icon: '📦', desc: 'Doorstep exchange friction' },
  'Social Validation Needed': { color: '#fbbf24', icon: '💬', desc: 'Peer & influencer advice' },
  'Unmet Needs Identified': { color: '#8b5cf6', icon: '💡', desc: 'High-signal feature gaps' },
};

function formatValue(value: number, unit: string) {
  if (unit === 'percent') return `${value.toFixed(1)}%`;
  if (value >= 1000) return Math.round(value).toLocaleString();
  return Math.round(value).toString();
}

function AnimatedNumber({ target, unit, duration = 1000 }: { target: number; unit: string; duration?: number }) {
  const [current, setCurrent] = useState(0);
  const startTime = useRef<number | null>(null);

  useEffect(() => {
    startTime.current = null;
    const step = (timestamp: number) => {
      if (!startTime.current) startTime.current = timestamp;
      const progress = Math.min((timestamp - startTime.current) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // cubic ease-out
      setCurrent(eased * target);
      if (progress < 1) requestAnimationFrame(step);
    };
    const id = requestAnimationFrame(step);
    return () => cancelAnimationFrame(id);
  }, [target, duration]);

  return <>{formatValue(current, unit)}</>;
}

export default function StatCard({
  label,
  value,
  unit,
  sparkline,
  delay = 0,
}: StatCardProps) {
  const { ref, inView } = useInView({ threshold: 0.2, triggerOnce: true });
  const rawId = useId();
  const gradId = `spark-${rawId.replace(/:/g, '')}`;
  const config = KPI_CONFIG[label] || { color: '#ff2d55', icon: '📈', desc: '' };
  const sparkData = (sparkline && sparkline.length > 0 ? sparkline : [value * 0.6, value * 0.8, value]).map((v, i) => ({ v, i }));

  return (
    <div
      ref={ref}
      className="card stat-card animate-enter"
      style={{
        animationDelay: `${delay}ms`,
        opacity: inView ? 1 : 0,
        minHeight: 148,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '18px 20px',
      }}
    >
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
          <span style={{ fontSize: 13, color: 'var(--text-secondary)', fontWeight: 600 }}>
            {label}
          </span>
          <span
            style={{
              fontSize: 14,
              width: 28,
              height: 28,
              borderRadius: 8,
              background: `${config.color}18`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {config.icon}
          </span>
        </div>

        <div
          className="stat-value tabular-nums"
          style={{
            fontSize: '32px',
            fontWeight: 800,
            color: 'var(--text-primary)',
            letterSpacing: '-0.03em',
            lineHeight: 1.1,
          }}
        >
          {inView ? <AnimatedNumber target={value} unit={unit} /> : formatValue(value, unit)}
        </div>

        {config.desc && (
          <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginTop: 4, fontWeight: 500 }}>
            {config.desc}
          </div>
        )}
      </div>

      {/* Sparkline */}
      <div style={{ height: 36, marginTop: 10 }}>
        <ResponsiveContainer width="100%" height={36}>
          <AreaChart data={sparkData} margin={{ top: 2, right: 0, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={config.color} stopOpacity={0.35} />
                <stop offset="100%" stopColor={config.color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="v"
              stroke={config.color}
              strokeWidth={2}
              fill={`url(#${gradId})`}
              dot={false}
              isAnimationActive={inView}
              animationDuration={800}
            />
            <Tooltip
              contentStyle={{
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border-strong)',
                borderRadius: 8,
                fontSize: 11,
                padding: '4px 8px',
                boxShadow: 'var(--shadow-card)',
              }}
              itemStyle={{ color: 'var(--text-primary)', fontWeight: 600 }}
              formatter={(val: any) => [formatValue(Number(val), unit), label]}
              labelFormatter={() => ''}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

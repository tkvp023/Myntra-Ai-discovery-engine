'use client';
import { useEffect, useRef, useState } from 'react';
import { useInView } from 'react-intersection-observer';
import {
  AreaChart, Area, ResponsiveContainer, Tooltip,
} from 'recharts';

interface StatCardProps {
  label: string;
  value: number;
  unit: 'count' | 'percent';
  sparkline: number[];
  trend: 'up' | 'down' | 'stable';
  trend_pct: number;
  delay?: number;
}

function formatValue(value: number, unit: string) {
  if (unit === 'percent') return `${value.toFixed(1)}%`;
  if (value >= 1000) return value.toLocaleString();
  return value.toString();
}

function AnimatedNumber({ target, unit, duration = 1200 }: { target: number; unit: string; duration?: number }) {
  const [current, setCurrent] = useState(0);
  const startTime = useRef<number | null>(null);

  useEffect(() => {
    startTime.current = null;
    const step = (timestamp: number) => {
      if (!startTime.current) startTime.current = timestamp;
      const progress = Math.min((timestamp - startTime.current) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      setCurrent(eased * target);
      if (progress < 1) requestAnimationFrame(step);
    };
    const id = requestAnimationFrame(step);
    return () => cancelAnimationFrame(id);
  }, [target, duration]);

  return <>{formatValue(current, unit)}</>;
}

export default function StatCard({
  label, value, unit, sparkline, trend, trend_pct, delay = 0,
}: StatCardProps) {
  const { ref, inView } = useInView({ threshold: 0.3, triggerOnce: true });
  const sparkData = sparkline.map((v, i) => ({ v, i }));

  const trendArrow = trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→';
  const trendClass = trend === 'up' ? 'up' : trend === 'down' ? 'down' : 'stable';

  return (
    <div
      ref={ref}
      className="card stat-card animate-enter"
      style={{
        animationDelay: `${delay}ms`,
        opacity: inView ? 1 : 0,
        minHeight: 140,
      }}
    >
      <div className="stat-trend" style={{}} data-trend={trendClass}>
        <span className={`stat-trend ${trendClass}`}>
          {trendArrow}{trend_pct}%
        </span>
      </div>

      <div className="stat-value">
        {inView ? <AnimatedNumber target={value} unit={unit} /> : '0'}
      </div>

      <div className="stat-label">{label}</div>

      {/* Sparkline */}
      <div style={{ marginTop: 'auto', height: 40 }}>
        <ResponsiveContainer width="100%" height={40}>
          <AreaChart data={sparkData} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id={`spark-${label}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#ff3f6c" stopOpacity={0.4} />
                <stop offset="100%" stopColor="#ff3f6c" stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="v"
              stroke="#ff3f6c"
              strokeWidth={2}
              fill={`url(#spark-${label})`}
              dot={false}
              animationDuration={inView ? 800 : 0}
            />
            <Tooltip
              contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
              itemStyle={{ color: 'var(--text-primary)' }}
              formatter={(val: any) => [formatValue(Number(val), unit), '']}
              labelFormatter={() => ''}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

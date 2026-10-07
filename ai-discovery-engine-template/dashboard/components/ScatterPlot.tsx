'use client';
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ZAxis, Cell,
} from 'recharts';
import { useInView } from 'react-intersection-observer';
import { CHART_COLORS } from '@/lib/constants';

interface ScatterPoint {
  x: number;
  y: number;
  z?: number;   // bubble size
  label?: string;
  color?: string;
}

interface ScatterPlotProps {
  data: ScatterPoint[];
  xLabel?: string;
  yLabel?: string;
  zLabel?: string;
  xUnit?: string;
  yUnit?: string;
  height?: number;
}

/**
 * ScatterPlot — Recharts scatter/bubble chart with dark theme.
 * Optional Z dimension drives bubble size (ZAxis).
 */
export default function ScatterPlot({
  data,
  xLabel = 'X',
  yLabel = 'Y',
  zLabel = 'Size',
  xUnit = '',
  yUnit = '',
  height = 300,
}: ScatterPlotProps) {
  const { ref, inView } = useInView({ threshold: 0.15, triggerOnce: true });

  if (!data || data.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">⚡</div>
        <div className="empty-state-text">No data available</div>
      </div>
    );
  }

  const hasZ = data.some((d) => d.z !== undefined);

  return (
    <div ref={ref} style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 8, right: 8, left: -16, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.6} />
          <XAxis
            dataKey="x"
            type="number"
            name={xLabel}
            tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `${v}${xUnit}`}
            label={{ value: xLabel, position: 'insideBottom', offset: -4, fill: 'var(--text-muted)', fontSize: 11 }}
          />
          <YAxis
            dataKey="y"
            type="number"
            name={yLabel}
            tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `${v}${yUnit}`}
          />
          {hasZ && <ZAxis dataKey="z" range={[40, 400]} name={zLabel} />}
          <Tooltip
            cursor={{ strokeDasharray: '3 3', stroke: 'var(--border)' }}
            content={({ payload }) => {
              if (!payload || payload.length === 0) return null;
              const d = payload[0]?.payload as ScatterPoint;
              return (
                <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, padding: '8px 12px', fontSize: 12 }}>
                  {d.label && <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>{d.label}</div>}
                  <div style={{ color: 'var(--text-secondary)' }}>{xLabel}: <strong>{d.x}{xUnit}</strong></div>
                  <div style={{ color: 'var(--text-secondary)' }}>{yLabel}: <strong>{d.y}{yUnit}</strong></div>
                  {d.z !== undefined && <div style={{ color: 'var(--text-secondary)' }}>{zLabel}: <strong>{d.z}</strong></div>}
                </div>
              );
            }}
          />
          <Scatter
            data={data}
            isAnimationActive={inView}
            animationDuration={700}
          >
            {data.map((entry, i) => (
              <Cell
                key={`cell-${i}`}
                fill={entry.color || CHART_COLORS[i % CHART_COLORS.length]}
                fillOpacity={0.85}
                stroke={entry.color || CHART_COLORS[i % CHART_COLORS.length]}
                strokeWidth={1}
                strokeOpacity={0.4}
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

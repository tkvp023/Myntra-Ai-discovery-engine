'use client';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import { useInView } from 'react-intersection-observer';
import { CHART_COLORS } from '@/lib/constants';

interface StackedBarProps {
  /**
   * data shape: array of objects where each object is one stack group.
   * Each object has a `name` key plus one key per stacked segment.
   * e.g. [ { name: 'Jan 2025', sizing: 30, price: 22, quality: 15 }, ... ]
   */
  data: Record<string, string | number>[];
  categoryKey?: string;
  seriesKeys: string[];
  seriesLabels?: Record<string, string>;
  colors?: string[];
  unit?: string;
  height?: number;
  /** If true, stacks to 100% (normalised) */
  normalised?: boolean;
}

const TOOLTIP_STYLE = {
  background: 'var(--bg-elevated)',
  border: '1px solid var(--border)',
  borderRadius: 8,
  fontSize: 12,
};

export default function StackedBar({
  data,
  categoryKey = 'name',
  seriesKeys,
  seriesLabels,
  colors,
  unit = '%',
  height = 280,
}: StackedBarProps) {
  const { ref, inView } = useInView({ threshold: 0.15, triggerOnce: true });
  const palette = colors || CHART_COLORS;

  if (!data || data.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📊</div>
        <div className="empty-state-text">No data available</div>
      </div>
    );
  }

  return (
    <div ref={ref} style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 8, right: 8, left: -16, bottom: 0 }}
          barCategoryGap="30%"
        >
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.6} vertical={false} />
          <XAxis
            dataKey={categoryKey}
            tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `${v}${unit}`}
          />
          <Tooltip
            contentStyle={TOOLTIP_STYLE}
            itemStyle={{ color: 'var(--text-primary)' }}
            formatter={((value: any, name: any) => [
              `${value ?? 0}${unit}`,
              seriesLabels?.[String(name)] ?? String(name ?? ''),
            ]) as any}
            cursor={{ fill: 'var(--bg-card-hover)', opacity: 0.5 }}
          />
          <Legend
            wrapperStyle={{ fontSize: 12, color: 'var(--text-secondary)', paddingTop: 12 }}
            formatter={(value: string) => seriesLabels?.[value] ?? value}
          />
          {seriesKeys.map((key, i) => (
            <Bar
              key={key}
              dataKey={key}
              name={key}
              stackId="stack"
              fill={palette[i % palette.length]}
              radius={i === seriesKeys.length - 1 ? [4, 4, 0, 0] : [0, 0, 0, 0]}
              isAnimationActive={inView}
              animationDuration={700}
              animationBegin={i * 60}
              opacity={0.9}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

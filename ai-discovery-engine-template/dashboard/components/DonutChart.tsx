'use client';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useInView } from 'react-intersection-observer';

interface DonutChartProps {
  data: { label?: string; source?: string; tag?: string; count: number; pct: number; color: string }[];
  title?: string;
  centerLabel?: string;
}

const RADIAN = Math.PI / 180;
function CustomLabel({ cx, cy, midAngle, innerRadius, outerRadius, pct }: any) {
  if (pct < 5) return null;
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);
  return (
    <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central" fontSize={11} fontWeight={600}>
      {pct.toFixed(0)}%
    </text>
  );
}

export default function DonutChart({ data, title, centerLabel }: DonutChartProps) {
  const { ref, inView } = useInView({ threshold: 0.3, triggerOnce: true });
  const total = data?.reduce((s, d) => s + (d.count || 0), 0) || 0;
  const safeTotal = total || 1;

  return (
    <div ref={ref}>
      {title && (
        <p style={{ fontSize: 13, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 16 }}>
          {title}
        </p>
      )}
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={data}
            dataKey="count"
            nameKey={data[0]?.source !== undefined ? 'source' : 'label'}
            cx="50%"
            cy="50%"
            innerRadius="55%"
            outerRadius="80%"
            paddingAngle={2}
            animationBegin={inView ? 0 : 99999}
            animationDuration={800}
            labelLine={false}
            label={CustomLabel}
          >
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.color} stroke="transparent" />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border)',
              borderRadius: 10,
              fontSize: 13,
            }}
            itemStyle={{ color: 'var(--text-primary)' }}
            formatter={(val: any, name: any) => [
              `${Number(val).toLocaleString()} (${((Number(val) / safeTotal) * 100).toFixed(1)}%)`,
              String(name ?? ''),
            ]}
          />
          <Legend
            layout="vertical"
            align="right"
            verticalAlign="middle"
            formatter={(value) => (
              <span style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>

      {/* Center total */}
      <div style={{ textAlign: 'center', marginTop: -20, position: 'relative', zIndex: 1 }}>
        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{centerLabel || 'total'}</div>
        <div style={{ fontSize: 20, fontWeight: 800, fontFamily: 'Outfit, sans-serif', color: 'var(--text-primary)' }}>
          {total.toLocaleString()}
        </div>
      </div>
    </div>
  );
}

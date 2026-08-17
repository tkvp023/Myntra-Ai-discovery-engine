'use client';
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, Tooltip, ResponsiveContainer, PolarRadiusAxis } from 'recharts';

export default function RadarChartComponent({ data }: { data: any[] }) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <RadarChart data={data} margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
        <PolarGrid stroke="rgba(255,255,255,0.08)" />
        <PolarAngleAxis
          dataKey="factor"
          tick={{ fill: 'rgba(255,255,255,0.65)', fontSize: 12 }}
        />
        <PolarRadiusAxis
          angle={90}
          domain={[0, 40]}
          tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 10 }}
          axisLine={false}
        />
        <Radar
          name="Importance %"
          dataKey="importance"
          stroke="#ff3f6c"
          fill="#ff3f6c"
          fillOpacity={0.25}
          strokeWidth={2}
          dot={{ r: 4, fill: '#ff3f6c', strokeWidth: 0 }}
        />
        <Radar
          name="Negative %"
          dataKey="negative_pct"
          stroke="#a855f7"
          fill="#a855f7"
          fillOpacity={0.15}
          strokeWidth={1.5}
          strokeDasharray="4 2"
          dot={false}
        />
        <Tooltip
          contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 10, fontSize: 12 }}
          formatter={(val: any, name: any) => [`${Number(val)}%`, String(name ?? '')]}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}

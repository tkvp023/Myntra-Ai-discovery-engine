'use client';

interface Matrix { rows: string[]; columns: string[]; values: number[][]; }

export default function HeatmapChart({ matrix }: { matrix: Matrix }) {
  if (!matrix?.values?.length) return <div className="empty-state"><div className="empty-state-icon">🔲</div><div className="empty-state-text">No comparison data yet</div></div>;

  const allVals = matrix.values.flat();
  const maxVal = Math.max(...allVals, 1);

  function getColor(val: number): string {
    const intensity = val / maxVal;
    if (intensity < 0.3) return `rgba(26,26,46,${0.5 + intensity})`;
    if (intensity < 0.6) return `rgba(168,85,247,${0.3 + intensity * 0.5})`;
    return `rgba(255,63,108,${0.4 + intensity * 0.5})`;
  }

  function getTextColor(val: number): string {
    return val / maxVal > 0.35 ? '#ffffff' : 'var(--text-primary)';
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ borderCollapse: 'separate', borderSpacing: 3, minWidth: 480 }}>
        <thead>
          <tr>
            <th style={{ width: 120 }} />
            {matrix.columns.map((col) => (
              <th key={col} style={{ padding: '6px 8px', fontSize: 12, color: 'var(--text-secondary)', fontWeight: 600, textAlign: 'center' }}>
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.rows.map((row, ri) => (
            <tr key={row}>
              <td style={{ fontSize: 12, color: 'var(--text-secondary)', paddingRight: 12, fontWeight: 500, whiteSpace: 'nowrap' }}>
                {row.replace('_', ' ')}
              </td>
              {matrix.values[ri].map((val, ci) => (
                <td key={ci} style={{
                  background: getColor(val),
                  color: getTextColor(val),
                  textAlign: 'center',
                  padding: '10px 16px',
                  borderRadius: 6,
                  fontSize: 13,
                  fontWeight: 700,
                  fontFamily: 'Outfit, sans-serif',
                  minWidth: 48,
                  transition: 'transform 0.15s ease',
                  cursor: 'default',
                }}
                  title={`${row} × ${matrix.columns[ci]}: ${val}`}
                >
                  {val}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      {/* Color scale legend */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 16 }}>
        <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Low</span>
        <div style={{ flex: 1, height: 6, borderRadius: 3, background: 'linear-gradient(90deg, #1a1a2e, #a855f7, #ff3f6c)' }} />
        <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>High</span>
      </div>
    </div>
  );
}

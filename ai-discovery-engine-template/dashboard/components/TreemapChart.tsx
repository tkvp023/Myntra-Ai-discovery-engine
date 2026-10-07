'use client';

const THEME_COLORS = ['#ff3f6c','#ff7849','#a855f7','#2dd4bf','#3b82f6','#fbbf24'];

interface TreeNode { name: string; value: number; }
interface TreeTheme { theme: string; children: TreeNode[]; }

export default function TreemapChart({ data }: { data: TreeTheme[] }) {
  if (!data || data.length === 0)
    return <div className="empty-state"><div className="empty-state-icon">🗺️</div><div className="empty-state-text">No needs data yet</div></div>;

  const grandTotal = data.reduce((s, theme) => s + theme.children.reduce((a, c) => a + c.value, 0), 0) || 1;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {data.map((theme, ti) => {
        const themeTotal = theme.children.reduce((s, c) => s + c.value, 0);
        const themePct = ((themeTotal / grandTotal) * 100).toFixed(1);
        const color = THEME_COLORS[ti % THEME_COLORS.length];
        return (
          <div key={theme.theme}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
              <span style={{ fontSize: 13, fontWeight: 700, color }}>{theme.theme}</span>
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{themePct}% of all needs · {themeTotal.toLocaleString()} mentions</span>
            </div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {theme.children.map((child) => {
                const pct = (child.value / grandTotal) * 100;
                const minW = 80;
                const width = Math.max(minW, Math.round(pct * 8));
                return (
                  <div
                    key={child.name}
                    title={`${child.name}: ${child.value.toLocaleString()} mentions`}
                    style={{
                      width,
                      background: `${color}22`,
                      border: `1px solid ${color}44`,
                      borderRadius: 8,
                      padding: '10px 12px',
                      display: 'flex', flexDirection: 'column', gap: 4,
                      transition: 'background 0.15s, transform 0.15s',
                      cursor: 'default',
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLElement).style.background = `${color}44`;
                      (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)';
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLElement).style.background = `${color}22`;
                      (e.currentTarget as HTMLElement).style.transform = 'translateY(0)';
                    }}
                  >
                    <span style={{ fontSize: 11, color, fontWeight: 700, lineHeight: 1.3 }}>{child.name}</span>
                    <span style={{ fontSize: 18, fontFamily: 'Outfit', fontWeight: 800, color: 'var(--text-primary)' }}>
                      {child.value.toLocaleString()}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

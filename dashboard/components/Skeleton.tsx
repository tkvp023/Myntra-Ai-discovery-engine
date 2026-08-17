'use client';

/**
 * Reusable skeleton placeholder components with shimmer animation.
 * Used by Next.js loading.tsx files for instant visual feedback during route transitions.
 */

function SkeletonBlock({ width, height, borderRadius = 8, style }: {
  width?: string | number; height?: string | number; borderRadius?: number; style?: React.CSSProperties;
}) {
  return (
    <div className="skeleton-shimmer" style={{
      width: width || '100%',
      height: height || 20,
      borderRadius,
      ...style,
    }} />
  );
}

export function SkeletonStatCard() {
  return (
    <div className="card" style={{ padding: 20 }}>
      <SkeletonBlock width="50%" height={14} />
      <div style={{ height: 8 }} />
      <SkeletonBlock width="40%" height={32} />
      <div style={{ height: 12 }} />
      <SkeletonBlock width="100%" height={40} borderRadius={6} />
    </div>
  );
}

export function SkeletonChart({ height = 240 }: { height?: number }) {
  return (
    <div className="card">
      <div className="card-header">
        <SkeletonBlock width="35%" height={14} />
        <SkeletonBlock width={60} height={22} borderRadius={12} />
      </div>
      <div className="card-body">
        <SkeletonBlock width="100%" height={height} borderRadius={10} />
      </div>
    </div>
  );
}

export function SkeletonBar({ count = 5 }: { count?: number }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <SkeletonBlock width="25%" height={14} />
          <SkeletonBlock width={`${70 - i * 10}%`} height={24} borderRadius={6} />
        </div>
      ))}
    </div>
  );
}

export function SkeletonText({ lines = 3, widths }: { lines?: number; widths?: string[] }) {
  const defaultWidths = ['90%', '100%', '70%', '85%', '60%'];
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {Array.from({ length: lines }).map((_, i) => (
        <SkeletonBlock key={i} width={widths?.[i] || defaultWidths[i % defaultWidths.length]} height={14} />
      ))}
    </div>
  );
}

export function SkeletonQuote() {
  return (
    <div style={{
      padding: '14px 16px',
      background: 'rgba(255,255,255,0.02)',
      borderRadius: 'var(--radius-md)',
      borderLeft: '3px solid rgba(255,255,255,0.08)',
    }}>
      <SkeletonText lines={2} widths={['95%', '60%']} />
      <div style={{ height: 10 }} />
      <div style={{ display: 'flex', gap: 8 }}>
        <SkeletonBlock width={70} height={20} borderRadius={12} />
        <SkeletonBlock width={55} height={20} borderRadius={12} />
        <SkeletonBlock width={45} height={20} borderRadius={12} />
      </div>
    </div>
  );
}

export function SkeletonFilterBar() {
  return (
    <div style={{ display: 'flex', gap: 8, padding: '12px 0', borderBottom: '1px solid var(--border)', marginBottom: 20 }}>
      {[65, 55, 75, 50].map((w, i) => (
        <SkeletonBlock key={i} width={w} height={26} borderRadius={20} />
      ))}
    </div>
  );
}

export default SkeletonBlock;

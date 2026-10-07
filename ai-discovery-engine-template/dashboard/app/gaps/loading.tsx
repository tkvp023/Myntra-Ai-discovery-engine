import { SkeletonChart, SkeletonQuote } from '@/components/Skeleton';

export default function GapsLoading() {
  return (
    <div className="container" style={{ paddingTop: 32, paddingBottom: 64 }}>
      {/* Header skeleton */}
      <div className="page-header">
        <div className="skeleton-shimmer" style={{ width: '40%', height: 32, borderRadius: 8 }} />
        <div style={{ height: 8 }} />
        <div className="skeleton-shimmer" style={{ width: '75%', height: 16, borderRadius: 6 }} />
      </div>

      <div className="grid-2" style={{ marginBottom: 24 }}>
        <SkeletonChart height={280} />
        <SkeletonChart height={280} />
      </div>

      {/* Quotes skeleton */}
      <div className="card">
        <div className="card-header">
          <div className="skeleton-shimmer" style={{ width: '40%', height: 14, borderRadius: 6 }} />
        </div>
        <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <SkeletonQuote />
          <SkeletonQuote />
          <SkeletonQuote />
        </div>
      </div>
    </div>
  );
}

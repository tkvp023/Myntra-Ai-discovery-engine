import { SkeletonStatCard, SkeletonChart } from '@/components/Skeleton';

export default function SummaryLoading() {
  return (
    <div className="container" style={{ paddingTop: 32, paddingBottom: 64 }}>
      {/* Header skeleton */}
      <div className="page-header">
        <div className="skeleton-shimmer" style={{ width: '55%', height: 36, borderRadius: 8 }} />
        <div style={{ height: 8 }} />
        <div className="skeleton-shimmer" style={{ width: '70%', height: 16, borderRadius: 6 }} />
      </div>

      {/* KPI stat cards */}
      <div className="grid-4" style={{ marginBottom: 32 }}>
        <SkeletonStatCard />
        <SkeletonStatCard />
        <SkeletonStatCard />
        <SkeletonStatCard />
      </div>

      {/* Chart cards */}
      <div className="grid-2" style={{ marginBottom: 32 }}>
        <SkeletonChart height={260} />
        <SkeletonChart height={260} />
      </div>

      <SkeletonChart height={180} />
    </div>
  );
}

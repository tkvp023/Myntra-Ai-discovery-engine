'use client';
import { SOURCE_COLORS } from '@/lib/constants';

interface SourceBadgeProps {
  source: string;
}

/**
 * SourceBadge — renders a coloured pill for a data source (Play Store, Reddit, etc.)
 */
export default function SourceBadge({ source }: SourceBadgeProps) {
  const color = SOURCE_COLORS[source] || '#6b7280';
  return (
    <span
      className="badge badge-source"
      style={{
        background: `${color}22`,
        color,
        borderColor: `${color}44`,
        border: '1px solid',
      }}
    >
      {source}
    </span>
  );
}

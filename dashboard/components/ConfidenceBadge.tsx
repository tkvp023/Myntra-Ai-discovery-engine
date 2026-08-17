'use client';
import { confBadgeClass } from '@/lib/constants';

interface ConfidenceBadgeProps {
  confidence: number;
  showLabel?: boolean;
}

/**
 * ConfidenceBadge — shows confidence score with colour-coded badge.
 * High ≥ 80% → green, Mid ≥ 60% → yellow, Low < 60% → red.
 */
export default function ConfidenceBadge({ confidence, showLabel = true }: ConfidenceBadgeProps) {
  const cls = confBadgeClass(confidence);
  const pct = (confidence * 100).toFixed(0);
  return (
    <span className={`badge ${cls}`} title={`Confidence: ${pct}%`}>
      {showLabel ? `${pct}% conf` : `${pct}%`}
    </span>
  );
}

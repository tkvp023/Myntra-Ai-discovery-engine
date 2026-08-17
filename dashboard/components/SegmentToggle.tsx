'use client';

interface Segment { label: string; value: string; }
const SEGMENTS: Segment[] = [
  { label: 'All', value: 'all' },
  { label: 'Gen-Z', value: 'gen_z' },
  { label: 'Millennial', value: 'millennial' },
  { label: 'Gen-X', value: 'gen_x' },
];

interface SegmentToggleProps {
  value: string;
  onChange: (v: string) => void;
}

export default function SegmentToggle({ value, onChange }: SegmentToggleProps) {
  return (
    <div className="segment-toggle" role="group" aria-label="Segment filter">
      {SEGMENTS.map((seg) => (
        <button
          key={seg.value}
          className={`segment-btn ${value === seg.value ? 'active' : ''}`}
          onClick={() => onChange(seg.value)}
          aria-pressed={value === seg.value}
        >
          {seg.label}
        </button>
      ))}
    </div>
  );
}

import { getQuestion } from '@/lib/api';
import QuestionSection from '@/components/QuestionSection';
import { QUESTION_META } from '@/lib/constants';
import { notFound } from 'next/navigation';
import type { Metadata } from 'next';

export async function generateStaticParams() {
  return Array.from({ length: 10 }, (_, i) => ({ id: String(i + 1) }));
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const qid = parseInt(id);
  const data = await getQuestion(qid);
  return {
    title: `Q${qid}: ${data.question_short}`,
    description: data.question_text,
  };
}

export default async function QuestionPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const qid = parseInt(id);
  if (isNaN(qid) || qid < 1 || qid > 10) notFound();

  const data = await getQuestion(qid);
  const meta = QUESTION_META[qid];
  const isBoth = meta?.sourceType === 'both';

  return (
    <div className="container" style={{ paddingTop: 32, paddingBottom: 64 }}>
      <div className="page-header" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10, flexWrap: 'wrap' }}>
          <span style={{
            background: 'var(--gradient-brand)',
            color: '#fff',
            fontFamily: 'Outfit',
            fontWeight: 800,
            fontSize: 14,
            padding: '4px 14px',
            borderRadius: 20,
          }}>
            Question {qid}
          </span>
          <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            {data.total_relevant_docs.toLocaleString()} classified documents
          </span>

          {/* Source Derivation Badge */}
          <span
            style={{
              fontSize: 12,
              fontWeight: 700,
              padding: '4px 12px',
              borderRadius: 16,
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              background: isBoth ? 'rgba(6, 182, 212, 0.12)' : 'rgba(168, 85, 247, 0.12)',
              border: `1px solid ${isBoth ? 'rgba(6, 182, 212, 0.35)' : 'rgba(168, 85, 247, 0.35)'}`,
              color: isBoth ? '#06b6d4' : '#c084fc',
            }}
          >
            <span>{isBoth ? '🔄' : '⚡'}</span>
            Data Derivation: {meta?.sourceLabel || (isBoth ? 'Both Primary & Secondary Sources' : '4 Primary Discovery Sources')}
          </span>
        </div>

        <h1 style={{ marginBottom: 12 }}>{data.question_text}</h1>

        {/* Source Derivation Transparency Note */}
        {meta?.sourceDetail && (
          <div
            style={{
              background: 'var(--glass-bg)',
              border: '1px solid var(--border)',
              borderLeft: `3px solid ${isBoth ? '#06b6d4' : '#a855f7'}`,
              borderRadius: 'var(--radius-sm)',
              padding: '10px 16px',
              fontSize: 12.5,
              lineHeight: 1.5,
              color: 'var(--text-secondary)',
            }}
          >
            <strong style={{ color: 'var(--text-primary)' }}>Source Derivation: </strong>
            {meta.sourceDetail}
          </div>
        )}
      </div>

      <QuestionSection data={data} questionId={qid} />
    </div>
  );
}

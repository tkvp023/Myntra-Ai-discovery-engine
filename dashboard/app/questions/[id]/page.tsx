import { getQuestion } from '@/lib/api';
import QuestionSection from '@/components/QuestionSection';
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

  return (
    <div className="container" style={{ paddingTop: 32, paddingBottom: 64 }}>
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
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
            {data.total_relevant_docs.toLocaleString()} relevant documents
          </span>
        </div>
        <h1>{data.question_text}</h1>
      </div>

      <QuestionSection data={data} questionId={qid} />
    </div>
  );
}

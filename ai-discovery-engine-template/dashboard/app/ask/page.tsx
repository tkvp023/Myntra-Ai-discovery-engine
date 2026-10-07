import AskContent from '@/components/AskContent';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Ask the Data',
  description: 'Natural-language queries over 8,182+ classified reviews across 5 sources with source citations and segment filtering.',
};

export default function AskPage() {
  return <AskContent />;
}

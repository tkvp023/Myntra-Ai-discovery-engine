import AskContent from '@/components/AskContent';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Ask the Data',
  description: 'Natural-language queries over 87,000+ classified reviews with source citations and segment filtering.',
};

export default function AskPage() {
  return <AskContent />;
}

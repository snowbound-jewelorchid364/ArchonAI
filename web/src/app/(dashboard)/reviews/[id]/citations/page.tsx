'use client';

import { useParams } from 'next/navigation';
import { useReview } from '@/hooks/useReview';

export default function CitationsPage() {
  const { id } = useParams<{ id: string }>();
  const { review, isLoading } = useReview(id);

  if (isLoading) return <div className="p-8">Loading citations...</div>;

  const citations = review?.citations || [];

  return (
    <div className="space-y-4 p-8">
      <h1 className="text-2xl font-bold">Citations ({citations.length})</h1>
      {citations.map((c: any, i: number) => (
        <div key={i} className="rounded border p-4">
          <a href={c.url} target="_blank" rel="noopener noreferrer" className="font-medium text-blue-600 hover:underline">
            {c.title}
          </a>
          <p className="mt-1 text-sm text-gray-600">{c.excerpt}</p>
          <p className="mt-1 text-xs text-gray-400">Credibility: {(c.credibility_score * 100).toFixed(0)}%</p>
        </div>
      ))}
    </div>
  );
}

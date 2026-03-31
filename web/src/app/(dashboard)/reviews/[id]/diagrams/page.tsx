'use client';

import { useParams } from 'next/navigation';
import { useReview } from '@/hooks/useReview';
import { MermaidDiagram } from '@/components/review/MermaidDiagram';

export default function DiagramsPage() {
  const { id } = useParams<{ id: string }>();
  const { review, isLoading } = useReview(id);

  if (isLoading) return <div className="p-8">Loading diagrams...</div>;

  const diagrams = review?.diagrams || [];

  return (
    <div className="space-y-6 p-8">
      <h1 className="text-2xl font-bold">Architecture Diagrams</h1>
      {diagrams.length === 0 && <p className="text-gray-500">No diagrams generated for this review.</p>}
      {diagrams.map((d: any, i: number) => (
        <div key={i}>
          <h2 className="mb-2 text-lg font-semibold">{d.title}</h2>
          <MermaidDiagram chart={d.content} />
        </div>
      ))}
    </div>
  );
}

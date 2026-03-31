'use client';

import { useParams } from 'next/navigation';
import { useReview } from '@/hooks/useReview';
import { FindingsTable } from '@/components/review/FindingsTable';
import { ConfidenceIndicator } from '@/components/review/ConfidenceIndicator';

export default function ReviewDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { review, isLoading } = useReview(id);

  if (isLoading) return <div className="p-8">Loading review...</div>;
  if (!review) return <div className="p-8">Review not found</div>;

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{review.repo_url}</h1>
          <p className="text-sm text-gray-500">Mode: {review.mode} | Status: {review.status}</p>
        </div>
        <ConfidenceIndicator score={review.confidence || 0} />
      </div>
      {review.findings && <FindingsTable findings={review.findings} />}
    </div>
  );
}

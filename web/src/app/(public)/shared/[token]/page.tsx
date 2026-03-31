import { api } from '@/lib/api';

interface Props {
  params: { token: string };
}

export default async function SharedReviewPage({ params }: Props) {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/share/${params.token}`, {
    cache: 'no-store',
  });

  if (!res.ok) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-lg text-gray-500">This shared review has expired or does not exist.</p>
      </div>
    );
  }

  const review = await res.json();

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-8">
      <div className="rounded-lg border bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-bold">Architecture Review</h1>
        <p className="text-sm text-gray-500">{review.repo_url} | {review.mode}</p>
      </div>
      <div className="rounded-lg border bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold">Executive Summary</h2>
        <p className="whitespace-pre-wrap text-gray-700">{review.executive_summary}</p>
      </div>
      <div className="rounded-lg border bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold">Findings ({review.findings?.length || 0})</h2>
        {review.findings?.map((f: any, i: number) => (
          <div key={i} className="mb-3 rounded border-l-4 p-3" style={{
            borderColor: f.severity === 'CRITICAL' ? '#dc2626' : f.severity === 'HIGH' ? '#f97316' : f.severity === 'MEDIUM' ? '#eab308' : '#6b7280'
          }}>
            <p className="font-medium">{f.title}</p>
            <p className="text-sm text-gray-600">{f.recommendation}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

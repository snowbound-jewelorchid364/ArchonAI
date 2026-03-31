"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { SeverityBadge } from "@/components/review/SeverityBadge";
import type { ReviewListItem } from "@/types";

export default function ReviewsPage() {
  const [reviews, setReviews] = useState<ReviewListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listReviews()
      .then(setReviews)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="py-12 text-center text-gray-500">Loading reviews...</div>;
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Reviews</h1>
        <Link
          href="/reviews/new"
          className="rounded-lg bg-archon-500 px-4 py-2 text-sm font-medium text-white hover:bg-archon-600"
        >
          New Review
        </Link>
      </div>

      {reviews.length === 0 ? (
        <div className="mt-12 text-center">
          <p className="text-gray-500">No reviews yet.</p>
          <Link href="/reviews/new" className="mt-4 inline-block text-archon-600 hover:underline">
            Run your first architecture review →
          </Link>
        </div>
      ) : (
        <div className="mt-6 overflow-hidden rounded-xl border border-gray-200 bg-white">
          <table className="w-full text-left text-sm">
            <thead className="border-b bg-gray-50 text-xs uppercase text-gray-500">
              <tr>
                <th className="px-6 py-3">Repository</th>
                <th className="px-6 py-3">Mode</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Findings</th>
                <th className="px-6 py-3">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {reviews.map((r) => (
                <tr key={r.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <Link href={`/reviews/${r.id}`} className="font-medium text-archon-600 hover:underline">
                      {r.repo_url.replace("https://github.com/", "")}
                    </Link>
                  </td>
                  <td className="px-6 py-4 capitalize">{r.mode.replace("_", " ")}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
                      r.status === "COMPLETED" ? "bg-green-100 text-green-700" :
                      r.status === "RUNNING" ? "bg-blue-100 text-blue-700" :
                      r.status === "FAILED" ? "bg-red-100 text-red-700" :
                      "bg-gray-100 text-gray-700"
                    }`}>
                      {r.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {r.critical_count > 0 && <SeverityBadge severity="CRITICAL" count={r.critical_count} />}
                    {r.high_count > 0 && <SeverityBadge severity="HIGH" count={r.high_count} />}
                    <span className="text-gray-500">{r.finding_count} total</span>
                  </td>
                  <td className="px-6 py-4 text-gray-500">{new Date(r.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

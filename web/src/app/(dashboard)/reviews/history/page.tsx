"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";
import Link from "next/link";

interface ReviewSummary {
  id: string;
  repo_url: string;
  mode: string;
  status: string;
  finding_count: number;
  created_at: string;
}

interface DiffResult {
  review_a: string;
  review_b: string;
  added: string[];
  removed: string[];
  unchanged: string[];
}

const STATUS_COLORS: Record<string, string> = {
  completed: "bg-green-100 text-green-800",
  running: "bg-blue-100 text-blue-800",
  failed: "bg-red-100 text-red-800",
  partial: "bg-yellow-100 text-yellow-800",
};

export default function ReviewHistoryPage() {
  const [reviews, setReviews] = useState<ReviewSummary[]>([]);
  const [selectedA, setSelectedA] = useState<string>("");
  const [selectedB, setSelectedB] = useState<string>("");
  const [diff, setDiff] = useState<DiffResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .get<ReviewSummary[]>("/reviews/history")
      .then(setReviews)
      .finally(() => setLoading(false));
  }, []);

  async function runDiff() {
    if (!selectedA || !selectedB) return;
    const result = await apiClient.get<DiffResult>(
      `/reviews/history/diff?review_a=${selectedA}&review_b=${selectedB}`
    );
    setDiff(result);
  }

  if (loading) return <div className="p-8">Loading history...</div>;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Review History</h1>

      <div className="bg-white rounded-lg shadow overflow-hidden mb-8">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left">Repo</th>
              <th className="px-4 py-3 text-left">Mode</th>
              <th className="px-4 py-3 text-left">Status</th>
              <th className="px-4 py-3 text-left">Findings</th>
              <th className="px-4 py-3 text-left">Date</th>
              <th className="px-4 py-3 text-left">Compare</th>
            </tr>
          </thead>
          <tbody>
            {reviews.map((r) => (
              <tr key={r.id} className="border-t hover:bg-gray-50">
                <td className="px-4 py-3">
                  <Link href={`/reviews/${r.id}`} className="text-indigo-600 hover:underline">
                    {r.repo_url.replace("https://github.com/", "")}
                  </Link>
                </td>
                <td className="px-4 py-3 capitalize">{r.mode}</td>
                <td className="px-4 py-3">
                  <span
                    className={`px-2 py-0.5 text-xs rounded-full ${STATUS_COLORS[r.status] ?? "bg-gray-100 text-gray-800"}`}
                  >
                    {r.status}
                  </span>
                </td>
                <td className="px-4 py-3">{r.finding_count}</td>
                <td className="px-4 py-3">{new Date(r.created_at).toLocaleDateString()}</td>
                <td className="px-4 py-3">
                  <label className="flex items-center gap-1">
                    <input
                      type="radio"
                      name="compareA"
                      value={r.id}
                      onChange={() => setSelectedA(r.id)}
                    />{" "}
                    A
                    <input
                      type="radio"
                      name="compareB"
                      value={r.id}
                      onChange={() => setSelectedB(r.id)}
                      className="ml-2"
                    />{" "}
                    B
                  </label>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedA && selectedB && (
        <button
          onClick={runDiff}
          className="bg-indigo-600 text-white px-4 py-2 rounded mb-6"
        >
          Compare Selected Reviews
        </button>
      )}

      {diff && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Diff Results</h2>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <h3 className="font-medium text-green-700 mb-2">Added ({diff.added.length})</h3>
              {diff.added.map((id) => (
                <div key={id} className="text-sm bg-green-50 p-2 rounded mb-1">{id}</div>
              ))}
            </div>
            <div>
              <h3 className="font-medium text-red-700 mb-2">Removed ({diff.removed.length})</h3>
              {diff.removed.map((id) => (
                <div key={id} className="text-sm bg-red-50 p-2 rounded mb-1">{id}</div>
              ))}
            </div>
            <div>
              <h3 className="font-medium text-gray-700 mb-2">Unchanged ({diff.unchanged.length})</h3>
              {diff.unchanged.map((id) => (
                <div key={id} className="text-sm bg-gray-50 p-2 rounded mb-1">{id}</div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

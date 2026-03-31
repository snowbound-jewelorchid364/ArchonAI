"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

const MODES = [
  { value: "review", label: "Review", desc: "Audit existing codebase" },
  { value: "design", label: "Design", desc: "Architecture from scratch" },
  { value: "migration_planner", label: "Migration Planner", desc: "Modernisation roadmap" },
  { value: "compliance_auditor", label: "Compliance Auditor", desc: "SOC2/HIPAA/GDPR audit" },
  { value: "due_diligence", label: "Due Diligence", desc: "Investor/acquirer package" },
  { value: "incident_responder", label: "Incident Responder", desc: "P0/P1 triage" },
  { value: "cost_optimiser", label: "Cost Optimiser", desc: "Cloud cost reduction" },
  { value: "scaling_advisor", label: "Scaling Advisor", desc: "Growth readiness" },
];

export default function NewReviewPage() {
  const router = useRouter();
  const [repoUrl, setRepoUrl] = useState("");
  const [mode, setMode] = useState("review");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const isValidUrl = repoUrl.startsWith("https://github.com/") && repoUrl.split("/").length >= 5;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isValidUrl) return;

    setSubmitting(true);
    setError("");

    try {
      const result = await api.createReview(repoUrl, mode);
      router.push(`/reviews/${result.review_id}?job=${result.job_id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create review");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-2xl font-bold">New Architecture Review</h1>
      <p className="mt-2 text-gray-600">Submit a GitHub repository for analysis by 6 specialist agents.</p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-6">
        {/* Repo URL */}
        <div>
          <label htmlFor="repo" className="block text-sm font-medium text-gray-700">
            GitHub Repository URL
          </label>
          <input
            id="repo"
            type="url"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/org/repo"
            className="mt-1 block w-full rounded-lg border border-gray-300 px-4 py-3 text-sm shadow-sm focus:border-archon-500 focus:ring-archon-500"
            required
          />
          {repoUrl && !isValidUrl && (
            <p className="mt-1 text-sm text-red-500">Enter a valid GitHub repository URL</p>
          )}
        </div>

        {/* Mode selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Analysis Mode</label>
          <div className="mt-2 grid gap-3 sm:grid-cols-2">
            {MODES.map((m) => (
              <button
                key={m.value}
                type="button"
                onClick={() => setMode(m.value)}
                className={`rounded-lg border p-4 text-left transition-colors ${
                  mode === m.value
                    ? "border-archon-500 bg-archon-50 ring-1 ring-archon-500"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <div className="text-sm font-semibold">{m.label}</div>
                <div className="mt-1 text-xs text-gray-500">{m.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={!isValidUrl || submitting}
          className="w-full rounded-lg bg-archon-500 px-6 py-3 text-sm font-semibold text-white hover:bg-archon-600 disabled:opacity-50"
        >
          {submitting ? "Queuing review..." : "Run Architecture Review"}
        </button>
      </form>
    </div>
  );
}

"use client";

import React, { useEffect, useState } from "react";
import { HealthScoreRing } from "@/components/health/HealthScoreRing";
import { ScoreTrendChart } from "@/components/health/ScoreTrendChart";

interface DomainScore {
  software: number;
  cloud: number;
  security: number;
  data: number;
  integration: number;
  ai: number;
}

interface LatestScore {
  id: string;
  review_id: string;
  repo_url: string;
  overall: number;
  domains: DomainScore;
  created_at: string;
}

interface TrendPoint {
  date: string;
  overall: number;
}

export default function HealthPage() {
  const [scores, setScores] = useState<LatestScore[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [trend, setTrend] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchLatestScores() {
      try {
        // Fetch snapshots to get unique repo_urls, then latest score per repo
        const snapsRes = await fetch("/api/v1/memory/snapshots?limit=100");
        if (!snapsRes.ok) return;
        const snaps: { repo_url: string }[] = await snapsRes.json();
        const uniqueRepos = [...new Set(snaps.map((s) => s.repo_url))];

        const latestScores: LatestScore[] = [];
        await Promise.all(
          uniqueRepos.map(async (repo) => {
            const res = await fetch(`/api/v1/health-score/${encodeURIComponent(repo)}/latest`);
            if (res.ok) {
              const data = await res.json();
              latestScores.push(data);
            }
          })
        );
        setScores(latestScores.sort((a, b) => b.overall - a.overall));
      } finally {
        setLoading(false);
      }
    }
    fetchLatestScores();
  }, []);

  useEffect(() => {
    if (!selected) { setTrend([]); return; }
    async function fetchTrend() {
      const res = await fetch(`/api/v1/health-score/${encodeURIComponent(selected!)}/history?limit=30`);
      if (!res.ok) return;
      const history: LatestScore[] = await res.json();
      setTrend(
        [...history]
          .reverse()
          .map((h) => ({ date: h.created_at, overall: h.overall }))
      );
    }
    fetchTrend();
  }, [selected]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-zinc-400">
        Loading health scores...
      </div>
    );
  }

  if (scores.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-2 text-zinc-400">
        <span className="text-4xl">🏥</span>
        <p>No architecture reviews completed yet.</p>
        <p className="text-sm">Run a review to see your health score.</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Architecture Health</h1>
        <p className="text-zinc-400 text-sm mt-1">
          Health scores across all reviewed repositories, computed from finding severity.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {scores.map((score) => (
          <div
            key={score.repo_url}
            onClick={() => setSelected(selected === score.repo_url ? null : score.repo_url)}
            className={`bg-zinc-900 border rounded-xl p-5 cursor-pointer transition-all ${
              selected === score.repo_url
                ? "border-indigo-500 ring-1 ring-indigo-500/40"
                : "border-zinc-800 hover:border-zinc-600"
            }`}
          >
            <p className="text-xs text-zinc-400 truncate mb-4">{score.repo_url}</p>
            <HealthScoreRing overall={score.overall} domains={score.domains} size={110} />
          </div>
        ))}
      </div>

      {/* Trend drawer */}
      {selected && trend.length > 0 && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white">Score Trend</h2>
            <span className="text-xs text-zinc-400 truncate max-w-xs">{selected}</span>
          </div>
          <ScoreTrendChart data={trend} width={600} height={160} />
        </div>
      )}
    </div>
  );
}

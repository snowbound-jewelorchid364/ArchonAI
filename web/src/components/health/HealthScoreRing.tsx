"use client";

import React from "react";

interface DomainScore {
  software: number;
  cloud: number;
  security: number;
  data: number;
  integration: number;
  ai: number;
}

interface HealthScoreRingProps {
  overall: number;
  domains: DomainScore;
  size?: number;
}

function ringColor(score: number): string {
  if (score >= 80) return "#22c55e"; // green-500
  if (score >= 60) return "#f59e0b"; // amber-500
  return "#ef4444"; // red-500
}

export function HealthScoreRing({ overall, domains, size = 120 }: HealthScoreRingProps) {
  const radius = (size - 16) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (overall / 100) * circumference;
  const color = ringColor(overall);

  const domainEntries = Object.entries(domains) as [string, number][];

  return (
    <div className="flex flex-col items-center gap-4">
      {/* SVG ring */}
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#27272a"
          strokeWidth={10}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={10}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{ transition: "stroke-dashoffset 0.6s ease" }}
        />
      </svg>
      {/* Score label centred over ring */}
      <div className="relative" style={{ marginTop: -(size + 8) }}>
        <span
          className="absolute inset-0 flex items-center justify-center text-2xl font-bold"
          style={{ color, height: size }}
        >
          {Math.round(overall)}
        </span>
      </div>
      {/* Spacer so domain bars sit below */}
      <div style={{ height: 8 }} />
      {/* Domain bars */}
      <div className="w-full space-y-1">
        {domainEntries.map(([domain, score]) => (
          <div key={domain} className="flex items-center gap-2 text-xs">
            <span className="w-20 capitalize text-zinc-400">{domain}</span>
            <div className="flex-1 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${score}%`,
                  backgroundColor: ringColor(score),
                }}
              />
            </div>
            <span className="w-6 text-right" style={{ color: ringColor(score) }}>
              {Math.round(score)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

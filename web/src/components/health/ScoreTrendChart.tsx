"use client";

import React, { useRef, useState } from "react";

interface DataPoint {
  date: string;
  overall: number;
}

interface ScoreTrendChartProps {
  data: DataPoint[];
  width?: number;
  height?: number;
}

function scoreColor(s: number): string {
  if (s >= 80) return "#22c55e";
  if (s >= 60) return "#f59e0b";
  return "#ef4444";
}

export function ScoreTrendChart({ data, width = 400, height = 160 }: ScoreTrendChartProps) {
  const [tooltip, setTooltip] = useState<{ x: number; y: number; point: DataPoint } | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center text-zinc-500 text-sm" style={{ width, height }}>
        No trend data yet
      </div>
    );
  }

  const padX = 32;
  const padY = 16;
  const innerW = width - padX * 2;
  const innerH = height - padY * 2;

  const xStep = data.length > 1 ? innerW / (data.length - 1) : innerW;
  const points = data.map((d, i) => ({
    px: padX + i * xStep,
    py: padY + innerH - (d.overall / 100) * innerH,
    ...d,
  }));

  const polyline = points.map((p) => `${p.px},${p.py}`).join(" ");

  return (
    <div className="relative">
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="overflow-visible"
        onMouseLeave={() => setTooltip(null)}
      >
        {/* Y-axis gridlines at 0, 50, 100 */}
        {[0, 50, 100].map((v) => {
          const cy = padY + innerH - (v / 100) * innerH;
          return (
            <g key={v}>
              <line x1={padX} y1={cy} x2={width - padX} y2={cy} stroke="#27272a" strokeWidth={1} />
              <text x={padX - 4} y={cy + 4} textAnchor="end" fontSize={9} fill="#71717a">
                {v}
              </text>
            </g>
          );
        })}

        {/* Trend line */}
        <polyline
          points={polyline}
          fill="none"
          stroke="#6366f1"
          strokeWidth={2}
          strokeLinejoin="round"
        />

        {/* Dots */}
        {points.map((p, i) => (
          <circle
            key={i}
            cx={p.px}
            cy={p.py}
            r={4}
            fill={scoreColor(p.overall)}
            stroke="#09090b"
            strokeWidth={1.5}
            className="cursor-pointer"
            onMouseEnter={() => setTooltip({ x: p.px, y: p.py, point: p })}
          />
        ))}

        {/* X-axis date labels (first + last) */}
        {points.length > 0 && (
          <>
            <text x={points[0].px} y={height - 2} textAnchor="middle" fontSize={9} fill="#71717a">
              {points[0].date.slice(0, 10)}
            </text>
            {points.length > 1 && (
              <text x={points[points.length - 1].px} y={height - 2} textAnchor="middle" fontSize={9} fill="#71717a">
                {points[points.length - 1].date.slice(0, 10)}
              </text>
            )}
          </>
        )}
      </svg>

      {/* Tooltip */}
      {tooltip && (
        <div
          className="absolute z-10 bg-zinc-900 border border-zinc-700 rounded px-2 py-1 text-xs pointer-events-none"
          style={{ left: tooltip.x + 8, top: tooltip.y - 32 }}
        >
          <span className="text-zinc-400">{tooltip.point.date.slice(0, 10)}: </span>
          <span style={{ color: scoreColor(tooltip.point.overall) }} className="font-bold">
            {Math.round(tooltip.point.overall)}
          </span>
        </div>
      )}
    </div>
  );
}

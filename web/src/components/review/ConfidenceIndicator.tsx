'use client';

interface Props {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showGrade?: boolean;
}

function getGrade(score: number): string {
  if (score >= 0.9) return 'A';
  if (score >= 0.75) return 'B';
  if (score >= 0.6) return 'C';
  if (score >= 0.4) return 'D';
  return 'F';
}

function getColor(score: number): string {
  if (score >= 0.8) return 'text-green-600';
  if (score >= 0.6) return 'text-yellow-600';
  if (score >= 0.4) return 'text-orange-600';
  return 'text-red-600';
}

export function ConfidenceIndicator({ score, size = 'md', showGrade = true }: Props) {
  const grade = getGrade(score);
  const color = getColor(score);
  const pct = Math.round(score * 100);
  const radius = size === 'sm' ? 16 : size === 'lg' ? 32 : 24;
  const stroke = size === 'sm' ? 3 : size === 'lg' ? 5 : 4;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score * circumference);

  return (
    <div className="flex items-center gap-2">
      <svg width={radius * 2 + stroke * 2} height={radius * 2 + stroke * 2} className="transform -rotate-90">
        <circle cx={radius + stroke} cy={radius + stroke} r={radius} fill="none" stroke="currentColor"
          strokeWidth={stroke} className="text-muted" />
        <circle cx={radius + stroke} cy={radius + stroke} r={radius} fill="none" stroke="currentColor"
          strokeWidth={stroke} strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round" className={color} />
      </svg>
      <div className="flex flex-col">
        {showGrade && <span className={`font-bold text-lg ${color}`}>{grade}</span>}
        <span className="text-xs text-muted-foreground">{pct}% confidence</span>
      </div>
    </div>
  );
}

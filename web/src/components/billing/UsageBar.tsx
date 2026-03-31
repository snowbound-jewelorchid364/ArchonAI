interface UsageBarProps {
  used: number;
  limit: number;
  label: string;
}

export function UsageBar({ used, limit, label }: UsageBarProps) {
  const pct = Math.min((used / limit) * 100, 100);
  const color = pct > 90 ? 'bg-red-500' : pct > 70 ? 'bg-yellow-500' : 'bg-blue-500';

  return (
    <div>
      <div className="flex justify-between text-sm">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium">{used} / {limit}</span>
      </div>
      <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-gray-200">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

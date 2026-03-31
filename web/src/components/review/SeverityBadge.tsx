import { cn } from "@/lib/utils";
import { severityColor } from "@/lib/utils";
import type { Severity } from "@/types";

interface SeverityBadgeProps {
  severity: Severity;
  className?: string;
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold",
        severityColor(severity),
        className,
      )}
    >
      {severity}
    </span>
  );
}

import type { AgentProgress } from "@/types";

interface AgentProgressPanelProps {
  agents: AgentProgress[];
}

const ALL_AGENTS = [
  "software-architect",
  "cloud-architect",
  "security-architect",
  "data-architect",
  "integration-architect",
  "ai-architect",
];

export function AgentProgressPanel({ agents }: AgentProgressPanelProps) {
  const agentMap = new Map(agents.map((a) => [a.agent, a]));

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      {ALL_AGENTS.map((name) => {
        const agent = agentMap.get(name);
        const status = agent?.status || "PENDING";

        const statusStyles: Record<string, string> = {
          PENDING: "border-gray-800 text-gray-600",
          RUNNING: "border-yellow-600 text-yellow-400 animate-pulse",
          COMPLETED: "border-green-700 text-green-400",
          FAILED: "border-red-700 text-red-400",
        };

        const icons: Record<string, string> = {
          PENDING: "\u23F3",
          RUNNING: "\u26A1",
          COMPLETED: "\u2705",
          FAILED: "\u274C",
        };

        return (
          <div
            key={name}
            className={`border rounded-lg p-3 text-sm ${statusStyles[status]}`}
          >
            <div className="flex items-center gap-2">
              <span>{icons[status]}</span>
              <span className="font-medium truncate">
                {name.replace("-", " ").replace(/\b\w/g, (c) => c.toUpperCase())}
              </span>
            </div>
            <p className="text-xs mt-1 opacity-70">{status}</p>
            {agent?.finding_count !== undefined && (
              <p className="text-xs opacity-50">{agent.finding_count} findings</p>
            )}
          </div>
        );
      })}
    </div>
  );
}

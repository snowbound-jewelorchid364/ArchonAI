export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";

export type AgentStatusValue = "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";

export interface Citation {
  url: string;
  title: string;
  excerpt: string;
  published_date?: string;
  credibility_score: number;
}

export interface Finding {
  id: string;
  title: string;
  description: string;
  severity: Severity;
  domain: string;
  file_path?: string;
  line_number?: number;
  recommendation: string;
  citations: Citation[];
  confidence: number;
  from_codebase: boolean;
}

export interface Artifact {
  id: string;
  artifact_type: "ADR" | "TERRAFORM" | "DIAGRAM" | "RUNBOOK";
  title: string;
  content: string;
  filename: string;
}

export interface AgentProgress {
  agent: string;
  status: AgentStatusValue;
  finding_count?: number;
  error?: string;
}

export interface ReviewPackage {
  run_id: string;
  repo_url: string;
  mode: string;
  created_at: string;
  duration_seconds: number;
  executive_summary: string;
  findings: Finding[];
  artifacts: Artifact[];
  citations: Citation[];
  agent_statuses: Record<string, string>;
  partial: boolean;
}

export interface ReviewListItem {
  id: string;
  repo_url: string;
  mode: string;
  status: string;
  finding_count: number;
  critical_count: number;
  high_count: number;
  created_at: string;
  partial: boolean;
}


export interface ShareLink {
  token: string;
  url: string;
  expires_at: string | null;
}

export interface ReviewStats {
  total_unique_citations: number;
  avg_credibility: number;
  domains_covered: number;
  high_credibility_count: number;
}

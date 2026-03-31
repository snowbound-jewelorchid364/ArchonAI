import * as vscode from 'vscode';

export interface AgentProgress {
    agent: string;
    status: 'queued' | 'running' | 'complete' | 'failed';
    findingCount: number;
    duration?: number;
}

export interface Finding {
    id: string;
    title: string;
    severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
    domain: string;
    description: string;
    recommendation: string;
    file?: string;
    line?: number;
    citations: { url: string; title: string }[];
    confidence: number;
}

export interface ReviewResult {
    id: string;
    status: string;
    mode: string;
    findings: Finding[];
    agentProgress: AgentProgress[];
    completedAt?: string;
    executiveSummary?: string;
}

export class ArchonClient {
    private apiUrl: string;
    private apiKey: string;
    private abortController?: AbortController;

    constructor(apiUrl: string, apiKey: string) {
        this.apiUrl = apiUrl.replace(/\/$/, '');
        this.apiKey = apiKey;
    }

    updateConfig(apiUrl: string, apiKey: string): void {
        this.apiUrl = apiUrl.replace(/\/$/, '');
        this.apiKey = apiKey;
    }

    dispose(): void {
        this.abortController?.abort();
    }

    private headers(): Record<string, string> {
        return {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
        };
    }

    async startReview(repoUrl: string, mode: string, hitlMode: string): Promise<string> {
        const resp = await fetch(`${this.apiUrl}/api/v1/reviews`, {
            method: 'POST',
            headers: this.headers(),
            body: JSON.stringify({ repo_url: repoUrl, mode, hitl_mode: hitlMode }),
        });
        if (!resp.ok) {
            const err = await resp.text();
            throw new Error(`Failed to start review: ${resp.status} ${err}`);
        }
        const data = await resp.json();
        return data.job_id;
    }

    async *streamProgress(jobId: string): AsyncGenerator<AgentProgress> {
        this.abortController = new AbortController();
        const resp = await fetch(`${this.apiUrl}/api/v1/jobs/${jobId}/stream`, {
            headers: this.headers(),
            signal: this.abortController.signal,
        });

        if (!resp.ok || !resp.body) {
            throw new Error(`Failed to stream: ${resp.status}`);
        }

        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) { break; }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6).trim();
                    if (data === '[DONE]') { return; }
                    try {
                        yield JSON.parse(data) as AgentProgress;
                    } catch { /* skip malformed */ }
                }
            }
        }
    }

    cancelStream(): void {
        this.abortController?.abort();
    }

    async getReview(reviewId: string): Promise<ReviewResult> {
        const resp = await fetch(`${this.apiUrl}/api/v1/reviews/${reviewId}`, {
            headers: this.headers(),
        });
        if (!resp.ok) {
            throw new Error(`Failed to get review: ${resp.status}`);
        }
        return await resp.json();
    }

    async getHistory(): Promise<ReviewResult[]> {
        const resp = await fetch(`${this.apiUrl}/api/v1/reviews`, {
            headers: this.headers(),
        });
        if (!resp.ok) {
            throw new Error(`Failed to get history: ${resp.status}`);
        }
        return await resp.json();
    }

    async downloadPackage(reviewId: string): Promise<Buffer> {
        const resp = await fetch(`${this.apiUrl}/api/v1/packages/${reviewId}/download`, {
            headers: this.headers(),
        });
        if (!resp.ok) {
            throw new Error(`Failed to download: ${resp.status}`);
        }
        const arrayBuf = await resp.arrayBuffer();
        return Buffer.from(arrayBuf);
    }
}

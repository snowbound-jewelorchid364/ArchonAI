import * as vscode from 'vscode';
import { ArchonClient, AgentProgress } from '../archon-client';

const AGENT_LABELS: Record<string, string> = {
    software_architect: 'Software Architect',
    cloud_architect: 'Cloud Architect',
    security_architect: 'Security Architect',
    data_architect: 'Data Architect',
    integration_architect: 'Integration Architect',
    ai_architect: 'AI Architect',
};

const STATUS_ICONS: Record<string, string> = {
    queued: 'circle-outline',
    running: 'sync~spin',
    complete: 'check',
    failed: 'error',
};

export class AgentStatusProvider implements vscode.TreeDataProvider<AgentStatusItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<AgentStatusItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;
    private agents: Map<string, AgentProgress> = new Map();

    constructor(private client: ArchonClient) {
        // Initialize all 6 agents as queued
        Object.keys(AGENT_LABELS).forEach(agent => {
            this.agents.set(agent, { agent, status: 'queued', findingCount: 0 });
        });
    }

    updateAgent(progress: AgentProgress): void {
        this.agents.set(progress.agent, progress);
        this._onDidChangeTreeData.fire(undefined);
    }

    reset(): void {
        Object.keys(AGENT_LABELS).forEach(agent => {
            this.agents.set(agent, { agent, status: 'queued', findingCount: 0 });
        });
        this._onDidChangeTreeData.fire(undefined);
    }

    refresh(): void {
        this._onDidChangeTreeData.fire(undefined);
    }

    getTreeItem(element: AgentStatusItem): vscode.TreeItem {
        return element;
    }

    getChildren(): AgentStatusItem[] {
        return Array.from(this.agents.values()).map(agent => {
            const label = AGENT_LABELS[agent.agent] || agent.agent;
            const icon = STATUS_ICONS[agent.status] || 'circle-outline';
            const desc = agent.status === 'complete'
                ? `${agent.findingCount} findings`
                : agent.status;
            return new AgentStatusItem(label, desc, icon, agent);
        });
    }
}

export class AgentStatusItem extends vscode.TreeItem {
    constructor(
        label: string,
        description: string,
        iconName: string,
        public readonly agent: AgentProgress
    ) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.description = description;
        this.iconPath = new vscode.ThemeIcon(iconName);
        this.tooltip = `${label}: ${agent.status} (${agent.findingCount} findings)`;
    }
}

import * as vscode from 'vscode';
import { ArchonClient, Finding } from '../archon-client';

const SEVERITY_ICONS: Record<string, string> = {
    CRITICAL: 'error',
    HIGH: 'warning',
    MEDIUM: 'info',
    LOW: 'circle-outline',
    INFO: 'note',
};

const SEVERITY_ORDER: Record<string, number> = {
    CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3, INFO: 4,
};

export class FindingsProvider implements vscode.TreeDataProvider<FindingItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<FindingItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;
    private findings: Finding[] = [];

    constructor(private client: ArchonClient) {}

    setFindings(findings: Finding[]): void {
        this.findings = findings.sort(
            (a, b) => (SEVERITY_ORDER[a.severity] || 4) - (SEVERITY_ORDER[b.severity] || 4)
        );
        this._onDidChangeTreeData.fire(undefined);
    }

    refresh(): void {
        this._onDidChangeTreeData.fire(undefined);
    }

    getTreeItem(element: FindingItem): vscode.TreeItem {
        return element;
    }

    getChildren(): FindingItem[] {
        return this.findings.map(f => {
            const icon = SEVERITY_ICONS[f.severity] || 'note';
            return new FindingItem(f, icon);
        });
    }
}

export class FindingItem extends vscode.TreeItem {
    constructor(public readonly finding: Finding, iconName: string) {
        super(
            `[${finding.severity}] ${finding.title}`,
            vscode.TreeItemCollapsibleState.None
        );
        this.description = finding.domain;
        this.iconPath = new vscode.ThemeIcon(iconName);
        this.tooltip = new vscode.MarkdownString(
            `**${finding.title}**\n\n` +
            `**Severity:** ${finding.severity}\n` +
            `**Domain:** ${finding.domain}\n` +
            `**Confidence:** ${(finding.confidence * 100).toFixed(0)}%\n\n` +
            `${finding.description}\n\n` +
            `**Recommendation:** ${finding.recommendation}`
        );

        // If finding has a file reference, make it clickable
        if (finding.file) {
            this.command = {
                command: 'vscode.open',
                title: 'Open File',
                arguments: [
                    vscode.Uri.file(finding.file),
                    finding.line ? { selection: new vscode.Range(finding.line - 1, 0, finding.line - 1, 0) } : undefined
                ],
            };
        }
    }
}

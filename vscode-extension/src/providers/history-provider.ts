import * as vscode from 'vscode';
import { ArchonClient, ReviewResult } from '../archon-client';

export class HistoryProvider implements vscode.TreeDataProvider<HistoryItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<HistoryItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;
    private reviews: ReviewResult[] = [];

    constructor(private client: ArchonClient) {}

    async refresh(): Promise<void> {
        try {
            this.reviews = await this.client.getHistory();
        } catch {
            this.reviews = [];
        }
        this._onDidChangeTreeData.fire(undefined);
    }

    getTreeItem(element: HistoryItem): vscode.TreeItem {
        return element;
    }

    getChildren(): HistoryItem[] {
        return this.reviews.map(r => new HistoryItem(r));
    }
}

export class HistoryItem extends vscode.TreeItem {
    constructor(public readonly review: ReviewResult) {
        const date = review.completedAt
            ? new Date(review.completedAt).toLocaleDateString()
            : 'In progress';
        super(`${review.mode} - ${date}`, vscode.TreeItemCollapsibleState.None);
        this.description = `${review.findings.length} findings`;
        this.iconPath = new vscode.ThemeIcon(
            review.status === 'completed' ? 'check' : 'sync~spin'
        );
        this.tooltip = `Review ${review.id}\nMode: ${review.mode}\nFindings: ${review.findings.length}`;
    }
}

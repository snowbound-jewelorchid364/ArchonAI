import * as vscode from 'vscode';
import { ArchonClient, Finding } from '../archon-client';

export class FindingsWebviewProvider implements vscode.WebviewViewProvider {
    private _view?: vscode.WebviewView;

    constructor(
        private readonly extensionUri: vscode.Uri,
        private readonly client: ArchonClient
    ) {}

    resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ): void {
        this._view = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this.extensionUri],
        };
        webviewView.webview.html = this.getEmptyHtml();
    }

    showFindings(findings: Finding[]): void {
        if (!this._view) { return; }
        this._view.webview.html = this.getFindingsHtml(findings);
    }

    private getEmptyHtml(): string {
        return `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: var(--vscode-font-family); color: var(--vscode-foreground); padding: 10px; }
        .empty { text-align: center; opacity: 0.6; margin-top: 40px; }
    </style>
</head>
<body>
    <div class="empty">
        <p>No findings yet.</p>
        <p>Run a review to see results.</p>
    </div>
</body>
</html>`;
    }

    private getFindingsHtml(findings: Finding[]): string {
        const severityColors: Record<string, string> = {
            CRITICAL: '#ff4444',
            HIGH: '#ff8800',
            MEDIUM: '#ffcc00',
            LOW: '#44aa44',
            INFO: '#4488cc',
        };

        const rows = findings.map(f => {
            const color = severityColors[f.severity] || '#888';
            const citations = f.citations.map(
                c => `<a href="${c.url}">${c.title}</a>`
            ).join(', ');
            return `<tr>
                <td><span style="color:${color};font-weight:bold">${f.severity}</span></td>
                <td>${f.title}</td>
                <td>${f.domain}</td>
                <td>${(f.confidence * 100).toFixed(0)}%</td>
                <td>${f.file || '-'}</td>
                <td>${citations || '-'}</td>
            </tr>`;
        }).join('');

        return `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: var(--vscode-font-family); color: var(--vscode-foreground); padding: 10px; }
        table { width: 100%; border-collapse: collapse; font-size: 12px; }
        th, td { padding: 6px 8px; text-align: left; border-bottom: 1px solid var(--vscode-widget-border); }
        th { font-weight: 600; opacity: 0.8; }
        a { color: var(--vscode-textLink-foreground); }
        .summary { margin-bottom: 16px; }
    </style>
</head>
<body>
    <div class="summary">
        <strong>${findings.length}</strong> findings |
        <span style="color:#ff4444">${findings.filter(f => f.severity === 'CRITICAL').length} critical</span> |
        <span style="color:#ff8800">${findings.filter(f => f.severity === 'HIGH').length} high</span>
    </div>
    <table>
        <thead><tr><th>Severity</th><th>Finding</th><th>Domain</th><th>Confidence</th><th>File</th><th>Citations</th></tr></thead>
        <tbody>${rows}</tbody>
    </table>
</body>
</html>`;
    }
}

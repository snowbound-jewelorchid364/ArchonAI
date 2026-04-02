import * as vscode from 'vscode';
import { ArchonClient } from './archon-client';
import { RunReviewCommand } from './commands/run-review';
import { SelectModeCommand } from './commands/select-mode';
import { AgentStatusProvider } from './providers/agent-status-provider';
import { FindingsProvider } from './providers/findings-provider';
import { HistoryProvider } from './providers/history-provider';
import { FindingsWebviewProvider } from './views/findings-webview';
import { configureApiKey, loadClientConfig } from './config';

let client: ArchonClient;

export async function activate(context: vscode.ExtensionContext) {
    const { apiUrl, apiKey } = await loadClientConfig(context);
    client = new ArchonClient(apiUrl, apiKey);

    const agentStatusProvider = new AgentStatusProvider(client);
    const findingsProvider = new FindingsProvider(client);
    const historyProvider = new HistoryProvider(client);

    vscode.window.registerTreeDataProvider('archon-agents', agentStatusProvider);
    vscode.window.registerTreeDataProvider('archon-findings', findingsProvider);
    vscode.window.registerTreeDataProvider('archon-history', historyProvider);

    const findingsWebview = new FindingsWebviewProvider(context.extensionUri, client);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('archon-findings-detail', findingsWebview)
    );

    const runReview = new RunReviewCommand(client, agentStatusProvider, findingsProvider, context);
    const selectMode = new SelectModeCommand();

    context.subscriptions.push(
        vscode.commands.registerCommand('archon.runReview', () => runReview.execute()),
        vscode.commands.registerCommand('archon.runDesign', () => runReview.execute('design')),
        vscode.commands.registerCommand('archon.selectMode', () => selectMode.execute()),
        vscode.commands.registerCommand('archon.showFindings', () => findingsProvider.refresh()),
        vscode.commands.registerCommand('archon.cancelReview', () => runReview.cancel()),
        vscode.commands.registerCommand('archon.openSettings', () => {
            vscode.commands.executeCommand('workbench.action.openSettings', 'archon');
        }),
        vscode.commands.registerCommand('archon.configure', () => configureApiKey(context))
    );

    const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusBar.text = 'ARCHON';
    statusBar.command = 'archon.runReview';
    statusBar.tooltip = 'Run Architecture Review';
    statusBar.show();
    context.subscriptions.push(statusBar);

    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration(async e => {
            if (e.affectsConfiguration('archon')) {
                const nextConfig = await loadClientConfig(context);
                client.updateConfig(nextConfig.apiUrl, nextConfig.apiKey);
            }
        })
    );

    console.log('ARCHON extension activated');
}

export function deactivate() {
    client?.dispose();
}

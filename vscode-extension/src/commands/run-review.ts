import * as vscode from 'vscode';
import { ArchonClient } from '../archon-client';
import { AgentStatusProvider } from '../providers/agent-status-provider';
import { FindingsProvider } from '../providers/findings-provider';

const MODES = [
    { label: 'Review', value: 'review', description: 'Audit existing codebase' },
    { label: 'Design', value: 'design', description: 'New product from scratch' },
    { label: 'Migration Planner', value: 'migration_planner', description: 'Modernisation project' },
    { label: 'Compliance Auditor', value: 'compliance_auditor', description: 'SOC2/HIPAA/GDPR audit' },
    { label: 'Due Diligence', value: 'due_diligence', description: 'Fundraise / M&A' },
    { label: 'Incident Responder', value: 'incident_responder', description: 'P0/P1 outage' },
    { label: 'Cost Optimiser', value: 'cost_optimiser', description: 'Cloud bill spike' },
    { label: 'PR Reviewer', value: 'pr_reviewer', description: 'Pull request opened' },
    { label: 'Scaling Advisor', value: 'scaling_advisor', description: 'Traffic growing' },
    { label: 'Drift Monitor', value: 'drift_monitor', description: 'Weekly architecture check' },
    { label: 'Feature Feasibility', value: 'feature_feasibility', description: '"Can we build X?"' },
    { label: 'Vendor Evaluator', value: 'vendor_evaluator', description: 'Database / cloud choice' },
    { label: 'Onboarding Accelerator', value: 'onboarding_accelerator', description: 'New CTO / senior hire' },
    { label: 'Sunset Planner', value: 'sunset_planner', description: 'Decommission a service' },
];

export class RunReviewCommand {
    private currentJobId?: string;

    constructor(
        private client: ArchonClient,
        private agentStatus: AgentStatusProvider,
        private findings: FindingsProvider
    ) {}

    async execute(defaultMode?: string): Promise<void> {
        const config = vscode.workspace.getConfiguration('archon');
        if (!config.get<string>('apiKey')) {
            const openSettings = 'Open Settings';
            const result = await vscode.window.showErrorMessage(
                'ARCHON API key not set. Configure it in settings.',
                openSettings
            );
            if (result === openSettings) {
                vscode.commands.executeCommand('workbench.action.openSettings', 'archon.apiKey');
            }
            return;
        }

        // Get repo URL from workspace
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            vscode.window.showErrorMessage('No workspace folder open. Open a project first.');
            return;
        }

        // Try to get Git remote URL
        let repoUrl: string | undefined;
        try {
            const gitExtension = vscode.extensions.getExtension('vscode.git');
            if (gitExtension) {
                const git = gitExtension.exports.getAPI(1);
                const repo = git.repositories[0];
                if (repo) {
                    const remotes = repo.state.remotes;
                    const origin = remotes.find((r: any) => r.name === 'origin');
                    if (origin && origin.fetchUrl) {
                        repoUrl = origin.fetchUrl;
                    }
                }
            }
        } catch {
            // Git extension not available
        }

        if (!repoUrl) {
            repoUrl = await vscode.window.showInputBox({
                prompt: 'Enter GitHub repository URL',
                placeHolder: 'https://github.com/org/repo',
                validateInput: (value) => {
                    if (!value.includes('github.com')) {
                        return 'Only GitHub repositories are supported';
                    }
                    return null;
                }
            });
        }

        if (!repoUrl) { return; }

        // Select mode
        const mode = defaultMode || config.get<string>('defaultMode', 'review');
        const hitlMode = config.get<string>('hitlMode', 'balanced');

        await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: `ARCHON: Running ${mode} review...`,
                cancellable: true,
            },
            async (progress, token) => {
                try {
                    // Start review
                    progress.report({ message: 'Starting review...' });
                    this.currentJobId = await this.client.startReview(repoUrl!, mode, hitlMode);

                    // Stream progress
                    for await (const agentProgress of this.client.streamProgress(this.currentJobId)) {
                        if (token.isCancellationRequested) {
                            this.client.cancelStream();
                            vscode.window.showInformationMessage('ARCHON: Review cancelled.');
                            return;
                        }

                        const pct = agentProgress.status === 'complete' ? 100 : 50;
                        progress.report({
                            message: `${agentProgress.agent}: ${agentProgress.status}`,
                            increment: pct / 6,
                        });

                        this.agentStatus.updateAgent(agentProgress);
                    }

                    // Get results
                    progress.report({ message: 'Fetching results...' });
                    const review = await this.client.getReview(this.currentJobId);
                    this.findings.setFindings(review.findings);

                    // Show summary
                    const totalFindings = review.findings.length;
                    const critical = review.findings.filter(f => f.severity === 'CRITICAL').length;
                    const high = review.findings.filter(f => f.severity === 'HIGH').length;

                    const msg = `Review complete: ${totalFindings} findings (${critical} critical, ${high} high)`;
                    const action = await vscode.window.showInformationMessage(
                        msg,
                        'View Findings',
                        'Download Package'
                    );

                    if (action === 'View Findings') {
                        vscode.commands.executeCommand('archon.showFindings');
                    } else if (action === 'Download Package') {
                        await this.downloadPackage(this.currentJobId);
                    }
                } catch (error: any) {
                    vscode.window.showErrorMessage(`ARCHON review failed: ${error.message}`);
                }
            }
        );
    }

    async cancel(): Promise<void> {
        this.client.cancelStream();
        vscode.window.showInformationMessage('ARCHON: Review cancelled.');
    }

    private async downloadPackage(jobId: string): Promise<void> {
        const uri = await vscode.window.showSaveDialog({
            defaultUri: vscode.Uri.file(`archon-review-${jobId}.zip`),
            filters: { 'ZIP Archive': ['zip'] },
        });
        if (!uri) { return; }

        try {
            const buffer = await this.client.downloadPackage(jobId);
            await vscode.workspace.fs.writeFile(uri, buffer);
            vscode.window.showInformationMessage(`Package saved to ${uri.fsPath}`);
        } catch (error: any) {
            vscode.window.showErrorMessage(`Download failed: ${error.message}`);
        }
    }
}

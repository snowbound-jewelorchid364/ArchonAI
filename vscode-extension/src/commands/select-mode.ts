import * as vscode from 'vscode';

const MODES = [
    { label: '$(search) Review', value: 'review', description: 'Audit existing codebase' },
    { label: '$(lightbulb) Design', value: 'design', description: 'New product from scratch' },
    { label: '$(arrow-right) Migration Planner', value: 'migration_planner' },
    { label: '$(law) Compliance Auditor', value: 'compliance_auditor' },
    { label: '$(briefcase) Due Diligence', value: 'due_diligence' },
    { label: '$(flame) Incident Responder', value: 'incident_responder' },
    { label: '$(graph) Cost Optimiser', value: 'cost_optimiser' },
    { label: '$(git-pull-request) PR Reviewer', value: 'pr_reviewer' },
    { label: '$(rocket) Scaling Advisor', value: 'scaling_advisor' },
    { label: '$(clock) Drift Monitor', value: 'drift_monitor' },
    { label: '$(question) Feature Feasibility', value: 'feature_feasibility' },
    { label: '$(package) Vendor Evaluator', value: 'vendor_evaluator' },
    { label: '$(person) Onboarding Accelerator', value: 'onboarding_accelerator' },
    { label: '$(trash) Sunset Planner', value: 'sunset_planner' },
];

export class SelectModeCommand {
    async execute(): Promise<void> {
        const selected = await vscode.window.showQuickPick(
            MODES.map(m => ({
                label: m.label,
                description: m.description || '',
                detail: `Mode: ${m.value}`,
                value: m.value,
            })),
            {
                placeHolder: 'Select ARCHON review mode',
                title: 'ARCHON — Select Mode',
            }
        );

        if (selected) {
            const config = vscode.workspace.getConfiguration('archon');
            await config.update('defaultMode', (selected as any).value, vscode.ConfigurationTarget.Workspace);
            vscode.window.showInformationMessage(`ARCHON mode set to: ${selected.label}`);
        }
    }
}

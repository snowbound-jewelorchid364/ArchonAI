import * as vscode from 'vscode';

export const API_KEY_SECRET = 'archon.apiKey';

export function getApiUrl(configuration: Pick<vscode.WorkspaceConfiguration, 'get'> = vscode.workspace.getConfiguration('archon')): string {
    return configuration.get<string>('apiUrl', 'https://api.archon.dev') ?? 'https://api.archon.dev';
}

export async function getApiKey(context: Pick<vscode.ExtensionContext, 'secrets'>): Promise<string> {
    return (await context.secrets.get(API_KEY_SECRET)) ?? '';
}

export async function loadClientConfig(
    context: Pick<vscode.ExtensionContext, 'secrets'>,
    configuration: Pick<vscode.WorkspaceConfiguration, 'get'> = vscode.workspace.getConfiguration('archon')
): Promise<{ apiUrl: string; apiKey: string }> {
    return {
        apiUrl: getApiUrl(configuration),
        apiKey: await getApiKey(context),
    };
}

export async function configureApiKey(
    context: Pick<vscode.ExtensionContext, 'secrets'>,
    inputBox: typeof vscode.window.showInputBox = vscode.window.showInputBox,
    showInfo: typeof vscode.window.showInformationMessage = vscode.window.showInformationMessage,
    showWarning: typeof vscode.window.showWarningMessage = vscode.window.showWarningMessage,
): Promise<void> {
    const apiKey = await inputBox({
        prompt: 'Enter your ARCHON API key',
        password: true,
        ignoreFocusOut: true,
    });

    if (!apiKey) {
        await showWarning('ARCHON API key not set — reviews will fail');
        return;
    }

    await context.secrets.store(API_KEY_SECRET, apiKey);
    await showInfo('ARCHON API key saved securely');
}

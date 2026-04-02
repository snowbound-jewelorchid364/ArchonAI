import assert from 'node:assert/strict';
import test from 'node:test';

import { API_KEY_SECRET, configureApiKey, loadClientConfig } from '../config';


test('test_configure_stores_key', async () => {
    const calls: Array<{ key: string; value: string }> = [];
    const context = {
        secrets: {
            get: async () => undefined,
            store: async (key: string, value: string) => {
                calls.push({ key, value });
            },
        },
    } as any;

    await configureApiKey(
        context,
        async () => 'secret-key',
        async () => undefined,
        async () => undefined,
    );

    assert.deepEqual(calls, [{ key: API_KEY_SECRET, value: 'secret-key' }]);
});


test('test_configure_cancel_shows_warning', async () => {
    let warned = '';
    const context = {
        secrets: {
            get: async () => undefined,
            store: async () => undefined,
        },
    } as any;

    await configureApiKey(
        context,
        async () => undefined,
        async () => undefined,
        async (message: string) => {
            warned = message;
            return undefined;
        },
    );

    assert.equal(warned, 'ARCHON API key not set — reviews will fail');
});


test('test_review_uses_secret_not_config', async () => {
    const requestedKeys: string[] = [];
    const configuration = {
        get<T>(key: string, defaultValue?: T): T {
            requestedKeys.push(key);
            return (defaultValue ?? 'https://api.archon.dev') as T;
        },
    };
    const context = {
        secrets: {
            get: async () => 'secret-from-storage',
        },
    } as any;

    const config = await loadClientConfig(context, configuration as any);

    assert.equal(config.apiKey, 'secret-from-storage');
    assert.equal(config.apiUrl, 'https://api.archon.dev');
    assert.deepEqual(requestedKeys, ['apiUrl']);
});

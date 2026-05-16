/**
 * Ghi environment.prod.ts + app-config.json lúc build (Vercel / CI).
 * Trên Vercel: mặc định apiBaseUrl=/api (proxy qua api/[...path].ts → ngrok, không CORS).
 * Local/override: API_BASE_URL=https://....ngrok-free.dev/api
 */
import { writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const defaultBase = process.env.VERCEL ? '/api' : 'https://pushup-wrench-ignore.ngrok-free.dev/api';
const raw = (process.env.API_BASE_URL || defaultBase).trim();
const apiBaseUrl = raw.replace(/\/$/, '');

const envTs = `/** Generated at build by scripts/write-env-prod.mjs — do not edit by hand. */
export const environment = {
  production: true,
  apiBaseUrl: '${apiBaseUrl}',
};
`;

writeFileSync(join(root, 'src/environments/environment.prod.ts'), envTs, 'utf8');
writeFileSync(
  join(root, 'src/assets/app-config.json'),
  JSON.stringify({ apiBaseUrl }, null, 2) + '\n',
  'utf8',
);
console.log('[write-env-prod] apiBaseUrl =', apiBaseUrl, process.env.VERCEL ? '(VERCEL proxy)' : '');

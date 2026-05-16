/**
 * Ghi environment.prod.ts lúc build (Vercel / CI).
 * Set biến API_BASE_URL trên Vercel → Settings → Environment Variables.
 */
import { writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const raw = (process.env.API_BASE_URL || 'https://pushup-wrench-ignore.ngrok-free.dev/api').trim();
const apiBaseUrl = raw.replace(/\/$/, '');

const content = `/** Generated at build by scripts/write-env-prod.mjs — do not edit by hand. */
export const environment = {
  production: true,
  apiBaseUrl: '${apiBaseUrl}',
};
`;

writeFileSync(join(root, 'src/environments/environment.prod.ts'), content, 'utf8');
console.log('[write-env-prod] apiBaseUrl =', apiBaseUrl);

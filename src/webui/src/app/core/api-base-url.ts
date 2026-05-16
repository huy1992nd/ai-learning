declare global {
  interface Window {
    __MEDASSIST_API_BASE__?: string;
  }
}

/** BE tunnel mặc định — đổi khi ngrok URL đổi (và trong `index.html`). */
export const DEFAULT_NGROK_API_BASE = 'https://pushup-wrench-ignore.ngrok-free.dev/api';

function fromWindow(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }
  const w = window.__MEDASSIST_API_BASE__?.trim();
  return w ? w.replace(/\/$/, '') : null;
}

/** Ưu tiên `window.__MEDASSIST_API_BASE__`; `/api` = proxy Vercel (cùng origin, không CORS). */
export function resolveApiBaseUrl(raw: string): string {
  const win = fromWindow();
  if (win) {
    return win;
  }
  const trimmed = raw.trim().replace(/\/$/, '');
  if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
    return trimmed;
  }
  if (trimmed.startsWith('/')) {
    return trimmed;
  }
  return DEFAULT_NGROK_API_BASE.replace(/\/$/, '');
}

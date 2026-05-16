/** BE tunnel mặc định — đổi khi ngrok URL đổi. */
export const DEFAULT_NGROK_API_BASE = 'https://pushup-wrench-ignore.ngrok-free.dev/api';

/** `/api` hoặc path tương đối → dùng ngrok (tránh vercel.app/api + 502). */
export function resolveApiBaseUrl(raw: string): string {
  const trimmed = raw.trim().replace(/\/$/, '');
  if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
    return trimmed;
  }
  return DEFAULT_NGROK_API_BASE.replace(/\/$/, '');
}

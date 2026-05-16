/** ngrok free tier: tránh trang cảnh báo HTML thay cho JSON/SSE. */
export const ngrokSkipHeader: Record<string, string> = {
  'ngrok-skip-browser-warning': 'true',
};

export function withNgrokHeaders(headers?: Record<string, string>): Record<string, string> {
  return { ...ngrokSkipHeader, ...headers };
}

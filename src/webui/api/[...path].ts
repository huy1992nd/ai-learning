/**
 * Vercel serverless proxy: /api/* → ngrok BE với header bỏ trang cảnh báo ngrok.
 * Rewrite trực tiếp tới ngrok trong vercel.json không gửi header này → HTML thay vì JSON.
 */
const NGROK_ORIGIN =
  process.env.NGROK_API_ORIGIN?.replace(/\/$/, '') ||
  'https://pushup-wrench-ignore.ngrok-free.dev';

const SKIP_REQUEST_HEADERS = new Set([
  'host',
  'connection',
  'content-length',
  'transfer-encoding',
]);

export const config = {
  maxDuration: 120,
};

export default async function handler(req: Request): Promise<Response> {
  const incoming = new URL(req.url);
  const target = `${NGROK_ORIGIN}${incoming.pathname}${incoming.search}`;

  const headers = new Headers();
  req.headers.forEach((value, key) => {
    if (!SKIP_REQUEST_HEADERS.has(key.toLowerCase())) {
      headers.set(key, value);
    }
  });
  headers.set('ngrok-skip-browser-warning', 'true');

  const init: RequestInit & { duplex?: 'half' } = {
    method: req.method,
    headers,
    redirect: 'manual',
  };

  if (req.method !== 'GET' && req.method !== 'HEAD') {
    init.body = req.body;
    init.duplex = 'half';
  }

  const upstream = await fetch(target, init);

  const outHeaders = new Headers(upstream.headers);
  outHeaders.delete('content-encoding');

  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: outHeaders,
  });
}

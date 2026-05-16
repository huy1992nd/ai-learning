/** Production (Vercel): gọi thẳng BE qua ngrok — tránh rewrite Vercel → 502 DNS_HOSTNAME_EMPTY. */
export const environment = {
  production: true,
  apiBaseUrl: 'https://pushup-wrench-ignore.ngrok-free.dev/api',
};

/** Dev: call API directly so SSE streams are not buffered by `ng serve` proxy. */
export const environment = {
  production: false,
  apiBaseUrl: 'http://localhost:8000/api',
};

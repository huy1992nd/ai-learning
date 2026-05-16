import { HttpInterceptorFn } from '@angular/common/http';

import { ngrokSkipHeader } from '../api-http-headers';

/** Gắn header khi gọi BE qua tunnel ngrok (admin login, catalog, …). */
export const ngrokInterceptor: HttpInterceptorFn = (req, next) => {
  if (req.url.includes('ngrok-free.dev')) {
    return next(req.clone({ setHeaders: ngrokSkipHeader }));
  }
  return next(req);
};

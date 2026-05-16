import { HttpInterceptorFn } from '@angular/common/http';

import { ngrokSkipHeader } from '../api-http-headers';

/** Gắn header ngrok cho mọi request tới tunnel (login POST, admin JWT, …). */
export const ngrokInterceptor: HttpInterceptorFn = (req, next) => {
  if (req.url.includes('ngrok-free.dev')) {
    return next(req.clone({ setHeaders: ngrokSkipHeader }));
  }
  return next(req);
};

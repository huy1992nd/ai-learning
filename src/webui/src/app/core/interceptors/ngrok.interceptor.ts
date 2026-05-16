import { HttpInterceptorFn } from '@angular/common/http';

import { ngrokSkipHeader } from '../api-http-headers';

/**
 * Header `ngrok-skip-browser-warning` trên GET khiến trình duyệt gửi preflight OPTIONS;
 * ngrok free đôi khi trả HTML cho OPTIONS (không có header đó) → lỗi CORS.
 * Chỉ gắn header cho POST/PUT/PATCH/DELETE hoặc request có Authorization.
 */
export const ngrokInterceptor: HttpInterceptorFn = (req, next) => {
  if (!req.url.includes('ngrok-free.dev')) {
    return next(req);
  }
  const needsHeader =
    req.method !== 'GET' ||
    req.headers.has('Authorization') ||
    req.headers.has('authorization');
  if (!needsHeader) {
    return next(req);
  }
  return next(req.clone({ setHeaders: ngrokSkipHeader }));
};

import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';

import { AdminAuthService } from '../services/admin-auth.service';

/**
 * Attach JWT for admin and doctor-portal calls only.
 * Must not match public catalog `GET /api/doctors/...` (plural "doctors").
 */
function shouldAttachAuthHeader(url: string): boolean {
  const u = (url.split('?')[0] ?? '').toLowerCase();
  // /api/admin/...  or  /api/admin
  if (/\/api\/admin(\/|$)/.test(u)) {
    return true;
  }
  // /api/doctor/...  (singular) — e.g. doctor schedule; not /api/doctors/...
  if (/\/api\/doctor(\/|$)/.test(u) && !/\/api\/doctors\//.test(u)) {
    return true;
  }
  return false;
}

export const adminAuthInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AdminAuthService);
  const token = auth.getToken();
  if (token && shouldAttachAuthHeader(req.url)) {
    return next(
      req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }),
    );
  }
  return next(req);
};

import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { AdminAuthService } from '../services/admin-auth.service';

export const adminAuthGuard: CanActivateFn = () => {
  const auth = inject(AdminAuthService);
  const router = inject(Router);
  if (auth.isAuthenticatedAsAdmin()) {
    return true;
  }
  return router.createUrlTree(['/admin/login']);
};

export const adminGuestGuard: CanActivateFn = () => {
  const auth = inject(AdminAuthService);
  const router = inject(Router);
  if (auth.isAuthenticatedAsAdmin()) {
    return router.createUrlTree(['/admin']);
  }
  return true;
};

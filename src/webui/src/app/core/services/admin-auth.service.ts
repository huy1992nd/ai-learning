import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';

import { LoginTokenResponse } from '../models/admin.models';
import { ApiBaseUrlService } from './api-base-url.service';

const STORAGE_TOKEN = 'medassist_admin_token';
const STORAGE_ROLE = 'medassist_admin_role';
const STORAGE_SUB = 'medassist_admin_sub';

@Injectable({ providedIn: 'root' })
export class AdminAuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly apiBase = inject(ApiBaseUrlService);

  login(email: string, password: string): Observable<LoginTokenResponse> {
    return this.http
      .post<LoginTokenResponse>(`${this.apiBase.base}/auth/login`, { email, password })
      .pipe(
        tap((res) => {
          localStorage.setItem(STORAGE_TOKEN, res.access_token);
          localStorage.setItem(STORAGE_ROLE, res.role);
        }),
      );
  }

  setSubFromEmail(email: string): void {
    localStorage.setItem(STORAGE_SUB, email);
  }

  clearSession(): void {
    localStorage.removeItem(STORAGE_TOKEN);
    localStorage.removeItem(STORAGE_ROLE);
    localStorage.removeItem(STORAGE_SUB);
  }

  logout(): void {
    this.clearSession();
    void this.router.navigate(['/admin/login']);
  }

  getToken(): string | null {
    return localStorage.getItem(STORAGE_TOKEN);
  }

  getRole(): string | null {
    return localStorage.getItem(STORAGE_ROLE);
  }

  getDisplayName(): string {
    return localStorage.getItem(STORAGE_SUB) ?? '';
  }

  isAuthenticatedAsAdmin(): boolean {
    const role = this.getRole();
    const token = this.getToken();
    return !!token && role?.toUpperCase() === 'ADMIN';
  }
}

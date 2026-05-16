import { Injectable, inject, signal } from '@angular/core';

import { withNgrokHeaders } from '../api-http-headers';
import { ApiBaseUrlService } from './api-base-url.service';

const STORAGE_KEY = 'chat_session_id';

function generateUuid(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID();
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

@Injectable({ providedIn: 'root' })
export class SessionService {
  private readonly apiBase = inject(ApiBaseUrlService);
  private readonly _sessionId = signal<string>(this.loadOrCreate());

  readonly sessionId = this._sessionId.asReadonly();

  async reset(): Promise<void> {
    const current = this._sessionId();
    try {
      await fetch(`${this.apiBase.base}/sessions/${current}`, {
        method: 'DELETE',
        headers: withNgrokHeaders(),
      });
    } catch {
      // Best-effort: even if the server call fails, still rotate locally.
    }
    const next = generateUuid();
    sessionStorage.setItem(STORAGE_KEY, next);
    this._sessionId.set(next);
  }

  private loadOrCreate(): string {
    if (typeof sessionStorage === 'undefined') {
      return generateUuid();
    }
    const existing = sessionStorage.getItem(STORAGE_KEY);
    if (existing) {
      return existing;
    }
    const next = generateUuid();
    sessionStorage.setItem(STORAGE_KEY, next);
    return next;
  }
}

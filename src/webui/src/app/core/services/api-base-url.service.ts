import { Injectable } from '@angular/core';

import { resolveApiBaseUrl } from '../api-base-url';
import { environment } from '../../../environments/environment';

/** URL gốc API (`…/api`). Luôn đọc qua getter — không cache `readonly` lúc inject. */
@Injectable({ providedIn: 'root' })
export class ApiBaseUrlService {
  private _base = resolveApiBaseUrl(environment.apiBaseUrl);

  get base(): string {
    return this._base;
  }

  setBaseUrl(url: string): void {
    const trimmed = url.trim().replace(/\/$/, '');
    if (trimmed) {
      this._base = resolveApiBaseUrl(trimmed);
    }
  }
}

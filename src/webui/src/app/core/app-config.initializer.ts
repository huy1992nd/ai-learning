import { provideAppInitializer } from '@angular/core';

import { environment } from '../../environments/environment';

export interface AppConfigFile {
  apiBaseUrl?: string;
}

/** Đọc `/assets/app-config.json` khi khởi động — ghi đè `environment.apiBaseUrl` (fix deploy Vercel còn bundle `/api`). */
export function provideAppConfigInitializer() {
  return provideAppInitializer(() => {
    return fetch('/assets/app-config.json', { cache: 'no-store' })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`app-config.json HTTP ${res.status}`);
        }
        return res.json() as Promise<AppConfigFile>;
      })
      .then((cfg) => {
        const url = (cfg.apiBaseUrl ?? '').trim().replace(/\/$/, '');
        if (url) {
          environment.apiBaseUrl = url;
        }
      })
      .catch((err) => {
        console.warn('[app-config] fallback to build-time apiBaseUrl:', environment.apiBaseUrl, err);
      });
  });
}

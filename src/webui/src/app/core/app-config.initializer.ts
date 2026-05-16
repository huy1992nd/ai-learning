import { inject, provideAppInitializer } from '@angular/core';

import { ApiBaseUrlService } from './services/api-base-url.service';

export interface AppConfigFile {
  apiBaseUrl?: string;
}

/** Đọc `/assets/app-config.json` trước khi app chạy — cập nhật `ApiBaseUrlService`. */
export function provideAppConfigInitializer() {
  return provideAppInitializer(() => {
    const apiBase = inject(ApiBaseUrlService);
    return fetch('/assets/app-config.json', { cache: 'no-store' })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`app-config.json HTTP ${res.status}`);
        }
        return res.json() as Promise<AppConfigFile>;
      })
      .then((cfg) => {
        if (cfg.apiBaseUrl?.trim()) {
          apiBase.setBaseUrl(cfg.apiBaseUrl);
        }
        console.info('[app-config] apiBaseUrl =', apiBase.base);
      })
      .catch((err) => {
        console.warn('[app-config] using default apiBaseUrl:', apiBase.base, err);
      });
  });
}

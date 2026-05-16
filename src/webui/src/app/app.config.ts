import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideTranslateLoader, provideTranslateService } from '@ngx-translate/core';

import { provideAppConfigInitializer } from './core/app-config.initializer';
import { routes } from './app.routes';
import { adminAuthInterceptor } from './core/interceptors/admin-auth.interceptor';
import { ngrokInterceptor } from './core/interceptors/ngrok.interceptor';
import { AppTranslateHttpLoader } from './core/i18n/translate-http.loader';
import { DEFAULT_LOCALE } from './core/i18n/translations';

export const appConfig: ApplicationConfig = {
  providers: [
    provideAppConfigInitializer(),
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideAnimationsAsync(),
    provideHttpClient(withInterceptors([ngrokInterceptor, adminAuthInterceptor])),
    provideTranslateService({
      loader: provideTranslateLoader(AppTranslateHttpLoader),
      fallbackLang: DEFAULT_LOCALE,
      lang: DEFAULT_LOCALE,
    }),
  ],
};

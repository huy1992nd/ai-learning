import { Injectable, effect, signal } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

import {
  DEFAULT_LOCALE,
  SupportedLocale,
  TranslationKey,
  normalizeLocale,
} from './translations';

const STORAGE_KEY = 'medassist_locale';

type Params = Record<string, string | number | boolean | null | undefined>;

@Injectable({ providedIn: 'root' })
export class I18nService {
  private readonly _locale = signal<SupportedLocale>(this.loadLocale());

  readonly locale = this._locale.asReadonly();

  constructor(private readonly translate: TranslateService) {
    this.translate.addLangs(['en', 'vi', 'ja']);
    this.translate.setFallbackLang(DEFAULT_LOCALE);
    this.translate.use(this._locale());

    effect(() => {
      const locale = this._locale();
      if (typeof document !== 'undefined') {
        document.documentElement.lang = locale;
      }
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(STORAGE_KEY, locale);
      }
      this.translate.use(locale);
    });
  }

  setLocale(locale: string): void {
    this._locale.set(normalizeLocale(locale));
  }

  t(key: TranslationKey, params?: Params): string {
    return this.translate.instant(key, params);
  }

  normalize(locale: string | null | undefined): SupportedLocale {
    return normalizeLocale(locale);
  }

  private loadLocale(): SupportedLocale {
    if (typeof localStorage !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        return normalizeLocale(stored);
      }
    }
    return DEFAULT_LOCALE;
  }
}

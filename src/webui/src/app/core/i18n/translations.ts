export const SUPPORTED_LOCALES = ['en', 'vi', 'ja'] as const;

export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];

export type TranslationKey = string;

export const DEFAULT_LOCALE: SupportedLocale = 'vi';

export function normalizeLocale(value: string | null | undefined): SupportedLocale {
  const raw = (value ?? '').trim().toLowerCase().replace('_', '-');
  const primary = raw.split('-', 1)[0];

  if (primary === 'jp' || primary === 'ja') {
    return 'ja';
  }
  if (primary === 'en') {
    return 'en';
  }
  if (primary === 'vi') {
    return 'vi';
  }
  return DEFAULT_LOCALE;
}

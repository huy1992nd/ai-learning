import type { KbCategory, KbEmbeddingStatus } from '../../../core/models/knowledge-base.models';

export const KB_CATEGORIES = [
  'INFECTIOUS_DISEASES',
  'RESPIRATORY',
  'CARDIOVASCULAR',
  'DIGESTIVE',
  'NEUROLOGICAL',
  'MUSCULOSKELETAL',
  'GENERAL_HEALTH',
  'OTHER',
] as const satisfies readonly KbCategory[];

export const KB_STATUSES = [
  'PENDING',
  'PROCESSING',
  'COMPLETED',
  'FAILED',
] as const satisfies readonly KbEmbeddingStatus[];

export const categoryI18nKey = (c: KbCategory) => `admin.kb.category.${c}`;
export const statusI18nKey = (s: KbEmbeddingStatus) => `admin.kb.status.${s}`;

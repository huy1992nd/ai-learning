export type KbCategory =
  | 'INFECTIOUS_DISEASES'
  | 'RESPIRATORY'
  | 'CARDIOVASCULAR'
  | 'DIGESTIVE'
  | 'NEUROLOGICAL'
  | 'MUSCULOSKELETAL'
  | 'GENERAL_HEALTH'
  | 'OTHER';

/** SRS document.status + chunk.embedding_status family */
export type KbEmbeddingStatus =
  | 'PENDING'
  | 'PROCESSING'
  | 'COMPLETED'
  | 'FAILED';

/** Mirrors FastAPI `GET /admin/knowledge-base/documents` item shape */
export interface KbDocument {
  id: number;
  title: string;
  category: KbCategory;
  original_filename: string;
  file_path: string | null;
  mime_type: string | null;
  status: KbEmbeddingStatus;
  total_chunks: number;
  metadata_json: string | null;
  processing_error: string | null;
  uploaded_by: string | null;
  created_at: string | null;
  updated_at: string | null;
  is_active: boolean;
  content_text?: string | null;
}

export interface KbListResponse {
  items: KbDocument[];
  total: number;
  page: number;
  page_size: number;
}

export interface KbUploadResponseBody {
  document: KbDocument;
}

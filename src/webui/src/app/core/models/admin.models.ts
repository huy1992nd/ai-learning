export interface DepartmentPublic {
  id: number;
  name: string;
  description: string | null;
  specialty: string | null;
  symptoms_keywords: string | null;
  common_diseases: string | null;
}

export type EmbeddingSyncStatus = 'ok' | 'failed';

export interface DepartmentMutationResponse {
  department: DepartmentPublic;
  embedding_status: EmbeddingSyncStatus;
  embedding_message?: string | null;
}

/** Payload for POST/PATCH admin department APIs */
export interface DepartmentWritePayload {
  name: string;
  description?: string | null;
  specialty?: string | null;
  symptoms_keywords?: string | null;
  common_diseases?: string | null;
}

export interface DoctorPublic {
  id: number;
  full_name: string;
  department_id: number;
  title: string | null;
  specialty: string | null;
  bio: string | null;
  photo_url: string | null;
  email: string;
  phone: string | null;
  is_active: boolean;
}

export interface AdminAppointmentRow {
  id: number;
  appointment_code: string;
  scheduled_at: string;
  severity: string | null;
  status: string | null;
  patient_name: string | null;
  patient_phone: string | null;
}

export interface LoginTokenResponse {
  access_token: string;
  token_type: string;
  role: string;
  expires_in_minutes: number;
}

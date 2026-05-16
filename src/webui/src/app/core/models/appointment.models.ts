// Shared TypeScript interfaces mirroring FastAPI BE Pydantic DTOs (app.models)
// app/models/session/patient_info_response.py → PatientInfoResponse
// app/models/appointment/appointment_create_request.py, appointment_public.py → AppointmentCreateRequest, AppointmentPublic

export interface PatientInfo {
  full_name?: string;
  date_of_birth?: string;
  gender?: string;
  phone?: string;
  email?: string;
  cccd?: string;
  bhyt?: string;
  address?: string;
  department_id?: number;
  department_name?: string;
  doctor_id?: number;
  doctor_name?: string;
  symptoms_summary?: string;
  severity?: string;
}

export interface PatientInfoResponse {
  session_id: string;
  patient_info: PatientInfo;
  flow_stage: string | null;
  selected_slot_start: string | null;
  registration_link_sent: boolean;
}

export interface AppointmentCreateRequest {
  full_name: string;
  date_of_birth?: string;
  gender?: string;
  phone: string;
  email?: string;
  cccd?: string;
  bhyt?: string;
  address?: string;
  doctor_id: number;
  department_id: number;
  scheduled_at: string;
  symptoms?: string;
  severity: string;
  session_id: string;
}

export interface AppointmentPublic {
  id: number;
  appointment_code: string;
  scheduled_at: string;
  severity?: string;
  symptoms?: string;
  status?: string;
  patient_name?: string;
  patient_phone?: string;
  doctor_name?: string;
  department_name?: string;
}

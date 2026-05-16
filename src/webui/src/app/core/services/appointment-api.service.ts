import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { ApiBaseUrlService } from './api-base-url.service';
import {
  AppointmentCreateRequest,
  AppointmentPublic,
  PatientInfoResponse,
} from '../models/appointment.models';

export interface DoctorCatalog {
  id: number;
  full_name: string;
  department_id: number;
  email: string;
}

export interface BookableSlotItem {
  slot_index: number;
  label: string;
  storage_value: string;
}

@Injectable({ providedIn: 'root' })
export class AppointmentApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBase = inject(ApiBaseUrlService);

  getPatientInfo(sessionId: string): Observable<PatientInfoResponse> {
    return this.http.get<PatientInfoResponse>(
      `${this.apiBase.base}/sessions/${sessionId}/patient-info`,
    );
  }

  getDoctorsForDepartment(departmentId: number): Observable<DoctorCatalog[]> {
    return this.http.get<DoctorCatalog[]>(
      `${this.apiBase.base}/departments/${departmentId}/doctors`,
    );
  }

  getBookableSlots(doctorId: number): Observable<{
    doctor_id: number;
    slots: BookableSlotItem[];
  }> {
    return this.http.get<{
      doctor_id: number;
      slots: BookableSlotItem[];
    }>(`${this.apiBase.base}/bookable-slots`, {
      params: { doctor_id: String(doctorId) },
    });
  }

  createAppointment(
    payload: AppointmentCreateRequest,
  ): Observable<AppointmentPublic> {
    return this.http.post<AppointmentPublic>(
      `${this.apiBase.base}/appointments`,
      payload,
    );
  }
}

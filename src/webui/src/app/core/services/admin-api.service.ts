import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { ApiBaseUrlService } from './api-base-url.service';
import {
  AdminAppointmentRow,
  DepartmentMutationResponse,
  DepartmentPublic,
  DepartmentWritePayload,
  DoctorPublic,
} from '../models/admin.models';

/**
 * Admin portal HTTP client.
 */
@Injectable({ providedIn: 'root' })
export class AdminApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBase = inject(ApiBaseUrlService);

  getDepartments(): Observable<DepartmentPublic[]> {
    return this.http.get<DepartmentPublic[]>(`${this.apiBase.base}/departments`);
  }

  getDepartment(id: number): Observable<DepartmentPublic> {
    return this.http.get<DepartmentPublic>(
      `${this.apiBase.base}/departments/${id}`,
    );
  }

  getDepartmentDoctors(departmentId: number): Observable<DoctorPublic[]> {
    return this.http.get<DoctorPublic[]>(
      `${this.apiBase.base}/departments/${departmentId}/doctors`,
    );
  }

  getAllDoctors(): Observable<DoctorPublic[]> {
    return this.http.get<DoctorPublic[]>(`${this.apiBase.base}/doctors`);
  }

  getDoctor(doctorId: number): Observable<DoctorPublic> {
    return this.http.get<DoctorPublic>(`${this.apiBase.base}/doctors/${doctorId}`);
  }

  getDoctorAppointments(
    doctorId: number,
  ): Observable<AdminAppointmentRow[]> {
    return this.http.get<AdminAppointmentRow[]>(
      `${this.apiBase.base}/admin/doctors/${doctorId}/appointments`,
    );
  }

  createDepartment(
    body: DepartmentWritePayload,
  ): Observable<DepartmentMutationResponse> {
    return this.http.post<DepartmentMutationResponse>(
      `${this.apiBase.base}/admin/departments`,
      body,
    );
  }

  updateDepartment(
    id: number,
    body: Partial<DepartmentWritePayload>,
  ): Observable<DepartmentMutationResponse> {
    return this.http.patch<DepartmentMutationResponse>(
      `${this.apiBase.base}/admin/departments/${id}`,
      body,
    );
  }
}

import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
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
  private readonly base = environment.apiBaseUrl;

  getDepartments(): Observable<DepartmentPublic[]> {
    return this.http.get<DepartmentPublic[]>(`${this.base}/departments`);
  }

  getDepartment(id: number): Observable<DepartmentPublic> {
    return this.http.get<DepartmentPublic>(
      `${this.base}/departments/${id}`,
    );
  }

  getDepartmentDoctors(departmentId: number): Observable<DoctorPublic[]> {
    return this.http.get<DoctorPublic[]>(
      `${this.base}/departments/${departmentId}/doctors`,
    );
  }

  getAllDoctors(): Observable<DoctorPublic[]> {
    return this.http.get<DoctorPublic[]>(`${this.base}/doctors`);
  }

  getDoctor(doctorId: number): Observable<DoctorPublic> {
    return this.http.get<DoctorPublic>(`${this.base}/doctors/${doctorId}`);
  }

  getDoctorAppointments(
    doctorId: number,
  ): Observable<AdminAppointmentRow[]> {
    return this.http.get<AdminAppointmentRow[]>(
      `${this.base}/admin/doctors/${doctorId}/appointments`,
    );
  }

  createDepartment(
    body: DepartmentWritePayload,
  ): Observable<DepartmentMutationResponse> {
    return this.http.post<DepartmentMutationResponse>(
      `${this.base}/admin/departments`,
      body,
    );
  }

  updateDepartment(
    id: number,
    body: Partial<DepartmentWritePayload>,
  ): Observable<DepartmentMutationResponse> {
    return this.http.patch<DepartmentMutationResponse>(
      `${this.base}/admin/departments/${id}`,
      body,
    );
  }
}

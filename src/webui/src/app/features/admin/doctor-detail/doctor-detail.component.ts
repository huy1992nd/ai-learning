import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';

import {
  AdminAppointmentRow,
  DoctorPublic,
} from '../../../core/models/admin.models';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { I18nService } from '../../../core/i18n/i18n.service';
import { TranslatePipe } from '@ngx-translate/core';

@Component({
  selector: 'app-doctor-detail',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatTableModule,
    MatIconModule,
    MatProgressSpinnerModule,
    TranslatePipe,
  ],
  templateUrl: './doctor-detail.component.html',
  styleUrl: './doctor-detail.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DoctorDetailComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly i18n = inject(I18nService);

  readonly apptColumns = [
    'appointment_code',
    'scheduled_at',
    'patient_name',
    'status',
  ] as const;

  readonly doctor = signal<DoctorPublic | null>(null);
  readonly appointments = signal<AdminAppointmentRow[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly apptError = signal<string | null>(null);

  ngOnInit(): void {
    const doctorId = Number(this.route.snapshot.paramMap.get('doctorId'));
    if (!Number.isFinite(doctorId)) {
      this.error.set(this.i18n.t('admin.doctor.invalid'));
      this.loading.set(false);
      return;
    }

    forkJoin({
      doctor: this.api.getDoctor(doctorId).pipe(
        catchError(() => of(null as DoctorPublic | null)),
      ),
      appointments: this.api.getDoctorAppointments(doctorId).pipe(
        catchError(() => {
          this.apptError.set(this.i18n.t('admin.doctor.appointmentsLoadError'));
          return of([] as AdminAppointmentRow[]);
        }),
      ),
    }).subscribe({
      next: ({ doctor, appointments }) => {
        if (!doctor) {
          this.error.set(this.i18n.t('admin.doctor.notFound'));
        } else {
          this.doctor.set(doctor);
        }
        this.appointments.set(appointments);
        this.loading.set(false);
      },
      error: () => {
        this.error.set(this.i18n.t('admin.dataLoadError'));
        this.loading.set(false);
      },
    });
  }

  backToDepartment(): void {
    const deptId = this.route.snapshot.paramMap.get('departmentId');
    if (deptId) {
      void this.router.navigate(['/admin/department', deptId]);
      return;
    }
    const d = this.doctor()?.department_id;
    if (d != null) {
      void this.router.navigate(['/admin/department', d]);
      return;
    }
    void this.router.navigate(['/admin/doctors']);
  }
}

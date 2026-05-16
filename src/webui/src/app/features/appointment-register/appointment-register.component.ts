import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
  signal,
} from '@angular/core';
import {
  AbstractControl,
  FormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

import {
  AppointmentApiService,
  BookableSlotItem,
  DoctorCatalog,
} from '../../core/services/appointment-api.service';
import { AppointmentPublic } from '../../core/models/appointment.models';
import { I18nService } from '../../core/i18n/i18n.service';
import { TranslatePipe } from '@ngx-translate/core';

function notFutureDateValidator(
  control: AbstractControl,
): ValidationErrors | null {
  if (!control.value) return null;
  const date = parseDateFromControl(control.value);
  if (!date) return { invalidDate: true };
  if (date > new Date()) return { futureDate: true };
  return null;
}

function parseDateFromControl(value: unknown): Date | null {
  if (value instanceof Date && !isNaN(value.getTime())) {
    return value;
  }

  if (typeof value !== 'string' || !value.trim()) {
    return null;
  }

  // Supports API format dd/mm/yyyy and input[type=date] format yyyy-mm-dd.
  if (value.includes('/')) {
    const parts = value.split('/');
    if (parts.length !== 3) return null;
    const [d, m, y] = parts.map(Number);
    const date = new Date(y, m - 1, d);
    return isNaN(date.getTime()) ? null : date;
  }

  if (value.includes('-')) {
    const parts = value.split('-');
    if (parts.length !== 3) return null;
    const [y, m, d] = parts.map(Number);
    const date = new Date(y, m - 1, d);
    return isNaN(date.getTime()) ? null : date;
  }

  return null;
}

function formatDateForInput(dateValue?: string): string {
  if (!dateValue) return '';
  const parts = dateValue.split('/');
  if (parts.length !== 3) return '';
  const [d, m, y] = parts;
  return `${y.padStart(4, '0')}-${m.padStart(2, '0')}-${d.padStart(2, '0')}`;
}

function formatDateForApi(dateValue?: string): string | undefined {
  if (!dateValue) return undefined;
  const parts = dateValue.split('-');
  if (parts.length !== 3) return undefined;
  const [y, m, d] = parts;
  return `${d.padStart(2, '0')}/${m.padStart(2, '0')}/${y.padStart(4, '0')}`;
}

function mapGenderToForm(g?: string): string {
  if (!g) return '';
  const u = g.toUpperCase();
  if (u === 'MALE') return 'MALE';
  if (u === 'FEMALE') return 'FEMALE';
  return g;
}

function mapGenderToApi(g: string): string | undefined {
  if (!g) return undefined;
  if (g === 'MALE' || g === 'FEMALE' || g === 'OTHER') return g;
  return g;
}

type PageState = 'loading' | 'form' | 'submitting' | 'success' | 'error';

@Component({
  selector: 'app-appointment-register',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    MatSnackBarModule,
    TranslatePipe,
  ],
  templateUrl: './appointment-register.component.html',
  styleUrl: './appointment-register.component.scss',
})
export class AppointmentRegisterComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly api = inject(AppointmentApiService);
  private readonly fb = inject(FormBuilder);
  private readonly snackBar = inject(MatSnackBar);
  readonly i18n = inject(I18nService);

  sessionId = '';

  readonly pageState = signal<PageState>('loading');
  readonly errorMessage = signal<string>('');
  readonly confirmation = signal<AppointmentPublic | null>(null);

  readonly form = this.fb.nonNullable.group({
    full_name: ['', [Validators.required, Validators.minLength(3)]],
    date_of_birth: ['', [notFutureDateValidator]],
    gender: [''],
    phone: ['', [Validators.required, Validators.pattern(/^0\d{9}$/)]],
    email: ['', [Validators.email]],
    cccd: ['', [Validators.pattern(/^\d{12}$/)]],
    bhyt: [''],
    address: [''],
    doctor_id: [0, [Validators.required, Validators.min(1)]],
    scheduled_at: ['', [Validators.required]],
    // Read-only display fields
    department_name: [{ value: '', disabled: true }],
    symptoms_summary: [{ value: '', disabled: true }],
    severity: [{ value: '', disabled: true }],
  });

  readonly doctors = signal<DoctorCatalog[]>([]);
  readonly bookableSlots = signal<BookableSlotItem[]>([]);
  readonly loadingSlots = signal(false);

  private departmentId = 0;

  ngOnInit(): void {
    const q = this.route.snapshot.queryParamMap;
    this.sessionId =
      q.get('sessionId') ?? q.get('session_id') ?? '';
    if (!this.sessionId) {
      // Dev / direct URL: form still usable; fields stay empty; submit needs a session from chat.
      this.pageState.set('form');
      return;
    }

    this.api.getPatientInfo(this.sessionId).subscribe({
      next: (res) => {
        const p = res.patient_info;
        this.departmentId = p.department_id ?? 0;
        this.form.patchValue({
          full_name: p.full_name ?? '',
          date_of_birth: formatDateForInput(p.date_of_birth),
          gender: mapGenderToForm(p.gender),
          phone: p.phone ?? '',
          email: p.email ?? '',
          cccd: p.cccd ?? '',
          bhyt: p.bhyt ?? '',
          address: p.address ?? '',
          department_name: p.department_name ?? '',
          symptoms_summary: p.symptoms_summary ?? '',
          severity: p.severity ?? '',
          doctor_id: p.doctor_id && p.doctor_id > 0 ? p.doctor_id : 0,
          scheduled_at: res.selected_slot_start ?? '',
        });
        if (this.departmentId) {
          this.api.getDoctorsForDepartment(this.departmentId).subscribe({
            next: (docs) => {
              this.doctors.set(docs);
              const pre = p.doctor_id && docs.some((d) => d.id === p.doctor_id) ? p.doctor_id : 0;
              if (pre) {
                this.form.patchValue({ doctor_id: pre });
                this.loadSlots(pre);
              }
            },
            error: () => this.doctors.set([]),
          });
        }
        this.pageState.set('form');
      },
      error: (err: HttpErrorResponse) => {
        if (err.status === 404) {
          this.errorMessage.set(
            this.i18n.t('appointment.sessionExpired'),
          );
        } else {
          this.errorMessage.set(this.i18n.t('appointment.loadError'));
        }
        this.pageState.set('error');
      },
    });
  }

  onDoctorChange(id: number): void {
    this.form.patchValue({ scheduled_at: '' });
    this.bookableSlots.set([]);
    if (id > 0) {
      this.loadSlots(id);
    }
  }

  loadSlots(doctorId: number): void {
    this.loadingSlots.set(true);
    this.api.getBookableSlots(doctorId).subscribe({
      next: (r) => {
        this.bookableSlots.set(r.slots);
        this.loadingSlots.set(false);
      },
      error: () => {
        this.bookableSlots.set([]);
        this.loadingSlots.set(false);
      },
    });
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.pageState.set('submitting');
    const v = this.form.getRawValue();

    this.api
      .createAppointment({
        full_name: v.full_name,
        date_of_birth: formatDateForApi(v.date_of_birth),
        gender: mapGenderToApi(v.gender),
        phone: v.phone,
        email: v.email || undefined,
        cccd: v.cccd || undefined,
        bhyt: v.bhyt || undefined,
        address: v.address || undefined,
        doctor_id: v.doctor_id,
        department_id: this.departmentId,
        scheduled_at: v.scheduled_at,
        symptoms: v.symptoms_summary || undefined,
        severity: v.severity || 'MILD',
        session_id: this.sessionId,
      })
      .subscribe({
        next: (appt) => {
          this.confirmation.set(appt);
          this.pageState.set('success');
        },
        error: (err: HttpErrorResponse) => {
          const detail =
            (err.error as { detail?: string })?.detail ??
            this.i18n.t('appointment.submitError');
          this.snackBar.open(detail, this.i18n.t('common.ok'), { duration: 6000 });
          this.pageState.set('form');
        },
      });
  }

  severityClass(s: string): string {
    const map: Record<string, string> = {
      URGENT: 'urgent',
      MODERATE: 'moderate',
      MILD: 'mild',
    };
    return map[s] ?? 'mild';
  }

  closeTab(): void {
    window.close();
  }
}

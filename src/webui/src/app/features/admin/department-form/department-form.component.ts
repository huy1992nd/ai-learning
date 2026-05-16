import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  inject,
  signal,
} from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { TranslatePipe } from '@ngx-translate/core';

import { I18nService } from '../../../core/i18n/i18n.service';
import type { DepartmentWritePayload } from '../../../core/models/admin.models';
import { AdminApiService } from '../../../core/services/admin-api.service';

function emptyToNull(s: string | null | undefined): string | null {
  const t = (s ?? '').trim();
  return t === '' ? null : t;
}

@Component({
  selector: 'app-department-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    TranslatePipe,
  ],
  templateUrl: './department-form.component.html',
  styleUrl: './department-form.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DepartmentFormComponent implements OnInit {
  private readonly fb = inject(NonNullableFormBuilder);
  private readonly api = inject(AdminApiService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly i18n = inject(I18nService);
  private readonly snackBar = inject(MatSnackBar);

  readonly mode = signal<'create' | 'edit'>('create');
  readonly departmentId = signal<number | null>(null);
  readonly loading = signal(false);
  readonly loadError = signal<string | null>(null);
  readonly saving = signal(false);

  readonly form = this.fb.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    description: [''],
    specialty: [''],
    symptoms_keywords: [''],
    common_diseases: [''],
  });

  ngOnInit(): void {
    const mode = this.route.snapshot.data['departmentFormMode'] as
      | 'create'
      | 'edit'
      | undefined;
    this.mode.set(mode === 'edit' ? 'edit' : 'create');

    if (this.mode() === 'edit') {
      const id = Number(this.route.snapshot.paramMap.get('departmentId'));
      if (!Number.isFinite(id)) {
        this.loadError.set(this.i18n.t('admin.department.invalid'));
        return;
      }
      this.departmentId.set(id);
      this.loading.set(true);
      this.api.getDepartment(id).subscribe({
        next: (d) => {
          this.form.patchValue({
            name: d.name,
            description: d.description ?? '',
            specialty: d.specialty ?? '',
            symptoms_keywords: d.symptoms_keywords ?? '',
            common_diseases: d.common_diseases ?? '',
          });
          this.loading.set(false);
        },
        error: () => {
          this.loadError.set(this.i18n.t('admin.department.form.loadError'));
          this.loading.set(false);
        },
      });
    }
  }

  backLink(): string[] {
    if (this.mode() === 'edit' && this.departmentId() != null) {
      return ['/admin/department', String(this.departmentId())];
    }
    return ['/admin/department'];
  }

  submit(): void {
    this.form.markAllAsTouched();
    if (this.form.invalid || this.saving()) {
      return;
    }

    const v = this.form.getRawValue();
    const payload: DepartmentWritePayload = {
      name: v.name.trim(),
      description: emptyToNull(v.description),
      specialty: emptyToNull(v.specialty),
      symptoms_keywords: emptyToNull(v.symptoms_keywords),
      common_diseases: emptyToNull(v.common_diseases),
    };

    this.saving.set(true);

    if (this.mode() === 'create') {
      this.api.createDepartment(payload).subscribe({
        next: (res) => this.onSaved(res.embedding_status, res.embedding_message, res.department.id),
        error: (err) => this.onSaveError(err),
      });
      return;
    }

    const id = this.departmentId();
    if (id == null) {
      this.saving.set(false);
      return;
    }

    const patch: Partial<DepartmentWritePayload> = { ...payload };
    this.api.updateDepartment(id, patch).subscribe({
      next: (res) => this.onSaved(res.embedding_status, res.embedding_message, res.department.id),
      error: (err) => this.onSaveError(err),
    });
  }

  private onSaved(
    embeddingStatus: 'ok' | 'failed',
    embeddingMessage: string | null | undefined,
    deptId: number,
  ): void {
    this.saving.set(false);
    this.snackBar.open(this.i18n.t('admin.department.saveSuccess'), undefined, {
      duration: 3500,
    });
    if (embeddingStatus === 'failed') {
      const detail = (embeddingMessage ?? '').trim();
      const msg = detail
        ? `${this.i18n.t('admin.department.embeddingWarning')} (${detail})`
        : this.i18n.t('admin.department.embeddingWarning');
      this.snackBar.open(msg, undefined, { duration: 8000 });
    }
    void this.router.navigate(['/admin/department', deptId]);
  }

  private onSaveError(err: { status?: number }): void {
    this.saving.set(false);
    let msg = this.i18n.t('admin.department.form.genericError');
    if (err.status === 409) {
      msg = this.i18n.t('admin.department.form.conflictError');
    }
    this.snackBar.open(msg, undefined, { duration: 5000 });
  }
}

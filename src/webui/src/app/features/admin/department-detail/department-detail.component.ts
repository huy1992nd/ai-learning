import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';

import {
  DepartmentPublic,
  DoctorPublic,
} from '../../../core/models/admin.models';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { I18nService } from '../../../core/i18n/i18n.service';
import { TranslatePipe } from '@ngx-translate/core';

@Component({
  selector: 'app-department-detail',
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
  templateUrl: './department-detail.component.html',
  styleUrl: './department-detail.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DepartmentDetailComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly i18n = inject(I18nService);

  readonly displayedColumns = [
    'id',
    'full_name',
    'specialty',
    'email',
  ] as const;

  readonly department = signal<DepartmentPublic | null>(null);
  readonly doctors = signal<DoctorPublic[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('departmentId'));
    if (!Number.isFinite(id)) {
      this.error.set(this.i18n.t('admin.department.invalid'));
      this.loading.set(false);
      return;
    }

    this.api.getDepartment(id).subscribe({
      next: (dept) => {
        this.department.set(dept);
        this.api.getDepartmentDoctors(id).subscribe({
          next: (docs) => {
            this.doctors.set(docs);
            this.loading.set(false);
          },
          error: () => {
            this.error.set(this.i18n.t('admin.doctors.loadError'));
            this.loading.set(false);
          },
        });
      },
      error: () => {
        this.error.set(this.i18n.t('admin.department.notFound'));
        this.loading.set(false);
      },
    });
  }

  editDepartment(): void {
    const d = this.department();
    if (d) {
      void this.router.navigate(['/admin/department', d.id, 'edit']);
    }
  }

  back(): void {
    void this.router.navigate(['/admin/department']);
  }

  openDoctor(row: DoctorPublic): void {
    const deptId = this.department()?.id ?? row.department_id;
    void this.router.navigate([
      '/admin/department',
      deptId,
      'doctor',
      row.id,
    ]);
  }
}

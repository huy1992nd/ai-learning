import {
  ChangeDetectionStrategy,
  Component,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';

import { DoctorPublic } from '../../../core/models/admin.models';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { I18nService } from '../../../core/i18n/i18n.service';
import { TranslatePipe } from '@ngx-translate/core';

@Component({
  selector: 'app-doctor-list',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatTableModule,
    MatIconModule,
    MatProgressSpinnerModule,
    TranslatePipe,
  ],
  templateUrl: './doctor-list.component.html',
  styleUrl: './doctor-list.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DoctorListComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  private readonly router = inject(Router);
  private readonly i18n = inject(I18nService);

  readonly displayedColumns = [
    'id',
    'full_name',
    'department_id',
    'specialty',
    'email',
  ] as const;

  readonly rows = signal<DoctorPublic[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  ngOnInit(): void {
    this.api.getAllDoctors().subscribe({
      next: (data) => {
        this.rows.set(data);
        this.loading.set(false);
      },
      error: () => {
        this.error.set(this.i18n.t('admin.doctors.loadError'));
        this.loading.set(false);
      },
    });
  }

  openRow(row: DoctorPublic): void {
    void this.router.navigate([
      '/admin/department',
      row.department_id,
      'doctor',
      row.id,
    ]);
  }
}

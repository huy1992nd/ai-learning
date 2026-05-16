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
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';

import { DepartmentPublic } from '../../../core/models/admin.models';
import { AdminApiService } from '../../../core/services/admin-api.service';
import { I18nService } from '../../../core/i18n/i18n.service';
import { TranslatePipe } from '@ngx-translate/core';

@Component({
  selector: 'app-department-list',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatTableModule,
    MatProgressSpinnerModule,
    TranslatePipe,
  ],
  templateUrl: './department-list.component.html',
  styleUrl: './department-list.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DepartmentListComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  private readonly router = inject(Router);
  private readonly i18n = inject(I18nService);

  readonly displayedColumns = ['id', 'name', 'description', 'specialty'] as const;
  readonly rows = signal<DepartmentPublic[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  ngOnInit(): void {
    this.api.getDepartments().subscribe({
      next: (data) => {
        this.rows.set(data);
        this.loading.set(false);
      },
      error: () => {
        this.error.set(this.i18n.t('admin.departments.loadError'));
        this.loading.set(false);
      },
    });
  }

  openCreate(): void {
    void this.router.navigate(['/admin/department/new']);
  }

  openRow(row: DepartmentPublic): void {
    void this.router.navigate(['/admin/department', row.id]);
  }
}

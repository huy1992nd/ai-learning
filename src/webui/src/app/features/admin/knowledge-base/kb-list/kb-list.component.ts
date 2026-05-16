import {
  ChangeDetectionStrategy,
  Component,
  inject,
  signal,
  OnInit,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTableModule } from '@angular/material/table';
import { TranslatePipe } from '@ngx-translate/core';

import { AdminKbApiService } from '../../../../core/services/admin-kb-api.service';
import type { KbDocument } from '../../../../core/models/knowledge-base.models';
import {
  KbUploadDialogComponent,
  type KbUploadDialogResult,
} from '../kb-upload-dialog.component';

@Component({
  selector: 'app-kb-list',
  standalone: true,
  imports: [
    CommonModule,
    TranslatePipe,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatDialogModule,
    MatTableModule,
    MatProgressSpinnerModule,
    MatPaginatorModule,
  ],
  templateUrl: './kb-list.component.html',
  styleUrl: './kb-list.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class KbListComponent implements OnInit {
  private readonly api = inject(AdminKbApiService);
  private readonly dialog = inject(MatDialog);

  readonly displayedColumns = [
    'filename',
    'category',
    'status',
    'chunks',
    'uploadedAt',
  ] as const;

  readonly pageSizeOptions = [10, 20, 50] as const;

  readonly rows = signal<KbDocument[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  /** Total rows across all pages (from API `total`). */
  readonly total = signal(0);
  /** 0-based page index (API `page` is 1-based). */
  readonly pageIndex = signal(0);
  readonly pageSize = signal(20);

  private fetchInFlight = false;

  ngOnInit(): void {
    this.fetchList();
  }

  onPage(event: PageEvent): void {
    const revert = { pageIndex: this.pageIndex(), pageSize: this.pageSize() };
    this.pageIndex.set(event.pageIndex);
    this.pageSize.set(event.pageSize);
    this.fetchList(revert);
  }

  retry(): void {
    this.fetchList();
  }

  openUpload(): void {
    this.dialog
      .open(KbUploadDialogComponent, {
        width: 'min(560px, 92vw)',
        maxHeight: '90vh',
        autoFocus: 'first-tabbable',
        panelClass: 'kb-upload-panel',
        backdropClass: 'kb-upload-backdrop',
      })
      .afterClosed()
      .subscribe((result: KbUploadDialogResult | undefined) => {
        if (result && result.uploaded > 0) {
          this.pageIndex.set(0);
          this.fetchList();
        }
      });
  }

  private fetchList(revertOnError?: { pageIndex: number; pageSize: number }): void {
    if (this.fetchInFlight) return;
    this.fetchInFlight = true;
    this.loading.set(true);
    this.error.set(null);

    const page = this.pageIndex() + 1;
    const pageSize = this.pageSize();

    this.api.list({ page, pageSize }).subscribe({
      next: (res) => {
        this.rows.set(res.items);
        this.total.set(res.total);
        this.pageIndex.set(Math.max(0, res.page - 1));
        this.pageSize.set(res.page_size);
        this.fetchInFlight = false;
        this.loading.set(false);
      },
      error: () => {
        if (revertOnError) {
          this.pageIndex.set(revertOnError.pageIndex);
          this.pageSize.set(revertOnError.pageSize);
        }
        this.error.set('admin.kb.loadError');
        this.fetchInFlight = false;
        this.loading.set(false);
      },
    });
  }
}

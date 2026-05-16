import {
  ChangeDetectionStrategy,
  Component,
  inject,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpEventType } from '@angular/common/http';
import {
  MatDialogModule,
  MatDialogRef,
} from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSelectModule } from '@angular/material/select';
import { TranslatePipe } from '@ngx-translate/core';
import { Subject, takeUntil } from 'rxjs';

import {
  KB_CATEGORIES,
  categoryI18nKey,
} from './categories';
import type { KbCategory } from '../../../core/models/knowledge-base.models';
import { AdminKbApiService } from '../../../core/services/admin-kb-api.service';

export type UploadStatus =
  | 'queued'
  | 'uploading'
  | 'uploaded'
  | 'failed'
  | 'rejected';

export interface UploadItem {
  id: string;
  file: File;
  status: UploadStatus;
  progressPct?: number;
  errorKey?: string;
}

export interface KbUploadDialogResult {
  uploaded: number;
}

const MAX_FILE_BYTES = 10 * 1024 * 1024;
const MAX_BATCH = 10;
const ALLOWED_EXT = ['pdf', 'txt', 'md', 'docx', 'json'] as const;

@Component({
  selector: 'app-kb-upload-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatDialogModule,
    MatFormFieldModule,
    MatIconModule,
    MatProgressBarModule,
    MatSelectModule,
    TranslatePipe,
  ],
  templateUrl: './kb-upload-dialog.component.html',
  styleUrl: './kb-upload-dialog.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class KbUploadDialogComponent {
  protected readonly dialogRef = inject<
    MatDialogRef<KbUploadDialogComponent, KbUploadDialogResult>
  >(MatDialogRef);
  private readonly kbApi = inject(AdminKbApiService);
  private readonly cancel$ = new Subject<void>();

  readonly categories = KB_CATEGORIES;
  readonly categoryKey = categoryI18nKey;

  readonly category = signal<KbCategory | null>(null);
  readonly files = signal<UploadItem[]>([]);
  readonly submitting = signal(false);
  readonly batchDone = signal(false);

  readonly hasQueued = () => this.files().some((f) => f.status === 'queued');

  setCategory(value: KbCategory): void {
    this.category.set(value);
  }

  onFilesPicked(input: HTMLInputElement): void {
    const list = input.files;
    if (!list) return;
    this.acceptFiles(Array.from(list));
    input.value = '';
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    if (!event.dataTransfer) return;
    this.acceptFiles(Array.from(event.dataTransfer.files));
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
  }

  removeFile(id: string): void {
    this.files.update((prev) => prev.filter((f) => f.id !== id));
  }

  cancel(): void {
    if (this.submitting() && !this.batchDone()) {
      this.cancel$.next();
      return;
    }
    const uploaded = this.files().filter((f) => f.status === 'uploaded').length;
    this.dialogRef.close({ uploaded });
  }

  async submit(): Promise<void> {
    const category = this.category();
    if (!category || this.submitting()) return;

    this.submitting.set(true);
    this.batchDone.set(false);

    let cancelled = false;
    const cancelSub = this.cancel$.subscribe(() => { cancelled = true; });

    try {
      const queue = this.files().filter((f) => f.status === 'queued');
      for (const item of queue) {
        if (cancelled) break;
        await this.uploadOne(item, category);
      }
    } finally {
      cancelSub.unsubscribe();
      this.submitting.set(false);
      this.batchDone.set(true);
    }
  }

  private uploadOne(item: UploadItem, category: KbCategory): Promise<void> {
    return new Promise<void>((resolve) => {
      this.patchFile(item.id, { status: 'uploading', progressPct: 0 });

      const sub = this.kbApi
        .upload(item.file, category)
        .pipe(takeUntil(this.cancel$))
        .subscribe({
          next: (event) => {
            if (event.type === HttpEventType.UploadProgress && event.total) {
              const pct = Math.round((100 * event.loaded) / event.total);
              this.patchFile(item.id, { status: 'uploading', progressPct: pct });
            } else if (event.type === HttpEventType.Response) {
              const body = event.body as { document?: unknown } | null;
              const ok =
                event.ok &&
                body &&
                typeof body === 'object' &&
                body.document != null;
              if (ok) {
                this.patchFile(item.id, { status: 'uploaded', progressPct: 100 });
              } else {
                this.patchFile(item.id, {
                  status: 'failed',
                  errorKey: 'admin.kb.upload.failed',
                });
              }
            }
          },
          error: () => {
            this.patchFile(item.id, { status: 'failed', errorKey: 'admin.kb.upload.failed' });
            sub.unsubscribe();
            resolve();
          },
          complete: () => {
            const current = this.files().find((f) => f.id === item.id);
            if (current?.status !== 'uploaded') {
              this.patchFile(item.id, { status: 'failed', errorKey: 'admin.kb.upload.failed' });
            }
            resolve();
          },
        });
    });
  }

  private patchFile(id: string, patch: Partial<UploadItem>): void {
    this.files.update((prev) =>
      prev.map((f) => (f.id === id ? { ...f, ...patch } : f)),
    );
  }

  private acceptFiles(incoming: File[]): void {
    const current = this.files();
    const remainingSlots = Math.max(0, MAX_BATCH - current.length);

    const additions: UploadItem[] = [];
    for (let i = 0; i < incoming.length; i++) {
      const file = incoming[i];
      const id = `${Date.now()}-${i}-${file.name}`;

      if (i >= remainingSlots) {
        additions.push({ id, file, status: 'rejected', errorKey: 'admin.kb.upload.tooManyFiles' });
        continue;
      }

      const ext = file.name.split('.').pop()?.toLowerCase() ?? '';
      const isAllowed = (ALLOWED_EXT as readonly string[]).includes(ext);
      if (!isAllowed) {
        additions.push({ id, file, status: 'rejected', errorKey: 'admin.kb.upload.fileBadType' });
        continue;
      }
      if (file.size > MAX_FILE_BYTES) {
        additions.push({ id, file, status: 'rejected', errorKey: 'admin.kb.upload.fileTooLarge' });
        continue;
      }
      additions.push({ id, file, status: 'queued' });
    }
    this.files.update((prev) => [...prev, ...additions]);
  }
}

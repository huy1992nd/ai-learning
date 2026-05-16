import { Pipe, PipeTransform } from '@angular/core';

import type { KbEmbeddingStatus } from '../../../core/models/knowledge-base.models';

@Pipe({ name: 'kbStatusClass', standalone: true, pure: true })
export class KbStatusClassPipe implements PipeTransform {
  transform(status: KbEmbeddingStatus): string {
    switch (status) {
      case 'COMPLETED':
        return 'kb-chip kb-chip--completed';
      case 'PROCESSING':
        return 'kb-chip kb-chip--processing';
      case 'FAILED':
        return 'kb-chip kb-chip--failed';
      case 'PENDING':
      default:
        return 'kb-chip kb-chip--pending';
    }
  }
}

import { Injectable, inject } from '@angular/core';
import {
  HttpClient,
  HttpEvent,
  HttpParams,
  HttpRequest,
} from '@angular/common/http';
import { Observable } from 'rxjs';

import { ApiBaseUrlService } from './api-base-url.service';
import type {
  KbCategory,
  KbListResponse,
  KbUploadResponseBody,
} from '../models/knowledge-base.models';

export interface KbListParams {
  page: number;
  pageSize: number;
  q?: string | null;
  category?: KbCategory | null;
  status?: string | null;
}

@Injectable({ providedIn: 'root' })
export class AdminKbApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBase = inject(ApiBaseUrlService);

  list(params: KbListParams): Observable<KbListResponse> {
    let httpParams = new HttpParams()
      .set('page', String(params.page))
      .set('page_size', String(params.pageSize));
    if (params.q?.trim()) {
      httpParams = httpParams.set('q', params.q.trim());
    }
    if (params.category) {
      httpParams = httpParams.set('category', params.category);
    }
    if (params.status?.trim()) {
      httpParams = httpParams.set('status', params.status.trim());
    }
    return this.http.get<KbListResponse>(
      `${this.apiBase.base}/admin/knowledge-base/documents`,
      { params: httpParams },
    );
  }

  /**
   * SRS `POST /admin/knowledge-base/documents` — multipart; 202 + `{ document }`.
   */
  upload(
    file: File,
    category: KbCategory,
  ): Observable<HttpEvent<KbUploadResponseBody>> {
    const form = new FormData();
    form.append('file', file, file.name);
    form.append('category', category);

    const req = new HttpRequest(
      'POST',
      `${this.apiBase.base}/admin/knowledge-base/documents`,
      form,
      { reportProgress: true },
    );
    return this.http.request<KbUploadResponseBody>(req);
  }
}

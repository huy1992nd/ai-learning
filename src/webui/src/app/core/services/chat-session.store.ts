import { Injectable, computed, inject, signal, ApplicationRef } from '@angular/core';
import { Router } from '@angular/router';

import { withNgrokHeaders } from '../api-http-headers';
import { ApiBaseUrlService } from './api-base-url.service';
import { ChatMessage, ConversationStage, DetectedLanguage, MessageCard, Severity } from '../../features/chat/models/message.model';
import { SessionService } from './session.service';
import { I18nService } from '../i18n/i18n.service';

interface StreamTokenFrame {
  token: string;
}

interface StreamErrorFrame {
  message: string;
}

interface AppointmentSseData {
  appointmentSetupDone?: boolean;
  sessionId?: string;
}

@Injectable({ providedIn: 'root' })
export class ChatSessionStore {
  private readonly session = inject(SessionService);
  private readonly appRef = inject(ApplicationRef);
  private readonly router = inject(Router);
  private readonly i18n = inject(I18nService);
  private readonly apiBase = inject(ApiBaseUrlService);

  private readonly _messages = signal<ChatMessage[]>([]);
  private readonly _isStreaming = signal(false);
  private readonly _error = signal<string | null>(null);
  
  private readonly _stage = signal<ConversationStage>('topic_guard');
  private readonly _language = signal<DetectedLanguage | null>(null);
  private readonly _severity = signal<Severity | null>(null);
  private readonly _threadClosed = signal(false);
  private readonly _showRegistrationCta = signal(false);
  /** When true, user messages stream from KB RAG (`POST /api/knowledge/chat/stream`). */
  private readonly _knowledgeResearchMode = signal(false);

  readonly sessionId = this.session.sessionId;
  readonly messages = this._messages.asReadonly();
  readonly isStreaming = this._isStreaming.asReadonly();
  readonly error = this._error.asReadonly();
  readonly stage = this._stage.asReadonly();
  readonly language = this._language.asReadonly();
  readonly severity = this._severity.asReadonly();
  readonly threadClosed = this._threadClosed.asReadonly();
  readonly showRegistrationCta = this._showRegistrationCta.asReadonly();
  readonly knowledgeResearchMode = this._knowledgeResearchMode.asReadonly();

  readonly canSend = computed(
    () => !this._isStreaming() && !this._threadClosed(),
  );

  private abortController: AbortController | null = null;

  async sendMessage(text: string): Promise<void> {
    const trimmed = text.trim();
    if (!trimmed || this._isStreaming()) {
      return;
    }

    this._error.set(null);
    this._messages.update((prev) => [
      ...prev,
      { role: 'user', content: trimmed },
      { role: 'assistant', content: '' },
    ]);
    this._isStreaming.set(true);

    const controller = new AbortController();
    this.abortController = controller;

    const streamPath = this._knowledgeResearchMode()
      ? '/knowledge/chat/stream'
      : '/chat/stream';

    try {
      const response = await fetch(`${this.apiBase.base}${streamPath}`, {
        method: 'POST',
        headers: withNgrokHeaders({
          'Content-Type': 'application/json',
          Accept: 'text/event-stream',
        }),
        body: JSON.stringify({
          session_id: this.sessionId(),
          message: trimmed,
          ...(!this._knowledgeResearchMode() ? { language: this.i18n.locale() } : {}),
        }),
        signal: controller.signal,
      });

      if (!response.ok || !response.body) {
        let detail = '';
        try {
          detail = await response.text();
        } catch {
          /* ignore */
        }
        throw new Error(this.httpErrorToMessage(response.status, detail));
      }

      await this.consumeSse(response.body);
    } catch (err) {
      if ((err as Error).name === 'AbortError') {
        // User stopped — remove the empty placeholder assistant message
        this._messages.update((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === 'assistant' && last.content.trim() === '') {
            return prev.slice(0, -1);
          }
          return prev;
        });
        return;
      }
      const raw = err instanceof Error ? err.message : 'Unknown error';
      const friendly = this.networkErrorToMessage(raw);
      this._error.set(friendly);
      // Replace empty placeholder with the error message inline
      this._messages.update((prev) => {
        const last = prev[prev.length - 1];
        if (last?.role === 'assistant' && last.content.trim() === '') {
          return [...prev.slice(0, -1), { role: 'assistant', content: `⚠️ ${friendly}` }];
        }
        return [...prev, { role: 'assistant', content: `⚠️ ${friendly}` }];
      });
      this.appRef.tick();
    } finally {
      this._isStreaming.set(false);
      this.abortController = null;
    }
  }

  /**
   * Push a fixed assistant message into the conversation without calling the API.
   * Used by quick-prompt chips that produce a scripted greeting (e.g. UC-16
   * "Research a disease" entry point).
   */
  seedAssistantMessage(text: string): void {
    if (this._threadClosed() || this._isStreaming()) {
      return;
    }
    this._messages.update((prev) => [
      ...prev,
      { role: 'assistant', content: text, timestamp: Date.now() },
    ]);
  }

  /** Next user turns use RAG knowledge chat until the session is cleared or reset. */
  enterKnowledgeResearchMode(): void {
    if (this._threadClosed() || this._isStreaming()) {
      return;
    }
    this._knowledgeResearchMode.set(true);
  }

  stop(): void {
    this.abortController?.abort();
  }

  clear(): void {
    this.stop();
    this._messages.set([]);
    this._error.set(null);
    this._stage.set('topic_guard');
    this._language.set(null);
    this._severity.set(null);
    this._threadClosed.set(false);
    this._showRegistrationCta.set(false);
    this._knowledgeResearchMode.set(false);
  }

  async resetSession(): Promise<void> {
    this.clear();
    await this.session.reset();
  }

  openRegistrationForm(): void {
    const sid = this.sessionId().trim();
    if (!sid) {
      return;
    }
    this._showRegistrationCta.set(false);
    void this.router.navigate(['/appointment/register'], {
      queryParams: { sessionId: sid },
    });
  }

  private async consumeSse(stream: ReadableStream<Uint8Array>): Promise<void> {
    const reader = stream.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let lastYieldMs = performance.now();

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          buffer += decoder.decode();
          buffer = buffer.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
          while (buffer.includes('\n\n')) {
            const sepIndex = buffer.indexOf('\n\n');
            const rawEvent = buffer.slice(0, sepIndex);
            buffer = buffer.slice(sepIndex + 2);
            this.handleSseEvent(rawEvent);
          }
          if (buffer.trim()) {
            this.handleSseEvent(buffer);
          }
          break;
        }
        buffer += decoder.decode(value, { stream: true });
        buffer = buffer.replace(/\r\n/g, '\n').replace(/\r/g, '\n');

        let sepIndex: number;
        while ((sepIndex = buffer.indexOf('\n\n')) !== -1) {
          const rawEvent = buffer.slice(0, sepIndex);
          buffer = buffer.slice(sepIndex + 2);
          this.handleSseEvent(rawEvent);
        }

        // Khi dữ liệu đã được buffer sẵn trong ReadableStream, mỗi
        // `await reader.read()` resolve đồng bộ trong microtask, khiến
        // microtask queue không bao giờ rỗng trong suốt vòng lặp — browser
        // không có cửa sổ để paint (rAF callback không fire), UI chỉ render
        // một lần khi stream kết thúc. Yield sang macrotask queue định kỳ
        // ~16ms (~60fps) để browser kịp paint progressive token-by-token.
        const now = performance.now();
        if (now - lastYieldMs > 16) {
          await new Promise<void>((resolve) =>
            requestAnimationFrame(() => resolve()),
          );
          lastYieldMs = performance.now();
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  private handleSseEvent(rawEvent: string): void {
    const lines = rawEvent.split('\n');
    let eventName: string | null = null;
    const dataLines: string[] = [];

    for (const line of lines) {
      if (line.startsWith('event:')) {
        eventName = line.slice(6).trim();
      } else if (line.startsWith('data:')) {
        dataLines.push(line.slice(5).trimStart());
      }
    }

    if (dataLines.length === 0) {
      return;
    }
    const data = dataLines.join('\n');

    if (eventName === 'done') {
      return;
    }
    if (eventName === 'error') {
      let raw: string;
      try {
        const parsed = JSON.parse(data) as StreamErrorFrame;
        raw = parsed.message;
      } catch {
        raw = data;
      }
      const friendly = this.i18n.t('chat.error.server');
      this._error.set(friendly);
      this._messages.update((prev) => {
        const last = prev[prev.length - 1];
        if (last?.role === 'assistant' && last.content.trim() === '') {
          return [...prev.slice(0, -1), { role: 'assistant', content: `⚠️ ${friendly}` }];
        }
        return [...prev, { role: 'assistant', content: `⚠️ ${friendly}` }];
      });
      this.appRef.tick();
      return;
    }
    
    if (eventName === 'state') {
       this._stage.set(data as ConversationStage);
       return;
    }
    
    if (eventName === 'language') {
       try {
         const parsed = JSON.parse(data) as DetectedLanguage;
         this._language.set({ ...parsed, code: this.i18n.normalize(parsed.code) });
       } catch {
         // ignore
       }
       return;
    }
    
    if (eventName === 'severity') {
       this._severity.set(data as Severity);
       return;
    }
    
    if (eventName === 'card') {
       try {
         const parsedCard = JSON.parse(data) as MessageCard;
         this.appendCardToLastAssistant(parsedCard);
       } catch {
         // ignore
       }
       return;
    }

    if (eventName === 'thread_closed') {
      this._threadClosed.set(true);
      return;
    }

    if (eventName === 'appointment') {
      try {
        const parsed = JSON.parse(data) as AppointmentSseData;
        if (parsed.appointmentSetupDone) {
          this._showRegistrationCta.set(true);
        }
      } catch {
        // ignore
      }
      return;
    }

    try {
      const parsed = JSON.parse(data) as StreamTokenFrame;
      if (parsed.token) {
        this.appendTokenToLastAssistant(parsed.token);
      }
    } catch {
      this.appendTokenToLastAssistant(data);
    }
  }

  private appendTokenToLastAssistant(token: string): void {
    this._messages.update((prev) => {
      if (prev.length === 0) {
        return [{ role: 'assistant', content: token }];
      }
      const last = prev[prev.length - 1];
      if (last.role !== 'assistant') {
        return [...prev, { role: 'assistant', content: token }];
      }
      const updated: ChatMessage = { ...last, content: last.content + token };
      return [...prev.slice(0, -1), updated];
    });
    this.appRef.tick();
  }
  
  private appendCardToLastAssistant(card: MessageCard): void {
    this._messages.update((prev) => {
      if (prev.length === 0) {
        return [{ role: 'assistant', content: '', card }];
      }
      const last = prev[prev.length - 1];
      if (last.role !== 'assistant') {
        return [...prev, { role: 'assistant', content: '', card }];
      }
      const updated: ChatMessage = { ...last, card };
      return [...prev.slice(0, -1), updated];
    });
    this.appRef.tick();
  }

  private httpErrorToMessage(status: number, detail: string): string {
    if (status === 0 || status === 502 || status === 503 || status === 504) {
      return this.i18n.t('chat.error.unreachable');
    }
    if (status === 429) {
      return this.i18n.t('chat.error.busy');
    }
    if (status === 401 || status === 403) {
      return this.i18n.t('chat.error.session');
    }
    if (status >= 500) {
      return this.i18n.t('chat.error.server');
    }
    if (status >= 400) {
      return detail || this.i18n.t('chat.error.client');
    }
    return this.i18n.t('chat.error.generic');
  }

  private networkErrorToMessage(raw: string): string {
    const lower = raw.toLowerCase();
    if (lower.includes('failed to fetch') || lower.includes('networkerror') || lower.includes('load failed')) {
      return this.i18n.t('chat.error.unreachable');
    }
    if (lower.includes('timeout') || lower.includes('timed out')) {
      return this.i18n.t('chat.error.timeout');
    }
    if (lower.includes('abort')) {
      return this.i18n.t('chat.error.cancelled');
    }
    return this.i18n.t('chat.error.generic');
  }
}

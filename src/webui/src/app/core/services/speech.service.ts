import { Injectable, inject, signal } from '@angular/core';
import { Subject } from 'rxjs';

import { environment } from '../../../environments/environment';
import { I18nService } from '../i18n/i18n.service';

const MAX_BYTES = 25 * 1024 * 1024; // 25 MB — Whisper API limit

function preferredMimeType(): string {
  const candidates = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/ogg;codecs=opus',
    'audio/wav',
  ];
  return candidates.find((m) => MediaRecorder.isTypeSupported(m)) ?? '';
}

@Injectable({ providedIn: 'root' })
export class SpeechService {
  private readonly i18n = inject(I18nService);

  readonly isRecording = signal(false);
  readonly isTranscribing = signal(false);
  readonly error = signal<string | null>(null);
  /** True while a text-to-speech request is in flight. */
  readonly ttsLoading = signal(false);
  readonly ttsError = signal<string | null>(null);

  /** Emits transcribed text after each successful STT call. */
  readonly transcription$ = new Subject<string>();

  private recorder: MediaRecorder | null = null;
  private chunks: Blob[] = [];
  private stream: MediaStream | null = null;

  private ttsAudio: HTMLAudioElement | null = null;
  private ttsObjectUrl: string | null = null;

  /** First call starts recording; second call stops and uploads to Whisper. */
  toggleRecording(sessionId: string): void {
    if (this.isRecording()) {
      this.initiateStop(sessionId);
    } else {
      void this.startRecording(sessionId);
    }
  }

  private async startRecording(sessionId: string): Promise<void> {
    this.error.set(null);
    this.chunks = [];

    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      this.error.set(this.i18n.t('speech.error.micPermission'));
      return;
    }

    this.stream = stream;
    const mimeType = preferredMimeType();
    const options = mimeType ? { mimeType } : {};
    const recorder = new MediaRecorder(stream, options);
    this.recorder = recorder;

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) this.chunks.push(e.data);
    };

    recorder.onstop = () => {
      void this.assembleAndUpload(sessionId);
    };

    recorder.start();
    this.isRecording.set(true);
  }

  private initiateStop(sessionId: string): void {
    if (!this.recorder || this.recorder.state === 'inactive') {
      return;
    }
    this.isRecording.set(false);
    // onstop will fire → assembleAndUpload
    this.recorder.stop();
    this.stream?.getTracks().forEach((t) => t.stop());
    this.stream = null;
  }

  private async assembleAndUpload(sessionId: string): Promise<void> {
    const mimeType = this.recorder?.mimeType ?? 'audio/webm';
    this.recorder = null;

    if (this.chunks.length === 0) {
      this.error.set(this.i18n.t('speech.error.emptyAudio'));
      return;
    }

    const blob = new Blob(this.chunks, { type: mimeType });
    this.chunks = [];

    if (blob.size > MAX_BYTES) {
      this.error.set(this.i18n.t('speech.error.tooLarge'));
      return;
    }

    await this.uploadAudio(blob, mimeType, sessionId);
  }

  private async uploadAudio(
    blob: Blob,
    mimeType: string,
    sessionId: string,
  ): Promise<void> {
    this.isTranscribing.set(true);
    this.error.set(null);

    const ext = mimeType.includes('wav') ? 'wav' : 'webm';
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('language', this.i18n.locale());
    formData.append('file', blob, `audio.${ext}`);

    try {
      const res = await fetch(`${environment.apiBaseUrl}/audio/speech-to-text`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({})) as { detail?: string };
        if (res.status === 422) {
          this.error.set(
            body.detail ??
              this.i18n.t('speech.error.emptyAudio'),
          );
        } else {
          this.error.set(this.i18n.t('speech.error.stt'));
        }
        return;
      }

      const data = (await res.json()) as { text: string };
      if (!data.text?.trim()) {
        this.error.set(this.i18n.t('speech.error.emptyAudio'));
        return;
      }

      this.transcription$.next(data.text);
    } catch {
      this.error.set(this.i18n.t('speech.error.stt'));
    } finally {
      this.isTranscribing.set(false);
    }
  }

  /**
   * Stops any current TTS playback and releases the blob URL.
   */
  stopTts(): void {
    if (this.ttsAudio) {
      this.ttsAudio.pause();
      this.ttsAudio = null;
    }
    if (this.ttsObjectUrl) {
      URL.revokeObjectURL(this.ttsObjectUrl);
      this.ttsObjectUrl = null;
    }
  }

  /**
   * POSTs to `/api/audio/text-to-speech` and plays the returned audio (default mp3).
   */
  async playTextToSpeech(rawMarkdown: string): Promise<void> {
    const text = plainTextForTts(rawMarkdown);
    if (!text.length) {
      this.ttsError.set(this.i18n.t('speech.error.noTtsContent'));
      return;
    }

    this.stopTts();
    this.ttsError.set(null);
    this.ttsLoading.set(true);

    try {
      const res = await fetch(`${environment.apiBaseUrl}/audio/text-to-speech`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          voice: 'alloy',
          response_format: 'mp3',
        }),
      });

      if (!res.ok) {
        this.ttsError.set(this.i18n.t('speech.error.ttsPlayback'));
        return;
      }

      const blob = await res.blob();
      this.ttsObjectUrl = URL.createObjectURL(blob);
      const audio = new Audio(this.ttsObjectUrl);
      this.ttsAudio = audio;
      audio.onended = () => this.stopTts();
      audio.onerror = () => {
        this.ttsError.set(this.i18n.t('speech.error.ttsAudio'));
        this.stopTts();
      };
      await audio.play();
    } catch {
      this.ttsError.set(this.i18n.t('speech.error.ttsConnection'));
      this.stopTts();
    } finally {
      this.ttsLoading.set(false);
    }
  }
}

/**
 * Produces speakable plain text from assistant markdown (no thinking blocks, light markdown strip).
 */
function plainTextForTts(raw: string): string {
  let t = raw.replace(/\r\n?/g, '\n').trim();
  if (!t) {
    return '';
  }

  // Match the same <think> blocks as RichTextPipe
  t = t.replace(/<think\b[^>]*>[\s\S]*?<\/think\s*>/gi, ' ');
  t = t.replace(/<think\b[^>]*>[\s\S]*$/i, ' ');

  t = t.replace(/```[a-zA-Z0-9_-]*\n?([\s\S]*?)```/g, ' $1 ');
  t = t.replace(/`([^`\n]+)`/g, ' $1 ');

  t = t.replace(/\[([^\]]+)]\([^)]+\)/g, '$1');
  t = t.replace(/\*\*([^*]+)\*\*/g, '$1');
  t = t.replace(/__([^_]+)__/g, '$1');
  t = t.replace(/(^|[^*])\*([^*]+)\*(?!\*)/g, '$1$2');
  t = t.replace(/(^|[^_])_([^_]+)_(?!_)/g, '$1$2');

  t = t.replace(/^#{1,6}\s+/gm, '');
  t = t.replace(/^\s*>\s?/gm, '');
  t = t.replace(/^\s*[-*+]\s+/gm, '');
  t = t.replace(/^\s*\d+\.\s+/gm, '');

  t = t.replace(/\s+/g, ' ').trim();
  return t;
}

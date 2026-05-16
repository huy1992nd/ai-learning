import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  effect,
  inject,
  input,
  viewChild,
} from '@angular/core';

import { ChatMessage } from '../models/message.model';
import { RichTextPipe } from '../pipes/rich-text.pipe';
import { SpeechService } from '../../../core/services/speech.service';
import { I18nService } from '../../../core/i18n/i18n.service';
import { TranslatePipe } from '@ngx-translate/core';

import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

@Component({
  selector: 'app-message-list',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatSnackBarModule,
    RichTextPipe,
    TranslatePipe,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './message-list.component.html',
  styleUrl: './message-list.component.scss',
})
export class MessageListComponent implements AfterViewInit {
  readonly messages = input.required<ChatMessage[]>();
  readonly isStreaming = input<boolean>(false);
  readonly isThinking = input<boolean>(false);

  readonly speech = inject(SpeechService);
  readonly i18n = inject(I18nService);
  private readonly snackBar = inject(MatSnackBar);

  private readonly scrollContainer = viewChild<ElementRef<HTMLElement>>('scrollContainer');

  constructor() {
    effect(() => {
      this.messages();
      this.isThinking(); // also scroll when thinking indicator appears/disappears
      queueMicrotask(() => this.scrollToBottom());
    });
  }

  ngAfterViewInit(): void {
    this.scrollToBottom();
  }

  private scrollToBottom(): void {
    const el = this.scrollContainer()?.nativeElement;
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }

  /** Play TTS for a bot message (raw markdown in `content`). */
  speakBotMessage(
    content: string | undefined,
    isLast: boolean,
    streaming: boolean,
  ): void {
    if (streaming && isLast) {
      return;
    }
    const text = content?.trim() ?? '';
    if (!text) {
      return;
    }
    void this.speech.playTextToSpeech(text).then(() => {
      const err = this.speech.ttsError();
      if (err) {
        this.snackBar.open(err, this.i18n.t('common.close'), { duration: 5000 });
      }
    });
  }
}

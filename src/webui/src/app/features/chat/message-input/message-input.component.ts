import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  OnDestroy,
  effect,
  inject,
  input,
  output,
  signal,
  viewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Subscription } from 'rxjs';

import { DetectedLanguage } from '../models/message.model';
import { SpeechService } from '../../../core/services/speech.service';
import { I18nService } from '../../../core/i18n/i18n.service';
import { TranslatePipe } from '@ngx-translate/core';

@Component({
  selector: 'app-message-input',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatTooltipModule,
    TranslatePipe,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './message-input.component.html',
  styleUrl: './message-input.component.scss',
})
export class MessageInputComponent implements OnDestroy {
  readonly disabled = input<boolean>(false);
  readonly streaming = input<boolean>(false);
  readonly detectedLanguage = input<DetectedLanguage | null>(null);
  readonly sessionId = input<string>('');

  readonly send = output<string>();
  readonly stopClicked = output<void>();

  readonly draft = signal('');

  readonly i18n = inject(I18nService);
  readonly speech = inject(SpeechService);
  private readonly snackBar = inject(MatSnackBar);
  private readonly textarea = viewChild<ElementRef<HTMLTextAreaElement>>('textarea');
  private wasDisabled = false;
  private readonly transcriptionSub: Subscription;

  constructor() {
    // Refocus textarea after streaming ends
    effect(() => {
      const disabled = this.disabled();
      if (this.wasDisabled && !disabled) {
        setTimeout(() => this.textarea()?.nativeElement.focus(), 0);
      }
      this.wasDisabled = disabled;
    });

    // Fill draft when STT transcription arrives; user reviews then sends manually
    this.transcriptionSub = this.speech.transcription$.subscribe((text) => {
      this.draft.set(text);
      setTimeout(() => this.textarea()?.nativeElement.focus(), 0);
    });

    // Show snackbar on STT errors
    effect(() => {
      const msg = this.speech.error();
      if (msg) {
        this.snackBar.open(msg, 'OK', { duration: 5000 });
      }
    });
  }

  ngOnDestroy(): void {
    this.transcriptionSub.unsubscribe();
  }

  toggleRecording(): void {
    this.speech.toggleRecording(this.sessionId());
  }

  detectedLocaleCode(): string {
    return this.i18n.normalize(this.detectedLanguage()?.code).toUpperCase();
  }

  submit(): void {
    const value = this.draft().trim();
    if (!value || this.disabled()) {
      return;
    }
    this.send.emit(value);
    this.draft.set('');
    setTimeout(() => this.textarea()?.nativeElement.focus(), 0);
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.submit();
    }
  }
}

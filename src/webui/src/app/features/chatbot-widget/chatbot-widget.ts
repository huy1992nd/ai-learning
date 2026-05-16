import { ChangeDetectionStrategy, Component, ElementRef, computed, effect, inject, signal, viewChild } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

import { ChatSessionStore } from '../../core/services/chat-session.store';
import { I18nService } from '../../core/i18n/i18n.service';
import { TranslatePipe } from '@ngx-translate/core';
import { TranslationKey } from '../../core/i18n/translations';
import { ConversationStage } from '../chat/models/message.model';
import { MessageInputComponent } from '../chat/message-input/message-input.component';
import { MessageListComponent } from '../chat/message-list/message-list.component';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-chatbot-widget',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
    TranslatePipe,
    MessageListComponent,
    MessageInputComponent,
  ],
  templateUrl: './chatbot-widget.html',
  styleUrl: './chatbot-widget.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatbotWidget {
  readonly chat = inject(ChatSessionStore);
  readonly i18n = inject(I18nService);

  readonly isOpen = signal(false);
  readonly isFullscreen = signal(false);

  private readonly scrollContainer = viewChild<ElementRef<HTMLElement>>('scrollContainer');

  constructor() {
    // Auto-scroll to bottom whenever messages or thinking state changes
    effect(() => {
      this.chat.messages();
      this.isThinking();
      // Use a microtask to let the DOM update first
      queueMicrotask(() => this.scrollToBottom());
    });
  }

  /** True when streaming but the last assistant message is still empty (AI hasn't typed yet) */
  readonly isThinking = computed(() => {
    if (!this.chat.isStreaming()) return false;
    const msgs = this.chat.messages();
    if (msgs.length === 0) return true;
    const last = msgs[msgs.length - 1];
    return last.role === 'assistant' && last.content.trim() === '';
  });

  readonly stages: { id: ConversationStage; labelKey: TranslationKey; icon: string }[] = [
    { id: 'topic_guard', labelKey: 'chat.stage.topic', icon: 'shield' },
    { id: 'greeting', labelKey: 'chat.stage.language', icon: 'language' },
    { id: 'symptoms', labelKey: 'chat.stage.symptoms', icon: 'healing' },
    { id: 'diagnosis', labelKey: 'chat.stage.diagnosis', icon: 'medical_services' },
    { id: 'department', labelKey: 'chat.stage.department', icon: 'local_hospital' },
  ];

  toggleOpen() {
    this.isOpen.set(!this.isOpen());
    if (!this.isOpen()) {
      this.isFullscreen.set(false);
    }
  }

  toggleFullscreen() {
    this.isFullscreen.set(!this.isFullscreen());
  }

  shortSessionId(): string {
    const id = this.chat.sessionId();
    return id.length > 8 ? `${id.slice(0, 8)}…` : id;
  }

  isStageCompleted(stage: ConversationStage): boolean {
    const current = this.chat.stage();
    const order: ConversationStage[] = [
      'topic_guard',
      'greeting',
      'symptoms',
      'diagnosis',
      'department',
      'ended'
    ];
    return order.indexOf(current) > order.indexOf(stage);
  }

  onSend(text: string): void {
    void this.chat.sendMessage(text);
  }

  onResearchDisease(): void {
    this.chat.enterKnowledgeResearchMode();
    this.chat.seedAssistantMessage(this.i18n.t('chat.quick.research.greeting'));
  }

  newConversation(): void {
    void this.chat.resetSession();
  }

  /** Exit fullscreen first so the registration route is visible behind the panel. */
  openRegistrationFormFromWidget(): void {
    if (this.isFullscreen()) {
      this.isFullscreen.set(false);
      queueMicrotask(() => this.chat.openRegistrationForm());
      return;
    }
    this.chat.openRegistrationForm();
  }

  private scrollToBottom(): void {
    const el = this.scrollContainer()?.nativeElement;
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }
}

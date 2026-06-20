import { Component, computed, inject } from '@angular/core';
import { LlmService } from '../../services/llm.service';
import { EpisodeSummary, ErrorResponse, Role } from '../../models/summary.model';
import { ChatService } from '../../services/chat.service';
import { AppLoggerService } from '../../services/app-logger.service';
import { createMessageId } from '../../utils/message-id';

@Component({
  selector: 'app-chat-input',
  templateUrl: './chat-input.component.html',
  styleUrls: ['./chat-input.component.scss'],
})
export class ChatInputComponent {
  llmService = inject(LlmService);
  chatService = inject(ChatService);
  logger = inject(AppLoggerService);
  isBusy = this.chatService.isBusy;
  hasConversation = computed(() => this.chatService.messages().length > 1);

  send(textarea: HTMLTextAreaElement) {
    if (this.isBusy()) {
      this.logger.debug('Ignored summary submission while chat is busy');
      return;
    }

    const text = textarea.value.trim();
    if (!text) {
      this.logger.debug('Ignored empty summary submission');
      return;
    }

    this.logger.info('Summary submission started', {
      textLength: text.length
    });

    this.chatService.addMessage({ id: createMessageId(), role: Role.user, avatar: 'U', content: text });
    textarea.value = '';
    this.chatService.setBusy(true);

    this.llmService.getSummary(text).subscribe({
      next: (data: EpisodeSummary) => this.showSummary(data),
      error: (err) => {
        this.logger.error('Summary submission failed', {
          status: err?.status,
          statusText: err?.statusText
        }, err);
        const errorResponse: ErrorResponse | undefined = err?.error;
        const message = errorResponse?.message ?? 'Something went wrong. Please try again.';
        this.chatService.addMessage({
          id: createMessageId(),
          role: Role.assistant,
          avatar: 'A',
          content: message
        });
        this.chatService.setBusy(false);
      },
    });
  }

  private showSummary(summary: EpisodeSummary) {
    this.chatService.addMessage({
      id: createMessageId(),
      role: Role.assistant,
      avatar: 'A',
      content: '',
      summary
    });
  }

  handleKeydown(event: KeyboardEvent, textarea: HTMLTextAreaElement) {
    if (event.key !== 'Enter' || event.shiftKey) {
      return;
    }

    event.preventDefault();
    this.send(textarea);
  }
}

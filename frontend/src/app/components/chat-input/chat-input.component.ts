import { Component, computed, inject } from '@angular/core';
import { LlmService } from '../../services/llm.service';
import { Role, Summary } from '../../models/summary.model';
import { ChatService } from '../../services/chat.service';
import { AppLoggerService } from '../../services/app-logger.service';

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
  private static readonly REVEAL_INTERVAL_MS = 16;
  private static readonly CHARACTERS_PER_SECOND = 180;

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

    this.chatService.addMessage({ id: crypto.randomUUID(), role: Role.user, avatar: 'U', content: text });
    textarea.value = '';
    this.chatService.setBusy(true);

    this.llmService.getSummary(text).subscribe({
      next: (data: Summary) => this.typeOut(data),
      error: (err) => {
        this.logger.error('Summary submission failed', {
          status: err?.status,
          statusText: err?.statusText
        }, err);
        this.chatService.addMessage({
          id: crypto.randomUUID(),
          role: Role.assistant,
          avatar: 'A',
          content: 'Sorry, something went wrong while generating the summary. Please try again.'
        });
        this.chatService.setBusy(false);
      },
    });
  }

  // Reveal the response in small character batches for smoother motion.
  private typeOut(summary: Summary) {
    const id = crypto.randomUUID();
    const text = summary.content;
    const characters = Array.from(text);
    const charactersPerTick = Math.max(
      1,
      Math.round(
        (ChatInputComponent.CHARACTERS_PER_SECOND * ChatInputComponent.REVEAL_INTERVAL_MS) / 1000
      )
    );

    this.chatService.addMessage({ id, role: Role.assistant, avatar: 'A', content: '' });
    this.chatService.setBusy(false);

    let i = 0;
    const timer = setInterval(() => {
      const nextChunk = characters.slice(i, i + charactersPerTick).join('');
      i += nextChunk.length;
      this.chatService.appendToMessage(id, nextChunk);

      if (i >= characters.length) {
        clearInterval(timer);
      }
    }, ChatInputComponent.REVEAL_INTERVAL_MS);
  }

  handleKeydown(event: KeyboardEvent, textarea: HTMLTextAreaElement) {
    if (event.key !== 'Enter' || event.shiftKey) {
      return;
    }

    event.preventDefault();
    this.send(textarea);
  }
}

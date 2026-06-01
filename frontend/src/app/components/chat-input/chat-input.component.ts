import { Component, inject } from '@angular/core';
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
  private static readonly WORD_INTERVAL_MS = 45;

  send(textarea: HTMLTextAreaElement) {
    if (this.isBusy()) {
      this.logger.debug('Ignored summary submission while chat is busy');
      return;
    }

    const text = textarea.value;
    this.logger.info('Summary submission started', {
      textLength: text.length
    });

    this.chatService.addMessage({ id: crypto.randomUUID(), role: Role.user, avatar: 'U', content: text });
    textarea.value = '';
    this.chatService.setBusy(true);

    this.llmService.getSummary(text).subscribe({
      next: (data: Summary) => this.typeOut(data.content),
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

  // Reveal the response one word at a time at a fixed interval.
  private typeOut(text: string) {
    const id = crypto.randomUUID();
    const words = text.split(/(?<=\s)/); // keep each word's trailing whitespace

    this.logger.info('Starting summary reveal', {
      messageId: id,
      wordCount: words.length,
      characterCount: text.length
    });

    this.chatService.addMessage({ id, role: Role.assistant, avatar: 'A', content: '' });
    this.chatService.setBusy(false);

    let i = 0;
    const timer = setInterval(() => {
      this.chatService.appendToMessage(id, words[i++] ?? '');
      if (i >= words.length) {
        clearInterval(timer);
        this.logger.info('Summary reveal completed', {
          messageId: id,
          wordCount: words.length
        });
      }
    }, ChatInputComponent.WORD_INTERVAL_MS);
  }
}

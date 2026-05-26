import { Component, inject } from '@angular/core';
import { LlmService } from '../../services/llm.service';
import { Message, Role, Summary, SummaryRequest } from '../../models/summary.model';
import { ChatService } from '../../services/chat.service';
@Component({
  selector: 'app-chat-input',
  templateUrl: './chat-input.component.html',
  styleUrls: ['./chat-input.component.scss'],
})
export class ChatInputComponent {
  llmService = inject(LlmService);
  chatService = inject(ChatService);
  isBusy = this.chatService.isBusy;

  send(textarea: HTMLTextAreaElement) {
    if (this.isBusy()) return;

    const text = textarea.value;
    const message: Message = {
      id: crypto.randomUUID(),
      role: Role.user,
      avatar: 'U',
      content: text
    };

    this.chatService.addMessage(message);
    textarea.value = '';
    this.chatService.setBusy(true);

    this.llmService.getSummary(text).subscribe({
      next: (data: Summary) => {
        this.chatService.addMessage({
          id: crypto.randomUUID(),
          role: Role.assistant,
          avatar: 'A',
          content: data.content
        });
        this.chatService.setBusy(false);
      },
      error: (err) => {
        console.error('getSummary failed', err);
        this.chatService.addMessage({
          id: crypto.randomUUID(),
          role: Role.assistant,
          avatar: 'A',
          content: 'Sorry, something went wrong while generating the summary. Please try again.'
        });
        this.chatService.setBusy(false);
      }
    });
  }
}

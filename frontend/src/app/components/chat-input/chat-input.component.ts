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

  send(textarea: HTMLTextAreaElement) {
    let message: Message = {
      id: crypto.randomUUID(),
      role: Role.user,
      avatar: 'U',
      content: textarea.value
    };

    this.chatService.addMessage(message);
    //TODO: add error handling
    console.log(textarea.value);
    this.llmService.getSummary(textarea.value).subscribe((data: Summary) => {
      this.chatService.addMessage({
        id: crypto.randomUUID(),
        role: Role.assistant,
        avatar: 'A',
        content: data.content
      });
    });
    textarea.value = '';
  }
}

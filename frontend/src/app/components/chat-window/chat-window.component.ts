import { Component, inject } from '@angular/core';
import { MessageBubbleComponent } from '../message-bubble/message-bubble.component';
import { TypingIndicatorComponent } from '../typing-indicator/typing-indicator.component';
import { ChatService } from '../../services/chat.service';

@Component({
  imports: [MessageBubbleComponent, TypingIndicatorComponent],
  selector: 'app-chat-window',
  templateUrl: './chat-window.component.html',
  styleUrls: ['./chat-window.component.scss']
})
export class ChatWindowComponent {
  chatService = inject(ChatService);
  messages = this.chatService.messages;
  isBusy = this.chatService.isBusy;
}

import { Component, inject } from '@angular/core';
import { ChatService } from '../../services/chat.service';

@Component({
  selector: 'app-chat-topbar',
  templateUrl: './chat-topbar.component.html',
  styleUrls: ['./chat-topbar.component.scss']
})
export class ChatTopbarComponent {
  chatService = inject(ChatService)
  clear() {
    this.chatService.clearMessages();
  }
}

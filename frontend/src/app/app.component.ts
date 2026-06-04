import { Component, computed, inject } from '@angular/core';
import { ChatTopbarComponent } from './components/chat-topbar/chat-topbar.component';
import { ChatWindowComponent } from './components/chat-window/chat-window.component';
import { ChatInputComponent } from './components/chat-input/chat-input.component';
import { ChatService } from './services/chat.service';

@Component({
  selector: 'app-root',
  imports: [ChatTopbarComponent, ChatWindowComponent, ChatInputComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  private readonly chatService = inject(ChatService);
  readonly hasConversation = computed(() => this.chatService.messages().length > 1);
}

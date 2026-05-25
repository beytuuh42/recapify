import { Injectable, signal } from '@angular/core';
import { Message, Role } from '../models/summary.model';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private readonly initialMessage: Message = {
    id: crypto.randomUUID(),
    role: Role.assistant,
    avatar: 'A',
    content: 'Hello, please provide the title of the tv show as well as its season and episode number that you want a summary of.'
  };

  messages = signal<Message[]>([]);

  constructor() {
    this.clearMessages();
  }

  addMessage(message: Message): void {
    this.messages.update((msgs) => [...msgs, message]);
  }

  clearMessages(): void {
    this.messages.set([{ ...this.initialMessage, id: crypto.randomUUID() }]);
  }
}

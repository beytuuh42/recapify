import { TestBed } from '@angular/core/testing';

import { ChatService } from './chat.service';
import { Role } from '../models/summary.model';

describe('ChatService', () => {
  let service: ChatService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ChatService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('starts with a single assistant greeting and idle state', () => {
    expect(service.messages()).toHaveLength(1);
    expect(service.messages()[0].role).toBe(Role.assistant);
    expect(service.messages()[0].avatar).toBe('A');
    expect(service.messages()[0].content).toContain('please provide the title');
    expect(service.isBusy()).toBe(false);
  });

  it('adds messages without mutating existing messages', () => {
    const initialMessage = service.messages()[0];
    const userMessage = {
      id: crypto.randomUUID(),
      role: Role.user,
      avatar: 'U',
      content: 'summarize Breaking Bad season 1 episode 1'
    } as const;

    service.addMessage(userMessage);

    expect(service.messages()).toEqual([initialMessage, userMessage]);
  });

  it('appends text to the matching message only', () => {
    const targetId = crypto.randomUUID();
    const otherId = crypto.randomUUID();

    service.addMessage({ id: targetId, role: Role.assistant, avatar: 'A', content: 'Hello' });
    service.addMessage({ id: otherId, role: Role.user, avatar: 'U', content: 'Unchanged' });

    service.appendToMessage(targetId, ', world');

    expect(service.messages().find((message) => message.id === targetId)?.content).toBe('Hello, world');
    expect(service.messages().find((message) => message.id === otherId)?.content).toBe('Unchanged');
  });

  it('updates busy state', () => {
    service.setBusy(true);
    expect(service.isBusy()).toBe(true);

    service.setBusy(false);
    expect(service.isBusy()).toBe(false);
  });

  it('clears messages back to a fresh assistant greeting', () => {
    const originalGreetingId = service.messages()[0].id;
    service.addMessage({ id: crypto.randomUUID(), role: Role.user, avatar: 'U', content: 'hello' });

    service.clearMessages();

    expect(service.messages()).toHaveLength(1);
    expect(service.messages()[0].role).toBe(Role.assistant);
    expect(service.messages()[0].id).not.toBe(originalGreetingId);
  });
});

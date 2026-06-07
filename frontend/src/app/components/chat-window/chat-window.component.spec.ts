import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatWindowComponent } from './chat-window.component';
import { ChatService } from '../../services/chat.service';
import { EpisodeSummary, Role } from '../../models/summary.model';

describe('ChatWindowComponent', () => {
  let fixture: ComponentFixture<ChatWindowComponent>;
  let chatService: ChatService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatWindowComponent],
      providers: [ChatService]
    }).compileComponents();

    fixture = TestBed.createComponent(ChatWindowComponent);
    chatService = TestBed.inject(ChatService);
  });

  it('hides the typing indicator once a summary message is present', () => {
    chatService.setBusy(true);
    chatService.addMessage({
      id: crypto.randomUUID(),
      role: Role.assistant,
      avatar: 'A',
      content: '',
      summary: { title: 'Pilot', final_summary: 'x', key_events: [], characters: [], chunk_summaries: [] } as EpisodeSummary
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('app-typing-indicator')).toBeNull();
  });

  it('scrolls the page to the bottom when messages update', async () => {
    const scrollTo = vi.spyOn(window, 'scrollTo').mockImplementation(() => {});
    fixture.detectChanges();

    Object.defineProperty(document.documentElement, 'scrollHeight', {
      configurable: true,
      value: 640
    });

    chatService.addMessage({
      id: crypto.randomUUID(),
      role: Role.assistant,
      avatar: 'A',
      content: 'A much longer summary line that should force the chat pane to stay pinned to the bottom.'
    });

    fixture.detectChanges();
    await fixture.whenStable();

    expect(scrollTo).toHaveBeenLastCalledWith({
      top: 640,
      behavior: 'smooth'
    });
  });
});

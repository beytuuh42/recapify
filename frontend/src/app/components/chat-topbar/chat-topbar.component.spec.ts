import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatTopbarComponent } from './chat-topbar.component';
import { ChatService } from '../../services/chat.service';

describe('ChatTopbarComponent', () => {
  let fixture: ComponentFixture<ChatTopbarComponent>;
  let chatService: ChatService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatTopbarComponent],
      providers: [ChatService]
    }).compileComponents();

    fixture = TestBed.createComponent(ChatTopbarComponent);
    chatService = TestBed.inject(ChatService);
  });

  it('renders successfully', () => {
    fixture.detectChanges();

    expect(fixture.componentInstance).toBeTruthy();
  });

  it('clears chat messages when starting a new conversation', () => {
    const clearMessages = vi.spyOn(chatService, 'clearMessages');
    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector('button') as HTMLButtonElement;
    button.click();

    expect(clearMessages).toHaveBeenCalledOnce();
  });
});

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, Subject, throwError } from 'rxjs';

import { ChatInputComponent } from './chat-input.component';
import { ChatService } from '../../services/chat.service';
import { LlmService } from '../../services/llm.service';
import { AppLoggerService } from '../../services/app-logger.service';
import { EpisodeSummary, Role } from '../../models/summary.model';

const mockSummary: EpisodeSummary = {
  title: 'Breaking Bad S1E1',
  final_summary: 'Walter starts cooking meth.',
  key_events: ['Walter begins his criminal journey'],
  characters: ['Walter White', 'Jesse Pinkman'],
  chunk_summaries: []
};

describe('ChatInputComponent', () => {
  let fixture: ComponentFixture<ChatInputComponent>;
  let chatService: ChatService;
  let llmService: { getSummary: ReturnType<typeof vi.fn> };
  let logger: {
    debug: ReturnType<typeof vi.fn>;
    info: ReturnType<typeof vi.fn>;
    error: ReturnType<typeof vi.fn>;
  };

  beforeEach(async () => {
    llmService = {
      getSummary: vi.fn()
    };
    logger = {
      debug: vi.fn(),
      info: vi.fn(),
      error: vi.fn()
    };

    await TestBed.configureTestingModule({
      imports: [ChatInputComponent],
      providers: [
        ChatService,
        { provide: LlmService, useValue: llmService },
        { provide: AppLoggerService, useValue: logger }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ChatInputComponent);
    chatService = TestBed.inject(ChatService);
  });

  it('submits the textarea value and marks chat as busy while waiting', () => {
    const pendingSummary = new Subject<EpisodeSummary>();
    llmService.getSummary.mockReturnValue(pendingSummary.asObservable());
    fixture.detectChanges();

    const textarea = fixture.nativeElement.querySelector('textarea') as HTMLTextAreaElement;
    const button = fixture.nativeElement.querySelector('button') as HTMLButtonElement;
    textarea.value = 'summarize Breaking Bad season 1 episode 1';

    button.click();
    fixture.detectChanges();

    expect(llmService.getSummary).toHaveBeenCalledWith('summarize Breaking Bad season 1 episode 1');
    expect(textarea.value).toBe('');
    expect(chatService.isBusy()).toBe(true);
    expect(button.disabled).toBe(true);
    expect(chatService.messages().at(-1)).toMatchObject({
      role: Role.user,
      avatar: 'U',
      content: 'summarize Breaking Bad season 1 episode 1'
    });
    expect(logger.info).toHaveBeenCalledWith('Summary submission started', {
      textLength: 'summarize Breaking Bad season 1 episode 1'.length
    });
  });

  it('ignores submissions while the chat is busy', () => {
    chatService.setBusy(true);
    fixture.detectChanges();

    const textarea = fixture.nativeElement.querySelector('textarea') as HTMLTextAreaElement;
    textarea.value = 'summarize something else';

    fixture.componentInstance.send(textarea);

    expect(llmService.getSummary).not.toHaveBeenCalled();
    expect(chatService.messages()).toHaveLength(1);
    expect(textarea.value).toBe('summarize something else');
    expect(logger.debug).toHaveBeenCalledWith('Ignored summary submission while chat is busy');
  });

  it('ignores empty submissions', () => {
    fixture.detectChanges();

    const textarea = fixture.nativeElement.querySelector('textarea') as HTMLTextAreaElement;
    textarea.value = '   ';

    fixture.componentInstance.send(textarea);

    expect(llmService.getSummary).not.toHaveBeenCalled();
    expect(chatService.messages()).toHaveLength(1);
    expect(logger.debug).toHaveBeenCalledWith('Ignored empty summary submission');
  });

  it('adds an error message and clears busy state when summary generation fails', () => {
    llmService.getSummary.mockReturnValue(throwError(() => ({
      status: 500,
      statusText: 'Internal Server Error'
    })));
    fixture.detectChanges();

    const textarea = fixture.nativeElement.querySelector('textarea') as HTMLTextAreaElement;
    textarea.value = 'summarize Breaking Bad season 1 episode 1';

    fixture.componentInstance.send(textarea);

    expect(chatService.isBusy()).toBe(false);
    expect(chatService.messages().at(-1)).toMatchObject({
      role: Role.assistant,
      avatar: 'A',
      content: 'Something went wrong. Please try again.'
    });
    expect(logger.error).toHaveBeenCalledWith(
      'Summary submission failed',
      {
        status: 500,
        statusText: 'Internal Server Error'
      },
      expect.anything()
    );
  });

  it('adds a structured summary message on successful response', () => {
    llmService.getSummary.mockReturnValue(of(mockSummary));
    fixture.detectChanges();

    const textarea = fixture.nativeElement.querySelector('textarea') as HTMLTextAreaElement;
    textarea.value = 'summarize Breaking Bad season 1 episode 1';

    fixture.componentInstance.send(textarea);

    const assistantMessage = chatService.messages().at(-1);
    expect(assistantMessage).toMatchObject({
      role: Role.assistant,
      avatar: 'A',
      content: '',
      summary: mockSummary
    });
    expect(chatService.isBusy()).toBe(true);
  });

  it('submits on Enter', () => {
    const pendingSummary = new Subject<EpisodeSummary>();
    llmService.getSummary.mockReturnValue(pendingSummary.asObservable());
    fixture.detectChanges();

    const textarea = fixture.nativeElement.querySelector('textarea') as HTMLTextAreaElement;
    textarea.value = 'summarize Severance season 1 episode 1';

    const enterEvent = new KeyboardEvent('keydown', {
      key: 'Enter',
      bubbles: true,
      cancelable: true
    });

    textarea.dispatchEvent(enterEvent);
    fixture.detectChanges();

    expect(enterEvent.defaultPrevented).toBe(true);
    expect(llmService.getSummary).toHaveBeenCalledWith('summarize Severance season 1 episode 1');
  });

  it('keeps Shift+Enter for multiline input', () => {
    fixture.detectChanges();

    const textarea = fixture.nativeElement.querySelector('textarea') as HTMLTextAreaElement;

    textarea.value = 'line 1';
    const shiftEnterEvent = new KeyboardEvent('keydown', {
      key: 'Enter',
      shiftKey: true,
      bubbles: true,
      cancelable: true
    });

    textarea.dispatchEvent(shiftEnterEvent);

    expect(shiftEnterEvent.defaultPrevented).toBe(false);
    expect(llmService.getSummary).not.toHaveBeenCalled();
  });
});

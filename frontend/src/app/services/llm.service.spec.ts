import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';

import { LlmService } from './llm.service';
import { AppLoggerService } from './app-logger.service';
import { EpisodeSummary } from '../models/summary.model';
import { environment } from '../../environments/environment';

describe('LlmService', () => {
  let service: LlmService;
  let httpTesting: HttpTestingController;
  let logger: Pick<AppLoggerService, 'info' | 'error'>;

  beforeEach(() => {
    logger = {
      info: vi.fn(),
      error: vi.fn()
    };

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: AppLoggerService, useValue: logger }
      ]
    });

    service = TestBed.inject(LlmService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('posts summary requests to the backend API and logs success', () => {
    const prompt = 'summarize Breaking Bad season 1 episode 1';
    const mockSummary: EpisodeSummary = {
      title: 'Breaking Bad S1E1',
      final_summary: 'Walter starts cooking meth.',
      key_events: ['Walter begins his criminal journey'],
      characters: ['Walter White', 'Jesse Pinkman'],
      chunk_summaries: []
    };
    let receivedSummary: EpisodeSummary | undefined;

    service.getSummary(prompt).subscribe((summary) => {
      receivedSummary = summary;
    });

    const req = httpTesting.expectOne(`${environment.apiUrl}api/v1/llm/summary`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toBe(prompt);

    req.flush(mockSummary);

    expect(receivedSummary).toEqual(mockSummary);
    expect(logger.info).toHaveBeenCalledWith('Requesting episode summary', {
      textLength: prompt.length
    });
    expect(logger.info).toHaveBeenCalledWith('Episode summary received', {
      durationMs: expect.any(Number),
      finalSummaryLength: mockSummary.final_summary.length,
      keyEventsCount: mockSummary.key_events.length
    });
  });

  it('logs failed summary requests with status metadata', () => {
    let receivedError: unknown;

    service.getSummary('bad request').subscribe({
      error: (error) => {
        receivedError = error;
      }
    });

    const req = httpTesting.expectOne(`${environment.apiUrl}api/v1/llm/summary`);
    req.flush('Server error', {
      status: 500,
      statusText: 'Internal Server Error'
    });

    expect(receivedError).toBeTruthy();
    expect(logger.error).toHaveBeenCalledWith(
      'Episode summary request failed',
      {
        durationMs: expect.any(Number),
        status: 500,
        statusText: 'Internal Server Error',
        url: `${environment.apiUrl}api/v1/llm/summary`
      },
      expect.anything()
    );
  });
});

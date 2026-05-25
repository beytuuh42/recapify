import { TestBed } from '@angular/core/testing';

import { LlmService } from './llm.service';

describe('LlmServiceService', () => {
  let service: LlmService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LlmService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

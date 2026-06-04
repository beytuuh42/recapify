import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EpisodeSummaryComponent } from './episode-summary.component';
import { EpisodeSummary } from '../../models/summary.model';

const summary: EpisodeSummary = {
  title: 'Pilot',
  final_summary: 'Walt cooks.',
  key_events: ['Event A', 'Event B'],
  characters: ['Walt', 'Jesse'],
  chunk_summaries: [
    { chunk_number: 1, title: 'Scene 1', summary: 'First.', key_events: [], characters: [] },
    { chunk_number: 2, title: 'Scene 2', summary: 'Second.', key_events: [], characters: [] }
  ]
};

describe('EpisodeSummaryComponent', () => {
  let fixture: ComponentFixture<EpisodeSummaryComponent>;
  let component: EpisodeSummaryComponent;

  beforeEach(async () => {
    vi.useFakeTimers();
    await TestBed.configureTestingModule({
      imports: [EpisodeSummaryComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(EpisodeSummaryComponent);
    component = fixture.componentInstance;
    component.summary = summary;
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('reveals the recap text before any other section', () => {
    fixture.detectChanges();

    expect(component.revealedText()).toBe('');
    expect(component.revealedKeyEvents()).toBe(0);
    expect(component.charactersVisible()).toBe(false);
    expect(component.revealedScenes()).toBe(0);

    // Recap is 11 chars at ~3 chars/tick over 16ms ticks.
    vi.advanceTimersByTime(16 * 5);
    expect(component.revealedText()).toBe(summary.final_summary);
    expect(component.revealedKeyEvents()).toBe(0);
  });

  it('reveals key events one at a time after the recap', () => {
    fixture.detectChanges();
    vi.advanceTimersByTime(16 * 5);

    vi.advanceTimersByTime(320);
    expect(component.revealedKeyEvents()).toBe(1);

    vi.advanceTimersByTime(320);
    expect(component.revealedKeyEvents()).toBe(2);
    expect(component.charactersVisible()).toBe(false);
  });

  it('reveals characters as a group, then scenes one at a time', () => {
    fixture.detectChanges();
    vi.advanceTimersByTime(16 * 5); // recap
    vi.advanceTimersByTime(320 * 2); // both key events

    vi.advanceTimersByTime(250); // section beat
    expect(component.charactersVisible()).toBe(true);
    expect(component.revealedScenes()).toBe(0);

    vi.advanceTimersByTime(250 + 450);
    expect(component.revealedScenes()).toBe(1);

    vi.advanceTimersByTime(450);
    expect(component.revealedScenes()).toBe(2);
  });
});

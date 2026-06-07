import { Component, EventEmitter, Input, OnInit, OnDestroy, Output, signal } from '@angular/core';
import { EpisodeSummary } from '../../models/summary.model';

@Component({
  selector: 'app-episode-summary',
  imports: [],
  templateUrl: './episode-summary.component.html',
  styleUrls: ['./episode-summary.component.scss']
})
export class EpisodeSummaryComponent implements OnInit, OnDestroy {
  @Input() summary!: EpisodeSummary;
  @Output() animationComplete = new EventEmitter<void>();

  // Recap text streams at the same rate the chat used previously.
  private static readonly REVEAL_INTERVAL_MS = 16;
  private static readonly CHARACTERS_PER_SECOND = 180;
  // One list item at a time, paced so a human can follow along.
  private static readonly KEY_EVENT_INTERVAL_MS = 320;
  private static readonly SCENE_INTERVAL_MS = 450;
  // Small beat before a whole section appears as a group.
  private static readonly SECTION_BEAT_MS = 250;

  revealedText = signal('');
  revealedKeyEvents = signal(0);
  charactersVisible = signal(false);
  revealedScenes = signal(0);

  private timers = new Set<ReturnType<typeof setInterval>>();

  ngOnInit() {
    this.revealRecap();
  }

  ngOnDestroy() {
    this.timers.forEach(clearInterval);
    this.timers.clear();
  }

  private revealRecap() {
    const characters = Array.from(this.summary.final_summary);
    const charsPerTick = Math.max(
      1,
      Math.round(
        (EpisodeSummaryComponent.CHARACTERS_PER_SECOND * EpisodeSummaryComponent.REVEAL_INTERVAL_MS) / 1000
      )
    );

    let i = 0;
    this.runInterval(EpisodeSummaryComponent.REVEAL_INTERVAL_MS, (stop) => {
      const chunk = characters.slice(i, i + charsPerTick).join('');
      i += chunk.length;
      this.revealedText.update(t => t + chunk);
      if (i >= characters.length) {
        stop();
        this.revealKeyEvents();
      }
    });
  }

  private revealKeyEvents() {
    if (!this.summary.key_events.length) {
      this.revealCharacters();
      return;
    }

    this.runInterval(EpisodeSummaryComponent.KEY_EVENT_INTERVAL_MS, (stop) => {
      this.revealedKeyEvents.update(n => n + 1);
      if (this.revealedKeyEvents() >= this.summary.key_events.length) {
        stop();
        this.revealCharacters();
      }
    });
  }

  private revealCharacters() {
    if (!this.summary.characters.length) {
      this.revealScenes();
      return;
    }

    this.runTimeout(EpisodeSummaryComponent.SECTION_BEAT_MS, () => {
      this.charactersVisible.set(true);
      this.revealScenes();
    });
  }

  private revealScenes() {
    if (!this.summary.chunk_summaries.length) {
      this.animationComplete.emit();
      return;
    }

    this.runTimeout(EpisodeSummaryComponent.SECTION_BEAT_MS, () => {
      this.runInterval(EpisodeSummaryComponent.SCENE_INTERVAL_MS, (stop) => {
        this.revealedScenes.update(n => n + 1);
        if (this.revealedScenes() >= this.summary.chunk_summaries.length) {
          stop();
          this.animationComplete.emit();
        }
      });
    });
  }

  private runInterval(ms: number, tick: (stop: () => void) => void) {
    const timer = setInterval(() => tick(() => this.clear(timer)), ms);
    this.timers.add(timer);
  }

  private runTimeout(ms: number, fn: () => void) {
    const timer = setTimeout(() => {
      this.timers.delete(timer);
      fn();
    }, ms);
    this.timers.add(timer);
  }

  private clear(timer: ReturnType<typeof setInterval>) {
    clearInterval(timer);
    this.timers.delete(timer);
  }
}

import { Component, Input, OnInit, OnDestroy, signal } from '@angular/core';
import { EpisodeSummary } from '../../models/summary.model';

@Component({
  selector: 'app-episode-summary',
  imports: [],
  templateUrl: './episode-summary.component.html',
  styleUrls: ['./episode-summary.component.scss']
})
export class EpisodeSummaryComponent implements OnInit, OnDestroy {
  @Input() summary!: EpisodeSummary;

  private static readonly REVEAL_INTERVAL_MS = 16;
  private static readonly CHARACTERS_PER_SECOND = 180;

  revealedText = signal('');
  sectionsVisible = signal(false);

  private timer: ReturnType<typeof setInterval> | null = null;

  ngOnInit() {
    const characters = Array.from(this.summary.final_summary);
    const charsPerTick = Math.max(
      1,
      Math.round(
        (EpisodeSummaryComponent.CHARACTERS_PER_SECOND * EpisodeSummaryComponent.REVEAL_INTERVAL_MS) / 1000
      )
    );

    let i = 0;
    this.timer = setInterval(() => {
      const chunk = characters.slice(i, i + charsPerTick).join('');
      i += chunk.length;
      this.revealedText.update(t => t + chunk);

      if (i >= characters.length) {
        clearInterval(this.timer!);
        this.timer = null;
        this.sectionsVisible.set(true);
      }
    }, EpisodeSummaryComponent.REVEAL_INTERVAL_MS);
  }

  ngOnDestroy() {
    if (this.timer) {
      clearInterval(this.timer);
    }
  }
}

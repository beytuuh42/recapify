import { Component, Input } from '@angular/core';
import { EpisodeSummary } from '../../models/summary.model';

@Component({
  selector: 'app-episode-summary',
  imports: [],
  templateUrl: './episode-summary.component.html',
  styleUrls: ['./episode-summary.component.scss']
})
export class EpisodeSummaryComponent {
  @Input() summary!: EpisodeSummary;
}

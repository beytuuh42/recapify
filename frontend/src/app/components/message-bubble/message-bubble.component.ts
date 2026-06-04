import { Component, Input } from '@angular/core';
import { EpisodeSummary, Role } from '../../models/summary.model';
import { EpisodeSummaryComponent } from '../episode-summary/episode-summary.component';

@Component({
  selector: 'app-message-bubble',
  imports: [EpisodeSummaryComponent],
  templateUrl: './message-bubble.component.html',
  styleUrls: ['./message-bubble.component.scss']
})
export class MessageBubbleComponent {
  @Input() role: Role = Role.assistant;
  @Input() avatar = '';
  @Input() text = '';
  @Input() summary?: EpisodeSummary;

  readonly Role = Role;
}

import { Component, Input } from '@angular/core';
import { Role } from '../../models/summary.model';

@Component({
  selector: 'app-message-bubble',
  templateUrl: './message-bubble.component.html',
  styleUrls: ['./message-bubble.component.scss']
})
export class MessageBubbleComponent {
  @Input() role: Role = Role.assistant;
  @Input() avatar = '';
  @Input() text = '';

  readonly Role = Role;
}

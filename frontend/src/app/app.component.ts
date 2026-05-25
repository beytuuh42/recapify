import { Component } from '@angular/core';
import { ChatTopbarComponent } from './components/chat-topbar/chat-topbar.component';
import { ChatWindowComponent } from './components/chat-window/chat-window.component';
import { ChatInputComponent } from './components/chat-input/chat-input.component';

@Component({
  selector: 'app-root',
  imports: [ChatTopbarComponent, ChatWindowComponent, ChatInputComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {}

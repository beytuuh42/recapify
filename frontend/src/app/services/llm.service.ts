import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Summary } from '../models/summary.model';
import { AppLoggerService } from './app-logger.service';
import { tap } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LlmService {
  private apiUrl = environment.apiUrl;

  constructor(
    private http: HttpClient,
    private logger: AppLoggerService
  ) { }

  getSummary(text: string) {
    const startedAt = performance.now();

    this.logger.info('Requesting episode summary', {
      textLength: text.length
    });

    return this.http.post<Summary>(`${this.apiUrl}api/v1/llm/summary`, text).pipe(
      tap({
        next: (summary) => {
          this.logger.info('Episode summary received', {
            durationMs: Math.round(performance.now() - startedAt),
            summaryLength: summary.content.length
          });
        },
        error: (err) => {
          this.logger.error('Episode summary request failed', {
            durationMs: Math.round(performance.now() - startedAt),
            status: err?.status,
            statusText: err?.statusText,
            url: err?.url
          }, err);
        }
      })
    );
  }
}

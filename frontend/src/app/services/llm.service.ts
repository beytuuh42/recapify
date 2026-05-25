import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Summary } from '../models/summary.model';

@Injectable({
  providedIn: 'root'
})
export class LlmService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  getSummary(text: string) {
    return this.http.post<Summary>(`${this.apiUrl}api/v1/llm/summary`, text);
  }
}

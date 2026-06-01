import { Injectable } from '@angular/core';
import * as Sentry from '@sentry/angular';

type LogAttributes = Record<string, unknown>;

@Injectable({
  providedIn: 'root'
})
export class AppLoggerService {
  debug(message: string, attributes: LogAttributes = {}): void {
    console.debug(message, attributes);
    Sentry.logger.debug(message, attributes);
  }

  info(message: string, attributes: LogAttributes = {}): void {
    console.info(message, attributes);
    Sentry.logger.info(message, attributes);
  }

  warn(message: string, attributes: LogAttributes = {}): void {
    console.warn(message, attributes);
    Sentry.logger.warn(message, attributes);
  }

  error(message: string, attributes: LogAttributes = {}, error?: unknown): void {
    console.error(message, attributes, error);
    Sentry.logger.error(message, attributes);

    if (error) {
      Sentry.captureException(error, {
        extra: attributes
      });
    }
  }
}

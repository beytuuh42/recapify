import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';
import { environment } from './environments/environment';
import * as Sentry from '@sentry/angular';

const apiOrigin = new URL(environment.apiUrl).origin;

Sentry.init({
  dsn: environment.sentryDsn || undefined,
  enabled: Boolean(environment.sentryDsn),
  environment: environment.sentryEnvironment,
  integrations: [
    Sentry.browserTracingIntegration()
  ],
  tracesSampleRate: environment.production ? 0.2 : 1.0,
  tracePropagationTargets: ['localhost', apiOrigin],
  enableLogs: true
});

if (!environment.production && environment.sentryDsn) {
  Sentry.logger.info('Sentry development logger initialized', {
    environment: environment.sentryEnvironment
  });
  Sentry.captureMessage('Sentry development client initialized', 'info');
}

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => {
    Sentry.captureException(err);
    console.error('Frontend bootstrap failed', err);
  });

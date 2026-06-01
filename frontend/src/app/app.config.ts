import { ApplicationConfig, ErrorHandler, inject, provideAppInitializer, provideZoneChangeDetection } from '@angular/core';
import { provideRouter, Router } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import * as Sentry from '@sentry/angular';

import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(),
    {
      provide: ErrorHandler,
      useValue: Sentry.createErrorHandler({
        logErrors: true
      })
    },
    {
      provide: Sentry.TraceService,
      deps: [Router]
    },
    provideAppInitializer(() => {
      inject(Sentry.TraceService);
    })
  ]
};

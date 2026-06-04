# Recapify (WIP)

Recapify is a full-stack AI application that generates concise episode recaps from natural-language requests.

Type something like:

```text
summarize Breaking Bad season 1 episode 9
```

Recapify extracts the media intent, finds subtitle data, summarizes the transcript with Gemini, and returns a readable recap in a chat-style interface.

## Live Demo

https://recapify-frontend.onrender.com

The demo is hosted on Render's free tier. The first request after inactivity can take 30-60 seconds while the services wake up.

## Why I Built This

Episode recaps are useful, but they are often scattered across websites, inconsistent in quality, or hard to find for a specific season and episode. Recapify explores a more direct workflow: ask for the exact episode you care about and receive a focused summary generated from subtitle data.

## What It Does

- Accepts natural-language requests such as `summarize Breaking Bad season 1 episode 9`.
- Extracts structured media intent from free text: title, season, episode, media type, and language.
- Searches for matching subtitle data through OpenSubtitles.
- Cleans SRT content and splits transcripts into manageable chunks.
- Generates chunk-level summaries with Gemini.
- Merges chunk summaries into one coherent episode recap.
- Caches generated summaries by title, season, episode, and language.
- Returns the result through an Angular chat UI.

## Engineering Highlights

- Built as a three-service system with Angular, Spring Boot, and FastAPI.
- Uses Spring Boot as the API boundary between the browser and the ML workflow.
- Keeps the ML workflow isolated in FastAPI: intent extraction, subtitle retrieval, transcript chunking, LLM summarization, summary merging, and caching.
- Uses LangChain and LangSmith prompt references for structured LLM workflows.
- Uses typed request and response models across the backend and ML service.
- Adds request correlation with propagated `X-Request-Id` values across backend and ML logs.
- Adds frontend observability through Sentry and local browser debugging through Playwright.
- Runs locally with Docker Compose hot reload across all services.

## Architecture

```text
User
  -> Angular frontend
  -> Spring Boot backend
  -> FastAPI ML service
  -> OpenSubtitles + Gemini
  -> Episode recap
```

The Angular frontend owns the chat experience. The Spring Boot backend exposes the frontend-facing API and forwards summary work to the ML service. The FastAPI service owns the AI workflow: it parses intent, fetches subtitles, chunks transcripts, calls Gemini, merges the final summary, and caches completed results.

## Tech Stack

| Area | Technology |
|---|---|
| Frontend | Angular 19, Signals, RxJS, Sentry, Playwright |
| Backend | Java 21, Spring Boot 4, WebClient, Lombok |
| ML service | Python 3.12, FastAPI, Pydantic, LangChain, LangSmith, Gemini |
| External APIs | OpenSubtitles, Google Gemini |
| Runtime | Docker, Docker Compose, Nginx |
| Observability | Sentry frontend telemetry, request IDs, structured service logs |

## Demo Flow

1. The user enters a request in the chat UI.
2. The frontend sends the raw text to the backend.
3. The backend creates a request ID and forwards the work to the ML service.
4. The ML service extracts structured intent from the request.
5. The ML service finds and downloads subtitles for the requested episode.
6. The transcript is cleaned, chunked, summarized, and merged.
7. The final recap is returned to the frontend and revealed in the chat.

## Running Locally

Prerequisites:

- Docker Desktop
- Git
- Google API key
- OpenSubtitles API credentials
- Optional: LangSmith credentials for prompt and tracing workflows

Create the ML environment file:

```bash
cp ml/.env.example ml/.env
```

Fill in:

```text
GOOGLE_API_KEY=...
OPEN_SUBTITLES_API_KEY=...
OPEN_SUBTITLES_USER=...
OPEN_SUBTITLES_PASSWORD=...
LANGSMITH_API_KEY=...
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
LANGSMITH_TRACING=true
```

Start the full development stack:

```bash
docker compose --profile dev watch
```

Open the frontend:

```text
http://localhost:4200
```

Development ports:

| Service | URL |
|---|---|
| Frontend | http://localhost:4200 |
| Backend | http://localhost:8081 |
| ML service | http://localhost:8000 |
| ML API docs | http://localhost:8000/docs |

## Testing

Run the focused unit tests from each service directory:

```bash
cd frontend && npm test
cd backend/recapify && ./mvnw test
cd ml && python -m unittest discover -s tests
```

The frontend suite runs on Vitest, the backend suite uses JUnit, and the ML service uses standard-library `unittest`.

## Observability and Debugging

Frontend events, errors, traces, and logs are sent to Sentry when a Sentry DSN is configured. In local development, browser console output is also useful for inspecting the frontend flow.

Backend and ML logs are written to stdout, so they are visible through Docker logs:

```bash
docker logs --tail 200 recapify-backend-dev
docker logs --tail 200 recapify-ml-dev
```

Requests through the backend receive an `X-Request-Id`. The same ID is propagated to the ML service, which makes it possible to follow one summary request across service logs.

The frontend also includes a Playwright-based debug script:

```bash
cd frontend
npm run debug:frontend
npm run debug:frontend -- "summarize Breaking Bad season 1 episode 1"
```

It captures browser console messages, page errors, failed requests, and HTTP errors from a running local frontend.

## Configuration

Frontend production builds generate `src/environments/environment.ts` from environment variables in `frontend/set-env.js`.

| Variable | Purpose | Default |
|---|---|---|
| `API_URL` | Backend base URL used by the frontend production build | `http://localhost:8080/` |
| `SENTRY_DSN` | Enables Sentry telemetry in the frontend | empty |
| `SENTRY_ENVIRONMENT` | Sentry environment name | `production` |
| `LLM_SERVICE_BASEURL` | Backend-to-ML service URL | `http://localhost:8000` |

In Docker Compose development, the backend points to the ML container with:

```text
LLM_SERVICE_BASEURL=http://ml-dev:8000
```

## Current Limitations and Next Steps

- The hosted demo runs on a free tier, so cold starts can make the first request slow.
- Subtitle availability and quality depend on OpenSubtitles results.
- The backend currently acts mainly as an API boundary and service orchestration layer.
- Focused unit tests now exist for all three services, but broader end-to-end coverage is still limited.
- Planned portfolio-focused improvements include richer structured recap presentation, clearer progress feedback during long-running summary generation, backend contract cleanup, and ML workflow separation.

## Project Structure

```text
recapify/
|-- frontend/              Angular chat UI
|-- backend/recapify/      Spring Boot API service
|-- ml/                    FastAPI ML service
|   `-- app/               ML service source
`-- docker-compose.yml     Dev and production container profiles
```

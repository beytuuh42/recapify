# AGENTS.md

Guidance for AI agents working in this repo. Read this before editing.

## Overview

Recapify generates AI summaries of TV/movie/anime episodes. A free-text user request flows through three services:

```
Browser → frontend (Angular) → backend (Spring Boot) → ml (FastAPI) → OpenSubtitles + Gemini
```

The backend is a thin pass-through to the ML service today; intent parsing, subtitle fetching, chunked summarization, and merging all live in `ml/`.

## Repo layout

```
recapify/
├── frontend/              # Angular 19 (Signals), served on :4200
├── backend/recapify/      # Spring Boot 4 / Java 21, served on :8080
├── ml/                    # FastAPI + LangChain + google-genai, served on :8000
│   ├── app/               # Source (main.py, LLMClient.py, srt_handler.py, …)
│   └── prompts/           # LLM prompt templates — see "Off-limits"
└── docker-compose.yml     # `dev` and `prod` profiles
```

Each service has its own `Dockerfile` (prod) and `Dockerfile.dev` (hot-reload).

## Dev commands

Standard dev loop (hot-reload for all three services):

```bash
cp ml/.env.example ml/.env   # fill in keys first
docker compose --profile dev watch
```

Per-service, outside Docker:

| Service  | Install / setup            | Run                                          | Test                  |
|----------|----------------------------|----------------------------------------------|-----------------------|
| frontend | `npm install`              | `npm start` (ng serve)                       | `npm test` (Karma)    |
| backend  | (mvnw is checked in)       | `./mvnw spring-boot:run`                     | `./mvnw test`         |
| ml       | `pip install -r requirements.txt` | `uvicorn app.main:app --reload --port 8000` | none                  |

There is **no test suite** at the moment across any service — placeholder specs only. Do not invent CI assumptions.

## Key files & wiring

- [docker-compose.yml](docker-compose.yml) — `dev` profile uses `Dockerfile.dev` + `develop.watch` per service; `prod` profile builds only `frontend-prod`.
- [backend/recapify/src/main/resources/application.properties](backend/recapify/src/main/resources/application.properties) — `LLM_SERVICE_BASEURL` env var points the backend at the ml service (defaults to `http://localhost:8000`).
- [frontend/set-env.js](frontend/set-env.js) — generates `src/environments/environment.ts` at **production build time** from `API_URL`. Local `ng serve` uses `environment.development.ts` via Angular's `fileReplacements`. The script normalizes `API_URL` to end with exactly one trailing slash; preserve that — `LlmService` concatenates `` `${apiUrl}api/v1/...` `` directly.
- [ml/app/main.py](ml/app/main.py) — Gemini model name and structured-output wiring are hardcoded here. Changing models is a code change, not config.

## Off-limits for AI

Do **not** modify these without an explicit ask from the maintainer:

- **`ml/prompts/*.txt`** — hand-tuned LLM prompts. Wording, structure, and example formatting are load-bearing.
- **`pom.xml`, `frontend/package.json`, `ml/requirements.txt`** — no dependency adds, bumps, or removals. Lockfile churn included.
- **`frontend/set-env.js`** — touch only if the user asked; comments in the file document past Render deploy footguns (don't read `NODE_ENV`, ensure trailing slash).
- **`.claude/`, `/plans/`, `/scratch/`** — gitignored working dirs; never commit anything under them.

## Conventions

Inferred from current code; follow them unless the user says otherwise.

- **Frontend (Angular 19):** standalone components, Signals-based state, single quotes in TS, 2-space indent (enforced by `.editorconfig`). Component files colocate `.ts` / `.html` / `.scss` / `.spec.ts` under `src/app/components/<name>/`.
- **Backend (Spring Boot / Java 21):** package root `com.recapify`, feature packages (`llm/`, `controllers/`). Lombok is on the annotation processor path — prefer `@Data`/`@RequiredArgsConstructor` over hand-written boilerplate. Use `WebClient` (already configured in [WebClientConfig.java](backend/recapify/src/main/java/com/recapify/WebClientConfig.java)) for outbound HTTP, not `RestTemplate`.
- **ML (Python / FastAPI):** routes live in [main.py](ml/app/main.py), Pydantic models in [models.py](ml/app/models.py). All public endpoints are versioned under `/api/v1/`. The cache layer ([cache.py](ml/app/cache.py)) is keyed by `(title, season, episode, language)`.
- **API surface contract:** both backend and ml expose `/api/v1/...`. Keep that prefix when adding endpoints so the frontend's `${apiUrl}api/v1/...` concatenation keeps working.

## PR & branching

- Feature branches off `main`, PR back to `main`, **merge commits** (not squash) — preserves history.
- Keep PRs scoped to one concern. If a change touches more than one service, call that out in the PR body.
- Render auto-deploys from `main`; assume any merge ships to production.

## Vocabulary

- **Intent** — the structured `SummarizeRequest` (`title`, `season`, `episode`, `language`) parsed from free-text user input by the ml `/api/v1/intent` endpoint.
- **Chunk** — a slice of an SRT transcript handed to the LLM for partial summarization; chunks are summarized in parallel then merged.
- **Episode summary** — the final merged output returned to the client; cached by `(title, season, episode, language)`.

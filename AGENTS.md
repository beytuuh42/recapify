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
│   └── app/               # Source (main.py, LLMClient.py, srt_handler.py, …)
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
| frontend | `npm install`              | `npm start` (ng serve)                       | `npm test` (Vitest)   |
| backend  | (mvnw is checked in)       | `./mvnw spring-boot:run`                     | `./mvnw test`         |
| ml       | `pip install -r requirements.txt` | `uvicorn app.main:app --reload --port 8000` | `python -m unittest discover -s tests` |

Each service now has focused unit tests. Keep new tests close to the code they cover and do not assume broader CI coverage than what exists in the repo.

## Verification policy

Default verification is log inspection with `docker logs` for the service that was changed. Use that first for startup/runtime checks.

After making changes, verify by inspecting logs for the service that was changed:

| Changed area | Verification command |
|--------------|----------------------|
| `frontend/` | `docker logs --tail 200 recapify-frontend-dev` |
| `backend/recapify/` | `docker logs --tail 200 recapify-backend-dev` |
| `ml/` | `docker logs --tail 200 recapify-ml-dev` |

If a change touches multiple services, inspect each relevant container log. Keep commands standalone; do not combine them with `;`, `&&`, pipes, loops, redirection, or command substitution.

Build, test, Docker compose, Maven, npm, Python, curl, and API smoke commands are allowed when the user explicitly asks for them, when you need stronger validation for the change, or when you are fixing a failing check.

Log inspection may only catch startup or runtime errors that were logged; it does not prove compilation, tests, or behavior unless those checks were explicitly requested.

## Change scope

Keep changes scoped to the requested behavior. Do not refactor unrelated code, rename files, change dependencies, reformat broad areas, or churn generated files unless explicitly requested.

## Key files & wiring

- [docker-compose.yml](docker-compose.yml) — `dev` profile uses `Dockerfile.dev` + `develop.watch` per service; `prod` profile builds only `frontend-prod`.
- [backend/recapify/src/main/resources/application.properties](backend/recapify/src/main/resources/application.properties) — `LLM_SERVICE_BASEURL` env var points the backend at the ml service (defaults to `http://localhost:8000`).
- [frontend/set-env.js](frontend/set-env.js) — generates `src/environments/environment.ts` at **production build time** from `API_URL`. Local `ng serve` uses `environment.development.ts` via Angular's `fileReplacements`. The script normalizes `API_URL` to end with exactly one trailing slash; preserve that — `LlmService` concatenates `` `${apiUrl}api/v1/...` `` directly.
- [ml/app/main.py](ml/app/main.py) — Gemini model name and structured-output wiring are hardcoded here. Changing models is a code change, not config.

## Off-limits for AI

Do **not** modify these without an explicit ask from the maintainer:

- **`pom.xml`, `frontend/package.json`, `ml/requirements.txt`** — no dependency adds, bumps, or removals. Lockfile churn included.
- **`frontend/set-env.js`** — touch only if the user asked; comments in the file document past Render deploy footguns (don't read `NODE_ENV`, ensure trailing slash).
- **`.claude/`, `/plans/`, `/scratch/`** — gitignored working dirs; never commit anything under them.

If a requested change appears to require touching an off-limits file, stop and ask first.

## Conventions

Inferred from current code; follow them unless the user says otherwise.

- **Frontend (Angular 19):** standalone components, Signals-based state, single quotes in TS, 2-space indent (enforced by `.editorconfig`). Component files colocate `.ts` / `.html` / `.scss` / `.spec.ts` under `src/app/components/<name>/`.
- **Backend (Spring Boot / Java 21):** package root `com.recapify`, feature packages (`llm/`, `controllers/`). Lombok is on the annotation processor path — prefer `@Data`/`@RequiredArgsConstructor` over hand-written boilerplate. Use `WebClient` (already configured in [WebClientConfig.java](backend/recapify/src/main/java/com/recapify/WebClientConfig.java)) for outbound HTTP, not `RestTemplate`.
- **ML (Python / FastAPI):** routes live in [main.py](ml/app/main.py), Pydantic models in [models.py](ml/app/models.py). Prompt definitions are pulled from LangSmith in [LLMClient.py](ml/app/LLMClient.py). All public endpoints are versioned under `/api/v1/`. The cache layer ([cache.py](ml/app/cache.py)) is keyed by `(title, season, episode, language)`.
- **API surface contract:** both backend and ml expose `/api/v1/...`. Keep that prefix when adding endpoints so the frontend's `${apiUrl}api/v1/...` concatenation keeps working.

## PR & branching

- Feature branches off `main`, PR back to `main`, **merge commits** (not squash) — preserves history.
- **Branch names:** short, lowercase, hyphenated, describe the change. e.g. `add-agents-md`, `fix-cors-prod`, `refactor-llm-client`. Do **not** use auto-generated harness names like `claude/zen-diffie-…`; rename before pushing.
- **Commit messages:** no `Co-Authored-By: Claude …` trailer, no "Generated with Claude Code" footer, no tool/agent self-attribution of any kind. Plain conventional messages only.
- Keep PRs scoped to one concern. If a change touches more than one service, call that out in the PR body.
- PR bodies: no tool self-attribution footers either.
- Render auto-deploys from `main`; assume any merge ships to production.

## Worktrees & multi-agent work

Use Git worktrees when multiple agents or CLIs may work at the same time. A branch is the line of work; a worktree is the folder where that branch is checked out.

Prefer explicit sibling worktrees outside the main checkout, for example:

```
../recapify-agent-frontend
../recapify-agent-backend
../recapify-agent-ml
```

Each agent should work in its assigned worktree and branch. Do not edit another agent's worktree unless explicitly asked.

For independent features, use separate branches and separate worktrees. For shared features, prefer separate sub-branches/worktrees and merge them into an integration branch after review.

Before editing, check the current branch and working tree status. Do not overwrite, revert, clean, or delete changes made by another agent unless explicitly instructed.

Do not push auto-generated worktree or agent branch names. Rename temporary branches to short, descriptive names before pushing.

After a PR is merged and the branch's changes are in `main`, delete the local branch and remove its worktree instead of leaving stale copies behind.

## Vocabulary

- **Intent** — the structured `SummarizeRequest` (`title`, `season`, `episode`, `language`) parsed from free-text user input by the ml `/api/v1/intent` endpoint.
- **Chunk** — a slice of an SRT transcript handed to the LLM for partial summarization; chunks are summarized in parallel then merged.
- **Episode summary** — the final merged output returned to the client; cached by `(title, season, episode, language)`.

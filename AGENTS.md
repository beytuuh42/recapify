# AGENTS.md

Guidance for AI agents working in this repo. Keep this file short and practical.

## Project Snapshot

Recapify is a three-service AI recap app:

```text
Browser -> Angular frontend -> Spring Boot backend -> FastAPI ML service -> OpenSubtitles + Gemini
```

The backend is currently a thin API boundary. Intent parsing, subtitle fetching, transcript chunking, LLM summarization, merge logic, and local summary caching live in `ml/`.

Ports:

- Frontend: `4200`
- Backend: `8081`
- ML service: `8000`

## Repo Layout

```text
frontend/              Angular 19 chat UI
backend/recapify/      Spring Boot 4 / Java 21 API boundary
ml/                    FastAPI ML service
ml/app/                ML source code
openspec/              Planned changes, specs, tasks, archives
docker-compose.yml     Dev and prod container profiles
```

## Planning

Use OpenSpec as the source of truth for planned work and archived decisions.

- Explore scope with `openspec-explore`.
- Create change artifacts with `openspec-propose`.
- Review `tasks.md` with the user before running `openspec-apply-change`.
- Implement from `tasks.md` with `openspec-apply-change`.
- When asked, commit on a feature branch named after the change, push, and open a PR with `gh pr create`. Use the proposal headline as the PR title and a short summary from `proposal.md` as the body.
- Archive with `openspec-archive-change` after the PR is merged.

To address PR review feedback, fetch comments with `gh pr view <number> --comments` and push fixes as follow-up commits on the same branch.

Do not maintain `.agents/ROADMAP.md`, `.agents/PLAN.md`, or `.agents/STATUS.md`.

## Worktrees

Application implementation work should happen in a sibling worktree on a feature branch, not directly in the main checkout.

Planning-only OpenSpec artifact work may happen in the current checkout unless the user asks for a separate worktree.

Before editing, check branch and working-tree status. Do not overwrite, revert, clean, or delete unrelated local changes.

## Verification

For app-code changes, inspect logs for the changed service:

```bash
docker logs --tail 200 recapify-frontend-dev
docker logs --tail 200 recapify-backend-dev
docker logs --tail 200 recapify-ml-dev
```

Use the relevant service log only. If a change touches multiple services, inspect each relevant service.

For docs or planning-only changes, runtime verification is not required. For test-only changes, run the targeted test when practical.

Do not combine verification commands with shell separators, pipes, loops, redirection, or command substitution.

## Secrets And Logging

Never commit `.env` files or real credentials.

Do not log API keys, tokens, raw credentials, or user PII. If you need to confirm a key is loaded, log a boolean such as `keyPresent=true`, never the value.

## Off-Limits Without Explicit Approval

Do not modify these unless the maintainer explicitly asks:

- `pom.xml`
- `frontend/package.json`
- `ml/requirements.txt`
- `frontend/set-env.js`

If a Python package is installed, removed, or updated during work, ask before changing `ml/requirements.txt`.

## Contract Notes

Both backend and ML expose `/api/v1/...`. Keep that prefix when adding endpoints.

The frontend builds request URLs by concatenating `environment.apiUrl` with `api/v1/...`. Preserve `frontend/set-env.js` trailing-slash behavior.

The backend reads `LLM_SERVICE_BASEURL` for the ML service URL and defaults to `http://localhost:8000`.

Changing Gemini model names or structured-output wiring is a code change in `ml/app/main.py`, not a config-only change.

## Coding Guidance

Keep changes scoped to the requested behavior. Do not refactor unrelated code, rename files, change dependencies, or reformat broad areas.

Frontend components are standalone Angular components using Signals. Keep component files colocated under `frontend/src/app/components/<name>/`.

Backend controllers should stay thin. Use `WebClient` for outbound HTTP.

ML changes should move toward clearer separation of routes, workflow orchestration, provider/client code, subtitle handling, cache, and models.

Keep tests close to the code they cover and scale test coverage with the risk of the change.

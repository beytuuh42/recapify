## 1. Production Images

- [x] 1.1 Implement `backend/recapify/Dockerfile` as a multi-stage production build that packages the Spring Boot app and runs it on a Java 21 runtime image.
- [x] 1.2 Implement `ml/Dockerfile` as a production FastAPI image that installs `requirements.txt` and starts the app on `0.0.0.0:8000` without reload mode.
- [x] 1.3 Build backend and ML production images locally to confirm Dockerfiles copy the required files and start with the expected commands.

## 2. Production Compose Topology

- [x] 2.1 Extend `docker-compose.yml` `prod` profile with `backend-prod` and `ml-prod` services.
- [x] 2.2 Configure `backend-prod` with `LLM_SERVICE_BASEURL=http://ml-prod:8000`.
- [x] 2.3 Configure `ml-prod` to read runtime secrets from an untracked production env file or documented environment variables.
- [x] 2.4 Ensure only `frontend-prod` publishes a host port by default and backend/ML remain internal to the Compose network.
- [x] 2.5 Decide whether to mount a named Docker volume for `ml/app/.cache`, then implement and document the chosen cache behavior.

## 3. Frontend API Routing

- [x] 3.1 Configure production frontend builds to use same-origin API access, such as `API_URL=/`.
- [x] 3.2 Update `frontend/nginx.conf` so `/api/v1/` requests proxy to `backend-prod:8080`.
- [x] 3.3 Preserve Angular static asset caching and client-side routing fallback for non-API paths.
- [x] 3.4 Verify Nginx passes useful proxy headers such as `Host`, `X-Real-IP`, `X-Forwarded-For`, and `X-Forwarded-Proto`.

## 4. Health And Runtime Configuration

- [x] 4.1 Add a lightweight backend health endpoint that does not call ML or external services.
- [x] 4.2 Add a lightweight ML health endpoint that does not call Gemini, OpenSubtitles, or LangSmith.
- [x] 4.3 Add production Docker healthchecks for frontend, backend, and ML services.
- [x] 4.4 Update secret hygiene so real local and production env files are ignored while example env files remain committed.
- [x] 4.5 Review backend CORS behavior after same-origin proxying and keep production exposure minimal.

## 5. Deployment Documentation

- [x] 5.1 Document the EC2 production deployment workflow, including prerequisites, env file setup, build/start commands, and smoke checks.
- [x] 5.2 Document which EC2 security group ports should be public and which services stay internal.
- [x] 5.3 Document frontend build-time environment behavior and how `API_URL=/` works with the Nginx proxy.
- [x] 5.4 Document log inspection and rollback commands for the production Compose stack.
- [x] 5.5 Note TLS as an expected production hardening step if it is not implemented in this change.

## 6. Verification

- [x] 6.1 Run the production Compose build for all services.
- [x] 6.2 Start the production Compose stack and verify containers become healthy.
- [x] 6.3 Smoke test frontend root, an Angular deep route, backend health through `/api/v1/health`, and ML health through the backend or internal container network as appropriate.
- [x] 6.4 Inspect relevant production service logs after startup and smoke tests.
- [x] 6.5 Run `openspec status --change "add-ec2-production-deployment"` and confirm the change is apply-ready.

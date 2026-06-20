## Context

Recapify currently has a complete Docker Compose development topology, but the production profile only builds and runs the Angular frontend. The frontend production image serves static files through Nginx, while the backend and ML production Dockerfiles are empty.

The existing frontend build writes `src/environments/environment.ts` from `frontend/set-env.js`, so production API configuration is baked into the Angular bundle at image build time. The backend currently allows CORS for `http://localhost:*` and reads `LLM_SERVICE_BASEURL` for the ML service URL. The ML service reads secrets from environment variables, loads `.env` during local startup, and stores summary cache files under `ml/app/.cache`.

The intended EC2 deployment is a single Docker-enabled instance running all three services with Docker Compose.

## Goals / Non-Goals

**Goals:**

- Provide production Dockerfiles for backend and ML services.
- Run all three services under the Compose `prod` profile.
- Publish only the frontend/Nginx service from EC2 and keep backend and ML reachable only on the Compose network.
- Route browser API requests through same-origin frontend Nginx proxying to the backend.
- Keep production secrets out of images and source control.
- Provide health checks and deployment documentation suitable for manual EC2 operation.

**Non-Goals:**

- Provision EC2 infrastructure, DNS, TLS certificates, or AWS resources through Terraform/CDK.
- Add CI/CD publishing to a registry.
- Add authentication, rate limiting, or user accounts.
- Replace the local ML cache with a managed database or external storage.
- Change Gemini model selection or ML summarization behavior.

## Decisions

### Use frontend Nginx as the public reverse proxy

Production browser traffic will enter through the frontend container. Static Angular assets will be served directly, and `/api/v1/*` requests will be proxied to `http://backend-prod:8080` over the Compose network.

Rationale:

- Keeps only one public service/port exposed on EC2.
- Avoids exposing the Spring Boot backend directly to the internet.
- Lets the frontend use same-origin API URLs such as `/api/v1/...`, minimizing CORS configuration.
- Fits the existing frontend production image, which already uses Nginx.

Alternative considered: expose backend on a separate public port and configure `API_URL` to `http://<ec2-host>:8081/`. This is simpler to implement but leaks deployment topology to the browser, requires broader CORS configuration, and exposes an unnecessary public surface.

### Keep `set-env.js` initially, but configure production API as same-origin

The frontend production build will continue using `set-env.js`, but EC2 production should build with `API_URL=/` or an equivalent same-origin base URL. The Angular code can continue concatenating `environment.apiUrl` with `api/v1/...`.

Rationale:

- Avoids broad frontend rewiring for the first production deployment.
- Keeps the current build model intact.
- Works cleanly with the Nginx proxy decision.

Alternative considered: runtime config via `assets/config.json` or `env.js` generated when the frontend container starts. This is more flexible for multi-environment immutable images, but it adds frontend bootstrapping complexity that is not needed for a single EC2 deployment.

### Build backend and ML production images as minimal runtime images

The backend Dockerfile should use a build stage to produce the Spring Boot jar and a Java 21 runtime stage to run it. The ML Dockerfile should install requirements into a Python slim image and run the FastAPI app with a production Uvicorn command bound to `0.0.0.0:8000`.

Rationale:

- Keeps build tools out of runtime images where practical.
- Matches existing service technology without new dependencies.
- Supports reproducible `docker compose --profile prod build` on EC2.

Alternative considered: run the development Dockerfiles in production. This would ship reload tooling and development commands into production, increasing startup cost and operational risk.

### Use environment files for runtime secrets, not baked image values

Production secrets for Gemini, OpenSubtitles, and LangSmith will be provided through environment variables or an untracked production env file on EC2. Examples may be committed, but real `.env` files must be ignored.

Rationale:

- Prevents secrets from being embedded into Docker images or committed to the repository.
- Fits the current ML service configuration, which already reads environment variables.
- Keeps manual EC2 deployment simple.

Alternative considered: AWS Secrets Manager or SSM Parameter Store. Those are better for mature AWS operations, but they add AWS-specific integration and IAM setup that is beyond this initial Compose deployment.

### Add lightweight application health endpoints

Backend and ML should expose lightweight health endpoints that do not call Gemini, OpenSubtitles, or other external dependencies. Compose healthchecks can use these endpoints to verify the process is accepting HTTP requests.

Rationale:

- Avoids spending API quota or leaking dependency outages into basic container liveness checks.
- Provides a stable operational check for EC2.

Alternative considered: rely only on container process status. That misses cases where the HTTP process is running but not serving requests correctly.

## Risks / Trade-offs

- Public Nginx proxy misconfiguration could break Angular client-side routing or API routing -> Add explicit tests/manual checks for `/`, deep Angular routes, and `/api/v1/health`.
- Build-time frontend env remains less flexible than runtime env -> Accept for single EC2 deployment and document that changing the public API base requires rebuilding the frontend image.
- ML cache inside the container filesystem will not survive container recreation unless a volume is configured -> Decide during implementation whether to mount a named volume for `ml/app/.cache`; document behavior either way.
- EC2 without TLS exposes traffic over HTTP -> Document that production internet use should place TLS in front of the frontend service, either with host-level reverse proxy, ALB, or a future Compose TLS proxy.
- Free-tier EC2 resource limits may make building all images on-instance slow -> Keep images reasonably small and document local build/push as a possible future optimization.

## Migration Plan

1. Add production Dockerfiles for backend and ML.
2. Update the production Compose profile to include frontend, backend, and ML services on the internal Compose network.
3. Update frontend Nginx to proxy `/api/v1/*` to backend while preserving Angular route fallback for all other paths.
4. Add lightweight health endpoints and Compose healthchecks.
5. Add example production env documentation and ignore real env files.
6. Verify local production profile builds and starts.
7. Deploy on EC2 with the required env file and run documented smoke checks.

Rollback strategy: stop the new production Compose stack and redeploy the previous frontend-only production service. Since this change does not require data migration, rollback is container-level.

## Open Questions

- Should the initial EC2 setup include a named Docker volume for the ML summary cache, or is ephemeral cache acceptable for the first deployment?
- Will TLS terminate directly on the EC2 host, through an AWS load balancer, or remain out of scope until after the first working deployment?

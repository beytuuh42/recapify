# EC2 Production Deployment

This deployment runs Recapify as three Docker Compose services on one Docker-enabled EC2 instance:

```text
Browser -> frontend-prod Nginx -> backend-prod -> ml-prod -> OpenSubtitles + Gemini
```

Only `frontend-prod` publishes a host port. Backend and ML containers stay private on the Compose network.

## Prerequisites

- EC2 instance with Docker and Docker Compose installed
- Repository checkout on the instance
- Google Gemini API key
- OpenSubtitles API key, username, and password
- LangSmith API key and endpoint

## Secrets

Create the production ML env file on the EC2 instance:

```bash
cp ml/.env.prod.example ml/.env.prod
```

Fill in real values:

```text
GOOGLE_API_KEY=...
OPEN_SUBTITLES_API_KEY=...
OPEN_SUBTITLES_USER=...
OPEN_SUBTITLES_PASSWORD=...
LANGSMITH_API_KEY=...
LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
LANGSMITH_TRACING=true
```

Do not commit `ml/.env.prod`. Real env files are ignored by Git.

## Network Exposure

Open only the frontend port in the EC2 security group.

| Service | Container | Host exposure |
|---|---|---|
| Frontend/Nginx | `frontend-prod:8080` | Public, default `4200`, use `80` on EC2 |
| Backend | `backend-prod:8080` | Internal only |
| ML | `ml-prod:8000` | Internal only |

For EC2 HTTP on port 80, set:

```bash
export FRONTEND_PROD_PORT=80
```

If you terminate TLS outside Compose, keep `FRONTEND_PROD_PORT` aligned with that reverse proxy or load balancer.

## Frontend API Configuration

Production frontend builds use `frontend/set-env.js` at image build time. The Compose production profile passes:

```text
FRONTEND_API_URL=/
```

That makes browser requests same-origin:

```text
/api/v1/llm/summary
```

The frontend Nginx container proxies `/api/v1/` to:

```text
http://backend-prod:8080
```

Nginx removes the browser `Origin` header before forwarding API requests to the private backend. The browser still sees same-origin responses from the frontend host, and the backend does not need to allow public origins for this internal proxy hop.

Changing `FRONTEND_API_URL`, Sentry DSN, or Sentry environment requires rebuilding the frontend image.

## Build And Start

Build all production images:

```bash
docker compose --profile prod build
```

Start the production stack:

```bash
docker compose --profile prod up -d
```

Check container status:

```bash
docker compose --profile prod ps
```

## Smoke Checks

From the EC2 host:

```bash
curl -f http://127.0.0.1:${FRONTEND_PROD_PORT:-4200}/
```

Check the backend health endpoint through the public frontend proxy:

```bash
curl -f http://127.0.0.1:${FRONTEND_PROD_PORT:-4200}/api/v1/health
```

Check ML health from inside the Docker network:

```bash
docker exec recapify-ml-prod python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=2).read()"
```

The health endpoints are lightweight process checks. They do not call Gemini, OpenSubtitles, or LangSmith.

## Logs

Inspect the relevant production service log:

```bash
docker logs --tail 200 recapify-frontend-prod
docker logs --tail 200 recapify-backend-prod
docker logs --tail 200 recapify-ml-prod
```

Requests through the backend propagate `X-Request-Id` to the ML service for cross-service log correlation.

## Cache Persistence

The production Compose profile mounts a named Docker volume at:

```text
/app/app/.cache
```

This preserves generated ML summary cache files across container recreation. Remove the cache only when you intentionally want to discard cached summaries:

```bash
docker volume rm <compose-project>_ml-cache
```

The exact volume name can include the Compose project name. Confirm it with:

```bash
docker volume ls
```

## Rollback

Stop the production stack:

```bash
docker compose --profile prod down
```

Then check out the previous known-good revision and start it again. This deployment does not perform a database migration.

## TLS

This Compose profile serves plain HTTP. For internet-facing production use, terminate TLS with an EC2 host reverse proxy, an AWS load balancer, or a future Compose-managed TLS proxy.

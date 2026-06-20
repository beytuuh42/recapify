## Why

Recapify can run all services in Docker for local development, but production deployment is incomplete: only the frontend has a production image and the production Compose profile does not run the backend or ML service. The project needs a repeatable EC2 deployment path that keeps backend services private, handles secrets safely, and avoids brittle frontend API configuration.

## What Changes

- Add production Docker images for the Spring Boot backend and FastAPI ML service.
- Extend the production Docker Compose profile so EC2 can run frontend, backend, and ML together.
- Serve the Angular app through the frontend Nginx container and proxy `/api/v1/*` requests to the backend over the internal Docker network.
- Configure production frontend API access as same-origin so the public browser does not need to know the backend container URL.
- Add production-ready service health endpoints or healthchecks for frontend, backend, and ML containers.
- Document EC2 deployment steps, required environment variables, secret handling, and operational verification commands.
- Harden environment-file hygiene so real production secrets are not committed.

## Capabilities

### New Capabilities

- `ec2-production-deployment`: Covers production container images, Compose topology, frontend API routing, environment configuration, health checks, and EC2 deployment documentation for running Recapify on a single Docker-enabled EC2 instance.

### Modified Capabilities

- None.

## Impact

- Affected services: `frontend`, `backend/recapify`, `ml`.
- Affected deployment files: `docker-compose.yml`, service Dockerfiles, frontend Nginx config, environment examples, `.gitignore`, and README or dedicated deployment docs.
- Affected runtime behavior: public traffic should enter through the frontend/Nginx container; backend and ML should communicate internally on the Compose network.
- No dependency changes are expected unless implementation discovers a missing production runtime package.

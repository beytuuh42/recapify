# Spec: ec2-production-deployment

## Purpose

Defines the production deployment contract for running Recapify on a single Docker-enabled EC2 instance, including production images, Compose topology, same-origin frontend API routing, runtime environment handling, health checks, and operator documentation.

## Requirements

### Requirement: Production Compose Runs All Services
The system SHALL provide a production Docker Compose profile that builds and runs the frontend, backend, and ML services on a single Docker-enabled host.

#### Scenario: Production profile starts complete stack
- **WHEN** an operator runs the documented production Compose command
- **THEN** Compose starts frontend, backend, and ML production containers

#### Scenario: Backend reaches ML internally
- **WHEN** the backend container requests the configured ML service base URL
- **THEN** it uses the ML container hostname on the Compose network rather than a public host port

### Requirement: Backend Production Image
The system SHALL provide a backend production Dockerfile that builds the Spring Boot application and runs the packaged application with a Java 21 runtime.

#### Scenario: Backend image starts HTTP server
- **WHEN** the backend production image is built and started
- **THEN** the Spring Boot application listens on its internal HTTP port

#### Scenario: Backend image excludes development server command
- **WHEN** the backend production container starts
- **THEN** it runs the packaged application rather than `spring-boot:run`

### Requirement: ML Production Image
The system SHALL provide an ML production Dockerfile that installs Python dependencies and runs the FastAPI application on `0.0.0.0:8000`.

#### Scenario: ML image starts HTTP server
- **WHEN** the ML production image is built and started with required environment variables
- **THEN** the FastAPI application listens on port `8000` inside the container

#### Scenario: ML image uses production command
- **WHEN** the ML production container starts
- **THEN** it runs a non-reload production server command rather than the development server command

### Requirement: Same-Origin Frontend API Routing
The system SHALL route production browser API requests through the frontend Nginx service using the same origin as the Angular application.

#### Scenario: Browser calls same-origin API
- **WHEN** the production Angular app sends a request for an `api/v1` endpoint
- **THEN** the request targets the same origin that served the frontend

#### Scenario: Nginx proxies API requests to backend
- **WHEN** frontend Nginx receives a request under `/api/v1/`
- **THEN** it forwards the request to the backend production container over the Compose network

#### Scenario: Angular routes remain available
- **WHEN** frontend Nginx receives a non-API path that does not match a static asset
- **THEN** it serves the Angular app shell for client-side routing

### Requirement: Backend And ML Stay Private
The system SHALL keep backend and ML production services off public host ports by default.

#### Scenario: Only frontend is published
- **WHEN** the production Compose profile is inspected
- **THEN** only the frontend service exposes a host port for public HTTP traffic

#### Scenario: Internal services remain addressable
- **WHEN** frontend or backend containers communicate with dependent services
- **THEN** they use Compose service names on the internal Docker network

### Requirement: Production Environment Handling
The system SHALL document and support production configuration through environment variables or untracked environment files without committing real secrets.

#### Scenario: Required secrets are externalized
- **WHEN** the ML production service starts
- **THEN** Gemini, OpenSubtitles, and LangSmith settings are read from runtime environment configuration rather than hard-coded image values

#### Scenario: Real env files are ignored
- **WHEN** a developer creates local or production `.env` files for ML secrets
- **THEN** Git does not track those real secret files

#### Scenario: Example env file remains available
- **WHEN** an operator prepares EC2 deployment
- **THEN** the repository provides a committed example listing required variable names without real credentials

### Requirement: Production Health Checks
The system SHALL provide lightweight health checks for production containers without calling paid or external provider APIs.

#### Scenario: Backend health check succeeds
- **WHEN** the backend health endpoint is requested
- **THEN** it returns a successful response without calling the ML service or external APIs

#### Scenario: ML health check succeeds
- **WHEN** the ML health endpoint is requested
- **THEN** it returns a successful response without calling Gemini, OpenSubtitles, or LangSmith

#### Scenario: Compose reports service health
- **WHEN** the production stack is running
- **THEN** Docker health status is available for frontend, backend, and ML containers

### Requirement: EC2 Deployment Documentation
The system SHALL document the manual EC2 deployment workflow for a Docker-and-Compose host.

#### Scenario: Operator deploys from documentation
- **WHEN** an operator follows the deployment documentation on a prepared EC2 instance
- **THEN** they can build, configure, start, verify, and inspect logs for the production stack

#### Scenario: Documentation describes network exposure
- **WHEN** an operator reviews the deployment documentation
- **THEN** it identifies which host ports should be opened publicly and which services remain internal

#### Scenario: Documentation describes frontend configuration
- **WHEN** an operator reviews the deployment documentation
- **THEN** it explains the production frontend API base URL and the implication of build-time frontend environment generation

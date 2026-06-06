## Why

`LlmService` currently acts as both the workflow orchestrator and the outbound ML HTTP client, and the `llm/` package is flat — DTOs, controller, service, and client concerns all coexist at the same level. Separating these layers makes the Spring Boot boundary easier to read and reason about without changing any external behavior.

## What Changes

- Extract a dedicated `MlServiceClient` that owns all outbound WebClient calls to the ML service (intent and summarize endpoints).
- Reduce `LlmService` to workflow orchestration only: call the client, coordinate results, return to the controller.
- Move DTOs (`SummaryRequest`, `SummaryResponse`, `Chunk`, `IntentRequest`) into a `dto/` sub-package.
- Move `MlServiceClient` into a `client/` sub-package.
- No changes to the public-facing API (`POST /api/v1/llm/summary`), request/response contracts, or logging behavior.

## Capabilities

### New Capabilities

- `backend-summary-boundary`: The Spring Boot `llm/` package separates controller, orchestration service, outbound ML client, and DTOs into distinct layers with clear responsibilities.

### Modified Capabilities

- None.

## Impact

- `backend/recapify/src/main/java/com/recapify/llm/` — restructured into sub-packages (`client/`, `dto/`)
- `LlmService.java` — slimmed to orchestration; outbound HTTP calls move to `MlServiceClient`
- `LlmController.java` — unchanged behavior, may need import updates
- `WebClientConfig.java` — unchanged
- No frontend changes
- No ML service changes
- No API contract changes

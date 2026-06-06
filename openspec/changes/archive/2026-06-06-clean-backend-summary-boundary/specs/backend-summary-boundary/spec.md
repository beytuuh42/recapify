## ADDED Requirements

### Requirement: ML client calls are isolated in a dedicated class
The Spring Boot `llm/` package SHALL contain a `MlServiceClient` class in the `client/` sub-package that is the sole owner of outbound WebClient HTTP calls to the ML service.

#### Scenario: Intent is extracted via the ML client
- **WHEN** the backend needs to extract intent from a user message
- **THEN** `MlServiceClient.extractIntent(String text)` is called to make the outbound HTTP POST to `/api/v1/intent`
- **AND** `LlmService` does not directly use `WebClient`

#### Scenario: Summary is fetched via the ML client
- **WHEN** the backend needs a full episode summary from the ML service
- **THEN** `MlServiceClient.fetchSummary(SummaryRequest req)` is called to make the outbound HTTP POST to `/api/v1/summarize`
- **AND** `LlmService` does not directly use `WebClient`

### Requirement: LlmService is limited to workflow orchestration
`LlmService` SHALL coordinate the summary workflow by calling `MlServiceClient` and returning results to the controller, without containing any WebClient or HTTP transport logic.

#### Scenario: Summary workflow is orchestrated
- **WHEN** `LlmService.getSummary(String text)` is called
- **THEN** it calls `MlServiceClient.extractIntent` to get a `SummaryRequest`
- **AND** calls `MlServiceClient.fetchSummary` with that request
- **AND** returns the `SummaryResponse` to the controller

### Requirement: DTOs are grouped in a sub-package
All data transfer objects for the LLM boundary (`SummaryRequest`, `SummaryResponse`, `Chunk`, `IntentRequest`) SHALL reside in the `com.recapify.llm.dto` sub-package.

#### Scenario: DTO classes are located in dto sub-package
- **WHEN** a developer inspects the `llm/` package
- **THEN** `SummaryRequest`, `SummaryResponse`, `Chunk`, and `IntentRequest` are found under `llm/dto/`
- **AND** no DTO records remain at the top-level `llm/` package

### Requirement: Public API behavior is unchanged
The refactoring SHALL not alter the behavior of `POST /api/v1/llm/summary`, including request shape, response shape, logging output, request ID propagation, or error handling.

#### Scenario: Summary endpoint responds identically before and after refactor
- **WHEN** a valid summary request is submitted to `POST /api/v1/llm/summary`
- **THEN** the response contains the same `SummaryResponse` fields as before the refactor
- **AND** request ID is propagated to the ML service via the `X-Request-Id` header

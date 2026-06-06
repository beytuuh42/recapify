## Context

The Spring Boot `llm/` package currently has a flat structure: controller, service, and four DTO records sit together with no sub-packaging. `LlmService` handles two distinct concerns — outbound WebClient HTTP calls to the ML service and workflow orchestration (intent → summarize). This makes the package harder to read and harder to test either layer in isolation. The change is purely internal; no external API, contract, or logging behavior changes.

Current layout:
```
llm/
  LlmController.java     controller
  LlmService.java        orchestration + ML HTTP client mixed
  SummaryRequest.java    DTO
  SummaryResponse.java   DTO
  Chunk.java             DTO
  IntentRequest.java     DTO
```

Target layout:
```
llm/
  LlmController.java         controller (unchanged)
  LlmService.java            orchestration only
  client/
    MlServiceClient.java     outbound WebClient calls
  dto/
    SummaryRequest.java
    SummaryResponse.java
    Chunk.java
    IntentRequest.java
```

## Goals / Non-Goals

**Goals:**
- Separate outbound ML HTTP calls into `MlServiceClient`
- Reduce `LlmService` to pure orchestration: call client, return result
- Group DTOs under `dto/` sub-package
- Keep all existing logging, request ID propagation, and error behavior intact

**Non-Goals:**
- Changing `POST /api/v1/llm/summary` request/response shape
- Adding new endpoints or workflow steps
- Introducing mocks or new test infrastructure
- Touching frontend, ML service, or `WebClientConfig`

## Decisions

### Split `LlmService` into service + client

`MlServiceClient` owns the `WebClient` injection and all `.post()` calls. It exposes two methods matching the current private behavior: `extractIntent(String text)` and `fetchSummary(SummaryRequest req)`. `LlmService` calls these and owns the orchestration (get intent, then get summary).

**Why**: Single responsibility. The ML HTTP surface is a stable, testable unit. Orchestration logic can evolve without touching HTTP code.

**Alternative considered**: Keep everything in `LlmService` but split into private methods. Rejected — private methods don't enforce the boundary or enable independent testing.

### Move DTOs to `dto/` sub-package

All four records (`SummaryRequest`, `SummaryResponse`, `Chunk`, `IntentRequest`) move to `com.recapify.llm.dto`. No field, accessor, or annotation changes.

**Why**: Keeps the top-level `llm/` package focused on behavioral classes. DTOs are stable and numerous enough to warrant grouping.

### Keep `WebClientConfig` unchanged

`WebClientConfig` is not in the `llm/` package and is not touched. `MlServiceClient` receives the configured `WebClient` bean by constructor injection exactly as `LlmService` does today.

## Risks / Trade-offs

- Package refactors in Java require import updates across all references. Risk is low here — the only consumers of `llm/` classes are within the same package and `WebClientConfig`. → Run `./mvnw compile` to catch any missed imports before committing.
- No behavior change means no new test coverage needed. If existing tests reference moved DTOs, imports update but logic stays identical.

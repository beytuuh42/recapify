## Context

The Spring Boot backend DTOs were originally written to mirror the Python/JSON snake_case field names 1:1 (`final_summary`, `key_events`, `chunk_summaries`, `media_type`). This is non-idiomatic Java — records should use camelCase. Jackson's `@JsonProperty` allows the Java fields to be camelCase while keeping the JSON wire format snake_case, so no contract change is needed. On the error side, `MlServiceClient` currently lets WebClient exceptions propagate untyped; the frontend receives a 500 from Spring Boot whenever the ML service is down or returns 404, and shows a hardcoded error string that doesn't tell the user what happened. The `isBusy` flag is cleared the moment the HTTP response arrives, meaning a user can type a new request while the previous summary is still animating — which will add a new message to the list while the animation timers from the previous message are still running.

## Goals / Non-Goals

**Goals:**
- Camelcase all Java DTO fields; preserve JSON wire format with `@JsonProperty`.
- `MlServiceClient` throws `ContentUnavailableException` on ML 404 and `MlServiceUnavailableException` on ML 503.
- `@ControllerAdvice` maps those exceptions to HTTP responses with `{ "error": "...", "message": "..." }` bodies.
- Frontend displays the `message` field from the error body.
- `isBusy` cleared only after animation completes.
- Remove dead `SummaryRequest` interface.

**Non-Goals:**
- No changes to the ML service (covered by `polish-ml-service`).
- No changes to the happy-path `POST /api/v1/llm/summary` response shape.
- No interactive intent-confirmation UI (tracked as a separate GitHub issue).
- No frontend model changes to accommodate the camelCase backend fields — the JSON wire format stays snake_case via `@JsonProperty`, so the frontend model is unaffected.

## Decisions

### @JsonProperty approach for DTO fields

Java record fields become camelCase (`finalSummary`, `keyEvents`, `chunkSummaries`, `mediaType`). Jackson's `@JsonProperty("final_summary")` on the record component preserves the wire name. Spring Boot's Jackson integration respects these annotations automatically with no configuration change.

**Alternative considered**: Configure a global `SNAKE_CASE` naming strategy on the ObjectMapper. Rejected — it would affect all Jackson serialization in the app, not just these DTOs, and is harder to reason about when reading individual files.

### Exception hierarchy in the backend

Two typed exceptions cover the known ML failure modes:

```
ContentUnavailableException    (maps ML 404 subtitle_not_found)
  → HTTP 404 to frontend
  → message: "We couldn't find content for {title} Season {season} Episode {episode}.
              Did we understand your request correctly?"

MlServiceUnavailableException  (maps ML 503)
  → HTTP 503 to frontend
  → message: "Something went wrong while generating the summary. Please try again."
```

Both are unchecked exceptions. `MlServiceClient` reads the ML error body, constructs the appropriate exception, and throws it. `@ControllerAdvice` in a new `GlobalExceptionHandler` class handles both.

### isBusy animation gate

`EpisodeSummaryComponent` already has a well-defined end point: the `revealScenes` interval's last tick (or `revealCharacters` if there are no scenes). Adding `@Output() animationComplete = new EventEmitter<void>()` and emitting there gives the parent chain a clean signal. `MessageBubbleComponent` passes the event through with its own `@Output()`. `ChatInputComponent` subscribes to it and calls `chatService.setBusy(false)` on emission.

**Alternative considered**: Use a shared signal in `ChatService` for animation state. Rejected — the animation lifecycle belongs to `EpisodeSummaryComponent`, not the service layer. An event output keeps the concern local.

## Risks / Trade-offs

- [Risk] The `@JsonProperty` annotations require adding Lombok or Jackson annotations to records. Spring Boot's Jackson integration already handles `@JsonProperty` on record components; no additional dependency needed.
- [Risk] `MlServiceClient` currently uses `.block()` which throws `WebClientResponseException` on non-2xx. Reading the error body requires `.onStatus()` or `.bodyToMono(String.class)` on the error path. This adds a few lines but is standard WebClient usage.
- [Risk] If the ML service error body format changes, `MlServiceClient`'s error parsing breaks silently. → Mitigation: parse defensively; fall back to `MlServiceUnavailableException` if the body can't be parsed.

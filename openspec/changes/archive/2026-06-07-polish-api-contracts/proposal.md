## Why

Three visible code quality issues remain across the Spring Boot backend and Angular frontend: Java record fields use snake_case (non-idiomatic in Java), errors from the ML service propagate to the browser as opaque 500s without user-readable messages, and the chat UI unblocks user input as soon as the HTTP response arrives rather than waiting for the summary animation to complete.

## What Changes

- Rename snake_case fields in Java DTOs to camelCase and add `@JsonProperty` annotations to preserve the JSON wire format.
- Add a Spring Boot `@ControllerAdvice` exception mapper that translates `ContentUnavailableException` and `MlServiceUnavailableException` into structured HTTP responses with user-readable messages.
- Update `MlServiceClient` to detect ML service 4xx/5xx responses and throw typed Java exceptions instead of propagating raw WebClient errors.
- Remove the dead `SummaryRequest` interface from the Angular model file (defined but never used).
- Fix the `isBusy` flag: emit an `animationComplete` event from `EpisodeSummaryComponent` at the end of the reveal sequence; bubble through `MessageBubbleComponent`; `ChatInputComponent` clears `isBusy` on that event rather than immediately after receiving the HTTP response.
- Update the frontend error handler to display the `message` field from the backend error response body instead of a hardcoded string.

## Capabilities

### New Capabilities

- `backend-error-responses`: The Spring Boot backend returns structured, user-readable error responses for known ML service failures (subtitle not found, service unavailable) rather than propagating raw exceptions.
- `frontend-animation-gate`: The chat input is locked until the summary reveal animation completes, preventing concurrent submissions during rendering.

### Modified Capabilities

<!-- None. The JSON wire format is preserved via @JsonProperty; observable API behavior is unchanged. -->

## Impact

- `backend/recapify/.../llm/dto/SummaryResponse.java` — field renames + `@JsonProperty`
- `backend/recapify/.../llm/dto/SummaryRequest.java` — field rename (`media_type` → `mediaType`) + `@JsonProperty`
- `backend/recapify/.../llm/dto/Chunk.java` — field renames + `@JsonProperty` if needed
- `backend/recapify/.../llm/client/MlServiceClient.java` — detect 4xx/5xx, throw typed exceptions
- `backend/recapify/.../llm/LlmController.java` or new `GlobalExceptionHandler.java` — `@ControllerAdvice`
- `backend/recapify/...` tests — update for renamed fields
- `frontend/src/app/models/summary.model.ts` — remove dead `SummaryRequest` interface
- `frontend/src/app/components/episode-summary/episode-summary.component.ts` — emit `animationComplete`
- `frontend/src/app/components/message-bubble/message-bubble.component.ts` — pass through event
- `frontend/src/app/components/chat-input/chat-input.component.ts` — clear `isBusy` on event
- `frontend/src/app/components/chat-input/chat-input.component.ts` — use error `message` from response body

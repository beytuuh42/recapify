## 1. Rename Java DTO fields to camelCase

- [x] 1.1 In `SummaryResponse.java`: rename `final_summary` → `finalSummary`, `key_events` → `keyEvents`, `chunk_summaries` → `chunkSummaries`; add `@JsonProperty("final_summary")` etc. to each record component
- [x] 1.2 In `SummaryRequest.java`: rename `media_type` → `mediaType`; add `@JsonProperty("media_type")`
- [x] 1.3 In `Chunk.java`: audit field names and rename any snake_case fields to camelCase with `@JsonProperty`
- [x] 1.4 Update all usages of old field names in `LlmService.java`, `MlServiceClient.java`, `LlmController.java` and their test files

## 2. Add typed backend exceptions

- [x] 2.1 Create `ContentUnavailableException` (unchecked) with fields `title`, `season`, `episode`, `language` in the `llm` package
- [x] 2.2 Create `MlServiceUnavailableException` (unchecked) in the `llm` package

## 3. Update MlServiceClient to throw typed exceptions

- [x] 3.1 In `MlServiceClient.fetchSummary`, add `.onStatus()` handling for 4xx responses: parse the ML error body (best-effort); if `code == "subtitle_not_found"`, throw `ContentUnavailableException`; otherwise throw `MlServiceUnavailableException`
- [x] 3.2 In `MlServiceClient.fetchSummary`, add `.onStatus()` handling for 5xx responses: throw `MlServiceUnavailableException`
- [x] 3.3 Update `MlServiceClientTest` to cover the ML 404 → `ContentUnavailableException` and ML 503 → `MlServiceUnavailableException` paths

## 4. Add @ControllerAdvice exception handler

- [x] 4.1 Create `GlobalExceptionHandler.java` with `@ControllerAdvice` and `@RestControllerAdvice`
- [x] 4.2 Add `@ExceptionHandler(ContentUnavailableException.class)` method returning HTTP 404 with body `{"error": "content_unavailable", "message": "We couldn't find content for {title} Season {season} Episode {episode}. Did we understand your request correctly?"}`
- [x] 4.3 Add `@ExceptionHandler(MlServiceUnavailableException.class)` method returning HTTP 503 with body `{"error": "service_unavailable", "message": "Something went wrong while generating the summary. Please try again."}`
- [x] 4.4 Add unit tests for `GlobalExceptionHandler` covering both exception types

## 5. Frontend: remove dead code and display error messages

- [x] 5.1 Remove the `SummaryRequest` interface from `frontend/src/app/models/summary.model.ts`
- [x] 5.2 In `ChatInputComponent.send()` error handler: read `err.error?.message` from the response body; fall back to `"Something went wrong. Please try again."` if absent
- [x] 5.3 Add an `ErrorResponse` interface to `summary.model.ts` with `error: string` and `message: string` fields

## 6. Frontend: animation gate for isBusy

- [x] 6.1 In `EpisodeSummaryComponent`: add `@Output() animationComplete = new EventEmitter<void>()`
- [x] 6.2 Emit `animationComplete` at the end of the last reveal phase: in `revealScenes` after the final interval tick, or in `revealCharacters` if `chunk_summaries` is empty, or in `revealKeyEvents` if both characters and scenes are empty
- [x] 6.3 In `MessageBubbleComponent`: add `@Output() animationComplete = new EventEmitter<void>()`; bind it to `EpisodeSummaryComponent`'s `animationComplete` output in the template
- [x] 6.4 In `ChatWindowComponent` or `ChatInputComponent`: bind to `MessageBubbleComponent`'s `animationComplete` output and call `chatService.setBusy(false)` on emission
- [x] 6.5 Remove the `chatService.setBusy(false)` call from `ChatInputComponent.showSummary()` (it will now be called via the event)
- [x] 6.6 Update `EpisodeSummaryComponent` spec to verify `animationComplete` is emitted after all reveal phases

## 7. Verify

- [x] 7.1 Run `./mvnw test` from `backend/recapify/` and confirm no regressions
- [x] 7.2 Run `npm test` from `frontend/` and confirm no regressions
- [x] 7.3 Start the stack; submit a request for a non-existent episode; confirm the frontend chat shows the user-readable "couldn't find content" message
- [x] 7.4 Submit a valid request; confirm the chat input remains disabled during the full animation and enables only after the scene breakdown finishes

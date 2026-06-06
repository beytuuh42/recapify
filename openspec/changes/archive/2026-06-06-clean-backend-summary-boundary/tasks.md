## 1. Create Package Structure

- [x] 1.1 Create `backend/recapify/src/main/java/com/recapify/llm/client/` directory
- [x] 1.2 Create `backend/recapify/src/main/java/com/recapify/llm/dto/` directory

## 2. Move DTOs

- [x] 2.1 Move `SummaryRequest.java` to `llm/dto/` and update its package declaration to `com.recapify.llm.dto`
- [x] 2.2 Move `SummaryResponse.java` to `llm/dto/` and update package declaration
- [x] 2.3 Move `Chunk.java` to `llm/dto/` and update package declaration
- [x] 2.4 Move `IntentRequest.java` to `llm/dto/` and update package declaration

## 3. Extract MlServiceClient

- [x] 3.1 Create `llm/client/MlServiceClient.java` as a `@Service` with constructor-injected `WebClient llmServiceWebClient`
- [x] 3.2 Move `addRequestIdHeader` helper into `MlServiceClient`
- [x] 3.3 Implement `extractIntent(String text)` in `MlServiceClient` with the WebClient POST logic and logging currently in `LlmService.getIntent()`
- [x] 3.4 Implement `fetchSummary(SummaryRequest req)` in `MlServiceClient` with the WebClient POST logic and logging currently in `LlmService.getSummary()`

## 4. Slim LlmService

- [x] 4.1 Replace `WebClient` field in `LlmService` with `MlServiceClient mlServiceClient`
- [x] 4.2 Rewrite `getIntent(String text)` to delegate to `mlServiceClient.extractIntent(text)` — keep the method signature for controller compatibility
- [x] 4.3 Rewrite `getSummary(String text)` to call `getIntent` then `mlServiceClient.fetchSummary` — orchestration only, no WebClient usage
- [x] 4.4 Remove `addRequestIdHeader` and the `REQUEST_ID_HEADER` / `REQUEST_ID_KEY` constants from `LlmService` (moved to client)

## 5. Update Imports

- [x] 5.1 Add `com.recapify.llm.dto.*` imports to `LlmController.java`, `LlmService.java`, and `MlServiceClient.java`
- [x] 5.2 Add `com.recapify.llm.client.MlServiceClient` import to `LlmService.java`

## 6. Verify

- [x] 6.1 Run `./mvnw compile` (or `mvnw.cmd compile` on Windows) from `backend/recapify/` and confirm zero compilation errors
- [x] 6.2 Run `./mvnw test` and confirm no regressions
- [x] 6.3 Start the stack and submit a recap request; confirm `POST /api/v1/llm/summary` returns a valid `SummaryResponse` with all fields
- [x] 6.4 Confirm `X-Request-Id` is propagated to the ML service by checking `docker logs --tail 50 recapify-backend-dev` and `recapify-ml-dev`

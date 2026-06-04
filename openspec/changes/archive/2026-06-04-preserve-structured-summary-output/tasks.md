## 1. Backend — Remove Summary Collapse

- [x] 1.1 Change `LlmService.getSummary()` return type from `Summary` to `SummaryResponse` and remove the `.map(res -> new Summary(res.final_summary()))` collapse (`backend/recapify/src/main/java/com/recapify/llm/LlmService.java:62-68`)
- [x] 1.2 Update `LlmController.createSummary()` to return `ResponseEntity<SummaryResponse>` instead of `ResponseEntity<Summary>` (`backend/recapify/src/main/java/com/recapify/llm/LlmController.java`)
- [x] 1.3 Delete `backend/recapify/src/main/java/com/recapify/llm/Summary.java` (no longer used)
- [x] 1.4 Verify backend compiles and `POST /api/v1/llm/summary` returns the full JSON structure via `docker logs --tail 200 recapify-backend-dev`

## 2. Frontend — Model Updates

- [x] 2.1 Add `ChunkSummary` and `EpisodeSummary` interfaces to `frontend/src/app/models/summary.model.ts` matching the backend `SummaryResponse` / `Chunk` shapes
- [x] 2.2 Add optional `summary?: EpisodeSummary` field to the `Message` interface in `summary.model.ts`
- [x] 2.3 Remove the `Summary` interface from `summary.model.ts` (replaced by `EpisodeSummary`)
- [x] 2.4 Update `LlmService.getSummary()` in `frontend/src/app/services/llm.service.ts` to type the HTTP response as `EpisodeSummary` instead of `Summary`

## 3. Frontend — Structured Summary Component

- [x] 3.1 Create `frontend/src/app/components/episode-summary/episode-summary.component.ts` as a standalone Angular component accepting `@Input() summary: EpisodeSummary`
- [x] 3.2 Create the component template rendering `final_summary` as the primary paragraph, `key_events` as a labeled list, `characters` as a labeled list, and `chunk_summaries` in chronological order (chunk title + summary text)
- [x] 3.3 Create minimal styles in `episode-summary.component.scss`

## 4. Frontend — Wire Summary Into Chat

- [x] 4.1 Update `app.component.ts` (or wherever `LlmService.getSummary()` is called) to build the assistant `Message` with `summary: episodeSummary` and `content: ''` instead of `content: summary.content`
- [x] 4.2 Update `MessageBubbleComponent` to accept `@Input() summary?: EpisodeSummary` and conditionally render `<app-episode-summary>` when `summary` is set, or the existing text path otherwise
- [x] 4.3 Update `ChatWindowComponent` template to pass `message.summary` to `<app-message-bubble>` alongside the existing `text` and `role` inputs

## 5. Verification

- [x] 5.1 Run existing frontend unit tests (`ng test --watch=false`) and confirm no regressions
- [x] 5.2 Start the stack and submit a recap request; confirm the response bubble shows title, final recap, key events, characters, and chunks
- [x] 5.3 Confirm user messages and the initial greeting still render as plain text
- [x] 5.4 Inspect `docker logs --tail 200 recapify-frontend-dev` and `recapify-backend-dev` for errors

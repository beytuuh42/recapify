## Context

The ML service at `POST /api/v1/summarize` returns a rich `EpisodeSummary` (defined in `ml/app/models.py`) with `title`, `final_summary`, `key_events`, `characters`, and `chunk_summaries`. The backend already deserializes this into `SummaryResponse.java` (which mirrors the full shape), but immediately collapses it to `new Summary(res.final_summary())` in `LlmService.java:68`. The frontend receives only a `{ content: string }` and renders it as a single paragraph.

All three services already have compatible types; the fix is primarily removing the collapse in the backend and adding structured rendering in the frontend.

## Goals / Non-Goals

**Goals:**
- Pass all `EpisodeSummary` fields through `POST /api/v1/llm/summary` without loss
- Render title, final recap, key events, characters, and chunk summaries as distinct UI sections
- Keep the change scoped to the summary response path only

**Non-Goals:**
- Token streaming (the full `EpisodeSummary` only exists after merge — stream is future work)
- Changes to the ML service (already returns the correct shape)
- Collapsible/expandable chunk detail (render all chunks; interaction polish is follow-up)
- User accounts, persistence, or conversation history

## Decisions

### 1. Use `SummaryResponse` as the backend response DTO

`SummaryResponse.java` already has all fields (`title`, `final_summary`, `key_events`, `characters`, `chunk_summaries: List<Chunk>`). Changing `LlmController` to return `ResponseEntity<SummaryResponse>` and `LlmService.getSummary()` to return `SummaryResponse` requires no new classes. `Summary.java` becomes unused and is removed.

Alternative considered: introduce a new `EpisodeSummaryResponse` DTO. Rejected — `SummaryResponse` already has the right shape; adding another layer is unnecessary churn.

### 2. Extend `Message` with an optional `summary` field rather than replacing `content`

The `Message` interface in `summary.model.ts` gets `summary?: EpisodeSummary`. Text messages (user input, initial greeting) continue using `content: string`. Assistant summary responses populate `summary` and leave `content` empty. This avoids serializing structured data into a string field and keeps `appendToMessage` (which operates on `content`) untouched.

Alternative considered: union type `content: string | EpisodeSummary`. Rejected — it breaks the initial greeting and user messages which must remain plain strings, and makes type-narrowing noisier throughout the component tree.

### 3. New standalone `EpisodeSummaryComponent` rendered from `MessageBubbleComponent`

A new `episode-summary` standalone Angular component renders the structured fields. `MessageBubbleComponent` receives an optional `@Input() summary?: EpisodeSummary` and conditionally renders either the existing text path or the new summary component. This keeps rendering logic out of `ChatWindowComponent` and avoids bloating the existing bubble template.

Alternative considered: render structured fields directly inside `message-bubble`. Rejected — the template would become hard to test and maintain as fields grow.

## Risks / Trade-offs

- **API contract change**: `POST /api/v1/llm/summary` response shape changes from `{ content }` to the full `EpisodeSummary` shape. No known external consumers, but frontend and backend must be deployed together.
  → Mitigation: coordinated update in a single branch; both services are in the same repo.

- **`appendToMessage` is now dead code for summary messages**: Summary messages are created with the full `summary` object; `appendToMessage` only operates on `content`. It remains useful for hypothetical future streaming of plain-text messages.
  → No mitigation needed; leave it in place.

- **`chunk_summaries` volume**: A long episode can produce many chunks. Rendering all of them without pagination may result in a tall response bubble.
  → Acceptable for portfolio scope; pagination or collapse is follow-up work.

## Migration Plan

1. Update backend (`LlmService`, `LlmController`, remove `Summary.java`) — no database migration needed.
2. Update frontend model, service, and add `EpisodeSummaryComponent` — single coordinated commit or PR.
3. Verify via `docker logs --tail 200 recapify-backend-dev` and `recapify-frontend-dev` after containers restart.
4. Rollback: revert the PR; no persistent state is affected.

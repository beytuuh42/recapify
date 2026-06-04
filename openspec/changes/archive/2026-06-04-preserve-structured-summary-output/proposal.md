## Why

The ML service already produces a rich `EpisodeSummary` (title, final recap, key events, characters, per-chunk summaries), but the backend discards all structure and returns only `final_summary` as a flat string. Users see a wall of text where a scannable, structured recap could be shown.

## What Changes

- Remove the backend's `.map(res -> new Summary(res.final_summary()))` collapse in `LlmService.java`
- Replace `Summary { content: String }` response with a DTO that carries all `EpisodeSummary` fields through the `/api/v1/llm/summary` endpoint
- Update `summary.model.ts` to declare the full `EpisodeSummary` interface (title, final_summary, key_events, characters, chunk_summaries)
- Update `LlmService` (Angular) to type the HTTP response as `EpisodeSummary` instead of `Summary`
- Add a structured summary component that renders title, final recap, key events, characters, and collapsible chunk breakdowns
- Retire the flat `Summary { content }` model from backend and frontend

## Capabilities

### New Capabilities

- `structured-summary-presentation`: The frontend renders `EpisodeSummary` fields as distinct, scannable sections instead of a single paragraph.

### Modified Capabilities

- `repo-generated-artifact-hygiene`: No requirement changes — implementation detail only.

## Impact

- **Backend**: `Summary.java`, `SummaryResponse.java`, `LlmService.java`, `LlmController.java` — collapse removed, DTO aligned with ML response shape
- **Frontend**: `summary.model.ts`, `llm.service.ts`, `message-bubble` or a new `episode-summary` component, `chat.service.ts` (Message content type may need to accommodate structured payloads)
- **API contract**: `POST /api/v1/llm/summary` response shape changes — not a breaking change for external consumers (none exist), but a coordinated frontend+backend update
- **No ML changes** — the ML service already returns the correct shape

## Why

The FastAPI ML service accumulated several quality problems while evolving from a hand-rolled multi-provider LLM orchestration to the current LangChain-based design: dead code from the old provider model, naming convention violations, a missing error boundary for unavailable subtitles, and orchestration logic embedded directly in a route handler. These are the most visible code quality gaps when the project is reviewed as a portfolio piece.

## What Changes

- Extract `create_summary` route handler orchestration into a dedicated `summary_workflow.py` module with a single `run_summary` function; route handler delegates entirely.
- Rename `LLMClient.py` to `llm_client.py` (Python module naming convention: snake_case).
- Rename the module-level `llm` variable to `llm_client` in `main.py`.
- Rename `SrtHandler.find_subtitle` / `fetch_subtitle` to `search_subtitles` / `download_subtitle` for clarity.
- Remove `LLMProvider` enum and the `ValueError` guard from `LlmClient.__init__`; replace with three named model string params (`intent_model`, `chunk_model`, `merge_model`).
- Remove `Transcript` model (defined but never used).
- Remove direct `from google.genai.errors import ServerError` import; handle retries and errors using LangChain-idiomatic patterns only.
- Remove `langchain-openai` and `openai` from `requirements.txt` (unused remnants of the pre-LangChain multi-provider design).
- Add `SubtitleNotFoundError` raised when `search_subtitles` returns no results; expose as HTTP 404 from the `/api/v1/summarize` route.
- Add focused unit tests for `run_summary` covering the cache hit path, cache miss path, and `ModelUnavailableError` path.
- Keep the `/api/v1/chat` dev endpoint untouched.

## Capabilities

### New Capabilities

- `ml-summary-workflow`: The ML summary orchestration is isolated in `summary_workflow.py`, separate from route definitions, enabling independent testing and clear entry points.
- `ml-subtitle-not-found`: The ML service returns HTTP 404 with a structured error body when no subtitles are found for the requested title/season/episode, instead of propagating an unhandled `IndexError` as a 500.

### Modified Capabilities

<!-- None. API contracts and observable behavior for existing happy paths are unchanged. -->

## Impact

- `ml/app/main.py` — thin route handlers; `create_summary` delegates to `run_summary`; module-level `llm` renamed
- `ml/app/LLMClient.py` → `ml/app/llm_client.py` — renamed; `LLMProvider` enum removed; constructor simplified
- `ml/app/summary_workflow.py` — new file
- `ml/app/srt_handler.py` — method renames; `SubtitleNotFoundError` raised on empty results
- `ml/app/models.py` — `LLMProvider` and `Transcript` removed
- `ml/app/errors.py` — `SubtitleNotFoundError` added
- `ml/requirements.txt` — `langchain-openai`, `openai`, `google-genai` removed as explicit dependencies
- `ml/tests/` — new `test_summary_workflow.py`
- No changes to any external API contracts, the backend, or the frontend

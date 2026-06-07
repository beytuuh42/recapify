## 1. Remove dead code and dependencies

- [x] 1.1 Remove `LLMProvider` enum from `models.py`
- [x] 1.2 Remove `Transcript` model from `models.py`
- [x] 1.3 Remove `langchain-openai` and `openai` from `requirements.txt`
- [x] 1.4 Remove `google-genai` as an explicit entry from `requirements.txt` (kept transitively via `langchain-google-genai`)

## 2. Rename files and fix naming conventions

- [x] 2.1 Rename `ml/app/LLMClient.py` → `ml/app/llm_client.py` and rename the class from `LLMClient` to `LlmClient`
- [x] 2.2 Update `from LLMClient import LLMClient` in `main.py` to `from llm_client import LlmClient`
- [x] 2.3 Update any other imports of `LLMClient` across the codebase
- [x] 2.4 Rename the module-level variable `llm = LlmClient(...)` to `llm_client` in `main.py`; update all usages in route handlers
- [x] 2.5 Rename `SrtHandler.find_subtitle` → `search_subtitles` and `fetch_subtitle` → `download_subtitle` in `srt_handler.py`; update all callers in `main.py`

## 3. Simplify LlmClient constructor

- [x] 3.1 Remove `provider: LLMProvider` parameter and the `ValueError` guard from `LlmClient.__init__`
- [x] 3.2 Keep `intent_model`, `chunk_model`, `merge_model` as the only constructor params with their existing defaults
- [x] 3.3 Update `main.py` instantiation to `LlmClient(merge_model="gemini-2.5-flash")` (no provider arg)

## 4. Remove google.genai direct import

- [x] 4.1 Remove `from google.genai.errors import ServerError` from `llm_client.py`
- [x] 4.2 Replace `retry_if_exception_type=(ServerError,)` in `with_retry(...)` with `retry_if_exception_type=(Exception,)` scoped to the chunk model chain only
- [x] 4.3 In `_invoke_structured`, replace the `ServerError` catch with a broad `Exception` catch that re-raises as `ModelUnavailableError` with the original exception chained (`raise ModelUnavailableError(...) from e`)
- [x] 4.4 In `summarize_chunks`, replace the `ServerError` catch with a broad `Exception` catch with the same re-raise pattern

## 5. Add SubtitleNotFoundError

- [x] 5.1 Add `SubtitleNotFoundError(title, season, episode, language)` to `errors.py`
- [x] 5.2 In `SrtHandler.download_subtitle`, check if `search_subtitles` returns an empty result list and raise `SubtitleNotFoundError` before attempting `download_and_parse`
- [x] 5.3 In `main.py` `create_summary` route handler, add a `SubtitleNotFoundError` catch that returns HTTP 404 with body `{"code": "subtitle_not_found", "title": ..., "season": ..., "episode": ..., "language": ...}`

## 6. Extract summary workflow

- [x] 6.1 Create `ml/app/summary_workflow.py` with `run_summary(request: SummarizeRequest, llm_client: LlmClient, srt_handler: SrtHandler) -> EpisodeSummary`
- [x] 6.2 Move the orchestration body from `create_summary` into `run_summary`: cache read, subtitle download and chunk, LLM chunk summarization, merge, cache write, and all related logging
- [x] 6.3 Keep `SubtitleNotFoundError` and `ModelUnavailableError` raised from `run_summary` (the route handler owns HTTP status translation)
- [x] 6.4 Replace `create_summary` body with delegation: call `run_summary(request, llm_client, srt_handler)`; keep the `SubtitleNotFoundError` (404) and `ModelUnavailableError` (503) catches in the route handler

## 7. Add workflow tests

- [x] 7.1 Create `ml/tests/test_summary_workflow.py`
- [x] 7.2 Add cache hit test: mock `cache.read` to return a valid serialized `EpisodeSummary`; assert result matches and `SrtHandler`/`LlmClient` are not called
- [x] 7.3 Add cache miss happy path test: mock `cache.read` to return `None`, mock all `SrtHandler` and `LlmClient` methods; assert valid `EpisodeSummary` returned and `cache.write` called once
- [x] 7.4 Add `ModelUnavailableError` test: mock `cache.read` to return `None`, mock `LlmClient.summarize_chunks` to raise `ModelUnavailableError`; assert the error propagates from `run_summary`

## 8. Verify

- [x] 8.1 Run `python -m unittest discover -s tests` from `ml/` and confirm all tests pass
- [x] 8.2 Start the stack and submit a recap request; confirm `POST /api/v1/summarize` returns a valid `EpisodeSummary`
- [x] 8.3 Submit a request for a non-existent episode; confirm the ML service returns HTTP 404 with `subtitle_not_found` code
- [x] 8.4 Confirm `X-Request-Id` propagation is unchanged in `docker logs --tail 50 recapify-ml-dev`

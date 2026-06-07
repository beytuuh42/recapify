## Context

The ML service evolved through two phases: an early hand-rolled multi-provider LLM client (supporting both Gemini and OpenAI), and the current LangChain-based implementation. The migration left behind dead code (`LLMProvider` enum, `Transcript` model, unused `openai`/`langchain-openai` dependencies, a direct `google.genai.errors` import) and a naming convention violation (`LLMClient.py` — Python modules must be snake_case). The `create_summary` route handler also carries the full orchestration body inline, which is the same concern that was cleaned up on the Spring Boot side in `clean-backend-summary-boundary`. The remaining functional gap is that a missing subtitle result causes an unhandled `IndexError` instead of a typed error and an appropriate HTTP status.

## Goals / Non-Goals

**Goals:**
- Extract `create_summary` orchestration to `summary_workflow.py`; route handler becomes a delegation call.
- Rename `LLMClient.py` → `llm_client.py`; update all imports.
- Rename `SrtHandler` methods to `search_subtitles` / `download_subtitle` for self-documenting naming.
- Remove `LLMProvider` enum; `LlmClient.__init__` takes three named model string params directly.
- Remove dead models (`Transcript`), dead deps (`langchain-openai`, `openai`), and the direct `google.genai.errors` import.
- Introduce `SubtitleNotFoundError` raised on empty subtitle search; exposed as HTTP 404 from `/api/v1/summarize`.
- Add `test_summary_workflow.py` covering the three key paths.

**Non-Goals:**
- No changes to the Spring Boot backend or Angular frontend.
- No streaming or progress state work (separate change).
- No internal refactoring of `LlmClient` prompt/chain logic.
- No subtitle result validation or confidence scoring (tracked as a separate GitHub issue).
- No multi-provider support.

## Decisions

### LlmClient constructor: remove provider enum, use three named params

```python
class LlmClient:
    def __init__(
        self,
        intent_model: str = "gemma-4-31b-it",
        chunk_model: str = "gemini-3.1-flash-lite",
        merge_model: str = "gemini-2.5-flash",
    ):
```

**Rationale**: The `LLMProvider` enum existed to support multiple providers. That goal was abandoned when the service moved to LangChain with a Gemini-only implementation. Keeping the enum creates false expectations and dead code. Flat string params are honest about the current scope and easy to extend if multi-provider returns.

**Alternative considered**: ModelConfig dataclass grouping the three model strings. Rejected as over-engineering for three values that are set once at startup.

### google.genai.errors removal strategy

The direct `ServerError` import is used in two places: `with_retry(retry_if_exception_type=(ServerError,))` and the catch blocks in `_invoke_structured` and `summarize_chunks`. The replacement: use `Exception` as the retry exception type (since `langchain-google-genai` already handles the retry surface through LangChain's retry utilities), and catch `Exception` with re-raise as `ModelUnavailableError` in the `_invoke_structured` helper. This removes the direct SDK dependency while preserving the same observable error behavior.

**Alternative considered**: Import `ServerError` from `langchain_google_genai` internals. Rejected — it's not part of that package's public API and would create a fragile coupling to an internal symbol.

### SubtitleNotFoundError placement

`SubtitleNotFoundError` is raised in `SrtHandler.download_subtitle` when `search_subtitles` returns an empty result list. It is caught in the `create_summary` route handler (and correspondingly in `run_summary`) and returned as HTTP 404 with a body of `{"code": "subtitle_not_found", "title": ..., "season": ..., "episode": ...}`. The Spring Boot backend will consume this in a follow-on change (`polish-api-contracts`).

**Alternative considered**: Raise the error in `run_summary` after calling `search_subtitles` separately. Rejected — `download_subtitle` already calls `search_subtitles` internally; raising at the point of failure keeps the error origin close to the cause.

### File rename cascade

Renaming `LLMClient.py` → `llm_client.py` requires updating `from LLMClient import LLMClient` in `main.py`. The class name `LlmClient` follows Python's PascalCase convention for classes (acronym as title case: `LlmClient` not `LLMClient`). The rename covers both the file and the class name.

## Risks / Trade-offs

- [Risk] Catching `Exception` broadly in `_invoke_structured` could suppress non-server errors. → Mitigation: re-raise immediately as `ModelUnavailableError` with the original exception chained (`from e`); callers see the translated error type, not a silent swallow.
- [Risk] `download_subtitle` raises `SubtitleNotFoundError` — if callers other than `run_summary` call it, they must handle the new exception. → Current callers: only `run_summary` and the `/api/v1/subtitles` route, which already returns data from `search_subtitles` (not `download_subtitle`). No hidden callers.

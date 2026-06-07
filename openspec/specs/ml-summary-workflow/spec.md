# Capability: ML Summary Workflow

## Purpose

Defines the ML service's summary orchestration layer: a dedicated `summary_workflow` module that owns all business logic for the summarize endpoint, keeping route handlers thin and the workflow independently testable.

## Requirements

### Requirement: Summary orchestration is isolated from route handlers
The ML service SHALL implement summary workflow orchestration in a dedicated `summary_workflow` module. The `create_summary` route handler SHALL delegate all business logic to `run_summary(request, llm_client, srt_handler)` and perform no orchestration itself.

#### Scenario: Route handler delegates entirely
- **WHEN** `POST /api/v1/summarize` is called with a valid `SummarizeRequest`
- **THEN** the route handler SHALL call `run_summary` and return its result, containing no cache, subtitle, or LLM logic inline

#### Scenario: Workflow is independently testable
- **WHEN** `run_summary` is called with mocked `LlmClient`, `SrtHandler`, and `cache` module
- **THEN** it SHALL execute the full orchestration path without requiring live external services

### Requirement: Workflow preserves existing orchestration order
The `run_summary` function SHALL implement: cache read → subtitle download and chunk → LLM chunk summarization → merge → cache write, in that order.

#### Scenario: Cache hit short-circuits the workflow
- **WHEN** `cache.read` returns a cached result for the requested title, season, episode, and language
- **THEN** `run_summary` SHALL return the cached `EpisodeSummary` without calling `SrtHandler` or `LlmClient`

#### Scenario: Cache miss triggers full workflow
- **WHEN** `cache.read` returns no result
- **THEN** `run_summary` SHALL call `srt_handler.download_subtitle`, chunk the transcript, summarize chunks, merge, write to cache, and return the `EpisodeSummary`

#### Scenario: LLM unavailability is propagated
- **WHEN** `LlmClient.summarize_chunks` raises `ModelUnavailableError`
- **THEN** `run_summary` SHALL propagate the error; the route handler SHALL return HTTP 503

### Requirement: Workflow test coverage
The ML service test suite SHALL include `test_summary_workflow.py` covering the cache hit path, cache miss (happy) path, and `ModelUnavailableError` path using mocked dependencies.

#### Scenario: Cache hit test
- **WHEN** `cache.read` is mocked to return a valid serialized `EpisodeSummary`
- **THEN** the test SHALL assert the result matches and that `SrtHandler` and `LlmClient` are not called

#### Scenario: Cache miss happy path test
- **WHEN** `cache.read` returns `None` and all `LlmClient` methods return valid results
- **THEN** the test SHALL assert a valid `EpisodeSummary` is returned and `cache.write` is called once

#### Scenario: Model unavailable test
- **WHEN** `LlmClient.summarize_chunks` raises `ModelUnavailableError`
- **THEN** the test SHALL assert that `run_summary` propagates `ModelUnavailableError`

## ADDED Requirements

### Requirement: Missing subtitle results in a typed error
The `SrtHandler.download_subtitle` method SHALL raise `SubtitleNotFoundError` when `search_subtitles` returns an empty result list, instead of propagating an `IndexError`.

#### Scenario: Empty subtitle search raises typed error
- **WHEN** `search_subtitles` returns a response with an empty data list
- **THEN** `download_subtitle` SHALL raise `SubtitleNotFoundError` containing the requested title, season, episode, and language

#### Scenario: Successful subtitle search proceeds normally
- **WHEN** `search_subtitles` returns at least one result
- **THEN** `download_subtitle` SHALL download and parse the first result and return the parsed subtitle list

### Requirement: Subtitle not found is exposed as HTTP 404
The `POST /api/v1/summarize` route handler SHALL catch `SubtitleNotFoundError` and return HTTP 404 with a structured error body.

#### Scenario: HTTP 404 on missing subtitle
- **WHEN** `run_summary` raises `SubtitleNotFoundError`
- **THEN** the route handler SHALL return HTTP 404 with body `{"code": "subtitle_not_found", "title": ..., "season": ..., "episode": ..., "language": ...}`

#### Scenario: Other errors are not affected
- **WHEN** `run_summary` raises `ModelUnavailableError`
- **THEN** the route handler SHALL return HTTP 503, not 404

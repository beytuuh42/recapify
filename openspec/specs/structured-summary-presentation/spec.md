# structured-summary-presentation Specification

## Purpose
Defines how the Recapify recap response is rendered in the frontend. The ML service produces a rich `EpisodeSummary` (title, final recap, key events, characters, chunk summaries); this capability ensures that structure is preserved end-to-end and presented as distinct, scannable sections rather than a flat paragraph.

## Requirements

### Requirement: Backend exposes full EpisodeSummary structure
The `POST /api/v1/llm/summary` endpoint SHALL return all fields of the ML service's `EpisodeSummary` response without collapsing them to a single string.

#### Scenario: Full structure is returned
- **WHEN** the ML service returns an `EpisodeSummary` for a valid summarize request
- **THEN** the backend response includes `title`, `final_summary`, `key_events`, `characters`, and `chunk_summaries`
- **AND** no fields are discarded or flattened before the response is sent to the frontend

#### Scenario: Chunk summaries are preserved
- **WHEN** the ML service returns chunk_summaries with per-chunk title, summary, key_events, and characters
- **THEN** each chunk's fields are present in the backend response unchanged

### Requirement: Frontend renders structured summary sections
The frontend SHALL render `EpisodeSummary` fields as distinct visual sections rather than a single flat paragraph.

#### Scenario: Final recap is displayed as the primary section
- **WHEN** a summary response is received by the frontend
- **THEN** the `final_summary` text is displayed as the main recap paragraph

#### Scenario: Key events are displayed as a list
- **WHEN** the summary response contains one or more `key_events`
- **THEN** they are rendered as a labeled list under a "Key Events" heading

#### Scenario: Characters are displayed as a named list
- **WHEN** the summary response contains one or more `characters`
- **THEN** they are rendered under a "Characters" heading

#### Scenario: Chunk breakdowns are displayed
- **WHEN** the summary response contains `chunk_summaries`
- **THEN** each chunk's title and summary text are rendered in chronological order

### Requirement: Plain-text messages continue to render unchanged
The frontend SHALL render user messages and non-summary assistant messages as plain text, unaffected by structured summary rendering.

#### Scenario: User messages render as plain text
- **WHEN** a message has role "user"
- **THEN** its content is displayed as a plain text string with no structured rendering

#### Scenario: Initial greeting renders as plain text
- **WHEN** the chat is initialized
- **THEN** the assistant's greeting message is displayed as plain text

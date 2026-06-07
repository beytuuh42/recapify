### Requirement: Chat input is locked until summary animation completes
`ChatInputComponent` SHALL keep `isBusy` set to `true` until `EpisodeSummaryComponent` emits an `animationComplete` event at the end of the full reveal sequence.

#### Scenario: Input locked during animation
- **WHEN** the backend response arrives and the summary begins animating
- **THEN** the chat input SHALL remain disabled until all reveal phases (recap text, key events, characters, scene breakdown) have completed

#### Scenario: Input unlocked after animation
- **WHEN** `EpisodeSummaryComponent` emits `animationComplete`
- **THEN** `ChatInputComponent` SHALL call `chatService.setBusy(false)` and the input SHALL become enabled

#### Scenario: Input locked during backend request
- **WHEN** the user submits a request and the backend has not yet responded
- **THEN** the chat input SHALL remain disabled (existing behavior, unchanged)

### Requirement: Frontend displays error message from backend response body
When the backend returns an error response, `ChatInputComponent` SHALL display the `message` field from the response body in the chat rather than a hardcoded fallback string.

#### Scenario: Backend error message shown to user
- **WHEN** the HTTP request to the backend fails with a 4xx or 5xx response containing a `message` field
- **THEN** the assistant message added to the chat SHALL contain the value of `message` from the error body

#### Scenario: Fallback for unparseable error
- **WHEN** the HTTP request fails and the response body has no `message` field
- **THEN** the assistant message SHALL contain a generic fallback: "Something went wrong. Please try again."

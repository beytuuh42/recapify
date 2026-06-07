### Requirement: ML service failures produce typed backend exceptions
`MlServiceClient` SHALL throw `ContentUnavailableException` when the ML service returns HTTP 404 and `MlServiceUnavailableException` when it returns HTTP 503, rather than propagating raw `WebClientResponseException`.

#### Scenario: ML 404 produces ContentUnavailableException
- **WHEN** the ML service returns HTTP 404 with a `subtitle_not_found` error body
- **THEN** `MlServiceClient.fetchSummary` SHALL throw `ContentUnavailableException` containing the title, season, episode, and language from the ML error body

#### Scenario: ML 503 produces MlServiceUnavailableException
- **WHEN** the ML service returns HTTP 503
- **THEN** `MlServiceClient.fetchSummary` SHALL throw `MlServiceUnavailableException`

#### Scenario: Unparseable ML error falls back to service unavailable
- **WHEN** the ML service returns a non-2xx response with an unrecognized or unparseable body
- **THEN** `MlServiceClient` SHALL throw `MlServiceUnavailableException`

### Requirement: Backend returns structured error responses to the frontend
A `@ControllerAdvice` exception handler SHALL map typed backend exceptions to HTTP responses with a JSON body containing `error` and `message` fields.

#### Scenario: ContentUnavailableException maps to HTTP 404
- **WHEN** `LlmController` propagates `ContentUnavailableException`
- **THEN** the response SHALL be HTTP 404 with body `{"error": "content_unavailable", "message": "We couldn't find content for {title} Season {season} Episode {episode}. Did we understand your request correctly?"}`

#### Scenario: MlServiceUnavailableException maps to HTTP 503
- **WHEN** `LlmController` propagates `MlServiceUnavailableException`
- **THEN** the response SHALL be HTTP 503 with body `{"error": "service_unavailable", "message": "Something went wrong while generating the summary. Please try again."}`

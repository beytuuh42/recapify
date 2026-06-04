# Migration Summary

## Immediate OpenSpec Change Recommendations

These items should become concrete OpenSpec changes because they are needed for portfolio readiness and have implementation scope.

### `preserve-structured-summary-output`

- Preserve the ML service's structured `EpisodeSummary` response through the backend and frontend.
- Render `final_summary`, `key_events`, `characters`, and `chunk_summaries` instead of flattening the response into one paragraph.
- Keep true token streaming out of scope; use structured rendering first.

Source roadmap items:

- Better summary formatting and presentation in the UI instead of dumping everything into one large paragraph.
- Decide how to expose richer summary structure in the UI.

### `add-summary-progress-states`

- Add visible progress states for the long-running summary workflow.
- Show phases such as understanding the request, finding subtitles, summarizing chunks, and merging the final recap.
- Treat true streaming as future work because the final `EpisodeSummary` only exists after chunk summarization and merge.

Source roadmap items:

- Frontend UX stabilization for portfolio-readiness.
- Frontend UI rework is still in progress; current state is improved but not yet portfolio-ready.

### `clean-backend-summary-boundary`

- Lightly restructure the Spring Boot summary boundary without over-engineering the small service.
- Separate frontend-facing controller/service concerns from the outbound ML client and DTOs.
- Preserve request ID propagation and API prefix behavior.

Source roadmap items:

- Backend contract and structure cleanup.

### `refactor-ml-summary-workflow`

- Move summary orchestration out of `main.py`.
- Separate API routes, workflow orchestration, subtitle handling, LLM client usage, cache access, and models.
- Add focused tests around workflow behavior with mocked external providers.

Source roadmap items:

- ML service refactor focused on route/workflow separation and LLM client readability.

### `polish-portfolio-readme`

- Rewrite README presentation for recruiters and engineers.
- Add an architecture diagram and current screenshots or a short demo GIF.
- Keep limitations honest and concise.
- Avoid using README as the complete backlog.

Source roadmap items:

- Portfolio polish: README quality, screenshots/demo assets, roadmap clarity, and repo presentation.

## README Highlights To Keep

These points can remain in public documentation, but should be short and curated.

- Hosted demo cold starts on Render free tier.
- Subtitle availability depends on OpenSubtitles data.
- The app is intentionally a three-service fullstack/AI portfolio project.
- Future work may include richer recap presentation, workflow progress feedback, and smarter transcript chunking.

## Discarded Or Stale Items

- Frontend design revamp so the product no longer reads like a generic chat tutorial.
- Frontend UI rework is still in progress; current state is improved but not yet portfolio-ready.

Reason: PR #11 already addressed the primary frontend polish concern. Remaining frontend work should be tracked as structured summary presentation or progress states, not a generic UI revamp.

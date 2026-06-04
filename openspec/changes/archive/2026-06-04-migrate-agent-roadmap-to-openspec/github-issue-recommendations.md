# GitHub Issue Recommendations

These items are useful backlog or research ideas, but they are not required before presenting Recapify as a portfolio project.

## Product Backlog

### Conversation history sidebar

- Add a sidebar that lets users revisit prior recap conversations.
- Start with local-only storage if implemented before user accounts.

Source roadmap items:

- Conversation sidebar with tracked conversation history in the UI.
- Naive local conversation persistence first.

### Database-backed persistence

- Introduce durable persistence for users, conversations, or generated summaries after the product scope justifies it.

Source roadmap items:

- Introduce database-backed persistence.
- Move from local storage to real user-backed persistence.

### User accounts

- Add accounts only if the app grows beyond portfolio/demo scope.

Source roadmap items:

- User/account features if the app grows beyond portfolio scope.

### Expanded recap modes

- Support movie, multi-episode, season, and multi-season summary modes after the single-episode flow is polished.

Source roadmap items:

- Summaries across multiple episodes.
- Summaries for entire seasons.
- Summaries across multiple seasons.
- Richer recap modes beyond the current episode summary flow.

## AI / ML Research Backlog

### Scene-aware transcript chunking

- Replace fixed transcript chunking with a strategy that better respects scene or narrative boundaries.
- Compare output quality against the current naive chunking approach.

Source roadmap items:

- Replace naive transcript chunking with scene-aware ML chunking.

### Cache infrastructure

- Introduce a production-grade cache only after cache behavior and deployment needs are clearer.

Source roadmap items:

- Introduce real cache infrastructure beyond the current local file cache.

### Model/provider routing

- Add multiple model/provider routing after the current workflow and contracts are cleaner.

Source roadmap items:

- Multiple model/provider routing once the current workflow is cleaner.

### Retrieval-augmented generation

- Explore RAG only if there is a concrete source corpus and evaluation strategy.

Source roadmap items:

- Introduce RAG / retrieval-based augmentation.

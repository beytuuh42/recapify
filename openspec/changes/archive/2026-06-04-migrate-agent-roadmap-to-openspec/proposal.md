## Why

The repository currently has a homemade `.agents` planning workflow that overlaps with OpenSpec and has mixed portfolio priorities, implementation plans, and long-term ideas in one place. Migrating to OpenSpec-centered planning will make active work clearer, preserve useful roadmap ideas, and remove stale coordination files before larger portfolio-readiness work begins.

## What Changes

- Extract useful items from `.agents/ROADMAP.md` before deleting it.
- Convert immediate portfolio-readiness work into OpenSpec-backed change recommendations.
- Convert non-immediate backlog ideas into GitHub issue recommendations rather than README roadmap content.
- Remove the obsolete `.agents/PLAN.md`, `.agents/STATUS.md`, and `.agents/ROADMAP.md` workflow from repo guidance.
- Update ignore rules for generated/runtime artifacts such as Python bytecode, local ML cache files, Angular cache/build output, and frontend dependencies.
- Keep README future-work content short and recruiter-facing instead of using it as a full backlog.

## Capabilities

### New Capabilities

- `openspec-planning-migration`: Defines how legacy `.agents` planning content is migrated into OpenSpec changes, GitHub issue recommendations, README highlights, or discarded.
- `repo-generated-artifact-hygiene`: Defines generated/cache artifacts that should stay out of version control.

### Modified Capabilities

- None.

## Impact

- `.agents/ROADMAP.md`: source content to extract, then remove from the active workflow.
- `.agents/PLAN.md` and `.agents/STATUS.md`: remove from the active workflow.
- `AGENTS.md`: update repo guidance to use OpenSpec instead of `.agents` handoff files.
- `.gitignore`: update ignore rules for generated/cache artifacts and remove obsolete `.agents` exceptions.
- `README.md`: possibly adjust future-work wording to stay concise and portfolio-facing.
- GitHub issues: recommended destination for lower-priority backlog items after extraction.

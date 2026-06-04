## Context

The repository currently contains a `.agents` workflow that predates OpenSpec. It mixes long-term backlog items, active implementation planning, and portfolio-readiness priorities. The project now uses OpenSpec for intentional change planning, so keeping both systems creates duplicated and conflicting sources of truth.

This migration is repo hygiene and planning cleanup. It does not implement application features.

## Goals / Non-Goals

**Goals:**

- Preserve useful `.agents/ROADMAP.md` content before removal.
- Move immediate portfolio-readiness work into OpenSpec change recommendations.
- Move lower-priority backlog ideas into GitHub issue recommendations.
- Keep README content concise, public-facing, and recruiter-oriented.
- Remove obsolete `.agents` workflow instructions from repo guidance.
- Ignore generated/cache artifacts that should not appear in status or commits.

**Non-Goals:**

- Implement portfolio-readiness feature work.
- Create every future GitHub issue automatically.
- Rewrite the full README beyond small future-work wording adjustments.
- Change application runtime behavior.
- Add or update dependencies.

## Decisions

### Decision 1: Use OpenSpec for immediate planned work

Immediate portfolio-readiness work should become OpenSpec change recommendations because those items need scope, requirements, design, and implementation tasks. This includes work such as structured summary output, backend contract cleanup, ML workflow refactoring, and portfolio README polish.

Alternative considered: keep a tracked roadmap checklist. That keeps planning lightweight, but it repeats the failure mode that created the current mixed-priority roadmap.

### Decision 2: Use GitHub issues for non-immediate backlog ideas

Future product ideas and research tracks should become GitHub issue recommendations, not README roadmap content. Issues are better for backlog tracking, labels, and later prioritization.

Alternative considered: put all future work in README. That makes the public README noisy and distracts from the portfolio story.

### Decision 3: Keep README future work short and curated

The README should present the project clearly to recruiters and engineers. It can mention a few credible future directions, but it should not serve as the full planning backlog.

### Decision 4: Retire `.agents` handoff files after extraction

Once useful content is classified, `.agents/ROADMAP.md`, `.agents/PLAN.md`, and `.agents/STATUS.md` should be removed from the active workflow and from repo guidance. OpenSpec changes and `openspec status` should become the planning source of truth.

### Decision 5: Add explicit generated-artifact ignore rules

The `.gitignore` should explicitly cover common generated artifacts for this repo: Python bytecode/cache directories, local ML cache files, frontend dependencies, Angular cache, and frontend build output.

## Risks / Trade-offs

- Useful roadmap content could be lost during migration -> Classify all existing roadmap items before deleting `.agents/ROADMAP.md`.
- GitHub issues may not be created immediately -> Produce a clear issue recommendation list as part of implementation so nothing important is forgotten.
- Removing `.agents` guidance may affect future agent handoffs -> Use OpenSpec changes and tasks as the new handoff mechanism.
- README may become too sparse if all future work is removed -> Keep a short, curated limitations/future-work section for public presentation.

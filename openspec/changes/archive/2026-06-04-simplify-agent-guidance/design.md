## Context

`AGENTS.md` was created before the current OpenSpec workflow and now reads like a combined project guide, contribution guide, handoff process, and agent policy. It also contains mojibake from Unicode arrows/tree characters, which makes the file harder to scan in CLI contexts.

This change is documentation/workflow cleanup only. It builds on the archived migration away from `.agents` planning files.

## Goals / Non-Goals

**Goals:**

- Rewrite `AGENTS.md` as a short, practical guide for agents.
- Keep only guidance that prevents likely implementation mistakes.
- Align worktree and verification instructions with actual OpenSpec usage.
- Use ASCII-safe text throughout.

**Non-Goals:**

- Change application code.
- Rewrite README.
- Define full human contribution policy.
- Add new workflow tooling.

## Decisions

### Decision 1: Keep `AGENTS.md` implementation-critical only

`AGENTS.md` should answer what an agent must know before changing the repo. Detailed PR etiquette, long branch naming explanations, and broad process narration add noise without improving implementation quality.

### Decision 2: Separate planning-only work from implementation work

OpenSpec planning artifacts may be created in the current checkout. Application implementation still belongs in a sibling worktree. This matches how the repo is actually being used and avoids unnecessary worktree churn for pure planning.

### Decision 3: Verification depends on change type

Docker log inspection remains useful for app-code runtime checks, but it is not meaningful for docs/planning-only changes. The rewritten guidance will distinguish app-code, test-only, and docs/planning changes.

### Decision 4: Use ASCII-only formatting

ASCII-safe diagrams avoid mojibake and keep the file readable in PowerShell, CLI sessions, and plain text viewers.

## Risks / Trade-offs

- Removing too much context could make future sessions less informed -> Keep architecture, ports, key files, contract notes, and off-limits files.
- Shorter worktree guidance could be misread as optional for implementation -> State clearly that application implementation happens in sibling worktrees.
- Verification guidance could become too loose -> Keep Docker logs for app-code changes and targeted tests for test-only changes.

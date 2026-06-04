## Why

`AGENTS.md` is currently too verbose, contains corrupted Unicode/mojibake, and mixes repo facts with old process detail. Agents need a short, practical guide that matches the OpenSpec workflow and prevents implementation mistakes without overwhelming every session.

## What Changes

- Rewrite `AGENTS.md` into a concise ASCII-only guide.
- Keep implementation-critical guidance: project snapshot, ports, repo layout, OpenSpec planning, worktree usage, verification, secrets, off-limits files, API/config gotchas, and scoped-change expectations.
- Remove stale multi-agent handoff assumptions, excessive PR etiquette, duplicated command tables, and old `.agents` workflow references.
- Clarify that implementation work uses sibling worktrees, while planning-only OpenSpec artifact work may happen in the current checkout.
- Clarify verification expectations for app code, docs/planning-only changes, and test-only changes.
- Do not change application code.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `openspec-planning-migration`: Refines the repository guidance requirement so `AGENTS.md` becomes a concise OpenSpec-aligned agent guide instead of a broad process manual.

## Impact

- `AGENTS.md`: rewritten for clarity and current workflow.
- `openspec/specs/openspec-planning-migration/spec.md`: updated after archive with the refined guidance requirement.
- No application source, runtime behavior, dependencies, or API contracts change.

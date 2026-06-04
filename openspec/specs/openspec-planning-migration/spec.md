# openspec-planning-migration Specification

## Purpose
TBD - created by archiving change migrate-agent-roadmap-to-openspec. Update Purpose after archive.
## Requirements
### Requirement: Legacy agent planning content is classified before removal
The repository planning migration SHALL classify useful `.agents/ROADMAP.md` content before deleting the legacy `.agents` workflow.

#### Scenario: Immediate portfolio work is found
- **WHEN** a roadmap item describes concrete work needed for portfolio readiness
- **THEN** it is captured as an OpenSpec change recommendation
- **AND** it is not left only in `.agents/ROADMAP.md`

#### Scenario: Future backlog work is found
- **WHEN** a roadmap item is useful but not needed for immediate portfolio readiness
- **THEN** it is captured as a GitHub issue recommendation
- **AND** it is not added as long-form backlog content in the README

#### Scenario: Public-facing project highlights are found
- **WHEN** a roadmap item is relevant to recruiters or hiring managers
- **THEN** it is captured as concise README-facing presentation content

#### Scenario: Weak or stale content is found
- **WHEN** a roadmap item is stale, duplicated, completed, or too speculative to track
- **THEN** it is discarded instead of migrated

### Requirement: Legacy agent workflow is removed from repository guidance
The repository guidance SHALL stop requiring `.agents/ROADMAP.md`, `.agents/PLAN.md`, and `.agents/STATUS.md` once useful roadmap content has been classified, and SHALL direct agents toward concise OpenSpec-centered planning guidance instead.

#### Scenario: Agent guidance is updated
- **WHEN** maintainers read `AGENTS.md`
- **THEN** the guidance points agents toward OpenSpec changes for planned work
- **AND** it no longer instructs agents to maintain `.agents` handoff files

#### Scenario: Legacy files are removed
- **WHEN** useful legacy planning content has been captured
- **THEN** `.agents/ROADMAP.md`, `.agents/PLAN.md`, and `.agents/STATUS.md` are removed from the active repository workflow

#### Scenario: OpenSpec workflow is concise
- **WHEN** agents read the planning guidance
- **THEN** the guidance describes explore, propose, apply, and archive at a practical level
- **AND** it avoids duplicating detailed OpenSpec instructions that are already handled by skills and CLI artifacts

### Requirement: Agent guidance is concise and implementation-critical
`AGENTS.md` SHALL provide only the repository guidance agents need before editing or planning work.

#### Scenario: Agent reads repository guidance
- **WHEN** an agent opens `AGENTS.md`
- **THEN** it can quickly identify the project architecture, service ports, repo layout, planning workflow, worktree expectations, verification policy, secrets rules, off-limits files, and contract gotchas
- **AND** it is not required to read stale PR etiquette, old handoff rules, duplicated command tables, or broad process narration

#### Scenario: Guidance uses portable text
- **WHEN** `AGENTS.md` is displayed in a terminal or CLI session
- **THEN** it uses ASCII-safe diagrams and punctuation
- **AND** it does not contain mojibake or corrupted Unicode characters

#### Scenario: Planning-only work is distinguished from implementation
- **WHEN** an agent creates or updates OpenSpec planning artifacts without changing application code
- **THEN** the guidance allows that work in the current checkout unless the user directs otherwise
- **AND** implementation work still happens in a sibling worktree on a feature branch

#### Scenario: Verification guidance matches change type
- **WHEN** an agent completes a docs or planning-only change
- **THEN** the guidance does not require runtime Docker log verification
- **AND** app-code changes and test-only changes still have appropriate verification expectations


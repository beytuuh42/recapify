## ADDED Requirements

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
The repository guidance SHALL stop requiring `.agents/ROADMAP.md`, `.agents/PLAN.md`, and `.agents/STATUS.md` once useful roadmap content has been classified.

#### Scenario: Agent guidance is updated
- **WHEN** maintainers read `AGENTS.md`
- **THEN** the guidance points agents toward OpenSpec changes for planned work
- **AND** it no longer instructs agents to maintain `.agents` handoff files

#### Scenario: Legacy files are removed
- **WHEN** useful legacy planning content has been captured
- **THEN** `.agents/ROADMAP.md`, `.agents/PLAN.md`, and `.agents/STATUS.md` are removed from the active repository workflow

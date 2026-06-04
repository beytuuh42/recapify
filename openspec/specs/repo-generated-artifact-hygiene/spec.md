# repo-generated-artifact-hygiene Specification

## Purpose
TBD - created by archiving change migrate-agent-roadmap-to-openspec. Update Purpose after archive.
## Requirements
### Requirement: Generated and runtime artifacts are ignored
The repository SHALL ignore generated, dependency, cache, and runtime files that are not intended to be committed.

#### Scenario: Python generated artifacts are created
- **WHEN** Python runs tests or application code
- **THEN** `__pycache__` directories and Python bytecode files are ignored by Git

#### Scenario: ML local cache files are created
- **WHEN** the ML service writes local summary cache files under `ml/app/.cache`
- **THEN** those generated cache files are ignored by Git

#### Scenario: Frontend generated artifacts are created
- **WHEN** Angular, npm, or local frontend builds create dependency, build, or framework cache directories
- **THEN** `frontend/node_modules`, `frontend/dist`, and `frontend/.angular` are ignored by Git

### Requirement: Obsolete agent ignore exceptions are removed
The repository SHALL remove `.agents` ignore exceptions when the legacy `.agents` planning workflow is retired.

#### Scenario: Ignore rules are updated
- **WHEN** `.gitignore` is reviewed after the planning migration
- **THEN** it no longer preserves `.agents/ROADMAP.md` as a tracked exception
- **AND** it does not imply that `.agents` is part of the active workflow


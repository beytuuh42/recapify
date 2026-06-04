## 1. Classify Legacy Planning Content

- [x] 1.1 Read `.agents/ROADMAP.md` and classify each item as immediate OpenSpec work, GitHub issue recommendation, README highlight, or discard.
- [x] 1.2 Create a written migration summary that lists the immediate OpenSpec change recommendations.
- [x] 1.3 Create a written GitHub issue recommendation list for non-immediate backlog ideas.
- [x] 1.4 Identify stale, duplicated, completed, or speculative roadmap items that should not be migrated.

## 2. Update Repository Workflow

- [x] 2.1 Update `AGENTS.md` to remove `.agents/ROADMAP.md`, `.agents/PLAN.md`, and `.agents/STATUS.md` workflow requirements.
- [x] 2.2 Update `AGENTS.md` to direct agents toward OpenSpec changes, tasks, and archived decisions as the planning source of truth.
- [x] 2.3 Remove obsolete `.agents` ignore exceptions from `.gitignore`.
- [x] 2.4 Remove `.agents/ROADMAP.md`, `.agents/PLAN.md`, and `.agents/STATUS.md` after useful content has been captured.

## 3. Ignore Generated Artifacts

- [x] 3.1 Add ignore rules for Python generated artifacts, including `__pycache__` and `*.py[cod]`.
- [x] 3.2 Add ignore rules for ML local cache files under `ml/app/.cache`.
- [x] 3.3 Add ignore rules for frontend generated artifacts, including `frontend/node_modules`, `frontend/dist`, and `frontend/.angular`.

## 4. README Backlog Cleanup

- [x] 4.1 Review `README.md` current limitations and next steps.
- [x] 4.2 Keep only concise recruiter-facing future work in the README.
- [x] 4.3 Move detailed future-product and research ideas to the GitHub issue recommendation list instead of README prose.

## 5. Verify

- [x] 5.1 Confirm `git status` no longer shows generated/cache files that should be ignored.
- [x] 5.2 Confirm OpenSpec status reports this change as complete after all artifacts are present.
- [x] 5.3 Inspect the final diff to ensure no application feature implementation was included.

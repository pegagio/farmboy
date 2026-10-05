# Tasks: Agent Python Environment

**Input**: Design documents from `specs/019-catalog-python-runtime-prerequisites/`

**Prerequisites**: Reviewed `spec.md` and `plan.md`; supporting decisions in `research.md`, `data-model.md`, `contracts/`, and `quickstart.md`.

**Organization**: Tasks are grouped by user story. No separate project-initialization or foundational work is required; the implementation uses the existing mise/uv setup.

## Phase 1: User Story 1 — Use PyYAML Without Setup Thrash (Priority: P1) 🎯 MVP

**Goal**: Prepare one project-local Python environment that the agent's documented invocation can use to perform safe YAML operations, with truthful checks and non-destructive handling of existing state.

**Independent Test**: In a clean disposable checkout, follow the preparation steps and run the documented `mise exec -- python` command. It selects the checkout's `.venv`, reports the pinned Python and PyYAML versions, and safely round-trips representative YAML. Check and preparation failures for absent or conflicting environments remain actionable and do not silently replace existing paths.

- [X] T001 [US1] Pin the required package as `PyYAML==6.0.3` in `requirements-agent.txt`.
- [X] T002 [US1] Configure existing-venv activation plus `python:prepare` and read-only `python:check` tasks in `mise.toml`; preparation must create only an absent `.venv`, use the installed mise Python with uv and `--no-python-downloads`, install into that explicit environment, and preserve/report existing or failed state as specified in `contracts/python-runtime.md`.
- [X] T003 [US1] Add focused disposable-fixture regression coverage for fresh preparation, explicit interpreter selection, and preservation when preparation encounters an existing path in `tests/test_agent_python_environment.py`.
- [X] T004 [US1] Run the clean-environment, ready-repeat, missing-package, existing-path, and package-acquisition-failure scenarios from `quickstart.md` in disposable checkouts; verify failed acquisition is reported truthfully without a success/readiness claim, the incomplete new environment fails `python:check`, and recovery guidance is actionable; record actual commands, interpreter/prefix, tool and package versions, outcomes, and failures/retries in `specs/019-catalog-python-runtime-prerequisites/validation.md`.

## Phase 2: User Story 2 — Know Which Python to Use (Priority: P1)

**Goal**: Let the agent identify and use the prepared repository environment during ordinary work, including between skill invocations, while preserving the higher-priority skill-tools instruction.

**Independent Test**: In a new non-interactive repository shell, follow `AGENTS.md` and confirm `mise exec -- python` selects the prepared local environment and imports PyYAML; confirm the skill-tools exception remains explicit.

- [X] T005 [US2] Document ordinary Python invocation, preparation/check expectations, failure recovery, and the skill-tools exception in `AGENTS.md`.
- [X] T006 [P] [US2] Add concise preparation and agent-environment pointers to `README.md` and `docs/installation.md`, keeping agent-environment setup distinct from bundle installation.

## Phase 3: User Story 3 — Consider Useful Additional Tools (Priority: P2)

**Goal**: Keep the agent dependency set evidence-based and provide a complete, reusable setup recipe for an explicitly adopting project.

**Independent Test**: The utility assessment gives each considered candidate a demonstrated use or failure, an alternative, a maintenance cost, and a disposition. In a second clean disposable project, use only the delivered guide to prepare and check the local environment; a separate existing-configuration fixture preserves unrelated settings and surfaces conflicts before changing them.

- [X] T007 [US3] Create `docs/agent-python-environment.md` with the complete copyable requirements, mise pins/activation and preparation/check task definitions, ignore guidance, agent instructions, prerequisites, adoption steps, verification, recovery, and existing-configuration merge rules from `contracts/python-runtime.md` and `quickstart.md`.
- [X] T008 [US3] Adopt the delivered recipe in a clean second disposable project without `.specify`, source-checkout helpers, or copied `.venv`; run preparation and the same direct YAML check, then record copied inputs and observed versions/results in `specs/019-catalog-python-runtime-prerequisites/validation.md`.
- [X] T009 [US3] Exercise the existing-configuration and pre-existing-environment fixture from `quickstart.md`; verify unrelated settings and the environment sentinel remain unchanged, surface conflicting keys for an operator decision, and record observations in `specs/019-catalog-python-runtime-prerequisites/validation.md`.

## Final Phase: Evidence and Scope Review

**Purpose**: Confirm the delivered feature remains within its approved scope and preserves the motivating historical evidence.

- [X] T010 Compare the final dependency and environment changes with the included/excluded utility dispositions in `specs/019-catalog-python-runtime-prerequisites/research.md`; verify the relevant Feature 017 record in `specs/017-flowkit-agent-configuration/follow-up.md` and original evidence remain unchanged, and record the paths and observed preservation in `specs/019-catalog-python-runtime-prerequisites/validation.md`.
- [X] T011 Replace the "keep versions if suitable" guidance in `docs/agent-python-environment.md` with the validated boundary: the unchanged recipe and check support Python `3.11.16`; leave differing existing pins untouched pending an operator decision and do not claim those alternatives are validated. Recheck the complete recipe and existing-configuration protections against `specs/019-catalog-python-runtime-prerequisites/plan.md` and the guide's check instructions, then record the focused result in `specs/019-catalog-python-runtime-prerequisites/validation.md`. Depends on completed T007 and T009.

## Dependencies & Execution Order

### Phase Dependencies

- **User Story 1 (Phase 1)**: No implementation dependency; delivers the prepared and checked local environment MVP.
- **User Story 2 (Phase 2)**: Depends on User Story 1 so the usage instructions name implemented tasks and invocation behavior.
- **User Story 3 (Phase 3)**: Depends on User Story 2 because the portable recipe must reproduce the implemented environment and agent guidance. Its clean and existing-configuration adoption checks proceed in order because they append evidence to the same validation record.
- **Evidence and Scope Review (Final Phase)**: Depends on all three stories and their recorded validation.

### User Story Dependencies

- **User Story 1 (P1)**: Can start immediately; no other user story dependency.
- **User Story 2 (P1)**: Starts after User Story 1.
- **User Story 3 (P2)**: Starts after User Story 2; uses the implemented source setup as the recipe baseline.

### Parallel Opportunities

- T005 and T006 can proceed in parallel after User Story 1 because they edit different guidance files.
- No other tasks are marked parallel: setup, tests, recipe, and adoption evidence depend on the artifacts or results of earlier tasks.

## Implementation Strategy

### MVP First (User Story 1)

1. Complete T001–T003.
2. Complete T004 in disposable checkouts and record actual results.
3. Confirm the direct invocation selects the project `.venv` and safely round-trips YAML before relying on the environment.

### Incremental Delivery

1. Deliver the PyYAML environment and preparation/check behavior (User Story 1).
2. Add ordinary agent usage guidance and concise project pointers (User Story 2).
3. Publish the copyable FlowKit recipe, prove clean-project adoption and existing-configuration preservation (User Story 3).
4. Complete the final scope and historical-evidence review.

### Corrective Follow-up Dependency

- T011 depends on completed T007 and T009 so the correction can be checked against the delivered guide and its existing-configuration protection.

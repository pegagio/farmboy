---

description: "Task list for Workflow Branch Validation and Controller Integration Coverage"
---

# Tasks: Workflow Branch Validation and Controller Integration Coverage

**Input**: Design documents from `specs/023-workflow-branch-validation-controller-integration/`

**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, and both contracts in `contracts/`

**Tests**: Regression and integration tests are required by FR-007 and FR-013–FR-016. Add focused failing tests before their corresponding implementation where practical.

**Organization**: Tasks follow the four prioritized user stories. Existing controller, graph, catalog, lifecycle, and disposable snapshot tests are the implementation surface; no project initialization or dependency setup is needed.

## Table of Contents

- [Phase 1: Setup](#phase-1-setup)
- [Phase 2: Foundational](#phase-2-foundational-shared-scenario-contract)
- [Phase 3: User Story 1](#phase-3-user-story-1---reject-invalid-definitions-before-delivery-priority-p1--mvp)
- [Phase 4: User Story 2](#phase-4-user-story-2---execute-only-the-selected-valid-route-priority-p1)
- [Phase 5: User Story 3](#phase-5-user-story-3---continue-after-independently-reviewed-progress-priority-p1)
- [Phase 6: User Story 4](#phase-6-user-story-4---trust-installed-consumer-regression-results-priority-p2)
- [Phase 7: Polish & Cross-Cutting Concerns](#phase-7-polish--cross-cutting-concerns)
- [Dependencies & Execution Order](#dependencies--execution-order)
- [Parallel Opportunities](#parallel-opportunities)
- [Implementation Strategy](#implementation-strategy)
- [Notes](#notes)

## Phase 1: Setup

**Purpose**: Confirm the existing project structure is the implementation target.

No setup tasks are required. This feature extends existing source, tests, fixtures, and documentation; it adds no dependency or build tool.

---

## Phase 2: Foundational (Shared Scenario Contract)

**Purpose**: Keep connected source and installed scenarios comparable while story-specific coverage is added.

- [x] T001 Extend the existing scenario fixture in `tests/consumer-fixtures/workflow-improvements/implementation-scope-cases.json` with stable scenario IDs, requirement IDs, valid-control references, one-mutation negative cases, and expected production outcomes for Feature 023; keep it as scenario input data and do not encode routing or guard decisions in the fixture.

**Checkpoint**: Shared scenarios can drive story-specific source and disposable-consumer checks without introducing another executor.

---

## Phase 3: User Story 1 - Reject invalid definitions before delivery (Priority: P1) 🎯 MVP

**Goal**: Reject malformed owned workflow definitions and impossible producer references before installation or workflow effects, with actionable diagnostics.

**Independent Test**: Run source/catalog validation over all ten active owned definitions and deprecated stop-only Start Feature; valid supported empty branches pass, invalid structure and producer cases fail with exact diagnostics and zero delivery or dispatch effects.

### Tests for User Story 1

- [x] T002 [P] [US1] Add controller definition tests in `tests/test_controller.py` for misplaced `cases.default`, malformed root/node/case/default containers, supported empty branches, and unknown, self, forward, cross-branch, and post-join-infeasible producer references; assert stable lowercase hyphenated `reason_code` values, exact node IDs, and root `location: workflow` or `steps` with an explicit null `step_id`, as required by `data-model.md` and `contracts/validation-boundaries.md`; exclude raw input values, rendered prompts, and host paths.
- [x] T003 [P] [US1] Add source inventory and graph tests in `tests/test_workflow_graph.py` and `tests/test_workflow_paths.py` proving every owned package is validated, valid earlier-producer references do not require pre-production outputs, and the deprecated Start Feature remains stop-only.
- [x] T004 [US1] Add catalog boundary tests in `tests/test_catalog.py` that attempt invalid source build, development snapshot, verification, and install/refresh from disposable inputs, assert rejection before package or consumer writes, and compare consumer before/after inventories.

### Implementation for User Story 1

- [x] T005 [US1] Extend `validate_workflow_definition()` and its graph/template helpers in `controllers/farmboy/scripts/python/controller.py` to validate malformed branch structures, reserve `default` as a sibling of `cases`, accept supported empty lists, and prove producer order and route feasibility with bounded prior-producer propagation; retain the existing `ValueError` failure contract and loop-condition/carrier rules.
- [x] T006 [US1] Project contextual definition diagnostics from `tools/validate_workflows.py` and validate source definitions before catalog packaging, release verification, development-snapshot approval, and delivery effects in `tools/catalog.py`; preserve existing ownership and installation checks.

**Checkpoint**: Source and catalog boundaries reject invalid definitions before delivery effects, while supported empty branches and feasible producer references remain valid.

---

## Phase 4: User Story 2 - Execute only the selected valid route (Priority: P1)

**Goal**: Render and check inputs only at the selected consuming boundary; preserve skips and supported empty/default routes.

**Independent Test**: Exercise production `render_template()` and `select_switch_branch()` behavior for preparation/source skips, empty/default choices, and delayed producer output; assert missing selected outputs block before the consuming effect and untaken outputs are never required.

### Tests for User Story 2

- [x] T007 [P] [US2] Extend `tests/test_implement_switch_routing.py` with production-route cases for both preparation/source skips, empty cases, empty top-level defaults, unknown choices without a fallback, and zero execution of untaken branch children.
- [x] T008 [P] [US2] Extend `tests/test_workflow_paths.py` and `tests/test_controller.py` with runtime rendering cases proving earlier producer references pass definition validation before production, are resolved only when consumed, and reject missing, invalid, or stale prior-pass outputs before affected effects.

### Implementation for User Story 2

- [x] T009 [US2] Update selected-route traversal and runtime preflight in `controllers/farmboy/scripts/python/controller.py` to render switch expressions/applicable metadata, select through `select_switch_branch()`, and render selected children only at consumption; preserve `render_template(value, inputs, outputs)`, current-output validation, and existing successor/guard behavior.
- [x] T010 [US2] Update the rendering and selected-child boundaries in `controllers/farmboy/controller-protocol.md` and `workflows/README.md` so the manual-prompt route observes the same selected-only rendering and safe-stop behavior as native dispatch.

**Checkpoint**: Supported skips and empty selections reach their declared successors without branch-local effects; selected missing inputs stop before their consumer.

---

## Phase 5: User Story 3 - Continue after independently reviewed progress (Priority: P1)

**Goal**: Prove connected, authorized continuation after genuine reviewed progress while retaining original historical evidence and applying current guards independently.

**Independent Test**: Run task-resolution and reviewed-source-correction sequences through assessment, eligible dispatch, independent review, marker-only tracking, actual post-pass capture, and guarded re-entry; then vary one negative guard per otherwise-valid control and assert its blocker and zero later dispatch.

### Tests for User Story 3

- [x] T011 [P] [US3] Add connected positive expectations in `tests/test_snapshot_validation.py` and scenario records in `tests/consumer-fixtures/workflow-improvements/implementation-scope-cases.json` for task resolution followed by marker-only tracking and for genuine reviewed source correction; assert historical scope/assessment/preimage digests remain unchanged while current evidence is rechecked.
- [x] T012 [P] [US3] Add attributable negative controls in `tests/test_implementation_progress.py` and `tests/test_controller.py` for forged, altered, missing, or unbound historical proof; stale current review; unauthorized task edits; missing or wrong-branch required outputs; no substantive progress; and each existing exhausted budget. Add otherwise-valid administrative-only, answer-only, marker-only, and fresh-child-session variants and assert none creates substantive resolution, reconstructs historical proof, or resets existing counters/budgets; retain same-child answer relay and independently reviewed genuine-progress controls. Each case must establish a valid control, mutate one guard, and assert the expected reason/action with no subsequent source dispatch.
- [x] T013 [US3] Extend `tests/test_phase_lifecycle.py` with regression assertions for applied roadmap-preimage readback: preserve receipt/effect identity and mutation count without invoking the writer again, and continue rejecting a separately changed non-roadmap artifact.

### Implementation for User Story 3

- [x] T014 [US3] Extend `tests/implementation_scope_snapshot.py` to execute the two connected positive traces using production rendering, branch selection, activation/history, task tracking, actual post-pass capture, and guarded progress/route helpers; use the existing exact `post-pass-capture` request fields `scope`, `trusted_request_reference`, `retained_scope_sha256`, `entry_history_sha256`, `task_tracking_successors`, `producer_pairs`, `eligibility_request`, `completion_branch`; record selected and prevented steps and counters without copying controller decisions into the harness. Assert successful traces produce zero undeclared workflow or phase dispatch, Git integration, real-roadmap verification, or feature/consumer acceptance effects.
- [x] T015 [US3] Extend `tests/implementation_scope_snapshot.py` to run each negative mutation from its valid control and capture the production blocker/action, zero later dispatch, unchanged retained records, and unchanged counters; cover assignment, unresolved gate, same-child answer relay, installation-drift stops, and the administrative-only, answer-only, marker-only, and fresh-child-session non-credit variants without fallback. Assert none reconstructs historical proof or resets budgets, and blocked traces produce zero undeclared workflow or phase dispatch, Git integration, real-roadmap verification, or feature/consumer acceptance effects.

**Checkpoint**: Both positive re-entry traces preserve their original historical bindings and current checks; each negative guard blocks for its intended reason without granting progress or resetting limits.

---

## Phase 6: User Story 4 - Trust installed-consumer regression results (Priority: P2)

**Goal**: Establish source parity with a supported disposable installed snapshot and emit portable observations whose claims match the execution mode.

**Independent Test**: Run the same route, definition, connected positive, and connected negative scenarios against source and installed modules/workflow bytes; require matching decisions and inspect complete provenance and honest deterministic-evidence labels.

### Tests for User Story 4

- [x] T016 [US4] Extend `tests/test_snapshot_validation.py` with paired source/installed assertions for valid skips and empty/default routes, malformed definition rejection, producer timing, both positive connected traces, all FR-009 negative guards, and matching selected/prevented steps, blockers, current-evidence decisions, and counters. Include lifecycle receipt-readback parity and successful/blocked trace assertions for zero undeclared workflow or phase dispatch, Git integration, real-roadmap verification, or feature/consumer acceptance effects; the disposable lifecycle execution is added in T018.
- [x] T017 [US4] Add portable-observation contract tests in `tests/test_snapshot_validation.py` for component IDs/versions/raw digests, repository-relative coordinates, tested CLI/runtime, installed inventory, scenario and requirement IDs, execution mode, expected/observed results, effects/dispatch, valid control, and parity; reject absolute paths, personal identifiers, secrets, and raw transcripts.

### Implementation for User Story 4

- [x] T018 [US4] Extend the supported disposable development-snapshot setup in `tests/implementation_scope_snapshot.py` and `tests/test_snapshot_validation.py` to load the same scenario descriptions against source and installed controller modules and workflow bytes; include a disposable applied-roadmap receipt readback/reassessment through the installed production lifecycle module as well as source, without mutating Feature 023's real roadmap. Assert no second writer invocation and unchanged receipt identity, timestamp, digest, and mutation count, then reject a separately changed non-roadmap artifact; use the existing catalog installer and initialized-consumer prerequisites, and fail when any required integration prerequisite is missing instead of counting a skip as parity. Preserve commit `54b394e` as a regression baseline rather than reimplementing its fix.
- [x] T019 [US4] Extend the feature-local observation writer in `tests/implementation_scope_snapshot.py` to record actual provenance, expected/observed outcomes, effects, retained before/after hashes, counters, valid-control/mutation references, and source/installed parity; include lifecycle effect and receipt identity, timestamp/digest, mutation count, retained receipt/preimage, and non-roadmap current-hash rejection observations. Enforce `Repository-relative coordinates only, with no host paths, personal identifiers, secrets or raw transcripts.` Label deterministic Reviewer/Tasker outcomes as deterministic; they cannot establish native agent identity/settings, publication, stock compatibility, adoption or acceptance.

**Checkpoint**: Every required source/installed scenario agrees or reports a parity failure; observations disclose actual provenance and do not imply live-agent execution or broader acceptance.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Document diagnostics, safe next actions, and the limits of observed evidence; complete focused validation.

- [x] T020 [P] Document definition/runtime boundaries, diagnostic interpretation, selected-route input timing, safe next actions, and deterministic evidence limits in `docs/installation.md` and `tests/consumer-fixtures/README.md`.
- [x] T021 Run the focused source and disposable-consumer commands in `specs/023-workflow-branch-validation-controller-integration/quickstart.md`, record actual CLI/runtime and component/source digests in feature-local `specs/023-workflow-branch-validation-controller-integration/validation/`, and report any unavailable prerequisite or failed parity scenario without claiming broader compatibility or acceptance.

---

## Dependencies & Execution Order

The order below keeps shared scenario input and production boundaries ahead of dependent stories, while preserving the existing single-file ownership constraints.

### Phase Dependencies

- **Setup (Phase 1)**: No initialization is required for this existing repository.
- **Foundational (Phase 2)**: Complete T001 before story work so scenarios have stable IDs and control/mutation structure.
- **User Stories**: US1 follows T001; US2 follows T001 and may use the validator outcome from T005. US3 follows T001 and the established production route/runtime boundaries from T005 and T009. US4 follows the source behaviors and connected harness from US1–US3. Within each story, add its tests before the corresponding implementation where practical.
- **Polish (Phase 7)**: Complete after the desired story work; T021 follows T020 and all source/installed scenario tasks.

### User Story Dependencies

- **US1 (P1)**: Depends on T001; independently testable at source/catalog definition and delivery boundaries.
- **US2 (P1)**: Depends on T001 and US1's shared validator behavior; independently testable at selected-route and input-consumption boundaries.
- **US3 (P1)**: Depends on T001, US1, and US2 production routing; preserves existing WR-01/WR-02 and commit `54b394e` roadmap-preimage behavior as regression baselines, without reimplementing those fixes.
- **US4 (P2)**: Depends on source cases in US1–US3 and the connected scenario harness; installed checks must use matching supported development-snapshot bytes.

### Within Each User Story

- Write or extend the focused regression expectation before changing its production behavior where practical.
- Keep definition feasibility separate from runtime output availability and from historical/current evidence validation.
- Each negative continuation case starts from a valid positive control and changes only its own guard.
- Keep tasks that edit the same file in execution order; parallel markers below apply only to disjoint files with satisfied dependencies.

### Parallel Opportunities

- After T001, T002 and T003 can proceed in parallel because they edit separate test files; T004 is catalog-test work and may also proceed in parallel with those tests.
- After T001, T007 and T008 can proceed in parallel because their test files are disjoint.
- Within US3, T011 and T012 may proceed in parallel; T013 uses a separate lifecycle test file and can proceed alongside them.
- Within US4, T017 must follow T016 because both change `tests/test_snapshot_validation.py`; do not parallelize them. T018 and T019 both modify `tests/implementation_scope_snapshot.py` and are sequential.
- Do not parallelize production edits to `controllers/farmboy/scripts/python/controller.py` across US1 and US2, or edits to `tools/catalog.py` and catalog tests across US1 tasks.

- **US2 example**: After T001, T007 (`tests/test_implement_switch_routing.py`) and T008 (`tests/test_workflow_paths.py`, `tests/test_controller.py`) may run in parallel because their file ownership is disjoint. T009 follows both tests and T005's validator work because it changes the shared controller; T010 follows T009 for the protocol and manual-prompt behavior.
- **US3 example**: After T001, T011 (`tests/test_snapshot_validation.py` and scenario fixture) and T012 (`tests/test_implementation_progress.py`, `tests/test_controller.py`) may run in parallel. T013 may proceed alongside them in `tests/test_phase_lifecycle.py`. T014 and T015 then run sequentially because both own `tests/implementation_scope_snapshot.py` and T015 builds on the positive traces.
- **US4 example**: Execute sequentially: T016 owns paired assertions in `tests/test_snapshot_validation.py`; T017 follows because it edits that same file; T018 follows T016/T017 while extending the shared snapshot harness and installed lifecycle case; T019 follows T018 to add its observation fields in that harness. The shared files make parallel assignment unsafe.

---

## Parallel Example: User Story 1

```text
After T001, assign the disjoint test changes independently:
- T002: controller definition tests in tests/test_controller.py
- T003: source inventory/path tests in tests/test_workflow_graph.py and tests/test_workflow_paths.py
- T004: delivery-boundary tests in tests/test_catalog.py
Then implement the shared validator and its delivery callers in dependency order through T005 and T006.
```

---

## Implementation Strategy

The strategy delivers the independently testable P1 definition boundary first, then adds runtime, continuation, and installed parity coverage in dependency order.

### MVP First (User Story 1 Only)

1. Complete T001 and the US1 tests T002–T004.
2. Implement T005–T006.
3. Validate all owned definitions and catalog/delivery rejection boundaries; supported empty branches and earlier producers must still pass.
4. Stop at the US1 checkpoint before proceeding to route/runtime or continuation work.

### Incremental Delivery

1. Deliver US1 definition and pre-delivery validation.
2. Add US2 selected-route rendering and consumption timing.
3. Add US3 connected reviewed-progress continuation and attributable guard controls, retaining WR-01/WR-02 and the existing `54b394e` lifecycle fix as regression baselines.
4. Add US4 supported installed parity and portable observations.
5. Complete the documentation and quickstart checks in Phase 7; unavailable installed prerequisites remain an explicit coverage gap.

### Parallel Team Strategy

After T001, disjoint story test files may be prepared in parallel where their listed dependencies are satisfied. Keep shared controller edits, the connected scenario adapter, and snapshot test changes ordered by file ownership. User story phases remain ordered because later coverage consumes earlier production behavior.

## Notes

- Every task is a checklist item with a sequential ID and a concrete repository path; story tasks carry the matching `[US1]`–`[US4]` label.
- `[P]` appears only on independent test or documentation tasks in disjoint files.
- Data-model constraints are captured in T002, T014–T019: diagnostic identifiers are stable lowercase hyphenated strings; root failures use `location: workflow` or `steps` and an explicit null `step_id`; node errors identify the exact node; do not include raw input values, rendered prompts or host paths; repository-relative coordinates only, with no host paths, personal identifiers, secrets or raw transcripts; simulated role labels are deterministic and cannot establish native agent identity/settings.
- The exact existing `post-pass-capture` request fields remain `scope`, `trusted_request_reference`, `retained_scope_sha256`, `entry_history_sha256`, `task_tracking_successors`, `producer_pairs`, `eligibility_request`, `completion_branch`; no new production persistence format is introduced.
- No task changes the specification, plan, contracts, roadmap, released metadata, external project, continuation accounting policy, or installed active consumer. No task creates a new engine, framework, dependency, or build tool.
- No task reimplements completed WR-01, WR-02, or commit `54b394e` behavior; those remain regression baselines.

## Phase 8: Convergence

- [x] T022 [US1] Extend `validate_workflow_definition()` in `controllers/farmboy/scripts/python/controller.py` so malformed do-while `steps`, unsupported switch `transition_labels`, and unknown template `prompt` references raise contextual `WorkflowDefinitionError` diagnostics while preserving `ValueError` compatibility and existing carrier/assignment guards; add valid-control/one-mutation assertions in `tests/test_controller.py` and `tests/test_workflow_graph.py` for stable reason codes, workflow IDs, exact consumer/switch step IDs (`step_id`), field locations, offending references, and actionable corrections per F023-CONVERGE-DIAGNOSTIC-CONTEXT / FR-002 / SC-001 / `contracts/validation-boundaries.md` (partial).
- [x] T023 [US1] Project the contextual definition diagnostics through the inventory JSON handler in `tools/validate_workflows.py` and add focused projection assertions in `tests/test_catalog.py` for malformed loop bodies, unsupported route labels, and unknown template inputs, including portable workflow/step/field/reference/correction fields per F023-CONVERGE-DIAGNOSTIC-CONTEXT / FR-002 / SC-001 / `contracts/validation-boundaries.md` (partial); depends on T022.

## Phase 9: Convergence

- [X] T024 [US1] Extend template-form validation in `controllers/farmboy/scripts/python/controller.py` to return contextual `WorkflowDefinitionError` diagnostics for unsupported expressions and malformed template delimiters while preserving `ValueError` compatibility; add valid-control/one-mutation assertions for workflow ID, consuming step ID, field location, offending reference, and correction in `tests/test_controller.py` and `tests/test_workflow_graph.py`, plus portable inventory JSON projection assertions in `tests/test_catalog.py` per F023-CONVERGE-UNSUPPORTED-TEMPLATE-FORM / FR-002 / SC-001 / `contracts/validation-boundaries.md` (partial); depends on T022 and T023.

## Phase 10: Convergence

- [X] T025 [US1] Preserve authored graph locations when `validate_workflow_definition()` traverses a do-while body by passing the loop node `.steps` prefix to recursive `visit()` in `controllers/farmboy/scripts/python/controller.py`; add valid loop-with-switch controls and single-mutation assertions in `tests/test_controller.py` and `tests/test_workflow_graph.py` for `steps[0].steps[0].transition_labels`, then assert that same location in actual portable inventory JSON through `tools/validate_workflows.py` and `tests/test_catalog.py` per F023-CONVERGE-NESTED-GRAPH-LOCATION / FR-002 / SC-001 / `contracts/validation-boundaries.md` Definition Boundary (partial); depends on T022 and T023.

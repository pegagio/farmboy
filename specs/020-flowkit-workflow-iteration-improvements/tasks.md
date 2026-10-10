---
description: "Dependency-ordered implementation tasks for Feature 020"
---

# Tasks: FlowKit Workflow Iteration and Improvements

**Input**: Design documents from `specs/020-flowkit-workflow-iteration-improvements/`

**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, and `quickstart.md`

**Organization**: Tasks are grouped by the seven user stories. Owner and approval gates are explicit dependencies; they do not grant approval or authorize external source changes.

**Sequencing amendment (2026-10-06)**: T037 remains pending for development-snapshot validation in a disposable initialized consumer. Production catalog release moved to the separate [post-closeout release handoff](post-closeout-release.md), with the prior T037 release wording retained there; this release is not a prerequisite for Feature 020 implementation, convergence, or closeout.

**Historical status assessment (2026-10-07, before lifecycle amendment)**: The October 6 deferral and sequencing amendment above are preserved as history. The October 7 `validation/roadmap-delivery.json` records six passing native Write trials for flow-roadmap 0.2.1 under Specify 1.0.10.dev0+pegagio.2, compatible within those tested cases, with zero demonstrated component incompatibilities and no roadmap pin change. T004's verification has resumed and those six trials are complete; T012's conditional extension delivery is not applicable on this evidence, so the existing pin remains unchanged. This does not establish universal compatibility, effective settings, broader client compatibility, publication, or Feature 020 acceptance. The retained implementation and delivery records also substantiate the FlowKit helper, Checker definition, correction/recheck and startup routes, and T037's validated development-snapshot delivery; T037 is complete for that development delivery. Production release remains a separate post-closeout handoff. T048's source-and-delivered-owner-resolution prerequisite is complete. T027 remains open for its own combined demonstration and requires fresh preparation/readiness evidence against the delivered snapshot; earlier readiness evidence is stale for that purpose. T028–T032 remain open, including final validation, independent convergence/review, and acceptance evidence. Do not mark these verification tasks complete from the retained peer reports; their execution and evidence integration remain separate implementation work.
**Historical lifecycle amendment checkpoint (2026-10-07, before Story 7)**: At that checkpoint the file had 67 tasks, 51 completed, and 16 open; T050/T051 were completed and T052–T067 remained open. The prior-scope readiness review is stale for later artifact amendments and does not establish Story 7 behavior.

**Historical task-marker snapshot (2026-10-08, after Analyze/Remediate and before subsequent Implement marker tracking)**: At this snapshot the file had 77 unique tasks, 68 completed and 9 open (T064–T067, T071–T072, T075–T077); T050/T051 and T052–T063, T068–T070, T073–T074 were marked complete then. Retain this as historical context; the task checkboxes are the live checklist authority. `validation/lifecycle-owner-delivery.json` records owner source delivery, independent review, convergence, and bounded disposable validation. `validation/lifecycle-delivery.json` and `validation/implementation-scope-summary.md` record parent development-source and disposable-snapshot validation. These receipts do not establish production publication, unchanged primary installed snapshots, live native-agent behavior or effective settings, Linux validation, or Feature 020 acceptance. Production release remains a separate post-closeout handoff.

## Phase 1: Setup

**Purpose**: Establish portable evidence locations used by the implementation and validation work.

- [X] T001 [P] Create the Feature 020 validation evidence guide and record rules for portable paths, SHA-256 provenance, sanitized errors, and separate implementation, native-launch, effective-settings, and acceptance claims in `specs/020-flowkit-workflow-iteration-improvements/validation/README.md`.
- [X] T002 [P] Add immutable fixtures for `select-feature-explicit-choice-reprompt-20261003`, `select-feature-pointer-approval-stop-20261003`, `select-feature-explicit-intent-redundant-gates-20261005`, `analyze-unresolved-checklist-gate-20261003`, and `clarify-agent-thread-limit-preflight-20261003` with their historical component provenance in `tests/consumer-fixtures/workflow-improvements/observations.json`; preserve the original bytes in `.specify/workflow-feedback/exports/consolidated-workflow-issues-20261005/report.json`.

---

## Phase 2: Foundational Approval and Compatibility Baseline

**Purpose**: Record required governing approval and the unchanged Spec Kit startup boundary before FlowKit-owned readiness work. Historical roadmap deferral is superseded by the dated current-status note above, which limits the completed compatibility evidence to six trials.

- [X] T003 [P] Obtain explicit operator approval for the exact proposed Constitution II/AGENTS reconciliation or record the unresolved decision, including rationale, historical supersession, affected source, and active-work migration in `specs/020-flowkit-workflow-iteration-improvements/validation/governance.json`; approval must identify the exact amendment and does not itself change governing files.
- [X] T004 [P] **Deferred by operator on 2026-10-06.** When roadmap compatibility verification resumes, first exercise the existing Write behavior against direct bounded requests, inferred amendments, ambiguity, stale state, and unsafe recovery; record observed outcomes and current source coordinates, version, digest, and tested CLI in `specs/020-flowkit-workflow-iteration-improvements/validation/roadmap-delivery.json`. Request an owner-reviewed extension change only if a case demonstrates an actual incompatibility; preserve the current pin if tests pass, and do not edit independently owned or installed files.
- [X] T005 [P] Record the current Spec Kit CLI pin, actual core checklist-startup behavior, and relevant installed-core source/version provenance as a compatibility baseline in `specs/020-flowkit-workflow-iteration-improvements/validation/readiness-compatibility-baseline.json`; record the file as a compatibility baseline only (the former core-delivery proposal is superseded), confirm that Feature 020 leaves core source, templates, installed commands, and pins unchanged, and route readiness through FlowKit.
- [X] T033 After T003 receives explicit approval, ratify only that exact amendment in `.specify/memory/constitution.md` with the approved version and effective date, and record its impact report and active-work migration in `specs/020-flowkit-workflow-iteration-improvements/validation/governance.json`; if approval is pending, preserve the operative constitution and keep authority-dependent work blocked.
- [X] T011 After T033, reconcile the approved governing wording into applicable operational guidance in `AGENTS.md` and `controllers/flow-kit/controller-protocol.md`, documenting the approved migration in `specs/020-flowkit-workflow-iteration-improvements/validation/governance.json`; preserve current operative rules until T033 is complete.
- [X] T034 Add the reviewed read-only `FlowKit-Readiness Checker` native definition to `agents/flow-kit/agents/flowkit-readiness-checker.toml` and its source registration in `agents/flow-kit/manifest.yml`, using the approved `gpt-6-luna`/`medium` settings. Update `tests/test_agent_configs.py`, `tests/test_agent_delivery.py`, `tests/test_snapshot_validation.py`, `tests/consumer-fixtures/agent-delivery/scenarios.json`, and the relevant `tests/test_workflow_graph.py` fixtures/assertions to validate the additive ninth definition, exact configuration, package/snapshot preservation, and declared assignments; the completed eight-role evidence in T020/T021 does not cover this addition. Record source/package provenance in `specs/020-flowkit-workflow-iteration-improvements/validation/summary.md`. This defines a source assignment only and does not establish native availability or effective settings.

---

## Phase 3: User Story 1 - Carry Clear Intent into Feature Activation (Priority: P1)

**Goal**: Activate or verify the operator's uniquely identified eligible feature while preserving lifecycle, mapping, specification bytes, and unrelated pointer data.

**Independent Test**: Run deterministic reference fixtures and disposable-consumer first activation, repeat activation, existing-specification, authorized switch, and unsafe/conflicting-state cases. Verify the exact target and bytes, zero routine reconfirmation, and focused stops before unsafe mutation.

### Tests for User Story 1

- [X] T006 [US1] Reopen for F020-R001–F020-R004: extend `tests/test_workflow_improvements.py` with a genuine first-activation fixture where `.specify/feature.json` is absent; typed absent-pointer snapshot/revalidation and pointer-creation expectations; a competing mapping through an in-project symlink or normalized physical-directory alias that blocks before mutation; and direct-target versus ambiguous-selection rendered-route cases. Preserve all existing fixtures and add no permissive assertions.

### Implementation for User Story 1

- [X] T007 [US1] Implement typed stable-ID, exact-title, explicit-menu, and canonical-answer resolution with selected/ambiguous/missing/blocked results and no mutation in `controllers/flow-kit/scripts/python/selection.py`; preserve generic approval-menu semantics.
- [X] T008 [US1] After T011 ratifies governing and operational guidance, correct F020-R001 and F020-R004 in `controllers/flow-kit/scripts/python/controller.py`: represent absent pointer state explicitly in the activation snapshot, verify it remains absent immediately before effect, create only the pointer on first activation, retain blocking for malformed or unexpectedly changed existing pointers, and compare target ownership by validated normalized physical identity or reject relevant symlink mappings; preserve extra pointer fields and existing specification bytes.
- [X] T009 [US1] After T011 ratifies governing and operational guidance, correct F020-R002 and F020-R003 in `workflows/speckit-flow-select-feature/workflow.yml` and `controllers/flow-kit/controller-protocol.md`: route an independently confirmed trusted direct target through typed resolution and current-state validation without the redundant selection gate, retain the choice gate for missing/ambiguous intent, connect stable-ID/menu resolution to that route, and use explicit string branch states compatible with the controller branch interface.

**Checkpoint**: The independent test matrix passes with exact target, lifecycle, pointer, and specification preservation; no unsafe case mutates state.

---

## Phase 4: User Story 2 - Recognize Authorized Changes and Consequential Decisions (Priority: P1)

**Goal**: Carry trusted direct authorization through bounded, separately requested operations while retaining explicit gates for unresolved or consequential decisions.

**Independent Test**: Compare a directly requested bounded amendment, an inferred or material change, injected approval evidence, a pending governing amendment, and a separately requested next phase. Verify authorization provenance and that completion does not invoke another workflow.

### Tests for User Story 2

- [X] T010 [US2] After T006, reopen for F020-R002 and F020-R003: exercise production rendering and branch routing for direct-target and ambiguous selection, and for both empty and nonempty patch states through `render_template` and `select_switch_branch`; retain the existing authorization-routing regressions for direct versus inferred requests, untrusted report/child instructions, pending approval, exact derived patch bytes, no-op roadmap patch, same-target revalidation, and separate invocation in `tests/test_workflow_improvements.py`.

### Implementation for User Story 2

- [X] T012 [US2] Only if T004 demonstrates an actual incompatibility and a reviewed owner delivery is authorized, update the existing roadmap component pin in `bundles/spec-kit-flow/bundle.yml` to that exact delivery and record source coordinates, version, digest, tested CLI, and compatibility evidence in `specs/020-flowkit-workflow-iteration-improvements/validation/roadmap-delivery.json`; otherwise preserve the current pin and record that verification remains deferred.
- [X] T013 [US2] After T011, update controller routing and manual-prompt guidance to carry only settled same-target intent across separately requested phases, preserve same-child decision relay and exact assignments, and stop on unavailable assignments in `controllers/flow-kit/controller-protocol.md` and `workflows/README.md`.

**Checkpoint**: Direct bounded authorization is inspectable and does not trigger a second exact-patch-only approval; every unresolved consequential case retains a focused human gate.

---

## Phase 5: User Story 3 - Receive Accurate Implementation Readiness (Priority: P1)

**Goal**: Make Analyze and the separately invoked Implement phase use the same FlowKit-owned current preparation evidence, preserving future proof and human acceptance as pending while the existing core startup gate remains unchanged.

**Independent Test**: Exercise the FlowKit helper and exact Luna/Medium Checker across satisfied preparation, missing independent review, future evidence, unknown/mixed classification, missing owner, stale evidence, contradictory markers, and unavailable assignment. Verify safe gaps take their declared owner correction and return to fresh artifact analysis and readiness assessment; Implement recomputes immediately before ordinary core startup and never bypasses the unchanged core gate. Independently exercise the existing Tasker correction route and fresh code assessment.

### Tests for User Story 3

- [X] T014 [P] [US3] Add shared readiness contract fixtures for checked quality, unchecked reviewer-owned quality, independent-review absence, pending implementation/acceptance evidence, unknown/mixed obligations, missing owners, stale digests, contradictory markers, incomplete coverage, and unavailable core capability in `tests/consumer-fixtures/workflow-improvements/readiness-cases.json`.
- [X] T015 [US3] After T010, add focused tests in `tests/test_readiness.py` and `tests/test_workflow_improvements.py` for the FlowKit report schema, complete criterion coverage, current source/evidence digests, stable blocker ownership, pending-future preservation, strict workflow outcome-envelope compatibility, and unchanged core checklist-gate behavior; cover repair/reassessment and stale Analyze-to-Implement handoff without changing core files.

### Implementation for User Story 3

- [X] T016 [US3] After T005, implement the deterministic FlowKit readiness helper/report in `controllers/flow-kit/scripts/python/readiness.py` and integrate its safe-path, active-identity, checklist-coverage, marker-count, stable-locator, source/evidence-digest, blocking-ID, pending-future-ID, and resume-action validation with `controllers/flow-kit/scripts/python/controller.py`; keep report detail outside the strict workflow outcome envelope and leave Spec Kit core unchanged.
- [x] T017 [US3] After T016 and T034, update `workflows/speckit-flow-analyze-remediate/workflow.yml` to run fresh artifact analysis plus the exact read-only `FlowKit-Readiness Checker`, merge their findings without substituting Checker judgment for independent review, and route safely repairable gaps to the smallest declared owner (Specifier, Planner, Tasker, actual independent Reviewer, or authorized main-task recorder); after each correction rerun fresh artifact analysis and Checker, retain stable findings, award progress only for substantive gap resolution, and stop on unavailable owners, consequential decisions, no progress, repeated findings, or the existing six-assessment/five-correction cap.
- [x] T018 [US3] After T016 and T034, update `workflows/speckit-flow-implement/workflow.yml` to rerun the same helper and exact Checker immediately before core `speckit.implement`, validate active identity and current adjacent digests, and block stale evidence, missing independent review, or any unchecked preparation item before Coder dispatch; allow ordinary core startup only when its existing checklist gate will pass, keep future obligations pending outside `checklists/`, and provide a safe Analyze resumption without invoking Analyze automatically.
- [X] T019 [US3] Document FlowKit-owned preparation classification, the Luna/Medium Checker's read-only boundary, correction-owner loop, substantive independent-review ownership, authorized evidence recording/obligation relocation, progress and cap rules, pending future obligations, the unchanged core checklist gate, Implement revalidation, and safe resumption in `docs/installation.md`.

**Checkpoint**: Analyze and Implement agree on current preparation readiness; no author self-check, stale result, unchecked future marker, or command success falsely satisfies an obligation.

---

## Phase 6: User Story 4 - Use Installed Agents in Future Chats and Worktrees (Priority: P2)

**Goal**: Validate one-time supported preparation and exact native named-agent availability in the three specified future-chat contexts while preserving consumer-owned state.

**Independent Test**: Run install/refresh preservation checks, then record each exact agent launch independently in an existing prepared checkout's future chat, a prepared worktree's future chat, and a new worktree's first chat. Preserve every failed, unavailable, or not-tested case.

### Tests for User Story 4

- [X] T020 [P] [US4] Extend install/refresh and worktree-payload tests to verify all eight tracked agent definitions, ignored `.worktreeinclude` payload, customized consumer definitions, unrelated agents/configuration, feedback, and unrelated components retain their bytes in `tests/test_agent_delivery.py` and `tests/test_snapshot_validation.py`.

### Implementation and Native Validation for User Story 4

- [X] T021 [US4] Inspect supported tracked and `.worktreeinclude` preparation in a disposable initialized consumer and record package provenance, payload inventory, preservation outcomes, tested CLI, and any exact missing path in `specs/020-flowkit-workflow-iteration-improvements/validation/cases.json`; if a supported gap is reproduced, prepare its exact project-config patch and wait for explicit operator approval before changing `.worktreeinclude`.
- [X] T022 [US4] After T021 and T037 install the Checker package from the validated development snapshot, in an existing prepared checkout's future chat request and record separate exact native launches for the original eight agents and the additive FlowKit-Readiness Checker in `specs/020-flowkit-workflow-iteration-improvements/validation/cases.json`; retain each result and provenance independently, and do not infer effective settings from its definition.
- [X] T023 [US4] After T022, in a prepared Codex-managed worktree's future chat request and record the same nine exact native launches with that worktree's preparation and definition provenance in `specs/020-flowkit-workflow-iteration-improvements/validation/cases.json`; retain failed/unavailable results and do not count source declarations as dispatch evidence.
- [X] T024 [US4] After T023, in the first chat created for a new Codex-managed worktree request and record the same nine exact native launches plus whether payload presence before chat initialization is established or unknown in `specs/020-flowkit-workflow-iteration-improvements/validation/cases.json`; retain failed first-chat cases if a later chat succeeds.
- [X] T025 [US4] After T024, reconcile all 27 context/role cases (24 original-role launches plus three additive Checker launches) against exact requested agent types and actual responses/errors; record effective settings and client identity only when observed, and report interface, startup, capacity, or preparation gaps without fallback, child cleanup, per-chat installation, or causal speculation in `specs/020-flowkit-workflow-iteration-improvements/validation/cases.json`.
- [X] T035 [US4] After T009, T013, T019, T021, T034, and T041, update `docs/installation.md` and affected manual guidance in `controllers/flow-kit/controller-protocol.md` with one-time preparation, supported tracked/ignored propagation, the original eight-agent inventory and additive Checker definition, the definitions-present/interface-unavailable distinction, fresh-chat validation procedure, exact still-unverified limitations, and no startup-causation guarantee or per-chat reinstall recommendation; do not claim Checker launch success before T022–T025.

**Checkpoint**: All 27 context/role cases have individual attributable results; the original eight-role matrix remains separately identifiable, and full availability is met only if all 27 exact launches succeed. Consumer preservation and any needed configuration authorization are separately evidenced.

---

## Phase 7: User Story 5 - Use the Improvements Sequentially (Priority: P2)

**Goal**: Demonstrate that the three improvement areas compose across separately invoked phases and retain a blocked variant with safe recovery evidence.

**Independent Test**: On one disposable same-feature project, demonstrate explicit activation, separate authoring/preparation, Analyze readiness, and separately requested Implement startup. In a blocked variant, preserve earlier outcomes and stop at an unresolved consequential decision or unavailable exact assignment.

### Tests for User Story 5

- [X] T026 [P] [US5] Add combined-sequence fixtures for stable feature identity and phase boundaries, readiness recomputation, pending future evidence, no implied acceptance, and blocked authority/agent outcomes in `tests/consumer-fixtures/workflow-improvements/combined-sequence.json`.

### Implementation and Combined Validation for User Story 5

- [X] T027 [US5] After T025, T026, applicable US1–US4 work, and successful T037 development-snapshot package validation and disposable-consumer installation, run and record the ready same-feature sequence with each phase separately requested, current target/readiness evidence, prompt decisions, pending future obligations, and Implement startup result in `specs/020-flowkit-workflow-iteration-improvements/validation/cases.json`; preserve exact snapshot or readiness blockers and do not claim readiness when prerequisites are unavailable.
- [X] T028 [US5] After T027, run and record the blocked sequence for one unresolved consequential authority decision or unavailable exact assignment, preserving prior successful cases, partial state, exact blocker, and safe resumption without unsafe mutation or fallback in `specs/020-flowkit-workflow-iteration-improvements/validation/cases.json`.

### Tasker-owned Implement correction substream (FR-023/SC-009)

**Purpose**: Within an operator-invoked Implement run, route routine in-scope task-plan repair after independent code review to the exact assigned Tasker, validate the revision before coding resumes, and require fresh independent code assessment. This substream is independent of the combined-sequence demonstrations and unrelated core/roadmap delivery gates.

- [X] T038 [US5] Reopen for F020-R006 and F020-R008. Extend `tests/test_implement_task_revision.py` with focused production-rendered Implement and installed-consumer cases. For F020-R006, exercise task-file and parent-directory symlink aliases before scope freezing; prove the installed pre-Tasker check blocks before Tasker dispatch or task-file writes and leaves the neighboring feature and active pointer bytes unchanged, then retain the post-revision guard case. For F020-R008, render the semantic-review step for a non-020 selected feature and assert the prompt binds to that validated feature's approved specification and frozen correction scope. Preserve existing finding/owner, history, digest, identity, exact-assignment, fresh-review, zero-progress, and stop-condition coverage; keep this repair path independent of external readiness/roadmap delivery gates.
- [X] T039 [US5] After T008, reopen for F020-R006 and F020-R008. In `controllers/flow-kit/scripts/python/controller.py`, validate active identity, the lexical selected task path and parent chain, and physical containment within the selected feature before reading task bytes or producing a frozen snapshot; block unsafe aliases before Tasker dispatch. Revalidate immediately before dispatch and retain the post-revision guard. Bind Tasker's result to the exact frozen finding/correction and eligible-owner snapshot, rejecting invented, omitted, substituted, wrong-owner, and out-of-scope mappings. Bind the main-controller semantic check to the validated selected feature and approved frozen specification/scope rather than a literal Feature 020 reference. Preserve feature identity, digests, history, uniqueness, and zero task-only progress; cover deployed pre-dispatch safety and non-020 scope cases in T038.
- [X] T040 [US5] After T038 and T039, reopen for F020-R008. In `workflows/speckit-flow-implement/workflow.yml`, invoke the bounded `speckit.tasks` revision with exact `FlowKit-Tasker` metadata and the verified frozen findings/task snapshot. Bind the main-controller semantic-review prompt to the validated selected feature identity and its approved specification/scope from that snapshot, preserving exact correction boundaries for features other than 020. Execute validation through the installed consumer helper path `.specify/flow-kit/scripts/python/controller.py`; validate the structured result before returning to Coder and require fresh independent review. Preserve consequential gates, correction/no-progress caps, exact-assignment preflight, and the prohibition on invoking another FlowKit workflow; require T038/T044 evidence for rendered non-020 scope and accepted/rejected installed-package cases.
- [X] T041 [US5] After T040 and T013, reopen for F020-R006 and F020-R008. Synchronize the Implement route in `workflows/speckit-flow-implement/flowchart.md`, `controllers/flow-kit/controller-protocol.md`, `workflows/README.md`, and `specs/020-flowkit-workflow-iteration-improvements/contracts/task-revision.md`: document active-identity and lexical/physical task-path preflight before task reads or Tasker dispatch, immediate pre-dispatch revalidation, post-revision checks, semantic review bound to the validated selected feature and frozen approved scope, installed consumer helper path, exact Tasker assignment, bounded return loop, no routine reopening approval, digest/history checks, stop conditions, and manual-prompt fallback. Synchronize the completed-history field name from `preserved_completed_ids` to `preserved_completed_task_ids` across the contract and applicable guidance. Preserve consequential gates.
- [X] T042 [US5] After T041, reopen for F020-R007. Update `specs/020-flowkit-workflow-iteration-improvements/quickstart.md` with exact focused commands and expected evidence for the installed-package consumer case: exercise the literal rendered validation command with the actual controller package under `.specify/flow-kit/scripts/python/`, verify one valid revision and one rejected revision, and retain the open-task, closed-task reopening, and missing-task cases. Distinguish production rendering/branch evidence from native Tasker dispatch, preserve the exact native record location, and document the synchronized runtime field `preserved_completed_task_ids` consistently with the contract.
- [X] T043 [US5] After T040 and T042, in an operator-directed Implement session, request the exact native `FlowKit-Tasker` assignment for a controlled in-scope task revision and record the actual response or exact availability error in `specs/020-flowkit-workflow-iteration-improvements/validation/tasker-native-dispatch.json`; do not count a no-op executable, label, or source declaration as native availability.
- [X] T044 [US5] After T038, T041, and T042, reopen for F020-R006 and F020-R008. Run and record the focused production-render, branch-routing, controller-validation, and actual installed-consumer-package cases from `specs/020-flowkit-workflow-iteration-improvements/quickstart.md`, including active-identity and task/parent symlink rejection before Tasker dispatch or writes, unchanged neighboring-feature and active-pointer bytes, the post-revision symlink guard, non-020 semantic-scope rendering, and valid plus rejected revisions using `.specify/flow-kit/scripts/python/controller.py` in the installed package layout. Retain open-task correction, completed-task reopening, missing-task append, and finding/owner rejection coverage. Record exact commands, actual outcomes, before/after task digests, finding/owner mapping, preserved history and other-feature bytes, and any stop reason in `specs/020-flowkit-workflow-iteration-improvements/validation/task-revision-cases.json`; do not count task edits as resolved code findings or treat T043's separate historical native-dispatch evidence as runtime validation.

**Checkpoint**: The ready and blocked variants preserve feature identity, invocation boundaries, required human decisions, and truthful implementation/acceptance status.

### Implement defect-progress continuation (FR-025/SC-011)

**Purpose**: Continue an otherwise authorized bounded Implement loop after fresh independent review resolves a previously recorded in-scope code defect, even when its owning task remains open; retain baseline, readiness, authority, no-progress, and iteration-cap safeguards.

- [x] T045 [US5] After T015 and T038–T044, add production-rendered controller and Implement-route regression cases in `tests/test_implement_task_revision.py` and `tests/test_workflow_improvements.py` for a frozen pre-correction baseline with one selected unfinished task and two stable defects mapped to its existing eligible owner; assert that fresh independent resolution of one prior defect continues while the other defect and parent task remain open, and cover new/recurring/renamed/omitted findings, task-only changes, readiness and authority failures, unavailable assignment, no-progress, and cap stops.
- [x] T046 [US5] After T045 and readiness ownership tasks T016/T018, update `controllers/flow-kit/scripts/python/controller.py` and `workflows/speckit-flow-implement/workflow.yml` to freeze the task/finding/owner/source-digest baseline before correction, preserve distinct task and finding identities in the existing strict outcome envelope and workflow result, award progress only for a previously recorded finding independently resolved against its requirement and deficiency, retain new or unresolved findings, and continue only with safe eligible work, current readiness, unchanged authority/scope, exact assignments, and remaining iteration budget; keep the parent task unchecked until its whole requirement is substantiated.
- [X] T047 [US5] After T046, synchronize `workflows/speckit-flow-implement/flowchart.md`, `controllers/flow-kit/controller-protocol.md`, `workflows/README.md`, and `specs/020-flowkit-workflow-iteration-improvements/quickstart.md` with the baseline, finding-to-task mapping, partial-defect progress, parent-task completion rule, and preserved stops; run the focused actual-controller/production-rendered cases and record commands, baseline and source digests, outcomes, limitations, and fresh independent Code Reviewer evidence in `specs/020-flowkit-workflow-iteration-improvements/validation/defect-progress-cases.json`.

---

## Phase 8: Polish, Traceability, and Validation

**Purpose**: Reconcile evidence, guidance, and source ownership across the complete feature.

- [x] T036 After T008–T009, T012 if T004 demonstrates a required extension change, T013, T016–T019, T034–T035, T039–T042, and T045–T047 settle their authorized source changes, reconcile controller, agent package, and changed workflow versions to source metadata and existing bundle pins in `bundles/spec-kit-flow/bundle.yml`; record each source/version/pin relationship and actual compatibility evidence, including readiness, Tasker routing, defect-progress continuation, and the unchanged core pin, in `specs/020-flowkit-workflow-iteration-improvements/validation/summary.md`. Keep the roadmap pin unchanged when its explicitly deferred compatibility check has not shown a required change; preserve exact source-delivery/Git blockers without modifying pins.
- [X] T037 After T036, install the current FlowKit development snapshot into a disposable initialized consumer using the supported `mise run catalog:install -- "$consumer_project" --development-snapshot` path. Record the exact source coordinates, component versions and pins, tested Specify CLI, preserved consumer/component inventory, installed package bytes and SHA-256 digests, and readiness/compatibility outcomes in `specs/020-flowkit-workflow-iteration-improvements/validation/summary.md`. Do not require clean release checkouts or Git tags, and do not modify `catalog/release.json` or `catalog/packages/`; this snapshot delivery supports T022–T024 and T027 without claiming production release.
- [X] T029 After T028 and applicable US1–US5 evidence, reassess each of the five immutable historical observations against current applicable component versions and record reproduced, not-reproduced, or not-tested with exact gap, requirement links, cases, and evidence in `specs/020-flowkit-workflow-iteration-improvements/validation/observations.json`; include actual FlowKit readiness correction/recheck and 27-case Checker/native evidence only when delivered and observed.
- [X] T031 After T037's validated development-snapshot install, T025, and T029, run the focused source, workflow-projection, nine-agent delivery, consumer-snapshot, FlowKit readiness/correction-loop, Implement task-revision, and defect-progress commands from `specs/020-flowkit-workflow-iteration-improvements/quickstart.md`; record exact commands, actual results, skipped cases, native-agent limitations, unchanged-core evidence, and prerequisite gaps in `specs/020-flowkit-workflow-iteration-improvements/validation/summary.md`.
- [X] T030 After T031, T025, T043, and T044, complete the FR-001–FR-025 and SC-001–SC-011 coverage map, source coordinates/digests, tested CLI/client context, deferred roadmap verification status, unresolved external limits, and separate acceptance/effective-settings claims in `specs/020-flowkit-workflow-iteration-improvements/validation/summary.md`.
- [X] T032 After T030, prepare the final source and evidence set for separately assigned independent semantic review, preserving unresolved evidence and making no release, Git, publication, deferred roadmap verification, runtime Checker-availability, or feature-acceptance claim in `specs/020-flowkit-workflow-iteration-improvements/validation/summary.md`.
- [X] T048 [US5] After T037, correct the FR-020 command-skill owner lookup in `controllers/flow-kit/scripts/python/controller.py` and add focused regressions in `tests/test_controller.py` (or a dedicated owner-resolution test module). Accept a valid enabled extension-owned command such as `speckit.flow-wiki.query` and its installed skill `speckit-flow-wiki-query` when the skill is absent from the core Codex files map only after validating a unique active registration, declared command, matching extension id/version/manifest hash, safe project-contained declared source path, and matching skill metadata source/name. Preserve core-manifest digest checks and rejection of unknown, disabled, or ambiguous registrations; malformed or mismatched extension manifest id/version/hash; invalid, escaping, or symlinked source paths; incorrect skill metadata; and core tampering. Report extension ownership attestation separately from observed source/skill digests and state that registration does not attest rendered skill-body bytes; do not fabricate expected body hashes or edit Spec Kit core or independently owned extensions. Test the actual matched controller package in a disposable consumer, deliver the corrected development snapshot with retained owned-payload provenance, and record the cases, digests, outcomes, limitations, and fresh independent Code Reviewer evidence in `specs/020-flowkit-workflow-iteration-improvements/validation/command-skill-owner-resolution.json`. Keep source versions and pins unchanged unless independent review requires a version change.

---

## Dependencies and Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; T001 and T002 may run in parallel.
- **Foundational work (Phase 2)**: T003 supplies the exact governing approval; T033 requires and ratifies that decision, and T011 reconciles it before authority-dependent work. T005 records the unchanged core compatibility boundary. T004's October 6 deferral is historical; the six October 7 trials are complete and establish no demonstrated incompatibility within their tested scope. T012 therefore requires no pin change on current evidence and remains conditional on a demonstrated incompatibility plus reviewed owner delivery.
- **User Story 1 (Phase 3)**: T006 → T007 → T008 → T009. T006 follows the shared test-file owner order; T008 and T009 require T011 so changed authority is ratified and operationally reconciled before use. T008/T009 are reopened for F020-R001–R004 and T006/T010 carry their precise runtime regressions.
- **User Story 2 (Phase 4)**: T010 follows T006 because both update `tests/test_workflow_improvements.py`; T013 requires T011 and T009 because both edit shared controller guidance. T004's six-trial compatibility evidence is complete within the recorded scope and does not block FlowKit source work; T012 requires an extension change only if evidence demonstrates an incompatibility and a reviewed owner delivery is authorized.
- **User Story 3 (Phase 5)**: T014/T015 establish fixtures and tests; T016 implements the FlowKit helper; T017/T018 integrate the same exact Checker and correction/recheck or startup route after T034 delivers its definition. T019 documents the contract. None requires Spec Kit core source delivery or a core pin change. The existing Tasker repair substream keeps its declared dependencies and remains independent of readiness implementation.
- **User Story 4 (Phase 6)**: T020/T021 preserve and inventory the original eight-agent preparation. T035 writes prospective installation/manual guidance after T019, T021, T034, and T041, without claiming Checker dispatch. T036 reconciles the reviewed Checker source and pins; T037 installs that source through a validated development snapshot. Then run T022 → T023 → T024 → T025 serially because they append to `validation/cases.json`. T021 may change project configuration only after a reproduced gap and explicit operator approval.
- **Historical User Story 5 dependency checkpoint (Phase 7)**: T026 may prepare fixtures earlier. T027 follows T025, applicable US1–US4 work, the completed T037 development-snapshot installation, and T048's completed corrected-source delivery with retained owned-payload provenance. T048 is a satisfied delivery prerequisite, not a current blocker. Readiness evidence from before T048's source correction is stale for T027 and must be freshly assessed against the delivered snapshot before a ready result can be claimed. T027 remains open for its own combined demonstration; T028 follows T027. Both write `validation/cases.json` and run serially. The FR-023 Tasker substream retains its existing order: T038/T039 after T008; T040 after both; T041 after T040/T013; T042, then T043/T044. The FR-025 defect-progress substream runs T045 → T046 → T047 after T015 and T038–T044; T046 also depends on readiness routes T016/T018. It needs no core delivery or roadmap verification.
- **Historical lifecycle-amendment dependency checkpoint**: The prior dependency sequence through T049 was complete; at that checkpoint T050–T067 were the open amended-scope tasks. Fresh readiness analysis is required against the current 77-task artifact after Story 7 reconciliation. The old T027–T032 open-task statements above remain dated history only and do not govern current eligibility.
- **Historical Polish dependency checkpoint (Phase 8)**: Complete source and documentation tasks T035/T039–T042/T045–T047, then T036 reconciles versions and the completed T037 development-snapshot delivery. Only then execute native Checker matrix T022–T025 and combined scenarios T027/T028. T029 reassesses the five observations. T031 validates source, snapshot package, readiness loop, native evidence, task revision, and defect-progress continuation; T030 completes FR-001–FR-025/SC-001–SC-011 coverage after T025/T043/T044; T032 prepares evidence for independent review, not the review itself. Final verification tasks remain open until their own work and evidence are recorded. Production release packaging is a separate post-closeout [handoff](post-closeout-release.md) and does not block Feature 020 implementation, convergence, or closeout.

### User Story Dependencies

- **User Story 1 (P1)**: Depends on T001–T003, T033, T011, and its regression tests. Selection implementation cannot use prospective authority until constitutional ratification and operational guidance reconciliation are complete.
- **User Story 2 (P1)**: Depends on User Story 1, T003, and T011 for FlowKit's approved bounded direct-amendment behavior. The six T004 compatibility trials are complete within tested scope; T012 needs no change on current evidence and is not a prerequisite for this source work. Other consequential decisions remain gated.
- **User Story 3 (P1)**: The FlowKit readiness path depends on T005 compatibility baseline, T014–T016 helper/report coverage, and T034 Checker definition; T017/T018 then implement Analyzer repair/recheck and Implement revalidation. No core-source delivery or pin change is required.
- **User Story 4 (P2)**: Preservation and native evidence are semantically independent of US1–US3, but T035 guidance follows T009/T013 and US3 T019 because they share controller protocol and installation documentation. A configuration alteration requires an explicit separate approval after T021 identifies a concrete supported gap.
- **Historical User Story 5 dependency checkpoint (P2)**: T026 may run earlier. Ready T027 depends on T025, applicable US1–US4 results, completed T037 installation of the validated FlowKit development snapshot, and T048's completed source delivery with retained owned-payload provenance. These delivery prerequisites are satisfied; T027 still requires fresh preparation/readiness evidence against the delivered snapshot and its own recorded demonstration. T028 follows T027; snapshot or readiness blockers prevent a ready claim. T029 follows T028 and applicable evidence. The FR-023 substream remains separate from these demonstrations and from core/roadmap owner deliveries. The FR-025 substream depends on the existing readiness/task-revision routes, runs T045 → T046 → T047, and must finish before T036 source-version reconciliation.
- **Historical task-marker checkpoint (2026-10-07)**: The earlier 51/77 completion count and statements that T052–T067 and T068–T077 were open describe that checkpoint only. A later 2026-10-08 snapshot recorded 68 completed and 9 open, with T064–T067, T071–T072, and T075–T077 pending at that time. These counts and ranges are historical; task checkboxes are the live checklist authority. T050/T051 record roadmap alignment and approval of the exact lifecycle policy. Neither prior-scope convergence nor checklist counts prove delivery or acceptance.

### Parallel Opportunities

- T001/T002 and the T005 compatibility baseline can proceed independently. T003 leads to T033 and then T011. T004's six recorded trials are complete within tested scope; T012 remains conditional on a demonstrated incompatibility and reviewed owner delivery. T034 adds the Checker definition/manifest as FlowKit source work.
- User Stories 1 and 3 have independent goals, but serialize changes to `controllers/flow-kit/scripts/python/controller.py` (T008/T016) and `tests/test_workflow_improvements.py` (T006/T010/T015). T016 owns the separate `readiness.py` helper; T017/T018 own separate workflow files after Checker source is declared.
- US2's T012 bundle edit may run alongside T013 only after shared prerequisites are complete; T009 and T013 share `controllers/flow-kit/controller-protocol.md` and must be serialized.
- US4 native cases update `validation/cases.json` serially after T037 installs the source Checker from a validated development snapshot; T022–T025 are complete, with per-case outcomes and provenance retained there. T035 shares `docs/installation.md` with T019 and follows it before final version reconciliation; its guidance reflects observed launch evidence and preserves unverified settings or client details.
- Historical US5 dependency assessment: T027 and T028 both update `validation/cases.json` and must run sequentially. T026 may be prepared independently earlier; T027's T035/T036/T037 development-snapshot delivery and T048 corrected-source delivery prerequisites are complete. T027 still needs fresh preparation/readiness evidence against that snapshot and its own recorded demonstration.
- **Historical parallel-opportunities checkpoint (2026-10-08, before later Implement marker tracking)**: At that snapshot T064–T067 and T071–T072 were open, and T075–T077 remained for downstream validation. T075 depends on T063–T064, completion of T071–T072, and revalidation of completed T073/T074 outputs against the corrected source. These marker states describe the snapshot only; consult the task rows for live status. The completed T027–T032 sequence is evidence for the prior scope. Readiness and attributable evidence remain required, and task markers do not establish delivery or acceptance.
- T017 and T018 edit distinct workflow definitions and may proceed in parallel after T016/T034; then T035 completes manual guidance and T036/T037 validate and install those sources in a development snapshot. T022–T025 were run after T037; Checker runtime evidence was not required to package the source that supplies it.
- The FR-023 tests in T038 use a dedicated file; T039 follows reopened T008 in `controller.py`, T040 follows T038/T039 in the Implement workflow, and T041 serializes shared protocol guidance before T035. Task revision source and tests proceed without waiting on unrelated roadmap/core-readiness deliveries.
- The FR-025 regression cases in T045 precede controller/workflow changes in T046; T047 then synchronizes charts, protocol/README/quickstart, and actual independent-review evidence. This change remains within the already authorized Implement loop and does not alter installed runtime copies or Feature 020's open verification tasks.

## Story Execution Examples

Each example separates safe concurrency from dependency order; stories may be semantically independent while tasks that edit a shared file still need serialization.

- **Setup and foundations**: T001 and T002 can run in parallel with T005 compatibility baseline. T003 then T033/T011; T004's six-trial evidence is complete within its recorded scope, and T034 is FlowKit Checker source work.
- **US1**: No safe internal parallel implementation work is planned: T006 → T007 → T008 → T009. The regression file and controller helper have later shared-file consumers.
- **US2**: T010 follows T006; after prerequisites, T012 may run in parallel with T013 only if T009 is complete, since they edit distinct bundle and workflow guidance files.
- **US3**: T014 can be prepared separately; T015 follows T010. Then T016 implements the helper; T034 supplies the Checker definition before T017/T018 workflows. T017 and T018 may proceed in parallel after those prerequisites, then T019 records their combined guidance.
- **US4**: T020 and T021 can proceed independently. T035 guidance follows T019/T021/T034/T041. T036/T037 validate and install the Checker through a development snapshot before the completed serial T022 → T023 → T024 → T025 cases in `validation/cases.json`.
- **US5**: T026 can be prepared independently. After applicable stories finish, with T037 development-snapshot installation and T048 corrected-source delivery already complete, perform fresh preparation/readiness assessment and then run T027 → T028 serially because both write `validation/cases.json`. In the task-revision substream, T038 and T039 can run in parallel after T008; then run T040 → T041 → T042. T043 (native dispatch evidence) and T044 (production-route evidence) then run independently into separate records and need not wait for T027/T028 or external readiness/roadmap delivery. For FR-025, run T045 regression cases → T046 source correction after T016/T018 → T047 guidance and actual-review evidence; T036 waits for this sequence.
- **US7**: Start T068/T069 independently. Serialize T070 after T054 and T071 after T056 because each shares an existing source file; run T072 after T060/T071, then T073 and T074. Validate the combined installed snapshot in T075 and record T076 native evidence. T077 remains unchecked with its manual matrix unperformed under the closeout waiver; dogfooding discoveries are reported as defects without requiring matrix completion.
- **US7**: T068 fixtures and T069 standalone helper can proceed without the roadmap owner runtime capability. T070 serializes the shared controller adapter after T054; T071 serializes Implement graph changes after T056; T072 follows T060 and T071 for shared workflow tests. T073 updates guidance after the graph. T074 reconciles pins after T062 and Story 7 source/docs/tests, then T075 validates the combined installed snapshot. T076 native evidence follows installed validation; T077 remains an unchecked, unperformed manual matrix waived for closeout. T067 reconciles evidence for the completed implementation scope and records the manual-evidence limit without requiring that matrix.
- **Polish**: T045 → T046 → T047, T036 → T037 delivery, and T022–T025 are complete. Perform fresh preparation/readiness assessment and T027 → T028, followed by T029, T031, T030, and T032 in dependency order. The production catalog release follows separate Converge and Closeout completion under the [handoff](post-closeout-release.md).

## Requirement and Success-Criteria Coverage

The task references below preserve traceability to every approved requirement and success criterion; they describe planned work, not evidence that an outcome has passed.

| Scope | Tasks |
|---|---|
| FR-001 | T002, T029 |
| FR-002–FR-006 | T006–T009 |
| FR-007 | T003, T010, T012–T013 |
| FR-008 | T003, T011, T033 |
| FR-009 | T011–T013, T027–T028 |
| FR-010–FR-014 | T005, T014–T019 |
| FR-015–FR-016 | T020–T021 |
| FR-017–FR-019 | T021–T025, T034–T037 |
| FR-020 | T009, T013, T019, T031, T034–T037, T048 |
| FR-021 | T026–T028, T048 |
| FR-022 | T001, T029–T030, T034–T037 |
| FR-023 | T038–T044 |
| FR-024 | T005, T014–T019, T027–T031, T034–T037 |
| FR-025 | T045–T047 |
| SC-001–SC-002 | T006–T009 |
| SC-003 | T003–T004, T010–T013, T033 |
| SC-004 | T005, T014–T019, T027–T031, T034–T037 |
| SC-005 | T022–T025, T034–T037 |
| SC-006 | T020–T021, T034–T037 |
| SC-007 | T002, T029–T030 |
| SC-008 | T026–T028, T030 |
| SC-009 | T038–T044 |
| SC-010 | T005, T014–T019, T027–T031, T034–T037 |
| SC-011 | T045–T047 |

FR-019's exact assignments and no-fallback requirements are retained in User Story 4's exact native requests and failure reporting. Capacity changes, child cleanup, Feature 016 centralized probing, Feature 019 prerequisites, and startup-control guarantees remain excluded constraints on related work.

## Implementation Strategy

### MVP First

1. Complete T001–T003, then T033 and T011 after exact governing approval, before the User Story 1 tests and implementation; stop if approval or target validation is unresolved.
2. Validate first activation, repeat activation, existing specification, stable references, lifecycle preservation, and unsafe stops independently.
3. Do not treat selection readiness as approval for User Story 2, a roadmap source change, or another workflow phase.

### Incremental Delivery

1. Deliver User Story 1 after its own tests and governing gate.
2. Deliver User Story 2 only after governing and roadmap owner gates are evidenced.
3. Deliver User Story 3 after FlowKit helper, exact Checker source definition, correction/reassessment and startup-revalidation routes pass focused tests against the unchanged core gate.
4. Validate User Story 4 preservation and its 27 individually recorded native cases (24 original-role launches and three Checker launches); retain external limitations as unmet cases.
5. Deliver the bounded FR-023 Tasker correction substream after its focused production-route tests and exact assignment checks; this substream does not wait for unrelated core-readiness or roadmap-owner delivery.
6. Complete T035 source guidance and the T045–T047 defect-progress loop, reconcile versions in T036, and validate/install the development snapshot in T037 before running the User Story 5 ready demonstration T027 and blocked demonstration T028. Reassess the observations in T029, then finish evidence reconciliation and independent-review preparation. Production release packaging is handed off separately after feature convergence and closeout.

## Notes

- [P] tasks use separate files and have no unfinished-task dependency.
- `[US1]` through `[US5]` map directly to the five stories in `specs/020-flowkit-workflow-iteration-improvements/spec.md`.
- Tasks describe future implementation and evidence work; checking a task cannot grant a human approval, change an external source owner, authorize configuration, accept Feature 020, or invoke another workflow.
- Readiness policy and delivery belong to FlowKit; Spec Kit core source, installed files, pins, and standalone behavior remain unchanged. The six October 7 Roadmap Write trials are complete and support compatibility only within their tested scope; T012's conditional extension delivery was not applicable and the roadmap pin is unchanged. Universal compatibility, publication, effective settings, and acceptance remain unestablished.
- The native matrix keeps the original eight exact agent names across three contexts and adds the Checker in those same contexts: 24 original-role cases plus three Checker cases. Every case needs its own result, provenance, and limitation fields; source definition does not prove launch availability.
- Tasker-owned revisions are bounded to independently evidenced in-scope code findings; reopening/appending tasks never resolves a finding or earns implementation progress. Fresh independent resolution evidence for a prior recorded defect may support continuation while its parent task remains open, but the task stays unchecked until its full requirement is substantiated.
- Existing Feature 017 qualifications, the unresolved historical capacity observation, manual fallback, and separately invoked phase boundaries remain intact.


## Phase 9: Convergence

- [X] T049 [US4] Demonstrate the existing prepared checkout's future-chat context in a physical repository checkout distinct from the prepared linked worktree used by T023; in one fresh top-level chat, request the same nine exact agent identities serially, verify checkout/worktree identity from repository metadata, and append each result, preparation/definition provenance, and unavailable detail to `specs/020-flowkit-workflow-iteration-improvements/validation/cases.json` and `specs/020-flowkit-workflow-iteration-improvements/validation/t025-native-context-matrix-20261007.json` without replacing T022/T023 evidence, per FR-017 and US4/AC1–AC2 (missing).

## Phase 10: User Story 6 - Record Evidence-Supported Phase Milestones (Priority: P1)

**Goal**: Give Specify, Implement, and Close Out explicit ownership of `specced`, `in-progress`, and `implemented`, with current evidence, bounded stale-state recovery, and the existing separate `verified` gate.

**Independent Test**: In an initialized disposable consumer using the exact reviewed owner and FlowKit development snapshot, execute the LC001–LC015 matrix in `quickstart.md` and `contracts/phase-lifecycle.md`; verify each effect/no-op/question/blocker, current evidence and receipt, unchanged verification gate, source ownership, and preserved consumer state. Separately exercise live named-agent and manual-prompt boundaries, recording unavailable evidence as a gap rather than a pass.

### Authorization and Owner Delivery Prerequisites

- [X] T050 [US6] Resolve `F020-LIFECYCLE-BRIEF-ROADMAP-001` by preparing the additive Feature 020 roadmap outcome/scope/notes amendment that preserves `planned`, existing entry fields, and transition history; apply it through the registered FlowKit-Roadmap owner route when current trusted operator authorization and governing rules clearly cover this bounded effect, without requesting approval solely for derived patch wording, and request one focused decision only if authority or consequence remains unsettled; record the before/after entry, authorization reference, owner version, and digest in `specs/020-flowkit-workflow-iteration-improvements/validation/lifecycle-governance.json` without advancing lifecycle status.
- [X] T051 [US6] Before runtime effects, present the exact `contracts/phase-lifecycle.md` policy and owner-command reconciliation for explicit operator approval; record the decision and any exact constitutional/authority conflict in `specs/020-flowkit-workflow-iteration-improvements/validation/lifecycle-governance.json`, change governing files only after a specifically approved amendment, and keep current authority operative if approval or an owner-compatible rule is absent.
- [X] T052 [US6] After T050–T051 and before owner-source effects, inspect the actual `pegagio/spec-kit-flow-roadmap` checkout identity/revision/dirty-index state, owner guidance, available access, permitted source-work route and task authority; report an exact blocker and safe resumption if any is missing, without assuming checkout availability or requiring the installed capability this task builds. Then deliver and independently review the additive `specification_ready` brief/review-contract mode in `scripts/python/review_contract.py` and its report template, plus `scripts/python/phase_lifecycle.py` evaluate/apply, the `speckit.flow-roadmap.write` mode in `commands/speckit.flow-roadmap.write.md`, manifest declarations, owner tests, and a compatible component version; record observed owner source coordinates/version/digest, tested CLI, review, actual permission/route evidence, and exact contract compatibility in `specs/020-flowkit-workflow-iteration-improvements/validation/lifecycle-owner-delivery.json` without editing installed copies or claiming publication.

### FlowKit Adapter and Owning Workflow Routes

- [X] T053 [US6] After T051–T052, add strict request, snapshot, evidence, proposal, receipt, no-op, blocker, question, and recovery fixtures for the approved lifecycle contract—including duplicate/unknown/null fields, unsafe paths, and all four receipt outcomes—in `tests/consumer-fixtures/workflow-improvements/phase-lifecycle-cases.json` before implementing the FlowKit adapter.
- [X] T054 [US6] After T051–T053, implement deterministic evidence collection, digest freshness checks, ordered one-edge routing, strict receipt validation, and `prepare`/`revalidate` command handling in `controllers/flow-kit/scripts/python/phase_lifecycle.py` and `controllers/flow-kit/scripts/python/controller.py`; FlowKit must never write roadmap bytes, and tests in `tests/test_phase_lifecycle.py` must reject unsupported or unsubstantiated effects.
- [X] T055 [P] [US6] After T052 and T054, add reviewed authoring-quality, `specification_ready` brief, lifecycle prepare/route/apply/verify nodes and exact FlowKit-Reviewer/FlowKit-Roadmap Agent assignments to `workflows/speckit-flow-specify/workflow.yml`; record `specced` only after current author checks, clarification, independent review, linkage and Must-Address brief resolution, without requiring the later Complete header or future implementation proof.
- [X] T056 [P] [US6] After T052 and T054, add FlowKit-Reviewer eligible-scope assessment, the existing Readiness Checker handoff, and lifecycle prepare/route/apply/verify nodes immediately before the first Coder in `workflows/speckit-flow-implement/workflow.yml`; record `in-progress` before coding, and route blocked readiness, missing assignments, or failed receipt to a precise stop with no Coder dispatch.
- [X] T057 [P] [US6] After T052 and T054, add full-current-scope completion assessment by FlowKit-Code Reviewer, lifecycle prepare/route/apply/verify by FlowKit-Roadmap Agent, and receipt verification by FlowKit-Reviewer before the first debrief in `workflows/speckit-flow-closeout/workflow.yml`; record `implemented` only on current independent completion evidence and keep the existing consequential `verified` decision gate as a later separate step.
- [X] T058 [US6] After T055–T057, synchronize exact node IDs, assignment labels, effect order, recovery branches and stop behavior in `workflows/speckit-flow-specify/flowchart.md`, `workflows/speckit-flow-implement/flowchart.md`, `workflows/speckit-flow-closeout/flowchart.md`, `controllers/flow-kit/controller-protocol.md`, and `workflows/README.md`, including the supported manual-prompt equivalent without automatic cross-workflow invocation.
- [X] T059 [US6] Document the three phase owners, evidence boundaries, explicit approval/resolution cases, ordered stale-state recovery, partial outcomes, exact owner version requirement, manual fallback and limits on verification/acceptance in `docs/installation.md` and `specs/020-flowkit-workflow-iteration-improvements/quickstart.md` while retaining production release as the separate `specs/020-flowkit-workflow-iteration-improvements/post-closeout-release.md` handoff.

### Lifecycle Regressions, Delivery, and Current-Scope Evidence

- [X] T060 [US6] After T055–T058, extend `tests/test_workflow_graph.py`, `tests/test_workflow_paths.py`, and `tests/test_phase_lifecycle.py` to assert declared node/role completeness, every recovery preflight, bounded three-edge ordering, no Coder before verified `in-progress`, no debrief before verified `implemented`, no implicit Verify/acceptance, preserved manual routes, and unchanged correction/progress caps.
- [X] T061 [US6] After T054–T060, implement and run deterministic LC001–LC015 cases from `specs/020-flowkit-workflow-iteration-improvements/quickstart.md` using `tests/consumer-fixtures/workflow-improvements/phase-lifecycle-cases.json`; cover successful and missing/stale proof for all three owners, repeat/equal/advanced state, three-edge and contradictory recovery, absent route, deferred/abandoned state, both partial-failure directions, receipt-record failure/retry, concurrent source changes, and verification return/deferral, recording actual results and case-level gaps in `specs/020-flowkit-workflow-iteration-improvements/validation/lifecycle-cases.json`.
- [X] T062 [US6] After T055–T061 and the reviewed owner delivery, reconcile actual controller/workflow/owner versions, manifest declarations, hashes and minimum compatible pins in `controllers/flow-kit/manifest.yml`, affected workflow metadata, and `bundles/spec-kit-flow/bundle.yml`; preserve unrelated pins, report exact source coordinates and tested CLI in `specs/020-flowkit-workflow-iteration-improvements/validation/lifecycle-delivery.json`, and do not edit production release archives or tags.
- [X] T063 [US6] After T062, install and refresh the supported FlowKit development snapshot in a disposable initialized consumer; record all actual owned payload hashes, owner/source versions, tested CLI, install/refresh results, and preservation of consumer configurations and unrelated components in `specs/020-flowkit-workflow-iteration-improvements/validation/lifecycle-snapshot.json` using the supported catalog path, with no claim of production release.
- [X] T064 [US6] After T063, run the focused helper, owner-contract, graph/projection, LC001–LC015, bundle and disposable-consumer checks from `specs/020-flowkit-workflow-iteration-improvements/quickstart.md`; retain nonzero actual commands/results, skipped cases and precise limitations in `specs/020-flowkit-workflow-iteration-improvements/validation/lifecycle-summary.md`, including checks that the explicit `verified` gate remains unchanged.
- [X] T065 [US6] After T063, validate actual launches for every exact native assignment used by the Specify, Implement, Close Out and recovery routes in separately requested isolated phase-validation contexts; record requested name, observed response/error, source/package provenance and context in `specs/020-flowkit-workflow-iteration-improvements/validation/lifecycle-native-cases.json`, preserve failed cases, and make no effective model/effort or interface-visibility claim unless observed.
- [ ] T066 [US6] Waived for closeout by the direct operator decision recorded in `validation/waived-manual-validation.json`; the original manual matrix remains unchecked and unperformed, is not a closeout prerequisite, and may yield defects through ordinary dogfooding without requiring matrix completion.
- [X] T067 [US6] After T050–T065, T068–T076 and separately requested current-scope Analyze/Remediate evidence, reconcile FR-026–FR-048, SC-012–SC-022, LC001–LC015 and SI001–SI015 to actual implementation and lifecycle/scope/native records in `specs/020-flowkit-workflow-iteration-improvements/validation/lifecycle-summary.md` and `specs/020-flowkit-workflow-iteration-improvements/validation/implementation-scope-summary.md`; preserve T066/T077 as unchecked and unperformed, record their closeout waiver and zero observed manual results in `validation/deferred-dogfooding.json` and `validation/waived-manual-validation.json`, and request fresh independent Code Reviewer assessment of the complete amended scope. Preserve exact unresolved implementation, owner, readiness, convergence and acceptance limits without claiming manual results or Feature 020 acceptance.

**Checkpoint**: All three owning routes have current evidence and independently verifiable effect receipts, ordered stale-state recovery is bounded and resumable, live/manual limitations remain explicit, and the separate `verified` gate is intact. These tasks do not authorize production release, Git integration, publication, or feature acceptance.

### Story 6 Dependencies and Parallel Opportunities

- T050 and T051 are separate authority prerequisites; neither blocks task generation. T050 uses any existing unambiguous trusted authorization for the bounded roadmap effect and asks only if the authority or consequence is genuinely unsettled. T051 obtains explicit approval for the runtime contract and for any necessary constitutional/authority amendment. T052 depends on both and is an actual independently owned `pegagio/spec-kit-flow-roadmap` source delivery prerequisite; the current installed owner cannot be assumed to implement this contract.
- T053 follows the approved runtime contract and owner interface; T054 follows T051–T053. T055, T056, and T057 may proceed in parallel after T052/T054 because each owns a distinct workflow graph; each retains its exact assigned Reviewer, Code Reviewer, Checker, and Roadmap Agent responsibilities.
- T058 serializes shared workflow guidance after all three graph routes. T059 can proceed alongside T060 after graph contracts stabilize because it edits documentation and quickstart paths.
- T060 graph/static regressions follow the graph edits; T061 depends on the helper, all three routes, and owner delivery. T062 waits for all source and tests to establish actual versions; T063 requires those exact pins and the development snapshot. T064 follows installed validation, while T065 live launches and T066 manual fallback may run independently after T063 and T058.
- T067 is the final evidence audit: it requires completed nondeferred new-scope tasks, current fresh Analyze/Remediate evidence for the amended non-marker artifacts, attributable evidence and explicitly recorded gaps, and an independent review. The operator approved audit completion with T066/T077 deferred to dogfooding on 2026-10-09; those task identities and unchecked markers remain unchanged, and the deferral neither supplies manual results nor establishes feature acceptance. Prior 49-task completion and earlier convergence do not satisfy it. Run Converge and Close Out only when separately invoked; production release remains after closeout per the handoff.

### Story 6 Requirement and Success-Criteria Coverage

| Scope | Tasks |
|---|---|
| FR-026 | T054–T057, T060–T061 |
| FR-027 | T052–T055, T060–T061 |
| FR-028 | T052, T054, T056, T060–T061 |
| FR-029 | T052, T054, T057, T060–T061, T067 |
| FR-030 | T057–T061, T067 |
| FR-031 | T050–T052, T055–T057, T060–T061 |
| FR-032–FR-033 | T052–T054, T060–T061 |
| FR-034 | T052, T055–T057, T061 |
| FR-035 | T050–T052, T061, T065–T066 |
| FR-036 | T052–T054, T061, T064 |
| FR-037 | T050–T059, T062–T067 |
| FR-038 | T060–T067 |
| SC-012–SC-013 | T054–T057, T060–T061, T065 |
| SC-014 | T052–T054, T061, T065 |
| SC-015 | T050–T052, T061, T065–T066 |
| SC-016 | T057–T059, T061, T064–T067 |

### Story 6 Incremental Strategy

1. Resolve the exact roadmap and runtime-contract decisions, then obtain the separately owned roadmap extension delivery before implementing any runtime transition.
2. Build the FlowKit adapter and three independently reviewed phase routes; keep owner writes in the owner extension and preserve manual fallback.
3. Pass focused schema, graph and LC001–LC015 checks before version/pin reconciliation and disposable development-snapshot validation.
4. Complete separately requested live-native and manual-fallback evidence, then fresh amended-scope analysis and independent review. Keep Converge, Close Out, production release and acceptance as distinct later work.

---

## Phase 11: User Story 7 - Continue the Full Authorized Implement Scope (Priority: P1)

**Goal**: Retain the operator-authorized requested task scope separately from current eligibility, then reassess and continue newly unblocked scoped work in the same Implement invocation under the existing readiness, authority, review, no-progress, exact-agent and five-pass safeguards.

**Independent Test**: Use the 15 SI cases in `specs/020-flowkit-workflow-iteration-improvements/quickstart.md` against production rendering and the supported installed development snapshot. Demonstrate full versus explicit-subset scope, T050/T051 enabling T052 in the same run, immutable correction history and fresh activation evidence, actual external-owner checks, exact stops, partial effects, and unchanged iteration limits. The manual fallback remains documented; its separate case matrix is waived for closeout and unperformed, with dogfooding findings reported as defects.

### Scope fixtures and source helper

- [X] T068 [P] [US7] Add all 15 adversarial SI001–SI015 fixtures with expected routes, evidence, provenance, and safe-resume fields to `tests/consumer-fixtures/workflow-improvements/implementation-scope-cases.json`, mapped to the Story 7 scenarios, FR-039–FR-048, and SC-017–SC-022 using `specs/020-flowkit-workflow-iteration-improvements/data-model.md` and `specs/020-flowkit-workflow-iteration-improvements/quickstart.md`; explicitly encode per-task `administrative-prerequisite` versus `substantive-implementation` proof, zero administrative progress, the `route-scoped-entry`/`route-scoped-execution` boundary, before-dispatch session/source-attempt history, the shared five-session budget, and the unchanged post-source generic no-progress predicate in SI002, SI003, SI007, SI011, and SI012.
- [X] T069 [US7] After T068, implement the standalone immutable scope, eligibility, task-activation, owner-source, fulfillment-proof, and execution-history validators in `controllers/flow-kit/scripts/python/implementation_scope.py`; preserve legacy version 1.0 behavior, retain every unfinished full-feature task and exact explicit subsets, classify each reviewed task before execution using its `completion_kind` as `administrative-prerequisite` or `substantive-implementation`, validate kind-specific requirement-complete proof, let valid administrative proof discharge requested/dependency accounting while excluding it from `resolved_ids`, `implementation_completed_task_ids`, and `substantive_progress`, and require source preimages/effects/validation/review for substantive completion; append and validate observed Coder-session/source-attempt records before dispatch (including failed or question-stopped dispatches), enforce one monotonic maximum of five modeled Coder sessions across both branches, validate actual owner checkout/access/guidance/route/authority without treating missing installed output as a source-work blocker, and add strict schema/history/proof/budget cases in `tests/test_implementation_scope.py` without depending on delivered roadmap runtime capability.
- [X] T070 [US7] After T054 and T069, add thin `implementation-scope`, `implementation-eligibility`, `implementation-activation`, `implementation-route`, and scoped `implementation-progress` adapters in `controllers/flow-kit/scripts/python/controller.py`; support only the reviewed Implement loop carrier `controller_loop_mode: implementation_scope`, verify its serialized value reaches dispatch, route `route-scoped-entry` and `route-scoped-execution` using actual append-only history and declared node membership, select preparation/first-source by ordinary strict route membership only while no source attempt has started, and after any source-attempt start invoke the unchanged generic `route_loop_assessment` with the actual prior/current substantive assessments and its existing progress/cap predicates; never pass either first-assessment exemption flag or count administrative proof as source resolution. Extend `tests/test_implementation_progress.py` and `tests/test_controller.py` for carrier/history validation, before-dispatch accounting, exact task completion kinds, immutable baselines and activation preimages, append-only predecessor checks, new-finding retention, scoped receipt fields, and unchanged legacy version 1.0 semantics.

### Same-invocation Implement routing and regressions

- [X] T071 [US7] After T056 and T070, extend `workflows/speckit-flow-implement/workflow.yml` with the reviewed `controller_loop_mode: implementation_scope` carrier on the existing five-body `implementation-loop`, an initial `route-scoped-entry` and final in-loop `route-scoped-execution`, and the contract's validated node/branch order; establish the trusted full-feature or exact explicit-subset request and all unfinished-task baseline before assessment, keep eligibility separate, reassess after independent review, Tasker tracking, substantiated prerequisites, and same-child answers, and durably increment the common `coder_sessions_started` before every new modeled Coder dispatch (including administrative/question passes) plus `source_attempts_started` before source dispatch. Permit preparation/first-source routing only before any source attempt; after any attempt keep every continuation behind the unchanged generic prior-remaining/resolved assessment with its actual previous/current substantive assessments and no exemption flags. Same-child answer resumption reuses its consumed session. Preserve readiness, authority, assignment, independent-progress, preparation/source no-progress, partial-effect, blocker, and nonresetting five-session/five-source-attempt stops; never reset or refill either counter. Address F020-LIFECYCLE-CODE-008 by binding post-pass history and successor packets to production node outputs. Tracks F020-LIFECYCLE-CODE-018 completion-validator/capture state consistency.
- [X] T072 [US7] After T060 and T071, extend `tests/test_workflow_graph.py`, `tests/test_workflow_paths.py`, `tests/test_workflow_improvements.py`, `tests/test_controller.py`, and the focused helper suites to validate actual production rendering, `controller_loop_mode` serialization and dispatch, exact initial/final route node placement, and SI001–SI015 behavior. Prove T050/T051→T052 same-invocation activation; administrative versus substantive completion proof and zero admin progress; preparation/first-source routing only before an attempt; actual session and source-attempt records persisted before dispatch including failure/question cases; same-child resumption without another session; a mixed preparation/source run consumes one global five-session budget with no reset/refund; and every post-attempt continuation uses the unchanged generic prior-remaining/resolved predicate, no-progress guard and cap without exemption flags. Retain immutable baselines, activation proof, owner failures, blockers, new findings and partial effects. Tracks F020-LIFECYCLE-CODE-008 by proving successful fresh forwarding and rejection of stale history or successors without replacing the earlier entry output with later state.
- [X] T073 [P] [US7] After T058–T059 and T071, synchronize `workflows/speckit-flow-implement/flowchart.md`, `controllers/flow-kit/controller-protocol.md`, `workflows/README.md`, and `docs/installation.md` with trusted scope establishment, requested-versus-eligible IDs, same-invocation reassessment points, source-owner checks, receipt fields, first-execution/progress distinction, and exact stop/resumption behavior; preserve the approved phase-lifecycle policy, same-child question relay, named-agent assignments, and manual-prompt boundary.

### Supported delivery and independent scope evidence

- [X] T074 [US7] After T062 and T072–T073, register the scope helper/controller operations and reviewed Implement graph version in `controllers/flow-kit/manifest.yml`, workflow metadata and `bundles/spec-kit-flow/bundle.yml`; reconcile actual source versions and hashes rather than guessing version values, preserve the lifecycle and other component pins, and record source coordinates, compatible payloads and exact pin mapping in `specs/020-flowkit-workflow-iteration-improvements/validation/implementation-scope-summary.md`.
- [X] T075 [US7] After T063–T064 and current completion of T071–T072, revalidate completed T073 guidance and T074 metadata/payload provenance against the corrected source, updating only if revalidation finds drift while preserving their completed history; then install/refresh the supported current development snapshot in a disposable initialized consumer and execute all 15 SI001–SI015 cases from `specs/020-flowkit-workflow-iteration-improvements/quickstart.md` against the exact installed helper and rendered Implement workflow. Record actual requested/eligible/pending/completed/outside IDs, per-task completion kinds and proof digests, source and append-only history digests, pre-dispatch session/attempt events, task-specific activation proof, both counters across preparation and source branches, actual previous/current substantive assessments passed to the generic post-source predicate, owner checks, effects, results and limitations in `specs/020-flowkit-workflow-iteration-improvements/validation/implementation-scope-cases.json` and summarize exact commands/results in `specs/020-flowkit-workflow-iteration-improvements/validation/implementation-scope-summary.md`. Tracks F020-LIFECYCLE-CODE-008 by validating actual post-pass durable history and complete Tasker successor outputs, including successful fresh forwarding and stale-history/successor rejection.
- [X] T076 [US7] After T075, separately validate actual launches for every exact native assignment used by the amended Implement scope and eligibility routes in isolated requested contexts; record requested names, actual responses/errors, source/package provenance, context and unsupported effective-setting details in `specs/020-flowkit-workflow-iteration-improvements/validation/implementation-scope-native-cases.json`, preserving unavailable cases and never substituting a generic agent. Tracks F020-LIFECYCLE-CODE-019 prerequisite completion evidence.
- [ ] T077 [US7] Waived for closeout by the direct operator decision recorded in `validation/waived-manual-validation.json`; the original full/restricted-scope manual matrix remains unchecked and unperformed, is not a closeout prerequisite, and may yield defects through ordinary dogfooding without requiring matrix completion.

**Checkpoint**: The immutable operator-requested scope remains complete across changing eligibility; safe newly eligible work continues within the same authorized invocation, while every substantive-progress, owner, human-decision, readiness, iteration and completion boundary retains attributable evidence.

### Story 7 Dependencies and Parallel Opportunities

- T068 fixtures and T069's standalone `implementation_scope.py` work can proceed without the roadmap owner's installed phase capability; T069 does not edit the shared `controller.py` owned by lifecycle task T054. T052's source task validates its actual checkout, access, guidance, route and authority before source effects, and does not require the capability it delivers.
- T070 waits for T054 only because both integrate the shared `controller.py` and progress contract; scope-model/fixture work is not blocked on T052. T071 waits for lifecycle graph T056 because both extend the same Implement workflow, then consumes the T070 adapter and serialized carrier. No owner runtime effect is inferred from building these FlowKit sources.
- T072 serializes shared workflow tests after lifecycle graph tests T060 and the scope route T071; it must exercise the exact controller/workflow integration and five-session cross-branch invariants rather than mock only final receipt shapes. T073 uses the manual/protocol files after graph semantics stabilize. T074 waits for lifecycle component/pin reconciliation T062 and scope source/guidance/tests to avoid concurrent metadata changes.
- T075 validates the combined delivered snapshot after lifecycle snapshot/source checks T063–T064 and current completion of T071–T072; it first revalidates completed T073 guidance and T074 metadata/payload provenance against the corrected source and updates them only if needed, preserving their completion history. T076 native launches and T077 manual-prompt comparisons follow the installed cases; neither claims effective model settings, universal clients, feature acceptance, publication, or production release.

### Story 7 Requirement, Criterion, and Scenario Coverage

| Scope | Tasks |
|---|---|
| FR-039 | T068–T072, T075, T077 |
| FR-040 | T068–T072, T075, T077 |
| FR-041 | T068–T070, T072, T075 |
| FR-042 | T069–T073, T075, T077 |
| FR-043 | T068–T073, T075–T077 |
| FR-044 | T068–T072, T075 |
| FR-045 | T068–T073, T075–T077 |
| FR-046 | T068–T070, T072, T075–T077; owner-source implementation prerequisite T052 |
| FR-047 | T068–T073, T075–T077 |
| FR-048 | T068–T077 |
| SC-017 | T068–T072, T075, T077 |
| SC-018 | T068–T073, T075–T077 |
| SC-019 | T068–T072, T075 |
| SC-020 | T068–T077 |
| SC-021 | T068–T073, T075–T077 |
| SC-022 | T068–T077 |
| SI001 / AC1 | T068–T072, T075 |
| SI002 / AC2 | T068–T072, T075–T077; T052 owner source/access/route evidence |
| SI003 / AC3 | T068–T072, T075, T077 |
| SI004 / AC4 | T068–T072, T075–T077 |
| SI005 / AC5 | T068–T070, T072, T075 |
| SI006 / AC6 | T068–T070, T072, T075 |
| SI007 / AC7 | T068–T073, T075–T077 |
| SI008 / AC8 | T068–T072, T075–T077 |
| SI009 / AC9 | T068–T070, T072, T075–T077 |
| SI010 / AC10 | T068–T070, T072, T075–T077 |
| SI011 / AC11 | T068–T072, T075 |
| SI012 / AC12 | T068–T072, T075 |
| SI013 / AC13 | T068–T072, T075, T077 |
| SI014 / AC14 | T068–T072, T075 |
| SI015 / AC15 | T068–T073, T075–T077 |

### Story 7 Incremental Strategy

1. Create the adversarial 15-case fixtures and standalone scope/history helper without touching lifecycle policy or requiring owner runtime support.
2. Integrate the controller adapters and same-invocation Implement graph after serializing edits to shared controller/workflow files; preserve the approved readiness, task-revision, independent-review and five-pass boundaries.
3. Reconcile source metadata, pins, guidance and a supported consumer snapshot before executing deterministic installed and native evidence; the manual case matrices are waived for closeout and remain unperformed.
4. Reassess current readiness and independently reconcile all new evidence before claiming convergence; historical 51/67 completion and the earlier lifecycle approval do not satisfy Story 7.

## Approved Close Out Recovery Correction (2026-10-09)

These two unchecked tasks implement only the approved correction recorded in the plan. They do not change roadmap dependency wording, establish recovery proof, complete deferred dogfooding, or perform the subsequent independent review, snapshot refresh, Converge, or Close Out phases.

- [X] T078 [US6] In the independently owned `pegagio/spec-kit-flow-roadmap` source, inspect the actual owner checkout, repository identity, dirty/index scope, applicable guidance, permitted source-work route, access, and task authority before editing `scripts/python/phase_lifecycle.py`. Parse the canonical positive dependency list separately from explicit no-dependency annotations so negated references never become edges; reject ambiguous or contradictory declarations, duplicate positive dependencies, and real dependency cycles. Add focused parser regressions and run the current Feature 020 consumer-ledger dependency closure against the delivered owner source, proving the `012`/`014` negated references add no false edges while duplicate positives and real cycles still fail. Record actual source/version/digest and test results; if owner access, route, or authority is unavailable, stop with that exact blocker and safe resumption action. Tracks `F020-CLOSEOUT-EDGE-DEP-PARSER-001` and FR-032, FR-037–FR-038, SC-013–SC-016.
- [X] T079 [US6] After T078, correct the FlowKit Close Out recovery route and its structured evidence helpers in `workflows/speckit-flow-closeout/workflow.yml`, `controllers/flow-kit/scripts/python/phase_lifecycle.py`, `controllers/flow-kit/controller-protocol.md`, `workflows/speckit-flow-closeout/flowchart.md`, and focused tests in `tests/test_phase_lifecycle.py`, `tests/test_workflow_graph.py`, and `tests/test_workflow_paths.py`. Require fresh exact `FlowKit-Roadmap Agent` current-scope linkage/brief, `FlowKit-Reviewer` preparation judgment, main-task recording of that exact verdict, `FlowKit-Readiness Checker` assessment, and `FlowKit-Reviewer` authenticated-start attestation, each bound to actual current scope and input digests. Accept start proof only from an actual recorded invocation/effect with its original occurrence time and source-scope evidence; allow only an independently verified status-only specification bridge, and fail closed when authority or provenance is missing. Preserve the three-adjacent-edge cap, genuine native assignments, owner-only effects, independent receipt verification, separate exact `verified` approval, the T066/T077 closeout waiver, and separation from acceptance/release. Exercise successful and missing, stale, contradictory, fabricated, wrong-role, and changed-scope proof cases through the production-rendered route; verify bounded effects and actual current-ledger integration, then record source provenance, results, and exact remaining gaps without claiming independent review or acceptance. Tracks `SPECCED-PROOF-002`, `INPROGRESS-PROOF-003`, `START-PROOF-004` and FR-032–FR-038, SC-013–SC-016.

### Recovery correction dependencies and coverage

T078 has no task dependency; its owner-source preflight is part of the task and any access or authority failure is a task-specific stop. T079 depends on completed T078 so the Close Out recovery tests can use the actual corrected owner parser and current ledger. The two tasks cover the four stable recovery gaps above; all previous 77 task IDs and markers, including unchecked T066/T077, remain unchanged.

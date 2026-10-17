# Tasks: Prepare specification

**Input**: Approved revised `spec.md` and `plan.md`, `research.md`, `data-model.md`, `contracts/prepare-specification.md` and `quickstart.md` in this feature.

**Status**: Revised spec/plan approved for implementation on 2026-10-17. Active revised tasks: all seven complete (T023–T029). T025 uses operator-reported native completion plus verified subject history/artifacts; T027 includes the completed ordinary clarification answer/review-stop turn. T026 combines operator-confirmed displayed Goal completion with readback showing no subsequent continuation. Historical tasks remain historical; T014/T022 remain superseded/unpassed. Literal checkboxes: 27 checked / 29 total, two unchecked (both historical superseded/unpassed). Revised technical verification is complete; human result review and any remaining authorized local commit are separate.

**Tests**: Acceptance execution is explicitly required by FR-017. Prepare the cases before implementation; observe the actual delivered skill in a separate real Codex session afterward. No new runner/framework is a task prerequisite. Fixture assertions alone cannot satisfy acceptance.

Phases 1–7 and their coverage/order notes below are historical baseline records. Only Phase 8 defines active revised work, after review. Superseded obligations are not passes.

## Phase 1: Setup

- [x] T001 Confirm the current installed command IDs, hooks and prerequisites in `tests/fixtures/prepare-specification/cases.md`, recording actual dependency/runtime identities and missing capability stops without new pins or environment setup. [FR-005, FR-010, FR-011]
- [x] T002 Define small named/eligible/negative-selection, no-question, single/multi-round clarification and interruption cases in `tests/fixtures/prepare-specification/cases.md`; establish the missing-skill baseline before delivery without presenting it as live behavior proof. [FR-001, FR-002, FR-006, FR-009, FR-017]

## Phase 2: Foundation

- [x] T003 Create `.agents/skills/farmboy-prepare-specification/SKILL.md` with standard discovery metadata, the prescribed boundary, one-session/current-model behavior and no implicit later-phase calls, delegation, configuration subsystem or custom controller. [FR-010, FR-011, FR-015]
- [x] T004 Establish an independent real subject session and available observation method in `specs/001-prepare-specification/validation/acceptance.md`; prefer existing automated driving, allow manual evaluation, and record unavailable runtime access as a blocker rather than building a runner or claiming acceptance. [FR-017]

## Phase 3: User Story 1 — Select work and prepare a draft (P1)

**Goal**: One resolved target, relevant cited context and an authored draft with roadmap-fit findings.
**Independent check**: Observe named/eligible and negative cases in the actual subject session, with unrelated entry comparison and no later-phase effects.

- [x] T005 [US1] Implement named/next-eligible selection, established ordering, prerequisite checks and ambiguity/no-work stops in `.agents/skills/farmboy-prepare-specification/SKILL.md`; recognize an already-active same target and do not infer terminal/deferred reactivation. [FR-001, FR-002]
- [x] T006 [US1] Compose selected-entry roadmap-write and bounded wiki-query behavior in `.agents/skills/farmboy-prepare-specification/SKILL.md`, preserving linkage, unrelated entries, citations and governing conflict/gap stops. [FR-003, FR-004, FR-016]
- [x] T007 [US1] Compose existing specify and roadmap-brief skills with current hook/scope handling in `.agents/skills/farmboy-prepare-specification/SKILL.md`; retain the draft, quality checklist and current fit findings instead of duplicating command logic. [FR-005]
- [x] T008 [US1] Observe the delivered skill’s named/eligible and negative cases in the separate real session and record target/context/artifact results in `specs/001-prepare-specification/validation/acceptance.md`; include unmet prerequisites, absent capabilities, ambiguity and wiki gaps/conflicts. [FR-001, FR-002, FR-003, FR-004, FR-005, FR-017]

## Phase 4: User Story 2 — Clarify and stop for review (P1)

**Goal**: Genuine answer waits, supported repeated rounds under the original launch and a separate final specification-review stop.
**Independent check**: Observe both a normal no-question case and deliberately ambiguous single/multi-round cases; scripted test responses never approve live work.

- [x] T009 [US2] Add existing clarify composition, genuine input waits, pending-question notes and a distinct final review stop to `.agents/skills/farmboy-prepare-specification/SKILL.md`; continue routine authorized work without redundant OKs. [FR-006, FR-007, FR-008]
- [x] T010 [US2] Add supported additional-round continuation and honest command/platform blocker handling to `.agents/skills/farmboy-prepare-specification/SKILL.md`, with no fabricated answers, quota bypass or requirement for another restart prompt. [FR-006, FR-008]
- [x] T011 [US2] Finish readable result summaries, current-artifact reconciliation and refresh of a stale roadmap-fit brief in `.agents/skills/farmboy-prepare-specification/SKILL.md`; define necessary terms, show useful examples and preserve the integration-merge history boundary. [FR-007, FR-014, FR-016]
- [x] T012 [US2] Observe a normal settled case executing the actual skill through final review in `specs/001-prepare-specification/validation/acceptance.md`; verify no invented questions, automatic approval, planning/tasks or other later-phase calls. [FR-007, FR-015, FR-017]
- [x] T013 [US2] Observe deliberately ambiguous single/multi-round cases in `specs/001-prepare-specification/validation/acceptance.md`, showing the subject asks and truly waits, incorporates test-only answers, continues supported rounds without restart requests and stops for final review. [FR-006, FR-008, FR-017]
- [ ] T014 **SUPERSEDED / NOT PASSED:** [US2] Observe native Goals activation, input/review stops, interruption/resume and platform/no-progress stopping behavior in the actual supported subject runtime; record the mechanism and results in `specs/001-prepare-specification/validation/acceptance.md` before any compatibility claim, without assuming access or substituting fixture results. [FR-008, FR-012, FR-017]


## Phase 5: User Story 3 — Resume and demonstrate portability (P2)

**Goal**: Current-artifact resume preserves identity and pending decisions; the workflow works in a disposable consumer without Farmboy-specific assumptions.
**Independent check**: Observe pending-question and pending-review resumes in the disposable project, including a changed-artifact variant and no duplicate effects.

- [x] T015 [US3] Add resume revalidation of the standard active-feature pointer, roadmap/spec identity and pending question/review in `.agents/skills/farmboy-prepare-specification/SKILL.md`; reuse existing artifacts without a run ledger or recovery engine. [FR-009]
- [x] T016 [US3] Observe interruption with pending input and pending review, then resume the real subject and record preserved decisions/no duplicate activation or spec creation in `specs/001-prepare-specification/validation/acceptance.md`. [FR-009, FR-017]
- [x] T017 [US3] Demonstrate the actual skill in the disposable Spec Kit project using its own artifacts and rules; record source/runtime provenance and portability results in `specs/001-prepare-specification/validation/acceptance.md`, without a second live-project adoption or per-step agents. [FR-010, FR-013, FR-017]
- [x] T018 [US3] Exercise changed artifacts, already-active identity and changed answers during resume, refine same-target revalidation in `.agents/skills/farmboy-prepare-specification/SKILL.md` if required, and record observed results in `specs/001-prepare-specification/validation/acceptance.md`. [FR-001, FR-008, FR-009, FR-017]

## Phase 6: Documentation and Acceptance Review

- [x] T019 Document invocation, prerequisites, standard project-local placement, manual fallback, examples and limitations in `docs/prepare-specification.md`, retaining simple composition and understandable language without a new installation/configuration system. [FR-011, FR-014]
- [x] T020 Reconcile `specs/001-prepare-specification/spec.md`, `specs/001-prepare-specification/plan.md`, `specs/001-prepare-specification/tasks.md` and the delivered `.agents/skills/farmboy-prepare-specification/SKILL.md`; complete `specs/001-prepare-specification/validation/acceptance.md` with actual results/remaining blockers, targeted privacy/phase-boundary checks and a human delivery-review recommendation. Do not infer acceptance or run closeout/commit/push. [FR-011, FR-015, FR-016, FR-017]

## Dependencies and Execution Order

- T001–T002 establish capabilities/cases before T003. T004 establishes the verification method before any live acceptance task.
- US1: T005 → T006 → T007 → T008. The first useful increment is an observed selected draft; it is not acceptance of the full feature.
- US2: T009 → T010; T011 completes review/reconciliation behavior before final US2 acceptance observations T012–T013; T014 follows the delivered interaction behavior and available actual runtime.
- US3: T015 precedes T016 and T018; T017 collects portability evidence from the same disposable-project runs. Each live test revalidates current source and prerequisites; earlier partial observations cannot establish later changes.
- T019 follows the delivered behavior; T020 follows all required observations and reports any genuine blocker instead of marking unperformed tests complete.

## Parallel Examples and Single-Session Baseline

US1, US2 and US3 each modify the same skill, so implementation edits remain sequential. Independent mechanical comparisons or documentation inspection may use ordinary tools without changing the one-session workflow. No per-story agents, model routing or parallel test platform is proposed; no task is marked `[P]` because useful source/evidence writes overlap.

## Requirement Coverage

| Requirement | Tasks |
|---|---|
| FR-001 | T002, T005, T008, T018 |
| FR-002 | T002, T005, T008 |
| FR-003 | T006, T008 |
| FR-004 | T006, T008 |
| FR-005 | T001, T007, T008 |
| FR-006 | T002, T009, T010, T013 |
| FR-007 | T009, T011, T012 |
| FR-008 | T009, T010, T013, T014, T018 |
| FR-009 | T002, T015, T016, T018 |
| FR-010 | T001, T003, T017 |
| FR-011 | T001, T003, T019, T020 |
| FR-012 | T014 |
| FR-013 | T017 |
| FR-014 | T011, T019 |
| FR-015 | T003, T012, T020 |
| FR-016 | T006, T011, T020 |
| FR-017 | T002, T004, T008, T012, T013, T014, T016, T017, T018, T020 |

## Implementation Strategy

After full-plan review, build the selected-draft increment, add clarification/review, then resume/portability. Keep acceptance observations current with source changes. Failure to observe required supported-runtime behavior blocks the relevant acceptance claim, not a reason to invent infrastructure. No task here is completed by document generation, and no future workflow is launched by this task list.

## Phase 7: Convergence

Assessment: 17 functional requirements, six success criteria, 12 user-story acceptance scenarios, eight grouped plan decisions, all 20 original tasks and three constitutional principles. Two HIGH partial findings; zero missing, contradicts or unrequested findings. No acceptance or native compatibility is inferred from source instructions.

- [x] T021 Resolve the installed clarify whole-session limit through a supported interpretation or an explicitly authorized dependency-policy change, then use the actual delivered skill in a separate real subject to finish the one-question and supported additional-round cases through human specification review; retain genuine waits and never reset a session limit by inference. Record results in `validation/acceptance.md` and complete T013 only when observed. Blocked on that dependency-policy decision; do not edit the dependency or expand authority from this task. [FR-006, FR-017, SC-002, SC-005] (partial, HIGH)
- [ ] T022 **SUPERSEDED / NOT PASSED:** Establish the existing supported native Goal input-stop mechanism and observe interruption/resume and final-review completion with the actual skill in the independent subject. Record the previously observed two continuations followed by stall, avoid repeated no-progress attempts or a replacement controller, and complete T014 only on actual evidence. Blocked on supported runtime behavior and the unfinished clarification path; no compatibility claim is authorized. [FR-012, FR-017, SC-006] (partial, HIGH)

Convergence follow-up: T021 is complete through documented unchanged-core composition and actual single/multi-round review stops; no dependency policy changed. T022 remains blocked on native Goal controls/access. A clean convergence or delivery-acceptance result is not claimed.

## Phase 8: Approved revised draft/handoff delivery

T014/T022 remain unchecked as historical failed/unproved native-wait obligations, superseded by the explicitly approved change of boundary. They are not active implementation tasks and must not be relabeled as passed. Historical completion of T013/T021 proves ordinary clarification under the former composition only.

- [x] T023 Update the existing Farmboy skill to automate selection/context and supported template/helper drafting through saved handoff; do not invoke a full interactive command then bypass its input requirement. End the native Goal at the usable draft/handoff and report inability to confirm completion honestly. [FR-001–005, FR-007–012, FR-016]
- [x] T024 Reconcile usage and fixture documents with ordinary core clarification after the completed Goal, explicit approval before planning and no extra Farmboy skill; preserve old evidence and unsupported-capability limits. [FR-006–007, FR-011, FR-014–015]
- [x] T025 Observe the actual revised skill in an independent subject completing a native Goal at an ambiguous draft/clarification handoff, before any answer, without renewed idle continuation; record artifacts/native state and blockers. [FR-012–013, FR-017; SC-002, SC-005–006]
- [x] T026 Observe the settled/no-question case natively completing at human-review handoff with no manufactured question or approval; verify affected selection/context/resume/portability protections proportionately. [FR-001–005, FR-007–009, FR-012–013, FR-017; SC-001, SC-003–006]
- [x] T027 Separately invoke existing clarify ordinarily after handoff in the real subject; observe a genuine pending question, actual answer incorporation and supported rounds/limits, ending at human review while the preparation Goal stays completed. [FR-006, FR-009, FR-017; SC-002–005]
- [x] T028 Observe no planning without explicit human spec approval: Goal completion, handoff, clarification answers and silence do not qualify. Record the test-only approval prerequisite without entering later workflows. [FR-007, FR-015, FR-017; SC-003]
- [x] T029 Reconcile changed artifacts and evidence, perform fresh targeted convergence/checks and report revised acceptance or concrete remaining blockers before authorized closeout. Preserve the historic failures and distinguish draft-stage success from approval. [FR-011–017; SC-001–006]

Execution order: review revised spec/plan/tasks → T023 → T024 → T025/T026 → T027 → T028 → T029. The revised review gate was explicitly approved on 2026-10-17; source changes have begun. Requirement coverage above is historical; T023–T029 provide current changed-boundary coverage. No new machine, runtime, dependency policy or infrastructure is approved.

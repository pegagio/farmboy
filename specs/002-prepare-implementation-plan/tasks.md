# Tasks: Prepare implementation plan

**Input**: Approved spec and design in `specs/002-prepare-implementation-plan/`.

**Execution status**: Pegagio explicitly approved the 27-task plan and separately selected implementation, independent verification and convergence. Task markers record work performed, not human result acceptance or a passing native compatibility claim. T023 records both supported native observations and the FAILED/UNACCEPTED automatic input-wait case; see validation/acceptance.md. No plan/result approval is inferred from test responses. Core `speckit-plan` produced plan/research/data-model/contracts/quickstart; this list uses the effective `tasks-template` returned by installed `setup_tasks.py`. Human result acceptance was subsequently explicit on 2026-10-17: “That sounds like exactly what we want. I like it”; see [acceptance evidence](validation/acceptance.md#human-result-acceptance). All 31 tasks remain performed. Pegagio subsequently authorized the scoped local delivery commit and roadmap002 verified status; integration remains unauthorized.

**Tests**: The specification explicitly requires independent real-session verification, negative cases and portability. Test tasks below create fixture inputs/expected observations and later record real results; they add no automated harness, controller, metrics or runtime tracking files.

## Table of Contents

Read [Format and paths](#format-and-paths), [Setup](#phase-1-setup), [Foundations](#phase-2-foundational), [Story 1](#phase-3-user-story-1--prepare-reviewable-work-priority-p1), [Story 2](#phase-4-user-story-2--reconcile-findings-priority-p1), [Story 3](#phase-5-user-story-3--review-and-resume-priority-p2), [Cross-cutting work](#phase-6-polish-and-cross-cutting-concerns), [Dependencies](#dependencies-and-execution-order), [Parallel examples](#parallel-examples), [Strategy](#implementation-strategy) and [Coverage](#requirement-and-outcome-coverage) and [Approved revision](#phase-7-approved-human-input-automation-handoff-revision).

## Format and paths

Every task uses `- [ ] Tnnn [P?] [USn?] description with exact file path`. `[P]` denotes file-independent work with no dependency on another incomplete task in the same phase; it does not authorize subagents or concurrent runtime feature owners. Source/docs/fixtures follow the paths in plan.md; no entity classes or persisted schema are needed for the conceptual data model.

## Phase 1: Setup

Confirm the reviewed installation and establish test cases without installing tools or changing global settings.

- [X] T001 Revalidate the existing core skills/helpers/templates/hooks and approved-spec metadata distinction; update only drifted design evidence in specs/002-prepare-implementation-plan/research.md, stopping for material intent changes or missing prerequisites (FR-001, FR-002, FR-003).
- [X] T002 [P] Create tests/fixtures/prepare-implementation-plan/cases.md with the disposable greeting fixture, test-only approval context, real-subject/evaluator distinction, version/source attribution procedure and expected absence of runtime state machinery; keep fixture inputs distinct from actual observations (FR-013, FR-014).

## Phase 2: Foundational

After T001–T002, establish one skill and guide, without implementing a reusable controller or copied core commands. No story begins until these shared boundaries are explicit.

- [X] T003 Create .agents/skills/farmboy-prepare-implementation-plan/SKILL.md metadata, selected-scope/one-session/current-model-effort boundary and capability checks; quote and enforce “One selected feature; explicit and ambient identity must agree before effects.” and forbid automatic activation, installation, Goal creation, implementation, commit, merge, push or next-workflow launch (FR-001, FR-011, FR-015).
- [X] T004 [P] Create docs/prepare-implementation-plan.md with the ordinary named-skill interface and explicit distinction between prerequisite specification approval and future human full-plan approval; quote “Explicit approval of current meaning is required; material changes require affected human review.” without adding a register (FR-002, FR-010, FR-011).

## Phase 3: User Story 1 — Prepare reviewable work (Priority: P1)

Deliver an approved-spec-to-proposal happy path with strict authorization gates. This is the incremental MVP, not acceptance of the full feature without Stories 2–3.

**Independent test**: A separate real subject runs the actual skill in a disposable project for an approved greeting spec. Observe plan/design/tasks and fresh clean analysis, current proposal links and Awaiting full-plan review; no greeting implementation or inferred approval. Negative approval cases stop before planning.

- [X] T005 [US1] Add positive conversational/note approval, missing approval, clarification-only approval negative, material-change uncertainty, identity conflict and missing prerequisite/capability cases to tests/fixtures/prepare-implementation-plan/cases.md before testing the skill (FR-001, FR-002; Story 1 scenarios 1–7).
- [X] T006 [US1] Implement identity/prerequisite/current-stage inspection and approval evidence recognition in .agents/skills/farmboy-prepare-implementation-plan/SKILL.md: available conversation OR applicable existing content-identifying review note is sufficient; no repeated approval when applicable, and no approval from silence, answers, analysis or Goal completion (FR-001, FR-002).
- [X] T007 [US1] Compose actual installed speckit-plan then speckit-tasks in .agents/skills/farmboy-prepare-implementation-plan/SKILL.md, honoring each command's helper/template requirements, mandatory/optional/conditional hook rules and actual input stops rather than reproducing command bodies or ignoring failures (FR-003, FR-008).
- [X] T008 [US1] Compose actual read-only speckit-analyze only after complete tasks in .agents/skills/farmboy-prepare-implementation-plan/SKILL.md; enforce “A pass requires zero actionable inconsistencies and zero unmet requirements, regardless of severity.”, latest-artifact analysis and “No actionable inconsistency or unmet requirement may be relabeled optional.” before full-plan handoff (FR-004, FR-010).
- [X] T009 [US1] Add ordinary invocation, clean-proposal links, optional-suggestion disclosure and no-approval/no-implementation examples to docs/prepare-implementation-plan.md, aligned with contracts/prepare-implementation-plan.md (FR-008, FR-010, FR-015).
- [X] T010 [US1] Independently observe the actual skill's clean proposal and prerequisite/approval negative cases in a separate real Codex subject; record source versions, session references, artifacts, actual outcomes and limitations in specs/002-prepare-implementation-plan/validation/acceptance.md rather than inferring success from fixture text (FR-013, FR-014; SC-001, SC-003, SC-006).

## Phase 4: User Story 2 — Reconcile findings (Priority: P1)

Add separate authorized repair and honest qualitative incomplete handoff. Story 1's complete command composition is reused; its happy-path evidence must not be invalidated.

**Independent test**: In an approved fixture, omit a required task, inspect unchanged artifacts immediately around analysis, then observe the separate automatic routine repair and later fresh analysis. Exercise severity/optional disguise and genuine input or unsuccessful-approach stops. Do not fabricate failed attempts or count cycles.

- [X] T011 [US2] Add missing-coverage repair, LOW/optional-labeled actual defect, optional-only result, useful continuation and genuinely stuck/repeated unsuccessful approach/required-decision scenarios to tests/fixtures/prepare-implementation-plan/cases.md; prescribe before/after source comparison around actual analysis and no numeric/counter policy (FR-004, FR-005, FR-007; SC-002, SC-007).
- [X] T012 [US2] Implement the separate routine in-scope repair step in .agents/skills/farmboy-prepare-implementation-plan/SKILL.md, already authorized by selected workflow; keep each analysis invocation read-only, perform edits outside it without per-repair approval and run fresh analysis after the last affected edit (FR-004, FR-005; SC-001, SC-002).
- [X] T013 [US2] Implement qualitative continuation/stopping in .agents/skills/farmboy-prepare-implementation-plan/SKILL.md: repair actionable findings, reanalyze and continue useful authorized work; stop INCOMPLETE when genuinely stuck, repeating unsuccessful approaches or requiring a human decision, explaining attempts and remaining issues using existing analysis/spec/plan/tasks only; enforce “Edits alone prove neither progress nor passing; no numeric limits, counters, scores or new persistence.” and forbid reset semantics, accounting/controller/database/ledger/metrics/tracking machinery or renamed equivalents (FR-007, FR-008; SC-007).
- [X] T014 [US2] Implement current-feature flow-back and new-decision/scope/material-intent review stops in .agents/skills/farmboy-prepare-implementation-plan/SKILL.md; preserve approved meaning, reject historical-feature rewrites and stop dependent work for required constitutional amendment authority rather than weakening governance (FR-005, FR-006, FR-008).
- [X] T015 [US2] Independently observe real read-only analysis, separate repair without repeated approval, fresh zero-defect result, optional-only review and actual incomplete/input behavior in a separate real subject; preserve actual attempts and gaps in specs/002-prepare-implementation-plan/validation/acceptance.md, leaving unsupported cases incomplete (FR-004–FR-008, FR-013; SC-001–SC-003, SC-006, SC-007).
- [X] T016 [US2] Document read-only-versus-repair authority, fresh-pass rule and concise INCOMPLETE examples in docs/prepare-implementation-plan.md, explaining no numeric/counter/tracking machinery and no polishing loop for optional suggestions (FR-004, FR-005, FR-007, FR-008).

## Phase 5: User Story 3 — Review and resume (Priority: P2)

Make the proposal understandable and resumable without additional state. Implement review/resume behavior before exercising the corresponding independent cases.

**Independent test**: Review an actual full proposal's additions/alternatives, request an in-scope simplification, interrupt/resume partial preparation and a saved review, change an affected artifact and inspect fresh reassessment. Verify the same feature, task identities and accepted decisions survive; Goal/analysis success is never approval.

- [X] T017 [US3] Add full-plan machinery review, simplification, partial/pending-review resume, changed answers/artifacts, applicable historical approval and native supported/unsupported-control cases to tests/fixtures/prepare-implementation-plan/cases.md before real evaluation (FR-001, FR-009–FR-013; SC-003–SC-007).
- [X] T018 [US3] Implement whole-proposal review in .agents/skills/farmboy-prepare-implementation-plan/SKILL.md with each new subsystem's responsibility, concrete need, alternatives, tradeoffs and recommendation, explicit absence when none is added, and FR-007/FR-009 explanation of existing-capability minimality; no plan approval or implementation follows automatically (FR-009, FR-010, FR-011, FR-015; SC-004, SC-007).
- [X] T019 [US3] Implement current-artifact-based partial/review/revision resume in .agents/skills/farmboy-prepare-implementation-plan/SKILL.md; enforce “Preserve current artifacts, accepted decisions and existing task identities on resume.”, avoid duplicate setup/activation, honor rejected repairs and changed answers, and invalidate analysis after affected edits (FR-001, FR-004, FR-006, FR-008; SC-005).
- [X] T020 [US3] Implement supported-native-capability boundaries in .agents/skills/farmboy-prepare-implementation-plan/SKILL.md: no automatic Goal creation or completed-spec-Goal revival, exact objective inspection when separately selected, completion only for a matching verified whole objective, INCOMPLETE compatibility on required input/unsupported behavior, and no invented pause/receipt/native-state mutation or controller (FR-012, FR-015; SC-003, SC-006).
- [X] T021 [US3] Finish docs/prepare-implementation-plan.md with full-plan review/simplification, same-feature resume, machinery alternatives and native compatibility limitations; distinguish supported observed behavior from future verification and keep standalone analyzer behavior unchanged (FR-009–FR-012; SC-004, SC-005).
- [X] T022 [US3] Independently observe actual review/simplification, partial/pending-review resume, changed answers/artifacts and preserved task/completion evidence in a separate real subject; record source/session references and any blockers in specs/002-prepare-implementation-plan/validation/acceptance.md (FR-001, FR-004, FR-006, FR-009, FR-010, FR-013; SC-003–SC-006).
- [X] T023 [US3] Independently verify native continuation, required-input stop, review handoff and interruption/resume only through actually exposed supported controls and separately operator-selected bounded Goal context; record observed success/failure in specs/002-prepare-implementation-plan/validation/acceptance.md, keep the completed specification Goal untouched and leave incompatible/unavailable cases unaccepted rather than build infrastructure (FR-012, FR-013; SC-003, SC-005, SC-006).

## Phase 6: Polish and cross-cutting concerns

Finish portable delivery evidence and documentation without a delivery commit or next workflow. Optional polish must not become an endless readiness gate.

- [X] T024 Add the delivered planning-skill entry point and links to README.md without rewriting Feature 001's historical boundary or implying automatic approval/delivery (FR-010, FR-011, FR-015).
- [X] T025 Independently exercise the complete delivered workflow in a separately initialized disposable Spec Kit project using its own configuration/governing artifacts; record actual hook behavior, portability, source/session attribution and missing-capability/identity/prerequisite results in specs/002-prepare-implementation-plan/validation/acceptance.md (FR-001, FR-003, FR-013, FR-014; SC-001–SC-007).
- [X] T026 Reconcile the now-delivered skill/guide/fixtures with specs/002-prepare-implementation-plan/quickstart.md, execute its authorized real validation scenarios and appropriate ad hoc link/format/privacy/source-scope checks, preserving any failed native observations and leaving required unperformed work incomplete (FR-011–FR-014; SC-006, SC-007).
- [X] T027 Reconcile affected spec/plan/tasks and final delivery observations in specs/002-prepare-implementation-plan/validation/acceptance.md, distinguishing actual implementation verification from human acceptance; stop for material-intent review or unresolved defects, and make no commit, integration, push, automatic plan approval or next-workflow transition (FR-006, FR-008, FR-015).

## Dependencies and execution order

This is a small single-session workflow: most functional changes share one skill file, so serial story implementation is deliberate. No workers/delegation/runtime parallelism are proposed.

Setup T001/T002 precedes foundations T003/T004. Each story follows foundations; the full command happy path in US1 precedes the US2 repair additions and US3 resume/review extensions. Tests for each story are defined before its implementation and actual independent evaluation follows that story's completed changes. For a story-specific development check, a prepared fixture may supply already-existing plan/tasks so US2/US3 can be exercised independently of generator setup; all stories must still pass together for final delivery.

The order is Setup → Foundations → US1 → US2 → US3 → cross-cutting verification. In a future implementation, T015 and T022/T023 use separate evaluator/subject sessions by constitutional acceptance requirement, not per-node runtime delegation. T025 verifies the combined result after all stories. T027 cannot mark unsupported runtime cases or unmet requirements complete.

Within a story, fixture task precedes skill changes, dependent edits to the same file run serially, and observation follows working source. Guide/fixture files do not execute a workflow by themselves. No migration, server, database, field-validation module or generated model is required: the data-model constraints are instructions over existing artifacts, quoted in the implementing tasks.

## Parallel examples

These are file independence examples only. Existing session/owner constraints still govern execution; `[P]` never authorizes spawning agents.

| Scope | Independent file work after prerequisites | Constraint |
|---|---|---|
| Setup | T001 research evidence and T002 fixture skeleton | No shared file; neither depends on the other's result |
| Foundation | T003 skill boundary and T004 guide boundary | Both follow Setup; distinct files |
| US1 | T009 guide can be drafted separately from the completed T006–T008 skill changes | Verify final alignment before T010; skill edits themselves are serial |
| US2 | T016 guide can be drafted from the approved design while T012–T014 skill sections are edited serially | T015 observes finished matching source; no `[P]` claim for shared skill or acceptance files |
| US3 | T021 guide can be drafted separately from T018–T020 skill changes | Native/review observations follow completed source; acceptance writes remain serial |

## Implementation strategy

After explicit full-plan approval and separately selected implementation, deliver an incremental US1 happy path with approval gates and independent evidence. Then add US2 repairs and US3 review/resume/native-boundary behavior, preserving earlier source and evidence. The MVP is a development increment, not permission to accept incomplete full-feature delivery. A minimal no-question/clean-analysis fixture can demonstrate US1 independently; defect and resume fixtures independently test the later stories.

Keep one Markdown skill and existing-command composition; do not add a subsystem to implement the stopping rule. If the implementation reveals a genuine new decision or material change, save current evidence and return to affected review. If native controls or required real-session verification are unavailable, report the exact INCOMPLETE compatibility/acceptance gap. Source checks and unchecked fixture expectations do not substitute for observed delivery.

## Requirement and outcome coverage

The mapping supports read-only analysis; it is not a runtime registry or a task-completion claim. Every outcome here requires buildable skill behavior or acceptance verification, so all SC entries are included.

| Requirement/outcome | Tasks |
|---|---|
| FR-001 | T001, T003, T005, T006, T019, T022, T025 |
| FR-002 | T001, T004, T005, T006, T010 |
| FR-003 | T001, T007, T025 |
| FR-004 | T008, T011, T012, T015, T016, T019 |
| FR-005 | T011, T012, T014, T015, T016 |
| FR-006 | T014, T019, T022, T027 |
| FR-007 | T011, T013, T015, T016, T018 |
| FR-008 | T007, T009, T013, T014, T016, T019, T027 |
| FR-009 | T017, T018, T021, T022 |
| FR-010 | T004, T008, T009, T017, T018, T021, T022, T024 |
| FR-011 | T003, T004, T016, T018, T021, T024, T026 |
| FR-012 | T017, T020, T021, T023, T026 |
| FR-013 | T002, T010, T015, T017, T022, T023, T025, T026 |
| FR-014 | T002, T010, T025, T026 |
| FR-015 | T003, T009, T018, T020, T024, T027 |
| SC-001 | T007, T008, T010, T012, T015, T025 |
| SC-002 | T008, T011, T012, T013, T015, T025 |
| SC-003 | T005, T006, T010, T014, T015, T020, T022, T023, T025 |
| SC-004 | T017, T018, T021, T022, T025 |
| SC-005 | T017, T019, T022, T023, T025 |
| SC-006 | T002, T010, T015, T022, T023, T025, T026 |
| SC-007 | T011, T013, T015, T017, T018, T025, T026 |

At the bootstrap-planning checkpoint these tasks did not authorize implementation; the subsequent explicit plan approval and implementation selection now supply that authority. No task introduces a new numeric stopping rule or accounting machinery, and no task authorizes a commit.

## Phase 7: Approved human-input automation handoff revision

Pegagio explicitly approved the narrow changed specification/design and its implementation/verification: “Yeah, sounds good. It sounds like Farmboy is - I like your recommendation. Let's go ahead and use that idea.” This is material authority for the bounded human-input endpoint, not a metadata-only extension of earlier digests or result approval. T001–T027 retain their performed status and historical native failure. Phase 7 supersedes their prior endpoint-only assumptions where necessary; it never retroactively changes the recorded native failure or completion evidence. Execute T028 → T029 → T030 → T031 serially. No Feature004 bridge behavior belongs here.

- [X] T028 Reconcile specs/002-prepare-implementation-plan/spec.md, plan.md, contracts/prepare-implementation-plan.md, data-model.md and research.md with the approved review-ready OR durable INCOMPLETE-for-human-input automation objective; define focused cases in tests/fixtures/prepare-implementation-plan/cases.md before source changes, retaining strict passing/approval/no-machinery boundaries and historical failure (FR-008, FR-010, FR-012, FR-013; SC-003, SC-005, SC-006).
- [X] T029 Implement objective/capability-checked completion only after durable required-input handoff and before waiting in .agents/skills/farmboy-prepare-implementation-plan/SKILL.md; reconcile docs/prepare-implementation-plan.md and specs/002-prepare-implementation-plan/quickstart.md; ordinary actual-answer continuation never automatically creates/reactivates a Goal, completes an overscoped objective or generalizes to technical failures (FR-004, FR-005, FR-008, FR-010, FR-012, FR-015).
- [X] T030 Independently execute the actual revised skill using a focused existing disposable greeting fixture and separately authorized bounded native Goal; observe durable INCOMPLETE, supported native complete readback BEFORE any answer, then ordinary real-answer continuation to fresh zero-defect full-plan review with unchanged completed Goal and no inferred approval/implementation; preserve source/session/native evidence and limitations in specs/002-prepare-implementation-plan/validation/acceptance.md (FR-012, FR-013; SC-002, SC-003, SC-005, SC-006).
- [X] T031 Reconcile final evidence/status in specs/002-prepare-implementation-plan/validation/acceptance.md, verify protected bridge hashes, perform focused format/link/privacy checks, fresh read-only speckit-analyze and approved speckit-converge; preserve T001–T027 and FAILED/UNACCEPTED automatic wait history and stop at human result review without acceptance or Git integration (FR-004, FR-006, FR-011–FR-015; SC-006, SC-007).

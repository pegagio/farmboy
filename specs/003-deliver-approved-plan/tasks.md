# Tasks: Deliver approved plan through closeout

**Input**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [operator contract](contracts/deliver-approved-plan.md), [quickstart](quickstart.md).

**Status**: Full-plan approval and composite implementation/verification/convergence/delivery were explicitly selected. Markers below count actual performed work only; runtime observations remain unchecked until actually obtained. This document is not implementation or test evidence. Tests are included because FR-015/SC-006 and the spec's independent tests expressly require actual-session verification and portability. Subsequent actual independent postcommit readback completed T030/T032; all33 markers now record performed work. Pegagio explicitly accepted the reviewed result with its disclosed limits; see [acceptance evidence](validation/acceptance.md#human-result-acceptance-and-postcommit-reconciliation).

## Table of Contents

Tasks follow the installed template's setup/foundation/story/polish organization with stable sequential identities.

- [Format and paths](#format-and-paths)
- [Phase 1: Setup](#phase-1-setup)
- [Phase 2: Foundation](#phase-2-foundation)
- [Phase 3: US1 — Approved eligible delivery](#phase-3-us1--approved-eligible-delivery)
- [Phase 4: US2 — Verification and convergence repair](#phase-4-us2--verification-and-convergence-repair)
- [Phase 5: US3 — Closeout and result review](#phase-5-us3--closeout-and-result-review)
- [Phase 6: US4 — Native handoff and resume](#phase-6-us4--native-handoff-and-resume)
- [Phase 7: Documentation and full validation](#phase-7-documentation-and-full-validation)
- [Dependencies and execution order](#dependencies-and-execution-order)
- [Implementation strategy](#implementation-strategy)
- [Phase 8: Convergence](#phase-8-convergence)

## Format and paths

Each line uses `- [ ] Tnnn [USn] description with path`. All paths are repository-relative. No task is marked parallel because the skill, fixtures and acceptance evidence share files, and runtime steps must stay in the selected session without delegation. Independent evaluator/subject observation is a later verification arrangement, not a delegated step in the delivered workflow. This proposal adds no dependency, core-skill change, controller, bookkeeping store or numeric repair policy.

## Phase 1: Setup

Define expected tests first; fixture text alone never marks behavior verified.

- [X] T001 Define the complete positive/negative/repair/closeout/native/resume/lifecycle case matrix from the 22 spec scenarios in tests/fixtures/deliver-approved-plan/cases.md, including fixture-only approvals, actual evaluator/subject separation and unperformed-case semantics (FR-015; SC-001–007).
- [X] T002 Prepare the ordinary evidence outline in specs/003-deliver-approved-plan/validation/acceptance.md, explicitly separating expected cases from future actual observations, limitations, approvals and human result acceptance; do not claim any case performed (FR-008/015).

## Phase 2: Foundation

Reuse installed command contracts; no infrastructure implementation is required.

- [X] T003 Create .agents/skills/farmboy-deliver-approved-plan/SKILL.md with valid frontmatter, bounded authority, capability resolution and the exact constraint “Explicit selected identity and ambient active-feature identity must agree before effects.” Require contained paths, verified dependencies and applicable explicit spec/full-plan approval (FR-001–004).
- [X] T004 Add governing boundaries to .agents/skills/farmboy-deliver-approved-plan/SKILL.md: existing model/effort, no delegated runtime steps, separate material-change review, no core-skill/tool installation and no controller/counter/reset/score/new-persistence/accounting machinery; no scope/dependency/governance or future 004 expansion (FR-002/014/016).

## Phase 3: US1 — Approved eligible delivery

Goal: implement the right approved work through actual existing capabilities. Independent test: observe correct positive execution and pre-effect negative stops in a real disposable subject.

- [X] T005 Refine US1 fixture inputs/expected observations before source changes in tests/fixtures/deliver-approved-plan/cases.md for conversation/note approval, missing/changed approval, identity mismatch, unready prerequisites, missing capability/mandatory hook and unrelated work (US1/AC1–4; SC-001).
- [X] T006 Implement ordinary installed speckit-implement invocation and applicable verification in .agents/skills/farmboy-deliver-approved-plan/SKILL.md, preserving its actual checklist gate, required input and mandatory/optional/conditional hook handling rather than emitting labels (FR-003/004/008).
- [X] T007 Document invocation, approvals, scope and protected unrelated work in docs/deliver-approved-plan.md with the operator contract's examples and no implied next-workflow authority (US1/AC1–4; FR-001–004/016).
- [X] T008 Independently observe actual US1 positive and negative cases using the real final skill in a disposable project; record session/source/commands/readback/limitations in specs/003-deliver-approved-plan/validation/acceptance.md without changing real Farmboy approvals (FR-008/015; SC-001).
- [X] T009 Check actual US1 source/observations against the approved constraints and privacy/path rules in .agents/skills/farmboy-deliver-approved-plan/SKILL.md and specs/003-deliver-approved-plan/validation/acceptance.md; keep unavailable cases unpassed (FR-001–004/014/016).

## Phase 4: US2 — Verification and convergence repair

Goal: drive actual required gaps to completion without hiding decisions or waived defects. Independent test: real missing behavior, useful repair, optional-only and required-decision cases.

- [X] T010 Define US2 missing/partial/conflicting/unverified behavior, severity disguise, optional-only, material-decision and stale-pass cases in tests/fixtures/deliver-approved-plan/cases.md before adding the repair composition (US2/AC1–5; SC-002/003).
- [X] T011 Compose ordinary installed speckit-converge after implementation in .agents/skills/farmboy-deliver-approved-plan/SKILL.md, honoring append-only follow-up tasks, clean-result byte preservation and subsequent implement/affected-check/reassessment (FR-003–005).
- [X] T012 Add separate authorized current-scope flow-back/repair and honest stop rules in .agents/skills/farmboy-deliver-approved-plan/SKILL.md, quoting “Zero actionable gaps and zero unmet obligations are required for clean delivery.” Preserve findings of any severity, accepted intent and merged history; stop for material changes or genuinely stuck work without numeric quotas (FR-005–008/014).
- [X] T013 Independently observe real US2 repair, genuine required input, optional-only and changed-evidence cases and preserve actual attempts/results in specs/003-deliver-approved-plan/validation/acceptance.md; do not fabricate repeated failure or pass from edits (FR-008/015; SC-002/003).
- [X] T014 Explain useful continuation, separate flow-back, genuine stops and fresh evidence requirements in docs/deliver-approved-plan.md, including no counters/reset/scoring/persistence substitutes (US2/AC1–5; FR-006–008/014).

## Phase 5: US3 — Closeout and result review

Goal: finish a coherent local candidate, then implemented/result review with no acceptance/integration inference. Independent test: real closeout, scoped final-commit contents and acceptance boundaries with ordinary Git/roadmap readback.

- [X] T015 Define US3 debrief/wiki findings, unsafe/unrelated commit scope, final scoped commit including implemented update, required-input/check stops and later explicit acceptance cases in tests/fixtures/deliver-approved-plan/cases.md; no forced commit-error test or special failure procedure (US3/AC1–7; SC-004).
- [X] T016 Compose installed roadmap-debrief on an actual attributable delta and relevant one-source wiki-ingest followed by wiki-lint in .agents/skills/farmboy-deliver-approved-plan/SKILL.md, with coherent delivery documentation, authorized routine correction and stale-assessment refresh; keep debrief recommendations separate from status authority (FR-007–009).
- [X] T017 Add the clarified ordinary delivery order to .agents/skills/farmboy-deliver-approved-plan/SKILL.md: finish required checks/documents, include the narrow implemented update with all scoped delivery artifacts, inspect scope/protect unrelated work, then make the final local commit. Report success only after actual commit success; report ordinary Git errors honestly without custom handling or new machinery (FR-010–012).
- [X] T018 Document the human-requested final scoped commit and its ordinary error reporting in docs/deliver-approved-plan.md; quote “Successful local delivery records implemented and hands off Awaiting result review; only subsequent explicit applicable human result acceptance separately authorizes verified.” Keep debrief recommendation-only, later acceptance outside delivery and integration separate (FR-009–011/014/016).
- [X] T019 Independently observe actual successful closeout with real debrief/ingest/lint and the implemented update plus all scoped delivery artifacts in the final authorized local fixture commit; record the actual commit and result-review handoff in specs/003-deliver-approved-plan/validation/acceptance.md (FR-008/015; SC-004).
- [X] T020 Inspect the observed final scoped commit and ordinary success-reporting boundary against tests/fixtures/deliver-approved-plan/cases.md; record in specs/003-deliver-approved-plan/validation/acceptance.md that implemented and scoped delivery artifacts are included, unrelated work is preserved and no success is asserted without actual commit success. No bespoke failure handling or forced Git-error experiment is required (US3/AC3/4/7; SC-004).
- [X] T021 Verify separately scoped fixture result-acceptance recording and debrief-only/nonacceptance negative cases from tests/fixtures/deliver-approved-plan/cases.md; document in specs/003-deliver-approved-plan/validation/acceptance.md that only actual applicable explicit acceptance authorizes verified and delivery itself never performs it (US3/AC5/6; FR-009/011).
- [X] T022 Reconcile the actual delivered skill, guide and closeout evidence in specs/003-deliver-approved-plan/validation/acceptance.md against every US3 scenario, especially incomplete non-advancement, no falsely inferred approval/integration and no undefined completion prerequisite (FR-009–011/016; SC-004).

## Phase 6: US4 — Native handoff and resume

Goal: preserve genuine input/approval boundaries and existing artifacts across interruptions. Independent test: matching native endpoint and actual later ordinary answer continuation, plus changed-artifact/pending-review resume.

- [X] T023 Define US4 partial resume, intact pending review, changed answers/evidence, bounded required-input/success endpoints, overscoped objective, unknown failure and unavailable-control cases in tests/fixtures/deliver-approved-plan/cases.md before source changes (US4/AC1–6; SC-005/007).
- [X] T024 Implement bounded native handoff rules in .agents/skills/farmboy-deliver-approved-plan/SKILL.md, quoting “Save the complete matching endpoint and verify supported native complete readback before requesting or waiting for human input.” Save INCOMPLETE outcome/exact input/artifacts/actual work/issues/next action only in existing notes; no success for arbitrary failures or unmet delivery-only objectives and no automatic Goal create/reactivation (FR-013/014).
- [X] T025 Implement current-artifact/Git/approval resume checks in .agents/skills/farmboy-deliver-approved-plan/SKILL.md preserving answers/task identities/checked evidence, reevaluating affected stale checks and presenting valid pending review without duplicate effects (FR-002/008/012/013).
- [X] T026 Document matching-objective limits, completion-before-input, incomplete-delivery versus successful-handoff distinction and separately selected ordinary continuation in docs/deliver-approved-plan.md without implying automatic waiting/resume works (FR-012/013; SC-005/007).
- [X] T027 Independently observe actual supported native settled/input endpoints and answer timing in a separately operator-selected bounded fixture Goal, plus negative objective/control/failure cases; record actual complete readback and limitations in specs/003-deliver-approved-plan/validation/acceptance.md without native-file mutation (FR-013/015; SC-007).
- [X] T028 Independently observe actual interruption/changed-artifact/changed-answer/pending-review resume and ordinary continuation outside the completed Goal; record preserved identities/evidence and absence of duplicate effects in specs/003-deliver-approved-plan/validation/acceptance.md (FR-008/012/015; SC-005).

## Phase 7: Documentation and full validation

Complete actual cross-story verification and expose the result; these tasks never bypass human gates.

- [X] T029 Link the delivered workflow guide and honest verification evidence from README.md without declaring acceptance, integration or future 004 delivery (FR-008/016).
- [X] T030 Independently demonstrate the complete local 001→002→003 lifecycle in Farmboy and a disposable Spec Kit project with the final delivered skill: actual clarification, separate explicit spec/full-plan approvals, repair, closeout, input/review stops and interruption/resume. Re-run every earlier case affected by subsequent source/artifact changes; preserve earlier observations as historical and record fresh results, exact source identity and unverified limits in specs/003-deliver-approved-plan/validation/acceptance.md. Do not rely on stale intermediate passes or claim unperformed Farmboy delivery from disposable evidence. Under explicit affected sequencing approval, perform required precommit observations first; independently observe actual final Farmboy commit/result after it exists and before successful result-review handoff. Keep this marker pending through commit; report postcommit performed completion in ordinary conversation without a receipt-only commit (FR-008/015; SC-001–007).
- [X] T031 Run focused Markdown/frontmatter/link/privacy checks and git diff --check on .agents/skills/farmboy-deliver-approved-plan/SKILL.md, docs/deliver-approved-plan.md, tests/fixtures/deliver-approved-plan/cases.md and current feature artifacts; use the prescribed skill Python environment if Python validation is used, and report dependencies rather than install them (FR-008/014; SC-001–007).
- [X] T032 Reconcile specs/003-deliver-approved-plan/spec.md, plan.md, tasks.md and validation/acceptance.md to actual work/results and present human result review with actual findings/limits; complete required artifact reconciliation before commit, then present successful result review only after actual independent postcommit result readback. Keep the final-observation portion/marker pending through commit; report actual completion in ordinary conversation without a receipt-only commit. No task marker, test or native Goal outcome grants acceptance, verified, integration, commit, merge or push authority beyond separately selected work (FR-007–013/015/016).

## Dependencies and execution order

The phase graph is Setup→Foundation→US1→US2→US3→US4→full validation. Later stories compose earlier behavior, but their fixture cases are independently testable with prepared approved current artifacts. Runtime steps stay sequential within the subject session.

T001/T002 precede source work. T003→T004 establish the common boundary. Within each story, expectations precede related source changes, then actual observation and guide/evidence reconciliation. US3 observations require the closeout/order behavior in T016–T018; US4 observations require T024–T026. T030 requires all stories and independent actual Farmboy execution using real approvals. Its precommit observations/checks precede commit; independent actual final commit/result observation follows commit and precedes successful human result-review handoff. T032 reconciles current artifacts before commit and concludes result review after that observation. Their pending postcommit portions do not block the scoped commit they must observe and are not passed in advance. T033 resolves sequencing before these steps. The current separately selected composite and affected approval authorize delivery/status/final local commit, never verified or integration.

Parallel examples: US1's shared source/evidence tasks are sequential; likewise US2, US3 and US4 each mutate the same skill/case/evidence files. There is no safe runtime parallel agent strategy proposed. Documentation and static reads may be batched when independent, but no [P] task implies delegated execution.

## Implementation strategy

US1 is the MVP for correct eligible implementation; it is not the full delivery feature or permission to skip later requirements. Incrementally add actual repair, local closeout and native/resume behavior, verifying each story before full-lifecycle observation. All 32 tasks are required for this proposal; no speculative polish task or extra framework is included. Each checkbox is checked only after genuine implementation/evidence under the separately selected execution authority. Do not insert template boilerplate commits after each task.

## Phase 8: Convergence

The historical assessment appended T033 for the genuine bootstrap evidence sequencing question. The human has now explicitly resolved that question; the required evidence is preserved and observed at its applicable stage.

- [X] T033 Record the exact subsequent human approval (“Yes”) of the explained sequencing correction in spec.md, plan.md, tasks.md, validation/acceptance.md and delivery.md: retain required precommit evidence and independent real-Farmboy execution; observe the actual final Farmboy commit/result independently after it exists and before successful human result review. Align T030/T032 dependencies without passing pending observations, recursive self-delivery, waived tests, new machinery or a receipt-only commit (T030; FR-008/015; SC-006).

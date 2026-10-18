# Tasks: Align workflow contracts with Diagram handoffs

**Input**: Approved [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md), [contract](contracts/workflow-handoffs.md) and [quickstart.md](quickstart.md).

**Stage**: All27 original tasks performed and checked, actual postcommit result inspected, and real human delivery acceptance recorded. The separate verified transition and scoped acceptance-record commit are explicitly authorized. No unobserved case becomes a pass; see [acceptance evidence](validation/acceptance.md#accepted-delivery-and-postcommit-readback). Earlier planning/implementation descriptions retain their historical context.

## Table of Contents

The work is grouped by the four approved user stories, preserving individually testable increments and final cross-cutting verification.

- [Format and Paths](#format-and-paths)
- [Phase 1: Setup](#phase-1-setup)
- [Phase 2: Foundational Contract](#phase-2-foundational-contract)
- [Phase 3: US1 — Already Selected Entry](#phase-3-us1--already-selected-entry)
- [Phase 4: US2 — Inspectable Outcome](#phase-4-us2--inspectable-outcome)
- [Phase 5: US3 — Ownership and Review](#phase-5-us3--ownership-and-review)
- [Phase 6: US4 — Standalone and Integration Boundary](#phase-6-us4--standalone-and-integration-boundary)
- [Phase 7: Cross-Cutting Verification and Reconciliation](#phase-7-cross-cutting-verification-and-reconciliation)
- [Dependencies and Execution Order](#dependencies-and-execution-order)
- [Implementation Strategy](#implementation-strategy)

## Format and Paths

Use `- [ ] Tnnn [P?] [USn?] Description with exact file path`. [P] means independent files after stated prerequisites, not permission to spawn runtime agents. Runtime changes are limited to the three existing Farmboy skills; docs/fixtures and current004 evidence support them. Historical specs001–003, core tools and constitution are not edit targets. Any future evidence path mentioned below is an intended output, not an already created result.

## Phase 1: Setup

Establish actual source/evidence boundaries before modifying runtime behavior; no new infrastructure is initialized.

- [X] T001 Inspect approved spec/current Git/worktree and record later implementation baseline, actual versions and source identities in specs/004-align-diagram-handoffs/validation/acceptance.md; preserve prior preparation/approval history and unrelated changes (FR-011/016).
- [X] T002 Define external positive/negative, standalone regression, real input/review/resume and independent-observation cases in tests/fixtures/diagram-handoffs/cases.md before runtime edits; preserve current source limitations without inventing a failed experiment (FR-001–016; SC-001–006).

## Phase 2: Foundational Contract

The common human-facing guide establishes meaning; it is not a runtime include, new mandatory request format or dependency.

- [X] T003 Author docs/workflow-handoffs.md from004 contracts/workflow-handoffs.md with ordinary-language examples for all three segments; preserve the constraint “Context references must be accessible under current authority; identify revision or current working state when needed.” Do not impose fixed packets or new provenance/state/transport machinery (FR-002/004/016).
- [X] T004 Document caller-associated workspace/core-helper handling in docs/workflow-handoffs.md, preserving “Identity must identify one contained feature and agree with any existing workspace pointer before effects.” Missing association asks the caller for conventional workspace preparation; no helper patch, hidden retargeting or queue activation (FR-002/003/015).

## Phase 3: US1 — Already Selected Entry

Goal: all three existing skills accept externally selected work while their standalone paths remain intact. Independent test: invoke each externally with associated workspace, required approvals and no local roadmap queue; inspect no reselection or activation. The test cases are prepared by T002 before edits.

- [X] T005 [P] [US1] Add a self-contained external-versus-standalone entry branch to .agents/skills/farmboy-prepare-specification/SKILL.md; use supplied identity/intent/segment/context/artifacts, check actual document fit, avoid roadmap selection/write/brief and create only a missing spec from effective template in the caller-associated directory, never a new feature/number/pointer (FR-001–004).
- [X] T006 [P] [US1] Add usable external entry to .agents/skills/farmboy-prepare-implementation-plan/SKILL.md; preserve ordinary plan/tasks/read-only analyze and separate repair, check current applicable spec approval, replace standalone ledger-eligibility gates with supplied selection and document checks, and preserve local path (FR-001–005/010).
- [X] T007 [P] [US1] Add usable external entry to .agents/skills/farmboy-deliver-approved-plan/SKILL.md; validate identity/context/current applicable spec/full-plan approval without queue eligibility re-adjudication; bypass local-only queue debrief/status writes while preserving implementation/verification/convergence/documentation and scoped candidate commit (FR-001–005/012).
- [X] T008 [US1] Extend all three entry sections in .agents/skills/farmboy-prepare-specification/SKILL.md, .agents/skills/farmboy-prepare-implementation-plan/SKILL.md and .agents/skills/farmboy-deliver-approved-plan/SKILL.md with precise unsupported-segment/identity/association/capability and material stale/conflicting/missing-context stops; no invented answers, silent retargeting, external fetch, fixed packets or second activation (FR-003–005/016).
- [X] T009 [US1] Independently observe positive external entry for each affected installed skill plus targeted guards in real Codex sessions, using tests/fixtures/diagram-handoffs/cases.md and recording actual outcomes/limits in specs/004-align-diagram-handoffs/validation/acceptance.md; executor and evaluator must differ, no per-step runtime agents or real-project fixture approvals (SC-001/006).

## Phase 4: US2 — Inspectable Outcome

Goal: existing artifact notes make actual completion/input/block/failure/interruption and next review inspectable. Independent test: read actual handoffs for the same request and reproduce pending-review/changed-answer resume without repeated effects. Depends on US1 entry routing; its output contract can be assessed independently of ownership implementation, which is out of scope.

- [X] T010 [US2] Reconcile external and standalone result wording in all three .agents/skills/farmboy-prepare-specification/SKILL.md, .agents/skills/farmboy-prepare-implementation-plan/SKILL.md and .agents/skills/farmboy-deliver-approved-plan/SKILL.md: feature/request/segment association, actual outcome, artifacts/evidence, remaining work/input/blockers and next action, using existing notes only (FR-006/010/012).
- [X] T011 [US2] Add checkpoint guidance to those same three .agents/skills/farmboy-prepare-specification/SKILL.md, .agents/skills/farmboy-prepare-implementation-plan/SKILL.md and .agents/skills/farmboy-deliver-approved-plan/SKILL.md files, preserving “A committed checkpoint reference must identify an actual Git revision; uncommitted artifacts must disclose base revision and current working state.” Keep reviewed and latest accepted handoff distinct, with no automatic checkpoint commit (FR-007/011).
- [X] T012 [US2] Preserve missing/affected-only resume, genuine changed answers, task identities, pending review no-op and supported bounded Goal completion/input exclusions across those same three .agents/skills/farmboy-prepare-specification/SKILL.md, .agents/skills/farmboy-prepare-implementation-plan/SKILL.md and .agents/skills/farmboy-deliver-approved-plan/SKILL.md files; do not create/restart Goals, fabricate approval or add counters/state (FR-006/010/015).
- [X] T013 [US2] Extend tests/fixtures/diagram-handoffs/cases.md for draft clarification/settled review, complete-plan review, actual committed-candidate result review, blocked/input/interrupted/technical-failure outcomes and resume, including dirty versus committed evidence; use existing native controls only (SC-002/006).
- [X] T014 [US2] Observe affected handoffs/resume/real input waits with a separate executing session/evaluator, using actual TEST ONLY answers after genuine stops, and record actual observations and any unavailable case in specs/004-align-diagram-handoffs/validation/acceptance.md; refresh affected earlier evidence after source edits (FR-006/007/015/016; SC-002/006).

## Phase 5: US3 — Ownership and Review

Goal: Farmboy consumes authority and returns evidence without owning coordination decisions. Independent test: sequential-owner and historical-approval scenarios preserve coordinator authority and require affected review only for materially changed meaning.

- [X] T015 [US3] Clarify Diagram-owned selection/eligibility/dependencies/ownership/approvals/handoff acceptance in all three .agents/skills/farmboy-prepare-specification/SKILL.md, .agents/skills/farmboy-prepare-implementation-plan/SKILL.md and .agents/skills/farmboy-deliver-approved-plan/SKILL.md files; no acquire/release/transfer API or local one-owner service, durable draft return enables coordinator release and separately authorized clarification retains authority while active (FR-008/009).
- [X] T016 [US3] Reconcile current-meaning approval checks in those same three .agents/skills/farmboy-prepare-specification/SKILL.md, .agents/skills/farmboy-prepare-implementation-plan/SKILL.md and .agents/skills/farmboy-deliver-approved-plan/SKILL.md files, preserving “Material changes require the affected review; unchanged applicable work is not reapproved.” Keep routine flow-back and reviewed/latest accepted handoff distinct (FR-005/010/011).
- [X] T017 [US3] Extend docs/workflow-handoffs.md with sequential-owner, one-active-owner, separately authorized ordinary clarification and isolated independent-feature examples; show missing authority stops without coordinator writes and historical approval remains evidence rather than approval of changed meaning (FR-008/009/011).
- [X] T018 [US3] Add targeted authority/approval cases in tests/fixtures/diagram-handoffs/cases.md and independently observe representative affected stops using a separate real executing session/evaluator; record actual results/limits in specs/004-align-diagram-handoffs/validation/acceptance.md without calling Diagram (SC-004/006).

## Phase 6: US4 — Standalone and Integration Boundary

Goal: preserve all three standalone workflows and describe separate integration honestly. Independent test: actual three local regressions plus candidate-to-integration contract review and unsupported-segment guard; no integration execution.

- [X] T019 [US4] Reconcile standalone branches in all three .agents/skills/farmboy-prepare-specification/SKILL.md, .agents/skills/farmboy-prepare-implementation-plan/SKILL.md and .agents/skills/farmboy-deliver-approved-plan/SKILL.md files: retain existing local roadmap/wiki/context/approval/hooks, delivery scoped commit and review stops; remove obsolete004-external-is-future-only wording in current runtime source without rewriting historical feature directories (FR-001/010/012).
- [X] T020 [US4] Add integration boundary examples to docs/workflow-handoffs.md: explicit UAT/final-result authorization, project branch/target/check policy and missing/conflicting-policy stop, Diagram serialization and database-only receipts, no implicit push/receipt commit, executor placement/implementation deferred, merge freezes history and later changes use new linked feature (FR-013/014).
- [X] T021 [US4] Update docs/prepare-specification.md, docs/prepare-implementation-plan.md and docs/deliver-approved-plan.md with both entry modes, examples, standalone-compatible prerequisites, current handoff boundaries and links to docs/workflow-handoffs.md; do not present planned behavior as accepted before evidence exists (FR-001/016).
- [X] T022 [US4] Update README.md to expose external entry on all three skills and retained standalone use, authority/integration exclusions, and current004 evidence links without rewriting001–003 history (FR-001/008/013/016).
- [X] T023 [US4] Run independent real-session standalone regression of each installed skill using tests/fixtures/diagram-handoffs/cases.md, including named/eligible local selection, plan approval gate and actual local delivery closeout; record actual results in specs/004-align-diagram-handoffs/validation/acceptance.md (SC-003/006).
- [X] T024 [US4] Review candidate-to-integration examples and observe unsupported-integration/scope stop from affected installed entry using tests/fixtures/diagram-handoffs/cases.md; record actual contract review and guard evidence, explicitly no executor/integration/service test, in specs/004-align-diagram-handoffs/validation/acceptance.md (SC-005/006).

## Phase 7: Cross-Cutting Verification and Reconciliation

Finish evidence on final affected source; pending implementation tasks are not proof of already performed work. Later delivery composition owns its prescribed converge/debrief/wiki/local commit, not this planning invocation.

- [X] T025 Reconcile actual final-source observation coverage against all16FR, sixSC and20 acceptance scenarios in specs/004-align-diagram-handoffs/validation/acceptance.md; rerun only affected cases after edits, distinguish unobserved cases/limits from passes and preserve historical evidence (FR-016; SC-001–006).
- [X] T026 Run focused skill frontmatter/links/privacy, unchanged historical001–003, no core-tool/constitution modifications and git diff --check validation; record actual outputs/limitations in specs/004-align-diagram-handoffs/validation/acceptance.md using existing skill-tools Python without adding dependencies (FR-011/016).
- [X] T027 Reconcile only current004 spec.md, plan.md, tasks.md and supporting contracts/quickstart with implemented meaning and actual status in specs/004-align-diagram-handoffs/; preserve approval applicability or stop for affected review on material change, preserve task IDs and no invented answers/status/acceptance (FR-005/011/015).

## Dependencies and Execution Order

Setup T001→T002, then foundation T003→T004, then US1 T005–T009, US2 T010–T014, US3 T015–T018, US4 T019–T024, then T025–T027. Cross-story runtime files overlap, so execute story phases sequentially. US1 remains the independently useful MVP; later stories add inspectable handoffs, authority precision and comprehensive local/integration-boundary regression. Each story has the independent test stated above; no final release can omit approved obligations.

### Within-story ordering

Prepare fixture expectations before behavior changes. T005/T006/T007 use different files and can be edited independently after T004; T008 waits for all three. T009 observes current source. Later story edits invalidate affected earlier observations; T025 requires final-source reconciliation and affected reruns, not blind repetition. T013 extends the already prepared expectations rather than requiring a preimplementation run to fail. No future final004 commit is a precondition of its own commit; postcommit readback belongs after later authorized delivery success, before result review, without receipt-only commits.

### Parallel examples

US1 has the only file-independent [P] group: T005/T006/T007 after T004. For US2 (T010–T014), US3 (T015–T018) and US4 (T019–T024), no safe parallel runtime-edit group is proposed because files/evidence overlap. This explicitly records the absence of a parallel opportunity for each story. No [P] label authorizes runtime delegation; use the existing session sequentially as instructed.

## Implementation Strategy

Deliver the smallest usable external entry across all three skills first (US1), validate that slice independently, then reconcile outcomes (US2), coordinator/approval semantics (US3) and standalone/integration boundaries (US4), refreshing affected evidence at the final checkpoint. Use existing artifacts and current findings for useful repairs without numeric limits/counters/reset/score/persistence/accounting machinery. A genuinely optional suggestion is separate; a defect or unmet requirement blocks. Explicit human full-plan review remains required before any task executes, followed by separately selected implementation. No task authorizes bridge/transport/scheduler/ownership service/integration executor/autonomous work or changes to core tools/constitution.

**Execution sequencing note**: Related entry/result/authority text edits were grouped before final-source runtime observation so later story text would not invalidate already costly subject runs. Task identities, story outcomes and independent verification obligations are unchanged; unchecked observation tasks remain pending until actual evidence. No scope or approved meaning changes.

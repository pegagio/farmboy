# Tasks: Concise delivery evidence

**Input**: Approved spec plus `plan.md`, `research.md`, `data-model.md`, `contracts/delivery-evidence.md`, `quickstart.md` in this directory.
**Status**: Full plan explicitly approved on 2026-10-19; all 14 tasks are accounted for in the scoped local delivery candidate. The closing task is confirmed by actual commit/readback in the ordinary handoff; real result acceptance remains pending.
**Tests**: Explicitly required by FR-011 and SC-001–005. Write focused fixture expectations first; observe actual revised skill separately from its evaluator.

## Phase 1: Setup

- [X] T001 Revalidate selected specification approval/content and feature/pointer, verified 003 dependency, current Git/index and unrelated changes; record applicable source/working-state boundaries in `specs/006-concise-delivery-evidence/delivery.md` without inferring plan/result approval.

## Phase 2: Foundational

- [X] T002 Define the focused case's concrete disposable-project setup, supported core capabilities, TEST ONLY approvals, executor/evaluator roles, deterministic seeds explicitly labeled SYNTHETIC FIXTURE SEED (not observed results), and expected observations in `tests/fixtures/deliver-approved-plan/cases.md`, following `specs/006-concise-delivery-evidence/quickstart.md`; keep raw driving/session output temporary and actual identities absent.

## Phase 3: US1 — Review verification without raw output (P1; MVP)

**Independent test:** Review retained fixture artifacts after raw output removal and establish source, checks/results, repairs/rechecks, limits and actual decision status. No reusable-test or consolidation policy is needed to assess the summary independently; final actual delivery observation is shared in T012.

- [X] T003 [US1] Add expected six-essential summary and required-reference checks to `tests/fixtures/deliver-approved-plan/cases.md` before skill edits; include dirty-source attribution, changed-source stale evidence, missing-proof stop and pending versus TEST ONLY decision cases (FR-002/003/006; SC-001/002/004).
- [X] T004 [US1] Update `.agents/skills/farmboy-deliver-approved-plan/SKILL.md` to require the concise source/check/result/repair/limit/decision account in existing notes, preserved actual-versus-expected attribution and durable required links; retain actual final-commit readback without recursive receipt commits or claimed future verification (FR-002/003/006/010).
- [X] T005 [US1] Align `docs/deliver-approved-plan.md` with the concise summary, stale-check/review applicability and required-reference behavior; explain that “No claim exceeds observed source/execution” and fixture decisions remain TEST ONLY, while real decisions retain role/content/conditions without private identity (FR-002/003/006/008/010).

## Phase 4: US2 — Keep repeat assets, exclude run debris (P1)

**Independent test:** Inspect a fixture commit and rerun retained tests without old logs; raw output is absent while reproducible test assets remain.

- [X] T006 [US2] Add `tests/fixtures/deliver-approved-plan/evidence-retention/test_count_lines.py`, `input.txt` and `expected.txt`: stdlib tests import disposable `count_lines.py:count_lines(text)`, compare controlled three-line input with expected `3`, and cover empty input plus a last line without newline; no third-party runner or copied raw transcript (FR-004/011; SC-003).
- [X] T007 [US2] Refine `.agents/skills/farmboy-deliver-approved-plan/SKILL.md` precommit ALL-scoped-artifacts language to include authorized durable deliverables/reusable assets and exclude temporary raw logs, transcripts/state and superseded intermediates; inspect actual index including already tracked raw material, preserve unrelated work, and require minimal justified privacy-safe exceptions (FR-001/004/005/008).
- [X] T008 [US2] Update `docs/deliver-approved-plan.md` with portable path/identity rules, raw versus expected-output examples, repeatable assets, minimal durable exceptions and actual staging inspection; retain “deletion cannot remove sole support for required claims” rather than prescribing a retention timer/service (FR-001/004/005/008; SC-003/005).

## Phase 5: US3 — Consolidate safely (P2)

**Independent test:** Consolidate authorized redundant toy-feature reports and confirm distinct findings/decisions and every affected required link survive, without touching historical Farmboy features.

- [X] T009 [US3] Add consolidation, tracked-file scope, minimal exception/project-rule conflict, privacy and unchanged external-boundary cases to `tests/fixtures/deliver-approved-plan/cases.md`; specify required retained meanings and exact expected stops, distinguishing static-only assertions from runtime observations (FR-007/009/010/012).
- [X] T010 [US3] Add bounded consolidation and project-evidence-rule handling to `.agents/skills/farmboy-deliver-approved-plan/SKILL.md`: preserve distinct findings/limits/actual decisions, repair affected links, retain mandatory source-preserving helper artifacts, and stop dependent closeout for missing proof or unresolved conflicts; preserve routing/authority and merged history (FR-007/009/010/012).
- [X] T011 [US3] Align `docs/deliver-approved-plan.md` with fixture-only initial consolidation targets, rule-conflict stops and preserved standalone/external handoffs; state “No new command, parameter packet, API or store is added” and exclude historic/cross-project cleanup (FR-007/009/010/012).

## Phase 6: Final verification and prescribed closeout

- [X] T012 Observe the actual final revised skill in one disposable delivery fixture under a separate evaluator using `specs/006-concise-delivery-evidence/quickstart.md`; populate fixture reports from actual observed results before consolidation and verify real failing check→repair→recheck, closeout/actual commit, unrelated work, retained six-essential summary/assets, consolidated links, raw-output removal/rerun and Awaiting result review. Record source content hashes/base plus relevant delta, observed decisions and material limits concisely in `specs/006-concise-delivery-evidence/delivery.md`; no simulation-only acceptance or native completion claim without controls/readback (FR-003/004/006/007/008/010/011; SC-001–005).
- [X] T013 Review final `.agents/skills/farmboy-deliver-approved-plan/SKILL.md`, `docs/deliver-approved-plan.md`, `tests/fixtures/deliver-approved-plan/cases.md` and fixture assets against every FR/SC; check links, privacy, actual candidate scope and unchanged routing/approval/core-report contracts; rerun affected verification after material edits and record remaining gaps honestly in `specs/006-concise-delivery-evidence/delivery.md` (FR-001–012).
- [X] T014 Under separately selected delivery authority, reconcile current `specs/006-concise-delivery-evidence/` artifacts with actual work, run installed convergence and useful repair/reassessment to zero actionable gaps, perform prescribed attributable roadmap-debrief, wiki ingestion/lint and narrow implemented update in `.specify/memory/roadmap.md`, then inspect/stage durable scoped artifacts and make the ordinary local delivery commit; report actual result/limits and stop Awaiting result review, without verified/acceptance/integration/push or receipt-only commits. Required core-generated reports remain governed by their contracts (FR-009/010/012).

## Dependencies and execution order

T001 → T002 → US1 (T003–T005) → US2 (T006–T008) → US3 (T009–T011) → T012 → T013 → T014. Within each story, tests/expectations precede affected behavior edits. T012 waits for all final source edits; source changes after observation invalidate affected evidence. T014's candidate commit is later than precommit observation; report its actual hash normally, never in a recursive receipt commit. If a core command adds required follow-up work, preserve task IDs and follow the selected delivery composition's repair rules.

## Parallel opportunities and examples

No [P] markers are proposed: the skill/guide/cases files recur across stories and this small workflow is simpler sequentially. US1 example: T004 skill wording then T005 matching guide; US2 example: T006 reusable assets then T007/T008 policy; US3 example: T009 case expectations then T010/T011 behavior. These are explicit serial examples, not agent dispatch instructions. Independent actual-skill evaluation in T012 is a verification boundary, not runtime delegation inside the skill.

## Implementation strategy

US1 is the smallest useful review-summary improvement. Deliver the full approved feature incrementally through US2 and US3 before final acceptance; no standalone partial delivery can claim all 006 requirements. Use existing commands/artifacts only. No counters, reset rules, scores, new persistence, accounting, generic harness or cleanup service. Missing essential capability/evidence or a material human decision stops dependent work. Passing analysis does not approve this proposal.

# Tasks: Coordinate independent plan-review handoff from user intent

**Input**: [Approved spec](spec.md), [plan](plan.md), [research](research.md), [existing data model](data-model.md), [caller contract](contracts/caller-handoff.md), [validation guide](quickstart.md).

**Tests**: Explicitly required by FR-014 and Constitution III. Focused source/transport checks and independently evaluated actual-session proof are separate obligations. These five coherent packages include their own setup, tests and evidence; none is implemented or checked off during planning.

## Phase 1: Setup (folded into T001)

No new project, package manager or infrastructure initialization. Before editing, verify approved spec and plan, current native delivery authority, clean isolated branch and actual core/consumer byte baseline. Preserve the source-only versus later consumer-installation boundary. Record real source/candidate hashes in existing feature validation notes.

## Phase 2: Foundational prerequisites (folded into T001/T002)

Read current native ReviewGrant and reviewer/adapter contracts at pinned private acceptance source; verify available exact-target independent-session/result tools. No new production helper/service/API is needed. Unknown or unavailable tools are a precise delivery blocker, not permission to install or alter controls. Author handoff/release precedes real reviewer writes.

## Phase 3: User Story 1 — Request review without manual dispatch (P1)

**Goal**: A selecting caller owns the user's one review request without becoming the semantic reviewer.

**Independent test**: Source assertions and a disposable caller input show correct entry selection, missing-scope question and complete handoff preparation without operator prompt/grant editing. Complete runtime journey is additionally required in T004.

- [x] T001 [US1] Add focused routing/selection/mandate tests first in `tests/fixtures/review-implementation-plan/test_caller_contract.py`, then implement the thin caller in `.agents/skills/farmboy-request-plan-review/SKILL.md` and the minimal direct-request versus dispatched-reviewer routing seam in `.agents/skills/farmboy-review-implementation-plan/SKILL.md`; keep caller-as-author separate from independent semantic decision, at most one reviewer, one-question missing substantive authority, no recursive caller/body routing and standalone usability; fold setup/source baselines into `specs/029-review-request-handoff/validation/verification.md`. Covers FR-001/002/004/005/006/013 and SC-001/002.

## Phase 4: User Story 2 — Preserve authority through handoff (P1)

**Goal**: Existing bounded grant and exact candidate reach an independent reviewer unchanged; missing/stale authority stops.

**Independent test**: Source plus private native transport fixtures reject omitted grant, incomplete/advice-only mandate, stale/wrong/revoked pins, changed proposal, busy author and author-as-reviewer. Verify preflight exact targeting before any dispatch.

- [x] T002 [US2] Extend `tests/fixtures/review-implementation-plan/test_caller_contract.py` and prepare shared disposable cases in `tests/fixtures/review-implementation-plan/prepare_caller_fixtures.py`/`cases.md`; implement caller grant preparation/transport and capability checks in `.agents/skills/farmboy-request-plan-review/SKILL.md` with a bounded reference in `.agents/skills/farmboy-diagram-work/references/native-protocol.md`, reusing existing `feature`, `pinned_handoff`, `expected_revision`, `reviewer_owner`, `reviewer_session`, `authorization` fields and actual human evidence, preserving adapter-only native acquire/record/release and reviewer identities without self-grant, silent repin, discovery/controls override, new schema or production transport service; use only a private Diagram `f6494a1e390d29e6657e95a6b6f6c28bebe09ac0` schema23/Feature9 source snapshot for current native proof and label controlled fixtures. Covers FR-003/004/005/006/007/011/012 and SC-002/003/005.

## Phase 5: User Story 3 — Collect outcome and stop (P2)

**Goal**: Bring the real result back with exact evidence and next decision; uncertainty never creates a second review or fictional completion.

**Independent test**: Each substantive disposition and incomplete/uncertain return correlates candidate/report/native terminal and ownership. A valid saved or live matching review is inspected/collected, not redispatched.

- [x] T003 [US3] Add outcome/resume/permission-refusal assertions and controlled collection fixtures in `tests/fixtures/review-implementation-plan/test_caller_contract.py`, `prepare_caller_fixtures.py` and `cases.md`, then complete `.agents/skills/farmboy-request-plan-review/SKILL.md` collection using existing child start/read/wait observations and native operation/current-state inspection; verify report path/digest, exact candidate/mandate, six conclusions, required/optional findings, native accepted disposition and absent ownership, preserving historical proposal versus report checkpoints and FARM-27/28 meanings; unknown dispatch/invalid report/failed checkpoint/disconnect stays incomplete with action/target/effects/denied-pending-uncertain outcome, no duplicate native finalize/retry, automatic repair/re-review/implementation, takeover or alternate-executor bypass. Covers FR-007/008/009/010/011/012 and SC-002/004/005.

- [x] T004 [US3] Execute and independently evaluate the actual candidate caller → separate actual reviewer → caller-return journeys from `specs/029-review-request-handoff/quickstart.md`, using prepared disposable real Git/native consumers and explicit TEST ONLY bounded mandates; observe complete no-copy request and all three substantive dispositions, missing-mandate/independence/refusal/uncertainty stop boundaries, no extra dispatch or later workflow, and standalone regression; retain actual source/fixture hashes, evaluator/caller/reviewer identities, prompt/grant evidence, commands, report/native terminal/release and preserved bytes in `specs/029-review-request-handoff/validation/verification.md`, clearly distinguishing actual model behavior, controlled negatives and unobserved host limits. Required unavailable observations remain unpassed blockers; no live Fusion/BGG, production-store fixture, control/tool installation change or Diagram-source mutation. Covers FR-014 and SC-001 through SC-006.

## Final Phase: Cross-cutting documentation, regression and handoff

- [x] T005 Update `README.md`, `docs/review-implementation-plan.md` and `docs/diagram-adapter.md` with the operator-facing caller, exact authority/standalone/dispatch limits and separate consumer-refresh boundary; perform applicable source-backed upkeep of `wiki/pages/independent-plan-review.md`, `wiki/pages/optional-diagram-adapter.md` and `wiki/sources.md` through existing ingestion/lint, run both maintained contract suites plus Python syntax and scoped diff checks from `specs/029-review-request-handoff/quickstart.md`, preserve generic/core/unrelated consumer bytes, reconcile actual outcomes through convergence and fresh read-only consistency analysis, checkpoint only authorized source/evidence with normal hooks and complete native result-review handoff/release. Record real checks and unresolved limits in `specs/029-review-request-handoff/validation/verification.md`; do not mark this task complete or imply acceptance/integration/deployment until required checks and human gates are actually met. Covers FR-009/010/011/012/013/014 and SC-004/005/006.

## Dependencies and execution order

T001 → T002 → T003 → T004 → T005. T004 evaluates the complete candidate, not a stale intermediate instruction set. All packages share caller/reference/fixture files, so no blanket [P] marker is appropriate. Documentation draft work may overlap observation preparation once contracts stabilize, but does not authorize another executing agent or concurrent writes. No per-story parallel example is safe for the shared-file packages; independent fixture cases may later run sequentially or through already authorized isolated evaluation mechanisms without modifying production coordination.

## Implementation strategy

The MVP is US1's complete selected-request handoff with actual applicable mandate; US2 enforces its authority constraints and US3 completes collection/stop. Delivery acceptance requires the complete five-package increment and actual-session evidence, not US1 prose alone. Setup and test bookkeeping stay inside their package; no fragmented infrastructure tasks or new tracking subsystem.

**Planning history**: At the original planning handoff all five tasks were unstarted. The exact plan was subsequently independently approved and delivery separately selected. Current checkboxes track local implementation/validation packages; final adapter commit → native handoff/release is recorded in the database after the candidate commit, without a receipt-only Git tail. No checkbox creates acceptance or transport facts. See delivery.md and validation/verification.md for actual work; final native readback remains authoritative.

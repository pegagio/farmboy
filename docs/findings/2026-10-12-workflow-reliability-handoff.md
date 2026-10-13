# FarmBoy Workflow Reliability Findings Handoff

This document preserves findings from the Feature 022 development session for three separately planned FarmBoy features: 023 — Workflow Branch Validation and Controller Integration Coverage; 024 — Implement Continuation and Correction Accounting; and 025 — Reusable Disposable Consumer Validation Fixture. The operator requested these roadmap additions on 2026-10-12, America/Los_Angeles. This is specification input, not an approved specification, implementation plan, or authorization to start another workflow.

## Table of Contents

The sections separate observed failures from desired outcomes and decisions that future feature sessions must resolve.

- [Authority and Scope](#authority-and-scope)
- [Session Findings and Evidence](#session-findings-and-evidence)
- [Feature 023: Branch and Integration Validation](#feature-023-branch-and-integration-validation)
- [Feature 024: Continuation and Correction Accounting](#feature-024-continuation-and-correction-accounting)
- [Feature 025: Disposable Consumer Fixture](#feature-025-disposable-consumer-fixture)
- [Sequencing and Session Handoff](#sequencing-and-session-handoff)

## Authority and Scope

The direct operator decision is to record the three prioritized improvements from the session audit as roadmap features and preserve enough context for future specification and planning. All changes must be owned within FarmBoy. Changes to Spec Kit, Codex, Excel, independently owned extensions, other consuming projects, and spreadsheet dependencies are excluded. Use the existing supported tooling and runtime pins; any later proposal for a new dependency still requires its own approval.

The [constitution](../../.specify/memory/constitution.md) remains governing authority. Preserve explicit workflow and scope selection, exact native-agent assignments, same-child question relay, consequential human gates, bounded correction, source ownership, evidence integrity, and separate Git/verification/acceptance decisions. None of these features authorizes skipping a gate, reconstructing historic evidence, resetting a consumed budget, or changing Feature 022 retrospectively. Fixed defects below are regression cases, not claims that the current source still has those defects.

## Session Findings and Evidence

The following observations explain why the operator prioritized these features. Reports are historical evidence; their hashes and claims describe their original observation time.

| Finding | Observation | Repository evidence | Relevant feature |
|---|---|---|---|
| WR-01 | Implement stopped before coding because switches put `default: []` under `cases`, while the branch helper required a top-level default. Both preparation/source skip routes needed correction. | [Blocked routing](../../specs/022-local-workflow-agent-timing-metrics/validation/implementation/blocked-routing.json) | 023 |
| WR-02 | After valid independent completion review and marker-only task tracking, re-entry rejected a historical assessment hash against current task bytes. The controller fix separated retained historical evidence from current-evidence validation. | [Blocked re-entry](../../specs/022-local-workflow-agent-timing-metrics/validation/implementation/blocked-reentry-after-tracking.json) | 023, 024 |
| WR-03 | After the controller upgrade, an older invocation lacked the newly required pre-effect assessment binding. A fresh invocation needed an explicit recovery decision; reconstructing the missing historic binding was prohibited. | [Fresh implementation outcome](../../specs/022-local-workflow-agent-timing-metrics/validation/implementation/fresh-outcome.json) and retained checkpoints | 024 |
| WR-04 | A first source attempt produced an incomplete helper and new review findings, but no whole task completion. The no-progress rule stopped before an ordinary corrective pass. | [Fresh implementation outcome](../../specs/022-local-workflow-agent-timing-metrics/validation/implementation/fresh-outcome.json) | 024 |
| WR-05 | Correction of T002/T009 succeeded, but the next pass left the T018 category-count assertion unresolved and stopped for no measurable progress. A separately authorized focused correction resolved it. | [Correction checkpoint](../../specs/022-local-workflow-agent-timing-metrics/validation/implementation/correction-checkpoint/outcome.json), [focused T018 checkpoint](../../specs/022-local-workflow-agent-timing-metrics/validation/implementation/focused-t018-checkpoint/outcome.json) | 024 |
| WR-06 | Five source sessions completed ten tasks but ended with the T015 carriage-return finding. Another five-session invocation completed five more tasks but stopped before live/Excel acceptance. The same overall limit covered normal dependency batches, corrections, and acceptance work. | [Next checkpoint](../../specs/022-local-workflow-agent-timing-metrics/validation/implementation/next-checkpoint/outcome.json), [remaining acceptance checkpoint](../../specs/022-local-workflow-agent-timing-metrics/validation/implementation/remaining-acceptance-checkpoint/outcome.json) | 024 |
| WR-07 | The disposable consumer initially could not locate the already-installed pinned Specify CLI. Adding a minimal consumer runtime declaration resolved bootstrap without installing another package. Codex project registration required a human step. | [Live round-trip evidence](../../specs/022-local-workflow-agent-timing-metrics/validation/implementation/live-roundtrip-a9b8e3b0.json), session observation recorded here | 025 |
| WR-08 | Copying the full Feature 022 artifact set into a minimal consumer allowed a real Reviewer turn, but its assessment correctly blocked on missing owning governance and validation prerequisites. Seven actual timing records were emitted; consumer implementation completion was never claimed. | [Live round-trip evidence](../../specs/022-local-workflow-agent-timing-metrics/validation/implementation/live-roundtrip-a9b8e3b0.json), [independent judgment](../../specs/022-local-workflow-agent-timing-metrics/validation/implementation/live-independent-judgement-a9b8e3b0.json) | 025 |

The final [implementation outcome](../../specs/022-local-workflow-agent-timing-metrics/validation/implementation/live-acceptance-checkpoint/outcome.json) substantiates all 23 tasks. The [convergence outcome](../../specs/022-local-workflow-agent-timing-metrics/validation/convergence/outcome.json) records clean convergence. These results show that recovery preserved the work, while the repeated starts and manual consumer setup exposed process friction. Independent review also caught genuine implementation defects; the goal is to improve continuation without weakening that review.

## Feature 023: Branch and Integration Validation

The desired outcome is early, actionable detection of invalid workflow routes and reliable regression coverage of the full controller sequence that previously failed during dogfooding.

**Scope**: Validate FarmBoy-owned workflow definitions against the actual installed controller semantics. Cover supported switch cases/defaults, empty skip branches, selected-branch isolation, template references that become available only after their producers run, and malformed or unsupported structures. Add executable integration cases for assessment → eligible source dispatch → independent review → marker tracking → post-pass capture → re-entry. Include legitimate historic preimage differences and invalid current evidence. Source and installed disposable-consumer behavior must agree.

**Candidate acceptance scenarios**:

- A misplaced `cases.default` is rejected before installation or workflow effects, with the exact workflow, step, and correction identified.
- A source route skips preparation and a preparation route skips source execution; untaken branches never run.
- Reviewed marker-only changes and legitimate source corrections permit re-entry against a trusted retained historical baseline.
- Forged/unbound history, stale current evidence, unauthorized task changes, missing outputs, no progress, and exhausted declared limits still block.
- A deterministic harness describes simulated dispatch accurately; it does not claim live named-agent behavior.

**Likely source touchpoints (planning leads)**: `controllers/farmboy/scripts/python/controller.py`, controller/package validation, `workflows/farmboy-*/workflow.yml`, `tests/test_workflow_graph.py`, `tests/test_workflow_paths.py`, `tests/test_controller.py`, `tests/test_readiness_workflow_routes.py`, and existing `tests/consumer-fixtures/`. Inspect existing coverage before adding a second validator or harness. Keep the tests sensitive to the real production branch/routing APIs rather than reproducing their logic in test-only code.

**Questions for specification/planning**: Which checks belong at source/catalog validation versus runtime preflight? Which scenarios require installed-consumer integration rather than graph inspection? What is the smallest reusable harness extension that exercises the actual APIs without invoking a native workflow runner or adding a framework?

## Feature 024: Continuation and Correction Accounting

The desired outcome is fewer unnecessary operator restarts while authorized, demonstrably progressing work continues within an inspectable, explicitly bounded invocation.

**Scope**: Clarify and implement accounting for normal dependency-ordered task batches, defect corrections, and acceptance observations. Address the first-attempt discovery case, fresh independent review, stable finding identities, actual source/session events, safe same-child continuation, and controller-upgrade recovery classification. Explain the next safe action, consumed limits, and whether the existing invocation can resume. Preserve settled same-target intent where current authority and evidence permit it; ambiguous recovery and consequential changes still need a human decision.

**Candidate acceptance scenarios**:

- An authorized feature with more than five healthy dependency batches can progress under a reviewed finite policy without treating each normal batch as a failed correction.
- Newly discovered in-scope defects have a defined baseline/first-correction path; discovery and administrative updates themselves earn no substantive resolution credit.
- A genuinely unresolved repeated defect stops at its declared limit. Renaming findings, refreshing eligibility, updating markers, receiving an answer, or restarting a child cannot manufacture progress or reset counters.
- Source attempts and failed dispatches remain accurately recorded. Same-child answers exclude human waiting from metrics and do not create another source session merely for the answer.
- Pending manual/live acceptance is reported separately from an implementation defect; resumption preserves the completed work and original observations.
- A changed controller contract produces a precise resume-compatible, fresh-assessment-required, or fresh-invocation-required outcome. Missing pre-effect proof is never recreated from current files.

**Likely source touchpoints (planning leads)**: Implement workflow, shared controller protocol, `implementation_scope.py`, progress/history/retention helpers, readiness re-entry checks, recovery summaries, and their regression/integration tests. Preserve metrics correlation and actual turn boundaries. Feature 023's coverage can be reused if available, but this feature is not blocked on its delivery.

**Questions for specification/planning**: What finite limits apply to normal batches, corrective work, and observations? Is corrective accounting per invocation, task, finding, or another stable unit, and how does it resist counter resets? What evidence permits the first correction after discovery? Which controller upgrades are safely resumable, and which require an explicit fresh invocation? These are future design decisions; this handoff does not prescribe an unlimited loop, a particular replacement cap, or a protocol migration implementation.

## Feature 025: Disposable Consumer Fixture

The desired outcome is a reproducible, maintainer-owned way to prepare a minimal valid FarmBoy consumer and execute a clearly bounded validation scenario with honest provenance and minimal manual setup.

**Scope**: Reuse the existing catalog development-snapshot installation route and approved runtime pins. Prepare an isolated initialized consumer with a small purpose-built feature, valid minimal owning governance, necessary checklist/plan/task evidence, and supported native-agent configuration. Check runtime discovery and component compatibility before presenting the fixture as ready. Provide a concise launch/registration handoff for Codex and explicit stop boundaries for a read-only observation or selected small implementation scenario. Preserve consumer-owned and machine-local data; distinguish deterministic package/dispatch fixtures from real agent observations.

**Candidate acceptance scenarios**:

- A prepared consumer resolves the already-installed pinned CLI and passes FarmBoy bootstrap; a missing/incompatible runtime is reported before agent dispatch, without ad hoc installation.
- The minimal fixture supports its intended assessment without missing governance or copied prerequisites from another feature.
- Preparation preserves source checkout bytes and unrelated consumer content. Repeated preparation has a documented safe behavior and never silently replaces an existing consumer or deletes data.
- Native validation uses the exact configured agent names and records actual observed results, component versions, source digests, and tested CLI version. No-op dispatch and copied TOML values are not reported as live behavior or verified effective settings.
- The report skill and spreadsheet dependencies remain excluded from consumers. A metrics scenario, when selected, preserves existing machine-local records and does not override `HOME` or fabricate observations.
- Where Codex registration/task launch requires a manual step, one concise handoff explains it. The fixture does not require a new Codex API, control the Codex app through a prohibited route, or claim automated registration.

**Likely source touchpoints (planning leads)**: Existing catalog preparation/install utilities, `tests/consumer-fixtures/`, packaging/install lifecycle tests, and maintainer documentation. Decide whether the public entry point should be an existing task-runner command, small script, or maintainer skill after inspecting existing utilities. Prefer reuse and no new dependency.

**Questions for specification/planning**: Where should fixtures live and what is their safe reuse/cleanup policy? Which scenarios are deterministic versus explicitly operator-selected live runs? What minimum artifact set establishes a valid assessment? How should launch instructions convey exact scope, stop boundaries, and continued-task authorization without relying on a changed Codex tool contract?

## Sequencing and Session Handoff

The recommended work order is 023, then 024, then 025; it is a priority recommendation, not a hard dependency chain. These features may reuse one another's delivered utilities when available, but they must remain independently scoped and avoid a harness/fixture dependency cycle. Feature 022 is evidence and metrics context, not a prerequisite for every scenario.

For a future feature session, select exactly the relevant roadmap entry, read this document and its cited evidence, inspect current source/tests, and use the separately invoked Specify/Clarify/Plan/Tasks workflows. Translate the candidate scenarios into reviewed requirements and measurable checks; resolve the listed design questions rather than treating implementation leads as settled architecture. No feature is activated and no specification directory is created by this roadmap amendment.

At this handoff, Feature 022 Close Out is waiting on its implemented → verified approval. Adding roadmap entries changes the ledger digest, so its previously prepared verification proposal becomes stale. Preserve that proposal and implemented receipt as history; obtain a fresh trusted debrief/proposal through the operator-selected workflow before any verification write. This document does not approve that transition, start wiki maintenance, or grant a commit/merge/push.

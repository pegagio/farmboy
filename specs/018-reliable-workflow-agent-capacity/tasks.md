# Tasks: Reliable Workflow Agent Capacity

**Input**: Design artifacts in `specs/018-reliable-workflow-agent-capacity/`.

**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, both files in `contracts/`, `quickstart.md`, and Constitution 6.0.0.

**Tests**: Required by FR-013/017 and SC-001–007. Write the story tests before their implementation and verify the relevant behavioral assertions fail for the missing behavior. Deterministic tests, no-op dispatch, and historical evidence do not replace native acceptance.

**Organization**: All three stories are P1. Deliver sequential lifecycle handling first, bounded exhaustion recovery second, and consumer setup guidance third. All tasks start unchecked. The implementation agent owns preparation, disposable test-only configuration, separately dispatched test workflow invocations, predetermined synthetic inputs, assertions, and evidence within the authorized validation scope; the operator performs no manual test cases or repeated commands. At most one initial Codex project setup may require the operator. Genuine consequential decisions remain gated. This file authorizes no Git integration, publication, real-consumer configuration changes, feature acceptance, or automatic product-workflow chaining.

## Contents

Follow the implementation phases, then verify dependencies and requirement coverage.

- [Format and Paths](#format-and-paths)
- [Phase 1: Setup](#phase-1-setup)
- [Phase 2: Foundational](#phase-2-foundational)
- [Phase 3: US1 — Continue Sequential Workflow Use](#phase-3-us1--continue-sequential-workflow-use)
- [Phase 4: US2 — Recover Safely from Exhaustion](#phase-4-us2--recover-safely-from-exhaustion)
- [Phase 5: US3 — Configure a Consumer at Install or Upgrade](#phase-5-us3--configure-a-consumer-at-install-or-upgrade)
- [Phase 6: Polish and Cross-Cutting Validation](#phase-6-polish-and-cross-cutting-validation)
- [Dependencies and Execution Order](#dependencies-and-execution-order)
- [Parallel Examples](#parallel-examples)
- [Implementation Strategy](#implementation-strategy)
- [Requirement Coverage](#requirement-coverage)

## Format and Paths

Each task uses `- [ ] TNNN [P]? [USn]? Description with paths`. `[P]` identifies only the explicitly paired tasks described below, after their prerequisites are complete; it does not authorize spawning agents. Story labels appear only in story phases. All paths are relative to the repository root.

Source belongs in `controllers/flow-kit/` and `tools/catalog.py`; installed copies are test outputs in disposable consumers. Portable validation belongs in `specs/018-reliable-workflow-agent-capacity/validation/` and contains relative references, normalized observations, component IDs/versions/digests, tested client/CLI, and source coordinates. Never store raw transcripts, secrets, absolute host paths, or unrelated configuration. Use `~/.codex/venvs/skill-tools/bin/python` for skill validation; introduce no dependencies.

## Phase 1: Setup

Record current evidence and prepare reproducible validation without assuming a configured or effective limit.

- [X] T001 Capture source revision, controller/workflow versions and SHA-256 digests, Specify and Codex CLI versions, and desktop build when available in `specs/018-reliable-workflow-agent-capacity/validation/baseline.json`; distinguish October 3 observation, operator-reported twelve, historical Feature 014 restoration, and current effective-capacity unknowns using `research.md`.
- [X] T002 Run existing controller/catalog baseline checks from `specs/018-reliable-workflow-agent-capacity/quickstart.md` and record commands, results, and limitations in `specs/018-reliable-workflow-agent-capacity/validation/baseline.json`; verify the skill-tools interpreter before testing and report missing dependencies without changing the environment.
- [ ] T003 Prepare an agent-owned native driver procedure in `specs/018-reliable-workflow-agent-capacity/validation/native-runbook.md` and bounded synthetic scenario manifest in `tests/consumer-fixtures/agent-capacity/scenarios.json`; specify agent-performed disposable initialization, test-only candidate-four config, exact consumer-owned agent definitions, typed identity/read/release checks, separate workflow invocations, predetermined test-actor questions/replies, artifact assertions, and evidence capture. Establish the authorized test scope once; request at most one initial Codex project setup if tooling requires it, never a manual test matrix or repeated command dispatch. Configure before the test chat starts; where supported, use verified driver-owned protected occupancy children to measure a constrained available budget in the same persistent chat rather than require separately configured manual chats. Record trust/override/reload limits and unsupported automation blockers. Enable a release adapter only after the agent establishes native terminal-child release, artifact retention, and a subsequent exact launch. Keep genuine consequential questions/decisions gated and do not supply a synthetic human verdict.

## Phase 2: Foundational

Build the shared persistence boundary before story operations. Do not weaken successful-preflight gating or add native dispatch to Python.

- [ ] T004 Create strict session/identity validation and JSON-stdin CLI scaffolding in `controllers/flow-kit/scripts/python/capacity.py` for the eight operations in `contracts/child-lifecycle.md`; enforce ledger constraints verbatim: schema `1.0`, "unsupported future versions reject writes.", parent "Canonical native parent identity; safe single path component.", children "Map keyed by canonical child ID; records may span invocations in this parent only.", recoveries "Launch-recovery records keyed by invocation/step/iteration/launch-attempt identity.", and updated time "UTC timestamp." Reject unknown fields, unsafe IDs, cross-parent mutation, and unverified caller labels; require `--project`, `--parent-chat-id`, and expected revision for mutations.
- [ ] T005 Implement locked atomic ledger persistence in `controllers/flow-kit/scripts/python/capacity.py` under `.specify/flow-controllers/agent-sessions/<parent-chat-id>/lifecycle.json`; enforce "Nonnegative integer; every mutation checks expected revision and increments it." Use bounded exclusive lock acquisition and atomic replacement, reject stale revisions and escaping/symlinked paths, never guess stale-lock deletion, and retain evidence independently of workflow `runs/`. Implement `inspect-session` as a validated read-only lookup returning revision and compact children/recorded-eligibility/recovery summaries; an absent ledger returns explicit absence with empty summaries and no stored revision, without creating directories, lock files, or a ledger. Recorded eligibility never substitutes for fresh native release observations.
- [ ] T006 Add foundation tests in `tests/test_capacity.py` for CLI contracts, malformed/future schemas, IDs, unknown fields, path traversal/symlinks, concurrent mutation, lock contention, stale revisions, atomic-write failures, and no partial overwrite; verify inspect-session returns compact existing-ledger summaries or an explicit absent-session result, never creates or changes files or eligibility, and Python never dispatches or releases a native child.

**Checkpoint**: Validated atomic session storage exists independently of successful workflow summaries. All story work depends on T001–T006.

## Phase 3: US1 — Continue Sequential Workflow Use

**Goal**: Preserve results and release verified completed FlowKit children immediately, including eligible earlier invocations in the same parent chat.

**Independent test**: In one persistent parent chat, complete at least three separately invoked workflows, more than twelve terminal children, and at least two necessary release cycles at documented constrained capacity. Verify prior-invocation entry cleanup, output usability, release before the next executable step, and a protected child awaiting an answer that receives continuation through the same child.

### Tests for US1

Implement negative and transition assertions before lifecycle operations.

- [ ] T007 [P] [US1] Add lifecycle contract tests in `tests/test_capacity.py` for immutable registration, probe null run IDs, result create-once/digest validation, immediate eligibility, earlier same-parent children, protected active/question/continuation/unrelated/unknown children, stale native observations, races, accepted release versus observed restoration, and excluded unproven legacy ownership.
- [ ] T008 [P] [US1] Add shared-protocol integration/regression assertions in `tests/test_controller.py` for entry cleanup, preservation before release, exact fresh probe/work assignments, same-child answer relay, release before the next executable node, no preflight run creation, installed graph authority, manual fallback, and unchanged gates across the ten active skills; validate `tests/consumer-fixtures/agent-capacity/scenarios.json` and the T003 driver boundary so synthetic inputs cannot authorize real product/Git/roadmap/acceptance actions or hide missing native automation.

### Implementation for US1

Implement typed registration, results, and validated release decisions before integrating native actions.

- [ ] T009 [US1] Implement register-child and observe-child in `controllers/flow-kit/scripts/python/capacity.py`; enforce child constraints verbatim: IDs "Exact native IDs with typed provenance.", invocation "Generated identifier for this invocation, including unsuccessful preflight.", workflow coordinates "Component coordinates from the inspected installed definition.", run ID "Null until successful preflight produces a workflow run; probes may remain null.", purpose "`probe` or `work`.", step/pass "Exact declaration and pass; probe uses a stable preflight assignment ID and null iteration.", agent "Exact declared native name; immutable.", execution "`running`, `waiting-for-answer`, `terminal`, or `unknown`.", interaction "Boolean; terminal turn alone does not establish it.", pending flags "Booleans; either protects the child.", and observation "Compact typed parent/state evidence and observation timestamp; no raw transcript." Keep agent, purpose, invocation, parent, step, and iteration immutable and run linkage post-preflight only.
- [ ] T010 [US1] Implement preserve-result in `controllers/flow-kit/scripts/python/capacity.py` as "create-once compact validated output" in `results/<child-id>.json`, with schema and immutable invocation/step/agent identity, result kind "`probe-readiness`, `step-output`, or `assessment`", and portable usable content; readiness is boolean with validated marker kind, never a `token` key. Enforce result fields "Existing immutable project-relative result and digest, or null until preserved." Separate substantive author outputs from review outcomes; reject raw questions/answers, secrets, host paths, missing files, and digest mismatch.
- [ ] T011 [US1] Implement plan-release and record-release in `controllers/flow-kit/scripts/python/capacity.py`; enforce release state "`retained`, `eligible`, `requested`, `accepted`, `failed`, or `unavailable`.", method/evidence "Capability-selected method and compact result evidence, or null.", and restoration "`unconfirmed` or `observed`; observed requires a subsequent successful exact launch reference." Require verified same-parent FlowKit ownership, terminal state, completed interaction, retained matching result, fresh native observation, unchanged revision, and supported adapter; exclude unsafe legacy records and fail closed on state changes or ambiguous results.
- [ ] T012 [US1] Integrate lifecycle calls into `controllers/flow-kit/controller-protocol.md` at invocation entry and every completed probe/work pass: register actual typed identities, preserve validated results, keep unfinished interaction protected, re-observe immediately before native release, and release eligible children before the next executable node. Prefer supported close/retire; use reversible archival only with validated client evidence from T003; never interrupt, guess IDs, edit app state, reuse probes, or clean another parent chat.
- [ ] T013 [US1] Add optional validated lifecycle references to successful run summaries in `controllers/flow-kit/scripts/python/recovery.py` and compatibility assertions in `tests/test_controller.py`; preserve `create_summary()` rejection of unsuccessful preflight, older summaries without references, original step/pass identity, retained outputs, and separate probe diagnostics without semantic progress.
- [ ] T014 [US1] Execute T007/T008 and affected existing controller tests; record results and evidence-retention assertions in `specs/018-reliable-workflow-agent-capacity/validation/us1-deterministic.json`, explicitly distinguishing static protocol checks from real native execution.
- [ ] T015 [US1] Using the agent-owned driver and synthetic inputs from T003 within the disposable-test scope in `validation/native-runbook.md`, have the implementation agent separately invoke Plan, Tasks, and Analyze and Remediate plus additional invocations as needed; record at least three completions, more than twelve terminal children, and two necessary release cycles in `specs/018-reliable-workflow-agent-capacity/validation/us1-native.json`. Prove immediate release, earlier same-parent entry cleanup, retained independent artifacts, protected same-child answer relay, exact assignments, and fresh successful launches after release; do not mark complete on simulation, unsupported ownership/release, or missing authorization.

**Checkpoint**: US1 is the MVP only after both deterministic and native criteria pass. US2 can use synthetic ledger fixtures for independent recovery tests without repeating the full US1 sequence.

## Phase 4: US2 — Recover Safely from Exhaustion

**Goal**: Recover a positively classified unstarted capacity launch failure within one cleanup sweep and one exact retry, or preserve a specific actionable stop.

**Independent test**: Force a capacity launch failure with an eligible completed child, then verify one release sweep and one successful exact-name retry. Separately exercise preflight, post-start, corrective-loop, repeated exhaustion, unknown failure, no eligible child, and failed/unavailable release; prove no completed mutation or started command is replayed.

### Tests for US2

Test the finite retry envelope and workflow-state boundary separately.

- [ ] T016 [P] [US2] Add recovery contract tests in `tests/test_capacity.py` for positive capacity classification, original launch identity, zero/one retries, retry exhaustion, no eligible child, ownership/result/state uncertainty, failed/unavailable release, exact-agent enforcement, and release acceptance without a successful launch; reject retry above one and mutation of the failed step/pass assignment.
- [ ] T017 [P] [US2] Add recovery integration tests in `tests/test_controller.py` covering unsuccessful preflight diagnostics without a run, existing-run partial state, corrective-loop pass/mutation preservation, no command replay, no retry after work starts, stable stop codes and resume actions, legacy summary compatibility, and unknown launch errors retaining existing unavailable behavior.

### Implementation for US2

Add bounded recovery without broadening the controller's execution authority.

- [ ] T018 [US2] Implement begin-recovery and record-retry in `controllers/flow-kit/scripts/python/capacity.py`; enforce recovery "retry count (zero or one)", result "`recovered` or `blocked`", exact parent/invocation/step/pass/agent, original launch, candidate/release references, retry reference, stable reason/resume action, and optional run ID. Require positive capacity failure plus at least one successful eligible release before permitting one retry; recovered requires that successful exact launch and restoration reference, never cleanup alone.
- [ ] T019 [US2] Add the seven capacity stop codes from `contracts/child-lifecycle.md` and validated optional recovery references in `controllers/flow-kit/scripts/python/recovery.py`; preserve completed work and current step/pass, keep preflight diagnostics outside runs, and retain normalized codes/relative references without raw native errors.
- [ ] T020 [US2] Integrate classification, one sweep and one fresh exact launch into `controllers/flow-kit/controller-protocol.md`; stop on unknown errors, no eligible child, failed/unavailable release, uncertain ownership/evidence/state, or repeated exhaustion. Preserve fingerprints, gates, and partial state; retry neither a started command nor an earlier completed node, and describe a fresh chat as fallback rather than a durable fix.
- [ ] T021 [US2] Run the recovery suites and record the complete failure/preservation matrix in `specs/018-reliable-workflow-agent-capacity/validation/us2-deterministic.json`, including launch-count assertions, unchanged completed artifacts/pass counts, specific blocked reasons, and old-summary compatibility.
- [ ] T022 [US2] Have the implementation agent execute native recovery cases from `validation/native-runbook.md` using T003 fixtures and scoped synthetic replies in a disposable consumer and record `specs/018-reliable-workflow-agent-capacity/validation/us2-native.json`: forced exhaustion with eligible release and successful exact retry, protected child, unavailable/failed release where supported, and repeated failure bounds. Separate genuinely observed cases from deterministic fault injection and leave unperformed required acceptance explicitly open.

**Checkpoint**: Positive recovery and safe stops are proven without replay or fallback identity. Native success is required for the restoration claim.

## Phase 5: US3 — Configure a Consumer at Install or Upgrade

**Goal**: Deliver visible, truthful, validation-backed setup guidance for install and refresh while preserving consumer config ownership and bytes.

**Independent test**: Install and refresh disposable consumers with absent, compatible, different/conflicting, malformed, and unsupported configuration; verify one qualified notice per operation and an accessible guide. Assert unchanged config bytes and ownership through install, refresh, partial failure/rollback, and removal. Apply the example only under explicit test authorization, verify behavior at candidate four, and distinguish configured from effective values.

### Tests for US3

Test catalog output separately from managed-file lifecycle preservation.

- [ ] T023 [P] [US3] Add notice/advisory tests in `tests/test_catalog.py` for install/refresh once-only success output, qualified post-mutation partial failures, all advisory states including unknown inspection, alias conflicts/different values, malformed bounded parsing, and unsupported clients; assert no global-config read, config writes, exposed unrelated fields, or effective/adoption claims.
- [ ] T024 [P] [US3] Add byte/digest ownership tests in `tests/test_bundle_lifecycle.py` for absent/existing/conflicting/malformed consumer `.codex/config.toml` through install, refresh, partial failure/rollback, and removal; assert config never enters managed files and consumer feedback, lifecycle ledgers/results, run summaries, and unrelated components survive.

### Implementation for US3

Prepare guidance and read-only advisory state, then integrate packaging and prove the recommendation.

- [ ] T025 [P] [US3] Author `controllers/flow-kit/agent-capacity.md` using `contracts/consumer-capacity-guidance.md`: operator merge into the existing `[agents]` table, canonical setting and legacy alias reconciliation, absent/compatible/conflicting/malformed/unsupported/unknown cases, trust/precedence, effective-value limits, conservative fresh-chat application unless live reload is verified, and resource/concurrency tradeoff. Clearly label four as a candidate until T030 passes; explain why increased capacity and lifecycle cleanup are complementary.
- [ ] T026 [P] [US3] Implement bounded read-only target-project advisory inspection in `tools/catalog.py` using existing standard-library TOML support; enforce advisory constraints verbatim: operation "`install`/`refresh`", operation state "`completed`/`partial-failure`", config state "`absent`/`compatible`/`review-needed`/`malformed`/`unsupported`/`unknown`", configured value "when safely known", recommendation value "once validated", `configuration_changed=false`, and `effective_capacity_verified=false`. Unsupported/unavailable inspection stays truthful, different valid values remain consumer choices, and malformed advice never changes a successful component outcome.
- [ ] T027 [US3] Integrate one install/refresh notice in `tools/catalog.py:install()` after successful controller installation and qualified output after partial mutation failure; reference `.specify/flow-kit/agent-capacity.md`, retain existing errors/ownership checks, and avoid duplicate notices from low-level preflight/package installation.
- [ ] T028 [US3] Add `controllers/flow-kit/agent-capacity.md` explicitly to `controller_package_files()` in `tools/catalog.py`, verify script enumeration includes `capacity.py`, and extend `tests/test_snapshot_validation.py` to prove development-snapshot payload/digests include both; exclude consumer `.codex/config.toml` and all consumer evidence from package ownership. Use temporary development snapshots; do not rebuild checked-in release archives.
- [ ] T029 [US3] Run catalog/lifecycle/snapshot tests and actual disposable initialize/install/refresh/partial-failure/remove routes per `quickstart.md`; record notices, guide accessibility, config before/after hashes, preservation and operation outcomes for all required states in `specs/018-reliable-workflow-agent-capacity/validation/us3-lifecycle.json` with actual Specify version and source digests.
- [ ] T030 [US3] Have the implementation agent verify the candidate-four configuration it prepared in T003 within the disposable-test scope, safely complete/release protected occupancy fixtures, and verify unconstrained application using supported metadata when exposed plus native sequential/release behavior from `validation/native-runbook.md`; record trust/override/reload evidence and actual client in `specs/018-reliable-workflow-agent-capacity/validation/us3-native.json`. Unknown effective values remain unknown; do not call CLI parsing or file presence runtime verification. Missing setting introspection alone is a disclosed limitation; supported setup/trust/reload handling and actual native behavior must still be validated. Establish constrained-budget evidence from supported runtime metadata or measured behavior, and record limits of attributing results to the configured candidate rather than infer effectiveness from the file. Reconcile spec/plan/research/tasks if candidate fails rather than publish untested advice.
- [ ] T031 [US3] After T030 succeeds, reconcile the tested recommendation, limitations, and source evidence in `controllers/flow-kit/agent-capacity.md`, `docs/installation.md`, and `specs/018-reliable-workflow-agent-capacity/research.md`; document easy install/upgrade/operator-merge/verification steps and packaged guide reference. Remove candidate wording only for the value actually validated, and retain unsupported/reload/effective-setting limits.

**Checkpoint**: Both install and refresh provide tested guidance; config stays consumer-owned and byte-preserved. No consumer adoption, publication, or feature acceptance follows from these checks.

## Phase 6: Polish and Cross-Cutting Validation

Complete source-package consistency and final proof without starting another workflow or publishing a release.

- [ ] T032 Update the reviewed controller version in `controllers/flow-kit/manifest.yml` and any protocol version declarations in `controllers/flow-kit/controller-protocol.md` consistently with repository versioning rules; record old/new component coordinates and digests in `specs/018-reliable-workflow-agent-capacity/validation/package.json`. Do not mutate checked-in release archives/catalog release pins without separate publication scope.
- [ ] T033 Run the full available unittest suite with the skill-tools interpreter, affected graph/path/agent-config regressions, development-snapshot validation, and `git diff --check`; record commands/results in `specs/018-reliable-workflow-agent-capacity/validation/final-checks.json`. Verify no graph topology, probe count/purpose, agent names, Select Feature approval routing, Feature 016/017 delivery, generated installed source, or real-consumer config changed; distinguish explicitly authorized disposable fixture setup from install/refresh/remove operations, which must preserve fixture config bytes.
- [ ] T034 Re-run affected disposable install/refresh/native checks against final T032 source coordinates where version/package changes invalidate earlier fingerprints; record attributable final artifacts in `specs/018-reliable-workflow-agent-capacity/validation/package.json`, retaining earlier evidence as earlier evidence rather than relabeling its digests.
- [ ] T035 Audit spec/plan/contracts/tasks and all validation records against FR-001–017 and SC-001–007; write `specs/018-reliable-workflow-agent-capacity/validation/acceptance.md` with requirement-to-evidence mapping, scenario executors and actual human involvement, failed/skipped/unknown checks, manual fallback, native bounds, and explicit remaining operator decisions. Missing safe ownership/release evidence or required actual native outcomes remains blocking; unavailable effective-setting introspection alone is a disclosed limitation, never a verified value or substitute for behavioral proof. Reconcile any divergence before claiming implementation readiness; recommend separately invoked FlowKit Converge and applicable review, and leave acceptance/roadmap/Git/publication to the operator.

## Dependencies and Execution Order

The main delivery path is setup → foundation → US1 lifecycle → US2 recovery → US3 guidance → final validation. All three stories retain independent test criteria; recovery depends on lifecycle implementation, and recommendation validation depends on native lifecycle results.

| Stage | Dependencies and order |
|---|---|
| Setup | T001 → T002 → T003. T003 establishes one agent-owned test scope and driver; only one initial project setup may require the operator. Unsupported capability/automation is a blocker, never a manual test assignment or permission for a substitute. |
| Foundation | T004 → T005 → T006; completed setup is required. |
| US1 | After foundation, T007/T008 may run together; then T009 → T010 → T011 → T012 → T013 → T014 → T015. Native tests use a development snapshot of implemented source. |
| US2 | After T014, T016/T017 may run together; then T018 → T019 → T020 → T021 → T022. T015 need not repeat for deterministic fixtures, but remains required acceptance. |
| US3 | After foundation, T023/T024 may run together and then T025/T026 may run together. T027 requires T026; T028 requires T025/T027 and lifecycle source. T029 follows T028; T030 requires T015/T022/T029; T031 follows T030. Default execution keeps this story after US2. |
| Final | T032 after all story implementations; T033 → T034 → T035. All native acceptance must pass before T035 can report criteria satisfied. |

The only marked parallel pairs are T007/T008, T016/T017, T023/T024, and T025/T026. Do not overlap later edits to shared `capacity.py`, `recovery.py`, `controller-protocol.md`, `tools/catalog.py`, or test files. Native acceptance runs sequentially so it measures the specified persistent-chat behavior.

## Parallel Examples

These examples identify work that can proceed concurrently without shared-file edits; they do not invoke agents or workflows.

- **US1**: After T006, author T007 in `tests/test_capacity.py` alongside T008 in `tests/test_controller.py`; finish both before T009.
- **US2**: After T014, author T016 in `tests/test_capacity.py` alongside T017 in `tests/test_controller.py`; finish both before T018.
- **US3**: After foundation, author T023 in `tests/test_catalog.py` alongside T024 in `tests/test_bundle_lifecycle.py`. After both, T025 guide drafting can proceed alongside T026 catalog inspection; T027/T028 integrate their outputs sequentially.

## Implementation Strategy

Deliver the smallest observable increment, and stop at each evidence checkpoint to assess divergence rather than infer success from checked tasks.

1. Establish current native identity/release capability and deterministic persistence first. Unavailable safe native controls remain a reported delivery blocker.
2. Complete US1 as the MVP: immediate safe release, retained outputs, protected question relay, and the real sustained same-chat test. A simulated ledger is not an MVP acceptance result.
3. Add US2's one-sweep/one-retry recovery and prove failure state preservation independently with prepared fixtures and real recovery evidence.
4. Add US3 notices/packaged guidance/config preservation, then validate candidate four before final recommendation wording.
5. Verify final source coordinates and full coverage. Record missing authorization or unavailable live evidence as open tasks; never replace them with mocked success, roadmap verification, implicit Git permission, or feature acceptance.

## Requirement Coverage

The mapping makes implementation and evidence gaps reviewable before any task is considered complete.

| Requirement | Tasks and proof |
|---|---|
| FR-001 | T001–T003, T030: controls, provenance, precedence and effective-value limits. |
| FR-002 | T001: October 3 observation versus historical Feature 014 and reported twelve. |
| FR-003 | T007–T010, T012–T015: fresh exact assignments and preserved usable results. |
| FR-004 | T007, T009, T011–T012, T015: verified same-parent ownership and protected children. |
| FR-005 | T008, T011–T015: entry/immediate release and separate restoration proof. |
| FR-006 | T016–T022: two launch attempts maximum, no replay or substitution. |
| FR-007 | T013, T017, T019–T022: preflight diagnostics versus partial-work summaries. |
| FR-008 | T011, T018–T022, T025: specific stops and fresh-chat fallback limits. |
| FR-009 | T023, T027, T029, T031: once-only install and refresh notices. |
| FR-010 | T025–T031: supported merge guidance, trust, aliases, validation and reload. |
| FR-011 | T024, T026–T029: byte preservation and ownership exclusion. |
| FR-012 | T025, T030–T031: modest measured value and cleanup tradeoff. |
| FR-013 | T006–T008, T014–T017, T021–T024, T029–T030, T033–T035: deterministic, lifecycle and native matrices. |
| FR-014 | T001, T010, T014–T015, T021–T022, T029–T030, T032–T035: portable attributable evidence. |
| FR-015 | T008, T012–T013, T020, T033: installed graph, same-child relay, manual fallback and gates. |
| FR-016 | T033–T035: independent features and excluded scope. |
| FR-017 | T003, T008, T015, T022, T029–T030, T035: agent-owned preparation, execution, synthetic interactions, evidence, and limited human setup. |
| SC-001 | T015: at least three invocations, >12 terminal children, two necessary release cycles. |
| SC-002 | T007–T008, T011–T015: immediate/entry release and protected-child assertions. |
| SC-003 | T016–T022: successful bounded recovery or preserved specific stop. |
| SC-004 | T023–T024, T029: five required configuration cases and unchanged bytes on both routes. |
| SC-005 | T025, T030–T031: actual candidate behavior, setup application and honest unsupported/unknown limits. |
| SC-006 | T001–T003, T015, T022, T030, T035: distinguish facts, static evidence, history and current acceptance. |
| SC-007 | T003, T008, T015, T022, T029–T030, T035: zero human-executed test cases/dispatch steps, at most one initial project setup, preserved genuine decision gates. |

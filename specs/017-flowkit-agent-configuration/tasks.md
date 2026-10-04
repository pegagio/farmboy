# Tasks: FlowKit Agent Configuration and Consumer Delivery

**Input**: Approved specification and reviewed design in `specs/017-flowkit-agent-configuration/`: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/agent-package.md`, `contracts/agent-delivery-cli.md`, and `quickstart.md`.

**Organization**: Tasks follow the three specification stories. All tasks are unfinished; no prior `tasks.md` or completed task history exists. Tests are included because FR-010 and FR-012–014 explicitly require lifecycle and configuration validation. Implementation must use existing tooling, preserve unrelated changes, and stop for unresolved support or authority decisions. This list does not authorize Git integration, publication, another workflow, or acceptance.

## Table of Contents

- [Format and Paths](#format-and-paths)
- [Phase 1: Setup](#phase-1-setup)
- [Phase 2: Foundation](#phase-2-foundation)
- [Phase 3: US1 — Recognize the Exact FlowKit Role (P1)](#phase-3-us1--recognize-the-exact-flowkit-role-p1)
- [Phase 4: US2 — Inspect Reviewed Instructions and Model Choices (P1)](#phase-4-us2--inspect-reviewed-instructions-and-model-choices-p1)
- [Phase 5: US3 — Acquire and Maintain Agents Safely (P2)](#phase-5-us3--acquire-and-maintain-agents-safely-p2)
- [Phase 6: Cross-Cutting Validation](#phase-6-cross-cutting-validation)
- [Dependencies and Parallel Work](#dependencies-and-parallel-work)
- [Requirement Coverage](#requirement-coverage)
- [Implementation Strategy](#implementation-strategy)
- [Task Author Self-Check](#task-author-self-check)
- [Phase 7: Convergence](#phase-7-convergence)
- [Phase 8: Convergence](#phase-8-convergence)
- [Phase 9: Convergence](#phase-9-convergence)
- [Operator-Directed Deferred Follow-up](#operator-directed-deferred-follow-up)

## Format and Paths

Every task has a sequential ID and an exact repository-relative path. `[US1]`–`[US3]` map to specification stories; `[P]` permits parallel work only after stated prerequisites are complete and when file ownership does not overlap. New source files are prospective. Consumer destinations in descriptions identify disposable test targets, not permission to alter an existing consuming product.

The package contract lists all eight canonical filenames. `.codex/agents/flowkit-*.toml` denotes exactly those eight local copies, never a destructive prefix glob. `workflows/speckit-flow-*/workflow.yml` denotes the ten active packages; deprecated Start Feature stays stop-only. Portable evidence belongs in `specs/017-flowkit-agent-configuration/validation.md`, introduced by T001 and extended by later evidence tasks.

## Phase 1: Setup

Record the current baseline and prepare bounded fixtures without changing upstream decisions.

- [X] T001 Record source revision, component versions/digests, installed Specify and Codex client versions, current eight-role inventory and approval references in `specs/017-flowkit-agent-configuration/validation.md`; distinguish observed facts from planned checks and omit absolute host paths, secrets and raw transcripts.
- [X] T002 Create lifecycle scenario fixtures in `tests/consumer-fixtures/agent-delivery/scenarios.json` for clean/customized/old-only inventories, package updates with a fixture-only new role, rename/retirement, duplicate identities and partial writes; map expected dispositions to the approved CLI contract without introducing a ninth production role.

## Phase 2: Foundation

Establish the canonical package boundary and strict reusable validation. T001–T002 precede this phase; story implementation follows its completion.

- [X] T003 Create `agents/flow-kit/manifest.yml` at package `flow-kit-agents` version `0.1.0`, schema `1.0`, with all eight exact name/file/destination mappings from the package contract and rename/retirement guidance; record no consumer ownership fields.
- [X] T004 Add manifest/package validation in `tools/catalog.py` and focused cases in `tests/test_catalog.py`: “duplicate names/files/destinations fail”, “contain nonempty required fields and match manifest names”, “cannot escape allowed roots via `..`, absolute paths or symlinks”, “Unlisted archive entries fail”, and “All reset targets must be current manifest entries”; reject malformed TOML, unsafe regular-file sources and version mismatch before mutation. Keep consumer copy handling separate from existing skill ownership.

**Checkpoint**: The inventory contract is enforceable. Canonical TOML population and packaging occur in the story phases; validation failures must not be weakened to accommodate incomplete inputs.

## Phase 3: US1 — Recognize the Exact FlowKit Role (P1)

Deliver exact prefixed identities across source and active dispatch paths while preserving responsibilities, topology and gates.

**Independent test**: Parse all eight canonical/local files and recursively enumerate every active delegated branch; assert one exact intended role per assignment, unchanged delegation/gates/probe timing, and stop without fallback on missing, malformed, duplicate or unavailable identities. A bounded live dispatch check later supplies distinct evidence.

- [X] T005 [P] [US1] Update identity and recursive branch assertions in `tests/test_agent_configs.py` for the eight package-contract filenames and prefixed names, canonical/local equality and distinct author/reviewer roles; recompute assignment coverage rather than freezing the historical count of 49.
- [X] T006 [P] [US1] Add exact-name negative/mixed-version and topology-preservation cases in `tests/test_controller.py`, `tests/test_workflow_graph.py` and `tests/test_workflow_paths.py`; cover missing/invalid/unavailable/ambiguous roles, main-task gates and existing stop paths without aliases, model overrides or changed probe timing.
- [X] T007 [US1] Populate the eight canonical `agents/flow-kit/agents/flowkit-*.toml` files and reconcile the eight `.codex/agents/flowkit-*.toml` local filenames/names from their existing role instructions using `contracts/agent-package.md`; preserve existing responsibilities and inspect local differences before replacement, routing any unresolved customization conflict to the operator.
- [X] T008 [US1] Migrate exact `agent` assignments on all nested branches of the ten active `workflows/speckit-flow-*/workflow.yml` packages and corresponding `flowchart.md` labels; preserve step IDs, booleans, transitions, human gates, manual fallback and deprecated Start Feature's stop-only behavior.
- [X] T009 [US1] Reconcile current identity discovery/allowlists and guidance in `controllers/flow-kit/scripts/python/controller.py`, `controllers/flow-kit/controller-protocol.md`, `controllers/flow-kit/skills/` and `tools/validate_workflows.py`; keep model/effort values solely in native TOML and preserve existing probe/capacity semantics.
- [X] T010 [US1] Reconcile current agent references in `AGENTS.md`, `README.md`, `workflows/README.md`, `docs/architecture.md`, `docs/installation.md` and affected `tests/consumer-fixtures/`; inventory remaining unprefixed references in `specs/017-flowkit-agent-configuration/validation.md`, preserving verified historical records/quotations and documenting why each retained reference is historical.
- [X] T011 [US1] Run identity/controller/graph/path tests and `tools/validate_workflows.py --fail-on-unexplained`, recording commands, observed assignment coverage and preservation findings in `specs/017-flowkit-agent-configuration/validation.md`; require zero unexplained current mismatches before advancing.

**Checkpoint**: Source identity migration is independently testable. Packaging and native effective-setting evidence remain later obligations.

## Phase 4: US2 — Inspect Reviewed Instructions and Model Choices (P1)

Apply the approved role contracts and settings after attributable tested-client support is established; separate configuration assertions from runtime observations.

**Independent test**: Compare eight configs with the approved table and role review, confirm author self-checks and independent review remain distinct, exercise supported fields/values on the tested client, and report unavailable effective settings explicitly.

- [x] T012 [US2] Reuse the accepted Feature 015 desktop evidence for native `model`/`model_reasoning_effort` field loading and the `gpt-6-luna`/`high` pair; verify only the remaining distinct approved pairs (`gpt-6.1-sol` with `low`, `medium` and `high`) through bounded native model/effort availability requests, reusing the prior disposable desktop configuration evidence for field loading. Map evidence to each role/pair and record client identity/version when available, method, result and inherited evidence limits in `specs/017-flowkit-agent-configuration/validation.md`. Unsupported or unavailable choices block their application pending operator resolution; metadata alone is insufficient.
- [X] T013 [US2] Extend `tests/test_agent_configs.py` to require explicit approved pairs and scope/output/question/blocker/self-check contracts for all eight definitions, while rejecting sandbox/tool permission expansion or workflow role-to-model maps; retain exact identity and author/reviewer separation checks.
- [X] T014 [US2] Apply supported approved values to the eight canonical `agents/flow-kit/agents/flowkit-*.toml` files: Sol/low for Roadmap Agent and Wiki Curator, Sol/high for Specifier, Planner and Reviewer, Sol/medium for Code Reviewer, and `gpt-6-luna`/`high` for Coder and Tasker; use exact `gpt-6.1-sol` strings for Sol and synchronize the eight local `.codex/agents/flowkit-*.toml` copies.
- [X] T015 [US2] Refine the eight `agents/flow-kit/agents/flowkit-*.toml` instruction contracts against `research.md#instruction-review`, routing structured questions/blockers to the main controller with same-child continuation and preserving command-required self-checks, separate review, role exclusions and workflow/Git/acceptance prohibitions; synchronize local copies and record a role-by-role authority-preservation diff in `specs/017-flowkit-agent-configuration/validation.md`. Return material authority changes to the operator.
- [X] T016 [US2] Document the eight approved settings, responsibility-based rationale, editable consumer defaults and distinctions among requested/support/live/effective settings in `docs/installation.md` and `docs/architecture.md`; retain no-fallback behavior and make evidence limits explicit without claiming benchmarks or savings.
- [X] T017 [US2] Run focused `tests/test_agent_configs.py` checks and review all eight instruction/settings diffs, recording configuration/support outcomes and unresolved evidence in `specs/017-flowkit-agent-configuration/validation.md`; author self-check does not replace assigned independent review.

**Checkpoint**: Every default has explicit supported approved settings and an inspectable role contract; live dispatch/effective observations are recorded in the final validation phase.

## Phase 5: US3 — Acquire and Maintain Agents Safely (P2)

Deliver the package through the catalog and expose consumer-owned install-missing/reset operations with predictable update, removal and bounded recovery behavior.

**Independent test**: Disposable initialized consumers exercise the full lifecycle matrix, assert bytes of preserved files, verify manifest-targeted reset only, inspect portable reports and provoke both preflight and mid-operation failures.

- [X] T018 [P] [US3] Add deterministic package-build/integrity tests in `tests/test_catalog.py` for canonical-source-only archives, package/source digests and coordinates, version pin consistency, changed bytes, unsafe/unlisted members and snapshots versus released metadata; preserve existing controller skill packaging behavior.
- [X] T019 [P] [US3] Add disposable-consumer lifecycle tests in `tests/test_bundle_lifecycle.py` using `tests/consumer-fixtures/agent-delivery/scenarios.json`: clean/repeat install, edited/prefixed/unprefixed/unrelated copies, cache-only refresh, fixture-new-role acquisition, reset-one/all, rename/retirement and removal; assert no per-copy hashes or customization classification and retain existing skill/component/feedback behavior.
- [X] T020 [US3] Implement deterministic `flow-kit-agents` archive construction and verification in `tools/catalog.py` from `agents/flow-kit/manifest.yml` and listed TOML only; expose catalog `agent_package` provenance (`id`, `version`, `artifact`, `sha256`, `source_repository`, `source_commit`, `source_sha256`, `status`) without packaging mutable local `.codex/agents/` files.
- [X] T021 [US3] Implement validated available-default cache staging/replacement at `.specify/flow-kit/agent-defaults/package.zip` and `manifest.json` through `tools/catalog.py`; retain the previous cache on staging/validation failure, use the pinned selected package and never hash/classify consumer copies or fetch an unpinned alternative.
- [X] T022 [US3] Implement `agents install-missing <project> [--json]` in `tools/catalog.py`: initialized-project/cache validation, manifest-order preflight, project-only readable identity collision checks, absent-target atomic copying and existing-path preservation; report directories/symlinks as unusable failures, warn on unrelated unparseable TOML and never scan global/personal files during delivery.
- [X] T023 [US3] Implement `agents reset <project> --agent <exact-name> [--json]` and `--all` in `tools/catalog.py`: mutually exclusive required selectors, current-manifest targets only, whole-selection preflight and atomic per-file reset/create; reject unknown names, unsafe ancestors and nonregular destinations, make discarded customization explicit, and preserve unrelated/retired/unprefixed files without a second interactive approval prompt.
- [X] T024 [US3] Implement portable human/JSON operation reporting in `tools/catalog.py` with “Allowed target outcomes are `created`, `preserved-existing`, `reset`, `failed`, `not-attempted`” and “overall status is `complete`, `failed` or `partial`”; preserve manifest order, include package/source provenance and operation inputs, route diagnostics to stderr, use exits 0/1/2 per contract, and identify completed/failed/not-attempted targets plus bounded same-target recovery without claiming bundle rollback.
- [X] T025 [US3] Integrate agent defaults into existing install/refresh/remove functions in `tools/catalog.py`: install caches then adds missing agents after component installation; refresh changes cache only, including newly added definitions; removal deletes available defaults while preserving every consumer copy, feedback and unrelated components. Keep existing managed-skill ledger/conflicts independent.
- [X] T026 [US3] Add the single forwarding `catalog:agents` task in `mise.toml` and CLI help in `tools/catalog.py` matching `contracts/agent-delivery-cli.md`; do not add wildcard reset selectors, aliases, additional wrappers or new dependencies.
- [X] T027 [US3] Add negative/recovery/report contract tests in `tests/test_agent_delivery.py` for unknown/both/neither selectors, missing/invalid cache, digest/version mismatch, duplicate names/files/destinations/project identities, malformed TOML, unlisted/path-escaping archive entries, destination/ancestor symlinks, directories and injected permission/write failures; assert preflight zero agent writes, precise partial results, atomic untruncated files, preserved prior cache and out-of-scope bytes, bounded retries, JSON/stdout/stderr and exit behavior.
- [X] T028 [US3] Update package pin and coordinated breaking-name versions in `bundles/spec-kit-flow/bundle.yml`, `controllers/flow-kit/manifest.yml` and affected active `workflows/speckit-flow-*/workflow.yml` against current source/release coordinates; document chosen versions in `specs/017-flowkit-agent-configuration/validation.md` and never overwrite released artifacts under unchanged coordinates.
- [X] T029 [US3] Regenerate `catalog/release.json` and `catalog/packages/` using the existing catalog build/development-snapshot path after explaining the necessary generated metadata/package change; verify package digests/version pins and source provenance, distinguishing local snapshot validation from publication and preserving independent roadmap/wiki components.
- [X] T030 [US3] Write step-by-step acquisition, customization, refresh-plus-install-missing, explicit reset-one/all, old-name migration, renamed/retired preservation, partial recovery and removal instructions in `docs/installation.md`; describe every affected-file disposition, direct editing, no ownership detection/merging, remaining native assignment dependencies and manual fallback without another workflow invocation.
- [X] T031 [US3] Run focused catalog, agent-delivery and bundle lifecycle suites in `tests/test_catalog.py`, `tests/test_agent_delivery.py` and `tests/test_bundle_lifecycle.py`; record expected/observed scenario results, tested versions/source digests and preserved files in `specs/017-flowkit-agent-configuration/validation.md`, with no usability claim for unresolved mixed-version/collision cases.

**Checkpoint**: Acquisition and maintenance work independently in disposable consumers, with manifest-bounded reset and explicit preservation/recovery results.

## Phase 6: Cross-Cutting Validation

Finish attributable lifecycle/live evidence and repository-wide checks after all story checkpoints. Evidence gaps stay visible; test success never grants acceptance.

- [X] T032 Execute the approved `specs/017-flowkit-agent-configuration/quickstart.md` matrix in disposable initialized consumers using the supported Specify version and development snapshot; record component IDs/versions/source coordinates/digests, scenario inputs, observed results and recovery outcomes in `specs/017-flowkit-agent-configuration/validation.md`, independently preserving customized fixtures before any reset.
- [X] T033 Validate all eight exact native names through the existing installed-controller dispatch/probe procedure in a disposable project/session, without invoking a later FlowKit phase or redesigning probes; record separate configuration, field/value support, live exact-dispatch and observed effective model/effort results in `specs/017-flowkit-agent-configuration/validation.md`. Treat unavailable fields/models as operator blockers, effective settings without native observation as unverified, and no-op transport/labels as insufficient live proof.
- [X] T034 Run the full existing unittest suite once after focused checks pass and run `tools/validate_workflows.py --fail-on-unexplained`; verify Feature 016/018 probe/capacity behavior, deprecated Start Feature, human gates, manual fallback and Diagram authority remain unchanged, recording checks or exact limitations in `specs/017-flowkit-agent-configuration/validation.md`.
- [X] T035 Reconcile final current references and operator-facing claims in `README.md`, `AGENTS.md`, `docs/installation.md`, `docs/architecture.md` and `workflows/README.md` with validated behavior; complete the requirement/evidence coverage and residual-gap report in `specs/017-flowkit-agent-configuration/validation.md` without rewriting historical feature/wiki provenance or claiming release, adoption, roadmap verification or acceptance.

## Dependencies and Parallel Work

Execute phases in order because settings/configuration packaging share source files. Task numbers within a phase specify the default sequence, with only the following parallel exceptions:

- T005 and T006 can run together after T004; T007–T011 wait for these test expectations and then run in order.
- T012 is a support gate before T014–T015 apply settings; T013 follows the US1 test updates. T014–T017 run in order because source files and evidence overlap.
- T018 and T019 can run together after T017 and T002; T020–T026 run sequentially in `tools/catalog.py`. T027 follows their interfaces; T028–T031 follow package implementation, and T029 requires T028.
- T032–T035 follow all stories and run sequentially because they append the same evidence report. Existing installed controller/source version differences require a development snapshot, not manual installed-copy edits.

The story dependency graph is `Setup → Foundation → US1 → US2 → US3 → Cross-cutting validation`. US1 is the smallest independently testable source MVP; it is not a release of migrated workflows into consumers without US2/US3 coordinated defaults delivery. US2 consumes renamed source definitions. US3 packages those reviewed definitions and must not invent a separate behavioral source.

### Parallel example: US1

Run T005 (`tests/test_agent_configs.py`) and T006 (`tests/test_controller.py`, graph/path tests) together after foundation. Keep T007–T009 source migrations sequential; shared config/controller writes are not parallel tasks.

### Parallel example: US2

There is no safe intra-story file-write parallel group: T013 shares the US1 agent-test file, T014–T015 share canonical/local TOML, and T012/T015/T017 append evidence. Run this story in sequence; client support validation is a prerequisite rather than an assumed answer.

### Parallel example: US3

Run T018 (`tests/test_catalog.py`) and T019 (`tests/test_bundle_lifecycle.py`) together after US2. Implement T020–T026 sequentially because they share `tools/catalog.py`; implement recovery tests only when those interfaces exist.

## Requirement Coverage

Coverage maps implementation obligations to concrete tasks; completion requires observed evidence, not merely marking this table covered.

| Requirements | Tasks | Validation focus |
|---|---|---|
| FR-001–002 | T003–T011, T028, T035 | Eight names, all nested assignments, discovery/current references and historical preservation |
| FR-003–006 | T012–T017, T033 | Approved instruction contracts/settings, support gate and independent-review distinction |
| FR-007 | T006, T009, T013, T033–T034 | No model map/override/alias; affected-name stop without fallback |
| FR-008–009 | T018–T026, T028–T031 | Consumer-owned copies, cache-only refresh, manifest reset and preservation on removal |
| FR-010–011 | T002, T019, T027, T030–T032, T035 | Full lifecycle/migration/error disposition, usable step-by-step guidance and fallback |
| FR-012–014 | T001, T011–T012, T017, T027, T031–T035 | Disposable consumer matrix, portable provenance and separate support/live/effective evidence |
| FR-015–016 | T006, T009, T020, T025, T028, T034–T035 | Existing probe/capacity/topology and generic-source/component/Diagram boundaries |
| SC-001–006 | T011, T017, T031–T035 | Identity, settings, operator predictability, preservation and attributed evidence/gaps |

## Implementation Strategy

Deliver US1 as the source MVP and validate its exact identities/topology. Add US2 only after tested-client support is confirmed, preserving the approved Tasker/Coder Luna/high choice and independent Sol/high Reviewer. Add US3 as the coordinated consumer-ready increment, then run the complete quickstart and live evidence checks.

Write requested test cases before the corresponding behavior and confirm they fail for the intended missing behavior; establish each phase checkpoint with focused checks. Broad testing occurs once after focused suites pass unless new changes/failures justify another run. Return unsupported settings, material authority changes and unresolved migration conflicts to the operator; never substitute a role/model or edit upstream decisions to force completion. Independent review belongs to the separately assigned Reviewer. Git integration, publication and acceptance need their own explicit authorization.

## Task Author Self-Check

All 35 task IDs are sequential, unique and unfinished; every task has repository-relative paths, and all story-phase tasks have the matching story label. Only disjoint test groups have `[P]`. Each story includes an independent test and checkpoint. The data-model constraints and CLI enums are carried into T004/T024; lifecycle preservation and error/retry cases are explicit. Approved values include `gpt-6-luna`/`high` for Tasker. All FR-001–016 and SC-001–006 map to implementation/evidence tasks. No specification, design, roadmap, installed component or implementation was changed by task generation. `.specify/extensions.yml` defines no `before_tasks` or `after_tasks` hooks; no hook dispatch is required. This self-check does not establish independent review or feature acceptance.


## Phase 7: Convergence

The 2026-10-04 present-state assessment found five remaining obligation groups. These tasks trace the gaps to the existing unfinished work; they do not replace, renumber or waive T012–T035. Follow their prerequisites, especially the tested-client support gate, and preserve completed identity work. Complete the referenced original tasks with evidence before completing the corresponding convergence task.

- [X] T036 Complete the three distinct Sol/low, Sol/medium and Sol/high desktop support checks remaining after reusing accepted Feature 015 field-loading and Luna/high evidence, mapping the resulting support evidence to all eight roles in `specs/017-flowkit-agent-configuration/validation.md`, then complete T012–T014 to apply and validate explicit settings in `agents/flow-kit/agents/flowkit-*.toml` and the corresponding local copies; preserve the operator-resolution gate if support remains unavailable. CRITICAL per FR-006, US2/AC3 and plan: supported-client validation before settings application (missing; F1).
- [X] T037 Complete T015–T017 to refine and independently assess the eight instruction contracts in `agents/flow-kit/agents/flowkit-*.toml`, synchronize local copies, and document allowed mutations, questions, blockers and evidence boundaries in `docs/architecture.md` and `specs/017-flowkit-agent-configuration/validation.md` per FR-003–005 and US2/AC1–2 (partial; F2).
- [X] T038 Complete T018–T027 and T031 to build and validate deterministic agent packaging, available-default cache, install-missing, manifest-targeted reset, portable reports and consumer-preserving removal in `tools/catalog.py`, `mise.toml`, `tests/test_agent_delivery.py` and the existing catalog/lifecycle suites per FR-008–010, US3/AC1–6 and plan: consumer-owned delivery (missing; F3).
- [X] T039 Complete T028–T030 and the migration guidance portion of T035 to coordinate breaking-name versions and package pins in `bundles/spec-kit-flow/bundle.yml`, `controllers/flow-kit/manifest.yml` and active workflow manifests, regenerate `catalog/release.json` and `catalog/packages/` through the existing build path, and explain acquisition/update/reset/mixed-version recovery in `docs/installation.md`; validate disposable installations before claiming name compatibility per FR-002, FR-011 and plan: coordinated component delivery (partial; F4).
- [X] T040 Complete T032–T035 to exercise the disposable-consumer matrix, exact native dispatch, observed effective settings or explicit gaps, full relevant checks and final requirement/claim reconciliation in `specs/017-flowkit-agent-configuration/validation.md`, `README.md`, `AGENTS.md` and current architecture/workflow guidance per FR-012–016, SC-001–006 and Constitution V (partial; F5).


## Phase 8: Convergence

The resumed assessment checked 16 functional requirements, six success criteria, 14 acceptance scenarios, nine implementation/design obligation groups and five constitution principles. It found two high-severity partial gaps. Delivery implementation and automated source evidence are present; the inherited native CLI transport failure is documented rather than represented as a passed check. These tasks preserve and complete the open T017/T033/T037/T040 obligations; no role substitution or evidence waiver is authorized.

- [X] T041 Obtain independent assessment of the eight canonical/local instruction and settings diffs by the exact assigned FlowKit review role in a Codex session that loads the migrated definitions; record findings and their resolution in `specs/017-flowkit-agent-configuration/validation.md`, then complete T017/T037. Preserve author/reviewer separation and report exact unavailable-role recovery without generic or old-name substitution per FR-003–005, US2/AC1–2 and plan: independent instruction assessment (partial; F6, HIGH).
- [X] T042 Complete the current all-eight exact native dispatch checks using the existing installed-controller procedure in a disposable consumer/session with coordinated agent/controller/workflow versions; separately record support, dispatch and observed effective settings or explicit observation gaps in `specs/017-flowkit-agent-configuration/validation.md`, retain the inherited Specify CLI transport limitation and complete T033/T040 only with attributable results per FR-012–014, US1 independent test, SC-005–006 and Constitution V (partial; F7, HIGH).


## Phase 9: Convergence

The fresh present-state assessment checked 16 functional requirements, six success criteria, 14 acceptance scenarios, nine design obligation groups and five constitution principles. Independent review and all-eight native readiness checks now have attributable evidence with explicit effective-setting gaps. Two HIGH partial reporting gaps remain; preserve all prior evidence and completion markers while correcting them.

- [X] T043 Make human agent-operation output in `tools/catalog.py` include the package/source provenance, exact operation/reset inputs and bounded recovery already represented by JSON; add focused human success/reset/partial-failure assertions in `tests/test_agent_delivery.py`, independently reassess the correction and record results in `specs/017-flowkit-agent-configuration/validation.md` per T024, FR-010/FR-011 and `contracts/agent-delivery-cli.md` (partial; F8, HIGH).
- [X] T044 Identify competing project-relative agent definition paths and the exact collision in `tools/catalog.py` identity-conflict reporting, with specific bounded recovery and no file contents or host paths; add duplicate-identity and destination-conflict attribution/preservation assertions in `tests/test_agent_delivery.py`, independently reassess and complete T040 final reconciliation in `specs/017-flowkit-agent-configuration/validation.md` per T024/T027, FR-010, specification Edge Cases: Identity collision and the CLI contract (partial; F9, HIGH).


## Operator-Directed Deferred Follow-up

On 2026-10-04 the operator deferred confirmed catalog prerequisite defect DEP017-01 to [a follow-up feature](follow-up.md), as recorded in the [specification disposition](spec.md#operator-directed-follow-up-disposition). T030/T032/T040 retain their historical completion evidence under the dependency-equipped tested interpreter; their coverage of unconditional setup/usability is now explicitly qualified. Preserve all 44 task IDs and completion markers. No current task is reopened and no current repair task is appended for this deferred work; no runtime approach, new feature number, environment change or feature acceptance is inferred.

---
description: "Dependency-ordered tasks for the FarmBoy naming cutover and approved native prompt-dispatch bindings"
---

# Tasks: FarmBoy Project and Workflow Naming

**Input**: Design documents from `specs/021-farmboy-project-workflow-naming/`

**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/naming.md`, `contracts/consumer-management.md`, and `quickstart.md`.

**Tests**: Update and run existing regression checks as required by FR-016. Add a focused naming regression only if existing suites do not cover a changed reference; do not add migration tests.

**Organization**: Tasks are grouped by the three approved user stories. This rename has no project initialization, new data model, persistence, service, or API work.

## Phase 1: Setup

**Purpose**: No project setup or dependency changes are needed for this source rename.

## Phase 2: Foundational Gate

**Purpose**: Satisfy the separate governance prerequisite before any rename implementation begins.

- [X] T001 Confirm that the separately reviewed and explicitly approved constitutional identity amendment is present in `.specify/memory/constitution.md`; block all rename work until then. Evidence: Constitution 8.0.0 contains the explicitly approved FarmBoy identity amendment, verified before implementation.

## Phase 3: User Story 1 — Discover and Invoke FarmBoy (Priority: P1)

**Goal**: Publish the existing ten purposes, nine project-owned roles, renderer, and owned feedback commands through their approved FarmBoy identities.

**Independent Test**: Inspect the renamed source bindings and confirm all ten `farmboy-<purpose>` skills/workflows, all nine exact `FarmBoy <role>` assignments, the renderer, and existing capture/report/intake commands resolve under their approved names, while old project-owned invocation names have no aliases.

### Implementation for User Story 1

- [X] T002 [P] [US1] Rename the controller source root and its ten active and deprecated launcher directories to the mappings in `specs/021-farmboy-project-workflow-naming/contracts/naming.md`, updating bootstrap/helper paths and the controller parser to read only `farmboy` metadata under `controllers/farmboy/`.
- [X] T003 [P] [US1] Rename the ten active workflow source directories and deprecated stop-only source to their approved FarmBoy identifiers, changing owned delegation containers from `flow_kit` to `farmboy` in producers and `tools/validate_workflows.py`; update workflow IDs and exact agent assignments while preserving nested fields, steps, and gates under `workflows/farmboy-<purpose>/`.
- [X] T004 [P] [US1] Rename the nine project-owned agent definitions and package root to the exact names, filenames, and unchanged role settings in `specs/021-farmboy-project-workflow-naming/contracts/naming.md` under `agents/farmboy/`.
- [X] T005 [P] [US1] Rename the renderer skill and both owned feedback extension source roots to `farmboy-render-workflow`, `farmboy-feedback`, and `farmboy-feedback-maintainer`; apply the mappings `speckit.flow-feedback.capture` → `speckit.farmboy-feedback.capture`, `speckit.flow-feedback.report` → `speckit.farmboy-feedback.report`, and `speckit.speckit-flow-feedback-maintainer.intake` → `speckit.farmboy-feedback-maintainer.intake`, including generated skills `speckit-farmboy-feedback-capture`, `speckit-farmboy-feedback-report`, and `speckit-farmboy-feedback-maintainer-intake` in manifests, command filenames/docs/self-references under `skills/farmboy-render-workflow/`, `extensions/farmboy-feedback/`, and `extensions/farmboy-feedback-maintainer/`. Update renderer instructions and grammar examples to show `farmboy.delegated` under `skills/farmboy-render-workflow/`. Keep maintainer intake separately packaged and outside generic bundle delivery.

**Checkpoint**: Source identity tables resolve for all ten purposes, nine roles, the renderer, and both feedback extensions without changing workflow or feedback data behavior.

## Phase 4: User Story 2 — Maintain a Consistent Cutover (Priority: P1)

**Goal**: Align package metadata, source references, documentation, and existing test expectations with the cutover while retaining current management interfaces and separating generic feedback delivery from maintainer intake.

**Independent Test**: Build the catalog using existing tooling, inspect bundle/package IDs and pins for both owned feedback extensions, confirm maintainer intake remains outside generic bundle delivery, and run existing install/lifecycle suites with FarmBoy names.

### Implementation for User Story 2

- [X] T006 [US2] Update bundle identity, controller/agent package IDs, owned feedback extension source mappings and pins, branded source/path constants, and project test-environment names in `bundles/farmboy/bundle.yml`, `tools/catalog.py`, and `mise.toml`; keep maintainer intake on its separate installation route and preserve existing command options and behavior. Evidence: catalog tests verify the new FarmBoy source is built directly for its new canonical ID and independent changed pins still require explicit compatible sources; no old-ID fallback or option was added.
- [X] T007 [US2] Generate catalog release metadata and package archives from renamed sources with the existing builder, updating `catalog/release.json` and `catalog/packages/` without hand-editing generated archives. Historical checkpoint evidence only: `build_development_snapshot` produced FarmBoy 0.18.0 metadata/packages and the then-used flow-roadmap 0.3.0 source provenance was dirty and unpublished. At that checkpoint the catalog contained controllers 0.8.0, roadmap 0.3.0, Specify 0.3.0, and Implement/Close Out 0.8.0; T007 remains a completed historical checkpoint, not current source/package coherence.
- [X] T008 [US2] Update managed path inclusion patterns and current install, feedback, maintainer, architecture, adoption, merge-bounded flow-back, and agent Python environment guidance to approved FarmBoy names in `.worktreeinclude`, `README.md`, `AGENTS.md`, `docs/installation.md`, `docs/architecture.md`, `docs/feedback.md`, `docs/consumer-adoption.md`, `docs/merge-bounded-flow-back.md`, `docs/agent-python-environment.md`, and `extensions/farmboy-feedback-maintainer/README.md` using identity, path, and link substitutions only; scan current owned documentation for unresolved active names, retaining actual repository URLs, independent extension IDs, and historical provenance where justified. Preserve governance and adoption behavior; do not amend the constitution in this task. Evidence: current owned-source scan found only intentional independent FlowKit Roadmap branding/data path terms and the test's old-key negative assertion; no obsolete owned invocation ID remains.
- [X] T009 [US2] Update existing catalog/agent-delivery expectations and feedback capture/report/intake regression expectations for renamed IDs, generated skills, commands, and paths in `tests/test_catalog.py`, `tests/test_agent_delivery.py`, `extensions/farmboy-feedback/tests/test_workflow_feedback.py`, and `extensions/farmboy-feedback-maintainer/tests/test_workflow_feedback_intake.py`. Evidence: catalog 28, agent delivery 22, and feedback suites 5 and 8 tests pass.

**Checkpoint**: The completed T007 catalog output is historical checkpoint evidence. T012 regenerated and verified the current coherent package snapshot; maintainer intake remains separate and existing management options and ownership rules are unchanged.

## Phase 5: User Story 3 — Preserve the Workbench Contract (Priority: P2)

**Goal**: Preserve workflow purpose, step IDs, routes, bounded loops, human gates, exact roles, manual fallback, evidence semantics, and nested delegation behavior through the rename.

**Independent Test**: Run existing controller, parser, graph, path, configuration, feedback, and lifecycle checks, including the 23-case workflow-owned roadmap boundary suite; compare workflow definitions against the reviewed Feature 022 correction after normalizing only approved identity/path replacements and the delegation-container spelling; rebuild and verify package pins before checking `farmboy` metadata round-trip and no old-key child dispatch in a fresh disposable consumer.

### Implementation for User Story 3

- [X] T010 [US3] Update controller, workflow, and agent regression coverage for `farmboy` delegation parsing, unchanged nested fields, and no old-key child dispatch in `tests/test_controller.py`, `tests/test_agent_configs.py`, `tests/test_implement_task_revision.py`, `tests/test_implementation_progress.py`, `tests/test_implementation_scope.py`, `tests/test_phase_lifecycle.py`, `tests/test_readiness.py`, `tests/test_readiness_workflow_routes.py`, `tests/test_workflow_graph.py`, `tests/test_workflow_improvements.py`, `tests/test_workflow_paths.py`, `tests/implementation_scope_snapshot.py`, and `tests/test_command_skill_ownership.py`; update fixtures `tests/consumer-fixtures/controller-workflow.yml`, `tests/consumer-fixtures/semantic-review-topology.json`, and `tests/consumer-fixtures/workflow-improvements/phase-lifecycle-cases.json`. Update `workflows/README.md` to document only the `farmboy` grammar while retaining independent `flow-wiki` IDs and ownership assertions. Cover the reviewed Feature 022 local milestone policy in `controllers/farmboy/scripts/python/milestone_policy.py`, the phase adapter's source guards and generic roadmap readback, authoring proof, and receipts; update the existing 23-case `tests/test_workflow_roadmap_boundary.py` module to verify all three phase graphs against generic roadmap 0.4.0 without requiring an extension-owned lifecycle helper or test matrix. **Evidence**: Full source suite passed all 358 tests; structural validation covered eleven workflow definitions with zero unexplained terminal paths.
- [X] T011 [US3] Update `tests/test_snapshot_validation.py` and `tests/test_bundle_lifecycle.py` to verify FarmBoy fresh installation, refresh, removal, feedback delivery, separate maintainer-intake installation, and ownership preservation. Diagnose native Specify CLI prompt-dispatch failures in the existing test harness. Apply the operator-approved mechanical correction by binding the existing `integration` input to all 109 previously unbound prompt nodes across the nine affected active workflow definitions; preserve Clarify 0.5.1 and its already-approved bindings. Do not change assertions, external Spec Kit, step IDs, roles, gates, routing, question caps, validator policy or add an adapter/framework. T012 performs the package-backed run after regeneration. **Evidence**: Exhaustive recursive inventory confirms all 113 active prompt nodes now bind the existing integration input; package-backed lifecycle passed four tests, including six native CLI workflow runs in the no-op Codex fixture.
- [X] T012 [US3] After T010/T011, regenerate `catalog/release.json` and `catalog/packages/` with the existing builder, then verify generated pins, versions and digests match current composition (bundle 0.18.3; Clarify 0.5.1; Analyze/Remediate 0.6.1; Close Out 0.9.2 and Implement 0.9.1; Converge, Plan and Tasks 0.5.1; Select Feature and Wiki Lint Update 0.2.1; Specify 0.4.1; controllers 0.9.1; independent roadmap 0.4.0); run the quickstart regression suites and structural validator, then perform fresh disposable-consumer checks with the pinned Specify CLI for FarmBoy metadata round-trip and native prompt dispatch on all lifecycle-exercised workflows. Record actual source/package coordinates, digests, CLI, results and skips in quickstart; distinguish T007 checkpoint evidence from current coherent packages. Use only regenerated packages. **Evidence**: Snapshot and package-backed lifecycle validation passed as recorded above. The final documentation/path consistency recheck is recorded in [quickstart.md](quickstart.md); the closeout re-debrief remains a parent workflow gate. T007 remains historical evidence only.

### Approved Closeout Correction Scope

The operator explicitly approved the bounded corrections identified by the Feature 021 Close Out review. Only T002, T003, T006, T008, T010, and T012 were reopened; their IDs and descriptions, all other task markers, and the historical evidence above remain intact. This reconciliation records correction scope and validation obligations; the historical 358-test result does not validate the corrections, so T012 must record fresh meaningful results.

| Finding | Existing task mapping | Correction and validation obligation |
| --- | --- | --- |
| CR021-001 | T002, T006, T008, T010, T012 | Route newly generated summaries, implementation history, and lifecycle witness references to `.specify/farmboy-controllers/`; align current source guards, protocol, documentation, and tests. Validate fresh disposable creation under the new root, milestone witness/readback, preservation of existing `.specify/flow-controllers/` history, and history-preserving removal. Rebuild the source-backed catalog and verify package metadata and digests. |
| CR021-002 | T008 | Restore the two architecture links to the existing `specs/017-flowkit-agent-configuration/contracts/agent-package.md` and `agent-delivery-cli.md`, retaining FarmBoy labels. Check both relative links resolve while the current agent manifest link remains valid. |
| CR021-003 | T003, T012 | Correct the Close Out exact-target example to the existing `specs/014-flowkit-workflow-improvements` directory, preserving the historical directory. Rebuild the affected workflow package and verify its catalog digest and the example target. |

Fresh implementation evidence for the reopened tasks is recorded below. T012's validation, independent review and fresh convergence are complete; the portable results are recorded in [closeout-corrections.md](validation/closeout-corrections.md).

| Task | Fresh evidence |
| --- | --- |
| T002 | `test_controller.py` and `test_phase_lifecycle.py` verify new summaries, implementation history, and lifecycle witnesses use `.specify/farmboy-controllers/`; tests preserve old completed history separately. |
| T003 | `test_workflow_paths.py` verifies the Close Out example resolves to the preserved Feature 014 directory; Close Out is version 0.9.2 with catalog digest `0237073c7d53a5d87390d410d2aacbb4d57f4cbddb267e9ffeb353adba0743d1`. |
| T006 | FarmBoy controller package 0.9.1 rebuilt with digest `a7c63afd41625b0144f704d1799f76d0f9f91f36d7c909f422766ccbe2001e0e`; catalog and bundle lifecycle tests preserve both prior and current history roots after removal. |
| T008 | The three current relative links in `docs/architecture.md` resolve; both Feature 017 links point to the unchanged historical contract directory. |
| T010 | Controller (63), phase lifecycle (30), workflow-owned roadmap boundary (23), workflow paths (29), and catalog (28) regression tests pass under the documented source inputs. |
| T012 | Bundle 0.18.3 catalog rebuilt; complete source suite passed 358 tests with no skips; both feedback suites passed (5 and 8); structural validation passed for eleven workflow definitions with zero unexplained terminal paths. Independent review passed 123 focused tests, and fresh convergence found no remaining implementation gaps across all 25 requirements and 12 task obligations. |

T012 must also run the relevant fresh regression and structural checks after T002/T003/T006/T008/T010 are corrected, record actual package versions and digests, and obtain independent review plus fresh convergence evidence. The reopened tasks cover only these approved corrections and their dependent validation; they do not authorize unrelated rename work or a roadmap write.

**Checkpoint**: Existing workflow contracts, delegation parsing, feedback behavior, and consumer lifecycle pass under the new names, and validation claims match observed evidence.

## Dependencies and Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No setup work is required.
- **Foundational Gate (Phase 2)**: T001 must be complete before any rename task begins. It confirms a separately approved constitutional amendment; task generation does not grant that approval.
- **User Story 1 (Phase 3)**: T002–T005 can proceed in parallel after T001 because they own distinct roots: controller, workflows, agents, and renderer/feedback extensions.
- **User Story 2 (Phase 4)**: T006–T008 follow the source renames; T007 follows T002–T006 so the updated validator and all renamed sources are included; T009 follows T005–T007. T008 can proceed independently of catalog generation after canonical mappings are settled.
- **User Story 3 (Phase 5)**: T010 follows T002–T005 and owns controller, policy, grammar, and workflow-boundary coverage. T011 follows source identity changes in T005–T007 and owns snapshot/lifecycle tests plus the existing dispatch-failure investigation; its regression files are disjoint from T010. T012 follows T010/T011 and performs final catalog regeneration before full validation and fresh-consumer checks.

### User Story Dependencies

- **User Story 1 (P1)**: Begins after T001 and establishes canonical source identities.
- **User Story 2 (P1)**: Depends on the source identities from User Story 1; catalog generation depends on source and metadata updates.
- **User Story 3 (P2)**: Depends on the renamed source/package surfaces so the existing behavioral contract can be validated end to end.

### Parallel Opportunities

- T002, T003, T004, and T005 are parallelizable after the constitutional gate because they own distinct source roots.
- T006 and T008 may proceed in parallel once canonical mappings are settled; T007 follows T006, while T009 follows T005–T007.
- T010 and T011 can proceed in parallel after renamed source identities are ready because they own disjoint regression files; T012 waits for both, regenerates current packages, and only then runs final package-backed validation.

Examples: For User Story 1, work on T002, T003, T004, and T005 in parallel after T001. For User Story 2, work on T006 and T008 in parallel after the canonical mappings are settled, then complete T007/T009 as their dependencies allow. For User Story 3, work on T010 and T011 in parallel after the renamed source identities are ready, then run T012 after both finish.

## Implementation Strategy

1. Stop before rename work until T001 confirms the separately approved constitutional amendment.
2. Rename the controller, workflow, agent, renderer, and owned feedback source roots in User Story 1; use `farmboy` in workflow delegation metadata and every owned parser while preserving nested field semantics.
3. Reconcile catalog source mappings/pins, generated package outputs, managed paths, current documentation, and feedback/package expectations in User Story 2. Keep maintainer intake separately packaged.
4. Complete local parser, policy, and workflow-boundary regression work in T010; complete snapshot/lifecycle assertions, the operator-approved two-node Clarify prompt-binding fix, and the approved mechanical batch of 109 remaining unbound prompt nodes in T011.
5. Regenerate final catalog packages after all source changes, then run the complete validation matrix and pinned-CLI fresh-consumer round-trip in T012. The approved integration-binding batch covers every active prompt node that lacked an explicit binding at the exhaustive recursive audit.
6. Report source coordinates and validation limits. Do not add migration, alias, journal, recovery, or consumer-conversion behavior.

## Notes

- `[P]` marks tasks in distinct source roots with no dependency on unfinished tasks.
- Each story's independent test criteria describe implementation-time verification; they do not imply that tests have already run.
- Retain independent `flow-roadmap` and `flow-wiki`, core Spec Kit commands, neutral feedback function/data names, unrelated schema fields, actual source coordinates, and historical evidence. Owned feedback command identities and the `flow_kit` container key change as specified; no old-key fallback is added.
- No migration feature, compatibility alias, migration test matrix, new model, service, API, framework, or dependency is part of this task list.

## Additional Closeout Consistency Corrections

The standing operator approval for T002/T008/T012 also covers the residual findings DOC021-004, DOC021-005 and NAME021-006 from the fresh debrief. These three tasks are complete after the focused current consistency checks documented in [quickstart.md](quickstart.md). README pins match the current bundle, controller and Close Out versions; the deprecated launcher directory now follows the canonical mapping with both file contents preserved and remains excluded from the unchanged controller archive; the final Quickstart paragraph records the completed independent review and convergence while retaining validation limits. Requirements and runtime behavior remain unchanged, so no package rebuild or version bump was needed. A fresh closeout re-debrief remains the parent workflow's gate.

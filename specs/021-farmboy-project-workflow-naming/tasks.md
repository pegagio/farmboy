---
description: "Dependency-ordered tasks for the FarmBoy pure naming cutover"
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
- [X] T007 [US2] Regenerate catalog release metadata and package archives from renamed sources using the existing builder, updating `catalog/release.json` and `catalog/packages/` with actual compatible source versions and digests without hand-editing generated archives. Evidence: `build_development_snapshot` generated FarmBoy 0.18.0 metadata/packages with bundle version and archive digests recorded in quickstart; flow-roadmap 0.3.0 source provenance is explicitly dirty and unpublished.
- [X] T008 [US2] Update managed path inclusion patterns and current install, feedback, maintainer, architecture, adoption, merge-bounded flow-back, and agent Python environment guidance to approved FarmBoy names in `.worktreeinclude`, `README.md`, `AGENTS.md`, `docs/installation.md`, `docs/architecture.md`, `docs/feedback.md`, `docs/consumer-adoption.md`, `docs/merge-bounded-flow-back.md`, `docs/agent-python-environment.md`, and `extensions/farmboy-feedback-maintainer/README.md` using identity, path, and link substitutions only; scan current owned documentation for unresolved active names, retaining actual repository URLs, independent extension IDs, and historical provenance where justified. Preserve governance and adoption behavior; do not amend the constitution in this task. Evidence: current owned-source scan found only intentional independent FlowKit Roadmap branding/data path terms and the test's old-key negative assertion; no obsolete owned invocation ID remains.
- [X] T009 [US2] Update existing catalog/agent-delivery expectations and feedback capture/report/intake regression expectations for renamed IDs, generated skills, commands, and paths in `tests/test_catalog.py`, `tests/test_agent_delivery.py`, `extensions/farmboy-feedback/tests/test_workflow_feedback.py`, and `extensions/farmboy-feedback-maintainer/tests/test_workflow_feedback_intake.py`. Evidence: catalog 28, agent delivery 22, and feedback suites 5 and 8 tests pass.

**Checkpoint**: Catalog packages and current guidance present a consistent FarmBoy cutover; maintainer intake remains separate and existing management options and ownership rules are unchanged.

## Phase 5: User Story 3 — Preserve the Workbench Contract (Priority: P2)

**Goal**: Preserve workflow purpose, step IDs, routes, bounded loops, human gates, exact roles, manual fallback, evidence semantics, and nested delegation behavior through the rename.

**Independent Test**: Run existing controller, parser, graph, path, configuration, feedback, and lifecycle checks; compare workflow definitions after normalizing only approved identity/path replacements and the delegation-container spelling; verify `farmboy` metadata round-trips through the pinned Specify CLI in a fresh disposable consumer and old-key metadata does not dispatch a child.

### Implementation for User Story 3

- [ ] T010 [US3] Update existing controller, workflow, and agent tests and fixtures to cover `farmboy` delegation parsing, unchanged nested fields, and no old-key child dispatch in `tests/test_controller.py`, `tests/test_agent_configs.py`, `tests/test_implement_task_revision.py`, `tests/test_implementation_progress.py`, `tests/test_implementation_scope.py`, `tests/test_phase_lifecycle.py`, `tests/test_readiness.py`, `tests/test_readiness_workflow_routes.py`, `tests/test_workflow_graph.py`, `tests/test_workflow_improvements.py`, `tests/test_workflow_paths.py`, `tests/implementation_scope_snapshot.py`, `tests/test_command_skill_ownership.py`, `tests/consumer-fixtures/controller-workflow.yml`, `tests/consumer-fixtures/semantic-review-topology.json`, and `tests/consumer-fixtures/workflow-improvements/phase-lifecycle-cases.json`; update grammar documentation in `workflows/README.md` to show only the new key, and update owned controller source/installed-helper paths and branded internal module names in `tests/test_command_skill_ownership.py` while retaining independent `flow-wiki` command and skill identifiers and existing ownership assertions.
- [ ] T011 [US3] Update existing snapshot and lifecycle assertions to verify renamed fresh installation, refresh, removal, feedback delivery, separately installed maintainer intake, and ownership preservation in `tests/test_snapshot_validation.py` and `tests/test_bundle_lifecycle.py`.
- [ ] T012 [US3] Run every existing suite listed in the validation matrix in `specs/021-farmboy-project-workflow-naming/quickstart.md`, including command-skill ownership, implementation/phase/readiness, snapshot/lifecycle, and both feedback-extension suites; run the structural validator and then perform the fresh disposable-consumer check with the pinned Specify CLI to verify `farmboy` metadata round-trips and old-key metadata does not dispatch. Record actual source/package versions, digests, CLI, observed results, and skips using `specs/021-farmboy-project-workflow-naming/quickstart.md`.

**Checkpoint**: Existing workflow contracts, delegation parsing, feedback behavior, and consumer lifecycle pass under the new names, and validation claims match observed evidence.

## Dependencies and Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No setup work is required.
- **Foundational Gate (Phase 2)**: T001 must be complete before any rename task begins. It confirms a separately approved constitutional amendment; task generation does not grant that approval.
- **User Story 1 (Phase 3)**: T002–T005 can proceed in parallel after T001 because they own distinct roots: controller, workflows, agents, and renderer/feedback extensions.
- **User Story 2 (Phase 4)**: T006–T008 follow the source renames; T007 follows T002–T006 so the updated validator and all renamed sources are included; T009 follows T005–T007. T008 can proceed independently of catalog generation after canonical mappings are settled.
- **User Story 3 (Phase 5)**: T010 follows T002–T005; T011 follows T005–T007. T010 and T011 use disjoint test files and can proceed in parallel. T012 depends on T002–T011.

### User Story Dependencies

- **User Story 1 (P1)**: Begins after T001 and establishes canonical source identities.
- **User Story 2 (P1)**: Depends on the source identities from User Story 1; catalog generation depends on source and metadata updates.
- **User Story 3 (P2)**: Depends on the renamed source/package surfaces so the existing behavioral contract can be validated end to end.

### Parallel Opportunities

- T002, T003, T004, and T005 are parallelizable after the constitutional gate because they own distinct source roots.
- T006 and T008 may proceed in parallel once canonical mappings are settled; T007 follows T006, while T009 follows T005–T007.
- T010 and T011 are parallelizable after renamed sources and packages are ready because they own disjoint regression files; T012 follows both.

## Implementation Strategy

1. Stop before rename work until T001 confirms the separately approved constitutional amendment.
2. Rename the controller, workflow, agent, renderer, and owned feedback source roots in User Story 1; use `farmboy` in workflow delegation metadata and every owned parser while preserving nested field semantics.
3. Reconcile catalog source mappings/pins, generated package outputs, managed paths, current documentation, and feedback/package expectations in User Story 2. Keep maintainer intake separately packaged.
4. Validate delegation parsing, the pinned-CLI fresh-consumer round-trip, feedback capture/report/intake, and the preserved workbench contract in User Story 3.
5. Report source coordinates and validation limits. Do not add migration, alias, journal, recovery, or consumer-conversion behavior.

## Notes

- `[P]` marks tasks in distinct source roots with no dependency on unfinished tasks.
- Each story's independent test criteria describe implementation-time verification; they do not imply that tests have already run.
- Retain independent `flow-roadmap` and `flow-wiki`, core Spec Kit commands, neutral feedback function/data names, unrelated schema fields, actual source coordinates, and historical evidence. Owned feedback command identities and the `flow_kit` container key change as specified; no old-key fallback is added.
- No migration feature, compatibility alias, migration test matrix, new model, service, API, framework, or dependency is part of this task list.

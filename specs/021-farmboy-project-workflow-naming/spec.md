# Feature Specification: FarmBoy Project and Workflow Naming

**Feature Branch**: `farmboy`
**Created**: 2026-10-09
**Status**: Draft
**Input**: Rename Spec Kit Flow / FlowKit to FarmBoy. Use “Spec et Labora”, `farmboy` for the project/bundle, `farmboy-<purpose>` for skills/workflows, and `FarmBoy <role>` for project-owned agents. The operator clarified on 2026-10-10 that this is a pure cutover: no migration feature or backward compatibility. The operator also explicitly includes project-owned feedback extensions and the `flow_kit` parser/key rename.

FarmBoy is the new identity of the existing agent-driven workbench structured by Spec Kit. This feature changes names and references, not capabilities, architecture or consumer-management behavior. Building the future code factory is separate work.

## Table of Contents

- [Clarifications](#clarifications)
- [User Scenarios and Testing](#user-scenarios-and-testing)
- [Requirements](#requirements)
- [Success Criteria](#success-criteria)
- [Assumptions](#assumptions)
- [Authority and Dependencies](#authority-and-dependencies)

## Clarifications

Direct operator decisions govern the current scope; earlier migration-oriented design is superseded.

### Session 2026-10-10

- Q: What should happen to a paused workflow that was started under the old names when its consumer migrates to FarmBoy? → A: The operator controls the situation and ensures there are no paused old-name runs. Checkpoint transfer/resumption is out of scope.
- **Owned scope addition**: Rename both project-owned feedback extensions and their existing command/skill identities, and replace the `flow_kit` delegation metadata key and this project's parsers with `farmboy`. Nested fields and behavior stay unchanged; no old-key adapter is added.
- **Scope correction**: The operator requires a pure rename cutover, with no migration feature. This supersedes earlier consumer-migration requirements and planning; the paused-run answer introduces no guard or recovery behavior.

## User Scenarios and Testing

The scenarios cover using the new identity and maintaining the existing behavior.

### User Story 1 — Discover and Invoke FarmBoy (Priority: P1)

As an operator, I want consistent FarmBoy names so I can find and invoke the same existing workflow purposes.

**Independent test**: Inspect a fresh supported installation and confirm all ten workflows and their assigned agents use the approved names.

**Acceptance scenarios**:
1. Product guidance identifies FarmBoy and “Spec et Labora”, and the bundle identity is `farmboy`.
2. Each `farmboy-<purpose>` skill/workflow resolves to its existing purpose and exact `FarmBoy <role>` assignments.
3. Old project-owned invocation names are not aliases for FarmBoy.

### User Story 2 — Maintain a Consistent Cutover (Priority: P1)

As a maintainer, I want names, paths, manifests, documentation and tests to agree after the cutover without adding another product feature.

**Independent test**: Inspect the naming mappings and built packages, then run existing installation/lifecycle tests with renamed expectations.

**Acceptance scenarios**:
1. Owned identifiers, source directories, helper references, package metadata, current documentation and test fixtures use the approved mappings.
2. Existing management commands retain their behavior and options under the new identities.
3. No migration command, migration record, compatibility adapter or new recovery behavior is introduced.
4. Existing installations are outside this feature's upgrade/support scope; any operator replacement is handled separately.

### User Story 3 — Preserve the Workbench Contract (Priority: P2)

As an operator, I want the renamed tools to behave as before.

**Independent test**: Compare workflow definitions after normalizing approved identity/path replacements, and run the existing graph, controller and lifecycle checks.

**Acceptance scenarios**:
1. The ten active purposes, step IDs, core commands, gates, routes, loop limits and role responsibilities remain unchanged.
2. Deprecated Start Feature remains stop-only and outside active delivery; planning and tasking remain separate.
3. Manual fallback, exact named dispatch and focused human decisions remain available.
4. Independent command/extension IDs, actual source coordinates, historical feature meaning and existing evidence remain intact.

### Edge Cases

These cases bound replacement rather than add new runtime behavior.

- Old text in an independent extension ID, unrelated grammar, actual URL or historical record is retained for its existing meaning.
- A mismatched active skill/workflow/agent reference is a rename defect, not permission to add a fallback alias.
- Existing customized installations, old records and checkpoints are not translated by this feature.
- No paused old-name runs need handling; the operator controls that condition.
- The separately approved constitutional identity amendment is in Constitution 8.0.0; implementation must verify that prerequisite and still needs its own operator invocation.

## Requirements

The requirements define the rename while preserving existing contracts. Stable FR identifiers are retained from the earlier draft; consumer-migration requirements are superseded by the pure-cutover decision.

### Functional Requirements

- **FR-001**: Branding MUST use FarmBoy, “Spec et Labora” and canonical project/bundle identity `farmboy`. External repository renaming and publication remain separately authorized.
- **FR-002**: Controller skills/workflows MUST use `farmboy-<purpose>`. Purposes remain `select-feature`, `specify`, `clarify`, `plan`, `tasks`, `analyze-remediate`, `implement`, `converge`, `closeout` and `wiki-lint-update`.
- **FR-003**: Project-owned agents MUST use `FarmBoy <role>` with unchanged responsibilities, settings and exact assignment semantics.
- **FR-004**: Reviewed name mappings MUST cover owned source paths, skills including the renderer, workflows, agents, both feedback extensions, delegation metadata and its parsers, manifests, helper references, current docs and tests. Retained independent identities, unrelated grammar and historical references MUST be distinguished from active naming defects.
- **FR-005**: Active references among renamed owned components MUST resolve consistently, with no unexplained old project-owned invocation names.
- **FR-006**: FarmBoy MUST provide no old-name invocation aliases or backward-compatibility layer for this cutover.
- **FR-007**: Migration of existing installations MUST be outside scope. This feature MUST add no migration command, legacy conversion reader or upgrade procedure between identities.
- **FR-008**: Existing installation, refresh, removal and consumer-ownership behavior MUST remain unchanged apart from identity/path values. No new consumer discovery, customization transfer or recovery mechanism is required.
- **FR-009**: Current installation and usage documentation MUST name FarmBoy and the existing management commands correctly. No new command or option is introduced by the rename.
- **FR-010**: The ten workflows remain independently reviewable; deprecated Start Feature remains stop-only and excluded from active delivery; planning and task generation remain separate.
- **FR-011**: Manual fallback and installed-workflow authority MUST remain unchanged; thin skills MUST NOT duplicate workflow policy.
- **FR-012**: Operator scope, bounded correction, same-child answer relay, consequential gates, separate phases and lifecycle/evidence semantics MUST remain unchanged. The rename grants no acceptance or Git authority.
- **FR-013**: Core Spec Kit commands and independent `flow-roadmap` / `flow-wiki` identities MUST remain unchanged. Owned `flow-feedback` and `speckit-flow-feedback-maintainer` extensions, their existing command/skill identifiers and source references MUST use FarmBoy names. The existing delegation container key MUST change from `flow_kit` to `farmboy` in owned workflows, parsers and validators, with unchanged nested fields and dispatch semantics and no legacy-key fallback. Generic component ownership and The Diagram's consumer boundary remain unchanged.
- **FR-014**: Merged feature history and existing evidence MUST retain meaning and attribution; historical names are not active naming defects.
- **FR-015**: The constitutional identity amendment MUST receive separate explicit approval before rename implementation. This specification does not amend the constitution.
- **FR-016**: Validation MUST focus on naming/reference consistency, coherent packages, fresh installation and existing workflow/controller/lifecycle regressions. No legacy migration matrix or migration-specific failure/retry tests are required.
- **FR-017**: Validation records MUST identify actual source/package versions, digests, CLI and observed results, preserving distinctions between static checks, dispatch, live behavior, release and acceptance.
- **FR-018**: This feature MUST NOT implement the future factory, migration/compatibility tooling, checkpoint transfer, new command capabilities, unrelated schemas or recovery behavior, unrelated workflow changes, external renames/publication or Git integration.

### Key Entities

No new domain model or persistence is introduced. Existing bundle/workflow/agent identities and references receive approved new values; existing installation and evidence formats retain their semantics. The delegation container key receives the approved spelling change to `farmboy`; its `delegated` and `agent` fields retain their types and meaning. Feedback journal/report data and historical evidence are not migrated.

## Success Criteria

These criteria assess the rename without adding consumer-upgrade functionality.

- **SC-001**: All ten purposes and nine existing roles resolve under the approved FarmBoy names in a fresh supported installation; no old invocation alias dispatches them.
- **SC-002**: Reviewed current owned surfaces have consistent mappings and zero unresolved active naming references; every retained old occurrence has an existing independent, unrelated grammar or historical reason; active owned parser metadata uses only `farmboy`.
- **SC-003**: Existing regression tests pass with renamed expectations, including existing ownership and removal protections; workflow definitions differ only by approved identity/path substitutions.
- **SC-004**: The cutover introduces zero new command capabilities/options, migration records/readers, compatibility adapters or recovery mechanisms.
- **SC-005**: All ten workflow purposes and decision boundaries remain unchanged; deprecated Start Feature has zero active bindings and remains stop-only.
- **SC-006**: Independent identities, actual coordinates and historical/evidence meaning remain intact.
- **SC-007**: Every validation claim is supported by its observed scope and provenance; no static result is presented as live execution or publication.

## Assumptions

The operator accepts a breaking name change and controls replacement of existing personal installations separately.

- There is no requirement to support upgrading an old-name installation to FarmBoy.
- There are no paused old-name runs to transfer; no guard or refusal check is added.
- Clear natural-language action labels may accompany canonical prefixed identifiers.
- Existing architectures, dependencies and management mechanisms are reused; only approved identity/path values and the delegation-container key spelling change.
- The selected feature directory and active identity remain unchanged.

## Authority and Dependencies

Direct operator approval settles the name, tagline and canonical naming scheme. The 2026-10-10 pure-cutover instruction supersedes consumer-migration design and requirements. Earlier brief/planning review artifacts describe the superseded scope and are not current verification of these revised artifacts.

[Feature 021](../../.specify/memory/roadmap.md#021--farmboy-project-and-workflow-naming--status-planned) retains verified prerequisites 011, 013, 014 and 017. [Constitution 8.0.0](../../.specify/memory/constitution.md), explicitly approved and applied by the operator on 2026-10-10, establishes the approved FarmBoy identities, including both owned feedback extensions and the `farmboy` delegation key. This satisfies the separate approval requirement in FR-015; implementation must verify the amendment and requires its own operator invocation. Existing reviewed source and installations remain operative during the constitution's bounded cutover transition.

The earlier planning-only exception authorized research/design under Constitution 7.0.0 and remains historical phase authority; it did not authorize tasks, implementation or a constitutional edit. The subsequent explicit Tasks invocation separately authorized task drafting, and its assigned independent reviewer completed task-quality review. That evidence does not establish a fresh standalone Plan review of the pure-cutover design. Current analysis/remediation reconciles mutable artifacts without granting implementation or acceptance.

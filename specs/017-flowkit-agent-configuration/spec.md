# Feature Specification: FlowKit Agent Configuration and Consumer Delivery

**Feature Directory**: `specs/017-flowkit-agent-configuration/`

**Created**: 2026-10-03

**Status**: Draft — configuration and delivery decisions unresolved

**Input**: Prefix the eight project-defined agents with `FlowKit-`, review their role instructions, select explicit suitable models and reasoning efforts, and decide a supported delivery path for consuming projects. The approved Feature 017 roadmap entry and its Open Questions define the scope.

This feature changes the reusable agent contract prospectively. It preserves reviewed delegated assignments, human authority, and independent review while making identities, configuration choices, and consumer lifecycle behavior inspectable. It does not authorize implementation before consequential decisions are settled.

## Table of Contents

- [User Scenarios & Testing](#user-scenarios--testing)
- [Requirements](#requirements)
- [Success Criteria](#success-criteria)
- [Assumptions](#assumptions)
- [Scope and Governing Context](#scope-and-governing-context)
- [Decisions Required Before Readiness](#decisions-required-before-readiness)

## User Scenarios & Testing

The journeys below describe distinct outcomes for maintainers and consumer operators. Testing a single journey establishes that outcome without establishing completion of the entire feature.

### User Story 1 - Recognize the Exact FlowKit Role (Priority: P1)

A workflow maintainer and consumer operator can distinguish FlowKit agents from other project agents. Each delegated step uses the exact prefixed name for its existing responsibility, with consistent discovery and validation across supported paths.

**Why this priority**: An inconsistent name prevents exact dispatch and can select the wrong configuration.

**Independent Test**: Compare all eight configured identities with every delegated assignment in the ten active workflows and with current controller, discovery, validation, documentation, and filename references. Demonstrate bounded exact named dispatch separately from configuration checks.

**Acceptance Scenarios**:

1. **Given** the eight reviewed roles, **when** their prospective identities are reconciled, **then** the exact names are FlowKit-Roadmap Agent, FlowKit-Specifier, FlowKit-Planner, FlowKit-Tasker, FlowKit-Reviewer, FlowKit-Coder, FlowKit-Code Reviewer, and FlowKit-Wiki Curator.
2. **Given** a delegated step on any branch, **when** its assignment is checked, **then** its exact prefixed name matches the intended reviewed configuration without unprefixed fallback or reassignment of responsibilities.
3. **Given** an absent, malformed, or unavailable prefixed agent, **when** the supported workflow checks or requests it, **then** it identifies the affected name and cause and stops according to the existing declared path without substituting another agent.
4. **Given** a main-task step or human gate, **when** names are renamed, **then** it remains in the main task and no new delegation is introduced.

### User Story 2 - Inspect Reviewed Instructions and Model Choices (Priority: P1)

A maintainer can inspect each role's scope and explicit model/effort choice, understand why it suits that responsibility, and distinguish requested settings from observed settings in a live child.

**Why this priority**: Explicit settings alone do not establish suitable responsibilities or effective runtime configuration.

**Independent Test**: Review the eight-role decision record against approved responsibilities, then compare each configuration with approved values and supported-client evidence. Record unavailable evidence separately.

**Acceptance Scenarios**:

1. **Given** any role, **when** its instruction review is completed, **then** the record states allowed work, prohibited scope expansion, expected outputs, question/blocker handling, and its explicit model/effort choice with suitability rationale.
2. **Given** an author and independent reviewer, **when** their instructions are assessed, **then** author self-checks remain required and do not substitute for assessment by a different assigned reviewer.
3. **Given** approved settings, **when** the configuration is inspected, **then** both values are explicit rather than omitted or implicitly inherited, with field support and value availability attributable to the tested client.
4. **Given** successful live exact named dispatch, **when** effective model or effort cannot be observed, **then** those settings are reported as unverified rather than inferred from configuration contents or a child label.
5. **Given** an unsupported field or unavailable value, **when** checked or exercised, **then** the affected role, requested setting, observed failure, and operator resolution are reported without silently selecting another setting.

### User Story 3 - Acquire and Maintain Agents Safely (Priority: P2)

A consumer operator can obtain reviewed configurations through a supported delivery path and predict what installation, refresh, migration, and removal will change in their project.

**Why this priority**: Delivery must make ownership and preservation of existing configurations and customizations clear.

**Independent Test**: Exercise the approved lifecycle procedure in disposable initialized consumers with an empty inventory, unprefixed roles, prefixed collisions, local edits, unrelated agents, and partial operations. Confirm the documented disposition of each affected file.

**Acceptance Scenarios**:

1. **Given** an initialized consumer without FlowKit agents, **when** the selected delivery procedure is followed, **then** the operator can obtain all eight configurations, identify their source and ownership, and inspect the result before invoking a workflow.
2. **Given** existing unprefixed configurations, **when** the documented migration is followed, **then** assignments and identities agree and the report identifies retained, changed, or unresolved files; this feature's selection grants no overwrite or deletion authority.
3. **Given** a prefixed collision or consumer customization, **when** install or refresh encounters it, **then** the selected ownership/conflict policy preserves content that is not authorized to change and names an exact resolution action.
4. **Given** an update to reviewed source, **when** refresh is followed, **then** the operator can determine which files are eligible for change and which conflicts remain unresolved.
5. **Given** removal of the delivered capability, **when** its procedure is followed, **then** only files authorized by the approved ownership policy are affected, unrelated agents and consumer-owned content survive, and remaining dependencies on removed names are reported.
6. **Given** a partial or interrupted operation, **when** the result is inspected, **then** completed changes and unresolved conflicts are reported with bounded recovery; no broad overwrite or silent success is assumed.

### Edge Cases

These cases require inspectable outcomes under the selected design:
- **Mixed versions**: Installed assignments and delivered names disagree. Report the mismatch and coordinated migration action without concealing it through fallback dispatch.
- **Identity collision**: Filenames, configured names, and referenced names disagree, or two files claim one name. Identify competing definitions before claiming a usable inventory.
- **Edited or unrecorded files**: A matching name does not establish lifecycle ownership or permission to overwrite.
- **Unsupported settings**: The tested client rejects a field or cannot supply a requested model/effort. Preserve the failure and the required operator resolution.
- **Limited visibility**: Configuration, child labels, and no-op dispatch supply distinct evidence; live exact selection or effective settings may remain unverified.
- **Consumer customization**: Instructions or settings differ from reviewed source. Apply the selected policy and report resulting evidence limits.
- **Feature 016 coordination**: Its separate name-discovery and probe design must use current exact identities. This feature does not introduce centralized probing or change probe timing.

## Requirements

Requirements define intended outcomes. Pending decisions are blockers rather than authority to fill values or select mechanisms during implementation.

### Functional Requirements

- **FR-001**: The eight roles MUST use the exact `FlowKit-` identities in User Story 1. Extra roles, new responsibility assignments, and compatibility aliases are not approved by this description.
- **FR-002**: Current workflow references on all delegated branches, controller expectations, configuration filenames and discovery references, tests, and documentation MUST be reconciled with the approved identities. Verified artifacts MUST retain their historical meaning.
- **FR-003**: Every role MUST receive an inspectable instruction-quality review covering responsibility fit, permitted outputs and mutations, exclusions, question routing, blockers, evidence expectations, and unambiguous instructions. Material authority or scope changes MUST return to the operator for a decision.
- **FR-004**: Approved responsibilities MUST remain: Roadmap Agent prepares scoped evidence and applies only approved roadmap changes; Specifier authors or clarifies the selected spec; Planner authors selected planning artifacts; Tasker derives selected tasks; Reviewer independently assesses selected artifacts and alignment; Coder implements selected eligible tasks; Code Reviewer independently inspects implementation; Wiki Curator maintains authorized cited wiki knowledge. Each is the corresponding prefixed role after migration. [Named agents, S018/S020/S021](../../wiki/pages/agent-roles-and-inheritance.md)
- **FR-005**: Authors MUST complete command-required self-checks and quality checklists; independent reviewers MUST NOT assess their own work. Main-task questions and consequential gates MUST remain in the main task, which relays answers to the same child when continuation is needed. [Authority, S017/S020/S021](../../wiki/pages/project-authority-and-review-gates.md)
- **FR-006**: Each role MUST have an operator-approved explicit model/effort pair, a responsibility-based suitability rationale, and evidence that the chosen fields and values are supported by the tested Codex client. [NEEDS CLARIFICATION: What exact model and reasoning-effort pair should each of the eight roles use? No per-role values or common default have been approved.]
- **FR-007**: Reviewed exact named assignments MUST remain without a FlowKit role-to-model map, workflow assignment default, or per-run agent/model/effort override. Missing, invalid, and unavailable required assignments MUST retain the stop-without-fallback contract. [Named agents, S020](../../wiki/pages/agent-roles-and-inheritance.md)
- **FR-008**: A supported delivery contract MUST be selected before implementation, identifying reviewed reusable source, delivery entry point, ownership, install and refresh behavior, customization/conflict policy, migration, recovery, and removal. [NEEDS CLARIFICATION: Should delivery use consumer-owned copyable templates, managed agent files, or another mechanism, and what ownership/customization/migration/removal policy is approved for that choice?]
- **FR-009**: The delivery decision MUST reconcile the current boundary: agent files are consumer-owned, do not install from this checkout into other consumers, and are excluded from FlowKit install, refresh, and removal. Until an explicit replacement policy is approved, that boundary remains authoritative. A prefix or matching filename MUST NOT imply ownership or overwrite authority. [Lifecycle, S005/S016](../../wiki/pages/installation-and-release-lifecycle.md); [current installation contract](../../docs/installation.md)
- **FR-010**: The selected lifecycle contract MUST define clean and repeat installation, upgrades, missing or changed ownership evidence, existing prefixed and unprefixed definitions, local edits, partial operations, and removal. Unauthorized consumer overwrites/deletions MUST be prevented; conflicts MUST identify affected files and bounded resolution.
- **FR-011**: Delivery guidance MUST make reviewed names and values inspectable and describe acquisition, migration, customization, refresh, recovery, removal, and evidence limits. Manual-prompt fallback and separate workflow invocation MUST remain available. [Lifecycle, S005/S016](../../wiki/pages/installation-and-release-lifecycle.md); [Authority, S001](../../wiki/pages/project-authority-and-review-gates.md)
- **FR-012**: Validation MUST exercise the selected lifecycle design in disposable initialized consumers and record component IDs, versions, source coordinates/digests, tested Specify CLI and supported Codex client identity, scenario inputs, and observed results. Reports MUST use portable references without secrets, raw transcripts, or absolute host paths. [Authority, S001](../../wiki/pages/project-authority-and-review-gates.md); [Lifecycle, S016](../../wiki/pages/installation-and-release-lifecycle.md)
- **FR-013**: Evidence MUST separately state configuration presence/consistency, supported field/value validation, live exact named dispatch, and observed effective model/effort. Labels, static checks, and no-op dispatch MUST NOT be described as live selection or effective-setting proof. Unobservable settings MUST remain unverified without misclassifying successful dispatch itself as failed. [Named agents, S020/S021](../../wiki/pages/agent-roles-and-inheritance.md)
- **FR-014**: Validation MUST cover all eight names, all active delegated assignment references, and the listed lifecycle cases. Missing evidence MUST be explicit. Local success MUST NOT imply publication, stock Spec Kit compatibility, automatic adoption, Git integration, roadmap verification, or feature acceptance. [Lifecycle, S005/S016](../../wiki/pages/installation-and-release-lifecycle.md)
- **FR-015**: Feature 016 MUST remain independent and outside this feature. Coordination is limited to exact-name discovery and validation evidence; Feature 017 MUST NOT add centralized probing, remove existing probes, or change unrelated workflow control flow. [Roadmap entries 016/017](../../.specify/memory/roadmap.md)
- **FR-016**: Generic source and component authority MUST remain unchanged. The bundle composes reviewed components rather than owning a second behavioral source; The Diagram remains a separate consumer with adapter authority and runtime outside this feature. [Diagram boundary, S001/S003](../../wiki/pages/diagram-adapter-boundary.md)

### Key Entities

These describe reviewable information without choosing its storage or delivery mechanism:
- **Reviewed configuration**: Exact name, responsibilities/exclusions, explicit model/effort pair, and suitability rationale.
- **Configuration decision record**: Approval and support evidence for role choices, reusable source, delivery, ownership, customization, migration, and lifecycle effects.
- **Consumer delivery state**: Received source and provenance, ownership where applicable, local edits, conflicts, and completed/unresolved operations.
- **Validation evidence**: Tested identities and versions, source digests, observed configuration/dispatch/settings outcomes, and observation limits.

## Success Criteria

These measure coverage and operator predictability as acceptance targets for later work; authoring this draft does not achieve them.

### Measurable Outcomes

- **SC-001**: All eight roles and every active delegated assignment use approved prefixed identities; review reports zero unexplained current-reference mismatches or unauthorized responsibility changes.
- **SC-002**: Eight of eight roles have approved instruction reviews and explicit model/effort decisions with suitability/support evidence; zero choices rely on omitted settings.
- **SC-003**: A consumer operator can follow approved acquisition and lifecycle guidance for all eight roles, with an inspectable expected disposition for every file affected by install, refresh, migration, conflicts, or removal.
- **SC-004**: Every listed disposable-consumer lifecycle case has expected and observed results; zero unrelated or unauthorized-to-change consumer files are modified or removed.
- **SC-005**: Each role has distinct configuration, live exact-dispatch, and effective-setting results or explicit evidence gaps. No unverified setting is presented as effective and no static/no-op result as live proof.
- **SC-006**: Every validation record identifies tested component/client versions and source provenance; every completion report distinguishes local outcomes from publication, adoption, and acceptance.

## Assumptions

These preserve approved scope while decisions remain pending:
- **Supported consumer**: Codex remains the initial supported integration. Another runtime, framework, dependency, or build tool is outside scope.
- **Prerequisites**: Roadmap Features 011, 014, and 015 are verified. Feature 016 is independent and not a prerequisite.
- **Current source**: The eight local configs are role-review inputs and currently omit model/effort fields. Their presence establishes neither delivery nor effective settings.
- **Approval boundary**: Selection and authoring do not approve model values, managed ownership, overwrites, new lifecycle authority, implementation, or publication.

## Scope and Governing Context

The [Feature 017 roadmap entry and Open Questions](../../.specify/memory/roadmap.md) supply approved scope. C-02 through C-05 and [Constitution 6.0.0](../../.specify/memory/constitution.md) govern authority, component boundaries, reviewable source/manual fallback, and evidence.

Wiki coverage is **Partial**: existing pages establish reviewed roles, named assignments, ownership, installation lifecycle, human gates, and The Diagram boundary. They do not establish Feature 017's prefix, model/effort selections, or delivery decision. The approved roadmap supplies new scope; the decisions below remain unresolved.

Governing context is [Named agents](../../wiki/pages/agent-roles-and-inheritance.md) (S018, S020, S021), [Installation and release lifecycle](../../wiki/pages/installation-and-release-lifecycle.md) (S005, S016), [Project authority and review gates](../../wiki/pages/project-authority-and-review-gates.md) (S001, S017, S020, S021), and [Diagram adapter boundary](../../wiki/pages/diagram-adapter-boundary.md) (S001, S003). Existing configs corroborate the baseline without approving future values or ownership.

Excluded are unrelated control-flow changes, retrospective semantic edits to verified artifacts, implicit consumer ownership changes, another workflow phase, roadmap or active-pointer edits, Git integration, publication, automatic adoption, and lifecycle acceptance. Select Feature feedback does not expand this feature into approval-gate redesign.

## Decisions Required Before Readiness

Two consequential decisions remain. The draft and author self-check claim neither independent review nor readiness for planning or implementation.

1. **Model and reasoning effort**: Approve exact values for all eight roles, individually or through an explicitly approved common pair, with suitability and supported-client evidence. No values are selected here.
2. **Delivery and ownership**: Select copyable consumer-owned templates, managed files, or another supported path; identify reviewed reusable source and decide customization, conflicts, migration, refresh, recovery, and removal. Departures from the current consumer-owned lifecycle boundary require an explicit operator decision before source changes.

FR-012 through FR-014 define the evidence policy. Exact supported fields and observable evidence still need verification for the selected settings and delivery choice; missing verification must stay visible.

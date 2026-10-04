# Feature Specification: FlowKit Agent Configuration and Consumer Delivery

**Feature Directory**: `specs/017-flowkit-agent-configuration/`

**Created**: 2026-10-03

**Status**: Complete

**Input**: Prefix the eight project-defined agents with `FlowKit-`, review their role instructions, select explicit suitable models and reasoning efforts, and decide a supported delivery path for consuming projects. The approved Feature 017 roadmap entry and its Open Questions define the scope.

This feature changes the reusable agent contract prospectively. It preserves reviewed delegated assignments, human authority, and independent review while making identities, configuration choices, and consumer lifecycle behavior inspectable. It does not authorize implementation before consequential decisions are settled.

## Table of Contents

- [User Scenarios & Testing](#user-scenarios--testing)
- [Clarifications](#clarifications)
- [Requirements](#requirements)
- [Success Criteria](#success-criteria)
- [Assumptions](#assumptions)
- [Scope and Governing Context](#scope-and-governing-context)
- [Decisions Required Before Readiness](#decisions-required-before-readiness)
- [Operator-Directed Follow-up Disposition](#operator-directed-follow-up-disposition)

## Clarifications

Accepted answers define the intended contract without selecting command syntax or implementation details.

### Session 2026-10-03

- Q: How should consuming projects receive and maintain the eight FlowKit agent configurations? → A: Deliver consumer-owned copies with install-missing and explicit reset-one/reset-all operations. Ordinary refresh updates available defaults without overwriting copies. Reset reapplies the selected package's defaults and discards customizations only for targeted FlowKit agents. Preserve unrelated agents and leave renamed or retired files for operator removal. Do not add per-file ownership hashes, automatic customization detection, or merging.
- Q: Should the eight FlowKit roles use individually justified model and reasoning-effort defaults, or share one common pair? → A: Allow responsibility-based defaults for each role. Planning researches suitable supported pairs and presents all eight choices with support and suitability evidence for operator approval before implementation.

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

**Independent Test**: Exercise install-missing, ordinary refresh, reset-one, reset-all, and removal in disposable initialized consumers with an empty inventory, unprefixed roles, existing prefixed files, local edits, unrelated agents, and partial operations. Confirm the documented disposition of each affected file.

**Acceptance Scenarios**:

1. **Given** an initialized consumer without FlowKit agents, **when** install-missing is followed, **then** all eight defaults are copied as consumer-owned configurations with inspectable source provenance; any existing files are preserved.
2. **Given** existing unprefixed configurations, **when** the documented migration is followed, **then** assignments and identities agree and the report identifies retained, changed, or unresolved files; this feature's selection grants no overwrite or deletion authority.
3. **Given** an existing prefixed file or consumer customization, **when** install-missing or ordinary refresh runs, **then** the existing copy is preserved; an operator may explicitly reset that agent or all current FlowKit agents to the selected package's defaults, discarding customizations only in the chosen targets.
4. **Given** an update to reviewed source, **when** ordinary refresh is followed, **then** available defaults are updated without overwriting consumer copies, and reset-one/reset-all can reapply those defaults only when explicitly requested.
5. **Given** removal of the delivered capability or renamed/retired definitions, **when** its procedure is followed, **then** consumer-owned agent copies remain for operator removal, unrelated agents survive, and guidance identifies obsolete definitions and remaining dependencies on their names.
6. **Given** a partial or interrupted operation, **when** the result is inspected, **then** completed changes and unresolved conflicts are reported with bounded recovery; no broad overwrite or silent success is assumed.

### Edge Cases

These cases require inspectable outcomes under the selected design:
- **Mixed versions**: Installed assignments and delivered names disagree. Report the mismatch and coordinated migration action without concealing it through fallback dispatch.
- **Identity collision**: Filenames, configured names, and referenced names disagree, or two files claim one name. Identify competing definitions before claiming a usable inventory.
- **Existing files**: Install-missing and ordinary refresh preserve existing consumer copies without per-file ownership hashes or automatic customization detection. Explicit reset supplies authority to discard customizations for its named targets.
- **Unsupported settings**: The tested client rejects a field or cannot supply a requested model/effort. Preserve the failure and the required operator resolution.
- **Limited visibility**: Configuration, child labels, and no-op dispatch supply distinct evidence; live exact selection or effective settings may remain unverified.
- **Consumer customization**: Instructions or settings may differ from reviewed source. Preserve copies during ordinary operations; explicit reset discards targeted customizations without automatic detection or merging. Report evidence limits without assuming copies match defaults.
- **Feature 016 coordination**: Its separate name-discovery and probe design must use current exact identities. This feature does not introduce centralized probing or change probe timing.

## Requirements

Requirements define intended outcomes. Exact model/effort choices require supported-client research and operator approval during planning, before implementation; clarification does not select those values.

### Functional Requirements

- **FR-001**: The eight roles MUST use the exact `FlowKit-` identities in User Story 1. Extra roles, new responsibility assignments, and compatibility aliases are not approved by this description.
- **FR-002**: Current workflow references on all delegated branches, controller expectations, configuration filenames and discovery references, tests, and documentation MUST be reconciled with the approved identities. Verified artifacts MUST retain their historical meaning.
- **FR-003**: Every role MUST receive an inspectable instruction-quality review covering responsibility fit, permitted outputs and mutations, exclusions, question routing, blockers, evidence expectations, and unambiguous instructions. Material authority or scope changes MUST return to the operator for a decision.
- **FR-004**: Approved responsibilities MUST remain: Roadmap Agent prepares scoped evidence and applies only approved roadmap changes; Specifier authors or clarifies the selected spec; Planner authors selected planning artifacts; Tasker derives selected tasks; Reviewer independently assesses selected artifacts and alignment; Coder implements selected eligible tasks; Code Reviewer independently inspects implementation; Wiki Curator maintains authorized cited wiki knowledge. Each is the corresponding prefixed role after migration. [Named agents, S018/S020/S021](../../wiki/pages/agent-roles-and-inheritance.md)
- **FR-005**: Authors MUST complete command-required self-checks and quality checklists; independent reviewers MUST NOT assess their own work. Main-task questions and consequential gates MUST remain in the main task, which relays answers to the same child when continuation is needed. [Authority, S017/S020/S021](../../wiki/pages/project-authority-and-review-gates.md)
- **FR-006**: Each role MUST have an operator-approved explicit model/effort pair, a responsibility-based suitability rationale, and evidence that the chosen fields and values are supported by the tested Codex client. Defaults MAY differ by role. Planning MUST research suitable supported pairs and present all eight choices with their rationale and support evidence for operator approval before implementation. Exact values are deferred to that research and decision rather than selected during clarification.
- **FR-007**: Reviewed exact named assignments MUST remain without a FlowKit role-to-model map, workflow assignment default, or per-run agent/model/effort override. Missing, invalid, and unavailable required assignments MUST retain the stop-without-fallback contract. [Named agents, S020](../../wiki/pages/agent-roles-and-inheritance.md)
- **FR-008**: FlowKit MUST deliver consumer-owned copies of reviewed agent defaults through the supported catalog path. Install-missing MUST add absent configurations and preserve existing files. Ordinary refresh MUST update available defaults without overwriting consumer copies. Explicit reset-one and reset-all MUST reapply the selected package's defaults and discard customizations only for the targeted current FlowKit agents; unrelated agents MUST survive. No command syntax is selected by this requirement.
- **FR-009**: Agent copies MUST remain consumer-owned after delivery. FlowKit removal MUST preserve them. Renamed or retired definitions MUST be documented, and old files MUST remain until the operator removes them. Per-file ownership hashes, automatic customization detection, and automatic merging MUST NOT be introduced. This approved delivery contract prospectively replaces the current exclusion of agent acquisition from the catalog lifecycle; existing lifecycle documentation remains baseline provenance. A prefix or matching filename MUST NOT grant overwrite authority outside an explicitly requested reset. [Lifecycle baseline, S005/S016](../../wiki/pages/installation-and-release-lifecycle.md); [current installation contract](../../docs/installation.md)
- **FR-010**: Lifecycle guidance and validation MUST define clean/repeat install-missing, ordinary refresh, reset-one/reset-all, existing prefixed and unprefixed definitions, local edits, partial operations, renamed/retired definitions, and removal. Reports MUST distinguish completed changes from unresolved failures and identify bounded recovery. Install-missing, ordinary refresh, and removal MUST preserve consumer copies; explicit reset MUST affect only its selected FlowKit targets.
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
- **Consumer delivery state**: Available package defaults and provenance, consumer-owned copies, explicitly selected reset targets, and completed/unresolved operations; this does not require per-file ownership tracking or automatic customization detection.
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

These preserve approved scope and accepted clarification decisions while exact model values await planning research and approval:
- **Supported consumer**: Codex remains the initial supported integration. Another runtime, framework, dependency, or build tool is outside scope.
- **Prerequisites**: Roadmap Features 011, 014, and 015 are verified. Feature 016 is independent and not a prerequisite.
- **Current source**: The eight local configs are role-review inputs and currently omit model/effort fields. Their presence establishes neither delivery nor effective settings.
- **Approval boundary**: The accepted clarification approves consumer-owned acquisition and targeted explicit reset semantics. Selection and authoring do not themselves invoke reset, approve model values, grant managed ownership, authorize implementation, or authorize publication.

## Scope and Governing Context

The [Feature 017 roadmap entry and Open Questions](../../.specify/memory/roadmap.md) supply approved scope. C-02 through C-05 and [Constitution 6.0.0](../../.specify/memory/constitution.md) govern authority, component boundaries, reviewable source/manual fallback, and evidence.

Wiki coverage is **Partial**: existing pages establish reviewed roles, named assignments, ownership, installation lifecycle, human gates, and The Diagram boundary. They do not establish Feature 017's prefix, model/effort selections, or delivery decision. The approved roadmap supplies new scope; the clarification session records the prospective delivery contract and model-selection policy without implying that the wiki establishes them.

Governing context is [Named agents](../../wiki/pages/agent-roles-and-inheritance.md) (S018, S020, S021), [Installation and release lifecycle](../../wiki/pages/installation-and-release-lifecycle.md) (S005, S016), [Project authority and review gates](../../wiki/pages/project-authority-and-review-gates.md) (S001, S017, S020, S021), and [Diagram adapter boundary](../../wiki/pages/diagram-adapter-boundary.md) (S001, S003). Existing configs corroborate the baseline without approving future values or ownership.

Excluded are unrelated control-flow changes, retrospective semantic edits to verified artifacts, managed ownership of consumer copies, per-file ownership hashes, automatic customization detection or merging, another workflow phase, roadmap or active-pointer edits, Git integration, publication, automatic adoption, and lifecycle acceptance. Select Feature feedback does not expand this feature into approval-gate redesign.

## Decisions Required Before Readiness

The substantive clarification decisions are recorded above. The draft and author self-check claim neither independent review nor readiness for planning or implementation.

The model-selection policy is settled: planning researches responsibility-based defaults and presents exact values for all eight roles with suitability and supported-client evidence for operator approval before implementation. No values are selected here. That planned approval is an implementation prerequisite rather than an unanswered clarification about specification scope.
The delivery and ownership decision is settled by the session above: consumer-owned copies, install-missing, ordinary refresh of available defaults, explicitly targeted reset, and operator-managed removal of copied or obsolete definitions. Planning must identify reviewed reusable source and the concrete interface without changing this contract.

FR-012 through FR-014 define the evidence policy. Exact supported fields and observable evidence still need verification for the selected settings and delivery choice; missing verification must stay visible.


## Operator-Directed Follow-up Disposition

On 2026-10-04 the operator explicitly directed that confirmed catalog prerequisite defect DEP017-01 be fixed in a follow-up feature and documented now. [The durable follow-up record](follow-up.md) preserves the observed failure, affected commands, future outcome and validation obligations; no numbered roadmap feature or replacement runtime approach is selected.

Original requirements and success criteria remain above as reviewed intent. Their current completion coverage has this approved qualification: FR-008 agent-delivery behavior and SC-003 file dispositions were demonstrated in the dependency-equipped tested interpreter; reproducible preparation of the advertised mise runtime remains deferred. FR-011 names, values, ownership, lifecycle and recovery guidance remains covered, while complete runnable dependency-provisioning guidance is deferred. The advertised mise command failed without PyYAML; deferral is not proof that its original unconditional usability target passed.

No remaining nondeferred buildable work is identified under this disposition. DEP017-01 remains a known unresolved follow-up, not an eligible current implementation task. This scope/evidence qualification preserves the original test results and all native/effective-setting limitations, and grants no roadmap verification, Git integration, publication or feature acceptance.

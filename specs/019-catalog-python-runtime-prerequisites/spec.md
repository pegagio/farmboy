# Feature Specification: Agent Python Environment

**Feature Directory**: `specs/019-catalog-python-runtime-prerequisites`
**Created**: 2026-10-04
**Status**: Complete
**Scope revised**: 2026-10-05 by direct operator instruction.

The agent should have the Python environment it needs for efficient repository work. PyYAML must be available in the environment the agent actually uses. Consider other utilities where recurring tasks or observed missing-tool failures justify them, without turning this into Spec Kit or FlowKit runtime integration.

## Contents

- [Clarifications](#clarifications)
- [User scenarios and testing](#user-scenarios--testing)
- [Requirements](#requirements)
- [Success criteria](#success-criteria)
- [Scope and assumptions](#scope-and-assumptions)
- [Authority and evidence](#authority-and-evidence)

## Clarifications

The latest operator decision supersedes the earlier repository-wide runtime and shared-Specify design choices.

### Session 2026-10-05

- Earlier discussion expanded the feature from a PyYAML setup defect into FlowKit execution-path inventory, compatibility checks and shared Specify interpreter selection. Those choices are superseded by the operator's subsequent scope correction.
- The approved scope is now the agent's Python environment: ensure PyYAML is installed, consider other useful tools, and make the environment straightforward for the agent to use within the repository. Coupling the solution to Spec Kit and FlowKit is not required.
- No additional package bundle, environment manager, installation location or machine-global change is selected by this scope decision.
- The operator additionally requires FlowKit to provide repeatable tooling and/or instructions so other projects can explicitly adopt the same agent-environment preparation pattern. Reuse does not require coupling the environment to Specify/FlowKit runtimes or automatically editing existing consumers.

## User Scenarios & Testing

These scenarios test the agent's actual working environment rather than an unrelated interpreter that happens to have the package.

### User Story 1 — Use PyYAML Without Setup Thrash (Priority: P1)

An agent performing repository work can parse and write YAML without discovering that its working Python lacks PyYAML.

**Independent test**: Follow the documented preparation and invocation convention in a clean supported environment; use the Python the agent is instructed to run to import `yaml` and round-trip a representative YAML document.

**Acceptance scenarios**:

1. Given the documented preparation is complete, when the agent uses the documented Python invocation, then PyYAML imports and its normal safe YAML operations work.
2. Given a fresh environment, when preparation is followed, then the agent can use that same environment without undocumented package installation or switching to a personal interpreter.
3. Given the environment is incomplete, when preparation is checked or the operation fails, then the agent receives a concise explanation and documented recovery instead of repeatedly guessing interpreters or installing packages ad hoc.

### User Story 2 — Know Which Python to Use (Priority: P1)

An agent can identify the supported repository Python environment during ordinary work, including between skill invocations.

**Independent test**: From a new repository session, follow the project guidance and confirm that the documented invocation selects the prepared environment and can import PyYAML.

**Acceptance scenarios**:

1. Given a new session, when the agent reads the project guidance, then it can identify the Python invocation and preparation instructions without tracing Specify or FlowKit internals.
2. Given multiple installed Python interpreters, when the documented invocation is used, then it selects the prepared environment; matching version numbers alone are not treated as evidence of matching installed packages.
3. Given an applicable higher-priority skill-tools interpreter instruction, when a script belongs to or validates Codex skills, then that instruction remains respected and its dependency gap is reported before changing the environment.

### User Story 3 — Consider Useful Additional Tools (Priority: P2)

The maintainer considers a small set of Python utilities that could reduce repeated missing-tool failures or make common agent tasks easier.

**Independent test**: Review the utility assessment and verify each proposed addition has a concrete recurring use or observed failure, a benefit and cost comparison, and an explicit disposition.

**Acceptance scenarios**:

1. Given an observed missing-tool failure or recurring task, when a utility is considered, then its purpose, expected benefit, existing alternatives and maintenance cost are documented.
2. Given a utility with no demonstrated benefit, when the assessment is completed, then it may be excluded; no minimum number of additional packages is required.
3. Given a proposed new dependency or tool, when adoption is considered, then its documented need and explicit approval precede installation.

### Edge Cases

These cases bound the environment preparation and invocation convention:

- PyYAML is installed in one interpreter but the agent runs another.
- Mise selects the expected Python version but that environment lacks the required package.
- A shell does not activate the repository's configured environment automatically.
- Installation is unavailable or fails; readiness is not claimed and the actual limitation is reported.
- An existing user-owned environment must not be replaced or modified silently.
- An optional utility is absent; the agent uses a documented alternative or reports the limitation rather than assuming it exists.

### Repeatable Project Adoption

The same preparation pattern must be usable outside this source checkout. FlowKit must provide portable instructions or reusable setup material, including the configuration/dependency inputs and validation steps needed in another project. Adoption is explicit; existing configuration or environments must be inspected and preserved unless the operator approves a conflicting change. A clean second project demonstrates repeatability rather than assuming it from local success.

## Requirements

These requirements replace the earlier FlowKit runtime-integration requirements for this mutable feature. Earlier review reports remain point-in-time evidence for the superseded scope.

### Functional Requirements

- **FR-001**: The project MUST provide a documented Python preparation and invocation convention for ordinary agent work within the repository.
- **FR-002**: PyYAML MUST be available in the environment selected by that invocation, with working safe YAML parsing and serialization.
- **FR-003**: Following documented preparation in a clean supported environment MUST establish the required package availability without undocumented interpreter substitutions or package installation steps.
- **FR-004**: Project agent guidance MUST identify the environment and invocation to use, including between skill invocations, while preserving applicable higher-priority skill-tools instructions.
- **FR-005**: Missing prerequisites or failed preparation MUST have concise, actionable diagnostics and recovery guidance. This does not require a new readiness protocol, command framework or structured capability-report system.
- **FR-006**: Additional utility candidates MUST be assessed against recurring tasks or observed failures, expected benefit, alternatives and maintenance cost. New dependencies or tools require documented need and explicit approval before adoption; an assessment selecting no additional packages is valid.
- **FR-007**: The change MUST remain limited to the agent's Python environment, preparation and usage guidance, justified utilities, and direct validation. It MUST NOT require Specify/FlowKit interpreter unification, component-specific launchers, workflow/protocol changes, automatic consumer runtime migration or a general-purpose runtime-management framework.
- **FR-008**: Validation MUST identify the actual interpreter, package versions, preparation performed and observed outcome. Prior failed preparation and successful alternate-interpreter observations MUST remain distinguishable; no historical Feature 017 evidence or test limitation is rewritten.

- **FR-009**: FlowKit MUST provide portable setup instructions and/or reusable configuration for other projects to adopt the same agent Python environment pattern. The delivery MUST state prerequisites, preparation, agent invocation and verification; handle existing project configuration without silent replacement; and be validated in a second disposable project without relying on this checkout’s installed state or personal paths.

## Success Criteria

These outcomes establish usable preparation, not implementation acceptance or broader product compatibility.

- **SC-001**: After documented preparation, the agent's documented Python invocation imports PyYAML and passes a representative safe YAML round-trip test in a clean supported environment, with zero undocumented setup steps.
- **SC-002**: A new repository session can use the documented environment without guessing which interpreter contains PyYAML; the selected interpreter and installed package version are recorded.
- **SC-003**: Every additional utility assessed has a concrete rationale and inclusion/exclusion disposition; every proposed addition has approval before adoption.
- **SC-004**: Incomplete preparation is reported truthfully with an actionable recovery instruction, without silently changing a user-owned or machine-global environment.

- **SC-005**: A second clean disposable project can adopt the FlowKit-provided setup material, prepare its local agent environment and pass the same interpreter/PyYAML validation without undocumented steps or source-checkout dependencies. An existing-configuration case preserves unrelated settings and makes any conflict requiring an operator decision explicit.

## Scope and Assumptions

The implementation should use the smallest maintainable preparation and invocation convention that meets these requirements. The environment mechanism remains for revised planning; no separate wrapper is required when existing project tooling and guidance are sufficient.

Spec Kit and FlowKit may benefit from the agent having PyYAML, but they do not own or dictate this feature's runtime design. Catalog lifecycle, compatibility matrices, per-component runtime profiles, agent ownership delivery tests and workflow-controller reconciliation are not required acceptance work for this feature. Changes to external repositories, machine-global environments, secrets, Git integration and publication remain outside scope.

## Authority and Evidence

The operator's latest direct scope correction on 2026-10-05 is the governing decision. Feature identity and directory remain unchanged to avoid a second feature or pointer transition.

[DEP017-01](../017-flowkit-agent-configuration/follow-up.md) records the motivating failure: the documented mise refresh used Python 3.11.16 without PyYAML, while a separate skill-tools interpreter with PyYAML 6.0.3 succeeded. This illustrates different package availability across interpreters; it does not require a catalog runtime redesign. Preserve the original record and Feature 017's accepted model-support evidence, effective-setting uncertainty and native Specify test limitations.

The earlier planning artifacts and roadmap briefs describe superseded designs. Their review outcomes do not establish readiness of this narrowed feature. Planning must be reconciled before task generation or implementation.

<!--
SYNC IMPACT REPORT
==================
Version change: 6.0.0 → 7.0.0
Bump rationale: MAJOR — define direct trusted operator authorization for bounded roadmap modification or activation while preserving focused gates for inferred or consequential decisions.
Modified principles: II. Human-Directed Authority (roadmap modification and activation authorization).
Added sections: none.
Removed sections: none.
Follow-up: Feature 020 must update reviewed workflow/controller source and validation before using the amended authority. Existing installed gates remain operative until a compatible reviewed component is installed; active work must revalidate its target, dependencies, and governing state, and no earlier gate is retroactively satisfied.
-->

# Spec Kit Flow Constitution

## Core Principles

### I. Spec Evolution and Merge-Bounded Persistence

The project MUST use the **Merge-Bounded Flow-Back Spec Persistence Model**.

- **One mutable change set**: Before a feature is merged, its `spec.md`, `plan.md`, `tasks.md`, and implementation MUST be treated as one mutable, reviewable unit.
- **Changes flow back**: Accepted discoveries MAY originate in any artifact, but their consequences MUST be applied throughout the artifact set before work proceeds from the changed direction. Lower-level artifacts and implementation MUST NOT silently contradict higher-level intent.
  - A change to intended behavior MUST be reflected in `spec.md`.
  - A change to technical approach MUST be reflected in `plan.md`.
  - A change to the required work MUST be reflected in `tasks.md`.
- **Operator-directed consistency gates**: The operator decides when to invoke FlowKit workflows. The agent MUST flag missing checks and unresolved divergence, ask the operator when existing feature decisions do not settle a conflict, and MUST NOT launch a workflow or its underlying commands without an operator instruction. Known divergence MUST block implementation or merge until the artifacts are reconciled or the operator directs a documented resolution.
  - After tasking or consequential artifact reconciliation, the agent SHOULD recommend the FlowKit analyze/remediate workflow before implementation starts or resumes.
  - After implementation, the agent SHOULD recommend the FlowKit convergence workflow until no gaps remain.
  - Before merge, the agent SHOULD recommend the project's applicable validation and a joint review of the artifact and implementation diffs.
- **Merge freezes history**: Acceptance into the project's designated integration branch is the persistence boundary. After that merge, the feature directory MUST be treated as a semantically immutable historical record. Editorial corrections MAY improve presentation only when they do not alter meaning.
- **Later changes flow forward**: A later requirement or behavioral change MUST be expressed in a new feature directory. The new feature MUST reference any earlier feature that it amends, replaces, or depends on when that relationship is material, and MUST NOT rewrite the earlier feature to describe the new outcome retroactively.

**Rationale:** This model permits requirements and implementation knowledge to converge while a feature is being developed, makes the merged feature a coherent unit of review, and preserves an auditable sequence of accepted changes without rewriting project history.

### II. Human-Directed Authority

The human operator MUST select the workflow and task scope. Every explicitly delegated workflow step MUST declare a reviewed Codex agent name. Naming an agent MUST NOT itself delegate a main-task step. Invocation authorizes those named assignments without a per-run agent, model, or effort override. A Codex controller MAY launch bounded step subagents and MUST follow the named assignments. It MUST stop for operator resolution when an assignment is missing, invalid, or unavailable; it MUST NOT silently choose a fallback assignment, expand the task scope, schedule work, or invoke another FlowKit workflow or an undeclared later phase. An operator-invoked workflow MAY execute reviewed, bounded core-command steps for correction and reassessment, including analysis and implementation, only when those steps are declared in its installed definition, remain within the selected feature and task scope, and preserve every consequential human gate. Those steps do not authorize invocation of another FlowKit workflow. The controller MUST present clarification questions and consequential review gates in the main task and relay the operator's answer to the same step subagent when continuation is needed. Successful commands MUST NOT implicitly verify a roadmap item, integrate Git changes, accept a feature, or grant acceptance in The Diagram. A direct trusted operator instruction that unambiguously authorizes a bounded roadmap modification or activation is the explicit human decision for that operation. Routine wording, numbering and linkage derived wholly within that instruction do not require a second approval solely for their exact patch bytes. The controller must make the resulting changes and their authorization inspectable and revalidate the current target, dependencies and governing state before effect. An inferred or unrequested roadmap change, constitutional amendment, authority change, material scope change, substantive product decision or ambiguous recovery must pass a focused explicit human decision gate before mutation. Selection changes active identity only and does not establish authoring, implementation, verification or acceptance. Separately requested phases may retain settled same-target intent after revalidation; completion does not invoke another workflow. Routine remediation MAY flow back only within the operator-issued controller scope.

**Rationale:** Reviewed agent names keep selection explicit while consumers configure those agents through Codex. Declared in-workflow correction may reach a conclusion without granting the controller authority to choose the next workflow or bypass an operator decision.

### III. Generic Source and Component Boundaries

This repository MUST own generic workflow source, any separately approved reusable preset, portable consumer feedback capture and reporting, and maintainer-only feedback intake. The `spec-kit-flow` repository and bundle MUST retain that identity. Workflow source owned by this repository MUST use `speckit-flow-<purpose>` IDs. Extension source MUST use its reviewed Spec Kit manifest ID, whether owned here or independently versioned; the bundle MUST pin that ID and version, and workflows MUST invoke commands the extension declares. A bundle MUST compose versioned components and MUST NOT become a second source of their behavior. The Diagram MUST remain a consumer rather than a runtime prerequisite; its registration, canonical work, projections, adapter feedback, and orchestration MUST stay in a separately versioned adapter under its own authority.

**Rationale:** These boundaries keep the generic workbench reusable and each component's behavior traceable to one reviewed source.

### IV. Reviewable Source and Manual Fallback

Changes MUST target reviewed source packages rather than installed copies in a consumer's `.specify/` directory. Workflow packages MUST remain independently reviewable, and planning and task generation MUST remain separate. A Codex controller MUST follow the installed, versioned workflow definition rather than duplicate its prompts, gates, or decision rules in a skill. Every workflow MUST preserve a usable manual-prompt path when native dispatch is unavailable. A new framework, dependency, or build tool MUST have a documented need and explicit approval before adoption.

**Rationale:** Independent review and a manual path let operators inspect and run the process without relying on one dispatch mechanism.

### V. Evidence-Based Validation and Feedback

Changed source definitions and bundle behavior MUST be validated in disposable initialized consumers where applicable. Validation records MUST identify component IDs, versions, source digests, tested CLI version, source coordinates, and observed results. A no-op agent run MUST be described as dispatch evidence, not live-agent validation. Local tests MUST NOT be presented as proof of publication, stock Spec Kit compatibility, or consumer adoption. Consumer feedback MUST remain local evidence; exported reports MUST omit raw transcripts, secrets, and absolute host paths. Maintainer intake MUST validate reports and propose dispositions; neither capture nor intake MAY directly change workflow source, presets, installed components, roadmaps, or runtime authority.

**Rationale:** Provenance and bounded claims make results reproducible while keeping feedback separate from governance and implementation.

## Component and Consumer Constraints

The generic bundle MUST require compatible, independently versioned roadmap and wiki extensions and MUST identify Codex as its initial supported integration until other integrations are validated and accepted. Consumer-owned feedback and unrelated components MUST survive bundle removal. A custom clarification preset or continuation policy MUST require its own approval; the current five-question clarification cap MUST NOT be described as removed by the existing workflows. Diagram-specific behavior MUST NOT enter the generic bundle through a consumer fixture or feedback report.

## Development and Review Gates

Before changing behavior, maintainers MUST reconcile the relevant specification, plan, and tasks under Principle I. Reviews MUST check operator authority, component boundaries, manual fallback, provenance, and the evidence supporting compatibility claims. After changes, maintainers MUST run relevant tests and checks, report any checks that could not run, and document changed user-facing workflows or installation requirements. Consumer feedback accepted for source change MUST re-enter specification, planning, tasking, and implementation through the normal feature flow. Publication and consumer acceptance require their own explicit decisions.

## Governance

This constitution governs project decisions when lower-level guidance conflicts with it. `AGENTS.md` provides operational agent guidance and MUST remain consistent with this constitution. Amendments MUST document the proposed rule change, its rationale, affected workflows or artifacts, and any migration needed for active work; they require explicit human review before acceptance. An amendment MUST NOT retroactively rewrite a merged feature's meaning.

Constitution versions use semantic versioning: MAJOR for incompatible governance changes or principle removal/redefinition, MINOR for a new principle or material expansion, and PATCH for non-semantic clarification. The first ratified constitution is version 1.0.0. Every amendment MUST update the version and last-amended date, and its review MUST verify compliance with the principles and identify any unresolved exceptions. Exceptions MUST be explicit, scoped, and approved by the human operator; an exception does not silently amend this constitution.

**Version**: 7.0.0 | **Ratified**: 2026-09-22 | **Last Amended**: 2026-10-05

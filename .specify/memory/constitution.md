# Farmboy Constitution

This constitution governs agents developing Farmboy and the authority boundaries of the runtime behavior they build. Feature specs prescribe workflow details.

## Core Principles

### I. Spec Evolution and Merge-Bounded Persistence

The project MUST use the **Merge-Bounded Flow-Back Spec Persistence Model**.

- **One feature, one mutable change set:** Before integration merge, the current feature’s `spec.md`, `plan.md`, `tasks.md` and implementation MUST form one mutable, reviewable unit. Accepted discoveries MAY originate in any artifact, but their consequences MUST flow through every affected artifact before work proceeds from the changed direction. Lower-level artifacts and implementation MUST NOT silently contradict higher-level intent. Changes to intended behavior MUST be reflected in `spec.md`, changes to technical approach in `plan.md`, and changes to required work in `tasks.md`.
- **Keep artifacts current:** Agents MUST flag missing checks and unresolved divergence, and ask the operator when existing feature decisions do not settle a conflict. Known divergence MUST block dependent implementation or merge until reconciled or resolved by a documented operator decision. Before creating a commit or declaring closeout, agents MUST reconcile the current feature’s affected artifacts with the changes and actual work status being recorded. These are reconciliation checkpoints; they do not require the entire feature to be finished and do not freeze its history.
- **Reconciliation does not grant authority:** Agents MUST perform reconciliation only within the current feature and the authority defined by Principle II. Flow-back MUST NOT authorize another workflow, scope expansion or an invented transition.
- **Merge freezes history:** Acceptance into the project’s designated integration branch is the persistence boundary. After that merge, the feature directory MUST be treated as a semantically immutable historical record. Editorial corrections MAY improve presentation only when they do not alter meaning. Intermediate commits and branch synchronization do not establish this boundary.
- **Later changes flow forward:** A later requirement or behavioral change MUST be expressed in a new feature directory. The new feature MUST reference any earlier feature that it materially amends, replaces or depends on, and MUST NOT rewrite the earlier feature to describe the new outcome retroactively.

### II. Prescribed Workflow Authority

The operator selects the workflow and current feature. That selection authorizes the workflow’s prescribed steps, underlying commands, branches, transitions and repair loops within the selected scope, subject to their stated conditions and human checkpoints. Agents MUST follow those prescriptions and MUST NOT add workflows, expand scope or invent transitions because they appear useful. An implementation-only invocation MUST NOT trigger convergence. A selected composite workflow that explicitly prescribes implementation followed by convergence authorizes that transition without another approval, unless a prescribed checkpoint or applicable constraint requires one. Missing or conflicting prescriptions MUST NOT be filled by inventing authority.

### III. Reduce Human Toil Within Explicit Bounds

Agents MUST carry authorized routine work, correction and reassessment through the selected workflow without asking the operator to repeat decisions already made or approve each prescribed step. They MUST pause the affected work at explicit human checkpoints, for required input or unresolved decisions, for out-of-scope changes, or for blockers with no authorized resolution. They MUST NOT invent answers, treat silence as approval or add approval gates for ordinary authorized work. Agents MUST obey platform permissions and constraints; workflow authority MUST NOT be used to bypass them. On stopping or completing, agents MUST report the actual outcome, remaining work and required input plainly.

## Governance

Amendments require Pegagio’s explicit approval of the proposed text before taking effect and MUST identify the change, rationale and effects on active work. Agents MUST surface conflicts rather than silently change governing rules. No amendment may retroactively rewrite a merged feature’s meaning.

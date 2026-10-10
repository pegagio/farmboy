# Merge-Bounded Flow-Back Spec Persistence Model

Merge-Bounded Flow-Back combines the adaptability of Flow-Back Spec with the historical integrity of Flow-Forward Spec. A feature's artifacts may evolve together while the feature is in progress, but the merge boundary freezes them as a record of the change that entered the project.


## README Guidance: Evolving Specifications

The following section is intended for inclusion in a project's README.md.

```md
## Evolving Specifications

This project uses the **Merge-Bounded Flow-Back Spec Persistence Model**. While a feature is being delivered, its `spec.md`, `plan.md`, and `tasks.md` are mutable working documents. Update them as understanding changes so they consistently describe the intended behavior, technical approach, and work to be done.

When the feature is accepted into the project's designated integration branch, those documents become a historical record and must not be substantively changed. Later changes belong in a new feature directory, with a reference to the earlier feature when relevant.
```

## Active Agent Guidance

The following section is intended for inclusion in project instructions that agents read during feature work, such as `AGENTS.md`. A README alone does not establish that agents receive these rules.

```md
## Merge-Bounded Feature Work

- Before the designated integration branch accepts a feature, treat its `spec.md`, `plan.md`, `tasks.md`, and implementation as one mutable change set. Flow accepted discoveries to the affected artifacts and reconcile their consequences before continuing from the changed direction.
- Flag missing checks and unresolved divergence. Recommend the applicable operator-invoked FarmBoy analysis/remediation, convergence, or pre-merge review. Do not launch workflows or their underlying commands independently. Known divergence blocks implementation or merge until reconciliation or an explicitly documented operator resolution.
- Acceptance into the project's designated integration branch freezes the feature's meaning. Make later behavioral changes in a new feature directory and reference earlier features they materially amend, replace, or depend on. Preserve the merged feature as history; allow editorial corrections only when meaning stays unchanged.
```

## Constitution Principle: Spec Evolution and Merge-Bounded Persistence

The following section is intended for inclusion in a project's Spec Kit constitution.

```md
## Spec Evolution and Merge-Bounded Persistence

The project MUST use the **Merge-Bounded Flow-Back Spec Persistence Model**.

- **One mutable change set**: Before a feature is merged, its `spec.md`, `plan.md`, `tasks.md`, and implementation MUST be treated as one mutable, reviewable unit.
- **Changes flow back**: Accepted discoveries MAY originate in any artifact, but their consequences MUST be applied throughout the artifact set before work proceeds from the changed direction. Lower-level artifacts and implementation MUST NOT silently contradict higher-level intent.
  - A change to intended behavior MUST be reflected in `spec.md`.
  - A change to technical approach MUST be reflected in `plan.md`;
  - A change to the required work MUST be reflected in `tasks.md`.
- **Operator-directed consistency gates**: The operator decides when to invoke FarmBoy workflows. The agent MUST flag missing checks and unresolved divergence, ask the operator when existing feature decisions do not settle a conflict, and MUST NOT launch a workflow or its underlying commands without an operator instruction. Known divergence MUST block implementation or merge until the artifacts are reconciled or the operator directs a documented resolution.
  - After tasking or consequential artifact reconciliation, the agent SHOULD recommend the FarmBoy analyze/remediate workflow before implementation starts or resumes.
  - After implementation, the agent SHOULD recommend the FarmBoy convergence workflow until no gaps remain.
  - Before merge, the agent SHOULD recommend the project's applicable validation and a joint review of the artifact and implementation diffs.
- **Merge freezes history**: Acceptance into the project's designated integration branch is the persistence boundary. After that merge, the feature directory MUST be treated as a semantically immutable historical record. Editorial corrections MAY improve presentation only when they do not alter meaning.
- **Later changes flow forward**: A later requirement or behavioral change MUST be expressed in a new feature directory. The new feature MUST reference any earlier feature that it amends, replaces, or depends on when that relationship is material, and MUST NOT rewrite the earlier feature to describe the new outcome retroactively.

**Rationale:** This model permits requirements and implementation knowledge to converge while a feature is being developed, makes the merged feature a coherent unit of review, and preserves an auditable sequence of accepted changes without rewriting project history.
```

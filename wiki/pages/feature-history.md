---
title: Feature artifacts and merge history
type: concept
sources: [S001, S002]
updated: 2026-10-17
---

# Feature artifacts and merge history

Before integration merge, a feature’s specification, plan, tasks and implementation form one mutable, reviewable unit. Accepted discoveries flow into every affected artifact before dependent work proceeds; behavior belongs in `spec.md`, technical approach in `plan.md`, and required work in `tasks.md`. (S001)

Commit and closeout are reconciliation checkpoints: artifacts must reflect the changes and actual work status being recorded, but unfinished work is allowed. Acceptance into the designated integration branch freezes the feature’s meaning; intermediate commits and branch synchronization do not. Later behavioral changes use a new feature directory with material links to earlier features. (S001)

Reconciliation stays inside the current feature and does not create execution authority. Known divergence blocks dependent implementation or merge until reconciled or resolved by a documented operator decision. Agents flag missing checks and ask when existing feature decisions do not settle a conflict; lower-level work must not silently contradict higher-level intent. See [workflow authority](./workflow-authority.md). (S001)

In the intended Diagram integration, distinguish the exact reviewed Git checkpoint from the latest accepted handoff checkpoint. Routine in-scope flow-back does not revoke historical approval; material changes require the affected human review again rather than treating old approval as approval of changed meaning. Git remains canonical for artifacts and evidence. (S002)

Integration receipts belong only in Diagram’s database, referring to Git checkpoints rather than triggering recursive project commits. The integration merge remains the historical persistence boundary. These are future [Diagram integration](./diagram-integration.md) contracts, not a new current workflow or an implemented receipt system. (S001, S002)

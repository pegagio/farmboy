---
title: Feature artifacts and merge history
type: concept
sources: [S001]
updated: 2026-10-16
---

# Feature artifacts and merge history

Before integration merge, a feature’s specification, plan, tasks and implementation form one mutable, reviewable unit. Accepted discoveries flow into every affected artifact before dependent work proceeds; behavior belongs in `spec.md`, technical approach in `plan.md`, and required work in `tasks.md`. (S001)

Commit and closeout are reconciliation checkpoints: artifacts must reflect the changes and actual work status being recorded, but unfinished work is allowed. Acceptance into the designated integration branch freezes the feature’s meaning; intermediate commits and branch synchronization do not. Later behavioral changes use a new feature directory with material links to earlier features. (S001)

Reconciliation stays inside the current feature and does not create execution authority. See [prescribed workflow authority](./workflow-authority.md). (S001)

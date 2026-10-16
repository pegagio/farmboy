---
title: Intended Diagram integration
type: concept
sources: [S001, S002, S004]
updated: 2026-10-16
---

# Intended Diagram integration

This page records intended integration design and open choices. Track implementation progress in roadmap/spec artifacts rather than a capability-status inventory here. Additional context comes from the operator discussion on 2026-10-16; the established delivery sequence comes from the local direction document. (S002, S004)

## Responsibilities and rationale

Diagram is the local cross-project control plane: the canonical queue of outstanding features/tasks, dependencies and lifecycle. Codex skill sessions capture operator intent into Diagram. A single coordination authority avoids competing writable queues after a project migrates from the roadmap extension. (S002, S004)

Farmboy defines and executes prescribed Spec Kit workflow segments and feedback loops, then returns outcomes and evidence. Diagram retains acceptance through its state-transition boundary; Farmboy execution does not become a second canonical lifecycle. This separates reusable execution from cross-project coordination. (S002, S004)

## Handoff boundaries

Keep task identity, workflow-run/segment identity, permitted execution scope, completion outcome and evidence distinct from canonical lifecycle acceptance. A completed execution does not itself imply merge or acceptance. Specify how context and authority are checked, pending questions and interruptions are returned, and stale or duplicate results are reconciled, without assuming a finalized schema, API or transport. (S002, S004)

Preserve human clarification and specification/full-plan review gates. Authorized prescribed transitions should not require redundant approvals; they must still respect explicit human checkpoints and execution scope. See [prescribed workflow authority](./workflow-authority.md). (S001, S004)

## Delivery relationship

Establish local human-driven Farmboy first, then human-driven Diagram integration, then bounded autonomous claiming. Begin autonomy with one worker on one project. Prove execution return and state handling before autonomous work. See [delivery direction and evidence](./delivery-direction.md) for stage outcomes and evidence. (S002, S004)

## Open decisions

Push, pull or hybrid dispatch and reusable worker contexts remain design decisions. Concrete handoff schemas, APIs and transport need feature-level decisions; this context does not settle them or decompose the roadmap into features. (S004)

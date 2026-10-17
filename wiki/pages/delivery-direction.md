---
title: Delivery direction and evidence
type: concept
sources: [S002, S004, S005, S006, S008]
updated: 2026-10-17
---

# Delivery direction and evidence

Farmboy aims to automate the proven manual Spec Kit lifecycle with less human toil and preserved repair loops and decisions. These are intended outcomes, not claims of implemented or accepted capabilities. (S002)

## Current local scope

The three local workflow features remain specification preparation, plan/tasks preparation and delivery through local closeout/result review. The approved Feature 001 course correction ends automated selection/context/drafting at a saved draft/handoff, with native Goal completion there. Ordinary existing clarification follows only when needed, outside that Goal; settled drafts go directly to human review. Explicit human spec approval remains prerequisite for planning, at the operator’s chosen review depth. Native completion at the revised handoff must be independently verified before capability is claimed. The earlier combined-clarification direction is historical. (S002)

Start with one Codex session using its existing model/effort and thin compositions of existing commands. Extra infrastructure needs a concrete current requirement or observed failure; explain alternatives at full-plan review. Bootstrap the earliest workflow manually, dogfood delivered segments, and demonstrate portability in a disposable project rather than require a second live adoption. Preserve real questions, bounded Goals verification and artifact-based resume. (S002, S005, S006)

## Eventual integration boundary

The intended four segments are specify/clarify, plan/task/reconcile, deliver a verified candidate, and integrate the authorized candidate. Human UAT/final-result review authorizes integration after the candidate; execution alone grants neither approval nor a push. Diagram coordinates features and serializes repository/target integration; Git files retain specifications, plans, tasks, code and evidence. The external Git executor’s home remains undecided. (S002)

Direction/wiki alignment records that intent now; later contract/workflow alignment is distinct from implementing a full adapter, executor or concurrency platform. [Intended Diagram integration](./diagram-integration.md) describes ownership, checkpoint and receipt boundaries. [Workflow authority](./workflow-authority.md) preserves current scope and human decisions. (S002)

The roadmap separates initial local workflow features 001–003 from subsequent contract/workflow alignment in 004, which depends on the delivered local lifecycle. That follow-up excludes a full Diagram adapter, integration executor and concurrency platform; the direction/wiki alignment is distinct documentation work. (S006)

## Delivery evidence

Local human-driven execution advances only after a real bounded feature demonstrates the full lifecycle, human interaction and reviews, repair, closeout, required stops and interruption/resume without lost input or duplicate effects. Native consistency, implementation and convergence goals need verification before custom continuation machinery. Fixtures or dispatch tests do not replace that demonstration. (S002)

Later human-driven Diagram integration must demonstrate context, checkpoint/evidence return, state reconciliation, stale/duplicate handling, serialized integration and preserved human decisions, without competing writable queues. Narrow autonomy begins with one worker on one project; prove bounded execution and safe stop/resume before broader concurrency. One active agent per feature permits sequential owner handoffs and later independent-feature concurrency on isolated branches/worktrees. (S002)

A scheduler, worker pool, recipe engine and elaborate accounting remain outside initial scope; metrics are optional. Executor placement, dispatch, reusable contexts and concrete integration schemas/APIs/transport remain later decisions. [Project context pointers](./project-context.md) distinguishes the roadmap ledger from durable wiki knowledge. (S002, S006)

[Specification preparation handoff](./specification-handoff.md) records the implemented draft/Goal boundary, ordinary clarification and separate approval, including the native-state evidence limits. (S008)

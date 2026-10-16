---
title: Delivery direction and evidence
type: concept
sources: [S002, S004, S005, S006]
updated: 2026-10-16
---

# Delivery direction and evidence

Farmboy aims to automate the proven manual Spec Kit lifecycle with less human toil and preserved repair loops and decisions. These are intended outcomes, not claims of implemented or accepted capabilities. (S002)

The desired experience has three segments: select/specify/clarify followed by specification review; plan/tasks and read-only analyze/repair until a fresh pass followed by full-plan review; implementation, convergence-created work and closeout followed by result review. Clarification answers do not substitute for specification review. (S002)

Stage one is local human-driven execution. Evidence to advance is a real bounded feature completing the full lifecycle, human interaction, reviews, repair, closeout, required stops and interruption/resume without lost input or duplicate effects. Native consistency, implementation and convergence goals need verification before custom continuation is added. (S002)

Stage two introduces human-driven Diagram coordination, with Diagram replacing the migrated project’s roadmap queue role. A real integrated run must demonstrate execution context, evidence return, state reconciliation, stale/duplicate handling and preserved decisions. Stage three starts with one worker on one project and requires bounded execution, safe stop/resume and no duplicate authority; completion does not imply acceptance or integration. (S002)

Initial scope excludes a scheduler, worker pool, recipe engine and elaborate accounting. Metrics are optional. Command mappings, feature completion and commit semantics remain phase-one decisions; dispatch and reusable contexts are later decisions. [Workflow authority](./workflow-authority.md) governs how these intended segments may execute. (S002)

[Intended Diagram integration](./diagram-integration.md) records coordination/execution responsibilities, handoff boundaries and open integration choices for later feature discussion. (S004)

## Local workflow guardrails

The initial feature boundaries are prepare specification → specification review; prepare plan/tasks with analyze/repair until a fresh pass → full-plan review; deliver an approved plan through implementation/convergence, reconciled closeout and local commit → result review. At full-plan review, the agent explains new infrastructure/subsystems, concrete rationale, simpler alternatives and its recommendation; the operator decides approval or simplification. These boundaries do not authorize executing the workflows. (S005, S006)

Start with one Codex session using its existing model/effort and thin compositions of existing commands. Reconsider delegation/configuration only for demonstrated need. Verify bounded Goals behavior and genuine input/review stops; use current artifacts for interruption/resume rather than a universal recovery system. Bootstrap the earliest workflow manually, dogfood delivered segments for later development, and demonstrate portability in a disposable Spec Kit project instead of requiring a second live-project adoption. (S005, S006)

[Project context pointers](./project-context.md) explains the roadmap’s role as the changing work ledger and the wiki’s role as durable contextual knowledge. (S006)

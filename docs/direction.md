# Farmboy direction

## Purpose

Farmboy automates Pegagio’s proven manual Spec Kit lifecycle, reducing human toil while preserving useful behavior, repair loops and human decisions. Build a simple local experience first, then integrate Diagram coordination, then introduce narrow autonomy.

The [constitution](../.specify/memory/constitution.md) governs authority. This document describes the intended product; it does not invoke a workflow or authorize implementation.

## Desired experience

Support three human-driven segments:

1. **Select, specify and clarify → specification review.** Discover relevant project context, select eligible work, author the specification and review its roadmap fit. Clarification may require repeated questions; answering them does not replace review of the finished specification.
2. **Plan, task and reconcile → full-plan review.** Generate the plan and tasks. Run read-only analysis, apply accepted repairs to affected artifacts, and repeat until a fresh analysis passes. Review the full plan before implementation.
3. **Implement, converge and close out → result review.** Complete eligible work, implement convergence-created tasks and reassess until clean. Preserve closeout reconciliation, completion recording, roadmap debrief, wiki maintenance and the agreed local commit behavior. Present actual results and remaining gaps.

These segments describe the experience to deliver. Their executable steps and transitions belong in selected workflows, under the constitution’s authority rules.

## Delivery stages

### 1. Local Farmboy, Pegagio drives

Preserve the full lifecycle using human-driven prompts and supported native capabilities. Verify the three intended native goals—consistency repair, implementation and convergence—before adding custom continuation machinery.

**Evidence to advance:** a real bounded feature completes the lifecycle, including interactive clarification, separate human reviews, repair loops, successful closeout, required stops and interruption/resume without lost input or duplicate effects. Isolated fixtures or dispatch tests support development but do not replace this demonstration.

### 2. Diagram coordinates, Pegagio still drives

Diagram supplies the canonical feature/task queue, dependencies and lifecycle. For a migrated project, it replaces the roadmap extension’s queue role. Farmboy remains reusable execution; Diagram-specific authority belongs at the adapter boundary.

**Evidence to advance:** a real integrated run demonstrates correct execution context, returned evidence, state reconciliation, stale/duplicate-result handling and preserved human decisions, without competing writable queues.

### 3. Narrow autonomous workers

Start small with one worker on one project, claiming eligible Diagram work and returning outcomes and evidence.

**Evidence for acceptance:** demonstrate bounded execution, safe stop/resume, no duplicate authority and preserved human checkpoints. Workflow completion must not imply acceptance or integration.

## Immediate focus and open decisions

Prepare the local phase-one specification and full plan for review. A scheduler, worker pool, new recipe engine and elaborate accounting system are outside that initial scope. Metrics are optional.

Settle exact command mappings, feature completion and local commit semantics in the phase-one spec. Decide dispatch mechanics and reusable contexts when later delivery needs them; they are not settled architecture.

Spec Tool Kit retains the proven prompts and full historical Farmboy/Diagram direction record. They are optional background when a task needs source detail, subject to repository access boundaries; routine work should not require loading them.

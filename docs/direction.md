# Farmboy direction

## Purpose

Farmboy automates Pegagio’s proven manual Spec Kit lifecycle, reducing human toil while preserving useful behavior, repair loops and human decisions. Build a simple local experience first, then integrate Diagram coordination, then introduce narrow autonomy.

The [constitution](../.specify/memory/constitution.md) governs authority. This document records agreed product direction, not executable workflow authority or proof of implemented capabilities. The integration alignment below does not expand the current feature or activate the separately planned contract/workflow alignment follow-up.

## Current local experience

Preserve the three human-driven segments already selected for local delivery:

1. **Prepare draft/handoff → ordinary clarification → human specification review.** Automated selection/context/drafting finishes with a saved usable draft, findings and explicit handoff. Its native Goal ends successfully there: ordinary existing Spec Kit clarification handles material questions afterward, outside that completed Goal; settled drafts go directly to human review. Clarification completion is not approval. Explicit human specification approval remains required before planning; the operator chooses review depth. The revised Feature 001 design is approved; actual runtime acceptance remains required before claiming the change works.
2. **Plan, task and reconcile → full-plan review.** Generate the plan and tasks. Analyze, apply accepted repairs to affected artifacts, and repeat until a fresh analysis passes. Review the full plan before implementation.
3. **Implement, converge and close out → result review.** Complete eligible work and convergence-created tasks, reassessing until clean. Preserve reconciled closeout, completion recording, roadmap debrief, wiki maintenance and the agreed local commit behavior. Present actual results and remaining gaps.

Executable steps and transitions belong in selected workflows under the constitution. Future integration direction does not silently add another phase to these local workflows.

## Eventual Diagram integration

### Coordination and canonical artifacts

Diagram owns feature-level coordination metadata: the queue, dependencies, ownership, approvals and exact Git checkpoint references. Git files remain canonical for specifications, plans, tasks, code and evidence. This refines earlier feature/task queue language: Diagram coordinates the feature rather than becoming another writable copy of its task or specification files. For a migrated project, Diagram replaces the roadmap extension’s queue role. Farmboy remains reusable execution, with Diagram-specific authority at the adapter boundary.

Allow one active agent per feature across its segments. Different owners may work sequentially after a handoff; this does not require one permanent agent for the feature. Independent features may proceed concurrently using isolated branches/worktrees.

### Four eventual segments and their human boundaries

1. **Specify and clarify → human specification review.**
2. **Plan, task and reconcile → human full-plan review.**
3. **Deliver a verified candidate → human UAT/final-result review.** Implement, converge, validate and return an inspectable candidate. UAT means user acceptance testing. The human reviews the candidate and evidence and authorizes integration; successful execution alone does not grant that authority.
4. **Integrate the authorized candidate → report the actual integration outcome.** Diagram serializes integration for the repository and target; an external executor performs the Git work. Where that executor lives remains undecided.

Project policy defines the branch strategy, integration target and required checks. Missing or conflicting rules must be surfaced before dependent integration work; the executor must not invent them. Integration authorization does not implicitly authorize a push.

### Approval, handoff and history

Keep the reviewed checkpoint distinct from the latest accepted handoff checkpoint. Routine in-scope flow-back keeps current artifacts coherent without revoking historical approval. Material changes require the affected human review again; historical approval is not approval of changed meaning.

Integration receipts belong only in Diagram’s database, referring to the relevant Git checkpoints. Do not create a project commit just to record the receipt and then recursively require a receipt for that commit. Integration merge freezes the feature’s historical meaning under the constitution; later material behavioral changes use a new linked feature.

## Delivery stages and evidence

**Local Farmboy, Pegagio drives.** Preserve the full lifecycle using human-driven prompts and supported native capabilities. Verify the intended native consistency, implementation and convergence goals before adding custom continuation machinery. Advance only after a real bounded feature demonstrates the full lifecycle, human reviews, repair loops, successful closeout, required stops and interruption/resume without lost input or duplicate effects. Isolated fixtures or dispatch tests do not replace that demonstration.

**Diagram coordinates, Pegagio still drives.** Demonstrate a real integrated run with correct execution context, checkpoint and evidence return, state reconciliation, stale/duplicate handling, serialized integration and preserved human decisions, without competing writable queues.

**Narrow autonomous workers.** Start with one worker on one project. Prove bounded execution, safe stop/resume and no duplicate authority before broader concurrency. Workflow completion must not imply human acceptance or integration.

## Scope and open decisions

Keep the initial local implementation focused on its approved specifications and roadmap. A scheduler, worker pool, new recipe engine and elaborate accounting system are outside that initial scope. Metrics are optional. Diagram constitution 6.0.0/roadmap 2.2.0 adopt draft completion/release after durable handoff and explicit clarification authority acquisition before edits, retained while active between questions. They require visible Specifying → Needs clarification/Awaiting spec review, resolved clarification → review, review → Ready for planning only by approval, and review → Needs clarification. Storage remains future 022/023 work; four macro phases and existing integration gates remain, without new local ownership/state machinery. Executor placement, dispatch mechanics, reusable contexts and concrete integration schemas/APIs/transport remain later feature decisions; this direction does not settle them or authorize implementation.

Spec Tool Kit retains the proven prompts and historical Farmboy/Diagram direction record as optional background, subject to repository access boundaries. Routine work should not require loading them.

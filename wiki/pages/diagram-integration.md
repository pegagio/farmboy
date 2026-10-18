---
title: Intended Diagram integration
type: concept
sources: [S001, S002, S004, S011, S012]
updated: 2026-10-18
---

# Intended Diagram integration

This page records agreed future integration direction and open choices, not implemented capabilities or authority to run work. The current direction refines earlier discussion of a feature/task queue into feature-level coordination; Git task files retain their canonical role. (S002, S004)

## Coordination and execution

Diagram owns feature-level queue, dependencies, ownership, approvals and exact Git checkpoint references. Git files remain canonical for specifications, plans, tasks, code and evidence. For migrated projects, Diagram replaces the roadmap extension’s queue role without creating a competing writable artifact store. (S002)

Farmboy supplies reusable prescribed workflow execution; Diagram-specific authority remains at the adapter boundary. Diagram serializes integration for the repository and target while an external executor performs the Git work. Executor placement is undecided. Project policy defines branch strategy, target and required checks; missing or conflicting rules must be surfaced before dependent integration work. No implicit push is authorized. (S002)

## Feature ownership and human boundaries

One agent may be active per feature across its segments. Different owners may work sequentially after a handoff. Independent features may proceed concurrently on isolated branches/worktrees; this does not introduce a worker pool into the initial local scope. (S002)

The eventual four segments are specify/clarify, plan/task/reconcile, deliver a verified candidate, and integrate the authorized candidate. Human specification and full-plan reviews remain distinct. Human UAT (user acceptance testing)/final-result review follows the candidate and authorizes integration; successful execution alone does not. This future boundary does not add phases to current local workflows. (S002)

## Checkpoints and receipts

Keep the reviewed Git checkpoint distinct from the latest accepted handoff checkpoint. Routine in-scope flow-back does not revoke historical approval; material changes require the affected review again. Integration receipts live only in Diagram’s database and refer to Git checkpoints, avoiding recursive project commits to record receipts. Integration merge freezes historical feature meaning; later material behavior changes use a new linked feature. (S001, S002)

[Workflow authority](./workflow-authority.md) governs current execution. [Feature history](./feature-history.md) explains persistence and reviewed versus current checkpoints. [Delivery direction](./delivery-direction.md) distinguishes current local scope, later alignment and integration evidence. (S001, S002)

## Open decisions

Executor placement, dispatch mechanics, reusable contexts and concrete integration schemas/APIs/transport remain later feature decisions. The agreed sequence remains local human-driven Farmboy, human-driven Diagram integration, then narrow autonomy. No adapter, executor or concurrency platform is implemented by this direction. (S002, S004)

Diagram constitution 6.0.0/roadmap 2.2.0 adopt durable draft handoff and ownership release, separately acquired clarification authority retained while active, and visible Specifying → Needs clarification/Awaiting spec review states. Resolved clarification leads to review; review reaches Ready for planning only on explicit approval or returns to Needs clarification. Representation/storage remains future 022/023 work; Farmboy adds no local Diagram state machinery. (S002)

The later004 [workflow handoff contract](./workflow-handoffs.md) now supplies explicit standalone/external entry and result semantics across the three existing Farmboy skills. It preserves this coordination/integration boundary, uses existing Git context rather than a replacement fit register, and implements no adapter transport or coordinator service. This contract addition does not turn the earlier direction alone into runtime acceptance evidence. (S011)

## Optional adapter addition

The later005 [optional adapter](./optional-diagram-adapter.md) supplies one selected-segment composition with small Farmboy-owned routing seams and consumer-side physical verification. It keeps standalone independent and requires deliberate project routing, actual native capability and separate human decisions. Its guide distinguishes prescribed behavior/source availability from runtime acceptance; this later addition does not retroactively change what the earlier direction or004 source implemented. (S012)

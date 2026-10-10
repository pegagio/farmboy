---
title: Workflow graph responsibility boundaries
type: reference
sources: [S023, S030]
updated: 2026-10-09
---

# Workflow graph responsibility boundaries

The Feature 014 inventory projects source topology: authored nodes, direct parents and branches, node types, explicit delegated assignments, commands, switch outcomes, gates, and loop policies. Only explicit delegation launches a child; an absent assignment means main-task execution. Gates and switches remain in the main task. (S023)

## Responsibility contracts

Roadmap Agent lists and prepares feature selections, inspects the active feature, and prepares Close Out’s wiki source selection. Reviewer independently verifies selected-feature activation, created and repaired specification linkage, and the specification’s roadmap brief. These checks remain separate from Specifier’s request preparation and specification authoring. (S023)

Reviewer performs roadmap debrief, artifact analysis, task eligibility checks, wiki lint, wiki maintenance assessment, and final closeout readiness. Code Reviewer independently assesses Converge results, Close Out debrief results, and implementation after each pass. Specifier, Planner, and Tasker own declared specification, plan, and task corrections; Coder implements eligible tasks; Wiki Curator ingests selected sources. (S023)

Approved roadmap writes and feature-pointer activation stay in the main task. Reviewed agent names do not transfer the human’s approval authority, and empty switch bodies do not authorize downstream work without completed evidence. New approved roadmap verification and trustworthy existing verification converge on the same Close Out wiki maintenance path. (S023)

## Evidence limits

Static graph tables establish declared source topology, not live native-agent availability, model or reasoning-effort identity, or project acceptance. Exact reviewed names and declared assignments are source facts; native selection and bounded live observations require separate evidence. Adjacent diagrams present the definitions rather than independently proving runtime behavior. (S023)

## Current phase ownership and recovery roles

The Feature 014 inventory above is historical topology. The current protocol keeps human approval, gates, switches and orchestration in the main task, while only the exact assigned FlowKit-Roadmap Agent invokes the versioned owner phase-milestone write. Main preparation is read-only; it revalidates the proposal and source snapshot immediately before effect. A separate FlowKit-Reviewer checks the actual discriminated receipt and current roadmap state before subsequent work. This owner delegation transfers no human approval authority. (S030)

Phase ownership assigns planned→specced to Specify, specced→in-progress to Implement and in-progress→implemented to Close Out. Recovery adds exact FlowKit-Readiness Checker assessment alongside Roadmap Agent and Reviewer evidence producers; the main task binds artifacts to actual declared native dispatch rather than JSON role labels. Normal in-progress closeout skips earlier-edge recovery. Missing capability, stale evidence, contradictory state or partial effect stops at the affected boundary; lifecycle labels imply no verification, acceptance, publication or Git integration. See the [assessment contract](./controller-assessment-contract.md) for retained recovery witnesses. (S030)

## Related pages

- [Named agents for delegated steps](./agent-roles-and-inheritance.md)
- [Controller assessment contract](./controller-assessment-contract.md)

---
title: Codex workflow controller design history
type: concept
sources:
- S033
- S002
- S018
- S019
- S020
- S021
- S024
updated: '2026-10-11'
---

# Codex workflow controller design history

Roadmap records Feature 013 as verified: direct `flow-kit-*` skills use the FlowKit catalog alongside Specify, with reviewed step models and a main controller. Feature 013 depends on verified Feature 011, not Feature 012. Verification remains distinct from publication and feature acceptance. (S018)

Feature 013 defines eight explicitly invoked `flow-kit-*` skills with names, each bound to one installed consumer workflow. Specification completion does not establish publication or broader compatibility. (S019)

Installed workflows own prompts, commands, branches and gates. Controllers cannot copy these into skills, launch later phases, choose undeclared fallbacks or infer Git integration, roadmap verification or acceptance from completion. Manual paths remain available. (S019)

Feature 013 excludes model roles and consumer mappings; initial IDs may be non-portable. (S019)

Verified Feature 015 uses reviewed Codex custom-agent names on explicitly delegated steps, with consumer-owned native agent files and Codex-managed optional model and effort settings. Its [assignment contract](./agent-roles-and-inheritance.md) supersedes the concrete step-model approach for updated workflows without rewriting verified Feature 013 history. (S018, S020)

## Step and interaction rules

Feature 013's earlier controller used concrete models and permitted a one-step model or effort override. In updated Feature 015 source, each delegated step instead names a reviewed Codex custom agent; the controller validates all branches and probes each selected native agent before work. No per-run agent, model, or effort override is available. Main-task steps and human gates remain with the driving agent. (S002, S019)

Main-task questions and gates relay accepted answers to the same child before continuation. Completion never starts another phase. (S019)

## Stop and recovery rules

A failed child preserves partial project edits and stops without automatic rollback or retry. An interrupted main task preserves files and completed-step evidence without built-in resume. A rejected preflight creates no workflow run or recovery record. (S019)

After execution starts, a compact local record keeps workflow identity and version, step statuses, reviewed agent assignments, repository-relative changed files, and the blocker, without full child transcripts. A bundle or skill-package refresh lets an active child finish, then stops before another step and requires a new invocation. (S002, S019)

## Delivery boundary

The FlowKit catalog route installs, refreshes, and removes its direct controller skills alongside pinned Specify workflows while preserving consumer-owned state. Native Specify bundle commands manage only their declared Specify components. Skill-name collisions or locally changed owned files stop unsafe replacement or removal. These are specification delivery and ownership contracts. (S019)

## Feature 014 approved scope

Feature 014's approved controller scope supports fresh evidence-based reassessment, semantic progress checks, finite loop caps, and attributable interruption/recovery evidence. Analyze reconciles affected spec→plan→tasks layers; Implement continues existing eligible tasks without wrapper re-specification, re-planning, re-tasking, or analysis. Each workflow reaches its own evidenced conclusion or a specific bounded stop without invoking another workflow. (S018)

## Feature 014 continuation and rendering

F014 rejects command-success or digest-only completion; its [assessment contract](./controller-assessment-contract.md) governs routing. Human answers and consequential choices remain operator-owned. (S021)

Source-faithful diagrams expose exact IDs, optional agents/commands, type shapes, delegated outlines, Start, and presentation-only declared transition labels. (S021)

## Abandoned capacity proposal

Feature 018’s [capacity proposal](./workflow-agent-capacity-proposal.md) is abandoned; its requirements are historical, and the original observation remains unresolved. (S024)

## Current README boundary

Current README distinguishes historical `0.4.1` models from unreleased controller `0.9.1` with reviewed native agents and no overrides. (S002)

## Related pages

- [Agent roles and assignment inheritance](./agent-roles-and-inheritance.md)
- [Bundle and workflow model](./bundle-and-workflow-model.md)
- [Workflow lifecycle](./workflow-lifecycle.md)
- [Workflow diagram conventions](./workflow-diagram-conventions.md)

[Current protocol](./codex-workflow-controllers.md). (S033)

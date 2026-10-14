---
title: Workflow delivery validation and recovery
type: howto
sources: [S005]
updated: 2026-10-14
---

# Workflow delivery validation and recovery

The installation guide separates definition validation from runtime consumption. Before building or installing a snapshot, correct the source definition and revalidate the complete graph, including untaken branches. Switch `default` belongs beside `cases`; supported empty branches are valid skips. Template references must name earlier producers available on every route to the consumer. This delivery check does not require an output before its producer runs. (S005)

## Diagnostics and selected consumption

A definition diagnostic identifies `reason_code`, workflow and step, authored location/reference, correction, `boundary: definition`, and safe `resume_action`. Root diagnostics use `workflow` or `steps` with a null step ID. Diagnostics exclude supplied input values, rendered prompts and host paths. The guide does not specify nested JSON paths for these diagnostic details. (S005)

During execution, the controller renders the switch expression and selection metadata, chooses the branch, and resolves each selected child's inputs when that child is reached. Empty branches continue to their successor. Missing, invalid or stale output required by the selected route stops execution at the consuming step before dispatch or effect, with the authored reference, reason and safe next action. (S005)

## Safe recovery and evidence limits

Restore or rerun the required producer, then revalidate current installation and evidence within the original scope. Do not invent output, reuse an earlier pass's output or skip a gate. Manual workflow prompts follow the same selected-route consumption and stop rules. (S005)

Deterministic fixtures and simulated children can verify controller decisions and source/installed parity. They do not establish native identity or effective settings, publication, stock Spec Kit compatibility, consumer adoption, real-feature roadmap verification or acceptance. Exact named-agent probes and consumer-controlled Codex settings remain separate evidence. (S005)

The [installation lifecycle](./installation-and-release-lifecycle.md) retains delivery ownership, historical supersession and release boundaries. (S005)

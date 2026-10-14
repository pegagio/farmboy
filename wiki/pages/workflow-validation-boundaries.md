---
title: Workflow validation boundaries
type: concept
sources: [S039]
updated: 2026-10-14
---

# Workflow validation boundaries

Feature 023 specifies definition, selected-route consumption and source/installed regression boundaries within existing FarmBoy authority. These are required contracts and success criteria, not measured implementation or live-agent proof. See [Codex controllers](./codex-workflow-controllers.md) for dispatch context and [assessment contract](./controller-assessment-contract.md) for connected continuation evidence. (S039)

## Definition validity

Definition validation must cover all active owned workflow packages before installation or workflow effects, preserving deprecated Start Feature's stop-only contract. Malformed switches, cases, defaults, unsupported routes and invalid template/producer references fail even in untaken branches. Diagnostics identify workflow ID, exact step ID, offending structure/reference and actionable correction; nested `cases.default` requires moving `default` alongside `cases`. (S039)

Supported empty cases and top-level empty defaults are valid skips. Valid earlier-producer references require no output before production; unknown, route-incompatible or too-late producers fail definition validation. Definition feasibility and current output availability are separate checks. (S039)

## Selected consumption

Runtime preflight must validate the selected route and currently required inputs before the consuming step's effects. Legitimate producer-dependent availability waits until production, then current outputs are checked at consumption. Only the selected supported branch executes; untaken branches require no branch-local outputs, and supported empty selections reach their declared successor without branch-local effects. (S039)

Unsupported selected choices, invalid installed structures or missing/invalid required inputs must stop before affected effects, retain observed evidence and report an exact blocker and safe resumption action under existing policy. These boundaries grant no later phase, roadmap verification, Git integration or acceptance. (S039)

## Deterministic parity and its limits

The specification requires disposable initialized consumers using supported installation of the same snapshot to match source outcomes for preparation/source skips, empty/default routes, malformed/default rejection, producer-dependent timing and connected positive/negative continuation cases. Coverage must exercise production routing APIs and guards; isolated helpers or test-only decision reproductions do not substitute. Differences remain validation failures. (S039)

Required portable observations record component IDs, versions, source digests, tested CLI version, source coordinates, scenario, execution mode, expected/observed outcomes and effects/dispatch observed or prevented, omitting raw transcripts, secrets and absolute host paths. Deterministic simulated dispatch suffices for regression outcomes but establishes no live-agent execution, effective agent settings, publication, stock Spec Kit compatibility, consumer adoption or acceptance. Separately authorized live observations remain limited to what was observed. (S039)

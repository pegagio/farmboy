# Farmboy

Farmboy is being rebooted around Pegagio's proven, human-directed Spec Kit prompts and full feature lifecycle.

The clean reboot was approved on 16 October 2026. This branch intentionally contains a planning baseline; it does not implement a replacement workflow or retain the old code and specifications as active requirements.

## Direction and next milestone

For project direction, goals, scope or roadmap context, consult the [local project direction](docs/direction.md).

The next milestone is review of the phase-one specification, followed by review of the complete implementation plan. The approved reboot choice is to replace the active product within the existing Farmboy repository while preserving its name and history.

Phase one keeps Pegagio driving three segments: select/specify/clarify then specification review; plan/tasks/analysis-and-repair then full-plan review; implementation/convergence-and-repair/closeout then result review. Preserve interactive clarification, all existing loops and the proven source prompts. Verify native `/goal` behavior before considering custom continuation. The first acceptance is a real feature from selection through successful closeout, including clarification and interruption/resume.

Phase two introduces Diagram's queue and canonical lifecycle under human direction. Phase three adds narrow workers only after execution-return and state handling are proven. Neither phase is implemented here.

## History and provenance

This branch descends normally from pre-reboot `develop`, commit `41edab98e0b9fe935866aa7907b54714c9664f08`. It preserves the existing Farmboy repository and prior Spec Kit Flow/FlowKit naming history. Superseded code, specs, tooling and installed components are retired from this branch's active tree; their history and reviewed snapshots remain accessible through the [archive and recovery guide](ARCHIVE.md). Existing `develop`, `master`, remote refs and linked worktrees are not rewritten.

The previous tree had no repository-root license file. Historical third-party license notices, including the roadmap/wiki extension notices, remain with their archived source. This documentation baseline does not introduce or change licensing.

# Farmboy

Farmboy is being rebooted around Pegagio's proven, human-directed Spec Kit prompts and full feature lifecycle.

The clean reboot was approved on 16 October 2026. This branch began with a planning baseline. Current workflow source and its verification evidence are linked below; superseded code and specifications are not active requirements.

## Direction and next milestone

For project direction, goals, scope or roadmap context, consult the [local project direction](docs/direction.md).

The reboot began with specification review followed by full-plan review; current workflow status and remaining acceptance limits are recorded in the linked feature evidence. The approved reboot choice is to replace the active product within the existing Farmboy repository while preserving its name and history.

Phase one keeps Pegagio driving three segments: select/specify/clarify then specification review; plan/tasks/analysis-and-repair then full-plan review; implementation/convergence-and-repair/closeout then result review. Preserve interactive clarification, all existing loops and the proven source prompts. Verify native `/goal` behavior before considering custom continuation. The first acceptance is a real feature from selection through successful closeout, including clarification and interruption/resume.

Phase two introduces Diagram's queue and canonical lifecycle under human direction. Phase three adds narrow workers only after execution-return and state handling are proven. Neither phase is implemented here.

## Workflow entry points

The local workflows preserve human approval between segments. Source availability does not establish delivery acceptance or authorize the next workflow.

- **Prepare specification**: `$farmboy-prepare-specification` saves a draft and clarification/review handoff; see the [guide](docs/prepare-specification.md).
- **Prepare implementation plan**: `$farmboy-prepare-implementation-plan` starts from an approved selected specification, composes existing plan/tasks/read-only analysis with separate authorized routine repair, and stops for human full-plan review; see the [guide](docs/prepare-implementation-plan.md) and [actual verification evidence](specs/002-prepare-implementation-plan/validation/acceptance.md), including unaccepted native limitations.

- **Deliver approved plan**: `$farmboy-deliver-approved-plan` composes actual implementation, verification, convergence/repair and delivery documentation/debrief/wiki closeout, includes implemented with scoped artifacts in the final local commit, then stops for human result review; see the [guide](docs/deliver-approved-plan.md) and [actual verification evidence](specs/003-deliver-approved-plan/validation/acceptance.md). Source availability and test success do not establish human result acceptance or verified/integration authority.

All three skills also accept explicitly **externally selected** work: the caller supplies selected identity, intent, segment and accessible authoritative Git context/artifact references in an associated workspace. Farmboy checks those documents without repeating queue eligibility/activation and returns truthful outcomes/evidence for coordinator-owned review and handoff. Standalone local behavior remains available without Diagram. See [external/standalone handoff guide](docs/workflow-handoffs.md) and [Feature004 observations](specs/004-align-diagram-handoffs/validation/acceptance.md). This adds no adapter/transport, ownership service or integration executor; integration/receipt decisions remain separate.

No controller, counters, numeric repair limits, progress scoring or runtime accounting/tracking store is added. A completed preparation Goal or passing analysis never approves the plan, implements work, commits or pushes.

## History and provenance

This branch descends normally from pre-reboot `develop`, commit `41edab98e0b9fe935866aa7907b54714c9664f08`. It preserves the existing Farmboy repository and prior Spec Kit Flow/FlowKit naming history. Superseded code, specs, tooling and installed components are retired from this branch's active tree; their history and reviewed snapshots remain accessible through the [archive and recovery guide](ARCHIVE.md). Existing `develop`, `master`, remote refs and linked worktrees are not rewritten.

The previous tree had no repository-root license file. Historical third-party license notices, including the roadmap/wiki extension notices, remain with their archived source. This documentation baseline does not introduce or change licensing.

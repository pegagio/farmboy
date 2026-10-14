---
title: Workflow graph responsibility boundaries
type: reference
sources: [S033]
updated: 2026-10-14
---

# Workflow graph responsibility boundaries

Historical Feature 014 topology and FlowKit phase assignments remain in [graph responsibility history](./workflow-graph-responsibility-history.md). The canonical protocol now requires exact FarmBoy names and `farmboy` delegation metadata; only explicit delegated steps launch children, while human gates, switches and orchestration stay in main. Source assignments are declarations, not live availability or model-setting evidence. (S033)

## Phase ownership

Specify owns planned→specced, Implement owns specced→in-progress, and Close Out owns in-progress→implemented. FarmBoy controller policy prepares current evidence and an explicit amendment for the assigned FarmBoy Roadmap Agent’s ordinary generic `speckit.flow-roadmap.write` invocation. Roadmap supplies contained configuration and generic writer/review interfaces, requiring version 0.4.0 or later; no extension lifecycle helper or phase-milestone token participates. (S033)

A separate FarmBoy Reviewer independently checks actual effect, main-retained command time, current source and ledger readback. Applied, not-applied and indeterminate receipts preserve partial-effect evidence; retry reassesses the original receipt rather than blindly repeating a write. Human approval is not transferred by delegation, and implemented status does not imply verified or accepted. (S033)

## Recovery and correction assignments

Earlier-edge recovery requires FarmBoy Roadmap Agent brief/linkage, FarmBoy Reviewer preparation and attestation, and FarmBoy Readiness Checker assessment. Main records and validates retained history and dispatch witnesses. Normal in-progress closeout skips earlier-edge recovery; stale evidence, unavailable assignments, contradictory state or partial effects stop at the affected boundary. (S033)

FarmBoy Code Reviewer independently evaluates implementation findings and whole-task fulfillment against original baselines and current evidence. FarmBoy Tasker owns bounded task revisions/marker changes after review; such edits earn no substantive progress themselves. Exact names and assignments do not establish effective settings, native launch or project acceptance. (S033)

## Related pages

- [Assessment contract](./controller-assessment-contract.md)
- [Codex controllers](./codex-workflow-controllers.md)
- [Loop limits](./workflow-loop-baselines-and-limits.md)

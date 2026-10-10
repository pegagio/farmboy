---
title: Feature 020 workflow lifecycle
type: concept
sources: [S027, S029]
updated: '2026-10-09'
---

# Feature 020 workflow lifecycle

## Feature 020 phase-owned milestones

Specify owns `planned` → `specced` after author quality, required clarification, independent review, roadmap brief, linkage and prerequisite evidence. Implement owns `specced` → `in-progress` after current reviewed artifacts, preparation, exact assignments and authorized eligible scope, before substantive coding. Close Out owns `in-progress` → `implemented` after current attributable completion/convergence, independent code review and required validation with no unresolved buildable defect. Labels, checkboxes and command success alone prove none of these milestones. (S027)

Delivered governing contracts and the trusted owning-phase invocation authorize routine advancement with immediate revalidation. Stale states recover through evidence-supported adjacent transitions, preserving real occurrence times and history; unavailable or ambiguous proof blocks. Consistent advanced states are retained without downgrade or fabricated events. `implemented` precedes the separate explicit `verified` gate and implies no acceptance, release or Git integration. (S027)

## Effect and recording outcomes

The lifecycle outcome separates `effect_state` from `record_state`. Only `applied` is a transition receipt: actual event identity/time, committed provenance and observed before/after bytes must establish the effect. An independently established applied effect survives receipt persistence failure; the command report must acknowledge the recording failure without claiming a durable receipt exists. (S029)

A `no-op` is an event-free assessment that retains state without a new transition identity/time or roadmap amendment. `not-applied` requires proof the proposed effect did not occur; an error exit or missing receipt alone is insufficient. `indeterminate` retains uncertainty and known proposal/observation data, never unestablished committed identity, occurrence time or final digest. Candidate or old hashes cannot masquerade as final readback. (S029)

Recovered recording is permitted only for independently established applied effects using existing event provenance and observed bytes; it retains the original actual occurrence time. Separately assigned Reviewer verification precedes the next action or safe retry. Report successful effects and later failures separately, without fabricated receipts, blind repetition or automatic rollback; partial success proves no overall completion. [Scoped evidence](./feature020-artifact-flow-back-and-convergence.md) preserves the corresponding task-accounting boundary. (S029)

## Related historical contracts

The [earlier topic contracts](./workflow-lifecycle.md) preserve dated source history alongside this current specification contract. (S027)

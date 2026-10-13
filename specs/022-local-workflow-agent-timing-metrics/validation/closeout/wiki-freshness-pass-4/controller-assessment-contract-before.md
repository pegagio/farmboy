---
title: Controller assessment contract
type: concept
sources: [S033]
updated: 2026-10-11
---

# Controller assessment contract

The canonical FarmBoy protocol supersedes the historical FlowKit protocol namespace; the earlier assessment and recovery contracts remain in [assessment history](./controller-assessment-history.md). Current source uses `farmboy.delegated` and exact `farmboy.agent` assignments, with workflow decisions retained in the installed graph. (S033)

## Evidence and recovery

New run summaries use `.specify/farmboy-controllers/runs/<run-id>/summary.json` after successful preflight. They retain workflow identity/version/digest, install fingerprints, exact assignments, step and iteration states, repository-relative changed paths, outcomes and bounded blockers. No transcripts, secrets or absolute host paths enter those records. Changed installation or workflow evidence stops further nodes; interrupted mutation needs fresh safe-scope assessment before resumption. (S033)

Assessment envelopes distinguish complete, continue, needs-human and blocked, using stable reason/action grammar and state-specific routing. Progress requires independently supported prior-finding or eligible-task resolution; command success, changed bytes and task markers do not suffice. Original finding preimages remain separate from fresh current proof, so regression-only repair can demonstrate progress without manufactured source churn. (S033)

Earlier-edge Close Out recovery requires current Roadmap Agent brief, independent Reviewer preparation, recorded readiness/start history, Readiness Checker evidence and Reviewer attestation. Main retains the actual native dispatch witness and sends its immutable path/digest to that same Reviewer child. The child cannot choose a trusted witness; later bookkeeping cannot replace it. Actual occurrence history and status-only specification bridges require retained authorization/effect evidence, never reconstructed task-marker history. (S033)

## Related pages

- [Codex controllers](./codex-workflow-controllers.md)
- [Graph responsibilities](./workflow-graph-responsibility-boundaries.md)
- [Loop limits](./workflow-loop-baselines-and-limits.md)

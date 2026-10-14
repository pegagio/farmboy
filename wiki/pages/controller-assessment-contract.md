---
title: Controller assessment contract
type: concept
sources: [S033, S039]
updated: 2026-10-14
---

# Controller assessment contract

The canonical FarmBoy protocol supersedes the historical FlowKit protocol namespace; the earlier assessment and recovery contracts remain in [assessment history](./controller-assessment-history.md). Current source uses `farmboy.delegated` and exact `farmboy.agent` assignments, with workflow decisions retained in the installed graph. (S033)

## Evidence and recovery

New run summaries use `.specify/farmboy-controllers/runs/<run-id>/summary.json` after successful preflight. They retain workflow identity/version/digest, install fingerprints, exact assignments, step and iteration states, repository-relative changed paths, outcomes and bounded blockers. No transcripts, secrets or absolute host paths enter those records. Changed installation or workflow evidence stops further nodes; interrupted mutation needs fresh safe-scope assessment before resumption. (S033)

Assessment envelopes distinguish complete, continue, needs-human and blocked, using stable reason/action grammar and state-specific routing. Progress requires independently supported prior-finding or eligible-task resolution; command success, changed bytes and task markers do not suffice. Original finding preimages remain separate from fresh current proof, so regression-only repair can demonstrate progress without manufactured source churn. (S033)

Earlier-edge Close Out recovery requires current Roadmap Agent brief, independent Reviewer preparation, recorded readiness/start history, Readiness Checker evidence and Reviewer attestation. Main retains the actual native dispatch witness and sends its immutable path/digest to that same Reviewer child. The child cannot choose a trusted witness; later bookkeeping cannot replace it. Actual occurrence history and status-only specification bridges require retained authorization/effect evidence, never reconstructed task-marker history. (S033)

Main may retain a validated historical Tasker prefix through `retained_task_tracking_count` and `retained_task_tracking_sha256`, binding canonical JSON of the original scope digest and exact successor prefix. Retention follows current validation and precedes later source effects. Recovery may extract that prefix only from an unchanged immutable pre-effect artifact whose original digest is independently anchored in execution history; child-selected digests and current source bytes cannot establish historical trust. The complete chain still receives structural, marker, description, scope, predecessor and digest validation. Bound-prefix paths and hashes remain historical witnesses; new successors and current eligibility, fulfillment, Reviewer, readiness and history-event evidence require current validation. Missing prefix binding preserves strict legacy current-evidence checks, so stale unbound records block. Scope and post-pass capture return the validated complete prefix count/digest for main to retain before further effects. (S033)

## Feature 023 connected evidence contract

Feature 023 requires executable coverage of assessment → eligible source dispatch → independent review → marker-only task tracking → post-pass capture → guarded re-entry. Both reviewed substantive task resolution and legitimate reviewed source correction with differing preimages must be exercised through production routing and guards; isolated helper tests alone do not satisfy this requirement. These are coverage obligations, not recorded successful runs. (S039)

Re-entry must retain trusted pre-effect historical evidence with original scope binding and digests, independently validate required current evidence, and permit legitimate reviewed preimage differences without replacing history. Forged, altered, missing or unbound history cannot be recreated from current files, tracking changes, post-pass capture or fresh assessment. (S039)

Negative coverage must isolate each blocker with otherwise valid surrounding conditions: invalid historical binding, stale required current evidence, unauthorized task edits, missing required outputs, no substantive progress and exhausted declared limits. Command success, markers, administrative updates, question answers and child restarts neither substantiate resolution nor reset limits. Feature 023 preserves existing accounting rather than redesigning it; the [validation boundaries](./workflow-validation-boundaries.md) define required parity and observation limits. (S039)

## Related pages

- [Codex controllers](./codex-workflow-controllers.md)
- [Graph responsibilities](./workflow-graph-responsibility-boundaries.md)
- [Loop limits](./workflow-loop-baselines-and-limits.md)

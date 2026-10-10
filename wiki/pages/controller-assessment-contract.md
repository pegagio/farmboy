---
title: Controller assessment contract
type: concept
sources: [S021, S022, S023, S030]
updated: 2026-10-09
---

# Controller assessment contract

Feature 014 requires assessment `reason_code` and any `resume_action` to match `^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$`: lowercase letters and digits separated by single hyphens, without spaces or underscores. Prompts that may emit these fields state the grammar, and the controller rejects malformed values before routing. (S021)

A `complete` envelope omits `next_step_id`, `gate_step_id`, and `resume_action`. A `continue` envelope contains only `next_step_id` targeting the declared loop body; a `blocked` envelope contains only a stable `resume_action`. Clean findings cannot justify an invalid envelope. Live verification records the rejection, corrects ambiguous source guidance, and retries refreshed source before claiming success. (S021)

Required operator input uses `blocked` with the exact question and resumption action. Shared paths remain permissible only when completed evidence determines downstream authorization; collapsed routing cannot collapse exact human choices or allow unverified success. Legacy `needs-human` remains compatibility for explicitly declared gates. (S021)

Authoring agents perform core-command self-checks, prerequisites, and quality checklists. These do not replace independent Reviewer or Code Reviewer assessment: authors cannot act as their own independent reviewers. This distinction changes no workflow nodes or review scope; Specify linkage and roadmap checks remain distinct. (S021)

The plan distinguishes read-only baseline/final checks from correction capacity; each workflow requires specific prior-finding or task resolution before another pass. Exact entry modes and limits are recorded in the [workflow loop reference](./workflow-loop-baselines-and-limits.md). (S022)

Close Out supplies each ingestion child the exact source-backed correction checklist alongside its unchanged single source argument. The checklist identifies the specific missing or stale claim to correct; independent assessment credits verified prior-claim resolution while retaining outstanding findings, rather than treating whole-source coverage as the progress unit. (S021)

Empty switch branches rejoin the next declared step, but a join grants no downstream authorization without completed evidence. Close Out’s newly approved verification and trustworthy existing verification paths join shared wiki maintenance; blocked or unapproved paths cannot acquire verified status through that join. Graph responsibilities remain explicit in the [workflow boundary reference](./workflow-graph-responsibility-boundaries.md). (S023)

## Current evidence and recovery contract

The main controller retains an immutable original finding baseline before coding. Unresolved findings keep original source preimages; fresh independently validated review proof is recorded separately as current evidence. Closure compares current source against the original preimage, allowing a subsequent regression-only repair without artificial source churn. Legacy recovery uses main-selected, independently verified historical baselines; child-created files or supplied hashes grant no authority. Current proof must match actual files, and labels, reports, markers or tests alone prove neither source correction nor whole-task fulfillment. A resolved finding can earn progress while its owning task remains open; whole-task closure needs independent completion evidence and no unresolved owned finding. (S030)

Earlier-edge Close Out recovery requires fresh Roadmap Agent brief/linkage, Reviewer preparation judgment, main-recorded readiness review and validated start history, Readiness Checker assessment, then Reviewer start attestation. History preserves the actual Implement identity, occurrence time, completed effects, original/current scope and independently evidenced status-only specification bridge; task markers cannot reconstruct history. After exact native Reviewer dispatch, the main task captures an immutable run-summary witness and relays its path/digest to that same child before attestation. The child waits for that reference; the main task validates identity and preserves its returned attestation unchanged. Later bookkeeping cannot replace the captured witness. Missing or changed binding blocks lifecycle preparation. (S030)

## Related pages

- [Codex workflow controller design](./codex-workflow-controllers.md)
- [Closeout and verification boundary](./closeout-and-verification-boundary.md)
- [Workflow loop baselines and limits](./workflow-loop-baselines-and-limits.md)

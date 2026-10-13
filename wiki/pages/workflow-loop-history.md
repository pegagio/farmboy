---
title: Workflow loop baselines and limits history
type: reference
sources: [S022, S030, S033]
updated: 2026-10-12
---

# Workflow loop baselines and limits history

Feature 014's plan assigns explicit evidence baselines and finite continuation capacity to each workflow. A validated `continue` must resolve a prior finding or eligible task against the preceding assessment. Changed digests, populated files, new questions, and command success alone do not establish progress. Untrustworthy comparison, failed prerequisites, stale evidence, repeated unresolved findings, or a still-incomplete final pass stop continuation. (S022)

## Assessment entry and capacity

Correction passes differ from read-only checks, so final confirmation grants no additional correction. (S022)

| Workflow | Baseline and allowed capacity |
|---|---|
| Clarify | Current significant ambiguity IDs and incorporated answers; five body passes, retaining the five-question cap per session. (S022) |
| Plan and Tasks | Required structure plus independent semantic findings against approved artifacts; five body passes each. (S022) |
| Analyze and Remediate | `assessment_only_first_pass: true` skips corrections for a read-only analysis baseline; six total passes permit five shared-waterfall corrections. (S022) |
| Implement | Unfinished eligible task IDs recorded before entry; five body passes, continuing only after a prior eligible task completes. (S022) |
| Converge | `assessment_before_correction: true` runs core convergence and shared assessment before each guarded correction; six command/assessment passes permit five corrections and final confirmation. (S022) |
| Close Out | Six fresh debrief checks permit five corrections; a separate sibling wiki loop permits five single-source ingest/lint/assessment passes. (S022) |
| Wiki Lint Update | Fresh lint findings and registered source identities; 26 lint/assessment checks permit 25 single-source refreshes and final confirmation. (S022) |

## Evidence needed to continue

Clarify must resolve a prior significant ambiguity in the specification; discovering a new question cannot substitute for resolving an unchanged earlier one. Plan and Tasks require independent resolution of structural or semantic findings, each carrying a stable ID, artifact location, violated requirement or constraint, and exact correction handoff. Planner and Tasker retain author-owned correction. (S022)

Analyze and Remediate requires fresh analysis after ordered artifact reconciliation. Converge requires fresh convergence after waterfall reconciliation, analysis, eligibility verification, and implementation; an intermediate blocker stops before another pass. Findings and task IDs remain scoped to the selected invocation, with reviewed assessment deriving stable IDs from inspectable artifacts when commands cannot supply them. (S022)

Closeout wiki progress requires substantive coverage or stale-claim resolution within the curated sources; timestamps receive no progress credit. Wiki Lint Update preserves unrelated findings during safe stale refreshes and retains pending source identities on bounded stops. Only a validated complete latest wiki assessment permits closeout commit-readiness reporting. (S022)

## Design ownership

Versioned workflow YAML owns prompts, branches, gates, loop conditions, and caps. The shared controller owns generic validation, outcome checking, progress comparison, and iteration-aware recovery. Native agent instructions remain consumer-owned Codex configuration, outside the bundle and any FlowKit role map. (S022)

## Historical retained scope and recovery limits

Historical table. Current Implement retains requested scope independently of eligibility and tracks Coder sessions/source attempts under the exact five-pass limit. Persisted session starts precede dispatch; failures and question-stopped sessions count. Same-child answers add evidence without another session. Preparation, answers, eligibility refresh, markers and Tasker changes never reset either budget. Continuation after source work requires independently evidenced prior-finding or scoped-task resolution and current history; no progress or exhausted capacity stops. (S030)

Close Out recovery substantiates only three adjacent edges: planned→specced→in-progress→implemented, preserving actual occurrence evidence. Verification requires separate explicit approval. Wiki maintenance retains five single-source passes; timestamps earn no progress. Recovery never reopens a capped Implement run. (S030)

## Related pages

- [Controller assessment contract](./controller-assessment-contract.md)

[Current protocol](./workflow-loop-baselines-and-limits.md). (S033)

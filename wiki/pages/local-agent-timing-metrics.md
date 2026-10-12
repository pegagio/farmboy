---
title: Local agent timing metrics design
type: decision
sources: [S018, S036]
updated: 2026-10-12
---

# Local agent timing metrics design

Feature 022 defines a simple local metrics collection-to-workbook design for FarmBoy and its consuming projects. Its roadmap requirements establish intended scope, not implemented instrumentation, release or adoption. (S018)

## Collection and delivery boundary

Agent invocations use the computer's wall clock through a small local adapter. Concurrent emissions have separate uniquely named structured files under shared `~/.farmboy/metrics`; shared appends and file locking are excluded. Collection failures warn and continue. Clock drift and skew are accepted; time is the only cost, with no token, monetary, CPU or distributed accounting. (S018)

FarmBoy Metrics Report (`farmboy-metrics-report`) is explicitly invoked within FarmBoy and excluded from consumer installation. It gathers completed records into a simple XLSX table while preserving source files; the operator creates graphs. Generic timing support remains available to consuming projects. (S018)

## Timing and identity

The specification measures controller-issued `probe`, `execution`, `continuation` and `retry` turns, including observed rejected dispatches. Each turn gets a unique `invocation_id`; `run_id` groups one workflow invocation, including preflight. A question ends a turn; same-child continuation starts another, excluding human waiting. Pending acknowledgements and polling remain timed. An unobserved end produces no invented completion. Signed `duration_ms` uses local-clock observations rendered as UTC millisecond timestamps; zero and negative values remain valid. No outcome or substitute status is recorded. (S036)

Record schema version 1 uses one JSON object per completed emission file. Exact agent/skill/workflow names come from invocation context; `project_label` uses a known nonpersonal logical identity or `unspecified`, excluding personal details, host paths, prompts and transcripts. Optional `model` and `effort` come from exact-name project agent TOML matching, independently of filenames; they describe explicit file settings, not verified runtime values. Unavailable settings are null; no dispatch override or inherited/global resolution follows. (S036)

## Workbook contract

The report discovers one fixed top-level candidate snapshot, excludes unfinished files and later arrivals, and reads each candidate at most once within 64 KiB. Invalid candidates are skipped with visible counts. Identical invocation copies collapse; conflicting valid copies exclude the whole invocation. Sources remain unchanged. Missing/empty usable input yields headers and zero rows; an inaccessible directory or more than 1,000,000 accepted rows fails visibly. (S036)

One uniquely named workbook under `~/.farmboy/metrics/reports/` contains one simple table. Its thirteen columns are `invocation_id`, `run_id`, `project`, `skill`, `workflow`, `step`, `invocation_kind`, `agent`, `model`, `effort`, `started_at`, `finished_at`, `duration_ms`. JSON retains `schema_version`, which Excel omits. Rows sort by start timestamp then invocation ID; text remains literal, duration numeric and unknown settings blank. No charts, dashboards, automatic interpretation or CSV export is included. Reporting preserves previous outputs and never initiates another workflow or acceptance action. (S036)

## Related pages

The [bundle model](./bundle-and-workflow-model.md) describes delivery boundaries; [controller design](./codex-workflow-controllers.md) describes invocation ownership. These existing contracts remain distinct from the proposed metrics behavior. (S018)

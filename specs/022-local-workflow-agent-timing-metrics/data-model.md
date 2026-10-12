# Data Model: Local Workflow Agent Timing Metrics

This model implements the current [specification](spec.md) without outcome classification. Identities correlate observations; they never establish task success or governance authority.

## Table of Contents

The entities separate transient timing context, published evidence and report output.

- [Run and Turn Context](#run-and-turn-context)
- [Metric Record](#metric-record)
- [Report Snapshot and Groups](#report-snapshot-and-groups)
- [Workbook and Summary](#workbook-and-summary)

## Run and Turn Context

`metrics_run_id` is a separate UUID generated after validated inspection and before probes, retained in the existing main-task context for one workflow invocation. It supplies the metric record's `run_id` across probes, working turns and same-child continuations, including resumption of that retained context. It is independent of the recovery summary's `run_id`; it is not passed to recovery creation or used to name a recovery directory.

Metrics context is only a correlation value; it creates no workflow state, pending file, journal or per-run metrics directory. Recovery ID generation, summary creation and updates remain unchanged. A failed preflight may leave observed metric files without a workflow summary. Metrics grant no recovery or resumption authority.

Each turn has an `invocation_id` UUID, run identity, exact step/agent/skill/workflow identities, safe project label and observed integer `started_ms`. The start token is transient and has no prompt, result, raw child identifier or pathname. A parent may hold multiple tokens for simultaneous children. The working child remains associated through main-task context only.

Lifecycle: prepare metadata → observe start → issue native request → retain through pending acknowledgements/polls → observe ending → publish completed record. An ending may be a question, failure or interruption, but that distinction is not persisted in metrics. A returned question closes the turn before human wait; same-child continuation receives a new token/identity. Unknown end or lost token yields no completed record. Repeated observations cannot publish a second file for that collector identity.

## Metric Record

The metric record contains twelve required fields and optional nullable `model` and `effort`. Reporting compares all fourteen fields and exports thirteen independently ordered workbook columns, omitting `schema_version`. Collector output includes the two optional keys even when `null`; reporting accepts their absence as `null` and tolerates other unknown fields without exporting them.

| Field | Type | Validation and meaning |
| --- | --- | --- |
| `schema_version` | Integer | Exactly `1`; booleans are not integers for validation. |
| `invocation_id` | String | Nonempty opaque turn identity; collector produces UUIDs, report does not reinterpret it as a child ID. |
| `run_id` | String | Nonempty opaque metrics correlation identity for one workflow invocation, retained across probes and modeled turns; independent of recovery identity. |
| `step_id` | String | Exact modeled ID; `preflight` for probes. |
| `invocation_kind` | String enum | `execution`, `continuation`, `retry`, `probe`. |
| `agent_name` | String | Exact supplied native dispatch name. |
| `skill_id` | String | Exact invoking FarmBoy skill ID. |
| `workflow_id` | String | Exact invoking installed FarmBoy workflow ID. |
| `project_label` | String | Known nonpersonal logical identity or `unspecified`; grouping label, not repository identity. |
| `started_at` | String | Valid UTC timestamp `YYYY-MM-DDTHH:MM:SS.mmmZ`. |
| `finished_at` | String | Same representation; allowed to equal or precede start. |
| `duration_ms` | Integer | Signed difference of timestamp epoch milliseconds; reject booleans, fractions and mismatched arithmetic. |
| `model` | String or null | Explicit `model` in the uniquely matching project agent TOML file; optional, absent normalizes to null. |
| `effort` | String or null | Explicit `model_reasoning_effort` in that file; optional, absent normalizes to null. |

JSON must be a UTF-8 object no larger than 65,536 bytes, without duplicate keys, nonfinite numeric constants or missing required values. A string projected to Excel must be representable without truncation: at most 32,767 characters and legal XML text characters. Reject unrepresentable strings as invalid-contract inputs rather than silently changing their value. No Unicode normalization or whitespace trimming occurs. All required strings are nonempty; fields resembling formulas remain valid literal text.

Read only explicit project agent-file settings by exact `name`; do not derive the filename from the display name, resolve global/inherited settings or infer values from FarmBoy defaults. Missing/unusable values become null. Optional strings obey the same literal-text bounds as other strings. Settings are metadata only and do not alter dispatch.

Collector metadata is an explicit allowlist drawn from validated assignments/context; no result field, replacement success/status, prompt, transcript, token/monetary accounting, personal detail or absolute host path is added. Reporter validation does not certify that an arbitrary user-authored record actually came from a workflow; records are local observations, not authenticated authority.

Completed filenames use `metric-<UUID>.json`. The emission filename normally contains the invocation UUID, but report equality uses the payload and allows a copied record under another completed-convention name. Temporary names are hidden `.metric-<UUID>-<random>.tmp`; they never qualify as completed input. Records remain immutable to collection and reporting.

## Report Snapshot and Groups

A report retains one list from a single top-level completed-file discovery. Discovery closes before candidate validation starts. It excludes symlinks, subdirectories, temporary/unrelated names and reports; no recursive scan or rescan occurs. Files completed after the retained list are for the next report. Enumeration is a filesystem listing, not a transactional snapshot of the whole directory.

Each candidate receives one bounded validation attempt. Open without following symlinks, confirm a regular file on the opened descriptor, reject oversized metadata, read at most 65,536 bytes, and reject detected replacement/change as unreadable input. Do not wait for writers or inspect unlimited bytes. Files that disappear after discovery count as unreadable, rather than silently reducing candidate totals.

Group only valid documented-field projections by invocation identity. Each group stores the first fourteen-field tuple after normalizing absent settings to null, number of candidates and a conflict flag. Equivalent subsequent tuples increase the count; any unequal tuple sets an irreversible conflict for that report, even if later copies match the first. Invalid copies never participate in choosing a valid value. Unknown extra fields, JSON key order and whitespace do not create conflicts.

Nonconflicting groups contribute one accepted row and `size-1` duplicate copies. Conflicting groups contribute zero rows, one conflicting identity and their full candidate count to conflicting files. Sort accepted rows lexically by canonical `started_at`, then `invocation_id`; canonical timestamps make that chronological UTC ordering. The 1,000,000-row ceiling applies after grouping, not raw file discovery.

## Workbook and Summary

One uniquely named `reports/farmboy-metrics-<report-UUID>.xlsx` contains worksheet `Metrics`, table `FarmBoyMetrics`, exactly the accepted rows and these thirteen columns in order: `invocation_id`, `run_id`, `project`, `skill`, `workflow`, `step`, `invocation_kind`, `agent`, `model`, `effort`, `started_at`, `finished_at`, `duration_ms`. Excel headers shorten `step_id` to `step`, `agent_name` to `agent`, `skill_id` to `skill`, `workflow_id` to `workflow`, and `project_label` to `project`; all other headers retain their field names. JSON keys remain unchanged. `schema_version` remains in JSON validation and duplicate comparison only. The integer duration column remains numeric; non-null other fields use explicit string cell types, including timestamps. Null settings become blank cells. Zero input uses `A1:M1` with no fake observation. One million accepted rows use `A1:M1000001`, within Excel's row limit.

The report summary belongs to skill output, not metric records or extra workbook sheets. It exposes output location and integer counts: `candidate_count`, `accepted_count`, `duplicate_count`, `conflicting_invocation_count`, `conflicting_file_count`, `invalid_counts` by category and `skipped_count`. Categories and count identities are defined in [the report contract](contracts/metrics-report.md).

A report UUID names an output artifact only; it is not another agent invocation metric. Source hashes used in validation are separate evidence and are not automatic workbook columns. Missing/inaccessible output or capacity failure publishes no successful workbook; no sources or prior reports are changed.

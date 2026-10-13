# Contract: FarmBoy Metrics Report

`farmboy-metrics-report` is explicitly invoked within FarmBoy and remains outside consumer controller/workflow inventories. Its proposed source is `skills/farmboy-metrics-report/`, following the existing maintainer source-skill pattern. Reporting launches no FarmBoy workflow or subsequent phase.

## Invocation and Environment

The maintainer invokes `$farmboy-metrics-report`; the skill checks the reviewed source layout and executes its source `scripts/metrics_report.py` with the prescribed skill-tools interpreter. Default input is `~/.farmboy/metrics`, output is its `reports/` child. The script exposes no initial config-file system, watch mode, cleanup, analysis or format selection. Importable `export_workbook(directory=...)` provides test injection, not an automatically chosen production destination.

The operator approved openpyxl 3.1.5 and required et-xmlfile for this maintainer-only design on 2026-10-11. Planning installed neither package. Missing dependencies fail visibly before output creation; the skill never installs them automatically. Consumers receive neither the skill nor these dependencies. FarmBoy source setup documents its local discovery symlink and separately authorized dependency preparation.

## Snapshot and Validation

Perform one top-level completed-convention discovery and close the retained list before reading candidates. Ignore directories, symlinks, hidden temporary names, unrelated filenames and prior reports. No recursion, rescan or waiting for writers. Missing input means zero candidates; an inaccessible existing directory is `input-inaccessible`, a report failure rather than an empty result.

Open each retained candidate once without following symlinks; verify regular-file identity, bound reads to 65,536 bytes and reject detected replacement/change. Invalid categories are `unreadable`, `oversized`, `malformed-json`, `unsupported-schema`, `invalid-contract`. Use one category per invalid candidate, with unreadable/oversized checks before parse, malformed JSON before schema, and supported schema before field validation. Validate via [the version-1 contract](metric-record.md). Never print raw candidate contents or absolute input paths in warnings.

Project the twelve required fields plus `model` and `effort`, normalizing missing settings to null. Equivalent projections sharing `invocation_id` yield one row. Any differing valid projection makes that whole identity conflicting, with no row regardless of later copies. Ignore extra fields for equality and columns. Invalid candidates do not become an authoritative variant or block other groups.

## Workbook

Sort accepted rows by canonical `started_at` then `invocation_id`, and fail `capacity-exceeded` above 1,000,000 accepted rows. Do not truncate, split or generate multiple workbooks. One workbook contains one worksheet `Metrics` and one table `FarmBoyMetrics`, with Excel headers in this order: `invocation_id`, `run_id`, `project`, `skill`, `workflow`, `step`, `invocation_kind`, `agent`, `model`, `effort`, `started_at`, `finished_at`, `duration_ms`. Map record fields `step_id`, `agent_name`, `skill_id`, `workflow_id`, and `project_label` to headers `step`, `agent`, `skill`, `workflow`, and `project`, respectively; JSON field names and duplicate equality remain unchanged. `schema_version` remains required for JSON validation and duplicate comparison but is omitted from Excel. Duration is numeric; non-null other values are explicitly typed literal strings. Null settings are blank cells. No formulas, links, charts or extra worksheets are generated.

Zero accepted input still produces the thirteen headers and a zero-data-row table `A1:M1`; no synthetic blank record. Header-only interoperability must be verified in Excel. For nonempty input, the table covers header plus exactly the accepted rows.

Stage uniquely under `reports/`, close successfully and publish by no-clobber hard link to `farmboy-metrics-<report-UUID>.xlsx`. Repeated reports produce distinct names; collisions/storage/write errors fail visibly and preserve earlier outputs. Source files—including invalid/unfinished ones—remain byte-for-byte unchanged. No successful output is announced before publication succeeds. A successful output location may be displayed as `~/.farmboy/metrics/reports/<name>.xlsx`, avoiding host-specific paths in portable evidence.

## Summary Counts

The skill returns a summary alongside the workbook location. Counts are about input/export handling and never agent outcome classification.

| Field | Meaning |
| --- | --- |
| `candidate_count` | Number of retained completed-convention candidates. |
| `accepted_count` | Distinct nonconflicting valid identities; equals workbook data rows. |
| `duplicate_count` | Extra valid copies in accepted nonconflicting groups only. |
| `conflicting_invocation_count` | Number of excluded valid identity groups with differing projections. |
| `conflicting_file_count` | All valid candidate copies belonging to those conflicting groups. |
| `invalid_counts` | Per-category invalid candidate counts. |
| `skipped_count` | Sum of invalid counts plus conflicting file count. |

The partition is `candidate_count = accepted_count + duplicate_count + skipped_count`. Conflict file counts include all copies, with no double counting as duplicate copies. For example, two accepted identities, one extra identical copy, two conflicting files for one identity and four invalid candidates give candidate count 9, accepted 2, duplicate 1, conflict identities 1, conflict files 2 and skipped 6.

Missing/empty/all-invalid/all-conflicting input yields zero rows and the visible counts. Partial usable input still exports. Directory, dependency, capacity or output failure is a report failure, not a collection warning or successful zero-input report. No source repair, authority inference, rescheduling, cleanup or acceptance action follows.

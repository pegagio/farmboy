# Validation Guide: Local Workflow Agent Timing Metrics

This guide describes validation for Feature 022. The deterministic commands below are acceptance targets; the live observations recorded later document the tested FarmBoy and disposable-consumer paths. Collection defaults to `~/.farmboy/metrics`; use injected temporary directories in tests so validation never touches real observations.

## Table of Contents

The sequence separates environment checks, deterministic evidence, delivery verification and live use.

- [Prerequisites](#prerequisites)
- [Deterministic Contracts](#deterministic-contracts)
- [Consumer Delivery](#consumer-delivery)
- [Live Round Trip](#live-round-trip)
  - [Observed live round trip (2026-10-12)](#observed-live-round-trip-2026-10-12)
- [Evidence and Limits](#evidence-and-limits)

## Prerequisites

Use the repository's pinned Python/Specify environment. The maintainer report uses the operator-approved openpyxl 3.1.5 and required et-xmlfile dependency in the prescribed skill-tools environment. Consumer installations do not receive these report dependencies.

```bash
mise run python:prepare
mise run python:check
mise exec -- specify --version
```

For scripts belonging to or validating skills, use the prescribed `~/.codex/venvs/skill-tools/bin/python` and verify the required imports before report testing. If a dependency is missing, report the issue; do not alter that environment automatically. Ordinary repository tests use prepared `mise exec -- python`. No workbook dependency is installed in disposable consumers.

Implementation must document a source-skill discovery symlink for `skills/farmboy-metrics-report/` inside FarmBoy only, following the existing renderer pattern. Do not add the report skill to consumer installation or invoke a workflow to generate a workbook.

## Deterministic Contracts

The proposed tests below should create bounded temporary directories and inject a fixed clock. They must assert behavioral contracts, not duplicate implementation internals.

```bash
~/.codex/venvs/skill-tools/bin/python -m unittest discover -s tests -p 'test_metrics.py'
~/.codex/venvs/skill-tools/bin/python -m unittest discover -s tests -p 'test_metrics_report.py'
mise exec -- python -m unittest discover -s tests -p 'test_controller.py'
mise exec -- python -m unittest discover -s tests -p 'test_catalog.py'
mise exec -- python -m unittest discover -s tests -p 'test_bundle_lifecycle.py'
git diff --check
```

Collection tests cover start/finish, pending acknowledgement/polling, question then continuation with a deliberately long human interval, retry, probe/preflight, rejected dispatch and observed interruption. Assert exact metadata, distinct UUIDs, run continuity, correct kind and twelve required fields plus nullable `model` and `effort`, without outcome/substitute status. Zero/equal and backward readings yield signed arithmetic at millisecond precision. Loss of the end/token yields no fabricated completion. Inject clock, metadata, unavailable helper, permission, full-disk and collision failures; original native result, routing and gates stay unchanged with category-only warnings.

Launch at least twenty actual simultaneous writers for two safe labels into one temporary directory. Verify twenty distinct complete JSON files, no overwritten records, no accepted stage files, no shared append or lock, and twenty matching exported rows. Exercise an existing final-name collision and unsupported hard link; neither may fall back to overwrite or a partially visible completed file.

Report tests use a fixed mixed snapshot with valid records, an identical copy, conflicting valid copies, unknown extra fields, malformed JSON, unsupported schema, missing/wrong fields, invalid duration, >64 KiB files, unreadable/disappearing candidates, symlinks, directories and unrelated/temporary names. Bound each attempted read to 65,536 bytes; count each invalid candidate once. Add a completed file after discovery and confirm exclusion until the next report. Assert the summary partition in [the report contract](contracts/metrics-report.md).

Test missing/empty/all-invalid/all-conflicting input, an inaccessible existing directory, output permission/collision/write failure, repeated outputs and the capacity boundary. Inject 1,000,001 distinct accepted identities at the writer seam to test fail-before-publication without a million source files. Record source hashes before/after all cases, including ignored stages and rejected records; every source and prior output remains intact.

Inspect exported ZIP/XML relationships, one table, exact row count/order and the thirteen headers in order: `invocation_id`, `run_id`, `project`, `skill`, `workflow`, `step`, `invocation_kind`, `agent`, `model`, `effort`, `started_at`, `finished_at`, `duration_ms`. Verify the shortened headers map to the unchanged JSON field names. Verify literal string cell types for `=1+1`, `+SUM(A1:A2)`, `@name` and `#N/A`, numeric duration type and absence of the schema-version column, no formula nodes and no silent text truncation. The zero-row workbook must contain a header-only table without a fake blank record. Automated writer/readback checks supplement actual Excel inspection below.

Agent-settings fixtures must cover exact `name` matching with unrelated filenames, explicit model/effort, one omitted setting, missing/unreadable/malformed/ambiguous files, and non-string values. Verify null fallback preserves collection and does not alter dispatch. Old supported twelve-field records remain accepted with blank settings cells; known optional settings participate in duplicate/conflict comparison. No global/inherited configuration lookup is performed.

## Consumer Delivery

Use the existing disposable initialized consumer harness; do not refresh the operator's active installation as a substitute for isolated validation. Record exact tested Specify CLI, component IDs/versions and source/package hashes. Build development snapshots only under the documented supported catalog path after implementation and explain any generated artifact updates.

For a fresh disposable Codex consumer, follow `docs/installation.md` and install the selected development snapshot with the supported catalog task:

```bash
mise run catalog:install <disposable-consumer> --development-snapshot
```

The placeholder names an already initialized temporary consumer, not this checkout. Verify `.specify/farmboy/scripts/python/metrics.py` exists and `.agents/skills/farmboy-metrics-report/` does not. Check all ten original controller/workflow bindings, source digests and unchanged gate/assignment graphs. Probes retain their preflight behavior; failed probing creates no workflow run summary despite completed probe metrics. Successful summary creation keeps its existing independent recovery identity; the retained metrics correlation ID remains unchanged.

Validate correlation independently of recovery: records from probes, execution, a same-child continuation and a retry within one controller invocation share one metrics `run_id`; another invocation gets a different value. Preserve the metrics ID when resuming the same retained controller context. Where a normal workflow summary exists, confirm its recovery ID is separate and normal recovery creation/update behavior is unchanged. Failed probing may produce completed probe metrics but must still produce no workflow summary. Metric files remain flat under the shared metrics directory, with no per-run folder or additional metrics state file.

Repeat supported refresh and removal in the disposable consumer; unrelated components and consumer-owned files remain, and collector removal leaves machine-local metrics and reports untouched. An inventory/no-op Codex fixture establishes packaging/dispatch topology only, not live agent execution or publication.

## Live Round Trip

After fixture checks, explicitly select a supported workflow/target under its normal authority gates. Observe a real exact-named-agent turn in FarmBoy and a disposable consumer. Include a real same-child question/answer: close the question turn before presenting it, wait for the human, then begin the continuation immediately before relay. Retain boundary-order evidence, inspect resulting files and verify the human wait is in neither duration. Pending polls keep the interval open. Do not launch a later workflow just to manufacture observations without operator authorization.

Within FarmBoy, explicitly invoke `$farmboy-metrics-report`. The skill returns the unique workbook location and visible candidate/accepted/invalid/duplicate/conflict counts; it preserves all metric files. If timing collection failed earlier, the report does not claim complete historical accounting.

### Observed live round trip (2026-10-12)

The FarmBoy and disposable-consumer observations used Specify CLI `1.0.10.dev0+pegagio.2`. FarmBoy exact-name probes and Reviewer/Checker turns emitted source-run records. The consumer's `farmboy-implement` run completed six exact-name agent probes and one real `FarmBoy Reviewer` execution at `assess-implementation-state`. All seven consumer records were independently read and validated from the production-default metrics directory; one metrics run identity covered the turns, and the human question-and-answer wait was excluded from invocation durations. The `model` and `effort` values came from passive exact-name project TOML reads; effective runtime settings were not independently verified.

The consumer's read-only Reviewer assessment was blocked because the copied fixture lacked current owning prerequisites. This confirms a live agent turn and metrics emission, not consumer implementation completion. The FarmBoy-side report included 16 source-run rows and these seven consumer rows. The maintainer report skill was explicitly invoked and produced `~/.farmboy/metrics/reports/farmboy-metrics-976182be-4456-4b56-a2f1-7f2e1da37014.xlsx`: 23 candidates and 23 accepted records, zero invalid, duplicate, conflicting, or skipped records, and unchanged input files. Its `Metrics` sheet contains the `FarmBoyMetrics` table with the thirteen specified columns, numeric duration cells, and all seven consumer invocations. These report-generation and readback checks do not establish Excel interoperability. The operator then opened both prepared workbooks in Excel; both opened without repair. The thirteen-column table and filtering worked, formula-looking text remained literal, and numeric durations `1,500` and `-200` summed to `1,300`. The header-only workbook showed zero observations. These are direct operator observations relayed through the same child; this agent did not repeat the UI inspection. Charting remains the operator's activity.

## Evidence and Limits

Implementation validation must retain repository-relative evidence paths identifying source digests, component versions, tested CLI, scenarios, expected/observed results, checks not run and fixture-versus-live classification. A brief record of Excel observations suffices; avoid raw prompts/transcripts, personal details, secrets and absolute host paths.

Clock drift, negative/zero intervals, tool/helper scheduling overhead and missed endings/writes remain accepted limitations. The record count measures available working turns, not accepted tasks or unique children. Local validation proves only the tested source/consumer/runtime path; it grants no release, adoption, Git integration, roadmap verification or feature acceptance.

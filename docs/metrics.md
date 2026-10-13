# Local Agent Timing Metrics

FarmBoy records best-effort wall-clock timing for observed native agent turns. A record measures an invocation boundary, not task success, quality, token use, or monetary cost. Timing uses local clock readings at millisecond precision; zero and negative durations are retained as observed, with no clock-skew correction.

## Record and boundaries

Each completed turn is one UTF-8 JSON file named `metric-<invocation-uuid>.json` in `~/.farmboy/metrics/`. The version-1 record requires `schema_version`, `invocation_id`, `run_id`, `step_id`, `invocation_kind`, `agent_name`, `skill_id`, `workflow_id`, `project_label`, `started_at`, `finished_at`, and `duration_ms`. `model` and `effort` are nullable optional strings. Timestamps use UTC `YYYY-MM-DDTHH:MM:SS.mmmZ`; duration is their signed difference in milliseconds. See the [record contract](../specs/022-local-workflow-agent-timing-metrics/contracts/metric-record.md) for validation and examples.

`run_id` correlates turns within one workflow invocation, including probes, continuations, and retries. `invocation_id` identifies one observed agent turn. Probe records use `step_id=preflight` and `invocation_kind=probe`; working turns use the modeled step and `execution`, `continuation`, or `retry`. A turn starts immediately before native dispatch or continuation and ends immediately after its observed ending. A question-producing turn ends before the human wait; the continuation starts after the answer is relayed. Pending polls remain inside the turn. No record is invented when an ending is not observed.

The optional model and effort values come only from explicit `model` and `model_reasoning_effort` keys in the uniquely matching exact-name project agent TOML file, read before timing starts. They are not resolved from inherited or global settings and do not claim runtime verification. Prompts, transcripts, human answers, secrets, personal details, host paths, tokens, monetary cost, and outcome classifications are excluded.

## Storage and reporting

Each record is published as a separate file through a temporary file and no-clobber publication, so concurrent collectors do not append to or lock a shared file. Collection is best-effort: if timing or persistence fails, FarmBoy warns and continues the original workflow result and gates. Do not treat a missing record as evidence that no turn occurred.

The `farmboy-metrics-report` skill is for explicit use inside the FarmBoy maintainer checkout. It reads a fixed snapshot of local records and writes a uniquely named Excel workbook under `~/.farmboy/metrics/reports/`; source records are preserved. The workbook contains the documented 13-column `Metrics` table and visible candidate, accepted, invalid, duplicate, and conflict counts. Empty input produces a header-only table. The report does not install dependencies, invoke another workflow, or claim complete historical accounting when collection may have failed. Consumer installations receive the collection helper, not this maintainer skill or its spreadsheet dependency.

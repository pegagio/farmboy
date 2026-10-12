# Contract: Metric Record Version 1

This contract defines twelve required fields and optional nullable `model` and `effort` in [the data model](../data-model.md). Reporting compares the fourteen-field projection after normalizing absent settings to null and exports thirteen columns, omitting `schema_version`; collection writes no other fields or result classification.

## Completed Payload

The example measures a working turn, not task success. Values are portable synthetic identities.

```json
{
  "schema_version": 1,
  "invocation_id": "759a38f2-af1a-4a68-a2a1-bf019797a70e",
  "run_id": "c2d3bcfa-3b15-4e9d-9f07-c9d5ed7ba925",
  "step_id": "implement-eligible-work",
  "invocation_kind": "execution",
  "agent_name": "FarmBoy Coder",
  "skill_id": "farmboy-implement",
  "workflow_id": "farmboy-implement",
  "project_label": "example-project",
  "started_at": "2026-10-11T20:00:00.125Z",
  "finished_at": "2026-10-11T20:00:01.625Z",
  "duration_ms": 1500,
  "model": "gpt-6-luna",
  "effort": "high"
}
```

## Validation

Require a UTF-8 JSON object of at most 65,536 bytes and all twelve required fields with the exact types described in the data model. `model` and `effort` may be absent, null or nonempty strings; absence normalizes to null. Present invalid types are invalid input. These settings are read from the exact named project agent file, not inferred runtime values. Reject duplicate keys, nonfinite constants, fractional duration, boolean numeric fields, impossible timestamps, missing/empty strings, unsupported schema and kind values. The two timestamps use exactly three fractional digits and a `Z` suffix; integer subtraction must equal duration. Zero and negative values are valid; do not clamp, correct, flag as outcomes or reinterpret them.

Projected strings must fit Excel's 32,767-character cell limit and legal XML text without alteration. Formula-like text such as `=1+1`, `+SUM(A1:A2)`, `@name` or `#N/A` remains literal text. Unknown extra keys do not invalidate supported records and do not enter workbook columns or duplicate equality. Collector output never adds outcome or substitutes such as success, completion status, result category or accepted flag.

## Identity and Compatibility

Collectors generate fresh UUIDs per turn and one shared metrics correlation UUID per workflow invocation, including probes. The existing `run_id` field carries that metrics UUID, independently of any recovery summary ID. Probe `step_id` is `preflight`; modeled IDs and exact agent/skill/workflow names come from the validated invocation. Same-child continuations and separately dispatched retries receive different invocation IDs. Raw child identities are excluded.

Completed candidate names are `metric-<canonical lowercase UUID>.json`. Publication creates at most one final path per collector turn, without overwrite. A manual copy may have another valid filename UUID; payload identity is the report grouping key. Future unknown fields are ignored under schema 1, while a different schema version is counted unsupported rather than guessed or migrated.

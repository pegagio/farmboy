# Contract: Local Timing Adapter

This is a local Python/CLI boundary, not a network service. The reviewed `controllers/farmboy/scripts/python/metrics.py` is the proposed source and is delivered as `.specify/farmboy/scripts/python/metrics.py` to consumers. Its package has no workbook dependency.

## Begin and Finish

`metrics.py begin` reads metadata JSON from stdin, validates exact allowed keys, generates an invocation UUID and returns a transient start token. The metadata carries `run_id`, `step_id`, `invocation_kind`, `agent_name`, `skill_id`, `workflow_id` and `project_label`, plus optional nullable `model` and `effort`. It comes from the validated main-task graph/context; no prompts or returned prose are parsed.

```json
{
  "run_id": "c2d3bcfa-3b15-4e9d-9f07-c9d5ed7ba925",
  "step_id": "create-plan",
  "invocation_kind": "execution",
  "agent_name": "FarmBoy Planner",
  "skill_id": "farmboy-plan",
  "workflow_id": "farmboy-plan",
  "project_label": "unspecified",
  "model": "gpt-6.1-sol",
  "effort": "high"
}
```

The token adds `invocation_id` and integer `started_ms` to that metadata. It has no destination, child ID or agent result. The main task retains it without a pending file. Sampling occurs after metadata preparation immediately before returning the token; the next controller action is the native request.

`metrics.py finish` reads the same token from stdin, samples integer `finished_ms` as its first timing operation, validates it, derives the version-1 record and passes it to the adapter. Call immediately after observing the ending before routing/review/persistence. A question ends a turn; human waiting is excluded. Pending acknowledgements/polls do not finish. A new continuation/retry receives a new token. If an ending is never observed, never call finish with a guessed clock value.

The importable API includes `read_agent_settings(project_dir, agent_name)` returning only nullable `model` and `effort`, `begin_invocation(metadata, clock_ms=...)`, `finish_invocation(token, clock_ms=..., adapter=...)` and `emit_record(record, directory=...)`. Injected clock/adapter/directory parameters support bounded fixtures; production CLI uses the default clock and `~/.farmboy/metrics`. No user configuration system or arbitrary destination flag is introduced. Explicit injection does not silently change production defaults.

## Agent Settings Metadata

Before clock capture, read the project `.codex/agents/*.toml` files with standard-library `tomllib` and locate one exact `name` match for the dispatch agent. Filenames need not match display names. Copy only a nonempty string `model` to `model` and `model_reasoning_effort` to `effort`; unavailable or unusable values are null. Missing, unreadable, malformed or ambiguous configuration does not prevent collection. Do not copy paths, instructions or other configuration, consult global/inherited defaults, or change dispatch settings. This is a passive metadata read; Codex continues to own agent configuration loading.

## Publication

Create the destination when absent, exclusively create a hidden staging file on that filesystem, serialize one bounded UTF-8 JSON object, close it and call a no-clobber hard link to `metric-<invocation-id>.json`. Only then remove the staging name. Record persistence time lies outside the observed interval. A repeated finish uses the same path and cannot replace an earlier file. Collision warns rather than retrying with a new invocation identity.

Collection owns only its staging file and newly created completed name. It never appends to another record, locks a shared file, scans the whole metrics directory or cleans up someone else's temporary files. Unsupported publication has no replace/direct-write fallback. Crashes may leave ignored stages or no completed record, with no reconstruction guarantee.

## Failure Isolation

Use bounded warning categories: `clock-unavailable`, `metadata-invalid`, `helper-unavailable`, `destination-unavailable`, `publication-collision`, `storage-failed`. Stdout may return `{"emitted": false, "warning_code": "storage-failed"}` or `{"emitted": true}`; these describe the adapter operation, are never metric fields and never classify the agent result. Diagnostics contain categories rather than record contents or absolute host paths.

The main task displays the warning and retains the original dispatch/child result, assignment, routing and human gate. Metrics helper failure—including launch failure—does not stop agent work, replace its error or start another phase. Rejected native requests with an observed end still generate timing records when collection works. Losing an ending/start token warns without inventing a record.

## Run Context and Dispatch Coverage

Validated `controller.py inspect` returns a separate transient `metrics_run_id` before availability probes. Retain it in the existing main-task context for the invocation and copy it into metric metadata as `run_id`. Preserve it through probes, working turns, same-child continuations and resumption of that retained context. Do not pass it to `recovery.py create` or use the recovery summary ID as the metrics grouping key. Main-task steps without an agent request emit no metric.

Metrics do not change recovery ID generation, summary creation, directory layout or update behavior. They introduce no recovery-creation parameter, directory reservation, new metrics state file or per-run metrics directory. Failed probing creates no workflow summary, but completed probe metrics may exist. The separate correlation value grants no recovery or resumption authority.

The shared protocol applies begin/finish to exact-name probes, delegated prompts/commands, same-child answers and separately dispatched retries. The helper cannot wrap the native tool internally; ordering is the supported main-task procedure and needs live evidence. Manual users can follow that same observed path. Agents launched by hand outside it are unmeasured, with no retrospective recovery or claim of automatic interception.

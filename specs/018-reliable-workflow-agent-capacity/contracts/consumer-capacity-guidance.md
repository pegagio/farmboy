# Contract: Consumer Capacity Guidance

Catalog install and refresh recommend setup; consumer configuration remains outside FlowKit ownership. A local guide ships with the shared controller package so it remains accessible after the ephemeral catalog stops.

## Notice and Merge Example

Emit one concise notice after successful bundle/controller installation. Proposed destination is `.specify/flow-kit/agent-capacity.md`; source is `controllers/flow-kit/agent-capacity.md`, added explicitly to controller package enumeration. On partial failure report the operation as partial and name the unapplied recommendation; never print a success banner or claim a value is effective.

A notice identifies install/refresh, operation outcome, preserved config ownership, setting, validation-backed recommendation, and guide path. Local config inspection is read-only and advisory; never enumerate unrelated config fields or read global settings to manufacture effective-capacity proof.

Proposed merge example, gated on candidate validation:

```toml
[agents]
max_concurrent_threads_per_session = 4
```

Merge into an existing `[agents]` table rather than append a duplicate table. Preserve other settings. Four is a planning candidate; a release may call it tested only after the live candidate-value scenarios pass. A valid different value is a consumer choice, not an error. If both legacy `max_threads` and canonical spelling exist, advise explicit reconciliation against the tested client and never guess precedence or rewrite either. No automatic configuration application or new configuration-writing CLI is introduced.

## Advisory States

The setup guide covers every case even if installer inspection cannot establish the state.

| State | Required guidance |
|---|---|
| Absent | Explain adding the field/table with operator approval, then verifying application. |
| Compatible | Retain the value and unrelated fields; verify actual runtime behavior before claiming effectiveness. |
| Review needed | Explain different values, aliases, inherited/runtime overrides, trust, and duplicate definitions; preserve ownership. |
| Malformed | Report bounded parse failure without dumping contents; repair explicitly before relying on the setting. |
| Unsupported | Do not claim the field works; provide client-version limitation and supported manual/fresh-chat fallback. |
| Unknown | Offer generic documented recommendation; distinguish unavailable inspection from absence. |

## Verification and Reload

Explain project trust and documented configuration precedence. A parsed file is a configured value, not an effective runtime observation. Use supported client metadata when exposed plus a documented constrained spawn/release experiment in a disposable test. Do not automatically fill capacity in a real consumer to infer a number.

The conservative documented procedure opens a new chat after applying configuration; omit this step only where the tested client proves supported live reload. This is setup application, not a recurring workaround for cumulative exhaustion. Distinguish concurrent child budget from cumulative completed child count; lifecycle cleanup is required even with a larger budget. Explain the resource/concurrency tradeoff without inventing costs.

## Ownership and Failure Behavior

Install, refresh, partial rollback, and remove preserve `.codex/config.toml` bytes and never include it in managed-file digests. The guide is an owned payload; actual config is not. Malformed config may limit capacity advice without turning a completed component installation into a failure. Component operation failure remains a failure with qualified partial-state reporting. Existing ownership conflicts stop as today; notices never bypass them.

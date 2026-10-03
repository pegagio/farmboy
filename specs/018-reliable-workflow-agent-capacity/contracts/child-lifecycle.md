# Contract: Child Lifecycle and Capacity Recovery

This proposed helper contract governs structured decisions and persistence. The native main-task controller performs actual launches, read-state calls, and release operations; the helper never executes them itself.

## Contents

The contract separates preparation from native side effects and their recorded outcomes.

- [Helper Operations](#helper-operations)
- [Payload Example](#payload-example)
- [Eligibility and Native Release](#eligibility-and-native-release)
- [Bounded Recovery](#bounded-recovery)
- [Stop Codes and Compatibility](#stop-codes-and-compatibility)

## Helper Operations

All commands require `--project <root>` and canonical `--parent-chat-id <id>`. Mutating payloads arrive through JSON stdin and require expected revision. These interfaces are proposed for implementation, not currently runnable commands.

| Operation | Input | Output |
|---|---|---|
| register-child | Native IDs/provenance, invocation, installed coordinates, purpose, agent, step/pass | Record plus new revision; conflicting registration rejected. |
| preserve-result | Registered identity, normalized validated result | Immutable result reference/digest and revision. |
| observe-child | Typed fresh terminal/interaction observation | State and eligibility, with protected/excluded reasons. |
| plan-release | Exact child, current observation and expected ledger revision | Eligible decision and operation ID, or explicit excluded reason. |
| record-release | Operation ID, native method and result | Accepted/failed/unavailable; restoration remains unconfirmed. |
| begin-recovery | Exact failed launch with confirmed capacity code | One sweep and at most one retry permitted. |
| record-retry | Native exact agent launch result | Observed restoration or blocked exhausted result. |
| inspect-session | Read-only session lookup | Compact children/eligibility/recovery summary. |

`inspect-session` validates an existing ledger and returns its revision with compact child, recorded eligibility, and recovery summaries; it does not replace fresh native observations for release. A missing ledger returns an explicit absent-session result with empty summaries and no stored revision, without creating directories, lock files, or a ledger. Inspection never changes eligibility or persisted evidence.

Before successful preflight, these records may exist without a workflow run. They must not populate `runs/`, mark executable workflow steps completed, or count as semantic progress. Once a run exists, compact references may be included without changing old summary semantics.

## Payload Example

This example uses bounded illustrative IDs and relative paths; actual IDs must come from the runtime.

```json
{
  "schema_version": "1.0",
  "expected_revision": 3,
  "parent_chat_id": "parent-example",
  "child_id": "child-example",
  "invocation_id": "invocation-example",
  "purpose": "work",
  "workflow_id": "speckit-flow-clarify",
  "agent_type": "Reviewer",
  "step_id": "assess-clarification-after-session",
  "iteration": 1,
  "execution_state": "terminal",
  "interaction_complete": true,
  "pending_question": false,
  "continuation_required": false,
  "result_ref": ".specify/flow-controllers/agent-sessions/parent-example/results/child-example.json",
  "result_sha256": "sha256:<64 lowercase hex characters>"
}
```

Native observation provenance and installed coordinates are mandatory in actual registration; the displayed observation is a selected projection, not a substitute for runtime ownership proof. Questions preserve same-child routing and remain protected until continuation actually finishes.

## Eligibility and Native Release

At workflow entry, inspect earlier records in the same parent chat. After every probe/work result, preserve output and evaluate interaction completion. Release eligible children before the next executable step. If release is unavailable or fails, record and report it rather than conceal accumulation; stop when the release requirement or next launch cannot safely be satisfied.

Eligibility requires all of: exact same-parent FlowKit ownership, terminal native execution, complete interaction, no pending answer/continuation, existing usable result with matching digest, fresh native observation, unchanged record revision, and supported release capability. Immediately before mutation re-observe through native tools; any change excludes the child. The helper does not make the backend mutation atomic, so minimize the observation-to-release gap and stop on a detected race or ambiguous backend result.

Use the exposed supported close/retire tool when available. Reversible native archival is a tested-client adapter, enabled only with evidence that it releases capacity and preserves artifacts. Never use interrupts, deletes, app database changes, guessed IDs, or unrelated thread cleanup. Record accepted release independently from observed restoration. Activity labels, idle status, elapsed time, and command exit status alone do not satisfy ownership or completion.

## Bounded Recovery

The original launch plus one retry are the only attempts for this step/pass instance. Retry only after a positively identified capacity error and a successful sweep releasing at least one eligible child. Re-read identities/state; skip protected candidates. If a release fails, ownership is uncertain, capability is missing, no eligible child can be released, or retry still fails, stop with preserved evidence. No sleep/retry loop and no retry of a command that started execution. Preserve workflow and installation fingerprints before allowing any later node.

Successful preflight still requires all exact agent checks. A failed preflight retry produces only lifecycle diagnostics, not a successful run. An existing workflow records the stable blocker and current step/pass without rollback or replay. Same-chat earlier-invocation cleanup is authorized; cross-chat cleanup is not.

## Stop Codes and Compatibility

Add stable codes `capacity-exhausted`, `capacity-recovery-exhausted`, `capacity-release-unavailable`, `capacity-release-failed`, `capacity-ownership-unverified`, `capacity-evidence-invalid`, and `capacity-state-changed` to the reviewed recovery boundary. Unknown launch causes retain existing child-unavailable behavior and are not retried as capacity failures. Portable records contain codes and relative references, not raw native error text.

Older summaries without lifecycle references remain readable. New ledger data is consumer-owned evidence and survives component removal. Older children without proven registration are skipped; import only when typed native parent identity and usable retained output can be verified. Native CLI or no-op dispatch acceptance does not establish desktop adapter support.

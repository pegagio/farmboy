# Data Model: Workflow Agent Capacity

The proposed standard-library helper stores lifecycle evidence separately from successful workflow run summaries. All stored paths are project-relative and all IDs are bounded native or generated invocation identifiers; no label is promoted into an identity.

## Contents

The entities define ownership, transition invariants, and evidence relationships.

- [Session Ledger](#session-ledger)
- [Child Record](#child-record)
- [Retained Result](#retained-result)
- [Recovery Attempt](#recovery-attempt)
- [Consumer Advisory](#consumer-advisory)
- [Validation Rules](#validation-rules)

## Session Ledger

One `lifecycle.json` belongs to one canonical parent chat under `.specify/flow-controllers/agent-sessions/<parent-chat-id>/`.

| Field | Contract |
|---|---|
| schema_version | `1.0`; unsupported future versions reject writes. |
| parent_chat_id | Canonical native parent identity; safe single path component. |
| revision | Nonnegative integer; every mutation checks expected revision and increments it. |
| children | Map keyed by canonical child ID; records may span invocations in this parent only. |
| recoveries | Launch-recovery records keyed by invocation/step/iteration/launch-attempt identity. |
| updated_at | UTC timestamp. |

An exclusive per-session lock plus revision comparison protects read/modify/atomic-replace operations. Contention or a stale revision fails without overwriting evidence. Use bounded acquisition without stale-lock deletion guesses; a stale lock requires reported recovery. Released records remain available after workflow completion, controller refresh, and bundle removal.

## Child Record

A child is registered once per native identity. Agent, purpose, owning invocation, parent, step, and iteration are immutable; only validated lifecycle observations and run linkage may change.

| Field | Contract |
|---|---|
| child_id / parent_chat_id | Exact native IDs with typed provenance. |
| invocation_id | Generated identifier for this invocation, including unsuccessful preflight. |
| workflow_id / workflow_version / workflow_sha256 | Component coordinates from the inspected installed definition. |
| run_id | Null until successful preflight produces a workflow run; probes may remain null. |
| purpose | `probe` or `work`. |
| step_id / iteration | Exact declaration and pass; probe uses a stable preflight assignment ID and null iteration. |
| agent_type | Exact declared native name; immutable. |
| execution_state | `running`, `waiting-for-answer`, `terminal`, or `unknown`. |
| interaction_complete | Boolean; terminal turn alone does not establish it. |
| pending_question / continuation_required | Booleans; either protects the child. |
| native_observation | Compact typed parent/state evidence and observation timestamp; no raw transcript. |
| result_ref / result_sha256 | Existing immutable project-relative result and digest, or null until preserved. |
| release_state | `retained`, `eligible`, `requested`, `accepted`, `failed`, or `unavailable`. |
| release_method / release_evidence_ref | Capability-selected method and compact result evidence, or null. |
| restoration_state | `unconfirmed` or `observed`; observed requires a subsequent successful exact launch reference. |

Transitions are `running → waiting-for-answer → running → terminal`; a terminal turn with pending interaction remains retained. After preserved result and verified completed interaction, `retained → eligible → requested → accepted`. Release error yields failed/unavailable and a specific diagnostic. Accepted release never resurrects or reuses the child. Result disappearance/digest mismatch or stale native state revokes eligibility before mutation. Subsequent launch proves observed restoration separately from accepted release.

## Retained Result

`results/<child-id>.json` is create-once compact validated output with schema version, invocation/step/agent identity, result kind (`probe-readiness`, `step-output`, or `assessment`), and portable structured content. Store readiness as a boolean plus validated marker kind; do not introduce a `token` key rejected by recovery portability validation. Results include no human question/answer transcripts, credentials, or host paths. Valid substantive child work outputs and evidence references remain usable after release. Keep author outputs distinct from independent review outcomes.

## Recovery Attempt

Fields include parent and invocation identity, exact failed step/pass/agent, stable failure code, original launch reference, candidate/release references, retry count (zero or one), retry launch reference, result (`recovered` or `blocked`), stable reason, optional run ID, and stable resume action. A recovered attempt names one successful retry of the exact assignment; cleanup without launch does not qualify. Launch failure is not command execution. Store normalized codes and compact bounded observations, never full tool outputs.

## Consumer Advisory

The catalog output has operation (`install`/`refresh`), operation_state (`completed`/`partial-failure`), config_state (`absent`/`compatible`/`review-needed`/`malformed`/`unsupported`/`unknown`), configured_value when safely known, recommendation_value once validated, setting key, guide path, `configuration_changed=false`, and `effective_capacity_verified=false`. This describes a file/advice state, not a runtime or consumer adoption assertion. No persistent consumer-config ownership entity is introduced.

## Validation Rules

Reject unsafe or mismatched IDs, unknown schema/state/fields, escaping or symlinked evidence paths, missing/mismatched result digests, stale revisions, cross-parent mutation, reassigned child ownership, contradictory terminal/question flags, and retry counts above one. Revalidate native terminal status immediately before release. Backend metadata cannot be replaced by caller-supplied labels. Missing legacy ownership evidence yields excluded eligibility, never blanket migration. Refer to [lifecycle contract](contracts/child-lifecycle.md) for example requests and failure codes.

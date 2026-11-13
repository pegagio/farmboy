# Bounded released-delivery recovery

Source capability: schema25/Feature9, retaining discovery1 and existing Review,
Checkpoint, Recovery and operation-receipt conventions. Deployment is separate:
source availability never migrates the selected schema24 store or installs tools.

`feature delivery recovery show` inspects; `record` consumes a strict
`delivery_recovery_policy` role with exact accepted-spec checkpoint/spec approval,
plan candidate/plan approval, current handoff/revision/queue/dependency pins and
attributable assessment. Decisions are authorize, renew (explicit previous
allowance), hold, clear-hold, assess-stop. Mandates use actual human
`authorize-bounded-delivery`; holds/clearances use `hold-delivery-recovery` and
`clear-delivery-recovery-hold`. Clearing a hold grants no mandate or readiness.
Coordinator assess-stop cannot clear an operator pause/denial. These are roles
of the existing native context, not a new authorization service.

A recoverable stop may include readiness: inspected expected_head,
workspace_clean, existing stopped-writer/preservation Recovery, attributable
failed/changed/evidence/unverified resolution, and coordinator
`continue-bounded-delivery` Review. Bare classification is not ready. A consumer
must establish actual remaining external rights/budgets before declaring ready;
native acceptance verifies report consistency, never repository truth, writer
death, semantic resolution or actual API counts.

Only a specifically opted-in, current, positively ready, unheld, unspent released
incomplete deliver/delivery can appear in ordinary discovery with
`recovery_mode: released-delivery`, under current project/delivery controls.
Completed handoffs, legacy/unclassified/paused/denied/unknown work remain stopped.
The existing one-child repeat guard remains held through process and native
outcome observation. No stale-lock cleanup, timeout takeover or process restart.

The selected child rechecks actual evidence read-only, then submits the stored
verified successor report using ordinary `feature run recover` and
`delivery_recovery` (allowance_operation and resolution). Its first authority
change is recover, never fresh acquire, claim or planning-selector misuse.
`discovery_selected` is forbidden on this role. Native immediate-transaction
checks repeat current pins, controls, authority, readiness, ownership and remaining
allowance. Divergence requires deliberate reinspection, never silent repinning.

The immutable origin preserves predecessor, new greater fence and complete
OriginalInput, including original spec/plan/review/dependency/identity/condition
references. Consumption derives from admitted successor origins: even startup
failure/incomplete release consumes the one allowance. Exact replay returns its
receipt and grants no ownership; another operation/process/poll does not renew.
Explicit human renewal changes only this run allowance, never permission,
credential/network/request/retry budgets. Existing active/manual/planning flows
retain their meanings; no new manual delivery launcher flag is introduced.

Reuse the same adapter delivery body and preserve partial code/tests/fixtures/task
IDs, checked evidence and unrelated work. Reassess only affected stale checks.
Dirty admission is no checkpoint. Actual normal-hook commit, delivery handoff and
released ownership are required for result review; exit0 alone is insufficient.
Acceptance/integration/install/push remain separate decisions. Failure, denial,
uncertain effects or exhausted authority stops without retry/fresh-run fallback.

Explicit `database upgrade --from-version 24 --to-version 25` preserves all prior
context columns/history/controls and adds one nullable delivery policy. NULL
legacy rows stay unknown/ineligible; no entry-time migration. Use existing
verified snapshots/restore and active-owner guards. Current implementation tests
use private stores and controlled children, not the user's BGG work, live schema,
real model/sandbox permissions or API endpoint.

## Schema26 consolidation

The preceding stage-specific schema history remains preserved. DIAG-24 normalizes current policy writes and consumption through [shared continuation](https://github.com/pegagio/diagram/blob/28ef13fb0da2f8d5f620e41f3909d66cd64bcbd7/docs/architecture/contracts/shared-continuation-v1.md). Existing commands/role scopes and immutable replay receipts remain compatibility adapters; no independent mutable policy column or automatic mandate renewal survives conversion. Matching source/client and separately authorized migration are required; no live cutover follows from this reference.

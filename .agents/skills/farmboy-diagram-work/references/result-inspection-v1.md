# Exact delivered-result inspection from a pinned worktree

DIAG-20 candidate source adds optional `Review.result_inspection` to the existing Feature9 result-review request on schema23. This document describes source capability; it does not assert installation in the selected live runtime. No new command, schema migration or workspace reassociation is introduced.

## Invocation and purpose

Use existing `diagram feature review record --feature FEATURE --operation OP --request-file FILE --file STORE --json` with `decision_kind: result`, `review.decision: accept`, current Feature/queue/dependency pins and exact current released delivery handoff. Existing actual human actor/provenance/outcome/approach/conditions and separate integration_permission rules remain unchanged. Inspection evidence is not consent, a delegated mandate, or native independent observation.

This route permits reviewing exact delivered version A in an externally verified clean same-repository worktree at A while its old checkout contains later B, even if B changed delivered paths. Never assert those successor files are unchanged. The selected worktree's full branch may differ; its HEAD must equal A, not an equal-content or descendant substitute commit.

## Optional report fields

All fields below are required except `original_checkout`. Unknown keys/types, malformed identities/refs/digests, incomplete or duplicate artifact paths and absent/false required assertions reject.

| Field | Required meaning |
|---|---|
| `handoff` | Exact current ordinary released delivery and Request.pinned_handoff. |
| `delivery_checkpoint` | Original full delivery commit plus exactly its complete unique path/SHA-256 set. Required-check, convergence and closeout references retain their existing membership/roles. |
| `original_association` | Historical ended-delivery `workspace`, `branch`, `worktree_key` copied exactly from native records; never rewritten as the selected worktree. |
| `workspace`, `branch`, `worktree_key` | Actual selected canonical worktree locator, full local symbolic ref and canonical worktree identity. |
| `repository_id`, `instance_id` | Exact current recorded repository and physical instance; clones are different instances. |
| `expected_head` | Exact delivery commit; must agree with top-level expected_head. |
| `workspace_clean` | Explicit true external inspection of clean index and worktree. |
| `artifacts_verified`, `context_applicable` | Explicit true external verification/applicability assertions. |
| `verification` | Basic Assessment actor/rationale/nonempty evidence; no Feature-only approval or execution fields. |
| `original_checkout` | Optional actual observation with historical locator `workspace`, actual full current `branch`, distinct current `expected_head`, `ancestry: verified-descendant` and basic `verification`. Verify locator resolution/physical identity and actual ancestry externally before asserting it. No successor-artifact-equality assertion exists. |

Request.repository_id, instance_id and worktree_key must be explicitly supplied and agree with the selected report. Request.expected_head and workspace_clean must agree as well. Do not omit identity expecting historical defaults to supply the alternate worktree. The selected root/ref come from the nested report; otherwise-forbidden top-level review workspace/branch fields stay forbidden.

## Native guards and retained history

Only current ordinary successful-delivery positive acceptance is eligible. No terminal/retired project or feature, active claim/run, changed source binding, stale delivery/handoff/Feature/queue/dependencies, missing/inapplicable spec/plan decision, or affected IntegrationReview candidate is admitted. The field is invalid on spec/plan review, negative result review, grants/dependency verification, acquire/handoff/recover/queue/offer commands, or with specification_advancement.

The selected proof uses existing reportWorkspace checks and a narrow same-repository result-inspection check; ordinary matchExecution remains exact-location guarded. Current delivery, association, binding, pins, upstream decisions and absence of writers are rechecked in the existing transaction before acceptance. Core validates consistency and native authority only; it never follows paths, runs Git or verifies consuming files physically.

Acceptance is saved against the unchanged original delivery checkpoint/handoff. The nested report is retained in existing approval decision JSON and operation readback. It does not update enrollment/context/ended runs, create a writer, insert another delivery, mark done or record integration. Integration permission is never inferred; a separately selected normal integration still requires actual destination reconciliation/policy/checks and completion evidence.

## Consumer procedure and failures

1. Read current Project/Feature/queue, exact delivery and upstream decisions. Preserve actual user acceptance provenance and scope; previously applicable explicit acceptance needs no redundant consent.
2. Inspect the selected physical repository/common-directory/instance/worktree, actual full branch, exact HEAD and clean index/worktree. Compare all delivery/evidence bytes to their immutable commit/digests and verify applicable historical spec/plan artifacts. A clone, altered/missing content, unverified scope or dirty state stops before submit.
3. When reporting original-checkout advancement, inspect its actual locator/ref/HEAD, resolve any locator alias to the recorded physical identity, prove delivery ancestor relationship and assess intervening changes. Do not report the old commit as current or equal hashes as ancestry/consent.
4. Serialize one strict request with actual current pins and the report, then submit once. Inspect operation/current state for the actual decision, exact original checkpoint, retained inspection and no new owner. Exact accepted replay returns its original receipt before changed mutable eligibility; changed payload under the same operation ID conflicts.
5. A domain rejection such as branch_mismatch or repository_binding_mismatch is distinct from a runtime permission denial. Refusal grants no acceptance; an absent operation is not an uncertain/accepted result. On unknown outcome inspect first; inaccessible inspection remains uncertainty. Do not reset another checkout, relink by inference, edit the database, switch stores, misreport HEAD or use backfill to bypass a normal review.

Existing error families and ordinary request behavior are retained. Older strict binaries reject the new unknown nested member. Deploy a matched accepted executable/client only under separate installation authority; source/tests/documentation alone neither install the capability nor authorize an actual Fusion retry. See the [feature validation guide](https://github.com/pegagio/diagram/blob/28ef13fb0da2f8d5f620e41f3909d66cd64bcbd7/specs/046-pinned-result-review/quickstart.md).

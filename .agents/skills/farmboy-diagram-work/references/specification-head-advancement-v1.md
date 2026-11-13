# Direct first specification-review advancement

DIAG-19 candidate source adds an optional Review member to the existing Feature9 review request on schema23. This describes source capability, not installation in a live selected store or executable. No migration or new command is required.

## Existing invocation

Use `diagram feature review record --feature FEATURE --operation OP --request-file FILE --file STORE --json` with the existing selected store and strict one-object transport. Existing identity, expected-head, cleanliness, current native pins and actual human Review fields remain required. There is no new command, standalone reconciliation state or automatic execution.

## New optional member

Only on a first positive spec review at an advanced HEAD, Review may additionally carry:

```json
{
  "specification_advancement": {
    "base_commit": "<exact original reviewed full commit>",
    "current_checkpoint": {
      "commit": "<actual inspected current full HEAD>",
      "artifacts": [{"path": "<each pinned path>", "sha256": "<unchanged digest>"}]
    },
    "ancestry": "verified-descendant",
    "artifacts_unchanged": true,
    "context_applicable": true,
    "verification": {
      "actor": "<actual consumer>",
      "rationale": "<actual ancestry, complete artifact and context inspection>",
      "evidence": ["<actual Git comparison/inspection references>"]
    }
  }
}
```

Angle-bracket values above are contract notation, not executable payloads or verified facts. The enclosing Review still supplies the actual user's decision; the evidence does not establish consent. Do not reuse a fixture approval or an unrelated approval ID.

See [feature data model](https://github.com/pegagio/diagram/blob/28ef13fb0da2f8d5f620e41f3909d66cd64bcbd7/specs/045-unchanged-spec-head/data-model.md) for exhaustive field and role constraints. Unknown fields, malformed/missing/false assertions and incomplete/changed artifact sets reject. `base_commit` matches the current exact accepted specification; current_checkpoint.commit matches Request.expected_head, is distinct, and its path/digest set is exactly equal to the pinned artifact set. Set equality must reject duplicates, missing/extra paths and mismatched digests. The consumer proves actual ancestry and bytes; native verifies the submitted report's structure/consistency and authority.

## Consumers and readback

An agent first performs actual Git/identity/cleanliness and applicability checks in the associated worktree and obtains/verifies actual current user approval. It then submits the existing review request with the optional evidence. Reinspect current operation/Feature after submission. An absent or refused result grants no approval; an uncertain result requires supported operation inspection before any retry.

On success, Approval.checkpoint and handoff remain the exact original reviewed artifacts. Approval.review.specification_advancement contains the inspected advanced checkpoint and consumer attribution. Existing Ready for planning follows only from the actual accepted approval. Ordinary separately selected planning uses its existing applicable approval and advanced-HEAD rules; it starts no earlier. No new flowback/recovery admission is introduced.

Existing error families remain: invalid_request/artifact_mismatch for malformed or inconsistent report, branch_mismatch for missing/inapplicable advanced proof, stale_coordination_revision or existing handoff/queue/dependency errors for stale inputs, and authority_conflict for an active writer. Consumer physical verification failures are reported before submission and must not be represented as independent native observations. No new general error family is required.

## Compatibility and ownership

Normal requests omit the optional member; their behavior and existing receipt data stay unchanged. Existing strict older binaries reject the new unknown nested member. A matched newer executable/client is needed for this capability, with its source pin documented after separate acceptance/deployment. This task adds no deployment or live consumer action. Feature9/schema23, Project4/Repository2 and unrelated contract families stay unchanged. The optional field is retained with the current decision in existing decision JSON; ordinary requests omit it and old receipts are not rewritten. Exact current queue/dependency pins are checked for this path, in addition to existing identity/state/ownership/revision guards.

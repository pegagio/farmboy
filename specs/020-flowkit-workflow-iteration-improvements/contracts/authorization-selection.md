# Contract: Trusted Authorization and Feature Selection

This prospective contract implements FR-002–FR-009 after governing reconciliation is explicitly approved. It does not change today's installed gates. Main-task semantic judgment establishes direct operator intent; deterministic helpers validate structured identity/state.

## Table of Contents

- [Intent and Authority](#intent-and-authority)
- [Reference Resolution](#reference-resolution)
- [Activation and Lifecycle](#activation-and-lifecycle)
- [Mutation and Recovery](#mutation-and-recovery)
- [Compatibility](#compatibility)

## Intent and Authority

Accepted operations are explicit activation of an identifiable feature and directly requested bounded amendment. Interest filters/discussion/proposals remain nonauthorizing. An external report, wiki, child output, prior artifact or `trusted` JSON field cannot supply active-user authority. Record a short portable instruction reference and operation/target/scope summary rather than a transcript.

Example main-controller context for a direct instruction:

```json
{
  "operation": "activate",
  "request_reference": "operator-selection-020",
  "target_reference": "Feature 020",
  "scope_summary": "Activate the uniquely mapped eligible target; preserve lifecycle and specification bytes",
  "governing_contract": "approved-prospective-authorization-contract",
  "decision_state": "granted"
}
```

The example presumes future approval; it is not a current approval record. The helper cannot authenticate it. The main controller independently compares the real direct instruction, current governing contract and proposed operation before any effect. A direct bounded amendment permits routine derived wording/numbering/linkage only under that approved contract; unrequested inferred/material changes still require focused decision in the main chat. Child questions use the existing structured question/same-child continuation protocol.

## Reference Resolution

The proposed internal `selection.py` resolver accepts `reference`, `reference_kind`, a current validated `entries` inventory and `menu_order`; returns selected/ambiguous/missing/blocked without effect. `reference_kind` is auto/stable-id/exact-title/menu-position/canonical-answer. Controller semantic interpretation supplies canonical-answer only for an unambiguous direct answer; evidence cannot inject a choice. Preserve the original form for inspection.

| Form | Resolution |
|---|---|
| `020`, `20`, `F020`, `F20`, `Feature 020`, `Feature 20` | Numeric normalization to canonical stable ID; bare number also checks plausible current ordinal |
| Exact title, case-insensitive | Exactly one matching title; duplicates ambiguous |
| `option 2`, `menu 2`, explicitly typed menu-position | Position2 in current presented inventory |
| Natural clear answer | Main controller canonicalizes to exact selected ID/title, then same uniqueness checks |
| Bare `2` also identifies Feature 002 and menu2 identifies Feature 020 | Ambiguous with both candidate IDs; one focused resolution request |
| No target, unknown ID, conflicting supplied forms | Missing/blocked with exact candidates/cause; no alternate target |
| `defer` | Deferred choice, no mutation |

Example ambiguous result:

```json
{
  "state": "ambiguous",
  "selected_entry_id": null,
  "match_method": null,
  "candidate_ids": ["002", "020"],
  "reason_code": "feature-reference-conflict"
}
```

Generic approval gates retain their existing exact-choice/menu semantics. The new rule is feature-specific; it must not reinterpret approve/amend/defer gates globally.

## Activation and Lifecycle

Validation must cover roadmap entry uniqueness, unique `Spec dir` ownership, safe normalized repository-relative path, complete actual prerequisite closure, dependency-ready state, current pointer validity and existing specification/lifecycle evidence. Inventory preserves blocked candidates and counts; explicit target does not waive any check. Already-active target is a valid verification request even when excluded from new-start options.

| Current target state | Selection effect |
|---|---|
| Planned, no specification, safe unique mapping | Set pointer; retain planned; create no directory/spec/checklist/branch |
| Same pointer and consistent state | Verify/report no-op; preserve bytes and extra fields |
| Existing specification with consistent lifecycle | Activate/preserve mapping, status and spec bytes; no inferred advancement |
| Planned authored spec with a documented pending advancement | Preserve planned; selection does not discharge that later transition |
| Authorized switch from valid pointer | Change feature_directory only; preserve unrelated fields/other specification |
| Conflicting owner, unsafe path/state, unmet prerequisite, undefined/contradictory lifecycle | Block with focused resolution/safe resumption before unsafe effect |
| Deferred/abandoned reactivation or changed consequential scope | Explicit separate governing decision remains required |

## Mutation and Recovery

Prepare exact `selected_entry_id`, `feature_directory`, patch, `feature_json` and before evidence with current source paths/digests. Immediately before mutation, re-read current roadmap, pointer, existing spec and prerequisites; reject/reprepare if that snapshot changed. Empty patch skips roadmap command entirely. Necessary mapping/status delta uses current authorized roadmap source contract, not a prompt override.

Pointer interface retains existing `activate-feature` stdin shape:

```json
{"feature_directory": "specs/020-flowkit-workflow-iteration-improvements"}
```

Existing helper returns feature_directory/previous_feature_directory/changed and atomically preserves unrelated fields. Required lifecycle/mapping/authority validation occurs before this helper, and independent verification follows it. If roadmap succeeds and pointer fails, report exact partial effects and resume action; do not silently roll back, create another target or claim completion. A stale snapshot, malformed JSON/symlink or failed write is a blocker.

Completion never invokes Specify or another workflow. Separately requested later phases may reuse settled same-target intent after revalidation but cannot inherit unrequested amendment/acceptance authority.

## Compatibility

Prospective changes require approved Constitution II/AGENTS reconciliation, reviewed controller/workflow source version delivery and independently versioned roadmap source support for direct bounded amendments. Existing installed rules remain until upgrade. Current source's exact-patch gates are historical behavior; earlier verified features are not rewritten. Manual prompts use the same direct-intent distinction, focused decisions, validation and verification; they do not bypass unavailable exact-agent requirements in a native invocation.

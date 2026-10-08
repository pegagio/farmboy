# Contract: Evidence-Supported Phase Lifecycle

This prospective Feature 020 interface covers FR-026–FR-038, SC-012–SC-016 and Story 6 scenarios 1–15. It does not authorize the current installed workflow to write a milestone. Source implementation, owner compatibility, explicit runtime-policy approval, review and installation must precede use. Existing roadmap vocabulary/history, core gates, exact native assignments and human verification remain constraints.

## Table of Contents

- [Ownership and State Rules](#ownership-and-state-rules)
- [Evidence and Trust](#evidence-and-trust)
- [Command Interface](#command-interface)
- [Apply and Receipt Semantics](#apply-and-receipt-semantics)
- [Recovery and Questions](#recovery-and-questions)
- [Validation Contract](#validation-contract)

## Ownership and State Rules

Normal transitions are Specify `planned→specced`, Implement `specced→in-progress`, Close Out `in-progress→implemented`. Selection changes identity only. A phase never writes verified as its ordinary milestone. Close Out debrief plus the exact consequential verification gate retain their existing role. Equal/advanced consistent state is preserved without a downgrade or duplicate event; later labels are not evidence.

Recovery is a separate declared mode of the invoked phase, bounded by its ceiling: Specify specced, Implement in-progress, Close Out implemented. It assesses missing adjacent edges individually, records their actual present occurrence and never invokes another workflow. The original milestone owning phase is recorded even when a later phase executes recovery. Contradictory/deferred/abandoned/regression states cannot be ordered through this routine mode. Missing installed route/version is a delivery blocker.

## Evidence and Trust

Every proof includes a contained relative path/current SHA-256 and exact reviewed-input digest map; no symlink escapes, raw transcript, absolute host path or secret. A shared source snapshot includes roadmap/config, active pointer, unique mapping, dependency closure, constitution, workflow graph/controller/extension compatibility, specification and relevant downstream/evidence files. Unknown/duplicate JSON keys and unsupported enum/schema values are rejected. A digest only identifies bytes; independent semantic findings must be assessed by the actual native role and bound to the current selected scope.

| Milestone | Required proof | Insufficient alone |
|---|---|---|
| specced | authored/amended current spec; complete author-quality criterion coverage; resolved required clarification; separately assigned Reviewer quality/linkage review and current roadmap brief with no unresolved required alignment finding; valid current prerequisites and settled consequential decisions | file presence, Draft/Complete header, author's own verdict, command exit, future implementation |
| in-progress | current reviewed spec/plan/tasks, verified dependencies, deterministic readiness plus exact Checker verdict/fresh guard, eligible authorized task scope and available required names | specced label, dependency status alone, unchecked-item exclusion without classification |
| implemented | current full-scope attributable implementation/convergence and independent Code Reviewer completion evidence; required validation satisfied; zero buildable unresolved implementation defects; pending future acceptance/release separated | task markers, Complete header, success code, old convergence predating amendment |

The evidence ordering is acyclic: an independently assigned `assess-authoring-quality` node first validates current author quality, required clarification and linkage without requiring a future brief; the new roadmap brief evidence mode then accepts that `specification_ready` assessment plus its current proof references; it does not require Close Out's Complete label or implementation. It preserves legacy `--spec-complete` behavior outside this mode, and rejects mixing incompatible legacy/new inputs. A final `assess-specification-milestone` node combines the completed independent authoring review with the completed current brief and checks unresolved Must-Address findings before prepare/write. Neither pre-brief review nor brief requires its own later result. New independent Specify quality review is required in addition to current linkage review. A new spec scope invalidates old full-scope completion proof regardless of preserved historical markers.

Main controller establishes trusted request origin, actual native assignment/run provenance and delivered approved contract. An `authorized=true` field, child output, stored approval or role string cannot supply that trust. Routine invocation authorizes only the explicitly delivered phase contract; consequential choices remain focused human decisions. Manual execution follows the same contracts/owner commands and preserves those decisions; lack of native dispatch is not permission to call a generic role or bypass review.

## Command Interface

These commands and fields are proposed delivery, not currently available. FlowKit's thin adapter validates evidence/routes without roadmap mutation:

```bash
python3 .specify/flow-kit/scripts/python/controller.py phase-lifecycle --project "$PWD" < lifecycle-request.json
```

Request `action` is `prepare` or `revalidate`. Required envelope fields are `schema_version`, `action`, `phase`, `feature_directory`, `entry_id`, `run_id`, `workflow_id`, `workflow_version`, `mode`, `decision_reference`, `milestone_evidence` and `snapshot`; `revalidate` also requires the previously prepared `proposal`. `mode` is normal/recovery. Snapshot is populated from actual current files, never trusted solely from caller-supplied values. Prepare returns `state` ready/no-op/blocked/question, `reason_code`, current `snapshot`, `evidence`, `blocking_ids`; ready includes exactly one single-edge `proposal`, blocked includes `resume_action`, question includes the structured request. No-op contains `retained_status` and no patch/event.

Example prepared request shape (digest aliases stand for real 64-character SHA-256 values; fixtures substitute actual digests):

```json
{
  "schema_version": "1.0",
  "action": "prepare",
  "phase": "implement",
  "feature_directory": "specs/901-phase-lifecycle",
  "entry_id": "901",
  "run_id": "demo-implement-1",
  "workflow_id": "speckit-flow-implement",
  "workflow_version": "0.7.0",
  "mode": "normal",
  "decision_reference": "validation/operator-decisions.json",
  "snapshot": {
    "schema_version": "1.0",
    "feature_directory": "specs/901-phase-lifecycle",
    "entry_id": "901",
    "phase": "implement",
    "workflow_id": "speckit-flow-implement",
    "workflow_version": "0.7.0",
    "run_id": "demo-implement-1",
    "current_status": "specced",
    "scope_sha256": "SPEC_SCOPE_SHA256",
    "source_map": {".specify/memory/roadmap.md": "ROADMAP_SHA256"},
    "dependency_states": [],
    "pending_future_ids": ["HUMAN-ACCEPT-001"]
  },
  "milestone_evidence": [{
    "milestone": "in-progress",
    "owning_phase": "implement",
    "assessments": [{"path": "validation/current-start-review.json", "sha256": "REVIEW_SHA256", "kind": "independent-review"}],
    "required_check_ids": ["current-artifacts", "dependencies", "readiness", "eligible-scope", "native-assignments"],
    "satisfied_check_ids": ["current-artifacts", "dependencies", "readiness", "eligible-scope", "native-assignments"],
    "unresolved_ids": [],
    "artifact_digests": {"specs/901-phase-lifecycle/spec.md": "SPEC_SCOPE_SHA256"},
    "historical_activity": [],
    "pending_future_ids": ["HUMAN-ACCEPT-001"]
  }]
}
```

Production snapshot maps include every required file from Evidence and Trust, not only the abbreviated example. `scope_sha256` binds the exact current intended scope; required-check coverage is determined by delivered policy, not caller-selected omissions. Prepare builds target `from_status`, `to_status`, original status digest, exact patch SHA and effect ID; it returns no command execution authority.

The existing roadmap Write command gains explicit `PHASE_MILESTONE_REQUEST=<relative JSON path>` mode for a controller-prepared packet plus controller-established trusted invocation. Its owner helper is:

```bash
python3 .specify/extensions/flow-roadmap/scripts/python/phase_lifecycle.py evaluate --project "$PWD" < lifecycle-request.json
python3 .specify/extensions/flow-roadmap/scripts/python/phase_lifecycle.py apply --project "$PWD" < lifecycle-proposal.json
```

Evaluate is read-only. Apply accepts the prepared proposal envelope: snapshot, milestone evidence, trusted-decision reference, from/to statuses, expected roadmap SHA, patch SHA, effect ID and recovery context. The caller independently verifies trust; owner code enforces schema/path/edge/evidence/source-state constraints. Only the owner helper may write roadmap bytes. The extension manifest must declare the new script and commands/report templates document mode semantics. Absent script or unsupported contract produces `lifecycle-owner-contract-unavailable` before mutation. Ordinary Write explicit-delta mode remains unchanged. New readiness mode in review-contract is additive and separately versioned; debrief remains outcome/delta/Must-Address evaluation and proposal-only.

## Apply and Receipt Semantics

Immediately before each write, acquire a cooperating roadmap lock, revalidate config/write containment and every relevant source/evidence digest, active target, unique mapping, dependencies and approved governing contract. The source bytes and exact candidate patch must match the prepared packet; changed relevant state yields not-applied with fresh reassessment or focused resolution. Do not transfer prior explicit verification approval to a materially changed patch.

Apply preserves all unrelated entry fields, dependencies, original evidence and other entries. Change only the selected adjacent status, its append-only current transition provenance, and normal roadmap Sync Impact Report/date/version metadata. Use existing roadmap version policy, not an invented status-only semver rule. The event identifies effect ID, actual occurrence time, owning phase, executing workflow/run, current scope/evidence and prior/resulting states; it never backdates to the referenced work. Build candidate bytes, compare exact preimage under lock, replace atomically, read back and validate expected bytes. Revalidate scope/evidence after effect before proceeding to coding/debrief. Cooperating locking cannot serialize arbitrary external editors; unexpected readback means indeterminate/concurrent-change, not another blind write.

`LifecycleReceipt` is a discriminated outcome envelope. Only `effect_state: applied` is a transition receipt; `no-op` is an explicitly event-free assessment record in the same envelope, and the other states are attempt outcomes. Common required fields are `schema_version` (1.0), `feature_directory`, `entry_id`, executing `phase`, `scope_sha256`, current `evidence`, `effect_state` and `record_state`. State-specific policy is strict: unknown fields, missing required fields, forbidden fields and null values are rejected. Optional fields are omitted when unsupported, never populated from guesses. SHA fields contain real 64-character SHA-256 values in production; aliases in these examples are substituted from actual fixtures.

| Effect state | Additional required fields | Optional fields and constraints | Forbidden fields |
|---|---|---|---|
| applied | `effect_id`, `owning_phase`, actual `from_status`, `to_status`, `occurred_at`, `roadmap_before_sha256`, verified `roadmap_after_sha256` | `record_error` is required only with failed recording. `recovery_evidence` is required only with recovered recording and binds original roadmap event/provenance plus independent current verification | `assessment_id`, `retained_status`, every `proposed_*` field, `reason_code`, `observed_roadmap_sha256` |
| no-op | `assessment_id`, `retained_status`, observed `roadmap_before_sha256` and `roadmap_after_sha256` (equal) | `record_error` is required only with failed recording. Current sufficient milestone proof is still required; the assessment identity identifies this read-only evaluation, never a roadmap transition | `effect_id`, `owning_phase`, `from_status`, `to_status`, `occurred_at`, every `proposed_*` field, `reason_code`, `observed_roadmap_sha256`, `recovery_evidence` |
| not-applied | `proposed_effect_id`, `owning_phase`, `proposed_from_status`, `proposed_to_status`, `reason_code`, known proposal `roadmap_before_sha256` | `roadmap_after_sha256` is permitted only from observed final readback. It may differ from the proposal preimage after an external edit; it proves observed bytes, not the proposed effect. `record_error` is required only with failed recording | actual `effect_id`, `from_status`, `to_status`, `occurred_at`, `assessment_id`, `retained_status`, `observed_roadmap_sha256`, `recovery_evidence` |
| indeterminate | `proposed_effect_id`, `owning_phase`, `proposed_from_status`, `proposed_to_status`, `reason_code`, known proposal `roadmap_before_sha256` | `observed_roadmap_sha256` is permitted only from actual readback whose relationship to the proposed commit is uncertain; omit it if unreadable. `record_error` is required only with failed recording | actual `effect_id`, `from_status`, `to_status`, `occurred_at`, verified `roadmap_after_sha256`, `assessment_id`, `retained_status`, `recovery_evidence` |

`record_state` is `recorded` or `failed` for any outcome. `recovered` is allowed only for applied effects independently established from existing roadmap event/provenance and observed bytes; its `occurred_at` is the original actual event time, never the retry or assessment time. `record_error` is forbidden unless recording failed; `recovery_evidence` is forbidden unless recording recovered. A failed persistence attempt may leave this outcome only in the actual command/controller error report; the report must not pretend a durable receipt exists. Blocking prepare assessments use `LifecycleAssessment`, not fabricated apply receipts without a prepared proposal.

Applied requires established actual event identity, occurrence time and both observed hashes. Known committed candidate bytes and valid event provenance establish applied even if record persistence or a later action fails. If those facts cannot be established, return indeterminate with only known proposal/observation data; do not force the applied schema. Definitely not-applied requires proof the writer did not apply the proposed effect, not merely an error exit or missing receipt. Optional final readback may be absent in that outcome without changing the established nonapplication. Neither a candidate digest nor an old observed digest may masquerade as final readback.

Examples are compact complete envelopes; fixture substitutions establish the named digests, evidence and timestamps rather than inventing them. The first records an actual effect:

```json
{
  "schema_version": "1.0", "feature_directory": "specs/901-phase-lifecycle", "entry_id": "901", "phase": "implement",
  "scope_sha256": "SPEC_SCOPE_SHA256", "evidence": [{"path": "validation/current-start-review.json", "sha256": "REVIEW_SHA256", "kind": "independent-review"}],
  "effect_state": "applied", "record_state": "recorded", "effect_id": "demo-implement-1-start-901", "owning_phase": "implement",
  "from_status": "specced", "to_status": "in-progress", "occurred_at": "2026-10-07T22:00:00Z",
  "roadmap_before_sha256": "BEFORE_SHA256", "roadmap_after_sha256": "AFTER_SHA256"
}
```

Repeat with current adequate proof yields an event-free no-op; it carries neither the earlier transition's identity/time nor a new one:

```json
{
  "schema_version": "1.0", "feature_directory": "specs/901-phase-lifecycle", "entry_id": "901", "phase": "implement",
  "scope_sha256": "SPEC_SCOPE_SHA256", "evidence": [{"path": "validation/repeat-start-review.json", "sha256": "REPEAT_REVIEW_SHA256", "kind": "independent-review"}],
  "effect_state": "no-op", "record_state": "recorded", "assessment_id": "demo-implement-2-assessment-901", "retained_status": "in-progress",
  "roadmap_before_sha256": "CURRENT_SHA256", "roadmap_after_sha256": "CURRENT_SHA256"
}
```

A rejected pre-write revalidation definitely did not apply its prepared effect. Here final readback is available; if unavailable, omit `roadmap_after_sha256` rather than insert null or the candidate digest:

```json
{
  "schema_version": "1.0", "feature_directory": "specs/901-phase-lifecycle", "entry_id": "901", "phase": "implement",
  "scope_sha256": "SPEC_SCOPE_SHA256", "evidence": [{"path": "validation/prewrite-rejection.json", "sha256": "REJECTION_SHA256", "kind": "quality-check"}],
  "effect_state": "not-applied", "record_state": "recorded", "proposed_effect_id": "demo-implement-1-start-901", "owning_phase": "implement",
  "proposed_from_status": "specced", "proposed_to_status": "in-progress", "reason_code": "stale-source-evidence",
  "roadmap_before_sha256": "BEFORE_SHA256", "roadmap_after_sha256": "OBSERVED_CURRENT_SHA256"
}
```

A verified commit whose receipt persistence fails remains applied, with an explicit recording failure in the command/controller report:

```json
{
  "schema_version": "1.0", "feature_directory": "specs/901-phase-lifecycle", "entry_id": "901", "phase": "implement",
  "scope_sha256": "SPEC_SCOPE_SHA256", "evidence": [{"path": "validation/commit-readback.json", "sha256": "READBACK_SHA256", "kind": "quality-check"}],
  "effect_state": "applied", "record_state": "failed", "record_error": "receipt-persistence-failed", "effect_id": "demo-implement-1-start-901", "owning_phase": "implement",
  "from_status": "specced", "to_status": "in-progress", "occurred_at": "2026-10-07T22:00:00Z",
  "roadmap_before_sha256": "BEFORE_SHA256", "roadmap_after_sha256": "AFTER_SHA256"
}
```

After a writer attempt with unreadable or unestablished actual effects, the outcome retains proposal identity only; this unreadable variant supplies no final or observed digest and no occurrence time:

```json
{
  "schema_version": "1.0", "feature_directory": "specs/901-phase-lifecycle", "entry_id": "901", "phase": "implement",
  "scope_sha256": "SPEC_SCOPE_SHA256", "evidence": [{"path": "validation/readback-failure.json", "sha256": "FAILURE_SHA256", "kind": "quality-check"}],
  "effect_state": "indeterminate", "record_state": "recorded", "proposed_effect_id": "demo-implement-1-start-901", "owning_phase": "implement",
  "proposed_from_status": "specced", "proposed_to_status": "in-progress", "reason_code": "committed-effect-unestablished", "roadmap_before_sha256": "BEFORE_SHA256"
}
```

Persist receipt/recovery in current run storage and verify with a separately assigned Reviewer before next phase action. No-op makes no transition event or roadmap amendment/date. On retry recover the actual effect from roadmap provenance/current bytes and independently revalidate evidence; never blindly repeat or roll back. Earlier authoring/coding success plus failed write reports both outcomes separately. Later failure after successful milestone retains that milestone and pending obligations. No partial outcome implies overall workflow completion, verified, Git integration, publication or acceptance.

## Recovery and Questions

Recover at most three missing edges, in order, stopping at the first unsupported effect. Close Out recovery of an old planned entry requires current authoring-ready proof, attributable authorized start activity with current compatibility/preparation review, and full current completion proof for the amended scope. Old tasks/convergence demonstrate only their recorded scope. Fresh assessments may validate adequate existing work without redoing coding; a report alone cannot fill absent historical start activity. Each effect has its own current snapshot/evidence and post-write verification; after success rebuild before the next edge.

Missing proof/failed command/unsupported owner route/unavailable exact role returns a precise blocker with safe resumption (deliver reviewed component, supply fresh owner review, correct readiness or separately request the necessary workflow). Do not ask a generic approval question to override these conditions. Contradictory target/mapping/evidence, ambiguous authority/recovery, deferred/abandoned reactivation, requested regression or material product/scope/constitutional change yields one focused main-controller request:

```json
{
  "kind": "question",
  "step_id": "resolve-phase-lifecycle-conflict",
  "question": "The advanced roadmap status and current amended scope conflict. Which bounded reconciliation should be authorized?",
  "options": ["Keep state and stop for current-scope evidence", "Provide an explicit reconciliation instruction"],
  "allow_custom_answer": true
}
```

The same child continues after the trusted answer; it revalidates current effect bytes and governing state. Approval cannot make false/missing evidence true. No route invokes another workflow or silently reactivates/regresses an entry.

## Validation Contract

All planned cases record case ID, FR/SC/Story mappings, exact workflow/controller/owner versions and source digests, CLI version/source coordinates, expected/actual effect order, source/pre/post hashes, native/controller provenance, pending future IDs, question/decision and result passed/failed/not-tested with precise gaps. Preserve original Feature 020 evidence; use additive lifecycle IDs and current-scope records. Inspect actual event counts/status/changed paths, not command exits alone.

| Case group | Story 6 | Requirements | Criteria | Required boundary |
|---|---|---|---|---|
| LC001 authoring-ready Draft; LC002 file/label/self-check/success/stale-review variants | 1–2 | FR026–027, FR031–032 | SC012–013 | specced only after independent current quality+brief; no future completion circularity |
| LC003 eligible startup; LC004 stale-readiness/dependency/no-scope/unavailable-role variants | 3–4 | FR026, FR028, FR032 | SC012–013 | in-progress verified before Coder; zero effect or coding on failed preflight |
| LC005 completion; LC006 old-scope/marker/label/unresolved-defect variants | 5–6 | FR026, FR029–030, FR038 | SC012–013, SC016 | implemented before debrief; full current-scope independent proof |
| LC007 repeat/equal/advanced and preserved verification | 7 | FR032–033 | SC014 | zero duplicate events/downgrades; event-free no-op schema rejects event identity/time; advanced labels cannot hide proof gaps |
| LC008 three-edge recovery; LC009 missing edge proof; LC010 contradictory; LC011 absent installed route | 8–11 | FR034–035 | SC014–015 | separate ordered substantiation/effects; current dates; no repeated adequate coding or workflow chaining |
| LC012 consequential categories | 12 | FR031, FR035, FR037 | SC015 | exact focused human decision; no mutation before it |
| LC013 write-then-later-fail and work-then-write-fail; receipt-record failure/retry | 13 | FR036 | SC013, SC015 | truthful state-specific outcomes; reject invented event time/final digest and failed-record-as-unapplied; recovered applied retains original event; no rollback/duplicate effect |
| LC014 mutate roadmap/pointer/dependency/constitution/config/spec/review between assessment and effect | 14 | FR032, FR036, FR038 | SC013, SC015 | stale proposal rejected; material decision invalidated; actual committed bytes inspected; uncertain outcomes omit unestablished final digest/time rather than null or candidate data |
| LC015 verify approve/return/defer and future-obligation variants | 15 | FR029–030, FR037–038 | SC016 | explicit verified gate retained; return/defer preserves implemented; no acceptance/release claim |

Source graph tests additionally assert no dangling/undeclared native nodes, exact preflight coverage of recovery branches, no Coder/debrief before verified milestone, bounded recovery maximum three effects, and preserved correction/progress caps. Packaging/manual tests assert coordinated owner versions/source hashes and equivalent manual decisions. Negative fixtures must fail for unsupported/duplicate JSON/path escapes, mixed legacy/new brief inputs and tampered owner receipts. Mock traces are deterministic ordering evidence; separately requested live native/consumer cases retain their narrower claim boundary.

# Feature 023 Data Model

These entities describe validation state and portable observations. Existing scope, assessment, history, task-tracking and receipt schemas remain authoritative; this feature does not migrate them or create a new production persistence layer.

## Table of Contents

The model connects source definitions to selected-route effects and retained evidence.

- [Workflow Definition and Dependency](#workflow-definition-and-dependency)
- [Validation Diagnostic](#validation-diagnostic)
- [Selected Route State](#selected-route-state)
- [Historical and Current Evidence](#historical-and-current-evidence)
- [Validation Observation](#validation-observation)

## Workflow Definition and Dependency

**Definition fields**: Existing `workflow.id`, `workflow.version`, inputs, steps, requirements and source digest. Each node has globally unique `id`, reviewed kind and optional exact `farmboy` assignment. Switch cases map choices to step arrays; optional sibling `default` holds an array. `cases.default` is invalid; empty arrays are supported skips.

**Derived dependency fields**: `consumer_step_id`, `field_path`, `reference`, `producer_step_id`, output key path, sequence position and enclosing branch/loop ancestry. These are ephemeral validation data, not new authored workflow fields. IDs must exist; an ordinary payload reference cannot be self/forward or cross mutually exclusive branches. Branch joins retain prior-producer states sufficient to reject a consumption unavailable on a reaching structural path. Existing loop conditions have their reviewed after-body timing and carrier rules.

**Relationship**: One definition contains many nodes/references; one consumer may reference several producers. Definition feasibility establishes no actual producer output or delegated authority.

## Validation Diagnostic

**Fields**: `reason_code`, `workflow_id`, `step_id`, `location`, `offending_reference`, `correction`, `boundary`, and applicable `resume_action`. Codes use stable lowercase hyphenated strings. Root errors use an explicit root location and absent step ID, rather than inventing a step; node errors always identify the exact node. `offending_reference` is an authored structure/reference identifier, never a raw supplied input value or transcript.

**Rules**: Every switch/template definition diagnostic supplies workflow/step/location/correction. Nested fallback correction explicitly directs placing `default` alongside `cases`. Source and runtime projections share the same contextual data; existing readable `ValueError` text remains compatible. Runtime stops include a safe action and prevented consuming step.

## Selected Route State

**Fields**: Existing definition/install fingerprints, resolved inputs, completed applicable output map, selected choice, selected node IDs, current consuming step, applicable pass, next successor, and observed/prevented dispatch trace. Only the test observation trace is newly persisted by the harness; production traversal remains main-controller context.

**Transitions**: definition-valid → required workflow inputs valid → expression available → supported branch selected → selected child inputs available → effect permitted → completed output captured → next consuming boundary. Any failed guard stops before its affected effect. Empty branch moves directly to the successor. Untaken nodes acquire neither completed outputs nor branch-local obligations. An output from an earlier pass is not fresh proof for a new pass's producer.

## Historical and Current Evidence

**Historical fields**: Existing immutable scope/digest, initial assessment, independently retained scope-bound assessment digest, finding baseline/source preimages, execution-history predecessor chain, and lifecycle proposal/preimage/receipt identity. Main retention happens before effects; child-provided hashes alone do not establish trusted retention.

**Current fields**: Current contained evidence paths/SHA-256 values, independent review, validated Tasker successor chain, actual producer pairs, reread history, recomputed eligibility and fresh readiness. `post-pass-capture` retains its existing exact request fields: `scope`, `trusted_request_reference`, `retained_scope_sha256`, `entry_history_sha256`, `task_tracking_successors`, `producer_pairs`, `eligibility_request`, `completion_branch`.

**Rules**: Preserve original history bytes/digests while actual source/task bytes may legitimately differ after reviewed work. Independently validate current hashes and permissible task deltas. Re-entry combines trustworthy historical binding with valid current evidence and remaining budgets; neither alone suffices. Question answers/admin changes/markers do not manufacture substantive progress or reset counters. Applied roadmap receipts use the validated roadmap preimage for pre-effect review; unrelated artifacts remain current-checked and the writer is not replayed during readback.

## Validation Observation

**Fields**: Scenario/requirement IDs; source or installed environment kind; `execution_mode`; component IDs/versions/raw source digests; source repository/commit/relative coordinates/dirty state; tested CLI and runtime; installed inventory digests; expected/observed decision, reason/action, selected/completed/prevented node IDs, effect counts, retained before/after hashes and counter values; parity result.

**Rules**: Repository-relative coordinates only, with no host paths, personal identifiers, secrets or raw transcripts. Hashes distinguish raw YAML/package bytes from normalized loaded-definition digests. Simulated Reviewer/Tasker outcomes are labelled deterministic; they cannot establish native identity, effective settings, publication, stock compatibility, adoption or acceptance. Every negative observation links a valid control and identifies its single mutation. See [connected-observations.md](contracts/connected-observations.md).

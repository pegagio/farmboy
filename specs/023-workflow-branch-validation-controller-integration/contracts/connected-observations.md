# Connected Controller Observation Contract

Observations are feature-local validation evidence, not production authority or a new controller state format. Extend existing snapshot reports and fixture adapters with these fields; preserve current scope/history/review/capture schemas.

## Scenario Execution

A scenario defines an ID, requirement IDs, valid control, one optional negative mutation and expected decision/blocker. Run the same description against source and supported installed snapshot modules/workflow bytes. Fixture functions prepare files and deterministic child outputs; all selection, rendering, scope, eligibility, activation, tracking, capture and progress decisions call production APIs. Trace actual reached boundaries instead of returning precomputed routing outcomes.

Positive trace order is assessment → selected source dispatch → independent review → allowed tracking → post-pass capture → guarded re-entry. Session/attempt records precede simulated source effects. Source trace and installed trace must agree on selected/skipped nodes, required-input boundary, continuation decision and limits; differences fail parity. A negative must first demonstrate a valid control, then reach its intended single guard with all preceding conditions valid. Zero dispatch after that guard is asserted.

## Portable Observation

The example illustrates the required shape; implementation supplies actual hashes/versions/results and never emits illustrative placeholders as evidence.

```json
{
  "scenario_id": "reviewed-task-marker-reentry",
  "requirement_ids": ["FR-007", "FR-008", "SC-004"],
  "environment_kind": "installed",
  "execution_mode": "deterministic-simulated-dispatch",
  "provenance": {
    "source_repository": "pegagio/farmboy",
    "source_commit": "<observed-commit>",
    "source_dirty": true,
    "source_coordinates": ["workflows/farmboy-implement/workflow.yml"],
    "components": [{"id": "farmboy-controllers", "version": "<observed-version>", "source_sha256": "<observed-raw-sha256>"}],
    "workflow_sha256": "<observed-raw-yaml-sha256>",
    "loaded_definition_sha256": "<observed-normalized-graph-sha256>",
    "installed_inventory_sha256": "<observed-inventory-sha256>",
    "tested_cli_version": "specify 1.0.10.dev0+pegagio.2",
    "python_version": "3.11.16"
  },
  "expected": {"decision": "continue"},
  "observed": {"decision": "continue", "reason_code": "<actual-production-reason>", "selected_step_ids": [], "prevented_step_ids": [], "source_effect_count": 1},
  "historical_binding_unchanged": true,
  "current_evidence_checked": true,
  "counters_before": {"coder_sessions_started": 1, "source_attempts_started": 1},
  "counters_after": {"coder_sessions_started": 1, "source_attempts_started": 1},
  "parity": "match",
  "live_agent_observation": "unverified"
}
```

Every actual component used has its own ID/version/source digest, including bundle, workflow, controller, agents and required extensions. Record source coordinates/commit and installed bytes rather than assuming version equality establishes parity. Include actual expected/observed reason/action, effect/dispatch records, original assessment/baseline before/after hashes and current evidence references. For blocked observations include `resume_action`, valid-control ID and single mutation. For lifecycle readback include effect/receipt identity, roadmap mutation count and receipt before/after digest.

Comparisons normalize environment-specific paths and file identity only in the report, not evidence validation. Current contained files still undergo production hash checks. No raw transcripts, secrets, personal names/usernames or absolute host paths appear in portable output. Deterministic synthetic role labels do not prove native agent identity/settings. No observation grants publication, stock Spec Kit compatibility, adoption, Git integration, roadmap verification of the real feature, or acceptance.

## Required Guard Families

The implementation records both positive sequences and separate otherwise-valid negatives for historical proof, stale current evidence, unauthorized task delta, missing/invalid/wrong-branch producer output, no substantive progress, both exhausted budgets, assignments/gates/relay and installation drift. Do not collapse budget and no-progress into one case that blocks only on the first guard. Invalid definition observations record zero delivery effects and dispatches. Post-effect readback retains applied receipt/preimage without replaying its writer and keeps non-roadmap current-hash rejection.

# Workflow Validation Boundary Contract

This contract extends current controller validation and diagnostics. It does not add workflow syntax, authorize effects or replace independent evidence checks.

## Definition Boundary

`validate_workflow_definition(definition)` remains read-only and either returns normally or raises `ValueError`. A contextual `ValueError` subclass may expose a diagnostic dictionary while preserving existing callers; the inventory CLI projects that dictionary in JSON and CLI errors retain readable text. Source inventory, catalog packaging/verification/preflight and installed `inspect` use this same implementation.

A node-level definition diagnostic has the following shape; field names are the planned diagnostic projection, not a claim that current source already emits it.

```json
{
  "reason_code": "misplaced-switch-default",
  "workflow_id": "farmboy-implement",
  "step_id": "route-readiness-before-core",
  "location": "steps[5].cases.default",
  "offending_reference": "cases.default",
  "correction": "Place default alongside cases on this switch.",
  "boundary": "definition",
  "resume_action": "correct-source-definition-and-revalidate"
}
```

Equivalent root failures identify `location: workflow` or `steps` and an explicit null `step_id`; they cannot manufacture a node ID. Structural/template failures always identify workflow and exact consumer/switch step. Do not include raw input values, rendered prompts or host paths. Preserve existing reason codes for unrelated evidence helpers.

The following structures have distinct outcomes.

| Structure/reference | Definition outcome | Selected runtime outcome |
|---|---|---|
| `cases: { skip: [] }` | Valid supported empty case | Zero child effects, then successor |
| `cases: { run: [...] }, default: []` | Valid top-level empty fallback | Unknown choice selects empty fallback |
| `cases: { default: [] }` | Invalid reserved fallback location | Invocation stops before effects |
| Missing fallback with supported named cases | Valid switch | Unknown selected choice blocks |
| Null/non-list branch or non-mapping cases | Invalid, exact field/type correction | Loaded invalid snapshot rejected before effects |
| Earlier same-route producer template | Valid without output | Check actual output at consumption |
| Unknown/self/forward/mutually exclusive producer | Invalid, consumer/reference diagnostic | No affected dispatch |
| Producer available only on one path to post-join consumer | Invalid unconditional consumption | Move consumer within producing branch; never infer prose termination |
| Supported after-body loop condition | Validate existing carrier/condition contract | Evaluate after body and retain readiness short-circuit |

Examples use the existing `{{ steps.produce.output.result }}` form. Definition validation proves producer ID/order/route, not that `result` exists or has a business meaning. Those checks use runtime rendering and existing typed helpers.

## Runtime Boundary

Preserve `render_template(value, inputs, outputs)` and `select_switch_branch(switch, choice)` APIs. Render only a switch's expression/applicable metadata, select using the production branch helper, and render selected children separately. Untaken branches are structurally checked, but their output availability is never requested. Explicit empty branches remain empty and next-node traversal proceeds normally.

Unavailable selected references block at the consuming step before child dispatch or mutation, identifying consumer ID, authored reference, reason and safe action. A safe action means restore/revalidate the current required producer/installation/evidence within the original scope, not fabricate an output or skip a gate. Existing installation-fingerprint rechecks and current evidence validators retain precedence. Do not use stale previous-pass outputs to satisfy current production.

## Effect and Recovery Boundary

Source/catalog checks must precede archive output approval and any consumer install/refresh writes. Record invalid-delivery before/after inventories and zero started install/dispatch effects. Deliberately invalid installed workflow tests use disposable consumers with otherwise valid installed prerequisites; distinguish loader/ownership rejection from graph diagnostic rejection and assert whichever boundary is actually reached.

Changed installation, unavailable assignment, invalid gate/answer and unresolved consequential input retain existing protocol safe stops. Recovery revalidates actual source/target/evidence, preserves partial effects and receipts, and never chooses another workflow or grants integration/acceptance. Manual-prompt guidance follows the same expression/selected-child rendering boundaries.

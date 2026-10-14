# Feature 023 Research

The decisions below use current owning source at commit `54b394e` and the approved specification. They are source inspection findings, not claims that new Feature 023 scenarios have executed.

## Table of Contents

Research resolves the technical allocation without expanding scope.

- [Shared Definition Validation](#shared-definition-validation)
- [Producer Timing and Selected Routes](#producer-timing-and-selected-routes)
- [Connected Evidence Harness](#connected-evidence-harness)
- [Delivery and Provenance](#delivery-and-provenance)
- [Historical Regression Boundaries](#historical-regression-boundaries)
- [Resolved Decisions](#resolved-decisions)

## Shared Definition Validation

**Observed**: `controllers/farmboy/scripts/python/controller.py` has `validate_workflow_definition`, `validate_workflow_graph`, `validate_template_forms`, `collect_agent_assignments` and runtime `inspect`. Graph validation checks node types, duplicate IDs, assignments, branch body types and reviewed loop carriers. Template validation accepts supported syntax and known workflow inputs but does not establish referenced producer identity/order/branch feasibility. `cases.default` is presently traversed as a named case, rather than specifically diagnosed as a misplaced fallback. `tools/validate_workflows.py` projects definitions; its loading checks are root/inventory checks, not equivalent production graph validation. Catalog workflow checks currently compare identity/version/pins/digests.

**Decision**: Extend the existing controller definition entry point, including contextual diagnostics and producer feasibility, and call it before source projection and catalog package/delivery effects. Validate malformed containers before recursive visitors. Keep the production implementation in controller source so source and installed callers share semantics.

**Rationale**: One validator closes the delivery/runtime gap without separate schema/routing implementations or upstream Specify changes.

**Alternatives considered**: A second JSON Schema validator would add an unapproved dependency and diverging semantics. Inventory-only assertions would miss installed/runtime equivalence. Runtime-only rejection leaves malformed delivery possible. Importing the controller with the existing importlib loader pattern avoids introducing a packaging framework.

## Producer Timing and Selected Routes

**Observed**: `render_template` recursively renders every dictionary/list supplied to it and raises on absent referenced output. `select_switch_branch` preserves empty lists and blocks unknown choices without a fallback. Existing `test_workflow_improvements.py` strips `cases`/`default` before rendering switches, then selects the branch; `test_workflow_paths.py` renders expressions directly. `test_implement_switch_routing.py` protects WR-01 top-level defaults and preparation/source mutual skips, but these small cases do not establish the full sequence with branch-local missing outputs. The controller protocol already says to resolve prior outputs only after completion.

**Decision**: Document and test step-local switch expression rendering and selected-child consumption through existing APIs. Extend static template validation using indexed IDs, branch ancestry and bounded prior-producer state propagation; payload references must be earlier and route-compatible. Existing loop predicates are checked after the body under their reviewed carrier/short-circuit rules. Actual output key/value validity remains a runtime check.

**Rationale**: Definition feasibility does not require outputs at invocation. Untaken bodies remain structurally validated but are never rendered for current availability. A branch-local producer cannot satisfy an unrelated consuming branch; a consumer after a join needs a producer available on every structural path reaching it. Prose stop prompts do not create static control-flow facts.

**Alternatives considered**: Eager whole-graph rendering falsely requires unproduced/untaken outputs. Relaxing unresolved templates hides real missing inputs. Full Cartesian route enumeration is unnecessary for the limited structured graph. New general expression/dataflow languages or output schemas would overreach this feature. Preserve supported source behavior with local branch placement where needed rather than inventing termination semantics from prose.

## Connected Evidence Harness

**Observed**: `tests/implementation_scope_snapshot.py` contains `exercise_installed_scope_matrix`, `_exercise_installed_task_revision_successor`, `_capture_post_pass_command` and `_capture_post_pass_state`. It uses installed prompt/CLI capture, actual scope/history/progress helpers and fixture source changes. `test_snapshot_validation.py` installs/refreshes/removes development snapshots and records provenance. Existing `test_controller.py` historical tests, `test_implementation_progress.py` defect tests and route/path tests provide narrower controls. Harness helpers construct inputs/evidence; they must not substitute copied guard or routing logic.

**Decision**: Extend this adapter and snapshot test with a paired source/installed scenario entry point and explicit connected traces. Use production `render_template`, `select_switch_branch`, activation/history, tracking validator, `post-pass-capture`, `implementation-progress-scoped` and route helpers. Factor only repeated fixture setup/evidence recording needed for the two positive and isolated negative sequences, retaining existing matrix behavior.

**Rationale**: Concrete reuse covers the missing connected boundary without creating another executor or waiting for Feature 025. Deterministic synthetic Reviewer/Tasker results test protocol enforcement while source/evidence mutations substantiate progress; they do not prove native Reviewer identity or live code quality.

**Alternatives considered**: Helper-only assertions do not meet FR-007/013. A new generic workflow runner duplicates the controller. A live-agent requirement adds nondeterminism and is explicitly unnecessary. Expanding all existing lifecycle scenarios is avoidable; representative parity plus focused regression guards is sufficient.

## Delivery and Provenance

**Observed**: `tools/catalog.py` provides `build_development_snapshot` and `install(..., development_snapshot=True, source_overrides=...)`. Snapshot integration uses a temporary initialized consumer, pinned archive extraction, `LocalCatalog`, explicit matching `FLOW_ROADMAP_SOURCE` and `SPECIFY_BIN`. The snapshot test skips if CLI or matching roadmap source is unavailable. Bundle source pins FarmBoy 0.18.3, controller 0.9.1, agents 0.2.0, flow-roadmap 0.4.0, flow-wiki 2.0.1 and farmboy-feedback 0.2.1. Current release metadata's controller source commit predates `54b394e`.

**Decision**: Validate the current source development snapshot, not released catalog bytes assumed to contain the fix. Reuse checksum-verified matching extension sources and supported installation. Treat missing integration prerequisites as an explicit coverage gap. Preserve released metadata/history; version/package changes belong to implementation delivery, with observed digests recorded then.

**Rationale**: Source/installed parity requires matching bytes and initialized core skills/extensions. Existing installation handles ownership and preservation. No external-owner edits or new dependency are needed.

**Alternatives considered**: Copying only controller.py into a fake consumer does not prove installation parity. In-place edits in the active consumer confuse source/effects. Relabelling a development snapshot as released or treating skipped tests as coverage would misstate evidence.

## Historical Regression Boundaries

**Observed**: `_validate_retained_implementation_assessment` verifies an independently retained scope/envelope digest and validates historical envelope structure without current-file comparison. Current progress remains independently checked. `phase_lifecycle.workflow_check` now uses the applied roadmap's validated preimage for retained pre-effect review while checking other sources against current bytes, preserving receipt recording/collision rules. Existing tests cover the corrected historical/current distinction.

**Decision**: Freeze these fixes as regression inputs: preserve original assessment/digests/source preimages across genuine changes, reject invalid retained proof and stale current evidence separately, and validate post-effect lifecycle readback without replaying the writer. Do not redesign caps, fabricate old proof from current files or mutate historical receipts.

**Rationale**: 023 strengthens executable confidence in the fixes and surrounding guards; 024/026 own separate continuation changes.

**Alternatives considered**: Re-baselining original evidence after effects erases trust. Treating every digest mismatch as stale rejects valid reviewed work. Accepting only matching historical digests without current checks weakens guards.

## Resolved Decisions

All technical unknowns are resolved in [plan.md](plan.md). No new dependency, tool, engine, external-owner change or substantive operator decision is proposed. Implementation may reveal source-definition feasibility mismatches; reconcile only behavior-preserving branch placement under the approved scope, and return a blocker if the resolution changes observable authority or scope. No implementation tests were run as part of this research; [quickstart.md](quickstart.md) specifies the required executable checks.

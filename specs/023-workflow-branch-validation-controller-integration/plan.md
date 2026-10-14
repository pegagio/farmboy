# Implementation Plan: Workflow Branch Validation and Controller Integration Coverage

**Feature**: 023 | **Date**: 2026-10-13 | **Spec**: [spec.md](spec.md)

**Git state**: Detached checkout at planning time. The setup helper reports feature identity `023-workflow-branch-validation-controller-integration`; this is not evidence of an existing Git branch. No branch creation or integration is authorized.

## Summary

Reject malformed workflow structures and impossible template dependencies through the existing controller validator before delivery, then prove selected-route availability and connected continuation through production APIs in source and disposable installed consumers. Extend existing `unittest` suites and `implementation_scope_snapshot.py`; do not add a routing engine or redesign continuation accounting. WR-01, WR-02 and commit `54b394e`'s post-effect roadmap-preimage correction are existing regression baselines.

## Table of Contents

The design separates definition feasibility, selected-step current availability, and evidence-based continuation.

- [Technical Context](#technical-context)
- [Constitution Check](#constitution-check)
- [Project Structure](#project-structure)
- [Definition and Runtime Design](#definition-and-runtime-design)
- [Connected Coverage](#connected-coverage)
- [Requirement Allocation](#requirement-allocation)
- [Delivery and Validation](#delivery-and-validation)
- [Risks and Decisions](#risks-and-decisions)

## Technical Context

Implementation stays within the portable controller and catalog tooling.

- **Language/Version**: Python 3.11.16, Bash launchers, YAML definitions and JSON evidence.
- **Primary Dependencies**: Existing PyYAML 6.0.3 and Specify CLI `1.0.10.dev0+pegagio.2`; standard-library `unittest`, `tempfile`, `hashlib` and `subprocess`, plus existing local catalog HTTP fixtures. No new dependencies/frameworks/build tools.
- **Storage**: Source YAML, install ownership/digest records, append-only consumer execution history and feature-local portable validation observations. No new production journal/database.
- **Testing**: Existing controller/graph/path/catalog tests and disposable snapshot integration. Deterministic simulated child results establish regression observations; live-agent execution remains unverified.
- **Target Platform**: Current supported Codex integration and pinned runtime. Record actual tested host/CLI; do not infer untested platform support.
- **Project Type**: Reusable workflow/controller source packages and consumer installation tools.
- **Performance Goals**: Bounded traversal of eleven owned definitions (ten active plus deprecated stop-only Start Feature), avoiding full Cartesian route expansion in production. No service latency target.
- **Constraints**: Preserve exact named assignments, human gates, same-child relay, manual fallback, retained historical proof, current evidence checks and existing caps. Edit reviewed source; mutate installed copies only in disposable negative tests.
- **Scale/Scope**: Existing controller validation, source inventory and catalog preflight; focused harness/fixture extensions and documentation. No independent-extension change, metrics dependency, or Feature 024/025 redesign.

## Constitution Check

Constitution 8.0.0 was evaluated before research and re-evaluated against this design. These self-checks do not replace independent plan review.

| Principle | Pre-research constraint | Post-design result |
|---|---|---|
| I — Mutable reviewed feature unit | Preserve approved spec, settled decisions and historical features | Pass: technical design covers 023 without rewriting scope/history |
| II — Human authority | Plan only; preserve assignments, gates and existing accounting | Pass: no tasks, implementation, roadmap effect, Git or acceptance authority |
| III — Generic boundaries | FarmBoy owns generic source; extensions retain their policy | Pass: no Diagram dependency or independently owned source edit |
| IV — Reviewed source/fallback | Reuse validators/harness; preserve manual path | Pass: shared controller entry point and existing tooling; no new engine/dependency |
| V — Evidence | Disposable initialized consumers, pinned provenance, bounded claims | Pass: paired source/installed scenarios and portable observations; simulation explicitly labelled |

No constitutional exception or unresolved substantive decision is requested.

## Project Structure

This command creates only the feature's design artifacts; `tasks.md` belongs to separately invoked task generation.

```text
specs/023-workflow-branch-validation-controller-integration/
  plan.md
  research.md
  data-model.md
  quickstart.md
  contracts/
    validation-boundaries.md
    connected-observations.md
```

Implementation extends the following existing owning locations.

```text
controllers/farmboy/scripts/python/controller.py
controllers/farmboy/controller-protocol.md
controllers/farmboy/scripts/python/phase_lifecycle.py  # preserve existing fix; change only if regression proves needed
tools/validate_workflows.py
tools/catalog.py
tests/test_controller.py
tests/test_workflow_graph.py
tests/test_workflow_paths.py
tests/test_implement_switch_routing.py
tests/test_catalog.py
tests/test_implementation_progress.py
tests/test_phase_lifecycle.py
tests/implementation_scope_snapshot.py
tests/test_snapshot_validation.py
tests/consumer-fixtures/workflow-improvements/implementation-scope-cases.json
docs/installation.md
tests/consumer-fixtures/README.md
workflows/README.md
```

**Structure decision**: Extend focused tests and existing scenario fixtures. The snapshot adapter already drives installed post-pass capture and scope helpers; its scenario functions are sufficient. Do not create a generic executor or require Feature 025's broader reusable fixture work.

## Definition and Runtime Design

`validate_workflow_definition()` remains the common entry point. Its graph/template helpers inspect the full graph without rendering outputs. Preserve the existing `ValueError` failure contract, adding structured location/correction context and a stable diagnostic projection in source inventory JSON; keep readable CLI errors. See [validation-boundaries.md](contracts/validation-boundaries.md).

1. Validate root, node and branch types before recursion; retain duplicate-ID, assignment, carrier, integration and condition guards. Reserve `default` outside `cases` and explicitly reject `cases.default`. Accept `[]` for supported case/default bodies; distinguish absent fallback from present empty fallback.
2. Index step IDs and supported template references with consuming field location and enclosing branch/loop ancestry. Reject unknown producers, ordinary payload self/forward references and mutually exclusive branch references. Propagate possible prior-producer sets through ordered sequences and branch joins; consumption outside a branch must be feasible on every structural path reaching it. Avoid full path enumeration. Never infer termination from prose stop prompts: keep consumers inside their producing branch or use existing structured carriers if existing definitions need local reconciliation, preserving gates and observable successors.
3. Handle loop predicates separately from ordinary payload templates. Existing conditions read body assessments after execution; readiness-gated conditions short-circuit non-continue outcomes before requiring readiness. Preserve reviewed assessment-only-first-pass and implementation-scope carrier rules. A prior iteration does not authorize an otherwise invalid forward payload reference.
4. `tools/validate_workflows.py` calls the controller validator before projection. Catalog `build`, `build_development_snapshot` and `verified_release` validate source definitions before approving assets. Install/refresh checks the exact workflow bytes being served before bundle/controller effects. Invalid source causes no package/delivery effects and consumer before/after inventories match.
5. Runtime `inspect` validates the loaded installed graph with the same validator. Traversal renders switch expression/applicable metadata only, calls `select_switch_branch()`, then renders each selected child at consumption. Do not recursively render a switch's untaken bodies. Missing selected output blocks before dispatch; unsupported choice without fallback blocks; explicit empty selection reaches the next declared node.

Definition checks prove producer identity/order/route feasibility, without requiring output values or guessing producer field schemas. Runtime `render_template()` and typed controller helpers check actual key-path/value/evidence validity at consumption. Render maps contain only completed outputs applicable to the current pass: stale prior-pass or untaken-branch outputs cannot satisfy a new consumption. Retain output digests and helper evidence where current policy requires them.

## Connected Coverage

Reuse source module loaders, scope fixtures and `tests/implementation_scope_snapshot.py`. A shared scenario description contains input mutations and expected results, never copied routing/guard decisions. Run each scenario with source modules/source YAML and with modules/YAML loaded from a supported disposable installation of the same snapshot. Start each negative from its own valid positive control.

Both positive sequences capture active scope, current initial assessment and its independently retained scope/envelope digest before effects. Advance actual Implement nodes using production rendering/branch selection; establish eligibility/activation; append session/attempt events before simulated source effects; materialize a small contained source correction; obtain deterministic Code Reviewer evidence; validate Tasker tracking; invoke actual `post-pass-capture`; then call `implementation-progress-scoped`/`implementation-route` with returned current state. Observe selected and prevented dispatch IDs and successor order. No-op Codex demonstrates dispatch only; substantive fixture changes and current review proof remain necessary.

- **Task-resolution case**: Independently prove one requested task complete, allow its marker-only tracking update, retain another eligible task/finding and reach guarded re-entry. Current task digest differs while original assessment/baseline bytes and retained digest remain identical.
- **Source-correction case**: Resolve one prior finding with a genuine source delta and current reproduction proof while its parent task remains open. Keep original finding preimages/ownership and remaining obligations; capture and re-entry verify current review/history. Preserve the existing ability for a later regression-only pass to close the originally corrected finding.

Negative cases mutate one guard in an otherwise valid connected state, assert its blocker/action and zero subsequent source dispatch, and verify unchanged retained records/counters: missing/altered/forged/unbound historical binding; stale current review hashes; task description/owner/marker edits without validated authority; missing/non-ready/wrong-branch Tasker/validator outputs; no prior substantive ID resolved; exhausted Coder session and source-attempt budgets; missing/unavailable assignment; unresolved human gate; wrong-child answer; installation drift. Exhausted-budget controls retain genuine reviewed progress; no-progress controls retain valid evidence/history/tracking and available budget. Administrative changes, answers and restarted children earn no source credit and never reset budgets.

Preserve post-effect roadmap regression in phase-lifecycle tests and representative installed parity: applied receipt readback uses the approved roadmap preimage while other artifacts remain current. Reassess the same effect without invoking its writer twice; assert ledger mutation count and retained receipt/effect identity unchanged. A separately altered non-roadmap source must still block. This disposable scenario authorizes no real project roadmap effect.

## Requirement Allocation

The map makes coverage reviewable without generating implementation task IDs.

| Requirements / criteria | Owning design and evidence |
|---|---|
| FR-001–003, SC-001 | Shared definition/graph/template validation; full owned inventory; malformed/default/type/reference controller/graph/catalog cases |
| FR-004–006, SC-002–003 | Step-local rendering/production selection; preparation/source skips, empty/default, unknown choice and missing selected-output path tests plus installed matrix |
| FR-007–008, SC-004 | Two connected positive source/installed sequences retaining historical scope/assessment/preimages while checking current review/tracking/capture |
| FR-009–010, SC-005 | Single-guard mutations with valid controls; production history/progress/cap guards; both budgets and administrative/question/restart non-credit checks |
| FR-011–012 | Production assignment/gate/answer/fingerprint checks and protocol; no fallback, next phase, integration or acceptance effects in observed trace |
| FR-013–014, SC-006 | Existing snapshot adapter/test and common scenarios; paired same-snapshot outcomes, failure on any discrepancy |
| FR-015–017, SC-007 | Portable observation contract, provenance/mode checks and source-owned installation/validation/manual guidance |

## Delivery and Validation

[quickstart.md](quickstart.md) gives current executable entry points, prerequisites and expected assertions. Run focused suites, then source inventory and catalog boundaries, then initialized-consumer parity. Integration skips block FR-014/SC-006 completion claims. Catalog release metadata predates the current controller fix; use supported development snapshot installation for parity and preserve released history.

Implementation observations belong under this feature's `validation/` and identify exact component versions, source/workflow/controller hashes, commit/dirty state, installed inventory digests, tested CLI/runtime and execution mode. Compare decisions and effects rather than paths/inodes. Update source protocol, validation, installation and manual docs to explain diagnostics and safe next actions. If package versions/pins or generated diagrams/catalog payloads need refresh, explain the necessary source/package change first and regenerate with supported tooling; no publication is implied.

## Risks and Decisions

False rejection of supported loops/branches, premature rendering and negatives that fail on the wrong guard are the material risks. Full source inventory, carrier fixtures, step-level traces, paired valid controls and exact reason/action assertions address them. Static validation deliberately avoids guessing output schemas or prose control flow; current runtime evidence validation stays authoritative. No unresolved decision remains. Continuation-policy or external-owner changes require operator resolution and spec reconciliation.

**Complexity tracking**: No constitutional violation or added engine/framework/dependency/storage subsystem.

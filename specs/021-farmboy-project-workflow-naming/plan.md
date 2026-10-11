# Implementation Plan: FarmBoy Project and Workflow Naming

**Branch**: `farmboy` | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

This revised plan describes a pure naming cutover plus explicitly approved mechanical native CLI prompt-dispatch corrections using existing workflow inputs. The operator explicitly removed consumer migration from scope. Earlier migration-oriented planning and review are superseded. The subsequent explicit Tasks invocation authorized task drafting and included independent task-quality review; it does not establish a fresh standalone Plan review of this design. Current analysis/remediation reconciles the mutable artifacts with the separately reviewed Feature 022 correction integrated by merge `6738a06`.

## Table of Contents

- [Approach](#approach)
- [Constitution Check](#constitution-check)
- [Source Layout After Authorized Implementation](#source-layout-after-authorized-implementation)
- [Implementation Boundaries](#implementation-boundaries)
- [Validation](#validation)
- [Risks and Non-Goals](#risks-and-non-goals)

## Approach

Perform coordinated name/path substitutions in reviewed source, update references and existing test expectations, and rebuild packages through the existing catalog builder. The only behavior correction is the operator-approved binding of existing prompt nodes to their workflows' already-declared `integration` inputs, fixing the observed disposable Specify CLI dispatch failures. No command capability, flag, persistent record, compatibility layer or other workflow behavior is added.

Use [contracts/naming.md](contracts/naming.md) for the exact ten workflow/skill bindings, nine agent roles, renderer and package mappings. Inspect old-name occurrences with `rg`; replace owned active identities while retaining independent roadmap/wiki IDs, unrelated schema fields, actual source URLs and immutable history. No new stored occurrence-inventory schema is required.

The existing Python/Bash/YAML/JSON/TOML/Markdown architecture and management interfaces remain in place. Preserve the corrected behavior delivered by [Feature 022](../022-workflow-owned-roadmap-boundary/spec.md) at reviewed correction `7a43bb3`, integrated by `6738a06`, using [boundary-merge.md](validation/boundary-merge.md) as provenance. Workflow-owned milestone policy and authoring proof, generic authorized amendments through roadmap 0.4.0, independent effect readback and retained receipts are inherited behavior, not new rename functionality. Earlier coupled baseline `b6dcae9` and rename checkpoint `87227a1` are historical states, not the graph/contract preservation baseline. Current pins include bundle 0.18.3, Clarify 0.5.1, controllers 0.9.1, Specify 0.4.1, Plan and Tasks 0.5.1, Analyze and Remediate 0.6.1, Implement 0.9.1 and Close Out 0.9.2, Select Feature 0.2.1, Converge 0.5.1, and Wiki Lint Update 0.2.1. Research decisions are in [research.md](research.md), existing schema boundaries in [data-model.md](data-model.md), unchanged management behavior in [contracts/consumer-management.md](contracts/consumer-management.md), and validation commands in [quickstart.md](quickstart.md).

## Constitution Check

The operator explicitly approved and applied [Constitution 8.0.0](../../.specify/memory/constitution.md) on 2026-10-10. Principle III now establishes FarmBoy and the approved owned feedback and delegation-key identities. Its bounded transition permits existing reviewed source and installed components to remain operative until separately invoked rename implementation and compatible installation take effect. The identity amendment is satisfied; FR-015 and T001 remain prerequisite verification before implementation.

The earlier planning-only exception authorized research/design under Constitution 7.0.0 and remains historical phase authority. It did not authorize tasks or implementation; the later explicit Tasks invocation separately authorized task drafting. The operator subsequently approved the bounded prompt-dispatch batch described in the current specification; that approval is limited to the previously unbound existing prompt nodes and associated workflow/bundle patch-version bumps.

The pre-research and post-design constitution checks pass for the rename and bounded correction under 8.0.0. Principles I, II, IV and V remain unchanged: current mutable artifacts may be reconciled; human authority, manual fallback, reviewed source and bounded evidence remain required. The correction approvals authorize the two named Clarify prompt bindings, the mechanical batch of 109 remaining unbound prompt nodes, and their associated workflow and bundle patch-version updates; they do not authorize actual-consumer operations, external changes, acceptance or Git integration.

## Source Layout After Authorized Implementation

Rename owned directories without reorganizing responsibilities. These paths are already present in the partial rename and merged correction; the table records the mappings to preserve, not work executed by this artifact reconciliation.

```text
bundles/farmboy/                         # bundles/spec-kit-flow/
controllers/farmboy/                     # controllers/flow-kit/
  scripts/python/milestone_policy.py    # Reviewed Feature 022 workflow-owned policy
  scripts/python/phase_lifecycle.py     # Local adapter, proof, generic write and effect readback
  skills/farmboy-<purpose>/              # Ten existing controller skills
agents/farmboy/                          # agents/flow-kit/
  agents/farmboy-<role>.toml              # Nine existing roles
skills/farmboy-render-workflow/          # Independently distributed renderer
workflows/farmboy-<purpose>/             # Ten active purposes
workflows/farmboy-start-feature/         # Deprecated stop-only source
extensions/farmboy-feedback/            # extensions/flow-feedback/
extensions/farmboy-feedback-maintainer/ # extensions/speckit-flow-feedback-maintainer/
```

Update manifests, exact role declarations/allowlists, bootstrap/helper references, `.worktreeinclude`, current docs and test fixtures together. New helper paths use `.specify/farmboy/`; new run records use `.specify/farmboy-controllers/`; established `.agents/skills/`, `.codex/agents/`, native registry schemas and independent extension paths retain their conventions. Existing completed history is left where it is; no transfer/import tooling is added.

## Implementation Boundaries

The implementation changes identities and references, with an explicitly approved mechanical integration binding correction to existing prompt nodes.

- Rename product/package identifiers and relevant files/directories, retaining existing purposes, inputs, defaults, step IDs, gates, routes, limits, roles and model/effort settings. Bind the existing `integration` input on all 109 prompt nodes that lacked the field at audit; do not change workflow structure, control flow or controller policy.
- Keep existing `catalog:install`, `catalog:refresh`, `catalog:remove`, `catalog:agents` and native Specify interfaces; update their owned name/path constants, not their behavior.
- Keep independent `flow-roadmap`, `flow-wiki` and core Spec Kit command identities unchanged. Rename both owned feedback extensions and their existing capture/report/intake command and skill identities using the naming contract. Change `flow_kit` to `farmboy` across owned workflow metadata, controller parsing, structural validation, renderer parsing, docs and tests; preserve nested delegation semantics and reject reliance on the old key. This project owns these readers; no external-project parser change is assumed or authorized.
- Update current usage/install docs and existing regression fixtures to the new names. Do not add old-name aliases, legacy readers, migration handling, journals, retry orchestration or consumer-reference discovery.
- Reconcile component versions/pins and regenerate catalog outputs using the existing builder. Preserve T007 as historical evidence, not proof of current composition. T012 verifies the source/package pins and digests after the explicitly approved patch bumps. The reviewed roadmap source is clean at `34483aa212e5cb3302615c0fad043d1eb908edc9`, with runtime identical to cleanup `7eec0b73b49d4d242d491530da5011de62b4d211`; report actual tested coordinates. Do not hand-edit generated archives or claim release/publication.

Existing installations are not upgraded by this feature. The operator handles replacement separately; this plan does not prescribe or implement a consumer migration procedure.

## Validation

Run existing agent/configuration, controller, workflow graph/path, catalog and lifecycle tests after updating their name/path expectations. Check all ten bindings, nine exact roles, standalone renderer and stop-only deprecation. Compare workflow graphs against reviewed Feature 022 correction `7a43bb3` with only reviewed identity/path and delegation-key replacements normalized. Explicitly cover the renamed `milestone_policy.py`, local phase adapter, generic roadmap write/configuration/review helpers, authoring proof, independent readback and retained receipts with `test_phase_lifecycle.py` and the 23-case `test_workflow_roadmap_boundary.py` suite. The roadmap extension no longer supplies the phase helper or its former owner test matrix. Run existing feedback capture/report/intake regressions with renamed paths and command expectations, plus focused parser checks for `farmboy` delegation and absence of old-key fallback. Verify the renamed metadata survives workflow delivery and inspection through the pinned Specify CLI in the disposable consumer.

Validate a fresh disposable initialized consumer with the existing install/refresh/remove path. Check new names resolve, old invocation aliases are absent, and independent components and existing ownership semantics are preserved. Use the existing lifecycle fixtures; do not add a legacy-migration matrix or interruption/retry subsystem tests.

Run documented project environment checks before ordinary Python tests; report missing prerequisites rather than changing an existing environment without authorization. T010–T012 validation uses disposable fixtures, not existing-consumer refresh. Earlier merge validation and the initial prompt-dispatch failure are historical observations, superseded by the approved complete binding batch and current results recorded in quickstart. Record actual source/package versions, digests, CLI, outcomes and any skips; native role availability remains distinct from static configuration checks. No Linux or live installed agent execution is claimed.

## Risks and Non-Goals

An indiscriminate global replacement can alter independent IDs, parser grammar, actual URLs or historical attribution. A reviewed mapping and focused reference scan handle that risk without creating new runtime machinery.

No migration feature, backward compatibility, new framework/dependency or unrelated schema, consumer customization transfer, checkpoint support or unrelated management behavior change is included. The future code factory, external repository rename, publication and Git integration remain separate. Task drafting and independent task-quality review were completed through the separately invoked Tasks workflow. Previous migration-design reviews remain historical and stale for this cutover design; current analysis is not a fresh standalone Plan review or implementation authorization.

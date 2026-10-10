# Implementation Plan: FarmBoy Project and Workflow Naming

**Branch**: `farmboy` | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

This revised plan describes a pure naming cutover. The operator explicitly removed consumer migration from scope. Earlier migration-oriented planning and review are superseded. The subsequent explicit Tasks invocation authorized task drafting and included independent task-quality review; it does not establish a fresh standalone Plan review of this design. Current analysis/remediation reconciles the mutable artifacts.

## Table of Contents

- [Approach](#approach)
- [Constitution Check](#constitution-check)
- [Source Layout After Authorized Implementation](#source-layout-after-authorized-implementation)
- [Implementation Boundaries](#implementation-boundaries)
- [Validation](#validation)
- [Risks and Non-Goals](#risks-and-non-goals)

## Approach

Perform coordinated name/path substitutions in reviewed source, update references and existing test expectations, and rebuild packages through the existing catalog builder. No new runtime feature, command capability, flag, persistent record or compatibility layer is added.

Use [contracts/naming.md](contracts/naming.md) for the exact ten workflow/skill bindings, nine agent roles, renderer and package mappings. Inspect old-name occurrences with `rg`; replace owned active identities while retaining independent roadmap/wiki IDs, unrelated schema fields, actual source URLs and immutable history. No new stored occurrence-inventory schema is required.

The existing Python/Bash/YAML/JSON/TOML/Markdown architecture, dependency pins and management interfaces remain in place. Research decisions are in [research.md](research.md), existing schema boundaries in [data-model.md](data-model.md), unchanged management behavior in [contracts/consumer-management.md](contracts/consumer-management.md), and validation commands in [quickstart.md](quickstart.md).

## Constitution Check

The operator explicitly approved and applied [Constitution 8.0.0](../../.specify/memory/constitution.md) on 2026-10-10. Principle III now establishes FarmBoy and the approved owned feedback and delegation-key identities. Its bounded transition permits existing reviewed source and installed components to remain operative until separately invoked rename implementation and compatible installation take effect. The identity amendment is satisfied; FR-015 and T001 remain prerequisite verification before implementation.

The earlier planning-only exception authorized research/design under Constitution 7.0.0 and remains historical phase authority. It did not authorize tasks or implementation; the later explicit Tasks invocation separately authorized task drafting. No new exception or constitutional amendment is needed for these bounded artifact corrections.

The pre-research and post-design constitution checks pass for this pure rename under 8.0.0. Principles I, II, IV and V remain unchanged: current mutable artifacts may be reconciled; human authority, manual fallback, reviewed source and bounded evidence remain required. The amendment and this analysis/remediation do not authorize implementation, actual consumer operations, external changes, acceptance or Git integration.

## Source Layout After Authorized Implementation

Rename owned directories without reorganizing responsibilities. These are future paths, not changes made during planning.

```text
bundles/farmboy/                         # bundles/spec-kit-flow/
controllers/farmboy/                     # controllers/flow-kit/
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

The implementation changes identities and references only.

- Rename product/package identifiers and relevant files/directories, retaining existing purposes, inputs, defaults, step IDs, gates, routes, limits, roles and model/effort settings.
- Keep existing `catalog:install`, `catalog:refresh`, `catalog:remove`, `catalog:agents` and native Specify interfaces; update their owned name/path constants, not their behavior.
- Keep independent `flow-roadmap`, `flow-wiki` and core Spec Kit command identities unchanged. Rename both owned feedback extensions and their existing capture/report/intake command and skill identities using the naming contract. Change `flow_kit` to `farmboy` across owned workflow metadata, controller parsing, structural validation, renderer parsing, docs and tests; preserve nested delegation semantics and reject reliance on the old key. This project owns these readers; no external-project parser change is assumed or authorized.
- Update current usage/install docs and existing regression fixtures to the new names. Do not add old-name aliases, legacy readers, migration handling, journals, retry orchestration or consumer-reference discovery.
- Reconcile component versions/pins and regenerate catalog outputs using the existing builder. Canonical source versions and the checked snapshot differ; use current compatible sources and report the actual tested coordinates. Do not hand-edit generated archives or claim release/publication.

Existing installations are not upgraded by this feature. The operator handles replacement separately; this plan does not prescribe or implement a consumer migration procedure.

## Validation

Run existing agent/configuration, controller, workflow graph/path, catalog and lifecycle tests after updating their name/path expectations. Check all ten bindings, nine exact roles, standalone renderer and stop-only deprecation. Compare workflow graphs with only reviewed identity/path and delegation-key replacements normalized. Run existing feedback capture/report/intake regressions with renamed paths and command expectations, plus focused parser checks for `farmboy` delegation and absence of old-key fallback. Verify the renamed metadata survives workflow delivery and inspection through the pinned Specify CLI in the disposable consumer.

Validate a fresh disposable initialized consumer with the existing install/refresh/remove path. Check new names resolve, old invocation aliases are absent, and independent components and existing ownership semantics are preserved. Use the existing lifecycle fixtures; do not add a legacy-migration matrix or interruption/retry subsystem tests.

Run documented project environment checks before ordinary Python tests; report missing prerequisites rather than changing an existing environment without authorization. Validation-guide commands are future implementation checks, not claims that the rename already works. Record source/package versions, digests, CLI, outcomes and any skips; native role availability remains distinct from static configuration checks.

## Risks and Non-Goals

An indiscriminate global replacement can alter independent IDs, parser grammar, actual URLs or historical attribution. A reviewed mapping and focused reference scan handle that risk without creating new runtime machinery.

No migration feature, backward compatibility, new framework/dependency or unrelated schema, consumer customization transfer, checkpoint support or management behavior change is included. The future code factory, external repository rename, publication and Git integration remain separate. Task drafting and independent task-quality review were completed through the separately invoked Tasks workflow. Previous migration-design reviews remain historical and stale for this pure-cutover design; current analysis is not a fresh standalone Plan review or implementation authorization.

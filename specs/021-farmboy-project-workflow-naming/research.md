# Research: FarmBoy Pure Rename Cutover

The operator's 2026-10-10 instruction supersedes the earlier automated migration proposal. This research records the narrower technical decisions; no implementation or consumer operation has run.

## Naming and Ownership

**Decision**: Apply one-to-one identity/path replacements using [the naming contract](contracts/naming.md). Preserve purpose and architecture.

**Evidence**: `controllers/flow-kit/manifest.yml` contains ten controller bindings; `agents/flow-kit/manifest.yml` contains nine roles; `skills/flowkit-render-workflow/` is distributed separately. Workflows and package roots are independently reviewed source.

**Rationale**: This is the requested rename, not a new tool. Exact mappings prevent broken references; a global substring replacement could modify independent IDs or historical meaning.

**Alternative rejected**: Blanket replacement across all history, external source coordinates and independent extension names.

## Existing Management Behavior

**Decision**: Retain the current catalog install/refresh/remove/agent interfaces and ownership mechanisms, changing only applicable identity/path values. Existing installations receive no cross-identity upgrade support.

**Evidence**: `tools/catalog.py` and `mise.toml` already define those interfaces; current tests cover their normal ownership and lifecycle behavior.

**Rationale**: No new management command or state machine is needed for a pure cutover.

**Superseded alternative**: The earlier proposed migration command, check/JSON interfaces, observation journal, legacy readers, retry orchestration and migration test matrix are removed from the design by direct operator decision. They are not deferred implementation tasks within this feature.

## Owned Feedback and Delegation Key

**Decision**: Rename owned `flow-feedback` and `speckit-flow-feedback-maintainer` extensions, their capture/report/intake command identities and generated skills. Rename the delegation container `flow_kit` to `farmboy` in this project's producers and readers, preserving `delegated` and `agent` semantics without an old-key adapter. Retain independent `flow-roadmap`, `flow-wiki`, core commands, unrelated fields, actual source URLs, merged specs and completed evidence.

**Evidence**: `tools/catalog.py` resolves roadmap/wiki sources separately but packages feedback from `extensions/flow-feedback/`. The maintainer extension is also source-owned under `extensions/speckit-flow-feedback-maintainer/`. `controllers/flow-kit/scripts/python/controller.py` and `tools/validate_workflows.py` read `flow_kit`; owned workflow definitions produce it. Inspection found no `flow_kit` reference in the available Spec Kit source/templates, so a required external parser change is not established. Validate actual metadata round-trip against the pinned CLI during implementation.

**Rationale**: The operator explicitly includes these source-owned identities in the cutover. Coordinated producer/reader replacement changes spelling without adding capability, compatibility or migration behavior. The prior decision to retain feedback/key names is superseded; ownership alone was never evidence of an external requirement.

## Packaging and Validation

**Decision**: Use the existing builder, coherent current manifests/pins and existing tests. Add only focused naming checks if existing coverage misses a changed reference.

**Evidence**: Canonical manifests record bundle 0.17.0, controllers 0.8.0 and agents 0.2.0; `catalog/release.json` is an older snapshot. Existing catalog, snapshot, agent and graph/path tests supply validation mechanisms.

**Rationale**: Name changes require coherent regenerated metadata/digests, but do not require a migration framework, new dependency or a new release mechanism. Actual implementation versions remain packaging decisions, with no publication claim.

## Governance Boundary

The operator explicitly approved and applied Constitution 8.0.0 on 2026-10-10. Principle III now establishes the approved FarmBoy, owned feedback and delegation-key identities; the separate identity amendment is satisfied and must be verified before implementation. Its bounded transition preserves operative existing source and installations until separately invoked implementation and compatible installation take effect. The earlier planning-only exception under Constitution 7.0.0 remains historical authority for research/design; the later explicit Tasks invocation separately authorized task drafting and included independent task-quality review. Neither that evidence nor current analysis establishes a fresh standalone Plan review. This document, the amendment and analysis/remediation grant no implementation or consumer-operation authority. Source research and design checks are not implementation, migration or live-agent evidence.

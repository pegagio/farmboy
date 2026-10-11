# Research: FarmBoy Pure Rename Cutover

The operator's 2026-10-10 instruction supersedes the earlier automated migration proposal. This research records the narrower technical decisions and reconciles their evidence on 2026-10-10. Partial rename implementation was preserved at checkpoint `87227a1` (T001–T009 complete); reviewed Feature 022 correction `7a43bb3` was integrated by merge `6738a06`. T010–T012 remain open and implementation is paused. This invocation edits artifacts only, with no consumer refresh or implementation.

## Naming and Ownership

**Decision**: Apply one-to-one identity/path replacements using [the naming contract](contracts/naming.md). Preserve purpose and architecture.

**Evidence**: Current `controllers/farmboy/manifest.yml` contains ten controller bindings; `agents/farmboy/manifest.yml` contains nine roles; `skills/farmboy-render-workflow/` is distributed separately. Their earlier FlowKit paths describe the pre-cutover naming evidence, not current source paths. Workflows and package roots remain independently reviewed source.

**Rationale**: This is the requested rename, not a new tool. Exact mappings prevent broken references; a global substring replacement could modify independent IDs or historical meaning.

**Alternative rejected**: Blanket replacement across all history, external source coordinates and independent extension names.

## Existing Management Behavior

**Decision**: Retain the current catalog install/refresh/remove/agent interfaces and ownership mechanisms, changing only applicable identity/path values. Existing installations receive no cross-identity upgrade support.

**Evidence**: `tools/catalog.py` and `mise.toml` already define those interfaces; current tests cover their normal ownership and lifecycle behavior.

**Rationale**: No new management command or state machine is needed for a pure cutover.

**Superseded alternative**: The earlier proposed migration command, check/JSON interfaces, observation journal, legacy readers, retry orchestration and migration test matrix are removed from the design by direct operator decision. They are not deferred implementation tasks within this feature.

## Owned Feedback and Delegation Key

**Decision**: Rename owned `flow-feedback` and `speckit-flow-feedback-maintainer` extensions, their capture/report/intake command identities and generated skills. Rename the delegation container `flow_kit` to `farmboy` in this project's producers and readers, preserving `delegated` and `agent` semantics without an old-key adapter. Retain independent `flow-roadmap`, `flow-wiki`, core commands, unrelated fields, actual source URLs, merged specs and completed evidence.

**Evidence**: Current `tools/catalog.py` resolves roadmap/wiki sources separately and packages `extensions/farmboy-feedback/`; maintainer intake remains owned under `extensions/farmboy-feedback-maintainer/`. Current controller/validator/workflow surfaces use `farmboy`. The old source paths and key were the historical ownership evidence for the approved replacements. Earlier inspection found no `flow_kit` reference in the available Spec Kit source/templates; that observation did not prove runtime compatibility. Actual metadata round-trip remains a separately authorized pinned-CLI validation check.

**Rationale**: The operator explicitly includes these source-owned identities in the cutover. Coordinated producer/reader replacement changes spelling without adding capability, compatibility or migration behavior. The prior decision to retain feedback/key names is superseded; ownership alone was never evidence of an external requirement.

## Packaging and Validation

**Decision**: Use the existing builder, coherent current manifests/pins and existing tests. Add only focused naming checks if existing coverage misses a changed reference.

**Evidence**: Current source manifests record bundle 0.18.0, controllers 0.9.0, agents 0.2.0, Specify 0.4.0, Implement/Close Out 0.9.0 and independent roadmap 0.4.0. Checked `catalog/release.json` still records controllers 0.8.0, roadmap 0.3.0, Specify 0.3.0 and Implement/Close Out 0.8.0 from historical T007 packaging with dirty roadmap provenance. T007 remains complete as that checkpoint; it does not prove current source/package coherence. Merge validation built temporary snapshots without regenerating checked catalog outputs. Final builder regeneration and package/source verification belong to remaining T011/T012 after separate authorization. The compatible roadmap source is clean at `34483aa212e5cb3302615c0fad043d1eb908edc9`, with runtime identical to reviewed cleanup `7eec0b73b49d4d242d491530da5011de62b4d211`.

**Rationale**: Name changes require coherent regenerated metadata/digests, but do not require a migration framework, new dependency or a new release mechanism. Actual implementation versions remain packaging decisions, with no publication claim.


## Corrected Behavioral Baseline

**Decision**: Preserve the separately reviewed Feature 022 correction, not the superseded coupled lifecycle design. Use [Feature 022](../022-workflow-owned-roadmap-boundary/spec.md), its [review](../022-workflow-owned-roadmap-boundary/review.md) and [boundary merge validation](validation/boundary-merge.md) as attributable baseline evidence.

**Evidence**: `controllers/farmboy/scripts/python/milestone_policy.py` and the local phase adapter own milestone evaluation, authoring proof, generic amendments, independent readback and receipts. Generic roadmap 0.4.0 supplies configuration, write and review interfaces without its former `phase_lifecycle.py` or phase test matrix. Local `test_phase_lifecycle.py` and the 23-case `test_workflow_roadmap_boundary.py` suite cover the boundary; the latter can validate a delivered generic configuration loader with `FARMBOY_TEST_ROADMAP_SOURCE`.

**Rationale**: Feature 022 already delivered the ownership correction. Feature 021 applies approved identity/path/key substitutions to that behavior without redesigning it. Comparing against `b6dcae9` or `87227a1` would attribute the correction to the rename incorrectly.

**Validation limits**: The merge record reports 356 source tests with one optional prerequisite skip, feedback suites of five/eight tests, snapshot and native delivery checks, and a synthetic installed joint check with actual generic writes/readback in disposable consumers. The enabled bundle lifecycle suite retains one unresolved `integration None` prompt-dispatch failure. No Linux or live installed phase-workflow result is established. These observations were not rerun by artifact reconciliation.

## Governance Boundary

The operator explicitly approved and applied Constitution 8.0.0 on 2026-10-10. Principle III now establishes the approved FarmBoy, owned feedback and delegation-key identities; the separate identity amendment is satisfied and must be verified before implementation. Its bounded transition preserves operative existing source and installations until separately invoked implementation and compatible installation take effect. The earlier planning-only exception under Constitution 7.0.0 remains historical authority for research/design; the later explicit Tasks invocation separately authorized task drafting and included independent task-quality review. Neither that evidence nor current analysis establishes a fresh standalone Plan review. This document, the amendment and analysis/remediation grant no implementation or consumer-operation authority. Source research and design checks are not implementation, migration or live-agent evidence.

---
title: Bundle model before FarmBoy
type: concept
sources:
- S001
- S002
- S016
- S017
- S018
- S019
- S021
- S027
- S032
updated: 2026-10-14
---

# Bundle model before FarmBoy

## Earlier source contracts

These records retain earlier intent; accepted Feature 014 refinements below govern revised workflows. (S021)

The `spec-kit-flow` repository and bundle own generic workflow and feedback source. A bundle composes versioned components; each workflow remains an independently reviewable source package, and extensions retain their reviewed manifest IDs. (S001, S002)

The previously ingested S002 snapshot recorded source bundle `0.5.0` and local catalog `0.4.1`: Codex, Specify `>=1.0.10.dev0`, Python 3, and pins `flow-roadmap` `0.2.1`, `flow-wiki` `2.0.1`, consumer `flow-feedback` `0.2.1`. Roadmap and wiki have separate repositories. (S002)

The bundle includes eight workflows: `speckit-flow-start-feature`, `speckit-flow-clarify`, `speckit-flow-plan`, `speckit-flow-tasks`, `speckit-flow-analyze-remediate`, `speckit-flow-implement`, `speckit-flow-converge`, and `speckit-flow-closeout`. It does not include a preset or the maintainer feedback intake component. (S001, S002)

The local FlowKit catalog release adds eight direct Codex controller skills alongside the Specify bundle. Native bundle commands manage the declared workflows and extensions, while FlowKit catalog install, refresh, and removal manage the direct skills as a separate owned package. (S002)

Generic source has no Diagram executable, database, registration command, canonical-state mutation, or runtime service dependency. (S001)

The manifest pins compatible versions; the catalog records source commits, required tags, archive SHA-256 and workflow digests, and release status. Codex is initially supported. (S016)

The amended constitution permits Codex controllers to dispatch bounded step subagents, but requires them to follow the installed, versioned workflow definition instead of copying its prompts, gates, or decision rules into a skill. Every workflow keeps a manual-prompt path when native dispatch is unavailable. (S017)

Verified Feature 013 defines direct `flow-kit-*` Codex controller skills installed through the FlowKit catalog route alongside the Specify bundle. Its roadmap records bounded consumer validation, without claiming publication or broader compatibility. (S018)

Verified Feature 015 replaces concrete step-model declarations in updated workflow source with explicit delegation and reviewed native agent names. (S018)

Feature 013 assigns direct skills to FlowKit catalog management; native Specify commands manage declared bundle components. (S019)

## Current README boundary

The old README pins and eight-workflow descriptions above preserve the previously ingested snapshot, not the refreshed README. Current README identifies FarmBoy bundle `0.18.3`, ten active workflows, and independent roadmap/wiki extensions; it excludes presets and maintainer intake and calls the catalog unreleased. See the [current composition](./bundle-and-workflow-model.md). (S002)

## Related page

[Current account](./bundle-and-workflow-model.md). Historical contracts remain provenance; Feature 021 establishes the naming cutover. (S032)

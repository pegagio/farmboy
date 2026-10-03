---
title: Bundle and workflow model
type: concept
sources:
- S001
- S002
- S016
- S017
- S018
- S019
- S021
updated: '2026-10-03'
---

# Bundle and workflow model

## Earlier source contracts

The following records retain earlier source intent; the accepted Feature 014 refinements below govern the revised workflow design. (S021)

The `spec-kit-flow` repository and bundle own generic workflow and feedback source. A bundle composes versioned components; each workflow remains an independently reviewable source package, and extensions retain their reviewed manifest IDs. (S001, S002)

The current source bundle is version `0.5.0`, while the checked-in local catalog remains the earlier `0.4.1` release. The bundle targets Codex, requires Specify `>=1.0.10.dev0` and Python 3, and pins `flow-roadmap` `0.2.1`, `flow-wiki` `2.0.1`, and the consumer `flow-feedback` extension `0.2.1`; roadmap and wiki are maintained in separate repositories. (S002)

The bundle includes eight workflows: `speckit-flow-start-feature`, `speckit-flow-clarify`, `speckit-flow-plan`, `speckit-flow-tasks`, `speckit-flow-analyze-remediate`, `speckit-flow-implement`, `speckit-flow-converge`, and `speckit-flow-closeout`. It does not include a preset or the maintainer feedback intake component. (S001, S002)

The local FlowKit catalog release adds eight direct Codex controller skills alongside the Specify bundle. Native bundle commands manage the declared workflows and extensions, while FlowKit catalog install, refresh, and removal manage the direct skills as a separate owned package. (S002)

Generic source has no Diagram executable, database, registration command, canonical-state mutation, or runtime service dependency. (S001)

The bundle manifest pins compatible component versions; the local release catalog binds packages to source commits, required release tags, archive SHA-256 digests, workflow source digests, and release status. Codex is the initial integration. (S016)

The amended constitution permits Codex controllers to dispatch bounded step subagents, but requires them to follow the installed, versioned workflow definition instead of copying its prompts, gates, or decision rules into a skill. Every workflow keeps a manual-prompt path when native dispatch is unavailable. (S017)

Verified Feature 013 defines direct `flow-kit-*` Codex controller skills installed through the FlowKit catalog route alongside the Specify bundle. Its roadmap records bounded consumer validation, without claiming publication or broader compatibility. (S018)

Verified Feature 015 replaces concrete step-model declarations in updated workflow source with explicit delegation and reviewed native agent names. (S018)

Feature 013 assigns direct skills to FlowKit catalog management; native Specify commands manage declared bundle components. (S019)

## Feature 014 approved scope

Feature 014's approved scope expands the reviewed design to ten active workflows and retains Start Feature as a stop-only deprecated definition excluded from active bundle and controller delivery. Select Feature and Specify replace the combined phase; Wiki Lint Update is separately invoked. The scope also includes a project-owned rendering skill and source-faithful diagrams. These roadmap requirements do not establish release or consumer adoption. (S018)

**Accepted supersession**: S001/S002's earlier eight-workflow bundle description includes active Start Feature; the amended S018 scope replaces that phase and requires ten active workflows. The earlier description remains historical source evidence; the F014 design is the prospective refinement. (S001, S002, S018, S021)

## Feature 014 workflow design

The specification names ten active workflows: Select Feature, Specify, Clarify, Plan, Tasks, Analyze and Remediate, Implement, Converge, Close Out, and Wiki Lint Update. Deprecated Start Feature reports deprecation without work and is excluded from active bindings. Independent source review and manual paths remain required. This specification describes intended behavior and validation requirements, not publication or acceptance. (S021)

## Roadmap dispositions

Features 001–015 are verified; 016 and 017 remain planned. Feature 018’s [capacity proposal](./workflow-agent-capacity-proposal.md) is abandoned, leaving its observation unresolved. Roadmap verification does not establish publication or consumer adoption. (S018)

## Related pages

- [Codex workflow controller design](./codex-workflow-controllers.md)
- [Project authority and review gates](./project-authority-and-review-gates.md)
- [Workflow lifecycle](./workflow-lifecycle.md)
- [Installation and release lifecycle](./installation-and-release-lifecycle.md)
- [Diagram adapter boundary](./diagram-adapter-boundary.md)

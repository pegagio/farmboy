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
- S027
- S032
- S035
- S003
updated: 2026-10-14
---

# Bundle and workflow model

## FarmBoy cutover (2026-10-10)

Feature 021 establishes **FarmBoy**, tagline **Spec et Labora**, and project/bundle ID `farmboy`. The ten skill/workflow IDs are `farmboy-select-feature`, `farmboy-specify`, `farmboy-clarify`, `farmboy-plan`, `farmboy-tasks`, `farmboy-analyze-remediate`, `farmboy-implement`, `farmboy-converge`, `farmboy-closeout` and `farmboy-wiki-lint-update`. Old invocation names have no aliases. Deprecated `farmboy-start-feature` stays stop-only and excluded; `farmboy-render-workflow` remains independently distributed. (S032)

Core Spec Kit commands and independent `flow-roadmap`/`flow-wiki` identities stay unchanged. Existing purposes, responsibilities and decision boundaries are preserved against the reviewed, merged Feature 022 correction. [Earlier bundle contracts](./bundle-model-before-farmboy.md) retain historical names and pins rather than current registrations. (S032)

## Qualified cutover verification

The roadmap records Feature 021's verified FarmBoy rename under Constitution 8.0.0, supported by an attributable implementation debrief and automated/native-fixture validation. That qualification is bounded: the snapshot remains unpublished, newly packaged FarmBoy live-agent behavior and Linux remain untested, and no consumer refresh, feature acceptance or Git integration follows from verification. Existing installations are handled separately; independent roadmap/wiki ownership and core command identities remain unchanged. Present-state ledger corrections do not reconstruct historical phase-owner effects or grant acceptance or publication. (S035)

## Feature 014 approved scope

Feature 014's approved scope expands the reviewed design to ten active workflows and retains Start Feature as a stop-only deprecated definition excluded from active bundle and controller delivery. Select Feature and Specify replace the combined phase; Wiki Lint Update is separately invoked. The scope also includes a project-owned rendering skill and source-faithful diagrams. These roadmap requirements do not establish release or consumer adoption. (S018)

**Accepted supersession**: S001/S002's earlier eight-workflow bundle description includes active Start Feature; the amended S018 scope replaces that phase and requires ten active workflows. The earlier description remains historical source evidence; the F014 design is the prospective refinement. (S001, S002, S018, S021)

## Feature 014 workflow design

The ten active workflows are Select Feature, Specify, Clarify, Plan, Tasks, Analyze and Remediate, Implement, Converge, Close Out, and Wiki Lint Update. Deprecated Start Feature performs no work and has no active binding. Independent review and manual paths remain required; the specification establishes intent and validation requirements, not publication or acceptance. (S021)

## Roadmap dispositions

Features 001–015 are verified; 016 is planned, 017 retains qualified verification, and 018's [capacity proposal](./workflow-agent-capacity-proposal.md) is abandoned. Verified 019 selects a project `.venv`, existing mise/uv, pinned PyYAML and explicit invocation; no extra utilities. Its [portable guide](./agent-python-environment.md) preserves existing settings. macOS arm64 evidence establishes no full catalog repair, stock Specify compatibility, real adoption, acceptance, publication or Git authority. DEP017-01 history remains qualified. (S018)

Feature 020’s [qualified verification and manual waiver](./feature020-verification-qualification.md) preserves unobserved manual equivalence and separate acceptance/release authority. (S018)

## Current README composition

The current README pins bundle `0.18.3`, controller package `0.9.1`, and `farmboy-agents` `0.2.0` for Codex, requiring Specify `>=1.0.10.dev0` and Python 3. Extension pins are `flow-roadmap` `0.4.0`, `flow-wiki` `2.0.1`, and `farmboy-feedback` `0.2.1`; no preset or maintainer intake is bundled. (S002)

The ten-workflow table pins Select Feature `0.2.1`, Specify `0.4.1`, Clarify/Plan/Tasks `0.5.1`, Analyze `0.6.1`, Implement `0.9.1`, Converge `0.5.1`, Close Out `0.9.2`, and Wiki Lint Update `0.2.1`. Manual prompts remain available; selection and specification require separate invocations. This is an unreleased development snapshot, not publication or consumer adoption. (S002)

Feature 022 adds [local timing and maintainer workbook reporting](./local-agent-timing-metrics.md) as prospective scope, preserving consumer boundaries. (S018)

[Metrics component boundaries](./local-metrics-component-boundary.md) separate collection and reporting. (S003)

## Related pages

- [Agent Python environment](./agent-python-environment.md)

- [Codex workflow controller design](./codex-workflow-controllers.md)
- [Project authority and review gates](./project-authority-and-review-gates.md)
- [Workflow lifecycle](./workflow-lifecycle.md)
- [Installation and release lifecycle](./installation-and-release-lifecycle.md)
- [Diagram adapter boundary](./diagram-adapter-boundary.md)

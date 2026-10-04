# Implementation Plan: FlowKit Agent Configuration and Consumer Delivery

**Branch**: `017-flowkit-agent-configuration` | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

**Input**: Approved scope and clarification decisions in `specs/017-flowkit-agent-configuration/spec.md`.

## Summary

Deliver the eight reviewed roles as exact `FlowKit-` identities, with explicit model and reasoning settings in native Codex TOML files. Keep authoritative generic defaults in a separately versioned source package, compose it through the existing catalog, and copy configurations into consumers without acquiring ownership of those copies. Bundle installation adds missing defaults; ordinary refresh replaces only the available-default package; targeted reset explicitly discards selected customizations. Copied agents and obsolete definitions survive bundle removal. Existing skill ownership behavior remains separate.

The operator approved all eight exact model/effort choices in [research.md](research.md#approved-model-and-effort-decisions): `gpt-6.1-sol` / `low` for Roadmap Agent and Wiki Curator; `gpt-6.1-sol` / `medium` for Code Reviewer; `gpt-6.1-sol` / `high` for Specifier, Planner and Reviewer; `gpt-6-luna` / `high` for Coder and Tasker. No further settings decision is pending. Support validation and independent planning review remain required. No implementation, task generation, acceptance, publication or lifecycle reset is authorized by these artifacts.

## Table of Contents

- [Technical Context](#technical-context)
- [Constitution Check](#constitution-check)
- [Project Structure](#project-structure)
- [Design and Delivery](#design-and-delivery)
- [Validation Strategy](#validation-strategy)
- [Risks and Implementation Prerequisites](#risks-and-implementation-prerequisites)
- [Author Self-Check](#author-self-check)

## Technical Context

The design extends current packaging and file-copy tooling rather than adding a framework or runtime.

**Language/Version**: Python 3.11.16; native TOML agent files; YAML workflow/package metadata; Markdown guidance.

**Primary Dependencies**: Existing Python standard library, PyYAML and Specify CLI integration; no new dependencies. Source pins Specify `1.0.10.dev0+pegagio.2` in `mise.toml`.

**Storage**: Versioned source defaults and catalog ZIP; installed available-default archive plus package metadata under `.specify/flow-kit/agent-defaults/`; consumer copies under `.codex/agents/`. No consumer-agent ownership ledger, content-hash tracking, or customization database.

**Testing**: Existing unittest suite (`tests/test_agent_configs.py`, `test_catalog.py`, `test_bundle_lifecycle.py`, `test_controller.py`, workflow graph/path tests), `tools/validate_workflows.py`, disposable initialized consumers, and separately attributable live named-agent evidence.

**Target Platform**: Codex project-local custom agents in trusted local consumers. CLI `0.157.1` and Specify version above were observed during planning; native desktop client compatibility and effective child settings require implementation-time evidence. Documentation alone is not version-specific client execution proof.

**Project Type**: Reusable workflow/package catalog with consumer-facing CLI lifecycle operations.

**Performance Goals**: Bounded file operations over the selected package's eight entries; no background service, inference call, transcript capture, or repository-wide custom-file scan for lifecycle operations. No invented latency SLA.

**Constraints**: Exact named dispatch, existing consequential gates, independent review, portable provenance, manual fallback, preserved consumer files, and no authority drift. All exact pairs are operator-approved; supported-client validation precedes applying settings to source configs.

**Scale/Scope**: Eight roles, ten active workflows and all nested delegated branches; deprecated Start Feature stays stop-only. Feature 016 probe changes and Feature 018 capacity behavior remain outside this feature.

## Constitution Check

Initial and post-design checks use Constitution 6.0.0. No exception is requested.

| Principle | Initial gate | Post-design result |
|---|---|---|
| I: merge-bounded flow-back | Spec decisions are authority; verified history stays intact | Pass: design affects prospective source and current docs; no historical semantic rewrite or upstream mutation |
| II: human direction | Named roles, questions, independent review and explicit consequential approval remain | Pass: all settings received explicit operator approval; no fallback, workflow chaining, roadmap/Git acceptance |
| III: component boundaries | Bundle composes source rather than duplicating behavior | Pass: separately versioned `flow-kit-agents` source package; The Diagram has no runtime role |
| IV: reviewed source/manual fallback | Reviewed source only; no new framework | Pass: native TOML and existing catalog; copies editable by consumer; existing manual prompt path retained |
| V: evidence | Disposable consumer results need coordinates, versions and digests | Pass by design: evidence contract separates config support, live dispatch and effective settings; execution remains required |

## Project Structure

The documentation output and prospective implementation surfaces are distinct.

### Documentation for this feature

Planning creates these artifacts only:

```text
specs/017-flowkit-agent-configuration/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── agent-package.md
│   └── agent-delivery-cli.md
└── checklists/
    ├── requirements.md
    └── planning.md
```

### Prospective source changes

These paths describe implementation boundaries; they are not created by planning.

```text
agents/flow-kit/manifest.yml                 # new reviewed package inventory/version
agents/flow-kit/agents/flowkit-*.toml         # eight canonical generic defaults
.codex/agents/flowkit-*.toml                 # source checkout's native role configs
workflows/speckit-flow-*/workflow.yml         # exact assignment migration only
controllers/flow-kit/                       # current discovery/guidance expectations only
catalog/release.json and catalog/packages/  # generated by existing catalog build
bundles/spec-kit-flow/bundle.yml            # package pin alongside existing components
tools/catalog.py                           # package/lifecycle implementation
mise.toml                                  # catalog agent operation entry point
tests/                                    # existing suites plus focused lifecycle cases
docs/installation.md                       # acquisition, update, reset and migration
```

**Structure decision**: Source default files in `agents/flow-kit/` own reusable behavior. Local `.codex/agents/` files are the source checkout's consumer-facing copies and must match approved defaults for maintainer validation; build packages only canonical source files. Avoid symlinks and independently maintained duplicate instructions. Existing skill/controller sources retain their authority.

## Design and Delivery

The contracts define exact inventory, CLI payloads and dispositions. A new package is necessary because generic agent defaults now have a reviewed lifecycle and provenance independent of controller skills; reusing the skill ownership ledger would contradict consumer ownership.

### Identity and instruction review

Migrate every active delegated assignment by exact one-to-one role identity, including nested switch/loop branches. Keep delegation booleans, step IDs, graph transitions and human gates unchanged. Update current validators, fixture expectations, discovery/manual guidance, installation docs and role references; preserve intentional historical quotations. Rename source-checkout files to canonical `flowkit-*.toml` names after reconciling existing local definitions. Never delete or rename consumer files automatically.

Each role's instruction record in research specifies scope, outputs, prohibitions and escalation. Refine wording to route structured questions/blockers through the main controller while preserving same-child continuation, command-required self-checks and separate review. Do not embed model choices in workflows or controller maps; `model` and `model_reasoning_effort` belong only in the native role configuration.

### Package composition and available defaults

Build deterministic `flow-kit-agents-<version>.zip` from the canonical manifest and eight reviewed files. Include package-level digest, version, source commit, source digest and released/snapshot status in catalog metadata. Artifact integrity hashes are permitted; they never track consumer-copy content. The initial package uses `0.1.0`; the prefix is a breaking dispatch change requiring coordinated version bumps for affected workflows/controllers and bundle. Select exact resulting versions during implementation against then-current source; never rewrite published artifacts in place.

Install/refresh validates package, inventory and paths before replacing the available-default cache. Bundle install invokes install-missing after successful component/default installation. Ordinary refresh updates the cache only; newly added agent definitions are acquired through explicit install-missing. Removal removes available package metadata/cache through the catalog path while preserving every `.codex/agents/` copy. Copied provenance remains inspectable through retained version-control history and portable operation reports; no permanent per-copy tracking is needed.

### Consumer customization and recovery

Users can edit native files directly. Install-missing skips any existing destination; skips are preservation evidence, not evidence of equivalence to defaults. Reset-one/all supplies overwrite authority only for manifest-listed current targets. Unknown names, ambiguous inventories, unsafe paths and invalid package data fail before any mutation. Existing unprefixed, retired and unrelated definitions remain untouched. A duplicate exact name elsewhere blocks a claim of usable dispatch and requires operator resolution.

Use per-file atomic replacement and preflight the entire chosen target set. A filesystem failure can produce partial completion; report written/skipped/failed/not-attempted targets explicitly. Do not add an ownership journal or automatic merge. Re-running install-missing retries absent files; re-running the identical explicit reset finishes targeted defaults after the operator inspects results. Reports warn against invoking migrated workflows until all required names resolve.

## Validation Strategy

Trace each test group to requirements; [quickstart.md](quickstart.md) supplies future runnable scenarios.

| Coverage | Requirements | Evidence |
|---|---|---|
| Exact eight names, fields, instruction reviews | FR-001–007 | TOML parse, approved decision table, native discovery check, unchanged delegation topology |
| Install-missing, refresh, targeted reset, removal | FR-008–011 | Disposable consumer matrix with byte comparisons and per-target outcomes |
| Package integrity and mixed-version migration | FR-002, FR-010, FR-012 | Version/digest verification; malformed inventory, duplicate name, symlink/path escape failures |
| All eight live role outcomes | FR-012–014 | Bounded exact-role invocation, client/account evidence; effective model/effort observed or explicitly unverified |
| Scope and authority preservation | FR-005, FR-007, FR-015–016 | Independent review, full graph validation, no workflow model map/probe redesign/Diagram coupling |

Existing tests that require omitted model fields or the old exact filenames must be intentionally updated. Reconcile active validators without merely loosening them. Broad source validation and disposable bundle lifecycle checks follow focused tests once implementation exists. No-op dispatch is only transport evidence. No tests are claimed run against nonexistent implementation.

## Risks and Implementation Prerequisites

The following conditions remain visible:

- **Approval**: All eight exact model/effort settings received operator approval during planning. Approval accepts the design choices, not effective-setting verification.
- **Client support**: Current documentation and host metadata support the current candidate fields/values; CLI version observation is not parsing, authorization or effective-runtime proof. Implementation must verify each on the tested client and record desktop identity if desktop evidence is used.
- **Migration**: Existing customized consumer definitions can retain old identities or incompatible instruction contracts. Preserve them, report unresolved names and provide explicit manual migration/reset guidance; never silently dispatch an alias.
- **Release drift**: Planning observed HEAD `ced0e9e67e49d1ff757e41e313445d5b504a8f9f`, catalog bundle `0.13.7`/controller `0.5.2`, and source controller `0.5.3`. Use a development snapshot for unreleased source validation and regenerate metadata only in implementation with a stated version/digest change. These numbers are baseline, not release approval.
- **Model economics**: Higher efforts trade latency/tokens for depth. No task-specific benchmark establishes quality/cost yet; review implementation-time evidence before claiming suitability achieved.
- **Future definitions**: Manifest-listed defaults determine current reset scope. Obsolete files survive and release notes identify rename/retirement; package defaults cannot infer authority over all files sharing a prefix.

## Author Self-Check

Plan, research, data model, CLI/package contracts and validation guide are substantive and cross-linked. All FR-001–016 have explicit design or validation coverage; no implementation tasks or new tool dependency were introduced. Pre-plan hook inventory contains no `before_plan` hooks. The optional `after_plan` wiki-ingest hook is reported for operator invocation; it is not executed here. [Planning checklist](checklists/planning.md) records self-checks and the approved model decisions. Independent review must be performed by the separately assigned Reviewer.

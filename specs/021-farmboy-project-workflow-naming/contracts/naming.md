# Contract: Canonical FarmBoy Names

This contract describes the future names approved in Feature 021. It authorizes no implementation or installation. Exact source mappings, ownership classification and referenced behavior are reviewed before packaging; historical/provenance names remain attributable.

## Table of Contents

- [Product and Packages](#product-and-packages)
- [Workflow and Skill Bindings](#workflow-and-skill-bindings)
- [Agent Names](#agent-names)
- [Feedback and Delegation Metadata](#feedback-and-delegation-metadata)
- [Paths and Retained Tokens](#paths-and-retained-tokens)
- [Invocation Contract](#invocation-contract)
- [Inventory Completion](#inventory-completion)

## Product and Packages

Product branding becomes **FarmBoy**, with **Spec et Labora** as the tagline. Logical project and bundle identity is `farmboy`; an actual hosted repository or local checkout rename is separately authorized.

| Current identity | Canonical replacement |
|---|---|
| `spec-kit-flow` bundle | `farmboy` |
| `flow-kit-controllers` package | `farmboy-controllers` |
| `flow-kit-agents` package | `farmboy-agents` |
| `flowkit-render-workflow` skill | `farmboy-render-workflow` |
| Deprecated `speckit-flow-start-feature` source | `farmboy-start-feature`, stop-only and not delivered |
| Deprecated `flow-kit-start-feature` source launcher | `farmboy-start-feature`, stop-only and not delivered |

The renderer remains independently distributed through its existing source mechanism. Product identity does not authorize adding it to controller delivery or registering an eleventh active workflow.

## Workflow and Skill Bindings

The controller skill and workflow share the new identifier; source remains independently reviewable. Display names may retain short existing action wording with FarmBoy branding.

| Current skill | Current workflow | New skill and workflow | Display name |
|---|---|---|---|
| `flow-kit-select-feature` | `speckit-flow-select-feature` | `farmboy-select-feature` | FarmBoy Select Feature |
| `flow-kit-specify` | `speckit-flow-specify` | `farmboy-specify` | FarmBoy Specify |
| `flow-kit-clarify` | `speckit-flow-clarify` | `farmboy-clarify` | FarmBoy Clarify |
| `flow-kit-plan` | `speckit-flow-plan` | `farmboy-plan` | FarmBoy Plan |
| `flow-kit-tasks` | `speckit-flow-tasks` | `farmboy-tasks` | FarmBoy Tasks |
| `flow-kit-analyze-remediate` | `speckit-flow-analyze-remediate` | `farmboy-analyze-remediate` | FarmBoy Analyze |
| `flow-kit-implement` | `speckit-flow-implement` | `farmboy-implement` | FarmBoy Implement |
| `flow-kit-converge` | `speckit-flow-converge` | `farmboy-converge` | FarmBoy Converge |
| `flow-kit-closeout` | `speckit-flow-closeout` | `farmboy-closeout` | FarmBoy Close Out |
| `flow-kit-wiki-lint-update` | `speckit-flow-wiki-lint-update` | `farmboy-wiki-lint-update` | FarmBoy Wiki Lint Update |

Purpose inputs, defaults, step IDs, routes, bounded loops, authority checks and gates remain unchanged. Required role values change only through the exact role mapping below. No spelling simplification such as an `analyze` alias is introduced.

## Agent Names

Each exact name and filename maps one-to-one; responsibilities, current model/effort defaults and consumer editability are preserved.

| Current exact name | New exact name | New TOML filename |
|---|---|---|
| `FlowKit-Roadmap Agent` | `FarmBoy Roadmap Agent` | `farmboy-roadmap-agent.toml` |
| `FlowKit-Specifier` | `FarmBoy Specifier` | `farmboy-specifier.toml` |
| `FlowKit-Planner` | `FarmBoy Planner` | `farmboy-planner.toml` |
| `FlowKit-Tasker` | `FarmBoy Tasker` | `farmboy-tasker.toml` |
| `FlowKit-Reviewer` | `FarmBoy Reviewer` | `farmboy-reviewer.toml` |
| `FlowKit-Coder` | `FarmBoy Coder` | `farmboy-coder.toml` |
| `FlowKit-Code Reviewer` | `FarmBoy Code Reviewer` | `farmboy-code-reviewer.toml` |
| `FlowKit-Wiki Curator` | `FarmBoy Wiki Curator` | `farmboy-wiki-curator.toml` |
| `FlowKit-Readiness Checker` | `FarmBoy Readiness Checker` | `farmboy-readiness-checker.toml` |

Example native definition fragment:

```toml
name = "FarmBoy Planner"
model = "gpt-6.1-sol"
model_reasoning_effort = "high"
```

The native `name`, workflow `farmboy.agent`, role allowlists and structured owner/reviewer identity values must agree. Exact-name unavailability stops before workflow work; no generic fallback or per-run override is added. Existing installations are outside this feature's cutover support; no agent-copy conversion or old-name alias is introduced.

## Feedback and Delegation Metadata

Both feedback extensions are owned here. The existing capabilities remain capture, report and maintainer intake; no new command behavior or journal/report schema is introduced.

| Current identity/path | Canonical replacement |
|---|---|
| `flow-feedback` | `farmboy-feedback` |
| `extensions/flow-feedback/` | `extensions/farmboy-feedback/` |
| `speckit-flow-feedback-maintainer` | `farmboy-feedback-maintainer` |
| `extensions/speckit-flow-feedback-maintainer/` | `extensions/farmboy-feedback-maintainer/` |
| `speckit.flow-feedback.capture` | `speckit.farmboy-feedback.capture` |
| `speckit.flow-feedback.report` | `speckit.farmboy-feedback.report` |
| `speckit.speckit-flow-feedback-maintainer.intake` | `speckit.farmboy-feedback-maintainer.intake` |
| Generated `speckit-flow-feedback-capture` skill | `speckit-farmboy-feedback-capture` |
| Generated `speckit-flow-feedback-report` skill | `speckit-farmboy-feedback-report` |
| Generated `speckit-speckit-flow-feedback-maintainer-intake` skill | `speckit-farmboy-feedback-maintainer-intake` |
| Delegation container `flow_kit` | `farmboy` |

Command files, self-references, manifest IDs/pins, catalog resolution, installation paths and test expectations follow these mappings. Neutral feedback module/function names need no cosmetic replacement; branded code identifiers and constants do. Existing `.specify/workflow-feedback/` data retains its location and meaning.

```yaml
farmboy:
  delegated: true
  agent: FarmBoy Planner
```

Controller/validator/renderer readers and all owned workflow producers use this key with unchanged nested semantics. The old key has no compatibility fallback and cannot authorize named delegation; existing main-task rules still apply to steps without valid delegation metadata. Tests must confirm new-key dispatch and that old-key metadata never launches a child, without adding migration handling.

## Paths and Retained Tokens


Owned source roots map as specified in [plan.md](../plan.md#source-layout-after-authorized-implementation). Managed consumer launchers use `.agents/skills/farmboy-<purpose>/`; helper manifests/scripts/ownership/cache use `.specify/farmboy/`; new controller summaries/history use `.specify/farmboy-controllers/`; new workflows use `.specify/workflows/farmboy-<purpose>/`; defaults create `.codex/agents/farmboy-<role>.toml`.

Retain core Spec Kit commands and independently sourced `flow-roadmap` / `flow-wiki` manifests and their declared commands. Owned feedback identifiers change according to the mappings above. Retain `.specify/workflow-feedback/` journals, completed `.specify/flow-controllers/` evidence, native bundle/extension/workflow registry filenames, merged features and actual source URLs. Owned delegation metadata producers and readers use `farmboy` only; unrelated structured fields retain their meanings. Verify delivery and inspection preserve that key through the pinned CLI instead of assuming external support or changing another project.

Project-owned test environment names `SPEC_KIT_FLOW_TEST_ROADMAP_SOURCE` and `SPEC_KIT_FLOW_TEST_WIKI_SOURCE` map to `FARMBOY_TEST_ROADMAP_SOURCE` and `FARMBOY_TEST_WIKI_SOURCE`; independently named extension source override `FLOW_ROADMAP_SOURCE` stays unchanged. Other current branded environment/configuration names require occurrence-level review rather than guessed prefix replacement.

`.worktreeinclude` current owned launcher/helper/workflow patterns must map to the new roots after separately authorized source implementation. Independent extensions and any consumer-owned entries remain untouched. No new legacy-record reader or compatibility adapter is added. The cutover applies to new source and fresh installations only.

## Invocation Contract

A future supported Codex invocation is `$farmboy-plan feature_context=021`; native inspection is `specify workflow info farmboy-plan`. A thin launcher invokes its installed bootstrap with workflow/skill IDs both `farmboy-plan` and the existing supported input translations. The installed workflow owns execution; a naming change never launches another phase. Manual prompts still run the selected workflow's reviewed commands and gates when native exact-agent dispatch is unavailable.

Fresh supported FarmBoy installations have no active old project-owned skill/workflow registrations. `$flow-kit-plan` and `specify workflow info speckit-flow-plan` cannot dispatch FarmBoy through an alias. Native missing-item diagnostics are acceptable; docs identify `farmboy-plan` as the replacement. Existing consumer launchers and customizations are outside this rename's replacement scope. No consumer discovery, transformation or retirement mechanism is added.

## Inventory Completion

Every active identity has a single mapping and all referenced targets resolve. Every old occurrence in the reviewed current surfaces has a disposition from [data-model.md](../data-model.md#naming-inventory). Independent IDs, history, unrelated grammar and actual coordinates require explicit retention rationales. Unresolved active old references, collisions, unexpected aliases, missing purposes or mismatched exact role names prevent rename completion. Historical names alone are not defects.

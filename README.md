# Spec Kit Flow

Spec Kit Flow is a human-directed, merge-bounded flow-back workbench for Spec-Driven Development. It packages ten active reusable Spec Kit workflows, portable consumer feedback, and a version-pinned bundle that composes independently maintained roadmap and wiki extensions.

This repository owns the generic workflow and feedback source. The repository and bundle ID are `spec-kit-flow`; its workflows use `speckit-flow-<purpose>` IDs, and the consumer feedback extension uses `flow-feedback`. The independent `spec-kit-flow-roadmap` and `spec-kit-flow-wiki` repositories publish the extension IDs `flow-roadmap` and `flow-wiki`.

## Contents

- [What the bundle installs](#what-the-bundle-installs)
- [Installation](#installation)
- [Using the workflows](#using-the-workflows)
- [Feedback and release status](#feedback-and-release-status)

## What the bundle installs

The [bundle source manifest](bundles/spec-kit-flow/bundle.yml) is version `0.14.0` and targets Codex. The controller package is `0.6.0`; the canonical agent package is `flow-kit-agents` `0.1.0`. The checked-in catalog is an unreleased development snapshot. Specify `>=1.0.10.dev0` and Python 3 are required. The bundle pins these extensions:

| Extension ID | Version | Purpose |
| --- | --- | --- |
| `flow-roadmap` | `0.2.1` | Governed roadmap changes and feature reviews; source: `spec-kit-flow-roadmap` |
| `flow-wiki` | `2.0.1` | Cited project context, ingestion, and linting; source: `spec-kit-flow-wiki` |
| `flow-feedback` | `0.2.1` | Local observation capture and portable report export; source: this repository |

It also installs the ten active workflows in [`workflows/`](workflows/README.md):

| Workflow ID | Version | Role |
| --- | --- | --- |
| `speckit-flow-select-feature` | `0.2.0` | List and discuss dependencies, select and activate a feature without authoring a spec |
| `speckit-flow-specify` | `0.2.0` | Author the active specification with cited context, verified linkage, and a roadmap brief |
| `speckit-flow-clarify` | `0.5.0` | Run one bounded clarification session |
| `speckit-flow-plan` | `0.5.0` | Review readiness and create the technical plan |
| `speckit-flow-tasks` | `0.5.0` | Generate implementation tasks separately from planning |
| `speckit-flow-analyze-remediate` | `0.5.0` | Analyze artifact consistency and route bounded remediation |
| `speckit-flow-implement` | `0.5.0` | Implement eligible tasks within the selected agent's scope |
| `speckit-flow-converge` | `0.5.0` | Compare implementation with the feature artifacts and close gaps |
| `speckit-flow-closeout` | `0.7.0` | Review completion, approve roadmap verification, maintain wiki context, and report commit readiness |
| `speckit-flow-wiki-lint-update` | `0.2.0` | Lint first, refresh stale registered sources, and report all unresolved wiki findings |

The bundle does not include a preset or `speckit-flow-feedback-maintainer`. Maintainer intake belongs in this source environment, not a consumer project.

## Installation

The checked-in catalog is the local `0.14.0` development snapshot, including ten controller skills and eight consumer-owned agent defaults. Ordinary installation requires a released catalog matching source; use development-snapshot mode in an initialized source checkout or disposable consumer to test current source. A compatible Specify CLI must be available; `mise.toml` records the tested fork version. Local packaging is not publication or consumer adoption.

To install the checked-in release from a checkout matching that release, run `mise run catalog:install /path/to/my-project` after preparing the checkout. To validate source changes that have not reached the catalog, create and initialize a disposable consumer under the system temporary directory, then use development-snapshot mode:

```sh
git clone https://github.com/pegagio/spec-kit-flow.git
cd spec-kit-flow
mise trust
mise install
SPECIFY_BIN="$(mise which specify)"
CONSUMER_DIR="$(mktemp -d)"
(cd "$CONSUMER_DIR" && "$SPECIFY_BIN" init --here --force --non-interactive --integration codex --integration-options="--skills")
PATH="$(dirname "$SPECIFY_BIN"):$PATH" python3 tools/catalog.py install "$CONSUMER_DIR" --development-snapshot
```

Snapshot mode builds a temporary catalog from current source and verified extension packages, accepts only an already initialized consumer under the system temp directory, records the package as unreleased, and leaves checked-in release metadata unchanged. The tested CLI is `1.0.10.dev0+pegagio.2`; compatibility with stock Spec Kit remains unverified. Inspect installed component IDs and provenance before use.

Development snapshots may be installed into the initialized source checkout or a disposable temporary consumer. The regular catalog task requires a matching released catalog. Codex-managed worktrees use `.worktreeinclude` to copy the existing ignored contributor context.

Consider project governance separately from installation: use the [consumer adoption review](docs/consumer-adoption.md) to inspect and decide whether to adopt the model. Installing FlowKit alone does not change project guidance or confirm adoption.

After pulling a newer reviewed release of this repository, refresh the bundle and its Codex skills with:

```sh
mise run catalog:refresh /path/to/my-project
```

The same task serves the temporary catalogs during refresh and verifies controller ownership before changing installed skills. Ordinary install and refresh reject snapshots. For development, `tools/catalog.py install` and `refresh` accept `--development-snapshot` only for an already initialized disposable consumer under the system temporary directory. Maintainers build release packages from clean checkouts at matching annotated tags with `mise run catalog:build <roadmap-checkout> <wiki-checkout>`. Review `catalog/release.json` and the packages before preparing a release. See [installation and lifecycle details](docs/installation.md) for provenance, removal, and release requirements.

## Using the workflows

Prepare a project constitution, use `speckit.flow-roadmap.write` for an approved roadmap, then use `speckit.flow-wiki.init` and `speckit.flow-wiki.ingest` to establish cited project context. In a project installed through the FlowKit catalog route, invoke one named controller skill from the selected Codex task. The ten active picker names and skill IDs are:

| Codex display name | Skill ID | Required input |
| --- | --- | --- |
| FlowKit Select Feature | `flow-kit-select-feature` | optional `feature_request` |
| FlowKit Specify | `flow-kit-specify` | active `.specify/feature.json` |
| FlowKit Clarify | `flow-kit-clarify` | `feature_context` |
| FlowKit Plan | `flow-kit-plan` | `feature_context` |
| FlowKit Tasks | `flow-kit-tasks` | `feature_context` |
| FlowKit Analyze | `flow-kit-analyze-remediate` | `feature_context` |
| FlowKit Implement | `flow-kit-implement` | `feature_context` |
| FlowKit Converge | `flow-kit-converge` | `feature_context` |
| FlowKit Close Out | `flow-kit-closeout` | `feature_context` |
| FlowKit Wiki Lint Update | `flow-kit-wiki-lint-update` | optional `lint_scope`, `authorized_urls` |

Use the `$skill-id key=value` form. For example, in the selected project's Codex task:

```text
$flow-kit-select-feature
# Separately, after activation:
$flow-kit-specify
```

The remaining workflows use the required `feature_context` input, for example `$flow-kit-tasks feature_context=013`. Each controller checks the compatible Specify runtime and installed workflow before starting. In the updated source workflows, every delegated step names a reviewed Codex custom agent. The controller validates assignments across all branches and probes each distinct native agent before workflow work. Codex loads the consumer-owned agent configuration, including optional model and effort settings; FlowKit has no per-run agent, model, or effort override. Native subagent activity shows a task label containing the agent name, and Codex may show model and effort in the child pane. The task keeps questions and gates in the main chat, sends answers back to the same child, and shows results and workspace diffs. The checked-in `0.4.1` release retains the earlier concrete-model behavior; use a matching release checkout for that version.

A typical operator-directed route is:

```text
select-feature → specify → clarify (as needed) → plan → tasks → analyze-remediate
              → implement → converge → closeout
```

The native CLI path remains available. Inspect an installed workflow and supply its required context when running it. For example:

```sh
specify workflow info speckit-flow-select-feature
specify workflow info speckit-flow-specify
specify workflow run speckit-flow-select-feature
```

The workflows preserve a manual-prompt fallback. Clarification may need another session after the current command's five-question cap. Analyze after task generation or consequential artifact reconciliation before implementation; converge after implementation until gaps are resolved. Planning and task generation remain separate. The closeout workflow requires a separately approved feature-completion operation and does not create one. The native `specify workflow run` path does not apply FlowKit's `reasoning_effort` values and does not provide the controller's child-chat experience.

Human review controls roadmap patches, material scope and authority changes, ambiguous recovery, Git integration, and acceptance. A completed controller never launches a later phase or implies that a feature was merged or accepted. See the [workflow command map](workflows/README.md) and [project constitution](.specify/memory/constitution.md) for the governing contracts.

## Feedback and release status

Consumers may use `flow-feedback` to capture local observations and export a portable report. Its commands are `speckit.flow-feedback.capture` and `speckit.flow-feedback.report`. Capture and export do not change workflow source or project authority; maintainer intake is a separate step. See [feedback guidance](docs/feedback.md).

The [release metadata](catalog/release.json) records packaged versions, source commits, digests, and local release status. The [installation guide](docs/installation.md) documents the tested CLI and local catalog route. The disposable lifecycle test proves bundle installation and native dispatch with a no-op Codex executable; it does not prove live-agent behavior or general consumer compatibility.


Start Feature is deprecated and excluded from current source bundle bindings. Its retained source only reports the replacement workflows and stops. Select Feature never creates or changes `spec.md`; an absent target directory is valid until Specify is separately invoked. Existing specifications remain untouched during selection.

See [agent configuration and consumer copies](docs/installation.md#agent-configuration-and-consumer-copies) for approved model/effort defaults, direct customization, update/install-missing and explicit reset commands.

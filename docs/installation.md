# Install and Use Spec Kit Flow

Use the catalog tasks in this repository to install or refresh the bundle. They serve the checked-in release packages on localhost for the duration of each command, so you do not need separate roadmap or wiki source checkouts to install it. The [bundle manifest](../bundles/spec-kit-flow/bundle.yml) and [release metadata](../catalog/release.json) are the sources for current component versions.

Ordinary catalog install and refresh use the checked-in release packages only from a checkout whose source matches that release; the installer rejects a catalog/source mismatch. To dogfood uncommitted source changes, use explicit development-snapshot mode in this repository’s initialized root or a disposable initialized consumer under the system temporary directory. Snapshot installation records unreleased provenance and does not change the checked-in catalog. Local packaging and installation do not imply publication.

## Contents

- [Prepare the checkout](#prepare-the-checkout)
- [Install in another project](#install-in-another-project)
- [Dogfood this repository](#dogfood-this-repository)
- [Use a workflow](#use-a-workflow)
- [Refresh or remove the bundle](#refresh-or-remove-the-bundle)
- [Build release packages](#build-release-packages)
- [Agent configuration and consumer copies](#agent-configuration-and-consumer-copies)

## Prepare the checkout

Run these commands from the Spec Kit Flow checkout. You need `mise` and access to the Specify CLI pinned in `mise.toml`. The repository does not distribute that CLI.

```sh
cd /path/to/spec-kit-flow
mise trust
mise install
mise run python:prepare
mise run python:check
mise exec -- specify --version
```

If `mise install` cannot obtain the pinned Specify fork, make that CLI available before continuing. The catalog tasks check its exact version and reject development snapshots or mismatched package hashes.

The Python preparation commands create and check this checkout's ignored `.venv` with the pinned PyYAML requirement. Ordinary repository Python work should use `mise exec -- python <args>`. Scripts belonging to or validating Codex skills continue to use the separately prescribed skill-tools interpreter. Bundle installation does not prepare Python packages. For a reusable setup in another project, see [Agent Python Environment](agent-python-environment.md).


## Install in another project

Choose an existing project directory outside this checkout, or create an empty one. The install task initializes it with Specify if needed.

```sh
mkdir -p /path/to/my-project
mise run catalog:install /path/to/my-project
```

Verify the installation from the project directory:

```sh
cd /path/to/my-project
specify bundle list
specify extension list
specify workflow list
```

The install task starts and stops its own localhost catalog. Do not add Specify's `--offline` flag; the resolver needs to contact that local catalog.

For Codex skill integration, initialize a new disposable consumer with the skills integration enabled. Existing projects need a Codex installation that discovers project skills under `.agents/skills/`:

```sh
specify init --here --force --non-interactive --integration codex --integration-options="--skills"
```

The supported catalog install also installs ten direct FlowKit skills, shared controller files, and `.specify/flow-kit/skills-install.json`. Native `specify bundle install` manages the workflows and extensions, not those direct skills. Use the FlowKit catalog task so both parts are installed and verified together.

After installation, adoption of project governance is a separate operator decision. Follow the [consumer adoption review](consumer-adoption.md) to inspect active agent guidance and governance, review exact changes, and record the evidence. Installation does not edit those project-owned files or confirm adoption.

To test unreleased controller/workflow changes, initialize an already-created disposable consumer under the system temporary directory, then use the explicit snapshot route:

```sh
consumer_dir="$(mktemp -d)"
specify_bin="$(mise which specify)"
(
  cd "$consumer_dir"
  "$specify_bin" init --here --force --non-interactive --integration codex --integration-options="--skills"
)
PATH="$(dirname "$specify_bin"):$PATH" python3 tools/catalog.py install "$consumer_dir" --development-snapshot
```

Snapshot mode builds a temporary catalog from current source and the checked-in extension packages. It is restricted to this repository’s initialized root or initialized temporary consumers, reports itself as unreleased in the ownership record, and does not change checked-in release metadata. Nested source-checkout targets and other persistent consumers are rejected. The normal install and refresh routes continue to reject snapshots.

## Dogfood this repository

Use a checkout whose source matches the checked-in release as a consumer when developing Spec Kit Flow. From its root, install the release if no `spec-kit-flow` bundle is present:

```sh
mise run catalog:install .
```

If `specify bundle list` already shows `spec-kit-flow`, refresh the existing installation instead:

```sh
mise run catalog:refresh .
```

When this checkout has uncommitted workflow or controller changes, use the explicit snapshot route to rebuild current source in a temporary catalog and refresh this initialized checkout:

```sh
mise run catalog:refresh . --development-snapshot
```

For an initialized checkout with no bundle installed, use `mise run catalog:install . --development-snapshot`. These commands preserve project-owned agents, governance, feature artifacts, wiki content, and controller run history under the same installation ownership checks. They do not commit, publish, or invoke a workflow. Normal release installation continues to require matching release metadata.

Both catalog commands install or refresh the ten active Specify workflows **and** the ten direct FlowKit Codex skills in `.agents/skills/flow-kit-*/`. They also write the separate skill ownership record under `.specify/flow-kit/`. Verify both parts from this checkout:

```sh
mise exec -- specify bundle list
mise exec -- specify workflow list
ls .agents/skills/flow-kit-*/SKILL.md
test -f .specify/flow-kit/skills-install.json
```

The skill picker should then show FlowKit Select Feature, FlowKit Specify, FlowKit Clarify, FlowKit Plan, FlowKit Tasks, FlowKit Analyze, FlowKit Implement, FlowKit Converge, and FlowKit Close Out in a Codex task for this project. If a task was already open before installation, open a fresh task to check discovery. Edit reviewed source under `controllers/`, `workflows/`, and the extension source packages, not the installed copies under `.agents/skills/` or `.specify/`. This repository ignores local installation records and installed payloads.

After installing in this checkout, new local Codex-managed worktrees copy its ignored installation records, FlowKit skill ownership record, extension and workflow payloads, and generated agent files through `.worktreeinclude`. No worktree setup script is needed. Run `mise install` in a worktree if the pinned tools are not already available there.

The copy reflects the source checkout's installed bundle. After changing reviewed release packages, run `mise run catalog:refresh .` in that checkout before creating a worktree. A fresh clone, remote worktree, or plain `git worktree add` does not receive this ignored state; run `mise run catalog:install .` there after preparing the checkout. The workflow registry can contain a temporary localhost catalog URL; use the catalog refresh task to update the bundle.

## Use a workflow

Inspect the workflow before running it in the installed project. Inspect selection and specification authoring as separate workflows:

```sh
specify workflow info speckit-flow-select-feature
specify workflow info speckit-flow-specify
$flow-kit-select-feature
# After selection completes, separately invoke:
$flow-kit-specify
```

The workflow stops at human review gates. Invoke each later workflow separately. The [workflow guide](../workflows/README.md) gives the route and manual fallback. While editing a workflow in this repository, you can run its source `workflow.yml` by path to test an uninstalled change.

In the Codex app, invoke the corresponding FlowKit skill in a task whose selected project is the consumer. The visible names, skill IDs, and required inputs are:

| Display name | Skill invocation | Required input |
| --- | --- | --- |
| FlowKit Select Feature | `$flow-kit-select-feature` | optional `feature_request` |
| FlowKit Specify | `$flow-kit-specify` | active `.specify/feature.json` |
| FlowKit Clarify | `$flow-kit-clarify` | `feature_context` |
| FlowKit Plan | `$flow-kit-plan` | `feature_context` |
| FlowKit Tasks | `$flow-kit-tasks` | `feature_context` |
| FlowKit Analyze | `$flow-kit-analyze-remediate` | `feature_context` |
| FlowKit Implement | `$flow-kit-implement` | `feature_context` |
| FlowKit Converge | `$flow-kit-converge` | `feature_context` |
| FlowKit Close Out | `$flow-kit-closeout` | `feature_context` |

For example, enter `$flow-kit-tasks feature_context=013` in the selected project's Codex task. Optional workflow inputs have defaults and can be supplied in the same `key=value` form. The controller locates the selected compatible Specify executable (preferring the project's mise selection), reads the installed composed workflow without executing native workflow dispatch, and stops before workflow work if runtime, workflow, input, or skill provenance checks fail.

Before workflow work, the FlowKit controller validates every delegated step name, including untaken branches, and probes each distinct native agent with that exact name as the Codex `agent_type`. Codex's native subagent activity shows each launched child. Probe labels include the agent name; work-child labels include the agent name and step ID, while the pane may also show model and reasoning effort. The task label helps the operator see what was launched; the exact `agent_type` request establishes native selection. FlowKit does not require a separate launch message or a per-run agent, model, or effort override. Each delegated step uses a bounded child; steps without explicit delegation metadata and all gates stay in the main task. The main task presents child questions as numbered options plus a custom answer when allowed and relays the response to the same child.

Codex custom-agent files are consumer-owned. Catalog installation adds missing reviewed defaults; you can then edit them directly. The native configuration fields look like this shortened example:

```toml
name = "FlowKit-Reviewer"
description = "Independently assesses workflow artifacts."
model = "gpt-6.1-sol"
model_reasoning_effort = "high"
developer_instructions = "Follow the task scope and return a concise result to the parent."
```

Use the exact reviewed work-type name declared by the workflow step. The canonical package supplies FlowKit-Roadmap Agent, FlowKit-Specifier, FlowKit-Planner, FlowKit-Tasker, FlowKit-Reviewer, FlowKit-Coder, FlowKit-Code Reviewer, and FlowKit-Wiki Curator. The catalog validates package TOML and readable project identities during delivery; the workflow controller delegates native configuration loading and model/effort resolution to Codex. Install-missing preserves existing copies, refresh updates available defaults only, and removal retains all copies. Explicit reset replaces selected current targets. See [agent delivery instructions](#agent-configuration-and-consumer-copies). A successful workflow loader check does not establish that native `specify workflow run` performs FlowKit's named-agent dispatch procedure; use the direct FlowKit Codex skill for that behavior and retain the manual workflow path as fallback.

## Refresh or remove the bundle

After updating this checkout to a newer reviewed release, return to its root and refresh the target project:

```sh
cd /path/to/spec-kit-flow
mise run catalog:refresh /path/to/my-project
```

For an in-repository installation, use `mise run catalog:refresh .` instead. Use the catalog task because a plain `specify bundle update` cannot reach the temporary catalog after the install task exits. Inspect the result if refresh fails; it may have changed some components before stopping. Refresh can remove components previously owned by the bundle when the new manifest omits them.

To remove the bundle, run this in the installed project:

```sh
specify bundle remove spec-kit-flow
specify bundle list
```

Confirm that unrelated components remain. The consumer's feedback journal is local evidence and should remain available after removal.

For a supported complete removal of the bundle and its direct FlowKit skills, run the catalog command from the source checkout:

```sh
mise run catalog:remove /path/to/my-project
```

It checks the recorded skill inventory and file digests before calling native bundle removal, then removes only unchanged FlowKit-owned skills and the ownership record. A collision or locally edited owned file stops removal for review. Recovery summaries under `.specify/flow-controllers/runs/`, unrelated skills, feedback, and independently installed components are preserved. The native `specify bundle remove` command alone removes the bundle contents but does not manage direct Codex skills.

After refresh, reassess current project state with the [consumer adoption review](consumer-adoption.md); refresh does not edit or confirm adoption. Bundle removal also leaves project-owned guidance, governance, feature history, and adoption review records intact.

## Build release packages

Maintainers need clean checkouts of the independent roadmap and wiki repositories at annotated release tags matching the [bundle manifest](../bundles/spec-kit-flow/bundle.yml). From this repository's root, run:

```sh
mise run catalog:build /path/to/spec-kit-flow-roadmap /path/to/spec-kit-flow-wiki
```

The builder checks source IDs, versions, tags, and cleanliness, then writes deterministic extension archives and source digests to `catalog/`. Review the resulting package contents and diff before committing a release. `--snapshot` is for development packaging; install and refresh reject snapshots. Do not edit archives directly.


## Start Feature deprecation

Current source replaces Start Feature with separately invoked Select Feature and Specify. Selection updates the exactly approved roadmap delta and active pointer without writing a specification; Specify authors the active target and runs its brief. Controller refresh removes an unchanged owned `flow-kit-start-feature` launcher and installs the replacements; a locally edited retired launcher blocks refresh for operator resolution. Historical catalog releases still contain the old workflow. Do not infer replacement discovery until the current development snapshot has been installed or refreshed. The deprecated source is retained as a stop-only compatibility notice, outside active bundle bindings.


## Agent Configuration and Consumer Copies

The development bundle includes `flow-kit-agents` 0.1.0, composed from canonical `agents/flow-kit/` source. Installed files under `.codex/agents/` are consumer-owned and may be edited directly. Package-level source/artifact digests establish provenance; FlowKit does not hash, classify, own or merge consumer copies.

| Role | Model | Effort |
|---|---|---|
| FlowKit-Roadmap Agent | `gpt-6.1-sol` | low |
| FlowKit-Specifier | `gpt-6.1-sol` | high |
| FlowKit-Planner | `gpt-6.1-sol` | high |
| FlowKit-Tasker | `gpt-6-luna` | high |
| FlowKit-Reviewer | `gpt-6.1-sol` | high |
| FlowKit-Coder | `gpt-6-luna` | high |
| FlowKit-Code Reviewer | `gpt-6.1-sol` | medium |
| FlowKit-Wiki Curator | `gpt-6.1-sol` | low |

Specifier, Planner and Reviewer retain depth for product, architecture and cross-artifact judgment. Coder and Tasker use bounded approved inputs with independent review. Roadmap/Wiki work is scoped bookkeeping; Code Reviewer independently checks selected implementation at medium effort. This rationale is engineering judgment rather than a measured quality/cost comparison. Native support, requested configuration, live exact-role dispatch and observed effective settings are distinct evidence categories.

### Install and Customize

Initialize a Specify consumer with the supported CLI version, then install the bundle from a matching catalog checkout. Installation adds absent defaults only after components are installed. Existing destinations, old unprefixed files and unrelated agents are preserved. Current unreleased source validation uses an initialized disposable consumer and `--development-snapshot`:

```bash
mise run catalog:install -- "$consumer_project" --development-snapshot
mise run catalog:agents -- install-missing "$consumer_project" --json
```

The first command already runs install-missing; the second is useful after refresh or to retry absent copies. Edit the resulting native files directly to customize instructions, model or effort. Changes are version-controlled by the consuming project according to its own policy.

### Update or Restore Defaults

Refresh updates the available-default cache only; it preserves all agent copies. To acquire newly added definitions after upgrading the selected bundle, refresh then run install-missing:

```bash
mise run catalog:refresh -- "$consumer_project" --development-snapshot
mise run catalog:agents -- install-missing "$consumer_project" --json
```

To discard selected customizations and reapply cached defaults, explicitly reset one exact current name or all current manifest entries:

```bash
mise run catalog:agents -- reset "$consumer_project" --agent "FlowKit-Planner" --json
mise run catalog:agents -- reset "$consumer_project" --all --json
```

Reset invocation authorizes replacing the selected copies without another interactive prompt. `--all` means the selected package inventory, never a prefix glob. Reset also creates missing selected files. Unknown names, conflicting exact identities, invalid package data, directories and unsafe/symlink paths fail rather than silently overwrite. Neither refresh nor install-missing performs reset.

### Migration, Recovery and Removal

The prefix change requires the coordinated bundle/controller/workflow versions; old-only inventories cannot dispatch migrated workflows. Retained old files are not renamed or deleted automatically. Review the new copies and manually carry customizations into their exact new names, or reset the selected current targets. A competing exact name in another file blocks delivery until the operator resolves that identity conflict. Renamed and retired files remain for manual removal after dependent assignments are inspected. Unparseable unrelated TOML produces a warning that inventory readiness is unverified.

Human and JSON output report package/source provenance, selected inputs, manifest-ordered target outcomes and recovery. Identity conflicts include competing project-relative paths and the exact name when portable. Path-like names or names containing control characters are reported as `<redacted>` with `identity_redacted: true`. JSON exposes these in a nullable `conflict` object with `name`, `identity_redacted`, `paths` and `recovery`. Resolve the competing definitions after inspecting dependent assignments, then retry the same operation. Outcomes are `created`, `preserved-existing`, `reset`, `failed` or `not-attempted`; status is `complete`, `failed` or `partial`. Exit codes are 0 for completion, 1 for validation/write/usability failure and 2 for argument errors; diagnostics go to stderr. Atomic per-file writes prevent truncated TOML. On partial results inspect completed/failed/unattempted targets, resolve the cause and reissue the same explicit operation. No bundle rollback is implied.

`catalog:remove` removes the available-default cache and existing managed components while retaining every consumer agent copy, feedback and unrelated component. Remaining workflow assignments may still require those native names. Manual workflow prompts remain available when native dispatch is unavailable; consumer installation is not evidence of successful native dispatch or feature acceptance.

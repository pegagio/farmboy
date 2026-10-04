---
title: Installation and release lifecycle
type: howto
sources: [S001, S002, S005, S016, S025]
updated: 2026-10-03
---

# Installation and release lifecycle

Catalog tasks install or refresh the bundle, ten active Specify workflows, and ten direct FlowKit Codex skills through a temporary localhost catalog, verifying components and skills together. Native bundle installation manages workflows and extensions, not direct skills. The install task can initialize an empty target project. (S005)

Prepare with `mise trust` and `mise install`, then use `mise run catalog:install <project-directory>` or `mise run catalog:install .` locally. Ordinary install and refresh require source matching the checked-in release and reject mismatches. Inspect installed identities and provenance before use; this repository does not distribute its pinned Specify CLI. (S005)

For uncommitted source, explicit development-snapshot install or refresh supports this repository's initialized root or an initialized disposable consumer under the system temporary directory. Dogfood with `mise run catalog:refresh . --development-snapshot`, or `catalog:install . --development-snapshot` when no bundle is installed. Nested source-checkout targets and other persistent consumers are rejected. A temporary catalog records unreleased snapshot provenance without changing checked-in release metadata. Ownership checks preserve project-owned agents, governance, feature artifacts, wiki, and controller history; these commands do not commit, publish, or invoke workflows. (S005)

Earlier README guidance allowed snapshots only in temporary consumers and prohibited source-root installation. That restriction is superseded here by the current guide's initialized-root route; AGENTS directs installation-path decisions to the guide and release metadata. This preserves the README's provenance without treating its older restriction as current or implying that the sources agree. (S002, S005, S001)

After a reviewed release, use `mise run catalog:refresh <project-directory>` from this checkout. Plain `specify bundle update` cannot reach the temporary catalog after the task exits or manage direct skills. Failed refresh may have changed components; a new manifest may remove formerly owned components. (S005)

Local Codex-managed worktrees copy ignored installed state through `.worktreeinclude`; fresh clones, remote worktrees, and plain Git worktrees need their own installation. Edit reviewed source packages rather than installed copies. (S002, S005)

Maintainers build deterministic release packages from clean roadmap and wiki checkouts at matching annotated tags. The bundle manifest and release metadata identify current component versions. Ordinary catalog install/refresh require matching release source; explicit development snapshots record unreleased provenance. Local packaging and installation do not establish publication. (S005)

Complete catalog removal checks skill ownership and digests before native removal; collisions or edited owned files stop for review. Recovery summaries, unrelated skills, independently installed components, and feedback survive. Native removal alone does not manage direct skills. Governance, guidance, feature history, and adoption records remain project-owned; adoption is a separate operator decision. (S005)

Release building checks source IDs, versions, clean feedback source, and clean annotated external tags. Installation checks package digests, pins, and the tested CLI. Disposable lifecycle success does not establish remote publication, stock compatibility, roadmap verification, Git integration, or acceptance. (S016, S005)

Select Feature and Specify are separate. Start Feature remains stop-only deprecated source outside active bindings; replacement discovery requires installation or refresh. Refresh replaces an unchanged owned retired launcher; local edits block for resolution. (S005)

The direct Codex path validates and probes every delegated branch's exact native agent names before work. Consumer-owned agent files and Codex control optional model/effort settings. Gates and undelegated steps stay in the main task. (S005)

Feature 017 specifies prospective consumer-owned acquisition and explicit resets; see [its delivery contract](./flowkit-agent-configuration-and-delivery.md). (S025)

## Related pages

- [Bundle and workflow model](./bundle-and-workflow-model.md)
- [Codex workflow controller design](./codex-workflow-controllers.md)
- [Workflow lifecycle](./workflow-lifecycle.md)
- [Named agents for delegated steps](./agent-roles-and-inheritance.md)

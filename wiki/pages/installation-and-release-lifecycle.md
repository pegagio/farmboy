---
title: Installation and release lifecycle
type: howto
sources: [S001, S002, S005, S016, S025]
updated: 2026-10-04
---

# Installation and release lifecycle

Catalog tasks install or refresh the bundle, ten active Specify workflows, and ten direct FlowKit Codex skills through a temporary localhost catalog, verifying components and skills together. Native bundle installation manages workflows and extensions, not direct skills. Install can initialize empty projects. (S005)

Preparation selects pinned tools through mise, but catalog agent handling requires PyYAML in the executing Python. `mise install` does not provision it: the documented catalog path failed with `ModuleNotFoundError: No module named 'yaml'`; a separately prepared interpreter succeeded. DEP017-01 defers repair and runnable provisioning guidance; this disclosure does not fix setup. Ordinary install/refresh require matching release source; the pinned Specify CLI is not distributed here. (S005)

Explicit development snapshots support the initialized source root or initialized temporary consumers; nested targets and other persistent consumers are rejected. They record unreleased provenance without changing release metadata, preserve project-owned artifacts/history, and do not invoke workflows or integrate Git. (S005)

Earlier README guidance allowed snapshots only in temporary consumers and prohibited source-root installation. That restriction is superseded here by the current guide's initialized-root route; AGENTS directs installation-path decisions to the guide and release metadata. This preserves the README's provenance without treating its older restriction as current or implying that the sources agree. (S002, S005, S001)

After a reviewed release, use `mise run catalog:refresh <project-directory>` from this checkout. Plain `specify bundle update` cannot reach the temporary catalog after the task exits or manage direct skills. Failed refresh may have changed components; a new manifest may remove formerly owned components. (S005)

Local Codex-managed worktrees copy ignored installed state through `.worktreeinclude`; fresh clones, remote worktrees, and plain Git worktrees need their own installation. Edit reviewed source packages rather than installed copies. (S002, S005)

Complete catalog removal checks skill ownership and digests before native removal; collisions or edited owned files stop for review. Recovery summaries, unrelated skills, independently installed components, and feedback survive. Native removal alone does not manage direct skills. Governance, guidance, feature history, and adoption records remain project-owned; adoption is a separate operator decision. (S005)

Release building checks source IDs, versions, clean feedback source, and clean annotated external tags. Installation checks package digests, pins, and the tested CLI. Disposable lifecycle success does not establish remote publication, stock compatibility, roadmap verification, Git integration, or acceptance. (S016, S005)

Select Feature and Specify are separate. Start Feature remains stop-only deprecated source outside active bindings; replacement discovery requires installation or refresh. Refresh replaces an unchanged owned retired launcher; local edits block for resolution. (S005)

The direct Codex path validates and probes every delegated branch's exact native agent names before work. Consumer-owned agent files and Codex control optional model/effort settings. Gates and undelegated steps stay in the main task. (S005)

Earlier Feature 017 specification described prospective acquisition; the current guide documents delivery operations under [its contract](./flowkit-agent-configuration-and-delivery.md). Install-missing adds absent defaults and preserves existing, old unprefixed and unrelated files. Refresh changes only available defaults; acquiring new copies requires install-missing. Explicit reset selects one exact current name or all manifest entries, replacing or creating those targets. Unknown names, unsafe paths and competing exact identities block delivery. Renamed/retired files remain for manual migration after dependent assignments are inspected. (S025, S005)

Human/JSON reports expose package/source provenance, selected inputs, target outcomes and recovery. Collisions identify portable competing paths; unsafe identities are redacted. Partial mutation requires inspecting completed, failed and unattempted targets, resolving the cause and retrying the same explicit operation; bundle rollback is not implied. Removal deletes available defaults while preserving every consumer agent copy. (S005)

## Related pages

- [Bundle and workflow model](./bundle-and-workflow-model.md)
- [Codex workflow controller design](./codex-workflow-controllers.md)
- [Workflow lifecycle](./workflow-lifecycle.md)
- [Named agents for delegated steps](./agent-roles-and-inheritance.md)

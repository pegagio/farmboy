---
title: Installation and release lifecycle
type: howto
sources:
- S001
- S002
- S005
- S016
- S025
- S032
- S034
updated: '2026-10-12'
---

# Installation and release lifecycle

## FarmBoy source cutover (2026-10-10)

New source and fresh supported installations use FarmBoy names. Managed skills use `.agents/skills/farmboy-<purpose>/`, helpers use `.specify/farmboy/`, workflows use `.specify/workflows/farmboy-<purpose>/`, and default agents use `.codex/agents/farmboy-<role>.toml`. New summaries/history use `.specify/farmboy-controllers/`; completed `.specify/flow-controllers/` history remains in place. (S032)

Existing install/refresh/remove/agent-management operations preserve their behavior and ownership protections. This cutover supplies no migration, old-name alias, legacy conversion reader, customization transfer or automatic existing-consumer refresh. Actual replacement requires separate operator instructions. [Earlier installation history](./installation-history-before-farmboy.md) preserves preceding guidance. (S032)

The unreleased snapshot: bundle 0.18.3, controllers 0.9.1 and Close Out 0.9.2. All 113 active prompt nodes bind `inputs.integration`: 111 additions across the Clarify fix and mechanical batch; two Specify bindings predated them. Steps, roles, gates, routes, caps and controller policy remain unchanged. (S032)

Native Specify lifecycle evidence uses a no-op Codex fixture; it proves fixture dispatch, not live FarmBoy agent execution. Linux, publication, stock compatibility, consumer adoption and acceptance remain unproved. (S032)

Current README and guides require release/source agreement for ordinary installation and unreleased provenance for snapshots. Installing or refreshing components does not adopt governance; inspect actual authority and guidance separately. (S002, S034)

## Retained management contracts

After a reviewed release, use `mise run catalog:refresh <project-directory>`. Plain `specify bundle update` cannot reach the temporary catalog after the task exits or manage direct skills. Failed refresh may have changed components; a new manifest may remove formerly owned components. (S005, S034)

Local Codex worktrees copy ignored installed state through `.worktreeinclude`; clones, remote and plain Git worktrees need installation. Edit reviewed source packages rather than installed copies. (S002, S005, S034)

Complete catalog removal checks skill ownership and digests before native removal; collisions or edited owned files stop for review. Recovery summaries, unrelated skills, independently installed components, and feedback survive. Native removal alone does not manage direct skills. Governance, guidance, feature history, and adoption records remain project-owned; adoption is a separate operator decision. (S005, S034)

Release building checks source IDs, versions, clean feedback source, and clean annotated external tags. Installation checks package digests, pins, and the tested CLI. Disposable lifecycle success does not establish remote publication, stock compatibility, roadmap verification, Git integration, or acceptance. (S016, S005, S034)

Select Feature and Specify are separate. Start Feature remains stop-only deprecated source outside active bindings; replacement discovery requires installation or refresh. Refresh replaces an unchanged owned retired launcher; local edits block for resolution. (S005, S034)

The direct Codex path validates and probes every delegated branch's exact names before work. Consumer-owned agent files and Codex control optional model/effort settings. Gates and undelegated steps stay in the main task. (S005, S034)

Earlier Feature 017 specification described prospective acquisition; the current guide documents delivery operations under [its contract](./flowkit-agent-configuration-and-delivery.md). Install-missing adds absent defaults and preserves existing, old unprefixed and unrelated files. Refresh changes only available defaults; acquiring new copies requires install-missing. Explicit reset selects one exact current name or all manifest entries, replacing or creating those targets. Unknown names, unsafe paths and competing exact identities block delivery. Renamed/retired files remain for manual migration after dependent assignments are inspected. (S025, S005, S034)

Human/JSON reports expose provenance, inputs, outcomes and recovery. Collisions identify portable paths; unsafe identities are redacted. Partial mutation requires inspecting outcomes, resolving the cause and retrying the explicit operation; no bundle rollback is implied. Removal deletes defaults, preserving consumer copies. (S005, S034)

Consumer collector and [maintainer report discovery](./maintainer-metrics-report-discovery.md). (S005)

## Related pages

- [Bundle and workflow model](./bundle-and-workflow-model.md)
- [Codex workflow controller design](./codex-workflow-controllers.md)
- [Workflow lifecycle](./workflow-lifecycle.md)
- [Named agents for delegated steps](./agent-roles-and-inheritance.md)

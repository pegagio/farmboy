---
title: Installation history before FarmBoy
type: howto
sources:
- S001
- S002
- S005
- S016
- S025
- S032
updated: '2026-10-11'
---

# Installation history before FarmBoy

Catalog tasks install/refresh the bundle, ten active workflows and ten direct Codex skills through a temporary localhost catalog, verifying both. Native bundle installation excludes direct skills; catalog install can initialize empty projects. (S005)

Preparation now provides `python:prepare`/`python:check`, an ignored local `.venv` with pinned PyYAML, `mise exec -- python` for ordinary work, and the skill-tools exception. Bundle installation does not prepare packages; a copyable agent-environment guide supports other projects. Earlier `mise install` alone failed on missing PyYAML; an alternate prepared interpreter succeeded. That historical failure remains, separate from current preparation and full catalog/native validation. Release matching and CLI availability remain prerequisites. (S005)

Explicit development snapshots support the initialized source root or initialized temporary consumers; nested targets and other persistent consumers are rejected. They record unreleased provenance without changing release metadata, preserve project-owned artifacts/history, and do not invoke workflows or integrate Git. (S005)

Earlier README guidance restricted snapshots to temporary consumers. That restriction is superseded here by the current guide's initialized-root route; AGENTS directs installation-path decisions to the guide and release metadata. The older restriction remains historical provenance. (S002, S005, S001)

## Refreshed README boundary

The temporary-only README restriction above belongs to its earlier snapshot. Refreshed README now explicitly permits the initialized source checkout or disposable temporary consumers, while ordinary installation and refresh reject snapshots. This change supersedes the earlier restriction without proving release or consumer adoption; see the [current lifecycle](./installation-and-release-lifecycle.md). (S002)

## Related page

[Current account](./installation-and-release-lifecycle.md). Historical contracts remain provenance; Feature 021 establishes the naming cutover. (S032)

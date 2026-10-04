# Contract: Reviewed FlowKit Agent Package

This prospective contract defines canonical generic source and portable catalog integrity. It does not acquire ownership of consumer copies.

## Package layout

The new reviewed source package `agents/flow-kit/` starts at version `0.1.0`. Catalog builds produce a deterministic archive containing `manifest.yml` and the eight `agents/*.toml` members below. Only listed files are accepted.

| Exact name | Source member | Consumer destination |
|---|---|---|
| FlowKit-Roadmap Agent | `agents/flowkit-roadmap-agent.toml` | `.codex/agents/flowkit-roadmap-agent.toml` |
| FlowKit-Specifier | `agents/flowkit-specifier.toml` | `.codex/agents/flowkit-specifier.toml` |
| FlowKit-Planner | `agents/flowkit-planner.toml` | `.codex/agents/flowkit-planner.toml` |
| FlowKit-Tasker | `agents/flowkit-tasker.toml` | `.codex/agents/flowkit-tasker.toml` |
| FlowKit-Reviewer | `agents/flowkit-reviewer.toml` | `.codex/agents/flowkit-reviewer.toml` |
| FlowKit-Coder | `agents/flowkit-coder.toml` | `.codex/agents/flowkit-coder.toml` |
| FlowKit-Code Reviewer | `agents/flowkit-code-reviewer.toml` | `.codex/agents/flowkit-code-reviewer.toml` |
| FlowKit-Wiki Curator | `agents/flowkit-wiki-curator.toml` | `.codex/agents/flowkit-wiki-curator.toml` |

## Manifest and configuration

Manifest entries follow this example, repeated for every role:

```yaml
schema_version: "1.0"
package:
  id: flow-kit-agents
  version: "0.1.0"
agents:
  - name: FlowKit-Planner
    file: agents/flowkit-planner.toml
    destination: .codex/agents/flowkit-planner.toml
changes:
  added: []
  renamed: []
  retired: []
```

`changes.renamed` entries use `from`, `to` and `guidance`; retirement entries use `name` and `guidance`. First release documents each unprefixed-to-prefixed migration here or release guidance. Metadata informs operators; it never grants authority to mutate old files.

Each TOML defines the three native required fields plus approved explicit `model`/`model_reasoning_effort`; `name` is exact dispatch identity. The operator-approved settings are in [research](../research.md#approved-model-and-effort-decisions); this manifest example does not supply runtime verification. Do not introduce sandbox/tool permission overrides as part of this feature.

## Integrity and composition

The bundle pins package ID/version. Catalog `agent_package` records artifact digest, source digest/commit/repository, version and released/snapshot status; verification rejects changed bytes, inconsistent version, duplicate identities and unsafe entries before consumers mutate. Package-level integrity hashes do not track individual consumer copies. A release cannot change an artifact under unchanged released coordinates; coordinated source/workflow/controller/bundle version bumps must accompany the breaking name change.

Available defaults are cached as `package.zip` and `manifest.json` under `.specify/flow-kit/agent-defaults/`. Metadata contains package provenance only. Ordinary refresh atomically replaces validated available defaults. Copy/reset consumes that selected package; it never fetches an unpinned alternative or silently regenerates settings.

## Compatibility boundaries

Ten active workflows migrate exact names while preserving step topology, assignment responsibilities, human gates and manual fallback. Deprecated Start Feature remains stop-only. A consumer with old-only names is reported unresolved; there is no alias. Feature 016 timing/probing and capacity configuration remain independent. Removal preserves consumer copies and documents dependent native assignments that remain if only defaults acquisition is removed.

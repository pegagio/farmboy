# Data Model: FlowKit Agent Configuration and Consumer Delivery

This is a file/package model, not a database schema. It separates reviewed defaults, available package state and consumer-owned copies so lifecycle logic never infers ownership.

## Table of Contents

- [Entities](#entities)
- [Validation and Relationships](#validation-and-relationships)
- [Transitions](#transitions)
- [Evidence Record](#evidence-record)

## Entities

Entities describe durable source and bounded operation output.

| Entity | Fields | Authority |
|---|---|---|
| Agent definition | `name`, `description`, `developer_instructions`, `model`, `model_reasoning_effort` | Canonical reviewed TOML; copied TOML becomes consumer-owned |
| Agent package manifest | `schema_version`, `package.id`, `package.version`, `agents[]` with exact `name`, relative `file`, project-relative `destination`; `changes` with additions/renames/retirements | Reviewed generic source inventory, not an ownership registry |
| Catalog package record | `id`, `version`, `artifact`, `sha256`, `source_repository`, `source_commit`, `source_sha256`, `status` | Bundle composition/integrity metadata; digests apply to source/package only |
| Available defaults | Package archive and its metadata at `.specify/flow-kit/agent-defaults/` | Selected catalog package; replaceable cache, not consumer agent state |
| Consumer agent copy | Native `.codex/agents/flowkit-*.toml` file | Consumer; no installed hash, equality flag or customization classification |
| Operation result | `schema_version`, `operation`, `status`, `package` provenance, `targets[]`, `warnings[]`, `recovery` | Portable observation of one operation; not permanent file ownership |
| Model decision | Exact role/pair, rationale, source evidence/date, approval status and operator amendment | Feature decision record; approval not inferred from authoring |

## Validation and Relationships

An inventory maps one exact name to one canonical file and one allowed destination; duplicate names/files/destinations fail. Definitions must parse as TOML, contain nonempty required fields and match manifest names. Source/package files must be regular and cannot escape allowed roots via `..`, absolute paths or symlinks. Unlisted archive entries fail. All reset targets must be current manifest entries.

A bundle references one selected version of `flow-kit-agents`; the archive digest verifies that artifact. Available defaults reference that selected package. Copy operations derive content/destination from it; they do not register ownership. Workflow delegated assignments resolve exact `name`, not a filename-derived alias or role-to-model mapping. Global/project duplicate exact names require explicit inventory failure/resolution before dispatch readiness is claimed.

Model support is client-specific evidence; a string matching the approved choice is necessary but insufficient for effective-setting verification. Do not reject ordinary consumer customization merely because it differs from source defaults; native availability/required role contract failures remain explicit.

## Transitions

Transitions are operations on separate entities, not a managed-copy lifecycle.

| Trigger | Available defaults | Consumer copies |
|---|---|---|
| Bundle install | Validate and stage selected package | Copy absent current targets; preserve existing paths |
| Install-missing | Require valid selected cache | Absent → copied; existing → preserved |
| Ordinary refresh | Old package → validated new package | No mutation, including missing/new definitions |
| Reset-one | Unchanged | Selected current target → current default, customization discarded |
| Reset-all | Unchanged | All current manifest targets → defaults; unrelated/retired/unprefixed untouched |
| Bundle removal | Remove available cache | Preserve every copy |
| Rename/retirement | New manifest/change guidance | Retain old definition until operator removal |
| Write failure | Preserve prior cache if cache replacement fails | Report completed targets and failed/not-attempted remainder; no silent success |

Consumer state is only absent or present for copy operations. There is deliberately no `owned`, `modified`, `clean`, `stale-copy` or content-difference classification.

## Evidence Record

Validation artifacts may describe the following independent observations:

```json
{
  "schema_version": "1.0",
  "role": "FlowKit-Planner",
  "requested": {"model": "gpt-6.1-sol", "model_reasoning_effort": "high"},
  "configuration": "passed",
  "field_value_support": "unverified",
  "live_exact_dispatch": "not_run",
  "effective_settings": {"status": "unverified", "reason": "No child settings observed"},
  "client": {"kind": "codex-cli", "version": "0.157.1"},
  "specify_cli_version": "1.0.10.dev0+pegagio.2",
  "source_coordinate": "agents/flow-kit/",
  "package_version": "0.1.0",
  "package_digest": "<observed-at-validation>"
}
```

This illustrative record is not observed validation. Real records identify source commit and digest, scenario input and actual outcomes, avoiding secrets, transcripts and absolute host paths. Successful exact dispatch can coexist with unverified effective settings.

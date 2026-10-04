# Contract: Consumer Agent Delivery CLI

This proposed interface extends `tools/catalog.py`. Commands below are design contracts, not currently available commands. Existing bundle commands keep their skill/component semantics.

## Commands and authority

All operations require an initialized consumer project and validated selected defaults. Proposed syntax is:

```text
python3 tools/catalog.py agents install-missing <project> [--json]
python3 tools/catalog.py agents reset <project> --agent "FlowKit-Planner" [--json]
python3 tools/catalog.py agents reset <project> --all [--json]
```

`--agent` requires one exact current manifest name. `--all` and `--agent` are mutually exclusive; no wildcard, omitted target, alias or prefix expansion is allowed. Reset command invocation explicitly authorizes discarding the selected files' customizations; help/result text makes this consequence clear. No additional interactive prompt is required by this contract. No reset occurs during install, refresh or removal.

`catalog install` caches defaults and invokes install-missing after component/default installation; existing skill conflicts still follow their existing validation. `catalog refresh` updates available defaults only. Operators invoke install-missing afterward to add newly introduced definitions. `catalog remove` preserves every consumer `.codex/agents/` file. `mise run catalog:agents -- ...` forwards the agent subcommand; individual extra wrappers are unnecessary.

## Disposition and errors

Install-missing preserves every existing destination regardless of content. A destination directory/symlink is preserved but reported as an unusable path with failure rather than claimed installed. Reset refuses nonregular destinations and symlink/unsafe parent paths; missing selected files can be created. Validate all planned targets before any agent write. Unknown name, missing cache, malformed inventory, package mismatch, duplicate exact names in the project inventory or path escapes fail with zero agent writes. Package installation and other bundle components may already have completed; reports distinguish those effects.

Do not scan personal/global config files as part of file delivery. Native inventory confirmation before dispatch can report duplicate global/project identities; delivery static checks cover readable project agent TOML only. Unparseable existing unrelated TOML is not authority to edit it: warn that full dispatch readiness is unverified. Duplicate project identities are actionable inventory conflicts.

## Portable result

`--json` emits one JSON object on stdout; diagnostics use stderr. Human output describes the same outcomes. Success exits 0; validation/write/unresolved usability failure exits 1; invalid command arguments exit 2. Targets preserve manifest order.

```json
{
  "schema_version": "1.0",
  "operation": "install-missing",
  "status": "complete",
  "package": {"id": "flow-kit-agents", "version": "0.1.0", "sha256": "<observed-digest>", "status": "snapshot"},
  "targets": [
    {"name": "FlowKit-Planner", "path": ".codex/agents/flowkit-planner.toml", "outcome": "preserved-existing"},
    {"name": "FlowKit-Coder", "path": ".codex/agents/flowkit-coder.toml", "outcome": "created"}
  ],
  "warnings": [],
  "recovery": null
}
```

Allowed target outcomes are `created`, `preserved-existing`, `reset`, `failed`, `not-attempted`; overall status is `complete`, `failed` or `partial`. Actual full-inventory results list all selected targets; this shortened example is illustrative. Reports include source provenance from package metadata, operation inputs and portable error codes/reasons, never raw transcripts, file contents or absolute host paths. No result includes a consumer hash, ownership bit or inferred customization classification.

## Recovery and migration

Atomic individual writes prevent truncated TOML. On failure after one or more writes, report `partial`, completed targets and exact recovery; never imply bundle rollback. Install-missing can retry remaining absent paths. Reset retry requires the same explicit targets; users inspect completed results before reissuing it. Available-default cache replacement retains the prior package if staging/validation fails.

Old unprefixed configs survive. To customize during migration, manually adapt retained instructions/settings to a new copied exact name after reviewing the contract; to start over, explicitly reset selected current agents. Remove duplicate/retired definitions manually only after inspecting dependent assignments. Mixed installed/default versions block readiness claims until coordinated package/workflow refresh and missing-name acquisition resolve them. No automatic deletion, alias or model fallback is supplied.

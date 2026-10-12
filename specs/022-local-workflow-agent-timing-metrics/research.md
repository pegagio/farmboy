# Research: Local Workflow Agent Timing Metrics

Research is bounded to the current clarified [specification](spec.md), Constitution 8.0.0, reviewed source and primary API documentation accessed on 2026-10-11. Findings propose design choices; they do not prove metrics implementation.

## Table of Contents

These decisions describe the basic technical approach and its approved maintainer-only dependency boundary.

- [Shared Dispatch Boundary](#shared-dispatch-boundary)
- [Preflight Correlation](#preflight-correlation)
- [Clock and Adapter](#clock-and-adapter)
- [Agent Settings Metadata](#agent-settings-metadata)
- [Completed Publication](#completed-publication)
- [Workbook Writer](#workbook-writer)
- [Delivery and Validation](#delivery-and-validation)

## Shared Dispatch Boundary

**Decision**: Place structured `begin`/`finish` helper calls beside native spawn and same-child continuation in the shared controller protocol.

**Rationale**: `controllers/farmboy/controller-protocol.md` directs main-task native exact-name dispatch, probes and interactive relay. `controllers/farmboy/scripts/python/controller.py` validates, renders and routes; it does not run native children. Timing that Python helper alone misses actual agent lifetime. One helper and shared protocol rule cover ten workflows without changing their graphs.

**Alternatives considered**: Timing child/core commands, duplicating rules across workflows, replacing native dispatch with a subprocess runner, or a generic telemetry layer. They miss probes/continuations, fragment behavior or violate named-agent boundaries. Adjacent helper-call scheduling remains uncorrected overhead; live ordering evidence is needed rather than exact runtime-profiling claims.

## Preflight Correlation

**Decision**: Generate one separate metrics correlation UUID in validated `inspect` output before probes and retain it in the existing main-task context for that workflow invocation. Use it as the metric record's `run_id` across probes and working turns. Do not reuse it as the recovery ID or change recovery creation.

**Rationale**: Metrics need a grouping key before probing starts, while recovery already owns its own identity and storage. The operator explicitly chose separate metrics correlation on 2026-10-12 to avoid unnecessary coupling. Retain the grouping key through continuations and resumption of the same controller context. Existing recovery behavior remains unchanged; no new directory or metrics state file is required. Use an already known nonpersonal project identity or `unspecified`.

**Alternatives considered**: Sharing the metrics UUID with recovery led to unnecessary recovery API, directory-reservation and validation changes; that approach is superseded by the operator's simplification. Early workflow summaries and retrospective metric rewriting remain unnecessary, while separate probe and working-turn metrics IDs would break correlation. A separate grouping key in the existing controller context is sufficient.

## Clock and Adapter

**Decision**: Capture `int(time.time() * 1000)` from the local wall clock, retain integer milliseconds, render millisecond UTC strings and use direct signed subtraction. No nanosecond precision is required. A stdlib helper owns observations and emission, never dispatch.

**Rationale**: The operator explicitly confirms millisecond precision is sufficient. Capture and convert once, then derive both timestamp strings and duration from the same integer millisecond values. This keeps the basic local wall-clock measurement consistent without a nanosecond requirement. Clock anomalies remain accepted. See [Python 3.11 time API](https://docs.python.org/3.11/library/time.html#time.time).

**Alternatives considered**: Monotonic/CPU/distributed clocks, correction and estimated missing endings. They add unapproved semantics. Start tokens remain in main-task context; no pending ledger is needed.

## Agent Settings Metadata

**Decision**: Add optional nullable `model` and `effort`, named by the operator on 2026-10-12. Read the matching project agent TOML by exact `name`, selecting only `model` and `model_reasoning_effort` with standard-library `tomllib` before clock capture. Missing/unusable values are null; there is no inheritance resolver or new dependency.

**Rationale**: The operator chose a basic file read to help compare durations by declared model/effort. The short field names describe explicit file settings, not verified runtime execution. Codex still selects and configures the native agent. [Official custom-agent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents) identifies `name` as the identity and supports model and reasoning-effort configuration.

**Alternatives considered**: Runtime inspection is not consistently exposed; hardcoded role/model mappings go stale; resolving global and inherited defaults adds unnecessary complexity. Prefixing the fields with `configured_` was explicitly rejected by the operator.

## Completed Publication

**Decision**: Exclusively stage in the target directory, close, hard-link to a completed unique name without overwrite, then unlink the writer-owned temporary name. Reuse for workbook publication.

**Rationale**: Exclusive final writes avoid collisions but expose partial data; replace-based publication hides partial data but overwrites existing paths. Same-directory hard links combine completed visibility with no-clobber behavior on the initial local filesystem. Test actual support and failures. See [Python 3.11 filesystem operations](https://docs.python.org/3.11/library/os.html#os.link).

**Alternatives considered**: Shared JSONL appends, locks, check-before-rename, ready markers or platform-specific rename. They introduce races, extra files or complexity. Unsupported linking warns/fails without unsafe fallback; no power-loss durability guarantee is inferred.

## Workbook Writer

**Decision — approved by the operator on 2026-10-11**: `openpyxl==3.1.5`, confined to the maintainer skill requirements and skill-tools environment, including required `et-xmlfile`. The operator answered “Yes” to the main-task dependency question, and the controller validated/relayed that answer to the same Planner child. Nothing is added to consumer or agent runtime requirements. No dependency installation or planning-phase environment change was authorized or performed.

**Rationale**: A maintained XLSX writer supplies real tables and explicit cell types. Write-only worksheets reduce retained cell memory; explicit public `TableColumn` headers must match header cells, and text types must override formula/error inference. Skill-tools currently has neither dependency; no installation occurred. PyPI lists stable 3.1.5, MIT license and Python >=3.8. See [package metadata](https://pypi.org/project/openpyxl/), [table API](https://openpyxl.readthedocs.io/en/stable/api/openpyxl.worksheet.table.html), [tables guidance](https://openpyxl.readthedocs.io/en/stable/worksheet_tables.html) and [write-only mode](https://openpyxl.readthedocs.io/en/stable/optimized.html).

**Alternatives considered**: XlsxWriter is a suitable writer, but tables are unavailable in its constant-memory mode; see [its table limitation](https://xlsxwriter.readthedocs.io/working_with_tables.html). Pandas adds unnecessary machinery. A stdlib ZIP/XML writer makes FarmBoy own spreadsheet-format correctness. CSV alone does not meet FR-016. A bundled arbitrary global runtime does not define a portable maintainer setup.

**Validation gap**: No writer was exercised during planning. Header-only table interoperability, literal string typing and write-only table headers need focused tests and Excel inspection. Use public `TableColumn` construction rather than private initialization helpers. Upstream documentation supports the proposal, not fulfilled feature behavior.

## Delivery and Validation

**Decision**: Collector in current controller scripts; report in top-level maintainer skills, with existing local source-skill discovery pattern. Collector imports no workbook dependency.

**Rationale**: `tools/catalog.py:controller_package_files` recursively includes scripts and enforces an exact controller inventory. It excludes top-level `skills/`. `controllers/farmboy/manifest.yml` lists ten bindings; `bundles/farmboy/bundle.yml` lists ten active workflows. Present source versions are controller 0.9.1 and bundle 0.18.3; tested CLI pin is `1.0.10.dev0+pegagio.2`. `catalog/release.json` records a snapshot, not a released metrics feature. `skills/farmboy-render-workflow/` and its observed local symlink establish the maintainer pattern. Metrics modules/tests remain proposals.

**Alternatives considered**: An eleventh bundled controller, extension, automatic reporting hook or writer import inside collection. These breach maintainer-only delivery or add unnecessary coupling. Existing unittest/disposable-consumer patterns cover package behavior; real named-agent observation remains separate from stub dispatch proof.

Dependency approval resolves the final Constitution IV planning gate. No technical clarification remains; absent packages and untested workbook/publication/native-order behavior remain explicit implementation validation gaps rather than claims of current feature behavior.

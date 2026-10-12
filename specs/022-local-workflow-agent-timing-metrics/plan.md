# Implementation Plan: Local Workflow Agent Timing Metrics

**Identity**: `specs/022-local-workflow-agent-timing-metrics/`; no Git branch created. **Date**: 2026-10-11. **Spec**: [Current clarified specification](spec.md).

**Input**: The active Feature 022 specification, including all three clarification decisions. The historical `specs/022-workflow-owned-roadmap-boundary/` is a separate record.

## Summary

Add a standard-library metrics helper to the reviewed controller package and timing calls beside the shared protocol's native dispatch and same-child continuation procedures. Each observed working turn produces one immutable JSON file under `~/.farmboy/metrics`; collection failure warns without changing workflow behavior. The maintainer-only `farmboy-metrics-report` source skill consolidates a fixed snapshot into one Excel table, retaining twelve required fields plus optional `model` and `effort`, signed wall-clock milliseconds, distinct turn identities and original inputs.

The operator explicitly approved `openpyxl==3.1.5` and its required `et-xmlfile` dependency on 2026-10-11 for the maintainer-only report design, replying “Yes” to the focused dependency question in this Plan step. The main controller validated and relayed that answer to the same Planner child. This resolves Constitution IV's design approval gate; no dependency was installed and no planning-phase environment change was authorized.

The operator refined the design on 2026-10-12: metrics use a separate correlation ID, recovery-creation changes are removed, and nullable `model` and `effort` describe project agent-file settings. The prior independent review covered the superseded design; fresh independent review remains pending.

## Table of Contents

The sections identify source integration, contracts, delivery boundaries and implementation validation.

- [Technical Context](#technical-context)
- [Constitution Check](#constitution-check)
- [Project Structure](#project-structure)
- [Design and Integration](#design-and-integration)
- [Validation Strategy](#validation-strategy)
- [Risks and Decisions](#risks-and-decisions)
- [Planning Self-Check](#planning-self-check)

## Technical Context

Native agents are launched by the main Codex task, not by a Python subprocess runner. The design extends that existing observation surface.

| Area | Approach |
| --- | --- |
| Language/version | Existing Python 3.11.16, Bash bootstrap, Markdown skills/protocol and YAML manifests. |
| Collection dependencies | Python standard library only; existing PyYAML 6.0.3 remains unchanged. |
| Workbook dependency | Operator-approved openpyxl 3.1.5 and required et-xmlfile, maintainer-only. No pandas, framework or build tool. |
| Storage | One completed JSON object per invocation; uniquely named XLSX files in `reports/`; no shared append file, lock, server or configuration file. |
| Testing | Existing unittest and disposable-consumer patterns; deterministic clocks, actual concurrent publication and live observation. |
| Platform | Supported local Codex consumers; initial observed host is macOS. Hard-link publication must be exercised on each filesystem/platform claimed supported. |
| Project type | Versioned controller package and an independent repository-owned maintainer skill. |
| Performance | No new latency SLA. One small bounded write per emission. Fixed snapshot, grouping and sorting use memory proportional to input; write-only worksheet output avoids retaining all worksheet cells. |
| Bounds | 64 KiB per candidate, 1,000,000 accepted rows, thirteen workbook columns. Zero/negative intervals remain valid; crashes can leave missing records. |
| Environment | Existing project `.venv` passed `mise run python:prepare` and its nested check without changes. Skill-tools lacks openpyxl/et-xmlfile; report readiness must diagnose missing dependencies without installing them. |

## Constitution Check

The pre-research check permits bounded design work. The post-design check repeats each constraint; it does not establish independent review or feature acceptance.

| Gate | Pre-research | Post-design |
| --- | --- | --- |
| I: Merge-bounded artifacts | Pass | Current clarified spec governs; only this feature's planning outputs are authored. Tasks remain separate. |
| II: Human authority | Pass | Main task retains exact native assignment, routing, interactive relay and consequential gates. Metrics add no outcome classification or authority. |
| III: Component boundaries | Pass | Collector belongs to `farmboy-controllers`; report is excluded from consumer manifest/package. No Diagram prerequisite or roadmap/wiki change. |
| IV: Source/manual fallback | Pass for research | Pass: reviewed source/manual boundaries preserved; operator approved the maintainer-only dependency design on 2026-10-11. Packages remain absent and no environment mutation occurred. |
| V: Evidence/provenance | Pass | Disposable consumer/package checks, source hashes, tested CLI and separately labeled live evidence required. No release/adoption claim. |

All five planning constitution gates pass and no exception is proposed. Dependency approval permits this design; it does not authorize environment mutation, implementation, publication or another workflow phase. Independent plan review remains a separate modeled step.

## Project Structure

Source paths identified as new are proposed implementation destinations, not files created by planning.

### Feature Documentation

Planning remains inside the selected feature.

```text
specs/022-local-workflow-agent-timing-metrics/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── metric-record.md
    ├── local-adapter.md
    └── metrics-report.md
```

### Reviewed Source

Reuse current controller packaging and the top-level maintainer-skill pattern.

```text
controllers/farmboy/
├── controller-protocol.md                 # shared native observation boundaries
├── manifest.yml                          # versioned collector delivery
└── scripts/python/
    ├── controller.py                     # transient correlation at inspect
    └── metrics.py                        # new stdlib adapter/schema/helper
skills/farmboy-metrics-report/             # new maintainer source skill
├── SKILL.md
├── agents/openai.yaml
├── requirements.txt                      # approved maintainer dependency design
└── scripts/metrics_report.py              # new consolidation/workbook writer
tests/
├── test_metrics.py                        # new collector contract tests
├── test_metrics_report.py                 # new report/round-trip tests
├── test_controller.py                     # existing helper/protocol integration
├── test_bundle_lifecycle.py               # existing delivery/removal checks
└── test_catalog.py                        # existing package inventory checks
docs/metrics.md                            # new usage/limits guide
docs/installation.md                       # collector versus maintainer setup
docs/architecture.md                       # adapter boundary
```

`tools/catalog.py:controller_package_files` already recursively packages controller scripts and rejects undeclared controller skills. Top-level `skills/farmboy-render-workflow/` and its observed local discovery symlink provide the maintainer pattern. The report receives a documented local `.agents/skills/farmboy-metrics-report` symlink only in FarmBoy; it never enters the controller inventory or bundle workflow list. Consumer-owned files and machine metrics survive removal. Versioned package/catalog snapshots belong to implementation validation; planning changes no manifests, archives, lockfiles or installed copies.

## Design and Integration

The shared protocol supplies one timing rule for all active workflows. Their graph, assignments and gates stay authoritative.

### Capture and Correlation

After normal install/input/graph validation, `controller.py inspect` returns a transient opaque `metrics_run_id` before probes. The main task retains this separate metrics correlation ID across probes, modeled turns and same-child continuations, including any resumption of the same retained controller context. Copy it into each metric record's existing `run_id` field. It is not the recovery summary ID and is never passed to recovery creation. It creates no directory, pending file or workflow summary; probe failure may still leave completed metrics.

Recovery keeps its existing ID generation, summary creation, directory layout and update behavior. This feature changes no recovery-creation API or implementation. Carry the metrics ID with the existing main-task run context; do not add a separate metrics state file, journal or per-run directory.

The metrics helper exposes `begin` and `finish` over JSON stdin/stdout and importable functions for tests. Before a dispatch, finish ordinary setup, then call `begin` with metadata from the validated graph. Hold its start token in main-task context; the next action is the native spawn or same-child continuation. Immediately after observing the turn's final response, question, failure, rejection or interruption, call `finish` first, before routing, review, question presentation or result persistence. It samples the end clock before validation/emission. Pending acknowledgements and polling never call `finish`.

Helper calls are adjacent to native boundaries; process/tool scheduling around those calls contributes small uncorrected local overhead. This is coarse workflow wall time. The helper does not execute an agent and cannot itself prove Codex followed the ordering; live validation must show the observable sequence. If timing fails, still execute the assigned action and preserve its result and gates with a category warning.

Use `execution` for a fresh turn, `continuation` for an answer sent to the same child, `retry` for a separately dispatched retry, and `probe` with `step_id=preflight` for availability checks. Each turn gets a new invocation UUID. Do not infer kind from result prose or reuse a start token across human waiting. Repeated ending observations retain one token/publication path, so collection creates at most one record. A lost token or unobserved ending remains a missing observation.

Use an existing known nonpersonal logical project identity when already available, otherwise `unspecified`. FarmBoy may use `farmboy` from its reviewed logical identity. Do not guess from a basename, home/account or remote URL, and do not add configuration discovery.

### Agent Settings Metadata

Before starting the timer, the main task uses the stdlib helper to read project agent TOML settings by exact `name`. Add optional `model` and `effort` from the file's `model` and `model_reasoning_effort`; missing/unusable/ambiguous settings become null. Use `tomllib`, not a configuration resolver. Do not infer values from shipped defaults or use the read to choose/override native dispatch. These columns describe explicit file settings, not verified runtime values. This limited metrics-only read is separate from Codex's configuration-loading authority.

### Adapter and Publication

The stdlib helper owns clock sampling, validation, serialization and a small default file adapter. Read the local wall clock with `int(time.time() * 1000)`, retain integer milliseconds, render exactly three fractional UTC digits, and subtract the captured millisecond values without correction. No nanosecond precision is required. No monotonic or CPU clock is used.

Write to an exclusively created hidden temporary file inside the metrics directory, close it, then publish with `os.link(temp, final)` to `metric-<invocation-uuid>.json`. A link must fail when the final name exists; no overwrite-capable replace or check-then-write path. Both names are on the same filesystem. Remove only the writer-owned temporary name afterward. Unsupported linking, permission/full-disk failures and collisions warn and continue; there is no unsafe fallback. This guarantees completed visibility without shared-file locks on tested filesystems, not power-loss durability.

Discover direct regular completed files only; ignore symlinks, directories, temporary names and `reports/`. Copies may have another syntactically valid filename UUID, so payload invocation identity drives deduplication. See [adapter](contracts/local-adapter.md) and [record](contracts/metric-record.md) contracts.

### Consolidation and Workbook

The explicit maintainer skill checks FarmBoy's reviewed source layout and invokes its source report script with the prescribed skill-tools interpreter. It loads the canonical validator from reviewed controller source, not an installed consumer copy; it does not bootstrap another workflow. Missing dependencies fail before output creation and never trigger installation.

Discover once and retain the candidate list; open each file once without following symlinks and read at most 65,536 bytes. Reject oversized files using metadata and bounded reads. Categorize invalid candidates, then project the twelve required fields plus nullable `model` and `effort`; normalize absent settings to null and ignore other extras for equality and columns. Group by invocation identity: equivalent fourteen-field values collapse, while any differing valid values exclude the entire identity. Do not select an authoritative copy. [The report contract](contracts/metrics-report.md) defines non-overlapping counts.

Sort accepted rows by `started_at`, then `invocation_id`, enforce the accepted-row cap, and write one worksheet `Metrics` and table `FarmBoyMetrics`. Apply the report contract's header mapping: `step_id` → `step`, `agent_name` → `agent`, `skill_id` → `skill`, `workflow_id` → `workflow`, and `project_label` → `project`; retain the JSON keys and use the report contract’s independent Excel column order. The approved openpyxl design uses write-only mode, public `TableColumn` headers matching cells and `WriteOnlyCell` explicit string types. Omit `schema_version` from Excel while retaining it in record validation and duplicate comparison. `duration_ms` is numeric; non-null other columns stay literal strings, including formula/error-like text; null settings become blank cells. For zero rows, create a header-only table range without a fabricated data row; test Excel interoperability before claiming fulfillment.

Write a uniquely staged XLSX under `reports/`, close the workbook, then publish without clobbering to `farmboy-metrics-<report-uuid>.xlsx` using the same link primitive. Errors fail visibly, leaving records and prior reports intact. Counts belong in skill output; the workbook contains one simple table, no charts, analysis or extra sheets. In-memory snapshot/group/sort storage remains proportional to inputs despite write-only cell emission.

## Validation Strategy

[Quickstart](quickstart.md) specifies future commands and expected observations; proposed implementation tests have not run during planning.

| Requirements | Evidence required |
| --- | --- |
| FR-001–005, FR-010 | Controlled probe/execution/question/continuation/retry/rejection/interruption sequence; zero/backward clock; pending polling; unique IDs, exact metadata and signed arithmetic, no outcome or substitute classification, excluded human wait. |
| FR-006–009, SC-002–003 | Adapter contracts and at least twenty simultaneous real writers across two labels; collision/clock/metadata/permission/storage failures; complete files, safe warnings and unchanged result/routing/gates. |
| FR-022, SC-008 | Exact agent-name matching despite different filenames; explicit values, one missing setting, missing/unreadable/malformed/ambiguous configuration, absent optional keys and null workbook cells. Metadata read occurs before timing; native dispatch and collection continue independently. No global configuration or settings inheritance is resolved. |
| FR-011 | Metadata allowlist and portable project labels; no prompts, transcripts, personal account/name, absolute host path or token/cost data in records/diagnostics. |
| FR-012, FR-021, SC-007 | Disposable supported install/refresh/removal delivers the helper but no report skill or writer dependency; preserves records; ten-controller graph/assignment inventory and manual path remain usable. Probe and modeled-turn records share the retained metrics correlation ID, independently of the existing recovery summary ID. Failed preflight creates no workflow run state, and metrics do not change recovery creation or existing history. |
| FR-013–015, FR-018–019 | Mixed snapshot, once-only bounded reads, late arrivals, missing/inaccessible directory, extras, malformed/oversized inputs, duplicates/conflicts; unchanged source hashes. Exercise 1,000,001 accepted identities via injected writer seam without a million physical files. |
| FR-016–017, SC-005–006 | XLSX relationships/table/XML and cell types, repeat outputs, failure/collision and zero-row table. Open normal and empty workbooks in Excel; sorting/filtering and numeric arithmetic work without repair. |
| FR-020, Constitution V | Exact component IDs/versions, tested CLI and source digests; distinguish fixture dispatch from live evidence and report unsupported cases. |

Controlled stubs prove topology only. Separately observe a real exact-named-agent execution and same-child question/continuation in FarmBoy and a disposable consumer; no publication/adoption follows. Existing relevant validation remains required.

## Risks and Decisions

Local clock skew/drift and missing records after crashes are accepted. Helper scheduling is uncorrected overhead. Protocol instructions can be skipped by a controller, so live ordering remains a material implementation validation requirement.

Hard links must work on the tested local filesystem; unsupported operation warns for collection and fails reporting. Interrupted writers may leave ignored temporary names, with no retention/cleanup automation. Large snapshots can exhaust memory before the row cap; failure cannot publish a partial workbook. Do not introduce an external sorter/database for hypothetical scale.

Header-only table interoperability needs Excel verification; do not silently add a blank observation or narrow the specification if it fails. The maintainer-only dependency decision is resolved by the operator's approval. A hand-written OOXML exporter would give FarmBoy disproportionate spreadsheet maintenance; CSV alone contradicts the approved round trip. No unresolved operator design decision remains; runtime and interoperability evidence are implementation validation obligations.

## Planning Self-Check

Author checks support independent review; the planner cannot approve its own plan.

- [x] Current spec and all clarification decisions used; historical byte-bound packets not treated as current approval.
- [x] Concrete current source/package integration and maintainer boundary identified.
- [x] FR-001–022 and SC-001–008 addressed; no outcome/token dimension, config framework, lock or extra workflow.
- [x] Research, data model, contracts and validation guide produced; no code/tasks/specification edits.
- [x] Hooks parsed: no before-plan hooks; optional after-plan wiki ingestion remains operator-selected.
- [x] Constitution IV dependency design approved explicitly by the operator; final planning gate passes without installation.
- [ ] Independent review completed by another assigned agent; outside this child's role.

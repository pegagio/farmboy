# Feature Specification: Local Workflow Agent Timing Metrics

**Feature Branch**: No branch created; identity is the selected specification directory.

**Created**: 2026-10-11

**Status**: Complete

**Input**: Direct operator decisions request basic machine-local wall-clock timing around FarmBoy agent invocations, concurrent collection as separate files under `~/.farmboy/metrics`, warnings with continued workflow execution on collection failure, and the maintainer-only FarmBoy Metrics Report skill (`farmboy-metrics-report`) consolidating records into one simple XLSX table while preserving the source records.

Feature 022 belongs exclusively to `specs/022-local-workflow-agent-timing-metrics/`. The historical `specs/022-workflow-owned-roadmap-boundary/` is a different feature record and is not this feature's target.

## Table of Contents

This specification separates operator-approved scope from routine defaults selected for the initial version.

- [Clarifications](#clarifications)
- [User Scenarios & Testing](#user-scenarios--testing-mandatory)
- [Requirements](#requirements-mandatory)
- [Success Criteria](#success-criteria-mandatory)
- [Assumptions](#assumptions)
- [Provenance and Governing Constraints](#provenance-and-governing-constraints)

## Clarifications

The following answers record operator decisions made during the bounded clarification session.

### Session 2026-10-11

- Q: When an agent returns a question and later resumes after your answer, should timing record each working turn separately and exclude the time waiting for you? → A: Record separate working turns and exclude human wait; the question-producing turn and each continuation have distinct records.
- Q: Which metadata should the first version require in every timing record? → A: A, but remove outcome. That’s hard to classify. Require the draft correlation fields except outcome; defer workflow/component versions, attempt number and model.
- Q: Should FarmBoy Metrics Report export the usable records when some input files are invalid or contain conflicting copies of the same invocation? → A: Export valid records; skip invalid files and exclude every conflicting copy of an invocation with visible counts. Identical copies become one row, and all source files are preserved.

**Follow-up decision (2026-10-12)**: Add optional `model` and `effort` values read from the matching project agent TOML file. The names have no `configured_` prefix, but represent file-declared settings rather than verified runtime settings. This supersedes the earlier model deferral; unavailable settings remain `null`.

## User Scenarios & Testing *(mandatory)*

The primary user is an operator running FarmBoy workflows in FarmBoy or a consuming project. The workbook user is a maintainer explicitly invoking FarmBoy Metrics Report within FarmBoy.

### User Story 1 - Measure agent work locally (Priority: P1)

As a workflow operator, I want each agent invocation to produce a small timing record so I can compare elapsed time and count invocations across agents, workflows and projects without collecting prompts or introducing a metrics service.

**Why this priority**: Reliable collection supplies the observations needed for every later comparison and report.

**Independent Test**: Run a representative delegated step, a continuation, a retry and an availability probe with controlled local-clock observations. Inspect the resulting separate records and compare their identity, boundaries, kinds and elapsed values to the observations.

**Acceptance Scenarios**:

1. **Given** a workflow dispatches its assigned agent, **When** that invocation returns a final response, **Then** one complete record identifies the exact assigned agent and invoking skill/workflow and measures the interval from immediately before dispatch to observation of that response.
2. **Given** an agent returns a question, **When** the operator later answers and the controller continues the same child, **Then** the question-producing turn and continuation have distinct invocation IDs within the same run and step, and the interval awaiting the human answer belongs to neither duration.
3. **Given** a new dispatch retries a failed step or probes agent availability, **When** it finishes, **Then** it has its own record and an explicit retry or probe kind so those counts can be distinguished from ordinary execution.
4. **Given** dispatch fails or a running invocation returns an observed failure or interruption, **When** control returns to the controller, **Then** a timing record captures the observed interval without classifying the result or implying successful task completion.
5. **Given** the local clock moves backward during an observed invocation, **When** its record is emitted, **Then** the signed elapsed value and both timestamps retain the observed discrepancy without clamping or clock correction.

### User Story 2 - Collect concurrently without changing workflow results (Priority: P1)

As an operator using several workflows or projects at once, I want observations to coexist in the shared local directory without collisions or locking, and I want collection problems to remain visible without blocking my work.

**Why this priority**: Collection is useful only if it preserves existing workflow behavior and supports concurrent invocations.

**Independent Test**: Complete multiple concurrent invocations across two project identities while another process reads records; also exercise an unwritable destination and an emission failure. Compare records and original workflow outcomes.

**Acceptance Scenarios**:

1. **Given** two consuming projects finish invocations concurrently, **When** they emit records, **Then** each record has a distinct filename and invocation identity, no record is overwritten, and no shared-file append or file lock is required.
2. **Given** emission is still in progress, **When** a report discovers its inputs, **Then** unfinished content is not accepted as a completed metric and the writer does not need to wait for the report.
3. **Given** collection cannot create or write its destination, **When** an agent invocation finishes, **Then** the operator sees a concise warning and the workflow retains its original result, assignments and gates.
4. **Given** the agent or controller stops abruptly before the end can be observed, **When** a later report runs, **Then** it does not fabricate a finish time, duration or recovered completion record.

### User Story 3 - Consolidate observations for Excel (Priority: P1)

As a FarmBoy maintainer, I want to explicitly run FarmBoy Metrics Report and receive one workbook containing a simple table of all valid records in the report's input snapshot, so I can sort, filter and build my own graphs in Excel.

**Why this priority**: The approved first feature includes the full collection-to-workbook round trip rather than requiring a future exporter.

**Independent Test**: Supply valid records from multiple projects, malformed and incomplete files, a duplicate record and a file completed after discovery. Invoke the maintainer skill and inspect table rows, warnings, destination and unchanged input bytes. The report can be tested with prepared records independently of live collection.

**Acceptance Scenarios**:

1. **Given** completed valid records from multiple projects, **When** the maintainer invokes `farmboy-metrics-report` within FarmBoy, **Then** one XLSX workbook contains one table row per distinct accepted invocation with its timing and identity fields and no charts or analysis.
2. **Given** malformed, unsupported, oversized or duplicate candidates alongside valid records, **When** reporting completes, **Then** valid distinct records appear once, skipped categories and counts are reported, and the original files remain intact.
3. **Given** collection continues during reporting, **When** new records become discoverable after the input snapshot, **Then** they are left for the next explicit report without extending or restarting the current report.
4. **Given** no valid records are available or the input directory does not yet exist, **When** the skill runs, **Then** it produces a workbook containing the table's column headers and reports zero accepted records.
5. **Given** an output file already exists or the report cannot write its output, **When** reporting is attempted, **Then** the existing file is not overwritten; a unique default name is used or the report fails visibly with all source records preserved.
6. **Given** a consumer receives FarmBoy timing support through a supported installation, **When** installed skills are inspected, **Then** FarmBoy Metrics Report is excluded from that consumer delivery.

### Edge Cases

The initial version must make the following limits and exceptional results inspectable:

- **Unobserved end**: A controller crash, lost child connection or abrupt termination can leave no completed record. Reporting cannot reconstruct the missing observation or promise complete historical accounting.
- **Pending execution**: Asynchronous dispatch acknowledgement and polling are not invocation completion. Time while the child is still working remains inside its interval.
- **Human wait**: A question ends the current measured turn; answering it creates a new measured continuation. Controller preparation, human gates and waiting after a returned question are excluded.
- **Clock anomalies**: Equal timestamps yield zero duration; backward movement can yield negative duration. These are accepted local-clock measurements, not corrected estimates of physical elapsed time.
- **Unrelated input**: Temporary files, subdirectories, prior workbooks and files outside the completed-record convention are ignored without recursion.
- **Invalid input**: Unreadable or malformed completed candidates receive one bounded validation attempt and are skipped with a category count. No automatic repair, rescanning, waiting for writers or raw-content warning is required.
- **Duplicate identity**: Repeated copies of the same invocation do not become repeated workbook rows. Conflicting copies are diagnosed rather than silently selected as authoritative.
- **Report capacity**: An input snapshot exceeding the one-table capacity fails clearly before publishing a misleading partial workbook; sources remain intact.
- **Spreadsheet interpretation**: Text dimensions are retained as text, including values that resemble formulas; duration remains numeric so the operator can calculate and chart it.

## Requirements *(mandatory)*

The requirements below preserve the operator-approved simplicity, delivery and authority boundaries. Defaults for unsettled details are identified in Assumptions.

### Functional Requirements

- **FR-001**: All active FarmBoy workflows MUST measure controller-issued agent invocations in FarmBoy and consuming projects through the supported workflow execution path, including availability probes, execution turns, same-child continuations and separately dispatched retries. Main-task steps without an agent invocation MUST NOT generate agent timing records.
- **FR-002**: Measurement MUST start immediately before the invocation or continuation request and end immediately after the controller observes that turn's final response, question, failure, interruption or dispatch rejection. Pending acknowledgements and polling MUST NOT end the interval. Record persistence time and human-answer waiting between turns MUST be excluded.
- **FR-003**: Each measured turn or rejected dispatch attempt MUST have a unique invocation identity and at most one completed metric record. A continuation or retry MUST receive a new invocation identity while retaining applicable workflow run and step identities; counts represent invocation records, not unique children or accepted tasks.
- **FR-004**: Records MUST NOT classify invocation outcomes or add a replacement status/success field. A timing record MUST NOT imply task success, feature acceptance, successful independent review or roadmap verification. An interval MUST be recorded only when its ending boundary is observed; no ending observation MUST mean no invented completion metric. Workflow results remain independent of metrics.
- **FR-005**: Duration MUST be a signed numeric value in milliseconds derived from the two observations of the local wall clock. Timestamps MUST represent those observations as UTC date-time strings with millisecond precision and a `Z` suffix. Zero and negative intervals MUST remain representable; monotonic timing, skew correction and clock synchronization are out of scope.
- **FR-006**: Collection MUST use a small local metrics adapter boundary so workflows submit an observation independently of its storage destination. This does not require a network API, daemon, metrics server or generalized collector framework.
- **FR-007**: The first adapter MUST write one self-contained structured record per uniquely named emission file under `~/.farmboy/metrics`, shared across projects on that computer. The initial specification default is one JSON object per file; shared-file appends and file locking MUST NOT be used.
- **FR-008**: Concurrent writers MUST neither replace another invocation's record nor expose unfinished content as a completed record. Completed records MUST be immutable from the collector's perspective. The completed-record discovery convention MUST distinguish published records from unfinished and unrelated files; exact naming and publication mechanics remain planning choices.
- **FR-009**: Collection failures, including unavailable timing or metadata and destination, collision or storage failures, MUST warn and continue without replacing an agent's result, changing its assignment, masking its failure, bypassing a human gate or invoking another phase. Warnings MUST identify the failure category without revealing record contents or absolute host paths.
- **FR-010**: Each valid record MUST contain the minimal dimensions in the record contract below. `agent_name` MUST be the exact dispatch name; `skill_id` and `workflow_id` MUST be the invoking FarmBoy identities. Names MUST NOT be guessed from a model, child title or returned prose. Probe records without a modeled workflow step MUST use a documented `step_id` value of `preflight`.
- **FR-011**: Records MUST exclude prompts, transcripts, secrets, personal details, absolute host paths, token accounting and monetary cost. A portable nonpersonal project label MUST use an existing known logical project identity when available and otherwise `unspecified`; it MUST NOT be derived from a user's home path or account name.
- **FR-012**: FarmBoy Metrics Report (`farmboy-metrics-report`) MUST be a maintainer-only skill explicitly invoked within FarmBoy. Consumer installation MUST deliver the approved timing/emission support and MUST exclude this reporting skill. It MUST NOT be scheduled or automatically invoked at workflow completion.
- **FR-013**: Reporting MUST discover the completed-record candidates directly in the default metrics directory once at report start. This fixed candidate snapshot MUST exclude unfinished files, subdirectories and later arrivals; reporting MUST NOT wait for emission or continuously rescan.
- **FR-014**: Reporting MUST validate each candidate once, reading at most 64 KiB per record, and skip unreadable, oversized, malformed or unsupported-schema candidates with visible category counts. It MUST validate required fields, field types, invocation-kind values and the duration's consistency with its timestamps to the documented millisecond precision. Unknown extra fields MUST NOT invalidate an otherwise supported record and MUST NOT become automatic workbook columns.
- **FR-015**: Reporting MUST group valid candidates by `invocation_id`. Identical metric values MUST produce one row and a duplicate count; conflicting valid values for one invocation identity MUST exclude that identity entirely and report a conflict count. Invalid candidates and conflicts MUST NOT block export of the remaining accepted records. No report-side repair or authority inference is allowed.
- **FR-016**: Reporting MUST produce one XLSX workbook with one simple table, thirteen columns in this order: `invocation_id`, `run_id`, `project`, `skill`, `workflow`, `step`, `invocation_kind`, `agent`, `model`, `effort`, `started_at`, `finished_at`, `duration_ms`, and one row per accepted distinct invocation. The shortened headers map to their documented JSON fields; `schema_version` MUST remain in JSON records and validation but MUST NOT be exported as a workbook column. Rows MUST be ordered by `started_at`, then `invocation_id`. Text MUST remain literal text; `duration_ms` MUST remain numeric. Graphs, dashboards, automatic interpretation and CSV export are excluded from the initial scope.
- **FR-017**: The default output MUST be a uniquely named workbook under `~/.farmboy/metrics/reports/`. Repeated reports MUST create distinct outputs without overwriting existing files, and success MUST expose the output location to the operator. An output failure MUST be a visible report failure and MUST NOT be described as a successful export.
- **FR-018**: Missing or empty input and snapshots containing no accepted records MUST produce a workbook with the same column headers and zero data rows. Reporting MUST summarize candidate, accepted, skipped and duplicate/conflict counts. An inaccessible existing input directory MUST instead fail visibly, because it does not establish that zero records exist.
- **FR-019**: Reporting MUST preserve every source record and unfinished file byte-for-byte, including files it rejects. A snapshot exceeding 1,000,000 accepted rows MUST fail with a capacity message instead of truncating data or creating extra workbooks. Source deletion, retention automation and historical recovery are excluded.
- **FR-020**: Concise documentation MUST explain invocation boundaries and count meaning, clock limitations, record schema and units, default collection/output locations, concurrency/completed-record behavior, warnings, report invocation, skipped inputs and source preservation. It MUST state that reporting is maintainer-only and distinguish tested local behavior from publication or consumer adoption.
- **FR-021**: Changes MUST preserve exact named-agent assignments, installed workflow ownership, manual-prompt fallback, boundary checks, human decisions and separately invoked phases. Manual execution MUST document how timing applies where the supported controller observes invocations and MUST NOT claim automatically measured or retrospectively recoverable timings for hand-run agents outside that path.

- **FR-022**: Metrics MAY include `model` and `effort` read from `.codex/agents/*.toml` by matching the exact agent `name`, independently of filenames. `model` maps to the file's `model`; `effort` maps to `model_reasoning_effort`. Missing, unreadable, malformed or ambiguous configuration, or an absent/invalid value, MUST yield `null` for unavailable settings without blocking timing collection. These fields describe explicit file settings, MUST NOT imply verified runtime values, and MUST NOT change native dispatch or resolve inherited/global defaults. Reporter MUST accept absent fields as `null` and show them as blank cells.

### Key Entities *(include if feature involves data)*

The entities describe observable information rather than an implementation architecture.

- **Invocation**: One controller-issued execution, continuation, retry or availability-probe turn, including a rejected dispatch attempt. It belongs to a workflow run and may belong to a modeled step and an existing child.
- **Metric record**: One immutable completed observation with an invocation identity, exact agent and invoking identities, a project label, start/end clock readings and signed duration, without result classification.
- **Report snapshot**: The fixed set of completed-record candidates discovered at the start of one explicit report. It does not assert that every past invocation emitted successfully.
- **Metrics workbook**: One preserved XLSX output containing the simple table of valid distinct records accepted from that snapshot.

The first record contract retains twelve required dimensions and adds two optional nullable fields, `model` and `effort`. Both optional fields are included as workbook columns.

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer `1`, identifying this initial contract. |
| `invocation_id` | Unique opaque identity for the measured turn or dispatch attempt. |
| `run_id` | Opaque identity shared by invocations in one explicit workflow run, including its preflight. |
| `step_id` | Exact modeled step ID, or `preflight` for availability probes before modeled steps. |
| `invocation_kind` | One of `execution`, `continuation`, `retry` or `probe`; a separately dispatched retry uses `retry`. |
| `agent_name` | Exact name supplied for dispatch, such as `FarmBoy Coder`. |
| `skill_id` | Invoking FarmBoy skill ID, such as `farmboy-implement`. |
| `workflow_id` | Invoking installed FarmBoy workflow ID. |
| `project_label` | Existing known nonpersonal logical project identity, otherwise `unspecified`; a grouping label, not a unique repository identifier. |
| `started_at` | Observed local-wall-clock start, rendered in UTC with millisecond precision. |
| `finished_at` | Observed local-wall-clock end, rendered in UTC with millisecond precision. |
| `duration_ms` | Signed elapsed milliseconds, calculated at the same precision as the timestamp pair. |
| `model` | Optional string or `null`; the matching project agent file's `model` value, not runtime verification. |
| `effort` | Optional string or `null`; that file's `model_reasoning_effort` value, not runtime verification. |

Workflow/component version, attempt number, token counts and raw child identifiers are not required first-version dimensions. `model` and `effort` are optional; absent values normalize to `null`. Outcome classification is excluded. Distinct invocation records support counts; kinds support filtering without inferring results unavailable to the controller.

## Success Criteria *(mandatory)*

The outcomes can be verified by inspecting observations, files, workbook contents and workflow behavior without assuming any implementation technology.

### Measurable Outcomes

- **SC-001**: In a controlled sequence covering execution, a question and continuation, a retry, a probe, a failed dispatch and an observed interruption, 100% of turns with available start/end observations and successful collection produce exactly one identifiable record with the correct boundaries and kind, without outcome or substitute result-classification fields; no measured interval includes the intervening human-answer wait.
- **SC-002**: A focused round trip with at least 20 simultaneous successful emissions across two project labels preserves all 20 distinct completed records and produces exactly 20 matching table rows with no overwritten record, accepted partial record or shared-file locking.
- **SC-003**: Every tested collection failure produces a visible category warning while leaving the observed agent result, workflow route, exact assignment and applicable human gate unchanged.
- **SC-004**: For a fixed mixed input snapshot, every valid distinct invocation appears once in the output table; every invalid or conflicting candidate is accounted for in the report summary; records completed after discovery are excluded until a subsequent report.
- **SC-005**: After repeated reports, 100% of source files retain their original bytes, prior output files remain intact, and each successful report has a distinct output. Empty valid input produces zero data rows with the documented columns.
- **SC-006**: The operator can open the output in Excel, sort/filter agent and workflow identities and calculate from numeric durations without repairing headers, cell types or formula interpretation; creating graphs remains the operator's choice.
- **SC-007**: A supported consumer installation exposes timing/emission capability without installing FarmBoy Metrics Report, while the maintainer can explicitly run that skill within FarmBoy. Neither a timing failure nor report completion initiates another workflow or acceptance action.

- **SC-008**: With valid explicit settings, emitted `model` and `effort` match the exact named project agent file; with missing or unusable settings, timing still emits with nullable settings. Supported records without these optional keys remain reportable, and the XLSX table contains both settings columns with blank cells for unknown values.

## Assumptions

These are routine defaults selected for this draft, except where explicitly identified as confirmed clarification decisions. They make the approved simple scope testable and remain reviewable within this feature.

- **Intermediate format**: One JSON object per file is selected for readable, independently consumable records. The operator authorized a simple intermediate format rather than mandating JSON; this selection adds no JSONL stream or CSV collector.
- **Timing grain (confirmed clarification)**: A controller-issued turn is the unit of measurement. Questions end a turn; same-child answers start another record, excluding human-answer waiting. Polling while a turn runs is included, controller work between turns is excluded, and unobserved endings remain missing observations.
- **Probe coverage**: Availability probes are agent invocations and are measured with kind `probe`; this does not implement Feature 016 or alter when probing occurs. Run correlation exists before preflight even when preflight stops before durable workflow state is created.
- **Record dimensions (confirmed clarification)**: Schema version, invocation/run/step IDs, kind, exact agent/skill/workflow IDs, portable project label, timestamps and signed millisecond duration are required. Outcome classification is excluded; version/attempt metadata remains deferred. Optional `model` and `effort` describe explicit project agent-file settings and remain `null` when unavailable; no inheritance resolver is required. A missing safe project identity uses `unspecified` rather than prompting for a new configuration system.
- **Report behavior**: The default output is a new uniquely named file in the metrics directory's `reports/` subdirectory. A single input discovery, one validation attempt per candidate, a 64 KiB record ceiling and a 1,000,000-row report ceiling provide bounded handling without locks, rescans, splitting or silent truncation.
- **Rejected inputs and duplicates (confirmed clarification)**: Invalid inputs are skipped and conflicting copies exclude that invocation, with visible category counts; usable records still export. Identical copies collapse to one row. All sources remain intact. This protects count meaning without claiming which conflicting observation is authoritative.
- **Delivery boundary**: Consumer capability follows the project's existing supported installation path; selecting this feature does not refresh existing consumers or publish a release. The report skill remains within FarmBoy and does not require a new FarmBoy workflow or authority model.
- **No scale or completeness guarantee**: This feature measures local time as the only cost and derives counts from available records. It does not guarantee records across abrupt crashes, failed writes or agents executed outside the observed path. No token, monetary, CPU or distributed timing is introduced.

## Provenance and Governing Constraints

Feature-specific authority comes from the direct operator decisions on 2026-10-11 and the current [Feature 022 roadmap entry](../../.specify/memory/roadmap.md#022--local-workflow-agent-timing-metrics--status-planned), not from inferred wiki coverage.

- **Dependencies**: Roadmap Features 013, 014 and 021 are recorded as verified delivery prerequisites. Feature 016 is separate and is not a dependency. Existing verification qualifications remain intact; these statuses do not prove new metrics behavior, publication or adoption.
- **C-01 — Merge-bounded persistence**: This feature's future accepted discoveries must flow through its own reviewable artifacts; historical feature specifications retain their meaning.
- **C-02 — Human-directed authority**: Timing and reporting preserve exact assignments, human gates and separately invoked phases. Successful collection or export grants no roadmap verification, acceptance or Git authority.
- **C-03 — Generic component boundaries**: Generic source owns emission behavior; consumers collect local evidence. The report skill is maintainer-only. The Diagram remains a consumer and is not a prerequisite.
- **C-04 — Reviewable source and fallback**: Implementation must target reviewed source, preserve manual fallback and separate planning/tasking. No dependency or build-tool adoption is approved by this specification; any newly required dependency needs documented need and explicit approval.
- **C-05 — Bounded validation and feedback**: Validation must distinguish fixture dispatch from live-agent observations and record tested source/component provenance without claiming release or adoption. Metrics are local observations, not governance decisions.

The [Constitution 8.0.0](../../.specify/memory/constitution.md) governs these boundaries. Supporting wiki context is partial: [Project authority and review gates](../../wiki/pages/project-authority-and-review-gates.md) cites S035 for generic ownership and operator authority; [Codex workflow controller design](../../wiki/pages/codex-workflow-controllers.md) cites S033 for exact dispatch, installed definition ownership and boundary checks; [Installation and release lifecycle](../../wiki/pages/installation-and-release-lifecycle.md) cites S002, S005, S016, S025, S032 and S034 for owned-file protection and the distinction between installation, publication and adoption. These IDs are registered in [wiki/sources.md](../../wiki/sources.md). Those pages establish governing context, not current metrics implementation or fulfilled Feature 022 prerequisites.

Initial exclusions remain token/monetary accounting, CPU/distributed timing or clock correction, remote ingestion, hosted services, metrics servers, charts, dashboards, automatic analysis or reporting, consumer report-skill installation, source deletion, locking, a generalized telemetry framework, an initial configuration-file system, unrelated workflow changes, migration, publication, Git integration and feature acceptance. The exact adapter call shape, filename mechanics, completed-file publication mechanism and workbook-writing approach belong to later planning within these requirements.

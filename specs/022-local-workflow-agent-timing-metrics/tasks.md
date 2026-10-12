---
description: "Dependency-ordered implementation tasks for local workflow agent timing metrics"
---

# Tasks: Local Workflow Agent Timing Metrics

**Input**: Design documents from `specs/022-local-workflow-agent-timing-metrics/`

**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, and `quickstart.md`

**Organization**: Tasks are grouped by the three P1 user stories. Each story has its own completion criteria; the report story consumes the shared record contract and can be developed independently of invocation wrapping after the foundation is ready.

## Phase 1: Setup

**Purpose**: Establish the maintainer-only report source package and its approved dependency declaration.

- [ ] T001 Create the FarmBoy-only maintainer report source scaffold and declare `openpyxl==3.1.5` plus required `et-xmlfile` in `skills/farmboy-metrics-report/SKILL.md`, `skills/farmboy-metrics-report/agents/openai.yaml`, and `skills/farmboy-metrics-report/requirements.txt`; create and document the local `.agents/skills/farmboy-metrics-report` discovery symlink in `docs/installation.md`; keep the source and dependency outside consumer controller and bundle inventories.

## Phase 2: Foundational

**Purpose**: Define the shared record and run-correlation primitives needed by collection and reporting.

- [ ] T005 [P] Add foundational record-contract tests in `tests/test_metrics.py` before implementing the helper: cover all twelve required fields (`schema_version` exactly `1` and booleans are not integers; nonempty opaque `invocation_id` and `run_id`; exact modeled `step_id`; exact `agent_name`, `skill_id`, `workflow_id`, and nonpersonal `project_label`; `started_at` and `finished_at` exactly `YYYY-MM-DDTHH:MM:SS.mmmZ`; signed integer `duration_ms`) and optional nullable `model` and `effort` (absent normalizes to null; present values are null or nonempty strings); cover `invocation_kind` exactly `execution`, `continuation`, `retry`, or `probe`; reject missing/empty strings, booleans or fractions in integer fields, duplicate JSON keys, nonfinite numeric constants, impossible timestamps, unsupported schema/kind, and mismatched duration arithmetic; verify equal/backward clock readings and the 65,536-byte JSON, 32,767-character and legal-XML-text limits without trimming or truncation against `specs/022-local-workflow-agent-timing-metrics/data-model.md` and `contracts/metric-record.md`.
- [ ] T002 Implement importable begin/finish helpers and the version-1 record contract with all twelve required fields at their exact types in `controllers/farmboy/scripts/python/metrics.py`, preserving these field constraints from `specs/022-local-workflow-agent-timing-metrics/data-model.md`: `schema_version` “Exactly `1`; booleans are not integers for validation.”; `invocation_id` “Nonempty opaque turn identity; collector produces UUIDs, report does not reinterpret it as a child ID.”; `run_id` “Nonempty opaque metrics correlation identity for one workflow invocation, retained across probes and modeled turns; independent of recovery identity.”; `step_id` “Exact modeled ID; `preflight` for probes.”; `invocation_kind` “`execution`, `continuation`, `retry`, `probe`.”; `agent_name` “Exact supplied native dispatch name.”; `skill_id` “Exact invoking FarmBoy skill ID.”; `workflow_id` “Exact invoking installed FarmBoy workflow ID.”; `project_label` “Known nonpersonal logical identity or `unspecified`; grouping label, not repository identity.”; `started_at` and `finished_at` “Valid UTC timestamp `YYYY-MM-DDTHH:MM:SS.mmmZ`.”; `duration_ms` “Signed difference of timestamp epoch milliseconds; reject booleans, fractions and mismatched arithmetic.”; `model` “Explicit `model` in the uniquely matching project agent TOML file; optional, absent normalizes to null.”; and `effort` “Explicit `model_reasoning_effort` in that file; optional, absent normalizes to null.” Also implement millisecond wall-clock sampling, invocation UUID creation, UTC timestamp formatting, JSON stdin/stdout interface, serialization, and public validation helpers; require a UTF-8 JSON object no larger than 65,536 bytes with no duplicate keys or nonfinite numeric constants, and reject projected strings over 32,767 characters or containing illegal XML characters without trimming or truncation (depends on T005).
- [ ] T003 [P] Add a transient metrics correlation UUID to the validated inspect result in `controllers/farmboy/scripts/python/controller.py`; keep it separate from recovery identity and leave recovery creation, summaries, and directories unchanged (depends on T002).
- [ ] T004 [P] Verify `controllers/farmboy/scripts/python/metrics.py` is automatically included at its installed path through `controller_package_files`; cover consumer delivery and exclusion of `skills/farmboy-metrics-report/` in `tests/test_catalog.py` and `tests/test_bundle_lifecycle.py`, preserving the ten controller bindings (depends on T002).

**Checkpoint**: Shared schema and correlation primitives are stable; user-story work can proceed.

## Phase 3: User Story 1 - Measure agent work locally (Priority: P1)

**Goal**: Emit one record for each observed probe, execution, continuation, retry, or rejected dispatch attempt, using the workflow's metrics `run_id` and a unique `invocation_id` per timed turn.

**Independent Test**: Drive controlled probe, execution, question-producing turn, same-child continuation, retry, dispatch rejection, and observed interruption boundaries. Confirm unique invocation IDs, shared run ID within a workflow, exact invoking identities, millisecond timestamps and duration, and no record when the end is unobserved.

### Implementation for User Story 1

### Tests for User Story 1

- [ ] T009 [US1] Write controller and metrics behavior tests in `tests/test_controller.py` and `tests/test_metrics.py` before implementation; cover probe/execution/continuation/retry boundaries, question/answer timing, pending polls, correlation, exact TOML name matching and unavailable/ambiguous settings, dispatch rejection, and failure or missing-end behavior (depends on T005).

### Implementation for User Story 1

- [ ] T006 [P] [US1] Add shared protocol instructions for creating a fresh turn token immediately before native dispatch or continuation, retaining it through pending acknowledgements and polls, and finishing it immediately after the observed turn boundary in `controllers/farmboy/controller-protocol.md` (depends on T009).
- [ ] T007 [P] [US1] Read optional `model` and `effort` from project `.codex/agents/*.toml` by exact `name` before timing starts, map `model` and `model_reasoning_effort`, and return null for unavailable or ambiguous settings in `controllers/farmboy/scripts/python/metrics.py` (depends on T002 and T009).
- [ ] T008 [US1] Specify probe `step_id=preflight`, exact `execution`/`continuation`/`retry` kinds, metrics run-ID retention across a workflow, known nonpersonal `project_label` fallback to `unspecified`, and the metadata allowlist in `controllers/farmboy/controller-protocol.md`; narrow its blanket TOML prohibition only to permit the passive metrics read of explicit `model` and `model_reasoning_effort` from the exact-name project agent file before timing, while preserving native dispatch/configuration authority, no spawn overrides, no inheritance or global resolution, and no claim of runtime verification; exclude prompts, transcripts, secrets, host paths, tokens, and human-answer waiting (depends on T006 and T009).

## Phase 4: User Story 2 - Collect concurrently without changing workflow results (Priority: P1)

**Goal**: Publish independent completed records without shared-file locking or collisions, and warn while preserving the original workflow result if collection fails.

**Independent Test**: Run at least twenty concurrent writers into one temporary metrics directory across two project labels while reading records. Inject collision, unsupported hard-link, permission, and storage failures; confirm complete non-overwritten files, concise category warnings, and unchanged dispatch results and gates.

### Implementation for User Story 2

### Tests for User Story 2

- [ ] T012 [US2] Write adapter and controller behavior tests in `tests/test_metrics.py` and `tests/test_controller.py` before implementation; cover concurrent publication, complete-file visibility, unique names, collision behavior, unsupported linking, bounded warnings, and preserved workflow results (depends on T009).

### Implementation for User Story 2

- [ ] T010 [US2] Publish each record through an exclusive hidden temporary file followed by no-clobber hard-link publication as `metric-<invocation-uuid>.json`, then remove only the writer-owned temporary name in `controllers/farmboy/scripts/python/metrics.py` (depends on T002 and T012).
- [ ] T011 [US2] Add warn-and-continue handling for unavailable timing, metadata, destination, collision, and storage failures to the collection procedure in `controllers/farmboy/controller-protocol.md` (depends on T006, T010, and T012).

## Phase 5: User Story 3 - Consolidate observations for Excel (Priority: P1)

**Goal**: Explicitly run the maintainer-only FarmBoy Metrics Report skill to create one simple XLSX table from a fixed input snapshot while preserving every source record.

**Independent Test**: Supply records from multiple projects plus malformed, oversized, duplicate, conflicting, and late-arriving inputs. Invoke the report against an injected temporary directory and inspect the accepted rows, visible counts, exact 13-column order, literal text/numeric duration types, unique output, and unchanged source bytes. Repeat with missing or empty input and verify a header-only table.

### Tests for User Story 3

- [ ] T018 [P] [US3] Write report contract tests in `tests/test_metrics_report.py` before implementation; cover single-snapshot behavior; UTF-8 JSON objects no larger than 65,536 bytes; required fields `schema_version`, `invocation_id`, `run_id`, `step_id`, `invocation_kind`, `agent_name`, `skill_id`, `workflow_id`, `project_label`, `started_at`, `finished_at`, and `duration_ms` at exact types; `schema_version` exactly `1`, `invocation_kind` exactly `execution`, `continuation`, `retry`, or `probe`, exact millisecond timestamp grammar `YYYY-MM-DDTHH:MM:SS.mmmZ`, signed duration equality, rejection of booleans/fractions, duplicate keys, nonfinite values, impossible timestamps, missing/empty required strings and unsupported schema/kind; `model` and `effort` absent or null normalize to null, non-null values must be nonempty strings, and other present types are invalid; rejection of strings over 32,767 characters or with illegal XML text without trimming/truncation; deduplication/conflicts; exact 13-column Excel order and shortened field mapping with JSON `schema_version` retained only for validation; literal text, numeric durations, zero-row output, no-clobber naming, output failures, failure above 1,000,000 accepted rows, unchanged input bytes, and missing dependency/source-layout failures before output creation without mutating the skill-tools environment (depends on T001).

### Implementation for User Story 3

- [ ] T013 [P] [US3] Implement one-time top-level discovery, bounded single reads, schema validation, invalid-category counts, and normalization of absent `model` and `effort` to null in `skills/farmboy-metrics-report/scripts/metrics_report.py`, importing the canonical validator from reviewed `controllers/farmboy/scripts/python/metrics.py`; validate a UTF-8 JSON object no larger than 65,536 bytes with the twelve required fields `schema_version`, `invocation_id`, `run_id`, `step_id`, `invocation_kind`, `agent_name`, `skill_id`, `workflow_id`, `project_label`, `started_at`, `finished_at`, and `duration_ms` at exact types; require `schema_version` exactly `1`, `invocation_kind` one of `execution`, `continuation`, `retry`, `probe`, timestamps exactly `YYYY-MM-DDTHH:MM:SS.mmmZ`, signed `duration_ms` equal to the timestamp difference, and nonempty required strings; accept `model` and `effort` as absent, null or nonempty strings (absent normalizes to null; other types are invalid); reject duplicate keys, nonfinite constants, booleans/fractions in integer fields, impossible timestamps, unsupported schema/kind, and strings over 32,767 characters or containing illegal XML text without trimming/truncation; ignore unknown extra fields, per `specs/022-local-workflow-agent-timing-metrics/data-model.md` and `contracts/metric-record.md` (depends on T001, T002, and T018).
- [ ] T014 [US3] Group records by `invocation_id`, collapse identical fourteen-field projections, exclude conflicting identities, and calculate the documented candidate, accepted, duplicate, conflict, skipped, and invalid counts in `skills/farmboy-metrics-report/scripts/metrics_report.py` (depends on T013).
- [ ] T015 [US3] Write worksheet `Metrics` and table `FarmBoyMetrics` with exactly `invocation_id`, `run_id`, `project`, `skill`, `workflow`, `step`, `invocation_kind`, `agent`, `model`, `effort`, `started_at`, `finished_at`, `duration_ms`; map shortened headers, retain JSON `schema_version` for validation and duplicate comparison but omit it from Excel, sort rows as specified, and preserve literal strings and numeric duration cells in `skills/farmboy-metrics-report/scripts/metrics_report.py` (depends on T014).
- [ ] T016 [US3] Publish uniquely named workbooks under `~/.farmboy/metrics/reports/` without overwriting prior outputs; create the same header-only table for zero accepted rows and fail visibly on output errors or above 1,000,000 accepted rows in `skills/farmboy-metrics-report/scripts/metrics_report.py` (depends on T015).
- [ ] T017 [US3] Complete `skills/farmboy-metrics-report/SKILL.md` so explicit invocation within FarmBoy verifies the reviewed source layout and `openpyxl==3.1.5`/`et-xmlfile` readiness before any output creation, runs the source report with the prescribed skill-tools interpreter, explains summary counts and locations, and never installs dependencies or launches another workflow (depends on T001 and T016).
- [ ] T019 [US3] Document schema, invocation boundaries, wall-clock limits, storage locations, concurrency, warnings, consumer delivery boundary, and explicit report usage in `docs/metrics.md`, `docs/architecture.md`, and `docs/installation.md` (depends on T006, T011, and T017).
- [ ] T020 [US3] Verify disposable consumer installation and removal deliver the collection helper but exclude the maintainer report skill and its dependency, while preserving local metric files and unrelated consumer components in `tests/test_bundle_lifecycle.py` and `tests/test_catalog.py` (depends on T004 and T017).

## Phase 6: Polish & Cross-Cutting Validation

**Purpose**: Validate the end-to-end round trip and record evidence without claiming publication or consumer adoption.

- [ ] T021 Run the deterministic collection, report, controller, catalog, and bundle lifecycle checks listed in `specs/022-local-workflow-agent-timing-metrics/quickstart.md`; inspect `controllers/farmboy/controller-protocol.md` to confirm the metrics-only TOML-read exception is narrow and preserves dispatch authority; correct failures in their owning source or test files.
- [ ] T022 Exercise the documented live observation path for an exact named agent in FarmBoy and a disposable consumer, then explicitly invoke the maintainer report and record bounded evidence in `specs/022-local-workflow-agent-timing-metrics/quickstart.md` without including transcripts, secrets, personal details, or absolute host paths.
- [ ] T023 Open one populated workbook and one header-only workbook in Excel, verify table interoperability, filtering, literal text, and numeric signed-duration calculations, and record the observations in `specs/022-local-workflow-agent-timing-metrics/quickstart.md`.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Establishes the report source package and approved dependency declaration.
- **Foundational (Phase 2)**: The record-contract tests (T005) are written from the approved contract before implementation; complete T002 after T005, then metrics correlation (T003) and package delivery (T004) before story work.
- **User Stories (Phases 3–5)**: All depend on foundational tasks. User Story 1 precedes User Story 2 because both extend shared controller timing and adapter behavior. User Story 3 can proceed after T002 and T001, in parallel with User Stories 1 and 2 after the foundation is complete.
- **Polish (Phase 6)**: Depends on the collection and reporting implementation and their deterministic tests.

### User Story Dependencies

- **User Story 1 (P1)**: Depends on T002, T003, T005, and test preparation T009; implement the invocation boundary only after its tests are written.
- **User Story 2 (P1)**: Depends on User Story 1's invocation boundaries and test preparation T012; implement concurrent no-clobber publication and failure isolation only after its tests are written.
- **User Story 3 (P1)**: Depends on T001, T002, and test preparation T018 for its maintainer package and canonical record validator; implementation follows its test task and can proceed independently of invocation wrapping.

### Parallel Opportunities

- After T005, T002 implements the canonical helper. Once T002 completes, T003 and T004 can proceed in parallel because they edit separate controller/catalog files. After T009 is written, T006 and T007 can proceed in parallel because they edit separate protocol and metrics files; T008 follows T006 because it edits the same protocol file.
- T012 prepares the US2 tests before implementation. Within US2, no safe implementation parallelism applies: T010 owns record publication, and dependent T011 adds its warn-and-continue protocol behavior after T010.
- After T001, T002, and T018, T013 implements report ingestion. Later report tasks remain sequential because T013-T016 extend the same report script, T017 follows report publication, and T019/T020 depend on settled implementation boundaries. Report tests are prepared before report implementation, not in parallel with it.
- Documentation (T019) can proceed once the protocol and report invocation behavior are settled; disposable-consumer verification (T020) follows the source-skill and package boundaries.

## Parallel Example: User Story 1

```text
After T002, T003, T004, T005, and T009 complete:
Worker A: Implement T006 in controllers/farmboy/controller-protocol.md.
Worker B: Implement T007 in controllers/farmboy/scripts/python/metrics.py.
Then complete T008 after T006 because both own controllers/farmboy/controller-protocol.md.
```

## Parallel Example: User Story 2

```text
Not applicable within this story: T011 depends on T010's publication behavior, so execute those implementation tasks in dependency order after T012 test preparation.
```

## Parallel Example: User Story 3

```text
Not applicable within this story: T013-T016 extend the same report script in dependency order, T017 follows report publication, and T019/T020 depend on settled boundaries; T018 prepares tests first. Avoid concurrent edits to skills/farmboy-metrics-report/scripts/metrics_report.py.
```

## Implementation Strategy

### MVP First

The approved MVP is the complete collection-to-workbook round trip: finish Setup and Foundational, then implement User Stories 1 and 2 for reliable local records and User Story 3 for a usable workbook. All three stories are P1 requirements of the requested feature; stopping after collection would leave the requested report unavailable.

### Incremental Delivery

1. Establish the record contract and separate metrics correlation ID.
2. Add timing around observed named-agent turns and validate the invocation boundaries.
3. Add no-clobber concurrent publication and warn-and-continue behavior.
4. Add the maintainer-only report, deduplication, validation, and 13-column workbook.
5. Validate consumer exclusion, live round trip, and populated and empty workbook interoperability.

## Notes

- Every task is an unchecked checklist item with a unique sequential ID and at least one exact repository path.
- `[P]` is omitted where tasks share files or depend on incomplete work.
- Test tasks are included because the plan and quickstart define concrete deterministic, concurrency, consumer-delivery, and workbook-interoperability validation obligations.
- Do not add recovery-creation changes, outcome fields, shared append files, locks, report automation, or additional Excel columns.

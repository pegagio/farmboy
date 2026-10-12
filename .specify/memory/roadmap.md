<!--
SYNC IMPACT REPORT
==================
Version change: 1.30.3 → 1.30.4
Bump rationale: PATCH — authorized status amendment for entry 022.
Status: specced → in-progress
Authorization: specs/022-local-workflow-agent-timing-metrics/validation/phase-lifecycle/implementation-decision-ea083f52.json
Evidence paths: ["specs/022-local-workflow-agent-timing-metrics/validation/phase-lifecycle/implementation-readiness-checker-assessment-ea083f52.json", "specs/022-local-workflow-agent-timing-metrics/validation/phase-lifecycle/independent-implementation-start-review-ea083f52.json"]
-->
<!--
SYNC IMPACT REPORT
==================
Version change: 1.30.2 → 1.30.3
Bump rationale: PATCH — authorized status amendment for entry 022.
Status: planned → specced
Authorization: specs/022-local-workflow-agent-timing-metrics/validation/phase-lifecycle/specification-decision.json
Evidence paths: ["specs/022-local-workflow-agent-timing-metrics/validation/phase-lifecycle/independent-roadmap-brief-review.json", "specs/022-local-workflow-agent-timing-metrics/validation/phase-lifecycle/independent-specification-milestone-review.json"]
-->
<!--
SYNC IMPACT REPORT
==================
Version change: 1.30.1 → 1.30.2
Bump rationale: PATCH — assign the operator-selected Feature 022 its physical specification mapping for activation.
Changes: add only Feature 022 Spec dir; preserve planned status, scope, dependencies, names and all existing specification bytes.
Specs affected: 022 (planned; mapping only).
Open questions added/resolved: Physical mapping resolved; specification/planning decisions remain open.
Notes: Operator requested FarmBoy Select Feature for Feature 022 on 2026-10-11. Selection activates identity only; no directory, specification, implementation, acceptance or Git integration is authorized by this patch.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.30.0 → 1.30.1
Bump rationale: PATCH — record the operator's settled Feature 022 maintainer skill name.
Changes: settle FarmBoy Metrics Report / farmboy-metrics-report and resolve the naming question; preserve maintainer-only delivery, scope, statuses, dependencies and historical reports.
Specs affected: 022 (planned; naming decision only).
Open questions added/resolved: Final skill name resolved by direct operator decision; other specification questions remain open.
Notes: Direct operator instruction on 2026-10-11 selects the report name. Feature activation is separately requested through FarmBoy Select Feature; this amendment does not itself activate, author, implement, publish or authorize Git integration.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.29.0 → 1.30.0
Bump rationale: MINOR — narrow Feature 022's workbook-generation skill to maintainer use within FarmBoy, excluding consumer installation.
Changes: keep timing/emission support available to FarmBoy consumers; make the separately invoked XLSX skill maintainer-only; mark its earlier report name provisional and record metrics-workbook as a recommendation. All feature states, dependencies and other collection decisions remain unchanged.
Specs affected: 022 (planned; workbook-skill delivery boundary clarified).
Open questions added/resolved: Maintainer-only use and exclusion from consumer installation are settled by direct operator instruction. Final skill name remains open; no name is accepted by this amendment.
Notes: Direct operator clarification on 2026-10-11 authorizes the delivery-boundary amendment. Name suggestions are proposals, not decisions. Prior sync reports retain the earlier scope as history. No external evidence is used. No activation, implementation, installation, publication or Git integration is authorized.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.28.0 → 1.29.0
Bump rationale: MINOR — expand Feature 022 to the operator-requested metrics collection/report round trip and lock-free per-emission files.
Changes: include the separately invoked farmboy-metrics-report skill producing a simple XLSX table; require one uniquely named intermediate file per emission instead of shared appends; retain the local adapter, ~/.farmboy/metrics, clock-drift/skew acceptance and warn-and-continue collection policy. Preserve all feature states, dependencies and existing verification evidence.
Specs affected: 022 (planned; report scope added and concurrent collection clarified).
Open questions added/resolved: Report inclusion, XLSX output and per-emission files are settled by direct operator instruction. Record format, fields, filename/completed-file convention, report input snapshot and output handling remain specification/planning questions.
Notes: Direct operator instruction on 2026-10-11 authorizes this bounded amendment. The previous future-only export exclusion and shared-append possibility are superseded; prior sync reports preserve their provenance. A self-contained JSON record per file is an assistant simplicity recommendation, not a mandated format. No external evidence is used. This amendment does not activate or implement the feature, generate metrics/workbooks, install dependencies, invoke another workflow, publish or authorize Git integration.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.27.0 → 1.28.0
Bump rationale: MINOR — relax Feature 022's CSV-only collection constraint to a simple structured intermediate format.
Changes: preserve local agent timing, the adapter boundary, ~/.farmboy/metrics and warn-and-continue behavior; record JSONL as a proposal and a future separately scoped FarmBoy consolidation/export skill producing CSV or XLSX. All feature states and dependencies remain unchanged.
Specs affected: 022 (planned; collection-format scope clarified).
Open questions added/resolved: The operator settles format flexibility; exact intermediate schema and file layout remain specification decisions. Preserve the original CSV request as superseded provenance.
Notes: Direct operator clarification on 2026-10-11 authorizes this amendment. JSONL is an assistant recommendation, not a settled format requirement. The future export skill is context, not an additional feature or implementation authorized here. No external evidence is used; no activation, implementation, publication or Git integration is authorized.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.26.4 → 1.27.0
Bump rationale: MINOR — add the directly requested local workflow-agent timing metrics feature.
Changes: add Feature 022 as planned; record local wall-clock timing, a small metrics adapter API, initial machine-local CSV collection, and the operator's destination and failure-policy decisions. Preserve all existing entries, lifecycle states, dependencies and verification qualifications.
Specs affected: 022 (new planned feature only).
Open questions added/resolved: Add final metadata/schema, invocation-boundary and CSV-file-layout questions for specification. The initial destination (~/.farmboy/metrics), warn-and-continue collection policy and acceptance of clock drift/skew are settled by direct operator decisions.
Notes: Direct operator request on 2026-10-11 authorizes this bounded addition for FarmBoy and projects consuming FarmBoy. Suggested extra dimensions remain proposals rather than settled requirements. Governing evidence: .specify/memory/constitution.md and the current .specify/memory/roadmap.md. No ADR or PRD evidence is used. This amendment does not activate the feature, create a specification, implement instrumentation, create metrics files, install components, publish or authorize Git integration.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.26.3 → 1.26.4
Bump rationale: PATCH — record Feature 021 verification supported by a fresh attributable implementation debrief.
Changes: record the adjacent implemented → verified recommendation and align Feature 021's current summary with observed evidence and validation limits.
Specs affected: 021 (verified); dependencies 011, 013, 014 and 017 retain verified.
Open questions added/resolved: none.
Notes: Fresh debrief: specs/021-farmboy-project-workflow-naming/roadmap-reviews/debrief-20261011T020448Z.md. Reviewed baseline 7a43bb37398baec7a757feb04cbb83dcb901fac4 through WORKTREE at HEAD 6738a067045b268feb7f5522d7841290ce70b3a2; snapshot sha256:c91b8e107d4e31e8ead46725212c2fad3997bad718041759525b6d8447e3402e remained stable. No unresolved findings. This amendment requires the separately gated operator approval and application readback; it does not reconstruct historical phase-owner effects or grant acceptance, publication, consumer refresh or Git integration. Preserve other entries, prior reports and existing qualifications.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.26.2 → 1.26.3
Bump rationale: PATCH — correct Feature 021's current recorded milestone without changing product scope.
Changes: record the adjacent in-progress → implemented current-state correction and align its current summary.
Specs affected: 021 (implemented); dependencies 011, 013, 014 and 017 retain verified.
Open questions added/resolved: none.
Notes: Explicit operator approval of this exact prerequisite amendment is required before application. Current evidence: specs/021-farmboy-project-workflow-naming/validation/closeout-corrections.md, current spec/plan/tasks/checklist/quickstart and .specify/memory/constitution.md. This is a present-state ledger correction supported by actual installed FlowKit-native reviews under the constitutional transition; it does not reconstruct earlier phase-owner effects, fabricate owner receipts, verify the feature, refresh consumers, grant acceptance, publish or authorize Git integration. Preserve all prior reports, other entries and qualifications.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.26.1 → 1.26.2
Bump rationale: PATCH — correct Feature 021's current recorded milestone without changing product scope.
Changes: record the adjacent specced → in-progress current-state correction and align its current summary.
Specs affected: 021 (in-progress); dependencies 011, 013, 014 and 017 retain verified.
Open questions added/resolved: none.
Notes: Explicit operator approval of this exact prerequisite amendment is required before application. Current evidence: specs/021-farmboy-project-workflow-naming/validation/closeout-corrections.md, current spec/plan/tasks/checklist/quickstart and .specify/memory/constitution.md. This is a present-state ledger correction supported by actual installed FlowKit-native reviews under the constitutional transition; it does not reconstruct earlier phase-owner effects, fabricate owner receipts, verify the feature, refresh consumers, grant acceptance, publish or authorize Git integration. Preserve all prior reports, other entries and qualifications.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.26.0 → 1.26.1
Bump rationale: PATCH — correct Feature 021's current recorded milestone without changing product scope.
Changes: record the adjacent planned → specced current-state correction and reconcile current title, summary and resolved constitutional notes.
Specs affected: 021 (specced); dependencies 011, 013, 014 and 017 retain verified.
Open questions added/resolved: mark the previously settled constitutional identity question resolved; preserve its historical wording.
Notes: Explicit operator approval of this exact prerequisite amendment is required before application. Current evidence: specs/021-farmboy-project-workflow-naming/validation/closeout-corrections.md, current spec/plan/tasks/checklist/quickstart and .specify/memory/constitution.md. This is a present-state ledger correction supported by actual installed FlowKit-native reviews under the constitutional transition; it does not reconstruct earlier phase-owner effects, fabricate owner receipts, verify the feature, refresh consumers, grant acceptance, publish or authorize Git integration. Preserve all prior reports, other entries and qualifications.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.25.0 → 1.26.0
Bump rationale: MINOR — include the directly approved owned feedback and delegation-parser rename in Feature 021.
Changes: rename both owned feedback extensions and their existing command/skill identities; replace the flow_kit delegation key and owned readers with farmboy, preserving existing behavior and nested fields. Independent roadmap/wiki and core commands stay unchanged.
Specs affected: 021 (planned; owned rename coverage expanded).
Open questions added/resolved: Feedback/parser inclusion is settled by direct operator instruction; constitutional identity approval remains required before implementation.
Notes: Direct operator scope instruction on 2026-10-10. No migration, compatibility fallback, implementation, constitutional amendment, lifecycle advancement or Git integration is authorized by this record. All other feature entries and historical reports are preserved.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.24.1 → 1.25.0
Bump rationale: MINOR — record the directly approved Feature 021 scope correction to a pure rename cutover.
Changes: remove consumer migration, compatibility, new management commands, journals and recovery/test-matrix scope; settle canonical names and retain existing behavior. Preserve all other features, states, dependencies and historical evidence.
Specs affected: 021 (planned; scope narrowed).
Open questions added/resolved: Naming and compatibility are settled; consumer migration is excluded. The constitutional identity amendment remains open.
Notes: Direct operator instruction on 2026-10-10: no migration feature, pure cutover, just a rename. Previous scope/review records remain historical; this amendment does not implement the rename, amend the constitution, advance lifecycle or authorize Git integration.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.24.0 → 1.24.1
Bump rationale: PATCH — restore the approved Feature 021 activation mapping after merging develop.
Changes: restore only the selected Spec dir linkage; preserve all feature states, dependencies and merged lifecycle evidence.
Specs affected: 021 (directory mapping only).
Open questions added/resolved: none.
Notes: Original activation was explicitly approved on 2026-10-08. This restores the uncommitted selection change preserved before the operator-requested merge on 2026-10-09. The original activation report is retained below; the active pointer still identifies the same target. No specification is created.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.23.0 → 1.23.1
Bump rationale: PATCH — record the explicitly approved Feature 021 target-directory mapping while preserving its planned lifecycle and existing approved scope.

Changes this revision:
  - Add Feature 021's Spec dir mapping to specs/021-farmboy-project-workflow-naming for separately invoked specification authoring.
  - Preserve every feature's lifecycle, scope, dependencies and historical verification evidence.
  - Retain the separate constitutional amendment required before rename implementation.

Specs affected: 021 (target-directory linkage only)
Open questions added/resolved: none; identifier, consumer-compatibility and constitutional-amendment decisions remain open.

Notes: Provenance: direct operator selection of Feature 021 and explicit approval of the exact directory mapping and active-pointer payload at the installed Select Feature activation gate on 2026-10-08. The target directory and specification are not created by this amendment. Pointer activation and independent verification are subsequent declared steps; this roadmap change alone does not establish activation, authoring, implementation, publication, Git integration or acceptance.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.23.0 / 1.22.4 → 1.24.0
Bump rationale: MINOR — reconcile the approved Feature 021 addition with develop's Feature 020 lifecycle and qualified verification history.
Changes: preserve both feature entries, all prior lifecycle evidence and governing decisions; retain the separately required constitutional identity amendment.
Specs affected: 020 and 021 (ledger integration only; statuses remain verified and planned respectively).
Open questions added/resolved: preserve Feature 021's approved naming and migration questions; resolve none.
Notes: Direct operator request on 2026-10-09 to merge develop into farmboy. Prior reports from both branches are retained below. No new feature scope, acceptance, publication or consumer migration is granted.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.22.2 → 1.23.0
Bump rationale: MINOR — add the explicitly approved FarmBoy project, skill, workflow and associated agent naming feature without changing existing lifecycle states or runtime behavior.

Changes this revision:
  - Add Feature 021 — FarmBoy Project and Workflow Naming with status planned.
  - Record consistent branding, owned identity reconciliation, consumer migration guidance and bounded validation within the approved rename scope.
  - Require a separately approved constitutional amendment before implementing changes to the currently mandated identities.
  - Preserve existing entries, dependencies, historical verification evidence and independently owned component authority.

Specs affected: 021 (new planned feature only)
Open questions added/resolved: Add Feature 021 identifier-mapping, consumer-compatibility and constitutional-amendment questions; resolve none.

Notes: Provenance: direct operator selection of FarmBoy and the Spec et Labora tagline, followed by explicit approval of the Feature 021 roadmap proposal on 2026-10-08. Governing repository evidence: .specify/memory/constitution.md and the existing .specify/memory/roadmap.md. Feature 020 remains reserved for parallel work and is not reconstructed from another checkout. No specification directory is assigned; this amendment grants no implementation, publication, external repository rename, consumer migration or Git integration authority.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.22.3 → 1.22.4
Bump rationale: PATCH — record qualified verification of entry 020 and correct its stale planned summary.
Feature-local operator waiver preserves unperformed T066/T077 manual cases; later dogfooding findings are defects, not mandatory matrix work.
Original milestone events, unrelated entries, dependencies and governing decisions are preserved. No acceptance, Git integration, release or publication effect.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.22.2 → 1.22.3
Bump rationale: PATCH — evidence-backed adjacent lifecycle status/provenance for entry 020.
Effect: lifecycle-feea7fc34b5d4018419cbab041634f17; owner closeout; actual occurrence 2026-10-09T19:39:48.027967Z.
Unrelated entries, decisions and history preserved. No verified, acceptance, integration or publication effect.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.22.1 → 1.22.2
Bump rationale: PATCH — evidence-backed adjacent lifecycle status/provenance for entry 020.
Effect: lifecycle-17640d8a7a1b93b3fd5dc03494959646; owner implement; actual occurrence 2026-10-09T19:35:23.038956Z.
Unrelated entries, decisions and history preserved. No verified, acceptance, integration or publication effect.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.22.0 → 1.22.1
Bump rationale: PATCH — evidence-backed adjacent lifecycle status/provenance for entry 020.
Effect: lifecycle-4f2aa461b8a3c0dd36ce037448c9e3ec; owner specify; actual occurrence 2026-10-09T19:22:58.296931Z.
Unrelated entries, decisions and history preserved. No verified, acceptance, integration or publication effect.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.21.0 → 1.22.0
Bump rationale: MINOR — add the operator-requested phase-owned lifecycle milestones, evidence boundaries and bounded stale-state recovery to Feature 020's planned scope.

Changes this revision:
  - Add Specify ownership of planned→specced after current authoring, quality, review and roadmap-brief evidence.
  - Add Implement ownership of specced→in-progress after current readiness and eligible-scope evidence, before coding.
  - Add Close Out ownership of in-progress→implemented after current full-scope implementation and independent-review evidence, before the existing explicit verified gate.
  - Record bounded ordered recovery and preserve Feature 020's planned status, dependencies, verification gate and all unrelated ledger content.

Specs affected: 020 (planned; FR-026–FR-038 and SC-012–SC-016 added)
Open questions added/resolved: Phase ownership and evidence boundaries are defined in the active Feature 020 amendment. Detailed prospective runtime policy still requires the explicit T051 decision; compatible extension delivery remains separately required.

Notes: Direct operator request on 2026-10-07 identified the stale planned state as a workflow lifecycle defect and authorized defining phase ownership, evidence and operator-decision boundaries in Feature 020. The additive entry text follows that approved feature scope and current contract proposal in specs/020-flowkit-workflow-iteration-improvements/contracts/phase-lifecycle.md. This roadmap amendment preserves planned; it does not authorize current runtime lifecycle writes, amend the constitution, install a workflow, publish components, or accept implementation.
-->

<!--
SYNC IMPACT REPORT
==================
Version change: 1.22.1 → 1.22.2
Bump rationale: PATCH — record Feature 019's independently reviewed implementation verification and reconcile its resolved planning notes within the existing approved scope.

Changes this revision:
  - Change only Feature 019 from implemented to verified after fresh full-delta debrief and explicit operator approval of this exact patch.
  - Reconcile Feature 019's environment and utility decisions and resolved planning questions with its reviewed plan, implementation and bounded validation.
  - Preserve prior superseded designs, all other entries, dependencies and Feature 017's original failure and evidence limitations.
  - Grant no acceptance, publication, actual external-project adoption or Git integration.

Specs affected: 019 (verification lifecycle and resolved planning bookkeeping only)
Open questions added/resolved: Resolve Feature 019 preparation/invocation and extra-utility questions; retain their original wording as historical questions.

Notes: Evidence: specs/019-catalog-python-runtime-prerequisites/roadmap-reviews/debrief-20261005T200520Z.md, tasks.md and validation.md. Review covers the complete attributable baseline-to-WORKTREE snapshot; local results and a disposable second-project fixture do not establish full catalog lifecycle, stock Specify compatibility or other-platform support.
-->

# FarmBoy — Spec Roadmap

This living roadmap records the project's completed specifications and leaves room for future features. It is not a commitment to new scope or sequence. The [constitution](constitution.md) governs this ledger; each entry points to its feature specification. The operator designated entries 001–011 verified on 2026-09-26; later entries carry their own lifecycle states below.

The Feature 020 integration preserves Feature 019's independently approved verification and Feature 020's lifecycle history. Both branches used revision 1.22.2 independently; the original sync reports retain that branch history, while the combined ledger retains the latest existing revision, 1.22.4. This reconciliation changes no feature scope, status, qualification or milestone provenance.

## Contents

- [Vision and end states](#vision-and-end-states)
- [Constraints and decisions](#constraints-and-decisions)
- [Planned specs](#planned-specs)
- [Open questions](#open-questions)
- [Cross-cutting notes](#cross-cutting-notes)

Status legend: **undecided** · **needs-info** · **planned** · **specced** · **in-progress** · **implemented** · **verified** · **deferred** · **abandoned**.

## Vision and end states

The constitution establishes the durable project direction; the completed specs define the current delivery boundary.

- Provide a reusable, human-directed Spec-Driven Development workbench whose feature artifacts stay consistent through merge-bounded flow-back and explicit review gates.
- Keep generic workflows, independently versioned extensions, portable consumer feedback, maintainer intake, and the bundle catalog traceable to reviewed source and bounded validation evidence.
- Preserve manual workflow paths and human control over agent selection, material scope, roadmap verification, Git integration, publication, and acceptance.
- Treat additional features as future roadmap amendments. Features 012 and 013 are verified independently; feature 014 covers accepted workflow improvements, and feature 015 covers named Codex agents for delegated steps.

## Constraints and decisions

These cross-cutting constraints come from the [constitution](constitution.md); they do not create new feature scope.

- **C-01 — Merge-bounded persistence**: Before merge, accepted discoveries flow through the current spec, plan, tasks, and implementation; after merge, behavioral changes move into a new feature directory. This keeps reviewable intent and historical records coherent.
- **C-02 — Human-directed authority**: The operator chooses workflows and task scope. Every delegated workflow step declares a reviewed Codex agent name; invocation authorizes that assignment without a per-run agent, model, or effort override. A Codex controller may launch bounded step subagents and must relay human decisions through the main task. Command success cannot confer roadmap, scope, integration, or acceptance decisions.
- **C-03 — Generic component boundaries**: This repository owns generic workflow and feedback source; the bundle composes versioned components. The Diagram remains a consumer, with adapter behavior governed separately.
- **C-04 — Reviewable source and fallback**: Changes target source packages, planning and task generation remain distinct, and each workflow retains a manual-prompt path. New build tools or dependencies require a documented need and approval.
- **C-05 — Bounded validation and feedback**: Disposable consumer tests record component and CLI provenance without claiming publication, stock compatibility, or live-agent quality. Feedback capture and intake provide evidence and proposals, not direct source or authority changes.

## Planned Specs

Entries 001–011 record verified history. Features 012, 013, 014, and 015 are verified. Feature 016 is planned; Feature 017 is verified with its documented follow-up qualification; Feature 018 is abandoned. Feature 019 is verified for its approved agent-environment scope motivated by DEP017-01; the original catalog failure and Feature 017 qualification remain preserved, and full catalog lifecycle repair is not claimed. Feature 018's proposed capacity repair and sequencing are retained as historical intent, not an active delivery commitment; the original observation remains unresolved. Feature 020 is verified for its reviewed buildable implementation and observed automated/native validation, with its operator-waived, unperformed T066/T077 manual matrices recorded in the entry qualification below. Feature 021 is verified for the approved FarmBoy rename under Constitution 8.0.0, supported by the [fresh implementation debrief](../../specs/021-farmboy-project-workflow-naming/roadmap-reviews/debrief-20261011T020448Z.md) and documented automated/native-fixture validation. The snapshot remains unpublished; newly packaged FarmBoy live-agent behavior and Linux remain untested, and no consumer refresh, feature acceptance or Git integration is implied. Feature 022 is planned for basic local workflow-agent timing, one structured file per emission and a maintainer-only workbook skill producing a simple XLSX table within FarmBoy. Dependencies describe delivery prerequisites between these specs, not the order in which an operator must run workflow phases.

### 001 — Start Eligible Feature  [status: verified]

- **Description**: Guide an operator from an eligible roadmap item through an approved patch, cited context, a specification draft, and roadmap brief.
- **Outcome**: An eligible start produces a reviewed feature draft and explicit next choice; ambiguous eligibility, dependencies, or context stop without a state change.
- **Scope (in)**: Eligibility and dependency checks, exact patch approval, governing-context coverage, specification drafting, brief, and manual fallback.
- **Scope (out)**: Automatic clarification, planning, agent dispatch, Git integration, acceptance, or Diagram runtime behavior.
- **Depends on**: none.
- **Governed by**: C-02, C-03, C-04.
- **Spec dir**: `specs/001-start-eligible-feature/`.

### 002 — Clarify Specification  [status: verified]

- **Description**: Run one bounded clarification session for an operator-selected active specification and route its result.
- **Outcome**: Accepted answers enter the spec incrementally, unresolved ambiguity remains visible, and the operator chooses continuation, planning readiness, or deferral.
- **Scope (in)**: One session, the current five-question boundary, result review, explicit routing, and manual fallback.
- **Scope (out)**: Automatically declaring readiness, launching planning, or introducing an unapproved continuation preset.
- **Depends on**: none.
- **Governed by**: C-02, C-04.
- **Spec dir**: `specs/002-clarify-specification/`.

### 003 — Plan Implementation  [status: verified]

- **Description**: Check planning readiness and create reviewable technical artifacts for a clarified feature.
- **Outcome**: A plan, research, data model, contracts, and quickstart are offered for review only after an explicit readiness decision.
- **Scope (in)**: Reviewed-spec confirmation, plan/return/defer gate, technical planning, and manual fallback.
- **Scope (out)**: Resolving product ambiguity through design assumptions or automatically generating tasks.
- **Depends on**: none.
- **Governed by**: C-02, C-04.
- **Spec dir**: `specs/003-plan-implementation/`.

### 004 — Generate Implementation Tasks  [status: verified]

- **Description**: Generate dependency-ordered tasks from reviewed design artifacts as a separate workflow phase.
- **Outcome**: The operator reviews task coverage and unexpected human work before choosing analysis, replanning, amendment, or deferral.
- **Scope (in)**: Task proposal generation, coverage review, explicit routing, and manual fallback.
- **Scope (out)**: Automatic implementation, agent selection, Git integration, or bypassing analysis.
- **Depends on**: none.
- **Governed by**: C-02, C-04.
- **Spec dir**: `specs/004-generate-tasks/`.

### 005 — Analyze and Remediate Artifacts  [status: verified]

- **Description**: Analyze spec, plan, and task consistency before implementation and route bounded corrections through affected artifacts.
- **Outcome**: Routine findings receive dependent-artifact reconciliation and another read-only analysis; consequential or blocked outcomes stop for a separate decision.
- **Scope (in)**: Analysis disposition, scoped spec/plan/task remediation, reanalysis, and manual fallback.
- **Scope (out)**: Unapproved constitutional, authority, material-scope, or ambiguous-recovery changes and automatic implementation.
- **Depends on**: none.
- **Governed by**: C-01, C-02, C-04.
- **Spec dir**: `specs/005-analyze-remediate/`.

### 006 — Implement Eligible Work  [status: verified]

- **Description**: Implement analyzed, eligible tasks within the operator-selected feature, task, and agent boundary.
- **Outcome**: Execution evidence is reviewed, discoveries return through the relevant artifacts and analysis, and blockers stop without expanding scope.
- **Scope (in)**: Eligible task execution, prerequisite checks, return routes, blocker handling, and manual fallback.
- **Scope (out)**: Automatic agent launch, implementation retries after artifact changes, roadmap verification, publication, or acceptance.
- **Depends on**: none.
- **Governed by**: C-01, C-02, C-04.
- **Spec dir**: `specs/006-implement-eligible-work/`.

### 007 — Converge Feature  [status: verified]

- **Description**: Compare implementation with current feature artifacts and route bounded remaining work to resolution.
- **Outcome**: Clean convergence stops for separate closeout; remediation tasks pass analysis before another implementation and convergence run.
- **Scope (in)**: Gap assessment, clean/remediation/blocked disposition, task analysis, and manual fallback.
- **Scope (out)**: Automatic closeout, Git integration, publication, or acceptance.
- **Depends on**: none.
- **Governed by**: C-01, C-02, C-04.
- **Spec dir**: `specs/007-converge-feature/`.

### 008 — Close Out Feature  [status: verified]

- **Description**: Guide explicit feature-completion review, roadmap verification, curated wiki maintenance, and commit-readiness review.
- **Outcome**: A separately approved completion operation and exact roadmap patch precede wiki ingestion and lint; commit readiness remains an operator decision.
- **Scope (in)**: Completion gate, roadmap debrief and patch review, selected wiki sources, lint, and manual fallback.
- **Scope (out)**: Inventing a completion operation, automatic commit or Git integration, or implied project acceptance.
- **Depends on**: none.
- **Governed by**: C-01, C-02, C-05.
- **Spec dir**: `specs/008-close-out-feature/`.

### 009 — Consumer Feedback  [status: verified]

- **Description**: Capture local workflow observations and export portable reports without changing source or authority.
- **Outcome**: Valid observations become append-only local evidence and deterministic digest-bearing JSON and Markdown reports; malformed or sensitive input is rejected.
- **Scope (in)**: Provenance validation, duplicate rejection, portability checks, offline capture and export.
- **Scope (out)**: Automatic report transfer, maintainer disposition, source changes, or roadmap mutation.
- **Depends on**: none.
- **Governed by**: C-02, C-03, C-05.
- **Spec dir**: `specs/009-consumer-feedback/`.

### 010 — Maintainer Feedback Intake  [status: verified]

- **Description**: Validate transferred consumer reports and record bounded maintainer disposition proposals.
- **Outcome**: Valid reports create a canonical inbox copy and triage proposal; duplicates link to earlier intake, while invalid input creates no record.
- **Scope (in)**: Schema, digest, provenance, evidence, and redaction checks; safe triage and duplicate handling.
- **Scope (out)**: Packaging intake into the consumer bundle or directly editing workflows, roadmaps, installed components, Git state, or agent policy.
- **Depends on**: 009.
- **Governed by**: C-02, C-03, C-05.
- **Spec dir**: `specs/010-maintainer-intake/`.

### 011 — Bundle Catalog and Lifecycle  [status: verified]

- **Description**: Package pinned workflow and extension components and guide verified installation, refresh, and removal in consumer projects.
- **Outcome**: The local catalog records reviewed provenance and checksums, and disposable lifecycle validation covers installation through removal without deleting consumer-owned evidence.
- **Scope (in)**: Bundle pins, deterministic release assets, catalog verification, tested CLI coordinates, lifecycle tests, and installation documentation.
- **Scope (out)**: Remote publication, stock Spec Kit compatibility claims, live-agent quality claims, or automatic consumer adoption.
- **Depends on**: 001, 002, 003, 004, 005, 006, 007, 008, 009, 010.
- **Governed by**: C-02, C-03, C-04, C-05.
- **Spec dir**: `specs/011-bundle-catalog/`.

### 012 — Consumer Adoption of Merge-Bounded Flow-Back  [status: verified]

- **Description**: Investigate how the FlowKit bundle should bring the Merge-Bounded Flow-Back Spec Persistence Model into consumer projects, then implement the selected mechanism.
- **Outcome**: New and refreshed bundle consumers have a validated, reviewable path to use the model in project guidance and governance; adoption is confirmed from project state rather than assumed from installation.
- **Scope (in)**: Compare an onboarding skill, a preset or template approach, and other supported mechanisms; review and refine the proposed README and constitution language as needed; implement the chosen path, conflict handling, and disposable-consumer validation.
- **Scope (out)**: Silent replacement of existing project governance, retroactive edits to merged feature history, a separate scope-creep policy, Diagram-specific behavior, and changes to Specify's global base template.
- **Depends on**: 011.
- **Governed by**: C-01, C-02, C-03, C-04, C-05.
- **Notes**: The operator set the adoption goal and requested investigation followed by implementation. Agents should recommend the operator-invoked FlowKit consistency workflows and flag missing checks rather than independently launch those workflows or their core commands. `docs/merge-bounded-flow-back.md` is a starting proposal, not required verbatim text; the selected delivery mechanism and bounded observations are recorded in Feature 012 research, contract, and validation.
- **Spec dir**: `specs/012-consumer-adoption/`
- **Verification**: The specification is `Complete`; the [fresh debrief](../../specs/012-consumer-adoption/roadmap-reviews/debrief-20260929T162707Z.md) recommends `verified` with zero Must-Address findings, and the operator explicitly approved this transition. The [validation record](../../specs/012-consumer-adoption/validation.md) bounds the result to reviewed source and disposable consumers; real-consumer adoption and Git integration remain separate.
- **Resolved delivery decision**: Use a reviewed runbook, reusable proposal text, evidence worksheet, and copyable manual prompt linked from installation and refresh instructions. A dedicated onboarding skill or installed preset was not selected for this delivery; see [research](../../specs/012-consumer-adoption/research.md#delivery-mechanism).
- **Resolved conflict decision**: Inspect existing governance and active guidance rule by rule, preserve equivalent or stricter compatible wording, present minimal exact patches, require an operator decision for constitutional amendments or material conflicts, and recheck baselines before accepted edits; see [research](../../specs/012-consumer-adoption/research.md#review-and-conflict-resolution) and the [adoption contract](../../specs/012-consumer-adoption/contracts/adoption.md#review-and-mutation-contract).
- **Resolved evidence decision**: Confirm adoption only with M1–M5 evidence in applicable active agent guidance and compatible governance, a known integration boundary, project-relative citations and digests, and a separate operator decision. Report incomplete or declined paths as `partial`, `declined`, or `unresolved` according to observed state; see [research](../../specs/012-consumer-adoption/research.md#adoption-evidence-and-outcomes), the [output contract](../../specs/012-consumer-adoption/contracts/adoption.md#output-contract), and [bounded validation](../../specs/012-consumer-adoption/validation.md). This does not assert adoption in a real consumer.

### 013 — FlowKit Codex Workflow Controllers  [status: verified]

- **Description**: Provide direct `flow-kit-*` Codex skills through the FlowKit catalog route alongside the Specify bundle so an operator can explicitly run each installed FlowKit workflow inside the consumer project's Codex task, with a main-task controller and bounded step subagents using concrete models declared in the workflow.
- **Outcome**: A consumer can invoke a stable, named skill for each of the eight workflows under its FlowKit display name, see progress and diffs in the Codex desktop task, use declared per-step models and reasoning efforts without choosing them at every step, override one named step when needed, answer clarification and review questions in the main task, and receive the workflow result without losing its human gates or separate phase boundaries.
- **Scope (in)**: Deliver and maintain direct Codex skill source through the supported FlowKit catalog install, refresh, and removal route with ownership-aware conflict handling; follow the installed, versioned workflow definition in a Codex task; define and validate concrete per-step model declarations in workflow YAML and FlowKit reasoning-effort metadata, using medium effort unless a step declaration or one-step operator override specifies otherwise; provide explicit invocation, required-input checks, visible effective assignments, bounded subagent dispatch, same-child continuation for interactive steps, and parent-mediated human decisions; validate fresh installation, refresh, removal, project context, interaction, and workflow outcomes in disposable consumers; document the operator-facing path and manual fallback.
- **Scope (out)**: Model roles or consumer model mappings, duplicating workflow prompts or decision rules in skills, silent fallback or undeclared model selection, invoking a later workflow without separate instruction, changing workflow prompt behavior solely to accommodate the controller, scheduling, Git integration, roadmap verification, or feature acceptance.
- **Depends on**: 011; no dependency on 012.
- **Governed by**: C-02, C-03, C-04, C-05.
- **Notes**: The previously approved thin launcher that delegates to `specify workflow run` is superseded for the Codex desktop path because its separate `codex exec` processes lose the desired task UI. The earlier bundle-installed skill delivery assumption is also superseded: native Specify bundle commands manage their declared Specify components, while the FlowKit catalog route manages direct Codex skills alongside them. Keep the installed workflow as the behavior authority and retain a manual-prompt fallback. The operator accepts that the initial concrete model IDs may be non-portable; model roles and consumer mappings are deferred to a later amendment. Live probes showed a different-model child task and parent-mediated answer relay; they did not prove full Specify integration or YAML model metadata support. The eight skills use stable `flow-kit-*` invocation names and the approved FlowKit display names in the feature specification.
- **Spec dir**: `specs/013-bundle-workflow-launchers/`

### 014 — FlowKit Workflow Improvements  [status: verified]

- **Description**: Review the original eight FlowKit workflows, deliver ten active workflows and retain Start Feature as stop-only deprecated source for correct gates, automation, continuation, and recovery so each operator-invoked workflow can reach an evidenced conclusion or a specific bounded stop. Address the accepted roadmap-linkage, readiness, task-generation, Converge, Close Out, and workflow-resumption findings as consequences of those control-flow gaps, and incorporate Feature 015's reviewed agent assignments with usable repository-local Codex agent configurations.
- **Outcome**: All ten active source workflows and the deprecated Start Feature source have a machine-checkable inventory of steps, branches, gates, assignments, terminal outcomes, and resumption evidence. Each workflow's routine in-scope corrective path reassesses fresh evidence and continues while measured progress remains, stopping at evidenced success, a consequential human decision, a repeated finding, no progress, a finite reviewed cap, or a specific blocker. The controller resumes only from validated, attributable state and never invokes another FlowKit workflow. Every explicitly delegated step uses an appropriate reviewed agent name, and the repository includes usable local configurations for the selected names. Roadmap edits, constitutional changes, material scope or authority changes, Git actions, feature acceptance, and other consequential decisions remain behind their existing explicit human gates.
- **Scope (in)**: Inventory and review all active workflow graphs and the deprecated definition, including branches, human gates, automatic core-command steps, terminal results, interruption/recovery evidence, and delegated-agent assignments; implement the shared controller and recovery support required for evidence-based continuation, fresh reassessment, progress comparison, a finite iteration cap, and safe resumption; update the active workflow definitions and manual-prompt paths to reach an evidenced conclusion or a specific bounded stop, including the approved Clarify continuation and Close Out completion behavior; complete Analyze's shared spec→plan→tasks corrective waterfall and Implement's continuation over existing eligible tasks without wrapper re-specification, re-planning, re-tasking, or analysis; preserve spec→plan→tasks ordering when findings change higher-level artifacts; use only inspectable command/artifact evidence, never command success alone, to claim progress or completion; apply the reviewed Roadmap Agent, Specifier, Planner, Tasker, Reviewer, Coder, Code Reviewer, and Wiki Curator assignments where appropriate and add repository-local Codex agent configuration files; split Start Feature into separately invoked Select Feature and Specify, with dependency discussion, exact human selection/activation, pointer-only selection, and same-target authoring; add a separately invoked Wiki Lint Update loop that lints first, refreshes registered authorized stale sources one at a time, and reports every unresolved issue; maintain a project-owned source-faithful workflow rendering skill and diagrams; collapse equivalent paths while retaining downstream authorization checks and use blocked for required operator input; add a machine-checked inventory and graph/branch fixtures; validate supported and rejected loop shapes, human gates, all-branch assignment preflight, resume state, manual fallbacks, and disposable initialized consumers.
- **Scope (out)**: Invoking one FlowKit workflow from another; undeclared later phases; installing or modifying agent files in consumer projects (a future feature may define bundle installation); silently changing the roadmap or constitution; bypassing consequential human gates; unbounded work or work outside the selected feature; implicit roadmap verification, Git integration, feature acceptance, or project acceptance; independent extension changes without their own review; retrospective edits to verified Feature 007/008 history; unrelated feedback or features.
- **Depends on**: 001, 002, 003, 004, 007, 008, 013, 015; no dependency on 012.
- **Governed by**: C-02, C-03, C-04, C-05.
- **Notes**: Five accepted maintainer intakes and the operator's corrected Converge-loop request define the current change set. `intake-4c31665697a1` records `speckit-flow-start-feature` 0.3.0 (`sha256:ccab39bda126a92f3f3242fc747702525f3677cb6e7ad52cd8211e50681302db`) reaching a roadmap brief without a `Spec dir` mapping despite a correct active feature pointer. Its proposed disposition is a workflow source change to establish or safely stop on the missing specification-to-roadmap linkage. `intake-0e38806b5f69` records `speckit-flow-clarify` 0.2.0 (`sha256:792b68979817fef06bbac3521b0f3034910dba44162a46ca208db27e218d6eb6`) leaving the operator to judge whether significant ambiguity remained after the agent's assessment. Its proposed disposition is an evidence-backed residual-ambiguity assessment and recommendation, preserving operator authority over substantive answers and separate workflow invocation; investigate final-gate presentation without assuming a UI cause. `intake-50695033844a` records `speckit-flow-plan` 0.2.0 (`sha256:5c5cfac1fbad27e5e87f159307bd06cc2efc4c20aa565bc3e126b10014418f21`) presenting an unconditional readiness gate after the operator invoked planning; the operator requested its removal. Its proposed disposition is an agent readiness assessment with a specific stop for missing prerequisites or material product ambiguity, without launching a later workflow. These three records were accepted as proposals, not authorization for source changes. Their local inbox and triage files are excluded from Git.
- **Task feedback**: `intake-1fb76e5dfaca` records a `speckit.tasks` command child asking for an extra design-choice confirmation before generating tasks, despite the operator invoking Tasks; investigate the cause without assuming the installed workflow defines that pre-generation gate. `intake-c95ee8c49f7e` records the operator request to replace the installed post-generation review gate with an agent coverage and completeness assessment that exits successfully when complete and reports specific material gaps otherwise. Both observed `speckit-flow-tasks` 0.2.0 (`sha256:8912f7c87e3ad6204a8cf325aa2823608c54bab37ab148aecb01dce46956ec30`). The second request supersedes the first intake's assumption that the post-generation gate should remain. Both are accepted proposals, not authorization for source changes; their local inbox and triage files are excluded from Git. The operator retains task review and separate Analyze invocation. This entry is the durable scope record for the normal specification, planning, task, implementation, and convergence flow.
- **Earlier Converge feedback (partly superseded)**: The operator chose remediation after `speckit-flow-converge` 0.2.0 (`sha256:90e0970e907ed84ca4c21d6f1b2d9a3d025766b7a2b7f59dacaa8c556481865f`) appended Feature 012 T017, then requested evidence-based routing to the existing Analyze step without a routine human classification gate. The recorded run `.specify/flow-controllers/runs/e5a89918-dbbf-4b1e-9494-2a2c1e31cc04/summary.json` shows the gate. Its proposal to stop after analysis for separate Implement and later Converge invocations is superseded by the operator's subsequent full-loop request; the evidence-based classification and analysis-before-implementation requirements remain.
- **Close Out gate correction**: In Feature 012, the operator authorized changing the existing spec status to `Complete`, and the resulting project state was inspectable. The installed Close Out workflow still required the operator to select `operation-available` before roadmap debrief. Feature 014 must let the agent recognize this routine case from evidence and continue without that classification question; if no authorized completion action or reliable evidence exists, it must stop with a specific reason. The installed `speckit-specify` skill creates a new feature and must not be used as a completion substitute. Preserve explicit approval for the exact roadmap verification patch and separate Git authority. This updates source prospectively rather than rewriting verified Feature 008 history.
- **Close Out debrief continuation**: The first Feature 012 debrief found stale current-artifact completion claims and no verification patch. After those claims were corrected, the operator had to invoke a fresh debrief manually; that second report recommended `verified`. The operator expects the invoked Close Out workflow to perform bounded in-scope reconciliation and rerun debrief itself, stopping only for a material decision, untrustworthy delta, repeated finding, or lack of progress. This is not authority to apply a roadmap patch, commit, or accept the feature without the existing review gates. The current installed workflow has no such loop, so Feature 014 must reconcile this target with the controller protocol and verified Feature 008 prospectively.
- **Converge loop correction**: The operator expects an invoked Converge run to identify gaps, create bounded tasks, flow back to spec and plan when needed, analyze the updated tasks, implement eligible fixes, and repeat Converge until clean or stopped by a real blocker or consequential decision. Constitution 6.0.0 now permits reviewed bounded core-command correction and reassessment inside the selected workflow while continuing to prohibit nested FlowKit invocation. Feature 014 applies that authority prospectively; verified Feature 007 history remains unchanged.
- **Accepted review refinements**: The operator approved the workflow simplifications, shared waterfalls, ten active workflow inventory, deprecated combined source, wiki reconciliation loops, and exact-source rendering conventions during the Feature 014 review. Current source behavior is recorded in the feature artifacts and current inventory. Local commits and static tests are not feature acceptance, release, consumer adoption, or proof of live named-agent behavior.
- **Spec dir**: `specs/014-flowkit-workflow-improvements/`
- **Verification**: The Complete specification, 89 completed tasks, current-task Implement invocation, fresh clean Converge assessment and independent Code Reviewer result are recorded in `specs/014-flowkit-workflow-improvements/validation/implement-current-tasks.json` and `specs/014-flowkit-workflow-improvements/validation/convergence-current-tasks.json`. The fresh debrief `specs/014-flowkit-workflow-improvements/roadmap-reviews/debrief-20261002T152822Z.md` returned `PROCEED WITH UPDATES` with zero Must-Address findings; its two roadmap-stale recommendations are addressed by the current role list and resolved-question/current-route wording. Defined live validation covers 23 scenarios with current source continuity, 127 passing automated tests and installation lifecycle evidence under `validation/live-workflows/`; it does not establish exhaustive branches, native model/effort identity, release, consumer adoption, Git integration or feature acceptance.

### 015 — Named Agents for Delegated Steps  [status: verified]

- **Description**: Let each explicitly delegated FlowKit workflow step name a consumer-configured Codex custom agent.
- **Outcome**: Every delegated step names a reviewed agent; different steps may name different agents. Main-task steps and human gates stay in the driving task. Codex's native subagent activity shows each launched child under a task label containing its reviewed agent name; exact native selection is verified separately, and the child pane shows model and reasoning effort when Codex exposes them.
- **Scope (in)**: A fixed reviewed set of agent names; Specify-compatible per-step agent declarations; explicit delegation; native Codex custom-agent configuration; all-branch named-agent preflight; native subagent visibility; main-task and human-gate boundaries; disposable-consumer and native-runner validation.
- **Scope (out)**: Feature 014 workflow changes and retrospective edits to verified Feature 013 artifacts.
- **Depends on**: 013; no dependency on 014.
- **Governed by**: C-02, C-03, C-04, C-05.
- **Notes**: Architect, Builder, Coder, and Verifier are the reviewed names. Codex owns each agent's optional model and reasoning settings; Feature 015 must prove exact named dispatch in the supported client.
- **Spec dir**: `specs/015-agent-roles-assignment-inheritance/`
- **Verification**: The completed spec, 29 checked tasks, final clean convergence pass, focused tests, and bounded native Codex observations are recorded in `specs/015-agent-roles-assignment-inheritance/validation.md` and `specs/015-agent-roles-assignment-inheritance/roadmap-reviews/debrief-20260929T225206Z.md`. The debrief returned `PROCEED WITH UPDATES` with no Must-Address findings; its two roadmap-stale recommendations are addressed below. This status does not imply a published catalog release or native Specify runner parity.

### 016 — Centralized Workflow Agent Probing  [status: planned]

- **Description**: Replace repeated agent probes across workflow runs with one dedicated workflow that checks every agent name used by the FlowKit workflows.
- **Outcome**: An operator can invoke one workflow to discover and probe each distinct named agent used by active workflow definitions. It reports which agents were successfully dispatched and which could not be verified. Ordinary workflow runs perform no agent probes.
- **Scope (in)**: Discover the distinct agent names from active workflow definitions; run one bounded, non-mutating probe for each name; report results and failures without silently substituting another agent; remove probes from the other workflows; update validation and documentation so the centralized workflow covers the agent-probe requirement.
- **Scope (out)**: Changing workflow agent assignments or agent configurations; automatic probing during ordinary workflow execution; treating configuration presence or no-op dispatch as proof of live named-agent behavior.
- **Depends on**: None.
- **Governed by**: C-02, C-03, C-04, C-05.
- **Notes**: This feature centralizes the agent-probe validation currently included in Feature 014's requirements. It should preserve evidence about which names were tested and what the probe established.
- **Spec dir**: `specs/016-centralized-agent-probing/`

### 017 — FlowKit Agent Configuration and Consumer Delivery  [status: verified]

- **Description**: Prefix the eight project-defined Codex agent names with `FlowKit-`, review their role configurations, select explicit models and reasoning efforts, and determine how those agents are installed into consuming projects.
- **Outcome**: FlowKit workflows use distinct, consistently named agents with reviewed role instructions and explicit model/effort settings. Consumers have a documented, reviewable delivery path whose ownership and lifecycle behavior are decided before implementation.
- **Scope (in)**: Rename Roadmap Agent, Specifier, Planner, Tasker, Reviewer, Coder, Code Reviewer, and Wiki Curator with the `FlowKit-` prefix; reconcile current workflow references, controller expectations, configuration filenames, tests, and documentation; review role scope, instruction quality, model suitability, and reasoning effort for each agent; investigate and select consumer installation, refresh, conflict handling, and removal behavior; validate the selected design in disposable consumers and distinguish configuration checks from live named-agent/model evidence.
- **Scope (out)**: Selecting models or efforts in this roadmap amendment; assuming an installation mechanism or permission to overwrite consumer-owned configurations; unrelated workflow control-flow changes; retrospective rewrites of verified feature artifacts; publication, automatic consumer adoption, Git integration, or feature acceptance.
- **Depends on**: 011, 014, 015.
- **Governed by**: C-02, C-03, C-04, C-05.
- **Notes**: The 2026-10-03 selection baseline had eight unprefixed configurations without model/effort settings and excluded agent acquisition from catalog delivery. Feature 017 now supplies eight exact `FlowKit-` identities, independently reviewed instructions and operator-approved explicit model/effort defaults through canonical `flow-kit-agents` 0.1.0, coordinated with bundle 0.14.0 and controllers 0.6.0. Consumer-owned copies use install-missing, cache-only refresh, explicitly targeted reset and preservation on removal. All 44 tasks are complete; recorded validation passed 55 focused checks and 158 full checks with one environment-dependent class skipped. All-eight exact native launch availability passed; effective settings remain unverified. The separately observed inherited native Specify Clarify transport failure remains a limitation. Component provenance, accepted model-support evidence, source-registry/disposable-consumer distinction and unavailable desktop version remain recorded in `specs/017-flowkit-agent-configuration/validation.md` and `native-dispatch.json`. Feature 016 remains independent; no probing or capacity behavior changed.
- **Verification qualification**: On 2026-10-04 the operator explicitly deferred DEP017-01 catalog Python prerequisite preparation and complete runnable provisioning guidance to a follow-up feature. Delivery behavior and file dispositions were demonstrated in the dependency-equipped tested interpreter; the advertised mise catalog refresh failed without PyYAML. Original unconditional FR-008/FR-011/SC-003 usability is not represented as passed. The unresolved defect, required future outcome and validation are retained in `specs/017-flowkit-agent-configuration/follow-up.md`; no numbered feature or runtime approach is selected. Verification applies to the reviewed nondeferred scope and grants no feature acceptance, publication, adoption or Git integration.
- **Spec dir**: `specs/017-flowkit-agent-configuration/`

### 018 — Reliable Workflow Agent Capacity  [status: abandoned]

- **Description**: Resolve the agent-thread capacity failure that blocks sequential FlowKit workflows in a persistent Codex chat, and provide consumer installation and upgrade guidance.
- **Outcome**: Sequential workflows can launch their declared agents without accumulating completed children until capacity is exhausted. Consumers receive actionable capacity configuration recommendations during installation and refresh while retaining ownership of their Codex configuration.
- **Scope (in)**: Investigate effective supported capacity settings and child lifecycle; preserve outputs before releasing verified completed children through supported controls; retain children awaiting answers or continuation; implement bounded capacity recovery and specific failure reporting; update controller guidance, tests, and documentation; print concise capacity recommendations and a setup-documentation reference from both catalog install and refresh; document how to merge the supported agents.max_concurrent_threads_per_session setting into consumer .codex/config.toml with a value justified by validation; explain effective-setting verification and whether the tested client requires reopening the chat; validate new installs and upgrades with absent, existing, and conflicting configuration, sustained sequential workflow execution, and capacity recovery in disposable consumers.
- **Scope (out)**: Select Feature selection or approval changes; Feature 017 agent configuration and delivery; Feature 016 centralized probing; generic-agent fallback; reuse of probe children for workflow work; cleanup of unrelated chats; silent edits to consumer-owned Codex configuration during installation, refresh, or removal; publication or Git integration.
- **Depends on**: 013, 014, 015.
- **Governed by**: C-02, C-03, C-04, C-05.
- **Notes**: Prioritize observation `clarify-agent-thread-limit-preflight-20261003` as a blocking defect before `select-feature-explicit-choice-reprompt-20261003` and `select-feature-pointer-approval-stop-20261003`. The local journal `.specify/workflow-feedback/observations.jsonl` records installed Clarify 0.4.5 and controller 0.5.3 failing the exact Reviewer preflight after a successful Specifier probe; the effective limit and root cause remain unconfirmed. [Prior capacity recovery](../../specs/014-flowkit-workflow-improvements/validation/live-workflows/capacity-recovery.json) records that reversible archival of verified completed children allowed a fresh named launch; this is historical evidence, not proof of the current cause. Preserve exact named dispatch and fresh bounded work children. A capacity increase alone does not establish resolution; validation must demonstrate sustained sequential use and safe lifecycle handling. Configuration guidance and controller cleanup must explain their complementary roles. Installation, refresh, and removal preserve consumer-owned configuration; no capacity value is selected by this amendment. Features 016 and 017 remain independent and unchanged.
- **Disposition**: Abandoned by direct operator decision on 2026-10-03 because the current approach and specification were rejected. The proposed scope and earlier notes above, feature artifacts, and investigation evidence remain preserved as history; no further implementation is authorized by this entry. The capacity issue remains unresolved, and no replacement feature or approach is selected. Features 016 and 017 remain unchanged.
- **Spec dir**: `specs/018-reliable-workflow-agent-capacity/`

### 019 — Agent Python Environment  [status: verified]

- **Description**: Ensure the agent has the Python environment needed for efficient repository work, with PyYAML available rather than repeatedly discovering it is missing.
- **Outcome**: Documented preparation and a straightforward invocation convention make PyYAML usable in the agent's actual working environment. Additional tools are considered only where recurring tasks or observed failures justify their benefit.
- **Scope (in)**: Agent Python environment preparation; PyYAML availability and direct YAML validation; project guidance for environment use between skill invocations; concise missing-prerequisite recovery; evidence-based consideration and explicit approval of any additional utilities; portable FlowKit-provided instructions and/or reusable configuration for explicit adoption in other projects, with clean second-project and existing-configuration checks.
- **Scope (out)**: Spec Kit/FlowKit runtime coupling or interpreter unification; per-component launchers, capability-report protocols or runtime-management frameworks; workflow/controller reconciliation, automatic consumer migration and catalog lifecycle redesign; external repository or machine-global changes; publication, Git integration or acceptance.
- **Depends on**: 011, 017.
- **Governed by**: C-01, C-02, C-03, C-04, C-05.
- **Notes**: DEP017-01 is motivating evidence, not a mandate to redesign the catalog. Preserve the original missing-PyYAML mise failure and distinct equipped-interpreter retry, accepted model evidence, unverified effective settings and native Specify test limits. Existing dependency references retain provenance; no Specify installation is required by this scope. The reviewed and implemented mechanism is an ignored project-local `.venv`, created from existing mise Python `3.11.16` with existing uv `0.12.5`, containing pinned `PyYAML==6.0.3`. Ordinary agent work uses `mise exec -- python` after `python:prepare` and read-only `python:check`; skill-tools instructions remain respected. The evidence-based utility assessment selected no additional packages. All eleven tasks are complete. Validation records two focused regression tests, fresh seven-task definition validation, direct safe YAML checks, truthful acquisition failure and recovery observations, a disposable second-project guide adoption and existing-configuration preservation. Evidence is limited to the tested macOS arm64 pins; full catalog lifecycle, stock Specify compatibility, publication, real consumer adoption and feature acceptance are not established.
- **Repeatability decision**: The operator requires other projects to be able to adopt the same simple agent environment pattern. Adoption must preserve existing project settings and environments or surface conflicts for explicit resolution; it does not require a new installer or runtime framework.
- **Superseded scope**: Earlier catalog-only, repository-wide FlowKit execution inventory, compatibility and shared-Specify interpreter proposals are retained in historical planning/review artifacts. The operator explicitly rejected that coupling on 2026-10-05. The revised specification governs. The previous integration plan was ineligible after that correction; the subsequently reviewed simple agent-environment plan dated 2026-10-05 replaced it and governs the completed implementation recorded in `specs/019-catalog-python-runtime-prerequisites/plan.md`, `tasks.md` and `validation.md`.
- **Spec dir**: `specs/019-catalog-python-runtime-prerequisites`

### 020 — FlowKit Workflow Iteration and Improvements  [status: verified]




<!-- flow-roadmap-lifecycle {"effect_id":"lifecycle-feea7fc34b5d4018419cbab041634f17","entry_id":"020","executing_phase":"closeout","feature_directory":"specs/020-flowkit-workflow-iteration-improvements","from_status":"in-progress","occurred_at":"2026-10-09T19:39:48.027967Z","owning_phase":"closeout","patch_sha256":"c78666f016c8b300eb132d8a0342867343366435108a5693a4839f8fc11a6f6b","roadmap_before_sha256":"43023e1edca12c9c000fe2d32803c31ab64a73a0fd6212c0346cf736226609e6","run_id":"20e5d4a4-aff8-471d-9ee9-e89ecc909792","scope_sha256":"a3777c5f6a88648c9e704e93d51f13a7c2c910b5fc2a7e4c8a0c03d12fd6cd75","to_status":"implemented","workflow_id":"speckit-flow-closeout","workflow_version":"0.8.0"} -->
<!-- flow-roadmap-lifecycle {"effect_id":"lifecycle-17640d8a7a1b93b3fd5dc03494959646","entry_id":"020","executing_phase":"closeout","feature_directory":"specs/020-flowkit-workflow-iteration-improvements","from_status":"specced","occurred_at":"2026-10-09T19:35:23.038956Z","owning_phase":"implement","patch_sha256":"928df6e52e9f0b2c7737623d75d1731ba964189f74b9cbceccff1fa372c97af9","roadmap_before_sha256":"d232601beb9080da214182653ed295334ac6f2f29771497b2c8ea8fc334b27e4","run_id":"20e5d4a4-aff8-471d-9ee9-e89ecc909792","scope_sha256":"a3777c5f6a88648c9e704e93d51f13a7c2c910b5fc2a7e4c8a0c03d12fd6cd75","to_status":"in-progress","workflow_id":"speckit-flow-closeout","workflow_version":"0.8.0"} -->
<!-- flow-roadmap-lifecycle {"effect_id":"lifecycle-4f2aa461b8a3c0dd36ce037448c9e3ec","entry_id":"020","executing_phase":"closeout","feature_directory":"specs/020-flowkit-workflow-iteration-improvements","from_status":"planned","occurred_at":"2026-10-09T19:22:58.296931Z","owning_phase":"specify","patch_sha256":"5bd1e1767158b596fcd81a20fdf3de7d3984ff9d33eb79b400a6ddf6517973cd","roadmap_before_sha256":"e324fb9c3a241e1a7c7084647faee55c5585be1f3046cc48fd78ebaf91d6fa71","run_id":"20e5d4a4-aff8-471d-9ee9-e89ecc909792","scope_sha256":"a3777c5f6a88648c9e704e93d51f13a7c2c910b5fc2a7e4c8a0c03d12fd6cd75","to_status":"specced","workflow_id":"speckit-flow-closeout","workflow_version":"0.8.0"} -->
- **Description**: Iterate on FlowKit workflows through one bounded feature addressing the five consolidated feedback observations across explicit intent and feature selection, Analyze/Implement checklist readiness, and named-agent availability in future chats and Codex-managed worktrees.
- **Outcome**: Clear operator instructions carry through the requested operations without redundant selection or approval prompts; uniquely resolving feature references are accepted; Analyze leaves an accurate implementation-readiness state; a project installed once supplies FlowKit skills and exact named-agent definitions to future chats in its checkout and Codex-managed worktrees, with tested preparation requirements and explicit reporting of client startup limitations. Specify records `specced` after current authoring and independent quality/brief evidence; Implement records `in-progress` after readiness and eligible-scope checks, before coding; Close Out records `implemented` after full-scope implementation and independent review, before the existing explicit `verified` gate.
- **Scope (in)**: Reproduce and reassess the five observations against current components; reconcile workflow/controller handling of direct authorization, stable feature IDs and menu positions; add declared Implement task-revision steps using exact FlowKit-Tasker for routine in-scope review corrections without repeated reopening approval, preserving history, independent code review, bounded progress and consequential gates; clarify Select Feature lifecycle rules so activation of a planned item without an authored specification retains planned, never implies specced or in-progress, and does not request a separate lifecycle decision solely because activation was requested; define handling for existing specifications and active pointers, with regression coverage for first activation, repeat activation and genuine state conflicts; propose any necessary governing-contract amendments through their explicit human gates; reconcile checklist ownership and preimplementation checks with future implementation and acceptance evidence; verify tracked agent definitions and installed payload propagation through the existing Git and `.worktreeinclude` mechanisms; correct supported project propagation configuration if validation identifies a gap; document one-time project installation and future-session discovery; validate exact native named-agent launches in an existing prepared checkout, a prepared worktree and the first chat created with a new Codex-managed worktree; record any client startup ordering failure without treating it as a missing installation or requiring installation for each chat; define evidence-supported Specify `planned→specced`, Implement `specced→in-progress`, and Close Out `in-progress→implemented` transitions, their phase-owned evidence and bounded ordered recovery of stale state while preserving the explicit `verified` gate; update affected source, documentation and regression coverage; validate each improvement area independently and demonstrate their combined sequential workflow behavior with component, CLI and client provenance.
- **Scope (out)**: An open-ended workflow cleanup backlog; unrelated workflow phases or features; catalog Python prerequisite work referenced as Feature 019/DEP017-01; implementation of Feature 016's centralized probing; reactivation of abandoned Feature 018; agent-thread capacity increases or child lifecycle cleanup; changes to Codex application or runtime code; discovery reload or repair for already-running chats; installation per chat or per agent; guarantees that FlowKit can control Codex chat initialization order; unreviewed model, effort, capacity-setting or lifecycle-control choices; silent consumer configuration changes; generic-agent fallback; implicit later workflow invocation, roadmap verification, Git integration, publication or feature acceptance.
- **Depends on**: 013, 014, 015, 017.
- **Governed by**: C-01, C-02, C-03, C-04, C-05.
- **Notes**: On 2026-10-05 the operator approved reopening T006/T008/T009/T010 for F020-R001–F020-R004 and explicitly added Tasker-owned routine task revision to this feature. This authorizes the scoped task changes and future reviewed source route, not unrelated task expansion or other workflow invocation. The operator explicitly included clarification of Select Feature status-transition rules in this feature on 2026-10-05 after repeated selection and activation instructions produced an unnecessary lifecycle question. Carry this requirement into the specification and task set. The operator requested one work item covering all three areas on 2026-10-05. Provenance: `.specify/workflow-feedback/exports/consolidated-workflow-issues-20261005/report.json` and its Markdown projection in commit `c4ff53c`, report ID `consolidated-workflow-issues-20261005`, integrity `sha256:2ed9a33656c5fa7ddcc0429d43c658c1f91e360c2731cc319a92b8b4bf962776`. Included observation IDs: `select-feature-explicit-choice-reprompt-20261003`, `select-feature-pointer-approval-stop-20261003`, `select-feature-explicit-intent-redundant-gates-20261005`, `analyze-unresolved-checklist-gate-20261003`, and `clarify-agent-thread-limit-preflight-20261003`. These describe earlier observed versions and do not establish current reproduction. Keep the three areas separately traceable in specification requirements, tasks and validation within this single feature. The operator narrowed the agent area on 2026-10-05 to future-session and new-worktree availability after one project installation, using existing supported project configuration, documentation and validation. Feature 018's abandoned proposal and unresolved thread-capacity observation remain historical evidence; this feature no longer promises their capacity remedy. The first-chat startup ordering explanation is a hypothesis to test, not an established Codex lifecycle contract. A fresh-chat workaround may be documented if needed; no FlowKit reinstallation per chat is expected. Feature 016 remains independent and is not a prerequisite unless later review establishes an approved dependency. On 2026-10-07 the operator asked to fix Feature 020's missing phase-owned lifecycle transitions before feature acceptance; the new specification and phase-lifecycle contract define the evidence and decision boundaries. The three original owner effects now record specced, in-progress and implemented at their actual occurrence times; their original scope evidence is preserved. Current closeout applies the operator-approved feature-local T066/T077 manual-validation waiver described below; later dogfooding findings are reported as defects, with no mandatory matrix completion obligation.
- **Verification qualification**: The Complete specification and current independent implementation assessment support the reviewed buildable scope and attributable automated/native validation; the [fresh debrief](../../specs/020-flowkit-workflow-iteration-improvements/roadmap-reviews/debrief-20261009T201232Z.md) recommends verified with zero Must-Address findings. Fresh convergence records 178 feature tests and 28 owner tests passed with zero skips; current independent policy reassessment verifies unchanged implementation/test inputs and does not claim new test execution. On 2026-10-09 the operator explicitly waived the unperformed T066/T077 manual matrices for this feature's closeout and future completion, as recorded in [the current specification qualification](../../specs/020-flowkit-workflow-iteration-improvements/spec.md#feature-020-closeout-qualification) and [waiver ledger](../../specs/020-flowkit-workflow-iteration-improvements/validation/waived-manual-validation.json). Those task rows remain unchecked, zero dogfooding/manual-case observations are recorded, and actor-level manual-path equivalence remains unobserved. Later dogfooding findings are defects for separately authorized work. This bounded verification does not imply feature/The Diagram acceptance, universal availability or adoption, effective native settings, publication, release or Git integration; acceptance and release remain pending.
- **Spec dir**: `specs/020-flowkit-workflow-iteration-improvements/`

### 021 — FarmBoy Project and Workflow Naming  [status: verified]

- **Description**: Rename Spec Kit Flow / FlowKit to FarmBoy through a pure name cutover, including associated skills, workflows, project-owned agents, both feedback extensions and delegation metadata parsing.
- **Outcome**: Consistent FarmBoy names and invocation references with existing workflow and management behavior preserved; no migration feature or compatibility layer.
- **Scope (in)**: Owned branding, repository/bundle identities, skill/workflow/agent names, identifiers, source paths and references; owned feedback capture/report/intake extension, command and skill identities; `flow_kit` → `farmboy` metadata key and owned parsers/validators; current usage/install documentation, packaging metadata and existing test expectations. Obtain a separately approved constitutional identity amendment before implementation.
- **Scope (out)**: Consumer migration or legacy conversion, old-name invocation aliases, new management commands/options, journals/adoption detection/recovery orchestration, checkpoint transfer, future factory behavior, independent command/extension renaming, historical rewrites, external repository renames/publication or Git integration.
- **Depends on**: 011, 013, 014, 017.
- **Governed by**: C-01, C-02, C-03, C-04, C-05.
- **Notes**: Direct operator decisions establish FarmBoy, “Spec et Labora”, `farmboy` project/bundle identity, `farmboy-<purpose>` skills/workflows and `FarmBoy <role>` agents. On 2026-10-10 the operator explicitly removed the migration feature: this is a pure rename, with existing installations handled separately. This supersedes prior consumer-migration guidance scope and derived migration design. The operator also explicitly includes the feedback code and `flow_kit` parser/key in this project; both are owned here. Independent roadmap/wiki and core command identities remain unchanged; nested delegation and feedback data semantics are preserved without old-name adapters. The former planning-only exception is superseded by the operator-approved Constitution 8.0.0 identity amendment and separately invoked implementation. Current correction evidence is recorded in [Closeout correction evidence](../../specs/021-farmboy-project-workflow-naming/validation/closeout-corrections.md). Present-state ledger amendments do not reconstruct historical phase-owner effects or grant verification, acceptance, publication or Git authority.
- **Spec dir**: `specs/021-farmboy-project-workflow-naming`

### 022 — Local Workflow Agent Timing Metrics  [status: in-progress]

- **Description**: Measure each agent invocation made by a FarmBoy skill/workflow using the computer's local wall clock. Start timing immediately before invoking the agent and emit a duration record when that invocation finishes, including the agent name and invoking skill/workflow identity. Provide a separately invoked maintainer-only skill, used from within FarmBoy itself, that gathers the collected records into one Excel workbook. Its settled display name is FarmBoy Metrics Report and its skill ID is `farmboy-metrics-report`.
- **Outcome**: Agent invocations in FarmBoy and its consuming projects emit structured records; a maintainer-only skill used within FarmBoy consolidates those machine-local records into a single XLSX file containing a simple table with one row per metric record. The operator can create graphs and further analysis in Excel. Clock drift and skew are accepted limitations of the requested measurement.
- **Scope (in)**: Timing around agent invocations across active FarmBoy workflows; elapsed duration with a documented unit, exact agent name and invoking skill/workflow identity; a small local metrics adapter API separating emission from collection; an initial adapter writing one uniquely named file per emission in a simple structured intermediate format under the shared machine-local default directory `~/.farmboy/metrics` across consuming projects; concurrent collection without shared-file appends or file locking; visible warnings with workflow continuation if collection fails; the explicitly invoked maintainer-only workbook-generation skill, available within FarmBoy itself, discovering and gathering completed metric files and producing one simple XLSX table while preserving source records; bounded handling and reporting of incomplete or malformed files during collection/report overlap; concise usage, schema, collection and report documentation; focused validation of concurrent emissions and the end-to-end collection/report round trip. Keep the implementation simple and retain the adapter boundary for a later collector without building that collector now.
- **Scope (out)**: Token accounting or monetary cost; CPU-time measurement, distributed timing or clock correction; Prometheus or other remote ingestion, hosted services, a metrics server, charts, dashboards or automatic analysis; installation or distribution of the workbook-generation skill into consumer projects; scheduled reporting, automatic invocation of that skill, deletion of source metrics, shared-file locking, a generalized telemetry framework or an initial configuration-file system; unrelated workflow changes, silent consumer migration, publication, Git integration or feature acceptance. CSV export is not required for the initial XLSX report.
- **Depends on**: 013, 014, 021; no dependency on 016.
- **Governed by**: C-01, C-02, C-03, C-04, C-05.
- **Notes**: Direct operator instructions on 2026-10-11 request basic local timing, explicitly accept drift and clock skew, select `~/.farmboy/metrics` and require warn-and-continue behavior for collection failures. The initial CSV-only collection idea was superseded by permission to use JSONL or another simple intermediate format. The latest operator instruction expands this same feature to include the report skill and an XLSX table, superseding the earlier future-only export exclusion, and calls for one file per emission to avoid shared-file collisions and locking. A self-contained JSON object in each uniquely named file is now the simplicity recommendation; JSONL remains acceptable and the precise format is a specification decision. The operator subsequently restricts the workbook-generation skill to maintainer use within FarmBoy; consumer projects receive timing/emission support, not this skill. The operator settles the display name as FarmBoy Metrics Report and the skill ID as `farmboy-metrics-report`, retaining room for future reporting expansion. The prior provisional name and metrics-workbook recommendation are superseded by this direct decision under the governed `farmboy-<purpose>` convention. Time is the only cost measure. Machine-local collection is shared across projects using FarmBoy; repository-owned source provides the behavior without project-specific hardcoded host paths. API shape, record schema, filename uniqueness, safe publication of completed files and report output location remain specification/planning decisions; a callable local helper is a simplicity proposal rather than a requirement for a network service. Preserve workflow assignments, human gates and failure outcomes independently of metrics. Feature 016's centralized probing remains separate.
- **Suggested dimensions (proposal)**: `run_id`, `step_id`, `invocation_id`, `started_at`, `finished_at`, `outcome` and a short portable `project_label` would support correlation, timing inspection, outcome filtering and separation of consuming projects. Workflow/component version and an attempt number may help later comparisons. These are suggestions for specification, not settled mandatory fields; omit prompts, transcripts, secrets and absolute host paths.
- **Spec dir**: `specs/022-local-workflow-agent-timing-metrics`

## Open Questions

Feature 022's collection/workbook round trip, maintainer-only workbook skill excluded from consumer installation, one file per emission without locking, XLSX table output, initial destination and non-blocking collection policy are settled by direct operator instructions. Resolve these bounded details during specification before implementation:

- Which simple intermediate format and suggested dimensions belong in the first record schema, and what timestamp format, duration unit and project-label convention support the XLSX table?
- How should separate dispatches, same-child continuations, retries, probes, human-answer waits and interrupted or failed invocations be represented so elapsed-time and count comparisons have a clear meaning?
- What simple filename and completed-file publication convention prevents concurrent emission collisions and keeps incomplete files out of reports without file locking? How should the report identify malformed records and define its input snapshot while emissions continue?
- Where should `farmboy-metrics-report` write its XLSX output, and how should an existing output or an empty input directory be handled?

Feature 021's naming and cutover scope are settled by direct operator decisions recorded in its [specification](../../specs/021-farmboy-project-workflow-naming/spec.md). Canonical names are `farmboy`, `farmboy-<purpose>` and `FarmBoy <role>`; old invocation aliases and consumer migration are excluded. Detailed source substitutions and validation follow the narrowed plan.

The previously listed naming/compatibility questions are retained as superseded history:
- Which exact FarmBoy names and identifiers replace the project-owned repository/bundle, skills, workflows and associated agents while preserving independently owned command and extension identities?
- What compatibility, alias, installation, refresh and migration treatment should existing consumers receive without overwriting consumer-owned customizations or evidence?

The governing question was resolved by the explicitly approved and applied [Constitution 8.0.0 amendment](constitution.md) on 2026-10-10. It is retained as superseded historical context:

- What exact constitutional amendment replaces the mandated Spec Kit Flow identities while preserving generic component boundaries and human-directed authority?

The former planning-only exception did not grant that amendment or implementation authority; the operator subsequently supplied those decisions separately.

Feature 019's following planning questions are resolved by its [reviewed plan](../../specs/019-catalog-python-runtime-prerequisites/plan.md), [utility assessment](../../specs/019-catalog-python-runtime-prerequisites/research.md) and [validation](../../specs/019-catalog-python-runtime-prerequisites/validation.md). The selected convention is existing mise/uv with a project-local `.venv`, explicit `mise exec -- python`, one required pinned PyYAML package and no additional utilities. Portable guide adoption remains explicit and preserves existing configuration. The original questions were:

- Which existing preparation and invocation convention gives the agent the required Python environment with minimal complexity?
- Which additional utilities, if any, have demonstrated benefits that justify adoption and explicit approval?

Feature 018's abandoned proposal left these questions unresolved. They are retained as historical investigation context rather than an active work commitment:

- Which supported capacity setting and effective value apply in the tested Codex client, and does the observed failure arise from concurrently open children, retained completed children, or another limit?
- Which supported lifecycle control releases verified completed children while preserving outputs and children still required for same-step question relay or continuation?
- What bounded recovery behavior is safe when capacity is exhausted, and how does the controller preserve preflight and partial-work evidence?
- What capacity value is justified by sustained sequential workflow validation, and how should consumers merge it with existing configuration and verify that it takes effect?
- What should install and refresh report for absent, existing, conflicting, or unsupported configuration, and does the tested client require reopening a chat to apply a change?

Feature 017's selection-time questions, now resolved by its [specification](../../specs/017-flowkit-agent-configuration/spec.md), [approved research](../../specs/017-flowkit-agent-configuration/research.md), [plan](../../specs/017-flowkit-agent-configuration/plan.md), and [validation](../../specs/017-flowkit-agent-configuration/validation.md) within their documented evidence limits, were:

- Which explicit model and reasoning effort suit each agent's responsibilities, and what evidence and supported Codex configuration fields justify those choices?
- Should consumers receive managed agent files, copyable templates, or another supported delivery mechanism, and where should reviewed reusable configuration source live?
- How should installation, refresh, and removal handle existing names, consumer customizations, ownership records, and migration from unprefixed agents?
- Which checks establish exact named-agent selection and effective model/effort settings, and how should unavailable models or unsupported configurations be reported?


Feature 014's planning questions, now resolved by its [specification](../../specs/014-flowkit-workflow-improvements/spec.md), [plan](../../specs/014-flowkit-workflow-improvements/plan.md), and [current convergence evidence](../../specs/014-flowkit-workflow-improvements/validation/convergence-current-tasks.json), were:

- Which reviewed step or component should establish the roadmap `Spec dir` mapping after the specification directory is known?
- How should the operator review an exact linkage patch, and how should missing, stale, or conflicting mappings stop or recover?
- How should the clarify agent classify and explain remaining significant ambiguity without mistaking the five-question session cap for readiness?
- How should the main task present clarification findings and any substantive human questions while preserving separate operator invocation of later workflows?
- Which specification evidence establishes planning readiness, and how should the plan workflow stop with a specific missing prerequisite or material product ambiguity without an unconditional confirmation gate?
- How should Tasks invocation signal authorization to generate from a reviewed plan without masking a material design gap?
- Which task-coverage evidence is sufficient for successful exit, and how should the agent report incomplete or materially divergent task proposals without a routine human review gate?
- Which command output and artifact evidence reliably distinguishes clean, appended-remediation, and blocked Converge results without asking the operator to classify routine outcomes?
- How can one explicit Converge invocation authorize bounded task analysis, implementation, and reassessment under Constitution II, and what governance amendment or scoped authority rule is required?
- When a convergence discovery changes intended behavior or technical approach, which spec → plan → tasks → analysis sequence must complete before remediation implementation resumes, and what stops or iteration bounds end the loop?
- Which disposable-consumer cases prove the start-feature, clarify, plan, tasks, and Converge changes through manual and direct Codex paths?
- Which inspectable spec status and convergence evidence lets Close Out finish the existing completion edit or recognize it as done without an operator classification gate, and what genuine ambiguity must stop the workflow?
- Which debrief findings can Close Out correct and reassess within its invoked scope, and what snapshot, iteration, and nonprogress rules stop repetition before the exact roadmap-patch gate?

Feature 015's planning questions, now resolved by its specification and validation, were:

- Can the supported Codex client select a custom agent by exact name for each delegated child and confirm its instructions load?
- How should a delegated step's agent name and explicit child marker be represented in Specify-compatible YAML while main-task steps remain in the driving task?
- Can the controller validate every possible named child before workflow work, and can the supported Codex client visibly identify each launched agent?
- Which named-agent behavior can native `specify workflow run` support, and how should any difference from the direct Codex controller be documented?

The supported Codex desktop demonstrated exact named selection and agent-specific instructions. Reviewed per-step `flow_kit.delegated` and `flow_kit.agent` metadata, full-graph preflight, and native task-label visibility are specified in `specs/015-agent-roles-assignment-inheritance/spec.md` and evidenced in its `validation.md`. The Specify loader preserved the metadata, while the separate native runner attempt stopped at disposable checkout trust before a delegated step; the documentation records that limit without claiming parity.

Feature 013 settled direct Codex skill delivery through the FlowKit catalog route alongside the Specify bundle. The controller follows the installed workflow definition; the tested Specify CLI accepted its model and FlowKit effort metadata. Disposable-consumer and desktop validation covered project context, same-child clarification, human gates, diffs, and step outcomes within the limits recorded in `specs/013-bundle-workflow-launchers/validation.md`. Its earlier plan for model roles and consumer mappings was superseded by Feature 015's native named-agent design; Feature 013 verification does not claim publication or broader compatibility.

## Cross-Cutting Notes

The separately invoked workflow route is select-feature, specify, optional clarification, planning, task generation, analysis, implementation, convergence, and closeout; start-feature remains stop-only deprecated source. That operational route is distinct from the delivery dependencies recorded above. The maintainer intake component remains outside the consumer bundle.

The operator designated all eleven entries verified on 2026-09-26. Their `spec.md` headers still say `Draft`; this roadmap records the operator's lifecycle decision without rewriting historical feature artifacts. No configured ADR or PRD evidence was available for this creation.

**Version**: 1.30.4 | **Ratified**: 2026-09-26 | **Last Amended**: 2026-10-12

# Feature Specification: Reusable independent plan review and Diagram adapter composition

**Feature Branch**: `025-independent-plan-review`

**Created**: 2026-10-22

**Status**: Approved specification — delivery candidate awaiting human result acceptance

**Input**: Pegagio explicitly selected Farmboy roadmap 025 for specification preparation (Sentinel_524ebeb6bb4c81918af39fa8abd11c2b). This specification proposes reusable upstream behavior based on the corrected Diagram DIAG-10 local composition, without installing or refreshing consumers. Farmboy's canonical tracker is its flow-roadmap ledger; native FB-1 is a mistaken, non-authoritative capture.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Obtain a useful independent whole-plan decision (Priority: P1)

Pegagio explicitly authorizes an independent reviewer to assess one exact implementation plan against the approved specification and real architecture. The reviewer answers the six agreed questions, distinguishes defects from optional improvements, and returns one understandable decision. This reduces human review toil without treating a consistency checker or the plan author as an independent reviewer.

**Why this priority**: The reusable semantic review is the value of this feature; coordination must not obscure the judgment.

**Independent Test**: In a disposable standalone Spec Kit project, a separately authorized reviewer examines an exact proposal and saves an attributable report. A separate evaluator observes the actual skill's review and stopping point, rather than accepting a simulation as runtime proof.

**Acceptance Scenarios**:

1. **Given** explicit bounded human authorization, an approved specification and a complete exact plan/tasks/checklist/design/fresh-analysis candidate, **When** a separate reviewer with no material authorship assesses it, **Then** the report answers all six questions with evidence, records mandate and reviewer, and approves only when no blocker or unmet obligation remains.
2. **Given** a sound plan with only optional non-blocking suggestions, **When** the reviewer decides, **Then** approval may coexist with those suggestions; they create no required correction, approval condition or automatic polishing cycle.
3. **Given** unnecessary machinery or an overly elaborate checklist that can be corrected within approved intent, **When** the reviewer returns findings, **Then** each blocking request identifies the artifact/problem, reason and expected correction, and the disposition returns to planning/tasking/consistency work without redesigning or editing the proposal.
4. **Given** a finding requiring changed product intent, user experience or constraints, **When** review reaches that boundary, **Then** it escalates the specification question, preserves the historical human spec approval, and grants no revised-spec approval.
5. **Given** absent/revoked/ambiguous authorization, uncertain candidate identity, a non-independent reviewer or missing required independent evidence, **When** review is attempted, **Then** it stops incomplete with the precise missing input; it manufactures no decision or authorization.

### User Story 2 — Compose the same review through the optional Diagram adapter (Priority: P1)

In a deliberately Diagram-enabled consumer, Pegagio selects an independent plan review. The adapter obtains or verifies current authority, calls the generic semantic body once, and alone records the result and releases ownership. Diagram remains the lifecycle and authority owner; generic Farmboy stays usable without Diagram.

**Why this priority**: The corrected responsibility split is part of the requested deliverable, not a later coupling patch.

**Independent Test**: In isolated compatible Diagram fixtures, observe direct entry wrapping once, verified inner reuse, returned disposition, exact native finalization and release/readback, plus refusals on stale or foreign context. No live store upgrade or real queued work is required for fixture coverage.

**Acceptance Scenarios**:

1. **Given** an enabled route and no existing inner invocation, **When** the ordinary review entry runs, **Then** it delegates once to the adapter, propagates its result and ends without executing the semantic body a second time.
2. **Given** matching current native feature/review segment, owner/session/run/epoch, candidate, actual grant and caller association, **When** the adapter invokes the body, **Then** the body verifies that context and reuses it without reacquiring, recursively wrapping or changing feature/pointer/branch.
3. **Given** a saved report/disposition, **When** the body returns, **Then** the adapter rechecks actual candidate/report and current grant/authority, checkpoints only authorized report evidence if required, finalizes the native disposition once and verifies ownership release/readback before stopping.
4. **Given** stale/foreign/uncertain authority, revocation or proposal drift before finalization, **When** continuation is assessed, **Then** dependent effects stop; preserved evidence and a supported explicit release or precise unresolved outcome replace invented approval, transfer or recovery.
5. **Given** missing compatible native capability, **When** the enabled adapter entry runs, **Then** it reports the exact blocker without standalone fallback, implicit installation, migration or permissions expansion.

### User Story 3 — Use and adopt the capability without a new framework (Priority: P2)

A consumer can use generic independent review through its existing supported execution context, or explicitly adopt the optional Diagram composition later. Neither upstream delivery nor a report silently changes a consuming project, installs a reviewer, or starts implementation.

**Why this priority**: Portability and clear adoption boundaries prevent a project-local correction from becoming a mandatory coordination system.

**Independent Test**: Focused entry/return tests and a disposable consumer demonstration verify generic use without Diagram imports/native commands, and adapter use without duplicate lifecycle ownership. Actual affected skill behavior must additionally be observed in a real independent Codex session before delivery acceptance, as required by the constitution.

**Acceptance Scenarios**:

1. **Given** an explicitly selected standalone review and sufficient project authority/artifacts, **When** the generic skill runs, **Then** it saves a report and disposition without Diagram inspection or a Diagram dependency, roadmap selection/activation, proposal repair, or another workflow.
2. **Given** an accepted review result, **When** the invocation ends, **Then** it neither launches implementation nor grants result acceptance, integration, publication or a standing future approval mandate.
3. **Given** upstream delivery, **When** a consumer has not explicitly authorized refresh, **Then** its installed/project-local skills and behavior remain unchanged; adoption instructions identify the separate refresh and compatibility step.

### Edge Cases

- A wrapper flag, historical receipt, matching digest or available tool is not current semantic authorization or proof of reviewer independence.
- A historical approval and the latest mutable proposal are distinct; verify actual applicability and report drift, never silently repin or rewrite approvals.
- Unavailable candidate/report/current-authority evidence remains unknown. A failed native finalization is not a successful saved decision; inspect uncertain outcomes before retrying existing operations.
- Partial review or technical failure preserves report/proposal evidence and returns incomplete, not an invented fourth substantive decision.
- A known execution hold or revocation stops the affected decision even if structural native admission previously succeeded.
- Unrelated dirty/staged files are preserved. A required checkpoint that cannot be isolated safely is a precise blocker; no broad staging, cleanup or false cleanliness.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Provide reusable `farmboy-review-implementation-plan` semantic review for one explicitly selected whole-plan candidate in an independent continuous session. Verify actual bounded human authorization, reviewer identity/independence and any required independent evidence under project governance; do not invent a standing mandate, identity service or authentication claim.
- **FR-002**: Verify the approved intent/specification and exact candidate's plan, tasks, checklist, supporting design, fresh consistency analysis and relevant actual architecture. Record exact references and distinguish committed content from base revision plus uncommitted work; uncertain or materially stale input stops dependent review.
- **FR-003**: Answer these exact six questions independently with rationale and relevant evidence:
  1. Are they reasonable for the scope of the feature?
  2. Do they add unnecessary machinery or ceremony?
  3. Do they align with the feature's intent?
  4. Is the architecture sound?
  5. Can the plan and/or tasks be tightened without redesigning?
  6. Is the execution checklist appropriate, or is it overly elaborate?
- **FR-004**: Save one attributable review report in the selected feature's existing validation area, covering candidate identity, reviewer, human mandate/protected intent/constraints, six answers, blocking versus optional findings, required independent evidence and disposition. Use existing artifacts and conventions rather than a new ledger, fixed transport packet or approval database.
- **FR-005**: Return one substantive disposition: approve; return for planning/tasking/consistency changes within approved specification meaning; or specification escalation for an actual product change/question. Approval requires zero unresolved blockers/unmet obligations. Optional findings remain explicitly non-blocking and create no required correction or condition. Technical/missing-input failure returns incomplete without a substantive decision.
- **FR-006**: Keep proposal artifacts unchanged during review. The reviewer must not redesign, repair planning/tasks/analysis, approve a revised specification or rewrite historical approvals. Record delegated decisions truthfully as the delegate's decision under the human mandate, not as direct human review. Approval alone grants no execution authority.
- **FR-007**: Preserve the ordinary verified-context/return seam: an enabled outer entry wraps once and returns once; a verified current inner call reuses authority and performs the semantic body once. Reject stale/foreign/missing context before effects without recursion, automatic acquisition or association changes. Standalone review requires no Diagram service.
- **FR-008**: Put all Diagram-specific grant transport, admission/acquisition or verified reuse, safe report checkpointing, native finalization and release/readback exclusively in `farmboy-diagram-work` and its native reference. The generic semantic body returns its report/disposition, never finalizes or releases native authority or completes a wider coordinator Goal. Diagram enforces its own state, approval and authority invariants.
- **FR-009**: The adapter must revalidate current native authority/grant/candidate and actual report evidence before finalization, preserve attributable results, and distinguish accepted finalization from local semantic completion. Use existing native incomplete/release/uncertainty procedures; add no competing lifecycle owner, retry controller, lease or recovery service.
- **FR-010**: Stop after the selected review's disposition or truthful incomplete outcome. Do not automatically repair, re-review, launch implementation or another workflow, add a scheduler, or infer result/integration/publication authority. Preserve execution holds, mandate limits and revocation.
- **FR-011**: Include focused portability and entry/return coverage for standalone independence, one outer wrap, matching inner reuse, stale/foreign refusal, one native finalization/release, failure/uncertainty and no next workflow. Keep tests proportionate and reuse existing mechanisms; fixtures do not prove live model obedience. Demonstrate actual affected skill interactions/stops in a real Codex session with a separate evaluator before runtime delivery acceptance.
- **FR-012**: Document generic usage and the optional Diagram route/compatibility and explicit later consumer refresh. Do not onboard Farmboy to Diagram, change live controls/schema, refresh consumers or install tooling as an effect of this feature. Use the integrated DIAG-10 correction as reference evidence, not a required generic dependency or authority to copy project coupling.

### Key Entities

- **Review candidate**: One feature's exact approved intent and reviewable proposal/architecture references, with current applicability and actual working-state observations.
- **Human mandate**: Explicit authorization for the named independent reviewer and bounded whole-plan role, protected intent, expected experience, constraints and any required independent evidence. It is existing attributable evidence, not a new stored service.
- **Review report/disposition**: The six answers, evidence and findings, plus approve, planning return, specification escalation or truthful incomplete outcome. The report does not itself acquire execution authority.
- **Adapter context**: Existing caller association and current native facts verified through the adapter reference; no new token, packet, owner or lifecycle.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Each complete review answers all six exact questions with attributable evidence and one unambiguous disposition; no blocking issue can coexist with approval, while an optional-only case can approve without a polishing loop.
- **SC-002**: Standalone and coordinated scenarios produce the same semantic assessment for the same proposal and mandate, while only the adapter performs native effects. Entry/return observations show one body execution, no duplicate acquisition/finalization and no next workflow.
- **SC-003**: Every negative boundary scenario stops without unauthorized approval, proposal edits, invented state or permission expansion, and identifies the exact missing/revoked/stale/uncertain input plus preserved work.
- **SC-004**: The portable disposable-consumer example and focused tests pass, and a separate evaluator records actual real-session skill behavior and human stopping points before delivery acceptance. Simulations or structural native acceptance alone do not satisfy this criterion.
- **SC-005**: A user can locate the report, understand required versus optional action and its next human/selected-workflow boundary, and adopt generic/optional adapter usage explicitly without a new controller or implicit installed consumer change.

## Assumptions

- Current constitutional bounded delegation permits an explicit independent reviewer mandate; it delegates no role automatically. No constitutional amendment is proposed.
- Roadmap 002 and 005 are verified prerequisites. Historical workflow specifications remain intact; this feature adds a reusable review entry and the optional adapter's matching composition.
- Existing generic execution context, artifact references and native Diagram DIAG-10 contracts suffice. Packaging/internal edits and focused verification mechanics belong to later planning, not this product specification.
- The reviewed Diagram correction is integrated at `d29c0809f722985bf2fd2a7fd5cfd8a2e4ce573e`. Installed Diagram/live store remain schema19; its schema20 review support is not installed. No current live review launch or upgrade is implied.

## Historical preparation handoff and fit

The effective core spec template was resolved through the installed Spec Kit command, and standard create-new-feature established this isolated worktree's literal `specs/025-independent-plan-review` pointer. Standalone Farmboy specification preparation was used; no native Diagram operations, planning/tasks, implementation, consumer refresh or real independent reviewer launch occurred. No native Goal was selected or created.

Wiki query supports standalone/external entry, caller association and return separation ([workflow handoffs](../../wiki/pages/workflow-handoffs.md), S011) and optional adapter routing/reuse/release separation ([optional adapter](../../wiki/pages/optional-diagram-adapter.md), S012). Coverage is partial for this new independent reviewer: those pages predate the correction and the adapter page's runtime version note is stale. The actual installed-source reference and expressly authorized Diagram correction informed this draft directly; no wiki update is claimed. Later authorized ingestion of this feature and current adapter docs can fill that gap.

At the saved preparation checkpoint, roadmap025 was activated/linked and its formal ledger status remained planned pending authoring assessment/review. Requirements and quality checks assess draft completeness, not a claim that future tests have run. At that handoff no material clarification remained and whole-spec approval/planning were still pending; no planning, implementation or commit had begun. Its source base was `e5f8bbf76f74da9898518e820aca936c54e2dcae` with the named draft and scoped roadmap amendment uncommitted.

## Current delivery handoff

The original whole-spec approval remains pinned to SHA-256486a4c5240b5d3e9e5b7a4ffe876717ad67e115c59cd75858046c7bdc4fbfcfe (retained exactly at checkpoint29a17983), and whole-plan approval to c950554e2fb5bf0fb7fab2f5cfa90e70d11286f0e6e9e9b2bdfa0546113de1fc. The approved requirements, scenarios, success criteria and assumptions are unchanged; current source metadata and historical handoff labels are reconciled only. Authorized implementation, controlled/private checks and actual independent skill evaluation are recorded in validation/verification.md. The former sandbox checkpoint gap was resolved by the reviewer’s own supported per-action approval, real report commit and accepted native disposition/release; no protection bypass. Human result acceptance remains pending. No installation, consumer refresh, native Farmboy onboarding, live migration, merge, push or automatic next phase.

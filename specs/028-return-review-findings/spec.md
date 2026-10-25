# Feature Specification: Return workflows consume plan-review findings

**Feature Branch**: `028-return-review-findings`

**Created**: 2026-10-25

**Status**: Draft — Needs clarification; not approved

**Input**: Pegagio selected initial specification preparation for native FARM-28. See [captured request](request.md). Source baseline: integrated FARM-27 at `20bbd66a941706c28d5afa959c8348031c405494`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Correct the findings that caused a planning return (Priority: P1)

After an independent reviewer returns a proposal for planning, tasking or consistency corrections, Pegagio separately selects the existing planning workflow. It reads the applicable committed review before revising the proposal, addresses the findings driving that return, and records how each was handled in the existing proposal and analysis notes. The reviewer itself has already stopped.

**Why this priority**: A return must lead to the requested corrections rather than another proposal that silently repeats the same problems.

**Independent Test**: Return a proposal with two required corrections, then separately select planning. Observe both findings consumed, their resulting changes linked in existing artifacts, fresh consistency assessment and the ordinary full-plan review handoff.

**Acceptance Scenarios**:

1. **Given** a current planning-return report with required changes to task coverage and approach, **When** planning is separately invoked, **Then** it reads the full applicable report before affected work and traces each required finding to a correction and current supporting evidence.
2. **Given** a return containing optional advice alongside required corrections, **When** the next workflow revises the proposal, **Then** it treats required corrections as obligations, keeps optional advice optional, and records considered advice as adopted or declined with a concise reason in existing notes.
3. **Given** a required correction cannot be resolved within approved specification meaning, **When** the next workflow assesses it, **Then** it preserves work, identifies the exact product question and stops for the affected human specification review rather than weakening the requirement or claiming a complete proposal.

### User Story 2 - Address a specification escalation without approving it (Priority: P1; conditional on Q1)

When review identifies a product-intent issue, Pegagio separately selects the applicable specification revision or clarification workflow. It consumes the report's actual product question, records its relationship to the specification changes or unresolved question, and returns to human specification review.

**Why this priority**: A technical correction workflow must not silently change or approve product intent. Whether this branch belongs in this feature remains Q1.

**Independent Test**: Escalate an actual intent question in a review, then separately select specification work. Observe report consumption and a saved question or revised draft, with no inferred specification approval or planning launch.

**Acceptance Scenarios**:

1. **Given** a current specification-escalation report, **When** the operator selects specification work, **Then** it reads the report and carries the finding into the existing specification notes and genuine product clarification where needed.
2. **Given** a product answer requires changed meaning, **When** that answer is saved, **Then** the revised draft awaits explicit human specification review; historical approval remains historical and grants no approval of the changed meaning.
3. **Given** no product answer is available, **When** preparation reaches its handoff, **Then** it saves the precise unresolved question and stops rather than inventing an answer or keeping preparation running through clarification.

### User Story 3 - Use the correct evidence and preserve resolved history (Priority: P1)

Pegagio can tell which review caused the return and why a finding requires current action. Old reports are not silently treated as current, and valid recorded resolution is not lost merely because artifacts have evolved.

**Why this priority**: Addressing the wrong report can produce convincing but irrelevant corrections or repeated work.

**Independent Test**: Supply wrong-feature, wrong-candidate, wrong-route, missing and altered report cases, plus an older finding with applicable resolution evidence. Observe precise stops for invalid evidence and reuse of valid resolutions without reopening settled work by default.

**Acceptance Scenarios**:

1. **Given** a report for another feature, candidate or return route, or bytes inconsistent with its committed evidence reference, **When** the selected workflow checks applicability, **Then** it stops affected work and identifies the mismatch without guessing a replacement report.
2. **Given** an earlier finding with recorded correction or supersession applicable to the current proposal, **When** the next workflow consumes the return evidence, **Then** it cites that resolution and identifies any remaining obligation instead of silently discarding the finding or repeating resolved work.
3. **Given** ambiguous resolution or conflicting report and current disposition, **When** the workflow assesses the return, **Then** it saves the precise missing evidence or decision and stops dependent work; priority alone supplies neither resolution nor blocking status.

### Edge Cases

- Multiple historical reports exist: use the report or report set applicable to the current return, preserving separate reviewed-candidate and report references; newest filename or latest commit alone is insufficient.
- Artifacts have changed since review: compare current changes and existing resolutions with the reviewed candidate. Commit difference alone does not invalidate all evidence or require another review.
- A low-priority finding is required: address it before reporting a complete return. High-priority optional advice remains optional unless its substance reveals an unmet obligation; ambiguity requires an explicit resolution.
- Required report references are unavailable through supported coordination inspection: stop with the exact missing capability/reference, preserving current artifacts; do not inspect private storage or invent a binding.
- A standalone consumer has no Diagram: use its explicit current return/report/candidate evidence under its own governance, preserving the same semantic checks without making Diagram mandatory.
- The requested next workflow is not authorized: finding a report or recording a disposition never launches that workflow or grants ownership/approval.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: For each included return branch, the next separately selected existing Farmboy workflow MUST locate and read the full applicable committed review before acting on the affected proposal or specification. Review finalization MUST continue to stop without invoking the returned workflow.
- **FR-002**: Evidence applicability MUST establish the same feature, reviewed candidate and current return disposition, including actual committed report integrity. Unavailable, ambiguous or mismatched evidence MUST stop affected work with the exact missing reference, capability or decision; no newest-report guess or fabricated association is allowed.
- **FR-003**: The returning workflow MUST identify each required finding driving the return, explain its disposition, and link its correction, applicable existing resolution/supersession evidence, or unresolved reason in existing affected feature artifacts. An unresolved required finding MUST prevent a successful complete handoff; it may support a truthful incomplete/input handoff.
- **FR-004**: Routine planning/task/analysis repairs MUST preserve approved intent, reconcile affected current artifacts and undergo the established fresh consistency assessment before the ordinary full-plan review handoff. No actionable inconsistency or unmet requirement may become optional merely to finish.
- **FR-005**: Included specification-return work MUST carry actual product questions into the existing specification/clarification path, avoid invented answers, and preserve explicit human specification review and approval before later planning. Required scope/intent changes discovered on planning return MUST stop at that boundary even if specification-return handling is deferred by Q1.
- **FR-006**: Historical findings MUST remain distinguishable from current unresolved obligations using existing resolution/applicability evidence. Neither a previous approval nor changed artifact revision alone proves a finding resolved or invalidates every historical decision.
- **FR-007**: Required/blocking status MUST be distinguished from priority. Optional advice MUST remain voluntary, with concise adopted/declined reasons in existing notes; ambiguous advice describing an unmet obligation MUST be surfaced rather than silently ignored or promoted solely by priority.
- **FR-008**: Farmboy MUST own semantic interpretation/correction and support standalone consumers. Its optional Diagram adapter MUST supply authoritative current evidence references using supported native records; Diagram MUST retain coordination/approval authority. This feature MUST NOT require a new tracking subsystem, ledger, report format, schema, runtime transition or launcher/control change.
- **FR-009**: Execution MUST remain within the selected workflow and current authority, preserving one owner, existing helpers/hooks, immutable integrated history and human gates. No automatic repair by the reviewer, next-workflow launch, approval, installation, consumer refresh, integration or publication is authorized by return evidence.
- **FR-010**: Final branch scope is [NEEDS CLARIFICATION: Should FARM-28 cover both planning-return and specification-return consumption together, or cover planning-return now and defer specification-return consumption to a later explicitly selected feature?]. Story 2 and its dedicated consumption behavior in FR-005 are provisional until this decision; the mandatory stop on changed product meaning applies in either option.

### Key Entities *(include if feature involves data)*

- **Applicable return review**: Existing committed report, reviewed candidate, attributable disposition and current evidence references explaining why work was returned; distinct from the revised proposal.
- **Finding disposition**: Existing artifact note identifying the finding and its correction/resolution, voluntary advice decision or precise unresolved input, with supporting references. This is content in existing artifacts, not a new tracking object.
- **Review boundary**: The existing human specification or full-plan decision required after the selected workflow; a workflow handoff does not itself make that decision.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In each included return scenario, every required finding driving the return has a traceable current correction/resolution or explicit unresolved reason; zero unresolved required findings coexist with a claimed complete successful return.
- **SC-002**: All tested wrong-feature, wrong-candidate, wrong-route, missing and altered report cases stop before affected work with a precise explanation; the resolved-history case reuses applicable evidence without automatic repeated repair.
- **SC-003**: Every observed included return ends at the prescribed human/input boundary with zero inferred approvals, reviewer-triggered next workflows or changes outside the selected scope. The product-intent escalation case always preserves the human specification gate.
- **SC-004**: Standalone and coordinated examples provide equivalent semantic handling using existing artifacts; no additional tracking subsystem or runtime/schema/control change is needed. Before delivery acceptance, actual affected skill interactions and stopping points are observed in a real session evaluated separately from execution; simulations alone do not establish acceptance.

## Assumptions

- Existing reusable review production and its stop behavior remain authoritative. FARM-28 changes downstream consumption and amends related workflow behavior prospectively; it does not rewrite integrated FARM-25 or FARM-27 history.
- FARM-27 is the complementary approved-plan delivery branch and provides established evidence/disposition semantics to reuse. No native execution dependency is implied by this relationship.
- The planning composite is the return entry for planning, tasking and consistency corrections; this draft does not add independent automatic invocations of those commands or change core Spec Kit command contracts.
- Existing current-feature specification, proposal, analysis and ordinary notes suffice for dispositions. Verification and internal edit placement are later planning decisions after scope clarification and whole-spec approval.

## Preparation notes and request fit

Verified external inner specification preparation reuses FARM-28 specify/draft run `run/db5cf9d81d1c115bc7c1583c2fbc630b`, epoch 2, Feature revision 2 / queue 3, owner `pegagio-agent-farm28-spec`, session `farm28-spec-20261025`. The conventional local pointer and effective directory are literally `specs/028-return-review-findings`; actual adopted repository/common-Git/worktree identities and committed request bytes were checked before native link. The outer adapter endpoint is saved draft/checklist, actual checkpoint, native clarification/review handoff and released-owner readback. No active native Goal was selected or created.

The installed project-pinned Spec Kit `1.0.10.dev0+pegagio.2` resolved the effective core specification template. Direct draft/checklist authoring follows the preparation workflow; the full interactive specify command was not run, no planning command was invoked, and its interactive questions were not simulated. Existing extension hooks have only optional post-plan/post-implementation ingestion; no mandatory hook is due for this drafting body. This feature pointer is intentionally ignored local state.

Constitution Principles I–IV and current direction support reconciliation, proportionate composition, explicit workflow selection and human review. Existing FARM-25 defines report production and stopping; FARM-27 defines delivery consumption, priority/required distinction and applicable historical resolution. Their integrated artifacts remain unchanged. The captured open scope question is retained as Q1, not silently decided by drafting.

Bounded read-only wiki query: [independent plan review](../../wiki/pages/independent-plan-review.md) (S013, S014), [optional adapter](../../wiki/pages/optional-diagram-adapter.md) (S012, S013, S014), and [workflow handoffs](../../wiki/pages/workflow-handoffs.md) (S011), with source IDs verified in the registry, support existing report/authority separation and human stops. Coverage is partial: those pages do not define downstream return consumption or decide Q1. The current FARM-28 request and eventual approved feature are the concrete source for that gap; no wiki changes were made.

**Handoff: Needs clarification.** Q1 above is the only material product question. The next operator-started step is ordinary `speckit-clarify` under separately acquired current native clarification authority. Its answer must reconcile this draft/checklist and then return to human whole-spec review. No approval, planning, implementation, integration, installation, push, schema/control change or BGG work occurred.

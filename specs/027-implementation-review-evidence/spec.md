# Feature Specification: Implementation consumes current plan-review evidence

**Feature Branch**: `027-implementation-review-evidence`
**Created**: 2026-10-24
**Native identity**: FARM-27
**Status**: Awaiting human specification review
**Input**: [Existing captured request](request.md): read applicable committed plan-review evidence before implementation, consider optional suggestions, and retain concise decisions in existing delivery notes.

## Problem and scope

A plan approval can reference a committed review that includes useful optional suggestions. Today the implementation context explicitly includes plan/tasks/design/research, but does not explicitly require reading that review. The delivery workflow retains closeout evidence without requiring a decision on each optional review suggestion. The operator cannot reliably tell whether the implementer considered those suggestions or noticed review findings inconsistent with approval.

This feature adds that bounded consumption and decision step to Farmboy's selected delivery workflow before its ordinary implementation invocation, on both standalone and externally coordinated routes. Bare core-command use outside that Farmboy workflow is outside this change; this boundary is a material review choice. An **applicable report** is the committed review associated with the selected feature's currently approved plan through its authoritative approval/handoff or the standalone rule below. “Current” means applicable to that approved meaning and candidate, rather than newest by date or filename. A **blocking finding** identifies an unresolved defect, required correction or unmet obligation that prevents implementation under the approval. Priority expresses importance; it does not alone establish blocking status.

FARM-27 changes neither review production nor approval/state authority. FARM-28, which addresses findings during return/replanning workflows, is separate. This specification amends the current behavior described by FARM-3/FARM-5/FARM-25 through a new feature; historical artifacts remain intact.

## User Scenarios & Testing

### User Story 1 - Read the review that actually supports approval (Priority: P1)

An authorized implementer starts from the current approved plan and reads its applicable committed review before any implementation effects, including project setup changes.

**Why this priority**: Approval metadata alone does not reveal the report's substantive findings.

**Independent Test**: Present a selected approved candidate alongside correct and decoy reports. Observe which committed bytes are read and whether execution stops before changes when evidence cannot be established.

**Acceptance Scenarios**:

1. **Given** a Diagram-approved plan with authoritative review evidence, **When** implementation begins, **Then** the adapter locates the report commit/path/digest through current native handoff/approval facts; Farmboy verifies the committed bytes and their selected-feature/candidate relationship, reads the whole report, and assesses its findings before implementation.
2. **Given** a newer report for another feature/checkpoint and an older report that supports the current approval, **When** selecting evidence, **Then** the applicable authoritative report is used. Date, conventional location and file existence alone cannot override authority.
3. **Given** a report that is missing, uncommitted, unreadable, digest-mismatched, associated with a different candidate, or contradicted by approval facts, **When** that report is required/applicable, **Then** implementation stops with the exact evidence gap and current references in existing notes. No substitute report, approval or successful delivery is fabricated.
4. **Given** routine flow-back preserving approved meaning with existing applicability evidence, **When** resuming work, **Then** the reviewed checkpoint remains distinct from current artifacts and does not force re-review solely because their commits differ. Materially changed meaning or unresolved applicability stops affected work under existing gates.

### User Story 2 - Catch unresolved obligations without turning advice into requirements (Priority: P1)

An implementer verifies that the review and approval permit work, while retaining the freedom to decline optional advice.

**Why this priority**: An approval must not conceal an unresolved blocker, and optional advice must stay optional.

**Independent Test**: Compare unresolved required findings, high-priority blocking findings, explicitly optional high-priority suggestions, resolved history and ambiguous contradictory classifications.

**Acceptance Scenarios**:

1. **Given** a current unresolved required finding or blocking finding, including a high-priority blocking finding, **When** approval otherwise appears to allow implementation, **Then** Farmboy stops before implementation and reports the inconsistency. Low priority does not waive a required correction or unmet obligation.
2. **Given** an explicitly non-blocking optional suggestion, even one labeled high priority, **When** it identifies no defect or unmet obligation, **Then** its priority alone does not block work or compel adoption. A report that simultaneously calls the same unresolved obligation optional is inconsistent and requires resolution, not semantic relabeling by the implementer.
3. **Given** historical required findings with identifiable resolution/supersession evidence applicable to the current approved plan, **When** assessing current blockers, **Then** Farmboy distinguishes them from unresolved findings and does not block solely because the historical text remains. An unsupported assertion of resolution is insufficient.
4. **Given** ambiguous current status or conflicting report/approval classifications, **When** no supported current evidence settles the conflict, **Then** Farmboy saves the precise unresolved question and stops; it does not revoke approvals, transition returns, repair the plan or launch re-review automatically.

### User Story 3 - Retain concise optional decisions across ordinary delivery and standalone use (Priority: P2)

The operator sees which optional suggestions were considered and why each was adopted or declined, using existing notes and workflow authority.

**Why this priority**: Deliberate decisions should survive closeout without a new tracking process.

**Independent Test**: Deliver a candidate with two optional suggestions through existing notes, and repeat with a non-Diagram consumer whose governance does not require a review report.

**Acceptance Scenarios**:

1. **Given** optional suggestions in an applicable report, **When** implementation proceeds, **Then** each is considered before the related implementation decision, and existing delivery/closeout notes record its report identifier/location, adopted or declined, and a concise reason by closeout. Declining a genuinely optional suggestion needs no new approval.
2. **Given** an adopted suggestion already covered by the approved plan, **When** implemented, **Then** notes identify that coverage; adoption is not claimed merely because it was considered. A suggestion needing work outside current authority is declined for this delivery with that reason, or dependent work stops for an actual necessary decision under existing rules. It never expands scope by itself.
3. **Given** an interrupted/resumed delivery, **When** the same applicable evidence and decisions remain valid, **Then** existing decisions are reused without duplicate notes or implementation. Changed relevant evidence/meaning is reassessed, preserving historical decisions as history.
4. **Given** a standalone or other non-Diagram consumer, **When** its current approval explicitly identifies a committed plan-review report or its governing workflow requires one, **Then** the same consumption/blocker/disposition behavior applies using existing Git and approval evidence. A report required but not identifiable causes a precise stop.
5. **Given** a non-Diagram consumer with neither a report-bearing approval nor a governing report requirement, **When** implementation starts, **Then** it records that no plan-review report applies and proceeds under its existing approvals. It does not require Diagram, invent a review obligation or select a stray report based only on its filename.

### Edge Cases

- No optional suggestions: record the applicable report and that none require disposition; do not invent suggestions or polishing work.
- A report remains at the conventional path but its working bytes differ: use verified committed evidence; disclose a relevant conflict rather than silently substituting local edits.
- Several referenced reports remain authoritative: consume the applicable set needed to interpret the current approval and explicit resolution/supersession evidence; do not treat all historical reviews as current or pick arbitrarily. Unsettled authority is a stop.
- If an optional suggestion exposes an actual unmet obligation, ordinary required-gap rules apply; it cannot be declined as advice simply to obtain clean delivery.
- A bare core implementation command does not acquire Farmboy composite authority or this composite's new behavior merely because its source is present. This feature does not patch core or make that command invoke delivery/convergence. The selected Farmboy delivery workflow consumes the evidence before calling it.
- Missing evidence or a genuine blocker preserves work and existing authority/release rules. This feature authorizes no control changes, recovery, acquisition retry or approval invalidation.

## Requirements

### Functional Requirements

- **FR-001**: Before implementation effects on each new or materially changed applicable input, Farmboy MUST establish the applicable committed report(s), read their full content and assess findings alongside the current approved plan. Ordinary resume MUST preserve/reuse valid prior assessment and reassess affected changes rather than replay work. Story 1 and Story 3.3 define acceptance.
- **FR-002**: The optional Diagram adapter MUST locate authoritative review references from current native handoff/approval facts. Consumer verification MUST check report path/commit/digest, selected feature/reviewed candidate and approval applicability using existing evidence. A differing current commit alone MUST NOT invalidate routine flow-back that preserves approved meaning. Missing, conflicting or unverifiable required evidence MUST stop dependent implementation with precise references/reason. Story 1 defines acceptance.
- **FR-003**: Farmboy MUST interpret findings and stop on any current unresolved required correction, blocking finding or unmet obligation inconsistent with approval. Priority alone MUST NOT turn explicit non-blocking optional advice into a blocker. Resolution/supersession must be evidenced and applicable, rather than inferred from approval alone. Unsettled ambiguity MUST stop for the exact missing resolution. Story 2 defines acceptance.
- **FR-004**: Farmboy MUST consider every applicable optional suggestion and record adopted/declined plus concise reason and report item reference in existing feature delivery/closeout notes. No new report format, registry or fixed ledger is required. With no optional suggestions, a concise “none” is sufficient. Decisions MUST be preserved and reconciled on resume and before closeout. Story 3 and edge cases define acceptance.
- **FR-005**: Optional adoption MUST remain voluntary and within selected authority and approved meaning. Adoption MUST flow through affected current artifacts under existing rules; material changes retain affected human review. Declining genuine advice MUST NOT force approval, correction, automatic re-review or a polishing cycle. It MUST NOT waive an actual unmet obligation. Stories 2–3 define acceptance.
- **FR-006**: For non-Diagram consumers, the applicable-report rule MUST be explicit and small: use report(s) explicitly supporting current approval or required by governing workflow; verify their existing committed evidence. Without either condition, record not applicable and retain existing behavior without Diagram lookup or a new report requirement. Story 3.4–5 defines acceptance.
- **FR-007**: Farmboy MUST own semantic assessment and implementation/closeout instructions; Diagram MUST retain state/approvals and authoritative evidence references. Place consumption before the selected Farmboy delivery workflow invokes ordinary implementation; cover its standalone and external routes without granting bare core-command use composite authority or running the body twice. Use actual existing integration points; do not assume skill ownership from names. The source-fit notes below identify observed boundaries, not a prescribed implementation design.
- **FR-008**: Preserve existing human gates, safe ownership/release behavior, standalone consumers and historical evidence. Add no tracking system, report framework, schema, blanket re-review requirement, return/replanning implementation, installation, launcher/control behavior, or consumer deployment requirement. This specification invocation makes no BGG changes and starts no later segment.

### Key Entities

- **Approved plan and applicability evidence**: the selected feature, approved meaning/candidate, attributable approval and any existing resolution or routine flow-back context.
- **Applicable committed review**: existing report bytes identified by path, commit and available integrity reference, with reviewed candidate, findings and disposition. No new storage model is introduced.
- **Optional decision**: an existing report item's adopted/declined outcome and concise reason retained in ordinary delivery notes.

## Success Criteria

### Measurable Outcomes

- **SC-001**: In every selected-report acceptance case, the implementer consumes the review supporting the current approval before changes; every missing/corrupt/wrong-feature/wrong-candidate required-evidence case stops before changes.
- **SC-002**: All unresolved required/blocking cases stop; all evidenced resolved-history cases and unambiguously non-blocking optional-priority cases avoid a false blocker. Ambiguous contradictions are reported without inferred approval.
- **SC-003**: Every applicable optional suggestion has one inspectable adopted/declined decision with a concise reason at closeout; resume preserves valid decisions without duplicate work.
- **SC-004**: Both report-applicable and report-not-required non-Diagram cases preserve their existing authority and work without a Diagram dependency or a newly imposed review.
- **SC-005**: The changed workflow is observed in an actual Codex executing session separate from its evaluator before delivery acceptance, including evidence reading, decision notes and required stops. Static/fixture assertions alone do not establish runtime acceptance. This is future verification, not work performed during specification.

## Assumptions

- Existing review reports distinguish required/blocking findings from optional suggestions and identify the reviewed candidate. When they do not, the implementer reports the gap rather than inventing classification or a new schema.
- Existing Git artifacts and attributable approvals/resolution evidence suffice. No new per-finding machine state or approval register is needed.
- Necessary context comes from the currently approved plan and applicable evidence, not all historical reviews. An unchanged applicable approval remains valid; this feature does not impose upstream integration or blanket re-review gates.

## Source fit and review handoff

The verified inner `farmboy-prepare-specification` invocation uses the adapter's current FARM-27 specify/draft run and contained literal pointer `specs/027-implementation-review-evidence`. The whole outer endpoint is the saved specification/checklist checkpoint, native review handoff and released ownership. No standalone roadmap activation, interactive clarification or later workflow is invoked.

Inspected at base `f24d4753ce2d76b777b65e8fcd04799f1dac4977`:

- `.agents/skills/speckit-implement/SKILL.md` explicitly loads tasks/plan and optional design/contracts/research/constitution/quickstart before setup changes. It has no explicit plan-review consumption rule. It is an existing core command source; its name does not grant this feature permission to modify upstream/core software. The bounded behavior belongs before this command is invoked by Farmboy delivery. Bare core-command invocations remain outside FARM-27; no permission to patch core is inferred.
- `.agents/skills/farmboy-deliver-approved-plan/SKILL.md` owns implementation invocation, convergence and existing feature-level delivery notes; it distinguishes optional advice from required gaps and preserves external/standalone routes. Its closeout notes are the existing durable disposition destination.
- `.agents/skills/farmboy-diagram-work/SKILL.md` and adjacent `references/native-protocol.md` own Diagram context/approval transport, verification and release. Native review evidence already has commit/artifact path/digest references. `docs/review-implementation-plan.md` assigns semantic judgment to Farmboy and distinguishes optional-only approval from unresolved blockers. No native schema change is needed.
- Constitution I–IV and `docs/direction.md` preserve scope, flow-back, standalone operation, runtime evidence and human gates. The old roadmap is historical; FARM is authoritative under its acknowledged cutover. No governing conflict was found in this bounded proposal.

The supplied BGG-1 example at `db561f32c42655b35118a0fd9a63c51ad009150b`, report `specs/001-collection-reads/validation/plan-review.md`, O1 (SDK native frame-size limit), motivates Stories 1 and 3. It is user-provided read-only evidence, not a BGG execution or independent verification claim. No BGG repository, token, controls, approval or workflow was accessed or changed.

**Material choices proposed for whole-spec review:** priority alone never blocks explicitly optional advice; any actual required/unmet obligation blocks at any priority; standalone report applicability follows explicit approval/governance; coverage is the Farmboy delivery composite before its core implementation call, rather than a core-command patch; ambiguous evidence stops without an automatic return or re-review. These are concrete proposals for approval, not unresolved placeholders or claimed human decisions.

**Handoff:** Awaiting human specification review. No substantive clarification question remains after stating these choices explicitly. The checklist discloses two literal interface/source-name exceptions for reviewer decision; no criteria are silently waived. This draft is neither approval nor evidence of achieved runtime behavior. Planning requires explicit whole-spec approval and resolution/acceptance of the disclosed checklist exceptions, then a separately selected planning segment.

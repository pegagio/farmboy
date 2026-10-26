# Feature Specification: Coordinate independent plan-review handoff from user intent

**Feature Branch**: `029-review-request-handoff`

**Created**: 2026-10-26

**Status**: Awaiting spec review

**Input**: FARM-29 [request](request.md): remove manual prompt/grant dispatch from an explicitly requested independent plan review, reusing existing Farm Boy and Diagram capabilities.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Request one independent review without dispatch work (Priority: P1)

As the operator, I want to ask the selecting coordinator for independent review of the current saved plan and receive the result, without copying prompts, choosing technical grant fields or coordinating sessions myself.

**Why this priority**: The reported Fusion handoff omitted the required caller-supplied grant. The independent reviewer correctly refused; the operator had to repair the handoff manually. The missing responsibility is before reviewer admission, not a reason to weaken that admission.

**Independent Test**: In a disposable Diagram-enabled project, give a selecting coordinator an exact saved candidate and an actual bounded human mandate. Independently observe it dispatch one separate reviewer using the existing entry/adapter, collect the saved report and released native disposition, and return the next action without operator prompt/JSON transfer.

**Acceptance Scenarios**:

1. **Given** one selected review-ready Feature, released author ownership, unchanged saved proposal and an explicit applicable whole-plan approval mandate, **When** the operator requests independent review, **Then** the selecting coordinator resolves the candidate and reviewer, assembles the existing bounded grant from that human authority, starts one independent reviewer and collects its actual outcome without another mechanical confirmation or manual prompt handoff.
2. **Given** the current selecting session materially authored the plan, **When** arranging review, **Then** it acts only as the caller: the semantic reviewer is a different session, with distinct native owner/session attribution and no material proposal authorship. The caller neither decides the review nor borrows the reviewer's ownership.
3. **Given** an ambiguous Feature or missing substantive mandate scope, including whether plan approval is delegated, **When** review is requested, **Then** the caller asks one concise question for that missing decision before dispatch. It does not require the operator to construct a grant, infer that the word “review” grants approval, or ask again about settled authority.

---

### User Story 2 - Preserve exact authority through the handoff (Priority: P1)

As the operator, I want the independent reviewer to receive the exact candidate, actual mandate and applicable constraints, so a convenient handoff cannot broaden authority or approve the wrong plan.

**Why this priority**: Eliminating manual dispatch must preserve the reviewer refusal that correctly exposed the original incomplete request.

**Independent Test**: Exercise valid, absent, ambiguous, stale, wrong-feature, revoked and author-as-reviewer contexts. Verify no dependent review admission occurs with invalid authority and that known current work is reused rather than duplicated.

**Acceptance Scenarios**:

1. **Given** a complete current handoff, **When** dispatching, **Then** caller-supplied grant and review context pin the actual Feature, candidate handoff/revision, approved intent, selected reviewer identities and human provenance/bounds. The existing adapter receives them unchanged and native Diagram remains the authority for admission, ownership, disposition and release.
2. **Given** changed proposal bytes, active author ownership, stale pins, revoked mandate, incompatible capability or an unavailable independent session, **When** preparing or entering review, **Then** dependent work stops with the precise missing input or failed action; no silent candidate replacement, grant renewal, self-issued reviewer grant or permissions workaround occurs.
3. **Given** an already dispatched matching review or an uncertain dispatch/result, **When** the coordinator resumes, **Then** it inspects the known session and native operation/current state before effects. It collects the matching result or reports uncertainty; it never starts a duplicate reviewer merely because the response was lost.

---

### User Story 3 - Return the result and genuine decision boundary (Priority: P2)

As the operator, I want the coordinator to bring back the independent report and explain the next action, so I see review findings and real decisions instead of workflow mechanics.

**Why this priority**: Launching alone would leave the operator as dispatcher. A completed handoff includes collecting and verifying the result, while technical failure must remain visible.

**Independent Test**: Observe approve, planning-return, specification-escalation and incomplete outcomes. Check candidate/report correlation, exact native state and absent ownership for completed endpoints; verify no unrequested repair, re-review or implementation follows.

**Acceptance Scenarios**:

1. **Given** a completed bounded delegated review, **When** collecting its result, **Then** the coordinator verifies exact candidate/report integrity and native accepted disposition/released ownership, reports all six review conclusions and required versus optional findings concisely, and identifies the next separately authorized action. It attributes delegated approval to the reviewer and actual human mandate, never to a fictional human personal review.
2. **Given** planning-return or specification-escalation, **When** reporting, **Then** the exact independent disposition and actionable findings are retained for the existing FARM-28 return workflow. Specification changes still require human whole-spec review; the coordinator does not rewrite the proposal or launch a repair/re-review cycle in this invocation.
3. **Given** denied execution, child disappearance, invalid report, failed report checkpoint or uncertain native finalization, **When** collecting, **Then** the coordinator returns incomplete with the exact action, target, known effects and denied/pending/uncertain outcome. It does not infer approval, clear someone else's ownership, retry blindly or use another executor to bypass refusal.

### Edge Cases

- A plain review request establishes no missing approval role. Existing explicit candidate-specific delegation may supply that role; a missing substantive decision is the legitimate human stop.
- A mandate grants advice only, or human plan acceptance is reserved: do not submit a delegated-approval grant to the native whole-plan decision route. Explain the missing applicable route/authority and ask only if the operator wants to supply it; do not invent a new advisory lifecycle or silently fall back from Diagram.
- A prior author run is still active: arrange no competing writer. The author must complete its supported handoff/release before reviewer admission; this feature grants no takeover or forced release.
- Native discovery selects another Feature or a launcher cannot target the intended manual review: do not change ordering, enable controls or add a selector. Use an already supported explicit independent-session entry if available; otherwise report that concrete route limitation before launch.
- The reviewer returns prose without a valid report/native terminal: treat it as incomplete. Process success, a report file, an old receipt and current ownership release are distinct observations.
- Caller disconnects while reviewer remains active: preserve known session/operation locators and inspect before any restart. No timeout takeover, automatic termination, lease or background monitor is introduced.
- Controls remain OFF on an authorized manual path. Automatic discovery/launch still requires its separately selected scope and existing controls; a valid grant changes neither.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Farm Boy MUST assign preparation/dispatch/collection of one independent whole-plan review to the selecting caller, before the generic semantic reviewer starts. This MUST compose existing capabilities rather than create a new execution engine or Diagram lifecycle.
- **FR-002**: The caller MUST resolve exactly one project, Feature, current review-ready candidate and applicable human mandate from actual request/native/Git evidence. It MUST ask only for materially missing selection or authority, one question at a time, and MUST NOT make the operator copy prompts or author technical grant fields.
- **FR-003**: Caller preparation MUST translate actual explicit bounded human authority into the existing per-invocation review grant, retaining its exact candidate, reviewer identities, protected intent/UX/constraints and provenance. It MUST NOT invent delegation, silently repin/renew a stale grant, broaden a role, or ask a reviewer to grant itself authority. Review alone MUST NOT imply delegated approval.
- **FR-004**: The semantic reviewer MUST be independent of material candidate authorship and execute in a separate session. The caller MAY be the plan author but MUST remain a dispatcher/collector, without semantic disposition or native reviewer ownership. Existing native independent-owner/session checks remain required and do not independently prove semantic independence.
- **FR-005**: The caller MUST use an existing supported independent-session/reviewer route and pass supplied grant/context unchanged into the existing reviewer/adapter composition. It MUST verify that the route selects this exact Feature and exposes the required permissions/capabilities before dispatch. Unavailable targeting or permissions is a precise blocker, not permission for a new launcher selector, changed discovery/control policy or bypass.
- **FR-006**: The existing adapter MUST continue to own native acquire-or-reuse, report checkpoint with normal hooks, disposition finalization and release/readback. The semantic reviewer remains one continuous invocation of the existing six-question body. The selecting caller MUST NOT wrap/acquire/finalize again, direct the substantive decision, modify proposal bytes or split review into per-step agents.
- **FR-007**: One selected invocation MUST dispatch at most one matching reviewer. Resumption MUST inspect known session/native operation/current authority and saved evidence before new effects. Exact historical replay MUST NOT be treated as a new live run or approval of current changed content. No durable dispatch registry, token service or second status store is required.
- **FR-008**: The caller MUST collect actual completion or a truthful incomplete outcome through the existing session/result mechanism. It MUST verify saved report path/digest, Feature/candidate/mandate applicability, native accepted disposition and ownership release for completed review. A local report, child exit or prose alone MUST NOT establish native completion.
- **FR-009**: Output MUST identify Feature/candidate, reviewer/mandate, report/checkpoint, six conclusions, required versus optional findings, native decision/release and the next ordinary action or substantive human input. Existing report evidence is reused; no duplicate approval ledger is added.
- **FR-010**: Approve, planning-return and specification-escalation MUST retain existing meanings and the FARM-27/FARM-28 report-consumption boundaries. This invocation MUST stop after the collected outcome, without automatic proposal repair, renewed review, implementation or broader “drive to completion” chaining.
- **FR-011**: Existing explicit human specification approval, result acceptance, integration/publication permissions and applicable holds/revocation MUST remain intact. Delegated whole-plan approval is allowed only under the actual bounded mandate and MUST be attributed truthfully. Neither dispatch nor review approval grants later execution authority.
- **FR-012**: Failures, denials, stale or missing evidence and uncertain outcomes MUST produce a precise action/target/reason/effects handoff. The caller MUST NOT manufacture successful disposition, erase ownership, change permissions, switch checkouts/executors after refusal or repeat an uncertain effect without inspection. Manual recovery remains explicit and separate.
- **FR-013**: The change MUST preserve generic standalone reviewer usability and existing authoring/planning/delivery behavior. Diagram-specific grant/native details stay in the optional adapter/caller composition; all current route declarations, controls and consumer installations remain unchanged by source delivery.
- **FR-014**: Acceptance MUST include focused source/transport regressions and an independently evaluated real executing session using disposable Git/native state. Cover complete no-copy handoff, omitted grant, incomplete mandate, stale/wrong candidate, author/reviewer independence, valid delegated approval, both negative dispositions, duplicate/uncertain resume and permission refusal. Controlled plumbing, actual model behavior, simulated failures and unobserved live host behavior MUST be distinguished. No real Fusion/BGG workflow or API request is needed or authorized by this proof.

### Key Entities *(include if feature involves data)*

- **Selecting caller**: Existing agent/session that interprets the operator's selected review request, prepares the bounded handoff and collects the result. It adds no stored coordination authority.
- **Review candidate and mandate**: Existing immutable proposal/spec/handoff references plus actual human scope and independent reviewer attribution. Existing native grant and approval fields remain authoritative; no new schema is proposed.
- **Review result**: Existing committed report, attributable disposition, native operation/handoff and released-state observations, or a precise incomplete record in ordinary session/feature notes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In the authorized complete review journey, the operator supplies the substantive review request/mandate and receives the correlated outcome with zero manual prompt transfers, grant-object edits or mechanical re-confirmations.
- **SC-002**: Each tested selected request starts at most one independent reviewer; resume/uncertainty cases create no duplicate review or disposition. All completed paths identify the exact reviewed candidate and saved report.
- **SC-003**: Every missing, wrong, stale, revoked or self-issued-authority case stops before unauthorized review effects; no test accepts a grant merely because a coordinator or reviewer claims it exists.
- **SC-004**: All three substantive dispositions preserve their existing states and next-action boundaries. Required findings remain required, optional advice remains optional, and no path enters implementation, integration or another workflow implicitly.
- **SC-005**: Every observed failure reports its exact known action/outcome and preserved evidence without claiming approval or release that was not recorded. Completed native reviews finish with released ownership verified.
- **SC-006**: Separate executing/evaluating evidence demonstrates the complete caller-to-independent-reviewer-to-caller journey, including stopping behavior; source-only or controlled-fixture evidence is never presented as that runtime proof.

## Assumptions

- This increment covers independent whole-plan review, not a universal “drive feature” entry, automatic segment chaining, periodic invocation or recovery automation.
- Actual user intent, project governance and candidate-specific context may establish an existing bounded mandate. An ambiguous request does not. No standing mandate is inferred from this feature or its approval.
- Existing independently invoked reviewer sessions and session/result tools are reused when available. No specific provider API, host profile, permanent process or cross-process callback framework is selected by this specification.
- Normal report checkpoint commits are within the actual selected review authority only when operator restrictions permit. Technical per-action permissions and refusal behavior remain unchanged.
- DIAG-6 remains a separate unapproved polling specification. FARM-29 does not supply future polling grants or broaden its stop/escalation policy. BGG dogfooding and a general “drive feature to next human decision” entry need their own selected scope; no duplicate mechanism is captured here.

## Request fit and evidence notes

Farm Boy owns reusable skill/caller composition. Its current source at `0f03fbe` contains the generic reviewer, optional adapter and FARM-27/FARM-28 review consumption/return behavior. The Diagram roadmap already contains completed DIAG-10, not this selecting-caller handoff. Native FARM history through FARM-28 contains no duplicate. FARM-29 was allocated by native capture, explicitly queued and claimed before isolated workspace preparation; no historical roadmap is reactivated.

Read-only Diagram source at integrated `f6494a1e` and installed launcher help establish the existing review-grant transport: launcher accepts `--review-grant-file`, refuses missing grant on review-plan and passes it unchanged; native plan review validates exact candidate/revision/selected reviewer and rejects recorded author identity/session reuse. The installed schema23/Feature9 target and Farm Boy's matched protocol are available. This source/interface inspection does not prove a live coordinator assembles or dispatches grants today. No Diagram core change is required by this scope; an unexpected missing native capability is a compatibility blocker for separately reviewed work.

Repository wiki query used configured `wiki/` with two topic-matched pages (within the 8-page/4000-token limits): [independent plan review](../../wiki/pages/independent-plan-review.md) (S013/S014) and [optional adapter](../../wiki/pages/optional-diagram-adapter.md) (S012/S013/S014). Registry entries are valid. They cover independent reviewer/adapter responsibility but not caller-side grant assembly/dispatch/collection, so coverage is partial. Their schema22 descriptions are stale against current source/installation; they are not operational authority. Future authorized ingestion of the actual FARM-29 delivery would close this coverage gap; this preparation does not edit wiki content.

Authoritative source fit: [constitution](../../.specify/memory/constitution.md), [direction](../../docs/direction.md), [review guide](../../docs/review-implementation-plan.md), [adapter guide](../../docs/diagram-adapter.md), current project-local reviewer/adapter skills and native protocol. The six review lenses are preserved: scope, unnecessary machinery, intent, architecture, tightening without redesign and checklist proportionality. Scope is a small caller-side composition over existing authority, with focused refusal/resume coverage rather than a distributed dispatcher or orchestration framework.

The effective core template was resolved with `specify preset resolve spec-template`. There are no configured before/after-specify hooks; the full interactive specify command was not invoked. This is the verified external draft body within the current native adapter run, not a second acquire or a separate per-step agent. Draft quality checks are not runtime acceptance, whole-spec approval or permission to plan. No live reviewer, FUSION-3 session, CAD operation, installed executable, controls or other Feature was changed by preparation.

**Handoff**: Awaiting human whole-spec review. No material product questions remain in this bounded draft. Approval and separately selected planning remain required; no implementation or deployment is authorized.

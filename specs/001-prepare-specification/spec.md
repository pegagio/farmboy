# Feature Specification: Prepare specification

**Feature Branch**: `reboot/2026-10-16/prompt-first`

**Created**: 2026-10-16

**Status**: Complete — revised implementation and technical verification; human result review pending

**Prior approval**: Pegagio approved the earlier specification/plan on 2026-10-16. On 2026-10-17 Pegagio approved preparing this boundary revision; that earlier preparation approval did not authorize implementation. Pegagio subsequently explicitly approved this revised specification and plan for implementation on 2026-10-17. The earlier native Goals test remains failed, not a pass.

**Delivery verification**: Revised source and required independent runtime observations are verified for this feature; targeted checks pass; local closeout and human result review remain distinct; see [actual observations and blockers](validation/acceptance.md). Specification approval is not delivery acceptance.

**Input**: User description: "Deliver roadmap feature 001: select a named or eligible roadmap feature, discover relevant wiki context and prepare a saved draft, then end automation with a clarification handoff or a human specification-review handoff. Preserve genuine interactive input waits, simple existing-capability composition, one-session execution, artifact-based resume and disposable-project portability."

## Clarifications

### Session 2026-10-16

- Q: If clarification reaches its question limit while important questions remain, should the selected workflow continue with another supported round or pause for your instruction? → A: Continue supported clarification rounds within the original workflow launch until specification consensus, genuinely waiting for answers and honoring command/platform limits; do not require repeated prompts to restart clarification.
- Q: May Codex automate verification, and what must acceptance observe? → A: Codex may drive tests, but observe a separate real Codex agent/session using the actual Farmboy skill, genuine question/input waits when needed and the final specification-review stop. Do not manufacture questions or count scripted test answers as real user approval; native runtime compatibility still requires actual evidence.

### Decision 2026-10-17 — revised automation boundary

Automated preparation finishes successfully when it saves a usable draft and explicit handoff. Material questions go to ordinary interactive Spec Kit clarification; otherwise the handoff is human specification review. The native Goal ends at that draft/handoff boundary and must not remain active awaiting answers. Existing clarify is reused; no additional Farmboy clarification skill is proposed. Clarification completion is not approval. Explicit human specification approval, at the review depth chosen by the operator, remains prerequisite for planning. This supersedes the earlier assumption that one active Goal spans clarification and review, without erasing the earlier decisions or failed evidence.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Select work and prepare its specification (Priority: P1)

An operator invokes Prepare specification for a named roadmap feature, or asks for the next eligible feature. The workflow establishes the target, records the selected feature as in progress, consults relevant project knowledge and drafts the specification. It does not make the operator repeat settled decisions.

**Why this priority**: A clear target and grounded draft provide immediate value and establish the context for every later step.

**Independent Test**: In a disposable Spec Kit project with a roadmap, wiki and known feature, invoke the workflow once by name and once through eligible selection. Inspect the selected entry, active feature and resulting draft without running planning or implementation.

**Acceptance Scenarios**:

1. **Given** an eligible named feature and project knowledge, **When** the operator invokes the workflow, **Then** only that feature becomes the active target, only its roadmap entry changes lifecycle state, and a draft specification reflects its scope and relevant cited constraints.
2. **Given** no named feature and a roadmap with an established ordering and eligible work, **When** the operator asks for the next feature, **Then** selection follows that ordering and eligibility rather than inventing work.
3. **Given** ambiguous identity, unsettled ordering, unmet prerequisites or no eligible feature, **When** selection cannot be resolved from current artifacts, **Then** the workflow explains the issue and requests the necessary decision instead of silently selecting or activating another feature.
4. **Given** a wiki coverage gap or a conflict with governing artifacts, **When** context is queried, **Then** the workflow reports the gap/conflict and resolves any consequential decision with the operator; it neither fabricates knowledge nor reads outside authorized boundaries.

---

### User Story 2 - Finish automation and clarify interactively (Priority: P1)

The operator receives a saved draft, findings and one explicit next step. If material ambiguities remain, automated preparation is complete at a handoff to the existing interactive clarify capability. The operator then answers real questions without a live preparation Goal. If no material ambiguity remains, the handoff is directly to human specification review.

**Why this priority**: Useful automation must finish at an observable boundary instead of repeatedly continuing while a person considers an answer.

**Independent Test**: Observe a separate real subject complete the native Goal at the saved-draft/handoff boundary in both ambiguous and settled cases. Separately invoke existing clarify ordinarily, observe a genuine question wait and answer incorporation, then human review. Do not conflate these outcomes.

**Acceptance Scenarios**:

1. **Given** a usable draft with material ambiguities, **When** automated preparation finishes, **Then** its Goal is natively complete and the saved handoff names the unresolved topics and existing interactive clarify entry point; it does not ask an answer and keep pursuing the same Goal.
2. **Given** a settled draft, **When** automated preparation finishes, **Then** its Goal is natively complete and the next step is human specification review, with no manufactured questions.
3. **Given** an operator-selected ordinary clarify invocation after handoff, **When** a material question is asked, **Then** execution genuinely waits, integrates only an actual answer and respects supported command limits and early termination; preparation’s completed Goal is not resumed.
4. **Given** clarification completes, **When** the result is presented, **Then** specification approval remains a separate explicit human decision; the operator chooses review depth.
5. **Given** a draft, completed preparation Goal or clarification answers without explicit specification approval, **When** later work is requested or considered, **Then** planning does not start by inference.

### User Story 3 - Resume the correct stage and preserve artifacts (Priority: P2)

Resume re-establishes the selected feature and whether work is interrupted drafting, a completed handoff, pending interactive input or pending human review. A completed draft/handoff is not replayed as fresh activation, and its Goal is not reactivated to wait for a person.

**Independent Test**: In a disposable project, observe interrupted drafting resume without duplicate effects; inspect a completed handoff; resume ordinary clarification with its pending question and preserve changed answers/artifacts; verify no approval or planning by silence.

**Acceptance Scenarios**:

1. **Given** interrupted drafting, **When** preparation resumes, **Then** it revalidates current artifacts and target identity without duplicate activation or creation; interruption/stall is not successful completion.
2. **Given** a completed handoff or pending interactive question/review, **When** the operator resumes, **Then** the correct next stage is presented without resurrecting the preparation Goal or inventing approval.
3. **Given** a supported disposable Spec Kit project, **When** the revised stages are exercised, **Then** drafting, native completion, ordinary clarification and human review work with its own artifacts and rules.

### Edge Cases

- Ambiguous selection, missing capabilities, governing conflicts and unusable prerequisites stop affected work with saved evidence. A partial/blocked draft is not a successfully completed handoff merely because the Goal stopped.
- A usable draft may deliberately contain unresolved product choices; those must be visible in the handoff and quality findings, never guessed away to make checks pass.
- An underlying authoring command may require input before completion. Do not ignore that instruction or claim the whole command completed; use a supported drafting path or report a blocker.
- Changed answers/artifacts require current-artifact reconciliation in the correct stage. A completed handoff does not freeze history or imply specification approval.
- Ordinary clarify preserves supported rounds and limits. No source-policy override, fabricated answer, forced mode switch or replacement continuation mechanism is authorized.
- Native stalled, paused, interrupted or budget-limited states are not evidence of the required successful Goal completion. Prose claiming a state change is insufficient.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The workflow MUST accept either an explicitly named roadmap feature or a request for the next eligible feature, resolving identity and prerequisites from the current project artifacts before activation.
- **FR-002**: Selection MUST use established roadmap ordering; ambiguity, unavailable prerequisites or absence of eligible work MUST produce an actionable stop rather than arbitrary selection.
- **FR-003**: The workflow MUST record only the selected feature’s in-progress status and necessary identity/linkage metadata; it MUST NOT change unrelated feature entries or infer verification/acceptance.
- **FR-004**: The workflow MUST query relevant wiki knowledge, retain supporting references and surface gaps/conflicts while honoring the constitution and authorized access boundaries.
- **FR-005**: The automated stage MUST use existing project templates/setup and relevant roadmap/wiki capabilities to save a coherent draft, its quality findings and current roadmap-fit evidence. It MUST NOT silently bypass input requirements of a full interactive command.
- **FR-006**: A successful automated result MUST hand off material ambiguities to the existing ordinary interactive clarify capability, without keeping the preparation Goal active. Interactive clarification MUST genuinely wait, incorporate actual answers, respect supported rounds/limits and distinguish completion from approval. No additional Farmboy clarification skill is required.
- **FR-007**: Every successful automated result MUST present saved artifact links, findings and exactly the applicable next stage: interactive clarification when material questions remain, otherwise human specification review. Explicit specification approval remains required before planning; review depth is the human’s choice.
- **FR-008**: Routine authorized drafting continues without redundant OKs. Required input needed to select or produce a usable draft, unresolved governing conflicts and genuine blockers stop affected work. Product ambiguities suitable for clarification belong in a successful saved handoff, not a live Goal waiting loop.
- **FR-009**: Resume MUST re-establish identity, current artifacts and stage before repeating an effect. It MUST avoid duplicate activation/spec creation and MUST NOT restart a completed preparation Goal to await interactive input or review.
- **FR-010**: The baseline MUST operate in one Codex session using its existing model/effort, with no per-step agent/model routing or separate configuration feature. A separate verification driver is outside that production workflow and does not introduce per-step workflow agents.
- **FR-011**: The workflow MUST remain a thin composition of existing capabilities, preferring the simplest adequate approach. Additional infrastructure requires a concrete current requirement or observed failure; a universal recovery system or custom controller is not a default requirement.
- **FR-012**: When a native Goal runs automated preparation, its objective MUST end successfully at the saved-draft/handoff boundary. Native completion MUST be observed before compatibility is claimed; stalled/paused states and prose-only claims are not success. This feature MUST NOT claim automatic Goal suspension/resumption across human clarification or review.
- **FR-013**: A separate real subject MUST demonstrate portability of automated draft/handoff and subsequent ordinary clarification/review in a disposable project; a second live-project adoption is unnecessary.
- **FR-014**: Specifications and summaries MUST define necessary technical terms and provide concrete examples where useful, retaining precise scope and contextual rationale.
- **FR-015**: This feature MUST NOT provide planning/tasks, implementation, convergence, closeout, remote publication, Diagram coordination or autonomous dispatch. The delivered workflow may invoke only its prescribed specification-preparation steps.
- **FR-016**: The workflow MUST preserve feature-scoped flow-back and current-artifact reconciliation; later changes to merged feature meaning MUST use a new linked feature record under the constitution.

- **FR-017**: Acceptance MUST observe a separate real subject executing the revised skill and actual native Goal completion at both handoffs. Separately observe ordinary interactive clarify question waits and answer incorporation, and no planning without explicit approval. The evaluator MUST NOT roleplay the subject or count scripted answers as real approval. Preserve earlier failed Goals evidence; do not relabel it as passing the new design.

### Key Entities

- **Selected feature**: The roadmap identity and associated feature directory defining the current work and its prerequisites.
- **Specification**: The feature’s mutable pre-merge statement of intended behavior, scenarios, requirements and success criteria.
- **Project context**: Relevant wiki claims with source references, governing rules and any exposed coverage gaps.
- **Draft/handoff**: Saved artifacts and explicit next stage; successful automated preparation may end with unresolved product choices.
- **Pending input or review**: A question in ordinary interactive clarification, or a separate human approval decision; neither is a live preparation Goal.
- **Preparation outcome**: Links to current artifacts and findings, identifying a successful clarification/review handoff or an incomplete/blocked attempt; it does not grant acceptance.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Named and eligible-selection acceptance cases identify exactly one feature; unrelated feature states remain unchanged, and every unresolved-selection case stops without inventing a target.
- **SC-002**: Ambiguous and settled draft cases each produce a usable saved handoff, with zero fabricated answers. Native preparation Goals complete at that boundary before clarification questions or human review waits.
- **SC-003**: Completed automated cases name the correct next stage and readable artifacts. Ordinary clarification completion never implicitly approves the spec, and no planning starts without explicit human approval.
- **SC-004**: Resume preserves target/current artifacts and the correct drafting, handoff, input or review stage, with zero duplicate effects and no resurrection of a completed Goal to wait for a person.
- **SC-005**: An independent real subject demonstrates ambiguous and no-question automated completion, then an ordinary interactive clarification wait/answer and human review in a disposable project; no replacement clarification implementation or second live adoption is required.
- **SC-006**: For the revised automated objective, actual native Goal completion is observed in both handoff cases, without renewed idle continuation after completion. Historic stalled runs remain failures under the former objective. Paused/interrupted/budget stops are reported as incomplete, not passed.

## Assumptions

- The operator supplies a supported Spec Kit project with its own roadmap, wiki, governance and relevant installed commands. Missing capability is a reported prerequisite gap, not permission to set up a new environment.
- Existing roadmap rules define eligibility and ordering; where they do not settle a consequential choice, the operator decides.
- The first delivered segment is bootstrapped manually and then used to prepare specifications for later Farmboy development. This bootstrap run does not demonstrate that the future composite already exists.
- The current Codex/Spec Kit baseline is an explicit product constraint; this specification does not select a new framework, storage format, transport or model.
- Automated preparation and ordinary interactive clarification are distinct invocation boundaries in the same session/model baseline. The operator starts clarification after the automated handoff; the existing command governs its supported rounds and genuine waits. No automatic planning follows either boundary.
- Context basis: [roadmap entry 001](../../.specify/memory/roadmap.md), [constitution](../../.specify/memory/constitution.md), and wiki [workflow authority](../../wiki/pages/workflow-authority.md) (S001), [delivery direction](../../wiki/pages/delivery-direction.md) (S002, S005, S006), [feature history](../../wiki/pages/feature-history.md) (S001) and [project context](../../wiki/pages/project-context.md) (S003, S006, S007). These sources guide intended requirements, not claims of completed acceptance.

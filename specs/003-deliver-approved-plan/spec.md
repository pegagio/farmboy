# Feature Specification: Deliver approved plan through closeout

**Feature Branch**: `reboot/2026-10-16/prompt-first`

**Feature Directory**: `specs/003-deliver-approved-plan`

**Created**: 2026-10-17

**Status**: Delivered and explicitly accepted — all33 tasks performed; roadmap verified

**Specification Approval**: Explicit full-spec approval supplied in trusted conversation; the conversation date was not established. Recorded during this planning session (UTC 2026-10-18). Reviewed clean outcome-focused spec SHA-256 before approval metadata: `bb8d74544c4b5f1e68f3c805c6650a58b043488fa275dd5ac73f5e490a50b487`.

**Approval Evidence and Applicability**: Assistant: “It now ends successful delivery at implemented, awaiting your result review, and your acceptance separately authorizes verified; incomplete handoff moves neither. All16 checks pass with zero findings, and it is ready for your full approval. Planning still has not started. Do you want to approve this updated spec?” User: “Yes”. Approval applies to the entire cleaned outcome-focused specification identified above, without the drafting-added reverse-write procedure or related implementation detail. Subsequent edits in this recording step change approval/status/handoff metadata only, not approved requirements, scenarios, success criteria or assumptions. Material changes still require affected explicit human review. This is specification approval, not plan approval, delivery acceptance or permission to implement, commit, integrate, merge or push. The operator intends separately selected bounded planning next; this ordinary authoring turn does not start it or create/reactivate a Goal.

**Input**: Operator-selected roadmap Feature 003: implement an explicitly approved plan, verify and converge/repair, reconcile spec/plan/tasks and implementation, complete delivery documentation/debrief/wiki ingestion/lint and the prescribed LOCAL delivery commit. Successful local delivery records `implemented` and ends Awaiting result review. Subsequent explicit applicable human result acceptance separately authorizes `verified`; incomplete attempts must not falsely advance either status. Integration, declaration integrated/complete, merge, push and future 004 external contracts/optional bridge remain separate.

## Table of Contents

This specification separates intended delivery behavior, approval metadata and preparation evidence.

- [Clarifications](#clarifications)
- [User Scenarios & Testing](#user-scenarios--testing-mandatory)
- [Requirements](#requirements-mandatory)
- [Success Criteria](#success-criteria-mandatory)
- [Assumptions](#assumptions)
- [Context and rationale](#context-and-rationale)
- [Unresolved topic](#unresolved-topic)
- [Preparation handoff](#preparation-handoff)
- [Current execution checkpoint](#current-execution-checkpoint)

## Clarifications

The following actual decisions settle their named topics only; neither approves the whole specification. Ordinary authoring occurs outside the completed preparation Goal.

**Explicit affected sequencing approval**: In subsequent trusted review, the assistant explained that requiring independent proof of the final Farmboy commit before permitting that commit creates a sequencing snag, and recommended retaining complete disposable evidence, making the scoped final commit and independently checking it afterward. The human answered “Yes”. This explicitly clarifies T030/SC-006 sequencing, rather than inferring authority from prior approval. All required precommit checks and observations remain prerequisites. Actual final Farmboy closing-commit/result observation occurs independently after that commit exists and before successful human result-review handoff. No missing observation passes in advance, no test is waived, and no recursive self-delivery or receipt-only commit is required. This is not result acceptance or verified authority.

### Session 2026-10-17

- Q: When Farmboy hits a point where it needs you, do we let it stop itself cleanly and write down where it left off, then pick up after you answer? That's what worked last time. It doesn't claim the feature's delivered, just that it'll pause safely instead of hanging indefinitely. Do you want that for003 too? → A: “Yes, that sounds ideal”. The operator explicitly confirmed the meaning: an explicitly bounded automation Goal may complete after durably saving the INCOMPLETE delivery outcome, exact required human input, artifact references, actual work/attempts and remaining issues, and ordinary next action; supported native completion and complete readback precede requesting input. Only the handoff objective succeeds. Delivery, approval and feature completion remain unclaimed. After an actual answer, continuation requires separately operator-selected ordinary interaction outside that completed Goal, without automatic restart or a new Goal. Unknown technical/helper failures and unmet overscoped delivery-only objectives do not qualify as successful handoffs.

- Q: Delivery ends at implemented, and your acceptance permits a separate move to verified. Integration is still separate. Pending verification or complete are not available statuses. Should we amend the spec to say implemented, and then verified on your acceptance? → A: “Yes”. Successful local delivery records `implemented` and hands off Awaiting result review. Selection of that future delivery workflow grants only its narrow implemented write, independently of debrief recommendations. Subsequent explicit applicable human result acceptance separately authorizes `implemented → verified`; delivery does not infer acceptance or perform that later transition. Incomplete attempts must not falsely advance either status. This decision does not approve the whole specification or authorize changing current 003 from in-progress.

**Later explicit closeout clarification**: During ordinary plan review, the human said “It feels like we should end with a commit,” then explicitly settled the concern: “Yeah, I agree. I am not, we do not need to worry about handling if the commit fails”. Finish checks and documents, include the implemented roadmap update and all scoped delivery artifacts, then make the final scoped local commit. Successful delivery is reported only after that commit actually succeeds; if Git errors, report the ordinary error honestly without claiming delivery success. This clarification adds no special failure procedure or machinery and does not approve the plan or implementation.

## User Scenarios & Testing *(mandatory)*

Convergence compares delivered behavior with current approved requirements and records missing work. Flow-back reconciles affected spec, plan, tasks and implementation so they describe the same current feature. Closeout prepares a reviewable local candidate; it does not integrate or complete the feature lifecycle.

### User Story 1 - Deliver eligible approved work (Priority: P1)

As the operator, I want delivery to implement and verify the correct approved feature without repeated permission for routine prescribed work.

**Why this priority**: Correct identity and approval are prerequisites for useful implementation.

**Independent Test**: Invoke the actual delivered workflow in an isolated project with applicable specification/full-plan approval; observe implementation, verification and an honest checkpoint without integration.

**Acceptance Scenarios**:

1. **Given** explicit selection, a matching active pointer, verified dependencies and applicable specification/full-plan approval, **When** delivery starts, **Then** it implements eligible tasks through actual existing capabilities and runs applicable verification without redundant routine approval requests.
2. **Given** missing approval, materially changed approved meaning, unverified dependencies or conflicting identities, **When** delivery starts, **Then** it stops before implementation with the exact deficiency, without activating another feature or inferring approval.
3. **Given** required command input, a missing capability or a failed mandatory hook, **When** execution reaches it, **Then** dependent work stops with the actual limitation preserved; an emitted command label or unrelated passing check is insufficient.
4. **Given** unrelated existing changes, **When** implementation proceeds, **Then** it preserves them and confines effects to the authorized current feature; consequential uncertainty becomes a specific blocker.

### User Story 2 - Resolve gaps and reconcile current intent (Priority: P2)

As the operator, I want useful in-scope verification and convergence repairs to continue until clean, with honest stops for decisions, so the candidate matches reviewed intent.

**Why this priority**: Checked tasks and repeated edits alone do not establish delivery or progress.

**Independent Test**: Exercise an actual missing-behavior case and a separate material-decision case. Observe repair/reassessment in the first and a precise preserved required-input boundary in the second.

**Acceptance Scenarios**:

1. **Given** missing approved behavior, **When** convergence records follow-up tasks, **Then** delivery implements them, reruns affected verification and reassesses the current candidate until no actionable gap or unmet obligation remains.
2. **Given** a required repair of any severity, **When** commentary calls it optional, **Then** it remains required; only suggestions identifying neither defects nor unmet requirements may remain optional and separately disclosed.
3. **Given** an accepted in-scope discovery, **When** affected requirements, design or work records change, **Then** current spec/plan/tasks and implementation are reconciled before dependent work or commit; merged historical features retain their meaning.
4. **Given** a new product decision, material scope change, rejected repair or repeated unsuccessful approaches with no useful authorized alternative, **When** delivery cannot continue safely, **Then** it saves actual attempts, remaining issues and exact required input/blocker rather than fabricate progress or waive defects.
5. **Given** a pass followed by an affected edit, **When** readiness is reconsidered, **Then** fresh verification/reassessment covers the latest affected artifacts; the earlier pass is insufficient.

### User Story 3 - Close out and present result review (Priority: P3)

As the operator, I want coherent documentation, debrief, maintained wiki and a bounded local commit before reviewing the candidate, with accurate evidence and limitations.

**Why this priority**: This completes local delivery while keeping acceptance and later integration separate.

**Independent Test**: Complete actual closeout in a disposable project; inspect commit contents, documentation, debrief, wiki results and the review handoff. Confirm no integration or final feature-completion operation occurs.

**Acceptance Scenarios**:

1. **Given** a technically verified, converged candidate with coherent artifacts, **When** closeout runs, **Then** delivery documentation describes changes, validation, evidence limits and optional suggestions; actual installed debrief and wiki ingestion/lint execute on relevant sources and their results are inspected.
2. **Given** actionable closeout findings, **When** authorized correction is possible, **Then** affected artifacts are repaired and stale assessments refreshed; missing authority or material decisions stop dependent closeout.
3. **Given** completed checks/documents and inspected authorized commit scope, **When** delivery closes out, **Then** it includes the implemented roadmap update and all scoped delivery artifacts in the final local commit, preserves unrelated work and reports successful delivery only after that commit succeeds. An actual Git error is reported honestly, without a successful-delivery claim.
4. **Given** successful local delivery recorded as `implemented`, **When** the candidate is presented, **Then** it reports Awaiting result review with the actual local commit, verification evidence and limitations, without acceptance, a `verified` write, integration, completion declarations, merge, push or another workflow.
5. **Given** successful checks, a debrief recommendation or silence without explicit applicable human result acceptance, **When** delivery finishes, **Then** it retains `implemented`; none of those signals authorizes `verified` or automatic scope/dependency/governance amendments.
6. **Given** later explicit human result acceptance applicable to the current delivered candidate, **When** acceptance is recorded separately from delivery, **Then** it authorizes `implemented → verified` without implying integration or permission to commit, merge or push.
7. **Given** an INCOMPLETE delivery handoff, **When** it is saved or its bounded automation Goal completes, **Then** it does not claim successfully recorded delivery status or infer verified; actual incomplete work/errors are reported honestly and automation success remains distinct from successful delivery.

### User Story 4 - Resume without lost decisions or duplicate effects (Priority: P3)

As the operator, I want interruptions and ordinary continuation to use current artifacts and genuine approvals without a new tracking system.

**Why this priority**: Restarting effects or trusting stale approval makes continuation unsafe.

**Independent Test**: Interrupt actual delivery at a partial checkpoint, change an affected artifact, then separately resume. Inspect preserved identities, fresh reassessment and absence of duplicate commits.

**Acceptance Scenarios**:

1. **Given** partial work, answers and checked evidence, **When** delivery resumes, **Then** it inspects current artifacts and approval applicability, performs missing/affected work only and preserves task identities without resetting or regenerating completed work.
2. **Given** an existing commit or usable pending result review and no revision request, **When** invoked again, **Then** delivery inspects current artifacts and Git state, preserves the pending review and avoids duplicate effects, inferred acceptance and terminal/deferred reactivation.
3. **Given** a matching native objective and supported completion controls, **When** its saved endpoint is reached, **Then** native completion/readback precede human waits. Unsupported controls, helper failure or an unmet objective are disclosed without fake success or host-state edits.
4. **Given** an explicitly bounded automation objective allowing an INCOMPLETE-for-human-input handoff and a genuine required decision, **When** delivery must stop, **Then** it durably saves INCOMPLETE delivery outcome, exact input, artifact references, actual work/attempts, remaining issues and ordinary next action in existing artifacts, reads back that content, completes the matching Goal through supported controls and verifies native complete readback before requesting input. The handoff succeeds while delivery remains incomplete.
5. **Given** that completed input-handoff Goal, **When** the human actually answers and separately selects ordinary continuation, **Then** delivery preserves the answer/current artifacts, checks approval applicability and resumes missing/affected work outside the completed Goal, without automatic restart or creating another Goal. The answer grants no unrelated approval.
6. **Given** an unknown technical/helper failure, unavailable native controls or an overscoped delivery-only objective still unmet, **When** execution stops, **Then** it saves the actual limitation and does not claim successful handoff completion, delivery or approval merely because input/blocker notes exist.

### Edge Cases

- Checked tasks with missing behavior/evidence remain gaps; markers alone cannot establish completion.
- Unavailable or failing required verification is reported exactly and prevents clean delivery.
- Assessment changes invalidate affected earlier passes; preserve task identities and refresh checks.
- Required delivery closeout must be explicitly prescribed even if a core command exposes similar optional hooks. Honor each command's actual hook contract and inspect prior effects to avoid duplicate execution.
- Wiki semantic conflicts needing a decision are preserved rather than resolved through invented policy.
- Debrief recommendations do not grant roadmap-write authority. Only the selected delivery workflow’s explicit narrow authorization permits its implemented write; separate explicit applicable result acceptance permits the later verified write. Automatic scope/dependency/governance amendments remain forbidden. Missing integration policy does not block local delivery unless it also prevents a required local action.
- Unrelated staged changes, secrets or unclear commit ownership require safe separation preserving original state, or an exact scope blocker; never commit everything by convenience.
- No changes to commit on resume requires inspecting the existing delivery state, not manufacturing an empty commit or extra work. An incomplete or uncertain outcome must be reported honestly and must not falsely advance status.
- Historical approval does not approve materially changed meaning; affected explicit review is required.

## Requirements *(mandatory)*

These requirements prescribe observable behavior without selecting a new runtime, controller, store or integration executor.

### Functional Requirements

- **FR-001**: Delivery MUST resolve one selected feature, matching active pointer, contained artifacts and verified dependencies before effects. Ambiguous/conflicting identity MUST stop affected work without choosing another feature.
- **FR-002**: Delivery MUST require explicit applicable specification and full-plan approval in conversation or an existing content-identifying review note. Answers, checks, analysis, Goal outcomes and silence MUST NOT grant approval. Material changes require affected human review before dependent work.
- **FR-003**: Delivery MUST compose actual installed implementation and convergence capabilities, applicable verification and existing closeout operations in prescribed order. Missing capability/input MUST stop dependent work; labels or improvised replacements MUST NOT substitute for execution. Each command owns its actual mandatory/optional/conditional hook contract.
- **FR-004**: Selecting this future delivery composition MUST authorize routine implementation → verification → convergence → follow-up implementation/reassessment within current approved scope without repeated OKs. Standalone implementation MUST NOT acquire convergence/delivery authority.
- **FR-005**: Convergence MUST identify all actionable discrepancies and unmet approved requirements, record required follow-up regardless of severity and reassess after repair. Clean delivery requires zero actionable gaps and zero unmet obligations. Optional suggestions must be separate and cannot cause endless polishing.
- **FR-006**: Delivery MUST continue useful authorized approaches using actual remaining findings and outcomes. When stuck, repeating unsuccessful approaches or needing a human decision, it MUST save actual attempts, remaining issues and exact next input/action. It MUST NOT fabricate attempts, answers or waived defects.
- **FR-007**: Affected current spec/plan/tasks, implementation and evidence MUST be coherent through flow-back before dependent work, commit and closeout. Routine reconciliation preserves approved intent; new scope and constitution changes need separate authority. Historical merged features MUST NOT be rewritten in meaning.
- **FR-008**: Verification MUST cover current affected behavior, required project checks and real workflow interactions. Affected edits invalidate stale passes. Reports MUST distinguish actual runtime observations, static checks, fixtures and unverified claims.
- **FR-009**: Closeout MUST include understandable delivery documentation, actual installed roadmap debrief, relevant wiki ingestion and subsequent lint, with findings reconciled within authority. Required failures/conflicts prevent clean closeout. Debrief remains recommendation-only: its recommendations MUST NOT authorize automatic status, scope, dependency or governance amendments. The delivery workflow’s own explicit narrow implemented authorization in FR-010 is independent of debrief recommendations; broader amendments require their separate authority.
- **FR-010**: After required checks, coherent artifacts and delivery documentation closeout, the selected future delivery workflow MUST include the narrow implemented roadmap update with all scoped delivery artifacts in the final local delivery commit, preserving unrelated work. Selection grants only that narrow implemented write, independently of debrief recommendations. Successful delivery MUST be reported only after the actual local commit succeeds. If Git errors, report the ordinary error honestly without claiming successful delivery; no special failure procedure or additional machinery is required. Any proposed new machinery still requires explanation with simpler alternatives at full-plan review. This planning invocation authorizes no status write or commit.
- **FR-011**: Successful local delivery MUST end with roadmap status `implemented` and Awaiting result review, presenting candidate/artifact references, the actual local commit, verification/convergence/closeout evidence, limitations and optional suggestions. Delivery MUST NOT infer result acceptance or perform `implemented → verified`; only subsequent explicit applicable human result acceptance separately authorizes that transition. Checks, debrief recommendations, silence, answers and Goal completion do not constitute acceptance. INCOMPLETE and Awaiting result review are handoff labels, not roadmap statuses; pending verification and complete are not new lifecycle values. Integration, declaration integrated/complete, merge, push and an undefined final feature-completion operation are neither prerequisites nor effects of delivery.
- **FR-012**: Resume MUST inspect current artifacts, Git state and approval applicability, preserve accepted answers, task identities and checked evidence, and perform missing/affected work only. A usable pending result review is presented rather than rebuilt. Duplicate effects, inferred acceptance and terminal/deferred reactivation are forbidden.
- **FR-013**: Native Goal use MUST inspect its entire actual objective and exposed supported controls. An explicitly bounded automation objective MAY succeed at a genuine required-input handoff only after durably saving the INCOMPLETE delivery outcome, exact required human input, artifact references, actual work/attempts and remaining issues, and ordinary next action in existing artifacts, then reading back the saved content, completing the matching Goal through supported controls and verifying native complete readback before requesting input. Completion is of the handoff objective, never delivery, approval, feature completion or authority to mark implemented/verified. After an actual answer, continuation MUST be separately operator-selected ordinary interaction outside the completed Goal, preserving artifacts/answers and approval gates without automatic restart or creating a new Goal. Unknown technical/helper failures, unavailable controls and unmet overscoped delivery-only objectives MUST NOT become successful handoffs. A clean-delivery-only objective requires actual clean delivery. Invented APIs/receipts, host-state mutation and false native success are forbidden.
- **FR-014**: Delivery MUST use existing session model/effort without delegated runtime steps or model routing, and compose existing capabilities/artifacts. No numeric attempt limits, counters/reset semantics, progress scoring, new persistence, controller, accounting/tracking machinery or renamed equivalent is permitted. Any proposed additional subsystem must explain concrete need, simpler alternatives, tradeoffs and recommendation at explicit full-plan review; no new tools/frameworks without approval.
- **FR-015**: Acceptance MUST include proportionate observation of the actual delivered skill in a real Codex session separate from its evaluator, covering affected interactions/stops and portability in a disposable Spec Kit project. Demonstrate the complete local lifecycle, genuine input/review stops, repair and interruption/resume, with explicit approvals between separately selected preparation and delivery segments. Simulations alone cannot establish acceptance.
- **FR-016**: This feature MUST keep standalone delivery separate from future 004 external selection/request-result contracts, Diagram coordination/ownership, optional bridge implementation and later integration execution. No duplicate queue/ownership/approval register, release/acquisition API or bridge packaging decision is introduced.

### Key Entities

- **Selected feature**: One current roadmap entry, standard active pointer and contained directory that agree before effects.
- **Approved intent**: Reviewed spec and full-plan meaning, with current applicability distinguished from historical approval.
- **Delivery candidate**: Implementation, coherent artifacts, actual evidence, delivery documentation and local commit; successful delivery is recorded as `implemented`. Technical verification is distinct from roadmap `verified`, which requires subsequent explicit applicable human result acceptance. Neither implies integration.
- **Remaining finding**: Actual required work or decision in existing tasks/notes, distinct from an optional suggestion; no parallel database.
- **Result-review handoff**: Existing notes/report identifying candidate, limitations and next review; a readable stage label, not a roadmap lifecycle value or ownership record.

## Success Criteria *(mandatory)*

These measurable acceptance outcomes are future obligations, not results established by drafting or its quality checklist.

### Measurable Outcomes

- **SC-001**: Every exercised missing-approval, identity-conflict, unready-dependency and changed-meaning case stops before dependent effects, reporting the exact prerequisite with zero fabricated approvals.
- **SC-002**: A real approved bounded feature reaches technically verified/converged delivery recorded as `implemented`, with zero actionable gaps/unmet obligations and no repeated permission requests for routine prescribed steps.
- **SC-003**: Every exercised required-repair case reaches verified repair or an honest exact blocker/input handoff; genuinely optional-only cases cause no polishing loop or reclassification of required work.
- **SC-004**: Every successful local delivery has coherent spec/plan/tasks, delivery documentation, debrief/wiki evidence and a local commit, records `implemented` and hands off Awaiting result review. Delivery performs zero verified transitions, merges or pushes and makes zero acceptance/integration/completion claims. Verified requires separate explicit applicable human acceptance; incomplete attempts falsely advance neither status.
- **SC-005**: Actual interruption/resume preserves all accepted answers, existing task identities and checked evidence, refreshes affected stale assessment and creates zero duplicate effects or feature directories.
- **SC-006**: Independently observed actual execution in Farmboy and a disposable project demonstrates the complete local lifecycle and affected human boundaries; simulations and unsupported native behavior are never labeled runtime proof. Required precommit checks/observations precede the closing commit. Independent observation of the actual final Farmboy commit/result follows its creation and precedes successful human result-review handoff; it is not a prerequisite for its own commit and is never passed in advance.
- **SC-007**: Every claimed native endpoint has saved evidence satisfying the entire objective and actual complete readback before requesting input or waiting for a person. A real bounded input-handoff case preserves every FR-013 handoff field and reports delivery INCOMPLETE; its separately selected answer continuation leaves the completed Goal unchanged and creates no new Goal. Unknown technical/helper failure, unavailable-control and unmet delivery-only-objective cases produce zero false handoff-success, delivery or approval claims.

## Assumptions

These defaults preserve agreed scope and the explicitly clarified Goal boundary.

- The operator is the project maintainer. Review artifacts may name established development tools while explaining workflow terms.
- Feature 002 is verified and supplies the planning segment. Dogfooding it for this specification requires explicit approval first and a separate invocation; this preparation does neither.
- Existing commands, templates, Git conventions and review notes suffice for the initial thin composition. Exact supported delivery command mapping belongs in planning after specification approval, not a new drafting-time controller/helper.
- Required closeout operations are explicit composition steps even when installed commands independently expose optional hooks. Prior effects are inspected to prevent duplicate execution.
- Local commit scope is the authorized delivery unit; unrelated changes are preserved. No new branch hook, integration target, remote operation or delivery acceptance is implied.
- Future delivery selection grants only the narrow implemented update included with scoped delivery artifacts in the final local commit. Successful delivery requires actual commit success; ordinary Git errors are reported without a delivery-success claim. Explicit applicable human acceptance separately authorizes verified. Debrief recommendations grant neither status-write authority nor scope/dependency/governance amendments. No special commit-failure machinery is needed.

## Context and rationale

Current roadmap entry003, constitution and direct operator instructions, including the narrow implemented/verified correction recorded above, settle the delivery endpoint and future 004 separation. Local closeout requires no integration or final feature-completion operation. The delivery commit is a reconciliation checkpoint; only a later separately authorized integration merge freezes historical meaning. Existing 001/002 remain delivered prerequisites, not historical artifacts to rewrite.

Installed wiki-query question: “What authority, local-delivery/result-review boundary, simplicity and saved-handoff constraints should Feature 003 preserve?” Effective settings were wiki/, query slice 8/context 4000, ingest cap 12/page 600 words/citations required, staleness 90 days, index-and-links mechanical repair and five unique configured page types. No environment overrides were found. Configuration/containment and index structure were inspected. Three pages were ranked from index metadata and estimated below 4000 tokens before body reads; no other page bodies or original sources were opened by this query.

Supported context: thin composition and local delivery before later integration ([delivery-direction](../../wiki/pages/delivery-direction.md), S002/S005/S006); selected-workflow authority, genuine gates and independent runtime/evaluator evidence ([workflow-authority](../../wiki/pages/workflow-authority.md), S001/S002); saved drafting handoff and explicit approval before planning ([specification-handoff](../../wiki/pages/specification-handoff.md), S008). These are the relied-upon pages; cited IDs were validated in the source registry. **Wiki-query verdict: Partial.** Gaps: exact current 003 closeout/local-commit contract, native required-input endpoint and latest 002 acceptance evidence. Likely future ingestion sources are current roadmap 003, this specification once settled and 002's acceptance record. Query itself writes nothing. S006's older ingestion and the handoff page's older native-API limitation do not establish current readiness. Direct authority/current roadmap independently settle scope; current native evidence must come from actual controls.

## Unresolved topic

None remains material to specification readiness after the actual Q1 answer and approved narrow lifecycle correction recorded above. FR-013, US4 scenarios4–6 and SC-007 now distinguish bounded automation handoff completion from incomplete delivery, approval and feature completion, including ordinary continuation and the failure/overscoped-objective exclusions. Exact supported command composition and verification methods remain planning work; the later explicit closeout clarification settles final-commit ordering, with no unanswered product decision.

## Preparation handoff

**Ready for planning — specification explicitly approved.** The actual full-spec approval applies to the cleaned outcome-focused bytes identified in the approval metadata above. The current Feature 003 roadmap remains in-progress. The later explicit closeout clarification above settles final-commit ordering without adding a special failure procedure. No removed procedure is approved or restored here. The ordinary authoring turn stops after cleanup/approval recording. The operator will separately select the bounded planning Goal and actual installed `$farmboy-prepare-implementation-plan`; no planning/tasks or new Goal starts here. Approval does not extend to a future plan or implementation, and material changes require affected human review.

Actual preparation used `.agents/skills/farmboy-prepare-specification/SKILL.md` in session `01a14c3d-493b-7e12-bcf1-79a0033ded20`, with existing session model/effort, no overrides and no delegation. Initial HEAD was clean at `3225d65ea9f689b96bbc358f6a0b1f3a9338685f`; 002 was verified. Installed roadmap-write's general amendment activated and linked 003 only, version 1.4.1 → 1.4.2. `specify preset resolve spec-template` resolved core `.specify/templates/spec-template.md`; inspected `create_new_feature.py --json --number 3 --short-name deliver-approved-plan` created this directory/template/pointer. Logical helper BRANCH_NAME is 003-deliver-approved-plan; actual branch remains `reboot/2026-10-16/prompt-first`. `check_prerequisites.py --json --paths-only` resolved 003 consistently. No branch hook was invented or invoked. Full interactive specify was not invoked; its quality criteria were used only for drafting assessment.

The preparation Goal previously ended successfully at its saved Needs clarification handoff; this ordinary authoring session does not restart, reactivate, create or otherwise mutate a Goal. Actual supported get_goal before/after readback is reported in-session. The quality checklist is reconciled at 16/16 against the corrected specification, with no regression or unchecked item. Earlier briefs remain historical; a fresh installed roadmap-brief report reviews these current bytes. No new runtime verification, roadmap mutation, status write, planning/tasks, implementation, commit, merge, push, infrastructure, core-skill change or future 004 work occurs here. Existing model/effort and repository branch conventions remain unchanged.

## Current execution checkpoint

The preparation/planning handoff above is historical. Explicit full-plan approval, composite execution and the subsequent affected sequencing approval are recorded in this specification and [plan.md](plan.md). The prior saved bootstrap question is resolved by that actual approval. [Delivery notes](delivery.md) and [acceptance evidence](validation/acceptance.md) preserve prior incomplete history and current performed work. Required final independent Farmboy commit/result observation remains pending until it actually occurs after the authorized scoped commit. No result acceptance, verified transition or completed-Goal restart is authorized.

## Human result acceptance

Recorded UTC 2026-10-18: Pegagio explicitly accepted delivery commit `52435fb0d0acaae8bf0333b4feffa8d42e69e20d` after review of the actual workflow, independent final-commit verification, all33 performed tasks and disclosed evidence limits. The reviewer identified two postcommit tasks observed in-session but still unchecked in the committed snapshot, and the unavailable-native-controls case as unobserved; the user answered “Yes” to accepting on that basis and reconciling records/marking003 verified. [Acceptance evidence](validation/acceptance.md#human-result-acceptance-and-postcommit-reconciliation) records the actual observations. This supersedes historical pending-result statements only; no requirement or evidence limit changes. It authorizes the separate implemented-to-verified record, not another commit,004 activation, merge, push or integration.

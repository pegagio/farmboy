# Feature Specification: Align workflow contracts with Diagram handoffs

**Feature Branch**: `reboot/2026-10-16/prompt-first`

**Feature directory**: `specs/004-align-diagram-handoffs/` (directory identity is independent of the Git branch)

**Created**: 2026-10-18

**Status**: Draft

**Handoff**: Ready for planning — full current specification explicitly approved

**Input**: Operator-selected roadmap Feature004: align standalone Farmboy workflow contracts with Diagram-owned coordination, defining external request/context and returned outcome/evidence boundaries without duplicate queue selection. Preserve standalone use, explicit reviews, canonical Git artifacts and separate integration. Prepare a saved draft only; “start the stack” means start specification work.

## Table of Contents

The approved feature covers execution entry, outcomes and authority; historical preparation notes remain attributable below.

- [Clarifications](#clarifications)
- [User Scenarios & Testing *(mandatory)*](#user-scenarios--testing-mandatory)
- [Requirements *(mandatory)*](#requirements-mandatory)
- [Success Criteria *(mandatory)*](#success-criteria-mandatory)
- [Assumptions](#assumptions)
- [Context, rationale and unresolved topics](#context-rationale-and-unresolved-topics)
- [Saved preparation handoff](#saved-preparation-handoff)

## Clarifications

The accepted answer below was supplied by the operator in this existing session before this ordinary clarification invocation; it is recorded without repeating the question. This resolves U1 only, not approval of the whole specification.

### Session 2026-10-18

- Q: What source is authoritative for project context and feature fit when Diagram replaces the roadmap queue, and what minimum authority/provenance must the caller provide? → A: Keep existing Git constitution, direction and feature artifacts authoritative for project rules/context. The caller supplies the already selected request/intent and accessible relevant references, identifying revisions or current working state when needed to identify the work and inputs. Diagram selects once and owns eligibility/coordination; Farmboy checks the request against those documents without reselecting or re-adjudicating queue eligibility. Ask for specific missing input before dependent work when required context is materially stale, conflicting or missing; do not invent answers, reapprove unchanged work or impose fixed packets, a new brief/register, provenance subsystem, mandatory-field/counter framework, custom state or transport architecture. The user accepted the lean recommendation with “I think it seems reasonable” and confirmed “Nope, sounds good”.

## User Scenarios & Testing *(mandatory)*

These stories describe the requested contract behavior, not capabilities already delivered. A checkpoint means an exact Git revision plus the relevant artifact references; a review approves meaning at a particular checkpoint. UAT means user acceptance testing of the delivered result. The external caller supplies already selected work; Farmboy executes only the requested segment.

### User Story 1 - Execute already selected work without competing selection (Priority: P1)

As a caller coordinating work outside Farmboy, I supply one feature, its request, authoritative context/fit references, current artifacts and requested segment so Farmboy can perform bounded execution without selecting or activating work again.

**Why this priority**: Repeating local roadmap selection would create a second coordination authority and can execute the wrong feature.

**Independent Test**: Present externally selected requests for specification preparation, planning and delivery, each with applicable prerequisites. Check each entry's selection behavior and failure behavior without connecting a Diagram service.

**Acceptance Scenarios**:

1. **Given** an externally selected feature with a complete request and applicable prerequisites, **When** the requested segment starts, **Then** Farmboy uses that identity and context and performs no roadmap queue selection, eligibility decision or activation mutation.
2. **Given** identity conflicts or materially stale, conflicting or missing required context, **When** entry is attempted, **Then** Farmboy asks for the specific missing input or resolution before dependent effects; it does not choose other work, invent answers or silently use unrelated ambient context.
3. **Given** a request for planning without applicable specification approval, or delivery without applicable specification and full-plan approval, **When** entry is attempted, **Then** the segment stops before dependent effects and identifies the missing approval.
4. **Given** a segment outside the three delivered Farmboy workflows, **When** it is requested, **Then** Farmboy reports the unsupported segment without creating a workflow or selecting a substitute. Integration is described as a separate future boundary, not executed here.
5. **Given** an external feature already associated with its workspace/artifacts, **When** Farmboy resumes it, **Then** it reuses that association and preserves existing answers and pending handoff; it creates neither a second feature directory nor a fresh activation.
6. **Given** a migrated project without a roadmap queue and an already selected request with accessible relevant references, **When** Farmboy checks context/fit, **Then** it uses existing Git constitution, direction and feature artifacts for project rules/context, identifies the work/input revisions or current working state when needed, and neither re-adjudicates eligibility nor requires a new fit brief, register or fixed packet. Unchanged applicable approval is not requested again.

### User Story 2 - Resume from an inspectable outcome and checkpoint (Priority: P1)

As the coordinating caller or next owner, I receive a saved, truthful outcome with evidence and remaining input so I can route review or continuation without mistaking execution success for acceptance.

**Why this priority**: Ownership and review require an attributable result even when execution stops for input or fails.

**Independent Test**: Inspect examples for draft clarification/review, full-plan review, delivered-candidate review, required input, blocked prerequisites and interrupted execution. A reader must identify the feature, actual result and next permitted action from each handoff.

**Acceptance Scenarios**:

1. **Given** a usable draft with unresolved product choices, **When** preparation finishes, **Then** the saved handoff says Needs clarification, identifies the unresolved topics and ordinary clarification as the later separately selected step, and ends its bounded preparation Goal before answers.
2. **Given** a settled draft, **When** preparation finishes, **Then** it returns Awaiting spec review without inventing questions or granting approval. Resolved ordinary clarification also leads to review, not planning approval.
3. **Given** a passing reconciled plan or a successfully delivered local candidate, **When** that segment finishes, **Then** the outcome names the appropriate full-plan or result-review boundary and its evidence, without claiming acceptance or integration.
4. **Given** required input, a technical failure or interruption, **When** Farmboy reports the result, **Then** it distinguishes work actually completed from incomplete work, records blockers/input and resume references, and does not label a partial result successful delivery.
5. **Given** an unchanged pending handoff or a later accepted answer, **When** the same feature resumes, **Then** existing answers and performed effects are preserved; valid pending review is presented rather than replayed, and only affected work is reassessed.
6. **Given** uncommitted draft artifacts, **When** a handoff is saved, **Then** it identifies the base revision, paths and dirty state honestly instead of claiming an exact committed checkpoint exists for those bytes or committing without authority.

### User Story 3 - Preserve coordination ownership and review meaning (Priority: P1)

As the operator, I retain Diagram's coordination decisions while allowing different execution owners to work sequentially on one feature.

**Why this priority**: A useful handoff must not grant ownership or approve changed meaning merely because Farmboy finished work.

**Independent Test**: Walk through two sequential owners, a historical approval followed by routine flow-back, and a material scope change. Inspect which authority each action requires without implementing a concurrency service.

**Acceptance Scenarios**:

1. **Given** Diagram-coordinated work, **When** Farmboy executes or returns a handoff, **Then** queue, eligibility, ownership, approvals and accepted handoff records remain Diagram-owned; local reporting alone does not acquire, release or transfer ownership.
2. **Given** specification preparation has saved its draft handoff, **When** automation ends, **Then** its returned outcome enables the coordinator's prescribed release; later clarification requires separately acquired authority retained while clarification is active. Farmboy invents no local acquisition/release operation.
3. **Given** a proposed sequential owner handoff, **When** execution authority is not established or another owner remains active, **Then** dependent work stops for coordination rather than assuming a transfer. Only one agent may be active on the feature; independent features require isolated workspaces.
4. **Given** historical approval and a later accepted handoff, **When** context is reported, **Then** their checkpoint references stay distinct. Routine in-scope reconciliation preserves historical approval; material meaning changes require the affected human review again before dependent work.

### User Story 4 - Retain standalone delivery and a separate integration boundary (Priority: P2)

As a standalone operator, I continue using Farmboy without Diagram. As a later integration caller, I can distinguish a reviewed candidate from authority to integrate it.

**Why this priority**: Contract alignment must preserve local value and avoid turning delivery into a hidden integration executor.

**Independent Test**: Exercise local named/eligible selection and the three local segments in an ordinary Spec Kit project, and inspect a candidate-to-integration example separately.

**Acceptance Scenarios**:

1. **Given** a standalone project with its configured roadmap and prerequisites, **When** the operator selects a supported workflow, **Then** existing local selection/context, artifact/pointer conventions, review stops and local delivery behavior remain usable without Diagram, bridge installation or service access.
2. **Given** a verified delivered candidate and human UAT/final-result review, **When** integration is considered, **Then** only explicit applicable human authorization permits the separate integration stage. Delivery/check success alone grants neither integration nor push.
3. **Given** a later authorized integration request, **When** branch strategy, target or required checks are missing/conflicting, **Then** the contract requires surfacing that policy gap before dependent integration; Diagram owns serialization by repository/target and the external executor remains unselected and unimplemented here.
4. **Given** integration outcome evidence, **When** a receipt is recorded by the future integration boundary, **Then** its authoritative record belongs only in Diagram's database and references canonical Git checkpoints, with no receipt-only project commit or recursive receipt chain. Integration merge freezes feature meaning; later material changes use a new linked feature.

### Edge Cases

- Explicit request identity disagrees with an ambient pointer or supplied artifact: report the mismatch before effects; do not silently retarget either feature.
- A migrated project has no roadmap queue: use existing Git constitution/direction/feature artifacts and the caller-selected request with accessible relevant references; do not require or recreate a queue or selection decision.
- Required context is materially stale, conflicting or inaccessible: identify the work and input versions/current state as needed and ask for the specific missing input or resolution before dependent work. Do not invent an answer or require blanket provenance packets. An approval covering changed meaning requires affected review; unchanged applicable approval does not require reapproval.
- Duplicate invocation after delivery must inspect the actual candidate and pending review before replaying a commit or returning a fabricated new result.
- Uncommitted work is inspectable but is not an exact committed handoff checkpoint; distinguish the two without introducing an automatic checkpoint commit.
- A caller requests integration, worker dispatch or ownership changes: return the scope boundary; no implicit adapter/service operation follows.
- Native completion controls unavailable or a Goal objective extends beyond the saved handoff: disclose the compatibility/objective limitation without fake state, host file edits or a success claim.

## Requirements *(mandatory)*

The externally selected path changes workflow entry/return contracts; it does not implement a transport, bridge, integration executor or coordination store.

### Functional Requirements

- **FR-001**: Each of the three Farmboy workflows MUST distinguish standalone selection from externally selected execution. Standalone entry MUST retain its configured local selection/context behavior and require no Diagram capability.
- **FR-002**: Externally selected entry MUST accept explicit feature identity, the execution request, authoritative context/fit references, canonical artifact references and requested segment. It MUST preserve the association of that feature with existing artifacts and workspace.
- **FR-003**: Externally selected entry MUST NOT repeat roadmap queue selection, eligibility adjudication or activation. Identity conflicts, absent required references or unsupported segments MUST stop dependent effects with a precise outcome; the caller remains responsible for resolving coordination.
- **FR-004**: Existing Git constitution, direction and feature artifacts MUST remain authoritative for project rules/context after roadmap queue retirement. The caller MUST supply the already selected request/intent and accessible relevant references, identifying revisions or current working state when needed to identify the work and inputs. Farmboy MUST check the request against those documents without selecting again or re-adjudicating Diagram queue eligibility. Materially stale, conflicting or missing required context MUST trigger a specific question before dependent work. Farmboy MUST NOT invent answers, demand reapproval of unchanged applicable work or impose a new fit brief, register, provenance subsystem, fixed packet, mandatory-field/counter framework, custom state or transport architecture.
- **FR-005**: Entry MUST check applicable segment prerequisites and current-meaning approvals using available authorized evidence. A supplied request or past approval MUST NOT bypass a missing prerequisite, governance conflict or material change requiring affected review.
- **FR-006**: Every segment MUST return the feature and request/segment association, actual outcome, artifact/evidence references, checkpoint state, remaining work/input or blockers and next review or ordinary action. Complete, incomplete, blocked and interrupted outcomes MUST remain distinguishable without claiming unperformed work.
- **FR-007**: Handoffs MUST distinguish the reviewed Git checkpoint, latest accepted handoff checkpoint and current working artifacts. Exact committed references MUST identify actual revisions; dirty/uncommitted artifacts MUST disclose their base revision and state instead of claiming committed identity.
- **FR-008**: Diagram MUST retain queue, eligibility, dependency, ownership, approval and accepted handoff authority for Diagram-coordinated work. Farmboy MUST return execution data without maintaining competing writable coordination records or treating local completion as acceptance of a handoff.
- **FR-009**: Contracts MUST preserve one active agent per feature and sequential owner handoffs. They MUST distinguish the draft-completion handoff from separately authorized active clarification, with release/acquisition governed by Diagram; independent features require isolation. No scheduler, locking service or local ownership API is added by this feature.
- **FR-010**: Specification preparation MUST end at a usable saved Needs clarification or Awaiting spec review handoff. Ordinary clarification MUST occur separately after that preparation Goal, retain genuine input waits and lead to human review. Planning MUST require explicit specification approval; delivery MUST require explicit full-plan approval as well.
- **FR-011**: Routine in-scope flow-back MUST keep affected artifacts coherent and preserve historical approvals, while keeping their reviewed checkpoints distinct from later handoffs. Material changes MUST trigger affected human review before dependent work. Git MUST remain canonical for spec, plan, tasks, code and evidence.
- **FR-012**: Delivery MUST retain implementation, verification, convergence, coherent delivery documentation and the prescribed scoped local commit, ending at human result review. It MUST NOT require integration or declare integration/completion by inference.
- **FR-013**: Contracts MUST describe the separate human UAT/final-result review authorizing integration, project-defined branch/target/check policy, Diagram serialization and an external executor. Missing/conflicting policy MUST stop dependent integration; executor implementation/placement and remote push remain outside this feature.
- **FR-014**: Integration receipts MUST remain Diagram database records referring to Git checkpoints, without recursive receipt commits in the project. Only integration merge freezes feature meaning; subsequent material changes MUST use a new linked feature.
- **FR-015**: Resume MUST preserve current identity, genuine answers, performed work and pending review/input. It MUST avoid duplicate activation/directories and repeated valid effects, reassessing only missing or affected work within authority.
- **FR-016**: Contracts MUST be understandable with defined terms and concrete request/result examples for all three segments and failures. Examples MUST identify authority and limitations without prescribing a transport, new schema store or runtime infrastructure. Any material workflow behavior change MUST be verified through the actual installed skill in a real session separate from its evaluator before delivery acceptance; simulation alone is insufficient.

### Key Entities *(include if feature involves data)*

- **Execution request**: Selected feature, request intent, requested segment, references to existing authoritative context/fit documents and their relevant revision/current working state when needed, artifact references and applicable prerequisite/approval evidence. This is a semantic contract, not a prescribed wire format.
- **Execution outcome**: Actual result associated with that request, artifacts/evidence, checkpoint state, remaining work or required input, and next review/action.
- **Checkpoint reference**: Exact Git identity of committed work, distinguished from a base revision with current uncommitted artifacts; historical reviewed and latest accepted handoff checkpoints have different meanings.
- **Coordination decision**: Diagram-owned eligibility, ownership, approval or handoff acceptance; a Farmboy outcome is evidence for a decision, not the decision itself.
- **Integration receipt**: Diagram-owned record of actual integration outcome and Git references, outside the project artifact commit chain.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In all three supported external entry examples, reviewers can identify the selected feature, intent, existing Git constitution/direction/feature-artifact authority, accessible relevant references, artifacts and segment, including work/input revisions or current working state when needed. Zero examples repeat queue selection, eligibility adjudication or activation, require fixed context packets or reapprove unchanged work. Every material stale/conflicting/missing-context example asks for the specific required input before dependent work.
- **SC-002**: Every tested successful, input-required, blocked and interrupted outcome identifies actual work, evidence limitations and the next permitted action without implying acceptance, ownership transfer or integration.
- **SC-003**: All three standalone workflow journeys remain usable without Diagram or bridge setup, preserving their existing human review stops and local delivery endpoint.
- **SC-004**: All reviewed approval/change and sequential-owner scenarios distinguish historical approval from current handoff, reject unsupported authority, and require affected review for material changes.
- **SC-005**: Every candidate-to-integration example separates delivery, human authorization, project policy and actual integration outcome; zero examples imply push permission or create a project receipt chain.
- **SC-006**: Before accepting material workflow changes, an independent evaluator observes each affected installed skill's actual entry, handoff and stopping behavior in a real session, with observed results and unobserved cases explicitly distinguished.

## Assumptions

These assumptions delimit this draft and incorporate the accepted U1 answer; they confer no specification approval.

- Context/fit uses existing Git project documents plus the already selected caller request and accessible references. Identification of revisions/current state is proportionate to the work and input ambiguity, not a new provenance subsystem. Standalone workflows retain their existing context paths without Diagram.

- Dependency003 is verified in the ledger and its delivery/acceptance records are committed at clean baseline `b334eb6944bd0360366798bf9f70d7c3d5ba4912`. It is unmerged; integration is not a prerequisite for004 specification work.
- Feature004 builds forward on [001](../001-prepare-specification/spec.md), [002](../002-prepare-implementation-plan/spec.md) and [003](../003-deliver-approved-plan/spec.md); their delivered historical artifacts remain intact during this drafting task.
- Core Farmboy stays standalone. An optional bridge may later acquire work, supply context and report results. Bridge implementation/packaging, full Diagram adapter, scheduler, autonomous workers and integration executor implementation/placement are separate later work.
- Existing model/effort, standard feature setup/pointer and existing artifacts remain sufficient for drafting. No new controller, runtime delegation, installs, accounting or core-tool/constitution changes are authorized.

## Context, rationale and unresolved topics

The authority split prevents competing queues and competing writable copies of work artifacts. The distinction between execution outcome and coordination decision preserves explicit reviews and sequential handoffs. Delivery remains useful before integration policy/executor implementation exists.

The installed wiki-query was asked which contained evidence supports external selection, ownership, checkpoints, review and standalone boundaries, and whether it settles context/fit after roadmap retirement. Configuration resolves to contained `wiki/`, no environment overrides, eight-page/4000-token query caps; four index-selected pages total1478 words (conservative estimate below the cap). Supporting pages and validated registry sources are:

- [Intended Diagram integration](../../wiki/pages/diagram-integration.md), S001/S002/S004: Diagram coordination, standalone/external boundary, owner handoffs and deferred executor choices.
- [Prescribed workflow authority](../../wiki/pages/workflow-authority.md), S001/S002: bounded selection, human approval and real-session acceptance requirements.
- [Feature artifacts and merge history](../../wiki/pages/feature-history.md), S001/S002: canonical artifacts, reviewed versus current checkpoints and merge boundary.
- [Specification preparation handoff](../../wiki/pages/specification-handoff.md), S008: draft/handoff completion before ordinary clarification and review. Its older native-control limitation is historical evidence, not a claim about controls exposed in this session.

**Query verdict**: Partial. All cited source IDs exist in [sources.md](../../wiki/sources.md). The selected pages support the boundaries above but do not settle the replacement authoritative context/fit source (U1). The operator has since resolved U1 in the Clarifications section; this does not retroactively change the query coverage verdict. A likely source for later ordinary wiki ingestion is this feature's reviewed specification. No wiki mutation or external original-source access occurred in the query. Diagram-version claims in the wiki/direction are contained intended context, not independently verified live Diagram capabilities.

Directly inspected governing/current sources are the [constitution](../../.specify/memory/constitution.md), [roadmap](../../.specify/memory/roadmap.md), [direction](../../docs/direction.md), delivered001–003 contracts and003 acceptance record. The effective template is `.specify/templates/spec-template.md`, resolved by `specify preset resolve spec-template` from core. No other repository or service was accessed.

**U1 resolved**: existing Git project documents remain authoritative for rules/context, with caller-selected intent and accessible references; identify work/input versions as needed and ask for specific material context gaps without queue reselection or new machinery. No material clarification topic remains. Transport, concrete integration schemas, executor placement and bridge packaging are deferred scope exclusions, not questions this draft must answer.

## Saved preparation handoff

**Awaiting spec review**. Ordinary installed `$speckit-clarify` has integrated the actual accepted U1 answer: zero new questions asked, one existing question answered/recorded. No critical ambiguities remain. The [quality checklist](checklists/requirements.md) is revalidated at16/16 for specification coverage and clarity, not implementation or runtime acceptance. Its non-checkbox prose is retained as the earlier assessment because the installed clarify contract permits only marker toggles; this saved current assessment supersedes its historical U1/incomplete/next-clarify notes. Future implementation and actual-session acceptance remain separate delivery obligations.

The responsible current roadmap brief is refreshed under `roadmap-reviews/` against this final saved draft. The next action is human specification review at the operator's chosen depth. This answer does not approve the whole specification; only explicit specification approval permits a separately selected planning workflow. No plan/tasks, implementation, commit, merge, push, integration or active-feature change occurs.

The native preparation Goal remains complete without reactivation or update. Clarification is ordinary continuation outside that Goal. Current artifacts are uncommitted on base `b334eb6944bd0360366798bf9f70d7c3d5ba4912`; the branch remains `reboot/2026-10-16/prompt-first`. No exact committed checkpoint is claimed for the draft bytes.

**Full-spec approval applicability**: The operator explicitly approved the full current clarified004 specification with “I approve the farmboy spec”, supplied as trusted conversation in the planning invocation. Exact SHA-256 captured BEFORE adding factual approval metadata: `eac9381995c10c3d2051e591da2ca0920453caee6b43b1477ed63618fb6d64c0`. No conversation timestamp is asserted. This approval covers the complete current meaning, including external entry changes across all three existing Farmboy runtime skills; it does not authorize rewriting historical001–003 feature directories. The earlier saved Awaiting spec review text is its historical clarification handoff, now superseded by this factual approval record. Only factual approval/handoff metadata changed after the captured digest. The separately selected planning workflow is authorized; the plan is not approved and implementation remains separately gated. No approval register is added.

**Current-feature implementation reconciliation**: Following explicit full-spec/full-plan approval and separately selected standalone composite delivery,004 runtime sources and guides now express the approved external entry across all three skills while preserving standalone behavior. The helper no-write rule is clarified to compare the actual would-be persisted literal before helper execution, not merely resolved paths. This preserves the approved no-retargeting/no-activation requirement; no product intent, historical001–003 meaning, core tool or constitution changed. Actual observations and remaining limits are in [acceptance evidence](validation/acceptance.md), and the current delivery boundary is in [delivery checkpoint](delivery.md). Earlier draft/review text remains attributable history rather than current acceptance.

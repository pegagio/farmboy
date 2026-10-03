# Feature Specification: Reliable Workflow Agent Capacity

**Feature Branch**: `feedback` (existing branch; no branch created)

**Feature Directory**: `specs/018-reliable-workflow-agent-capacity/`

**Created**: 2026-10-03

**Status**: Abandoned

**Disposition (2026-10-03)**: The operator abandoned Feature 018 because the current approach and specification were not accepted as the right solution. The requirements below and the associated plan, tasks, and validation artifacts are retained as the abandoned proposal and investigation record; they are not active implementation scope. The capacity observation remains unresolved, and no replacement approach or feature is selected by this disposition.

**Input**: Resolve observation `clarify-agent-thread-limit-preflight-20261003` before the two Select Feature observations. Support sustained sequential FlowKit workflow use in a persistent Codex chat, safe completed-child lifecycle handling, bounded capacity recovery, and actionable consumer installation and upgrade guidance. The operator approved Feature 018 and explicitly requested its in-progress transition, governing-context query, specification, and roadmap brief.

## Table of Contents

This specification defines user outcomes, observable requirements, validation criteria, and approved authority boundaries.

- [Clarifications](#clarifications)
- [User Scenarios & Testing](#user-scenarios--testing)
- [Requirements](#requirements)
- [Success Criteria](#success-criteria)
- [Assumptions](#assumptions)
- [Scope and Governing Context](#scope-and-governing-context)

## Clarifications

Accepted answers refine the existing capacity-recovery scope without changing unrelated workflows.

### Session 2026-10-03

- Q: May a workflow release completed FlowKit child agents from earlier workflow invocations in the same chat? → A: Yes. Release eligible completed FlowKit children from current and earlier invocations in the same chat, with verified ownership, preserved results, and no pending interaction.
- Q: When should FlowKit release a completed child whose result is preserved and which is no longer needed for an answer or continuation? → A: Release each child as soon as it becomes eligible, with bounded recovery if a later launch still fails.

## User Scenarios & Testing

The operator invokes every workflow separately. Capacity handling supports that sequence while preserving exact named dispatch, human questions, and inspectable evidence.

Feature validation is agent-owned. The implementation agent prepares disposable consumers, applies test-only configuration, executes the selected validation sequence, supplies bounded synthetic scenario inputs, and collects evidence. The operator may provide one-time Codex project setup if required by the client; validation must not depend on the operator manually executing a test matrix or repeatedly dispatching commands. Synthetic responses exercise test interactions only and never stand in for genuine consequential human decisions or acceptance.

### User Story 1 - Continue Sequential Workflow Use (Priority: P1)

A project operator runs successive workflows in one persistent chat without completed children accumulating until another declared agent cannot launch. Results remain available after eligible children release their capacity; children needed for substantive answers or continuation remain available.

**Why this priority**: The reported Reviewer launch failure prevented Clarify from starting and can block every workflow using delegated agents.

**Independent Test**: In a disposable consumer, run at least three separately invoked workflows with more than twelve terminal children in total. Use a documented constrained capacity that requires at least two release cycles. Verify subsequent exact-name launches, preserved results, and retention of a child awaiting an answer.

**Acceptance Scenarios**:

1. **Given** a child has completed and its required result has been preserved, **When** it is no longer needed for same-step continuation, **Then** supported lifecycle handling releases its capacity immediately upon eligibility without waiting for a workflow boundary or launch failure, and preserves the result and reviewed work.
2. **Given** a readiness child has returned its validated token, **When** preflight proceeds, **Then** it becomes eligible for release and is never reused for workflow work.
3. **Given** a child is running or waiting for a substantive operator answer, **When** capacity management runs, **Then** it retains that child and relays the answer to the same child.
4. **Given** eligible completed FlowKit children from an earlier invocation occupy capacity in the same parent chat, **When** another workflow is separately invoked, **Then** it may release those children after verifying ownership and preserved results, and its exact declared agents can launch within the documented effective capacity.

### User Story 2 - Recover Safely from Exhaustion (Priority: P1)

An operator receives a specific capacity failure and bounded recovery rather than only a generic instruction to restart the chat. Recovery preserves workflow state and required human interactions without substituting an agent or silently expanding scope.

**Why this priority**: Recovery must not lose questions, replay mutations, or obscure a failed named launch.

**Independent Test**: Exercise exhaustion before workflow state exists and after work starts. Verify eligible cleanup, bounded fresh launch attempts, retained partial work, and a specific stop when safe recovery is unavailable.

**Acceptance Scenarios**:

1. **Given** an exact named launch fails before workflow work, **When** eligible completed children can be released, **Then** failure and release evidence remain inspectable, only the failed launch may be retried within the reviewed bound, and no workflow run is claimed until required preflight checks pass.
2. **Given** exhaustion occurs after partial work, **When** recovery is attempted, **Then** completed commands and mutations are not replayed, a failed launch is distinguished from an executing-child failure, and partial state and resumption instructions remain visible.
3. **Given** no eligible children exist, ownership or terminal status is uncertain, release fails, or the recovery bound is reached, **When** launching cannot safely continue, **Then** the workflow stops with the affected agent and step, observed error, attempted recovery, and smallest supported next action.
4. **Given** an unrelated chat or a child required for continuation exists, **When** capacity is exhausted, **Then** recovery does not alter it merely to obtain capacity.

### User Story 3 - Configure a Consumer at Install or Upgrade (Priority: P1)

A consumer maintainer receives a concise capacity recommendation and linked setup instructions during installation and upgrade. Guidance identifies a supported setting and tested value, preserves configuration ownership, explains merging and verification, and describes how completed-child handling prevents accumulation.

**Why this priority**: A fix proven only in the source checkout leaves consuming projects exposed to the blocking failure.

**Independent Test**: Install and refresh disposable consumers with absent, compatible, conflicting, malformed, and unsupported configuration. Verify visible guidance and byte-preservation through install, refresh, and removal.

**Acceptance Scenarios**:

1. **Given** no explicit consumer capacity setting, **When** catalog installation succeeds, **Then** its result shows the recommendation and setup reference without claiming a setting was applied.
2. **Given** an existing consumer upgrades, **When** catalog refresh succeeds, **Then** it receives actionable guidance and updated controller lifecycle behavior without silent configuration edits.
3. **Given** existing compatible, conflicting, malformed, or unsupported configuration, **When** following the guidance, **Then** the operator can inspect and merge a proposed setting while preserving unrelated values and distinguish unconfirmed effective values from verified ones.
4. **Given** the operator explicitly applies the recommendation, **When** following its verification procedure, **Then** they can determine whether it took effect and whether the tested client requires a fresh chat or another supported reload action.
5. **Given** FlowKit removal, **When** removal completes, **Then** consumer-owned capacity configuration, feedback, and retained workflow evidence remain unchanged.

### Edge Cases

These cases require a safe result rather than guessed ownership, capacity, or authority.

- A completed child has no retained result, an unresolved question, ambiguous terminal state, or missing ownership identity.
- All children are active, awaiting answers, or required for continuation.
- An unknown launch failure resembles assignment, model, or configuration failure rather than confirmed capacity exhaustion.
- The client exposes no supported release control, or release succeeds without restoring capacity.
- Preflight partially succeeds before another probe fails; partial preflight does not establish a successful run.
- Exhaustion occurs during a correction loop; completed work and iteration evidence must remain intact.
- Consumer configuration uses inherited defaults, legacy aliases, project overrides, duplicate settings, unsupported keys, or malformed values.
- Install or refresh fails partway through; guidance must distinguish applied component updates from unapplied recommendations.
- A larger capacity permits more concurrency but completed children still accumulate; this does not establish successful lifecycle resolution.

## Requirements

Requirements define observable behavior and evidence. Planning selects supported mechanisms and measured configuration values.

### Functional Requirements

- **FR-001**: Investigation MUST record tested client/runtime versions, supported capacity controls, configuration precedence, any established effective value, and the distinction between concurrent capacity and retained completed children. Unknown values and causes MUST remain explicitly unknown.
- **FR-002**: Investigation MUST distinguish the October 3 observation from historical recovery evidence. Neither the reported twelve-child count nor earlier recovery establishes the current operative limit or cause.
- **FR-003**: Before release, eligible terminal children MUST have their required result, owning workflow/preflight and step, exact agent, and validated outcome retained. Work children MUST remain fresh for each delegated step and pass; probes MUST never become work children.
- **FR-004**: Lifecycle handling MUST act only on verified terminal FlowKit children from current or earlier workflow/preflight invocations in the same parent chat whose interaction is complete and whose results require no further same-child continuation. Active, answer-waiting, continuation-required, unrelated, and uncertain-ownership children MUST be excluded.
- **FR-005**: The release procedure MUST use supported controls and record capability availability and operation results. Eligible children MUST be released as soon as their required results are preserved and no pending answer or continuation remains, without waiting for a workflow boundary or launch failure. At workflow entry, the controller MUST promptly process eligible retained children from earlier invocations in the same parent chat. Bounded recovery remains available if a later launch still fails. An accepted release operation MUST NOT be described as capacity restoration without a subsequent successful exact named launch.
- **FR-006**: Recovery MUST have a finite documented attempt bound and target only the failed launch. It MUST preserve failure and cleanup evidence, never replay completed mutations, never automatically restart an executing command child, and never bypass preflight or substitute an agent.
- **FR-007**: Exhaustion before successful preflight MUST preserve its specific diagnostic without claiming workflow execution. Failure after work starts MUST preserve partial artifacts, current step/iteration, completed results, and a safe resumption action.
- **FR-008**: Failed or unavailable recovery MUST report the exact affected agent and step, observed failure, attempted actions and results, remaining limitation, and smallest supported operator action. A fresh-chat recommendation MUST be identified as fallback rather than durable resolution.
- **FR-009**: Both catalog installation and refresh MUST show a concise capacity recommendation and setup-documentation reference. They MUST distinguish recommendations from applied settings and avoid claiming consumer adoption or effective capacity from successful installation.
- **FR-010**: Setup guidance MUST identify the supported project-level setting and consumer configuration destination, show a mergeable example with a validation-justified value, explain existing-setting and legacy-alias handling, and provide effective-setting verification and any tested reload requirement. Unsupported clients and unobservable effective values MUST be reported as limitations.
- **FR-011**: Installation, refresh, and removal MUST preserve consumer-owned Codex configuration and unrelated settings byte-for-byte. Applying a recommendation remains a separate explicit consumer action; this feature introduces no silent configuration mutation.
- **FR-012**: Guidance MUST explain the complementary roles of configured capacity and terminal-child release, the concurrency tradeoff of a larger value, and why a capacity increase alone is insufficient proof of resolution.
- **FR-013**: Validation MUST cover new installation and upgrade with absent, compatible, conflicting, malformed, and unsupported configuration, partial component-update failure, and removal preservation. It MUST separately establish sustained sequential execution, repeated safe release, protected active/answer-waiting children, unavailable recovery, and bounded exhaustion stops.
- **FR-014**: Validation MUST identify component IDs, versions, source coordinates/digests, tested CLI/client, lifecycle actions, and fresh exact-name launch outcomes. Static fixtures and no-op launch checks MUST remain distinct from live workflow/recovery evidence; portable records MUST omit raw transcripts, secrets, and absolute host paths.
- **FR-015**: Implementation MUST preserve installed workflow authority, exact assignments, same-child human answer relay, consequential gates, manual fallback, and separate later-workflow invocation. Changed recovery intent MUST be reconciled prospectively without rewriting verified feature history.
- **FR-016**: Feature 018 MUST remain independent of Features 016 and 017 and MUST NOT change centralized probing, agent names/configuration delivery, Select Feature gates, publication, Git integration, or acceptance. Its repair precedes the separately recorded Select Feature observations.
- **FR-017**: Feature validation MUST be executable by the implementation agent end to end within the authorized disposable-test scope, including environment preparation, test-only configuration, workflow invocation sequence, bounded synthetic inputs, assertions, and evidence capture. The operator MUST NOT be assigned significant manual testing work; at most one-time Codex project setup may be requested when the client requires it. Genuine consequential human decisions and acceptance remain explicit gates; unavailable automation MUST produce a specific blocker rather than a manual test assignment or a success claim.

### Key Entities

The feature handles compact lifecycle and configuration evidence rather than raw transcripts or credentials.

- **Child lifecycle record**: Exact agent, owning workflow/preflight and step, interaction state, retained result reference, release eligibility, operation outcome, and subsequent launch evidence.
- **Capacity diagnostic**: Tested environment, established effective controls, failed launch, cleanup/retry attempts, protected children, bounded stop reason, and resumption action.
- **Consumer recommendation**: Supported setting, tested value and rationale, configuration destination, merge instructions, ownership boundary, verification procedure, and reload limitations.
- **Validation record**: Source/component provenance, scenario, observed results, preserved-state assertions, and limits of proof.

## Success Criteria

These outcomes can be checked independently of the selected implementation mechanism.

### Measurable Outcomes

- **SC-001**: At least three separately invoked workflows complete in one persistent chat with more than twelve terminal children in total and at least two necessary release cycles, without capacity failure caused by accumulation of eligible completed children.
- **SC-002**: Every tested eligible child is released before advancing to the next executable step, or an unavailable/failed release is explicitly reported; newly discovered eligible children from earlier invocations are processed at workflow entry. Every release preserves its required result and ownership evidence; zero active, answer-waiting, continuation-required, uncertain-ownership, or unrelated children are released.
- **SC-003**: Every exhaustion case either launches the exact required agent within the documented finite recovery bound or produces a specific preserved-state stop; zero completed mutations are replayed and zero fallback identities are used.
- **SC-004**: Both install and upgrade cases display actionable recommendations and verification instructions across all five configuration states; removal and non-configuring operations preserve consumer configuration bytes in every case.
- **SC-005**: An operator following tested guidance can apply and verify the recommendation without restarting their chat unless an explicit tested client limitation requires it; unsupported or unobservable cases produce limitations rather than success claims.
- **SC-006**: Every validation conclusion distinguishes observed current behavior, historical evidence, static checks, and remaining uncertainty. No capacity-only increase is accepted as lifecycle resolution.
- **SC-007**: All prescribed validation commands, scenario interactions, and evidence collection are performed by the implementation agent, with zero operator-executed test cases or repeated command-dispatch steps. Any required operator environment setup is limited to one initial Codex project setup; genuine consequential decisions remain separate from test labor.

## Assumptions

These assumptions separate settled product scope from planning research.

- Consumers use the supported catalog install/refresh route; native bundle commands alone do not establish direct-controller delivery.
- The operator authorizes bounded handling of eligible completed FlowKit children from current and earlier invocations in the same parent chat. Ambiguous ownership or recovery requires an explicit decision rather than inferred permission.
- The supported setting, measured value, release mechanism, recovery attempt count, verification, and reload procedure remain technical research. If supported controls are unavailable, implementation must report a blocker rather than invent a configuration or unsafe workaround.
- Constrained test capacity makes repeated release observable. The sequence exceeds the observation's reported twelve-child count without assuming twelve was the operative limit.
- Verified Features 013, 014, and 015 are prerequisites. Features 016 and 017 are neither dependencies nor a place to absorb this repair.

## Scope and Governing Context

The [Feature 018 roadmap entry](../../.specify/memory/roadmap.md) and direct operator approval establish scope. The [constitution](../../.specify/memory/constitution.md) governs artifact consistency, human authority, generic ownership, source-only edits, evidence, and separate acceptance.

The governing wiki query supports installed workflow authority and retained consumer state ([controller design](../../wiki/pages/codex-workflow-controllers.md), S019/S020), exact named dispatch and consumer-owned agent files ([named agents](../../wiki/pages/agent-roles-and-inheritance.md), S020/S021), and consequential gates with bounded evidence ([authority and review gates](../../wiki/pages/project-authority-and-review-gates.md), S001/S017/S021). All cited IDs exist in the source registry. Coverage is **Partial**: the selected pages do not establish capacity configuration, effective limits, supported child-release semantics, or the new consumer recommendation. Future ingestion of Feature 018's reviewed research and plan is the concrete coverage remedy; no ingestion is performed by this query.

The local journal `.specify/workflow-feedback/observations.jsonl`, observation `clarify-agent-thread-limit-preflight-20261003`, records installed Clarify 0.4.5/controller 0.5.3, a successful Specifier readiness probe, and Reviewer launch failure before work. Its twelve-child count does not establish the limit or cause. [Feature 014 capacity recovery](../014-flowkit-workflow-improvements/validation/live-workflows/capacity-recovery.json) records earlier restoration after reversible archival of verified completed test children; it is historical evidence rather than proof of the current cause or a selected production mechanism.

This feature prospectively amends Feature 013 recovery/delivery contracts and Feature 014 lifecycle/validation behavior while preserving Feature 015 exact assignments. Existing generic stop rules must be reconciled through specification, plan, and tasks before source implementation. Excluded are Select Feature changes, centralized probing, agent configuration delivery, unrelated chats, silent consumer configuration changes, roadmap verification, Git integration, publication, and acceptance. This draft does not authorize implementation or an unrequested later workflow.

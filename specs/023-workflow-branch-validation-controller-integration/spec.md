# Feature Specification: Workflow Branch Validation and Controller Integration Coverage

**Feature**: 023

**Feature Branch**: None; the selected feature is being authored in a detached checkout.

**Created**: 2026-10-13

**Status**: Complete

**Input**: Author Feature 023 from its approved roadmap entry: detect malformed FarmBoy-owned workflow branches before installation or effects and provide executable coverage of complete controller progress and guarded re-entry in source and disposable installed consumers.

## Table of Contents

This specification defines observable validation boundaries and regression outcomes; implementation allocation belongs to later planning.

- [User Scenarios & Testing](#user-scenarios--testing-mandatory)
- [Requirements](#requirements-mandatory)
- [Success Criteria](#success-criteria-mandatory)
- [Assumptions](#assumptions)
- [Authority and Source Context](#authority-and-source-context)

## User Scenarios & Testing *(mandatory)*

Maintainers need early, actionable diagnostics. Operators need supported routes and reviewed continuation to work while preserving evidence and human authority.

### User Story 1 - Reject invalid definitions before delivery (Priority: P1)

As a maintainer, I can validate owned workflow definitions before installation so malformed branches never reach consumers or begin workflow effects.

**Why this priority**: WR-01 showed a misplaced default stopping an authorized invocation before source execution. Early detection removes avoidable operator recovery.

**Independent Test**: Validate representative valid and invalid definitions through source/catalog checks, inspect diagnostics, and prove invalid definitions cause no installation or workflow effects.

**Acceptance Scenarios**:

1. **Given** a switch with `cases.default` instead of a top-level `default`, **When** source/catalog validation runs, **Then** it rejects the definition before installation or workflow effects and identifies the workflow ID, exact step ID, offending `cases.default` structure, and correction to place `default` alongside `cases`.
2. **Given** a malformed case/default or route structure unsupported by the current reviewed controller contract, **When** definition validation runs, **Then** it rejects the definition with an exact location and actionable correction before installation or effects.
3. **Given** a supported empty case or top-level empty default, **When** definition validation runs, **Then** it accepts that skip rather than treating emptiness as a missing branch.
4. **Given** a template input references an unknown producer or one that cannot supply it before consumption on the selected route, **When** definition validation runs, **Then** it rejects the reference; a valid earlier-producer reference is accepted without requiring its output before execution.

### User Story 2 - Execute only the selected valid route (Priority: P1)

As an operator, I can follow a supported preparation or source route while skipped work remains skipped and producer-dependent inputs are checked when they become necessary.

**Why this priority**: Structural validity alone does not prove actual routing honors skips or resolves inputs at the right boundary.

**Independent Test**: Exercise supported choices through production routing, observing selected/skipped steps and required input availability before effects.

**Acceptance Scenarios**:

1. **Given** a supported source choice that skips preparation, **When** routing advances, **Then** preparation steps do not execute and their branch-local outputs are not required.
2. **Given** a supported preparation choice that skips source execution, **When** routing advances, **Then** source steps do not execute and their branch-local outputs are not required.
3. **Given** a supported empty case or default is selected, **When** routing advances, **Then** it performs no branch-local work and proceeds to its declared successor with applicable guards intact.
4. **Given** a consuming input depends on an eligible earlier producer, **When** that producer has not run, **Then** the valid reference does not prematurely block the invocation; after production, the consuming step proceeds only if its required current output is available and valid.
5. **Given** a selected choice has no supported case/default or a selected consuming step lacks a valid required output, **When** runtime preflight reaches the boundary, **Then** it blocks before the affected step's effects and reports an exact blocker and safe next action.

### User Story 3 - Continue after independently reviewed progress (Priority: P1)

As an operator, I can continue an authorized controller sequence after genuine reviewed progress and permitted task tracking while the original assessment remains trustworthy historical evidence.

**Why this priority**: WR-02 showed a historical baseline rejected solely because valid later task bytes differed. Re-entry must preserve historical proof and independently check current requirements.

**Independent Test**: Exercise assessment → eligible source dispatch → independent review → marker-only task tracking → post-pass capture → guarded re-entry as one connected sequence. Change one guard at a time to verify attributable rejection.

**Acceptance Scenarios**:

1. **Given** trusted retained pre-effect assessment evidence bound to the selected scope and an eligible source pass, **When** independent review substantiates substantive task resolution and permitted marker-only tracking changes task bytes before post-pass capture, **Then** re-entry selects next eligible work using valid current evidence without requiring the historical digest to match new task bytes.
2. **Given** legitimate source corrections within authorized scope produce independently reviewed substantive resolution and current source differs from historical preimages, **When** post-pass capture and re-entry occur, **Then** the retained historical baseline remains valid and required current evidence is separately verified.
3. **Given** historical evidence is forged, altered, missing, or unbound, **When** re-entry is requested, **Then** it blocks without reconstructing pre-effect proof from current files.
4. **Given** required current evidence is stale, a required output is missing, or task edits exceed the independently reviewed permitted tracking change, **When** re-entry is requested, **Then** it blocks even with otherwise trustworthy historical evidence.
5. **Given** a pass lacks independently substantiated substantive progress or an existing declared limit is exhausted, **When** continuation is requested, **Then** it stops with retained evidence and a precise safe next action; command success, marker changes, administrative updates, questions, and child restarts neither manufacture progress nor refill limits.
6. **Given** a required assignment is unavailable or a consequential human decision is unresolved, **When** the affected boundary is reached, **Then** it stops without fallback, bypass, scope expansion, or another workflow; permitted question continuation relays the answer to the same assigned child.

### User Story 4 - Trust installed-consumer regression results (Priority: P2)

As a maintainer, I can compare source and disposable installed-consumer behavior and distinguish deterministic observations from actual live-agent evidence.

**Why this priority**: Source-only checks cannot establish installed behavior, and simulated dispatch cannot establish live-agent behavior.

**Independent Test**: Run representative parity cases and connected continuation sequences against source and a disposable installation of the same snapshot. Compare outcomes and inspect provenance.

**Acceptance Scenarios**:

1. **Given** source and a disposable initialized consumer share the same component snapshot, **When** supported skip/empty/default routes, producer-dependent input timing, and the complete positive sequences run, **Then** they agree on selected steps, input boundaries, guard decisions, and continuation outcomes.
2. **Given** representative invalid definitions, **When** supported installation is attempted, **Then** it rejects them; **Given** an invalid installed snapshot encountered during invocation, **When** runtime validation runs, **Then** it rejects before workflow effects with equivalent actionable diagnostics.
3. **Given** connected negative continuation cases in both environments, **When** outcomes are compared, **Then** historical-binding, current-evidence, unauthorized-edit, missing-output, no-progress, and exhausted-limit guards block consistently.
4. **Given** a report uses deterministic simulated dispatch, **When** its evidence is read, **Then** it identifies that mode, observed results, component IDs/versions/source digests, tested CLI version, and source coordinates and makes no live-agent, publication, stock compatibility, or adoption claim.
5. **Given** the changed validation behavior and an observed blocked route, **When** maintainers or operators consult the documentation, **Then** they can identify the applicable validation boundary, interpret the diagnostic, find the safe next action, and distinguish observed evidence from unverified claims.

### Edge Cases

Each case preserves the distinction between definition validity, selected-route availability, and continuation authority.

- Empty lists are valid skips only where supported by the reviewed contract; absent, wrongly typed, and unsupported branch structures remain errors.
- An unknown selected choice without a supported default blocks before its affected effects; a supported top-level default routes normally.
- Untaken branches have no execution or branch-local output obligation, but malformed definition structure remains a definition-validation error even when untaken.
- Valid earlier-producer references need no output at invocation start; a missing/invalid output after production blocks consumption.
- Historical source/task digests may differ after reviewed work; stale required current digests must still fail.
- Later marker changes, post-pass capture, or fresh assessments cannot recreate missing original pre-effect proof.
- Interrupted or changed installation/workflow evidence retains its stop and follows existing safe-scope reassessment/resumption policy rather than silently continuing.

## Requirements *(mandatory)*

The feature strengthens validation and coverage within existing FarmBoy ownership and authority; it does not redesign continuation accounting.

### Functional Requirements

- **FR-001**: FarmBoy MUST validate owned source/catalog definitions before installation or workflow effects, rejecting malformed switches/cases/defaults, unsupported route structures, and invalid template/producer references. Checks MUST cover all active owned workflow packages and preserve deprecated Start Feature's stop-only contract.
- **FR-002**: Definition diagnostics MUST identify workflow ID, exact step ID, offending structure/reference, and actionable correction. Nested `cases.default` MUST explicitly direct placement of `default` alongside `cases`.
- **FR-003**: Definition validation MUST accept supported empty cases/defaults and valid earlier-producer references without demanding outputs before production. It MUST reject unknown or route-incompatible producers and references that cannot be available before consumption.
- **FR-004**: Runtime preflight MUST validate the selected route and currently required inputs before the consuming step's effects. It MUST defer legitimate producer-dependent availability checks until production and verify current outputs at consumption.
- **FR-005**: Routing MUST execute only the selected supported branch. Untaken branches MUST neither execute nor require branch-local outputs; supported empty selections MUST reach their declared successor without branch-local effects.
- **FR-006**: Unsupported selected choices, invalid installed structures, or missing/invalid required inputs MUST block before affected effects, preserving observed evidence and reporting the exact blocker and safe resumption action under existing policy.
- **FR-007**: Executable coverage MUST exercise the connected assessment → eligible source dispatch → independent review → marker-only task tracking → post-pass capture → guarded re-entry sequence for reviewed substantive task resolution and legitimate reviewed source corrections. Isolated helper tests alone do not satisfy it.
- **FR-008**: Re-entry MUST preserve trusted retained pre-effect historical evidence with original scope binding and digests, independently validate required current evidence, and permit legitimate reviewed preimage differences without replacing history.
- **FR-009**: Negative coverage MUST demonstrate continued blocking of forged/altered/missing/unbound historical evidence, stale required current evidence, unauthorized task edits, missing required outputs, no substantive progress, and exhausted existing declared limits. Each guard MUST be exercised with otherwise valid surrounding conditions so its observed blocker is attributable.
- **FR-010**: Markers, command success, administrative updates, question answers, and child restarts MUST NOT count as substantive resolution, reset limits, or reconstruct historical proof. Current reviewed accounting policy MUST remain intact.
- **FR-011**: Validation and coverage MUST preserve exact reviewed named assignments, independent review, consequential human gates in the main controller, same-child answer relay, bounded correction, safe stops, and manual fallback. Missing, invalid, or unavailable assignments MUST stop without silent fallback.
- **FR-012**: Successful routing/correction/validation MUST NOT grant another phase, roadmap verification, Git integration, feature acceptance, or consumer/Diagram acceptance. Consequential authority/scope changes MUST retain their explicit human gate.
- **FR-013**: Coverage MUST exercise actual production routing APIs and guard behavior, reusing the current controller, graph/path tests, and disposable-consumer fixtures. Test-only reproductions of routing/guard decisions MUST NOT substitute for production behavior. Harness architecture/allocation remain planning work.
- **FR-014**: Disposable initialized-consumer integration MUST verify source parity for supported preparation/source skips, empty/default routes, malformed/default rejection, producer-dependent input timing, and connected positive/negative continuation cases. Consumers MUST have the prerequisites needed for these scenarios and use supported source snapshot installation.
- **FR-015**: Portable observations MUST record component IDs, versions, source digests, tested CLI version, source coordinates, scenario, execution mode, expected/observed outcome, and effects/dispatch observed or prevented. They MUST omit raw transcripts, secrets, and absolute host paths.
- **FR-016**: Reports MUST distinguish deterministic simulated dispatch from actual live-agent observations. Deterministic coverage suffices for required regression outcomes; it MUST neither require nor imply live-agent execution, effective agent settings, publication, stock Spec Kit compatibility, or consumer adoption.
- **FR-017**: Changed validation behavior, boundaries, diagnostic interpretation, and evidence limits MUST be documented, including identification of blocked routes and safe next actions.

### Key Entities

These describe inspectable evidence and decisions rather than storage or implementation mechanics.

- **Workflow definition**: Reviewed component identity/version/digest, steps, supported branches, assignments, and producer/consumer dependencies.
- **Selected route**: Supported choice, selected steps, successor, and currently required inputs; untaken branches remain separate.
- **Historical assessment binding**: Trusted retained pre-effect evidence tied to original scope and source/task preimages.
- **Current evidence**: Present inputs, independent review, task tracking, and post-pass observations required for the next guarded decision.
- **Validation observation**: Portable scenario result with provenance, execution mode, observed/prevented effects, outcome/diagnostic, and source/installed comparison.

## Success Criteria *(mandatory)*

Outcomes are measured against the acceptance scenarios; successful checks establish observations rather than feature acceptance.

### Measurable Outcomes

- **SC-001**: Every malformed/unsupported definition scenario is rejected before installation or workflow effects, with zero delegated dispatches and all four diagnostic elements: workflow ID, step ID, offending structure/reference, and actionable correction.
- **SC-002**: All supported skip and empty/default scenarios select the expected successor, execute zero untaken steps, and require zero outputs solely from untaken branches.
- **SC-003**: Every valid producer-dependent reference is accepted before production and checked before consumption; every missing/invalid required input blocks before its consuming step's effects.
- **SC-004**: Both connected positive scenarios complete guarded re-entry with original historical evidence intact and current evidence independently validated: substantive task resolution followed by marker-only tracking, and reviewed source correction with differing historical preimages.
- **SC-005**: Every FR-009 negative guard blocks in source and installed-consumer observations, with zero unauthorized continuations or consumed-limit resets.
- **SC-006**: Every FR-014 parity scenario has matching source/installed outcomes; differences remain reported validation failures.
- **SC-007**: Every observation contains FR-015/FR-016 provenance and execution-mode information; zero simulation results claim live behavior or broader publication, compatibility, adoption, or acceptance proof.

## Assumptions

Approved scope settles observable boundaries; technical allocation and harness mechanics remain for separately invoked planning.

- **Existing behavior**: WR-01 and WR-02 are fixed historical defects and permanent regression cases, not assertions of current broken source.
- **Dependencies**: Features 013, 014, 020, and 021 are verified roadmap prerequisites. Features 024/025 are complementary, not prerequisites; Feature 022 provides historical evidence rather than a required metrics dependency.
- **Validation boundaries**: Definition structure and reference feasibility are checked before installation/effects; selected-route current availability before consumption; installed consumers establish representative parity and connected sequences.
- **Reuse**: Existing production controller/routing, graph/path tests, fixtures, supported runtime pins, and installation mechanisms are the starting point. No new engine, framework, dependency, or build tool is authorized.
- **Exclusions**: Changes to Spec Kit, Codex, independently owned extensions, other projects, continuation/accounting redesign, replacement caps, budget resets, and weakened authority/evidence/correction guards are excluded.
- **Evidence limits**: Deterministic tests establish routing/guard observations. Live-agent validation is not required; separately authorized live observations must be described only to the extent observed.

## Authority and Source Context

Direct roadmap, constitution, and findings supply Feature 023 requirements where the wiki lacks feature-specific coverage. Wiki summaries explain existing authority and guards without creating scope.

- **Approved scope**: [Roadmap entry 023](../../.specify/memory/roadmap.md) defines outcomes, boundaries, dependencies, and historical regression framing.
- **Governing authority**: [Constitution 8.0.0](../../.specify/memory/constitution.md), especially Principles II–V, governs human authority, source ownership, manual fallback, component boundaries, and evidence claims.
- **Findings**: [Feature 023 handoff](../../docs/findings/2026-10-12-workflow-reliability-handoff.md#feature-023-branch-and-integration-validation) and WR-01/WR-02 identify required routing and historical-evidence regressions.
- **Original observations**: [WR-01 blocked routing](../022-local-workflow-agent-timing-metrics/validation/implementation/blocked-routing.json) records nested defaults and prevention of source dispatch; [WR-02 blocked re-entry](../022-local-workflow-agent-timing-metrics/validation/implementation/blocked-reentry-after-tracking.json) records valid tracking followed by incorrect historical/current comparison. They describe their original observation time.
- **Authority context**: [Project authority and review gates](../../wiki/pages/project-authority-and-review-gates.md) (S035) summarizes Constitution 8 and invocation limits.
- **Controller context**: [Workflow graph responsibility boundaries](../../wiki/pages/workflow-graph-responsibility-boundaries.md), [Controller assessment contract](../../wiki/pages/controller-assessment-contract.md), and [Workflow loop baselines and limits](../../wiki/pages/workflow-loop-baselines-and-limits.md) (S033) summarize phase ownership, retained historical/current evidence, independent substantive resolution, and existing limits.

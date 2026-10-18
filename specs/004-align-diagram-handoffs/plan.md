# Implementation Plan: Align workflow contracts with Diagram handoffs

**Branch**: `reboot/2026-10-16/prompt-first` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

**Input**: Full approved clarified Feature004 specification. Pre-approval-metadata SHA-256: `eac9381995c10c3d2051e591da2ca0920453caee6b43b1477ed63618fb6d64c0`. Direct approval: “I approve the farmboy spec”. No approval timestamp inferred.

**Stage**: Delivered and explicitly accepted — all27 tasks performed; roadmap verified; scoped acceptance-record commit authorized.

## Summary

Add usable externally selected entry and consistent result handoffs to all three existing Farmboy Markdown skills, preserving each standalone entry. Branch explicitly on caller-selected external execution before local queue selection/activation or local-only roadmap operations. The caller identifies work, intent, segment, authoritative Git context and artifact references in ordinary language; no fixed packet/schema is required. Diagram selects and owns coordination. Farmboy validates local execution context and applicable approvals without re-adjudicating queue eligibility. Ask for specific material missing/stale/conflicting input before dependent work.

Each skill retains its existing segment implementation and human boundary. External specification drafting uses caller-associated artifacts and the effective template, without roadmap activation or a second directory. External planning uses ordinary plan/tasks/read-only analysis plus separate authorized repair. External delivery retains implementation/check/convergence/documentation and its prescribed local scoped commit, returns the candidate to result review and leaves coordination status/acceptance to the caller. Integration is described, not executed.

## Table of Contents

The proposal separates scope, mechanisms, validation and review so the full implementation can be assessed before work starts.

- [Technical Context](#technical-context)
- [Constitution Check](#constitution-check)
- [Project Structure](#project-structure)
- [Implementation Design](#implementation-design)
- [Mechanisms and Alternatives](#mechanisms-and-alternatives)
- [Verification and Delivery Sequencing](#verification-and-delivery-sequencing)
- [Review Handoff](#review-handoff)

## Technical Context

**Language/Version**: Markdown skills and documentation; existing installed Spec Kit Python helpers, currently Specify1.0.10.dev0+pegagio.2. Validation scripts belonging to skills use `~/.codex/venvs/skill-tools/bin/python`. No new language runtime.

**Primary Dependencies**: Existing ordinary Spec Kit plan/tasks/analyze/implement/converge, template resolution and local roadmap/wiki extensions on their standalone paths. Native Goal controls only when explicitly selected and exposed. No new package, library, build tool, service, model routing or runtime agent dependency.

**Storage**: Existing canonical Git feature artifacts and `.specify/feature.json` workspace association. Existing spec/plan/delivery notes hold handoffs. Diagram's own coordination/receipt records are outside implementation scope. No new runtime persistence.

**Testing**: Existing Markdown fixture conventions, focused link/frontmatter/privacy/static checks and separate real-session evaluator observations of affected installed skills. No framework or automated runtime harness added. [Quickstart](quickstart.md) defines future cases, not executed evidence.

**Target Platform**: Existing Codex/Spec Kit project environment; portable skill directories, current session model/effort and standard contained workspace conventions.

**Project Type**: Three thin human-driven Markdown workflow compositions; no server, executable adapter or API.

**Performance Goals**: No queue reselection/duplicate effects; preserve bounded handoffs and ordinary continuation without introducing artificial latency/throughput targets or repair quotas.

**Constraints**: No historical001–003 rewrite, core skill/helper or constitution change, service/repository access expansion, new coordinator/transport/bridge/executor/scheduler/worker implementation, counters/reset/score/accounting framework. Current full004 approval authorizes needed runtime edits to all three Farmboy skills; the earlier001 roadmap exclusion does not prohibit forward004 runtime work.

**Scale/Scope**: Three entry paths and their standalone regressions; one active execution owner per feature is coordinator policy, not a Farmboy lock/service implementation.

## Constitution Check

These gates passed before research and were rechecked after design; they constrain the later implementation, not a claim of runtime acceptance.

| Principle | Pre-research assessment | Post-design assessment |
|---|---|---|
| I — Flow-back/history | Approved004 builds forward; preserve historical001–003 directories | Runtime sources/docs change under004; keep004 spec/plan/tasks coherent; only integration merge freezes meaning |
| II — Prescribed authority | Full-spec approval and selected planning only | Ordinary installed commands; no implementation now; external request cannot grant coordination or next-phase authority |
| III — Bounded toil/simplicity | Existing capabilities suffice; no new infrastructure justified | Three small inline entry branches, existing artifacts, explicit missing-input/review stops; future real-session executing subject separate from evaluator |

All prerequisites001–003 are verified.003 is committed but unmerged; integration is not a planning prerequisite. No constitutional exception or amendment is needed. Ordinary input after an automation handoff occurs outside its completed Goal; no automatic restart is introduced.

## Project Structure

This feature adds design/evidence documents and edits existing runtime sources only after full-plan approval and separately selected implementation.

### Documentation (this feature)

`specs/004-align-diagram-handoffs/` holds spec.md, plan.md, research.md, data-model.md, contracts/workflow-handoffs.md, quickstart.md and tasks.md. Future `validation/acceptance.md` holds actual observations in the existing feature-evidence convention; it is not a runtime database. Existing roadmap reviews remain historical evidence.

### Source Code (repository root)

Planned changes: `.agents/skills/farmboy-prepare-specification/SKILL.md`, `.agents/skills/farmboy-prepare-implementation-plan/SKILL.md`, `.agents/skills/farmboy-deliver-approved-plan/SKILL.md`; their three existing `docs/` guides; `README.md`; new explanatory `docs/workflow-handoffs.md`; new `tests/fixtures/diagram-handoffs/cases.md`. No new script or framework is needed. Core `.specify/scripts/`, installed core `speckit-*` skills and constitution stay unchanged. Historical specs001–003 are read-only references, not edit targets.

**Structure Decision**: Keep each shipped skill self-contained. A short common semantic contract is repeated where needed, while the new guide explains usage without becoming a required runtime include. Do not install or invoke a fourth bridge skill.

## Implementation Design

Research decisions and helper evidence are in [research.md](research.md); [data-model.md](data-model.md) describes semantic concepts without a serialized format. [Contract](contracts/workflow-handoffs.md) defines concrete three-segment examples, routing, failures, authority and checkpoint rules.

1. Resolve entry intent before effects: standalone keeps current local roadmap selection/prerequisite/context behavior; explicit external request uses caller-selected identity/intent/segment/references and never runs queue selection/activation. Ambiguous entry intent is a specific required input, not inference of external authority. An explicit external request remains subject to applicable local project rules and segment prerequisites.
2. Inspect caller-associated feature artifacts and workspace. Existing pointer, if present, must agree before any helper; a mismatch is not repaired by retargeting. Core helpers require an associated standard workspace pointer; the caller must supply that association when missing. Verify any effective SPECIFY_FEATURE_DIRECTORY also resolves to that same existing association before invoking normal helpers; their normal mode can persist a directory, so do not let environment resolution retarget or mutate the pointer during read-only assessment. This is local artifact resolution, not a second roadmap activation or new caller packet. In the supported ready workspace, no pointer/queue mutation occurs. External specification can fill a missing spec at the caller's already associated directory using the resolved template, without invoking create-new-feature or generating a number. Missing supported capability is a precise stop; no helper installation/core patch.
3. Context/fit checks use existing Git constitution/direction/feature files plus selected intent and accessible relevant references, identifying revisions/current state only as needed. External entry substitutes this document check for local roadmap queue fit/brief; it does not require an absent roadmap/wiki or a new fit report. Existing relevant wiki context may be queried if configured/authorized; no access expansion follows references.
4. Keep segment bodies and required human reviews. External planning/delivery check applicable approval evidence and local execution prerequisites, while Diagram owns queue eligibility/dependencies. Do not reapply local verified-ledger gates to external queue decisions. Missing governance or material context blocks dependent steps with a specific question; unchanged approvals remain applicable.
5. Return consistent human-readable execution data in existing notes: feature/request/segment, actual outcome, artifacts/evidence, actual Git checkpoint or honest dirty-state/base reference, required input/blockers/remaining work and next review/action. Do not introduce mandatory named fields, counters, fixed packets, a register or persistence format. Preserve pending handoffs and changed answers; repeat only affected work.
6. Standalone delivery retains roadmap-debrief/write and wiki closeout exactly as prescribed. External delivery does not require/recreate a retired local roadmap queue, run its queue-status update or invent a debrief entry. Instead compare delivery against the selected request and canonical artifacts in existing delivery notes; configured applicable wiki documentation maintenance remains, without requiring a new wiki in a migrated project. Return the actual committed candidate for coordinator-owned handoff/status/review. The local scoped commit remains required for successful delivery; external outcome does not mark local or Diagram verified, accept/release ownership, integrate or push.
7. Document coordinator-owned single-active-owner, release after durable draft handoff, separately acquired active clarification and sequential handoffs without implementing the ownership service. Keep historical reviewed checkpoints distinct from accepted handoffs. Material changes require affected review; routine flow-back does not erase historical approval.
8. Document final-result/UAT review as explicit integration authorization, project branch/target/check policy, missing-policy stop, Diagram serialization and Diagram-only receipt references. No integration executor or receipt write is implemented. Later integration merge freezes history; later behavior changes use new linked features.

## Mechanisms and Alternatives

Every proposed addition, including ordinary persistent artifacts/dependencies, is disclosed here. No new runtime subsystem, dependency or persistent coordination structure is proposed.

| Item | Responsibility and concrete need | Simpler alternative | Tradeoff and recommendation |
|---|---|---|---|
| Inline entry branch in each existing skill | Honor already selected external work while retaining local entry | Require manual bypass of local steps | Small repeated text is easier to ship/review than a loader/controller; recommend explicit self-contained branches |
| Common outcome language in existing notes | Make continuation/review inspectable without granting authority | Conversation-only return | Saved ordinary artifacts survive interruption; no schema/register; recommend concise existing-note handoffs |
| Existing pointer/core helper use | Resolve the same contained artifacts for ordinary core commands | Patch core helpers or transparently retarget | Caller-associated workspace avoids new activation effects; precise missing-association input is preferable to hidden retargeting; no new pointer file type |
| New docs/workflow-handoffs.md | Explain external usage/ownership/integration and all three examples | Repeat full explanation in three guides | One linked explanatory guide reduces drift, but is not runtime-required; recommend guide plus self-contained skills |
| New fixture cases and ordinary004 acceptance.md | Define affected cases and later observed evidence | Static review alone | Real-session observation costs time but is constitutionally required; reuse Markdown conventions and manual/separate evaluator, no harness |
| Current feature plan/research/data-model/contracts/quickstart/tasks | Reviewable design and ordered work required by installed planning | Conversation-only proposal | Normal Git documents are durable review material, not runtime persistence; recommend existing Spec Kit artifacts |
| Existing Spec Kit extensions/native controls | Preserve local workflow behavior and explicitly selected bounded Goals | New execution framework or global configuration | Resolve capabilities at use; disclose unavailable controls without substitution. No new dependency/install |

No new approval register, request schema store, provenance service, counters/reset semantics, progress scores, accounting, controller, bridge, transport, scheduler or ownership service is proposed. Continuation reads current artifacts and actual findings; it has no numeric repair-cycle limit. Optional suggestions cannot hide an unmet obligation or prolong polishing.

## Verification and Delivery Sequencing

After explicit plan approval and separate implementation selection, write fixture expectations before runtime edits. Proportionate acceptance uses a separate real Codex executing session from its evaluator for each affected installed skill. Reuse the same model/effort; no per-step runtime delegation. A human can serve as evaluator; do not add a harness. Run positive external entry for all three segments, standalone regressions for all three, and representative context/identity/approval/missing-capability/scope failures, resume and genuine review/input stops. [Quickstart](quickstart.md) maps cases to requirements and evidence. No experiments are run by planning.

Record actual source/work versions and limitations in ordinary004 acceptance notes. Do not claim all possible unavailable-control cases passed if not observed. Tests establish behavior only; explicit human acceptance remains separate. For this self-hosted planning-skill change, verify the candidate skill in a disposable project with TEST ONLY approvals after source edits, not by demanding a future004 final commit before it may exist. Required precommit checks and independent affected-skill observations precede local delivery commit; inspect the actual final commit afterward in conversation before result review. No recursive receipt-only commit or self-referential precommit proof task.

## Review Handoff

**Awaiting full-plan review**. Proposal artifacts: [research](research.md), [data model](data-model.md), [contract](contracts/workflow-handoffs.md), [quickstart](quickstart.md), [tasks](tasks.md) and this plan, all interpreting the approved [spec](spec.md). The final analysis result is reported in this session and current hashes bind its evidence. No analysis report store is added. All implementation/verification task markers remain unchecked. Optional suggestions: none proposed.

The operator must explicitly approve the complete plan before separately selecting implementation. This planning workflow stops before implementation, runtime experiments, delivery status changes, commit, merge, push or integration. This new planning Goal is separate from the completed specification-preparation objective; only the matching saved endpoint may complete it through supported controls/readback.

**Planning assessment checkpoint**: The first actual read-only analysis found an incorrect acceptance-scenario count in T025 and an overbroad no_persist claim in research. Separate authorized drafting repair changed22 to20 and documented the exact paths-only versus normal-helper behavior plus pre-effect environment/pointer agreement. No requirement or approved meaning changed; all27 task identities are preserved. Fresh actual installed read-only analysis after those repairs reported zero actionable inconsistencies and zero unmet planning-coverage requirements:22/22FR/SC items covered,20 scenarios,27 ordered unchecked tasks, zero unmapped tasks/constitution conflicts/ambiguities/duplications, no optional suggestions. Its structured coverage report and current-artifact hashes are in this session. This factual assessment/handoff note is recorded separately from the read-only analyzer; a final fresh assessment checks the saved version before native completion. All implementation and future runtime acceptance remain pending, not planning prerequisites. No material question or optional addition remains.

**Full-plan approval and execution applicability**: The operator explicitly approved the FULL current27-task proposal and separately selected composite implementation/delivery: “Approved. Proceed with implementation”. Exact current plan SHA-256 captured BEFORE this metadata: `a702681bd386e19413853e7017e0cd518ce0c0f6effd9f9e1b571aa1463e93a5`. No conversation timestamp is asserted. This applies to all27 ordered tasks, all supporting design and needed runtime changes across all three existing Farmboy skills/guides, with standalone compatibility and historical001–003 feature directories preserved. Earlier proposal/review text remains its historical checkpoint, superseded as to approval by this factual record. Actual installed farmboy-deliver-approved-plan is selected in standalone mode for004, including ordinary implement/check/converge and authorized repairs, documentation/debrief/wiki, narrow implemented recording and final scoped LOCAL commit. No verified/acceptance, next feature, merge, push or integration is authorized.

**Helper no-write clarification**: For helper-dependent external execution, the standard caller-established pointer must already exist and the helper's would-be persisted value must equal its existing literal value. Resolved path equality alone is insufficient: equivalent aliases/trailing separators can rewrite pointer bytes. Inspect the installed persistence convention before helpers; when it would write, ask for that specific conventional caller preparation, without silently changing environment/pointer or patching core tools. This is a precision correction within the approved no-retargeting/no-activation contract, not a new runtime mechanism.

**Implementation-stage metadata**: The full current proposal was explicitly approved and actual standalone delivery separately selected, as recorded above. Runtime entry/result/ownership guidance was implemented in the three approved Farmboy skill files; no shared runtime loader, new dependency or state mechanism was added. Independent runtime evaluation is ongoing and current performed task markers/evidence are authoritative; no real result acceptance, verified status or integration has occurred. The earlier plan-review checkpoint is historical.

## Accepted delivery closeout

Actual standalone delivery completed at `c77591602d16a2503ec66ee0b679ec308d64ebd1` on `reboot/2026-10-16/prompt-first`, committing all29 scoped files. Postcommit readback confirmed the actual scope, clean worktree/index, selected004 implemented and001–003 unchanged/verified; historical001–003 directories remained unchanged. Independent real-session observations, convergence, debrief and wiki lint are recorded in [acceptance evidence](validation/acceptance.md#accepted-delivery-and-postcommit-readback).

Pegagio subsequently explicitly accepted the result and authorized committing these scoped records with “Let's commit both of these results. I accept them.” The separate004 implemented-to-verified transition is authorized; all27 tasks are performed. Unobserved live Diagram integration and native-failure experiments remain unobserved. This current closeout supersedes earlier pending-review/precommit notes without changing approved behavior or historical evidence. No new test campaign, merge, push, integration or next-feature activation follows.

# Implementation Plan: Prepare implementation plan

**Branch**: `reboot/2026-10-16/prompt-first` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

**Status**: Revised 31-task delivery verified and accepted by Pegagio on 2026-10-17; local delivery commit authorized; not integrated. Earlier automatic native input waiting remains FAILED/UNACCEPTED.

**Input**: Pegagio approved specification content SHA-256 `45f531df10edb4303b4e2c04e63b6e81664678995cf058065c97dc69390a68a1`. Approval was captured before editing metadata. Reviewed pre-acceptance-record spec SHA-256 `75bbd7f9c4cf91478dc375da58771fd4b1e52ccb6b70b1dcae2ed3e67a88da3e` includes the explicitly approved material human-input endpoint revision below; earlier metadata-only statements apply only to their recorded checkpoint. Approval-time metadata reversal reproduced approved bytes before later factual flow-back. The latest user instruction explicitly authorizes the changed FR-012, human-input acceptance scenario and SC-006 verification obligation. Same owner/session: Pegagio, `01a14b62-0782-7c30-8824-31199e2d0d0b`. Setup's `BRANCH=002-prepare-implementation-plan` is a logical feature label derived from the pointer; the actual Git branch above is authoritative.

## Table of Contents

Read the complete proposal before approval: [Summary](#summary), [Technical Context](#technical-context), [Constitution Check](#constitution-check), [Project Structure](#project-structure), [Design and execution](#design-and-execution), [Machinery review](#machinery-review), [Verification and review](#verification-and-review), [Complexity Tracking](#complexity-tracking), [Plan approval](#plan-approval) and [Implementation checkpoint](#implementation-checkpoint) and [Approved handoff revision](#approved-human-input-handoff-revision).

## Summary

Deliver one thin Markdown skill that composes existing planning, task generation and read-only analysis, with a separate routine repair step authorized by workflow selection. Stop for human full-plan review only after fresh analysis finds zero actionable inconsistencies and zero unmet requirements. Disclose genuinely optional suggestions separately. Preserve approval evidence, artifact identity, decisions and useful authorized continuation without runtime state infrastructure.

## Technical Context

**Language/Version**: Markdown skill instructions; existing Python helpers under the project's Python 3.11.16 mise pin. No new executable runtime code or dependency is proposed.

**Primary Dependencies**: Installed `speckit-plan`, `speckit-tasks`, `speckit-analyze`, their existing setup/prerequisite helpers, effective template resolution and extension hook contracts. The current Spec Kit init records `1.0.10.dev0+pegagio.2`; consumer versions and capabilities must be inspected at execution time, not assumed portable from this checkout.

**Storage**: Existing feature Git artifacts and available conversation only. No new runtime state store, approval register, counters, schemas, controller or accounting files.

**Testing**: Version-controlled Markdown fixture cases and an existing real Codex session/CLI observation procedure, evaluated independently. No new harness/framework. Static checks support source consistency but cannot prove runtime acceptance.

**Target Platform**: Existing Codex session with a configured Spec Kit project; same model/effort, no per-step agents or routing. Current development host is macOS; portability means execution in an independently initialized disposable project, not a second live adoption or an untested all-platform claim.

**Project Type**: Prompt-based developer workflow; user interface is a named skill plus ordinary Markdown handoffs.

**Performance Goals**: Reduce manual command chaining and redundant approvals; continue useful authorized repairs and stop at actual decision/blockage/review boundaries. No latency target, iteration quota or progress scoring is introduced.

**Constraints**: Approved FR-001–FR-015 and SC-001–SC-007, including the replacement Q4 qualitative stop and explicit ban on numeric limits/counters/reset semantics/new persistence/tracking machinery. Existing core skills remain unchanged. No install, model change, implementation, commit, merge or push from the planning workflow.

**Scale/Scope**: One active selected feature and one existing session. Separate independent evaluation is acceptance work, not delegation of runtime workflow nodes. No queue, scheduler, worker pool or Diagram adapter.

## Constitution Check

The following gates passed before research and were re-evaluated after design. Runtime acceptance is future work, not a pre-planning execution gate.

| Gate | Before research | After design | Basis |
|---|---|---|---|
| I — Coherent feature flow-back | Pass | Pass | Current feature only; behavior edits return to spec review when material; historical features are preserved. |
| II — Selected workflow authority | Pass | Pass | Invoke only the three existing commands and prescribed hooks, with separate authorized routine repair; later implementation requires plan approval and separate selection. |
| III — Routine autonomy and human decisions | Pass | Pass | No per-repair approvals for routine work; genuine new decisions/scope/material intent changes stop dependent work. |
| Simplicity and understandable artifacts | Pass | Pass | One skill, guide and fixture cases; no runtime state machinery. Existing artifacts explain repair attempts and remaining issues. |
| Independent real-session acceptance | Pass as design obligation | Pass as design obligation | Verification tasks require a separate real subject/evaluator and portability evidence; source checks alone cannot accept delivery. |
| Specification approval | Pass | Pass | Exact approved digest and metadata-only distinction recorded above and in spec; the plan was unapproved at that planning checkpoint and was subsequently explicitly approved below. |

Generic plan guidance mentions research agents; the approved single-session/no-per-step-delegation constraint takes precedence. Research uses current installed source and prior-feature patterns in this checkout. There is no unsettled technology choice requiring dispatch or additional product input.

## Project Structure

Only the following documentation is produced during this planning invocation; runtime delivery files remain proposed until full-plan approval.

### Documentation (this feature)

The effective plan template supplies the structure. Supporting artifacts give decisions, interface expectations and future runnable validation, without new runtime formats.

```text
specs/002-prepare-implementation-plan/
  spec.md                         # approved meaning plus approval metadata
  plan.md                         # this full proposal
  research.md                     # source-grounded decisions and alternatives
  data-model.md                   # conceptual existing artifacts; no storage schema
  contracts/prepare-implementation-plan.md
  quickstart.md                   # future real-session validation guide
  tasks.md                        # separately generated implementation tasks
  validation/acceptance.md        # future observations, not created as evidence now
```

### Source Code (repository root)

These paths follow Feature 001's existing packaging pattern; none is created during this planning pass.

```text
.agents/skills/farmboy-prepare-implementation-plan/SKILL.md
  # user-invoked thin skill
docs/prepare-implementation-plan.md
tests/fixtures/prepare-implementation-plan/cases.md
README.md                        # add the documented entry point
```

**Structure Decision**: Add one peer skill and companion guide/fixtures. Reuse installed `.specify/scripts/python/setup_plan.py`, `setup_tasks.py` and `check_prerequisites.py`; do not fork them or duplicate their template/hook behavior. Verification observations belong in the existing feature's ordinary acceptance Markdown, not a runtime event ledger.

## Design and execution

The future skill's responsibility is ordered composition and clear handoff, not reimplementation of the core commands. [Research](research.md) records the concrete command interfaces and alternatives; [contract](contracts/prepare-implementation-plan.md) defines invocation, transitions and examples.

1. Inspect current project guidance/constitution, active pointer and explicit target, current approval evidence and affected artifacts before mutation. Require ready declared prerequisites. Explicit/ambient identity conflicts, missing capability or material approval uncertainty stop dependent work; do not create another feature or install tools. Available conversation approval OR an applicable existing review note suffices, without a new register.
2. If the same feature has an intact pending full-plan review and no requested revision, present it rather than regenerate. If approved already, recognize the boundary and stop; never implement. For interrupted partial planning, preserve artifacts and answers, inspect which required outputs actually exist and resume only missing/affected steps. `setup_plan.py` preserves an existing plan, but the invoking agent must not overwrite it with a fresh template. For accepted revisions, update affected sections and rerun necessary downstream tasks/analysis without duplicating existing task identities or discarding completed-task evidence.
3. Invoke installed `speckit-plan` ordinarily, including its pre/post hook handling. It owns template/setup, research and design outputs and required input stops. Then invoke installed `speckit-tasks` against the completed design. It owns the effective tasks template, ordering and required hooks. A failed prerequisite/input stops dependent commands. No generic model-switching, workers or branch/roadmap activation is added here.
4. Invoke installed `speckit-analyze` after complete tasks. It owns its prerequisite check, read-only comparisons, structured output and hooks. The analysis invocation never edits artifacts. The selected composite explicitly authorizes a separate follow-up repair step to fix routine current-scope defects without another human confirmation; the standalone analyzer's optional manual-remediation question does not become a redundant composite gate. Core analyzer source is not modified.
5. Examine actual actionable findings and unmet requirements, not severity thresholds or edits performed. Apply useful authorized repairs outside analysis, preserving approved meaning and flowing corrections through affected plan/tasks/supporting artifacts. Re-run analysis on the latest artifacts after the final repair. Stop INCOMPLETE when genuinely stuck, repeating unsuccessful approaches or needing human input; concisely explain attempted approaches and remaining issues in the existing artifacts/conversation. No numeric limit, counter, reset semantics, score, loop history store or new persistence is used. Never reclassify a defect as optional to claim a pass.
6. Once fresh analysis establishes zero actionable inconsistencies and zero unmet requirements, disclose genuinely optional suggestions separately and present the complete proposal for human full-plan review. Add no polishing loop for optional improvements. Show new machinery/need/alternatives/recommendation, including an explicit explanation of how the stopping rule stays within existing capabilities. Do not approve or execute the plan.

No automatic Goal creation is proposed; the completed authoring specification Goal remains untouched. For a separately operator-selected automation Goal whose actual entire objective is a saved review-ready OR INCOMPLETE-for-human-input handoff, durably save the INCOMPLETE planning outcome, exact required input, current artifact references, attempted work/remaining issues and next ordinary action in existing spec/plan notes; inspect that saved handoff, then complete the matching automation Goal through actually exposed supported controls and verify native readback BEFORE waiting for a person. This is successful handoff-objective completion only: it is neither passing analysis, a review-ready plan, plan approval nor implementation authority. After an actual answer, continue by separately operator-started ordinary interaction outside the completed Goal; never create or reactivate a Goal automatically. An overscoped unmet clean-proposal objective, unavailable native controls, arbitrary helper failure or unknown technical failure does not qualify for this human-input endpoint. Preserve the exact limitation without fabricating success, answers or controls. Ordinary manual invocation remains the baseline. No controller, automatic live waiting or native-file mutation is introduced.

## Machinery review

The recommendation is thin composition using existing capabilities. This is a concrete design choice for full-plan review, not an implementation approval.

| Proposed item | Concrete need | Simpler alternative and tradeoff | Recommendation |
|---|---|---|---|
| One Markdown skill | Encode the selected order, gates, separate repair authority and handoff so the operator need not chain commands manually | Continue manual command chaining; less source to maintain but repeats toil and relies on memory | Add the peer skill after approval, reusing ordinary commands |
| Usage guide and fixture cases | Explain invocation/review and specify proportionate real acceptance observations | Skill-only instructions are shorter but leave portability and negative-path expectations hard to inspect | Use existing Feature 001 Markdown patterns; no test framework |
| Feature design/acceptance Markdown | Review the approach and later retain attributable observations | Conversation-only evidence is hard to inspect after handoff | Reuse ordinary spec/plan/tasks/acceptance docs; no runtime machine consumes an evidence schema |
| No-progress behavior | Avoid repeating unsuccessful approaches while preserving useful repairs | Exact cycle quotas/counters/scores would introduce policy and bookkeeping the operator explicitly rejected | Use actual analysis findings and existing artifacts plus concise INCOMPLETE explanation only |
| Native compatibility verification | Establish actual behavior before claims | Assume waits/Goal completion work, or build a controller to mask failures | Observe existing exposed native controls in a separate real session; disclose unsupported behavior and stop affected work |

No database, controller, event ledger, metrics framework, approval registry, progress score, persistent counter/state file, numeric repair limit, new dependency, service or renamed equivalent is proposed. Nothing parses the conceptual data model as a runtime schema. No subsystem exists merely to account for iterations. FR-007 and FR-009 compliance is met by these instructions and artifact inspection, not an added helper/harness.

## Verification and review

[Quickstart](quickstart.md) prescribes future runnable real-session checks and expected results. The implementation task list must cover every FR/SC and all three stories, including negative prerequisites, read-only analysis versus separate repair, retained task identities/answers, changed-artifact invalidation, genuine human input, optional-only handoff, blockage, review and portability. Actual observations require a separate executing subject/evaluator; synthetic fixture contents alone are not acceptance.

This manually bootstrapped proposal is assessed now by installed read-only analysis after task generation. Final analysis is reported in the same session with coverage, findings and SHA-256s so no separate analysis state file is needed. It proves artifact readiness only, not future skill execution or native compatibility. The operator reviews this whole plan and tasks before separately selecting implementation. Optional after-plan wiki ingestion is offered by the installed hook and is not selected in this bounded invocation.

## Complexity Tracking

No constitutional violation or justified exception is proposed. No complexity-tracking subsystem is created by this template heading. The full-plan review may approve or simplify the proposed skill/guide/fixtures; prohibited tracking machinery cannot be introduced as a routine implementation detail.

## Plan approval

Pegagio explicitly approved the current 27-task proposal with “Sounds good. Approved.” Approved pre-metadata plan SHA-256: `ee6e13687370b5def1ad2a310b24aa2dd79aefff144b4226c68f93c27f4facc1`, captured before this status/note edit. At approval-recording time this was metadata-only: reversing the status change and removing the note reproduced approved bytes, verified before implementation. The initial current-stage/evidence flow-back changed factual metadata only; the later explicitly approved human-input revision below changes design meaning under new user authority. The proposed skill/guide/fixtures, reuse of existing commands, qualitative repair rule and prohibition on accounting/tracking machinery are unchanged. Later material design changes require affected human review; this approval does not approve the completed result.

The operator separately selected installed `speckit-implement`, independent real-session delivery verification, `speckit-converge` and eligible in-scope repairs/flow-back/reassessment. No unrelated workflow, other feature, commit, merge or push is authorized. The completed specification-preparation Goal remains untouched. Session: `01a14b62-0782-7c30-8824-31199e2d0d0b`.

## Implementation checkpoint

The one approved Markdown skill, usage guide, fixture cases and README entry point now exist; the core skills remain unchanged. [Actual evidence](validation/acceptance.md) records separate real executing subjects, current source hashes, ordinary workflow successes, supported native activation/completion/manual pause-resume and the failed automatic input wait. No new subsystem or runtime persistence was added. The earlier proposed/future descriptions above describe the reviewed design and bootstrap stage, not a claim that the skill is still absent.

Verification execution is distinct from native-claim acceptance: the automatic missing-input behavior failed and is UNACCEPTED, while the then-current contract's INCOMPLETE ordinary handoff/later operator-started resume and complete-proposal-only Goal success were honored. The failed native case is not recast as a pass or fixed by new machinery. Human result acceptance remains separate. At that checkpoint a new explicit contract decision was still required; the approved revision below supplies it without changing the historical failed observation.

## Approved human-input handoff revision

The user explicitly approved this narrow changed design and its implementation/verification. Pre-revision plan SHA-256 `af161562239e9cda71c51c2154ec3d014f6dfc27e1ad97c2ab37d27cf22bf8d1` is historical; this revision changes approved meaning rather than metadata alone. For a separately operator-selected automation Goal whose actual entire objective is a saved review-ready OR INCOMPLETE-for-human-input handoff, durably save the INCOMPLETE planning outcome, exact required input, current artifact references, attempted work/remaining issues and next ordinary action in existing spec/plan notes; inspect that saved handoff, then complete the matching automation Goal through actually exposed supported controls and verify native readback BEFORE waiting for a person. This is successful handoff-objective completion only: it is neither passing analysis, a review-ready plan, plan approval nor implementation authority. After an actual answer, continue by separately operator-started ordinary interaction outside the completed Goal; never create or reactivate a Goal automatically. An overscoped unmet clean-proposal objective, unavailable native controls, arbitrary helper failure or unknown technical failure does not qualify for this human-input endpoint. Preserve the exact limitation without fabricating success, answers or controls.

Implement only Markdown instructions and existing-artifact handoff, using exposed native get/update controls when actually available. Reuse the existing greeting fixture and a separate real subject/evaluator to read native completion before supplying any answer, then observe ordinary answer continuation and fresh read-only analysis with unchanged completed Goal. Static negative guards cover overscoped objectives and missing controls/failure non-generalization unless actual observations establish more. No bridge behavior, controller, new persistence or other machinery is proposed: successful live waiting was disproved, and the simpler existing handoff pattern resolves the approved need. Tasks T028–T031 append to the performed historical tasks.

## Human result acceptance

On 2026-10-17, after review of the completed 31/31 result, zero-actionable-issue final analysis, gap-free convergence and the approved handoff behavior, Pegagio said: “That sounds like exactly what we want. I like it”. This explicitly accepts the Feature002 delivery, including the bounded saved-INCOMPLETE automation endpoint and ordinary answer continuation. It does not accept the earlier failed automatic waiting behavior, approve a planned fixture for implementation or authorize another workflow, commit, merge or push. The exact reviewed artifact hashes and verification limits are retained in [acceptance evidence](validation/acceptance.md#human-result-acceptance).

Acceptance/status flow-back changes records only; all 31 task markers and delivered skill behavior remain unchanged. Optional roadmap debrief and wiki ingestion were not selected. Pegagio subsequently approved marking roadmap002 verified and making the scoped local delivery commit with the separately approved Feature004 planning documentation. Roadmap002 is now verified and remains selected; no Feature003 activation, integration, push or historical freeze is authorized or claimed.

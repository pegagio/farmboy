# Implementation Plan: Deliver approved plan through closeout

**Branch**: `reboot/2026-10-16/prompt-first` | **Date (UTC)**: 2026-10-18 | **Spec**: [spec.md](spec.md)

**Input**: Approved cleaned outcome-focused specification, pre-approval-metadata SHA-256 `bb8d74544c4b5f1e68f3c805c6650a58b043488fa275dd5ac73f5e490a50b487`. Approval conversation date is unknown. The latest explicit human closeout clarification is recorded in spec.md; it settles final-commit ordering without approving this plan.

**Status**: Approved — implementation and prescribed composite verification/convergence/delivery selected.

**Plan Approval**: Explicit human approval applies to reviewed pre-approval-metadata SHA-256 `d223b6157e51a4f2c191bad50f251093dfc6613befff8c1d7868ab5b3e4f2e1a`, the current final-commit design, all linked supporting artifacts and all 32 existing tasks. Trusted conversation: after the assistant recommended this revised complete-final-commit plan and committed to drive independent live test subjects with TEST-ONLY fixture answers, the user said “Perfect. Well, I accept the plan then”. The superseded dirty-tail design is not approved. Conversation date was not supplied. Later material changes require affected human review; no real Farmboy result acceptance exists.

**Selected execution authority**: The operator separately selected actual implementation, independent native-subject verification/disposable projects, convergence/repair, current-feature flow-back, actual debrief/wiki closeout, only 003 implemented, and a final scoped local commit with normal Git settings/hooks. This authorizes neither verified nor integration/merge/push, next-feature activation or constitution/core-skill changes. No main authoring Goal is created/reactivated.

## Table of Contents

The proposal follows the effective installed plan template and exposes the consequential order choice for human review.

- [Summary](#summary)
- [Technical Context](#technical-context)
- [Constitution Check](#constitution-check)
- [Project Structure](#project-structure)
- [Design and delivery sequence](#design-and-delivery-sequence)
- [Machinery review](#machinery-review)
- [Validation and review handoff](#validation-and-review-handoff)
- [Current implementation checkpoint](#current-implementation-checkpoint)

## Summary

Deliver one thin Markdown skill composing actual installed implementation, verification, convergence/repair and documentation closeout for one approved selected feature. Finish checks/documents, include the implemented roadmap update with all scoped delivery artifacts, then make the final local commit. Report implemented/Awaiting result review only after actual commit success. Later explicit applicable human result acceptance separately authorizes verified; integration remains separate. The latest direct human clarification settles this simple order without a special failure procedure or a new question.

## Technical Context

The existing prompt-first repository supplies the command capabilities; no application service or library is introduced.

**Language/Version**: Markdown skill/guide/fixtures; existing Spec Kit Python helpers on the repository's Python3.11.16 toolchain. Skill-owned Python validation, if useful, uses `~/.codex/venvs/skill-tools/bin/python`; report missing environment/packages rather than install.

**Primary Dependencies**: Installed speckit-implement, speckit-converge, roadmap-debrief/write, wiki-ingest/lint; ordinary Git and native Goal controls only when actually exposed. Core commands own their helpers/templates/hooks.

**Storage**: Existing Git files, feature spec/plan/tasks and concise existing artifact notes; existing roadmap/wiki formats. No new runtime persistence, schema or approval register.

**Testing**: Fixtures defined before skill implementation, proportionate static source/format/privacy checks and independent actual-session observation. Repository has no general test-runner task in mise.toml; do not invent a passing suite. Real verification remains future work.

**Target Platform**: Existing Codex session and a disposable local Spec Kit project; one operator, one selected feature.

**Project Type**: Prompt-first workflow skill and documentation.

**Performance Goals**: Reduce repeated operator permission for routine authorized work; continue useful repairs without numeric quotas. No latency/service throughput claim applies.

**Constraints**: Existing model/effort; no delegated runtime steps, tool installation, core-skill changes, counters/reset/scoring/accounting/controller or new persistence. Preserve explicit reviews, material-change review and scope boundaries.

**Scale/Scope**: One delivery skill, one guide, README link, fixture case document and current-feature acceptance evidence. Future 004 external request/result contracts, bridge/Diagram, integration execution and autonomous workers excluded.

## Constitution Check

The same checks apply before research and after design; all pass at proposal level, with future runtime evidence still required.

| Principle | Before research / after design | Basis |
|---|---|---|
| I — Flow-back/history | Pass / Pass | Current-feature reconciliation precedes dependent work/commit/closeout; material changes return to affected review; no historical rewrite or integration freeze claim. |
| II — Prescribed authority | Pass / Pass | Explicit spec approval applies; later delivery requires explicit plan approval and separately selected work. Commands retain actual write/hook boundaries. Only narrow implemented authority; acceptance separately gates verified. |
| III — Bounded toil/simplicity | Pass / Pass | Useful repair with honest stops, native completion before human waits, no new machinery; complete artifacts exposed at human full-plan review. |
| III — Actual verification | Planned obligation | Later real executing subject is separate from evaluator, with portability/full-lifecycle evidence; no source/fixture assertion stands in for observation. |

No constitutional exception or amendment is proposed.

## Project Structure

The structure extends the existing skill/guide/fixture pattern; no generated core file, lockfile or dependency manifest changes are planned.

### Documentation (this feature)

Review the complete proposal, not just this summary.

```text
specs/003-deliver-approved-plan/
  spec.md
  plan.md
  research.md
  data-model.md
  contracts/deliver-approved-plan.md
  quickstart.md
  tasks.md
  validation/acceptance.md          # later actual evidence, not created as proof now
```

### Source Code (repository root)

There is no new runtime code layer.

```text
.agents/skills/farmboy-deliver-approved-plan/SKILL.md
docs/deliver-approved-plan.md
tests/fixtures/deliver-approved-plan/cases.md
README.md
```

**Structure Decision**: Match the existing 001/002 source/guide/fixture organization. Do not edit their historical feature content or installed core commands. All future paths above are proposed work, not files claimed delivered by planning.

## Design and delivery sequence

The [research](research.md), [data model](data-model.md), [operator contract](contracts/deliver-approved-plan.md) and [validation guide](quickstart.md) provide the complete details and alternatives.

1. Resolve the explicit selected spec and active pointer, contained paths, verified prerequisites, current artifacts and applicable spec/full-plan approval. Present a valid pending result review without regeneration. Resolve actual capabilities/hooks before dependent effects.
2. Invoke installed implement ordinarily. Preserve its checklist input gate and all required hooks. Run applicable project verification and inspect actual results; a task marker alone proves nothing.
3. Invoke installed converge only after implement has run on complete tasks. It may append traceable follow-up tasks only. Separately reconcile routine current-scope flow-back; implement the follow-ups and rerun affected checks/convergence. Zero actionable gaps and zero unmet obligations are required regardless of severity. Material changes or genuine required input stop dependent work.
4. Reconcile delivery documentation and actual implementation evidence. Invoke installed roadmap-debrief on an attributable complete delta; resolve routine findings without treating its recommendations as roadmap authority. Invoke wiki-ingest on relevant authorized source(s), one per invocation, then lint; repair in-scope knowledge issues and refresh stale assessments. Missing/untrustworthy evidence or unresolved required findings stop clean delivery.
5. After all required checks, artifact reconciliation and documentation/debrief/wiki closeout, include the selected entry’s narrow implemented update through the installed roadmap-write capability. This authority belongs to the selected delivery workflow, not to debrief recommendations; it grants no verified, scope/dependency/governance or integration amendment.
6. Inspect the final scoped contents, including that roadmap update and all authorized delivery artifacts, protect unrelated staged/unstaged work and make the prescribed final LOCAL delivery commit. Report success only after the actual commit succeeds. If Git errors, report the ordinary error honestly without claiming successful delivery. No special failure procedure or additional bookkeeping is proposed.
7. Present implemented/Awaiting result review with the actual commit, complete evidence and limitations/optional suggestions. There is no intentionally uncommitted final status amendment, extra receipt-only commit, integration prerequisite, merge, push or declaration integrated/complete. If a selected native Goal’s entire saved endpoint is satisfied, complete/read it back before human review. A qualifying required-input endpoint saves INCOMPLETE and finishes only that bounded objective; it grants no delivery/status/approval success.

Later explicit applicable human result acceptance independently authorizes the separate implemented→verified recording action, outside this skill. This plan does not authorize performing it now or committing the resulting amendment implicitly.

## Machinery review

No new subsystem, framework, service, runtime persistence, accounting/tracking store, controller, counter/reset policy or progress score is proposed.

| Proposed item | Current need/responsibility | Simpler alternatives and tradeoffs | Recommendation |
|---|---|---|---|
| One Markdown composition skill | Repeatable approved implementation→convergence→closeout without repeated routine OKs | Manual chaining has less source but leaves coordination toil; a controller adds unjustified state/maintenance | Use the existing thin skill pattern. |
| Guide, fixtures, ordinary acceptance notes | Explain authority and prove actual interactions/portability | Source-only checks cannot establish runtime acceptance; a new testing framework is unnecessary | Reuse existing fixture/evaluator approach; no new harness dependency. |
| Final scoped commit includes implemented update | End delivery with all scoped artifacts committed, as directly requested | Manual command chaining still requires operator coordination; added failure machinery has no demonstrated need | Finish checks/documents, include the narrow update and commit; report ordinary Git errors honestly. |
| Existing artifact-based continuation | Preserve actual answers/tasks and precise missing work | New attempt/digest/ownership ledgers duplicate current artifacts | Inspect existing state, continue useful work or stop honestly; no new bookkeeping subsystem. |

No reverse-write authority or special commit-failure mechanism is proposed. Workflow continuation is ordinary command composition and current-artifact inspection; a bounded native objective ends before human interaction, and an actual answer requires separately selected ordinary continuation rather than automatic Goal restart.

## Validation and review handoff

Verification tasks are future work after explicit plan approval, not experiments run by this planning session. Define expectations first and independently observe actual execution for all four stories, including negative approval/identity cases, real repair and required input, closeout/status/commit behavior, no accidental verified/integration, native success/failure boundaries, resume and complete local lifecycle portability. T030 must re-run earlier cases affected by later changes against the final skill source, preserving intermediate observations as history rather than current proof. Fixtures must use their own approvals and local commits; they cannot accept this Farmboy result. No subject delegates steps or changes model/effort.

The full-plan handoff must link this plan, research, data-model, contract, quickstart and ordered tasks, plus fresh read-only analysis after the latest affected edit. Passing analysis never approves the plan. Optional suggestions remain separate and cannot drive polishing.

**Historical review handoff**: The proposal reached Awaiting full-plan review with fresh analysis; the explicit approval and selected execution authority above now supersede that pending-review state. Review this entire [plan](plan.md), [research](research.md), [data model](data-model.md), [operator contract](contracts/deliver-approved-plan.md), [validation guide](quickstart.md) and all 32 ordered [tasks](tasks.md). The human’s requested final-commit order is incorporated; it is not full-plan approval. No unresolved product question or optional suggestion is proposed. Implementation requires explicit full-plan approval and separately selected work. Current 003 remains in-progress; no runtime experiment, status write or commit has occurred.

**Review feedback and reconciliation**: Actual feedback “It feels like we should end with a commit” and latest direct guidance settle the ordinary final-commit path without special failure handling. Separate authorized edits therefore update the ordinary success path and relevant spec wording, remove hypothetical commit-failure tests/procedures and retain ordinary honest error reporting. All 32 task IDs and unchecked states survive; no new task or subsystem is needed. The earlier stale-evidence repair remains in T030. Earlier analysis covered the earlier proposal only; fresh installed read-only analysis must cover these final saved artifacts. No before-plan/before-tasks/before-analyze/after-tasks/after-analyze hooks are registered; optional after-plan wiki-ingest remains unselected.

## Current implementation checkpoint

The human explicitly approved the narrow T030/SC-006 sequencing correction and scoped Farmboy delivery commit after the assistant explained the circular precommit-proof requirement; the actual answer was “Yes”. This is affected approval, not an inference from the earlier whole-plan approval. Preserve all required existing disposable/current-source/native evidence and independent real-Farmboy execution. A separate native Codex subject executes the actual delivered skill without runtime delegation, using real003 spec/full-plan approvals and exact scoped authority; the driver remains independent evaluator. Complete required precommit checks, current-artifact reconciliation and fresh debrief/wiki closeout, record only003 implemented, then include roadmap and all scoped artifacts in the final normal local commit. Independently inspect actual Git/artifact/result after that commit exists and before successful human result-review handoff.

T030/T032 contain precommit and postcommit work; only their performed portions may be reported before commit. Pending final observation does not block its own commit. Preserve honest pending markers in the committed artifact snapshot; record actual postcommit readback and logical task completion in ordinary conversation, with no receipt-only commit or dirty tail to capture identity. T033 records the explicit sequence resolution. Fresh convergence assesses current due obligations separately from mandatory postcommit observation; no missing observation is waived or passed early. The prior INCOMPLETE checkpoint and RETHINK debrief remain historical. No new subsystem, unrelated demonstration, recovery procedure or test waiver is proposed. Future004 and later explicit result acceptance remain separate.

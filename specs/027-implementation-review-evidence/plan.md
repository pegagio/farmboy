# Implementation Plan: Implementation consumes current plan-review evidence

**Branch**: `027-implementation-review-evidence` | **Date**: 2026-10-24 | **Spec**: [spec.md](spec.md)

**Input**: Whole specification at `f040dd9123cb8ae4e9b677774a39129eb33f4039`, approved through `approval/cd639c1cd5a60c55708cc3a6b4b38f46`, including the disclosed checklist exceptions and Farmboy delivery-only boundary. Externally selected FARM-27 plan/planning-handoff; no FARM-28 dependency or BGG work.

## Summary

Add committed review consumption to Farmboy delivery after identity/approval checks and before ordinary implementation, including setup effects. Generic delivery reads and assesses evidence, distinguishes current obligations from advice and resolved history, and retains optional decisions in existing notes. The optional adapter locates authoritative Diagram references; Diagram retains state/approval authority. Bare Spec Kit commands remain unchanged.

## Table of Contents

- [Technical Context](#technical-context)
- [Constitution Check](#constitution-check)
- [Project Structure](#project-structure)
- [Design and Execution](#design-and-execution)
- [Verification](#verification)
- [Complexity Tracking](#complexity-tracking)
- [Planning Handoff](#planning-handoff)

## Technical Context

**Language/Version**: Markdown skills/guides; existing Python 3.11 standard-library fixtures. Use `~/.codex/venvs/skill-tools/bin/python` for skill validation.

**Primary Dependencies**: Existing Farmboy delivery/optional adapter, Git, installed Spec Kit implementation/convergence and actual Codex evaluation facilities. No added package, framework or tool.

**Storage**: Existing committed review/design artifacts, ordinary feature delivery/closeout notes and Diagram authority records. No new persistence.

**Testing**: Existing focused unittest contract suite, extended delivery/adapter fixture recipes and separately evaluated actual Codex execution. Text checks do not prove semantic obedience.

**Target Platform**: Existing local Codex environment; generic delivery remains portable without Diagram.

**Project Type**: Reusable workflow instructions with an optional coordination adapter.

**Performance Goals**: Read the full applicable evidence set on new/materially changed relevant input; reuse valid assessments/decisions on resume. No throughput service or timing machinery.

**Constraints**: No core skill, native schema, launcher/control, live consumer, installation or report-production changes. Preserve human gates and ownership; required-evidence failure stops before implementation. No new report obligation for report-free standalone use.

**Scale/Scope**: One feature; maintained delivery/adapter sources, guides and existing fixture assets. Several reports may support an approval; newest filename/date never selects authority.

## Constitution Check

Pre-research and post-design gates pass for this bounded proposal. Implementation and runtime acceptance remain future work.

| Principle | Design evidence and gate |
|---|---|
| I — Flow-back | Approved spec bytes/historical meaning remain intact. Reconcile affected current artifacts on optional adoption; material meaning returns to human review. Commit inequality alone does not invalidate applicability. |
| II — Selected authority | Only planning/tasking/analysis and necessary adapter checkpoint/handoff now. Whole-plan approval and separately selected delivery remain required. |
| III — Bounded toil and simplicity | Existing seams/notes replace no subsystem. Before acceptance, an evaluator separate from actual executing Codex session verifies changed skill behavior. |
| IV — Human gates | Consistency assessment neither creates nor revokes approval. Actual unresolved product/resolution questions return to existing human boundaries. |

## Project Structure

Use ordinary feature artifacts and maintained Farmboy source locations. Do not edit historical specs or installed consumer copies.

```text
specs/027-implementation-review-evidence/
  spec.md
  plan.md
  research.md
  data-model.md
  contracts/review-consumption.md
  quickstart.md
  tasks.md
  validation/analysis.md

.agents/skills/farmboy-deliver-approved-plan/SKILL.md
.agents/skills/farmboy-diagram-work/SKILL.md
.agents/skills/farmboy-diagram-work/references/native-protocol.md
docs/deliver-approved-plan.md
docs/diagram-adapter.md
docs/review-implementation-plan.md
tests/fixtures/deliver-approved-plan/cases.md
tests/fixtures/diagram-adapter/cases.md
tests/fixtures/review-implementation-plan/test_contract.py
```

**Structure Decision**: Extend existing files and fixture locations. The data model describes existing relationships, not classes/schema to implement. The contract describes instruction behavior, not a new API or packet.

## Design and Execution

The [research](research.md), [relationships](data-model.md) and [behavior contract](contracts/review-consumption.md) elaborate this design.

1. During adapter-owned delivery preparation, follow the current native plan approval to its originating handoff and existing `review_evidence` and `plan_candidate` checkpoint references. Use supported handoff/operation inspection for referenced records. Verify actual committed path/digest/feature/candidate facts; no private SQL or directory/date selection. Missing supported evidence is a precise stop, never a reason to add native fields or patch external software.
2. Supply these existing references as ordinary same-session context to the externally selected body, reusing current run authority and the single invocation. Adapter owns native recording/release; generic delivery assesses meaning without Diagram commands/version coupling.
3. On non-Diagram routes, applicability comes from explicit report-bearing approval or a governing report requirement. Neither condition means record not applicable and retain ordinary behavior. Required-but-unavailable evidence stops without Diagram lookup or stray-report selection.
4. Before implementation/setup effects, read the full applicable committed report set alongside the approved plan and resolution evidence. Verify relationship as well as integrity. Disclose relevant local conflicting edits; working bytes never replace committed evidence. Routine later commits preserving approved meaning remain valid with applicability evidence; material/uncertain changes stop under existing gates.
5. Assess findings: unresolved required corrections, blockers or unmet obligations stop at any priority. Explicit non-blocking optional advice remains voluntary even at high priority. Resolved/superseded history needs applicable evidence; approval alone does not establish resolution. Ambiguous or contradictory status stops with exact missing resolution. Preserve work/use existing incomplete and release rules; no automatic return/re-review or manufactured successful delivery.
6. Consider optional suggestions before related implementation decisions. By closeout record adopted/declined, report/item reference and reason in ordinary notes. Adoption requires actual approved coverage/work and coherent flow-back; out-of-scope advice may be declined with that reason. No suggestions means a concise none. Resume reuses valid decisions, reassesses relevant changes and preserves history without duplicate work.
7. Update guides and fixtures, then verify actual skill behavior during separately authorized delivery. Bare core commands, approval semantics and report production stay unchanged.

## Verification

The [quickstart](quickstart.md) defines concrete cases. [tasks.md](tasks.md) orders source changes, fixture coverage and independent runtime evaluation. Cover authoritative versus decoy/multiple reports; missing/uncommitted/unreadable/corrupt/wrong-feature/wrong-candidate evidence; local conflicts; routine/material flow-back; low-priority requirements/high-priority blockers; high-priority optional advice; evidenced/unsupported resolution; ambiguity; adoption/decline/none; resume and standalone applicability/no-report use.

Run `~/.codex/venvs/skill-tools/bin/python -B -m unittest discover -s tests/fixtures/review-implementation-plan -p test_contract.py`, scoped links/privacy checks and `git diff --check`. Extend source contract tests for placement, ordering and boundary regressions only; a classifier in tests would not verify the workflow. Historical native-composition tests require separately authorized external source/compiler prerequisites and are not a mandate to refresh tools or live systems for this instruction change.

Before acceptance, a real executing Codex session follows final skills in disposable selected work; a separate evaluator observes reads, effect order, dispositions, stops and single-body routing. Future evaluation requires actual explicit evaluation/delegation authority and compatible private tools/fixtures. Missing capability leaves acceptance incomplete, without static substitutes or installation. Retain concise actual observations in feature `delivery.md` and `validation/verification.md`, keeping raw output disposable. Planning claims no future runtime result.

## Complexity Tracking

No new subsystem/infrastructure or constitutional deviation is proposed. Existing instructions supply semantics, native records supply authority and Git/notes supply evidence. Manual lookup alone is smaller but leaves the observed omission. A registry/parser/state machine adds format/synchronization obligations without need; reject it. Continuation and handoff use existing resume, native run and review mechanisms without numeric limits, counters/reset semantics, scores, new persistence or accounting machinery.

## Planning Handoff

The original planning run `run/aa91c005414e3ae0e219b775422136fa`, epoch 3, stopped at Git staging with `index.lock: Operation not permitted`; it was released without a planning handoff. Its seven proposal files were preserved and their hashes verified unchanged before this continuation.

The epoch 4 successor also stopped at protected Git staging and was released without a planning handoff; the proposal remained untracked and preserved. Pegagio explicitly authorized this continuation to request ordinary per-action approval for exact feature staging and normal commit, retaining hooks and stopping on an approval denial or unavailable mechanism.

Verified current inner run: `run/67e53b7d3bbf9549269b571639b2a692`, epoch 5, FARM-27 plan/planning-handoff, owner `pegagio-agent-farm27-approved-checkpoint`, session `farm27-scoped-approval-recovery-20261025`. Explicit human-authorized successor recovery preserves the original approved input and task identities. Only this handoff metadata and refreshed analysis evidence require repair; the proposal decisions remain unchanged. Whole outer endpoint: complete proposal, fresh read-only analysis, scoped checkpoint and accepted native awaiting-plan-review handoff/released ownership. No Goal was created. Native acceptance/release must be verified separately; this plan does not assert an unperformed handoff.

Final proposal assessment is retained in [validation/analysis.md](validation/analysis.md). Optional after-plan wiki ingestion is presented but unselected; no mandatory plan/tasks/analyze hooks are configured. No unresolved product question is introduced. Next action after successful native handoff is human whole-plan review; passing analysis is neither approval nor delivery authority.

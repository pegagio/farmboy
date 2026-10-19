# Implementation Plan: Concise delivery evidence

**Branch**: `006-concise-delivery-evidence` | **Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)
**Status**: Full plan explicitly approved; delivered candidate accepted on 2026-10-19. See delivery.md for the actual decision and disclosed limits.
**Input**: Approved Feature 006 specification. Pegagio explicitly said “approved” after the detailed specification review on 2026-10-19. Approved specification SHA-256: `2911e5ffeb67a45323131c1200f6cc7ef8d6c363a80ad62fe728a6801f22d36b`. This records specification approval only; it does not approve this plan or authorize implementation. The spec's earlier draft/preparation handoff remains an attributable historical checkpoint.

## Summary

Edit the existing delivery skill and guide to retain concise evidence and reusable verification assets while excluding raw run output from the scoped commit. Keep the summary in existing feature delivery documentation rather than adding an evidence system. Extend the existing delivery acceptance cases with one focused disposable delivery fixture; retain its small repeatable tests and expected results. Verify the actual revised skill under a separate evaluator, then retain a concise Feature 006 delivery summary rather than raw session output.

## Technical Context

**Language/Version**: Markdown workflow instructions; Python 3.11 standard library for a small fixture test.
**Primary Dependencies**: Existing Codex sessions, installed Spec Kit/Farmboy commands and Git. No new packages, skill installer or harness dependency.
**Storage**: Existing Git Markdown and fixture files; ordinary temporary directories for disposable projects/output. No database or new machine state.
**Testing**: Source/contract review and one independent actual-skill delivery observation, with repeatable toy-project tests after temporary output removal. Existing commands retain their own verification/hook contracts.
**Target Platform**: Existing supported Codex/Spec Kit environment. Native Goal behavior is claimed only when supported controls and readback are actually available.
**Project Type**: Prompt workflow and operator documentation, not a new application.
**Performance Goals**: All six review essentials remain understandable from concise retained artifacts; zero required references depend solely on discarded output.
**Constraints**: Preserve current routing, external association/authority, convergence, actual commit and review endpoints. Preserve private identities, unrelated work and merged feature meaning. No upstream/Diagram/global-hook changes or pushes.
**Scale/Scope**: One skill, one operator guide, existing delivery fixture area and current Feature 006 artifacts. No repository-wide evidence cleanup.

## Constitution Check

Pre-research gates: PASS. Current approved specification, matching pointer/branch and verified roadmap dependency 003 establish this segment's prerequisites. No product ambiguity or constitutional exception identified.

Post-design gates: PASS. Existing workflows and current-feature artifacts express the change; no new authority or persistence layer. Historical specs remain untouched. Actual independent real-session acceptance is a required later task, not a claimed planning result. Implementation, commit and human result acceptance remain separately gated. No runtime delegation is introduced; the independent evaluator is outside the executing delivery skill.

## Project Structure

### Documentation (this feature)

```text
specs/006-concise-delivery-evidence/
  spec.md
  plan.md
  research.md
  data-model.md
  contracts/delivery-evidence.md
  quickstart.md
  tasks.md
  delivery.md                 # later concise performed-results account
```

### Source and reusable verification assets

```text
.agents/skills/farmboy-deliver-approved-plan/SKILL.md
docs/deliver-approved-plan.md
tests/fixtures/deliver-approved-plan/cases.md
tests/fixtures/deliver-approved-plan/evidence-retention/
   test_count_lines.py        # future retained stdlib unittest for toy subject code
   input.txt                 # future controlled test input
   expected.txt              # future deterministic expected line count
```

**Structure Decision**: Extend the existing fixture directory with three small reusable assets, not a general runner. The existing cases file holds setup/observation instructions, including obsolete-report seeds; no second fixture framework. `data-model.md` describes existing documentation content, not a schema. `contracts/delivery-evidence.md` documents the skill's operator-facing behavior, not a new API. No ignore change is needed when the fixture/project and raw output live outside Git. Ignore rules alone cannot exclude tracked files.

## Design and delivery sequence

1. Follow [research decisions](research.md) and [behavior contract](contracts/delivery-evidence.md). Add the evidence distinction to the delivery skill's documentation and precommit inspection, without replacing its routing or core-command composition. Refine ALL-scoped-artifacts language so it includes all required durable assets and excludes disposable output.
2. Align the operator guide with the skill: summary content, privacy, minimal justified durable exceptions, actual source attribution, stale evidence, required references and exact incomplete stops. A base hash plus relevant working delta identifies precommit checks; report the resulting commit normally after success without a self-referential receipt commit.
3. Author each story's focused fixture expectations before its corresponding behavior edits; add reusable toy tests before the reusable-asset/staging policy edits. The disposable subject implements a tiny line-count function. Retained input/expected result and stdlib test make its verification repeatable; the evaluator supplies TEST ONLY fixture approvals. Seed duplicate current-feature reports and required links plus disposable output so the same delivery demonstrates scope inspection and consolidation/reference repair. No actual private data enters the seeds.
4. In one actual execution against final changed skill/guide, a separate evaluator observes implementation, a real failed check and useful repair/recheck, closeout and Awaiting result review. Use ordinary installed commands and a supported disposable Spec Kit project. Preserve unrelated staged/unstaged fixture work. Review actual committed scope and returned required references, then remove disposable logs/output and rerun retained tests. Keep the toy implementation/candidate available until verification is complete; output deletion must not delete reusable source/tests. Record distinct executor/evaluator roles and exact source content hashes without retaining private identities or session IDs.
5. Use static/fixture assertions within the same focused case for policy conflict stops, minimal durable exceptions, stale results, already tracked raw files, missing-proof handling, historical scope and unchanged external handoffs. Do not require a second live Diagram exercise or a new acceptance framework. Actual runtime claims remain limited to observed behavior.
6. During separately authorized delivery, reconcile current 006 artifacts, invoke prescribed convergence/closeout capabilities, and retain concise actual results in `delivery.md`. Required original helper reports remain governed by their source-preserving contracts: do not delete a current mandatory report or patch core helpers just to simplify evidence. Only redundant mutable fixture reports are initial consolidation targets. Refresh any affected authoritative assessment through its responsible command. Normal roadmap-debrief/write and wiki maintenance remain the selected delivery workflow's work; no additional workflow or recursive commit is added here.

## Verification and review

[Quickstart](quickstart.md) defines the setup, commands and expected observations. [Tasks](tasks.md) will order implementation and checks after plan approval. Before implementation, run installed read-only `speckit-analyze` against latest spec/plan/tasks, separately repair in-scope actionable findings, and repeat until zero actionable inconsistencies and zero unmet requirements. Raw analysis detail can remain disposable; this plan records the concise final result and unresolved limits. Do not treat a green report as plan approval.

## Infrastructure and persistent additions

No new subsystem, store, service, scheduler, registry, accounting or generic framework is proposed. Durable additions are the normal Spec Kit design/task documents, three small reusable test assets, and later `delivery.md` for actual results. The concrete need for these is repeatable verification and an understandable review after raw output disappears. Simpler alternative: instructions alone would reduce files but fail to retain executable verification assets; a generic harness or retention engine adds no needed behavior. Recommendation: retain this small file-based approach and existing workflows.

Continuation uses current artifacts and actual findings; there are no attempt counters, reset rules, scores, progress database or new controller. Routine repairs are separate from read-only analysis. A material decision or missing required capability produces an exact incomplete handoff rather than invented authority.

## Historical planning checkpoint

Base HEAD remains `e1183047592c9f8cfc8d434c48e0e428fb4779ad`; selected artifacts and roadmap activation are uncommitted. No implementation has run. Native Goal controls are unavailable and no Goal completion is claimed. No other project or historical feature artifacts are changed.


## Historical analysis and planning handoff

Installed `speckit-plan` setup/design and `speckit-tasks` setup/generation completed for this same feature. Read-only `speckit-analyze` found A1 (synthetic report seeds could be mistaken for observed results) and A2 (fixture-first wording disagreed with per-story task order). Separate authorized repairs explicitly label seeds as synthetic, populate failure/repair evidence from real observed checks before consolidation, and align the plan with task order. Fresh read-only reassessment covers the repaired proposal: 12 functional requirements plus 5 buildable success criteria mapped to 14 tasks; zero actionable inconsistencies, zero unmet requirements, zero constitutional issues and zero unmapped tasks. Actual runtime verification remains future work.

Tasks: setup/foundation 2; US1 3; US2 3; US3 3; final verification/closeout 3. All 14 remain unchecked. Sequential execution is intentional because skill/guide/cases files overlap; no parallel runtime agents are proposed. Optional post-plan wiki-ingest was presented and remains unselected; there are no mandatory applicable plan/tasks/analyze hooks. No new persistent system or machinery is introduced; only ordinary design/task documents, three later reusable fixture assets and a later concise delivery account.

**Historical planning handoff: Awaiting full-plan review.** Review this plan, research, descriptive content model, behavior contract, quickstart and ordered tasks. No material unresolved product decision remains. The required human decision is whether to approve this full proposal or request changes; passing analysis does not approve it or authorize implementation. No implementation, commit, merge or push occurred. All selected changes remain uncommitted on the recorded base, and native Goal completion is not claimed.

## Subsequent human decision and execution

Pegagio explicitly approved this full plan and requested execution on 2026-10-19. The reviewed plan digest and exact scope of that approval are retained in [delivery.md](delivery.md), together with actual execution results and remaining result review. The earlier planning checkpoint remains historical; metadata reconciliation changes no approved implementation design.

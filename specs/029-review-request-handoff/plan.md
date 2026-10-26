# Implementation Plan: Coordinate independent plan-review handoff from user intent

**Branch**: `029-review-request-handoff` | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md)

**Input**: Approved specification at `9b080d09d3e4cbe905ff2023bdd71919e6e7881e`; native spec approval `approval/30c17446b5cfac036fd04acd462b324e`. User selected planning only (Sentinel_416b9b49480c81919e07cd9ed157995c). Approved specification/request/checklist bytes remain unchanged.

## Summary

Add one thin selecting-caller skill, `farmboy-request-plan-review`, that prepares an already authorized independent review, starts one separate reviewer using existing session tools, collects the correlated result and stops. Keep `farmboy-review-implementation-plan` as the independent semantic body and `farmboy-diagram-work` as the native adapter. Small routing/reference seams distinguish an operator-facing caller request from an already dispatched reviewer entry. No Diagram production change, new process manager, schema or persistent dispatch state is planned.

## Technical Context

**Language/Version**: Markdown skill instructions and documentation; Python3.11 standard-library fixture/contract tests, following current Farm Boy conventions.

**Primary Dependencies**: Existing independent session/task start/read/wait facilities exposed by the host; existing generic reviewer/adapter and native Feature9 review grant; matched Diagram schema23/Project4/Repository2/Issue-query6. Private native fixtures use immutable integrated Diagram `f6494a1e390d29e6657e95a6b6f6c28bebe09ac0` and its existing acceptance helpers. Existing pinned older fixtures remain historical, not current schema proof.

**Storage**: No new runtime storage. Existing native grant/run/operation/handoff records and Git feature/report artifacts; ordinary caller session retains child/operation locators. A request/grant file, if the selected route needs one, is transport only, not a journal or credential.

**Testing**: Existing `tests/fixtures/review-implementation-plan/test_contract.py`, focused new caller-contract tests, disposable real Git/native fixtures and independently evaluated actual executing sessions. Controlled test-double results are separate from actual model behavior.

**Target Platform**: Existing local Codex environment with a supported separate-session start and result inspection/wait route. Missing capabilities stop precisely without installation or substitute orchestration.

**Project Type**: Reusable agent workflow skill with optional Diagram composition.

**Performance Goals**: One selected review, at most one dispatched independent reviewer, no manual prompt/grant transfer. No latency, scale or throughput infrastructure is needed.

**Constraints**: Preserve approved spec bytes, six-question rubric, bounded human authority, independent reviewer attribution, one continuous reviewer invocation, adapter-only native mutation and all later human gates. Do not edit consumer projects, installed tools, controls or other worktrees. No implicit repair, re-review or implementation chain.

**Scale/Scope**: One human requesting one independent whole-plan review. One new caller skill; minimal routing/reference seams and focused shared fixtures. Standalone generic review remains supported.

## Constitution Check

*Pre-research and post-design gates: PASS.*

- Principle I: Preserve the approved specification and merged historical features. New design/tasks carry this feature's change; actual discoveries flow back before implementation, with renewed review for material meaning changes.
- Principle II: Operator requests one review. Caller dispatch is within that selected invocation, not a new segment or approval mandate. No unrequested planning/repair/delivery follows.
- Principle III: Remove technical human dispatch, reuse existing tools and stop only for real missing scope, capability or failure. Actual skill behavior requires a separate evaluating session; fixture-only success cannot establish acceptance.
- Principle IV: Grant contents derive from actual explicit candidate-specific human delegation. The caller can be the plan author; the separate reviewer cannot materially author the candidate. Approval remains attributable and grants no later execution.
- Runtime boundary: caller-level session dispatch does not split the semantic review into per-step agents. The adapter and reviewer still compose in the single independent session. Existing native per-Feature/workspace authority protects actual reviewer writes.

No amendment, exemption or extra approval ledger is needed. Initial planning is report-free, not a FARM-28 return; no prior required findings apply.

## Project Structure

### Documentation (this feature)

```text
specs/029-review-request-handoff/
├── request.md, spec.md, checklists/requirements.md  # exact approved inputs
├── plan.md, research.md, data-model.md
├── contracts/caller-handoff.md
├── quickstart.md, tasks.md, analysis.md
└── validation/verification.md                    # later actual delivery evidence
```

### Source Code (repository root)

```text
.agents/skills/farmboy-request-plan-review/SKILL.md             # new thin caller
.agents/skills/farmboy-review-implementation-plan/SKILL.md      # routing seam only
.agents/skills/farmboy-diagram-work/references/native-protocol.md # caller/grant reference
README.md
docs/review-implementation-plan.md
docs/diagram-adapter.md
tests/fixtures/review-implementation-plan/
├── test_contract.py
├── test_caller_contract.py
├── prepare_caller_fixtures.py
└── cases.md
wiki/pages/independent-plan-review.md, wiki/sources.md          # applicable source-backed upkeep
```

**Structure Decision**: Existing project-local skill directory-copy packaging remains unchanged. Add the caller entry rather than make the semantic reviewer dispatch itself. Existing planning and delivery bodies are untouched. Existing helper/fixture facilities may be extended locally for TEST ONLY transport; they are not production machinery or a new API. No Diagram core/launcher modification or consumer deployment is part of delivery.

## Design and implementation sequence

1. **Caller entry (US1)**: Define selection/route/mandate checks and user-facing behavior. A user review request enters the caller; an independently dispatched reviewer enters the existing semantic body with verified caller context. Add one small routing seam to the review body and guides, without recursive dispatch. Missing substantive role/selection asks one concise question; settled authority is reused. Generic standalone caller dispatch carries explicit applicable scope without Diagram dependencies.
2. **Bounded handoff (US2)**: Caller inspects actual proposal/approved intent, release/current review state and host capabilities; chooses independent reviewer labels, builds the existing grant from actual human evidence and supplies exact references in the initial reviewer prompt. No self-issued grant or fabricated mandate. The optional adapter remains sole native acquire/record/release owner. Current source `ReviewGrant` fields are documented rather than recreated as a new transport schema; see contract.
3. **Collection and stop (US3)**: Wait/read known child through existing host tools, inspect exact candidate/report/accepted native terminal/release and present concise six-question results. Resume uses known locators, immutable correlation and current records, never a new dispatch on uncertainty. Preserve approve/planning-return/specification-escalation/incomplete and FARM-27/28 consumption semantics. No new durable registry; loss of needed context is an explicit manual-inspection stop.
4. **Focused acceptance**: Source/transport assertions and disposable private native cases precede real-session observations. Evaluator observes the actual candidate caller starting an actual independent reviewer, not just the semantic reviewer alone. Reuse the shared negative matrix where each boundary lives; no Cartesian host/state matrix.
5. **Documentation/convergence**: Document ordinary use, install-source-only boundary and capability limits, update relevant wiki through its existing ingestion/lint workflow during authorized delivery, run all applicable maintained checks, reconcile actual evidence and final analysis, then committed result-review handoff/release. Human implementation acceptance and integration remain separate.

## Validation and evidence

The [quickstart](quickstart.md) defines exact checks, fixture cases and real-session evidence. Required coverage includes missing caller-supplied grant (the reported incident), incomplete/advice-only mandate, stale/wrong/revoked grant, candidate change, author/reviewer independence, busy ownership, unavailable targeting/permissions, all three substantive outcomes, invalid/uncertain collection and duplicate resume. Grant fixtures reuse current Diagram schema23/Feature9; do not claim the old schema20 composition fixture is current coverage.

The actual-session proof uses disposable projects and explicit TEST ONLY human delegation. An evaluator is separate from the executing caller; reviewer is separate from material proposal authorship. Record source/fixture hashes, subject/evaluator/reviewer session identities, grant provenance, prompt/transport evidence, actual reads/effects, report digests, native dispositions/release and absence of extra dispatch/implementation in existing validation notes. Some refusal variants may be controlled injections; label them. No live Fusion/BGG or production-store mutation, model installation or changed execution controls are needed.

No repository `mise run validate` task or qualification-selector policy exists in Farm Boy; do not invent either or modify Diagram's policy. Run maintained Python contract suites, syntax/diff checks and the planned private composition/real-session cases with retained actual commands/results. Future missing tools or permissions remain unpassed delivery obligations, not reasons to mark complete. Planning runs only artifact/consistency checks, not implementation tests or models.

## Complexity Tracking

No constitutional violation or new subsystem is proposed. One thin caller skill makes the missing responsibility explicit. Putting this in the semantic reviewer would collapse independence/authority boundaries; duplicating it across every authoring skill would multiply maintenance. Existing session tools, native records and report return fields suffice. A universal “drive feature” router, scheduler, child supervisor, cross-process callback API or dispatch journal is excluded.

## Planning Handoff

Awaiting whole-plan review after complete task generation and fresh read-only consistency analysis. No unresolved technical/product decision is left to implementation. Optional post-plan wiki ingestion is unselected; no enabled mandatory plan/tasks/analyze hook exists. No native Goal was created. Planning does not invoke an independent review of this plan or authorize implementation.

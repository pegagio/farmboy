---
title: Preimplementation review gates
type: concept
sources: [S007, S008, S009, S021, S029]
updated: '2026-10-09'
---

# Preimplementation review gates

## Earlier feature contracts

The following cited contracts preserve earlier feature intent; Feature 014's prospective refinements are distinguished below. (S021)

Clarification runs one bounded session against the operator-selected active specification. Human answers are incorporated into the specification before the next question; the result distinguishes resolved, outstanding, and deferred ambiguity. The current five-question cap is a session boundary, not proof of planning readiness. (S007)

The operator chooses another clarification session, planning readiness, or deferral. Continuing uses the same feature; deferral stays explicit rather than becoming a product default. Neither an empty question set nor an ended session selects planning automatically. (S007)

Planning requires an operator-identified clarified feature and explicit confirmation that the specification was reviewed. The readiness choices are plan, return to clarification, and defer; unresolved product ambiguity cannot be settled by a technical design assumption. A completed plan leaves plan, research, data model, contracts, and quickstart for review without generating tasks. (S008)

Task generation is a separate step for an operator-selected planned feature. It proposes dependency-ordered work from reviewed design artifacts, reports task coverage and unexpected human actions, and leaves the proposal for review. The operator may choose separate analysis, return to planning, explicit task amendment, or deferral; no route begins implementation directly. (S009)

## Feature 014 core-skill output loops

Clarify begins with the standard skill session, then assesses significant remaining ambiguity and repeats while prior ambiguities are resolved within a finite bound. The five-question limit remains per session and every substantive answer comes from the operator; clarification does not declare planning readiness. (S021)

Plan delegates prerequisites, research, design generation, and constitutional gates to the core skill. Its existing assessment combines structural checks with independent semantic review, respecting justified inapplicability and returning exact actionable findings to Planner through the bounded correction path. Populated files alone do not establish satisfactory design. (S021)

Tasks combines format, section, dependency, and story-coverage checks with independent semantic assessment, returning exact findings to Tasker while preserving task IDs, completion markers, completed work, and reviewed design. Unchecked implementation tasks are not generation failures. Analyze and implementation remain separate invocations. (S021)

Both reviews check accepted requirements, internal and cross-artifact consistency, and required coverage. Findings identify the artifact or section, governing requirement or decision, deficiency, and approved-scope correction. Reviewers do not edit reviewed artifacts. Stable finding identities and substantive resolution establish progress; rewording or renaming findings does not. Baselines count toward the cap, and repeated findings, stale evidence, no progress, or the cap stop. Product answers and material scope decisions remain operator-owned. Specify's independent roadmap brief checks alignment rather than supplying a general content-review loop. (S021)

**Accepted supersession**: S007–S009 require terminal/readiness/coverage choices in the earlier contracts; S021 removes routine classification gates and uses evidence-driven continuation or blocked recovery. Human answers and consequential authority remain required. (S007, S008, S009, S021)

## Feature 020 preparation and readiness

Analyze and Implement share FlowKit-owned readiness without changing Spec Kit core. Preparation requires substantive current independent review; an author checklist or clean analysis alone cannot prove readiness. Missing, stale or contradictory preparation evidence blocks, while safe in-scope gaps enter declared correction and reassessment. Each unresolved criterion identifies ownership, evidence and due phase. Future implementation, acceptance and release obligations remain traceable and pending; evidenced relocation outside the core checklist gate preserves stable identities and provenance without satisfying them. (S029)

FlowKit-Readiness Checker independently reports preparation gaps without authoring artifacts or replacing Reviewer. Author checks and independent review remain required. [Agent roles](./agent-roles-and-inheritance.md) retains this separation. (S029)

## Related pages

- [Workflow lifecycle](./workflow-lifecycle.md)

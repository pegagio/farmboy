---
title: Workflow lifecycle
type: concept
sources: [S002, S006, S007, S010, S013, S017, S018, S019, S021, S029]
updated: 2026-10-14
---

# Workflow lifecycle

## Earlier source contracts

The following records retain earlier source intent; the accepted Feature 014 refinements below govern the revised workflow design. (S021)

Earlier README combined Start Feature, then optional Clarify, Plan, Tasks, Analyze, Implement, Converge and Close Out. Current README separately invokes Select Feature and Specify after constitution, approved roadmap and cited wiki preparation; selection never authors `spec.md`. (S002)

Feature 013 used reviewed concrete step-model assignments for bounded Codex subagents. Updated Feature 015 source uses reviewed per-step native agent names instead. Human questions and review gates stay in the main task; completing one workflow does not authorize a later phase. (S002, S019)

Verified Feature 013 preserves eight separately invoked phases with a main controller and step subagents. Direct skills use the FlowKit catalog alongside the Specify bundle. (S018)

Verified Feature 015 assigns a reviewed native Codex agent name to each delegated step. Task labels show intended names; native selection is verified separately. (S018)

Planning and task generation are separate. Clarification may need another session after the current five-question command limit. Analyze follows task generation or consequential artifact reconciliation; converge follows implementation until identified gaps are resolved. (S002)

Workflows preserve a manual-prompt fallback. Closeout requires a separately approved feature-completion operation and does not create one; completing a workflow does not merge or accept a feature. (S002)

Starting a feature requires unique roadmap eligibility, satisfied dependencies, an exact approved patch, and cited governing context. Partial or missing context blocks a speculative start. (S006)

The five-question clarification cap ends a session, not the ambiguity review; the operator explicitly chooses another session, planning readiness, or deferral. (S007)

Read-only analysis precedes any artifact remediation, and routine corrections return through dependent artifacts before another analysis. Consequential findings stop for a separate decision. (S010)

Closeout requires a separately approved completion operation, an exact roadmap verification patch approved by the operator, curated wiki maintenance, and a separate commit-readiness decision. (S013)

## Feature 014 approved scope

Feature 014's approved scope separates read-only candidate/dependency discussion and exact human selection/activation from same-target specification authoring. Selection updates only approved roadmap state and the active pointer; specification authoring is separately invoked. It also adds independent wiki maintenance while retaining separate planning and task generation. (S018)

**Accepted supersession**: The earlier S002 snapshot documented the combined start-feature route; S018 specifies separate Select Feature and Specify workflows and a stop-only deprecated combined source. This is a prospective F014 replacement, not a rewrite of verified earlier feature history. (S002, S018, S021)

## Feature 014 phase boundaries

Feature 014 requires separate Select Feature and Specify invocations before optional Clarify, Plan, Tasks, Analyze and Remediate, Implement, Converge, and Close Out. Wiki Lint Update is separately selected for wiki maintenance and needs no active feature. No successful phase silently starts another. (S021)

Clarify assesses residual ambiguity after operator-answered bounded sessions. Plan and Tasks independently assess structural and semantic outputs and return exact findings to authors; Implement repeats eligible work while progress is evidenced. Required input blocks with its question and resumption action. (S021)

## Abandoned work

Feature 018’s [capacity proposal](./workflow-agent-capacity-proposal.md) authorizes no further implementation. Its artifacts remain historical; the capacity issue is unresolved and no replacement is selected. (S018)

[Feature 020 contract](./feature020-workflow-lifecycle.md). (S029)

## Related pages

- [Codex workflow controller design](./codex-workflow-controllers.md)
- [Project authority and review gates](./project-authority-and-review-gates.md)
- [Bundle and workflow model](./bundle-and-workflow-model.md)
- [Consumer feedback boundary](./consumer-feedback-boundary.md)
- [Installation and release lifecycle](./installation-and-release-lifecycle.md)
- [Feature start contract](./feature-start-contract.md)
- [Preimplementation review gates](./preimplementation-review-gates.md)
- [Artifact flow-back and convergence](./artifact-flow-back-and-convergence.md)
- [Closeout and verification boundary](./closeout-and-verification-boundary.md)
- [Wiki source maintenance](./wiki-source-maintenance.md)

---
title: Named agents for delegated steps
type: concept
sources: [S018, S020, S021, S023, S025]
updated: 2026-10-03
---

# Named agents for delegated steps

Verified Feature 015 requires a reviewed Codex custom-agent name on each explicitly delegated FlowKit step. It depends on verified Feature 013 and has no dependency on Feature 014. The verification rests on the completed spec, convergence, tests, and bounded native Codex observations; it does not claim publication or native Specify runner parity. (S018, S020)

Feature 015's earlier reviewed vocabulary was Architect, Builder, Coder, and Verifier; its exact-name rule required a reviewed change for additions. Feature 014's approved role set below supersedes that vocabulary without granting approval authority. (S020, S021)

Each consumer owns its native Codex custom-agent TOML files. Codex resolves optional model and reasoning-effort settings, including inheritance. FlowKit does not maintain a role map or alter consumer agent files during install, refresh, or removal. (S020)

Every delegated executable step declares both `flow_kit.delegated: true` and its reviewed `flow_kit.agent`. An executable step without delegation remains in the main task; gates and switches stay there. An agent name alone does not create delegation, and there is no workflow-level default or per-run agent, model, or effort override. (S020)

Before workflow work, the controller validates every possible delegated assignment, including untaken branches, and confirms that each selected named agent can start a bounded child. It stops on a missing, invalid, or unavailable agent without silently substituting another. Codex's native subagent activity shows probe labels containing the agent name and workflow-child labels containing both the agent name and step ID. The label is a launch cue; the exact native agent request and readiness probe establish selection separately. The child pane may show model and effort, and FlowKit does not require a separate launch message or native-agent-name field. (S020)

Updated workflow source uses explicit delegation and agent names instead of Feature 013's concrete step-model declarations. A Feature 015 controller rejects a legacy concrete declaration with a migration reason. Native `specify workflow run` behavior must be checked separately; loader acceptance alone does not establish matching named-agent behavior. (S020)

The constitution amendment requiring reviewed agent names was approved and applied before workflow or controller source changes. (S020)

## Feature 014 approved scope

Feature 014 depends on verified Feature 015 and reviews the exact native name on every delegated branch. Its delivery boundary adds usable configurations only in this repository's consumer checkout; installing or modifying agent files in other consumers is excluded. The roadmap scope preserves consumer ownership and requires responsibility-fit review, not merely agent availability. (S018)

## Feature 014 assignment requirements

Feature 014 requires Roadmap Agent, Specifier, Planner, Tasker, Reviewer, Coder, Code Reviewer, and Wiki Curator across ten active workflows. Reviewer independently assesses specifications, plans, tasks, and roadmap alignment; Code Reviewer independently inspects implementation changes. Authors and independent reviewers use different agent types, with findings following existing correction paths or bounded stops; this assignment change adds no nodes. (S021)

Native configurations are repository-local; the temporary Coder probe is replaced with ordinary responsibilities. Authoring agents still perform command-required self-checks, prerequisites, and quality checklists, which cannot replace independent assessment. Exact roadmap approval and mutation authority remain in the main task. Structural checks and no-op dispatch are distinguished from live named-agent evidence. (S021)

The inventory distinguishes exact graph responsibilities from native dispatch and model evidence; see [workflow graph responsibility boundaries](./workflow-graph-responsibility-boundaries.md). (S023)

Feature 017 specifies prospective prefixed identities and model review; see [its delivery contract](./flowkit-agent-configuration-and-delivery.md). (S025)

## Related pages

- [Codex workflow controller design](./codex-workflow-controllers.md)
- [Project authority and review gates](./project-authority-and-review-gates.md)
- [Installation and release lifecycle](./installation-and-release-lifecycle.md)

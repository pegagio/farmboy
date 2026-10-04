---
title: FlowKit agent configuration and consumer delivery
type: decision
sources: [S025, S026]
updated: 2026-10-04
---

# FlowKit agent configuration and consumer delivery

Feature 017's initial clarification left packaging and operation syntax for planning. The later approved design selects canonical `agents/flow-kit/` defaults, separately versioned `flow-kit-agents`, and a consumer defaults cache. Completed scope is qualified by the operator-directed DEP017-01 deferral; local evidence establishes neither publication nor acceptance. (S025, S026)

## Reviewed defaults

Native `model` and `model_reasoning_effort` fields contain the approved pairs; workflows and controllers have no role-to-model map or per-run override. Consumers may customize their copies; unavailable assignments or settings require operator resolution without substitution. (S026)

| Exact roles | Model / effort | Responsibility rationale |
|---|---|---|
| FlowKit-Roadmap Agent; FlowKit-Wiki Curator | `gpt-6.1-sol` / `low` | Bounded approved-ledger work and cited-source bookkeeping |
| FlowKit-Specifier; FlowKit-Planner; FlowKit-Reviewer | `gpt-6.1-sol` / `high` | Product, architecture and independent semantic judgment |
| FlowKit-Code Reviewer | `gpt-6.1-sol` / `medium` | Independent selected implementation/test assessment |
| FlowKit-Coder; FlowKit-Tasker | `gpt-6-luna` / `high` | Approved eligible coding/task derivation with dependency/test reasoning and independent review |

Every pair and its qualitative rationale is operator-approved; no project benchmark establishes savings or quality equivalence. (S026)

## Consumer ownership and lifecycle

Bundle install and explicit install-missing add absent configurations, preserving existing files. Refresh replaces available defaults only; explicit reset-one/reset-all discards customizations only in selected current manifest targets. Removal preserves consumer copies. Old, retired and unrelated definitions survive for operator inspection/removal; prefixes confer no overwrite authority. Per-copy ownership hashes, automatic customization detection and merging remain excluded. (S026)

Portable human/JSON reports identify package version/digests/source provenance, normalized operation inputs and each target's actual created, preserved-existing, reset, failed or not-attempted disposition. Duplicate identities, unsafe destinations and mixed versions block usable-inventory claims. Arbitrary unsafe identity evidence is redacted and marked `identity_redacted`; reports omit host paths and secrets. Partial completion states written targets and bounded recovery, rather than implying rollback: retry absent paths or the same explicitly selected reset after inspecting results. (S026)

## Evidence boundaries and deferred outcome

Accepted desktop field/value evidence and operator-confirmed Sol pair observations establish support separately from current all-eight exact native launch availability. Readiness tokens prove launch availability, not role task behavior. Effective settings of all eight current roles remain unverified; desktop version is unavailable. Disposable configurations matched canonical/source-project bytes, but native launches used the source registry, not a separate disposable desktop session. (S026)

Recorded focused/full checks retain the skipped legacy class and its separately expanded native Specify Clarify `integration None` failure. No-op dispatch and loader success do not prove native behavior; local results imply neither stock compatibility nor publication/acceptance. (S026)

DEP017-01 remains unresolved: advertised mise refresh failed because its Python lacked PyYAML; an existing dependency-equipped skill-tools interpreter succeeded. FR-008/FR-011/SC-003 coverage applies to that tested environment; the original unconditional setup/usability target is not claimed passed. The approved follow-up must provide reproducible dependencies, supported catalog entry points and fresh-consumer validation using documented preparation. No numbered feature or provisioning approach is selected. (S026)

## Related pages

Feature 016 remains independent; coordination changes identities, not its probe timing. The generic component boundary and The Diagram's separate authority remain intact. (S025, S026)

- [Named agents for delegated steps](./agent-roles-and-inheritance.md)
- [Installation and release lifecycle](./installation-and-release-lifecycle.md)

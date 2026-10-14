---
title: FlowKit agent configuration and consumer delivery
type: decision
sources: [S025, S026, S018, S027, S005]
updated: 2026-10-14
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
| FlowKit-Readiness Checker | `gpt-6-luna` / `medium` | Bounded read-only preparation assessment (S005) |
| FlowKit-Coder; FlowKit-Tasker | `gpt-6-luna` / `high` | Approved eligible coding/task derivation with dependency/test reasoning and independent review |

The eight Feature 017 pairs are operator-approved; the later guide adds the Checker configuration and rationale. These are requested definitions, not observed effective settings or measured quality/cost equivalence. (S026, S005)

## Consumer ownership and lifecycle

Bundle install and explicit install-missing add absent configurations, preserving existing files. Refresh replaces available defaults only; explicit reset-one/reset-all discards customizations only in selected current manifest targets. Removal preserves consumer copies. Old, retired and unrelated definitions survive for operator inspection/removal; prefixes confer no overwrite authority. Per-copy ownership hashes, automatic customization detection and merging remain excluded. The current guide confirms these consumer-preserving operations and explicitly selected reset authority. (S026, S005)

Portable human/JSON reports identify package version/digests/source provenance, normalized operation inputs and each target's actual created, preserved-existing, reset, failed or not-attempted disposition. Duplicate identities, unsafe destinations and mixed versions block usable-inventory claims. Arbitrary unsafe identity evidence is redacted and marked `identity_redacted`; reports omit host paths and secrets. Partial completion states written targets and bounded recovery, rather than implying rollback: retry absent paths or the same explicitly selected reset after inspecting results. (S026)

## Evidence boundaries and deferred outcome

Accepted desktop field/value evidence and operator-confirmed Sol pair observations establish support separately from current all-eight exact native launch availability. Readiness tokens prove launch availability, not role task behavior. Effective settings of all eight current roles remain unverified; desktop version is unavailable. Disposable configurations matched canonical/source-project bytes, but native launches used the source registry, not a separate disposable desktop session. (S026)

Recorded focused/full checks retain the skipped legacy class and its separately expanded native Specify Clarify `integration None` failure. No-op dispatch and loader success do not prove native behavior; local results imply neither stock compatibility nor publication/acceptance. (S026)

DEP017-01 remains unresolved: advertised mise refresh lacked PyYAML, while an existing equipped skill-tools interpreter succeeded. Original FR-008/FR-011/SC-003 setup coverage remains qualified. The original deferral called for catalog preparation and fresh-consumer validation; at that point no numbered follow-up existed. (S026)

> ⚠ conflict: S026 originally targets catalog repair; later S018 explicitly supersedes that broader scope with verified 019’s agent environment, excluding interpreter unification/component launchers. 019 proves no catalog repair or retrospective Feature 017 coverage. (S026, S018)

Verified 019 supplies project `.venv`/mise/uv preparation, pinned PyYAML and portable guidance; no extra utilities. Tested macOS arm64 guide adoption establishes neither full catalog repair, stock Specify compatibility nor real adoption/acceptance. (S018)

## Related pages

The narrower follow-up is described in [Agent Python environment](./agent-python-environment.md); it preserves this delivery record. (S018, S027)

Feature 016 remains independent; coordination changes identities, not its probe timing. The generic component boundary and The Diagram's separate authority remain intact. (S025, S026)

- [Named agents for delegated steps](./agent-roles-and-inheritance.md)
- [Installation and release lifecycle](./installation-and-release-lifecycle.md)

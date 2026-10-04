# Research: FlowKit Agent Configuration and Consumer Delivery

Research date: 2026-10-03. Accepted specification policy, reviewed design and unverified runtime evidence remain distinct. The operator approved the complete eight-role model/effort table below during planning.

## Table of Contents

- [Evidence and Baseline](#evidence-and-baseline)
- [Approved Model and Effort Decisions](#approved-model-and-effort-decisions)
- [Instruction Review](#instruction-review)
- [Delivery Decisions](#delivery-decisions)
- [Remaining Validation Evidence](#remaining-validation-evidence)

## Evidence and Baseline

Read-only source inspection found eight unprefixed `.codex/agents/*.toml` configurations, each with name, description and developer instructions but no model/effort. `tests/test_agent_configs.py` currently asserts omitted settings, eight exact files, ten active workflows and 49 assignments; implementation must recompute branch coverage rather than treat 49 as immutable. `tools/catalog.py` packages controller skills and tracks those owned files with hashes; it excludes agent configurations. Existing managed-skill semantics must remain independent of consumer-owned agent copies.

Official [Subagents documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents), fetched 2026-10-03, documents standalone project TOML, `name` as identity, and `model`/`model_reasoning_effort` as supported file settings. File settings override resolved inherited/spawn settings. This supports explicit pairs in role files; it does not establish effective settings of any tested child.

Official [Models documentation](https://learn.chatgpt.com/docs/models), fetched 2026-10-03, recommends GPT-6.1 Sol for complex agentic work and Luna for focused repeatable work, subject to account/client access. It describes Sol as less costly than Astra for complex work. These are qualitative source claims, not project benchmarks or price estimates.

The current desktop host's exposed task tool model metadata advertises `gpt-6.1-sol` with `low`, `medium`, `high`, `xhigh`, `max` and `ultra`, and `gpt-6-luna` with `high` among its supported efforts; current choices use `low`/`medium`/`high`. This is availability metadata, not successful account dispatch or observed effective settings. CLI `codex-cli 0.157.1` and Specify `1.0.10.dev0+pegagio.2` were observed locally. No exact candidate config was applied or run during planning. Field validation, per-role live dispatch and effective settings remain implementation evidence obligations.

## Approved Model and Effort Decisions

**Decision status**: All eight exact pairs below are operator-approved. No model/effort decision remains pending. Approval selects the defaults; tested-client support and effective-runtime evidence remain separate implementation obligations.

**Criteria**: Assess the normal delegated scope, product ambiguity, cross-artifact dependencies, validation obligations and consequence of missed findings. Distinguish execution of approved eligible tasks from architectural/product judgment. Use lower effort for straightforward bounded work; retain depth for logic/edge cases. Current official [Subagents guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents) supports those qualitative effort distinctions. Model and effort recommendations remain engineering judgment; no project benchmark, success-rate comparison, measured latency/token usage or price calculation establishes suitability or savings.

| Exact role | Approved `model` | Approved `model_reasoning_effort` | Status and rationale |
|---|---|---|---|
| FlowKit-Roadmap Agent | `gpt-6.1-sol` | `low` | Operator-approved: scoped ledger inspection and applying an already approved exact patch are bounded; unresolved authority/dependencies return to the operator |
| FlowKit-Specifier | `gpt-6.1-sol` | `high` | Operator-approved: product ambiguity, scope preservation and requirement consistency require substantial judgment |
| FlowKit-Planner | `gpt-6.1-sol` | `high` | Operator-approved: architecture tradeoffs, support research and cross-artifact design reconciliation need depth |
| FlowKit-Tasker | `gpt-6-luna` | `high` | Operator-approved: approved spec and plan bound task derivation; high effort supports dependency ordering, preserved IDs/completion and requirement/validation coverage, followed by independent Sol/high review |
| FlowKit-Reviewer | `gpt-6.1-sol` | `high` | Operator-approved: independent semantic assessment of specs, plans, tasks and roadmap alignment traces assumptions, contradictions and evidence; deliverable existence or checked boxes do not establish correctness |
| FlowKit-Coder | `gpt-6-luna` | `high` | Operator-approved: explicitly selected eligible tasks and an established plan bound coding scope; high effort supports implementation/test reasoning and blocker detection |
| FlowKit-Code Reviewer | `gpt-6.1-sol` | `medium` | Operator-approved: medium effort for independent selected implementation/test assessment |
| FlowKit-Wiki Curator | `gpt-6.1-sol` | `low` | Operator-approved: authorized bounded-source bookkeeping/citations favor low effort; unresolved contradictions remain explicit rather than invented resolutions |

**Support evidence**: Host metadata advertises `gpt-6.1-sol` with `low`/`medium`/`high` and `gpt-6-luna` with `high`; fetched documentation supports the file fields and qualitative model roles. This is not exact-pair client parsing, account dispatch or effective-setting proof. Approval of Coder and Tasker does not waive those implementation checks.

**Tradeoffs and rejected approach**: The initial all-Sol assessment overweighted worst-case complexity and underweighted bounded eligible coding. Luna/high is now the approved coding and task-generation tradeoff; focused validation and independent review remain necessary. Low effort for Roadmap/Wiki prioritizes responsiveness for bounded work; substantial dependency ambiguity or conflicts must follow existing escalation paths. Tasker derives tasks from an approved spec and plan, with independent Sol/high review checking dependency and coverage gaps; unresolved upstream ambiguity remains a blocker. Sol/high for Specifier, Planner and Reviewer favors judgment without selecting Astra's additional capability/cost absent demonstrated need. Higher effort generally increases tokens/latency; no project-specific savings or quality equivalence are claimed. Consumers may customize the defaults. Unavailable values require operator resolution, never automatic model substitution.

## Instruction Review

The baseline instructions are well scoped. Prospective refinements make output/escalation contracts uniform without granting new responsibilities.

| Role | Allowed mutations and expected output | Exclusions and proposed clarification |
|---|---|---|
| Roadmap Agent | Scoped evidence, smallest exact patch, application only with recorded approval; preserve IDs/dependency evidence | No self-approval, unsolicited selection/spec changes; return exact question/blocker to controller when authorization is missing |
| Specifier | Selected spec/command-required checklist; changed paths and substantive questions | No roadmap/pointer/plan/tasks/code; author self-check is not independent review; main task relays answers to same child |
| Planner | Selected planning outputs, rationale, risks, validation and unresolved decisions | No scope/task/code changes or self-independent-review; complete core-command checks and route approval questions |
| Tasker | Selected task list, preserved IDs/completion and dependency/validation outputs | No upstream mutation/implementation; explicit upstream gap blocks unsafe tasking |
| Reviewer | Read-only selected artifacts/evidence, stable actionable findings and route | No edits/self-review/acceptance; independently assess rather than reuse author assertions |
| Coder | Explicit eligible tasks, relevant checks, exact task IDs/paths/results | No redesign/re-task/re-analysis authority; question or blocker ends current delegated scope pending controller relay |
| Code Reviewer | Read-only selected diff/test evidence; concrete defects distinct from risks | No edits/self-review/invented tasks; existing eligible correction route or exact task-plan/operator blocker |
| Wiki Curator | Authorized sources and cited wiki pages; provenance/conflicts/results | No feature/roadmap edits or unauthorized URLs; preserve source evidence boundaries and route conflicts/questions |

All roles retain prohibitions on another workflow, Git integration and claiming acceptance. Descriptions identify responsibilities rather than model capability. Instruction refinements are editorial contract clarity, not permission escalation. Implementation must report a role-by-role diff against this review and return any material authority change to the operator.

## Delivery Decisions

Accepted spec policy is consumer-owned catalog copies with explicit reset; design choices implement it as follows.

**Decision**: Create canonical `agents/flow-kit/` source and separately versioned `flow-kit-agents` package, pin it in the bundle, and validate artifact/source digest at package level. **Rationale**: Agent defaults are now reviewed reusable source, distinct from owned controller skills; package provenance need not claim ownership of copied files. **Alternatives**: Packaging `.codex/agents/` directly would make source-checkout customizations generic source authority; extending `skills-install.json` would impose expressly rejected ownership semantics.

**Decision**: Cache the selected defaults archive/manifest under `.specify/flow-kit/agent-defaults/`; install missing copies at bundle install and expose an explicit install-missing operation. **Rationale**: Users get a simple first install and can acquire newly added definitions after refresh. **Alternatives**: Manual copying adds setup friction; automatic refresh overwrites would violate the accepted contract. Refresh only replaces available defaults and never copies/replaces agents.

**Decision**: Use manifest-selected reset-one/all with no customization detection, consumer hashes or merging. **Rationale**: An explicit reset supplies narrow authority; a broad filename prefix does not. **Alternatives**: A blanket glob can destroy unrelated prefixed agents; historical inventory deletion violates obsolete-definition preservation.

**Decision**: Preflight all selected targets and use atomic individual writes with exact partial-operation reporting. **Rationale**: Existing file tooling can provide bounded recovery without a new journal/framework. **Alternatives**: Promise whole-bundle transactional rollback would add unnecessary scope and risk concealing partial external component operations.

**Decision**: Reconcile exact assignments and client discovery while preserving graphs/probe timing. **Rationale**: Renaming breaks native dispatch without coordinated installed/default identities. **Alternatives**: Compatibility aliases and implicit model maps are excluded; centralized probing belongs to Feature 016.

## Remaining Validation Evidence

Research resolved the delivery approach and the operator approved all eight exact pairs. Independent review remains separate from that decision. Documentation and advertised metadata are support inputs, not exact-pair execution proof. Implementation must record supported-client field parsing, live eight-role dispatch and effective-setting evidence or gaps; planning cannot claim future checks passed.

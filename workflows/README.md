# Spec Kit Flow Workflows

These are the reviewed, versioned source packages for the human-directed Spec Kit Flow super-states. Install a package only from its reviewed directory, validate native list, information, resolution, registry attribution, and source-copy equality, and never edit an installed copy. The FlowKit catalog also installs a direct Codex skill for each workflow; these controller skills follow the installed YAML and keep its prompts, commands, gates, and branches authoritative.

Each packaged workflow preserves its manual-prompt fallback and explicit human gates. Assessment envelopes in both the installed and manual paths require `reason_code` and any `resume_action` to match `^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$`: lowercase letters and digits joined by single hyphens, with no underscores or spaces. Delegated executable steps name a reviewed Codex custom agent in `flow_kit.agent`; Codex loads that agent's consumer-owned configuration. The workflow controller does not map roles to models or parse custom-agent TOML; catalog delivery separately validates package definitions and readable project identities. Executable steps without delegation metadata, gates, branch decisions, and questions remain in the main Codex task.

Use the selected consumer project in the Codex task and invoke one skill at a time. Required inputs come from the installed workflow definition:

| Workflow | Codex skill and display name | Required input | Delegated step agents |
| --- | --- | --- | --- |
| `speckit-flow-select-feature` | `$flow-kit-select-feature` — FlowKit Select Feature | optional `feature_request` | roadmap reading and selection preparation: FlowKit-Roadmap Agent; activation verification: FlowKit-Reviewer |
| `speckit-flow-specify` | `$flow-kit-specify` — FlowKit Specify | active `.specify/feature.json` | target inspection: FlowKit-Roadmap Agent; request preparation and drafting: FlowKit-Specifier; linkage and brief: FlowKit-Reviewer |
| `speckit-flow-clarify` | `$flow-kit-clarify` — FlowKit Clarify | `feature_context` | `clarify-session`: FlowKit-Specifier; ambiguity assessments: FlowKit-Reviewer |
| `speckit-flow-plan` | `$flow-kit-plan` — FlowKit Plan | `feature_context` | `create-plan`: FlowKit-Planner; `verify-plan-output`: FlowKit-Reviewer |
| `speckit-flow-tasks` | `$flow-kit-tasks` — FlowKit Tasks | `feature_context` | `generate-tasks`: FlowKit-Tasker; `verify-task-output`: FlowKit-Reviewer |
| `speckit-flow-analyze-remediate` | `$flow-kit-analyze-remediate` — FlowKit Analyze | `feature_context` | `analyze-artifacts`, `assess-analysis`: FlowKit-Reviewer; artifact correction: FlowKit-Specifier, FlowKit-Planner, or FlowKit-Tasker by layer |
| `speckit-flow-implement` | `$flow-kit-implement` — FlowKit Implement | `feature_context` | initial task assessment: FlowKit-Reviewer; implementation: FlowKit-Coder; post-pass assessment: FlowKit-Code Reviewer |
| `speckit-flow-converge` | `$flow-kit-converge` — FlowKit Converge | `feature_context` | task recording and waterfall correction: FlowKit-Tasker, FlowKit-Specifier, FlowKit-Planner by layer; analysis and eligibility: FlowKit-Reviewer; implementation: FlowKit-Coder; convergence/code assessment: FlowKit-Code Reviewer |
| `speckit-flow-closeout` | `$flow-kit-closeout` — FlowKit Close Out | `feature_context` (exact repository-relative spec directory) | readiness, debrief, analysis, eligibility, and lint: FlowKit-Reviewer; post-implementation debrief assessment: FlowKit-Code Reviewer; artifact correction: FlowKit-Specifier, FlowKit-Planner, or FlowKit-Tasker; implementation: FlowKit-Coder; wiki preparation: FlowKit-Roadmap Agent; wiki ingest: FlowKit-Wiki Curator |
| `speckit-flow-wiki-lint-update` | `$flow-kit-wiki-lint-update` — FlowKit Wiki Lint Update | optional `lint_scope`, `authorized_urls` | lint and assessment: FlowKit-Reviewer; source refresh: FlowKit-Wiki Curator |

For example: `$flow-kit-clarify feature_context=013`. The controller checks the selected compatible Specify runtime and installed workflow, then validates every named assignment across possible branches. It requests each native child with the exact reviewed `agent_type`. Codex's subagent activity shows each launch: probe labels include the agent name, and work-child labels include the agent name and step ID. Model and effort appear when Codex exposes them. The label provides launch visibility; the exact `agent_type` request establishes native selection. No run-time assignment override is available. Codex custom-agent configuration belongs to the consumer and is loaded by Codex itself. Clarification questions and review gates appear in the main task. A child question is answered there and relayed to the same child. The main task reports results and visible workspace diffs. Use the manual paths below if named-agent dispatch is unavailable.

For a project-scoped agent, create a file such as `.codex/agents/reviewer.toml` in the consumer project:

```toml
name = "FlowKit-Reviewer"
description = "Independently assesses workflow artifacts."
developer_instructions = "Follow the task scope and return a concise result to the parent."
```

A delegated workflow step names the matching native agent directly:

```yaml
- id: analyze-artifacts
  flow_kit:
    delegated: true
    agent: FlowKit-Reviewer
  command: "speckit.analyze"
  integration: "{{ inputs.integration }}"
```

Codex owns optional `model` and `model_reasoning_effort` fields and their inheritance behavior. FlowKit does not read or change consumer `.codex/agents/` files. The reviewed work-type names are FlowKit-Roadmap Agent, FlowKit-Specifier, FlowKit-Planner, FlowKit-Tasker, FlowKit-Reviewer, FlowKit-Coder, FlowKit-Code Reviewer, and FlowKit-Wiki Curator. Existing assessment nodes perform independent review; this assignment change adds no workflow nodes.

| Workflow | Core or extension commands |
| --- | --- |
| `speckit-flow-select-feature` | `speckit.flow-roadmap.write` |
| `speckit-flow-specify` | `speckit.flow-wiki.query`, `speckit.specify`, `speckit.flow-roadmap.write`, `speckit.flow-roadmap.brief` |
| `speckit-flow-clarify` | `speckit.clarify` |
| `speckit-flow-plan` | `speckit.plan`, `speckit.clarify` |
| `speckit-flow-tasks` | `speckit.tasks` |
| `speckit-flow-analyze-remediate` | `speckit.analyze`, `speckit.specify`, `speckit.plan`, `speckit.tasks` |
| `speckit-flow-implement` | `speckit.implement` |
| `speckit-flow-converge` | `speckit.converge`, `speckit.specify`, `speckit.plan`, `speckit.tasks`, `speckit.analyze`, `speckit.implement` |
| `speckit-flow-closeout` | `speckit.specify`, `speckit.plan`, `speckit.tasks`, `speckit.analyze`, `speckit.implement`, `speckit.flow-roadmap.debrief`, `speckit.flow-roadmap.write`, `speckit.flow-wiki.ingest`, `speckit.flow-wiki.lint` |
| `speckit-flow-wiki-lint-update` | `speckit.flow-wiki.lint`, `speckit.flow-wiki.ingest` |

## Manual feature-selection path

Select Feature lists dependency-ready roadmap choices, blocked unfinished features, prerequisite chains, immediate unlock counts, and distinct downstream dependents. Discuss dependencies with the operator and wait for one exact selection or defer. Optional interest never authorizes automatic selection.

Recheck only the chosen entry. For an existing spec, preserve its directory and contents. For a new feature, propose a repository-relative target without creating it. Show the exact roadmap delta and active-pointer payload together. Only approval authorizes `speckit.flow-roadmap.write`, followed by `controller.py activate-feature` to update `.specify/feature.json`. Verify unique roadmap ownership and pointer agreement. No specification, checklist, feature directory, or branch is created. A pointer failure after the roadmap write is a reported partial state, not an implicit rollback. Stop after reporting selection; authoring is separately invoked.

## Manual specification-authoring path

Specify reads the active `feature_directory` and resolves its exact unique roadmap entry. A reserved target may lack a directory or spec; missing or malformed selection, escaping paths, and ambiguous mapping stop. Retrieve cited context, then prepare the authoring request from the roadmap outcome, scope, dependencies, and current decisions. Stop on material missing context or required human input.

Pass `SPECIFY_FEATURE_DIRECTORY` explicitly to `speckit.specify`. Author or revise only that target, preserving existing reviewed decisions and active identity. Verify the produced directory and pointer against the selected entry. Missing or stale linkage may be repaired only through exact patch approval and fresh verification; a different generated target or pointer drift must stop rather than being legitimized by a new mapping. Both verified paths reach one roadmap brief with explicit `SPEC_TARGET` and `ROADMAP_ENTRY`, then one report. Clarify and Plan remain separate invocations.

## Deprecated Start Feature

`speckit-flow-start-feature` is retained as a stop-only deprecated source, with replacement links in its metadata. It is excluded from the current bundle and controller package. The former combined selection/authoring path is replaced by the two workflows above; invoking the deprecated source does not launch either replacement.

The seven loop workflows—Clarify, Plan, Tasks, Implement, Analyze and Remediate, Converge, and Closeout—use `blocked` for both unmet prerequisites and required operator input. Their reports preserve the specific question or blocker and safe resumption action. `complete` remains distinct from blocked, and only evidenced `continue` permits another pass. Roadmap patch approval remains an explicit human gate; commit readiness is checked and reported automatically.

## Manual clarification path

When native clarification dispatch is unavailable, run `speckit.clarify` on the operator-selected active specification one session at a time within the same invocation. The command checks for significant ambiguity and may finish without questions. The five-question cap applies per session. Present every substantive question in the main task, wait for the operator's answer, and apply only that answer to the current session. After each session, assess the current specification and confirm that the session resolved a significant ambiguity before continuing. On later sessions, compare against the previous assessment's remaining question IDs.

Stop as clarified when no significant unresolved ambiguity remains, without invoking Plan or treating that result as automatic planning approval. Stop with a specific decision when the question is outside Clarify's authority, on no measurable progress, after five sessions, or on a genuine blocker. Preserve accepted answers and report remaining question IDs with the smallest safe resumption action.

## Manual planning path

When native planning dispatch is unavailable, record the missing required planning files or placeholder sections for the operator-selected reviewed specification, then invoke `speckit.plan`. Let the core skill perform research, constitutional gates, and design generation; keep technical work within the feature scope and ask the operator for substantive product decisions.

Have an independent FlowKit-Reviewer perform structural and semantic assessment against the approved specification, repository constraints, and required and applicable outputs, accepting justified not-applicable sections. Check design consistency, stated tradeoffs and risks, and an actionable validation approach as well as substantive content and unresolved placeholders. Return exact located findings to FlowKit-Planner verbatim, with stable ID, artifact_location, violated_requirement or accepted decision, observed_deficiency, and exact_correction. Feed safely repairable findings back into `speckit.plan`, preserving completed design and existing decisions.

Fresh review must confirm substantive resolution of prior findings and retain new blocking findings before retry or completion; required-file production alone does not establish completion. Wording-only or digest-only edits, renamed or repeated findings, and successful commands do not prove progress. Preserve the substantive product question verbatim, wait for the operator's answer, and never infer that answer. Stop when independent review finds no material gaps, an operator answer or blocker prevents continuation, no progress occurs, or the five-pass safety limit is reached. Present artifacts and the exact outcome for review; task generation requires a separate operator instruction.

## Manual task-generation path

When native task workflow dispatch is unavailable, record exact missing task output or coverage gaps from the reviewed specification and design, then invoke `speckit.tasks` without a routine pre-generation question. Check that tasks.md is populated with correctly formatted tasks, applicable story phases, dependency coverage, independent test criteria, and the core skill's supporting sections. Unchecked implementation tasks are expected; completion here means generation is finished.

Have an independent FlowKit-Reviewer perform structural and semantic assessment against the approved requirements and reviewed design. Check necessary story and dependency coverage, contradictions, untestable tasks, unresolved placeholders, and unsupported scope. Return exact located findings to FlowKit-Tasker verbatim, with stable ID, artifact_location, violated_requirement or accepted decision, observed_deficiency, and exact_correction. Feed safely repairable findings back into `speckit.tasks`, preserving task IDs, completion markers, approved decisions, and completed work.

Fresh review must confirm substantive resolution of prior findings and retain new blocking findings before retry or completion; required-file production alone does not establish completion. Wording-only or digest-only edits, renamed or repeated findings, and successful commands do not prove progress. Preserve the substantive product question verbatim, wait for the operator's answer, and never infer that answer. Stop with the exact material design gap, missing prerequisite, operator question, no-progress result, or five-pass safety limit. Complete only when independent review finds no material task-quality or coverage gaps. Present the task plan for review; the operator may separately invoke Analyze. Task generation does not change reviewed design or begin implementation.

## Manual analysis and remediation path

When native analysis dispatch is unavailable, use the same evidence-based continuation contract manually. Run fresh `speckit.analyze` on the active specification, plan, and tasks without modifying them, then classify that report from its findings and current artifacts; missing, failed, or stale analysis is a blocker. Every correction decision uses the latest completed analyzer report; do not ask the operator to classify a routine result. Clean analysis ends successfully, while consequential decisions and genuine blockers stop with the evidence and required operator action.

Use one shared specification → plan → tasks waterfall, entering at the highest affected artifact. The first loop pass skips all corrections and establishes the read-only analysis baseline. For routine findings within the issued scope, enter the waterfall and then run the same analyzer and assessment again: specification changes require `speckit.specify` → `speckit.plan` → `speckit.tasks` → `speckit.analyze`; plan changes require plan → tasks → analyze; task changes require tasks → analyze. Continue while each pass resolves tracked findings. Stop on repeated findings, no measurable progress, stale evidence, an exhausted five-pass safety cap for corrections (six total passes including the baseline), or a blocker. Preserve completed work and report the smallest safe resumption action. Constitutional amendments, authority or material-scope changes, and ambiguous recovery require an explicit operator decision.

## Manual implementation path

When native implementation dispatch is unavailable, first record unfinished eligible task IDs from the operator-selected feature's existing task plan. If none remain, verify completion and stop. Otherwise invoke `speckit.implement` for all remaining eligible tasks. After each session, inspect current task and validation evidence against the prior task list. If eligible tasks remain and the session completed a previously unfinished task, run another implementation session. Continue until complete, a concrete blocker or required operator input, no progress, or the five-pass safety cap. The FlowKit wrapper does not invoke Specify, Plan, Tasks, Analyze, or another FlowKit workflow.

Report completed and remaining task IDs, validation results, changed paths, and the exact blocker or operator question when work stops. Confirm completion from the task checklist and validation evidence, not merely command success. Treat no progress or cap exhaustion as a bounded stop, preserve completed work, and identify a safe resumption point. Leave Converge, roadmap verification, Git integration, and acceptance for separate operator action.

## Manual convergence path

When native convergence dispatch is unavailable, run `speckit.converge` for the operator-selected implemented feature on every pass. Classify its fresh findings, appended remediation tasks, prerequisite errors, and validation evidence. The command owns gap detection and task recording; the wrapper assessment owns routing and loop control. A clean result stops at Feature Converged; Close Out requires a separate operator instruction.

For routine in-scope findings, enter the shared specification → plan → tasks waterfall at the highest affected artifact; implementation-only gaps skip all three stages. Preserve existing task IDs, completion markers, and convergence work. Analyze changed tasks before implementation; check fresh analysis and exact task eligibility before invoking `speckit.implement`. Already recorded work also receives fresh analysis. An analysis blocker or required operator decision prevents implementation and stops with the exact required action.

After implementation, return directly to `speckit.converge` within the same invocation. Compare its next report against the prior gap baseline before authorizing another correction. A prior gap must be resolved in current behavior and validation; appended tasks, checkbox claims, and changed bytes alone do not demonstrate progress. Five correction passes are followed by a final convergence check, using six total loop passes. Stop before further correction on no progress, repeated findings, stale evidence, failed prerequisites, or cap exhaustion. Substantive product, constitutional, authority, material-scope, and ambiguous-recovery decisions require operator input without taking the consequential action. One main-task report handles every final outcome, preserving completed work and the exact resumption action. Convergence does not integrate Git, update the roadmap, accept the feature, or invoke Close Out.

## Manual closeout path

When native closeout dispatch is unavailable, identify the feature by its exact repository-relative specification directory and inspect current convergence and completion evidence. Clear evidence authorizes an in-place Draft-to-Complete update to that existing specification; do not create a feature or change its requirements. Existing Complete specifications proceed to a fresh debrief without another status write. Current trusted already-verified evidence may bypass the correction loop, but it does not bypass wiki maintenance.

Pass the explicit `SPEC_TARGET` to every debrief and approved roadmap-write command. Run `speckit.flow-roadmap.debrief` at the start of every loop pass. Its first assessment establishes the finding baseline. For routine in-scope findings, enter one shared specification → plan → tasks waterfall at the highest affected artifact, preserving task IDs and completed work. Run fresh analysis, assess exact task eligibility, and implement only eligible work. A blocked eligibility assessment or unresolved implementation blocker stops before another debrief. No eligible work permits the next fresh check. After correction, rerun debrief; continue only when a prior finding was resolved. Six checks allow five correction passes and a final confirmation. Required operator input, stale evidence, repeated findings, no progress, missing prerequisites, or cap exhaustion stop with the exact question or blocker and safe resumption action.

Present the exact roadmap verification patch for approval before running `speckit.flow-roadmap.write`. Preserve the original return or defer choice and make no write for either. Re-read the roadmap to verify an approved write; command success alone is insufficient. Both newly verified and already-verified features curate durable wiki sources and enter a five-pass reconciliation loop. Each pass selects one authorized source, ingests it, runs full wiki lint with an empty scope argument, and reassesses exact source-coverage and page findings. Map stale pages through their citations to source identities; do not ingest the pages themselves. Repeat only when a prior gap is substantively resolved and the next refresh remains within the approved source set. Conflicting source authority, unavailable sources, age-only warnings without changed claims, unsupported repairs, scope expansion, no progress, and cap exhaustion stop as blocked. Preserve conflicts and required operator questions rather than choosing a claim or bumping timestamps. Clean, current ingestion, coverage, lint, and Git-change evidence are required before the commit-readiness report. One final report preserves outcomes and partial state; closeout does not commit, integrate Git, accept the feature, or invoke another workflow.

## Manual wiki lint/update path

Invoke `$flow-kit-wiki-lint-update` to maintain the project wiki; no active feature is required. Empty `lint_scope` runs full wiki lint. An optional exact page filename or supported check narrows the lint scope. Supply exact registered remote source URLs explicitly through `authorized_urls` (one URL per line) before permitting their refresh; registered local project sources identified by stale findings are within invocation scope.

Start with lint, retain all findings, and map source-backed stale pages through cited S-ids to registered source identities. Deduplicate shared sources. Refresh one eligible source per pass, then rerun lint. Independent inconsistencies or other findings remain visible while safe stale sources are refreshed; conflicted authority, unsupported repairs, age-only warnings without substantive update evidence, and unavailable or unauthorized sources are reported for resolution. No timestamp-only refresh or arbitrary claim rewrite is allowed. Continue only when a prior finding is substantively resolved. Twenty-six lint assessments allow at most 25 single-source refreshes and final confirmation; exhausted capacity or no progress reports remaining sources and the smallest safe resumption action. Clean means the latest lint has no unresolved findings. The final report includes every remaining issue, suggested action, refreshed source, and partial update. Do not mutate feature artifacts, roadmap, or Git, and do not invoke another workflow.

## Exact semantic review handoffs

Plan and Tasks keep independent FlowKit-Reviewer findings separate from the strict assessment envelope. Each finding retains its stable ID, artifact location, violated requirement or accepted decision, observed deficiency, and exact correction. Request preparation forwards the full findings verbatim to FlowKit-Planner or FlowKit-Tasker. Fresh review confirms substantive resolution and retains new blocking findings; renamed findings, rewording, changed digests, or command success cannot prove progress. Preserve unanswered product questions for same-child operator relay or a specific blocked recovery. Existing topology and five-pass bounds apply; task history survives correction. Deterministic scripted-agent fixtures verify handoff and controller routing, not live reasoning.

Implement, Converge, and Closeout require an attributable implementation delta for FlowKit-Code Reviewer findings. Retain stable finding IDs, affected locations, requirements, observed deficiencies, exact corrections, and eligible task mappings. Forward those exact findings to FlowKit-Coder through the existing correction path and use fresh independent review to confirm resolution. A finding without a safe eligible task route stops with a specific task-recording or reopening resumption action. Implement cannot invent or reopen tasks. These paths grant no product answer, later workflow invocation, roadmap write, Git integration, or acceptance.

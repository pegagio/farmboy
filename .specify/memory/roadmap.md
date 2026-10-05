<!--
SYNC IMPACT REPORT
==================
Version change: 1.18.4 → 1.19.0
Bump rationale: MINOR — propose one new planned feature for the operator-requested workflow improvements across the five consolidated feedback observations.

Changes this revision:
  - Add Feature 020 — FlowKit Workflow Iteration and Improvements as planned, covering explicit intent and feature selection, checklist readiness, and agent capacity.
  - Preserve Feature 016 as planned, Feature 017 as verified with qualification, and Feature 018 as abandoned.
  - Do not reuse Feature 019, which is referenced by the October 5 report as independent catalog Python prerequisite work but is absent from this checkout's ledger.

Specs affected: 020 (planned; specification not yet authored)
Open questions added/resolved: Feature 020 must establish current reproducibility, supported capacity behavior, and the authorization contract before choosing implementation details.

Notes: Direct operator request on 2026-10-05 groups all three improvement areas into one work item. Evidence: .specify/workflow-feedback/exports/consolidated-workflow-issues-20261005/report.json and report.md, committed in c4ff53c. Feedback is evidence, not implementation or acceptance; this proposal changes no workflow, constitution, active feature pointer, or installed component.
-->

# Spec Kit Flow — Spec Roadmap

This living roadmap records the project's completed specifications and leaves room for future features. It is not a commitment to new scope or sequence. The [constitution](constitution.md) governs this ledger; each entry points to its feature specification. The operator designated entries 001–011 verified on 2026-09-26; later entries carry their own lifecycle states below.

## Contents

- [Vision and end states](#vision-and-end-states)
- [Constraints and decisions](#constraints-and-decisions)
- [Planned specs](#planned-specs)
- [Open questions](#open-questions)
- [Cross-cutting notes](#cross-cutting-notes)

Status legend: **undecided** · **needs-info** · **planned** · **specced** · **in-progress** · **implemented** · **verified** · **deferred** · **abandoned**.

## Vision and end states

The constitution establishes the durable project direction; the completed specs define the current delivery boundary.

- Provide a reusable, human-directed Spec-Driven Development workbench whose feature artifacts stay consistent through merge-bounded flow-back and explicit review gates.
- Keep generic workflows, independently versioned extensions, portable consumer feedback, maintainer intake, and the bundle catalog traceable to reviewed source and bounded validation evidence.
- Preserve manual workflow paths and human control over agent selection, material scope, roadmap verification, Git integration, publication, and acceptance.
- Treat additional features as future roadmap amendments. Features 012 and 013 are verified independently; feature 014 covers accepted workflow improvements, and feature 015 covers named Codex agents for delegated steps.

## Constraints and decisions

These cross-cutting constraints come from the [constitution](constitution.md); they do not create new feature scope.

- **C-01 — Merge-bounded persistence**: Before merge, accepted discoveries flow through the current spec, plan, tasks, and implementation; after merge, behavioral changes move into a new feature directory. This keeps reviewable intent and historical records coherent.
- **C-02 — Human-directed authority**: The operator chooses workflows and task scope. Every delegated workflow step declares a reviewed Codex agent name; invocation authorizes that assignment without a per-run agent, model, or effort override. A Codex controller may launch bounded step subagents and must relay human decisions through the main task. Command success cannot confer roadmap, scope, integration, or acceptance decisions.
- **C-03 — Generic component boundaries**: This repository owns generic workflow and feedback source; the bundle composes versioned components. The Diagram remains a consumer, with adapter behavior governed separately.
- **C-04 — Reviewable source and fallback**: Changes target source packages, planning and task generation remain distinct, and each workflow retains a manual-prompt path. New build tools or dependencies require a documented need and approval.
- **C-05 — Bounded validation and feedback**: Disposable consumer tests record component and CLI provenance without claiming publication, stock compatibility, or live-agent quality. Feedback capture and intake provide evidence and proposals, not direct source or authority changes.

## Planned Specs

Entries 001–011 record verified history. Features 012, 013, 014, and 015 are verified. Feature 016 is planned; Feature 017 is verified with its documented follow-up qualification; Feature 018 is abandoned. Its proposed capacity repair and sequencing are retained as historical intent, not an active delivery commitment; the original observation remains unresolved. Feature 020 is planned for one consolidated workflow improvement iteration. Dependencies describe delivery prerequisites between these specs, not the order in which an operator must run workflow phases.

### 001 — Start Eligible Feature  [status: verified]

- **Description**: Guide an operator from an eligible roadmap item through an approved patch, cited context, a specification draft, and roadmap brief.
- **Outcome**: An eligible start produces a reviewed feature draft and explicit next choice; ambiguous eligibility, dependencies, or context stop without a state change.
- **Scope (in)**: Eligibility and dependency checks, exact patch approval, governing-context coverage, specification drafting, brief, and manual fallback.
- **Scope (out)**: Automatic clarification, planning, agent dispatch, Git integration, acceptance, or Diagram runtime behavior.
- **Depends on**: none.
- **Governed by**: C-02, C-03, C-04.
- **Spec dir**: `specs/001-start-eligible-feature/`.

### 002 — Clarify Specification  [status: verified]

- **Description**: Run one bounded clarification session for an operator-selected active specification and route its result.
- **Outcome**: Accepted answers enter the spec incrementally, unresolved ambiguity remains visible, and the operator chooses continuation, planning readiness, or deferral.
- **Scope (in)**: One session, the current five-question boundary, result review, explicit routing, and manual fallback.
- **Scope (out)**: Automatically declaring readiness, launching planning, or introducing an unapproved continuation preset.
- **Depends on**: none.
- **Governed by**: C-02, C-04.
- **Spec dir**: `specs/002-clarify-specification/`.

### 003 — Plan Implementation  [status: verified]

- **Description**: Check planning readiness and create reviewable technical artifacts for a clarified feature.
- **Outcome**: A plan, research, data model, contracts, and quickstart are offered for review only after an explicit readiness decision.
- **Scope (in)**: Reviewed-spec confirmation, plan/return/defer gate, technical planning, and manual fallback.
- **Scope (out)**: Resolving product ambiguity through design assumptions or automatically generating tasks.
- **Depends on**: none.
- **Governed by**: C-02, C-04.
- **Spec dir**: `specs/003-plan-implementation/`.

### 004 — Generate Implementation Tasks  [status: verified]

- **Description**: Generate dependency-ordered tasks from reviewed design artifacts as a separate workflow phase.
- **Outcome**: The operator reviews task coverage and unexpected human work before choosing analysis, replanning, amendment, or deferral.
- **Scope (in)**: Task proposal generation, coverage review, explicit routing, and manual fallback.
- **Scope (out)**: Automatic implementation, agent selection, Git integration, or bypassing analysis.
- **Depends on**: none.
- **Governed by**: C-02, C-04.
- **Spec dir**: `specs/004-generate-tasks/`.

### 005 — Analyze and Remediate Artifacts  [status: verified]

- **Description**: Analyze spec, plan, and task consistency before implementation and route bounded corrections through affected artifacts.
- **Outcome**: Routine findings receive dependent-artifact reconciliation and another read-only analysis; consequential or blocked outcomes stop for a separate decision.
- **Scope (in)**: Analysis disposition, scoped spec/plan/task remediation, reanalysis, and manual fallback.
- **Scope (out)**: Unapproved constitutional, authority, material-scope, or ambiguous-recovery changes and automatic implementation.
- **Depends on**: none.
- **Governed by**: C-01, C-02, C-04.
- **Spec dir**: `specs/005-analyze-remediate/`.

### 006 — Implement Eligible Work  [status: verified]

- **Description**: Implement analyzed, eligible tasks within the operator-selected feature, task, and agent boundary.
- **Outcome**: Execution evidence is reviewed, discoveries return through the relevant artifacts and analysis, and blockers stop without expanding scope.
- **Scope (in)**: Eligible task execution, prerequisite checks, return routes, blocker handling, and manual fallback.
- **Scope (out)**: Automatic agent launch, implementation retries after artifact changes, roadmap verification, publication, or acceptance.
- **Depends on**: none.
- **Governed by**: C-01, C-02, C-04.
- **Spec dir**: `specs/006-implement-eligible-work/`.

### 007 — Converge Feature  [status: verified]

- **Description**: Compare implementation with current feature artifacts and route bounded remaining work to resolution.
- **Outcome**: Clean convergence stops for separate closeout; remediation tasks pass analysis before another implementation and convergence run.
- **Scope (in)**: Gap assessment, clean/remediation/blocked disposition, task analysis, and manual fallback.
- **Scope (out)**: Automatic closeout, Git integration, publication, or acceptance.
- **Depends on**: none.
- **Governed by**: C-01, C-02, C-04.
- **Spec dir**: `specs/007-converge-feature/`.

### 008 — Close Out Feature  [status: verified]

- **Description**: Guide explicit feature-completion review, roadmap verification, curated wiki maintenance, and commit-readiness review.
- **Outcome**: A separately approved completion operation and exact roadmap patch precede wiki ingestion and lint; commit readiness remains an operator decision.
- **Scope (in)**: Completion gate, roadmap debrief and patch review, selected wiki sources, lint, and manual fallback.
- **Scope (out)**: Inventing a completion operation, automatic commit or Git integration, or implied project acceptance.
- **Depends on**: none.
- **Governed by**: C-01, C-02, C-05.
- **Spec dir**: `specs/008-close-out-feature/`.

### 009 — Consumer Feedback  [status: verified]

- **Description**: Capture local workflow observations and export portable reports without changing source or authority.
- **Outcome**: Valid observations become append-only local evidence and deterministic digest-bearing JSON and Markdown reports; malformed or sensitive input is rejected.
- **Scope (in)**: Provenance validation, duplicate rejection, portability checks, offline capture and export.
- **Scope (out)**: Automatic report transfer, maintainer disposition, source changes, or roadmap mutation.
- **Depends on**: none.
- **Governed by**: C-02, C-03, C-05.
- **Spec dir**: `specs/009-consumer-feedback/`.

### 010 — Maintainer Feedback Intake  [status: verified]

- **Description**: Validate transferred consumer reports and record bounded maintainer disposition proposals.
- **Outcome**: Valid reports create a canonical inbox copy and triage proposal; duplicates link to earlier intake, while invalid input creates no record.
- **Scope (in)**: Schema, digest, provenance, evidence, and redaction checks; safe triage and duplicate handling.
- **Scope (out)**: Packaging intake into the consumer bundle or directly editing workflows, roadmaps, installed components, Git state, or agent policy.
- **Depends on**: 009.
- **Governed by**: C-02, C-03, C-05.
- **Spec dir**: `specs/010-maintainer-intake/`.

### 011 — Bundle Catalog and Lifecycle  [status: verified]

- **Description**: Package pinned workflow and extension components and guide verified installation, refresh, and removal in consumer projects.
- **Outcome**: The local catalog records reviewed provenance and checksums, and disposable lifecycle validation covers installation through removal without deleting consumer-owned evidence.
- **Scope (in)**: Bundle pins, deterministic release assets, catalog verification, tested CLI coordinates, lifecycle tests, and installation documentation.
- **Scope (out)**: Remote publication, stock Spec Kit compatibility claims, live-agent quality claims, or automatic consumer adoption.
- **Depends on**: 001, 002, 003, 004, 005, 006, 007, 008, 009, 010.
- **Governed by**: C-02, C-03, C-04, C-05.
- **Spec dir**: `specs/011-bundle-catalog/`.

### 012 — Consumer Adoption of Merge-Bounded Flow-Back  [status: verified]

- **Description**: Investigate how the FlowKit bundle should bring the Merge-Bounded Flow-Back Spec Persistence Model into consumer projects, then implement the selected mechanism.
- **Outcome**: New and refreshed bundle consumers have a validated, reviewable path to use the model in project guidance and governance; adoption is confirmed from project state rather than assumed from installation.
- **Scope (in)**: Compare an onboarding skill, a preset or template approach, and other supported mechanisms; review and refine the proposed README and constitution language as needed; implement the chosen path, conflict handling, and disposable-consumer validation.
- **Scope (out)**: Silent replacement of existing project governance, retroactive edits to merged feature history, a separate scope-creep policy, Diagram-specific behavior, and changes to Specify's global base template.
- **Depends on**: 011.
- **Governed by**: C-01, C-02, C-03, C-04, C-05.
- **Notes**: The operator set the adoption goal and requested investigation followed by implementation. Agents should recommend the operator-invoked FlowKit consistency workflows and flag missing checks rather than independently launch those workflows or their core commands. `docs/merge-bounded-flow-back.md` is a starting proposal, not required verbatim text; the selected delivery mechanism and bounded observations are recorded in Feature 012 research, contract, and validation.
- **Spec dir**: `specs/012-consumer-adoption/`
- **Verification**: The specification is `Complete`; the [fresh debrief](../../specs/012-consumer-adoption/roadmap-reviews/debrief-20260929T162707Z.md) recommends `verified` with zero Must-Address findings, and the operator explicitly approved this transition. The [validation record](../../specs/012-consumer-adoption/validation.md) bounds the result to reviewed source and disposable consumers; real-consumer adoption and Git integration remain separate.
- **Resolved delivery decision**: Use a reviewed runbook, reusable proposal text, evidence worksheet, and copyable manual prompt linked from installation and refresh instructions. A dedicated onboarding skill or installed preset was not selected for this delivery; see [research](../../specs/012-consumer-adoption/research.md#delivery-mechanism).
- **Resolved conflict decision**: Inspect existing governance and active guidance rule by rule, preserve equivalent or stricter compatible wording, present minimal exact patches, require an operator decision for constitutional amendments or material conflicts, and recheck baselines before accepted edits; see [research](../../specs/012-consumer-adoption/research.md#review-and-conflict-resolution) and the [adoption contract](../../specs/012-consumer-adoption/contracts/adoption.md#review-and-mutation-contract).
- **Resolved evidence decision**: Confirm adoption only with M1–M5 evidence in applicable active agent guidance and compatible governance, a known integration boundary, project-relative citations and digests, and a separate operator decision. Report incomplete or declined paths as `partial`, `declined`, or `unresolved` according to observed state; see [research](../../specs/012-consumer-adoption/research.md#adoption-evidence-and-outcomes), the [output contract](../../specs/012-consumer-adoption/contracts/adoption.md#output-contract), and [bounded validation](../../specs/012-consumer-adoption/validation.md). This does not assert adoption in a real consumer.

### 013 — FlowKit Codex Workflow Controllers  [status: verified]

- **Description**: Provide direct `flow-kit-*` Codex skills through the FlowKit catalog route alongside the Specify bundle so an operator can explicitly run each installed FlowKit workflow inside the consumer project's Codex task, with a main-task controller and bounded step subagents using concrete models declared in the workflow.
- **Outcome**: A consumer can invoke a stable, named skill for each of the eight workflows under its FlowKit display name, see progress and diffs in the Codex desktop task, use declared per-step models and reasoning efforts without choosing them at every step, override one named step when needed, answer clarification and review questions in the main task, and receive the workflow result without losing its human gates or separate phase boundaries.
- **Scope (in)**: Deliver and maintain direct Codex skill source through the supported FlowKit catalog install, refresh, and removal route with ownership-aware conflict handling; follow the installed, versioned workflow definition in a Codex task; define and validate concrete per-step model declarations in workflow YAML and FlowKit reasoning-effort metadata, using medium effort unless a step declaration or one-step operator override specifies otherwise; provide explicit invocation, required-input checks, visible effective assignments, bounded subagent dispatch, same-child continuation for interactive steps, and parent-mediated human decisions; validate fresh installation, refresh, removal, project context, interaction, and workflow outcomes in disposable consumers; document the operator-facing path and manual fallback.
- **Scope (out)**: Model roles or consumer model mappings, duplicating workflow prompts or decision rules in skills, silent fallback or undeclared model selection, invoking a later workflow without separate instruction, changing workflow prompt behavior solely to accommodate the controller, scheduling, Git integration, roadmap verification, or feature acceptance.
- **Depends on**: 011; no dependency on 012.
- **Governed by**: C-02, C-03, C-04, C-05.
- **Notes**: The previously approved thin launcher that delegates to `specify workflow run` is superseded for the Codex desktop path because its separate `codex exec` processes lose the desired task UI. The earlier bundle-installed skill delivery assumption is also superseded: native Specify bundle commands manage their declared Specify components, while the FlowKit catalog route manages direct Codex skills alongside them. Keep the installed workflow as the behavior authority and retain a manual-prompt fallback. The operator accepts that the initial concrete model IDs may be non-portable; model roles and consumer mappings are deferred to a later amendment. Live probes showed a different-model child task and parent-mediated answer relay; they did not prove full Specify integration or YAML model metadata support. The eight skills use stable `flow-kit-*` invocation names and the approved FlowKit display names in the feature specification.
- **Spec dir**: `specs/013-bundle-workflow-launchers/`

### 014 — FlowKit Workflow Improvements  [status: verified]

- **Description**: Review the original eight FlowKit workflows, deliver ten active workflows and retain Start Feature as stop-only deprecated source for correct gates, automation, continuation, and recovery so each operator-invoked workflow can reach an evidenced conclusion or a specific bounded stop. Address the accepted roadmap-linkage, readiness, task-generation, Converge, Close Out, and workflow-resumption findings as consequences of those control-flow gaps, and incorporate Feature 015's reviewed agent assignments with usable repository-local Codex agent configurations.
- **Outcome**: All ten active source workflows and the deprecated Start Feature source have a machine-checkable inventory of steps, branches, gates, assignments, terminal outcomes, and resumption evidence. Each workflow's routine in-scope corrective path reassesses fresh evidence and continues while measured progress remains, stopping at evidenced success, a consequential human decision, a repeated finding, no progress, a finite reviewed cap, or a specific blocker. The controller resumes only from validated, attributable state and never invokes another FlowKit workflow. Every explicitly delegated step uses an appropriate reviewed agent name, and the repository includes usable local configurations for the selected names. Roadmap edits, constitutional changes, material scope or authority changes, Git actions, feature acceptance, and other consequential decisions remain behind their existing explicit human gates.
- **Scope (in)**: Inventory and review all active workflow graphs and the deprecated definition, including branches, human gates, automatic core-command steps, terminal results, interruption/recovery evidence, and delegated-agent assignments; implement the shared controller and recovery support required for evidence-based continuation, fresh reassessment, progress comparison, a finite iteration cap, and safe resumption; update the active workflow definitions and manual-prompt paths to reach an evidenced conclusion or a specific bounded stop, including the approved Clarify continuation and Close Out completion behavior; complete Analyze's shared spec→plan→tasks corrective waterfall and Implement's continuation over existing eligible tasks without wrapper re-specification, re-planning, re-tasking, or analysis; preserve spec→plan→tasks ordering when findings change higher-level artifacts; use only inspectable command/artifact evidence, never command success alone, to claim progress or completion; apply the reviewed Roadmap Agent, Specifier, Planner, Tasker, Reviewer, Coder, Code Reviewer, and Wiki Curator assignments where appropriate and add repository-local Codex agent configuration files; split Start Feature into separately invoked Select Feature and Specify, with dependency discussion, exact human selection/activation, pointer-only selection, and same-target authoring; add a separately invoked Wiki Lint Update loop that lints first, refreshes registered authorized stale sources one at a time, and reports every unresolved issue; maintain a project-owned source-faithful workflow rendering skill and diagrams; collapse equivalent paths while retaining downstream authorization checks and use blocked for required operator input; add a machine-checked inventory and graph/branch fixtures; validate supported and rejected loop shapes, human gates, all-branch assignment preflight, resume state, manual fallbacks, and disposable initialized consumers.
- **Scope (out)**: Invoking one FlowKit workflow from another; undeclared later phases; installing or modifying agent files in consumer projects (a future feature may define bundle installation); silently changing the roadmap or constitution; bypassing consequential human gates; unbounded work or work outside the selected feature; implicit roadmap verification, Git integration, feature acceptance, or project acceptance; independent extension changes without their own review; retrospective edits to verified Feature 007/008 history; unrelated feedback or features.
- **Depends on**: 001, 002, 003, 004, 007, 008, 013, 015; no dependency on 012.
- **Governed by**: C-02, C-03, C-04, C-05.
- **Notes**: Five accepted maintainer intakes and the operator's corrected Converge-loop request define the current change set. `intake-4c31665697a1` records `speckit-flow-start-feature` 0.3.0 (`sha256:ccab39bda126a92f3f3242fc747702525f3677cb6e7ad52cd8211e50681302db`) reaching a roadmap brief without a `Spec dir` mapping despite a correct active feature pointer. Its proposed disposition is a workflow source change to establish or safely stop on the missing specification-to-roadmap linkage. `intake-0e38806b5f69` records `speckit-flow-clarify` 0.2.0 (`sha256:792b68979817fef06bbac3521b0f3034910dba44162a46ca208db27e218d6eb6`) leaving the operator to judge whether significant ambiguity remained after the agent's assessment. Its proposed disposition is an evidence-backed residual-ambiguity assessment and recommendation, preserving operator authority over substantive answers and separate workflow invocation; investigate final-gate presentation without assuming a UI cause. `intake-50695033844a` records `speckit-flow-plan` 0.2.0 (`sha256:5c5cfac1fbad27e5e87f159307bd06cc2efc4c20aa565bc3e126b10014418f21`) presenting an unconditional readiness gate after the operator invoked planning; the operator requested its removal. Its proposed disposition is an agent readiness assessment with a specific stop for missing prerequisites or material product ambiguity, without launching a later workflow. These three records were accepted as proposals, not authorization for source changes. Their local inbox and triage files are excluded from Git.
- **Task feedback**: `intake-1fb76e5dfaca` records a `speckit.tasks` command child asking for an extra design-choice confirmation before generating tasks, despite the operator invoking Tasks; investigate the cause without assuming the installed workflow defines that pre-generation gate. `intake-c95ee8c49f7e` records the operator request to replace the installed post-generation review gate with an agent coverage and completeness assessment that exits successfully when complete and reports specific material gaps otherwise. Both observed `speckit-flow-tasks` 0.2.0 (`sha256:8912f7c87e3ad6204a8cf325aa2823608c54bab37ab148aecb01dce46956ec30`). The second request supersedes the first intake's assumption that the post-generation gate should remain. Both are accepted proposals, not authorization for source changes; their local inbox and triage files are excluded from Git. The operator retains task review and separate Analyze invocation. This entry is the durable scope record for the normal specification, planning, task, implementation, and convergence flow.
- **Earlier Converge feedback (partly superseded)**: The operator chose remediation after `speckit-flow-converge` 0.2.0 (`sha256:90e0970e907ed84ca4c21d6f1b2d9a3d025766b7a2b7f59dacaa8c556481865f`) appended Feature 012 T017, then requested evidence-based routing to the existing Analyze step without a routine human classification gate. The recorded run `.specify/flow-controllers/runs/e5a89918-dbbf-4b1e-9494-2a2c1e31cc04/summary.json` shows the gate. Its proposal to stop after analysis for separate Implement and later Converge invocations is superseded by the operator's subsequent full-loop request; the evidence-based classification and analysis-before-implementation requirements remain.
- **Close Out gate correction**: In Feature 012, the operator authorized changing the existing spec status to `Complete`, and the resulting project state was inspectable. The installed Close Out workflow still required the operator to select `operation-available` before roadmap debrief. Feature 014 must let the agent recognize this routine case from evidence and continue without that classification question; if no authorized completion action or reliable evidence exists, it must stop with a specific reason. The installed `speckit-specify` skill creates a new feature and must not be used as a completion substitute. Preserve explicit approval for the exact roadmap verification patch and separate Git authority. This updates source prospectively rather than rewriting verified Feature 008 history.
- **Close Out debrief continuation**: The first Feature 012 debrief found stale current-artifact completion claims and no verification patch. After those claims were corrected, the operator had to invoke a fresh debrief manually; that second report recommended `verified`. The operator expects the invoked Close Out workflow to perform bounded in-scope reconciliation and rerun debrief itself, stopping only for a material decision, untrustworthy delta, repeated finding, or lack of progress. This is not authority to apply a roadmap patch, commit, or accept the feature without the existing review gates. The current installed workflow has no such loop, so Feature 014 must reconcile this target with the controller protocol and verified Feature 008 prospectively.
- **Converge loop correction**: The operator expects an invoked Converge run to identify gaps, create bounded tasks, flow back to spec and plan when needed, analyze the updated tasks, implement eligible fixes, and repeat Converge until clean or stopped by a real blocker or consequential decision. Constitution 6.0.0 now permits reviewed bounded core-command correction and reassessment inside the selected workflow while continuing to prohibit nested FlowKit invocation. Feature 014 applies that authority prospectively; verified Feature 007 history remains unchanged.
- **Accepted review refinements**: The operator approved the workflow simplifications, shared waterfalls, ten active workflow inventory, deprecated combined source, wiki reconciliation loops, and exact-source rendering conventions during the Feature 014 review. Current source behavior is recorded in the feature artifacts and current inventory. Local commits and static tests are not feature acceptance, release, consumer adoption, or proof of live named-agent behavior.
- **Spec dir**: `specs/014-flowkit-workflow-improvements/`
- **Verification**: The Complete specification, 89 completed tasks, current-task Implement invocation, fresh clean Converge assessment and independent Code Reviewer result are recorded in `specs/014-flowkit-workflow-improvements/validation/implement-current-tasks.json` and `specs/014-flowkit-workflow-improvements/validation/convergence-current-tasks.json`. The fresh debrief `specs/014-flowkit-workflow-improvements/roadmap-reviews/debrief-20261002T152822Z.md` returned `PROCEED WITH UPDATES` with zero Must-Address findings; its two roadmap-stale recommendations are addressed by the current role list and resolved-question/current-route wording. Defined live validation covers 23 scenarios with current source continuity, 127 passing automated tests and installation lifecycle evidence under `validation/live-workflows/`; it does not establish exhaustive branches, native model/effort identity, release, consumer adoption, Git integration or feature acceptance.

### 015 — Named Agents for Delegated Steps  [status: verified]

- **Description**: Let each explicitly delegated FlowKit workflow step name a consumer-configured Codex custom agent.
- **Outcome**: Every delegated step names a reviewed agent; different steps may name different agents. Main-task steps and human gates stay in the driving task. Codex's native subagent activity shows each launched child under a task label containing its reviewed agent name; exact native selection is verified separately, and the child pane shows model and reasoning effort when Codex exposes them.
- **Scope (in)**: A fixed reviewed set of agent names; Specify-compatible per-step agent declarations; explicit delegation; native Codex custom-agent configuration; all-branch named-agent preflight; native subagent visibility; main-task and human-gate boundaries; disposable-consumer and native-runner validation.
- **Scope (out)**: Feature 014 workflow changes and retrospective edits to verified Feature 013 artifacts.
- **Depends on**: 013; no dependency on 014.
- **Governed by**: C-02, C-03, C-04, C-05.
- **Notes**: Architect, Builder, Coder, and Verifier are the reviewed names. Codex owns each agent's optional model and reasoning settings; Feature 015 must prove exact named dispatch in the supported client.
- **Spec dir**: `specs/015-agent-roles-assignment-inheritance/`
- **Verification**: The completed spec, 29 checked tasks, final clean convergence pass, focused tests, and bounded native Codex observations are recorded in `specs/015-agent-roles-assignment-inheritance/validation.md` and `specs/015-agent-roles-assignment-inheritance/roadmap-reviews/debrief-20260929T225206Z.md`. The debrief returned `PROCEED WITH UPDATES` with no Must-Address findings; its two roadmap-stale recommendations are addressed below. This status does not imply a published catalog release or native Specify runner parity.

### 016 — Centralized Workflow Agent Probing  [status: planned]

- **Description**: Replace repeated agent probes across workflow runs with one dedicated workflow that checks every agent name used by the FlowKit workflows.
- **Outcome**: An operator can invoke one workflow to discover and probe each distinct named agent used by active workflow definitions. It reports which agents were successfully dispatched and which could not be verified. Ordinary workflow runs perform no agent probes.
- **Scope (in)**: Discover the distinct agent names from active workflow definitions; run one bounded, non-mutating probe for each name; report results and failures without silently substituting another agent; remove probes from the other workflows; update validation and documentation so the centralized workflow covers the agent-probe requirement.
- **Scope (out)**: Changing workflow agent assignments or agent configurations; automatic probing during ordinary workflow execution; treating configuration presence or no-op dispatch as proof of live named-agent behavior.
- **Depends on**: None.
- **Governed by**: C-02, C-03, C-04, C-05.
- **Notes**: This feature centralizes the agent-probe validation currently included in Feature 014's requirements. It should preserve evidence about which names were tested and what the probe established.
- **Spec dir**: `specs/016-centralized-agent-probing/`

### 017 — FlowKit Agent Configuration and Consumer Delivery  [status: verified]

- **Description**: Prefix the eight project-defined Codex agent names with `FlowKit-`, review their role configurations, select explicit models and reasoning efforts, and determine how those agents are installed into consuming projects.
- **Outcome**: FlowKit workflows use distinct, consistently named agents with reviewed role instructions and explicit model/effort settings. Consumers have a documented, reviewable delivery path whose ownership and lifecycle behavior are decided before implementation.
- **Scope (in)**: Rename Roadmap Agent, Specifier, Planner, Tasker, Reviewer, Coder, Code Reviewer, and Wiki Curator with the `FlowKit-` prefix; reconcile current workflow references, controller expectations, configuration filenames, tests, and documentation; review role scope, instruction quality, model suitability, and reasoning effort for each agent; investigate and select consumer installation, refresh, conflict handling, and removal behavior; validate the selected design in disposable consumers and distinguish configuration checks from live named-agent/model evidence.
- **Scope (out)**: Selecting models or efforts in this roadmap amendment; assuming an installation mechanism or permission to overwrite consumer-owned configurations; unrelated workflow control-flow changes; retrospective rewrites of verified feature artifacts; publication, automatic consumer adoption, Git integration, or feature acceptance.
- **Depends on**: 011, 014, 015.
- **Governed by**: C-02, C-03, C-04, C-05.
- **Notes**: The 2026-10-03 selection baseline had eight unprefixed configurations without model/effort settings and excluded agent acquisition from catalog delivery. Feature 017 now supplies eight exact `FlowKit-` identities, independently reviewed instructions and operator-approved explicit model/effort defaults through canonical `flow-kit-agents` 0.1.0, coordinated with bundle 0.14.0 and controllers 0.6.0. Consumer-owned copies use install-missing, cache-only refresh, explicitly targeted reset and preservation on removal. All 44 tasks are complete; recorded validation passed 55 focused checks and 158 full checks with one environment-dependent class skipped. All-eight exact native launch availability passed; effective settings remain unverified. The separately observed inherited native Specify Clarify transport failure remains a limitation. Component provenance, accepted model-support evidence, source-registry/disposable-consumer distinction and unavailable desktop version remain recorded in `specs/017-flowkit-agent-configuration/validation.md` and `native-dispatch.json`. Feature 016 remains independent; no probing or capacity behavior changed.
- **Verification qualification**: On 2026-10-04 the operator explicitly deferred DEP017-01 catalog Python prerequisite preparation and complete runnable provisioning guidance to a follow-up feature. Delivery behavior and file dispositions were demonstrated in the dependency-equipped tested interpreter; the advertised mise catalog refresh failed without PyYAML. Original unconditional FR-008/FR-011/SC-003 usability is not represented as passed. The unresolved defect, required future outcome and validation are retained in `specs/017-flowkit-agent-configuration/follow-up.md`; no numbered feature or runtime approach is selected. Verification applies to the reviewed nondeferred scope and grants no feature acceptance, publication, adoption or Git integration.
- **Spec dir**: `specs/017-flowkit-agent-configuration/`

### 018 — Reliable Workflow Agent Capacity  [status: abandoned]

- **Description**: Resolve the agent-thread capacity failure that blocks sequential FlowKit workflows in a persistent Codex chat, and provide consumer installation and upgrade guidance.
- **Outcome**: Sequential workflows can launch their declared agents without accumulating completed children until capacity is exhausted. Consumers receive actionable capacity configuration recommendations during installation and refresh while retaining ownership of their Codex configuration.
- **Scope (in)**: Investigate effective supported capacity settings and child lifecycle; preserve outputs before releasing verified completed children through supported controls; retain children awaiting answers or continuation; implement bounded capacity recovery and specific failure reporting; update controller guidance, tests, and documentation; print concise capacity recommendations and a setup-documentation reference from both catalog install and refresh; document how to merge the supported agents.max_concurrent_threads_per_session setting into consumer .codex/config.toml with a value justified by validation; explain effective-setting verification and whether the tested client requires reopening the chat; validate new installs and upgrades with absent, existing, and conflicting configuration, sustained sequential workflow execution, and capacity recovery in disposable consumers.
- **Scope (out)**: Select Feature selection or approval changes; Feature 017 agent configuration and delivery; Feature 016 centralized probing; generic-agent fallback; reuse of probe children for workflow work; cleanup of unrelated chats; silent edits to consumer-owned Codex configuration during installation, refresh, or removal; publication or Git integration.
- **Depends on**: 013, 014, 015.
- **Governed by**: C-02, C-03, C-04, C-05.
- **Notes**: Prioritize observation `clarify-agent-thread-limit-preflight-20261003` as a blocking defect before `select-feature-explicit-choice-reprompt-20261003` and `select-feature-pointer-approval-stop-20261003`. The local journal `.specify/workflow-feedback/observations.jsonl` records installed Clarify 0.4.5 and controller 0.5.3 failing the exact Reviewer preflight after a successful Specifier probe; the effective limit and root cause remain unconfirmed. [Prior capacity recovery](../../specs/014-flowkit-workflow-improvements/validation/live-workflows/capacity-recovery.json) records that reversible archival of verified completed children allowed a fresh named launch; this is historical evidence, not proof of the current cause. Preserve exact named dispatch and fresh bounded work children. A capacity increase alone does not establish resolution; validation must demonstrate sustained sequential use and safe lifecycle handling. Configuration guidance and controller cleanup must explain their complementary roles. Installation, refresh, and removal preserve consumer-owned configuration; no capacity value is selected by this amendment. Features 016 and 017 remain independent and unchanged.
- **Disposition**: Abandoned by direct operator decision on 2026-10-03 because the current approach and specification were rejected. The proposed scope and earlier notes above, feature artifacts, and investigation evidence remain preserved as history; no further implementation is authorized by this entry. The capacity issue remains unresolved, and no replacement feature or approach is selected. Features 016 and 017 remain unchanged.
- **Spec dir**: `specs/018-reliable-workflow-agent-capacity/`

### 020 — FlowKit Workflow Iteration and Improvements  [status: planned]

- **Description**: Iterate on FlowKit workflows through one bounded feature addressing the five consolidated feedback observations across explicit intent and feature selection, Analyze/Implement checklist readiness, and agent capacity.
- **Outcome**: Clear operator instructions carry through the requested operations without redundant selection or approval prompts; uniquely resolving feature references are accepted; Analyze leaves an accurate implementation-readiness state; sequential workflow execution has an evidence-backed capacity remedy or a specific supported limitation and recovery path.
- **Scope (in)**: Reproduce and reassess the five observations against current components; reconcile workflow/controller handling of direct authorization, stable feature IDs and menu positions; propose any necessary governing-contract amendments through their explicit human gates; reconcile checklist ownership and preimplementation checks with future implementation and acceptance evidence; investigate supported agent capacity and lifecycle behavior and implement a reviewed remedy without adopting Feature 018's rejected design by default; update affected source, documentation and regression coverage; validate each improvement area independently and demonstrate their combined sequential workflow behavior with component, CLI and client provenance.
- **Scope (out)**: An open-ended workflow cleanup backlog; unrelated workflow phases or features; catalog Python prerequisite work referenced as Feature 019/DEP017-01; implementation of Feature 016's centralized probing; reactivation of abandoned Feature 018; unreviewed model, effort, capacity-setting or lifecycle-control choices; silent consumer configuration changes; generic-agent fallback; implicit later workflow invocation, roadmap verification, Git integration, publication or feature acceptance.
- **Depends on**: 013, 014, 015, 017.
- **Governed by**: C-01, C-02, C-03, C-04, C-05.
- **Notes**: The operator requested one work item covering all three areas on 2026-10-05. Provenance: `.specify/workflow-feedback/exports/consolidated-workflow-issues-20261005/report.json` and its Markdown projection in commit `c4ff53c`, report ID `consolidated-workflow-issues-20261005`, integrity `sha256:2ed9a33656c5fa7ddcc0429d43c658c1f91e360c2731cc319a92b8b4bf962776`. Included observation IDs: `select-feature-explicit-choice-reprompt-20261003`, `select-feature-pointer-approval-stop-20261003`, `select-feature-explicit-intent-redundant-gates-20261005`, `analyze-unresolved-checklist-gate-20261003`, and `clarify-agent-thread-limit-preflight-20261003`. These describe earlier observed versions and do not establish current reproduction. Keep the three areas separately traceable in specification requirements, tasks and validation within this single feature. Feature 018's abandoned proposal remains historical evidence; its unresolved capacity issue is reassessed here under a fresh design. Feature 016 remains independent and is not a prerequisite unless later review establishes an approved dependency.
- **Spec dir**: `specs/020-flowkit-workflow-iteration-improvements/`

## Open Questions

Feature 018's abandoned proposal left these questions unresolved. They are retained as historical investigation context rather than an active work commitment:

- Which supported capacity setting and effective value apply in the tested Codex client, and does the observed failure arise from concurrently open children, retained completed children, or another limit?
- Which supported lifecycle control releases verified completed children while preserving outputs and children still required for same-step question relay or continuation?
- What bounded recovery behavior is safe when capacity is exhausted, and how does the controller preserve preflight and partial-work evidence?
- What capacity value is justified by sustained sequential workflow validation, and how should consumers merge it with existing configuration and verify that it takes effect?
- What should install and refresh report for absent, existing, conflicting, or unsupported configuration, and does the tested client require reopening a chat to apply a change?

Feature 017's selection-time questions, now resolved by its [specification](../../specs/017-flowkit-agent-configuration/spec.md), [approved research](../../specs/017-flowkit-agent-configuration/research.md), [plan](../../specs/017-flowkit-agent-configuration/plan.md), and [validation](../../specs/017-flowkit-agent-configuration/validation.md) within their documented evidence limits, were:

- Which explicit model and reasoning effort suit each agent's responsibilities, and what evidence and supported Codex configuration fields justify those choices?
- Should consumers receive managed agent files, copyable templates, or another supported delivery mechanism, and where should reviewed reusable configuration source live?
- How should installation, refresh, and removal handle existing names, consumer customizations, ownership records, and migration from unprefixed agents?
- Which checks establish exact named-agent selection and effective model/effort settings, and how should unavailable models or unsupported configurations be reported?


Feature 014's planning questions, now resolved by its [specification](../../specs/014-flowkit-workflow-improvements/spec.md), [plan](../../specs/014-flowkit-workflow-improvements/plan.md), and [current convergence evidence](../../specs/014-flowkit-workflow-improvements/validation/convergence-current-tasks.json), were:

- Which reviewed step or component should establish the roadmap `Spec dir` mapping after the specification directory is known?
- How should the operator review an exact linkage patch, and how should missing, stale, or conflicting mappings stop or recover?
- How should the clarify agent classify and explain remaining significant ambiguity without mistaking the five-question session cap for readiness?
- How should the main task present clarification findings and any substantive human questions while preserving separate operator invocation of later workflows?
- Which specification evidence establishes planning readiness, and how should the plan workflow stop with a specific missing prerequisite or material product ambiguity without an unconditional confirmation gate?
- How should Tasks invocation signal authorization to generate from a reviewed plan without masking a material design gap?
- Which task-coverage evidence is sufficient for successful exit, and how should the agent report incomplete or materially divergent task proposals without a routine human review gate?
- Which command output and artifact evidence reliably distinguishes clean, appended-remediation, and blocked Converge results without asking the operator to classify routine outcomes?
- How can one explicit Converge invocation authorize bounded task analysis, implementation, and reassessment under Constitution II, and what governance amendment or scoped authority rule is required?
- When a convergence discovery changes intended behavior or technical approach, which spec → plan → tasks → analysis sequence must complete before remediation implementation resumes, and what stops or iteration bounds end the loop?
- Which disposable-consumer cases prove the start-feature, clarify, plan, tasks, and Converge changes through manual and direct Codex paths?
- Which inspectable spec status and convergence evidence lets Close Out finish the existing completion edit or recognize it as done without an operator classification gate, and what genuine ambiguity must stop the workflow?
- Which debrief findings can Close Out correct and reassess within its invoked scope, and what snapshot, iteration, and nonprogress rules stop repetition before the exact roadmap-patch gate?

Feature 015's planning questions, now resolved by its specification and validation, were:

- Can the supported Codex client select a custom agent by exact name for each delegated child and confirm its instructions load?
- How should a delegated step's agent name and explicit child marker be represented in Specify-compatible YAML while main-task steps remain in the driving task?
- Can the controller validate every possible named child before workflow work, and can the supported Codex client visibly identify each launched agent?
- Which named-agent behavior can native `specify workflow run` support, and how should any difference from the direct Codex controller be documented?

The supported Codex desktop demonstrated exact named selection and agent-specific instructions. Reviewed per-step `flow_kit.delegated` and `flow_kit.agent` metadata, full-graph preflight, and native task-label visibility are specified in `specs/015-agent-roles-assignment-inheritance/spec.md` and evidenced in its `validation.md`. The Specify loader preserved the metadata, while the separate native runner attempt stopped at disposable checkout trust before a delegated step; the documentation records that limit without claiming parity.

Feature 013 settled direct Codex skill delivery through the FlowKit catalog route alongside the Specify bundle. The controller follows the installed workflow definition; the tested Specify CLI accepted its model and FlowKit effort metadata. Disposable-consumer and desktop validation covered project context, same-child clarification, human gates, diffs, and step outcomes within the limits recorded in `specs/013-bundle-workflow-launchers/validation.md`. Its earlier plan for model roles and consumer mappings was superseded by Feature 015's native named-agent design; Feature 013 verification does not claim publication or broader compatibility.

## Cross-Cutting Notes

The separately invoked workflow route is select-feature, specify, optional clarification, planning, task generation, analysis, implementation, convergence, and closeout; start-feature remains stop-only deprecated source. That operational route is distinct from the delivery dependencies recorded above. The maintainer intake component remains outside the consumer bundle.

The operator designated all eleven entries verified on 2026-09-26. Their `spec.md` headers still say `Draft`; this roadmap records the operator's lifecycle decision without rewriting historical feature artifacts. No configured ADR or PRD evidence was available for this creation.

**Version**: 1.19.0 | **Ratified**: 2026-09-26 | **Last Amended**: 2026-10-05

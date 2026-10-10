# Quickstart: Validate Feature 020 Workflow Improvements

This is a validation guide for future implementation. Baseline commands can run now; new readiness helper/Checker delivery and native matrices are prospective. Their absence is a gap, never a passing zero-test run. All live workflow phases below require their own operator invocation; this guide does not grant mutation, cross-repository change, Git integration or acceptance authority.

## Table of Contents

- [Prerequisites and Baseline](#prerequisites-and-baseline)
- [Focused Source Validation](#focused-source-validation)
- [Tasker-Owned Implement Revision](#tasker-owned-implement-revision)
- [Disposable Consumer Validation](#disposable-consumer-validation)
- [Validation Delivery and Post-Closeout Release](#validation-delivery-and-post-closeout-release)
- [Native Context Matrix](#native-context-matrix)
- [Combined Workflow Demonstration](#combined-workflow-demonstration)
- [Evidence and Result Review](#evidence-and-result-review)
- [Implement Defect-Progress Validation](#implement-defect-progress-validation)

- [Lifecycle Amendment Validation](#lifecycle-amendment-validation)

- [Requested Scope Validation](#requested-scope-validation)

## Prerequisites and Baseline

Start in the Spec Kit Flow source checkout. Use existing prepared pinned tools; do not install new packages or repair DEP017-01 as part of this feature. Read [installation constraints](../../docs/installation.md). Skill-related validation uses the existing skill-tools interpreter. Record actual component metadata and selected CLI output:

```sh
~/.codex/venvs/skill-tools/bin/python -c 'import sys,yaml; print(sys.version.split()[0]); print(yaml.__version__)'
specify --version
git rev-parse HEAD
git status --short
cat controllers/flow-kit/manifest.yml
cat agents/flow-kit/manifest.yml
cat catalog/release.json
git ls-files .codex/agents .worktreeinclude
cat .worktreeinclude
```

Expected current CLI baseline is `specify 1.0.10.dev0+pegagio.2`; the readiness amendment retains this core pin and requires reviewed compatible FlowKit helper/Checker delivery. Stop on absent/incorrect prerequisites with exact dependency/source gap. `mise exec` can also show the selected version when trusted-config access is available; a sandbox trusted-config write failure does not prove the selected direct executable absent. Record version evidence without portable host paths.

Governing reconciliation and any independently needed roadmap delivery must be explicitly approved/validated before testing authority-dependent effects. Roadmap compatibility verification is currently deferred; the readiness design needs no core delivery. [Research](research.md#proposed-governing-reconciliation) supplies proposed wording only. Existing installed exact gates remain active until approved upgrade.

## Focused Source Validation

Existing baseline regression commands are runnable today:

```sh
~/.codex/venvs/skill-tools/bin/python -m unittest discover -s tests -p 'test_controller.py'
~/.codex/venvs/skill-tools/bin/python -m unittest discover -s tests -p 'test_workflow_paths.py'
~/.codex/venvs/skill-tools/bin/python -m unittest discover -s tests -p 'test_agent_delivery.py'
~/.codex/venvs/skill-tools/bin/python -m unittest discover -s tests -p 'test_agent_configs.py'
~/.codex/venvs/skill-tools/bin/python tools/validate_workflows.py --fail-on-unexplained
```

Implementation adds focused `tests/test_workflow_improvements.py` plus shared fixtures. Require the file and at least one executed test before treating the future suite as evidence:

```sh
test -f tests/test_workflow_improvements.py
~/.codex/venvs/skill-tools/bin/python -m unittest discover -s tests -p 'test_workflow_improvements.py' -v
```

Selection cases: explicit stable forms/exact title/natural canonical answer; reordered menu; bare ordinal conflicting with stable ID; first/repeat/existing-spec/switch; unsafe mapping/duplicate owner/malformed pointer/dependency/state drift; direct bounded amendment versus injected evidence/inferred material change; no-op roadmap skip; preserved spec/extra pointer fields; exact partial mutation failure. Assert actual mutation and absence/presence of required focused questions, not just prompt substrings.

## Tasker-Owned Implement Revision

Run the production-rendered Implement task-revision cases and workflow graph projection after changing the source route:

```sh
~/.codex/venvs/skill-tools/bin/python -m unittest tests.test_implement_task_revision.ImplementTaskRevisionRouteTests.test_openCorrectionTaskSkipsTaskerAndClosedOrMissingTaskUsesExactAssignment -v
~/.codex/venvs/skill-tools/bin/python -m unittest tests.test_implement_task_revision.TaskRevisionValidationTests.testCompletedCorrectionTaskCanBeReopenedWithFindingAndHistoryPreserved -v
~/.codex/venvs/skill-tools/bin/python -m unittest tests.test_implement_task_revision.TaskRevisionValidationTests.testMissingInScopeCorrectionTask_isAcceptedWithoutProgressCredit -v
~/.codex/venvs/skill-tools/bin/python -m unittest discover -s tests -p 'test_implement_task_revision.py' -v
~/.codex/venvs/skill-tools/bin/python -m unittest tests.test_implement_task_revision.InstalledConsumerTaskRevisionTests.testLiteralRenderedValidationCommandAcceptsAndRejectsConsumerRevision -v
~/.codex/venvs/skill-tools/bin/python tools/validate_workflows.py --json --fail-on-unexplained
```

The route case exercises `skip` when an eligible open correction task exists and `revise` when correction work needs reopening or appending. It also routes preflight and immediate revalidation failures to stop before Tasker. The installed-consumer case copies the actual controller package to `.specify/flow-kit/`, executes the literal preflight command against task-file and parent-directory symlink aliases, and verifies the neighboring feature and active pointer remain byte-identical while the rendered blocked branch excludes Tasker. It also checks a changed task digest blocks the adjacent pre-dispatch revalidation. Production rendering of the semantic-review prompt uses a non-020 selected feature and its frozen specification text/digest. After Tasker, the separate main-controller semantic check and deterministic validator enforce exact finding/owner mappings, scope digest, history, and physical containment. These cases prove the deterministic installed route, not native agent availability.

The literal helper invocations run from the disposable consumer root with their JSON payloads on stdin. `task-revision-preflight` runs first with the selected feature and task paths; it returns task/specification text and digests only after active identity, symlink-free lexical ancestry, and physical containment checks. `frozen-scope.json` includes the approved selected-feature specification digest, exact findings/corrections, eligible task-owner mapping, and fixed Tasker owner. Rerun preflight immediately before delegation with both expected digests. `task-revision-payload.json` combines the original preflight snapshot, frozen scope, Tasker's structured result, and the separate main-controller semantic review. The same validation command must be exercised with an affirmative and a rejected semantic review:

```sh
python3 .specify/flow-kit/scripts/python/controller.py task-revision-preflight --project "$PWD" < task-revision-target.json
python3 .specify/flow-kit/scripts/python/controller.py task-revision-scope < frozen-scope.json
python3 .specify/flow-kit/scripts/python/controller.py task-revision-preflight --project "$PWD" < task-revision-recheck.json
python3 .specify/flow-kit/scripts/python/controller.py validate-task-revision --project "$PWD" < task-revision-payload.json
```

Expected evidence is a scope digest before Tasker, `state: ready` with `substantive_progress: false` for the valid revision, and `state: blocked` with `task-revision-semantic-review-required` for the rejected revision. The automated installed-package test constructs both payloads and verifies the literal commands using the actual package files.

Native evidence is separate. After T040 and T042, a main controller may request exact native `FlowKit-Tasker` dispatch for one controlled in-scope audit/revision case. Record the actual native response or exact availability error in `validation/tasker-native-dispatch.json`. Agent-definition presence, an assignment label, source metadata, a no-op executable or the deterministic route tests do not prove native availability. A no-change result is valid only when the exact native Tasker ran the bounded task audit and returned that result.

Readiness implementation adds focused `tests/test_readiness.py` covering FlowKit helper/report, actual production-rendered Analyzer correction routes and immediate Implement revalidation. Before counting it as validation, require the test module and at least one executed test; current absence is not a passing result.

```sh
test -f tests/test_readiness.py
~/.codex/venvs/skill-tools/bin/python -m unittest tests.test_readiness -v
```

Cases: checked quality; missing author correction; missing existing independent-review verdict; plan/task owner repair; authorized recorder update; reviewed future-obligation relocation with stable identity and pending status; unknown or mixed purpose; unavailable owner/Checker; stale evidence/digest; contradictory marker/metadata; incomplete coverage; out-of-scope decision; same unresolved findings; no progress; cap exhaustion; and a previously ready handoff invalidated before core startup. Exercise actual installed FlowKit helper commands and rendered correction/stop branches in disposable consumers. Assert that core source and installed/generated core helpers/templates remain unchanged, the core checklist scan sees zero unchecked preparation items only in ready cases, and future obligations stay pending outside `checklists/`. Do not run or require the superseded core `--readiness` flag.

A routine gap must take its declared owner correction and return to fresh artifact analysis and Readiness Checker assessment; writing a clean report alone is insufficient. Substantive review stays with FlowKit-Reviewer; the Luna/Medium Checker cannot supply missing review evidence. Persist each gap's stable ID, owner, missing evidence, disposition and any exact blocked resumption. Validate native Checker launch separately from deterministic fixtures, using the reviewed new definition without a per-run model override.

After focused implementation checks pass, run the existing broader suite once with actual runtime/source prerequisites and report every skipped integration case:

```sh
SPECIFY_BIN="$(command -v specify)" ~/.codex/venvs/skill-tools/bin/python -m unittest discover -s tests
```

## Disposable Consumer Validation

Use temporary initialized consumers and the existing unreleased snapshot path after source implementation. Existing snapshot test is runnable with the prepared selected CLI:

```sh
SPECIFY_BIN="$(command -v specify)" ~/.codex/venvs/skill-tools/bin/python -m unittest discover -s tests -p 'test_snapshot_validation.py' -v
```

For an operator-authorized manual prepared consumer:

```sh
consumer_dir="$(mktemp -d)"
specify_bin="$(command -v specify)"
(
  cd "$consumer_dir"
  "$specify_bin" init --here --force --non-interactive --integration codex --integration-options="--skills"
)
~/.codex/venvs/skill-tools/bin/python tools/catalog.py install "$consumer_dir" --development-snapshot
```

These setup commands write only the explicitly chosen disposable consumer. Verify bundle/workflow/extension versions, installed skill/controller ownership and all eight readable role identities before live work. Use the current source snapshot only after independently required source/pin compatibility is real. Readiness delivery keeps core unchanged and must prove compatibility with its existing gate; unchanged pins alone establish no improved FlowKit behavior. Roadmap direct-write compatibility remains unverified until its deferred cases run.

Consumer-preservation fixtures capture pre/post bytes for customized agents, unrelated definitions/config, project guidance, existing feedback and unrelated components. Install-missing/refresh preserve them; no reset is requested. Validate tracked native files and exact ignored `.worktreeinclude` payload in Codex-managed contexts. Correct only an evidenced missing propagation entry after an explicit visible project-config approval; do not silently add broad `.codex` copying or a setup script.

## Validation Delivery and Post-Closeout Release

T037 supplies the package used for Feature 020 verification through the existing development-snapshot installation path above. Record the unreleased status, source and package digests, component versions and pins, tested CLI, installed inventory, consumer preservation and actual compatibility results. An existing source-checkout refresh is useful dogfood evidence but does not alone establish the required disposable-consumer validation. Native availability and combined workflow results still require their own cases; snapshot installation does not complete them.

Production release packaging is a separate pending [post-Closeout activity](post-closeout-release.md). Feature verification, Converge and Closeout do not wait for production catalog generation or release tags. After Closeout and explicitly authorized Git integration establish the reviewed revisions, a separately authorized release pass checks the actual builder prerequisites, generates and validates the production catalog and archives, and tests installation of those released packages. It does not automatically push or publish, and development-snapshot results must retain their unreleased provenance.

## Native Context Matrix

Run through native Codex chats under operator direction, not a shell no-op or a planner-spawn substitute. Main controller owns the exact named requests and records all results according to [availability contract](contracts/future-session-availability.md). Do not change model/effort or dispatch assignments.

1. Prepare the existing checkout once, then open a future chat there; inspect discovery/inventory and request all eight exact native roles with bounded read-only probes.
2. Open a future chat in a prepared Codex-managed worktree; inspect tracked/ignored payload provenance and request all eight roles.
3. Create a new Codex-managed worktree from the prepared source with its first chat. Record whether payload presence before initialization is established or unknown, then request all eight roles.

The original exact names are Roadmap Agent, Specifier, Planner, Tasker, Reviewer, Coder, Code Reviewer and Wiki Curator with the `FlowKit-` spelling shown in the contract. After the additive Checker delivery, also request exact `FlowKit-Readiness Checker` in each of these same contexts and record three separate additional cases; its Luna/Medium source configuration is not effective-runtime proof. Cases require actual agent_type selection and returned response/error, not pane labels. Sequential probes do not authorize lifecycle cleanup/capacity changes. Preserve unavailable names, interface absence, native limits and not-tested cases individually; stop workflow work when a required assignment is unavailable.

First-chat failure remains a failed case even if a later fresh chat succeeds. Record the fresh-chat result separately and only claim a supported workaround if observed. Present-files/interface-absence is not missing installation. Effective model/effort/client version remains unavailable where not observed. The original twenty-four successes remain required, plus three separate exact Checker launches after its additive source delivery; partial execution is not averaged to passed.

## Combined Workflow Demonstration

Use one disposable uniquely mapped feature and the current compatible source installations. The operator separately invokes each selected workflow phase; do not auto-run them from this document or chain them because an earlier command succeeded.

- Explicitly activate the feature: expect correct pointer and unchanged planned/no-spec lifecycle without selection/pointer/status reconfirmation; independently verify mapping/bytes.
- Separately request Specify and required preparation phases; maintain same identity, legitimate product/governing decisions and author-versus-reviewer evidence.
- Separately request Analyze: expect clean current artifacts and readiness ready only after real preparation obligations are satisfied; future test/acceptance criteria stay pending.
- Separately request Implement: expect recomputed readiness and eligible startup without a generic future-evidence override. Stop the demonstration at evidenced startup unless more work is explicitly requested.

Retain a blocked variant with unresolved consequential authority or exact-agent unavailability: expect focused question/exact blocker, safe resumption and no unsafe effect/fallback; earlier successful results remain recorded. Use the actual approved governing contract and source/install evidence; neither a design amendment nor an earlier planning report passes a runtime test.

Within an authorized Implement run, exercise both a still-open correction task and an independently reviewed defect whose correction task is closed or absent. Expect exact FlowKit-Tasker dispatch, a bounded task revision preserving unrelated history, validated continuation and fresh independent code review, with zero routine reopening approval. Reject out-of-scope revisions, missing named assignments, invalid task diffs, no progress, repeated findings and cap exhaustion. Task-only edits are not completed implementation. Use production renderer/branch routes and actual before/after task evidence, rather than inspecting YAML shape alone (FR-023/SC-009).

## Evidence and Result Review

Write future portable `validation/observations.json`, `validation/cases.json` and a concise human summary according to [validation evidence](contracts/validation-evidence.md). Map all five historical IDs and all 25 requirements and eleven success criteria; link each current disposition to concrete cases/evidence or exact gaps. Preserve original reports/journal bytes.

Record component/source/package IDs, versions, coordinates/digests, CLI version, client identity/context or unavailable, preparation and actual result. Exclude personal host paths, secrets and raw transcripts. Review source/manual prompt agreement, owner/pin compatibility and per-area/combined/native failures independently. Local tests, exact launches, effective settings, publication/adoption and human acceptance remain separate. A result that could not run names its exact prerequisite/cause and does not count as complete.


## Implement Defect-Progress Validation

After FR-025/SC-011 is implemented, extend the existing controller, Implement task-revision and production-rendered route suites with an actual pre-pass baseline containing a selected open task and two independently recorded defects mapped to it. Resolve one defect in source and obtain a fresh independent review: the validated route must continue, the other defect and parent task must remain open, and no routine reauthorization is requested. This is local source/route validation, not a native-context matrix or user acceptance run.

Negative cases preserve an unchanged or recurring defect, renamed/omitted IDs, a finding discovered only after correction, unsupported task ownership, stale evidence, marker/report-only changes, ready-gate failure, unavailable exact agent, consequential scope decision and a final allowed pass requesting continuation. Require the same no-progress/cap stops, record historical source and outcome digests, and prove whole-task completion needs all its requirements satisfied. Do not modify old stopped-run records or installed copies to make the demonstration pass.


Automatic defect-closure helper regression command:

```sh
~/.codex/venvs/skill-tools/bin/python -m unittest tests.test_implementation_progress -v
```

The implementation baseline helper captures current source/ownership before coding. The progress helper validates a fresh native Code Reviewer result and returns namespaced task/finding resolution sets plus a next baseline. The controller supplies the immutable digest, persists historical pass evidence, and attaches the validated next baseline automatically; the operator does not perform manual ID comparisons or reapprove routine continuation. A copied-controller subprocess case proves one prior defect closes while its parent task remains unchecked. Source tests do not prove a live new-role launch, effective settings, installed consumer adoption or release delivery.


## Lifecycle Amendment Validation

This 2026-10-07 addition validates new Story 6/FR-026–FR-038/SC-012–SC-016 separately from original 49-task completion. Commands below for new helpers/tests/fixtures are **planned implementation deliverables** and must exist/run nonzero coverage before a passing result can be recorded. Their absence is not success. Current baseline validation can run; this planning pass does not execute runtime effects or claim implementation.

### Phase ownership and evidence boundary

Specify owns `planned→specced` after current authoring-quality and clarification checks, independent review, a current authored-ready roadmap brief, unique linkage, valid dependency closure, and no unsettled consequential decision. The later Complete header, plan/tasks, implementation, verification, and future acceptance are not prerequisites for this milestone. Implement owns `specced→in-progress` before any Coder dispatch; require current reviewed specification/plan/tasks, verified dependency closure, a current Readiness Checker assessment, an authorized eligible task scope, and every exact declared assignment. Close Out owns `in-progress→implemented` before the first roadmap debrief; require attributable full-scope completion, current convergence, required validation, an independent Code Reviewer assessment, and no buildable unresolved defect. Keep future verification, acceptance, and release obligations explicit and pending.

All three transitions use the approved phase-lifecycle policy hash and the independently versioned `flow-roadmap` owner interface at `>=0.3.0`. FlowKit validates the current source map and strict evidence, then asks the owner to prepare a read-only assessment. Rebuild and revalidate the exact proposal immediately before one adjacent owner write; independently inspect its actual discriminated receipt and current roadmap state before subsequent work. Equal or consistently advanced state does not get a duplicate event or a downgrade. Missing owner capability, stale/contradictory/ambiguous proof, missing recovery route, and failed or partial writes stop at the exact boundary. Recovery records only individually substantiated adjacent transitions at their true occurrence times; deferred or abandoned state requires focused operator resolution. The existing explicit `verified` gate remains separate after `implemented`; no lifecycle result implies Git integration, publication, or acceptance.

The manual-prompt fallback follows the same phase owner, evidence set, prepare → revalidate → owner write → independent receipt verification sequence. Check that the exact assigned native agent actually performed each delegated review; a role string inside JSON is not proof of native identity. Never substitute a generic agent, use ordinary roadmap delta mode for the milestone, or invoke a later workflow phase. The production-release handoff remains separate in [post-closeout-release.md](post-closeout-release.md).

### Prerequisites and source checks

Reconcile durable entry 020 outcome/scope/notes without changing its current status merely for planning; approve/deliver the runtime milestone/recovery contract and independent roadmap-owner source; generate Tasker-owned new lifecycle work and obtain fresh Analyze readiness. Inspect actual delivered workflow/controller/roadmap versions and hashes against the [plan](plan.md#delivery-prerequisites-and-risks). Use pinned Specify fork and skill-tools Python for skill validation. Prepared native definitions remain consumer-owned; no model/effort change or per-chat reinstall. Preserve original cases/history and pending acceptance/release IDs.

Run existing source checks after implementation and the new focused lifecycle modules:

```bash
PYTHON="$HOME/.codex/venvs/skill-tools/bin/python"
"$PYTHON" -m unittest discover -s tests -p 'test_phase_lifecycle.py'
"$PYTHON" -m unittest discover -s tests -p 'test_workflow_graph.py'
"$PYTHON" -m unittest discover -s tests -p 'test_workflow_paths.py'
"$PYTHON" -m unittest discover -s tests -p 'test_readiness_workflow_routes.py'
"$PYTHON" -m unittest discover -s tests -p 'test_snapshot_validation.py'
"$PYTHON" tools/validate_workflows.py --fail-on-unexplained
```

The new `tests/test_phase_lifecycle.py` and existing `tests/test_workflow_graph.py` and `tests/test_workflow_paths.py` are the task-owned lifecycle test modules (T054/T060). Require a printed nonzero test count from each discovery command and explicit LC001–LC015 coverage through the fixture harness (T061), not unittest's zero-discovery exit. The existing `tools/validate_workflows.py --fail-on-unexplained` command validates all current workflow projections and terminal paths. In the independent roadmap source run its documented baseline suite plus new phase-lifecycle/brief-contract tests, record exact commands/counts and source coordinates. Do not run tests against manually patched installed payloads. Current fixture orchestration uses unittest and existing development snapshot mechanisms; no new tool/dependency is introduced.

### Disposable installed matrix

Use the existing disposable initialized consumer setup and supported development snapshot from this guide, including the new independent roadmap source version. The new `tests/test_phase_lifecycle.py` fixture harness owns a temporary initialized consumer and provides the runtime packet/template files; fixtures substitute current SHA-256 values for the [contract](contracts/phase-lifecycle.md#command-interface) aliases. Planned `tests/consumer-fixtures/workflow-improvements/phase-lifecycle-cases.json` is the canonical baseline and LC001–LC015 fixture input assigned to T053/T061; the harness materializes its snapshots and packets in the temporary consumer. Never use the real Feature 020 roadmap as a disposable mutation target.

For a fixture's read-only boundary:

```bash
python3 .specify/flow-kit/scripts/python/controller.py phase-lifecycle --project "$PWD" < validation/lifecycle-request.json
python3 .specify/extensions/flow-roadmap/scripts/python/phase_lifecycle.py evaluate --project "$PWD" < validation/lifecycle-request.json
```

Invoke apply only through the authorized modeled roadmap Write node or the explicitly authorized manual fixture path. The controller/test harness supplies an actual trusted fixture decision and verifies event/status hashes, not an `authorized` input flag. Source fixtures may mock agents only for routing tests; these outputs never become live independent review evidence.

| Cases to run | Procedure and expected result |
|---|---|
| LC001–LC002 | Prepare Draft with real current independent authoring-ready/brief proof; record specced only. Remove or stale each proof; retain planned with exact blocker, even with Complete/header/checklist/command success. Assert legacy brief booleans are unchanged and incompatible mixed mode rejected. |
| LC003–LC004 | Prepare reviewed eligible scope, verified dependencies and Checker/fresh readiness; trace write+verification before first Coder. Vary each dependency/readiness/input/role/scope condition; assert no state effect and no Coder. |
| LC005–LC006 | Bind convergence/completion/code review to amended exact scope; retain future acceptance/release IDs, record implemented before debrief. Substitute older-scope proof or unresolved defect; block effect/debrief despite checked tasks/Complete. |
| LC007 | Reinvoke each owner at equal and later consistent states; compare events/state/unrelated bytes/verification provenance. No event or downgrade. Validate event-free no-op with required assessment identity/retained status/equal observed digests; reject injected `effect_id`, `occurred_at`, actual/proposed transition fields, nulls and a changed/unobserved final digest. Remove required proof or add contradictory advanced proof; assert blocker/focused decision. Selection itself makes no milestone. |
| LC008–LC011 | From stale planned Close Out fixture, substantiate all three edges independently; record current dated specced, in-progress, implemented in order without Coder replay. Remove one edge's proof, introduce competing mapping/authority, or remove route/version; stop at exact unsupported effect and preserve prior actual effects. |
| LC012 | Supply deferred, abandoned, requested regression, scope/product and constitutional/authority conflicts; capture one focused main-task question per disputed effect. Unanswered/declined decisions cause zero affected mutation; explicit answers revalidate and cannot override missing proof. |
| LC013 | Inject writer success then later step failure, authoring success then write failure, and receipt persistence failure after atomic commit. Inspect actual committed state/recording outcome, retain partial reports, retry with fresh proof; no rollback or duplicated event. Validate definitely not-applied with proposed identity and optional truly observed final digest; reject actual event/time, copied candidate/old hashes and null placeholders. Validate applied/failed with actual event time and verified before/after hashes plus `record_error`; reject classification as not-applied solely because persistence failed. Recovered applied requires original event time/identity and `recovery_evidence`, never retry time. |
| LC014 | After prepare change each roadmap/pointer/dependency/governance/config/evidence input; revalidate/apply rejects stale packet before unsafe effect. Repeat material verification patch change after prior approval; require new exact gate. Simulate uncontrolled editor race; report observed/indeterminate state without blind rewrite. Validate indeterminate proposal identity with no actual occurrence/transition identity or verified final digest; accept omission of unavailable readback, allow a separately observed uncertain readback only as `observed_roadmap_sha256`, and reject nulls or invented/candidate final digests/timestamps. |
| LC015 | After implemented exercise approve, return and defer at existing verified gate. Record verified only for current exact approved patch; return/defer preserves implemented and pending future obligations. Assert zero Git/publication/acceptance effect. |

### Live and manual boundary checks

Separately request each owning workflow in prepared isolated demo projects after source/fixture review. Capture actual required native preflight, fresh role children, current evidence, roadmap effect receipts and explicit verification question/answer. This guide does not invoke the next workflow. Execute the manual-prompt path under its explicitly authorized fixture scope with the same read-only checks, owner Write and decisions; compare event order and blockers with native cases. Missing native assignments yield supported stop/manual resumption without generic substitution. Configuration and dispatch results do not claim effective model/effort or universal client behavior.

Store new portable lifecycle cases and summary additively under feature validation, using the [validation record contract](contracts/phase-lifecycle.md#validation-contract). Map LC001–LC015 to every Story 6 scenario, FR-026–FR-038 and SC-012–SC-016. Record zero-test/environment/absent-owner cases failed or not-tested with exact gap, preserve all historical cases, and require independent review of real source delta and validation before claiming amended convergence. Rebuild/refresh only the authorized development snapshot; production release and feature acceptance remain separate pending obligations.

## Requested Scope Validation

This prospective Story 7 guide covers FR-039–FR-048/SC-017–SC-022 separately from LC001–LC015 and historical 49-task convergence. Current 51/67 completion reflects T050/T051's actual administrative alignment/policy decision, not delivered continuation behavior. Do not repeat that approved policy or mutate the real roadmap to create a test. Tasker adds scoped implementation/validation work; current independent Analyze/readiness is required afterward.

### Source and installed prerequisites

After source implementation, run focused suites using the prepared skill-tools interpreter:

```bash
PYTHON="$HOME/.codex/venvs/skill-tools/bin/python"
"$PYTHON" -m unittest discover -s tests -p 'test_implementation_scope.py'
"$PYTHON" -m unittest discover -s tests -p 'test_implementation_progress.py'
"$PYTHON" -m unittest discover -s tests -p 'test_implement_task_revision.py'
"$PYTHON" -m unittest discover -s tests -p 'test_controller.py'
"$PYTHON" -m unittest discover -s tests -p 'test_workflow_graph.py'
"$PYTHON" -m unittest discover -s tests -p 'test_workflow_paths.py'
"$PYTHON" tools/validate_workflows.py --fail-on-unexplained
```

`tests/test_implementation_scope.py` and `tests/consumer-fixtures/workflow-improvements/implementation-scope-cases.json` are planned new deliverables. Require nonzero printed counts and all 15 fixture IDs. The existing test modules above are real paths, to be extended rather than replaced with permissive shape checks. Install/refresh only a supported disposable initialized consumer with the exact delivered new Implement/controller/roadmap pins; record actual CLI/version/source/digests. Missing owner support affects runtime-consumer cases, while source-work cases inspect a permitted fixture owner checkout before work. Snapshot matching and preservation are mandatory; production tags remain post-closeout.

### Fifteen-case Story 7 matrix

The harness materializes actual request/baseline/eligibility/source/readiness packets from fixture definitions and invokes production rendering plus proposed installed `implementation-scope`, `implementation-eligibility`, `implementation-activation`, `implementation-route` and additive progress operations. Exercise the actual new Implement-only loop mode and the unchanged generic function on its post-source branch; other workflows/default callers retain their existing semantics. These operations are not yet delivered; absent modules or zero discovery produce an exact failed/not-tested result, never a pass. Known finding/source preimages, actual independent task fulfillment proofs, declared graph/node membership and the append-only session/attempt history must be captured before simulated correction. Administrative proof discharges request accounting but is absent from substantive progress IDs. Adversarial payloads vary only the tested field. Deterministic fixture/native-stub outcomes are routing evidence, not actual live independent review or effective settings.

| Case / Story 7 scenario | Required evidence and procedure | Expected boundary | Requirement / criterion |
|---|---|---|---|
| SI001 / AC1 | Full request includes all current unfinished IDs, some initially blocked; compare trusted snapshot to eligibility generated subset | No ID dropped; separate prerequisite blockers retained | FR-039–FR-041, SC-017 |
| SI002 / AC2 | Freeze T050/T051/T052 plus every other fixture-scoped ID; execute one declared preparation session, substantiate actual decision and requirement-complete independent administrative proofs; verify source unchanged, count session 1/attempt 0; assess actual owner source/access/rules/route, readiness and fresh T052 preimage; inspect declared preparation-to-first-source adapter and pre-dispatch start records | T050/T051 discharge accounting but resolve no implementation ID; same run starts T052 with session 2/attempt 1, no generic post-source predicate before first attempt and zero new routine approval; no missing-output self-prerequisite, source must be permitted by owner rules | FR-040–FR-043, FR-046, SC-018–SC-020 |
| SI003 / AC3 | Trusted explicit subset T050/T051, T052 later eligible; validate both administrative-prerequisite proofs against actual answers/effects and all requirements, plus exact Tasker tracking; compare dispatch/source/history; inject asserted approval, reviewer-role string, marker-only and partial-proof variants | Subset completes administratively with zero substantive_progress and implementation_completed_task_ids empty; T052 outside/unexecuted; forged/incomplete proof fails accounting, no feature implementation/acceptance claim | FR-039–FR-040, FR-047, SC-017, SC-021 |
| SI004 / AC4 | Propose new task/effect beyond actual request; capture focused main-task decision; unanswered and answered variants | No disputed effect before actual decision; answer revalidates, cannot waive stale proof | FR-039, FR-043, FR-045, SC-021 |
| SI005 / AC5 | Known defect and initially blocked task frozen; resolve defect, activate later task with fresh preimage; compare all original baseline bytes/digests/history | Original scope/defect bytes immutable, new activation distinct and task identity stable | FR-041, FR-044, FR-047, SC-019 |
| SI006 / AC6 | Resolve one prior defect and discover another after correction; include unchanged third finding; inject rename/omission/retroactive-before variants | Only actual prior resolution credit; new/unchanged findings remain open; forged baseline rejected | FR-041, FR-044, SC-019 |
| SI007 / AC7 | Pending consequential input in declared preparation node via same child; actual main-task answer, independent administrative fulfillment, new eligibility and all common guards; inspect rendered node order, consumed session/history and source-attempt state; repeat unchanged preparation, counterfeit input and attempted undeclared-node variants | Same child resumes without new session; first source route only at attempt 0; repeated preparation without real prerequisite/input fulfillment blocks preparation-no-progress; administrative event zero code credit and never re-enters a source-stalled run | FR-042–FR-043, FR-045, SC-018–SC-020 |
| SI008 / AC8 | Newly dependency-ready task with missing/stale spec/task/checklist/independent readiness digest; exercise helper+Checker disagreement | Exact readiness stop before Coder, safe Analyze resumption; no approved-answer override | FR-042, FR-045, SC-020 |
| SI009 / AC9 | Existing scoped external task, permitted actual fixture checkout/access/AGENTS/source route/task authority and current readiness | Same invocation executes only owner-permitted source effects; ownership does not exclude request | FR-046, SC-018, SC-020 |
| SI010 / AC10 | Vary absent checkout, access failure, owner authority conflict, missing source route, unsafe effect; compare runtime capability as deliverable-only variant | Exact affected source blocker/resume; no fallback/blanket override; missing intended runtime output alone does not block source work | FR-045–FR-046, SC-020 |
| SI011 / AC11 | Record source attempt before dispatch, test successful/no-effect/failed-dispatch/question-stopped attempts; after each vary decision/checklist/marker/report/rename-only changes, arbitrary proof path, new eligible task, erased attempt, empty replacement baseline and first-pass exemption flag; call actual generic predicate with genuine pre-attempt substantive assessment | Attempt cannot return to preparation/first-source; zero substantive resolution blocks no-progress with unresolved work, no new-eligibility loophole; forged history and administrative IDs as resolved are rejected | FR-043–FR-045, SC-019–SC-020 |
| SI012 / AC12 | Mix preparation and source sessions totaling five, including question-stopped/failed-dispatch variants; request continue with source ordinal below five; vary answer/eligibility/branch/reassessment/rewound counter; separately test valid fifth-session terminal completion | One monotonic global counter: iterations_used = coder_sessions_started = 5, no sixth dispatch/refund/reset; actual source-attempt count/effects/remaining work retained; valid terminal completion allowed, further continuation stops loop-cap-exhausted | FR-043, FR-045, FR-047, SC-020–SC-021 |
| SI013 / AC13 | Some scoped tasks completed; another individually blocked while another eligible; then introduce global readiness failure or later partial failure | Continue safe other work only absent common blocker; full requested receipt preserves effects/failures/pending, no false scope exhaustion/completion | FR-040, FR-042, FR-045, FR-047, SC-018, SC-021 |
| SI014 / AC14 | Child/generated/external output proposes narrower/larger scope; tamper digest/history/task descriptions | Retain actual trusted request; record recommendation only; stale/forged identity rejected | FR-039–FR-041, FR-047, SC-017, SC-019 |
| SI015 / AC15 | Required exact assignment absent or actual consequential question unanswered; preserve same child's pending state | Stop affected coding with named gap/resume; earlier progress cannot invent fallback/answer | FR-043, FR-045, FR-047, SC-020–SC-021 |

FR-048/SC-022 apply to every SI case and the source/package/manual reconciliation. Cases are one-to-one with all 15 acceptance scenarios; variants must retain per-variant outcomes rather than hiding initial failures. Record exact criterion and proof for every pass/stop; local helper success alone cannot substantiate actual operator intent/native review.

### Evidence reconciliation and manual/live limits

Add portable `validation/implementation-scope-cases.json` and `validation/implementation-scope-summary.md` with required common ValidationCase fields from the [data model](data-model.md#feedback-and-validation-results), including requirements, expected/observed/result, component provenance, evidence hashes and limitations. Scope-specific fields are `requested_task_ids`, `eligible_task_ids`, `pending_task_ids`, `completed_task_ids`, `administrative_prerequisite_ids`, `implementation_completed_task_ids`, `fulfillment_proof_digests`, `outside_task_ids`, `scope_sha256`, `before_baseline_sha256`, `activation_sha256`, `review_sha256`, `after_baseline_sha256`, `iterations_used`, `coder_sessions_started`, `source_attempts_started`, `execution_history_sha256`, `substantive_progress`, actual decision references, blocker/resume and observed effects. Include proof completion_kind and requirement coverage per task, declared preparation/source branch/node, actual pre-dispatch events, generic predicate previous/current substantive assessments and original/predecessor history hashes plus actual relative owner source coordinates. Digest unavailable/unobserved stays an explicit gap, never invented null/current hash substituted for before evidence.

Run the authorized manual-prompt fixture path with full and restricted scope, same decisions/readiness/budget and source/owner checks; compare with production modeled routes. Separately authorized live execution records exact available native assignments, actual same-child input and independent review. Record effective settings/client/pane observations only if directly observed. External real checkout not inspected, unavailable live capacity, unrun manual cases or old snapshots are exact not-tested limits. Independent review must map every new requirement/scenario to actual source/evidence and preserve old LC/native/feedback records. No future case result is asserted by this planning pass; no workflow phase, source effect, Git or acceptance is invoked here.

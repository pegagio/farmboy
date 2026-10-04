# Feature 017 Session Handoff

Resume Feature 017, FlowKit Agent Configuration and Consumer Delivery, on the existing `specs/017-flowkit-agent-configuration` branch. Read `spec.md`, `plan.md`, `research.md`, `tasks.md`, both contracts, and the latest sections of `validation.md` before acting. The active pointer already selects this feature. This is a checkpoint of incomplete work, not feature acceptance.

## Current Close Out Disposition: 2026-10-04

The operator approved and applied the exact lifecycle repair: roadmap entry 017 is `implemented`, roadmap version `1.18.3`; verification remains unapproved; the declared Close Out status step has marked the specification Complete with the operator-directed follow-up qualification retained. The documented mise catalog refresh failed because its selected Python lacked the existing PyYAML dependency; the skill-tools retry succeeded in its separately recorded prepared environment.

The operator explicitly deferred DEP017-01 to a follow-up feature and requested documentation now. See [follow-up.md](follow-up.md), [the authoritative scope qualification](spec.md#operator-directed-follow-up-disposition), and [current evidence](validation.md#close-out-discovery-and-approved-follow-up-deferral). Prior zero-gap statements are qualified: no remaining nondeferred buildable work is identified, while the advertised runtime setup/provisioning gap remains unresolved. Preserve all 44 task markers and prior native/test limitations. No numbered follow-up feature, runtime solution, environment change, verification, acceptance or Git integration is authorized by that deferral.

## Final Resume Status: 2026-10-04

The authorized resume is complete: all 44 tasks are checked, including the two reporting corrections T043/T044 appended by core Converge. Independent exact `FlowKit-Reviewer` and `FlowKit-Code Reviewer` assessments are clear. The core Implement/Converge loop ended with `converged`; the final Converge pass left `tasks.md` unchanged. See [final validation](validation.md#final-core-convergence-result) and [native dispatch evidence](native-dispatch.json).

All eight exact native readiness launches succeeded without substitutions or per-run overrides. Effective model/effort remains explicitly unverified. Accepted support evidence, unavailable desktop version, source-project registry matched to disposable installed defaults, and the inherited native Specify transport failure remain documented. Final checks passed 55 focused tests and 158 full tests with one environment-dependent class skipped. Codex CLI is currently `0.160.0`; the earlier `0.157.1` evidence remains historical. No commit, push, merge, release, roadmap verification or acceptance occurred. Any such next action still requires explicit operator authorization.

The checkpoint narrative below is retained as historical context; its unfinished-task and unavailable-role statements are superseded by this final status.

## Objective

Finish all outstanding tasks and reach verified convergence. Run the core `$speckit-implement` for remaining work, then `$speckit-converge`. If convergence appends tasks, implement those tasks and repeat. Preserve existing task IDs, completion markers, scope and consequential human gates. Do not invoke another FlowKit workflow automatically. No commit, push, merge, release, roadmap verification or acceptance is authorized by this handoff.

## Current State

The eight roles now have exact `FlowKit-` names, canonical defaults in `agents/flow-kit/`, matching project-local `.codex/agents/flowkit-*.toml` files, approved explicit settings and structured question/blocker contracts. All 49 active delegated assignments use the renamed identities. The catalog implements deterministic packaging, validated default caching, install-missing, explicit reset-one/all and consumer-preserving refresh/removal. Installation guidance and coordinated snapshot versions are updated: bundle `0.14.0`, controllers `0.6.0`, agents `0.1.0`. Independent extensions retain their pinned artifacts. Nothing is published.

Approved settings remain:

| Roles | Model | Effort |
|---|---|---|
| Roadmap Agent, Wiki Curator | `gpt-6.1-sol` | `low` |
| Specifier, Planner, Reviewer | `gpt-6.1-sol` | `high` |
| Code Reviewer | `gpt-6.1-sol` | `medium` |
| Coder, Tasker | `gpt-6-luna` | `high` |

Thirty-six of 42 tasks are complete. T017/T037/T041 require independent configuration/instruction assessment. T033/T040/T042 require all-eight exact native dispatch checks and separate observed effective-setting results or explicit observation gaps. Both readiness checklists are fully checked; these quality checklists do not establish implementation acceptance.

## Remaining Work and Blocker

The previous chat loaded the old unprefixed registry. Native launches of `FlowKit-Reviewer` and `FlowKit-Code Reviewer` failed with `unknown agent_type` before creating a child. That chat's convergence goal was marked blocked after three consecutive turns with this same condition. This fresh session must confirm the renamed project agents are loaded. Do not substitute generic or old-name roles, supply per-run model/effort overrides, or repeat already accepted pair-support tests to bypass exact selection.

Use the exact assigned FlowKit review role for independent assessment of all eight instruction/settings diffs; the author cannot independently review its own work. Resolve attributable findings through eligible tasks and record the independent result. Use the existing installed-controller probe/dispatch procedure in a disposable initialized consumer with coordinated source snapshot versions to check all eight exact names without entering a later workflow phase. The source checkout's installed controller inventory was not refreshed and may still name old roles; use the catalog path rather than editing installed copies manually.

Native field/value support is already satisfied: accepted Feature 015 desktop observations established agent-file loading and Luna/high; three bounded Sol availability probes requested low/medium/high, and the operator confirmed all three model/effort indicators in the desktop UI. This supports the settings, not exact dispatch of the eight renamed roles. No additional screenshots or repeated field/pair probes are needed. Unobservable effective settings must remain unverified; configuration contents, labels and no-op transport are not equivalent to live role selection.

## Validation and Limits

The last source/disposable agent-delivery discovery run passed 154 tests with one environment-dependent class skipped. Focused final checks passed 51 tests; workflow validation reported zero unexplained terminals. Tested Specify was `1.0.10.dev0+pegagio.2`, Python `3.11.16`, and Codex CLI `0.157.1`. Desktop app version was not captured. Snapshot source coordinates identify the pre-checkpoint base revision plus content digests; do not treat a base commit alone as the complete snapshot content.

The skipped legacy native `BundleLifecycleTests` class was separately enabled using the pinned roadmap/wiki archives. That expanded run executed 153 tests and had one failure: native Specify reached Clarify's `assess-clarification-after-session` prompt and reported `Cannot dispatch prompt: integration None CLI not found or not installed.` The source prompt omitted integration before Feature 017 as well. Explicit integration input did not fix it. The ineffective fixture change was removed, and the failure remains recorded. Do not describe the expanded run as green or change unrelated workflow/probe behavior merely to suppress it. The direct FlowKit controller path and generic native CLI transport are separate evidence categories.

Use the existing skill-tools Python environment for skill validation; do not install dependencies or change environments without the required approval. Useful commands from the repository root are:

```sh
PYTHONPATH=tests SPECIFY_BIN="$(mise which specify)" "$HOME/.codex/venvs/skill-tools/bin/python" -m unittest discover -s tests
"$HOME/.codex/venvs/skill-tools/bin/python" tools/validate_workflows.py --fail-on-unexplained
git diff --check
```

Read the environment requirements in `tests/test_bundle_lifecycle.py` before enabling the skipped class. Keep results and any new evidence portable: no personal names, host paths, raw transcripts or secrets in project artifacts. Retain staged/checkpointed feedback and wiki provenance. Optional roadmap/wiki hooks remain operator-controlled. Finish with an honest task and convergence audit, preserving explicit gaps until evidence resolves them.

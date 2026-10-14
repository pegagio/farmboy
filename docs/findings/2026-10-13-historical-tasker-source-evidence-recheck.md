# Historical Tasker Source Evidence Recheck

Feature 023's fifth source session exposed an Implement evidence lifecycle defect: the retained Tasker successor chain contains source-file witnesses that were current when tracking occurred, but the scope adapter rereads them after a later authorized task changes those files. The current guard blocks correctly for the supplied records; the workflow needs a reviewed contract for immutable tracking witnesses and separately current source proof. This report proposes no guard relaxation or roadmap amendment.

## Table of Contents

The report records the failed continuation and preserves its recovery boundary.

- [Observation](#observation)
- [Cause and Ownership](#cause-and-ownership)
- [Expected Behavior and Regression Cases](#expected-behavior-and-regression-cases)
- [Evidence](#evidence)
- [Recovery Boundary](#recovery-boundary)
- [Authorized Resolution](#authorized-resolution)

## Observation

Run `9a496f02-51c0-4ac0-87fd-a2b92f3a93d0` retained its original Feature 023 scope and consumed five source attempts and five Coder sessions. T008 activated with the current preimages of `tests/test_controller.py` and `tests/test_workflow_paths.py`, then changed those files within its reviewed ownership. Earlier Tasker results had included those same source paths as evidence for T002 and T003 tracking.

The main controller's `implementation-history` request to record the completed fifth child returned `task-tracking-evidence-stale`. It wrote no outcome event. The fifth session and attempt remain consumed, and the child's actual source result is preserved separately. No historical hash, successor, marker, source file, or counter was restored or rewritten to make validation pass.

| Historical witness | Retained SHA-256 | Later authorized owner |
| --- | --- | --- |
| `tests/test_workflow_paths.py` | `52f7bcd646a7a19c7e990a0a79f08676f3d74888d4e7095d8226f697d1bfad17` | T008 |
| `tests/test_controller.py` | `e39e45b1e706d07c1fe02fa938aaab31992b24e3a3936fa6b7bab18c2573df51` | T008 |

Both retained hashes match the corresponding T008 before-source copies and activation preimages. The later byte changes do not by themselves prove regression or forgery; current task fulfillment still needs fresh independent source review.

## Cause and Ownership

The main controller retained the native Tasker results with mutable source references. The structural successor validator accepted the append-only marker transition. Later, `_implementation_scope_binding` in [the installed controller source](../../controllers/farmboy/scripts/python/controller.py) rereads every historical `tasker_result.evidence` and `reviewer_result.evidence` path against current bytes, not just the current completion proof.

Using immutable handoff artifacts when each successor is created could avoid this particular failure. That does not justify rewriting an already retained chain. The workflow currently lacks an enforced evidence lifecycle contract that distinguishes immutable historical tracking witnesses from current task proof. A later fix must decide whether to enforce immutable witness capture, add explicitly bound historical source preimages, or combine both. Removing current checks globally is not a proposed fix.

This is separate from [the first-correction continuation stop](2026-10-13-implement-first-defect-correction-stop.md). Feature 023's historical-proof and connected-trace coverage is relevant to reproducing the defect; its eventual implementation owner remains an operator decision. No feature activation, roadmap status change, or general continuation-policy change is implied.

## Expected Behavior and Regression Cases

A later legitimate task may change a source file cited by an earlier task without invalidating an independently bound historical tracking event. The current task proof must still be checked against current files.

- **Valid overlap**: Complete and track one task, retain its immutable evidence, activate a later task on the same file, change source, and successfully record the later session outcome without changing earlier digests.
- **Current proof**: Reassess the earlier requirements when needed; a new source regression cannot inherit stale completion credit.
- **Historical integrity**: Forged, altered, missing, unbound, replayed, or cross-scope records still block. A copied source file alone does not establish prior trust.
- **Evidence contract**: Reject or explicitly snapshot mutable witness references before a successor becomes durable; do not discover the contract conflict only after later effects.
- **Accounting**: Failed outcome recording does not reset or refill the consumed session and attempt counters. Recovery appends an actual completion observation only after the original chain is safely validated.
- **Authority**: Retain the original roadmap effect and receipt; perform no repeated owner write, Git integration, or feature acceptance.

## Evidence

The installed Implement workflow and controller package are version `0.9.1`. The normalized installed workflow digest is `419a55e85f8b6b1c7df2b59c07d2ce3a79e6bf3c73282053a4af131d9f460ca1`; the installed development-snapshot controller package digest is `d835835c552594bffe977b9953b5aeea28ca59559a2343786cf8275d4514e4ff`. Source coordinates are `pegagio/farmboy`, commit `54b394e` plus the inspected dirty worktree. Runtime is Python 3.11.16 with PyYAML 6.0.3 and Specify CLI `1.0.10.dev0+pegagio.2`.

Feedback observation `implement-historical-tasker-evidence-live-recheck-feature023-20261013` is captured in `.specify/workflow-feedback/observations.jsonl` for later intake.

- **Retained successor chain**: `.specify/farmboy-controllers/runs/9a496f02-51c0-4ac0-87fd-a2b92f3a93d0/route-entry-pass5.json`.
- **Before-source copies**: The same run's `T008-pass5-before-test_controller.py` and `T008-pass5-before-test_workflow_paths.py`.
- **Ready activation**: The same run's `T008-pass5-activation.json`.
- **Failed append**: The same run's `source-outcome-pass5.json`.
- **Actual source result**: The same run's `source-result-pass5.json`.
- **Independent partial-source assessment**: [Pass 5 review](../../specs/023-workflow-branch-validation-controller-integration/validation/implementation-code-review-pass5.json).
- **Original history**: `.specify/farmboy-controllers/implementation-history/9a496f02-51c0-4ac0-87fd-a2b92f3a93d0.json`.

## Recovery Boundary

At the original stop, the fifth child had completed but its outcome event had not been appended. Preserve the original scope, complete successor chain, pre-effect bindings, current source delta, original applied start receipt, and all consumed sessions and attempts. Do not relabel history without an actual append, replay source work, restore older source bytes to pass a hash check, or reconstruct historical trust from today's files. Recovery requires independent validation of original records and current proof; budget authority is a separate decision.

## Authorized Resolution

The operator explicitly authorized this controller repair and continued Feature 023 with an extended budget. The controller now accepts an independently retained, scope-bound historical prefix count and digest, validates its full append-only marker structure, and preserves its original evidence hashes without rereading historical source bytes. New suffix evidence remains current. Current eligibility now independently checks assessment, classification, fulfillment, source, validation and review-file evidence, including outside-scope prerequisite proofs. A stale current proof still blocks even with valid historical receipts.

The original prefix was recovered from the unchanged pre-effect `route-entry-pass5.json` whose digest was already anchored in independently retained execution history. No successor or historical source hash changed. The fifth completion outcome then appended through the installed production adapter, preserving the first fourteen events and counters at five sessions and five attempts.

The run's separately retained operator-authorized ceiling is twenty sessions and attempts, replacing its default five for this run alone. The receipt binds original scope, history prefix, consumed counts, authority evidence and an independently retained digest. The generic default remains five; no-progress checks remain unchanged. Both new bindings use canonical UTF-8 JSON without ASCII escaping. Native independent review verified the repair, stale-current-proof rejection, Unicode witnesses, six-attempt routing/capture, and counter preservation.

Delivery used the ownership-checked controller-only development-package refresh, version `0.9.1`, digest `68255ae44355adf633230ac9e25e3d376a2cd34c44f81b30c0f36b38949e774c`. The retained installed workflow definition remains unchanged. The same run's `historical-prefix-recovery.json`, `operator-budget-extension.json`, `authorized-controller-refresh.json`, and `source-outcome-pass5-recovered.json` record recovery. The original roadmap receipt and ledger digests remain unchanged; no owner write repeated. This resolution does not establish feature completion or acceptance.

The ninth independent review exposed a wording regression in the source workflow's capture prompt: its optional recovery fields appeared in the sentence parsed as the eight required fields. Separating the optional-field instruction into its own sentence preserved forwarding semantics and restored the existing supported capture parser without changing the installed active workflow. The snapshot rerun then reached the strict current-proof check and rejected a synthetic Reviewer label used as a file reference; the pending connected-harness tasks must materialize contained evidence rather than weaken this check. [Pass 9 review](../../specs/023-workflow-branch-validation-controller-integration/validation/implementation-code-review-pass9.json) records both observations. This maintenance correction earns no feature-task or source-progress credit.

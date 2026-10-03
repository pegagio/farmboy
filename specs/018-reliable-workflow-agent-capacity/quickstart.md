# Quickstart Validation: Reliable Workflow Agent Capacity

This guide defines agent-owned validation to run after implementation. It contains no claim that Feature 018 behavior already exists. The implementation agent prepares disposable consumers, configures test fixtures, separately dispatches the selected native workflows, executes scenario inputs/assertions, and captures evidence within the authorized test scope. The operator may perform one initial Codex project setup if the client requires it; no manual test matrix or repeated command dispatch is assigned to them. Genuine consequential decisions remain human gates. Preserve actual source/client provenance and never change this source checkout's consumer configuration for a test.

## Contents

Follow baseline checks, disposable lifecycle checks, and native acceptance in order.

- [Prerequisites and Baseline](#prerequisites-and-baseline)
- [Disposable Installation and Upgrade](#disposable-installation-and-upgrade)
- [Native Sequential Acceptance](#native-sequential-acceptance)
- [Failure and Preservation Matrix](#failure-and-preservation-matrix)
- [Completion Evidence](#completion-evidence)

## Prerequisites and Baseline

Use the pinned Specify fork, configured mise tools, a client capable of exact custom-agent selection, and consumer-owned agent definitions. The feature does not deliver Feature 017 agent configuration. No-op Codex proves dispatch only.

Run from the source checkout:

```sh
mise exec -- specify --version
codex --version
~/.codex/venvs/skill-tools/bin/python -m unittest discover -s tests -p 'test_controller.py'
~/.codex/venvs/skill-tools/bin/python -m unittest discover -s tests -p 'test_catalog.py'
git diff --check
```

Expected: Specify `1.0.10.dev0+pegagio.2`, recorded actual CLI/client version, baseline tests pass. After implementation also run the proposed `test_capacity.py` suite, affected lifecycle/snapshot suites, and full available suite. New suite commands are not proof until those files exist.

## Disposable Installation and Upgrade

Create a system-temporary project. Initialize only that disposable project:

```sh
consumer_dir="$(mktemp -d)"
specify_bin="$(mise which specify)"
(
  cd "$consumer_dir"
  "$specify_bin" init --here --force --non-interactive --integration codex --integration-options="--skills"
)
PATH="$(dirname "$specify_bin"):$PATH" python3 tools/catalog.py install "$consumer_dir" --development-snapshot
PATH="$(dirname "$specify_bin"):$PATH" python3 tools/catalog.py refresh "$consumer_dir" --development-snapshot
```

Expected after implementation: one notice for each operation, packaged guide available, unchanged consumer config bytes. Configure absent, compatible, different-value/alias conflict, malformed, and client-unsupported cases in separate temporary fixtures. Capture bytes before and after install, refresh, induced partial failure, and removal; preserve existing tests' ownership collision checks. Snapshot mode never updates checked-in release archives or metadata.

The agent applies the documented merge in the disposable consumer only, configuring candidate four before the native test chat starts. If existing context must reload, the agent uses a supported context/reload mechanism; request only one initial project setup if tooling requires human setup. Capture trust/override/effective-setting evidence without exposing unrelated configuration. Use verified driver-owned protected occupancy children to obtain a documented constrained available budget in that same persistent chat, measuring behavior rather than assuming the setting is effective. Keep those children protected through their test interactions and complete/release them safely afterward. Neither constrained availability nor candidate four is called tested until its native results pass. Unavailable automation is a specific blocker rather than a request for manual scenario execution.

For removal preservation, use the supported catalog route from the source checkout:

```sh
PATH="$(dirname "$specify_bin"):$PATH" python3 tools/catalog.py remove "$consumer_dir"
```

Expected: only unchanged owned components are removed; consumer config, feedback, run summaries, lifecycle ledger, and retained outputs remain.

## Native Sequential Acceptance

The agent prepares a small synthetic feature and consumer-owned exact agent definitions in the disposable project using `tests/consumer-fixtures/agent-capacity/scenarios.json`. The main-task driver separately invokes Plan, Tasks, and Analyze and Remediate within the authorized validation scope, with additional invocations as necessary to exceed twelve terminal children; no product workflow launches another workflow. These are agent-executed test invocations, not actions performed by this planning guide or commands assigned to the operator. Predetermined synthetic question/response pairs may exercise protected-child answer relay; they are test-actor inputs, not human verdicts. Unexpected genuine product questions or consequential decisions stop at their existing gate without assigning manual testing labor.

At a constrained documented child budget, record at least three completed workflow invocations, more than twelve terminal children, and two necessary release cycles. Preserve real child outputs and independent durable-artifact assertions. Verify every eligible child is processed before the next executable step. Seed a proven eligible child from a prior same-chat invocation; verify entry cleanup and no cross-chat cleanup. Keep one real child awaiting an operator answer and prove it remains available for the same-child answer relay.

The agent separately forces a capacity launch failure with eligible completed children, verifies one sweep and one exact retry, and verifies a fresh successful launch after accepted native release. Confirm the actually tested close/archival adapter retains outputs. Release completed occupancy fixtures safely and repeat the sequential scenario with unconstrained available slots in the same candidate-four project before marking consumer guidance validation-backed. Record exact desktop build and effective value when observable; record unknown when not observable. Record every scenario's executor and any actual human setup/decision separately to verify FR-017/SC-007.

## Failure and Preservation Matrix

Tests must distinguish launched work from failed launch attempts.

| Scenario | Expected result |
|---|---|
| Exhaustion before preflight success | Diagnostic ledger only; no run summary claiming execution. |
| One successful cleanup/retry | Exact agent launched; original failure and restoration reference retained. |
| Repeated exhaustion | At most two launches for that instance; stable blocked recovery. |
| Unknown launch error | No capacity retry; specific existing unavailable/error stop. |
| All children protected or unrelated | No release, no fallback identity, exact operator next action. |
| Missing result, wrong digest, ownership uncertainty, stale revision/state | Reject eligibility without mutation. |
| Release unavailable/fails or accepted without restoration | Distinct results; no unproven recovery success. |
| Child command fails after starting | Existing partial-work stop; no automatic command retry. |
| Corrective-loop launch failure | Completed mutations and pass count preserved; no replay. |
| Config absent/existing/conflicting/malformed/unsupported | Guidance is truthful; install/refresh/remove never write config. |
| Partial component update | Failed operation remains failed; qualified component state and unapplied guidance. |

## Completion Evidence

Record component IDs/versions/digests, source coordinates, actual client/CLI, native identities and launch outcomes, preserved relative artifact references, release and retry evidence, before/after config hashes, positive and negative assertions, and untested boundaries. Keep raw transcripts, secrets, and absolute host paths out of portable records. Planning artifacts, model simulations, and historical recovery are not completion evidence. Do not mark Feature 018 complete if safe native lifecycle handling, sustained sequential use, or validated consumer guidance remains unproven.

# Feature 023 Validation Quickstart

This is the implementation validation guide. Commands below use existing entry points; new scenario assertions are planned extensions and have not run during planning. A passing legacy suite alone does not establish Feature 023 coverage.

## Table of Contents

Run focused checks before the installed parity scenario; preserve actual results and prerequisites.

- [Prerequisites](#prerequisites)
- [Source and Focused Regression Checks](#source-and-focused-regression-checks)
- [Disposable Installed Parity](#disposable-installed-parity)
- [Expected Connected Outcomes](#expected-connected-outcomes)
- [Evidence and Safe Recovery](#evidence-and-safe-recovery)

## Prerequisites

Use the checkout's documented environment, without installing packages ad hoc or modifying existing environments without authorization.

```bash
mise run python:prepare
mise run python:check
mise exec -- specify --version
```

Expected versions are Python 3.11.16, PyYAML 6.0.3 and Specify `1.0.10.dev0+pegagio.2`. Python scripts belonging to or validating Codex skills use the separate documented skill-tools interpreter; the commands here validate repository source/runtime. Review `mise.toml`, `requirements-agent.txt`, `bundles/farmboy/bundle.yml` and `controllers/farmboy/manifest.yml` for actual snapshot pins before executing.

Snapshot integration needs `SPECIFY_BIN` resolving to the pinned CLI and `FLOW_ROADMAP_SOURCE` pointing to a reviewed local flow-roadmap source with ID/version matching bundle pin 0.4.0. Wiki/feedback archives are checksum-verified by existing fixture helpers. Obtain required sources through supported existing project setup, not a guessed checkout, external project edit or dependency upgrade. Local HTTP catalog fixtures require loopback binding permission. Missing CLI/source/permission is an exact blocker to installed coverage; a skipped test is not successful parity.

## Source and Focused Regression Checks

The following commands exist today. Implementation extends their assertions and records their observed results.

```bash
mise exec -- python tools/validate_workflows.py --json --fail-on-unexplained
mise exec -- python -m unittest discover -s tests -p test_controller.py
mise exec -- python -m unittest discover -s tests -p test_workflow_graph.py
mise exec -- python -m unittest discover -s tests -p test_workflow_paths.py
mise exec -- python -m unittest discover -s tests -p test_implement_switch_routing.py
mise exec -- python -m unittest discover -s tests -p test_catalog.py
mise exec -- python -m unittest discover -s tests -p test_implementation_progress.py
mise exec -- python -m unittest discover -s tests -p test_phase_lifecycle.py
```

Expected source validation covers all ten active definitions plus deprecated Start Feature with no dispatch/effects. Malformed `cases.default`, wrong container/body types and impossible producer references fail before delivery with workflow/step/location/correction diagnostics. Supported empty/default/skip routes pass. Selected-child availability checks happen after eligible production; missing selected outputs block before effects and untaken outputs are never required.

Catalog tests should mutate a disposable source snapshot, assert invalid build/verification/install rejection and compare consumer inventories; do not mutate real installed/source assets during manual experiments. Existing topology snapshots may require supported regeneration if source definitions are necessarily reconciled; inspect each expected difference and do not accept a blanket snapshot update.

## Disposable Installed Parity

Use the existing integration entry point with prerequisites configured in the shell.

```bash
mise exec -- python -m unittest discover -s tests -p test_snapshot_validation.py
```

The test creates a temporary consumer outside the repository, initializes core Specify skills, serves matching extension catalogs, and invokes supported `tools/catalog.py install`/refresh with `--development-snapshot` and explicit `--roadmap-source`. It loads installed controller/scope modules and workflow, exercises the extended matrix and checks ownership/preservation on cleanup. Do not hand-copy controller source as an installation substitute or refresh this active feature's consumer merely to run parity.

The extended matrix runs the same scenario inputs/expectations against source and installed modules. Compare raw source/installed digests, selected node traces, missing-input boundaries, historical/current decisions, counters and blocked effects. Both environments must match every FR-014 scenario. Invalid installed-definition tests deliberately alter only disposable YAML and record whether loader/ownership or shared graph validation stopped first; each claimed diagnostic boundary must actually be reached.

## Expected Connected Outcomes

Each positive executes production assessment/scope → eligible dispatch/history → simulated source correction → independent current review → validated marker tracking → actual CLI post-pass capture → guarded re-entry. Prove original historical assessment/source digests remain unchanged despite genuine task/source differences. The next eligible obligation remains identified rather than claiming full feature completion from markers.

For negatives, demonstrate a valid control before changing one guard. Require the intended production blocker and safe action for retained-proof corruption/absence/unbinding, stale current review, unauthorized task edits, missing/wrong-branch/non-ready outputs, no substantive progress and each exhausted budget. Administrative changes, answers and fresh child sessions neither earn progress nor refill limits. Assignment/gate/relay/fingerprint failures stop before affected dispatch without choosing fallback or another phase.

The applied roadmap-preimage regression verifies readback/reassessment without a second writer effect; original receipt identity/timestamp/digest and mutation count remain unchanged. An unrelated artifact digest change must continue to block. These are disposable evidence fixtures, not roadmap changes to Feature 023.

## Evidence and Safe Recovery

Record feature-local portable observations following [connected-observations.md](contracts/connected-observations.md), with actual component IDs/versions/digests, source coordinates/dirty state, installed inventory, tested CLI/runtime, mode and expected/observed effects. Label deterministic synthetic review/dispatch explicitly; no live-agent, effective-settings, publication, stock compatibility, adoption or acceptance claim follows.

On failure preserve original history, current diagnostic and any applied receipt. Correct the smallest source/fixture prerequisite, revalidate the selected scope and installation, then rerun the affected case from a fresh valid control. Never recapture missing historical proof from current files, replay a roadmap writer for readback, erase counted sessions or bypass a gate. Report unavailable integration checks and outstanding mismatches plainly.

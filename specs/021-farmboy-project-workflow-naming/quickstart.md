# Quickstart: FarmBoy Rename Validation

The constitutional identity amendment is approved and applied in Constitution 8.0.0. The operator approved binding the existing `integration` input to all 109 previously unbound prompt nodes across nine workflows; the two Clarify prompt bindings were already applied under the earlier bounded approval. The operator separately approved the bounded Close Out correction: new controller records use `.specify/farmboy-controllers/`, the two historical Feature 017 contract links resolve to their preserved directory, and the Close Out example names the real Feature 014 directory. Validation uses disposable fixtures only and refreshes no existing consumer. Checks preserve reviewed Feature 022 correction `7a43bb3`, integrated by `6738a06` ([merge provenance](validation/boundary-merge.md)).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Existing Regression Checks](#existing-regression-checks)
- [Fresh Consumer Check](#fresh-consumer-check)
- [Results](#results)

## Prerequisites

Use the implemented source, pinned Specify CLI and compatible independent extension sources. Current source pins are bundle 0.18.3; Clarify 0.5.1; Analyze/Remediate 0.6.1; Close Out 0.9.2; Implement 0.9.1; Converge, Plan and Tasks 0.5.1; Select Feature and Wiki Lint Update 0.2.1; Specify 0.4.1; controllers 0.9.1; and roadmap 0.4.0. T007's earlier catalog output is historical checkpoint evidence, not the final coherent composition. T012 regenerates packages with the existing builder and records actual source/package pins and digests. Local packaging is not publication.

```sh
mise run python:prepare
mise run python:check
specify_bin="$(mise which specify)"
"$specify_bin" --version
```

If the existing environment check fails, report the dependency issue and obtain authorization for its documented repair. This guide does not repair `.venv` or add dependencies. The current pins in `mise.toml` are Python `3.11.16` and Specify CLI `1.0.10.dev0+pegagio.2`; `requirements-agent.txt` pins PyYAML `6.0.3`. Record actual tested versions rather than assuming those pins prove readiness.

For local lifecycle/boundary, snapshot and bundle lifecycle coverage, supply reviewed compatible independent sources. The roadmap manifest must declare `flow-roadmap` 0.4.0 matching the implemented bundle pin and provide the generic configuration/write/brief/review interfaces. It no longer supplies `phase_lifecycle.py` or an owner phase test matrix; their absence is intentional and tested. Current reviewed roadmap source is clean at `34483aa212e5cb3302615c0fad043d1eb908edc9`, with runtime identical to cleanup `7eec0b73b49d4d242d491530da5011de62b4d211`. Bundle lifecycle also requires compatible `flow-wiki` source. Snapshot validation extracts checksum-verified wiki and renamed feedback archives from the regenerated catalog; missing or mismatched packages are failures, not skips.

```sh
roadmap_source=/path/to/reviewed-compatible-roadmap-source
wiki_source=/path/to/reviewed-compatible-wiki-source
export SPECIFY_BIN="$specify_bin"
export FLOW_ROADMAP_SOURCE="$roadmap_source"
export FARMBOY_TEST_ROADMAP_SOURCE="$roadmap_source"
export FARMBOY_TEST_WIKI_SOURCE="$wiki_source"
export PYTHON="$PWD/.venv/bin/python"
```

`FLOW_ROADMAP_SOURCE` remains the independent owner's unchanged input. The two `FARMBOY_TEST_*` inputs are the approved renamed project test inputs from T006/T011; their former `SPEC_KIT_FLOW_TEST_*` names receive no fallback. Use the implemented test constants as authority for any other renamed report inputs. These environment values are test inputs, not new runtime dependencies or management options. The disposable catalog tests bind localhost; if the execution environment denies that bind, record the blocked suite and reason without reporting a pass.

## Existing Regression Checks

Update existing name/path expectations during implementation, then run the existing suites below. Each unittest discovery command must report a nonzero test count; a zero-test exit or a skipped prerequisite is not coverage.

| Task coverage | Existing suites |
|---|---|
| T009 packaging and delivery | Agent configuration/delivery and catalog |
| T010 delegation, ownership and controller behavior | Controller, command-skill ownership, implementation revision/progress/scope, local phase lifecycle, workflow-owned roadmap boundary/policy, readiness/routes, workflow graph/improvements/paths |
| T011 disposable delivery and ownership preservation | Snapshot validation and bundle lifecycle |
| T009/T012 feedback and structural checks | Both feedback extension discovery suites and workflow structural validator |

```sh
for suite in agent_configs agent_delivery catalog controller command_skill_ownership implement_task_revision implementation_progress implementation_scope phase_lifecycle workflow_roadmap_boundary readiness readiness_workflow_routes workflow_graph workflow_improvements workflow_paths snapshot_validation bundle_lifecycle; do
  mise exec -- python -m unittest discover -s tests -p "test_${suite}.py" -v || exit $?
done
mise exec -- python tools/validate_workflows.py --json --fail-on-unexplained
mise exec -- python -m unittest discover -s extensions/farmboy-feedback/tests
mise exec -- python -m unittest discover -s extensions/farmboy-feedback-maintainer/tests
```

Run existing extension feedback tests through unittest discovery in `extensions/farmboy-feedback/tests/` and `extensions/farmboy-feedback-maintainer/tests/`. Check capture/report/intake names, unchanged journal/report behavior, `farmboy` parser delegation and absence of old-key dispatch.

Check ten active bindings, nine exact roles, the standalone renderer, deprecated stop-only source, reference consistency and absence of old invocation aliases. Compare graphs against reviewed Feature 022 correction `7a43bb3` with only approved identity/path and delegation-key substitutions normalized. The `phase_lifecycle` suite loads local controller code and fixtures; `workflow_roadmap_boundary` exercises the workflow-owned policy/adapter, authoring proof, generic amendment and independent effect/readback/receipt contract, including all three phase graphs. Its delivered configuration-loader check uses `FARMBOY_TEST_ROADMAP_SOURCE` and requires no extension phase helper. `snapshot_validation` uses `FLOW_ROADMAP_SOURCE` and `SPECIFY_BIN`; `bundle_lifecycle` uses `SPECIFY_BIN` and both `FARMBOY_TEST_*_SOURCE` inputs. The shared snapshot helper and consumer fixtures are exercised by these suites, not standalone test modules. Missing prerequisites must remain explicit skips or failures; record each affected suite and do not count it as passing evidence. If the loop stops on a failed suite, later suites are not run and must be reported as such.

No migration suite, legacy-conversion fixture or new failure/retry matrix is part of this feature. Add a focused naming regression only if the existing suites do not cover a changed reference.

## Fresh Consumer Check

This section is future separately authorized disposable validation, not a request to refresh this checkout or any existing installation. Create only an empty disposable consumer. The following existing development-snapshot route requires a compatible roadmap source and checksum-pinned wiki dependency; use the existing source and temporary-consumer restrictions.

```sh
validation_root="$(mktemp -d "${TMPDIR:-/tmp}/farmboy-validation.XXXXXX")"
consumer_project="$validation_root/fresh"
mkdir -p "$consumer_project"
(
  cd "$consumer_project"
  "$specify_bin" init --here --force --non-interactive --integration codex --integration-options="--skills"
)
mise run catalog:install -- "$consumer_project" --development-snapshot --roadmap-source "$roadmap_source"
(
  cd "$consumer_project"
  "$specify_bin" bundle list
  "$specify_bin" workflow info farmboy-plan
)
```

`--force` applies only to the newly created empty fixture. Expected: bundle `farmboy`, all ten documented FarmBoy workflows/skills, nine configured roles, `farmboy-feedback` with its capture/report skills, and retained independent roadmap/wiki identities. Verify workflow metadata round-trips with `farmboy` through the pinned CLI. Validate maintainer intake through its existing separate extension installation route; it remains outside generic bundle delivery. Inspect all bindings rather than inferring them from Plan alone. In this fresh fixture, old owned names must not act as invocation aliases.

Use existing refresh/remove lifecycle fixtures with renamed expectations to verify unchanged behavior. This guide does not direct removal or replacement of any actual personal installation. Native role availability can be checked in a fresh Codex session with the new exact names; configuration presence alone is not a live launch result.

## Results

Validation used Python 3.11.16, PyYAML 6.0.3, and Specify CLI `1.0.10.dev0+pegagio.2` on macOS arm64. The prepared project Python checks passed. `mise exec -- python tools/catalog.py build <roadmap-source> <wiki-source> --snapshot` rebuilt an unreleased FarmBoy 0.18.3 snapshot with three extensions and ten workflows after the approved correction. No publication or consumer-adoption claim is made.

A complete recursive walk verified all 113 prompt nodes across the ten active workflow definitions explicitly bind the existing `inputs.integration`. The earlier proposal count of 107 omitted two nested Implement stop prompts; the corrected batch contains 109 newly bound nodes across nine workflows, in addition to the four previously bound nodes (two Clarify, two Specify). The affected workflow versions are Analyze/Remediate 0.6.1, Close Out 0.9.1, Converge 0.5.1, Implement 0.9.1, Plan 0.5.1, Select Feature 0.2.1, Specify 0.4.1, Tasks 0.5.1, and Wiki Lint Update 0.2.1. Clarify remains 0.5.1. No workflow steps, roles, gates, routes, question caps, validator policy, or controller policy changed.

The complete source suite passed all 358 tests with no skips when the reviewed roadmap/wiki source inputs and pinned CLI were supplied. The suite exercises fresh recovery-summary creation, implementation-history writes, lifecycle witness/readback, and controller-package/bundle removal while preserving both existing `.specify/flow-controllers/` history and new `.specify/farmboy-controllers/` records. The native bundle lifecycle suite passed all four tests, including disposable install, refresh, removal and native Specify workflow runs for Clarify, Plan, Tasks, Analyze/Remediate, Implement and Converge. The Codex executable was a no-op fixture: this validates Specify CLI dispatch and workflow completion under that test harness, not live Codex agent launches. Separate feedback capture/report and maintainer-intake suites passed five and eight tests, respectively. The three current architecture links resolve, including both historical Feature 017 contracts; the Close Out Feature 014 example matches the preserved directory. `tools/validate_workflows.py --json --fail-on-unexplained` passed for eleven source definitions (the ten active workflows plus the deprecated stop-only source), with zero unexplained terminal paths. `git diff --check` passed.

The generated release metadata records this composition:

| Component | Version | Source commit | Package SHA-256 |
|---|---:|---|---|
| FarmBoy controllers | 0.9.1 | `6738a067045b268feb7f5522d7841290ce70b3a2` | `a7c63afd41625b0144f704d1799f76d0f9f91f36d7c909f422766ccbe2001e0e` |
| FarmBoy agents | 0.2.0 | `6738a067045b268feb7f5522d7841290ce70b3a2` | `e12aaf80e5ae88f06180efdba2d4154fe5658bf15ebfe21e58f7b61bb307e39a` |
| FarmBoy Feedback | 0.2.1 | `6738a067045b268feb7f5522d7841290ce70b3a2` | `6eb29db32dfb072470fc0b558b0f064381161dc2f94c400d994885a94ca2a058` |
| Flow Roadmap | 0.4.0 | `34483aa212e5cb3302615c0fad043d1eb908edc9` | `90a28d748e6d48fb7ade335f7f40e2cb778a5e959aee1f96ff537e18feff4366` |
| Flow Wiki | 2.0.1 | `0292ff66758e36849cee4e0f6bcbdac51629e1d0` | `20cebb4f591d5a83b0c45ae28a0448cb9d29368e5b65e2d28ba106a3ffd488ff` |

Every package archive digest and all ten workflow digests matched `catalog/release.json`. The Close Out workflow is 0.9.2 with digest `0237073c7d53a5d87390d410d2aacbb4d57f4cbddb267e9ffeb353adba0743d1`; the FarmBoy controller package is 0.9.1 with digest `a7c63afd41625b0144f704d1799f76d0f9f91f36d7c909f422766ccbe2001e0e`. The Clarify workflow digest is `d47daa0f4e1d4f1bcb908585797c220ca8b2ffc0cbf53c2dce68856ea4293a6b`; the nine prompt-binding workflow digests are recorded in catalog metadata. The independent roadmap and wiki source checkouts were read-only and clean at the commits shown above. No existing consumer was refreshed. No Linux or live installed-agent behavior was tested.

The closeout-correction implementation, independent review and fresh convergence are complete. The independent review passed 123 focused tests, and convergence found no remaining implementation gaps. The subsequent residual consistency corrections completed T002, T008 and T012: README pins now match the current snapshot, the excluded deprecated launcher path matches the canonical mapping, and this record no longer describes review or convergence as pending. The controller archive and active workflow digests remain unchanged. A final closeout re-debrief is the parent workflow's remaining gate. These results establish local implementation and test evidence only, not Feature 021 acceptance or release publication. Live FarmBoy agent dispatch and Linux validation remain unproved.

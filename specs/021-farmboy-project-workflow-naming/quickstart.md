# Quickstart: FarmBoy Rename Validation

The constitutional identity amendment is approved and applied in Constitution 8.0.0. These checks run after separately invoked rename implementation. They validate the new names using existing tooling; they do not implement a cutover or upgrade an existing consumer.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Existing Regression Checks](#existing-regression-checks)
- [Fresh Consumer Check](#fresh-consumer-check)
- [Results](#results)

## Prerequisites

Use the implemented source, pinned Specify CLI and compatible independent extension sources. Source manifests and the checked catalog snapshot currently differ; validate the actual package/source coordinates used. Follow existing build documentation to regenerate artifacts rather than hand-editing archives or assuming publication.

```sh
mise run python:prepare
mise run python:check
specify_bin="$(mise which pipx:specify-cli)"
"$specify_bin" --version
```

If the existing environment check fails, report the dependency issue and obtain authorization for its documented repair. This guide does not repair `.venv` or add dependencies. The current pins in `mise.toml` are Python `3.11.16` and Specify CLI `1.0.10.dev0+pegagio.2`; `requirements-agent.txt` pins PyYAML `6.0.3`. Record actual tested versions rather than assuming those pins prove readiness.

For owner lifecycle, snapshot and bundle lifecycle coverage, supply reviewed compatible independent sources. The roadmap manifest must match the implemented bundle's `flow-roadmap` pin and include `tests/python/test_phase_lifecycle.py` and `tests/python/test_review_contract.py`; the lifecycle suite imports those owner tests. Bundle lifecycle also requires the compatible `flow-wiki` source. Snapshot validation extracts checksum-verified wiki and renamed feedback archives from the regenerated catalog; missing or mismatched packages are failures, not skips.

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
| T010 delegation, ownership and controller behavior | Controller, command-skill ownership, implementation revision/progress/scope, phase lifecycle, readiness/routes, workflow graph/improvements/paths |
| T011 disposable delivery and ownership preservation | Snapshot validation and bundle lifecycle |
| T009/T012 feedback and structural checks | Both feedback extension discovery suites and workflow structural validator |

```sh
for suite in agent_configs agent_delivery catalog controller command_skill_ownership implement_task_revision implementation_progress implementation_scope phase_lifecycle readiness readiness_workflow_routes workflow_graph workflow_improvements workflow_paths snapshot_validation bundle_lifecycle; do
  mise exec -- python -m unittest discover -s tests -p "test_${suite}.py" -v || exit $?
done
mise exec -- python tools/validate_workflows.py --json --fail-on-unexplained
mise exec -- python -m unittest discover -s extensions/farmboy-feedback/tests
mise exec -- python -m unittest discover -s extensions/farmboy-feedback-maintainer/tests
```

Run existing extension feedback tests through unittest discovery in `extensions/farmboy-feedback/tests/` and `extensions/farmboy-feedback-maintainer/tests/`. Check capture/report/intake names, unchanged journal/report behavior, `farmboy` parser delegation and absence of old-key dispatch.

Check ten active bindings, nine exact roles, the standalone renderer, deprecated stop-only source, reference consistency and absence of old invocation aliases. Compare graphs with only approved identity/path and delegation-key substitutions normalized. The `phase_lifecycle` suite loads its owner matrix from `FLOW_ROADMAP_SOURCE`; `snapshot_validation` uses that source and `SPECIFY_BIN`; `bundle_lifecycle` uses `SPECIFY_BIN` and both `FARMBOY_TEST_*_SOURCE` inputs. The shared snapshot helper and consumer fixtures are exercised by these suites, not standalone test modules. Missing prerequisites must remain explicit skips or failures; record each affected suite and do not count it as passing evidence. If the loop stops on a failed suite, later suites are not run and must be reported as such.

No migration suite, legacy-conversion fixture or new failure/retry matrix is part of this feature. Add a focused naming regression only if the existing suites do not cover a changed reference.

## Fresh Consumer Check

Create only an empty disposable consumer. The following existing development-snapshot route requires a compatible roadmap source and checksum-pinned wiki dependency; use the existing source and temporary-consumer restrictions.

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

Record tested source/package versions, digests, CLI, outcomes and skipped prerequisites. Local source checks and disposable delivery results do not establish publication, universal compatibility or acceptance. The historical planning-only exception authorized design; the applied amendment and current analysis/remediation still do not authorize these implementation or consumer operations. Future validation requires the separately invoked implementation scope.

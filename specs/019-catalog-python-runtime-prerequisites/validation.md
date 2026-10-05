# Validation: Agent Python Environment

## Environment and source

Validation used disposable temporary projects with isolated mise configuration, state and cache directories. Their package caches and `.venv` directories were removed after each scenario. The source checkout's previously absent, ignored `.venv` was prepared separately under T002 below. No global Python package or skill-tools environment was changed. The source revision at the start was `d9f12e2` on `specs/017-flowkit-agent-configuration`.

Observed tools: mise `2026.10.0` (`macos-arm64`), uv `0.12.5`, CPython `3.11.16`, and PyYAML `6.0.3`. The selected mise interpreter was the installed Python `3.11.16`; disposable successful invocations reported `.venv/bin/python` and a `.venv` `sys.prefix`. The venv executable is a symlink to the mise-managed base binary on this platform, so the prefix and mise-selected command establish environment selection; resolving `sys.executable` follows that symlink.

## T002 — source checkout preparation

The source checkout `.venv` path was verified absent before preparation. `mise run python:prepare` then created it from the selected mise Python and installed PyYAML `6.0.3`; its final check passed. A following `mise run python:check` passed. Both `mise exec -- python ...` and `mise exec -- python3 ...` reported the project-local `.venv` prefix, Python `3.11.16` and PyYAML `6.0.3`; the `python` invocation also passed the safe YAML round-trip. The environment remains ignored by Git. Mise state/cache and uv cache used for this preparation were temporary; the local project environment is the only persistent setup change.

## T004 — preparation and failure scenarios

In a clean disposable project with the source `mise.toml` and `requirements-agent.txt`, these commands passed:

```sh
mise run python:prepare
mise run python:check
mise exec -- python -c 'import sys, yaml; print(sys.executable); print(sys.prefix); print(sys.version.split()[0]); print(yaml.__version__); sample={"items":["one",2],"enabled":True}; assert yaml.safe_load(yaml.safe_dump(sample)) == sample'
```

Preparation created the local `.venv`, installed PyYAML `6.0.3`, and ended with `python:check: ready`. On the initially absent environment, mise also emitted its built-in “no venv found” warning before the task created `.venv`; the preparation command still succeeded. The direct `python` invocation reported `.venv/bin/python`, `.venv` as its prefix, Python `3.11.16`, and PyYAML `6.0.3`; its safe YAML round-trip assertion passed. The same check with `mise exec -- python3` also selected `.venv`, covering the executable name used by the repository's catalog tasks.

After adding a sentinel file to the ready environment, a repeated `mise run python:prepare` passed and reported that the existing environment was not changed; the sentinel remained byte-for-byte unchanged. To exercise the missing-package state, the disposable environment was modified with `mise exec -- uv pip uninstall --python .venv/bin/python PyYAML`. `mise run python:check` then exited `1` with `No module named 'yaml'` and targeted recovery guidance. `mise run python:prepare` also exited `1`, reported that the existing environment was incomplete and unchanged, and did not reinstall the package. A direct import-spec check returned `None`; the sentinel remained unchanged.

For the existing-path scenario, `.venv` was a directory containing only an `operator-owned.txt` sentinel. `mise run python:prepare` exited `1` because `.venv/bin/python` was absent. The sentinel and directory contents were unchanged.

Package acquisition failure was exercised with `UV_OFFLINE=1` and a private empty uv cache. `mise run python:prepare` created a new `.venv`, then uv reported that pinned PyYAML was unavailable while the network was disabled. Preparation exited `1` with an explicit incomplete-environment message. The subsequent `mise run python:check` exited `1`, reported the actual fixture interpreter and Python `3.11.16`, failed the PyYAML import, and did not claim readiness. Recovery remains the documented, operator-approved targeted install into the compatible local environment.

The first sandboxed package acquisition attempt also failed because DNS access to `pypi.org` was unavailable. Repeating only the disposable fixture acquisition with approved network escalation succeeded. That failed attempt remains part of the evidence; the successful retry does not recast the blocked attempt as success.

## T003 — regression tests

`python3 -m unittest tests.test_agent_python_environment -v` passed: two tests covering fresh preparation plus explicit `python` and `python3` selection, and preservation/reporting for an existing incomplete path. Their mise state/config/cache and uv package cache are isolated under temporary directories. Package download required the scoped network escalation described above.

## T008 — second-project adoption

A second temporary project was created without `.specify`, source-checkout helpers or a copied `.venv`. Its `requirements-agent.txt`, complete relevant `mise.toml` configuration/task block, `.gitignore` rule and ordinary-agent instruction were copied from [the delivered guide](../../docs/agent-python-environment.md). The existing mise Python and uv pins were already installed; `mise install python uv` reported both as already installed and installed zero tools.

In that project, `mise run python:prepare`, `mise run python:check`, and the same `mise exec -- python -c ...` YAML round-trip passed. The project reported its own `.venv/bin/python` prefix, Python `3.11.16` and PyYAML `6.0.3`. A repeated preparation also passed without replacing the environment. No Specify or FlowKit runtime was present in the fixture.

## T009 — existing configuration preservation

A disposable existing-project fixture contained unrelated task/settings, Python pin `3.10`, uv pin `0.12.5`, a non-default `.project-venv` activation path, an existing `python:check` task, PyYAML `6.0.2`, existing agent guidance and ignore content, plus an operator-owned `.venv/operator-owned.txt`. Inspection identified the Python pin, activation path, existing task name and PyYAML requirement as conflicts needing operator decisions. No recipe inputs were merged while those decisions were unresolved. SHA-256 snapshots of the existing config, requirement, guidance and ignore files were identical before and after inspection; the environment sentinel also remained identical. This demonstrates the guide's preservation procedure, not an automated migration tool.

## T010 — scope and historical evidence

The implementation dependency change is limited to `requirements-agent.txt` containing `PyYAML==6.0.3`, matching the required disposition in [research.md](research.md). No pytest, HTTP client, rich output, schema library or other extra package was added; the utility alternatives and their observed-use limits remain documented there.

`specs/017-flowkit-agent-configuration/follow-up.md` retained its baseline SHA-256 `c5818fc7663e7fed921cd0e051b804610ad20b7cb2297d5734efd110cf464311`. No tracked Feature 017 file differs from the starting revision; its accepted agent evidence, original missing-PyYAML failure, alternate-interpreter retry, limitations and disposition remain unchanged. The source Feature 017 records were checked read-only against `HEAD` and the worktree.

## T011 — validated Python boundary

Updated the portable guide to state that its unchanged recipe and check support Python `3.11.16`, and that differing existing pins stay untouched pending an operator decision; the guide makes no alternate-version validation claim. The requirements block is byte-equal to `requirements-agent.txt`. The copied mise block parses as TOML and its Python/uv pins, environment activation, and `python:prepare`/`python:check` task definitions equal the source `mise.toml`. The guide's existing-project instructions retain unrelated configuration, flag conflicting pins and task names for operator decisions, and keep the existing `.venv` unchanged, consistent with the repeatable-adoption requirements in the plan and the previously recorded T009 sentinel/config preservation result.

The source checkout's read-only `mise run python:check` passed with Python `3.11.16` and PyYAML `6.0.3`. A direct `mise exec -- python` safe YAML serialization/parsing round-trip also passed with those versions. Mise used an isolated temporary cache because writing its default user cache was denied; its offline version-list warnings for the separately configured `pipx:specify-cli` did not affect either check. The T009 disposable conflict/preservation fixture was not rerun because this change only corrects documentation; its recorded file hashes and environment sentinel remain the fixture evidence for that behavior.

## Limits

The scenarios establish the documented setup on the observed macOS arm64 host with these pinned tools. They do not establish other-platform support, full catalog lifecycle success, stock Specify compatibility, publication or adoption by another real project. The second project was disposable validation only. No package was installed into a global interpreter or the skill-tools environment, and no feature acceptance or roadmap verification is implied.

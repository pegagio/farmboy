# Quickstart Validation: Agent Python Environment

This guide describes the implementation target. The preparation/check tasks and requirements file are not implemented by planning; execute these scenarios only after implementation and in a disposable checkout. This replaces the superseded runtime-integration validation matrix.

## Prerequisites and Preparation

Use the current macOS repository context with mise available and repository configuration trusted. Work from the repository root. For a fresh checkout whose `.venv` path is absent:

```sh
mise install python uv
mise run python:prepare
mise run python:check
```

Expected: existing pinned Python/uv are provisioned, a local `.venv` is created from mise's Python, PyYAML 6.0.3 is installed there and checking reports success. Specify installation is not required. Retain actual failure and recovery results if network/cache acquisition fails.

An existing environment must not be recreated silently. Preparation succeeds read-only when it is ready; otherwise inspect its interpreter and package state before choosing recovery. After explicit approval to repair a compatible existing local environment, use:

```sh
mise exec -- uv pip install --python .venv/bin/python -r requirements-agent.txt
mise run python:check
```

Do not replace an incompatible or unrelated existing path without a separate decision. No `--clear`, automatic fallback interpreter, global package installation or skill-tools modification belongs to recovery.

## Actual Agent Invocation

In a new shell without interactive activation, use the same convention the agent will follow between skill invocations:

```sh
mise exec -- python -c 'import sys, yaml; print(sys.executable); print(sys.version.split()[0]); print(yaml.__version__); sample={"items":["one",2],"enabled":True}; assert yaml.safe_load(yaml.safe_dump(sample)) == sample'
```

Expected: interpreter/prefix belongs to this checkout's `.venv`, Python matches the retained 3.11.16 pin, PyYAML is 6.0.3 and the assertion passes. Version equality alone does not establish environment selection; the check task verifies `sys.prefix` as well. Bare Python in an unactivated shell is not the documented invocation.

Review `AGENTS.md` for that convention and the preserved skill-tools exception. Review the short setup documentation for zero hidden installation steps. The direct YAML check, not success in an unrelated personal interpreter, establishes this feature's readiness.

## Negative and Preservation Scenarios

Use separate disposable fixtures; do not damage the active checkout or user environments.

| Scenario | Expected observation |
|---|---|
| No `.venv` | Check fails with preparation guidance; no fallback or creation at check time. |
| Compatible `.venv` missing PyYAML | Check identifies missing package; preparation leaves existing state unchanged and explains authorized targeted repair. |
| Wrong Python or non-venv/conflicting/external-symlink path | Concise failure; original contents remain unchanged; no automatic recreation. |
| Package acquisition unavailable | Preparation fails truthfully; incomplete new state does not pass checking. Recovery remains documented and explicit. |
| Already-ready `.venv` | Repeated preparation/check succeeds without replacing it or modifying unrelated packages/files. |
| Another activated environment | The explicit mise invocation still selects this checkout's prepared `.venv`; explicit uv target prevents package installation elsewhere. |

## Second-Project Adoption and Conflict Preservation

After implementation, create a second clean disposable directory outside the source checkout with no `.specify`, `.venv` or implicit access to source helper scripts. Copy only the actual delivered snippets from `docs/agent-python-environment.md`: dependency file, minimal configuration including complete preparation/check task definitions, ignore rule and agent-guidance paragraph. If tasks use local files, copy those exact documented files too. Use the documented mise trust step for this new configuration; do not hand-author replacements for missing guide content.

From that project's root, run:

```sh
mise trust
mise install python uv
mise run python:prepare
mise run python:check
mise exec -- python -c 'import sys, yaml; print(sys.executable); print(sys.version.split()[0]); print(yaml.__version__); sample={"items":["one",2],"enabled":True}; assert yaml.safe_load(yaml.safe_dump(sample)) == sample'
```

Expected: the interpreter/prefix belongs to the second project's local `.venv`, declared versions match and safe YAML operations succeed without Specify, FlowKit installed state or source-checkout helper access. Retest preparation/check without replacing the ready environment. Record copied inputs, trust/setup steps, interpreter/package/tool versions, observed results and any failure/retry separately. Missing snippets or undocumented setup mean this scenario has not passed.

Use another disposable fixture with existing `mise.toml` tool pins and unrelated tasks/settings, dependency and agent-guidance content, ignore rules and a pre-existing `.venv` sentinel. Record their contents before adoption. Follow the guide's inspection/merge steps: compatible, non-conflicting keys merge without duplicate tables or deleting unrelated content; differing Python/uv pins, PyYAML requirements, activation values or colliding task names require an explicit decision before those keys change. Check that the environment sentinel and unrelated settings remain unchanged. An unresolved conflict is a successful preservation/diagnostic observation, not successful preparation; an explicitly approved compatible merge must still pass the direct interpreter/YAML check to establish readiness.

This fixture tests the user-directed reuse requirement. It does not authorize automatic edits or environment changes in any real consumer project, and does not establish untested platform support.

## Evidence and Completion Boundaries

Record revision, actual interpreter/prefix and Python/PyYAML/mise/uv versions, commands used, preparation performed, outcome and any failed attempt/retry separately. Portable project records replace machine-specific prefixes with relative paths or neutral descriptions.

Verify the utility assessment's explicit exclusions and scan implementation changes for unintended runtime coupling. Confirm Feature 017 historical files remain unchanged, including the original missing-PyYAML failure, alternate-interpreter retry and native/model-support limits. Passing these checks does not imply full catalog lifecycle, Specify compatibility, publication or feature acceptance. No environment, package, second-project adoption or implementation tests were run by this planning command.

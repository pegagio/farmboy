# Research: Agent Python Environment

This research resolves the narrowed feature's environment and utility choices. It replaces the superseded shared-Specify/runtime-profile design and supports [plan.md](plan.md); findings are design evidence, not installed-environment validation.

## Environment Decision

**Decision**: Use an ignored project `.venv` created from the existing mise Python 3.11.16 installation. Existing uv installs one pinned requirement, `PyYAML==6.0.3`; existing mise activates `.venv` and supplies the explicit `mise exec -- python` invocation. Keep all existing tool pins.

**Rationale**: `mise.toml` selects Python and uv but declares no Python packages; repository `.venv` is absent. `tools/catalog.py`, `tools/validate_workflows.py` and multiple tests import `yaml`. The motivating [DEP017-01 record](../017-flowkit-agent-configuration/follow-up.md) documents a mise-selected interpreter missing PyYAML and a different equipped interpreter succeeding. Python version selection and installed-package availability are separate facts.

**Alternatives considered**: Installing into mise's base Python would affect other projects sharing that installation. Reusing Specify's pipx environment restores the rejected coupling. Reusing skill-tools for all work blurs its higher-priority skill-specific role. A uv packaged project/lockfile adds metadata without benefit for one dependency with no runtime dependencies; a plain pinned requirements file is adequate. Custom launchers and inventories are unnecessary because mise already supplies environment activation and explicit execution.

Mise documents existing-venv activation through `_.python.venv`, including `mise exec`; shims alone do not activate it. uv supports selecting the target Python explicitly. Use a path from `mise where python` when creating the environment to avoid accepting an unrelated same-version interpreter. [Mise Python documentation](https://mise.jdx.dev/lang/python.html), [uv environment documentation](https://docs.astral.sh/uv/pip/environments/).

## Preparation and Version Decision

**Decision**: Retain the tested 6.0.3 PyYAML baseline and require the actual documented Python to pass safe YAML operations. Preparation creates only an absent local environment; checking existing state is read-only. Targeted package repair is documented and requires authorization before modifying an existing user-owned environment.

**Rationale**: A single exact requirement is reviewable and reproducible without introducing a dependency-management framework. PyYAML 6.0.3 is an existing observed baseline and published distribution; it is not claimed to have passed this new preparation path. An explicit `uv pip install --python .venv/bin/python -r requirements-agent.txt` avoids activated external-environment discovery. uv's creation command can replace an existing virtual environment, so guard the target before invoking it; do not use overwrite/clear flags. [PyYAML 6.0.3 distribution](https://pypi.org/project/PyYAML/6.0.3/), [uv package installation](https://docs.astral.sh/uv/pip/packages/), [uv venv reference](https://docs.astral.sh/uv/reference/cli/#uv-venv).

**Alternatives considered**: Unbounded latest versions weaken repeatable observations; hash-lock generation and broad compatibility matrices exceed this one-package goal. Automatic environment creation at shell entry or check time would make read-only usage mutate state.

## Portable Delivery Decision

**Decision**: Provide one self-contained guide, `docs/agent-python-environment.md`, with copyable dependency, mise configuration/task and agent-guidance inputs plus preparation and verification instructions. Reuse the same two small tasks in each adopting project. Keep environments project-local and adoption explicit.

**Rationale**: The direct operator decision, now FR-009 / SC-005, requires repeatability outside this checkout. Documentation can carry this small setup without a bundle component, installer framework or Specify integration. A second disposable project must use the actual guide snippets, so absence of undocumented source-checkout dependencies is observed rather than assumed. Existing target configuration and environments require inspection and non-destructive merging; differing pins, activation settings or task names are surfaced before adoption.

**Alternatives considered**: Repository-only instructions do not satisfy reuse. Automatic consumer installation or globally sharing an environment exceeds scope and risks unrelated projects. Adding a template/component release layer is unnecessary for the initial one-package recipe. The baseline guide is macOS and uses current pins; a compatible target's existing pins are not replaced automatically and need direct validation, while incompatible choices remain a bounded adoption decision.

## Utility Assessment

The selected set contains PyYAML only. No minimum number of extras is required; the repository's observed use, rather than anticipated agent convenience, governs adoption.

| Candidate/use | Evidence and benefit | Existing alternative and cost | Disposition |
|---|---|---|---|
| PyYAML: YAML read/write | Confirmed missing import in DEP017-01; maintained tools/tests import `yaml`. Directly eliminates that failure for the documented agent invocation. | No YAML parser in the Python stdlib; one pinned external package to maintain. | Required by approved scope. |
| pytest: test execution | Maintained tests use `unittest`; no observed missing-pytest failure or pytest-specific test need. | Existing stdlib unittest runs the current suite. Another runner would add dependencies and conventions. | Exclude; no demonstrated benefit here. |
| requests/httpx: HTTP operations | Existing catalog code uses stdlib HTTP/URL facilities; no missing-client failure identified. | Existing `urllib` and HTTP helpers suffice for current tasks. Adds dependency updates and redundant API choices. | Exclude until an actual task demonstrates a gap. |
| rich: formatted terminal output | No recurring formatting failure in the named defect or maintained tools. | Plain text/JSON output already exists; formatting package adds maintenance without established reduction in thrash. | Exclude. |
| jsonschema: validation | No schema-library gap identified for the environment feature. | Existing explicit validation and stdlib JSON remain sufficient; another dependency cannot be justified by speculative use. | Exclude. |
| JSON/TOML/path/process utilities | Maintained code uses these repeatedly. | Python 3.11 already provides `json`, `tomllib`, `pathlib` and `subprocess`; no installation needed. | Document availability through stdlib, no added packages. |

This bounded assessment is not an exhaustive repository inventory and does not authorize installing excluded tools. If an ordinary task later needs another library, record its concrete use and request approval before adoption. `specify_cli` is an existing component's dependency, not an agent convenience package; its separate runtime remains unchanged.

## Evidence and Limits

Observed locally on 2026-10-05: mise `2026.10.0`, uv `0.12.5`, existing Python pin `3.11.16`, no repository `.venv`, no root requirements/pyproject/uv lock declaration, `.venv/` already ignored and absent from worktree copying. Core setup resolved the active feature and reported a synthetic branch; Git reports `specs/017-flowkit-agent-configuration`.

Read-only source inspection and official documentation resolved the design unknowns. No environment creation, package acquisition, negative fixture execution, second-project adoption or new preparation success was observed. Primary documentation may describe newer tool behavior; implementation must validate the planned settings and commands with the retained local versions. Feature 017 and earlier Feature 019 reports remain point-in-time evidence and are not rewritten.

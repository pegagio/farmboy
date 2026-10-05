# Agent Python Environment

This guide provides a small, opt-in project-local Python setup for agents that need PyYAML during ordinary repository work. It uses existing mise and uv, installs no Python packages globally, and keeps each project's `.venv` local. It is separate from Spec Kit Flow bundle installation. The unchanged recipe and its check support Python `3.11.16`; leave different existing Python pins untouched pending an operator decision. This recipe does not validate alternate Python versions.

## Copyable project inputs

Add a `requirements-agent.txt` file:

```text
PyYAML==6.0.3
```

Merge the following entries into the existing `mise.toml` tables. Do not duplicate table headers or overwrite unrelated project settings. The Python and uv values below are the versions validated for this recipe. If an existing project has different pins, leave them untouched until an operator decides how to reconcile the conflict.

```toml
[tools]
python = "3.11.16"
uv = "0.12.5"

[env]
_.python.venv = ".venv"

[tasks."python:prepare"]
description = "Prepare the project-local Python environment without replacing existing state"
run = '''
set -eu
if [ -e .venv ] || [ -L .venv ]; then
  if [ -L .venv ]; then
    echo "python:prepare: .venv is a symlink; inspect it before choosing recovery." >&2
    exit 1
  fi
  if [ -d .venv ] && mise run python:check; then
    echo "python:prepare: existing .venv is ready; it was not changed."
    exit 0
  fi
  echo "python:prepare: existing .venv is incomplete or incompatible and was not changed." >&2
  echo "Inspect it; after approving repair, use: mise exec -- uv pip install --python .venv/bin/python -r requirements-agent.txt" >&2
  exit 1
fi

python_path="$(mise which python)"
if ! uv venv --python "$python_path" --no-python-downloads .venv; then
  echo "python:prepare: could not create .venv with the installed mise Python; inspect the failure before retrying." >&2
  exit 1
fi
if ! uv pip install --python .venv/bin/python -r requirements-agent.txt; then
  echo "python:prepare: package installation failed; .venv may be incomplete and does not pass readiness checks." >&2
  exit 1
fi
mise run python:check
'''

[tasks."python:check"]
description = "Check the project-local Python and PyYAML environment without changing it"
run = '''
set -eu
if [ -L .venv ]; then
  echo "python:check: .venv is a symlink; inspect the path before use." >&2
  exit 1
fi
if [ ! -x .venv/bin/python ]; then
  echo "python:check: .venv/bin/python is missing; run mise run python:prepare." >&2
  exit 1
fi
mise exec -- python - <<'PY'
from pathlib import Path
import sys

expected_python = "3.11.16"
expected_pyyaml = "6.0.3"
expected_prefix = (Path.cwd() / ".venv").resolve()
actual_python = ".".join(str(part) for part in sys.version_info[:3])
actual_prefix = Path(sys.prefix).resolve()
print(f"python:check: interpreter={sys.executable}; prefix={sys.prefix}; Python={actual_python}")
try:
    import yaml
    sample = {"items": ["one", 2], "enabled": True}
    assert yaml.safe_load(yaml.safe_dump(sample)) == sample
except Exception as exc:
    print(f"python:check: PyYAML import or safe YAML round-trip failed: {exc}", file=sys.stderr)
    print("Inspect .venv; after approving repair, install requirements into that environment.", file=sys.stderr)
    raise SystemExit(1)

if actual_python != expected_python:
    print(f"python:check: expected Python {expected_python}, found {actual_python}.", file=sys.stderr)
    raise SystemExit(1)
if actual_prefix != expected_prefix:
    print(f"python:check: expected project prefix {expected_prefix}, found {actual_prefix}.", file=sys.stderr)
    raise SystemExit(1)
if yaml.__version__ != expected_pyyaml:
    print(f"python:check: expected PyYAML {expected_pyyaml}, found {yaml.__version__}.", file=sys.stderr)
    raise SystemExit(1)

print(f"python:check: ready; executable={sys.executable}; prefix={sys.prefix}; Python={actual_python}; PyYAML={yaml.__version__}")
PY
'''
```

Add `.venv/` to the project's `.gitignore`. Do not copy or propagate the environment between checkouts or worktrees.

## Agent instructions

For ordinary project Python commands, including work between skill invocations, use `mise exec -- python <args>` after preparation and a successful check. Do not guess another interpreter or install packages ad hoc when the check fails. Scripts belonging to or validating Codex skills continue to use the applicable skill-tools interpreter and its own dependency instructions.

## Prepare and verify

From the adopting project's root, trust the configuration and install its declared mise tools, then prepare and check the local environment:

```sh
mise trust
mise install python uv
mise run python:prepare
mise run python:check
mise exec -- python -c 'import sys, yaml; print(sys.executable); print(sys.prefix); print(sys.version.split()[0]); print(yaml.__version__); sample={"items":["one",2],"enabled":True}; assert yaml.safe_load(yaml.safe_dump(sample)) == sample'
```

The check reports the interpreter, prefix and package versions. It confirms the Python pin, project `.venv` prefix, exact PyYAML version and safe serialization/parsing. A successful import in another shell or environment does not establish that this project's invocation is ready.

## Existing projects and recovery

Before adopting the recipe in an existing project, inspect `mise.toml`, dependency files, agent guidance, ignore rules and `.venv`. Merge only missing, non-conflicting keys into existing tables. Preserve unrelated tasks and settings. Do not duplicate TOML tables or task names. Differing Python/uv pins, a different dependency declaration or activation path, and colliding task names require an explicit decision before those items change. Keep `.venv` content unchanged while resolving the conflict.

Preparation creates `.venv` only when the path is absent. A ready existing environment passes preparation without modification. Symlinks, incomplete environments and incompatible Python/package versions stop with a diagnostic; inspect existing state before choosing recovery. An incomplete newly created environment after failed package acquisition does not pass the check. After approving repair of a compatible existing local environment, the targeted command is:

```sh
mise exec -- uv pip install --python .venv/bin/python -r requirements-agent.txt
mise run python:check
```

Replacing an incompatible environment requires a separate decision. The recipe does not install into a global Python, alter skill-tools or claim support for platforms beyond those actually validated.

#!/usr/bin/env bash
# Prepare a project-local environment without replacing existing state.
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

if [ ! -f requirements-agent.txt ]; then
  echo "python:prepare: requirements-agent.txt is missing from the project root; add it before creating .venv." >&2
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

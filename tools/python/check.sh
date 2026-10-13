#!/usr/bin/env bash
# Validate the environment path before invoking its Python interpreter.
set -eu
if [ -L .venv ]; then
  echo "python:check: .venv is a symlink; inspect the path before use." >&2
  exit 1
fi
if [ ! -x .venv/bin/python ]; then
  echo "python:check: .venv/bin/python is missing; run mise run python:prepare." >&2
  exit 1
fi
mise exec -- python tools/python/check.py

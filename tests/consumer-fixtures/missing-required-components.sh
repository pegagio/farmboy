#!/usr/bin/env bash
set -euo pipefail

# Proves that a clean consumer cannot claim success when a required component
# is unavailable. This fixture intentionally does not install any components.

specify_bin=${SPECIFY_BIN:?Set SPECIFY_BIN to the compatible specify executable.}
source_root=${FARMBOY_ROOT:?Set FARMBOY_ROOT to the FarmBoy checkout.}
fixture_root=$(mktemp -d "${TMPDIR:-/tmp}/farmboy-missing.XXXXXX")
trap 'rm -rf "$fixture_root"' EXIT

cd "$fixture_root"
"$specify_bin" init --here --force --non-interactive --integration codex --integration-options="--skills" >/dev/null
if "$specify_bin" bundle install "$source_root/bundles/farmboy/bundle.yml" --offline; then
  echo "expected missing required components to reject installation" >&2
  exit 1
fi

if "$specify_bin" bundle list | grep -q "farmboy"; then
  echo "failed installation incorrectly recorded a compatible bundle" >&2
  exit 1
fi

echo "missing required components were explicit and no bundle was recorded"

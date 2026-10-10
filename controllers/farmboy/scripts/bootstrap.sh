#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "usage: bootstrap.sh PROJECT_DIR WORKFLOW_ID SKILL_ID" >&2
  exit 2
fi

project_dir="$(cd -- "$1" && pwd -P)"
workflow_id="$2"
skill_id="$3"
shift 3
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
package_dir="$(cd -- "$script_dir/.." && pwd -P)"
controller="$script_dir/python/controller.py"
manifest="$package_dir/manifest.yml"

if [[ ! -f "$manifest" || ! -f "$controller" ]]; then
  echo "FarmBoy controller package is incomplete" >&2
  exit 1
fi

expected_version="$(awk '/^requires:/{inside=1;next} inside && /^  specify_cli_version:/{print $2; exit}' "$manifest" | tr -d '"')"
if [[ -z "$expected_version" ]]; then
  echo "FarmBoy controller manifest has no Specify CLI version pin" >&2
  exit 1
fi

cd "$project_dir"
mise_selected=""
if command -v mise >/dev/null 2>&1; then
  mise_selected="$(mise which specify 2>/dev/null || true)"
fi

candidate_count=0
only_candidate=""
seen_candidates="|"
IFS=: read -r -a path_entries <<< "${PATH:-}"
for path_entry in "${path_entries[@]}"; do
  [[ -n "$path_entry" ]] || path_entry="."
  candidate="$path_entry/specify"
  if [[ -x "$candidate" && -f "$candidate" ]]; then
    resolved_candidate="$(cd -- "$(dirname -- "$candidate")" && pwd -P)/$(basename -- "$candidate")"
    case "$seen_candidates" in
      *"|$resolved_candidate|"*) ;;
      *)
        seen_candidates+="$resolved_candidate|"
        candidate_count=$((candidate_count + 1))
        only_candidate="$resolved_candidate"
        ;;
    esac
  fi
done

if [[ -n "$mise_selected" ]]; then
  if [[ ! -x "$mise_selected" || ! -f "$mise_selected" ]]; then
    echo "mise-selected Specify executable is missing or not executable" >&2
    exit 1
  fi
  specify_bin="$mise_selected"
elif [[ $candidate_count -eq 1 ]]; then
  specify_bin="$only_candidate"
elif [[ $candidate_count -eq 0 ]]; then
  echo "Specify executable not found in mise or PATH" >&2
  exit 1
else
  echo "ambiguous Specify executables in PATH" >&2
  exit 1
fi

shebang="$(head -n 1 "$specify_bin")"
if [[ "$shebang" == '#!/usr/bin/env '* ]]; then
  python_name="${shebang#\#!/usr/bin/env }"
  python_bin="$(command -v "$python_name" || true)"
elif [[ "$shebang" == '#!'* ]]; then
  python_bin="${shebang#\#!}"
else
  echo "selected Specify executable has no supported Python shebang" >&2
  exit 1
fi
if [[ -z "$python_bin" || ! -x "$python_bin" ]]; then
  echo "selected Specify Python runtime is missing or not executable" >&2
  exit 1
fi

exec "$python_bin" "$controller" inspect \
  --project "$project_dir" \
  --workflow-id "$workflow_id" \
  --skill-id "$skill_id" \
  --specify "$specify_bin" \
  --expected-version "$expected_version" \
  "$@"

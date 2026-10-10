#!/usr/bin/env python3
"""Project every source workflow into a static branch and gate inventory."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_ROOT = ROOT / "workflows"
STOP_WORDS = re.compile(r"\b(stop|blocked|blocker|defer|cap|resume|escalat)\w*\b", re.IGNORECASE)
SUCCESS_WORDS = re.compile(r"\b(clean|success|complete|converged|executed|ready|resolved)\b", re.IGNORECASE)


def node_kind(node: dict[str, Any]) -> str:
    """Return the authored step kind used by the controller inventory."""
    if isinstance(node.get("type"), str):
        return node["type"]
    if "command" in node:
        return "command"
    if "prompt" in node or "input" in node:
        return "prompt"
    return "unknown"


def _walk(nodes: list[dict[str, Any]], *, parent: str | None = None, branch: str | None = None):
    for node in nodes:
        yield node, parent, branch
        kind = node_kind(node)
        if kind == "switch":
            for choice, children in node.get("cases", {}).items():
                yield from _walk(children, parent=node.get("id"), branch=str(choice))
            yield from _walk(node.get("default", []), parent=node.get("id"), branch="default")
        elif kind == "do-while":
            yield from _walk(node.get("steps", []), parent=node.get("id"), branch="loop-body")


def expand_paths(nodes: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Expand declared switch alternatives while preserving sequence order."""
    paths: list[list[dict[str, Any]]] = [[]]
    for node in nodes:
        if node_kind(node) == "switch":
            branches = list(node.get("cases", {}).items())
            if "default" in node:
                branches.append(("default", node.get("default", [])))
            if not branches:
                branches = [("<missing-branches>", [])]
            expanded: list[list[dict[str, Any]]] = []
            for prefix in paths:
                for choice, children in branches:
                    for child_path in expand_paths(children):
                        expanded.append(prefix + [{"id": node.get("id"), "type": "switch-choice", "choice": str(choice)}] + child_path)
            paths = expanded
        else:
            for path in paths:
                path.append(node)
    return paths


def _prompt_text(node: dict[str, Any]) -> str:
    """Read either source-YAML prompt form without guessing at command output."""
    value = node.get("prompt")
    if value is None and isinstance(node.get("input"), dict):
        value = node["input"].get("prompt")
    return value if isinstance(value, str) else ""


def audit_terminals(paths: list[list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Classify each expanded path ending as success, bounded stop, or unexplained."""
    successes: list[dict[str, Any]] = []
    stops: list[dict[str, Any]] = []
    unexplained: list[dict[str, Any]] = []
    for path in paths:
        if not path:
            unexplained.append({"path": [], "terminal_step_id": None, "reason": "empty-path"})
            continue
        terminal = path[-1]
        kind = node_kind(terminal)
        if kind == "gate":
            continue  # Gate options are inventoried separately as explicit human decisions.
        elif (kind == "command" and isinstance(terminal.get("id"), str)
              and terminal["id"].startswith("return-to-")
              and any(node_kind(node) == "gate" for node in path[:-1])):
            stops.append({
                "path": [item.get("id") for item in path],
                "terminal_step_id": terminal.get("id"),
                "reason": "operator-selected-return-command-ends-current-workflow",
            })
        else:
            text = _prompt_text(terminal) if kind == "prompt" else ""
            if SUCCESS_WORDS.search(text):
                successes.append({"path": [item.get("id") for item in path], "terminal_step_id": terminal.get("id")})
            elif STOP_WORDS.search(text):
                stops.append({"path": [item.get("id") for item in path], "terminal_step_id": terminal.get("id")})
            else:
                unexplained.append({
                    "path": [item.get("id") for item in path],
                    "terminal_step_id": terminal.get("id"),
                    "reason": f"terminal-{kind}-has-no-explicit-outcome",
                })
    return successes, stops, unexplained


def project_workflow(definition: dict[str, Any]) -> dict[str, Any]:
    """Build branch, gate, loop, assignment, and terminal projections."""
    metadata = definition.get("workflow", {})
    steps = definition.get("steps", [])
    flattened = list(_walk(steps))
    assignments = []
    branches = []
    gates = []
    loops = []
    for node, parent, branch in flattened:
        step_id = node.get("id")
        kind = node_kind(node)
        assignment = node.get("farmboy")
        if isinstance(assignment, dict) and assignment.get("delegated") is True:
            assignments.append({"step_id": step_id, "agent": assignment.get("agent"), "parent": parent, "branch": branch})
        if kind == "switch":
            for choice, body in node.get("cases", {}).items():
                branches.append({"switch": step_id, "choice": str(choice), "first_step": body[0].get("id") if body else None})
            if "default" in node:
                body = node.get("default", [])
                branches.append({"switch": step_id, "choice": "default", "first_step": body[0].get("id") if body else None})
        elif kind == "gate":
            gates.append({"step_id": step_id, "options": node.get("options", [])})
        elif kind == "do-while":
            loops.append({"loop_id": step_id, "condition": node.get("condition"),
                          "max_iterations": node.get("max_iterations"),
                          "body_step_ids": [item.get("id") for item in node.get("steps", [])]})
    paths = expand_paths(steps)
    successes, stops, unexplained = audit_terminals(paths)
    first = next((node for node in steps if node_kind(node) in {"prompt", "command"}), None)
    return {
        "workflow_id": metadata.get("id"),
        "version": metadata.get("version"),
        "entry_step_id": steps[0].get("id") if steps else None,
        "initial_assessment_step": first.get("id") if first else None,
        "nodes": [{"step_id": node.get("id"), "kind": node_kind(node), "parent": parent, "branch": branch}
                  for node, parent, branch in flattened],
        "branches": branches,
        "success_paths": successes,
        "continuation_edges": loops,
        "human_decisions": gates,
        "bounded_stops": stops,
        "assignments": assignments,
        "native_agent_selection": {
            "status": "unverified",
            "reason": "Static workflow validation does not request native Codex subagents.",
        },
        "unexplained_terminal_paths": unexplained,
    }


def load_workflows() -> list[dict[str, Any]]:
    """Read active and deprecated source workflow definitions in stable order."""
    paths = sorted(WORKFLOW_ROOT.glob("farmboy-*/workflow.yml"))
    definitions = []
    for path in paths:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("workflow"), dict) or not isinstance(data.get("steps"), list):
            raise ValueError(f"malformed workflow definition: {path.relative_to(ROOT)}")
        definitions.append(data)
    identities = [item["workflow"]["id"] for item in definitions]
    if not definitions or len(set(identities)) != len(identities):
        raise ValueError("source workflow inventory is empty or has duplicate identities")
    return definitions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the full projection as JSON")
    parser.add_argument("--fail-on-unexplained", action="store_true", help="return failure when a branch lacks an explicit outcome")
    args = parser.parse_args()
    projections = [project_workflow(definition) for definition in load_workflows()]
    if args.json:
        print(json.dumps({"workflows": projections}, indent=2, sort_keys=True))
    else:
        for item in projections:
            print(f"{item['workflow_id']}@{item['version']}: {len(item['nodes'])} nodes, {len(item['branches'])} branches, "
                  f"{len(item['human_decisions'])} human gates, {len(item['continuation_edges'])} loops, "
                  f"{len(item['assignments'])} assignments, native-agent-selection={item['native_agent_selection']['status']}, "
                  f"{len(item['unexplained_terminal_paths'])} unexplained terminals")
    return int(args.fail_on_unexplained and any(item["unexplained_terminal_paths"] for item in projections))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, yaml.YAMLError) as error:
        raise SystemExit(f"workflow inventory failed: {error}")

#!/usr/bin/env python3
"""Read and preflight an installed FlowKit workflow for a Codex task."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    from specify_cli.workflows.engine import WorkflowEngine
except ImportError:  # The controller is executed with the selected Specify runtime.
    WorkflowEngine = None  # type: ignore[assignment,misc]


REVIEWED_AGENT_NAMES = {
    "FlowKit-Roadmap Agent", "FlowKit-Specifier", "FlowKit-Planner", "FlowKit-Tasker", "FlowKit-Reviewer",
    "FlowKit-Coder", "FlowKit-Code Reviewer", "FlowKit-Wiki Curator",
}
INPUT_REFERENCE = re.compile(r"\{\{\s*inputs\.([A-Za-z0-9_-]+)\s*\}\}")
STEP_REFERENCE = re.compile(r"\{\{\s*steps\.([A-Za-z0-9_-]+)\.output\.([A-Za-z0-9_.-]+)\s*\}\}")
LOOP_CONDITION = re.compile(
    r"^\{\{\s*steps\.([A-Za-z0-9_-]+)\.output\.state\s*==\s*(['\"])continue\2\s*\}\}$"
)
REASON_CODE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
OUTCOME_STATES = {"complete", "continue", "needs-human", "blocked"}


@dataclass(frozen=True)
class StepAssignmentIntent:
    """Identify the native Codex agent assigned to one delegated workflow step."""

    step_id: str
    agent_name: str

    def to_dict(self) -> dict[str, str]:
        """Return the portable representation used by controller output and recovery."""
        return asdict(self)


def select_specify_executable(mise_selected: Path | None, path_candidates: Iterable[Path]) -> Path:
    """Choose the selected mise runtime or one unambiguous PATH executable."""
    candidates = list(dict.fromkeys(Path(item) for item in path_candidates))
    if mise_selected is not None:
        selected = Path(mise_selected)
        if not selected.is_file() or not os.access(selected, os.X_OK):
            raise ValueError("mise-selected Specify executable is missing or not executable")
        return selected
    if not candidates:
        raise ValueError("Specify executable not found in mise or PATH")
    if len(candidates) != 1:
        raise ValueError("ambiguous Specify executables in PATH")
    selected = candidates[0]
    if not selected.is_file() or not os.access(selected, os.X_OK):
        raise ValueError("Specify executable is missing or not executable")
    return selected


def check_specify_version(actual_output: str, expected_version: str) -> str:
    """Require the selected Specify CLI to match the controller package pin."""
    actual = actual_output.strip()
    expected = f"specify {expected_version}"
    if actual != expected:
        raise ValueError(f"expected Specify {expected_version}, found {actual or 'no version output'}")
    return actual


def load_installed_definition(project_root: Path, workflow_id: str) -> dict[str, Any]:
    """Load the composed workflow definition without creating native run state."""
    if WorkflowEngine is None:
        raise RuntimeError("Specify workflow loader is unavailable in this Python runtime")
    project = Path(project_root).resolve()
    definition = WorkflowEngine(project).load_workflow(workflow_id)
    data = definition.data
    metadata = data.get("workflow", {})
    if metadata.get("id") != workflow_id:
        raise ValueError(f"loaded workflow ID mismatch: expected {workflow_id}, found {metadata.get('id')}")
    source_path = getattr(definition, "source_path", None)
    if source_path:
        try:
            source_path = Path(source_path).resolve().relative_to(project.resolve()).as_posix()
        except ValueError:
            source_path = None
    serialized = json.loads(json.dumps(data))
    return {
        "workflow": serialized["workflow"],
        "version": metadata.get("version"),
        "inputs": serialized.get("inputs", {}),
        "steps": serialized.get("steps", []),
        "requires": serialized.get("requires", {}),
        "source_path": source_path,
        "sha256": hashlib.sha256(json.dumps(serialized, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
    }


def validate_workflow_definition(definition: dict[str, Any]) -> None:
    """Validate named-agent metadata placement before returning a workflow graph."""
    workflow = definition.get("workflow", {})
    if any(key in workflow for key in ("agent", "model", "reasoning_effort", "default_agent", "default_model", "default_reasoning_effort")):
        raise ValueError("workflow-level agent and model defaults are unsupported")
    if any(key in definition for key in ("agent", "model", "reasoning_effort", "default_agent", "default_model", "default_reasoning_effort")):
        raise ValueError("top-level agent and model defaults are unsupported")
    if not isinstance(workflow.get("id"), str) or not isinstance(workflow.get("version"), str):
        raise ValueError("workflow ID and version must be strings")
    validate_workflow_graph(definition["steps"])
    collect_agent_assignments(definition["steps"])
    validate_template_forms(definition["steps"], set(definition.get("inputs", {})))


def validate_template_forms(steps: list[dict[str, Any]], input_names: set[str]) -> None:
    """Reject unsupported expressions anywhere in the installed step graph."""
    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "condition" and value.get("type") == "do-while":
                    continue
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
        elif isinstance(value, str) and ("{{" in value or "}}" in value):
            expressions = re.findall(r"\{\{.*?\}\}", value, flags=re.DOTALL)
            for expression in expressions:
                input_match = INPUT_REFERENCE.fullmatch(expression)
                if input_match:
                    if input_match.group(1) not in input_names:
                        raise ValueError(f"unsupported template input: {input_match.group(1)}")
                elif not STEP_REFERENCE.fullmatch(expression):
                    raise ValueError("unsupported template expression in workflow graph")
            remainder = re.sub(r"\{\{.*?\}\}", "", value, flags=re.DOTALL)
            if "{{" in remainder or "}}" in remainder:
                raise ValueError("unsupported template expression in workflow graph")

    visit(steps)


def file_fingerprint(path: Path) -> dict[str, int | str] | None:
    """Return stable content and file-identity evidence, or None if absent."""
    candidate = Path(path)
    try:
        details = candidate.stat()
        content_digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(details.st_mode):
        raise ValueError(f"installation record is not a regular file: {candidate.name}")
    return {"sha256": content_digest, "device": details.st_dev, "inode": details.st_ino}


def installation_fingerprints(project_root: Path) -> dict[str, dict[str, int | str] | None]:
    """Snapshot both Specify and FlowKit installation records without writing."""
    root = Path(project_root)
    return {
        "bundle_record": file_fingerprint(root / ".specify/bundle-records.json"),
        "skill_record": file_fingerprint(root / ".specify/flow-kit/skills-install.json"),
    }


def verify_controller_install(project_root: Path, skill_id: str, workflow_id: str) -> dict[str, Any]:
    """Verify the selected skill and shared helper against their ownership record."""
    project = Path(project_root)
    record_path = project / ".specify/flow-kit/skills-install.json"
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"FlowKit controller ownership record is missing or unreadable: {error}") from error
    if record.get("package") != "flow-kit-controllers" or record.get("status") != "installed":
        raise ValueError("FlowKit controller package is not in installed state")
    controllers = record.get("controllers")
    matches = [item for item in controllers or [] if item.get("skill_id") == skill_id]
    if len(matches) != 1 or matches[0].get("workflow_id") != workflow_id:
        raise ValueError("FlowKit skill-to-workflow binding differs from the installed ownership record")
    owned_files = record.get("files")
    if not isinstance(owned_files, dict):
        raise ValueError("FlowKit controller ownership file inventory is malformed")
    required = {
        f".agents/skills/{skill_id}/SKILL.md",
        f".agents/skills/{skill_id}/agents/openai.yaml",
        ".specify/flow-kit/manifest.yml",
        ".specify/flow-kit/controller-protocol.md",
        ".specify/flow-kit/scripts/bootstrap.sh",
        ".specify/flow-kit/scripts/python/controller.py",
        ".specify/flow-kit/scripts/python/recovery.py",
    }
    for relative in required:
        expected = owned_files.get(relative)
        target = project / relative
        if not isinstance(expected, str) or not target.is_file():
            raise ValueError(f"FlowKit-owned controller file is missing: {relative}")
        observed = hashlib.sha256(target.read_bytes()).hexdigest()
        if observed != expected:
            raise ValueError(f"FlowKit-owned controller file was changed: {relative}")
    installed_manifest = (project / ".specify/flow-kit/manifest.yml").read_text(encoding="utf-8")
    manifest_version = re.search(r'^  version:\s*["\']?([^"\'\n]+)', installed_manifest.split("package:\n", 1)[1], re.MULTILINE)
    if manifest_version is None or manifest_version.group(1).strip() != record.get("version"):
        raise ValueError("FlowKit controller manifest version differs from the installation record")
    skill_text = (project / f".agents/skills/{skill_id}/SKILL.md").read_text(encoding="utf-8")
    declared_name = re.search(r"^name:\s*([^\n]+)", skill_text, re.MULTILINE)
    if declared_name is None or declared_name.group(1).strip() != skill_id:
        raise ValueError("installed FlowKit skill frontmatter differs from its ID")
    return record


def _node_kind(step: dict[str, Any]) -> str:
    if "type" in step:
        return str(step["type"])
    if "command" in step:
        return "command"
    if "prompt" in step or "input" in step:
        return "prompt"
    return "unknown"


def validate_workflow_graph(steps: list[dict[str, Any]]) -> None:
    """Reject unsupported nodes, malformed loops, duplicate IDs, and model placement."""
    seen: set[str] = set()

    def visit(nodes: list[dict[str, Any]], *, inside_loop: bool = False) -> None:
        for node in nodes:
            if not isinstance(node, dict):
                raise ValueError("workflow step must be a mapping")
            step_id = node.get("id")
            if not isinstance(step_id, str) or not step_id.strip():
                raise ValueError("workflow step is missing a nonempty id")
            if step_id in seen:
                raise ValueError(f"duplicate step id: {step_id}")
            seen.add(step_id)
            kind = _node_kind(node)
            if kind not in {"prompt", "command", "gate", "switch", "do-while"}:
                raise ValueError(f"unsupported workflow step type {kind}: {step_id}")
            if kind == "command" and node.get("integration") not in (None, "codex", "{{ inputs.integration }}"):
                raise ValueError(f"unsupported command integration on step {step_id}")
            if "model" in node or "reasoning_effort" in node:
                raise ValueError(f"concrete model and effort settings are unsupported on step {step_id}; use a named Codex agent")
            if "agent" in node or "delegated" in node:
                raise ValueError(f"agent assignment on step {step_id} must use explicit flow_kit metadata")
            assignment = node.get("flow_kit")
            if "flow_kit" in node:
                if kind not in {"prompt", "command"}:
                    raise ValueError(f"agent delegation is not allowed on {kind} step {step_id}")
                if not isinstance(assignment, dict) or set(assignment) != {"delegated", "agent"} or assignment.get("delegated") is not True:
                    raise ValueError(f"flow_kit metadata must explicitly delegate step {step_id}")
                agent_name = assignment.get("agent")
                if not isinstance(agent_name, str) or agent_name not in REVIEWED_AGENT_NAMES:
                    raise ValueError(f"step {step_id} names an unknown or invalid Codex agent: {agent_name!r}")
            if kind == "gate":
                options = node.get("options")
                if (not isinstance(options, list) or not options
                    or any(not isinstance(option, str) or not option.strip() for option in options)
                    or len(set(options)) != len(options)):
                    raise ValueError(f"gate options must be distinct nonempty strings: {step_id}")
            if kind == "switch":
                cases = node.get("cases", {})
                if not isinstance(cases, dict):
                    raise ValueError(f"switch cases must be a mapping: {step_id}")
                if "transition_labels" in node:
                    labels = node["transition_labels"]
                    branch_keys = set(cases) | ({"default"} if "default" in node else set())
                    if (not isinstance(labels, dict) or not labels
                            or any(key not in branch_keys or not isinstance(label, str) or not label.strip()
                                   for key, label in labels.items())):
                        raise ValueError(f"transition labels must name existing branches with nonempty text: {step_id}")
                for branch in cases.values():
                    if not isinstance(branch, list):
                        raise ValueError(f"switch case must contain a step list: {step_id}")
                    visit(branch, inside_loop=inside_loop)
                default = node.get("default", [])
                if not isinstance(default, list):
                    raise ValueError(f"switch default must contain a step list: {step_id}")
                visit(default, inside_loop=inside_loop)
            if "assessment_only_first_pass" in node:
                if kind != "do-while" or not isinstance(node["assessment_only_first_pass"], bool):
                    raise ValueError("assessment_only_first_pass requires a boolean on a do-while node")
            if "assessment_before_correction" in node:
                if kind != "do-while" or not isinstance(node["assessment_before_correction"], bool):
                    raise ValueError("assessment_before_correction requires a boolean on a do-while node")
                if node["assessment_before_correction"] and node.get("assessment_only_first_pass"):
                    raise ValueError("loop assessment modes are mutually exclusive")
            if kind == "do-while":
                if inside_loop:
                    raise ValueError(f"nested do-while loops are unsupported: {step_id}")
                condition = node.get("condition")
                body = node.get("steps")
                maximum = node.get("max_iterations")
                if node.get("assessment_before_correction") and not isinstance(condition, str):
                    raise ValueError("assessment_before_correction requires an assessment condition")
                if not isinstance(condition, bool):
                    if not isinstance(condition, str) or LOOP_CONDITION.fullmatch(condition.strip()) is None:
                        raise ValueError(f"do-while condition is unsupported or incomplete: {step_id}")
                if isinstance(maximum, bool) or not isinstance(maximum, int) or maximum < 1:
                    raise ValueError(f"do-while max_iterations must be a positive integer: {step_id}")
                if not isinstance(body, list) or not body:
                    raise ValueError(f"do-while steps must be a nonempty list: {step_id}")
                if isinstance(condition, str):
                    match = LOOP_CONDITION.fullmatch(condition.strip())
                    assessment_id = match.group(1) if match is not None else None
                    body_ids = {item.get("id") for item in body if isinstance(item, dict)}
                    if assessment_id not in body_ids:
                        raise ValueError(f"do-while condition must reference an in-body assessment step: {step_id}")
                    assessor = next(item for item in body if isinstance(item, dict) and item.get("id") == assessment_id)
                    if node.get("assessment_before_correction"):
                        if (len(body) != 3 or _node_kind(body[0]) != "command" or assessor is not body[1]
                                or _node_kind(assessor) != "prompt" or _node_kind(body[2]) != "switch"
                                or body[2].get("expression") != "{{ steps." + assessment_id + ".output.state }}"
                                or set(body[2].get("cases", {})) not in (
                                    {"continue", "complete", "blocked"},
                                    {"continue", "complete", "needs-human", "blocked"})
                                or any(body[2]["cases"].get(state) for state in ("complete", "needs-human", "blocked"))
                                or body[2].get("default")):
                            raise ValueError(f"assessment_before_correction requires command, assessment, and guarded correction: {step_id}")
                    elif assessor is not body[-1] or _node_kind(assessor) not in {"prompt", "command"}:
                        raise ValueError(f"do-while condition must reference the final fresh assessment step: {step_id}")
                visit(body, inside_loop=True)

    if not isinstance(steps, list):
        raise ValueError("workflow steps must be a list")
    visit(steps)


def evaluate_loop_condition(condition: str | bool, outputs: dict[str, dict[str, Any]]) -> bool:
    """Evaluate only the reviewed boolean literal or assessment-state comparison."""
    if isinstance(condition, bool):
        return condition
    if not isinstance(condition, str):
        raise ValueError("do-while condition must be a boolean or supported expression")
    match = LOOP_CONDITION.fullmatch(condition.strip())
    if match is None:
        raise ValueError("do-while condition is not a complete supported expression")
    step_id = match.group(1)
    if step_id not in outputs or not isinstance(outputs[step_id], dict) or "state" not in outputs[step_id]:
        raise ValueError(f"unresolved do-while assessment output: {step_id}.state")
    return outputs[step_id]["state"] == "continue"


def route_assessment(
    assessment: dict[str, Any],
    *,
    loop_body_step_ids: set[str],
    human_gate_step_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Route a validated assessment state without performing workflow work."""
    state = assessment.get("state") if isinstance(assessment, dict) else None
    if state == "complete":
        return {"action": "complete"}
    if state == "continue":
        next_step_id = assessment.get("next_step_id")
        if not isinstance(next_step_id, str) or next_step_id not in loop_body_step_ids:
            raise ValueError("continue assessment must name a next step inside its loop body")
        return {"action": "continue", "next_step_id": next_step_id}
    if state == "needs-human":
        gates = human_gate_step_ids or set()
        if gates:
            gate_step_id = assessment.get("gate_step_id")
            if not isinstance(gate_step_id, str) or gate_step_id not in gates:
                raise ValueError("needs-human assessment must name a declared main-task gate")
            return {"action": "needs-human", "gate_step_id": gate_step_id}
        resume_action = assessment.get("resume_action")
        if not isinstance(resume_action, str) or REASON_CODE.fullmatch(resume_action) is None:
            raise ValueError("needs-human assessment without a gate must name a stable resume action")
        return {"action": "needs-human", "resume_action": resume_action}
    if state == "blocked":
        resume_action = assessment.get("resume_action")
        if not isinstance(resume_action, str) or REASON_CODE.fullmatch(resume_action) is None:
            raise ValueError("blocked assessment must name a stable resume action")
        return {"action": "blocked", "resume_action": resume_action}
    raise ValueError("assessment state is unsupported")


def validate_outcome_envelope(
    envelope: dict[str, Any],
    project_root: Path,
    loop_body_step_ids: set[str],
    human_gate_step_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Validate a machine-readable assessment against current project evidence."""
    if not isinstance(envelope, dict):
        raise ValueError("assessment envelope must be a mapping")
    allowed = {"state", "reason_code", "evidence", "remaining_ids", "resolved_ids", "next_step_id", "gate_step_id", "resume_action"}
    if set(envelope) - allowed:
        raise ValueError("assessment envelope contains unsupported fields")
    if envelope.get("state") not in OUTCOME_STATES:
        raise ValueError("assessment state is unsupported")
    reason = envelope.get("reason_code")
    if not isinstance(reason, str) or REASON_CODE.fullmatch(reason) is None:
        raise ValueError("assessment reason_code must be a stable identifier")
    evidence = envelope.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("assessment requires current evidence")
    project = Path(project_root).resolve()
    seen_paths: set[str] = set()
    normalized_evidence: list[dict[str, str]] = []
    for item in evidence:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            raise ValueError("assessment evidence must contain only path and sha256")
        relative = item.get("path")
        digest = item.get("sha256")
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValueError("assessment evidence path must stay inside the project")
        if not isinstance(digest, str) or SHA256.fullmatch(digest) is None:
            raise ValueError("assessment evidence SHA-256 is malformed")
        try:
            candidate = (project / relative).resolve(strict=True)
        except OSError as error:
            raise ValueError("assessment evidence file does not exist or cannot be resolved") from error
        try:
            normalized = candidate.relative_to(project).as_posix()
        except ValueError as error:
            raise ValueError("assessment evidence path resolves outside the project") from error
        if not candidate.is_file():
            raise ValueError("assessment evidence must name an existing file")
        observed = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if observed != digest:
            raise ValueError("assessment evidence digest does not match current bytes")
        if normalized in seen_paths:
            raise ValueError("assessment evidence paths must be distinct")
        seen_paths.add(normalized)
        normalized_evidence.append({"path": normalized, "sha256": observed})

    id_values: dict[str, list[str]] = {}
    for key in ("remaining_ids", "resolved_ids"):
        values = envelope.get(key, [])
        if not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values):
            raise ValueError(f"assessment {key} must be a list of nonempty identifiers")
        if len(values) != len(set(values)):
            raise ValueError(f"assessment {key} identifiers must be distinct")
        id_values[key] = values
    if set(id_values["remaining_ids"]) & set(id_values["resolved_ids"]):
        raise ValueError("assessment remaining and resolved identifiers contradict")
    state = envelope["state"]
    expected_route_key = {
        "complete": None,
        "continue": "next_step_id",
        "needs-human": "gate_step_id" if human_gate_step_ids else "resume_action",
        "blocked": "resume_action",
    }[state]
    route_keys = {"next_step_id", "gate_step_id", "resume_action"} & set(envelope)
    expected_route_keys = {expected_route_key} if expected_route_key else set()
    if route_keys != expected_route_keys:
        raise ValueError("assessment must provide exactly the route field required by its state")
    if state == "complete" and id_values["remaining_ids"]:
        raise ValueError("complete assessment has unresolved in-scope work")
    if state == "continue" and not id_values["remaining_ids"]:
        raise ValueError("continue assessment has no unresolved in-scope work")
    normalized = dict(envelope)
    normalized["evidence"] = normalized_evidence
    normalized["remaining_ids"] = id_values["remaining_ids"]
    normalized["resolved_ids"] = id_values["resolved_ids"]
    route_assessment(normalized, loop_body_step_ids=loop_body_step_ids, human_gate_step_ids=human_gate_step_ids)
    return normalized


def assessment_made_progress(previous: dict[str, Any], current: dict[str, Any]) -> bool:
    """Require explicit resolution of a prior finding; byte changes are insufficient."""
    previous_remaining = set(previous.get("remaining_ids", []))
    current_resolved = set(current.get("resolved_ids", []))
    return bool(previous_remaining & current_resolved)


def route_loop_assessment(
    assessment: dict[str, Any],
    *,
    iteration: int,
    max_iterations: int,
    loop_body_step_ids: set[str],
    human_gate_step_ids: set[str] | None = None,
    previous_assessment: dict[str, Any] | None = None,
    assessment_only_first_pass: bool = False,
    assessment_before_correction: bool = False,
) -> dict[str, Any]:
    """Route pre-loop or refreshed loop evidence, stopping on no progress or cap."""
    if isinstance(iteration, bool) or not isinstance(iteration, int) or iteration < 0:
        raise ValueError("loop iteration must be a nonnegative integer")
    if isinstance(max_iterations, bool) or not isinstance(max_iterations, int) or max_iterations < 1:
        raise ValueError("loop max_iterations must be a positive integer")
    if not isinstance(assessment_only_first_pass, bool):
        raise ValueError("assessment_only_first_pass must be a boolean")
    if not isinstance(assessment_before_correction, bool):
        raise ValueError("assessment_before_correction must be a boolean")
    if assessment_before_correction and assessment_only_first_pass:
        raise ValueError("loop assessment modes are mutually exclusive")
    route = route_assessment(assessment, loop_body_step_ids=loop_body_step_ids,
                             human_gate_step_ids=human_gate_step_ids)
    if route["action"] != "continue":
        return route
    if iteration == 0:
        return route
    if (assessment_only_first_pass or assessment_before_correction) and iteration == 1 and previous_assessment is None:
        if iteration >= max_iterations:
            return {"action": "blocked", "blocker": "loop-cap-exhausted"}
        return route
    if previous_assessment is None:
        made_progress = iteration == 1 and bool(assessment.get("resolved_ids"))
    else:
        made_progress = assessment_made_progress(previous_assessment, assessment)
    if not made_progress:
        return {"action": "blocked", "blocker": "no-progress"}
    if iteration >= max_iterations:
        return {"action": "blocked", "blocker": "loop-cap-exhausted"}
    return route


def validate_required_inputs(workflow: dict[str, Any], supplied: dict[str, Any]) -> dict[str, Any]:
    """Apply declared defaults and reject missing required workflow inputs."""
    declared = workflow.get("inputs", {})
    values: dict[str, Any] = {}
    unknown = sorted(set(supplied) - set(declared))
    if unknown:
        raise ValueError(f"unknown workflow input: {', '.join(unknown)}")
    for name, definition in declared.items():
        if name in supplied:
            values[name] = supplied[name]
        elif "default" in definition:
            values[name] = definition["default"]
        elif definition.get("required"):
            raise ValueError(f"missing required workflow input: {name}")
        if name in values:
            expected_type = definition.get("type")
            if expected_type == "string" and not isinstance(values[name], str):
                raise ValueError(f"workflow input must be a string: {name}")
            if definition.get("required") and isinstance(values[name], str) and not values[name].strip():
                raise ValueError(f"missing required workflow input: {name}")
            options = definition.get("enum")
            if options and values[name] not in options:
                raise ValueError(f"workflow input is not an allowed value: {name}")
    return values


def parse_key_values(arguments: list[str] | None, *, argument_name: str) -> dict[str, str]:
    """Parse unique key=value CLI tokens without printing supplied values."""
    values: dict[str, str] = {}
    for token in arguments or []:
        if "=" not in token:
            raise ValueError(f"{argument_name} must use key=value syntax")
        key, value = token.split("=", 1)
        if not key or key in values:
            raise ValueError(f"{argument_name} key is empty or repeated: {key}")
        values[key] = value
    return values


def collect_agent_assignments(steps: list[dict[str, Any]]) -> list[StepAssignmentIntent]:
    """Enumerate explicitly delegated steps and their native agent names across every branch."""
    validate_workflow_graph(steps)

    def collect(nodes: list[dict[str, Any]]) -> list[StepAssignmentIntent]:
        assignments: list[StepAssignmentIntent] = []
        for step in nodes:
            step_id = step["id"]
            kind = _node_kind(step)
            assignment = step.get("flow_kit")
            if "flow_kit" in step:
                assignments.append(StepAssignmentIntent(step_id=step_id, agent_name=assignment["agent"]))
            if kind == "switch":
                for branch in step.get("cases", {}).values():
                    assignments.extend(collect(branch))
                assignments.extend(collect(step.get("default", [])))
            elif kind == "do-while":
                assignments.extend(collect(step.get("steps", [])))
        return assignments

    return collect(steps)


def render_template(value: Any, inputs: dict[str, Any], outputs: dict[str, dict[str, Any]]) -> Any:
    """Render only the documented input and prior-step-output references."""
    if isinstance(value, list):
        return [render_template(item, inputs, outputs) for item in value]
    if isinstance(value, dict):
        rendered_mapping = {key: render_template(item, inputs, outputs) for key, item in value.items()}
        if rendered_mapping.get("type") == "gate":
            source_options = value.get("options")
            dynamic = (isinstance(source_options, list) and len(source_options) == 1
                       and isinstance(source_options[0], str)
                       and STEP_REFERENCE.fullmatch(source_options[0].strip()) is not None)
            if dynamic:
                options = rendered_mapping.get("options")
                if not isinstance(options, list) or len(options) != 1 or not isinstance(options[0], list):
                    raise ValueError("dynamic gate options must resolve to an array")
                rendered_mapping["options"] = list(options[0])
            options = rendered_mapping.get("options")
            if (not isinstance(options, list) or not options
                or any(not isinstance(option, str) or not option.strip() for option in options)
                or len(set(options)) != len(options)):
                raise ValueError("rendered gate options must be distinct nonempty strings")
        return rendered_mapping
    if not isinstance(value, str):
        return value

    def input_value(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in inputs:
            raise ValueError(f"unresolved input reference: {name}")
        return str(inputs[name])

    rendered = INPUT_REFERENCE.sub(input_value, value)

    def output_value(match: re.Match[str]) -> str:
        step_id, key_path = match.groups()
        current: Any = outputs.get(step_id)
        for key in key_path.split("."):
            if not isinstance(current, dict) or key not in current:
                raise ValueError(f"unresolved step output reference: {step_id}.{key_path}")
            current = current[key]
        return str(current)

    # A whole output reference may carry a dynamic gate option list.
    whole_output = STEP_REFERENCE.fullmatch(rendered.strip())
    if whole_output is not None:
        step_id, key_path = whole_output.groups()
        current: Any = outputs.get(step_id)
        for key in key_path.split("."):
            if not isinstance(current, dict) or key not in current:
                raise ValueError(f"unresolved step output reference: {step_id}.{key_path}")
            current = current[key]
        if isinstance(current, list):
            return list(current)
    rendered = STEP_REFERENCE.sub(output_value, rendered)
    if "{{" in rendered or "}}" in rendered:
        raise ValueError(f"unsupported or unresolved template expression: {rendered}")
    return rendered


def installed_skill_name(command_id: str) -> str:
    """Apply the pinned Specify command-to-skill naming rule."""
    return command_id.replace(".", "-")


def resolve_installed_skill(project_root: Path, command_id: str) -> dict[str, str]:
    """Find exactly one project-local Codex skill matching a Specify command."""
    expected_name = installed_skill_name(command_id)
    project = Path(project_root)
    roots = [project / ".agents/skills", project / ".codex/skills"]
    matches: list[Path] = []
    for root in roots:
        candidate = root / expected_name / "SKILL.md"
        if candidate.is_file():
            matches.append(candidate)
    if not matches:
        raise ValueError(f"installed Codex command skill not found: {expected_name}")
    if len(matches) > 1:
        raise ValueError(f"ambiguous installed Codex command skill: {expected_name}")
    skill_file = matches[0]
    text = skill_file.read_text(encoding="utf-8")
    name_match = re.search(r"^name:\s*[\"']?([^\"'\n]+)", text, re.MULTILINE)
    if name_match is None or name_match.group(1).strip() != expected_name:
        raise ValueError(f"installed Codex skill declares a different name: {expected_name}")
    project_relative = skill_file.relative_to(project).as_posix()
    provenance: str | None = None
    manifest_path = project / ".specify/integrations/codex.manifest.json"
    if manifest_path.is_file():
        try:
            integration_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError("selected project's Codex skill provenance manifest is malformed") from error
        recorded_digest = integration_manifest.get("files", {}).get(project_relative)
        actual_digest = hashlib.sha256(skill_file.read_bytes()).hexdigest()
        if recorded_digest is None:
            raise ValueError(f"selected project's Codex manifest has no skill provenance: {expected_name}")
        if recorded_digest != actual_digest:
            raise ValueError(f"installed Codex command skill differs from its provenance record: {expected_name}")
        provenance = "codex.manifest.json"
    return {"name": expected_name, "path": str(skill_file), "command_id": command_id, "provenance": provenance or "unrecorded"}


def validate_child_question(request: dict[str, Any], expected_step_id: str) -> dict[str, Any]:
    """Validate one child question before presenting it in the main task."""
    if not isinstance(request, dict) or request.get("kind") != "question":
        raise ValueError("child request must have kind question")
    if request.get("step_id") != expected_step_id:
        raise ValueError("child question step_id differs from the active step")
    question = request.get("question")
    if not isinstance(question, str) or not question.strip():
        raise ValueError("child question text must be nonempty")
    options = request.get("options")
    if not isinstance(options, list) or len(options) > 5:
        raise ValueError("child question options must be a list of up to five choices")
    option_ids: list[str] = []
    for option in options:
        if isinstance(option, str):
            option_id = option
        elif isinstance(option, dict) and isinstance(option.get("description"), str) and option["description"].strip():
            option_id = option.get("id")
        else:
            raise ValueError("child question options need nonempty IDs and descriptions")
        if not isinstance(option_id, str) or not option_id.strip():
            raise ValueError("child question options need nonempty IDs and descriptions")
        option_ids.append(option_id)
    if len(set(option_ids)) != len(option_ids):
        raise ValueError("child question options must be distinct")
    flags = [request[key] for key in ("allow_custom_answer", "allow_custom", "custom_allowed") if key in request]
    if not flags or any(not isinstance(flag, bool) for flag in flags) or len(set(flags)) != 1:
        raise ValueError("child question custom-answer flag is missing or conflicting")
    if not options and not flags[0]:
        raise ValueError("child question needs options or a custom answer")
    return {
        "kind": "question", "step_id": expected_step_id, "question": question.strip(),
        "options": options, "allow_custom_answer": flags[0],
    }


def resolve_child_answer(request: dict[str, Any], answer: str, child_id: str, target_child_id: str) -> dict[str, str]:
    """Require an explicit answer addressed to the child that asked."""
    question = validate_child_question(request, request.get("step_id", "") if isinstance(request, dict) else "")
    if not child_id or target_child_id != child_id:
        raise ValueError("answer must continue the same child")
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("an explicit human answer is required")
    chosen = answer.strip()
    options = question["options"]
    option_ids = [option if isinstance(option, str) else option["id"] for option in options]
    if chosen.isdigit() and 1 <= int(chosen) <= len(option_ids):
        chosen = option_ids[int(chosen) - 1]
    else:
        matching = [option for option in option_ids if option.casefold() == chosen.casefold()]
        if matching:
            chosen = matching[0]
        elif not question["allow_custom_answer"]:
            raise ValueError("human answer is not an allowed option")
    return {"step_id": question["step_id"], "child_id": child_id, "answer": chosen}


def validate_gate_choice(gate: dict[str, Any], answer: str) -> str:
    """Resolve one explicit human verdict against installed gate options."""
    if not isinstance(gate, dict) or gate.get("type") != "gate":
        raise ValueError("human verdict requires a gate step")
    options = gate.get("options")
    if not isinstance(options, list) or not options or any(not isinstance(option, str) or not option.strip() for option in options):
        raise ValueError("gate options must be nonempty strings")
    if len(set(options)) != len(options):
        raise ValueError("gate options must be distinct")
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("an explicit human gate choice is required")
    choice = answer.strip()
    if choice.isdigit() and 1 <= int(choice) <= len(options):
        return options[int(choice) - 1]
    for option in options:
        if option.casefold() == choice.casefold():
            return option
    raise ValueError("human gate choice is not an allowed option")


def select_switch_branch(switch: dict[str, Any], choice: str) -> list[dict[str, Any]]:
    """Return only the branch selected by a validated gate result."""
    if not isinstance(switch, dict) or switch.get("type") != "switch":
        raise ValueError("branch selection requires a switch step")
    cases = switch.get("cases", {})
    if not isinstance(cases, dict) or not isinstance(choice, str):
        raise ValueError("switch cases or choice are invalid")
    branch = cases.get(choice, switch.get("default"))
    if not isinstance(branch, list):
        raise ValueError("switch has no branch for the selected choice")
    return branch


def activate_feature(project_root: Path, feature_directory: str) -> dict[str, Any]:
    """Activate an approved project-relative target without creating feature files."""
    project = project_root.resolve()
    if (not isinstance(feature_directory, str) or not feature_directory
            or Path(feature_directory).is_absolute() or "\\" in feature_directory
            or any(part in {"", ".", ".."} for part in feature_directory.split("/"))
            or feature_directory.split("/")[0] in {".git", ".specify"}):
        raise ValueError("feature_directory must be a normalized project-relative directory")
    target = project / feature_directory
    try:
        target.resolve().relative_to(project)
    except ValueError as error:
        raise ValueError("feature_directory escapes the project") from error
    if target.exists() and not target.is_dir():
        raise ValueError("feature_directory is not a directory")
    metadata = project / ".specify"
    pointer = metadata / "feature.json"
    if not metadata.is_dir() or metadata.is_symlink() or pointer.is_symlink():
        raise ValueError("activation requires a local initialized .specify directory and nonsymlink pointer")
    data = json.loads(pointer.read_text(encoding="utf-8")) if pointer.exists() else {}
    if not isinstance(data, dict):
        raise ValueError("active feature state must be a JSON object")
    previous = data.get("feature_directory")
    if "feature_directory" in data and (not isinstance(previous, str) or not previous):
        raise ValueError("existing feature_directory must be a nonempty string")
    if previous == feature_directory:
        return {"feature_directory": feature_directory, "previous_feature_directory": previous, "changed": False}
    data["feature_directory"] = feature_directory
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=metadata, prefix=".feature-", delete=False) as handle:
            temporary_path = Path(handle.name)
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.chmod(temporary_path, stat.S_IMODE(pointer.stat().st_mode) if pointer.exists() else 0o644)
        os.replace(temporary_path, pointer)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return {"feature_directory": feature_directory, "previous_feature_directory": previous, "changed": True}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect_parser = subparsers.add_parser("inspect", help="load an installed workflow without executing it")
    inspect_parser.add_argument("--project", type=Path, required=True)
    inspect_parser.add_argument("--workflow-id", required=True)
    inspect_parser.add_argument("--specify", type=Path, required=True)
    inspect_parser.add_argument("--expected-version", required=True)
    inspect_parser.add_argument("--skill-id", required=True)
    inspect_parser.add_argument("--input", action="append", default=[])
    question_parser = subparsers.add_parser("question", help="validate a structured child question from JSON on stdin")
    question_parser.add_argument("--step-id", required=True)
    answer_parser = subparsers.add_parser("answer", help="validate an answer and same-child relay from JSON on stdin")
    answer_parser.add_argument("--child-id", required=True)
    answer_parser.add_argument("--target-child-id", required=True)
    gate_parser = subparsers.add_parser("gate", help="validate an explicit gate verdict from JSON on stdin")
    branch_parser = subparsers.add_parser("branch", help="select only the chosen switch branch from JSON on stdin")
    assessment_parser = subparsers.add_parser("assessment", help="validate and route an assessment envelope from JSON on stdin")
    assessment_parser.add_argument("--project", type=Path, required=True)
    assessment_parser.add_argument("--loop-body-step", action="append", default=[])
    assessment_parser.add_argument("--human-gate-step", action="append", default=[])
    loop_route_parser = subparsers.add_parser("route-loop", help="route refreshed loop evidence from JSON on stdin")
    loop_route_parser.add_argument("--assessment-only-first-pass", action="store_true")
    loop_route_parser.add_argument("--assessment-before-correction", action="store_true")
    loop_route_parser.add_argument("--iteration", type=int, required=True)
    loop_route_parser.add_argument("--max-iterations", type=int, required=True)
    loop_route_parser.add_argument("--project", type=Path, required=True)
    loop_route_parser.add_argument("--loop-body-step", action="append", default=[])
    loop_route_parser.add_argument("--human-gate-step", action="append", default=[])
    condition_parser = subparsers.add_parser("loop-condition", help="evaluate the reviewed loop condition from JSON on stdin")
    condition_parser.add_argument("--condition", required=True)
    activate_parser = subparsers.add_parser("activate-feature", help="activate an approved directory without creating a spec")
    activate_parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "inspect":
        verify_controller_install(args.project, args.skill_id, args.workflow_id)
        output = subprocess.run([str(args.specify), "--version"], cwd=args.project, text=True, capture_output=True, check=True).stdout
        check_specify_version(output, args.expected_version)
        definition = load_installed_definition(args.project, args.workflow_id)
        validate_workflow_definition(definition)
        supplied_inputs = parse_key_values(args.input, argument_name="workflow input")
        definition["resolved_inputs"] = validate_required_inputs(definition, supplied_inputs)
        definition["agent_assignments"] = [item.to_dict() for item in collect_agent_assignments(definition["steps"])]
        definition["preflight_inputs_valid"] = True
        definition["installation_fingerprints"] = installation_fingerprints(args.project)
        print(json.dumps(definition, sort_keys=True))
        return 0
    payload = json.load(sys.stdin)
    if args.command == "activate-feature":
        result = activate_feature(args.project, payload["feature_directory"])
    elif args.command == "question":
        result = validate_child_question(payload, args.step_id)
    elif args.command == "answer":
        result = resolve_child_answer(payload["request"], payload["answer"], args.child_id, args.target_child_id)
    elif args.command == "gate":
        result = {"choice": validate_gate_choice(payload["gate"], payload["answer"])}
    elif args.command == "branch":
        result = {"steps": select_switch_branch(payload["switch"], payload["choice"])}
    elif args.command == "assessment":
        body_ids = set(args.loop_body_step)
        gate_ids = set(args.human_gate_step)
        outcome = validate_outcome_envelope(payload, args.project, body_ids, gate_ids)
        route = route_assessment(outcome, loop_body_step_ids=body_ids, human_gate_step_ids=gate_ids)
        result = {"outcome": outcome, "route": route}
    elif args.command == "route-loop":
        body_ids = set(args.loop_body_step)
        gate_ids = set(args.human_gate_step)
        outcome = validate_outcome_envelope(payload["assessment"], args.project, body_ids, gate_ids)
        previous = payload.get("previous_assessment")
        result = route_loop_assessment(
            outcome, iteration=args.iteration, max_iterations=args.max_iterations,
            loop_body_step_ids=body_ids, human_gate_step_ids=gate_ids,
            previous_assessment=previous,
            assessment_only_first_pass=args.assessment_only_first_pass,
            assessment_before_correction=args.assessment_before_correction,
        )
    elif args.command == "loop-condition":
        result = {"continue": evaluate_loop_condition(args.condition, payload.get("outputs", {}))}
    else:
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        print(f"FlowKit controller preflight failed: {error}", file=sys.stderr)
        raise SystemExit(1)

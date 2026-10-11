#!/usr/bin/env python3
"""Read and preflight an installed FarmBoy workflow for a Codex task."""

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

try:
    from selection import resolve_feature_reference
except ImportError:  # The package can also be imported by repository tests.
    resolve_feature_reference = None  # type: ignore[assignment]

try:
    from readiness import ReadinessError, assess as assess_readiness, record_review as record_readiness_review, recorder_error_report
except ImportError:  # The package can also be imported by repository tests.
    ReadinessError = ValueError  # type: ignore[assignment,misc]
    assess_readiness = None  # type: ignore[assignment]
    record_readiness_review = None  # type: ignore[assignment]
    recorder_error_report = None  # type: ignore[assignment]

try:
    from phase_lifecycle import LifecycleError, prepare as prepare_phase_lifecycle, revalidate as revalidate_phase_lifecycle, strict_json as strict_lifecycle_json, validate_receipt as validate_lifecycle_receipt, validate_recovery_start_history, workflow_check as workflow_lifecycle_check
except ImportError:  # The package can also be imported by repository tests.
    LifecycleError = ValueError  # type: ignore[assignment,misc]
    prepare_phase_lifecycle = None  # type: ignore[assignment]
    revalidate_phase_lifecycle = None  # type: ignore[assignment]
    strict_lifecycle_json = None  # type: ignore[assignment]
    validate_lifecycle_receipt = None  # type: ignore[assignment]
    validate_recovery_start_history = None  # type: ignore[assignment]
    workflow_lifecycle_check = None  # type: ignore[assignment]

try:
    import implementation_scope as implementation_scope_module
except ImportError:  # The package can also be imported by repository tests.
    implementation_scope_module = None  # type: ignore[assignment]


REVIEWED_AGENT_NAMES = {
    "FarmBoy Roadmap Agent", "FarmBoy Specifier", "FarmBoy Planner", "FarmBoy Tasker", "FarmBoy Reviewer",
    "FarmBoy Coder", "FarmBoy Code Reviewer", "FarmBoy Wiki Curator", "FarmBoy Readiness Checker",
}
INPUT_REFERENCE = re.compile(r"\{\{\s*inputs\.([A-Za-z0-9_-]+)\s*\}\}")
STEP_REFERENCE = re.compile(r"\{\{\s*steps\.([A-Za-z0-9_-]+)\.output\.([A-Za-z0-9_.-]+)\s*\}\}")
LOOP_CONDITION = re.compile(
    r"^\{\{\s*steps\.([A-Za-z0-9_-]+)\.output\.state\s*==\s*(['\"])continue\2"
    r"(?:\s*&&\s*steps\.([A-Za-z0-9_-]+)\.output\.readiness_gate\.state\s*==\s*(['\"])ready\4)?\s*\}\}$"
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
    def scoped_carriers(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        found = []
        for node in nodes:
            if node.get("controller_loop_mode") == "implementation_scope":
                found.append(node)
            for branch in node.get("cases", {}).values():
                found.extend(scoped_carriers(branch))
            found.extend(scoped_carriers(node.get("default", [])))
            found.extend(scoped_carriers(node.get("steps", [])))
        return found
    carriers = scoped_carriers(definition["steps"])
    if carriers and workflow["id"] != "farmboy-implement":
        raise ValueError("implementation_scope carrier is only supported by farmboy-implement")
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
    """Snapshot both Specify and FarmBoy installation records without writing."""
    root = Path(project_root)
    return {
        "bundle_record": file_fingerprint(root / ".specify/bundle-records.json"),
        "skill_record": file_fingerprint(root / ".specify/farmboy/skills-install.json"),
    }


def verify_controller_install(project_root: Path, skill_id: str, workflow_id: str) -> dict[str, Any]:
    """Verify the selected skill and shared helper against their ownership record."""
    project = Path(project_root)
    record_path = project / ".specify/farmboy/skills-install.json"
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"FarmBoy controller ownership record is missing or unreadable: {error}") from error
    if record.get("package") != "farmboy-controllers" or record.get("status") != "installed":
        raise ValueError("FarmBoy controller package is not in installed state")
    controllers = record.get("controllers")
    matches = [item for item in controllers or [] if item.get("skill_id") == skill_id]
    if len(matches) != 1 or matches[0].get("workflow_id") != workflow_id:
        raise ValueError("FarmBoy skill-to-workflow binding differs from the installed ownership record")
    owned_files = record.get("files")
    if not isinstance(owned_files, dict):
        raise ValueError("FarmBoy controller ownership file inventory is malformed")
    required = {
        f".agents/skills/{skill_id}/SKILL.md",
        f".agents/skills/{skill_id}/agents/openai.yaml",
        ".specify/farmboy/manifest.yml",
        ".specify/farmboy/controller-protocol.md",
        ".specify/farmboy/scripts/bootstrap.sh",
        ".specify/farmboy/scripts/python/controller.py",
        ".specify/farmboy/scripts/python/recovery.py",
    }
    for relative in required:
        expected = owned_files.get(relative)
        target = project / relative
        if not isinstance(expected, str) or not target.is_file():
            raise ValueError(f"FarmBoy owned controller file is missing: {relative}")
        observed = hashlib.sha256(target.read_bytes()).hexdigest()
        if observed != expected:
            raise ValueError(f"FarmBoy owned controller file was changed: {relative}")
    installed_manifest = (project / ".specify/farmboy/manifest.yml").read_text(encoding="utf-8")
    manifest_version = re.search(r'^  version:\s*["\']?([^"\'\n]+)', installed_manifest.split("package:\n", 1)[1], re.MULTILINE)
    if manifest_version is None or manifest_version.group(1).strip() != record.get("version"):
        raise ValueError("FarmBoy controller manifest version differs from the installation record")
    skill_text = (project / f".agents/skills/{skill_id}/SKILL.md").read_text(encoding="utf-8")
    declared_name = re.search(r"^name:\s*([^\n]+)", skill_text, re.MULTILINE)
    if declared_name is None or declared_name.group(1).strip() != skill_id:
        raise ValueError("installed FarmBoy skill frontmatter differs from its ID")
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
            if "controller_loop_mode" in node and (
                    kind != "do-while" or node.get("controller_loop_mode") != "implementation_scope"):
                raise ValueError("unsupported controller_loop_mode carrier or body")
            if kind == "command" and node.get("integration") not in (None, "codex", "{{ inputs.integration }}"):
                raise ValueError(f"unsupported command integration on step {step_id}")
            if "model" in node or "reasoning_effort" in node:
                raise ValueError(f"concrete model and effort settings are unsupported on step {step_id}; use a named Codex agent")
            if "agent" in node or "delegated" in node:
                raise ValueError(f"agent assignment on step {step_id} must use explicit farmboy metadata")
            assignment = node.get("farmboy")
            if "farmboy" in node:
                if kind not in {"prompt", "command"}:
                    raise ValueError(f"agent delegation is not allowed on {kind} step {step_id}")
                if not isinstance(assignment, dict) or set(assignment) != {"delegated", "agent"} or assignment.get("delegated") is not True:
                    raise ValueError(f"farmboy metadata must explicitly delegate step {step_id}")
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
                loop_mode = node.get("controller_loop_mode")
                if loop_mode == "implementation_scope" and (
                        not isinstance(condition, str)
                        or condition.strip() != '{{ steps.route-scoped-execution.output.state == "continue" }}'):
                    raise ValueError("implementation_scope must route its actual post-source assessment with the exact route-scoped-execution condition")
                if node.get("assessment_before_correction") and not isinstance(condition, str):
                    raise ValueError("assessment_before_correction requires an assessment condition")
                if not isinstance(condition, bool):
                    if not isinstance(condition, str) or LOOP_CONDITION.fullmatch(condition.strip()) is None:
                        raise ValueError(f"do-while condition is unsupported or incomplete: {step_id}")
                if isinstance(maximum, bool) or not isinstance(maximum, int) or maximum < 1:
                    raise ValueError(f"do-while max_iterations must be a positive integer: {step_id}")
                if not isinstance(body, list) or not body:
                    raise ValueError(f"do-while steps must be a nonempty list: {step_id}")
                if loop_mode is not None:
                    expected_body = ["route-scoped-entry", "prepare-scoped-prerequisites", "implement-tasks",
                                     "assess-implementation-after-pass", "route-post-assessment",
                                     "capture-post-pass-state", "route-scoped-execution"]
                    if (loop_mode != "implementation_scope" or step_id != "implementation-loop"
                            or maximum != 5
                            or "assessment_only_first_pass" in node
                            or "assessment_before_correction" in node
                            or [item.get("id") for item in body if isinstance(item, dict)] != expected_body
                            or len(body) != len(expected_body)):
                        raise ValueError("unsupported controller_loop_mode carrier or body")
                    # The scoped carrier is specific to the reviewed Implement workflow.
                    # Other generic loops retain their existing validation semantics.
                if isinstance(condition, str):
                    match = LOOP_CONDITION.fullmatch(condition.strip())
                    assessment_id = match.group(1) if match is not None else None
                    body_ids = {item.get("id") for item in body if isinstance(item, dict)}
                    def contains_step(nodes: list[dict[str, Any]], expected: str) -> bool:
                        for candidate in nodes:
                            if candidate.get("id") == expected:
                                return True
                            if any(contains_step(branch, expected) for branch in candidate.get("cases", {}).values()):
                                return True
                            if contains_step(candidate.get("default", []), expected):
                                return True
                            if contains_step(candidate.get("steps", []), expected):
                                return True
                        return False

                    if assessment_id not in body_ids and not contains_step(body, assessment_id or ""):
                        raise ValueError(f"do-while condition must reference an in-body assessment step: {step_id}")
                    assessor = next((item for item in body if isinstance(item, dict) and item.get("id") == assessment_id), None)
                    if loop_mode == "implementation_scope":
                        if (assessment_id != "route-scoped-execution"
                                or condition.strip() != '{{ steps.route-scoped-execution.output.state == "continue" }}'
                                or _node_kind(body[-1]) != "prompt"
                                or body[-1].get("id") != "route-scoped-execution"
                                or "farmboy" in body[-1]
                                or any(key in body[-1] for key in ("agent", "model", "reasoning_effort"))
                                or not contains_step(body, "route-post-assessment")):
                            raise ValueError("implementation_scope must route its actual post-source assessment")
                        readiness_gate_id = match.group(3)
                        if readiness_gate_id is not None and not contains_step(body, readiness_gate_id):
                            raise ValueError("implementation_scope readiness gate is not in its loop body")
                    elif node.get("assessment_before_correction"):
                        if assessor is None:
                            raise ValueError(f"assessment_before_correction assessor must be top-level: {step_id}")
                        if (len(body) != 3 or _node_kind(body[0]) != "command" or assessor is not body[1]
                                or _node_kind(assessor) != "prompt" or _node_kind(body[2]) != "switch"
                                or body[2].get("expression") != "{{ steps." + assessment_id + ".output.state }}"
                                or set(body[2].get("cases", {})) not in (
                                    {"continue", "complete", "blocked"},
                                    {"continue", "complete", "needs-human", "blocked"})
                                or any(body[2]["cases"].get(state) for state in ("complete", "needs-human", "blocked"))
                                or body[2].get("default")):
                            raise ValueError(f"assessment_before_correction requires command, assessment, and guarded correction: {step_id}")
                        readiness_gate_id = match.group(3)
                        if readiness_gate_id is not None:
                            continue_nodes = body[2]["cases"].get("continue", [])

                            def contains_id(nodes: list[dict[str, Any]], expected: str) -> bool:
                                for candidate in nodes:
                                    if candidate.get("id") == expected:
                                        return True
                                    if any(contains_id(branch, expected) for branch in candidate.get("cases", {}).values()):
                                        return True
                                    if contains_id(candidate.get("default", []), expected):
                                        return True
                                return False

                            if not contains_id(continue_nodes, readiness_gate_id):
                                raise ValueError(
                                    f"readiness loop condition gate must be in the continue branch: {step_id}"
                                )
                    elif assessor is not body[-1] or _node_kind(assessor) not in {"prompt", "command"}:
                        raise ValueError(f"do-while condition must reference the final fresh assessment step: {step_id}")
                visit(body, inside_loop=True)

    if not isinstance(steps, list):
        raise ValueError("workflow steps must be a list")
    visit(steps)


def evaluate_loop_condition(condition: str | bool, outputs: dict[str, dict[str, Any]]) -> bool:
    """Evaluate reviewed assessment continuation and optional readiness gate."""
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
    if outputs[step_id]["state"] != "continue":
        return False
    readiness_gate_id = match.group(3)
    if readiness_gate_id is None:
        return True
    gate_output = outputs.get(readiness_gate_id)
    if not isinstance(gate_output, dict) or not isinstance(gate_output.get("readiness_gate"), dict):
        raise ValueError(f"unresolved do-while readiness gate output: {readiness_gate_id}.readiness_gate.state")
    return gate_output["readiness_gate"].get("state") == "ready"


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
            assignment = step.get("farmboy")
            if "farmboy" in step:
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

    substitutions: list[tuple[str, str]] = []

    def protect_replacement(replacement: str) -> str:
        marker = f"\x00FARMBOY_RENDER_{len(substitutions)}\x00"
        substitutions.append((marker, replacement))
        return marker

    def input_value(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in inputs:
            raise ValueError(f"unresolved input reference: {name}")
        return protect_replacement(str(inputs[name]))

    rendered = INPUT_REFERENCE.sub(input_value, value)

    def output_value(match: re.Match[str]) -> str:
        step_id, key_path = match.groups()
        current: Any = outputs.get(step_id)
        for key in key_path.split("."):
            if not isinstance(current, dict) or key not in current:
                raise ValueError(f"unresolved step output reference: {step_id}.{key_path}")
            current = current[key]
        rendered_value = (json.dumps(current, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                          if isinstance(current, (dict, list)) else str(current))
        return protect_replacement(rendered_value)

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
    for marker, replacement in substitutions:
        rendered = rendered.replace(marker, replacement)
    return rendered


def installed_skill_name(command_id: str) -> str:
    """Apply the pinned Specify command-to-skill naming rule."""
    return command_id.replace(".", "-")


def _parse_unique_yaml(text: str, description: str) -> Any:
    """Parse YAML while rejecting duplicate keys and malformed documents."""
    try:
        import yaml
    except ImportError as error:  # pragma: no cover - runtime dependency is supplied by Specify.
        raise ValueError(f"YAML support is required to validate {description}") from error

    class UniqueKeyLoader(yaml.SafeLoader):
        pass

    def construct_mapping(loader: Any, node: Any, deep: bool = False) -> dict[Any, Any]:
        mapping: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in mapping:
                raise ValueError(f"{description} contains a duplicate YAML key")
            mapping[key] = loader.construct_object(value_node, deep=deep)
        return mapping

    UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
    try:
        return yaml.load(text, Loader=UniqueKeyLoader)
    except (TypeError, yaml.YAMLError, ValueError) as error:
        raise ValueError(f"{description} is malformed") from error


def _load_unique_yaml(path: Path, description: str) -> Any:
    """Load YAML while rejecting duplicate keys and malformed documents."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ValueError(f"{description} is malformed") from error
    return _parse_unique_yaml(text, description)


def _contained_regular_file(project: Path, relative: str, description: str) -> Path:
    """Resolve a project-relative regular file without symlinked path components."""
    candidate_relative = Path(relative)
    if candidate_relative.is_absolute() or not relative or "\\" in relative or any(part in {"", ".", ".."} for part in relative.split("/")):
        raise ValueError(f"{description} path is unsafe")
    candidate = project
    for component in candidate_relative.parts:
        candidate = candidate / component
        if candidate.is_symlink():
            raise ValueError(f"{description} path contains a symlink")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(project)
    except (OSError, ValueError) as error:
        raise ValueError(f"{description} path escapes the project or is missing") from error
    if not resolved.is_file():
        raise ValueError(f"{description} is not a regular file")
    return resolved


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build a JSON object while rejecting duplicate keys at every nesting level."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON object contains a duplicate key")
        result[key] = value
    return result


def _extension_command_owner(project: Path, command_id: str) -> dict[str, str] | None:
    """Validate and describe a unique enabled registered Codex extension owner."""
    registry_path = project / ".specify/extensions/.registry"
    for directory in (project / ".specify", project / ".specify/extensions"):
        if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
            raise ValueError("selected project's extension registry path is unsafe")
    if registry_path.is_symlink():
        raise ValueError("selected project's extension registry is unsafe")
    if not registry_path.exists():
        return None
    if not registry_path.is_file():
        raise ValueError("selected project's extension registry is unsafe")
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"), object_pairs_hook=_unique_json_object)
    except (OSError, UnicodeError, ValueError) as error:
        raise ValueError("selected project's extension registry is malformed") from error
    if not isinstance(registry, dict) or registry.get("schema_version") != "1.0" or not isinstance(registry.get("extensions"), dict):
        raise ValueError("selected project's extension registry is malformed")

    matches: list[tuple[str, dict[str, Any]]] = []
    for extension_id, record in registry["extensions"].items():
        if not isinstance(extension_id, str) or not isinstance(record, dict):
            raise ValueError("selected project's extension registry is malformed")
        commands = record.get("registered_commands")
        if commands is None:
            continue
        if not isinstance(commands, dict):
            raise ValueError("selected project's extension registry is malformed")
        codex_commands = commands.get("codex", [])
        if not isinstance(codex_commands, list) or any(not isinstance(item, str) for item in codex_commands):
            raise ValueError("selected project's extension registry is malformed")
        if len(codex_commands) != len(set(codex_commands)):
            raise ValueError("selected project's extension registry contains duplicate commands")
        if command_id in codex_commands:
            matches.append((extension_id, record))
    if not matches:
        return None
    if len(matches) != 1:
        raise ValueError(f"ambiguous registered Codex extension owner for {command_id}")

    extension_id, record = matches[0]
    if record.get("enabled") is not True:
        raise ValueError(f"registered Codex extension owner is disabled for {command_id}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", extension_id):
        raise ValueError("registered extension ID is invalid")
    version = record.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("registered extension version is missing")
    manifest_hash = record.get("manifest_hash")
    hash_match = re.fullmatch(r"sha256:([0-9a-f]{64})", manifest_hash) if isinstance(manifest_hash, str) else None
    if hash_match is None:
        raise ValueError("registered extension manifest hash is missing or malformed")

    manifest_relative = f".specify/extensions/{extension_id}/extension.yml"
    manifest_path = _contained_regular_file(project, manifest_relative, "registered extension manifest")
    manifest_digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    if manifest_digest != hash_match.group(1):
        raise ValueError(f"registered extension manifest hash differs from installed bytes: {extension_id}")
    manifest = _load_unique_yaml(manifest_path, "registered extension manifest")
    if not isinstance(manifest, dict):
        raise ValueError("registered extension manifest is malformed")
    identity = manifest.get("extension")
    if not isinstance(identity, dict) or identity.get("id") != extension_id or identity.get("version") != version:
        raise ValueError("registered extension identity or version differs from its manifest")
    provides = manifest.get("provides")
    declarations = provides.get("commands") if isinstance(provides, dict) else None
    if not isinstance(declarations, list):
        raise ValueError("registered extension command declarations are malformed")
    command_matches = [item for item in declarations if isinstance(item, dict) and item.get("name") == command_id]
    if len(command_matches) != 1:
        raise ValueError(f"registered extension does not declare exactly one command named {command_id}")
    source_relative = command_matches[0].get("file")
    if not isinstance(source_relative, str):
        raise ValueError("registered extension command source path is malformed")
    source_path = _contained_regular_file(project, f".specify/extensions/{extension_id}/{source_relative}", "registered extension command source")

    return {
        "owner_id": extension_id,
        "owner_version": version,
        "manifest_path": manifest_relative,
        "manifest_sha256": manifest_digest,
        "command_source_relative": source_relative,
        "command_source_path": source_path.relative_to(project).as_posix(),
        "command_source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
    }


def _skill_frontmatter(skill_file: Path) -> dict[str, Any]:
    """Read one YAML frontmatter document from an installed skill."""
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("installed Codex skill has no YAML frontmatter")
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as error:
        raise ValueError("installed Codex skill has unterminated YAML frontmatter") from error
    # Parse in memory using the same duplicate-key-safe loader without creating files.
    value = _parse_unique_yaml("\n".join(lines[1:end]), "installed Codex skill frontmatter")
    if not isinstance(value, dict):
        raise ValueError("installed Codex skill frontmatter is malformed")
    return value


def _registered_extension_provenance(owner: dict[str, str], frontmatter: dict[str, Any], skill_digest: str, expected_name: str) -> dict[str, str]:
    """Bind an installed skill to its declared extension command and report limits."""
    metadata = frontmatter.get("metadata")
    source = metadata.get("source") if isinstance(metadata, dict) else None
    source_relative = owner["command_source_relative"]
    if source != f"{owner['owner_id']}:{source_relative}":
        raise ValueError(f"installed Codex skill source metadata differs from its registered owner: {expected_name}")
    return {
        "provenance": "registered-extension",
        "owner_id": owner["owner_id"],
        "owner_version": owner["owner_version"],
        "manifest_path": owner["manifest_path"],
        "manifest_sha256": owner["manifest_sha256"],
        "command_source_path": owner["command_source_path"],
        "command_source_sha256": owner["command_source_sha256"],
        "skill_sha256": skill_digest,
        "integrity_limit": "registered ownership and observed digests; rendered skill body equality is not verified",
    }


def resolve_installed_skill(project_root: Path, command_id: str) -> dict[str, str]:
    """Find one project-local Codex skill and validate its available owner provenance."""
    expected_name = installed_skill_name(command_id)
    project = Path(project_root).resolve(strict=True)
    roots = [project / ".agents/skills", project / ".codex/skills"]
    matches: list[Path] = []
    for root in roots:
        candidate = root / expected_name / "SKILL.md"
        if candidate.exists():
            relative = candidate.relative_to(project).as_posix()
            matches.append(_contained_regular_file(project, relative, "installed Codex skill"))
    if not matches:
        raise ValueError(f"installed Codex command skill not found: {expected_name}")
    if len(matches) > 1:
        raise ValueError(f"ambiguous installed Codex command skill: {expected_name}")
    skill_file = matches[0]
    frontmatter = _skill_frontmatter(skill_file)
    if frontmatter.get("name") != expected_name:
        raise ValueError(f"installed Codex skill declares a different name: {expected_name}")
    project_relative = skill_file.relative_to(project).as_posix()
    actual_digest = hashlib.sha256(skill_file.read_bytes()).hexdigest()
    provenance: dict[str, str] | None = None
    manifest_path = project / ".specify/integrations/codex.manifest.json"
    for directory in (project / ".specify", project / ".specify/integrations"):
        if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
            raise ValueError("core Codex provenance manifest path is unsafe")
    if manifest_path.is_symlink():
        raise ValueError("core Codex provenance manifest path is unsafe")
    if manifest_path.exists():
        manifest_path = _contained_regular_file(project, ".specify/integrations/codex.manifest.json", "core Codex provenance manifest")
        try:
            integration_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ValueError("selected project's Codex skill provenance manifest is malformed") from error
        if not isinstance(integration_manifest, dict) or not isinstance(integration_manifest.get("files"), dict):
            raise ValueError("selected project's Codex skill provenance manifest is malformed")
        owned_files = integration_manifest["files"]
        if project_relative in owned_files:
            recorded_digest = owned_files[project_relative]
            if not isinstance(recorded_digest, str) or not SHA256.fullmatch(recorded_digest):
                raise ValueError(f"selected project's Codex manifest has malformed skill provenance: {expected_name}")
            if recorded_digest != actual_digest:
                raise ValueError(f"installed Codex command skill differs from its provenance record: {expected_name}")
            provenance = {"provenance": "codex.manifest.json", "skill_sha256": actual_digest}
        else:
            owner = _extension_command_owner(project, command_id)
            if owner is None:
                raise ValueError(f"selected project's Codex manifest has no skill provenance: {expected_name}")
            provenance = _registered_extension_provenance(owner, frontmatter, actual_digest, expected_name)
    else:
        owner = _extension_command_owner(project, command_id)
        if owner is not None:
            provenance = _registered_extension_provenance(owner, frontmatter, actual_digest, expected_name)
        else:
            metadata = frontmatter.get("metadata")
            source = metadata.get("source") if isinstance(metadata, dict) else None
            if isinstance(source, str) and ":" in source:
                raise ValueError(f"installed Codex skill declares an owner without an active registration: {expected_name}")
            provenance = {"provenance": "unrecorded", "skill_sha256": actual_digest}
    return {"name": expected_name, "path": str(skill_file), "command_id": command_id, **provenance}


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


def _normalized_mapping_target(project: Path, directory: str) -> Path:
    """Resolve a safe project-relative mapping to its physical target identity."""
    if (not directory or Path(directory).is_absolute() or "\\" in directory
            or any(part in {"", ".", ".."} for part in directory.split("/"))
            or directory.split("/")[0] in {".git", ".specify"}):
        raise ValueError("feature mapping is not a safe project-relative directory")
    target = (project / directory).resolve(strict=False)
    target.relative_to(project.resolve())
    return target


def _write_absent_feature_pointer(project: Path, feature_directory: str) -> dict[str, Any]:
    """Create the first active pointer without replacing a concurrently created file."""
    metadata = project / ".specify"
    pointer = metadata / "feature.json"
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=metadata,
                                         prefix=".feature-", delete=False) as handle:
            temporary_path = Path(handle.name)
            json.dump({"feature_directory": feature_directory}, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary_path, 0o644)
        os.link(temporary_path, pointer)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return {"feature_directory": feature_directory, "previous_feature_directory": None, "changed": True}


def _selection_blocked(selected_entry_id: str | None, reason_code: str) -> dict[str, Any]:
    return {"state": "blocked", "selected_entry_id": selected_entry_id, "reason_code": reason_code}


def prepare_feature_activation(project_root: Path, snapshot: dict[str, Any]) -> dict[str, Any]:
    """Validate a selected roadmap snapshot without changing project state."""
    project = project_root.resolve()
    if not isinstance(snapshot, dict):
        return _selection_blocked(None, "selection-snapshot-invalid")
    entries = snapshot.get("entries")
    selected_id = snapshot.get("selected_entry_id")
    if not isinstance(entries, list) or not isinstance(selected_id, str):
        return _selection_blocked(None, "selection-snapshot-invalid")
    if selected_id.isdigit():
        selected_id = str(int(selected_id)).zfill(max(3, len(selected_id)))
    ids: dict[str, dict[str, Any]] = {}
    mapping_owners: dict[Path, list[str]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            return _selection_blocked(selected_id, "feature-inventory-invalid")
        entry_id = entry.get("id", entry.get("entry_id"))
        title = entry.get("title")
        status = entry.get("status")
        directory = entry.get("feature_directory")
        dependencies = entry.get("dependency_ids", [])
        if (not isinstance(entry_id, str) or not entry_id.isdigit() or not isinstance(title, str)
                or not title.strip() or not isinstance(status, str) or not isinstance(dependencies, list)
                or any(not isinstance(item, str) for item in dependencies)):
            return _selection_blocked(selected_id, "feature-inventory-invalid")
        canonical_id = str(int(entry_id)).zfill(max(3, len(entry_id)))
        if canonical_id in ids:
            return _selection_blocked(selected_id, "feature-inventory-duplicate-id")
        ids[canonical_id] = entry
        if directory is not None:
            if not isinstance(directory, str):
                return _selection_blocked(selected_id, "feature-mapping-invalid")
            try:
                normalized_target = _normalized_mapping_target(project, directory)
            except (OSError, RuntimeError, ValueError):
                return _selection_blocked(selected_id, "feature-mapping-unsafe")
            mapping_owners.setdefault(normalized_target, []).append(canonical_id)
    if selected_id not in ids:
        return _selection_blocked(selected_id, "selected-feature-missing")
    selected = ids[selected_id]
    directory = selected.get("feature_directory")
    try:
        normalized_directory = _normalized_mapping_target(project, directory) if isinstance(directory, str) else None
    except (OSError, RuntimeError, ValueError):
        return _selection_blocked(selected_id, "feature-mapping-unsafe")
    if normalized_directory is None or mapping_owners.get(normalized_directory) != [selected_id]:
        return _selection_blocked(selected_id, "feature-mapping-not-unique")
    target = project / directory
    if target.exists() and not target.is_dir():
        return _selection_blocked(selected_id, "feature-mapping-not-directory")
    status = selected["status"].casefold()
    if status in {"abandoned", "deferred", "complete", "completed"}:
        return _selection_blocked(selected_id, "feature-lifecycle-not-selectable")
    if status not in {"planned", "specced", "in-progress", "verified"}:
        return _selection_blocked(selected_id, "feature-lifecycle-unknown")

    visited: set[str] = set()
    active: set[str] = set()

    def verify_dependencies(entry_id: str) -> str | None:
        if entry_id in active:
            return "feature-dependency-cycle"
        if entry_id in visited:
            return None
        active.add(entry_id)
        entry = ids[entry_id]
        dependencies = entry.get("dependency_ids", [])
        for dependency in dependencies:
            canonical_dependency = str(int(dependency)).zfill(max(3, len(dependency))) if dependency.isdigit() else dependency
            if canonical_dependency not in ids:
                return "feature-dependency-missing"
            if ids[canonical_dependency].get("status", "").casefold() != "verified":
                return "feature-dependency-unmet"
            problem = verify_dependencies(canonical_dependency)
            if problem:
                return problem
        active.remove(entry_id)
        visited.add(entry_id)
        return None

    dependency_problem = verify_dependencies(selected_id)
    if dependency_problem:
        return _selection_blocked(selected_id, dependency_problem)

    spec_path = target / "spec.md"
    actual_spec_digest = None
    if spec_path.is_symlink():
        return _selection_blocked(selected_id, "feature-spec-symlink")
    if spec_path.exists():
        if not spec_path.is_file():
            return _selection_blocked(selected_id, "feature-spec-invalid")
        try:
            actual_spec_digest = hashlib.sha256(spec_path.read_bytes()).hexdigest()
        except OSError:
            return _selection_blocked(selected_id, "feature-spec-unavailable")
        expected_digest = selected.get("spec_sha256")
        if expected_digest != actual_spec_digest:
            return _selection_blocked(selected_id, "feature-spec-snapshot-stale")
    elif selected.get("spec_sha256") is not None:
        return _selection_blocked(selected_id, "feature-spec-snapshot-stale")
    elif status in {"specced", "in-progress", "verified"}:
        return _selection_blocked(selected_id, "feature-spec-required-by-lifecycle")

    roadmap_path = snapshot.get("roadmap_path")
    roadmap_digest = snapshot.get("roadmap_sha256")
    pointer_path = project / ".specify/feature.json"
    if (not isinstance(roadmap_path, str) or Path(roadmap_path).is_absolute() or "\\" in roadmap_path
            or any(part in {"", ".", ".."} for part in roadmap_path.split("/"))
            or not isinstance(roadmap_digest, str) or not SHA256.fullmatch(roadmap_digest)):
        return _selection_blocked(selected_id, "selection-source-snapshot-invalid")
    roadmap_file = project / roadmap_path
    metadata = project / ".specify"
    if metadata.is_symlink() or pointer_path.is_symlink() or roadmap_file.is_symlink():
        return _selection_blocked(selected_id, "selection-source-symlink")
    try:
        roadmap_file.resolve().relative_to(project)
        pointer_path.resolve().relative_to(project)
        roadmap_bytes = roadmap_file.read_bytes()
        pointer_bytes = pointer_path.read_bytes() if pointer_path.exists() else None
    except (OSError, RuntimeError, ValueError):
        return _selection_blocked(selected_id, "selection-source-unavailable")
    if hashlib.sha256(roadmap_bytes).hexdigest() != roadmap_digest:
        return _selection_blocked(selected_id, "selection-roadmap-snapshot-stale")
    pointer_snapshot = snapshot.get("pointer_snapshot")
    if not isinstance(pointer_snapshot, dict) or set(pointer_snapshot) != {"state", "sha256"}:
        return _selection_blocked(selected_id, "selection-pointer-snapshot-invalid")
    pointer_digest = pointer_snapshot.get("sha256")
    if pointer_bytes is None:
        if pointer_snapshot != {"state": "absent", "sha256": None}:
            return _selection_blocked(selected_id, "selection-pointer-snapshot-stale")
    elif (pointer_snapshot.get("state") != "present" or not isinstance(pointer_digest, str)
          or hashlib.sha256(pointer_bytes).hexdigest() != pointer_digest):
        return _selection_blocked(selected_id, "selection-pointer-snapshot-stale")
    if pointer_bytes is None:
        pointer = {}
    else:
        try:
            pointer = json.loads(pointer_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return _selection_blocked(selected_id, "active-feature-pointer-malformed")
    if not isinstance(pointer, dict):
        return _selection_blocked(selected_id, "active-feature-pointer-malformed")
    previous = pointer.get("feature_directory")
    if previous is not None and (not isinstance(previous, str) or not previous):
        return _selection_blocked(selected_id, "active-feature-pointer-malformed")
    if previous is not None and previous != directory:
        try:
            previous_target = _normalized_mapping_target(project, previous)
        except (OSError, RuntimeError, ValueError):
            return _selection_blocked(selected_id, "active-feature-pointer-unmapped")
        if previous_target not in mapping_owners:
            return _selection_blocked(selected_id, "active-feature-pointer-unmapped")
    return {
        "state": "ready", "selected_entry_id": selected_id, "feature_directory": directory,
        "lifecycle_status": selected["status"], "existing_spec": spec_path.is_file(),
        "spec_sha256": actual_spec_digest, "pointer": pointer,
    }


def activate_selected_feature(project_root: Path, snapshot: dict[str, Any]) -> dict[str, Any]:
    """Revalidate a prepared selection immediately before atomic pointer activation."""
    proposal = prepare_feature_activation(project_root, snapshot)
    if proposal["state"] != "ready":
        return proposal
    # Repeat the full snapshot check immediately before effect. First activation uses
    # exclusive link creation so an intervening writer is never overwritten.
    current = prepare_feature_activation(project_root, snapshot)
    if current["state"] != "ready":
        return current
    pointer = Path(project_root) / ".specify/feature.json"
    if snapshot["pointer_snapshot"]["state"] == "absent":
        result = _write_absent_feature_pointer(Path(project_root).resolve(), proposal["feature_directory"])
    else:
        result = activate_feature(project_root, proposal["feature_directory"])
    current_pointer = pointer.read_bytes()
    verified = prepare_feature_activation(project_root, {
        **snapshot,
        "pointer_snapshot": {"state": "present", "sha256": hashlib.sha256(current_pointer).hexdigest()},
    })
    if verified["state"] != "ready":
        return _selection_blocked(proposal["selected_entry_id"], "activation-postcondition-failed")
    return {
        "state": "complete", "selected_entry_id": proposal["selected_entry_id"],
        "feature_directory": proposal["feature_directory"], "lifecycle_status": proposal["lifecycle_status"],
        "existing_spec": proposal["existing_spec"], "activation": result,
    }


TASK_LINE = re.compile(r"^- \[([ xX])\] (T[0-9]{3}) (.+)$")

def _valid_finding_id(value: Any) -> bool:
    """Treat finding IDs as opaque, nonblank identities across correction helpers."""
    return isinstance(value, str) and bool(value.strip())


def _task_records(contents: str) -> dict[str, tuple[str, str]]:
    """Extract task checkbox lines by stable ID while rejecting duplicates."""
    records: dict[str, tuple[str, str]] = {}
    for line in contents.splitlines():
        match = TASK_LINE.fullmatch(line)
        if match is None:
            continue
        marker, task_id, description = match.groups()
        if task_id in records:
            raise ValueError(f"duplicate task ID: {task_id}")
        records[task_id] = (marker, description)
    return records


def task_revision_scope_digest(feature_directory: str, tasks_path: str, frozen_scope: dict[str, Any]) -> str:
    """Return the stable digest a main-controller semantic review must bind to."""
    findings = frozen_scope.get("findings")
    eligible_owners = frozen_scope.get("eligible_task_owners")
    approved_specification_sha256 = frozen_scope.get("approved_specification_sha256")
    if (not feature_directory or Path(feature_directory).is_absolute() or "\\" in feature_directory
            or any(part in {"", ".", ".."} for part in feature_directory.split("/"))
            or tasks_path != f"{feature_directory}/tasks.md"
            or not isinstance(findings, list) or not findings
            or any(not isinstance(item, dict) or not isinstance(item.get("id"), str)
                   or not _valid_finding_id(item["id"])
                   or not isinstance(item.get("exact_correction"), str)
                   or not item["exact_correction"].strip() for item in findings)
            or len({item["id"] for item in findings}) != len(findings)
            or not isinstance(eligible_owners, dict)
            or not isinstance(approved_specification_sha256, str)
            or re.fullmatch(r"[0-9a-f]{64}", approved_specification_sha256) is None
            or any(not isinstance(task_id, str) or re.fullmatch(r"T[0-9]{3}", task_id) is None
                   or owner != "FarmBoy Tasker" for task_id, owner in eligible_owners.items())
            or frozen_scope.get("permitted_added_task_owner") != "FarmBoy Tasker"
            or frozen_scope.get("tasker_owner") != "FarmBoy Tasker"):
        raise ValueError("invalid frozen task revision scope")
    return hashlib.sha256(json.dumps({
        "feature_directory": feature_directory,
        "tasks_path": tasks_path,
        "findings": frozen_scope.get("findings"),
        "eligible_task_owners": frozen_scope.get("eligible_task_owners"),
        "approved_specification_sha256": approved_specification_sha256,
        "permitted_added_task_owner": frozen_scope.get("permitted_added_task_owner"),
        "tasker_owner": frozen_scope.get("tasker_owner"),
    }, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def task_revision_preflight(
    project_root: Path,
    feature_directory: str,
    tasks_path: str,
    expected_tasks_sha256: str | None = None,
    expected_specification_sha256: str | None = None,
) -> dict[str, Any]:
    """Verify selected-feature identity and safe task paths before reading task bytes."""
    project = Path(project_root).resolve()
    if (not isinstance(feature_directory, str) or not feature_directory
            or Path(feature_directory).is_absolute() or "\\" in feature_directory
            or any(part in {"", ".", ".."} for part in feature_directory.split("/"))
            or not isinstance(tasks_path, str)
            or tasks_path != f"{feature_directory}/tasks.md"):
        return {"state": "blocked", "reason_code": "task-revision-path-out-of-scope"}
    lexical_feature = project / feature_directory
    lexical_tasks = project / tasks_path
    lexical_specification = project / feature_directory / "spec.md"
    pointer_path = project / ".specify/feature.json"
    try:
        for candidate in (pointer_path, lexical_feature, lexical_tasks, lexical_specification):
            try:
                relative_candidate = candidate.relative_to(project)
            except ValueError:
                return {"state": "blocked", "reason_code": "task-revision-path-out-of-scope"}
            current = project
            for part in relative_candidate.parts:
                current = current / part
                if current.is_symlink():
                    return {"state": "blocked", "reason_code": "task-revision-path-symlink"}
        if pointer_path.is_symlink():
            return {"state": "blocked", "reason_code": "task-revision-pointer-symlink"}
        pointer_bytes = pointer_path.read_bytes()
        pointer = json.loads(pointer_bytes)
        if not isinstance(pointer, dict) or pointer.get("feature_directory") != feature_directory:
            return {"state": "blocked", "reason_code": "task-revision-feature-identity-changed"}
        physical_feature = lexical_feature.resolve(strict=True)
        physical_tasks = lexical_tasks.resolve(strict=True)
        physical_specification = lexical_specification.resolve(strict=True)
        physical_feature.relative_to(project)
        physical_tasks.relative_to(physical_feature)
        physical_specification.relative_to(physical_feature)
        if (physical_tasks != physical_feature / "tasks.md" or not physical_tasks.is_file()
                or physical_specification != physical_feature / "spec.md" or not physical_specification.is_file()):
            return {"state": "blocked", "reason_code": "task-revision-path-out-of-scope"}
        # Path ancestry and active identity are checked before the selected task file
        # is opened. The second call supplies an expected digest immediately before
        # delegation and rejects any intervening task or identity change.
        tasks_bytes = physical_tasks.read_bytes()
        tasks_sha256 = hashlib.sha256(tasks_bytes).hexdigest()
        if expected_tasks_sha256 is not None and tasks_sha256 != expected_tasks_sha256:
            return {"state": "blocked", "reason_code": "task-revision-digest-mismatch"}
        specification_bytes = physical_specification.read_bytes()
        specification_sha256 = hashlib.sha256(specification_bytes).hexdigest()
        if (expected_specification_sha256 is not None
                and specification_sha256 != expected_specification_sha256):
            return {"state": "blocked", "reason_code": "task-revision-specification-changed"}
        return {
            "state": "ready", "feature_directory": feature_directory,
            "tasks_path": tasks_path, "tasks_before_text": tasks_bytes.decode("utf-8"),
            "tasks_before_sha256": tasks_sha256,
            "specification_sha256": specification_sha256,
            "specification_text": specification_bytes.decode("utf-8"),
            "pointer_sha256": hashlib.sha256(pointer_bytes).hexdigest(),
        }
    except FileNotFoundError:
        return {"state": "blocked", "reason_code": "task-revision-path-missing"}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RuntimeError, ValueError):
        return {"state": "blocked", "reason_code": "task-revision-path-validation-failed"}


def validate_task_revision(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Validate a bounded Tasker edit against active identity, digest, and task history."""
    project = Path(project_root).resolve()
    if not isinstance(payload, dict):
        return {"state": "blocked", "reason_code": "task-revision-payload-invalid"}
    feature_directory = payload.get("feature_directory")
    expected_path = payload.get("tasks_path")
    before_text = payload.get("tasks_before_text")
    result = payload.get("tasker_result")
    frozen_scope = payload.get("frozen_scope")
    semantic_review = payload.get("semantic_review")
    if (not isinstance(feature_directory, str) or not isinstance(expected_path, str)
            or not isinstance(before_text, str) or not isinstance(result, dict)
            or not isinstance(frozen_scope, dict) or not isinstance(semantic_review, dict)):
        return {"state": "blocked", "reason_code": "task-revision-payload-invalid"}
    try:
        if (not feature_directory or Path(feature_directory).is_absolute() or "\\" in feature_directory
                or any(part in {"", ".", ".."} for part in feature_directory.split("/"))
                or expected_path != f"{feature_directory}/tasks.md"):
            return {"state": "blocked", "reason_code": "task-revision-path-out-of-scope"}
        lexical_feature = project / feature_directory
        lexical_task_path = project / expected_path
        # Inspect each lexical component before resolve(): Path.resolve() erases the
        # symlink evidence needed to reject a cross-feature alias safely.
        for candidate in (lexical_feature, lexical_task_path):
            try:
                relative_candidate = candidate.relative_to(project)
            except ValueError:
                return {"state": "blocked", "reason_code": "task-revision-path-out-of-scope"}
            current = project
            for part in relative_candidate.parts:
                current = current / part
                if current.is_symlink():
                    return {"state": "blocked", "reason_code": "task-revision-path-symlink"}
        normalized_feature = _normalized_mapping_target(project, feature_directory)
        expected_feature_path = normalized_feature / "tasks.md"
        task_path = lexical_task_path.resolve(strict=False)
        try:
            task_path.relative_to(project)
            task_path.relative_to(normalized_feature)
        except ValueError:
            return {"state": "blocked", "reason_code": "task-revision-path-out-of-scope"}
        pointer_path = project / ".specify/feature.json"
        if pointer_path.is_symlink():
            raise ValueError("active feature pointer is a symlink")
        pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
        if not isinstance(pointer, dict) or pointer.get("feature_directory") != feature_directory:
            return {"state": "blocked", "reason_code": "task-revision-feature-identity-changed"}
        if (lexical_task_path != lexical_feature / "tasks.md"
                or task_path != expected_feature_path):
            return {"state": "blocked", "reason_code": "task-revision-path-out-of-scope"}
        before_digest = hashlib.sha256(before_text.encode("utf-8")).hexdigest()
        after_bytes = task_path.read_bytes()
        after_digest = hashlib.sha256(after_bytes).hexdigest()
        if result.get("feature_directory") != feature_directory:
            return {"state": "blocked", "reason_code": "task-revision-feature-identity-changed"}
        if result.get("revision_state") != "updated":
            return {"state": "blocked", "reason_code": "task-revision-result-invalid"}
        if result.get("tasks_path") != expected_path:
            return {"state": "blocked", "reason_code": "task-revision-path-out-of-scope"}
        if result.get("tasks_before_sha256") != before_digest or result.get("tasks_after_sha256") != after_digest:
            return {"state": "blocked", "reason_code": "task-revision-digest-mismatch"}
        before = _task_records(before_text)
        after_text = after_bytes.decode("utf-8")
        after = _task_records(after_text)
        if not before or not after or not set(before).issubset(after):
            return {"state": "blocked", "reason_code": "task-revision-history-deleted"}
        before_non_task_lines = [line for line in before_text.splitlines() if TASK_LINE.fullmatch(line) is None]
        after_non_task_lines = [line for line in after_text.splitlines() if TASK_LINE.fullmatch(line) is None]
        if before_non_task_lines != after_non_task_lines:
            return {"state": "blocked", "reason_code": "task-revision-unrelated-document-content-changed"}
        finding_ids = result.get("finding_ids")
        task_mappings = result.get("task_mappings")
        reopened_ids = result.get("reopened_task_ids")
        added_ids = result.get("added_task_ids")
        preserved_ids = result.get("preserved_completed_task_ids")
        frozen_findings = frozen_scope.get("findings")
        eligible_task_owners = frozen_scope.get("eligible_task_owners")
        permitted_added_owner = frozen_scope.get("permitted_added_task_owner")
        tasker_owner = frozen_scope.get("tasker_owner")
        if (any(not isinstance(value, list) for value in (finding_ids, task_mappings, reopened_ids, added_ids, preserved_ids, frozen_findings))
                or not isinstance(eligible_task_owners, dict)
                or not isinstance(permitted_added_owner, str)
                or permitted_added_owner != "FarmBoy Tasker"
                or tasker_owner != "FarmBoy Tasker"):
            return {"state": "blocked", "reason_code": "task-revision-result-invalid"}
        if (not frozen_findings or any(not isinstance(item, dict)
                                       or not isinstance(item.get("id"), str)
                                       or not _valid_finding_id(item["id"])
                                       or not isinstance(item.get("exact_correction"), str)
                                       or not item["exact_correction"].strip()
                                       for item in frozen_findings)):
            return {"state": "blocked", "reason_code": "task-revision-frozen-findings-invalid"}
        frozen_ids = [item["id"] for item in frozen_findings]
        if len(set(frozen_ids)) != len(frozen_ids):
            return {"state": "blocked", "reason_code": "task-revision-frozen-findings-invalid"}
        if (not finding_ids or any(not _valid_finding_id(item) for item in finding_ids)
                or len(set(finding_ids)) != len(finding_ids)):
            return {"state": "blocked", "reason_code": "task-revision-findings-invalid"}
        if set(finding_ids) != set(frozen_ids):
            return {"state": "blocked", "reason_code": "task-revision-finding-snapshot-mismatch"}
        if (any(not isinstance(task_id, str) or task_id not in before
                or owner != tasker_owner
                for task_id, owner in eligible_task_owners.items())
                or not permitted_added_owner.strip()):
            return {"state": "blocked", "reason_code": "task-revision-owner-snapshot-invalid"}
        if (any(not isinstance(item, str) for item in reopened_ids + added_ids + preserved_ids)
                or len(set(reopened_ids + added_ids)) != len(reopened_ids) + len(added_ids)):
            return {"state": "blocked", "reason_code": "task-revision-task-ids-invalid"}
        if any(item not in before for item in reopened_ids) or any(item in before or item not in after for item in added_ids):
            return {"state": "blocked", "reason_code": "task-revision-task-ids-invalid"}
        before_order = list(before)
        after_order_without_additions = [task_id for task_id in after if task_id not in added_ids]
        if before_order != after_order_without_additions:
            return {"state": "blocked", "reason_code": "task-revision-task-id-renumbered"}
        changed_ids: set[str] = set()
        for task_id, (before_marker, before_description) in before.items():
            after_marker, after_description = after[task_id]
            if (after_marker, after_description) == (before_marker, before_description):
                continue
            changed_ids.add(task_id)
            if task_id in reopened_ids:
                if before_marker not in {"x", "X"} or after_marker != " " or not after_description.startswith(before_description):
                    return {"state": "blocked", "reason_code": "task-revision-completed-history-changed"}
            else:
                return {"state": "blocked", "reason_code": "task-revision-unrelated-task-changed"}
        if changed_ids != set(reopened_ids):
            return {"state": "blocked", "reason_code": "task-revision-change-set-mismatch"}
        mapping_by_finding: dict[str, dict[str, Any]] = {}
        for mapping in task_mappings:
            if (not isinstance(mapping, dict) or not isinstance(mapping.get("finding_id"), str)
                    or not isinstance(mapping.get("task_ids"), list)
                    or not isinstance(mapping.get("owner"), str)
                    or mapping["finding_id"] in mapping_by_finding
                    or any(not isinstance(task_id, str) for task_id in mapping["task_ids"])
                    or len(set(mapping["task_ids"])) != len(mapping["task_ids"])):
                return {"state": "blocked", "reason_code": "task-revision-task-mapping-invalid"}
            mapping_by_finding[mapping["finding_id"]] = mapping
        if set(mapping_by_finding) != set(frozen_ids):
            return {"state": "blocked", "reason_code": "task-revision-finding-mapping-mismatch"}
        mapped_task_ids: set[str] = set()
        for finding in frozen_findings:
            mapping = mapping_by_finding[finding["id"]]
            if not mapping["task_ids"] or mapping["owner"] != tasker_owner:
                return {"state": "blocked", "reason_code": "task-revision-wrong-owner"}
            for task_id in mapping["task_ids"]:
                if task_id not in reopened_ids and task_id not in added_ids:
                    return {"state": "blocked", "reason_code": "task-revision-task-mapping-out-of-scope"}
                expected_owner = (eligible_task_owners.get(task_id) if task_id in reopened_ids
                                  else permitted_added_owner)
                if expected_owner != mapping["owner"]:
                    return {"state": "blocked", "reason_code": "task-revision-wrong-owner"}
                mapped_task_ids.add(task_id)
        if mapped_task_ids != set(reopened_ids + added_ids):
            return {"state": "blocked", "reason_code": "task-revision-task-mapping-mismatch"}
        for task_id in added_ids:
            marker, description = after[task_id]
            if marker != " " or not description.strip() or not any(finding in description for finding in finding_ids):
                return {"state": "blocked", "reason_code": "task-revision-added-task-invalid"}
        for task_id in reopened_ids:
            description = after[task_id][1]
            if not any(finding in description for finding in finding_ids):
                return {"state": "blocked", "reason_code": "task-revision-finding-unmapped"}
        changed_descriptions = [after[item][1] for item in reopened_ids + added_ids]
        if any(not any(finding in description for description in changed_descriptions) for finding in finding_ids):
            return {"state": "blocked", "reason_code": "task-revision-finding-unmapped"}
        if added_ids:
            previous_numbers = [int(task_id[1:]) for task_id in before]
            added_numbers = sorted(int(task_id[1:]) for task_id in added_ids)
            if added_numbers != list(range(max(previous_numbers) + 1, max(previous_numbers) + 1 + len(added_numbers))):
                return {"state": "blocked", "reason_code": "task-revision-task-id-renumbered"}
            before_ids = list(before)
            after_ids = list(after)
            first_added_position = min(after_ids.index(task_id) for task_id in added_ids)
            if after_ids[:first_added_position] != before_ids or after_ids[first_added_position:] != added_ids:
                return {"state": "blocked", "reason_code": "task-revision-task-id-renumbered"}
        preserved_completed = sorted(
            task_id for task_id, (marker, description) in before.items()
            if marker in {"x", "X"} and task_id not in reopened_ids
            and after[task_id] == (marker, description)
        )
        if sorted(preserved_ids) != preserved_completed:
            return {"state": "blocked", "reason_code": "task-revision-completed-history-changed"}
        scope_digest = task_revision_scope_digest(feature_directory, expected_path, frozen_scope)
        reviewed_finding_ids = semantic_review.get("finding_ids")
        reviewed_task_ids = semantic_review.get("task_ids")
        reviewed_finding_ids_valid = (isinstance(reviewed_finding_ids, list)
                                       and all(isinstance(item, str) for item in reviewed_finding_ids)
                                       and len(set(reviewed_finding_ids)) == len(reviewed_finding_ids))
        reviewed_task_ids_valid = (isinstance(reviewed_task_ids, list)
                                   and all(isinstance(item, str) for item in reviewed_task_ids)
                                   and len(set(reviewed_task_ids)) == len(reviewed_task_ids))
        if (semantic_review.get("reviewer") != "main-controller"
                or semantic_review.get("state") != "approved"
                or not isinstance(semantic_review.get("rationale"), str)
                or not semantic_review["rationale"].strip()
                or semantic_review.get("scope_sha256") != scope_digest
                or not reviewed_finding_ids_valid
                or set(reviewed_finding_ids) != set(frozen_ids)
                or not reviewed_task_ids_valid
                or set(reviewed_task_ids) != mapped_task_ids):
            return {"state": "blocked", "reason_code": "task-revision-semantic-review-required"}
        validated = {
            "state": "ready", "feature_directory": feature_directory,
            "tasks_path": expected_path, "tasks_before_sha256": before_digest,
            "tasks_after_sha256": after_digest, "finding_ids": finding_ids,
            "eligible_task_ids": sorted(set(reopened_ids + added_ids)),
            "preserved_completed_task_ids": preserved_completed,
            "scope_sha256": scope_digest,
            "substantive_progress": False,
        }
        requested_scope = payload.get("requested_scope")
        if requested_scope is not None:
            if (not isinstance(requested_scope, dict)
                    or requested_scope.get("feature_directory") != feature_directory
                    or not isinstance(payload.get("retained_scope_sha256"), str)
                    or requested_scope.get("scope_sha256") != payload["retained_scope_sha256"]
                    or not isinstance(payload.get("trusted_request_reference"), str)
                    or not payload["trusted_request_reference"]):
                return {"state": "blocked", "reason_code": "task-revision-requested-scope-invalid"}
            source_task_digest = requested_scope.get("input_digests", {}).get(expected_path)
            successors = payload.get("task_tracking_successors", [])
            if not isinstance(source_task_digest, str) or not SHA256.fullmatch(source_task_digest) or not isinstance(successors, list):
                return {"state": "blocked", "reason_code": "task-revision-successor-predecessor-invalid"}
            event: dict[str, Any] = {
                "successor_kind": "task-plan-revision",
                "predecessor_event_sha256": successors[-1]["sha256"] if successors else "0" * 64,
                "scope_sha256": requested_scope["scope_sha256"],
                "tasker_assignment": "FarmBoy Tasker",
                "tasks_before_text": before_text,
                "tasks_after_text": after_text,
                "tasker_result": {key: result[key] for key in (
                    "revision_state", "tasks_before_sha256", "tasks_after_sha256", "finding_ids",
                    "task_mappings", "reopened_task_ids", "added_task_ids", "preserved_completed_task_ids")},
                "frozen_scope": frozen_scope,
                "semantic_review": semantic_review,
                "validation_result": dict(validated),
            }
            event["sha256"] = implementation_scope_module._digest(event)
            tracked_chain = [*successors, event]
            revised_records: dict[str, tuple[str, str]] = {}
            try:
                tracked_ids = implementation_scope_module.validate_task_tracking_successors(
                    tracked_chain, initial_tasks_sha256=source_task_digest,
                    current_tasks_text=after_text, scope_sha256=requested_scope["scope_sha256"],
                    requested_task_ids=set(requested_scope.get("requested_task_ids", [])),
                    feature_directory=feature_directory, tasks_path=expected_path,
                    approved_specification_sha256=requested_scope.get("input_digests", {}).get(
                        f"{feature_directory}/spec.md"),
                    revision_records_out=revised_records)
                current_tasks = {task_id: {"marker": "checked" if marker in {"x", "X"} else "unchecked",
                                           "description": description}
                                 for task_id, (marker, description) in after.items()}
                implementation_scope_module.validate_requested_scope(
                    requested_scope, current_tasks,
                    trusted_request_reference=payload["trusted_request_reference"],
                    retained_scope_sha256=payload["retained_scope_sha256"],
                    trusted_requested_task_ids=payload.get("trusted_requested_task_ids"),
                    tasker_tracked_task_ids=tracked_ids,
                    tasker_revised_task_records=revised_records)
            except (TypeError, ValueError) as error:
                return {"state": "blocked", "reason_code": str(error) or "task-revision-successor-invalid"}
            validated["task_tracking_successor"] = event
        return validated
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RuntimeError, ValueError):
        return {"state": "blocked", "reason_code": "task-revision-validation-failed"}


def _progress_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _progress_evidence(project: Path, evidence: Any) -> list[dict[str, str]]:
    """Read current contained evidence without following lexical symlink aliases."""
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("progress-evidence-missing")
    result = []
    for item in evidence:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            raise ValueError("progress-evidence-invalid")
        name, digest = item["path"], item["sha256"]
        if (not isinstance(name, str) or not name or Path(name).is_absolute()
                or any(p in {"", ".", ".."} for p in name.split("/")) or "\\" in name):
            raise ValueError("progress-evidence-path-unsafe")
        path = project
        for part in name.split("/"):
            path = path / part
            if path.is_symlink():
                raise ValueError("progress-evidence-path-unsafe")
        path.resolve(strict=True).relative_to(project)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("progress-evidence-stale")
        if any(x["path"] == name for x in result):
            raise ValueError("progress-evidence-duplicate")
        result.append(dict(item))
    return result


def _progress_findings(project: Path, findings: Any, selected: set[str]) -> list[dict[str, Any]]:
    if not isinstance(findings, list):
        raise ValueError("progress-findings-invalid")
    result = []
    for finding in findings:
        required = ("id", "task_id", "artifact_location", "violated_requirement", "observed_deficiency", "exact_correction")
        if (not isinstance(finding, dict) or not _valid_finding_id(finding.get("id"))
                or any(not isinstance(finding.get(k), str)
                or not finding[k].strip() for k in required)
                or finding["task_id"] not in selected
                or finding["id"] in selected or any(x["id"] == finding["id"] for x in result)):
            raise ValueError("progress-finding-owner-or-identity-invalid")
        evidence = _progress_evidence(project, finding.get("evidence"))
        source = finding["artifact_location"].split(":", 1)[0]
        if source not in {item["path"] for item in evidence}:
            raise ValueError("progress-finding-source-missing")
        result.append({**{k: finding[k] for k in required}, "evidence": evidence})
    return result


def capture_implementation_baseline(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Freeze selected tasks and known defects before a correction starts."""
    project = Path(project_root).resolve()
    try:
        feature = payload["feature_directory"]
        preflight = task_revision_preflight(project, feature, f"{feature}/tasks.md")
        if preflight["state"] != "ready":
            return preflight
        tasks = _task_records(preflight["tasks_before_text"])
        selected = payload["selected_task_ids"]
        if (not isinstance(selected, list) or not selected or len(set(selected)) != len(selected)
                or any(not isinstance(x, str) or x not in tasks for x in selected)):
            raise ValueError("progress-selected-tasks-invalid")
        findings = _progress_findings(project, payload.get("findings", []), set(selected))
        baseline = {"schema_version": "1.0", "feature_directory": feature,
                    "pointer_sha256": preflight["pointer_sha256"],
                    "specification_sha256": preflight["specification_sha256"],
                    "tasks": {x: {"marker": tasks[x][0], "description": tasks[x][1]} for x in selected},
                    "findings": findings}
        remaining = [f"task:{x}" for x in selected if tasks[x][0] == " "]
        remaining += [f"finding:{x['id']}" for x in findings]
        return {"state": "ready", "baseline": baseline, "baseline_sha256": _progress_digest(baseline),
                "remaining_ids": remaining}
    except (KeyError, TypeError, ValueError, OSError, RuntimeError):
        return {"state": "blocked", "reason_code": "implementation-baseline-invalid",
                "resume_action": "reassess-current-selected-tasks-and-findings"}


def _progress_source_origins(baseline: dict[str, Any], records: Any) -> dict[str, list[dict[str, str]]]:
    """Recover legacy preimages only from controller-retained, digest-bound baselines.

    These records are historical comparisons, not current filesystem evidence.
    Their digests and chronological order must be retained by the main controller,
    just like the active baseline digest; a child cannot supply their authority.
    """
    if not isinstance(records, list):
        raise ValueError("progress-source-baselines-invalid")
    originals = {finding["id"]: finding for finding in baseline["findings"]}
    origins = {}
    identity = ("id", "task_id", "artifact_location", "violated_requirement", "observed_deficiency", "exact_correction")
    for record in records:
        if not isinstance(record, dict) or set(record) != {"baseline", "baseline_sha256"}:
            raise ValueError("progress-source-baselines-invalid")
        historic = record["baseline"]
        if (not isinstance(historic, dict) or historic.get("schema_version") != "1.0"
                or _progress_digest(historic) != record["baseline_sha256"]
                or any(historic.get(key) != baseline.get(key) for key in (
                    "feature_directory", "pointer_sha256", "specification_sha256"))):
            raise ValueError("progress-source-baselines-invalid")
        for finding in historic["findings"]:
            current = originals.get(finding["id"])
            if current is None:
                continue
            if any(finding.get(key) != current.get(key) for key in identity):
                raise ValueError("progress-source-baseline-finding-changed")
            proof = finding.get("evidence")
            if (not isinstance(proof, list) or not proof
                    or any(not isinstance(item, dict) or set(item) != {"path", "sha256"}
                           or not isinstance(item["path"], str) or not item["path"]
                           or Path(item["path"]).is_absolute() or "\\" in item["path"]
                           or any(part in {"", ".", ".."} for part in item["path"].split("/"))
                           or not isinstance(item["sha256"], str) or SHA256.fullmatch(item["sha256"]) is None
                           for item in proof)
                    or len({item["path"] for item in proof}) != len(proof)
                    or finding["artifact_location"].split(":", 1)[0] not in {item["path"] for item in proof}):
                raise ValueError("progress-source-baselines-invalid")
            origins.setdefault(finding["id"], proof)
    return origins


def validate_implementation_progress(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Validate independent closure without treating an unfinished parent as complete.

    The controller supplies the original frozen baseline/digest and verifies the
    actual native reviewer dispatch. A role label or digest is not authentication.
    """
    project = Path(project_root).resolve()
    try:
        baseline, review = payload["baseline"], payload["review"]
        if (not isinstance(baseline, dict) or baseline.get("schema_version") != "1.0"
                or _progress_digest(baseline) != payload["baseline_sha256"]
                or not isinstance(review, dict) or review.get("reviewer") != "FarmBoy Code Reviewer"
                or review.get("baseline_sha256") != payload["baseline_sha256"]):
            raise ValueError("progress-baseline-or-review-invalid")
        feature = baseline["feature_directory"]
        current = task_revision_preflight(project, feature, f"{feature}/tasks.md")
        if (current["state"] != "ready" or current["pointer_sha256"] != baseline["pointer_sha256"]
                or current["specification_sha256"] != baseline["specification_sha256"]):
            raise ValueError("progress-scope-changed")
        tasks = _task_records(current["tasks_before_text"])
        selected = baseline["tasks"]
        if (not isinstance(selected, dict) or not selected
                or any(x not in tasks or tasks[x][1] != v["description"] for x, v in selected.items())):
            raise ValueError("progress-task-scope-changed")
        old = {x["id"]: x for x in baseline["findings"]}
        source_origins = _progress_source_origins(baseline, payload.get("finding_source_baselines", []))
        findings = review["findings"]
        if (not isinstance(findings, list) or any(not isinstance(x, dict) for x in findings)
                or any(not isinstance(x.get("id"), str) for x in findings)
                or len({x["id"] for x in findings}) != len(findings)
                or {x["id"] for x in findings} != set(old)):
            raise ValueError("progress-prior-finding-coverage-invalid")
        resolved = []
        unresolved = []
        evidence = []
        for assessment in findings:
            finding = old[assessment["id"]]
            if assessment.get("task_id") != finding["task_id"]:
                raise ValueError("progress-finding-owner-changed")
            status = assessment.get("status")
            if status == "unresolved":
                proof = _progress_evidence(project, assessment.get("evidence"))
                if finding["artifact_location"].split(":", 1)[0] not in {x["path"] for x in proof}:
                    raise ValueError("progress-unresolved-source-missing")
                unresolved.append({**finding, "evidence": source_origins.get(finding["id"], finding["evidence"]),
                                   "current_evidence": proof})
            elif status == "resolved":
                if (not isinstance(assessment.get("resolution_summary"), str)
                        or not assessment["resolution_summary"].strip()):
                    raise ValueError("progress-resolution-evidence-missing")
                proof = _progress_evidence(project, assessment.get("evidence"))
                before = {x["path"]: x["sha256"] for x in source_origins.get(finding["id"], finding["evidence"])}
                source = finding["artifact_location"].split(":", 1)[0]
                if not any(x["path"] == source and before.get(source) != x["sha256"] for x in proof):
                    raise ValueError("progress-source-not-corrected")
                evidence.extend(proof)
                resolved.append(f"finding:{finding['id']}")
            else:
                raise ValueError("progress-finding-status-invalid")
        new = _progress_findings(project, review.get("new_findings", []), set(selected))
        if any(x["id"] in old for x in new):
            raise ValueError("progress-new-finding-is-prior")
        unresolved.extend(new)
        complete = review.get("completed_task_ids", [])
        if (not isinstance(complete, list) or any(not isinstance(x, str) for x in complete)
                or len(set(complete)) != len(complete) or any(x not in selected for x in complete)
                or any(x["task_id"] in complete for x in unresolved)):
            raise ValueError("progress-parent-task-still-unresolved")
        if complete:
            task_proof = _progress_evidence(project, review.get("task_completion_evidence"))
            if not any(x["path"] != f"{feature}/tasks.md" for x in task_proof):
                raise ValueError("progress-task-marker-only-evidence")
            evidence.extend(task_proof)
        resolved += [f"task:{x}" for x in complete if selected[x]["marker"] == " "]
        remaining = [f"task:{x}" for x in selected if x not in complete
                     and (selected[x]["marker"] == " " or any(f["task_id"] == x for f in unresolved))]
        remaining += [f"finding:{x['id']}" for x in unresolved]
        next_baseline = {**baseline, "tasks": {x: {"marker": selected[x]["marker"], "description": tasks[x][1]}
                          for x in selected if x not in complete}, "findings": unresolved}
        return {"state": "ready", "remaining_ids": remaining, "resolved_ids": resolved,
                "findings": unresolved, "evidence": list({x["path"]: x for x in evidence}.values()),
                "substantive_progress": bool(resolved), "baseline": next_baseline,
                "baseline_sha256": _progress_digest(next_baseline)}
    except (KeyError, TypeError, ValueError, OSError, RuntimeError):
        return {"state": "blocked", "reason_code": "implementation-progress-invalid",
                "resume_action": "reassess-original-baseline-and-current-independent-code-evidence"}


def advance_implementation_baseline(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Bind a validated Tasker correction to the next baseline without progress credit."""
    try:
        baseline = payload["baseline"]
        revision = payload["task_revision_payload"]
        if (_progress_digest(baseline) != payload["baseline_sha256"]
                or not isinstance(revision, dict)
                or revision.get("feature_directory") != baseline["feature_directory"]):
            raise ValueError("progress-transition-baseline-invalid")
        before = _task_records(revision["tasks_before_text"])
        if any(task not in before or before[task][1] != value["description"]
               for task, value in baseline["tasks"].items()):
            raise ValueError("progress-transition-before-scope-changed")
        expected_findings = {x["id"]: x["exact_correction"] for x in baseline["findings"]}
        if revision["frozen_scope"].get("approved_specification_sha256") != baseline["specification_sha256"]:
            raise ValueError("progress-transition-specification-scope-changed")
        frozen = revision["frozen_scope"]["findings"]
        if (not isinstance(frozen, list) or len({x["id"] for x in frozen}) != len(frozen)
                or not frozen or any(expected_findings.get(x["id"]) != x["exact_correction"] for x in frozen)):
            raise ValueError("progress-transition-finding-scope-changed")
        checked = validate_task_revision(project_root, revision)
        if checked["state"] != "ready":
            return checked
        feature = baseline["feature_directory"]
        preflight = task_revision_preflight(project_root, feature, f"{feature}/tasks.md")
        if (preflight["state"] != "ready" or preflight["pointer_sha256"] != baseline["pointer_sha256"]
                or preflight["specification_sha256"] != baseline["specification_sha256"]):
            raise ValueError("progress-transition-identity-changed")
        after = _task_records(preflight["tasks_before_text"])
        tasks = {x: {**v, "description": after[x][1]} for x, v in baseline["tasks"].items()}
        for task in checked["eligible_task_ids"]:
            tasks[task] = {"marker": " ", "description": after[task][1]}
        mappings = {x["finding_id"]: x["task_ids"] for x in revision["tasker_result"]["task_mappings"]}
        findings = []
        for finding in baseline["findings"]:
            owners = mappings.get(finding["id"], [finding["task_id"]])
            owner = finding["task_id"] if finding["task_id"] in owners else owners[0]
            if owner not in tasks:
                raise ValueError("progress-transition-owner-missing")
            findings.append({**finding, "task_id": owner})
        next_baseline = {**baseline, "tasks": tasks, "findings": findings}
        return {"state": "ready", "baseline": next_baseline,
                "baseline_sha256": _progress_digest(next_baseline), "substantive_progress": False,
                "previous_baseline_sha256": payload["baseline_sha256"],
                "task_revision_scope_sha256": checked["scope_sha256"]}
    except (KeyError, TypeError, ValueError, OSError, RuntimeError):
        return {"state": "blocked", "reason_code": "implementation-baseline-transition-invalid",
                "resume_action": "reassess-frozen-scope-and-current-tasker-revision"}


def _implementation_scope_binding(project_root: Path, payload: dict[str, Any]) -> tuple[Any, dict[str, Any], set[str], dict[str, tuple[str, str]]]:
    """Revalidate a trusted scope snapshot against the active task file and inputs."""
    project = Path(project_root).resolve()
    if implementation_scope_module is None:
        raise ValueError("implementation-scope-helper-unavailable")
    required = {"scope", "trusted_request_reference", "retained_scope_sha256"}
    allowed = required | {"trusted_requested_task_ids", "task_tracking_successors"}
    if not isinstance(payload, dict) or not required.issubset(payload) or set(payload) - allowed:
        raise ValueError("implementation-scope-request-invalid")
    scope = payload["scope"]
    if not isinstance(scope, dict):
        raise ValueError("implementation-scope-request-invalid")
    feature = scope.get("feature_directory")
    preflight = task_revision_preflight(project_root, feature, f"{feature}/tasks.md" if isinstance(feature, str) else "")
    if preflight.get("state") != "ready":
        raise ValueError("implementation-scope-active-target-invalid")
    required_sources = {
        ".specify/feature.json": preflight["pointer_sha256"],
        f"{feature}/spec.md": preflight["specification_sha256"],
        f"{feature}/tasks.md": preflight["tasks_before_sha256"],
    }
    supplied_digests = scope.get("input_digests")
    if not isinstance(supplied_digests, dict) or any(
            supplied_digests.get(path) != digest for path, digest in required_sources.items()
            if path != f"{feature}/tasks.md"):
        raise ValueError("implementation-scope-required-source-binding-missing")
    original_tasks_sha256 = supplied_digests.get(f"{feature}/tasks.md")
    if not isinstance(original_tasks_sha256, str) or not SHA256.fullmatch(original_tasks_sha256):
        raise ValueError("implementation-scope-required-source-binding-missing")
    records = _task_records(preflight["tasks_before_text"])
    tracking = payload.get("task_tracking_successors", [])
    revised_task_records: dict[str, tuple[str, str]] = {}
    derived_task_records: dict[str, tuple[str, str]] = {}
    if tracking:
        tracked_ids = implementation_scope_module.validate_task_tracking_successors(
            tracking, initial_tasks_sha256=original_tasks_sha256,
            current_tasks_text=preflight["tasks_before_text"], scope_sha256=scope.get("scope_sha256"),
            requested_task_ids=set(scope.get("requested_task_ids", [])),
            feature_directory=feature, tasks_path=f"{feature}/tasks.md",
            approved_specification_sha256=supplied_digests.get(f"{feature}/spec.md"),
            revision_records_out=revised_task_records,
            derived_task_records_out=derived_task_records)
    elif preflight["tasks_before_sha256"] == original_tasks_sha256:
        tracked_ids = set()
    else:
        raise ValueError("task-tracking-proof-required")
    current_tasks = {task_id: {"marker": "checked" if marker.strip().lower() == "x" else "unchecked",
                               "description": description}
                     for task_id, (marker, description) in records.items()}
    for source_path, expected in scope.get("input_digests", {}).items():
        if source_path == f"{feature}/tasks.md":
            if preflight["tasks_before_sha256"] != original_tasks_sha256 and not tracking:
                raise ValueError("task-tracking-proof-required")
            continue
        observed = hashlib.sha256(_contained_regular_file(project, source_path, "implementation scope input").read_bytes()).hexdigest()
        if observed != expected:
            raise ValueError("implementation-scope-input-stale")
    checked = implementation_scope_module.validate_requested_scope(
        scope, current_tasks, trusted_request_reference=payload["trusted_request_reference"],
        retained_scope_sha256=payload["retained_scope_sha256"],
        trusted_requested_task_ids=payload.get("trusted_requested_task_ids"),
        tasker_tracked_task_ids=tracked_ids,
        tasker_revised_task_records=revised_task_records)
    for event in tracking:
        if event.get("successor_kind") == "task-plan-revision":
            continue
        for result_key in ("tasker_result", "reviewer_result"):
            for evidence in event[result_key]["evidence"]:
                current = _contained_regular_file(project, evidence["path"], "task tracking evidence")
                if hashlib.sha256(current.read_bytes()).hexdigest() != evidence["sha256"]:
                    raise ValueError("task-tracking-evidence-stale")
    return implementation_scope_module, checked, tracked_ids, derived_task_records


def _scope_binding_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Preserve immutable scope identity plus separately retained Tasker successors."""
    keys = ("scope", "trusted_request_reference", "retained_scope_sha256",
            "trusted_requested_task_ids", "task_tracking_successors")
    return {key: payload[key] for key in keys if key in payload}


def validate_implementation_scope(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Validate the exact authorized full-feature or subset request before eligibility."""
    try:
        _, scope, tracked_ids, derived = _implementation_scope_binding(project_root, payload)
        return {"state": "ready", "scope": scope, "scope_sha256": scope["scope_sha256"],
                "requested_task_ids": scope["requested_task_ids"],
                "tasker_tracked_task_ids": sorted(tracked_ids),
                "tasker_derived_task_ids": sorted(derived)}
    except (KeyError, TypeError, ValueError, OSError, RuntimeError) as error:
        reason = str(error) if str(error) else "implementation-scope-invalid"
        return {"state": "blocked", "reason_code": reason,
                "resume_action": "reestablish-the-trusted-current-implementation-scope"}


def validate_implementation_eligibility(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Validate complete task accounting, kind-specific proof, and current source inputs."""
    try:
        binding_payload = _scope_binding_payload(payload)
        module, scope, tracked_ids, derived_task_records = _implementation_scope_binding(project_root, binding_payload)
        required = {"scope", "trusted_request_reference", "retained_scope_sha256", "assessment", "proofs",
                    "proof_requirements", "completion_classifications", "source_requirement_ids",
                    "retained_predecessor_sha256"}
        allowed = required | {"trusted_requested_task_ids", "task_tracking_successors",
                              "completed_prerequisites", "retained_prerequisite_sha256"}
        if set(payload) - allowed or not required.issubset(payload):
            raise ValueError("implementation-eligibility-request-invalid")
        assessment = payload["assessment"]
        if not isinstance(assessment, dict) or not isinstance(assessment.get("input_digests"), dict):
            raise ValueError("implementation-eligibility-assessment-invalid")
        for source_path, expected in assessment.get("input_digests", {}).items():
            observed = hashlib.sha256(_contained_regular_file(Path(project_root).resolve(), source_path, "eligibility input").read_bytes()).hexdigest()
            if observed != expected:
                raise ValueError("implementation-eligibility-input-stale")
        checked = module.validate_task_eligibility(
            scope, assessment, payload["proofs"], proof_requirements=payload["proof_requirements"],
            completion_classifications=payload["completion_classifications"],
            source_requirement_ids=payload["source_requirement_ids"],
            completed_prerequisites=payload.get("completed_prerequisites", {}),
            retained_prerequisite_sha256=payload.get("retained_prerequisite_sha256", {}),
            tasker_tracked_task_ids=tracked_ids,
            tasker_derived_task_records=derived_task_records,
            retained_predecessor_sha256=payload["retained_predecessor_sha256"])
        return {"state": "ready", "scope_sha256": scope["scope_sha256"],
                "eligibility": checked, "eligibility_sha256": hashlib.sha256(json.dumps(checked, sort_keys=True, separators=(",", ":")).encode()).hexdigest()}
    except (AttributeError, KeyError, TypeError, ValueError, OSError, RuntimeError) as error:
        reason = str(error) if str(error) else "implementation-eligibility-invalid"
        return {"state": "blocked", "reason_code": reason,
                "resume_action": "reassess-current-scope-eligibility-and-prerequisite-proof"}


def capture_post_pass_state(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Capture current durable history and actual validated Tasker producer outputs."""
    try:
        required = {"scope", "trusted_request_reference", "retained_scope_sha256", "entry_history_sha256",
                    "task_tracking_successors", "producer_pairs", "eligibility_request", "completion_branch"}
        optional = {"trusted_requested_task_ids"}
        if not required.issubset(payload) or set(payload) - required - optional:
            raise ValueError("post-pass-capture-request-invalid")
        module = implementation_scope_module
        if module is None:
            raise ValueError("post-pass-capture-helper-unavailable")
        candidate_pairs = payload["producer_pairs"]
        if not isinstance(candidate_pairs, list):
            raise ValueError("post-pass-producer-pairs-invalid")
        if not isinstance(payload["task_tracking_successors"], list):
            raise ValueError("post-pass-successor-chain-invalid")
        successor_chain = list(payload["task_tracking_successors"])
        completion = payload["completion_branch"]
        if type(completion) is not bool or len(candidate_pairs) > 1:
            raise ValueError("post-pass-producer-branch-invalid")
        expected = {"revise-task-plan": "validate-task-revision",
                    "track-reviewed-task-outcomes": "validate-reviewed-task-tracking",
                    "track-reviewed-completion": "validate-reviewed-completion-tracking"}
        normalized_pairs = []
        for producer in candidate_pairs:
            if not isinstance(producer, dict) or set(producer) != {
                    "tasker_step_id", "validator_step_id", "tasker_result", "validator_result"}:
                raise ValueError("post-pass-producer-pair-invalid")
            if (producer["tasker_step_id"] not in expected
                    or expected[producer["tasker_step_id"]] != producer["validator_step_id"]):
                raise ValueError("post-pass-producer-pair-invalid")
            if (completion and producer["tasker_step_id"] != "track-reviewed-completion"
                    or not completion and producer["tasker_step_id"] == "track-reviewed-completion"):
                raise ValueError("post-pass-producer-branch-invalid")
            tasker_result, validator_result = producer["tasker_result"], producer["validator_result"]
            if not isinstance(tasker_result, dict) or not isinstance(validator_result, dict):
                raise ValueError("post-pass-producer-output-missing")
            if validator_result.get("state") not in ({"complete"} if completion else {"ready"}):
                raise ValueError("post-pass-validator-state-invalid")
            if "task_tracking_successor" not in validator_result:
                raise ValueError("post-pass-successor-output-missing")
            successor = validator_result["task_tracking_successor"]
            if successor is not None:
                successor_chain.append(successor)
            normalized_pairs.append({"tasker_step_id": producer["tasker_step_id"],
                "validator_step_id": producer["validator_step_id"],
                "tasker_result_sha256": module._digest(tasker_result),
                "validator_result_sha256": module._digest(validator_result),
                "task_tracking_successor_sha256": module._digest(successor) if successor is not None else None})
        if completion and (len(candidate_pairs) != 1 or candidate_pairs[0]["validator_result"].get("state") != "complete"):
            raise ValueError("post-pass-completion-proof-missing")
        scope_binding = {**_scope_binding_payload(payload), "task_tracking_successors": successor_chain}
        _, scope, _, _ = _implementation_scope_binding(project_root, scope_binding)
        entry_digest = payload["entry_history_sha256"]
        if not isinstance(entry_digest, str) or not module.SHA256.fullmatch(entry_digest):
            raise ValueError("post-pass-entry-history-invalid")
        history_path, history_relative = _implementation_history_path(Path(project_root), scope)
        if history_path.is_symlink() or not history_path.is_file():
            raise ValueError("post-pass-current-history-missing")
        current_history = json.loads(history_path.read_text(encoding="utf-8"))
        current_digest = current_history.get("sha256") if isinstance(current_history, dict) else None
        if not isinstance(current_digest, str):
            raise ValueError("post-pass-current-history-invalid")
        current_history, _ = _read_implementation_history(Path(project_root), scope, current_digest)
        prefix = _empty_implementation_history(scope)
        entry_seen = prefix["sha256"] == entry_digest
        for event in current_history["events"]:
            prefix = module.append_execution_event(prefix, event, scope_sha256=scope["scope_sha256"],
                                                   retained_history_sha256=prefix["sha256"])
            entry_seen = entry_seen or prefix["sha256"] == entry_digest
        if not entry_seen:
            raise ValueError("post-pass-entry-history-not-ancestor")

        scope_result = validate_implementation_scope(Path(project_root), {
            **scope_binding, "task_tracking_successors": successor_chain})
        if scope_result.get("state") != "ready":
            raise ValueError(scope_result.get("reason_code", "post-pass-successor-chain-invalid"))
        eligibility_request = payload["eligibility_request"]
        if not isinstance(eligibility_request, dict):
            raise ValueError("post-pass-eligibility-request-invalid")
        eligibility_payload = {**eligibility_request, **scope_binding,
                               "task_tracking_successors": successor_chain}
        eligibility = validate_implementation_eligibility(Path(project_root), eligibility_payload)
        if eligibility.get("state") != "ready":
            raise ValueError(eligibility.get("reason_code", "post-pass-eligibility-invalid"))
        if completion and eligibility["eligibility"].get("pending_task_ids"):
            raise ValueError("post-pass-completion-proof-incomplete")
        state = {"scope": scope, "history": current_history,
                 "history_path": history_relative, "task_tracking_successors": successor_chain,
                 "eligibility": eligibility, "producer_records": normalized_pairs,
                 "completion_validator_state": "complete" if completion else "ready"}
        return {"state": "ready", "post_pass_state": state}
    except (AttributeError, KeyError, TypeError, ValueError, OSError, RuntimeError, json.JSONDecodeError) as error:
        reason = str(error) if str(error) else "post-pass-capture-invalid"
        return {"state": "blocked", "reason_code": reason,
                "resume_action": "revalidate-current-post-pass-history-and-producers"}


def validate_implementation_activation(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Bind one task's fresh eligibility, preimages, route, and readiness before effects."""
    try:
        binding_payload = _scope_binding_payload(payload)
        module, scope, _, _ = _implementation_scope_binding(project_root, binding_payload)
        required = {"scope", "trusted_request_reference", "retained_scope_sha256", "activation", "eligibility_sha256",
                    "predecessor_baseline_sha256", "task_id", "required_paths"}
        allowed = required | {"trusted_requested_task_ids", "task_tracking_successors"}
        if set(payload) - allowed or not required.issubset(payload):
            raise ValueError("implementation-activation-request-invalid")
        activation = payload["activation"]
        if not isinstance(activation, dict) or not isinstance(activation.get("source_preimages"), list):
            raise ValueError("implementation-activation-request-invalid")
        for preimage in activation.get("source_preimages", []):
            relative = module._relative_path(preimage.get("path"), "activation-source")
            path = Path(project_root).resolve() / relative
            current = Path(project_root).resolve()
            for part in Path(relative).parts:
                current = current / part
                if current.is_symlink():
                    raise ValueError("task-activation-path-symlink")
            if preimage.get("state") == "absent":
                if path.exists():
                    raise ValueError("task-activation-preimage-stale")
            elif preimage.get("state") == "present":
                if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != preimage.get("sha256"):
                    raise ValueError("task-activation-preimage-stale")
            else:
                raise ValueError("task-activation-preimage-invalid")
        checked = module.validate_task_activation(
            activation, scope_sha256=scope["scope_sha256"], eligibility_sha256=payload["eligibility_sha256"],
            predecessor_baseline_sha256=payload["predecessor_baseline_sha256"], task_id=payload["task_id"],
            required_paths=set(payload["required_paths"]))
        return {"state": "ready", "activation": checked, "scope_sha256": scope["scope_sha256"]}
    except (AttributeError, KeyError, TypeError, ValueError, OSError, RuntimeError) as error:
        reason = str(error) if str(error) else "implementation-activation-invalid"
        return {"state": "blocked", "reason_code": reason,
                "resume_action": "refresh-task-eligibility-preimages-and-readiness"}


def _implementation_history_path(project_root: Path, scope: dict[str, Any]) -> tuple[Path, str]:
    """Resolve the one consumer-local append-only history path for a validated scope."""
    run_id = scope.get("run_id")
    if not isinstance(run_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,99}", run_id):
        raise ValueError("implementation-history-run-id-invalid")
    relative = Path(".specify/farmboy-controllers/implementation-history") / f"{run_id}.json"
    path = Path(project_root).resolve() / relative
    cursor = Path(project_root).resolve()
    for part in relative.parts[:-1]:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError("implementation-history-path-symlink")
    if path.is_symlink():
        raise ValueError("implementation-history-path-symlink")
    return path, relative.as_posix()


def _empty_implementation_history(scope: dict[str, Any]) -> dict[str, Any]:
    """Build the canonical zero-event predecessor used before the first dispatch."""
    history = {"schema_version": "1.0", "scope_sha256": scope["scope_sha256"], "events": [],
               "coder_sessions_started": 0, "source_attempts_started": 0}
    history["sha256"] = hashlib.sha256(
        json.dumps(history, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    return history


def _read_implementation_history(project_root: Path, scope: dict[str, Any], retained_sha256: str) -> tuple[dict[str, Any], str]:
    """Read durable history and require the independently retained current predecessor."""
    path, relative = _implementation_history_path(project_root, scope)
    try:
        history = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        history = _empty_implementation_history(scope)
    if history.get("sha256") != retained_sha256:
        raise ValueError("implementation-history-retained-state-stale")
    implementation_scope_module.validate_execution_history(
        history, scope_sha256=scope["scope_sha256"], retained_history_sha256=retained_sha256)
    return history, relative


def append_implementation_execution_event(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Persist one validated append-only event before its modeled Coder dispatch."""
    try:
        if implementation_scope_module is None:
            raise ValueError("implementation-history-request-invalid")
        project_root = Path(project_root).resolve()
        required_fields = {"scope", "trusted_request_reference", "retained_scope_sha256",
                           "event", "retained_history_sha256"}
        if not required_fields.issubset(payload) or set(payload) - required_fields - {"trusted_requested_task_ids", "task_tracking_successors"}:
            raise ValueError("implementation-history-request-invalid")
        binding_payload = _scope_binding_payload(payload)
        module, scope, _, _ = _implementation_scope_binding(project_root, binding_payload)
        history_path, history_relative = _implementation_history_path(project_root, scope)
        history_path.parent.mkdir(parents=True, exist_ok=True)
        expected_history_sha256 = payload["retained_history_sha256"]
        history, _ = _read_implementation_history(project_root, scope, expected_history_sha256)
        for item in payload["event"].get("evidence", []):
            candidate = _contained_regular_file(project_root, item["path"], "implementation history evidence")
            observed = hashlib.sha256(candidate.read_bytes()).hexdigest()
            if observed != item["sha256"]:
                raise ValueError("implementation-history-evidence-stale")
        history = implementation_scope_module.append_execution_event(
            history, payload["event"], scope_sha256=scope["scope_sha256"],
            retained_history_sha256=expected_history_sha256)
        descriptor, temporary_name = tempfile.mkstemp(prefix=".implementation-history-", suffix=".tmp",
                                                       dir=history_path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(history, stream, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_name, history_path)
        except Exception:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise
        return {"state": "ready", "history": history, "history_sha256": history["sha256"],
                "coder_sessions_started": history["coder_sessions_started"],
                "source_attempts_started": history["source_attempts_started"],
                "history_path": history_relative}
    except (KeyError, TypeError, ValueError, OSError, RuntimeError, json.JSONDecodeError) as error:
        reason = str(error) if str(error) else "implementation-history-invalid"
        return {"state": "blocked", "reason_code": reason,
                "resume_action": "revalidate-append-only-coder-execution-history"}


def route_scoped_implementation(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Route preparation before source attempts and generic progress after source starts."""
    try:
        module = implementation_scope_module
        required = {"scope", "trusted_request_reference", "retained_scope_sha256", "retained_history_sha256",
                    "assessment", "eligible_task_ids", "declared_node_ids"}
        allowed = required | {"previous_assessment", "trusted_requested_task_ids", "task_tracking_successors",
                              "eligibility_request"}
        if module is None or not required.issubset(payload) or set(payload) - allowed:
            raise ValueError("implementation-route-request-invalid")
        scope_binding = _scope_binding_payload(payload)
        _, scope, _, _ = _implementation_scope_binding(project_root, scope_binding)
        history, history_path = _read_implementation_history(
            project_root, scope, payload["retained_history_sha256"])
        nodes = set(payload["declared_node_ids"])
        if nodes != {"prepare-scoped-prerequisites", "implement-tasks"}:
            raise ValueError("implementation-route-nodes-invalid")
        assessment = validate_outcome_envelope(payload["assessment"], Path(project_root), nodes, set())
        previous_raw = payload.get("previous_assessment")
        previous = None if previous_raw is None else validate_outcome_envelope(previous_raw, Path(project_root), nodes, set())
        validated_eligibility = None
        if assessment["state"] == "complete":
            eligibility_request = payload.get("eligibility_request")
            if not isinstance(eligibility_request, dict):
                raise ValueError("scoped-completion-proof-required")
            validated_eligibility = validate_implementation_eligibility(project_root, eligibility_request)
            if validated_eligibility.get("state") != "ready":
                raise ValueError("scoped-completion-proof-required")
        route = module.route_scoped_implementation_assessment(
            history=history, assessment=assessment, eligible_task_ids=payload["eligible_task_ids"],
            declared_node_ids=nodes, previous_assessment=previous,
            generic_route=route_loop_assessment, retained_history_sha256=payload["retained_history_sha256"],
            eligibility=(validated_eligibility.get("eligibility") if validated_eligibility else None),
            eligibility_sha256=(validated_eligibility.get("eligibility_sha256") if validated_eligibility else None))
        return {**route, "state": route["action"], "route": route,
                "history": history, "history_path": history_path}
    except (KeyError, TypeError, ValueError, OSError, RuntimeError) as error:
        reason = str(error) if str(error) else "implementation-route-invalid"
        return {"state": "blocked", "reason_code": reason,
                "resume_action": "reassess-current-scoped-implementation-route"}


def validate_scoped_implementation_progress(project_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Validate substantive progress after source work and apply the unchanged generic guard."""
    try:
        if implementation_scope_module is None or payload.get("controller_loop_mode") != "implementation_scope":
            raise ValueError("implementation-loop-carrier-required")
        required = {"controller_loop_mode", "scope", "trusted_request_reference", "retained_scope_sha256",
                    "retained_history_sha256", "assessment", "eligible_task_ids", "declared_node_ids",
                    "previous_assessment", "progress", "administrative_prerequisite_ids"}
        optional = {"trusted_requested_task_ids", "task_tracking_successors", "eligibility_request"}
        if not required.issubset(payload) or set(payload) - required - optional:
            raise ValueError("implementation-progress-scope-request-invalid")
        scope_binding = _scope_binding_payload(payload)
        _, scope, _, _ = _implementation_scope_binding(project_root, scope_binding)
        history, _ = _read_implementation_history(project_root, scope, payload["retained_history_sha256"])
        if history.get("source_attempts_started", 0) < 1:
            raise ValueError("implementation-progress-before-source-attempt")
        progress = validate_implementation_progress(Path(project_root), payload["progress"])
        if progress.get("state") != "ready":
            return progress
        administrative = payload["administrative_prerequisite_ids"]
        if (not isinstance(administrative, list)
                or any(not isinstance(task_id, str) or not re.fullmatch(r"T[0-9]{3}", task_id)
                       for task_id in administrative)
                or len(administrative) != len(set(administrative))):
            raise ValueError("administrative-prerequisite-ids-invalid")
        assessment = payload["assessment"]
        if not isinstance(assessment, dict) or assessment.get("resolved_ids") != progress.get("resolved_ids"):
            raise ValueError("implementation-substantive-assessment-mismatch")
        administrative_resolution_ids = {f"task:{task_id}" for task_id in administrative}
        if administrative_resolution_ids & set(progress.get("resolved_ids", [])):
            raise ValueError("administrative-proof-counted-as-source-progress")
        previous = payload["previous_assessment"]
        if (not isinstance(previous, dict)
                or administrative_resolution_ids & set(previous.get("resolved_ids", []))):
            raise ValueError("administrative-proof-counted-as-prior-source-progress")
        route_payload = {key: payload[key] for key in (
            "scope", "trusted_request_reference", "retained_scope_sha256", "retained_history_sha256",
            "assessment", "eligible_task_ids", "declared_node_ids", "previous_assessment")}
        route_payload.update({key: payload[key] for key in (
            "trusted_requested_task_ids", "task_tracking_successors", "eligibility_request") if key in payload})
        routed = route_scoped_implementation(Path(project_root), route_payload)
        if routed.get("state") == "blocked":
            return routed
        return {**progress, "state": routed["state"], "history": history,
                "scoped_route": routed["route"],
                "controller_loop_mode": "implementation_scope"}
    except (KeyError, TypeError, ValueError, OSError, RuntimeError) as error:
        reason = str(error) if str(error) else "implementation-progress-scope-invalid"
        return {"state": "blocked", "reason_code": reason,
                "resume_action": "reassess-substantive-progress-against-frozen-scope"}


def _controller_loop_modes(steps: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Collect reviewed specialized loop carriers from the complete graph."""
    result: list[dict[str, str]] = []
    for step in steps:
        if "controller_loop_mode" in step:
            result.append({"step_id": step["id"], "mode": step["controller_loop_mode"]})
        for branch in step.get("cases", {}).values() if isinstance(step.get("cases"), dict) else []:
            result.extend(_controller_loop_modes(branch))
        result.extend(_controller_loop_modes(step.get("default", [])))
        result.extend(_controller_loop_modes(step.get("steps", [])))
    return result


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
    selected_activation_parser = subparsers.add_parser("activate-selected-feature", help="revalidate and activate a selected roadmap snapshot")
    selected_activation_parser.add_argument("--project", type=Path, required=True)
    task_revision_parser = subparsers.add_parser("validate-task-revision", help="validate a bounded task-list correction")
    task_revision_parser.add_argument("--project", type=Path, required=True)
    task_revision_scope_parser = subparsers.add_parser(
        "task-revision-scope", help="digest a frozen task-revision scope before Tasker dispatch"
    )
    task_revision_preflight_parser = subparsers.add_parser(
        "task-revision-preflight", help="validate active feature and safely snapshot its task plan"
    )
    task_revision_preflight_parser.add_argument("--project", type=Path, required=True)
    resolve_parser = subparsers.add_parser("resolve-feature", help="resolve a typed roadmap reference without mutation")
    readiness_parser = subparsers.add_parser("readiness", help="assess FarmBoy preparation evidence without mutation")
    readiness_parser.add_argument("--project", type=Path, required=True)
    lifecycle_parser = subparsers.add_parser("phase-lifecycle", help="validate and prepare a phase lifecycle request without roadmap writes")
    lifecycle_parser.add_argument("--project", type=Path, required=True)
    for operation in ("implementation-scope", "implementation-eligibility", "implementation-activation",
                      "implementation-history", "implementation-route", "implementation-progress-scoped",
                      "post-pass-capture"):
        operation_parser = subparsers.add_parser(operation, help="validate scoped Implement evidence and routing")
        operation_parser.add_argument("--project", type=Path, required=True)
    for operation in ("implementation-baseline", "implementation-progress", "implementation-baseline-transition"):
        progress_parser = subparsers.add_parser(operation, help="freeze or validate independently reviewed defect progress")
        progress_parser.add_argument("--project", type=Path, required=True)
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
        definition["controller_loop_modes"] = _controller_loop_modes(definition["steps"])
        definition["preflight_inputs_valid"] = True
        definition["installation_fingerprints"] = installation_fingerprints(args.project)
        print(json.dumps(definition, sort_keys=True))
        return 0
    scoped_commands = {"implementation-scope", "implementation-eligibility", "implementation-activation",
                       "implementation-history", "implementation-route", "implementation-progress-scoped",
                       "post-pass-capture"}
    payload = (strict_lifecycle_json(sys.stdin.read())
               if args.command in scoped_commands | {"phase-lifecycle"} and strict_lifecycle_json
               else json.load(sys.stdin))
    operation_failed = False
    if args.command == "implementation-baseline":
        result = capture_implementation_baseline(args.project, payload)
    elif args.command == "implementation-baseline-transition":
        result = advance_implementation_baseline(args.project, payload)
    elif args.command == "implementation-progress":
        result = validate_implementation_progress(args.project, payload)
    elif args.command == "implementation-scope":
        result = validate_implementation_scope(args.project, payload)
    elif args.command == "implementation-eligibility":
        result = validate_implementation_eligibility(args.project, payload)
    elif args.command == "implementation-activation":
        result = validate_implementation_activation(args.project, payload)
    elif args.command == "implementation-history":
        result = append_implementation_execution_event(args.project, payload)
    elif args.command == "implementation-route":
        result = route_scoped_implementation(args.project, payload)
    elif args.command == "implementation-progress-scoped":
        result = validate_scoped_implementation_progress(args.project, payload)
    elif args.command == "post-pass-capture":
        result = capture_post_pass_state(args.project, payload)
    if args.command in scoped_commands | {"implementation-baseline", "implementation-baseline-transition", "implementation-progress"}:
        operation_failed = result.get("state") == "blocked"
    elif args.command == "activate-feature":
        result = activate_feature(args.project, payload["feature_directory"])
    elif args.command == "activate-selected-feature":
        result = activate_selected_feature(args.project, payload)
    elif args.command == "resolve-feature":
        if resolve_feature_reference is None:
            raise RuntimeError("feature reference resolver is unavailable")
        result = resolve_feature_reference(
            payload.get("reference"), payload.get("reference_kind", "auto"),
            payload.get("entries"), payload.get("menu_order"),
        ).to_dict()
    elif args.command == "readiness":
        feature_directory = payload.get("feature_directory")
        action = payload.get("action", "assess")
        if assess_readiness is None or not isinstance(feature_directory, str):
            result = {"schema_version": "1.0", "feature_directory": feature_directory,
                      "state": "blocked", "reason_code": "readiness-helper-unavailable",
                      "blocking_ids": ["readiness-helper-unavailable"], "pending_future_ids": [],
                      "criteria": [], "source_evidence": [],
                      "resume_action": "restore-the-reviewed-readiness-helper-and-rerun-analysis"}
        elif action == "assess":
            reviewer_report = payload.get("reviewer_report")
            if reviewer_report is not None and not isinstance(reviewer_report, dict):
                result = {"schema_version": "1.0", "feature_directory": feature_directory,
                          "state": "blocked", "reason_code": "readiness-review-payload-invalid",
                          "blocking_ids": ["readiness-review-payload-invalid"], "pending_future_ids": [],
                          "criteria": [], "source_evidence": [],
                          "resume_action": "provide-current-independent-review-evidence"}
            else:
                result = assess_readiness(args.project, feature_directory, reviewer_report)
        elif action == "record-review":
            reviewer_report = payload.get("reviewer_report")
            if not isinstance(reviewer_report, dict):
                operation_failed = True
                if recorder_error_report is None:
                    result = {"state": "blocked", "reason_code": "readiness-helper-unavailable",
                              "resume_action": "restore-the-reviewed-readiness-helper"}
                else:
                    result = recorder_error_report(feature_directory, "readiness-review-payload-invalid")
            else:
                if record_readiness_review is None:
                    operation_failed = True
                    result = {"state": "blocked", "reason_code": "readiness-helper-unavailable"}
                else:
                    try:
                        result = record_readiness_review(args.project, feature_directory, reviewer_report)
                    except (OSError, ReadinessError) as error:
                        operation_failed = True
                        result = recorder_error_report(feature_directory, str(error))

        else:
            result = {"state": "blocked", "reason_code": "readiness-action-invalid"}
    elif args.command == "phase-lifecycle":
        if not isinstance(payload, dict):
            operation_failed = True
            result = {"state": "blocked", "reason_code": "lifecycle-request-invalid",
                      "blocking_ids": ["lifecycle-request-invalid"],
                      "resume_action": "provide-a-strict-lifecycle-request"}
        elif payload.get("action") == "validate-start-history":
            if validate_recovery_start_history is None:
                operation_failed = True
                result = {"state": "blocked", "reason_code": "lifecycle-helper-unavailable",
                          "blocking_ids": ["lifecycle-helper-unavailable"],
                          "resume_action": "restore-the-reviewed-phase-lifecycle-helper"}
            else:
                try:
                    result = validate_recovery_start_history(args.project, payload)
                except (LifecycleError, KeyError, TypeError, ValueError) as error:
                    operation_failed = True
                    reason = str(error) or "start-history-validation-failed"
                    result = {"state": "blocked", "reason_code": reason,
                              "blocking_ids": [reason],
                              "resume_action": "restore-main-retained-start-history-and-authorization-inputs"}
        elif payload.get("action") == "validate-receipt":
            if validate_lifecycle_receipt is None or set(payload) != {"action", "receipt"}:
                operation_failed = True
                result = {"state": "blocked", "reason_code": "lifecycle-receipt-validator-unavailable",
                          "blocking_ids": ["lifecycle-receipt-validator-unavailable"]}
            else:
                try:
                    result = {"state": "valid", "receipt": validate_lifecycle_receipt(payload["receipt"])}
                except (LifecycleError, KeyError, TypeError, ValueError) as error:
                    operation_failed = True
                    reason = str(error) or "lifecycle-receipt-invalid"
                    result = {"state": "blocked", "reason_code": reason,
                              "blocking_ids": [reason], "resume_action": "supply-a-contract-valid-current-receipt"}
        elif payload.get("action") in {"validate-specification-ready", "verify-effect"}:
            try:
                if workflow_lifecycle_check is None:
                    raise LifecycleError("lifecycle-helper-unavailable")
                result = workflow_lifecycle_check(args.project, payload)
                operation_failed = result.get("state") == "blocked"
            except (LifecycleError, ImportError, OSError, RuntimeError, KeyError, TypeError, ValueError, AttributeError) as error:
                operation_failed = True
                reason = str(error) if isinstance(error, LifecycleError) else "workflow-lifecycle-check-failed"
                result = {"state": "blocked", "reason_code": reason,
                          "blocking_ids": [reason], "resume_action": "restore-current-workflow-evidence"}
        elif payload.get("action") in {"prepare", "revalidate"}:
            operation = prepare_phase_lifecycle if payload.get("action") == "prepare" else revalidate_phase_lifecycle
            if operation is None:
                operation_failed = True
                result = {"state": "blocked", "reason_code": "lifecycle-helper-unavailable",
                          "blocking_ids": ["lifecycle-helper-unavailable"],
                          "resume_action": "restore-the-reviewed-phase-lifecycle-helper"}
            else:
                result = operation(args.project, payload)
                operation_failed = result.get("state") == "blocked"
        else:
            operation_failed = True
            result = {"state": "blocked", "reason_code": "lifecycle-action-invalid",
                      "blocking_ids": ["lifecycle-action-invalid"],
                      "resume_action": "use-prepare-revalidate-or-validate-receipt"}
    elif args.command == "validate-task-revision":
        result = validate_task_revision(args.project, payload)
    elif args.command == "task-revision-scope":
        try:
            feature_directory = payload["feature_directory"]
            tasks_path = payload["tasks_path"]
            frozen_scope = payload["frozen_scope"]
            if (not isinstance(feature_directory, str) or not isinstance(tasks_path, str)
                    or not isinstance(frozen_scope, dict)):
                raise ValueError("invalid frozen scope")
            result = {"scope_sha256": task_revision_scope_digest(feature_directory, tasks_path, frozen_scope)}
        except (KeyError, TypeError, ValueError):
            result = {"state": "blocked", "reason_code": "task-revision-frozen-scope-invalid"}
    elif args.command == "task-revision-preflight":
        result = task_revision_preflight(
            args.project, payload.get("feature_directory"), payload.get("tasks_path"),
            payload.get("expected_tasks_sha256"), payload.get("expected_specification_sha256"),
        )
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
    return 2 if operation_failed else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as error:
        print(f"FarmBoy controller preflight failed: {error}", file=sys.stderr)
        raise SystemExit(1)

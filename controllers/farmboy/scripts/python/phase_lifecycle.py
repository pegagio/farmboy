#!/usr/bin/env python3
"""Validate workflow-owned lifecycle evidence and prepare generic roadmap deltas."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


VERSION = "1.0"
POLICY_SHA256 = "09738d2d65ab12117308d586f77a2140a1cedebbad9d9bc33f0408fb822f1bd4"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,95}$")
STATUSES = ("planned", "specced", "in-progress", "implemented", "verified")
# These roadmap dispositions are valid observations but are deliberately not
# orderable lifecycle milestones. Preserve them through snapshot validation so
# the owner can return its focused operator question instead of an adapter
# schema blocker.
NON_ORDERABLE_STATUSES = {"deferred", "abandoned", "undecided", "needs-info"}
SNAPSHOT_STATUSES = {*STATUSES, *NON_ORDERABLE_STATUSES}
MILESTONES = {"specify": "specced", "implement": "in-progress", "closeout": "implemented"}
OWNERS = {value: key for key, value in MILESTONES.items()}
CHECKS = {
    "specced": {"authoring-quality", "clarification", "independent-review", "roadmap-brief", "linkage", "dependencies", "consequential-decisions"},
    "in-progress": {"current-artifacts", "dependencies", "readiness", "eligible-scope", "native-assignments"},
    "implemented": {"full-scope-completion", "attributable-delta", "convergence", "independent-code-review", "validation", "no-buildable-defects", "future-obligations-separated"},
}
ROLES = {
    "specced": {"FarmBoy Reviewer", "FarmBoy Roadmap Agent"},
    "in-progress": {"FarmBoy Reviewer", "FarmBoy Readiness Checker"},
    "implemented": {"FarmBoy Code Reviewer"},
}
ASSESSMENT_FIELDS = {"schema_version", "kind", "reviewer", "state", "feature_directory", "scope_sha256", "artifact_digests", "required_check_ids", "satisfied_check_ids", "unresolved_ids"}
SNAPSHOT_FIELDS = {"schema_version", "feature_directory", "entry_id", "phase", "workflow_id", "workflow_version", "run_id", "current_status", "source_map", "dependency_states", "scope_sha256", "pending_future_ids"}
REQUEST_FIELDS = {"schema_version", "action", "phase", "feature_directory", "entry_id", "run_id", "workflow_id", "workflow_version", "mode", "decision_reference", "milestone_evidence", "snapshot"}
PROPOSAL_FIELDS = {"schema_version", "snapshot", "milestone_evidence", "decision", "from_status", "to_status", "expected_roadmap_sha256", "patch_sha256", "effect_id", "recovery"}
EVIDENCE_FIELDS = {"milestone", "owning_phase", "assessments", "required_check_ids", "satisfied_check_ids", "unresolved_ids", "artifact_digests", "historical_activity", "pending_future_ids"}
RECEIPT_COMMON = {"schema_version", "feature_directory", "entry_id", "phase", "scope_sha256", "evidence", "effect_state", "record_state"}
START_HISTORY_FIELDS = {"action", "schema_version", "feature_directory", "current_scope_sha256", "trusted_inputs"}
START_HISTORY_INPUTS = {
    "source_run", "baseline", "original_spec", "current_spec", "status_run",
    "status_authorization", "status_effect", "status_validation", "feature_pointer",
}
START_ATTESTATION_FIELDS = {
    "schema_version", "kind", "reviewer", "state", "feature_directory", "scope_sha256",
    "workflow_id", "workflow_version", "run_id", "step_id", "child_id", "source_run_id",
    "original_scope_sha256", "occurred_at", "history_validation", "recorded_dispatch", "dispatch_witness",
    "required_check_ids", "satisfied_check_ids", "unresolved_ids", "artifact_digests",
}
START_DISPATCH_WITNESS_FIELDS = {
    "schema_version", "kind", "feature_directory", "scope_sha256", "workflow_id",
    "workflow_version", "run_id", "step_id", "agent", "child_id", "source_summary",
}
START_CHECKS = {
    "recorded-implement-invocation", "completed-implementation-effect", "original-occurrence-time",
    "source-scope-link", "authorized-status-only-bridge",
}


class LifecycleError(ValueError):
    """A lifecycle packet is unsafe, stale, or outside the approved contract."""


def strict_json(text: str) -> Any:
    """Decode JSON while rejecting duplicate keys and non-finite numbers."""
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise LifecycleError("duplicate-json-key")
            result[key] = value
        return result

    def invalid(_: str) -> None:
        raise LifecycleError("nonfinite-json-value")

    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)
    except LifecycleError:
        raise
    except (ValueError, TypeError) as error:
        raise LifecycleError("invalid-json") from error


def _no_nulls(value: Any) -> None:
    if value is None:
        raise LifecycleError("null-value-invalid")
    if isinstance(value, dict):
        for item in value.values():
            _no_nulls(item)
    elif isinstance(value, list):
        for item in value:
            _no_nulls(item)


def _exact(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    _no_nulls(value)
    if not isinstance(value, dict) or set(value) != fields:
        raise LifecycleError(f"{label}-schema-invalid")
    return value


def _relative(value: Any) -> str:
    if (not isinstance(value, str) or not value or value.startswith(("/", "~")) or "\\" in value
            or ":" in value or any(ord(char) < 32 for char in value)
            or any(part in {"", ".", ".."} for part in value.split("/"))):
        raise LifecycleError("unsafe-relative-path")
    path = PurePosixPath(value)
    if path.is_absolute():
        raise LifecycleError("unsafe-relative-path")
    return value


def _hash(value: Any) -> str:
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise LifecycleError("digest-invalid")
    return value


def _id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value) or value in {".", ".."}:
        raise LifecycleError(f"{label}-invalid")
    return value


def _digest_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _read_current(project: Path, path: str) -> bytes:
    relative = _relative(path)
    candidate = project
    for part in PurePosixPath(relative).parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise LifecycleError("source-path-symlink")
    try:
        raw = candidate.read_bytes()
    except OSError as error:
        raise LifecycleError("source-file-unavailable") from error
    if not candidate.is_file():
        raise LifecycleError("source-file-unavailable")
    return raw


def _string_list(value: Any, label: str, *, unique: bool = True) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise LifecycleError(f"{label}-invalid")
    if unique and len(set(value)) != len(value):
        raise LifecycleError(f"{label}-duplicate")
    return value


def _validate_snapshot(snapshot: Any) -> dict[str, Any]:
    snapshot = _exact(snapshot, SNAPSHOT_FIELDS, "snapshot")
    if snapshot["schema_version"] != VERSION or snapshot["phase"] not in MILESTONES:
        raise LifecycleError("snapshot-version-or-phase-invalid")
    for field in ("feature_directory",):
        path = _relative(snapshot[field])
        if not path.startswith("specs/"):
            raise LifecycleError("feature-directory-invalid")
    for field in ("entry_id", "workflow_id", "workflow_version", "run_id"):
        _id(snapshot[field], field)
    if snapshot["current_status"] not in SNAPSHOT_STATUSES:
        raise LifecycleError("lifecycle-status-invalid")
    _hash(snapshot["scope_sha256"])
    _string_list(snapshot["pending_future_ids"], "pending-future-ids")
    if not isinstance(snapshot["source_map"], dict) or not snapshot["source_map"]:
        raise LifecycleError("source-map-invalid")
    for path, expected in snapshot["source_map"].items():
        _relative(path)
        _hash(expected)
    if not isinstance(snapshot["dependency_states"], list):
        raise LifecycleError("dependency-states-invalid")
    for state in snapshot["dependency_states"]:
        _exact(state, {"entry_id", "status"}, "dependency-state")
        _id(state["entry_id"], "dependency-entry")
        if state["status"] not in STATUSES:
            raise LifecycleError("dependency-status-invalid")
    return snapshot


def _validate_reference(project: Path, reference: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    reference = _exact(reference, {"path", "sha256", "kind"}, "evidence-reference")
    path = _relative(reference["path"])
    expected = _hash(reference["sha256"])
    if not isinstance(reference["kind"], str) or not reference["kind"].strip():
        raise LifecycleError("evidence-kind-invalid")
    actual = _digest_bytes(_read_current(project, path))
    if actual != expected:
        raise LifecycleError("stale-assessment-evidence")
    if path not in snapshot["source_map"] or snapshot["source_map"][path] != expected:
        raise LifecycleError("evidence-snapshot-mismatch")
    return reference


def _trusted_start_inputs(project: Path, value: Any) -> tuple[dict[str, bytes], dict[str, dict[str, str]]]:
    """Read main-task-retained recovery witnesses and reject incomplete references."""
    if not isinstance(value, dict) or set(value) != START_HISTORY_INPUTS:
        raise LifecycleError("start-history-trusted-inputs-invalid")
    raw_by_name: dict[str, bytes] = {}
    refs: dict[str, dict[str, str]] = {}
    for name in sorted(START_HISTORY_INPUTS):
        reference = _exact(value[name], {"path", "sha256"}, "start-history-reference")
        path = _relative(reference["path"])
        digest = _hash(reference["sha256"])
        raw = _read_current(project, path)
        if _digest_bytes(raw) != digest:
            raise LifecycleError("start-history-stale-trusted-input")
        refs[name] = {"path": path, "sha256": digest}
        raw_by_name[name] = raw
    return raw_by_name, refs

def _status_only_bridge(original: bytes, current: bytes) -> bool:
    """Allow the one recorded Draft-to-Complete header change, byte for byte."""
    original_lines = original.splitlines(keepends=True)
    current_lines = current.splitlines(keepends=True)
    status_pattern = re.compile(rb"^\*\*Status\*\*: (Draft|Complete)(\r?\n)?$")
    original_matches = [index for index, line in enumerate(original_lines) if status_pattern.fullmatch(line)]
    current_matches = [index for index, line in enumerate(current_lines) if status_pattern.fullmatch(line)]
    if len(original_matches) != 1 or current_matches != original_matches:
        return False
    index = original_matches[0]
    if not status_pattern.fullmatch(original_lines[index]).group(1) == b"Draft":
        return False
    if not status_pattern.fullmatch(current_lines[index]).group(1) == b"Complete":
        return False
    expected = list(original_lines)
    match = status_pattern.fullmatch(expected[index])
    assert match is not None
    expected[index] = b"**Status**: Complete" + (match.group(2) or b"")
    return expected == current_lines


def validate_recovery_start_history(project: Path, packet: Any) -> dict[str, Any]:
    """Return typed read-only proof of a recorded Implement start and authorized scope bridge.

    The caller must supply source paths and digests retained by the main task;
    this helper never discovers authority by following child-provided filenames.
    """
    packet = _exact(packet, START_HISTORY_FIELDS, "start-history-packet")
    if packet["action"] != "validate-start-history":
        raise LifecycleError("start-history-action-invalid")
    if packet["schema_version"] != VERSION:
        raise LifecycleError("start-history-version-invalid")
    feature = _relative(packet["feature_directory"])
    current_scope = _hash(packet["current_scope_sha256"])
    raw, refs = _trusted_start_inputs(project, packet["trusted_inputs"])
    if refs["current_spec"]["path"] != f"{feature}/spec.md" or refs["feature_pointer"]["path"] != ".specify/feature.json":
        raise LifecycleError("start-history-target-reference-invalid")
    if _digest_bytes(raw["current_spec"]) != current_scope:
        raise LifecycleError("start-history-current-scope-mismatch")
    try:
        summary = strict_json(raw["source_run"].decode("utf-8"))
        baseline_record = strict_json(raw["baseline"].decode("utf-8"))
        status_run = strict_json(raw["status_run"].decode("utf-8"))
        status_authorization = strict_json(raw["status_authorization"].decode("utf-8"))
        status_effect = strict_json(raw["status_effect"].decode("utf-8"))
        status_validation = strict_json(raw["status_validation"].decode("utf-8"))
        pointer = strict_json(raw["feature_pointer"].decode("utf-8"))
    except (UnicodeDecodeError, LifecycleError) as error:
        raise LifecycleError("start-history-record-invalid") from error
    baseline = _exact(baseline_record, {"baseline", "baseline_sha256", "remaining_ids", "state"}, "start-history-baseline")
    baseline_body = baseline["baseline"]
    if not isinstance(baseline_body, dict):
        raise LifecycleError("start-history-baseline-invalid")
    baseline_digest = _digest_bytes(json.dumps(
        baseline_body, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    if baseline["baseline_sha256"] != baseline_digest:
        raise LifecycleError("start-history-baseline-digest-invalid")
    if (not isinstance(summary.get("run_id"), str) or not summary["run_id"]
            or summary.get("workflow_id") != "farmboy-implement"
            or summary.get("status") != "stopped"
            or not isinstance(summary.get("started_at"), str)
            or not isinstance(summary.get("steps"), dict)
            or not isinstance(summary.get("child_tasks"), list)
            or not isinstance(summary.get("effective_assignments"), list)
            or not isinstance(summary.get("changed_files"), list)):
        raise LifecycleError("start-history-run-identity-invalid")
    try:
        started = datetime.fromisoformat(summary["started_at"].replace("Z", "+00:00"))
    except ValueError as error:
        raise LifecycleError("start-history-occurrence-invalid") from error
    if started.tzinfo is None or started.utcoffset() is None:
        raise LifecycleError("start-history-occurrence-invalid")
    source_feature = feature
    if (baseline_body.get("feature_directory") != source_feature
            or baseline_body.get("specification_sha256") != _digest_bytes(raw["original_spec"])
            or baseline_body.get("pointer_sha256") != _digest_bytes(raw["feature_pointer"])
            or pointer.get("feature_directory") != source_feature
            or summary.get("baseline_evidence") != {
                "baseline_sha256": baseline_digest,
                "path": refs["baseline"]["path"],
            }):
        raise LifecycleError("start-history-source-scope-mismatch")
    steps = summary["steps"]
    if not isinstance(steps.get("implement-eligible-work"), dict) or steps["implement-eligible-work"].get("status") != "completed":
        raise LifecycleError("start-history-implementation-step-missing")
    if not isinstance(steps.get("capture-implementation-baseline"), dict) or steps["capture-implementation-baseline"].get("status") != "completed":
        raise LifecycleError("start-history-baseline-step-missing")
    coder_children = [child for child in summary["child_tasks"]
                      if isinstance(child, dict) and child.get("agent") == "FarmBoy Coder"
                      and child.get("step_id") == "implement-eligible-work"
                      and isinstance(child.get("child_id"), str) and child["child_id"]]
    assignments = summary["effective_assignments"]
    if (not coder_children or not isinstance(assignments, list)
            or not any(isinstance(item, dict) and item.get("agent_name") == "FarmBoy Coder"
                       and item.get("step_id") == "implement-eligible-work" for item in assignments)
            or not any(isinstance(path, str) and path.startswith(source_feature + "/")
                       for path in summary["changed_files"])):
        raise LifecycleError("start-history-implementation-effect-missing")
    status_steps = status_run.get("steps")
    status_changed_files = status_run.get("changed_files")
    if (not isinstance(status_steps, dict) or not isinstance(status_changed_files, list)
            or not isinstance(status_run.get("run_id"), str) or not status_run["run_id"]
            or status_run.get("workflow_id") != "farmboy-closeout"
            or not isinstance(status_steps.get("mark-converged-specification-complete"), dict)
            or status_steps["mark-converged-specification-complete"].get("status") != "completed"
            or refs["current_spec"]["path"] not in status_changed_files):
        raise LifecycleError("start-history-status-run-invalid")
    if (status_authorization.get("status_action") != "run"
            or status_authorization.get("feature_directory") != source_feature
            or status_authorization.get("spec_before_sha256") != baseline_body.get("specification_sha256")
            or not isinstance(status_authorization.get("authority"), str)
            or not status_authorization["authority"].strip()):
        raise LifecycleError("start-history-status-authorization-invalid")
    if (status_effect.get("step_id") != "mark-converged-specification-complete"
            or status_effect.get("kind") != "bounded-existing-specification-status-update"
            or status_effect.get("feature_directory") != source_feature
            or status_effect.get("before_status") != "Draft"
            or status_effect.get("after_status") != "Complete"
            or status_effect.get("before_sha256") != baseline_body.get("specification_sha256")
            or status_effect.get("after_sha256") != current_scope
            or status_effect.get("exact_diff") != "**Status**: Draft -> **Status**: Complete"
            or status_effect.get("other_specification_bytes_preserved") is not True):
        raise LifecycleError("start-history-status-effect-invalid")
    if (status_validation.get("state") != "ready"
            or status_validation.get("spec_path") != refs["current_spec"]["path"]
            or status_validation.get("before_sha256") != baseline_body.get("specification_sha256")
            or status_validation.get("after_sha256") != current_scope
            or status_validation.get("allowed_change") != "Status Draft to Complete only"
            or status_validation.get("requirements_and_all_other_bytes_preserved") is not True
            or status_validation.get("convergence_intent_preserved") is not True
            or status_validation.get("feature_acceptance_established") is not False):
        raise LifecycleError("start-history-status-bridge-unverified")
    future_ids = status_validation.get("future_manual_task_ids")
    remaining_ids = baseline_record.get("remaining_ids")
    task_records = baseline_body.get("tasks")
    if (not isinstance(future_ids, list)
            or any(not isinstance(identifier, str) or not re.fullmatch(r"T[0-9]{3}", identifier)
                   for identifier in future_ids)
            or len(future_ids) != len(set(future_ids))
            or not isinstance(remaining_ids, list)
            or not isinstance(task_records, dict)
            or not set(future_ids).issubset({item.removeprefix("task:") for item in remaining_ids
                                             if isinstance(item, str) and item.startswith("task:")})
            or any(not isinstance(task_records.get(identifier), dict)
                   or task_records[identifier].get("marker") != " " for identifier in future_ids)):
        raise LifecycleError("start-history-future-obligations-not-preserved")
    if not _status_only_bridge(raw["original_spec"], raw["current_spec"]):
        raise LifecycleError("start-history-scope-bridge-invalid")
    return {
        "schema_version": VERSION,
        "kind": "authorized-implementation-start-history",
        "state": "validated",
        "feature_directory": feature,
        "source_run_id": summary["run_id"],
        "source_workflow_id": summary["workflow_id"],
        "occurred_at": summary["started_at"],
        "original_scope_sha256": baseline_body["specification_sha256"],
        "scope_sha256": current_scope,
        "completed_step_ids": ["capture-implementation-baseline", "implement-eligible-work"],
        "future_manual_task_ids": future_ids,
        "trusted_inputs": refs,
    }


def _validate_start_attestation(project: Path, reference: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    record = strict_json(_read_current(project, reference["path"]).decode("utf-8"))
    record = _exact(record, START_ATTESTATION_FIELDS, "start-attestation")
    if (record["schema_version"] != VERSION or record["kind"] != "authorized-implementation-start"
            or record["reviewer"] != "FarmBoy Reviewer" or record["state"] != "ready"
            or record["feature_directory"] != snapshot["feature_directory"]
            or record["scope_sha256"] != snapshot["scope_sha256"]
            or record["workflow_id"] != snapshot["workflow_id"]
            or record["workflow_version"] != snapshot["workflow_version"]
            or record["run_id"] != snapshot["run_id"]
            or record["step_id"] != "attest-recovery-start"
            or not isinstance(record["child_id"], str) or not record["child_id"].strip()):
        raise LifecycleError("start-attestation-identity-invalid")
    dispatch = _exact(record["recorded_dispatch"],
                      {"agent", "step_id", "workflow_id", "workflow_version", "run_id", "child_id"},
                      "start-attestation-dispatch")
    if (dispatch["agent"] != "FarmBoy Reviewer" or dispatch["step_id"] != "attest-recovery-start"
            or dispatch["workflow_id"] != snapshot["workflow_id"]
            or dispatch["workflow_version"] != snapshot["workflow_version"]
            or dispatch["run_id"] != snapshot["run_id"] or dispatch["child_id"] != record["child_id"]):
        raise LifecycleError("start-attestation-dispatch-mismatch")
    witness_ref = _exact(record["dispatch_witness"], {"path", "sha256"}, "start-dispatch-witness-reference")
    witness_path = _relative(witness_ref["path"])
    expected_witness_path = (
        f".specify/farmboy-controllers/runs/{snapshot['run_id']}/recovery-start-dispatch-witness.json")
    witness_digest = _hash(witness_ref["sha256"])
    if (witness_path != expected_witness_path
            or snapshot["source_map"].get(witness_path) != witness_digest
            or _digest_bytes(_read_current(project, witness_path)) != witness_digest):
        raise LifecycleError("start-attestation-dispatch-witness-stale")
    witness = strict_json(_read_current(project, witness_path).decode("utf-8"))
    witness = _exact(witness, START_DISPATCH_WITNESS_FIELDS, "start-dispatch-witness")
    source_summary_ref = _exact(witness["source_summary"], {"path", "sha256"},
                                 "start-dispatch-source-summary")
    source_summary_path = _relative(source_summary_ref["path"])
    expected_source_summary_path = (
        f".specify/farmboy-controllers/runs/{snapshot['run_id']}/dispatch-summary-at-capture.json")
    source_summary_digest = _hash(source_summary_ref["sha256"])
    if (source_summary_path != expected_source_summary_path
            or snapshot["source_map"].get(source_summary_path) != source_summary_digest
            or _digest_bytes(_read_current(project, source_summary_path)) != source_summary_digest):
        raise LifecycleError("start-attestation-dispatch-source-stale")
    captured_summary = strict_json(_read_current(project, source_summary_path).decode("utf-8"))
    if (witness["schema_version"] != VERSION
            or witness["kind"] != "main-retained-native-dispatch-witness"
            or witness["feature_directory"] != snapshot["feature_directory"]
            or witness["scope_sha256"] != snapshot["scope_sha256"]
            or witness["workflow_id"] != snapshot["workflow_id"]
            or witness["workflow_version"] != snapshot["workflow_version"]
            or witness["run_id"] != snapshot["run_id"]
            or witness["step_id"] != "attest-recovery-start"
            or witness["agent"] != "FarmBoy Reviewer"
            or witness["child_id"] != record["child_id"]
            or captured_summary.get("run_id") != witness["run_id"]
            or captured_summary.get("workflow_id") != witness["workflow_id"]
            or captured_summary.get("workflow_version") != witness["workflow_version"]):
        raise LifecycleError("start-attestation-dispatch-witness-invalid")
    captured_children = captured_summary.get("child_tasks")
    captured_assignments = captured_summary.get("effective_assignments")
    if (not isinstance(captured_children, list)
            or not any(isinstance(child, dict) and child.get("agent") == witness["agent"]
                       and child.get("step_id") == witness["step_id"]
                       and child.get("child_id") == witness["child_id"] for child in captured_children)
            or not isinstance(captured_assignments, list)
            or not any(isinstance(item, dict) and item.get("agent_name") == witness["agent"]
                       and item.get("step_id") == witness["step_id"] for item in captured_assignments)):
        raise LifecycleError("start-attestation-dispatch-capture-unverified")
    run_summary_path = f".specify/farmboy-controllers/runs/{snapshot['run_id']}/summary.json"
    run_summary = strict_json(_read_current(project, run_summary_path).decode("utf-8"))
    children = run_summary.get("child_tasks") if isinstance(run_summary, dict) else None
    assignments = run_summary.get("effective_assignments") if isinstance(run_summary, dict) else None
    if (not isinstance(run_summary, dict)
            or run_summary.get("run_id") != snapshot["run_id"]
            or run_summary.get("workflow_id") != snapshot["workflow_id"]
            or run_summary.get("workflow_version") != snapshot["workflow_version"]
            or not isinstance(children, list)
            or not any(isinstance(child, dict) and child.get("agent") == "FarmBoy Reviewer"
                       and child.get("step_id") == "attest-recovery-start"
                       and child.get("child_id") == witness["child_id"] for child in children)
            or not isinstance(assignments, list)
            or not any(isinstance(item, dict) and item.get("agent_name") == "FarmBoy Reviewer"
                       and item.get("step_id") == "attest-recovery-start" for item in assignments)):
        raise LifecycleError("start-attestation-main-dispatch-unverified")
    required = set(_string_list(record["required_check_ids"], "start-attestation-required-checks"))
    satisfied = set(_string_list(record["satisfied_check_ids"], "start-attestation-satisfied-checks"))
    unresolved = _string_list(record["unresolved_ids"], "start-attestation-unresolved-ids")
    if required != START_CHECKS or satisfied != START_CHECKS or unresolved:
        raise LifecycleError("start-attestation-incomplete")
    _id(record["source_run_id"], "start-source-run")
    _hash(record["original_scope_sha256"])
    _hash(record["scope_sha256"])
    reference = _exact(record["history_validation"], {"path", "sha256"}, "start-history-validation-reference")
    validation_path = _relative(reference["path"])
    if validation_path != f"{snapshot['feature_directory']}/validation/phase-lifecycle/start-history-validation.json":
        raise LifecycleError("start-history-validation-path-invalid")
    validation_digest = _hash(reference["sha256"])
    if snapshot["source_map"].get(validation_path) != validation_digest:
        raise LifecycleError("start-history-validation-snapshot-mismatch")
    if _digest_bytes(_read_current(project, validation_path)) != validation_digest:
        raise LifecycleError("start-history-validation-stale")
    validated = strict_json(_read_current(project, validation_path).decode("utf-8"))
    validated = _exact(validated, {
        "schema_version", "kind", "state", "feature_directory", "source_run_id", "source_workflow_id",
        "occurred_at", "original_scope_sha256", "scope_sha256", "completed_step_ids",
        "future_manual_task_ids", "trusted_inputs",
    }, "validated-start-history")
    if (validated["schema_version"] != VERSION
            or validated["kind"] != "authorized-implementation-start-history"
            or validated["state"] != "validated"
            or validated["feature_directory"] != snapshot["feature_directory"]
            or validated["source_workflow_id"] != "farmboy-implement"
            or validated["scope_sha256"] != snapshot["scope_sha256"]
            or record["source_run_id"] != validated["source_run_id"]
            or record["occurred_at"] != validated["occurred_at"]
            or record["original_scope_sha256"] != validated["original_scope_sha256"]
            or validated["completed_step_ids"] != ["capture-implementation-baseline", "implement-eligible-work"]):
        raise LifecycleError("start-attestation-history-mismatch")
    expected_history = validate_recovery_start_history(project, {
        "action": "validate-start-history", "schema_version": VERSION,
        "feature_directory": validated["feature_directory"],
        "current_scope_sha256": validated["scope_sha256"],
        "trusted_inputs": validated["trusted_inputs"],
    })
    if expected_history != validated:
        raise LifecycleError("start-history-validation-mismatch")
    for trusted in validated["trusted_inputs"].values():
        if snapshot["source_map"].get(trusted["path"]) != trusted["sha256"]:
            raise LifecycleError("start-history-source-snapshot-mismatch")
    try:
        occurred_at = datetime.fromisoformat(record["occurred_at"].replace("Z", "+00:00"))
    except (AttributeError, ValueError) as error:
        raise LifecycleError("start-attestation-occurrence-invalid") from error
    if occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
        raise LifecycleError("start-attestation-occurrence-invalid")
    artifacts = record["artifact_digests"]
    if not isinstance(artifacts, dict) or artifacts.get(f"{snapshot['feature_directory']}/spec.md") != snapshot["scope_sha256"]:
        raise LifecycleError("start-attestation-current-inputs-missing")
    for path, expected in artifacts.items():
        relative = _relative(path)
        if _hash(expected) != _digest_bytes(_read_current(project, relative)):
            raise LifecycleError("start-attestation-stale-input")
        if snapshot["source_map"].get(relative) != expected:
            raise LifecycleError("start-attestation-snapshot-mismatch")
    return record


def _validate_assessment(project: Path, reference: dict[str, Any], snapshot: dict[str, Any], milestone: str) -> dict[str, Any]:
    raw = _read_current(project, reference["path"])
    record = strict_json(raw.decode("utf-8"))
    record = _exact(record, ASSESSMENT_FIELDS, "independent-assessment")
    if (record["schema_version"] != VERSION or record["kind"] != reference["kind"]
            or record["reviewer"] not in ROLES[milestone] or record["state"] not in {"ready", "complete"}
            or record["feature_directory"] != snapshot["feature_directory"]
            or record["scope_sha256"] != snapshot["scope_sha256"]):
        raise LifecycleError("independent-assessment-invalid")
    required = set(_string_list(record["required_check_ids"], "assessment-required-checks"))
    satisfied = set(_string_list(record["satisfied_check_ids"], "assessment-satisfied-checks"))
    unresolved = _string_list(record["unresolved_ids"], "assessment-unresolved-ids")
    if not required or required != satisfied or unresolved:
        raise LifecycleError("independent-assessment-incomplete")
    artifacts = record["artifact_digests"]
    if not isinstance(artifacts, dict):
        raise LifecycleError("assessment-artifacts-invalid")
    for path, expected in artifacts.items():
        relative = _relative(path)
        digest = _hash(expected)
        if _digest_bytes(_read_current(project, relative)) != digest:
            raise LifecycleError("stale-assessment-artifact")
        if relative not in snapshot["source_map"] or snapshot["source_map"][relative] != digest:
            raise LifecycleError("assessment-snapshot-mismatch")
    spec_path = f"{snapshot['feature_directory']}/spec.md"
    if artifacts.get(spec_path) != snapshot["scope_sha256"]:
        raise LifecycleError("assessment-scope-input-missing")
    if milestone == "implemented":
        feature = snapshot["feature_directory"]
        required_docs = {f"{feature}/spec.md", f"{feature}/plan.md", f"{feature}/tasks.md"}
        paths = {_relative(path) for path in artifacts}
        if not required_docs.issubset(paths):
            raise LifecycleError("implemented-assessment-documents-missing")
        if any(path.endswith("roadmap.md") or path.endswith("roadmap.yml")
               or path.startswith(".specify/memory/") for path in paths):
            raise LifecycleError("implemented-assessment-includes-mutable-ledger")
        code_paths = {path for path in paths if not path.startswith(feature + "/")
                      and not path.startswith(".specify/")}
        test_paths = {path for path in paths if path.startswith("tests/")
                      or "/validation/" in path or "/test" in path}
        if not code_paths or not test_paths:
            raise LifecycleError("implemented-assessment-code-or-test-proof-missing")
    return record


def _validate_group(project: Path, group: Any, snapshot: dict[str, Any], *, require_start_attestation: bool = False) -> dict[str, Any]:
    group = _exact(group, EVIDENCE_FIELDS, "milestone-evidence")
    milestone = group["milestone"]
    if milestone not in CHECKS or group["owning_phase"] != OWNERS[milestone]:
        raise LifecycleError("milestone-owner-mismatch")
    required = set(_string_list(group["required_check_ids"], "required-checks"))
    satisfied = set(_string_list(group["satisfied_check_ids"], "satisfied-checks"))
    unresolved = _string_list(group["unresolved_ids"], "unresolved-ids")
    if required != CHECKS[milestone] or satisfied != required or unresolved:
        raise LifecycleError("milestone-proof-incomplete")
    if not isinstance(group["artifact_digests"], dict):
        raise LifecycleError("artifact-digests-invalid")
    for path, expected in group["artifact_digests"].items():
        relative = _relative(path)
        digest = _hash(expected)
        actual = _digest_bytes(_read_current(project, relative))
        if actual != digest:
            raise LifecycleError("stale-artifact-evidence")
        if relative not in snapshot["source_map"] or snapshot["source_map"][relative] != digest:
            raise LifecycleError("artifact-snapshot-mismatch")
    if not isinstance(group["assessments"], list) or not group["assessments"]:
        raise LifecycleError("independent-assessment-missing")
    seen_roles: set[str] = set()
    reviewed_checks: set[str] = set()
    for ref in group["assessments"]:
        _validate_reference(project, ref, snapshot)
        assessment = _validate_assessment(project, ref, snapshot, milestone)
        seen_roles.add(assessment["reviewer"])
        reviewed_checks.update(assessment["satisfied_check_ids"])
    if not ROLES[milestone].issubset(seen_roles) or not CHECKS[milestone].issubset(reviewed_checks):
        raise LifecycleError("milestone-independent-coverage-incomplete")
    if not isinstance(group["historical_activity"], list):
        raise LifecycleError("historical-activity-invalid")
    start_attestations = []
    for ref in group["historical_activity"]:
        _validate_reference(project, ref, snapshot)
        if ref["kind"] == "authorized-implementation-start":
            start_attestations.append(_validate_start_attestation(project, ref, snapshot))
    if require_start_attestation and len(start_attestations) != 1:
        raise LifecycleError("authorized-start-attestation-required")
    if _string_list(group["pending_future_ids"], "pending-future-ids") != snapshot["pending_future_ids"]:
        raise LifecycleError("future-obligations-mismatch")
    return group


def validate_request(project: Path, request: Any) -> dict[str, Any]:
    """Validate strict shapes and all caller-supplied current evidence digests."""
    action = request.get("action") if isinstance(request, dict) else None
    fields = REQUEST_FIELDS | ({"proposal"} if action == "revalidate" else set())
    request = _exact(request, fields, "request")
    if request["schema_version"] != VERSION or action not in {"prepare", "revalidate"}:
        raise LifecycleError("request-version-or-action-invalid")
    if request["phase"] not in MILESTONES or request["mode"] not in {"normal", "recovery"}:
        raise LifecycleError("phase-or-mode-invalid")
    for field in ("entry_id", "run_id", "workflow_id", "workflow_version"):
        _id(request[field], field)
    feature = _relative(request["feature_directory"])
    if not feature.startswith("specs/"):
        raise LifecycleError("feature-directory-invalid")
    decision = _relative(request["decision_reference"])
    snapshot = _validate_snapshot(request["snapshot"])
    if any(snapshot[field] != request[field] for field in ("phase", "feature_directory", "entry_id", "run_id", "workflow_id", "workflow_version")):
        raise LifecycleError("request-snapshot-identity-mismatch")
    if not isinstance(request["milestone_evidence"], list):
        raise LifecycleError("milestone-evidence-invalid")
    seen: set[str] = set()
    for group in request["milestone_evidence"]:
        checked = _validate_group(
            project, group, snapshot,
            require_start_attestation=(request["phase"] == "closeout"
                                       and request["mode"] == "recovery"
                                       and snapshot["current_status"] == "specced"
                                       and isinstance(group, dict)
                                       and group.get("milestone") == "in-progress"),
        )
        if checked["milestone"] in seen:
            raise LifecycleError("duplicate-milestone-evidence")
        seen.add(checked["milestone"])
    for path, expected in snapshot["source_map"].items():
        if _digest_bytes(_read_current(project, path)) != expected:
            raise LifecycleError("stale-source-evidence")
    if snapshot["source_map"].get(f"{feature}/spec.md") != snapshot["scope_sha256"]:
        raise LifecycleError("scope-snapshot-mismatch")
    if decision not in snapshot["source_map"]:
        raise LifecycleError("decision-snapshot-missing")
    decision_record = strict_json(_read_current(project, decision).decode("utf-8"))
    decision_record = _exact(decision_record, {"schema_version", "policy_sha256", "feature_directory", "phase", "scope_sha256", "kind", "reference"}, "phase-decision")
    if (decision_record["schema_version"] != VERSION or decision_record["policy_sha256"] != POLICY_SHA256
            or decision_record["feature_directory"] != feature or decision_record["phase"] != request["phase"]
            or decision_record["scope_sha256"] != snapshot["scope_sha256"]
            or decision_record["kind"] not in {"routine-invocation", "operator-resolution"}
            or not isinstance(decision_record["reference"], str) or not decision_record["reference"].strip()
            or snapshot["source_map"][decision] != _digest_bytes(_read_current(project, decision))):
        raise LifecycleError("governing-contract-mismatch")
    if request["action"] == "revalidate":
        validate_proposal(request["proposal"])
    return request


def validate_proposal(proposal: Any) -> dict[str, Any]:
    """Validate a proposal without treating it as permission or applying it."""
    proposal = _exact(proposal, PROPOSAL_FIELDS, "proposal")
    if proposal["schema_version"] != VERSION:
        raise LifecycleError("proposal-version-invalid")
    snapshot = _validate_snapshot(proposal["snapshot"])
    _exact(proposal["decision"], {"reference", "sha256", "contract_sha256"}, "proposal-decision")
    _relative(proposal["decision"]["reference"])
    _hash(proposal["decision"]["sha256"])
    if proposal["decision"]["contract_sha256"] != POLICY_SHA256:
        raise LifecycleError("governing-contract-mismatch")
    for field in ("expected_roadmap_sha256", "patch_sha256"):
        _hash(proposal[field])
    if proposal["from_status"] not in STATUSES or proposal["to_status"] not in OWNERS:
        raise LifecycleError("proposal-status-invalid")
    if STATUSES.index(proposal["to_status"]) != STATUSES.index(proposal["from_status"]) + 1:
        raise LifecycleError("proposal-not-adjacent")
    target_index = STATUSES.index(proposal["to_status"])
    ceiling_index = STATUSES.index(MILESTONES[snapshot["phase"]])
    if target_index > ceiling_index:
        raise LifecycleError("proposal-owner-invalid")
    _id(proposal["effect_id"], "effect-id")
    recovery = _exact(proposal["recovery"], {"mode", "ceiling", "roadmap_path", "source_preimage", "verification"}, "recovery")
    if recovery["mode"] not in {"normal", "recovery"} or recovery["ceiling"] != MILESTONES[snapshot["phase"]]:
        raise LifecycleError("recovery-ceiling-invalid")
    if recovery["mode"] == "normal" and proposal["to_status"] != MILESTONES[snapshot["phase"]]:
        raise LifecycleError("normal-proposal-phase-mismatch")
    _relative(recovery["roadmap_path"])
    if not isinstance(recovery["source_preimage"], str) or not isinstance(recovery["verification"], list):
        raise LifecycleError("proposal-preimage-invalid")
    if not isinstance(proposal["milestone_evidence"], list):
        raise LifecycleError("proposal-evidence-invalid")
    seen: set[str] = set()
    for group in proposal["milestone_evidence"]:
        _exact(group, EVIDENCE_FIELDS, "milestone-evidence")
        if group["milestone"] in seen:
            raise LifecycleError("duplicate-milestone-evidence")
        seen.add(group["milestone"])
    operations = {key: value for key, value in proposal.items() if key != "patch_sha256"}
    operations["recovery"] = {key: value for key, value in recovery.items() if key != "verification"}
    actual_patch = hashlib.sha256(json.dumps(operations, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    if proposal["patch_sha256"] != actual_patch:
        raise LifecycleError("proposal-patch-digest-invalid")
    return proposal


def validate_receipt(receipt: Any) -> dict[str, Any]:
    """Apply the contract's strict discriminated receipt schema."""
    if not isinstance(receipt, dict):
        raise LifecycleError("receipt-schema-invalid")
    state = receipt.get("effect_state")
    state_fields = {
        "applied": {"effect_id", "owning_phase", "from_status", "to_status", "occurred_at", "roadmap_before_sha256", "roadmap_after_sha256"},
        "no-op": {"assessment_id", "retained_status", "roadmap_before_sha256", "roadmap_after_sha256"},
        "not-applied": {"proposed_effect_id", "owning_phase", "proposed_from_status", "proposed_to_status", "reason_code", "roadmap_before_sha256"},
        "indeterminate": {"proposed_effect_id", "owning_phase", "proposed_from_status", "proposed_to_status", "reason_code", "roadmap_before_sha256"},
    }
    if state not in state_fields:
        raise LifecycleError("receipt-effect-state-invalid")
    allowed = RECEIPT_COMMON | state_fields[state]
    optional = {"not-applied": {"roadmap_after_sha256"}, "indeterminate": {"observed_roadmap_sha256"}}.get(state, set())
    record_state = receipt.get("record_state")
    if record_state == "failed":
        allowed.add("record_error")
    elif record_state == "recovered" and state == "applied":
        allowed.add("recovery_evidence")
    elif record_state != "recorded":
        raise LifecycleError("receipt-record-state-invalid")
    if not allowed.issubset(receipt) or set(receipt) - allowed - optional:
        raise LifecycleError("receipt-schema-invalid")
    _no_nulls(receipt)
    if receipt["schema_version"] != VERSION or receipt["phase"] not in MILESTONES:
        raise LifecycleError("receipt-value-invalid")
    _relative(receipt["feature_directory"])
    _id(receipt["entry_id"], "receipt-entry")
    _hash(receipt["scope_sha256"])
    for field, value in receipt.items():
        if field.endswith("sha256"):
            _hash(value)
    evidence = receipt["evidence"]
    if not isinstance(evidence, list) or not evidence:
        raise LifecycleError("receipt-evidence-missing")
    for ref in evidence:
        _exact(ref, {"path", "sha256", "kind"}, "receipt-evidence")
        _relative(ref["path"])
        _hash(ref["sha256"])
        if not isinstance(ref["kind"], str) or not ref["kind"].strip():
            raise LifecycleError("receipt-evidence-invalid")
    if state == "applied":
        _id(receipt["effect_id"], "receipt-effect")
        if (receipt["to_status"] not in OWNERS or receipt["owning_phase"] != OWNERS[receipt["to_status"]]
                or receipt["from_status"] not in STATUSES
                or STATUSES.index(receipt["to_status"]) != STATUSES.index(receipt["from_status"]) + 1):
            raise LifecycleError("receipt-edge-invalid")
        if not isinstance(receipt["occurred_at"], str):
            raise LifecycleError("receipt-occurrence-invalid")
        try:
            occurred_at = datetime.fromisoformat(receipt["occurred_at"].replace("Z", "+00:00"))
        except ValueError as error:
            raise LifecycleError("receipt-occurrence-invalid") from error
        if occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
            raise LifecycleError("receipt-occurrence-invalid")
    elif state == "no-op":
        _id(receipt["assessment_id"], "receipt-assessment")
        if receipt["retained_status"] not in STATUSES or receipt["roadmap_before_sha256"] != receipt["roadmap_after_sha256"]:
            raise LifecycleError("receipt-no-op-invalid")
    else:
        _id(receipt["proposed_effect_id"], "receipt-proposed-effect")
        if (receipt["proposed_to_status"] not in OWNERS or receipt["owning_phase"] != OWNERS[receipt["proposed_to_status"]]
                or receipt["proposed_from_status"] not in STATUSES
                or STATUSES.index(receipt["proposed_to_status"]) != STATUSES.index(receipt["proposed_from_status"]) + 1
                or not isinstance(receipt["reason_code"], str) or not receipt["reason_code"]):
            raise LifecycleError("receipt-proposed-edge-invalid")
    if record_state == "failed" and not isinstance(receipt.get("record_error"), str):
        raise LifecycleError("receipt-record-error-invalid")
    if record_state == "recovered":
        recovery = receipt.get("recovery_evidence")
        if state != "applied" or not isinstance(recovery, list) or not recovery:
            raise LifecycleError("receipt-recovery-evidence-invalid")
        for ref in recovery:
            _exact(ref, {"path", "sha256", "kind"}, "recovery-evidence")
            _relative(ref["path"])
            _hash(ref["sha256"])
    return receipt


def validate_assessment(project: Path, assessment: Any, request: dict[str, Any]) -> dict[str, Any]:
    """Validate every read-only owner outcome before the workflow routes it."""
    if not isinstance(assessment, dict):
        raise LifecycleError("owner-assessment-schema-invalid")
    state = assessment.get("state")
    state_fields = {
        "ready": {"proposal"},
        "no-op": {"retained_status"},
        "blocked": {"resume_action"},
        "question": {"request"},
    }
    if state not in state_fields:
        raise LifecycleError("owner-assessment-state-invalid")
    required = {"state", "reason_code", "evidence", "blocking_ids"} | state_fields[state]
    if state != "blocked":
        required.add("snapshot")
    optional = {"snapshot"} if state == "blocked" else set()
    if not required.issubset(assessment) or set(assessment) - required - optional:
        raise LifecycleError("owner-assessment-schema-invalid")
    _no_nulls(assessment)
    if "snapshot" in assessment and assessment["snapshot"] != request["snapshot"]:
        raise LifecycleError("owner-assessment-snapshot-mismatch")
    _id(assessment["reason_code"], "assessment-reason")
    blocking_ids = _string_list(assessment["blocking_ids"], "assessment-blocking-ids")
    evidence = assessment["evidence"]
    if not isinstance(evidence, list) or (state in {"ready", "no-op"} and not evidence):
        raise LifecycleError("owner-assessment-evidence-invalid")
    for reference in evidence:
        _validate_reference(project, reference, request["snapshot"])
    if state in {"ready", "no-op"} and blocking_ids:
        raise LifecycleError("owner-assessment-unexpected-blocker")
    if state == "ready":
        proposal = validate_proposal(assessment["proposal"])
        if proposal["snapshot"] != request["snapshot"]:
            raise LifecycleError("lifecycle-proposal-snapshot-mismatch")
    elif state == "no-op":
        if assessment["retained_status"] not in STATUSES:
            raise LifecycleError("owner-assessment-retained-status-invalid")
    elif state == "blocked":
        action = assessment["resume_action"]
        if not isinstance(action, str) or not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", action):
            raise LifecycleError("owner-assessment-resumption-invalid")
        if not blocking_ids:
            raise LifecycleError("owner-assessment-blocker-missing")
    else:
        question = assessment["request"]
        _exact(question, {"kind", "step_id", "question", "options", "allow_custom_answer"}, "owner-question")
        if (question["kind"] != "question" or not isinstance(question["step_id"], str)
                or not question["step_id"] or not isinstance(question["question"], str)
                or not question["question"].strip() or not _string_list(question["options"], "question-options")
                or question["allow_custom_answer"] is not True or not blocking_ids):
            raise LifecycleError("owner-question-invalid")
    return assessment


def _workflow_module(project: Path) -> Any:
    """Load the policy shipped beside this controller, never extension policy."""
    script = Path(__file__).with_name("milestone_policy.py")
    spec = importlib.util.spec_from_file_location("farmboy_workflow_milestone_policy", script)
    if spec is None or spec.loader is None:
        raise LifecycleError("lifecycle-workflow-policy-unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def roadmap_delta(proposal: dict[str, Any]) -> str:
    """Render a complete authorized amendment through the ordinary write command."""
    validate_proposal(proposal)
    delta = {
        "roadmap_path": proposal["recovery"]["roadmap_path"],
        "entry_id": proposal["snapshot"]["entry_id"],
        "feature_directory": proposal["snapshot"]["feature_directory"],
        "expected_roadmap_sha256": proposal["expected_roadmap_sha256"],
        "from_status": proposal["from_status"], "to_status": proposal["to_status"],
        "authorization_reference": proposal["decision"]["reference"],
        "evidence_paths": sorted({ref["path"] for group in proposal["milestone_evidence"]
                                  for ref in group["assessments"] + group["historical_activity"]}),
    }
    return ("Apply this explicitly authorized roadmap delta: " + json.dumps(delta, sort_keys=True)
            + ". Revalidate the current configured path, entry identity, mapping and exact preimage digest immediately before effect; stop on drift. "
            "Change only the selected status heading, update the standard version, amendment date and Sync Impact Report with the authorization and evidence provenance. "
            "Preserve all other entry bytes and existing history. Report actual changes and failures; this delta grants no verification, acceptance or Git authority.")


def prepare(project: Path, request: Any) -> dict[str, Any]:
    """Validate current evidence against the locally owned milestone policy."""
    try:
        request = validate_request(project, request)
        policy = _workflow_module(project)
        try:
            result = policy.evaluate(project, request, __import__("yaml"))
        except policy.ContractError as error:
            raise LifecycleError(str(error)) from error
        result = validate_assessment(project, result, request)
        if result["state"] == "ready":
            result = {**result, "roadmap_delta": roadmap_delta(result["proposal"])}
        return result
    except LifecycleError as error:
        return {"state": "blocked", "reason_code": str(error), "evidence": [],
                "blocking_ids": [str(error)], "resume_action": "restore-current-approved-lifecycle-evidence-and-rerun"}
    except (ImportError, OSError, RuntimeError, TypeError, ValueError, KeyError, AttributeError):
        return {"state": "blocked", "reason_code": "lifecycle-workflow-evaluation-failed", "evidence": [],
                "blocking_ids": ["lifecycle-workflow-evaluation-failed"],
                "resume_action": "inspect-the-current-workflow-policy-and-rerun-preparation"}


def revalidate(project: Path, request: Any) -> dict[str, Any]:
    """Repeat preparation with the exact prior proposal and reject changed effects."""
    if not isinstance(request, dict) or request.get("action") != "revalidate":
        return {"state": "blocked", "reason_code": "revalidate-request-required", "evidence": [],
                "blocking_ids": ["revalidate-request-required"], "resume_action": "supply-the-original-prepared-proposal"}
    return prepare(project, request)


def workflow_check(project: Path, payload: Any) -> dict[str, Any]:
    """Validate authoring proof or independently read back a generic amendment."""
    import yaml
    policy = _workflow_module(project)
    if payload.get("action") == "validate-specification-ready":
        _exact(payload, {"action", "packet_path"}, "authoring-check")
        try:
            return {"state": "ready", **policy.validate_specification_ready(project, payload["packet_path"], yaml)}
        except policy.ContractError as error:
            raise LifecycleError(str(error)) from error
    _exact(payload, {"action", "proposal", "command_succeeded", "occurred_at"}, "effect-check")
    if payload["action"] != "verify-effect" or not isinstance(payload["command_succeeded"], bool):
        raise LifecycleError("effect-check-invalid")
    proposal = validate_proposal(payload["proposal"])
    try:
        occurred = datetime.fromisoformat(payload["occurred_at"].replace("Z", "+00:00"))
        if occurred.tzinfo is None or occurred.utcoffset() is None:
            raise ValueError("missing timezone")
    except (AttributeError, TypeError, ValueError) as error:
        raise LifecycleError("receipt-occurrence-invalid") from error
    roadmap = proposal["recovery"]["roadmap_path"]
    original = proposal["recovery"]["source_preimage"].encode()
    if _digest_bytes(original) != proposal["expected_roadmap_sha256"]:
        raise LifecycleError("proposal-preimage-invalid")
    snapshot = proposal["snapshot"]
    refs = next((group["assessments"] for group in proposal["milestone_evidence"]
                 if group["milestone"] == proposal["to_status"]), [])
    base = {"schema_version": VERSION, "feature_directory": snapshot["feature_directory"],
            "entry_id": snapshot["entry_id"], "phase": snapshot["phase"],
            "scope_sha256": snapshot["scope_sha256"], "evidence": refs, "record_state": "recorded"}
    reason = "write-effect-not-established"
    observed = None
    try:
        observed = _read_current(project, roadmap)
        ledger = policy.entries(original.decode())
        selected = ledger[snapshot["entry_id"]]
        if selected["status"] != proposal["from_status"] or selected["spec_dir"] != snapshot["feature_directory"]:
            raise LifecycleError("proposal-entry-preimage-invalid")
        heading = original.decode()[selected["start"]:selected["heading_end"]]
        updated = heading.replace(f"[status: {proposal['from_status']}]", f"[status: {proposal['to_status']}]", 1)
        expected = original.decode()[:selected["start"]] + updated + original.decode()[selected["heading_end"]:]
        def normalize(value: str) -> tuple[str, tuple[int, int, int], str]:
            # All prior reports and ledger bytes remain part of the preimage.
            footers = list(policy.FOOTER.finditer(value))
            if len(footers) != 1:
                raise LifecycleError("roadmap-version-footer-invalid")
            footer = footers[0]
            version = tuple(int(footer.group(i)) for i in (1, 2, 3))
            date = footer.group(0).rsplit(":", 1)[-1].strip()
            normalized = value[:footer.start()] + f"<version-footer ratified={footer[4]}>" + value[footer.end():]
            return normalized, version, date
        expected_text, before_version, _ = normalize(expected)
        impact_match = re.match(r"\A<!--\s*SYNC IMPACT REPORT\b.*?-->\n", observed.decode(), flags=re.S)
        if impact_match is None:
            raise LifecycleError("roadmap-delta-provenance-missing")
        impact = impact_match.group(0)
        actual_text, after_version, after_date = normalize(observed.decode()[impact_match.end():])
        if (actual_text != expected_text or after_version != (*before_version[:2], before_version[2] + 1)
                or after_date != occurred.astimezone(timezone.utc).date().isoformat()):
            raise LifecycleError("roadmap-delta-readback-mismatch")
        authorization = re.findall(r"^Authorization: (.*)$", impact, flags=re.M)
        evidence_lines = re.findall(r"^Evidence paths: (.*)$", impact, flags=re.M)
        expected_paths = sorted({ref["path"] for group in proposal["milestone_evidence"]
                                 for ref in group["assessments"] + group["historical_activity"]})
        if (authorization != [proposal["decision"]["reference"]] or len(evidence_lines) != 1
                or strict_json(evidence_lines[0]) != expected_paths):
            raise LifecycleError("roadmap-delta-provenance-missing")
        receipt = {**base, "effect_state": "applied", "effect_id": proposal["effect_id"],
                   "owning_phase": OWNERS[proposal["to_status"]], "from_status": proposal["from_status"],
                   "to_status": proposal["to_status"], "occurred_at": payload["occurred_at"],
                   "roadmap_before_sha256": proposal["expected_roadmap_sha256"], "roadmap_after_sha256": _digest_bytes(observed)}
    except (LifecycleError, policy.ContractError, KeyError, UnicodeError, ValueError) as error:
        reason = str(error) or reason
        state = "not-applied" if observed == original else "indeterminate"
        receipt = {**base, "effect_state": state, "proposed_effect_id": proposal["effect_id"],
                   "owning_phase": OWNERS[proposal["to_status"]], "proposed_from_status": proposal["from_status"],
                   "proposed_to_status": proposal["to_status"], "reason_code": reason,
                   "roadmap_before_sha256": proposal["expected_roadmap_sha256"]}
        if observed is not None:
            receipt["roadmap_after_sha256" if state == "not-applied" else "observed_roadmap_sha256"] = _digest_bytes(observed)
    source_stable = True
    for path, expected_sha256 in snapshot["source_map"].items():
        if path == roadmap:
            continue
        try:
            if _digest_bytes(_read_current(project, path)) != expected_sha256:
                source_stable = False
        except LifecycleError:
            source_stable = False
    try:
        for group in proposal["milestone_evidence"]:
            _validate_group(project, group, snapshot,
                            require_start_attestation=proposal["recovery"]["mode"] == "recovery"
                            and group["milestone"] == "in-progress" and snapshot["phase"] != "implement")
    except (LifecycleError, KeyError, TypeError, ValueError):
        source_stable = False
    try:
        if policy.roadmap_configuration(project, yaml)["roadmap_path"] != roadmap:
            source_stable = False
    except (policy.ContractError, OSError, KeyError, TypeError, ValueError):
        source_stable = False
    validate_receipt(receipt)
    receipt = _record_effect_receipt(project, proposal, receipt)
    verified = (receipt["effect_state"] == "applied" and receipt["record_state"] == "recorded"
                and source_stable and payload["command_succeeded"])
    if not source_stable:
        reason = "post-effect-source-changed"
    elif not payload["command_succeeded"]:
        reason = "roadmap-command-failed-after-readback"
    elif receipt["record_state"] == "failed":
        reason = receipt["record_error"]
    return {"state": "verified" if verified else "blocked", "receipt": receipt,
            "current_status": proposal["to_status"] if receipt["effect_state"] == "applied" else "unestablished",
            "reason_code": "generic-delta-independently-verified" if verified else reason,
            "resume_action": "retain-receipt-and-reassess-current-state-before-any-retry"}


def _record_effect_receipt(project: Path, proposal: dict, receipt: dict) -> dict:
    """Persist only workflow evidence; never mutate the independently owned ledger."""
    import os
    relative = f"{proposal['snapshot']['feature_directory']}/validation/phase-lifecycle/{proposal['effect_id']}.json"
    try:
        # Reject every existing symlink before creating directories or a record.
        _relative(relative)
        cursor = project
        for part in Path(relative).parts:
            cursor /= part
            if cursor.is_symlink():
                raise LifecycleError("receipt-path-symlink")
        target = project / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            retained = strict_json(_read_current(project, relative).decode())
            validate_receipt(retained)
            if retained != receipt:
                raise LifecycleError("receipt-collision-requires-reassessment")
            return retained
        raw = (json.dumps(receipt, sort_keys=True) + "\n").encode()
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        if _read_current(project, relative) != raw:
            raise LifecycleError("receipt-readback-mismatch")
    except (OSError, LifecycleError, ValueError):
        receipt = {**receipt, "record_state": "failed", "record_error": "workflow-receipt-persistence-failed"}
    return validate_receipt(receipt)

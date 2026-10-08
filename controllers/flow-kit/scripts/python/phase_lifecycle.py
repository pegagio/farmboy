#!/usr/bin/env python3
"""Validate lifecycle evidence and delegate read-only preparation to its owner."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from datetime import datetime
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
    "specced": {"FlowKit-Reviewer", "FlowKit-Roadmap Agent"},
    "in-progress": {"FlowKit-Reviewer", "FlowKit-Readiness Checker"},
    "implemented": {"FlowKit-Code Reviewer"},
}
ASSESSMENT_FIELDS = {"schema_version", "kind", "reviewer", "state", "feature_directory", "scope_sha256", "artifact_digests", "required_check_ids", "satisfied_check_ids", "unresolved_ids"}
SNAPSHOT_FIELDS = {"schema_version", "feature_directory", "entry_id", "phase", "workflow_id", "workflow_version", "run_id", "current_status", "source_map", "dependency_states", "scope_sha256", "pending_future_ids"}
REQUEST_FIELDS = {"schema_version", "action", "phase", "feature_directory", "entry_id", "run_id", "workflow_id", "workflow_version", "mode", "decision_reference", "milestone_evidence", "snapshot"}
PROPOSAL_FIELDS = {"schema_version", "snapshot", "milestone_evidence", "decision", "from_status", "to_status", "expected_roadmap_sha256", "patch_sha256", "effect_id", "recovery"}
EVIDENCE_FIELDS = {"milestone", "owning_phase", "assessments", "required_check_ids", "satisfied_check_ids", "unresolved_ids", "artifact_digests", "historical_activity", "pending_future_ids"}
RECEIPT_COMMON = {"schema_version", "feature_directory", "entry_id", "phase", "scope_sha256", "evidence", "effect_state", "record_state"}


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
    return record


def _validate_group(project: Path, group: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
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
    for ref in group["historical_activity"]:
        _validate_reference(project, ref, snapshot)
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
        checked = _validate_group(project, group, snapshot)
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


def _owner_module(project: Path) -> Any:
    """Load the registered compatible owner helper; no installed copy is edited."""
    script_relative = ".specify/extensions/flow-roadmap/scripts/python/phase_lifecycle.py"
    manifest_relative = ".specify/extensions/flow-roadmap/extension.yml"
    try:
        import yaml
    except ImportError as error:
        raise LifecycleError("lifecycle-owner-runtime-unavailable") from error
    try:
        manifest_raw = _read_current(project, manifest_relative)
        _read_current(project, script_relative)
    except LifecycleError as error:
        if str(error) == "source-file-unavailable":
            raise LifecycleError("lifecycle-owner-contract-unavailable") from error
        raise
    try:
        manifest = yaml.safe_load(manifest_raw.decode("utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise LifecycleError("lifecycle-owner-manifest-invalid") from error
    extension = manifest.get("extension", {}) if isinstance(manifest, dict) else {}
    if not isinstance(extension, dict):
        raise LifecycleError("lifecycle-owner-contract-unavailable")
    version = extension.get("version")
    if extension.get("id") != "flow-roadmap" or not isinstance(version, str):
        raise LifecycleError("lifecycle-owner-contract-unavailable")
    try:
        version_tuple = tuple(int(part) for part in version.split("."))
    except ValueError as error:
        raise LifecycleError("lifecycle-owner-version-invalid") from error
    if len(version_tuple) != 3 or version_tuple < (0, 3, 0):
        raise LifecycleError("lifecycle-owner-contract-unavailable")
    declared = [item.get("file") for item in (manifest.get("provides", {}).get("scripts", [])) if isinstance(item, dict)]
    if "scripts/python/phase_lifecycle.py" not in declared:
        raise LifecycleError("lifecycle-owner-contract-unavailable")
    script = project / script_relative
    spec = importlib.util.spec_from_file_location("flowkit_registered_roadmap_lifecycle", script)
    if spec is None or spec.loader is None:
        raise LifecycleError("lifecycle-owner-contract-unavailable")
    module = importlib.util.module_from_spec(spec)
    script_before = _digest_bytes(_read_current(project, script_relative))
    try:
        spec.loader.exec_module(module)
    except (ImportError, OSError, RuntimeError, ValueError) as error:
        raise LifecycleError("lifecycle-owner-contract-unavailable") from error
    if _digest_bytes(_read_current(project, script_relative)) != script_before:
        raise LifecycleError("lifecycle-owner-source-changed-during-load")
    if not callable(getattr(module, "evaluate", None)) or not callable(getattr(module, "validate_receipt", None)):
        raise LifecycleError("lifecycle-owner-contract-unavailable")
    return module


def prepare(project: Path, request: Any) -> dict[str, Any]:
    """Validate current evidence and ask the roadmap owner for read-only evaluation."""
    try:
        request = validate_request(project, request)
        owner = _owner_module(project)
        result = owner.evaluate(project, request, __import__("yaml"))
        return validate_assessment(project, result, request)
    except LifecycleError as error:
        return {"state": "blocked", "reason_code": str(error), "evidence": [],
                "blocking_ids": [str(error)], "resume_action": "restore-current-approved-lifecycle-evidence-and-rerun"}
    except (ImportError, OSError, RuntimeError, TypeError, ValueError):
        return {"state": "blocked", "reason_code": "lifecycle-owner-evaluation-failed", "evidence": [],
                "blocking_ids": ["lifecycle-owner-evaluation-failed"],
                "resume_action": "inspect-the-current-owner-package-and-rerun-preparation"}


def revalidate(project: Path, request: Any) -> dict[str, Any]:
    """Repeat preparation with the exact prior proposal and reject changed effects."""
    if not isinstance(request, dict) or request.get("action") != "revalidate":
        return {"state": "blocked", "reason_code": "revalidate-request-required", "evidence": [],
                "blocking_ids": ["revalidate-request-required"], "resume_action": "supply-the-original-prepared-proposal"}
    return prepare(project, request)

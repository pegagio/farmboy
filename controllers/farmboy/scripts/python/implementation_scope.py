"""Strict, standalone validation for requested Implement scope and history.

The functions in this module validate recorded evidence shapes and relationships.
They do not establish operator authority, native-agent identity, or actual effects;
the main controller must independently bind those facts before calling them.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import PurePosixPath
from typing import Any, Callable


SCHEMA_VERSION = "1.0"
MAX_CODER_SESSIONS = 5
SHA256 = re.compile(r"^[0-9a-f]{64}$")
TASK_ID = re.compile(r"^T[0-9]{3}$")
FINDING_ID = re.compile(r"^[A-Z][A-Z0-9-]{2,}$")
EXECUTION_KINDS = {"preparation", "first-source-execution", "corrective-source-execution"}
HISTORY_KINDS = {"coder-session-start", "source-attempt-start", "coder-session-outcome", "operator-input"}


class ImplementationScopeError(ValueError):
    """An unsafe, stale, incomplete, or internally inconsistent scope record."""


def _exact_fields(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ImplementationScopeError(f"{label}-schema-invalid")
    return value


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def _text_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256.fullmatch(value) is not None


def _relative_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ImplementationScopeError(f"{label}-path-invalid")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in value.split("/")):
        raise ImplementationScopeError(f"{label}-path-invalid")
    if value.startswith("~") or ":" in value.split("/", 1)[0]:
        raise ImplementationScopeError(f"{label}-path-invalid")
    return value


def _occurrence_time(value: Any, label: str) -> datetime:
    try:
        if not isinstance(value, str) or "T" not in value:
            raise ValueError
        observed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if observed.tzinfo is None or observed.utcoffset() is None:
            raise ValueError
        return observed
    except (TypeError, ValueError):
        raise ImplementationScopeError(f"{label}-time-invalid") from None


def _validate_outcome(assessment: dict[str, Any], declared_node_ids: set[str]) -> None:
    """Validate the standalone strict envelope before choosing a route."""
    state = assessment.get("state") if isinstance(assessment, dict) else None
    route_field = {"continue": "next_step_id", "blocked": "resume_action"}.get(state)
    fields = {"state", "reason_code", "evidence", "remaining_ids", "resolved_ids"}
    _exact_fields(assessment, fields | ({route_field} if route_field else set()), "scoped-assessment")
    if state not in {"complete", "continue", "blocked"}:
        raise ImplementationScopeError("scoped-assessment-state-invalid")
    reason_pattern = r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*"
    if not isinstance(assessment["reason_code"], str) or not re.fullmatch(reason_pattern, assessment["reason_code"]):
        raise ImplementationScopeError("scoped-assessment-reason-invalid")
    _evidence_list(assessment["evidence"], "scoped-assessment-evidence")
    for field in ("remaining_ids", "resolved_ids"):
        values = assessment[field]
        if (not isinstance(values, list) or any(not isinstance(item, str) or not item.strip() for item in values)
                or len(values) != len(set(values))):
            raise ImplementationScopeError("scoped-assessment-accounting-invalid")
    if set(assessment["remaining_ids"]) & set(assessment["resolved_ids"]):
        raise ImplementationScopeError("scoped-assessment-accounting-invalid")
    if state == "complete" and assessment["remaining_ids"]:
        raise ImplementationScopeError("scoped-assessment-incomplete")
    if state == "continue":
        if not assessment["remaining_ids"] or assessment["next_step_id"] not in declared_node_ids:
            raise ImplementationScopeError("scoped-route-node-undeclared")
    if state == "blocked":
        action = assessment["resume_action"]
        if not isinstance(action, str) or not re.fullmatch(reason_pattern, action):
            raise ImplementationScopeError("scoped-assessment-resumption-invalid")


def _evidence_list(value: Any, label: str, *, allow_empty: bool = False) -> list[dict[str, str]]:
    if not isinstance(value, list) or (not allow_empty and not value):
        raise ImplementationScopeError(f"{label}-missing")
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in value:
        _exact_fields(item, {"path", "sha256"}, label)
        path = _relative_path(item["path"], label)
        if path in seen or not _is_sha256(item["sha256"]):
            raise ImplementationScopeError(f"{label}-invalid")
        seen.add(path)
        result.append({"path": path, "sha256": item["sha256"]})
    return result


def validate_task_completion_classification(
    classification: dict[str, Any], *, task_id: str, task_description: str,
    required_requirement_ids: list[str], source_requirement_ids: list[str], scope_sha256: str,
) -> dict[str, Any]:
    """Bind the reviewed task's completion kind before its execution begins."""
    _exact_fields(classification, {"task_id", "task_description_sha256", "completion_kind", "requirement_ids",
                                   "source_requirement_ids", "scope_sha256", "classification_evidence"},
                  "task-completion-classification")
    if (classification["task_id"] != task_id or classification["scope_sha256"] != scope_sha256
            or classification["task_description_sha256"] != _text_digest(task_description)):
        raise ImplementationScopeError("task-completion-classification-stale")
    required = classification["requirement_ids"]
    source = classification["source_requirement_ids"]
    if (not isinstance(required, list) or len(required) != len(set(required)) or set(required) != set(required_requirement_ids)
            or not isinstance(source, list) or len(source) != len(set(source)) or not set(source).issubset(set(required))
            or set(source) != set(source_requirement_ids)):
        raise ImplementationScopeError("task-completion-classification-requirements-invalid")
    if classification["completion_kind"] not in {"administrative-prerequisite", "substantive-implementation"}:
        raise ImplementationScopeError("completion-kind-invalid")
    if source and classification["completion_kind"] != "substantive-implementation":
        raise ImplementationScopeError("source-requirement-cannot-be-administrative")
    if not source and classification["completion_kind"] != "administrative-prerequisite":
        raise ImplementationScopeError("administrative-task-classification-invalid")
    _evidence_list(classification["classification_evidence"], "task-classification-evidence")
    return classification


def validate_requested_scope(
    scope: dict[str, Any],
    current_tasks: dict[str, dict[str, Any]],
    *,
    trusted_request_reference: str,
    retained_scope_sha256: str,
    trusted_requested_task_ids: list[str] | None = None,
    tasker_tracked_task_ids: set[str] | None = None,
    tasker_revised_task_records: dict[str, tuple[str, str]] | None = None,
) -> dict[str, Any]:
    """Validate an immutable full-feature or exact-subset request snapshot."""
    fields = {"schema_version", "run_id", "feature_directory", "request_reference", "request_kind",
              "requested_task_ids", "task_records", "input_digests", "scope_sha256"}
    _exact_fields(scope, fields, "requested-scope")
    if scope["schema_version"] != SCHEMA_VERSION or not isinstance(scope["run_id"], str) or not scope["run_id"]:
        raise ImplementationScopeError("requested-scope-identity-invalid")
    feature = _relative_path(scope["feature_directory"], "feature")
    if not feature.startswith("specs/") or len(PurePosixPath(feature).parts) < 2:
        raise ImplementationScopeError("requested-scope-feature-invalid")
    if scope["request_reference"] != trusted_request_reference or not trusted_request_reference:
        raise ImplementationScopeError("trusted-request-binding-required")
    if scope["request_kind"] not in {"full-feature", "explicit-subset"}:
        raise ImplementationScopeError("request-kind-invalid")
    ids = scope["requested_task_ids"]
    if (not isinstance(ids, list) or not ids or any(not isinstance(item, str) or not TASK_ID.fullmatch(item) for item in ids)
            or len(ids) != len(set(ids))):
        raise ImplementationScopeError("requested-task-ids-invalid")
    if scope["request_kind"] == "explicit-subset":
        if (not isinstance(trusted_requested_task_ids, list) or len(trusted_requested_task_ids) != len(set(trusted_requested_task_ids))
                or ids != trusted_requested_task_ids):
            raise ImplementationScopeError("explicit-subset-request-mismatch")
    elif trusted_requested_task_ids is not None:
        raise ImplementationScopeError("full-feature-request-has-explicit-subset")
    if not isinstance(scope["task_records"], list) or len(scope["task_records"]) != len(ids):
        raise ImplementationScopeError("requested-task-records-incomplete")
    records: dict[str, dict[str, Any]] = {}
    for item in scope["task_records"]:
        _exact_fields(item, {"task_id", "marker", "description", "description_sha256"}, "requested-task-record")
        task_id = item["task_id"]
        if task_id in records or task_id not in ids or task_id not in current_tasks:
            raise ImplementationScopeError("requested-task-record-identity-invalid")
        marker = item["marker"]
        description = item["description"]
        if marker not in {"checked", "unchecked"} or not isinstance(description, str) or not description.strip():
            raise ImplementationScopeError("requested-task-record-invalid")
        if not _is_sha256(item["description_sha256"]) or item["description_sha256"] != _text_digest(description):
            raise ImplementationScopeError("requested-task-description-digest-invalid")
        current = current_tasks[task_id]
        revised = (tasker_revised_task_records or {}).get(task_id)
        if revised is None:
            expected_marker, expected_description = marker, description
            if marker == "unchecked" and tasker_tracked_task_ids is not None and task_id in tasker_tracked_task_ids:
                expected_marker = "checked"
        else:
            expected_marker, expected_description = revised
            if expected_marker == "unchecked" and task_id in (tasker_tracked_task_ids or set()):
                expected_marker = "checked"
        if current != {"marker": expected_marker, "description": expected_description}:
            raise ImplementationScopeError("requested-task-snapshot-stale")
        records[task_id] = item
    if set(records) != set(ids):
        raise ImplementationScopeError("requested-task-records-incomplete")
    originally_unfinished = {item["task_id"] for item in scope["task_records"] if item["marker"] == "unchecked"}
    if scope["request_kind"] == "full-feature" and set(ids) != originally_unfinished:
        raise ImplementationScopeError("full-feature-scope-dropped-unfinished-task")
    digests = scope["input_digests"]
    if not isinstance(digests, dict) or not digests or any(not _relative_path(path, "scope-input") or not _is_sha256(value) for path, value in digests.items()):
        raise ImplementationScopeError("requested-scope-input-digests-invalid")
    expected = _digest({key: value for key, value in scope.items() if key != "scope_sha256"})
    if not _is_sha256(scope["scope_sha256"]) or scope["scope_sha256"] != expected or retained_scope_sha256 != expected:
        raise ImplementationScopeError("requested-scope-digest-mismatch")
    return scope


def _validate_task_revision_successor(
    event: Any, *, predecessor: str, before_text_expected: str, scope_sha256: str,
    feature_directory: str, tasks_path: str,
    requested_task_ids: set[str], approved_specification_sha256: str,
) -> dict[str, tuple[str, str]]:
    """Validate a previously controller-approved in-scope Tasker revision."""
    fields = {"successor_kind", "predecessor_event_sha256", "scope_sha256", "tasker_assignment",
              "tasks_before_text", "tasks_after_text", "tasker_result", "frozen_scope",
              "semantic_review", "validation_result", "sha256"}
    _exact_fields(event, fields, "task-revision-successor")
    if (event["successor_kind"] != "task-plan-revision" or event["scope_sha256"] != scope_sha256
            or event["tasker_assignment"] != "FarmBoy Tasker"
            or not isinstance(event["tasks_before_text"], str) or not isinstance(event["tasks_after_text"], str)
            or event["tasks_before_text"] != before_text_expected
            or _text_digest(event["tasks_before_text"]) != predecessor):
        raise ImplementationScopeError("task-revision-successor-chain-invalid")
    before_text, after_text = event["tasks_before_text"], event["tasks_after_text"]
    before, after = _parse_tracking_task_text(before_text), _parse_tracking_task_text(after_text)
    before_ids, after_ids = list(before), list(after)
    if not set(before_ids).issubset(after_ids) or [item for item in after_ids if item in before] != before_ids:
        raise ImplementationScopeError("task-revision-successor-inventory-invalid")
    before_non_task = [line for line in before_text.splitlines() if re.fullmatch(r"- \[[ xX]\] T[0-9]{3} .+", line) is None]
    after_non_task = [line for line in after_text.splitlines() if re.fullmatch(r"- \[[ xX]\] T[0-9]{3} .+", line) is None]
    if before_non_task != after_non_task:
        raise ImplementationScopeError("task-revision-successor-document-changed")
    tasker = event["tasker_result"]
    _exact_fields(tasker, {"revision_state", "tasks_before_sha256", "tasks_after_sha256", "finding_ids",
                           "task_mappings", "reopened_task_ids", "added_task_ids",
                           "preserved_completed_task_ids"}, "task-revision-successor-tasker-result")
    frozen_scope = event["frozen_scope"]
    if isinstance(frozen_scope, dict):
        _exact_fields(frozen_scope, {"findings", "eligible_task_owners", "approved_specification_sha256",
                                     "permitted_added_task_owner", "tasker_owner"}, "task-revision-successor-scope")
    findings = frozen_scope.get("findings") if isinstance(frozen_scope, dict) else None
    owners = frozen_scope.get("eligible_task_owners") if isinstance(frozen_scope, dict) else None
    reviewer = event["semantic_review"]
    result = event["validation_result"]
    if not isinstance(findings, list) or not findings or not isinstance(owners, dict):
        raise ImplementationScopeError("task-revision-successor-scope-invalid")
    finding_ids = [item.get("id") for item in findings if isinstance(item, dict)]
    reopened = tasker["reopened_task_ids"]
    added = tasker["added_task_ids"]
    preserved = tasker["preserved_completed_task_ids"]
    if (tasker["revision_state"] != "updated" or not isinstance(tasker["finding_ids"], list)
            or set(tasker["finding_ids"]) != set(finding_ids) or len(finding_ids) != len(findings)
            or any(not isinstance(item, dict) or not isinstance(item.get("exact_correction"), str)
                   or not item["exact_correction"].strip() or not isinstance(item.get("id"), str)
                   or not FINDING_ID.fullmatch(item["id"]) for item in findings)
            or frozen_scope.get("tasker_owner") != "FarmBoy Tasker"
            or frozen_scope.get("permitted_added_task_owner") != "FarmBoy Tasker"
            or not _is_sha256(frozen_scope.get("approved_specification_sha256"))
            or frozen_scope.get("approved_specification_sha256") != approved_specification_sha256
            or not isinstance(reopened, list) or not isinstance(added, list) or not isinstance(preserved, list)
            or any(not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id) for task_id in reopened + added + preserved)
            or len(reopened + added) != len(set(reopened + added))
            or not isinstance(tasker["task_mappings"], list)
            or tasker["tasks_before_sha256"] != predecessor
            or tasker["tasks_after_sha256"] != _text_digest(after_text)):
        raise ImplementationScopeError("task-revision-successor-tasker-proof-invalid")
    expected_revision_scope = task_revision_scope_digest(feature_directory, tasks_path, frozen_scope)
    if (not isinstance(result, dict) or result.get("state") != "ready"
            or result.get("tasks_before_sha256") != predecessor
            or result.get("tasks_after_sha256") != _text_digest(after_text)
            or result.get("finding_ids") != tasker["finding_ids"]
            or result.get("eligible_task_ids") != sorted(reopened + added)
            or result.get("scope_sha256") != expected_revision_scope):
        raise ImplementationScopeError("task-revision-successor-validation-missing")
    if (not isinstance(reviewer, dict) or reviewer.get("reviewer") != "main-controller"
            or reviewer.get("state") != "approved" or reviewer.get("finding_ids") != sorted(finding_ids)
            or reviewer.get("task_ids") != sorted(reopened + added)
            or not isinstance(reviewer.get("rationale"), str) or not reviewer["rationale"].strip()
            or reviewer.get("scope_sha256") != expected_revision_scope):
        raise ImplementationScopeError("task-revision-successor-semantic-review-missing")
    mappings: dict[str, dict[str, Any]] = {}
    for mapping in tasker["task_mappings"]:
        if (not isinstance(mapping, dict) or set(mapping) != {"finding_id", "task_ids", "owner"}
                or mapping["finding_id"] in mappings or mapping["owner"] != "FarmBoy Tasker"
                or not isinstance(mapping["task_ids"], list)
                or any(not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id) for task_id in mapping["task_ids"])
                or len(mapping["task_ids"]) != len(set(mapping["task_ids"]))):
            raise ImplementationScopeError("task-revision-successor-mapping-invalid")
        mappings[mapping["finding_id"]] = mapping
    if set(mappings) != set(finding_ids) or any(not set(mapping["task_ids"]).issubset(set(reopened + added))
                                                  for mapping in mappings.values()):
        raise ImplementationScopeError("task-revision-successor-mapping-invalid")
    if any(task_id not in before or owners.get(task_id) != "FarmBoy Tasker" for task_id in reopened):
        raise ImplementationScopeError("task-revision-successor-owner-invalid")
    if not set(reopened).issubset(requested_task_ids):
        raise ImplementationScopeError("task-revision-successor-outside-requested-scope")
    if any(not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id) or owner != "FarmBoy Tasker"
           or task_id not in before for task_id, owner in owners.items()):
        raise ImplementationScopeError("task-revision-successor-owner-invalid")
    if any(task_id in before for task_id in added):
        raise ImplementationScopeError("task-revision-successor-added-id-invalid")
    changed: set[str] = set()
    for task_id, (before_marker, before_description) in before.items():
        after_marker, after_description = after[task_id]
        if (before_marker, before_description) == (after_marker, after_description):
            continue
        if (task_id not in reopened or before_marker not in {"x", "X"} or after_marker != " "
                or not after_description.startswith(before_description)
                or not any(finding in after_description for finding in finding_ids)):
            raise ImplementationScopeError("task-revision-successor-delta-invalid")
        changed.add(task_id)
    if changed != set(reopened):
        raise ImplementationScopeError("task-revision-successor-delta-invalid")
    if added:
        nums = [int(task_id[1:]) for task_id in before]
        if sorted(int(task_id[1:]) for task_id in added) != list(range(max(nums) + 1, max(nums) + len(added) + 1)):
            raise ImplementationScopeError("task-revision-successor-added-id-invalid")
        if after_ids[len(before_ids):] != added:
            raise ImplementationScopeError("task-revision-successor-added-id-invalid")
        for task_id in added:
            marker, description = after[task_id]
            if marker != " " or not any(finding in description for finding in finding_ids):
                raise ImplementationScopeError("task-revision-successor-added-task-invalid")
    expected_preserved = sorted(task_id for task_id, (marker, _) in before.items()
                                if marker in {"x", "X"} and task_id not in reopened)
    if preserved != expected_preserved:
        raise ImplementationScopeError("task-revision-successor-completed-history-invalid")
    mapped = {task for item in mappings.values() for task in item["task_ids"]}
    if mapped != set(reopened + added):
        raise ImplementationScopeError("task-revision-successor-mapping-invalid")
    expected_sha = _digest({key: value for key, value in event.items() if key != "sha256"})
    if event["sha256"] != expected_sha:
        raise ImplementationScopeError("task-revision-successor-digest-invalid")
    authorized_ids = requested_task_ids | set(added)
    return {task_id: ("checked" if marker in {"x", "X"} else "unchecked", description)
            for task_id, (marker, description) in after.items() if task_id in authorized_ids}


def task_revision_scope_digest(feature_directory: Any, tasks_path: Any, frozen_scope: Any) -> str:
    """Recompute the exact approved semantic scope for a Tasker revision."""
    if not isinstance(feature_directory, str) or not isinstance(tasks_path, str) or not isinstance(frozen_scope, dict):
        raise ImplementationScopeError("task-revision-successor-scope-invalid")
    findings = frozen_scope.get("findings")
    eligible_owners = frozen_scope.get("eligible_task_owners")
    approved_specification_sha256 = frozen_scope.get("approved_specification_sha256")
    if (not feature_directory.startswith("specs/") or "\\" in feature_directory
            or any(part in {"", ".", ".."} for part in feature_directory.split("/"))
            or tasks_path != f"{feature_directory}/tasks.md"
            or not isinstance(findings, list) or not findings
            or any(not isinstance(item, dict) or not isinstance(item.get("id"), str)
                   or not FINDING_ID.fullmatch(item["id"])
                   or not isinstance(item.get("exact_correction"), str) or not item["exact_correction"].strip()
                   for item in findings)
            or len({item["id"] for item in findings}) != len(findings)
            or not isinstance(eligible_owners, dict)
            or not _is_sha256(approved_specification_sha256)
            or any(not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id) or owner != "FarmBoy Tasker"
                   for task_id, owner in eligible_owners.items())
            or frozen_scope.get("permitted_added_task_owner") != "FarmBoy Tasker"
            or frozen_scope.get("tasker_owner") != "FarmBoy Tasker"):
        raise ImplementationScopeError("task-revision-successor-scope-invalid")
    return _digest({
        "feature_directory": feature_directory,
        "tasks_path": tasks_path,
        "findings": findings,
        "eligible_task_owners": eligible_owners,
        "approved_specification_sha256": approved_specification_sha256,
        "permitted_added_task_owner": frozen_scope["permitted_added_task_owner"],
        "tasker_owner": frozen_scope["tasker_owner"],
    })


def validate_task_tracking_successors(
    successors: Any,
    *,
    initial_tasks_sha256: str,
    current_tasks_text: str,
    scope_sha256: str,
    requested_task_ids: set[str],
    feature_directory: str = "",
    tasks_path: str = "",
    approved_specification_sha256: str | None = None,
    revision_records_out: dict[str, tuple[str, str]] | None = None,
    derived_task_records_out: dict[str, tuple[str, str]] | None = None,
) -> set[str]:
    """Validate append-only Tasker marker and reviewed task-revision successors."""
    if not isinstance(successors, list):
        raise ImplementationScopeError("task-tracking-successors-invalid")
    tracked: set[str] = set()
    revision_records: dict[str, tuple[str, str]] = {}
    predecessor = initial_tasks_sha256
    previous_event = "0" * 64
    previous_text: str | None = None
    for event in successors:
        if not isinstance(event, dict):
            raise ImplementationScopeError("task-tracking-successor-schema-invalid")
        if event.get("successor_kind") == "task-plan-revision":
            common_fields = {"successor_kind", "predecessor_event_sha256", "scope_sha256", "tasker_assignment",
                             "tasks_before_text", "tasks_after_text", "tasker_result", "frozen_scope",
                             "semantic_review", "validation_result", "sha256"}
            _exact_fields(event, common_fields, "task-revision-successor")
            if (event["scope_sha256"] != scope_sha256 or event["tasker_assignment"] != "FarmBoy Tasker"
                    or event["predecessor_event_sha256"] != previous_event
                    or not isinstance(event["tasks_before_text"], str)
                    or (previous_text is not None and event["tasks_before_text"] != previous_text)):
                raise ImplementationScopeError("task-revision-successor-chain-invalid")
            revised = _validate_task_revision_successor(event, predecessor=predecessor,
                before_text_expected=event["tasks_before_text"], scope_sha256=scope_sha256,
                feature_directory=feature_directory, tasks_path=tasks_path,
                requested_task_ids=requested_task_ids,
                approved_specification_sha256=approved_specification_sha256)
            reopened = set(event["tasker_result"]["reopened_task_ids"])
            tracked.difference_update(reopened)
            revision_records.update(revised)
            previous_event = event["sha256"]
            predecessor = _text_digest(event["tasks_after_text"])
            previous_text = event["tasks_after_text"]
            continue
        fields = {"predecessor_event_sha256", "scope_sha256", "tasker_assignment", "tasks_before_text",
                  "tasks_after_text", "tasker_result", "reviewer_result", "sha256"}
        _exact_fields(event, fields, "task-tracking-successor")
        if (event["scope_sha256"] != scope_sha256 or event["tasker_assignment"] != "FarmBoy Tasker"
                or event["predecessor_event_sha256"] != previous_event
                or (previous_text is not None and event["tasks_before_text"] != previous_text)):
            raise ImplementationScopeError("task-tracking-successor-chain-invalid")
        before_text, after_text = event["tasks_before_text"], event["tasks_after_text"]
        if not isinstance(before_text, str) or not isinstance(after_text, str):
            raise ImplementationScopeError("task-tracking-successor-text-invalid")
        before_sha, after_sha = _text_digest(before_text), _text_digest(after_text)
        if before_sha != predecessor or before_sha == after_sha:
            raise ImplementationScopeError("task-tracking-successor-preimage-invalid")
        before, after = _parse_tracking_task_text(before_text), _parse_tracking_task_text(after_text)
        if list(before) != list(after):
            raise ImplementationScopeError("task-tracking-task-inventory-changed")
        changed: set[str] = set()
        for task_id, (before_marker, before_description) in before.items():
            after_marker, after_description = after[task_id]
            if before_description != after_description:
                raise ImplementationScopeError("task-tracking-task-description-changed")
            if before_marker == after_marker:
                continue
            if before_marker != " " or after_marker not in {"x", "X"}:
                raise ImplementationScopeError("task-tracking-marker-transition-invalid")
            changed.add(task_id)
        # Marker tracking is the only permitted byte-level edit. Comparing the
        # entire documents after masking checkbox values also rejects changes
        # to headings, prose, task grouping, whitespace, and other plan state.
        if _mask_task_markers(before_text) != _mask_task_markers(after_text):
            raise ImplementationScopeError("task-tracking-non-marker-content-changed")
        tasker = event["tasker_result"]
        reviewer = event["reviewer_result"]
        _exact_fields(tasker, {"state", "tasks_before_sha256", "tasks_after_sha256", "completed_task_ids", "evidence"},
                      "task-tracking-tasker-result")
        _exact_fields(reviewer, {"reviewer", "completed_task_ids", "evidence"}, "task-tracking-reviewer-result")
        tasker_ids = tasker["completed_task_ids"]
        reviewer_ids = reviewer["completed_task_ids"]
        if (tasker["state"] != "ready" or tasker["tasks_before_sha256"] != before_sha
                or tasker["tasks_after_sha256"] != after_sha or reviewer["reviewer"] != "FarmBoy Code Reviewer"
                or not isinstance(tasker_ids, list)
                or any(not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id) for task_id in tasker_ids)
                or len(tasker_ids) != len(set(tasker_ids))
                or not isinstance(reviewer_ids, list)
                or any(not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id) for task_id in reviewer_ids)
                or len(reviewer_ids) != len(set(reviewer_ids))
                or set(tasker_ids) != changed or set(reviewer_ids) != changed or not changed
                or not changed.issubset(requested_task_ids | set(revision_records))):
            raise ImplementationScopeError("task-tracking-independent-proof-mismatch")
        _evidence_list(tasker["evidence"], "task-tracking-tasker-evidence")
        _evidence_list(reviewer["evidence"], "task-tracking-review-evidence")
        expected_event_sha = _digest({key: value for key, value in event.items() if key != "sha256"})
        if event["sha256"] != expected_event_sha:
            raise ImplementationScopeError("task-tracking-successor-digest-invalid")
        tracked.update(changed)
        previous_event = expected_event_sha
        predecessor = after_sha
        previous_text = after_text
    if successors and (successors[-1]["tasks_after_text"] != current_tasks_text):
        raise ImplementationScopeError("task-tracking-current-preimage-mismatch")
    if not successors and _text_digest(current_tasks_text) != initial_tasks_sha256:
        raise ImplementationScopeError("task-tracking-proof-required")
    if revision_records_out is not None:
        revision_records_out.update({task_id: record for task_id, record in revision_records.items()
                                     if task_id in requested_task_ids})
    if derived_task_records_out is not None:
        derived_task_records_out.update({task_id: record for task_id, record in revision_records.items()
                                         if task_id not in requested_task_ids})
    return tracked


def _parse_tracking_task_text(contents: str) -> dict[str, tuple[str, str]]:
    """Parse marker-only task successors with the task grammar used by the controller."""
    records: dict[str, tuple[str, str]] = {}
    for line in contents.splitlines():
        match = re.fullmatch(r"- \[([ xX])\] (T[0-9]{3}) (.+)", line)
        if match is None:
            continue
        marker, task_id, description = match.groups()
        if task_id in records:
            raise ImplementationScopeError("task-tracking-duplicate-task-id")
        records[task_id] = (marker, description)
    if not records:
        raise ImplementationScopeError("task-tracking-task-inventory-invalid")
    return records


def _mask_task_markers(contents: str) -> str:
    """Replace only task checkbox values, preserving every other source byte."""
    return re.sub(r"(?m)^(- \[)[ xX](\] T[0-9]{3} .+)$", r"\1_\2", contents)


def validate_task_fulfillment_proof(
    proof: dict[str, Any],
    *,
    task_id: str,
    task_description: str,
    required_requirement_ids: list[str],
    scope_sha256: str,
    expected_completion_kind: str,
) -> dict[str, Any]:
    """Validate requirement-complete administrative or substantive proof."""
    base = {"task_id", "task_description_sha256", "completion_kind", "requirements", "proof_evidence",
            "review_evidence", "scope_sha256"}
    kind = proof.get("completion_kind") if isinstance(proof, dict) else None
    kind_fields = {
        "administrative-prerequisite": {"trusted_decision_references", "permitted_effect_route",
                                        "administrative_state_before", "administrative_state_after",
                                        "no_source_effect_evidence"},
        "substantive-implementation": {"activation_sha256", "source_delta_evidence", "validation_evidence"},
    }
    if kind not in kind_fields:
        raise ImplementationScopeError("completion-kind-invalid")
    if kind != expected_completion_kind:
        raise ImplementationScopeError("fulfillment-kind-does-not-match-classification")
    _exact_fields(proof, base | kind_fields[kind], "task-fulfillment-proof")
    if proof["task_id"] != task_id or proof["scope_sha256"] != scope_sha256:
        raise ImplementationScopeError("fulfillment-proof-scope-mismatch")
    if proof["task_description_sha256"] != _text_digest(task_description):
        raise ImplementationScopeError("fulfillment-proof-task-stale")
    requirements = proof["requirements"]
    if not isinstance(requirements, list):
        raise ImplementationScopeError("fulfillment-requirements-invalid")
    observed: set[str] = set()
    for requirement in requirements:
        _exact_fields(requirement, {"requirement_id", "satisfied", "evidence"}, "fulfillment-requirement")
        identifier = requirement["requirement_id"]
        if identifier in observed or identifier not in required_requirement_ids or requirement["satisfied"] is not True:
            raise ImplementationScopeError("fulfillment-requirement-incomplete")
        _evidence_list(requirement["evidence"], "requirement-evidence")
        observed.add(identifier)
    if observed != set(required_requirement_ids):
        raise ImplementationScopeError("fulfillment-requirement-incomplete")
    _evidence_list(proof["proof_evidence"], "fulfillment-proof-evidence")
    review = proof["review_evidence"]
    _exact_fields(review, {"reviewer", "verdict", "reference", "sha256"}, "fulfillment-review")
    if (review["reviewer"] != "FarmBoy Code Reviewer" or review["verdict"] != "complete"
            or not isinstance(review["reference"], str) or not review["reference"] or not _is_sha256(review["sha256"])):
        raise ImplementationScopeError("independent-fulfillment-review-required")
    if kind == "administrative-prerequisite":
        refs = proof["trusted_decision_references"]
        if (not isinstance(refs, list) or any(not isinstance(value, str) or not value for value in refs)
                or not isinstance(proof["permitted_effect_route"], str) or not proof["permitted_effect_route"]):
            raise ImplementationScopeError("administrative-proof-incomplete")
        before = proof["administrative_state_before"]
        after = proof["administrative_state_after"]
        for snapshot in (before, after):
            _exact_fields(snapshot, {"state", "sha256", "evidence"}, "administrative-state-snapshot")
            if not isinstance(snapshot["state"], dict) or not snapshot["state"] or not _is_sha256(snapshot["sha256"]):
                raise ImplementationScopeError("administrative-state-evidence-required")
            _evidence_list(snapshot["evidence"], "administrative-state-evidence")
        if proof["no_source_effect_evidence"] is not True:
            raise ImplementationScopeError("administrative-source-effect-present")
    else:
        if not _is_sha256(proof["activation_sha256"]):
            raise ImplementationScopeError("task-activation-evidence-required")
        _evidence_list(proof["source_delta_evidence"], "source-delta-evidence")
        _evidence_list(proof["validation_evidence"], "validation-evidence")
    return proof


def validate_task_eligibility(
    scope: dict[str, Any], assessment: dict[str, Any], proofs: dict[str, dict[str, Any]],
    *, proof_requirements: dict[str, list[str]] | None = None,
    completion_classifications: dict[str, dict[str, Any]] | None = None,
    source_requirement_ids: dict[str, list[str]] | None = None,
    completed_prerequisites: dict[str, dict[str, Any]] | None = None,
    retained_prerequisite_sha256: dict[str, str] | None = None,
    tasker_tracked_task_ids: set[str] | None = None,
    tasker_derived_task_records: dict[str, tuple[str, str]] | None = None,
    retained_predecessor_sha256: str,
) -> dict[str, Any]:
    """Require complete, nonoverlapping accounting for every requested task."""
    fields = {"assessment_id", "scope_sha256", "predecessor_sha256", "input_digests", "task_states",
              "eligible_task_ids", "pending_task_ids", "global_blockers", "iteration", "evidence"}
    _exact_fields(assessment, fields, "task-eligibility")
    requested = scope["requested_task_ids"]
    derived_records = tasker_derived_task_records or {}
    if not isinstance(derived_records, dict) or set(derived_records) & set(requested):
        raise ImplementationScopeError("tasker-derived-task-records-invalid")
    execution_ids = [*requested, *sorted(derived_records)]
    if (assessment["scope_sha256"] != scope["scope_sha256"] or not _is_sha256(assessment["predecessor_sha256"])
            or not _is_sha256(retained_predecessor_sha256)
            or assessment["predecessor_sha256"] != retained_predecessor_sha256):
        raise ImplementationScopeError("eligibility-scope-mismatch")
    if not isinstance(assessment["assessment_id"], str) or not assessment["assessment_id"]:
        raise ImplementationScopeError("eligibility-identity-invalid")
    if isinstance(assessment["iteration"], bool) or not isinstance(assessment["iteration"], int) or assessment["iteration"] < 0:
        raise ImplementationScopeError("eligibility-iteration-invalid")
    if not isinstance(assessment["input_digests"], dict) or not assessment["input_digests"]:
        raise ImplementationScopeError("eligibility-inputs-missing")
    for path, digest in assessment["input_digests"].items():
        _relative_path(path, "eligibility-input")
        if not _is_sha256(digest):
            raise ImplementationScopeError("eligibility-input-digest-invalid")
    _evidence_list(assessment["evidence"], "eligibility-evidence")
    prerequisites = completed_prerequisites or {}
    retained = retained_prerequisite_sha256 or {}
    if not isinstance(prerequisites, dict) or not isinstance(retained, dict) or set(prerequisites) != set(retained):
        raise ImplementationScopeError("prerequisite-proof-binding-invalid")
    for dependency, prerequisite in prerequisites.items():
        if not isinstance(dependency, str) or not TASK_ID.fullmatch(dependency) or dependency in requested:
            raise ImplementationScopeError("prerequisite-outside-scope-required")
        _exact_fields(prerequisite, {"task_id", "description", "requirement_ids", "source_requirement_ids",
                                     "classification", "proof"}, "completed-prerequisite")
        if (prerequisite["task_id"] != dependency or not isinstance(prerequisite["description"], str)
                or not prerequisite["description"] or not _is_sha256(retained[dependency])
                or retained[dependency] != _digest(prerequisite)):
            raise ImplementationScopeError("prerequisite-proof-binding-invalid")
        validate_task_completion_classification(prerequisite["classification"], task_id=dependency,
            task_description=prerequisite["description"], required_requirement_ids=prerequisite["requirement_ids"],
            source_requirement_ids=prerequisite["source_requirement_ids"], scope_sha256=scope["scope_sha256"])
        validate_task_fulfillment_proof(prerequisite["proof"], task_id=dependency,
            task_description=prerequisite["description"], required_requirement_ids=prerequisite["requirement_ids"],
            scope_sha256=scope["scope_sha256"],
            expected_completion_kind=prerequisite["classification"]["completion_kind"])
    states: dict[str, dict[str, Any]] = {}
    for item in assessment["task_states"] if isinstance(assessment["task_states"], list) else []:
        _exact_fields(item, {"task_id", "state", "dependency_ids", "evidence", "blocker", "resume_action", "proof_sha256"}, "task-state")
        task_id = item["task_id"]
        if task_id in states or task_id not in execution_ids or item["state"] not in {"eligible", "pending", "blocked", "completed-with-proof"}:
            raise ImplementationScopeError("task-state-invalid")
        dependencies = item["dependency_ids"]
        if (not isinstance(dependencies, list) or len(dependencies) != len(set(dependencies))
                or any(not isinstance(dep, str) or not TASK_ID.fullmatch(dep) for dep in dependencies)):
            raise ImplementationScopeError("task-state-dependencies-invalid")
        _evidence_list(item["evidence"], "task-state-evidence")
        if item["state"] in {"blocked", "pending"}:
            if not isinstance(item["blocker"], str) or not item["blocker"] or not isinstance(item["resume_action"], str) or not item["resume_action"]:
                raise ImplementationScopeError("task-state-resumption-missing")
        elif item["blocker"] is not None or item["resume_action"] is not None:
            raise ImplementationScopeError("task-state-unexpected-blocker")
        if item["state"] == "completed-with-proof":
            if (task_id not in proofs or not _is_sha256(item["proof_sha256"])
                    or proof_requirements is None or task_id not in proof_requirements
                    or completion_classifications is None or task_id not in completion_classifications
                    or source_requirement_ids is None or task_id not in source_requirement_ids):
                raise ImplementationScopeError("completed-task-proof-missing")
            record = next((record for record in scope["task_records"] if record["task_id"] == task_id), None)
            description = record["description"] if record else derived_records[task_id][1]
            validate_task_completion_classification(completion_classifications[task_id], task_id=task_id,
                task_description=description, required_requirement_ids=proof_requirements[task_id],
                source_requirement_ids=source_requirement_ids[task_id], scope_sha256=scope["scope_sha256"])
            validate_task_fulfillment_proof(proofs[task_id], task_id=task_id,
                task_description=description, required_requirement_ids=proof_requirements[task_id],
                scope_sha256=scope["scope_sha256"],
                expected_completion_kind=(completion_classifications or {}).get(task_id, {}).get("completion_kind"))
            if item["proof_sha256"] != _digest(proofs[task_id]):
                raise ImplementationScopeError("completed-task-proof-digest-mismatch")
        elif item["proof_sha256"] is not None:
            raise ImplementationScopeError("task-state-unexpected-proof")
        states[task_id] = item
    if set(states) != set(execution_ids):
        raise ImplementationScopeError("task-state-coverage-incomplete")
    tracked = tasker_tracked_task_ids or set()
    if (not isinstance(tracked, set) or not tracked.issubset(set(execution_ids))
            or any(states[task_id]["state"] != "completed-with-proof" for task_id in tracked)):
        raise ImplementationScopeError("task-tracking-completion-proof-required")
    for task_id, item in states.items():
        if item["state"] == "eligible":
            if (completion_classifications is None or task_id not in completion_classifications
                    or proof_requirements is None or task_id not in proof_requirements
                    or source_requirement_ids is None or task_id not in source_requirement_ids):
                raise ImplementationScopeError("task-completion-classification-missing")
            record = next((record for record in scope["task_records"] if record["task_id"] == task_id), None)
            description = record["description"] if record else derived_records[task_id][1]
            validate_task_completion_classification(completion_classifications[task_id], task_id=task_id,
                task_description=description, required_requirement_ids=proof_requirements[task_id],
                source_requirement_ids=source_requirement_ids[task_id], scope_sha256=scope["scope_sha256"])
        if item["state"] == "eligible":
            if any(dependency not in prerequisites and (dependency not in states or states[dependency]["state"] != "completed-with-proof")
                   for dependency in item["dependency_ids"]):
                raise ImplementationScopeError("task-eligible-dependency-incomplete")
    eligible = assessment["eligible_task_ids"]
    pending = assessment["pending_task_ids"]
    if (not isinstance(eligible, list) or not isinstance(pending, list) or len(eligible) != len(set(eligible))
            or len(pending) != len(set(pending))):
        raise ImplementationScopeError("eligibility-partition-invalid")
    expected_eligible = {key for key, value in states.items() if value["state"] == "eligible"}
    expected_pending = set(states) - expected_eligible - {key for key, value in states.items() if value["state"] == "completed-with-proof"}
    if set(eligible) != expected_eligible or set(pending) != expected_pending or set(eligible) & set(pending):
        raise ImplementationScopeError("eligibility-partition-invalid")
    if not isinstance(assessment["global_blockers"], list):
        raise ImplementationScopeError("global-blockers-invalid")
    for blocker in assessment["global_blockers"]:
        _exact_fields(blocker, {"reason_code", "resume_action", "evidence"}, "global-blocker")
        if not isinstance(blocker["reason_code"], str) or not blocker["reason_code"] or not isinstance(blocker["resume_action"], str) or not blocker["resume_action"]:
            raise ImplementationScopeError("global-blocker-invalid")
        _evidence_list(blocker["evidence"], "global-blocker-evidence")
    if assessment["global_blockers"] and eligible:
        raise ImplementationScopeError("global-blocker-cannot-have-eligible-tasks")
    return assessment


def validate_task_activation(
    activation: dict[str, Any], *, scope_sha256: str, eligibility_sha256: str,
    predecessor_baseline_sha256: str, task_id: str, required_paths: set[str],
) -> dict[str, Any]:
    """Validate fresh task-specific source preimages before a task's first effect."""
    fields = {"activation_id", "task_id", "scope_sha256", "eligibility_sha256", "predecessor_baseline_sha256",
              "occurred_at", "requirements", "source_preimages", "route_evidence", "readiness_evidence", "iteration"}
    _exact_fields(activation, fields, "task-activation")
    for field, retained in (("scope_sha256", scope_sha256), ("eligibility_sha256", eligibility_sha256),
                            ("predecessor_baseline_sha256", predecessor_baseline_sha256)):
        if not _is_sha256(activation[field]) or not _is_sha256(retained):
            raise ImplementationScopeError("task-activation-digest-invalid")
    if (activation["task_id"] != task_id or activation["scope_sha256"] != scope_sha256
            or activation["eligibility_sha256"] != eligibility_sha256
            or activation["predecessor_baseline_sha256"] != predecessor_baseline_sha256):
        raise ImplementationScopeError("task-activation-stale")
    if not isinstance(activation["activation_id"], str) or not activation["activation_id"]:
        raise ImplementationScopeError("task-activation-identity-invalid")
    _occurrence_time(activation["occurred_at"], "task-activation")
    if isinstance(activation["iteration"], bool) or not isinstance(activation["iteration"], int) or activation["iteration"] < 1:
        raise ImplementationScopeError("task-activation-iteration-invalid")
    requirements = activation["requirements"]
    if not isinstance(requirements, list) or not requirements or any(not isinstance(item, str) or not item for item in requirements):
        raise ImplementationScopeError("task-activation-requirements-missing")
    preimages = activation["source_preimages"]
    if not isinstance(preimages, list):
        raise ImplementationScopeError("task-activation-preimages-invalid")
    found: set[str] = set()
    for item in preimages:
        if not isinstance(item, dict) or item.get("state") not in {"present", "absent"}:
            raise ImplementationScopeError("task-activation-preimage-invalid")
        expected_fields = {"path", "state", "sha256"} if item["state"] == "present" else {"path", "state"}
        _exact_fields(item, expected_fields, "task-activation-preimage")
        path = _relative_path(item["path"], "activation-source")
        if path in found or (item["state"] == "present" and not _is_sha256(item["sha256"])):
            raise ImplementationScopeError("task-activation-preimage-invalid")
        found.add(path)
    if found != required_paths:
        raise ImplementationScopeError("task-activation-source-coverage-incomplete")
    _evidence_list(activation["route_evidence"], "activation-route-evidence")
    _evidence_list(activation["readiness_evidence"], "activation-readiness-evidence")
    return activation


def validate_owner_source_assessment(assessment: dict[str, Any]) -> dict[str, Any]:
    """Validate observed owner-source facts without confusing them with runtime delivery."""
    fields = {"task_id", "component_id", "source_identity", "source_coordinates", "access_state",
              "guidance_evidence", "source_route", "authority_evidence", "state", "reason_code", "resume_action"}
    state = assessment.get("state") if isinstance(assessment, dict) else None
    required = fields if state == "blocked" else fields - {"reason_code", "resume_action"}
    _exact_fields(assessment, required, "owner-source-assessment")
    if not TASK_ID.fullmatch(assessment["task_id"] if isinstance(assessment["task_id"], str) else ""):
        raise ImplementationScopeError("owner-source-task-invalid")
    for name in ("component_id", "source_identity"):
        if not isinstance(assessment[name], str) or not assessment[name]:
            raise ImplementationScopeError("owner-source-identity-missing")
    coordinates = assessment["source_coordinates"]
    _exact_fields(coordinates, {"repository", "revision", "dirty_state", "relative_paths"}, "owner-source-coordinates")
    if (not isinstance(coordinates["repository"], str) or not coordinates["repository"]
            or coordinates["repository"].startswith("/") or "Users/" in coordinates["repository"]
            or not isinstance(coordinates["revision"], str) or not coordinates["revision"]
            or coordinates["dirty_state"] not in {"clean", "dirty", "unknown"}
            or not isinstance(coordinates["relative_paths"], list)):
        raise ImplementationScopeError("owner-source-coordinates-invalid")
    for path in coordinates["relative_paths"]:
        _relative_path(path, "owner-source")
    if assessment["access_state"] not in {"read-write", "read-only", "denied", "unknown"}:
        raise ImplementationScopeError("owner-source-access-invalid")
    _evidence_list(assessment["guidance_evidence"], "owner-guidance-evidence")
    _evidence_list(assessment["authority_evidence"], "owner-authority-evidence")
    route = assessment["source_route"]
    _exact_fields(route, {"state", "description", "evidence"}, "owner-source-route")
    if route["state"] not in {"permitted", "missing", "conflicted", "unknown"} or not isinstance(route["description"], str) or not route["description"]:
        raise ImplementationScopeError("owner-source-route-invalid")
    _evidence_list(route["evidence"], "owner-route-evidence")
    if assessment["state"] == "ready":
        if (assessment["access_state"] != "read-write" or route["state"] != "permitted"
                or coordinates["dirty_state"] == "unknown"):
            raise ImplementationScopeError("owner-source-readiness-unsubstantiated")
    elif assessment["state"] == "blocked":
        if not isinstance(assessment["reason_code"], str) or not assessment["reason_code"] or not isinstance(assessment["resume_action"], str) or not assessment["resume_action"]:
            raise ImplementationScopeError("owner-source-resumption-missing")
    else:
        raise ImplementationScopeError("owner-source-state-invalid")
    return assessment


def validate_execution_history(history: dict[str, Any], *, scope_sha256: str, retained_history_sha256: str,
                               max_coder_sessions: int = MAX_CODER_SESSIONS) -> dict[str, Any]:
    """Validate append-only pre-dispatch session/attempt history and global cap."""
    if type(max_coder_sessions) is not int or max_coder_sessions < MAX_CODER_SESSIONS:
        raise ImplementationScopeError("execution-budget-invalid")
    _exact_fields(history, {"schema_version", "scope_sha256", "events", "coder_sessions_started", "source_attempts_started", "sha256"}, "execution-history")
    if (not _is_sha256(scope_sha256) or not _is_sha256(retained_history_sha256)
            or history["schema_version"] != SCHEMA_VERSION or history["scope_sha256"] != scope_sha256):
        raise ImplementationScopeError("execution-history-scope-mismatch")
    for counter in ("coder_sessions_started", "source_attempts_started"):
        if type(history[counter]) is not int or history[counter] < 0:
            raise ImplementationScopeError("execution-history-counter-invalid")
    events = history["events"]
    if not isinstance(events, list):
        raise ImplementationScopeError("execution-history-events-invalid")
    previous = "0" * 64
    sessions = 0
    attempts = 0
    active_session: tuple[str, str] | None = None
    attempt_started = False
    seen: set[str] = set()
    session_ids: set[str] = set()
    for event in events:
        base = {"event_id", "predecessor_sha256", "scope_sha256", "event_kind", "declared_node_id",
                "occurred_at", "evidence", "sha256"}
        kind = event.get("event_kind") if isinstance(event, dict) else None
        extras = {
            "coder-session-start": {"coder_session_id", "coder_sessions_started", "source_attempts_started", "execution_kind"},
            "source-attempt-start": {"coder_session_id", "coder_sessions_started", "source_attempts_started", "execution_kind"},
            "coder-session-outcome": {"coder_session_id", "coder_sessions_started", "source_attempts_started", "outcome"},
            "operator-input": {"coder_session_id", "coder_sessions_started", "source_attempts_started", "same_child_resume"},
        }
        if kind not in HISTORY_KINDS:
            raise ImplementationScopeError("execution-history-event-kind-invalid")
        _exact_fields(event, base | extras[kind], "execution-history-event")
        for counter in ("coder_sessions_started", "source_attempts_started"):
            if type(event[counter]) is not int or event[counter] < 0:
                raise ImplementationScopeError("execution-history-counter-invalid")
        if (not isinstance(event["event_id"], str) or not event["event_id"] or event["event_id"] in seen
                or event["scope_sha256"] != scope_sha256 or event["predecessor_sha256"] != previous
                or not isinstance(event["declared_node_id"], str) or not event["declared_node_id"]):
            raise ImplementationScopeError("execution-history-chain-invalid")
        _occurrence_time(event["occurred_at"], "execution-history")
        _evidence_list(event["evidence"], "execution-history-evidence")
        event_hash = _digest({key: value for key, value in event.items() if key != "sha256"})
        if event["sha256"] != event_hash:
            raise ImplementationScopeError("execution-history-event-digest-invalid")
        seen.add(event["event_id"])
        session_id = event["coder_session_id"]
        if not isinstance(session_id, str) or not session_id:
            raise ImplementationScopeError("execution-history-session-invalid")
        if kind == "coder-session-start":
            if (active_session is not None or event["execution_kind"] not in EXECUTION_KINDS
                    or session_id in session_ids):
                raise ImplementationScopeError("execution-history-session-order-invalid")
            if event["execution_kind"] == "preparation" and attempts > 0:
                raise ImplementationScopeError("execution-history-preparation-after-source-attempt")
            if event["execution_kind"] == "preparation" and event["declared_node_id"] != "prepare-scoped-prerequisites":
                raise ImplementationScopeError("execution-history-node-mismatch")
            if event["execution_kind"] != "preparation" and event["declared_node_id"] != "implement-tasks":
                raise ImplementationScopeError("execution-history-node-mismatch")
            if event["execution_kind"] == "first-source-execution" and attempts != 0:
                raise ImplementationScopeError("execution-history-first-source-repeated")
            if event["execution_kind"] == "corrective-source-execution" and attempts == 0:
                raise ImplementationScopeError("execution-history-corrective-source-before-first")
            sessions += 1
            if sessions > max_coder_sessions or event["coder_sessions_started"] != sessions or event["source_attempts_started"] != attempts:
                raise ImplementationScopeError("execution-history-counter-invalid")
            active_session = (session_id, event["execution_kind"])
            attempt_started = False
            session_ids.add(session_id)
        elif kind == "source-attempt-start":
            if active_session != (session_id, event["execution_kind"]) or event["execution_kind"] not in {"first-source-execution", "corrective-source-execution"}:
                raise ImplementationScopeError("execution-history-attempt-order-invalid")
            if attempt_started or event["declared_node_id"] != "implement-tasks":
                raise ImplementationScopeError("execution-history-attempt-order-invalid")
            attempt_started = True
            attempts += 1
            if event["execution_kind"] == "first-source-execution" and attempts != 1:
                raise ImplementationScopeError("execution-history-first-source-repeated")
            if event["execution_kind"] == "corrective-source-execution" and attempts < 2:
                raise ImplementationScopeError("execution-history-corrective-source-before-first")
            if event["coder_sessions_started"] != sessions or event["source_attempts_started"] != attempts:
                raise ImplementationScopeError("execution-history-counter-invalid")
        else:
            if active_session is None or active_session[0] != session_id:
                raise ImplementationScopeError("execution-history-session-order-invalid")
            expected_node = "prepare-scoped-prerequisites" if active_session[1] == "preparation" else "implement-tasks"
            if event["declared_node_id"] != expected_node:
                raise ImplementationScopeError("execution-history-node-mismatch")
            if active_session[1] != "preparation" and not attempt_started:
                raise ImplementationScopeError("execution-history-source-attempt-missing")
            if event["coder_sessions_started"] != sessions or event["source_attempts_started"] != attempts:
                raise ImplementationScopeError("execution-history-counter-invalid")
            if kind == "operator-input" and event["same_child_resume"] is not True:
                raise ImplementationScopeError("execution-history-input-resume-invalid")
            if kind == "coder-session-outcome":
                if event["outcome"] not in {"completed", "failed-dispatch", "question-stopped"}:
                    raise ImplementationScopeError("execution-history-outcome-invalid")
                if event["outcome"] != "question-stopped":
                    active_session = None
        previous = event_hash
    if history["coder_sessions_started"] != sessions or history["source_attempts_started"] != attempts:
        raise ImplementationScopeError("execution-history-counter-invalid")
    expected = _digest({key: value for key, value in history.items() if key != "sha256"})
    if history["sha256"] != expected or retained_history_sha256 != expected:
        raise ImplementationScopeError("execution-history-digest-mismatch")
    return history


def append_execution_event(history: dict[str, Any], event: dict[str, Any], *, scope_sha256: str,
                           retained_history_sha256: str, max_coder_sessions: int = MAX_CODER_SESSIONS) -> dict[str, Any]:
    """Return a validated history successor; callers persist it before dispatch."""
    validate_execution_history(history, scope_sha256=scope_sha256, retained_history_sha256=retained_history_sha256,
                               max_coder_sessions=max_coder_sessions)
    previous = history["events"][-1]["sha256"] if history["events"] else "0" * 64
    if event.get("predecessor_sha256") != previous:
        raise ImplementationScopeError("execution-history-predecessor-mismatch")
    successor = {key: value for key, value in history.items() if key != "sha256"}
    successor["events"] = [*history["events"], event]
    successor["coder_sessions_started"] = event.get("coder_sessions_started", history["coder_sessions_started"])
    successor["source_attempts_started"] = event.get("source_attempts_started", history["source_attempts_started"])
    successor["sha256"] = _digest(successor)
    validate_execution_history(successor, scope_sha256=scope_sha256, retained_history_sha256=successor["sha256"],
                               max_coder_sessions=max_coder_sessions)
    return successor


def route_scoped_implementation_assessment(
    *, history: dict[str, Any], assessment: dict[str, Any], eligible_task_ids: list[str],
    declared_node_ids: set[str], previous_assessment: dict[str, Any] | None = None,
    generic_route: Callable[..., dict[str, Any]] | None = None, retained_history_sha256: str,
    eligibility: dict[str, Any] | None = None, eligibility_sha256: str | None = None,
    max_coder_sessions: int = MAX_CODER_SESSIONS,
) -> dict[str, Any]:
    """Route before first source attempt, then require the unchanged generic guard."""
    validate_execution_history(history, scope_sha256=history.get("scope_sha256"),
                               retained_history_sha256=retained_history_sha256, max_coder_sessions=max_coder_sessions)
    _validate_outcome(assessment, declared_node_ids)
    active = False
    for event in history["events"]:
        if event["event_kind"] == "coder-session-start":
            active = True
        elif event["event_kind"] == "coder-session-outcome" and event["outcome"] != "question-stopped":
            active = False
    if active:
        raise ImplementationScopeError("execution-history-session-unclosed")
    if (not isinstance(eligible_task_ids, list)
            or any(not isinstance(task, str) or not TASK_ID.fullmatch(task) for task in eligible_task_ids)
            or len(eligible_task_ids) != len(set(eligible_task_ids))):
        raise ImplementationScopeError("scoped-eligible-ids-invalid")
    if any("task:" + task not in assessment["remaining_ids"] for task in eligible_task_ids):
        raise ImplementationScopeError("scoped-assessment-accounting-invalid")
    if assessment["state"] == "complete" and eligible_task_ids:
        raise ImplementationScopeError("scoped-assessment-accounting-invalid")
    if assessment["state"] == "complete":
        if (not isinstance(eligibility, dict) or not _is_sha256(eligibility_sha256)
                or eligibility_sha256 != _digest(eligibility)
                or eligibility.get("scope_sha256") != history.get("scope_sha256")
                or eligibility.get("eligible_task_ids") != []
                or eligibility.get("pending_task_ids") != []
                or not isinstance(eligibility.get("task_states"), list)
                or not eligibility["task_states"]
                or any(not isinstance(item, dict) or item.get("state") != "completed-with-proof"
                       for item in eligibility["task_states"])):
            raise ImplementationScopeError("scoped-completion-proof-required")
    attempts = history.get("source_attempts_started")
    sessions = history.get("coder_sessions_started")
    if (isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 0
            or isinstance(sessions, bool) or not isinstance(sessions, int) or sessions < 0 or sessions > max_coder_sessions):
        raise ImplementationScopeError("execution-history-counter-invalid")
    if attempts == 0:
        if assessment["state"] == "blocked":
            return {"action": "blocked", "resume_action": assessment["resume_action"]}
        if assessment["state"] == "complete":
            return {"action": "complete"}
        node = assessment.get("next_step_id")
        if node not in declared_node_ids or node not in {"prepare-scoped-prerequisites", "implement-tasks"}:
            raise ImplementationScopeError("scoped-route-node-undeclared")
        if not eligible_task_ids:
            if (node != "prepare-scoped-prerequisites" or assessment.get("reason_code") != "operator-decision-required"
                    or not any(item.startswith("task:") for item in assessment["remaining_ids"])):
                return {"action": "blocked", "blocker": "scoped-work-pending"}
        if sessions >= max_coder_sessions:
            return {"action": "blocked", "blocker": "loop-cap-exhausted"}
        return {"action": "continue", "next_step_id": node}
    if generic_route is None or not callable(generic_route):
        raise ImplementationScopeError("generic-post-source-predicate-required")
    if previous_assessment is None:
        raise ImplementationScopeError("generic-post-source-predecessor-required")
    generic_result = generic_route(
        assessment,
        iteration=attempts,
        max_iterations=max_coder_sessions,
        loop_body_step_ids=declared_node_ids,
        previous_assessment=previous_assessment,
    )
    if generic_result.get("action") == "continue":
        if sessions >= max_coder_sessions:
            return {"action": "blocked", "blocker": "loop-cap-exhausted"}
        if not eligible_task_ids:
            return {
                "action": "blocked",
                "blocker": "scoped-work-pending",
                "reason_code": assessment["reason_code"],
            }
        if generic_result.get("next_step_id") != "implement-tasks":
            raise ImplementationScopeError("scoped-post-source-route-invalid")
    return generic_result

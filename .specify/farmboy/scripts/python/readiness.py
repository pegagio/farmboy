#!/usr/bin/env python3
"""Build a deterministic, read-only FarmBoy preparation-readiness report."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any


CHECKBOX = re.compile(r"^\s*- \[([ xX])\](?:\s+(.*?))?\s*$")
CORE_MARKER = re.compile(r"- \[[ xX]\]")
TASK_ID = re.compile(r"^T[0-9]{3}\s+")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_CATEGORIES = {
    "preparation-quality", "preparation-review", "implementation-evidence",
    "human-acceptance", "unresolved",
}


class ReadinessError(ValueError):
    """A malformed or unsafe readiness input that must block assessment."""


def _safe_file(root: Path, relative: str, *, required: bool = True) -> tuple[Path, bytes] | None:
    """Read one repository-relative regular file after rejecting symlink aliases."""
    path = PurePosixPath(relative)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ReadinessError("readiness-path-out-of-scope")
    candidate = root
    for part in path.parts:
        candidate = candidate / part
        try:
            details = candidate.lstat()
        except FileNotFoundError:
            if required:
                raise ReadinessError("readiness-input-missing") from None
            return None
        if stat.S_ISLNK(details.st_mode):
            raise ReadinessError("readiness-path-symlink")
    if not stat.S_ISREG(candidate.lstat().st_mode):
        raise ReadinessError("readiness-input-not-regular")
    return candidate, candidate.read_bytes()


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _task_status_snapshot(data: bytes) -> dict[str, Any]:
    """Describe task text and a status-insensitive digest for narrow re-entry checks."""
    try:
        lines = data.decode("utf-8").splitlines(keepends=True)
    except UnicodeDecodeError as error:
        raise ReadinessError("readiness-tasks-not-utf8") from error
    normalized: list[str] = []
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for number, line in enumerate(lines, start=1):
        match = CHECKBOX.match(line.rstrip("\r\n"))
        if match is None or not TASK_ID.match(match.group(2)):
            normalized.append(line)
            continue
        identifier, separator, description = match.group(2).partition(" ")
        if not separator or identifier in seen:
            raise ReadinessError("readiness-task-snapshot-invalid")
        seen.add(identifier)
        marker_start = line.find("[")
        if marker_start < 0 or marker_start + 2 >= len(line):
            raise ReadinessError("readiness-task-snapshot-invalid")
        normalized.append(line[:marker_start + 1] + " " + line[marker_start + 2:])
        items.append({
            "id": identifier,
            "line": number,
            "text_sha256": _digest(match.group(2).encode()),
            "marker": "checked" if match.group(1).lower() == "x" else "unchecked",
        })
    return {"sha256": _digest(data), "status_insensitive_sha256": _digest("".join(normalized).encode()),
            "items": items}


def _json_file(root: Path, relative: str, *, required: bool = False) -> tuple[dict[str, Any], str] | None:
    item = _safe_file(root, relative, required=required)
    if item is None:
        return None
    _, data = item
    try:
        parsed = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ReadinessError("readiness-json-invalid") from error
    if not isinstance(parsed, dict):
        raise ReadinessError("readiness-json-invalid")
    return parsed, _digest(data)


def _active_feature(root: Path, selected: str) -> None:
    pointer = _json_file(root, ".specify/feature.json", required=True)
    assert pointer is not None
    data, _ = pointer
    if data.get("feature_directory") != selected:
        raise ReadinessError("readiness-feature-identity-mismatch")


def _feature_root(root: Path, feature_directory: str) -> Path:
    feature = PurePosixPath(feature_directory)
    if feature.is_absolute() or len(feature.parts) < 2 or feature.parts[0] != "specs" or any(
        part in {"", ".", ".."} for part in feature.parts
    ):
        raise ReadinessError("readiness-feature-path-out-of-scope")
    target = root
    for part in feature.parts:
        target = target / part
        try:
            details = target.lstat()
        except FileNotFoundError:
            raise ReadinessError("readiness-feature-missing") from None
        if stat.S_ISLNK(details.st_mode):
            raise ReadinessError("readiness-path-symlink")
    if not stat.S_ISDIR(target.lstat().st_mode):
        raise ReadinessError("readiness-feature-not-directory")
    try:
        target.resolve(strict=True).relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as error:
        raise ReadinessError("readiness-feature-path-out-of-scope") from error
    return target


def _checklist_files(root: Path, feature: Path) -> list[tuple[str, bytes]]:
    checklist_dir = feature / "checklists"
    if not checklist_dir.exists():
        return []
    if checklist_dir.is_symlink() or not checklist_dir.is_dir():
        raise ReadinessError("readiness-path-symlink")
    found: list[tuple[str, bytes]] = []
    checklist_paths: list[Path] = []
    def walk_error(_: OSError) -> None:
        raise ReadinessError("readiness-checklist-unreadable")
    for current, directories, filenames in os.walk(checklist_dir, followlinks=False, onerror=walk_error):
        directory = Path(current)
        for name in list(directories):
            child = directory / name
            if child.is_symlink():
                raise ReadinessError("readiness-path-symlink")
        checklist_paths.extend(directory / name for name in filenames)
    for path in sorted(checklist_paths):
        relative = path.relative_to(root).as_posix()
        item = _safe_file(root, relative, required=True)
        assert item is not None
        found.append((relative, item[1]))
    return found


def _items(files: list[tuple[str, bytes]]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    criteria: list[dict[str, Any]] = []
    source_digests: dict[str, str] = {}
    for relative, data in files:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ReadinessError("readiness-checklist-not-utf8") from error
        source_digests[relative] = _digest(data)
        occurrences: dict[str, int] = {}
        for line_number, line in enumerate(text.splitlines(), start=1):
            match = CHECKBOX.match(line)
            has_core_marker = CORE_MARKER.search(line) is not None
            if not match:
                if has_core_marker:
                    raise ReadinessError("readiness-checklist-item-malformed")
                continue
            # Spec Kit core scans literal checkbox markers in the whole line.
            # Do not let a valid leading marker hide another marker in its text.
            # That would make this report say ready while core still sees an
            # unchecked item (or count a second checked item).
            if len(CORE_MARKER.findall(line)) != 1:
                raise ReadinessError("readiness-checklist-item-malformed")
            marker, exact_text = match.groups()
            if exact_text is None or not exact_text.strip():
                raise ReadinessError("readiness-checklist-item-malformed")
            exact_text = exact_text.strip()
            occurrence = occurrences.get(exact_text, 0) + 1
            occurrences[exact_text] = occurrence
            item_hash = hashlib.sha256(f"{relative}\0{exact_text}\0{occurrence}".encode()).hexdigest()[:16]
            criteria.append({
                "id": f"criterion-{item_hash}",
                "source_path": relative,
                "line": line_number,
                "source_item": exact_text,
                "occurrence": occurrence,
                "marker": "checked" if marker.lower() == "x" else "unchecked",
                "source_sha256": source_digests[relative],
            })
    return criteria, source_digests


def _review_state(root: Path, feature_directory: str, source_digests: dict[str, str]) -> tuple[bool, dict[str, Any]]:
    review_path = f"{feature_directory}/validation/readiness-review.json"
    review_file = _json_file(root, review_path)
    if review_file is None:
        return False, {"state": "missing", "path": review_path}
    review, review_digest = review_file
    reviewer = review.get("reviewer")
    inputs = review.get("reviewed_inputs")
    if (review.get("schema_version") != "1.0" or review.get("state") != "complete"
            or reviewer != "FarmBoy Reviewer" or not isinstance(inputs, dict)
            or not isinstance(review.get("reviewer_verdict_sha256"), str)
            or not SHA256.fullmatch(review["reviewer_verdict_sha256"])):
        return False, {"state": "invalid", "path": review_path, "sha256": review_digest}
    required = dict(source_digests)
    for name in ("spec.md", "plan.md", "tasks.md"):
        rel = f"{feature_directory}/{name}"
        item = _safe_file(root, rel, required=True)
        assert item is not None
        required[rel] = _digest(item[1])
    reconciliations = review.get("reconciliations", [])
    if not isinstance(reconciliations, list):
        return False, {"state": "invalid", "path": review_path, "sha256": review_digest}
    by_path = {item.get("source_path"): item for item in reconciliations if isinstance(item, dict)}
    equivalent = set(inputs) == set(required)
    task_status_delta: dict[str, Any] | None = None
    if equivalent:
        for path, current_digest in required.items():
            original_digest = inputs[path]
            if original_digest == current_digest:
                continue
            if path == f"{feature_directory}/tasks.md":
                saved_snapshot = review.get("task_status_snapshot")
                task_file = _safe_file(root, path, required=True)
                assert task_file is not None
                try:
                    current_snapshot = _task_status_snapshot(task_file[1])
                except ReadinessError:
                    equivalent = False
                    break
                if (not isinstance(saved_snapshot, dict)
                        or saved_snapshot.get("sha256") != original_digest
                        or not SHA256.fullmatch(str(saved_snapshot.get("status_insensitive_sha256", "")))
                        or saved_snapshot.get("status_insensitive_sha256") != current_snapshot["status_insensitive_sha256"]
                        or [{key: item.get(key) for key in ("id", "line", "text_sha256")}
                            for item in saved_snapshot.get("items", []) if isinstance(item, dict)] != [
                            {key: item[key] for key in ("id", "line", "text_sha256")}
                            for item in current_snapshot["items"]
                        ]):
                    equivalent = False
                    break
                old_items = {item["id"]: item["marker"] for item in saved_snapshot.get("items", [])
                             if isinstance(item, dict) and isinstance(item.get("id"), str)}
                changed = [item["id"] for item in current_snapshot["items"]
                           if old_items.get(item["id"]) != item["marker"]]
                task_status_delta = {
                    "original_sha256": original_digest,
                    "current_sha256": current_digest,
                    "changed_task_ids": changed,
                    "equivalence": "task-status-markers-only",
                }
                continue
            record = by_path.get(path)
            if path not in source_digests or not isinstance(record, dict):
                equivalent = False
                break
            if record.get("source_file_sha256_before") != original_digest or record.get("source_file_sha256_after") != current_digest:
                equivalent = False
                break
            source = _safe_file(root, path, required=True)
            assert source is not None
            try:
                reconstructed = _reverse_reconciliation(source[1], record.get("changes"))
            except ReadinessError:
                equivalent = False
                break
            if _digest(reconstructed) != original_digest:
                equivalent = False
                break
    if not equivalent:
        return False, {"state": "stale", "path": review_path, "sha256": review_digest,
                       "reviewer": reviewer, "expected_inputs": required}
    return True, {"state": "complete", "path": review_path, "sha256": review_digest,
                  "reviewer": reviewer, "reviewed_inputs": inputs, "current_inputs": required,
                  **({"task_status_delta": task_status_delta} if task_status_delta is not None else {})}


def _reverse_reconciliation(current: bytes, changes: Any) -> bytes:
    """Undo only recorded marker checks and line relocations for digest comparison."""
    if not isinstance(changes, list):
        raise ReadinessError("readiness-reconciliation-invalid")
    try:
        lines = current.decode("utf-8").splitlines(keepends=True)
    except UnicodeDecodeError as error:
        raise ReadinessError("readiness-reconciliation-invalid") from error
    removals = [change for change in changes if isinstance(change, dict) and change.get("action") == "remove"]
    markers = [change for change in changes if isinstance(change, dict) and change.get("action") == "check"]
    if len(removals) + len(markers) != len(changes):
        raise ReadinessError("readiness-reconciliation-invalid")
    for change in sorted(removals, key=lambda item: item.get("line_number", 0)):
        position = change.get("line_number")
        original_line = change.get("original_line")
        if not isinstance(position, int) or position < 1 or not isinstance(original_line, str) or position - 1 > len(lines):
            raise ReadinessError("readiness-reconciliation-invalid")
        lines.insert(position - 1, original_line)
    for change in markers:
        position = change.get("line_number")
        original_line = change.get("original_line")
        updated_line = change.get("updated_line")
        if (not isinstance(position, int) or position < 1 or position > len(lines)
                or not isinstance(original_line, str) or not isinstance(updated_line, str)
                or lines[position - 1] != updated_line):
            raise ReadinessError("readiness-reconciliation-invalid")
        lines[position - 1] = original_line
    return "".join(lines).encode("utf-8")


def _future_obligations(root: Path, feature_directory: str) -> tuple[list[dict[str, Any]], list[str]]:
    path = f"{feature_directory}/validation/future-obligations.json"
    loaded = _json_file(root, path)
    if loaded is None:
        return [], []
    data, _ = loaded
    entries = data.get("obligations")
    blockers: list[str] = []
    pending: list[dict[str, Any]] = []
    if data.get("schema_version") != "1.0" or data.get("feature_directory") != feature_directory or not isinstance(entries, list):
        return [], ["future-obligation-record-invalid"]
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            blockers.append("future-obligation-record-invalid")
            continue
        identifier = entry.get("id")
        source_digest = entry.get("source_item_sha256")
        before_digest = entry.get("source_file_sha256_before")
        after_digest = entry.get("source_file_sha256_after")
        status = entry.get("status")
        if (not isinstance(identifier, str) or not identifier or identifier in seen
                or not all(isinstance(value, str) and SHA256.fullmatch(value)
                           for value in (source_digest, before_digest, after_digest))
                or status != "pending" or not entry.get("owner") or not entry.get("due_phase")
                or not entry.get("expected_evidence") or not entry.get("source_path")
                or not entry.get("source_item") or entry.get("recorded_by") != "main-task-recorder"):
            blockers.append("future-obligation-record-invalid")
            continue
        seen.add(identifier)
        pending.append({"id": identifier, "owner": entry["owner"], "due_phase": entry["due_phase"],
                        "status": "pending", "source_path": entry["source_path"],
                        "source_item": entry["source_item"], "source_item_sha256": source_digest})
    return pending, blockers


def _classifications(root: Path, feature_directory: str, criteria: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], str | None, list[dict[str, Any]]]:
    path = f"{feature_directory}/validation/preparation.json"
    loaded = _json_file(root, path)
    if loaded is None:
        return {}, None, []
    data, classification_digest = loaded
    records = data.get("criteria")
    if data.get("schema_version") != "1.0" or data.get("feature_directory") != feature_directory or not isinstance(records, list):
        raise ReadinessError("readiness-classification-invalid")
    current = {item["id"] for item in criteria}
    output: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            raise ReadinessError("readiness-classification-invalid")
        identifier = record.get("id")
        category = record.get("category")
        owner = record.get("owner")
        if (identifier not in current or identifier in output or category not in ALLOWED_CATEGORIES
                or not isinstance(owner, str) or not owner.strip()):
            raise ReadinessError("readiness-classification-invalid")
        output[identifier] = record
    if set(output) != current:
        raise ReadinessError("criterion-coverage-incomplete")
    relocations = data.get("relocations", [])
    if not isinstance(relocations, list):
        raise ReadinessError("readiness-classification-invalid")
    relocated: list[dict[str, Any]] = []
    seen_relocated: set[str] = set()
    for item in relocations:
        if not isinstance(item, dict) or not isinstance(item.get("classification"), dict):
            raise ReadinessError("readiness-classification-invalid")
        classification = item["classification"]
        identifier = classification.get("id")
        if (not isinstance(identifier, str) or identifier in current or identifier in seen_relocated
                or classification.get("category") not in {"implementation-evidence", "human-acceptance"}
                or item.get("action") != "relocate-future-obligation"
                or item.get("source_path") != classification.get("source_path")
                or item.get("source_item") != classification.get("source_item")
                or not all(isinstance(item.get(key), str) and SHA256.fullmatch(item[key])
                           for key in ("source_file_sha256_before", "source_file_sha256_after", "review_evidence_sha256"))):
            raise ReadinessError("readiness-classification-invalid")
        seen_relocated.add(identifier)
        relocated.append(item)
    return output, classification_digest, relocated


def _current_review_inputs(root: Path, feature_directory: str, checklist_digests: dict[str, str]) -> dict[str, str]:
    required = dict(checklist_digests)
    for name in ("spec.md", "plan.md", "tasks.md"):
        relative = f"{feature_directory}/{name}"
        item = _safe_file(root, relative, required=True)
        assert item is not None
        required[relative] = _digest(item[1])
    return required


def _preflight_output(root: Path, feature_directory: str, relative: str) -> str | None:
    """Validate one feature-local output and return its current digest, if present."""
    path = PurePosixPath(relative)
    feature = PurePosixPath(feature_directory)
    if (path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts)
            or path.parts[:len(feature.parts)] != feature.parts):
        raise ReadinessError("readiness-record-path-out-of-scope")
    candidate = root
    for index, part in enumerate(path.parts):
        candidate = candidate / part
        try:
            details = candidate.lstat()
        except FileNotFoundError:
            if index != len(path.parts) - 1:
                raise ReadinessError("readiness-record-parent-missing") from None
            return None
        if stat.S_ISLNK(details.st_mode):
            raise ReadinessError("readiness-record-path-unsafe")
        if index < len(path.parts) - 1 and not stat.S_ISDIR(details.st_mode):
            raise ReadinessError("readiness-record-parent-not-directory")
        if index == len(path.parts) - 1:
            if not stat.S_ISREG(details.st_mode):
                raise ReadinessError("readiness-record-destination-not-regular")
            try:
                candidate.resolve(strict=True).relative_to((root / feature_directory).resolve(strict=True))
            except (OSError, ValueError) as error:
                raise ReadinessError("readiness-record-path-out-of-scope") from error
            return _digest(candidate.read_bytes())
    raise ReadinessError("readiness-record-path-invalid")


def _live_review_state(root: Path, feature_directory: str, checklist_digests: dict[str, str],
                       reviewer_report: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    expected = _current_review_inputs(root, feature_directory, checklist_digests)
    if (reviewer_report.get("reviewer") != "FarmBoy Reviewer"
            or reviewer_report.get("state") != "complete"
            or reviewer_report.get("findings") not in ([], None)
            or reviewer_report.get("reviewed_inputs") != expected):
        return False, {"state": "stale-or-invalid", "reviewer": reviewer_report.get("reviewer"),
                       "reviewed_inputs": reviewer_report.get("reviewed_inputs"), "current_inputs": expected}
    return True, {"state": "complete", "reviewer": "FarmBoy Reviewer",
                  "reviewed_inputs": expected,
                  "verdict_sha256": _digest(json.dumps(reviewer_report, sort_keys=True, separators=(",", ":")).encode())}


def assess(project_root: Path, feature_directory: str, reviewer_report: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return readiness evidence for the currently active feature without mutation."""
    root = Path(project_root).resolve(strict=True)
    try:
        _active_feature(root, feature_directory)
        feature = _feature_root(root, feature_directory)
        files = _checklist_files(root, feature)
        criteria, checklist_digests = _items(files)
        classifications, classification_digest, relocations = _classifications(root, feature_directory, criteria)
        if reviewer_report is None:
            review_current, review = _review_state(root, feature_directory, checklist_digests)
        else:
            review_current, review = _live_review_state(root, feature_directory, checklist_digests, reviewer_report)
        pending_future, future_errors = _future_obligations(root, feature_directory)
        pending_ids = {item["id"] for item in pending_future}
        if pending_ids.intersection(item["id"] for item in criteria):
            raise ReadinessError("readiness-criterion-identity-collision")
        if any(item["classification"]["id"] not in pending_ids for item in relocations):
            raise ReadinessError("readiness-classification-invalid")
    except (ReadinessError, OSError) as error:
        reason = str(error) if isinstance(error, ReadinessError) else "readiness-input-unreadable"
        return {
            "schema_version": "1.0", "feature_directory": feature_directory, "state": "blocked",
            "reason_code": reason, "blocking_ids": [reason], "pending_future_ids": [], "criteria": [],
            "source_evidence": [], "resume_action": "repair-readiness-inputs-and-rerun-analysis",
        }

    blockers: list[str] = list(future_errors)
    if not review_current:
        blockers.append("independent-review-missing")
    for criterion in criteria:
        classification = classifications.get(criterion["id"], {})
        category = classification.get("category", "preparation-quality")
        owner = classification.get("owner", "specifier" if criterion["source_path"].endswith("/requirements.md") else "independent-reviewer")
        criterion["category"] = category
        criterion["owner"] = owner
        criterion["due_phase"] = classification.get("due_phase", "preparation")
        if category in {"implementation-evidence", "human-acceptance"}:
            criterion["status"] = "blocked"
            criterion["finding_id"] = "future-obligation-not-relocated"
            blockers.append("future-obligation-not-relocated")
        elif category == "unresolved":
            criterion["status"] = "blocked"
            criterion["finding_id"] = "obligation-classification-unresolved"
            blockers.append("obligation-classification-unresolved")
        elif criterion["marker"] == "unchecked":
            criterion["status"] = "blocked"
            criterion["finding_id"] = criterion["id"]
            blockers.append(criterion["id"])
        elif category == "preparation-review" and not review_current:
            criterion["status"] = "blocked"
            criterion["finding_id"] = "independent-review-missing"
            blockers.append("independent-review-missing")
        elif not review_current:
            criterion["status"] = "blocked"
            criterion["finding_id"] = "independent-review-missing"
            blockers.append("independent-review-missing")
        else:
            criterion["category"] = "preparation-quality"
            criterion["owner"] = "quality-owner"
            criterion["status"] = "satisfied"
            criterion["evidence"] = [{"path": criterion["source_path"], "sha256": criterion["source_sha256"]}]
    blockers = list(dict.fromkeys(blockers))
    source_evidence = [{"path": path, "sha256": digest} for path, digest in sorted(checklist_digests.items())]
    for name in ("spec.md", "plan.md", "tasks.md"):
        relative = f"{feature_directory}/{name}"
        source = _safe_file(root, relative, required=True)
        assert source is not None
        source_evidence.append({"path": relative, "sha256": _digest(source[1])})
    if classification_digest:
        source_evidence.append({"path": f"{feature_directory}/validation/preparation.json", "sha256": classification_digest})
    future_file = _safe_file(root, f"{feature_directory}/validation/future-obligations.json", required=False)
    if future_file:
        source_evidence.append({"path": f"{feature_directory}/validation/future-obligations.json", "sha256": _digest(future_file[1])})
    source_evidence.append({"path": f"{feature_directory}/validation/readiness-review.json",
                            "sha256": review.get("sha256"), "state": review.get("state")})
    is_ready = not blockers and all(item["marker"] == "checked" for item in criteria)
    return {
        "schema_version": "1.0", "feature_directory": feature_directory,
        "state": "ready" if is_ready else "blocked",
        "reason_code": "preparation-ready" if is_ready else "preparation-evidence-incomplete",
        "blocking_ids": blockers,
        "pending_future_ids": [item["id"] for item in pending_future],
        "criteria": criteria,
        "source_evidence": source_evidence,
        "independent_review": review,
        "pending_future_obligations": pending_future,
        "resume_action": "" if is_ready else "resolve-owned-readiness-findings-and-rerun-fresh-assessments",
    }



def recorder_error_report(feature_directory: str, reason: str) -> dict[str, Any]:
    """Return bounded recovery information for a failed recording operation."""
    resume_action = "repair-readiness-inputs-and-rerun-analysis"
    if reason == "readiness-review-payload-invalid":
        resume_action = "provide-a-current-independent-review-object"
    elif reason == "readiness-record-write-rolled-back":
        resume_action = "rerun-the-same-current-review-verdict-after-a-fresh-assessment"
    elif reason.startswith("readiness-record-recovery-required:"):
        resume_action = "inspect-listed-readiness-paths-and-reconcile-before-retrying"
    return {"schema_version": "1.0", "feature_directory": feature_directory,
            "state": "blocked", "reason_code": reason,
            "blocking_ids": [reason], "pending_future_ids": [], "criteria": [],
            "source_evidence": [], "resume_action": resume_action}


def record_review(project_root: Path, feature_directory: str, reviewer_report: dict[str, Any]) -> dict[str, Any]:
    """Record a current exact verdict and apply only its supported checklist decisions."""
    if not isinstance(reviewer_report, dict):
        raise ReadinessError("readiness-review-payload-invalid")
    root = Path(project_root).resolve(strict=True)
    _active_feature(root, feature_directory)
    feature = _feature_root(root, feature_directory)
    files = _checklist_files(root, feature)
    criteria, checklist_digests = _items(files)
    expected = dict(checklist_digests)
    for name in ("spec.md", "plan.md", "tasks.md"):
        relative = f"{feature_directory}/{name}"
        item = _safe_file(root, relative, required=True)
        assert item is not None
        expected[relative] = _digest(item[1])
    tasks_path = f"{feature_directory}/tasks.md"
    task_snapshot = _task_status_snapshot(_safe_file(root, tasks_path, required=True)[1])
    if (reviewer_report.get("reviewer") != "FarmBoy Reviewer"
            or reviewer_report.get("state") != "complete"
            or reviewer_report.get("reviewed_inputs") != expected
            or reviewer_report.get("findings") not in ([], None)
            or not isinstance(reviewer_report.get("satisfied_criteria", []), list)
            or not isinstance(reviewer_report.get("future_classifications", []), list)):
        raise ReadinessError("readiness-review-verdict-invalid-or-stale")
    criteria_by_id = {item["id"]: item for item in criteria}
    satisfied = reviewer_report.get("satisfied_criteria", [])
    future_classifications = reviewer_report.get("future_classifications", [])
    if not isinstance(satisfied, list) or len(satisfied) != len(set(satisfied)) or not isinstance(future_classifications, list):
        raise ReadinessError("readiness-review-verdict-invalid-or-stale")
    changes: dict[str, list[dict[str, Any]]] = {}
    source_bytes = {path: data for path, data in files}
    for identifier in satisfied:
        criterion = criteria_by_id.get(identifier)
        if (criterion is None or criterion["marker"] != "unchecked"
                or criterion["source_path"].endswith("/requirements.md")):
            raise ReadinessError("readiness-review-marker-owner-invalid")
        changes.setdefault(criterion["source_path"], []).append({
            "id": identifier, "action": "check", "line_number": criterion["line"],
            "source_item": criterion["source_item"], "occurrence": criterion["occurrence"],
        })
    classified_ids: set[str] = set()
    for record in future_classifications:
        if (not isinstance(record, dict) or not isinstance(record.get("id"), str)
                or record.get("category") not in {"implementation-evidence", "human-acceptance"}
                or not all(isinstance(record.get(key), str) and record[key].strip()
                           for key in ("owner", "due_phase", "expected_evidence", "source_path", "source_item"))):
            raise ReadinessError("readiness-review-verdict-invalid-or-stale")
        identifier = record["id"]
        criterion = criteria_by_id.get(identifier)
        if (criterion is None or criterion["marker"] != "unchecked" or identifier in classified_ids
                or identifier in satisfied or criterion["source_path"] != record["source_path"]
                or criterion["source_item"] != record["source_item"]):
            raise ReadinessError("readiness-review-classification-does-not-match-source")
        classified_ids.add(identifier)
        same_text = [item for item in criteria
                     if item["source_path"] == criterion["source_path"]
                     and item["source_item"] == criterion["source_item"]]
        if len(same_text) > 1:
            raise ReadinessError("readiness-relocation-duplicate-text-ambiguous")
        changes.setdefault(criterion["source_path"], []).append({
            "id": identifier, "action": "remove", "line_number": criterion["line"],
            "source_item": criterion["source_item"], "occurrence": criterion["occurrence"],
        })

    reconciliations: list[dict[str, Any]] = []
    after_by_path: dict[str, bytes] = {}
    for path, path_changes in sorted(changes.items()):
        lines = source_bytes[path].decode("utf-8").splitlines(keepends=True)
        recorded: list[dict[str, Any]] = []
        for change in sorted(path_changes, key=lambda item: item["line_number"], reverse=True):
            index = change["line_number"] - 1
            if index < 0 or index >= len(lines):
                raise ReadinessError("readiness-review-source-changed")
            original_line = lines[index]
            match = CHECKBOX.match(original_line)
            if (match is None or match.group(1).lower() != " "
                    or match.group(2) != change["source_item"]):
                raise ReadinessError("readiness-review-source-changed")
            if change["action"] == "check":
                updated_line = re.sub(r"- \[ \]", "- [x]", original_line, count=1)
                lines[index] = updated_line
                recorded.append({**change, "original_line": original_line, "updated_line": updated_line})
            else:
                del lines[index]
                recorded.append({**change, "original_line": original_line})
        after_bytes = "".join(lines).encode("utf-8")
        after_by_path[path] = after_bytes
        reconciliations.append({
            "source_path": path, "source_file_sha256_before": _digest(source_bytes[path]),
            "source_file_sha256_after": _digest(after_bytes), "changes": recorded,
        })

    reviewer_verdict_digest = _digest(json.dumps(reviewer_report, sort_keys=True, separators=(",", ":")).encode())
    record = {
        "schema_version": "1.0", "feature_directory": feature_directory,
        "state": "complete", "reviewer": "FarmBoy Reviewer", "reviewed_inputs": expected,
        "task_status_snapshot": task_snapshot,
        "reviewer_verdict_sha256": reviewer_verdict_digest,
        "satisfied_criteria": satisfied, "future_classifications": future_classifications,
        "reconciliations": reconciliations,
    }
    destination = feature / "validation/readiness-review.json"
    review_bytes = (json.dumps(record, sort_keys=True, indent=2) + "\n").encode()

    preparation_path = f"{feature_directory}/validation/preparation.json"
    preparation_file = _json_file(root, preparation_path)
    preparation_digest: str | None = None
    preparation_bytes: bytes | None = None
    if preparation_file is not None and classified_ids:
        preparation, preparation_digest = preparation_file
        classifications, verified_digest, _ = _classifications(root, feature_directory, criteria)
        if verified_digest != preparation_digest:
            raise ReadinessError("readiness-classification-stale")
        if not classified_ids.issubset(classifications):
            raise ReadinessError("readiness-classification-invalid")
        preparation["criteria"] = [item for item in preparation["criteria"] if item["id"] not in classified_ids]
        prior_relocations = preparation.get("relocations", [])
        if not isinstance(prior_relocations, list):
            raise ReadinessError("readiness-classification-invalid")
        for classification in future_classifications:
            reconciliation = next(item for item in reconciliations
                                  if item["source_path"] == classification["source_path"])
            preparation.setdefault("relocations", []).append({
                "action": "relocate-future-obligation", "classification": classifications[classification["id"]],
                "source_path": classification["source_path"], "source_item": classification["source_item"],
                "source_file_sha256_before": reconciliation["source_file_sha256_before"],
                "source_file_sha256_after": reconciliation["source_file_sha256_after"],
                "review_evidence_sha256": _digest(review_bytes),
            })
        preparation_bytes = (json.dumps(preparation, sort_keys=True, indent=2) + "\n").encode()

    ledger_relative = f"{feature_directory}/validation/future-obligations.json"
    ledger_path = root / ledger_relative
    ledger_records = [
        {**classification,
         "source_item_sha256": hashlib.sha256(classification["source_item"].encode()).hexdigest(),
         "source_file_sha256_before": next(item["source_file_sha256_before"] for item in reconciliations if item["source_path"] == classification["source_path"]),
         "source_file_sha256_after": next(item["source_file_sha256_after"] for item in reconciliations if item["source_path"] == classification["source_path"]),
         "status": "pending", "recorded_by": "main-task-recorder",
         "review_evidence_sha256": _digest(review_bytes)}
        for classification in future_classifications
    ]
    ledger_bytes: bytes | None = None
    if ledger_records:
        loaded_ledger = _json_file(root, ledger_relative)
        if loaded_ledger is None:
            ledger = {"schema_version": "1.0", "feature_directory": feature_directory, "obligations": []}
        else:
            ledger, _ = loaded_ledger
        existing = ledger.get("obligations")
        if (ledger.get("schema_version") != "1.0" or ledger.get("feature_directory") != feature_directory
                or not isinstance(existing, list)
                or any(isinstance(item, dict) and item.get("id") in classified_ids for item in existing)):
            raise ReadinessError("future-obligation-record-invalid")
        ledger["obligations"].extend(ledger_records)
        ledger_bytes = (json.dumps(ledger, sort_keys=True, indent=2) + "\n").encode()

    # Revalidate authority and all reviewed inputs immediately before effect.
    _active_feature(root, feature_directory)
    now_files = _checklist_files(root, feature)
    _, now_checklists = _items(now_files)
    now_inputs = dict(now_checklists)
    for name in ("spec.md", "plan.md", "tasks.md"):
        relative = f"{feature_directory}/{name}"
        item = _safe_file(root, relative, required=True)
        assert item is not None
        now_inputs[relative] = _digest(item[1])
    if now_inputs != expected:
        raise ReadinessError("readiness-review-verdict-stale")
    output_data: dict[str, bytes] = {}
    if ledger_bytes is not None:
        output_data[ledger_relative] = ledger_bytes
    if preparation_bytes is not None:
        output_data[preparation_path] = preparation_bytes
    output_data[f"{feature_directory}/validation/readiness-review.json"] = review_bytes
    for path, data in after_by_path.items():
        output_data[path] = data
    output_digests = {path: _preflight_output(root, feature_directory, path) for path in output_data}
    # Recheck every destination and source after all validation, before the first write.
    latest_files = _checklist_files(root, feature)
    _, latest_checklists = _items(latest_files)
    if _current_review_inputs(root, feature_directory, latest_checklists) != expected:
        raise ReadinessError("readiness-review-verdict-stale")
    for path, previous_digest in output_digests.items():
        if _preflight_output(root, feature_directory, path) != previous_digest:
            raise ReadinessError("readiness-record-destination-changed")
    original_bytes: dict[str, bytes | None] = {}
    for relative in output_data:
        current = _safe_file(root, relative, required=False)
        original_bytes[relative] = current[1] if current is not None else None
        original_digest = _digest(current[1]) if current is not None else None
        if original_digest != output_digests[relative]:
            raise ReadinessError("readiness-record-destination-changed")
    try:
        for relative, data in output_data.items():
            _atomic_write(root / relative, data)
    except (OSError, ReadinessError) as error:
        rollback: list[str] = []
        conflicts: list[str] = []
        for relative, intended in output_data.items():
            try:
                current_file = _safe_file(root, relative, required=False)
                current = current_file[1] if current_file is not None else None
                original = original_bytes[relative]
                if current == original:
                    continue
                if current != intended or _preflight_output(root, feature_directory, relative) != _digest(intended):
                    conflicts.append(relative)
                    continue
                rollback.append(relative)
            except (OSError, ReadinessError):
                conflicts.append(relative)
        if conflicts:
            raise ReadinessError("readiness-record-recovery-required:" + ",".join(conflicts)) from error
        for relative in reversed(rollback):
            path = root / relative
            intended_digest = _digest(output_data[relative])
            try:
                # Recheck immediately before each compensation. In particular,
                # restore the removed checklist source before removing its ledger.
                if _preflight_output(root, feature_directory, relative) != intended_digest:
                    raise ReadinessError("readiness-record-recovery-required:" + relative)
                original = original_bytes[relative]
                if original is None:
                    path.unlink()
                else:
                    _atomic_write(path, original)
            except (OSError, ReadinessError) as rollback_error:
                raise ReadinessError("readiness-record-recovery-required:" + relative) from rollback_error
        raise ReadinessError("readiness-record-write-rolled-back") from error
    return {"state": "recorded", "path": destination.relative_to(root).as_posix(),
            "sha256": _digest(review_bytes), "reviewed_inputs": expected,
            "updated_paths": [*([ledger_relative] if ledger_bytes is not None else []),
                              *([preparation_path] if preparation_bytes is not None else []),
                              destination.relative_to(root).as_posix(), *sorted(after_by_path)]}


def _atomic_write(path: Path, data: bytes) -> None:
    """Replace one validated feature-local artifact through a same-directory temp file."""
    if path.parent.is_symlink() or not path.parent.is_dir() or (path.exists() and path.is_symlink()):
        raise ReadinessError("readiness-record-path-unsafe")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
    except OSError:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    command = subparsers.add_parser("assess", help="assess the active feature's current checklist evidence")
    command.add_argument("--project", type=Path, required=True)
    command.add_argument("--feature-directory", required=True)
    review_command = subparsers.add_parser("record-review", help="record a current exact Reviewer verdict")
    review_command.add_argument("--project", type=Path, required=True)
    review_command.add_argument("--feature-directory", required=True)
    args = parser.parse_args(argv)
    operation_failed = False
    try:
        if args.command == "assess":
            result = assess(args.project, args.feature_directory)
        elif args.command == "record-review":
            payload = json.load(sys.stdin)
            result = record_review(args.project, args.feature_directory, payload)
    except (OSError, ReadinessError) as error:
        operation_failed = True
        reason = str(error)
        result = recorder_error_report(args.feature_directory, reason)
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    # A blocked assessment is a successful inspection with findings. Recorder
    # failures are operational errors and keep their structured recovery JSON.
    return 2 if operation_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Read and validate one fixed snapshot of local FarmBoy metric records."""

from __future__ import annotations

import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
CONTROLLER_SCRIPTS = REPOSITORY_ROOT / "controllers/farmboy/scripts/python"
if not CONTROLLER_SCRIPTS.is_dir():
    raise RuntimeError("report source layout is incomplete: controller metrics helper is missing")
sys.path.insert(0, str(CONTROLLER_SCRIPTS))
try:
    from metrics import MAX_INPUT_BYTES, validate_record
except ImportError as error:
    raise RuntimeError("report source layout is incomplete: controller metrics helper is unavailable") from error


CANDIDATE_NAME = re.compile(r"metric-([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.json\Z")
INVALID_CATEGORIES = ("unreadable", "oversized", "malformed-json", "unsupported-schema", "invalid-contract")
PROJECTION_FIELDS = (
    "schema_version", "invocation_id", "run_id", "step_id", "invocation_kind",
    "agent_name", "skill_id", "workflow_id", "project_label", "started_at",
    "finished_at", "duration_ms", "model", "effort",
)


class ReportInputError(RuntimeError):
    """A report input directory could not be enumerated safely."""


class _MalformedMetricJson(ValueError):
    """A candidate has invalid JSON structure or prohibited JSON values."""


class _UnparsedJsonInteger:
    """A syntactically valid integer too large for Python's guarded conversion."""


def _parse_json_integer(value: str) -> int | _UnparsedJsonInteger:
    """Parse ordinary integers while keeping oversized unknown values ignorable."""
    try:
        return int(value)
    except ValueError:
        return _UnparsedJsonInteger()


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build one JSON object while rejecting duplicate keys."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _MalformedMetricJson("duplicate-key")
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    """Reject JSON's non-standard NaN and infinity constants."""
    raise _MalformedMetricJson("nonfinite-number")


def _completed_name(name: str) -> bool:
    """Return whether a direct entry uses the completed metric filename convention."""
    return CANDIDATE_NAME.fullmatch(name) is not None


def discover_candidates(directory: Path) -> list[Path]:
    """Capture one sorted top-level list of completed regular metric files."""
    root = Path(directory)
    try:
        root_stat = root.lstat()
    except FileNotFoundError:
        return []
    except OSError as error:
        raise ReportInputError("input-inaccessible") from error
    if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
        raise ReportInputError("input-inaccessible")
    try:
        entries = list(root.iterdir())
    except OSError as error:
        raise ReportInputError("input-inaccessible") from error

    candidates: list[Path] = []
    for path in entries:
        if not _completed_name(path.name):
            continue
        try:
            entry_stat = path.lstat()
        except FileNotFoundError:
            # The name was present at discovery but disappeared before classification.
            candidates.append(path)
            continue
        except OSError:
            candidates.append(path)
            continue
        if stat.S_ISREG(entry_stat.st_mode):
            candidates.append(path)
    return sorted(candidates, key=lambda item: item.name)


def _same_file_state(before: os.stat_result, after: os.stat_result) -> bool:
    return (
        before.st_dev == after.st_dev
        and before.st_ino == after.st_ino
        and before.st_size == after.st_size
        and before.st_mtime_ns == after.st_mtime_ns
    )


def _read_candidate(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    """Read a candidate once with a strict byte bound and reject detected mutation."""
    try:
        before_path = path.lstat()
        if not stat.S_ISREG(before_path.st_mode):
            return None, "unreadable"
        if before_path.st_size > MAX_INPUT_BYTES:
            return None, "oversized"
        no_follow = getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, os.O_RDONLY | no_follow)
        with os.fdopen(descriptor, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or not _same_file_state(before_path, opened):
                return None, "unreadable"
            if opened.st_size > MAX_INPUT_BYTES:
                return None, "oversized"
            raw = stream.read(MAX_INPUT_BYTES + 1)
            after_open = os.fstat(stream.fileno())
            after_path = path.lstat()
            if not _same_file_state(opened, after_open) or not _same_file_state(opened, after_path):
                return None, "unreadable"
    except OSError:
        return None, "unreadable"
    if len(raw) > MAX_INPUT_BYTES:
        return None, "oversized"
    try:
        parsed = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_json_object,
                            parse_constant=_reject_nonfinite, parse_int=_parse_json_integer)
    except (UnicodeDecodeError, json.JSONDecodeError, _MalformedMetricJson, ValueError):
        return None, "malformed-json"
    except RecursionError:
        return None, "invalid-contract"
    if (isinstance(parsed, dict) and "schema_version" in parsed
            and (type(parsed["schema_version"]) is not int or parsed["schema_version"] != 1)):
        return None, "unsupported-schema"
    try:
        record = validate_record(parsed)
    except ValueError:
        return None, "invalid-contract"
    return record, None


def read_metric_records(directory: Path) -> dict[str, Any]:
    """Return validated records and input counts from one fixed discovery snapshot."""
    candidates = discover_candidates(Path(directory))
    records: list[dict[str, Any]] = []
    invalid_counts: dict[str, int] = {}
    for candidate in candidates:
        record, category = _read_candidate(candidate)
        if category is not None:
            invalid_counts[category] = invalid_counts.get(category, 0) + 1
        elif record is not None:
            records.append(record)
    return {
        "records": records,
        "candidate_count": len(candidates),
        "invalid_counts": {category: invalid_counts[category] for category in INVALID_CATEGORIES if category in invalid_counts},
    }


def consolidate_records(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Collapse identical invocation projections and exclude every conflicting group."""
    if not isinstance(snapshot, dict) or set(snapshot) != {"records", "candidate_count", "invalid_counts"}:
        raise ValueError("snapshot-contract-invalid")
    records = snapshot["records"]
    candidate_count = snapshot["candidate_count"]
    invalid_counts = snapshot["invalid_counts"]
    if not isinstance(records, list):
        raise ValueError("snapshot-records-invalid")
    if isinstance(candidate_count, bool) or not isinstance(candidate_count, int) or candidate_count < 0:
        raise ValueError("snapshot-candidate-count-invalid")
    if not isinstance(invalid_counts, dict) or any(
        category not in INVALID_CATEGORIES
        or isinstance(count, bool)
        or not isinstance(count, int)
        or count < 0
        for category, count in invalid_counts.items()
    ):
        raise ValueError("snapshot-invalid-counts-invalid")
    normalized_records = [validate_record(record) for record in records]
    invalid_total = sum(invalid_counts.values())
    if candidate_count != len(normalized_records) + invalid_total:
        raise ValueError("snapshot-counts-inconsistent")

    groups: dict[str, list[dict[str, Any]]] = {}
    for record in normalized_records:
        groups.setdefault(record["invocation_id"], []).append(record)

    accepted: list[dict[str, Any]] = []
    duplicate_count = 0
    conflicting_invocation_count = 0
    conflicting_file_count = 0
    for group in groups.values():
        projections = {tuple(record[field] for field in PROJECTION_FIELDS) for record in group}
        if len(projections) != 1:
            conflicting_invocation_count += 1
            conflicting_file_count += len(group)
            continue
        accepted.append(group[0])
        duplicate_count += len(group) - 1

    skipped_count = invalid_total + conflicting_file_count
    summary = {
        "candidate_count": candidate_count,
        "accepted_count": len(accepted),
        "duplicate_count": duplicate_count,
        "conflicting_invocation_count": conflicting_invocation_count,
        "conflicting_file_count": conflicting_file_count,
        "invalid_counts": {category: invalid_counts[category] for category in INVALID_CATEGORIES if category in invalid_counts},
        "skipped_count": skipped_count,
    }
    if summary["accepted_count"] + duplicate_count + skipped_count != candidate_count:
        raise ValueError("snapshot-counts-inconsistent")
    return {"records": accepted, "summary": summary}

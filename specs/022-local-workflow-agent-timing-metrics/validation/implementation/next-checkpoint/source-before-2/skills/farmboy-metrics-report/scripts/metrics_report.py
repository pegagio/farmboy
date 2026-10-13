#!/usr/bin/env python3
"""Read and validate one fixed snapshot of local FarmBoy metric records."""

from __future__ import annotations

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
    from metrics import MAX_INPUT_BYTES, parse_record_json
except ImportError as error:
    raise RuntimeError("report source layout is incomplete: controller metrics helper is unavailable") from error


CANDIDATE_NAME = re.compile(r"metric-([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.json\Z")
INVALID_CATEGORIES = ("unreadable", "oversized", "malformed-json", "unsupported-schema", "invalid-contract")


class ReportInputError(RuntimeError):
    """A report input directory could not be enumerated safely."""


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
        record = parse_record_json(raw)
    except ValueError as error:
        if str(error) == "schema-version-unsupported":
            return None, "unsupported-schema"
        if str(error).startswith("json-"):
            return None, "malformed-json"
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

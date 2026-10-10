#!/usr/bin/env python3
"""Validate transferred FarmBoy feedback reports and create proposal records."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


REPORT_SCHEMA_VERSION = "1.0"
DISPOSITIONS = {"workflow-source-change", "preset-investigation", "agent-policy-investigation", "reproduction-requested", "deferred", "rejected"}
DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
COMPONENT_DIGEST = re.compile(r"^(?:sha256:)?[a-f0-9]{64}$")
REQUIRED_OBSERVATION_FIELDS = (
    "observation_id", "observed_at", "component", "integration", "consumer_project_ref",
    "execution_profile", "expected_behavior", "observed_behavior", "safety_response",
    "manual_fallback_status", "evidence_references", "suggested_change_target", "reporter_disposition",
)
REPORTER_DISPOSITIONS = {"observed", "exported", "received", "triaged", "deferred", "rejected", "duplicate", "reproduction-requested", "workflow-source-change", "preset-investigation", "agent-policy-investigation"}
SENSITIVE_KEY = re.compile(r"(?:secret|password|credential|private.?key|transcript|token)", re.I)
ABSOLUTE_PATH = re.compile(r"(?:file://|(?<![A-Za-z0-9./])/(?!/))[^\s\"']+")
SENSITIVE_VALUE = re.compile(r"(?:sk-[A-Za-z0-9_-]{8,}|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY)")


class IntakeValidationError(ValueError):
    """A portable feedback intake contract violation."""


def canonical_json(value: Any) -> str:
    """Render deterministic JSON for integrity checks and evidence records."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    """Calculate the contract's prefixed SHA-256 digest."""
    return "sha256:" + hashlib.sha256(canonical_json(value).encode()).hexdigest()


def reject(message: str) -> None:
    """Raise a classified intake rejection."""
    raise IntakeValidationError(message)


def require_string(value: Any, field: str) -> str:
    """Require one non-empty string field."""
    if not isinstance(value, str) or not value.strip():
        reject(f"{field} must be a non-empty string")
    return value


def reject_sensitive(value: Any, field: str = "report") -> None:
    """Reject reports containing nonportable or sensitive material."""
    if isinstance(value, dict):
        for key, child in value.items():
            if SENSITIVE_KEY.search(str(key)):
                reject(f"forbidden sensitive field: {field}.{key}")
            reject_sensitive(child, f"{field}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_sensitive(child, f"{field}[{index}]")
    elif isinstance(value, str):
        if ABSOLUTE_PATH.search(value):
            reject(f"absolute host path is forbidden: {field}")
        if SENSITIVE_VALUE.search(value):
            reject(f"sensitive value is forbidden: {field}")


def validate_report(value: Any) -> dict[str, Any]:
    """Validate report shape, integrity, component provenance, and redaction."""
    if not isinstance(value, dict):
        reject("report must be a JSON object")
    reject_sensitive(value)
    for field in ("schema_version", "report_id", "producer", "created_at", "integrity_digest", "observations"):
        if field not in value:
            reject(f"missing report field: {field}")
    if value["schema_version"] != REPORT_SCHEMA_VERSION:
        reject("unsupported report schema_version")
    for field in ("report_id", "producer", "created_at", "integrity_digest"):
        require_string(value[field], field)
    if not DIGEST.fullmatch(value["integrity_digest"]):
        reject("report integrity_digest must be a SHA-256 digest")
    unsigned = dict(value)
    provided_digest = unsigned.pop("integrity_digest")
    if digest(unsigned) != provided_digest:
        reject("report integrity digest mismatch")
    observations = value["observations"]
    if not isinstance(observations, list) or not observations:
        reject("report must contain observations")
    seen: set[str] = set()
    for index, observation in enumerate(observations):
        if not isinstance(observation, dict):
            reject(f"observation {index} must be an object")
        if observation.get("schema_version") != REPORT_SCHEMA_VERSION:
            reject(f"observation {index} has unsupported schema_version")
        for field in REQUIRED_OBSERVATION_FIELDS:
            if field not in observation:
                reject(f"observation {index} is missing {field}")
        for field in REQUIRED_OBSERVATION_FIELDS:
            if field not in {"component", "execution_profile", "evidence_references"}:
                require_string(observation[field], f"observation {index}.{field}")
        observation_id = observation["observation_id"]
        if observation_id in seen:
            reject(f"duplicate observation_id in report: {observation_id}")
        seen.add(observation_id)
        component = observation["component"]
        if not isinstance(component, dict):
            reject(f"observation {index}.component must be an object")
        for field in ("id", "version", "digest"):
            require_string(component.get(field), f"observation {index}.component.{field}")
        if not COMPONENT_DIGEST.fullmatch(component["digest"]):
            reject(f"observation {index}.component.digest must be a SHA-256 digest")
        if not isinstance(observation["execution_profile"], dict):
            reject(f"observation {index}.execution_profile must be an object")
        if not isinstance(observation["evidence_references"], list) or not observation["evidence_references"]:
            reject(f"observation {index}.evidence_references must be a non-empty list")
        if not all(isinstance(item, str) and item.strip() for item in observation["evidence_references"]):
            reject(f"observation {index}.evidence_references must contain non-empty strings")
        if observation["reporter_disposition"] not in REPORTER_DISPOSITIONS:
            reject(f"observation {index}.reporter_disposition is not recognized")
    return value


def root_from_script() -> Path:
    """Locate the source repository from this packaged maintainer script."""
    return Path(__file__).resolve().parents[4]


def existing_records(triage_dir: Path) -> list[dict[str, Any]]:
    """Load only valid JSON triage records for duplicate detection."""
    records: list[dict[str, Any]] = []
    if not triage_dir.exists():
        return records
    for path in sorted(triage_dir.glob("*.json")):
        try:
            records.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            reject(f"existing triage record is invalid JSON: {path.name}")
    return records


def intake(report_path: Path, disposition: str, rationale: str, received_at: str, root: Path | None = None) -> dict[str, Any]:
    """Create an inbox copy and bounded disposition without mutating source artifacts."""
    if disposition not in DISPOSITIONS:
        reject("unrecognized disposition")
    require_string(rationale, "rationale")
    require_string(received_at, "received_at")
    reject_sensitive(rationale, "rationale")
    reject_sensitive(received_at, "received_at")
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        reject(f"report does not exist: {report_path}")
    except json.JSONDecodeError as error:
        reject(f"report is not valid JSON: {error.msg}")
    report = validate_report(report)
    source_root = root or root_from_script()
    inbox_dir = source_root / "feedback/inbox"
    triage_dir = source_root / "feedback/triage"
    duplicates = [record for record in existing_records(triage_dir) if record.get("report_integrity_digest") == report["integrity_digest"]]
    record_base = "intake-" + hashlib.sha256(report["integrity_digest"].encode()).hexdigest()[:12]
    record_id = record_base if not duplicates else f"{record_base}-duplicate-{len(duplicates)}"
    status = "duplicate" if duplicates else "triaged"
    effective_disposition = "duplicate" if duplicates else disposition
    next_action = "Preserve the duplicate relationship; do not create a second source proposal." if duplicates else "Create or amend a FarmBoy specification proposal, then use the normal planning, task, and implementation flow."
    record = {
        "schema_version": "1.0",
        "intake_id": record_id,
        "received_at": received_at,
        "report_id": report["report_id"],
        "report_integrity_digest": report["integrity_digest"],
        "component_coordinates": [observation["component"] for observation in report["observations"]],
        "validation_result": "accepted",
        "status": status,
        "proposed_disposition": effective_disposition,
        "rationale": rationale,
        "duplicate_of": duplicates[0].get("intake_id") if duplicates else None,
        "next_action": next_action,
    }
    inbox_dir.mkdir(parents=True, exist_ok=True)
    triage_dir.mkdir(parents=True, exist_ok=True)
    if not duplicates:
        (inbox_dir / f"{record_id}.json").write_text(canonical_json(report) + "\n", encoding="utf-8")
    (triage_dir / f"{record_id}.json").write_text(canonical_json(record) + "\n", encoding="utf-8")
    return record


def main(argv: list[str] | None = None) -> int:
    """Run one non-mutating maintainer intake action."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--disposition", required=True)
    parser.add_argument("--rationale", required=True)
    parser.add_argument("--received-at", required=True)
    parser.add_argument("--root", type=Path)
    args = parser.parse_args(argv)
    try:
        record = intake(args.report, args.disposition, args.rationale, args.received_at, args.root)
    except IntakeValidationError as error:
        print(json.dumps({"status": "rejected", "reason": str(error)}, sort_keys=True))
        return 2
    print(json.dumps(record, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

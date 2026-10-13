#!/usr/bin/env python3
"""Validate, capture, and export portable FarmBoy feedback evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

OBSERVATION_SCHEMA_VERSION = "1.0"
REPORT_SCHEMA_VERSION = "1.0"
REQUIRED_FIELDS = (
    "observation_id", "observed_at", "component", "integration", "consumer_project_ref",
    "execution_profile", "expected_behavior", "observed_behavior", "safety_response",
    "manual_fallback_status", "evidence_references", "suggested_change_target", "reporter_disposition",
)
SENSITIVE_KEY = re.compile(r"(?:secret|password|credential|private.?key|transcript|token)", re.I)
ABSOLUTE_PATH = re.compile(r"(?:file://|(?<![A-Za-z0-9./])/(?!/))[^\s\"']+")
SENSITIVE_VALUE = re.compile(r"(?:sk-[A-Za-z0-9_-]{8,}|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY)")
DIGEST = re.compile(r"^(?:sha256:)?[a-f0-9]{64}$")
DISPOSITIONS = {"observed", "exported", "received", "triaged", "deferred", "rejected", "duplicate", "reproduction-requested", "workflow-source-change", "preset-investigation", "agent-policy-investigation"}


class FeedbackValidationError(ValueError):
    """A portable feedback contract violation."""


def canonical_json(value: Any) -> str:
    """Render deterministic JSON for storage and integrity checks."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    """Return the portable SHA-256 digest of canonical JSON."""
    return "sha256:" + hashlib.sha256(canonical_json(value).encode()).hexdigest()


def reject(message: str) -> None:
    """Raise a validation failure with a stable message."""
    raise FeedbackValidationError(message)


def require_string(value: Any, field: str) -> str:
    """Require one non-empty string field."""
    if not isinstance(value, str) or not value.strip():
        reject(f"{field} must be a non-empty string")
    return value


def reject_sensitive(value: Any, field: str = "observation") -> None:
    """Reject raw transcripts, secrets, and absolute host paths recursively."""
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


def validate_observation(value: Any) -> dict[str, Any]:
    """Validate and normalize one consumer observation."""
    if not isinstance(value, dict):
        reject("observation must be a JSON object")
    reject_sensitive(value)
    missing = [name for name in REQUIRED_FIELDS if name not in value]
    if missing:
        reject("missing required observation fields: " + ", ".join(missing))
    if value.get("schema_version", OBSERVATION_SCHEMA_VERSION) != OBSERVATION_SCHEMA_VERSION:
        reject("unsupported observation schema_version")
    component = value["component"]
    if not isinstance(component, dict):
        reject("component must be an object")
    for name in ("id", "version", "digest"):
        require_string(component.get(name), f"component.{name}")
    if not DIGEST.fullmatch(component["digest"]):
        reject("component.digest must be a SHA-256 digest")
    for name in REQUIRED_FIELDS:
        if name not in {"component", "execution_profile", "evidence_references"}:
            require_string(value[name], name)
    if not isinstance(value["execution_profile"], dict):
        reject("execution_profile must be an object")
    if not isinstance(value["evidence_references"], list) or not value["evidence_references"]:
        reject("evidence_references must be a non-empty list")
    if not all(isinstance(item, str) and item.strip() for item in value["evidence_references"]):
        reject("evidence_references must contain non-empty strings")
    if value["reporter_disposition"] not in DISPOSITIONS:
        reject("reporter_disposition is not recognized")
    normalized = dict(value)
    normalized["schema_version"] = OBSERVATION_SCHEMA_VERSION
    return normalized


def read_json(path: Path) -> Any:
    """Read one JSON input document."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        reject(f"input file does not exist: {path}")
    except json.JSONDecodeError as error:
        reject(f"input file is not valid JSON: {error.msg}")
    raise AssertionError("unreachable")


def read_journal(path: Path) -> list[dict[str, Any]]:
    """Read append-only evidence while rejecting corruption and duplicate IDs."""
    if not path.exists():
        reject(f"journal does not exist: {path}")
    observations: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            observation = validate_observation(json.loads(line))
        except json.JSONDecodeError as error:
            reject(f"journal line {line_number} is not valid JSON: {error.msg}")
        if observation["observation_id"] in seen:
            reject(f"journal contains duplicate observation_id: {observation['observation_id']}")
        seen.add(observation["observation_id"])
        observations.append(observation)
    if not observations:
        reject("journal contains no observations")
    return observations


def capture(input_path: Path, journal_path: Path) -> dict[str, Any]:
    """Append one validated observation without contacting a source authority."""
    observation = validate_observation(read_json(input_path))
    if journal_path.exists() and observation["observation_id"] in {item["observation_id"] for item in read_journal(journal_path)}:
        reject(f"duplicate observation_id: {observation['observation_id']}")
    journal_path.parent.mkdir(parents=True, exist_ok=True)
    with journal_path.open("a", encoding="utf-8") as journal:
        journal.write(canonical_json(observation) + "\n")
    return {"status": "captured", "observation_id": observation["observation_id"], "journal": str(journal_path)}


def markdown(report: dict[str, Any]) -> str:
    """Create a readable projection from the same object written as JSON."""
    lines = ["# Workflow Feedback Report", "", f"- **Report ID**: `{report['report_id']}`", f"- **Created**: {report['created_at']}", f"- **Producer**: {report['producer']}", f"- **Integrity**: `{report['integrity_digest']}`", ""]
    for observation in report["observations"]:
        component = observation["component"]
        lines.extend([f"## {observation['observation_id']}", "", f"- **Component**: `{component['id']}` {component['version']} (`{component['digest']}`)", f"- **Integration**: {observation['integration']}", f"- **Expected**: {observation['expected_behavior']}", f"- **Observed**: {observation['observed_behavior']}", f"- **Safety response**: {observation['safety_response']}", f"- **Manual fallback**: {observation['manual_fallback_status']}", f"- **Suggested target**: {observation['suggested_change_target']}", f"- **Reporter disposition**: {observation['reporter_disposition']}", "- **Evidence references**:"])
        lines.extend(f"  - `{reference}`" for reference in observation["evidence_references"])
        lines.append("")
    return "\n".join(lines)


def report(journal_path: Path, json_path: Path, markdown_path: Path, producer: str, created_at: str, report_id: str) -> dict[str, Any]:
    """Export a portable report and Markdown projection from local evidence."""
    result = {"schema_version": REPORT_SCHEMA_VERSION, "report_id": require_string(report_id, "report_id"), "producer": require_string(producer, "producer"), "created_at": require_string(created_at, "created_at"), "observations": read_journal(journal_path)}
    reject_sensitive(result)
    result["integrity_digest"] = digest(result)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(canonical_json(result) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown(result) + "\n", encoding="utf-8")
    return {"status": "exported", "report_id": result["report_id"], "integrity_digest": result["integrity_digest"]}


def main(argv: list[str] | None = None) -> int:
    """Run a capture or report action."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    capture_parser = commands.add_parser("capture")
    capture_parser.add_argument("--input", type=Path, required=True)
    capture_parser.add_argument("--journal", type=Path, default=Path(".specify/workflow-feedback/observations.jsonl"))
    report_parser = commands.add_parser("report")
    report_parser.add_argument("--journal", type=Path, required=True)
    report_parser.add_argument("--json", dest="json_path", type=Path, required=True)
    report_parser.add_argument("--markdown", type=Path, required=True)
    report_parser.add_argument("--producer", required=True)
    report_parser.add_argument("--created-at", required=True)
    report_parser.add_argument("--report-id", required=True)
    args = parser.parse_args(argv)
    try:
        output = capture(args.input, args.journal) if args.action == "capture" else report(args.journal, args.json_path, args.markdown, args.producer, args.created_at, args.report_id)
    except FeedbackValidationError as error:
        print(json.dumps({"status": "rejected", "reason": str(error)}, sort_keys=True))
        return 2
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

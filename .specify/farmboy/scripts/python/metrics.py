"""Local wall-clock timing records for observed FarmBoy agent turns."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import tomllib
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable


SCHEMA_VERSION = 1
MAX_INPUT_BYTES = 65_536
MAX_EXCEL_TEXT_LENGTH = 32_767
INVOCATION_KINDS = frozenset({"execution", "continuation", "retry", "probe"})
REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "invocation_id",
        "run_id",
        "step_id",
        "invocation_kind",
        "agent_name",
        "skill_id",
        "workflow_id",
        "project_label",
        "started_at",
        "finished_at",
        "duration_ms",
    }
)
OPTIONAL_FIELDS = frozenset({"model", "effort"})
RECORD_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS
METADATA_FIELDS = frozenset(
    {
        "run_id",
        "step_id",
        "invocation_kind",
        "agent_name",
        "skill_id",
        "workflow_id",
        "project_label",
    }
)
TIMESTAMP_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\Z")


def _is_xml_text(value: str) -> bool:
    """Return whether every code point is legal in XML 1.0 text."""
    return all(
        character in "\t\n\r"
        or 0x20 <= ord(character) <= 0xD7FF
        or 0xE000 <= ord(character) <= 0xFFFD
        or 0x10000 <= ord(character) <= 0x10FFFF
        for character in value
    )


def _validate_projected_string(value: Any, field: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value):
        raise ValueError(f"{field}-must-be-nonempty-string")
    if len(value) > MAX_EXCEL_TEXT_LENGTH:
        raise ValueError(f"{field}-exceeds-excel-cell-limit")
    if not _is_xml_text(value):
        raise ValueError(f"{field}-contains-illegal-xml-text")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as error:
        raise ValueError(f"{field}-is-not-valid-unicode") from error
    return value


def _timestamp_epoch_ms(value: Any, field: str) -> int:
    text = _validate_projected_string(value, field)
    if not TIMESTAMP_PATTERN.fullmatch(text):
        raise ValueError(f"{field}-timestamp-format-invalid")
    try:
        parsed = datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    except ValueError as error:
        raise ValueError(f"{field}-timestamp-invalid") from error
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    delta = parsed - epoch
    return delta.days * 86_400_000 + delta.seconds * 1_000 + delta.microseconds // 1_000


def validate_record(record: Any) -> dict[str, Any]:
    """Validate a metric object and return its stable fourteen-field projection."""
    if not isinstance(record, dict):
        raise ValueError("record-must-be-object")
    if not REQUIRED_FIELDS.issubset(record):
        raise ValueError("record-required-field-missing")
    version = record["schema_version"]
    if isinstance(version, bool) or not isinstance(version, int) or version != SCHEMA_VERSION:
        raise ValueError("schema-version-unsupported")
    for field in REQUIRED_FIELDS - {"schema_version", "duration_ms"}:
        _validate_projected_string(record[field], field)
    kind = _validate_projected_string(record["invocation_kind"], "invocation_kind")
    if kind not in INVOCATION_KINDS:
        raise ValueError("invocation-kind-unsupported")
    if kind == "probe" and record["step_id"] != "preflight":
        raise ValueError("probe-step-must-be-preflight")
    duration = record["duration_ms"]
    if isinstance(duration, bool) or not isinstance(duration, int):
        raise ValueError("duration-ms-must-be-integer")
    started_ms = _timestamp_epoch_ms(record["started_at"], "started_at")
    finished_ms = _timestamp_epoch_ms(record["finished_at"], "finished_at")
    if duration != finished_ms - started_ms:
        raise ValueError("duration-ms-does-not-match-timestamps")

    model = record.get("model")
    effort = record.get("effort")
    if model is not None:
        _validate_projected_string(model, "model")
    if effort is not None:
        _validate_projected_string(effort, "effort")

    projection = {field: record[field] for field in REQUIRED_FIELDS}
    projection["model"] = model
    projection["effort"] = effort
    # Stable public field ordering is useful to JSON consumers and test fixtures.
    return {field: projection[field] for field in (
        "schema_version", "invocation_id", "run_id", "step_id", "invocation_kind",
        "agent_name", "skill_id", "workflow_id", "project_label", "started_at",
        "finished_at", "duration_ms", "model", "effort",
    )}


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("json-duplicate-key")
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    raise ValueError("json-nonfinite-number")


def parse_record_json(raw: bytes | str) -> dict[str, Any]:
    """Parse bounded UTF-8 JSON and validate a version-1 metric record."""
    if isinstance(raw, str):
        try:
            encoded = raw.encode("utf-8")
        except UnicodeEncodeError as error:
            raise ValueError("json-input-not-valid-unicode") from error
    elif isinstance(raw, bytes):
        encoded = raw
    else:
        raise ValueError("json-input-must-be-bytes-or-string")
    if len(encoded) > MAX_INPUT_BYTES:
        raise ValueError("json-input-exceeds-limit")
    try:
        text = encoded.decode("utf-8")
        record = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        if isinstance(error, ValueError) and str(error).startswith("json-"):
            raise
        raise ValueError("json-input-invalid") from error
    return validate_record(record)


def _read_clock_ms(clock_ms: Callable[[], int] | int | None) -> int:
    value = int(time.time() * 1000) if clock_ms is None else (clock_ms() if callable(clock_ms) else clock_ms)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("clock-must-return-integer-milliseconds")
    return value


def _format_timestamp(epoch_ms: int) -> str:
    try:
        instant = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(milliseconds=epoch_ms)
    except (OverflowError, ValueError) as error:
        raise ValueError("clock-timestamp-out-of-range") from error
    return instant.strftime("%Y-%m-%dT%H:%M:%S.") + f"{instant.microsecond // 1000:03d}Z"


def _validate_metadata(metadata: Any) -> dict[str, Any]:
    if not isinstance(metadata, dict) or not METADATA_FIELDS.issubset(metadata):
        raise ValueError("invocation-metadata-invalid")
    if set(metadata) - METADATA_FIELDS - OPTIONAL_FIELDS:
        raise ValueError("invocation-metadata-field-unsupported")
    kind = _validate_projected_string(metadata["invocation_kind"], "invocation_kind")
    if kind not in INVOCATION_KINDS:
        raise ValueError("invocation-kind-unsupported")
    if kind == "probe" and metadata["step_id"] != "preflight":
        raise ValueError("probe-step-must-be-preflight")
    projected: dict[str, Any] = {}
    for field in METADATA_FIELDS:
        projected[field] = _validate_projected_string(metadata[field], field)
    for field in OPTIONAL_FIELDS:
        value = metadata.get(field)
        projected[field] = None if value is None else _validate_projected_string(value, field)
    return projected


def read_agent_settings(project_root: Path, agent_name: str) -> dict[str, str | None]:
    """Read only explicit model settings from the unique project agent TOML name match."""
    unavailable = {"model": None, "effort": None}
    if not isinstance(agent_name, str) or not agent_name:
        return unavailable
    agents_directory = project_root / ".codex" / "agents"
    try:
        if not agents_directory.is_dir():
            return unavailable
        files = sorted(agents_directory.glob("*.toml"))
        matches: list[dict[str, Any]] = []
        for path in files:
            if path.is_symlink() or not path.is_file():
                return unavailable
            try:
                with path.open("rb") as stream:
                    settings = tomllib.load(stream)
            except (OSError, UnicodeError, tomllib.TOMLDecodeError):
                # A malformed or unreadable file could contain a competing exact-name entry.
                return unavailable
            if isinstance(settings, dict) and settings.get("name") == agent_name:
                matches.append(settings)
    except OSError:
        return unavailable
    if len(matches) != 1:
        return unavailable

    settings = matches[0]
    model = settings.get("model")
    effort = settings.get("model_reasoning_effort")
    result: dict[str, str | None] = {}
    for output_name, value in (("model", model), ("effort", effort)):
        if isinstance(value, str) and value:
            try:
                result[output_name] = _validate_projected_string(value, output_name)
            except ValueError:
                result[output_name] = None
        else:
            result[output_name] = None
    return result


def begin_invocation(
    metadata: dict[str, Any], *, clock_ms: Callable[[], int] | int | None = None,
) -> dict[str, Any]:
    """Return a transient UUID and start-time token immediately before dispatch."""
    prepared = _validate_metadata(metadata)
    started_ms = _read_clock_ms(clock_ms)
    return {**prepared, "invocation_id": str(uuid.uuid4()), "started_ms": started_ms}


def emit_record(record: Any, *, directory: Path | None = None) -> dict[str, Any]:
    """Publish one complete record without replacing another invocation's file."""
    try:
        prepared = validate_record(record)
        invocation_id = prepared["invocation_id"]
        try:
            canonical_id = str(uuid.UUID(invocation_id))
        except (AttributeError, TypeError, ValueError) as error:
            raise ValueError("invocation-id-must-be-uuid-for-publication") from error
        if canonical_id != invocation_id:
            raise ValueError("invocation-id-must-be-canonical-uuid-for-publication")
        serialized = json.dumps(prepared, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
        if len(serialized) > MAX_INPUT_BYTES:
            raise ValueError("record-exceeds-publication-limit")
    except (TypeError, ValueError, UnicodeError):
        return {"emitted": False, "warning_code": "metadata-invalid"}

    try:
        metrics_directory = Path.home() / ".farmboy" / "metrics" if directory is None else Path(directory)
        metrics_directory.mkdir(parents=True, exist_ok=True)
        if metrics_directory.is_symlink() or not metrics_directory.is_dir():
            return {"emitted": False, "warning_code": "destination-unavailable"}
        final_path = metrics_directory / f"metric-{canonical_id}.json"
    except (OSError, RuntimeError, TypeError, ValueError):
        return {"emitted": False, "warning_code": "destination-unavailable"}

    try:
        temporary_path = metrics_directory / f".metric-{canonical_id}-{uuid.uuid4()}.tmp"
    except (OSError, RuntimeError, TypeError, ValueError):
        return {"emitted": False, "warning_code": "storage-failed"}
    descriptor: int | None = None
    temporary_created = False
    published = False
    cleanup_failed = False
    try:
        descriptor = os.open(temporary_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        temporary_created = True
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = None
            stream.write(serialized)
            stream.flush()
        try:
            os.link(temporary_path, final_path)
            published = True
        except FileExistsError:
            return {"emitted": False, "warning_code": "publication-collision"}
        except OSError:
            return {"emitted": False, "warning_code": "storage-failed"}
    except (OSError, TypeError, ValueError):
        return {"emitted": False, "warning_code": "storage-failed"}
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if temporary_created:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass
            except OSError:
                cleanup_failed = True

    if published:
        result = {"emitted": True}
        if cleanup_failed:
            result["warning_code"] = "storage-failed"
        return result
    return {"emitted": False, "warning_code": "storage-failed"}


def finish_invocation(
    token: dict[str, Any], *, clock_ms: Callable[[], int] | int | None = None,
    adapter: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Close one observed working turn and return its validated metric record."""
    finished_ms = _read_clock_ms(clock_ms)
    if not isinstance(token, dict) or set(token) != METADATA_FIELDS | OPTIONAL_FIELDS | {"invocation_id", "started_ms"}:
        raise ValueError("invocation-token-invalid")
    metadata = {field: token[field] for field in METADATA_FIELDS | OPTIONAL_FIELDS}
    prepared = _validate_metadata(metadata)
    invocation_id = _validate_projected_string(token["invocation_id"], "invocation_id")
    started_ms = token["started_ms"]
    if isinstance(started_ms, bool) or not isinstance(started_ms, int):
        raise ValueError("invocation-token-start-invalid")
    record = {
        "schema_version": SCHEMA_VERSION,
        **prepared,
        "invocation_id": invocation_id,
        "started_at": _format_timestamp(started_ms),
        "finished_at": _format_timestamp(finished_ms),
        "duration_ms": finished_ms - started_ms,
    }
    prepared = validate_record(record)
    (emit_record if adapter is None else adapter)(prepared)
    return prepared


def _read_json_object(stream: Any) -> dict[str, Any]:
    raw = stream.buffer.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError("json-input-exceeds-limit")
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        if isinstance(error, ValueError) and str(error).startswith("json-"):
            raise
        raise ValueError("json-input-invalid") from error
    if not isinstance(value, dict):
        raise ValueError("json-input-must-be-object")
    return value


def main(argv: list[str] | None = None) -> int:
    """Provide bounded JSON stdin/stdout commands for invocation boundaries."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("begin", "finish"))
    args = parser.parse_args(argv)
    try:
        payload = _read_json_object(sys.stdin)
        if args.command == "begin":
            result = begin_invocation(payload)
            sys.stdout.write(json.dumps(result, ensure_ascii=True, separators=(",", ":")) + "\n")
        else:
            adapter_result: dict[str, Any] = {"emitted": False, "warning_code": "helper-unavailable"}
            def publish(record: dict[str, Any]) -> dict[str, Any]:
                nonlocal adapter_result
                adapter_result = emit_record(record)
                return adapter_result
            finish_invocation(payload, adapter=publish)
            sys.stdout.write(json.dumps(adapter_result, ensure_ascii=True, separators=(",", ":")) + "\n")
        return 0
    except OSError:
        sys.stdout.write('{"emitted":false,"warning_code":"clock-unavailable"}\n')
        return 0
    except (TypeError, ValueError):
        sys.stdout.write('{"emitted":false,"warning_code":"metadata-invalid"}\n')
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

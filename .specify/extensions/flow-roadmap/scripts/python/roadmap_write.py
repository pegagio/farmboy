#!/usr/bin/env python3
"""Apply exact caller-authorized status amendments without consumer policy."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
from typing import Any

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("roadmap_write_loader", Path(__file__).with_name("load_config.py"))
if _spec is None or _spec.loader is None:
    raise RuntimeError("roadmap loader unavailable")
loader = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(loader)
ContractError = loader.ContractError
STATUSES = {"undecided", "needs-info", "planned", "specced", "in-progress", "implemented", "verified", "deferred", "abandoned"}
SHA = re.compile(r"^[0-9a-f]{64}$")
ENTRY = re.compile(r"^###\s+(\d+)\s+[—-]\s+.+?\s+\[status:\s*([^\]]+)\]\s*$", re.M)
FIELD = re.compile(r"^-\s+\*\*([^*]+?)(?::)?\*\*:?\s*(.*)$", re.M)
FOOTER = re.compile(r"\*\*Version\*\*:\s*(\d+)\.(\d+)\.(\d+)\s*\|\s*\*\*Ratified\*\*:\s*(\d{4}-\d{2}-\d{2})\s*\|\s*\*\*Last Amended\*\*:\s*\d{4}-\d{2}-\d{2}")
DELTA_FIELDS = {"roadmap_path", "entry_id", "feature_directory", "expected_roadmap_sha256",
                "from_status", "to_status", "authorization_reference", "evidence_paths"}

def byte_digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def strict_json(text: str) -> Any:
    """Reject ambiguous JSON before handling an authorized delta."""
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ContractError("duplicate JSON key")
            value[key] = item
        return value
    def invalid(_):
        raise ContractError("nonfinite JSON value")
    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)
    except (ValueError, TypeError) as error:
        raise ContractError("invalid JSON") from error

def relative(value: Any) -> str:
    if (not isinstance(value, str) or not value or value.startswith(("/", "~")) or "\\" in value
            or any(ord(char) < 32 for char in value) or ":" in value or "-->" in value
            or any(p in {"", ".", ".."} for p in value.split("/"))):
        raise ContractError("unsafe relative path")
    return value

def safe_path(project: Path, value: str, *, existing: bool = True) -> Path:
    """Validate every component without following symlinks."""
    path = project / relative(value)
    cursor = project
    for part in Path(value).parts:
        cursor /= part
        if cursor.is_symlink():
            raise ContractError("symlink path")
    loader.require_contained(path, project, "roadmap amendment path")
    if existing and not path.is_file():
        raise ContractError("source file missing")
    return path

def read_bytes(project: Path, value: str) -> bytes:
    path = safe_path(project, value)
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(descriptor, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ContractError("source must be a regular file")
        return stream.read()

def entries(text: str) -> dict[str, dict]:
    """Read unique entry blocks, mappings and dependency declarations."""
    found = list(ENTRY.finditer(text))
    if not found:
        raise ContractError("roadmap-ledger-missing")
    if len(found) != len(re.findall(r"^###\s+\d+\s+[—-]", text, re.M)):
        raise ContractError("malformed roadmap heading")
    result = {}
    mappings = set()
    for number, match in enumerate(found):
        entry_id = match[1]
        if entry_id in result:
            raise ContractError("duplicate-roadmap-id")
        end = found[number + 1].start() if number + 1 < len(found) else len(text)
        if match[2] not in STATUSES:
            raise ContractError("invalid roadmap status")
        block = text[match.end():end]
        fields = {}
        for field in FIELD.finditer(block):
            key = field[1].rstrip(":").lower()
            # Fields after the next top-level section are not entry fields.
            if re.search(r"^## ", block[:field.start()], re.M):
                break
            if key in fields:
                raise ContractError("duplicate-roadmap-field")
            fields[key] = field[2].strip()
        required = {"description", "outcome", "scope (in)"}
        if not required.issubset(fields) or any(not fields[key] for key in required):
            raise ContractError("required roadmap fields missing")
        mapping = fields.get("spec dir")
        if mapping is not None:
            mapping = mapping.strip().strip("`").rstrip("/")
            relative(mapping)
            if mapping in mappings:
                raise ContractError("duplicate specification mapping")
            mappings.add(mapping)
        declaration = fields.get("depends on", "").strip()
        clauses = [clause.strip() for clause in declaration.split(";")]
        clauses = [clause[:-1].rstrip() if clause.endswith(".") else clause for clause in clauses]
        positive = clauses[0]
        id_token = r"(?:\d{3}|`\d{3}`)(?:-brief)?"
        positive_list = (rf"{id_token}(?:\s+\([^()\d;]+\))?"
                         rf"(?:\s*,\s*{id_token}(?:\s+\([^()\d;]+\))?)*")
        negative_list = rf"no dependency on {id_token}(?:\s*,\s*{id_token})*"
        retired = re.fullmatch(r"~~(.*?)~~ _None — dependency edge retired with", positive)
        if positive.lower() in {"", "none"}:
            if len(clauses) > 1:
                raise ContractError("dependency-annotation-invalid")
            dependencies = []
        elif retired and re.fullmatch(positive_list, retired[1].rstrip(".").strip()):
            if len(clauses) > 1:
                raise ContractError("dependency-annotation-invalid")
            dependencies = []
        elif re.fullmatch(positive_list, positive):
            dependencies = re.findall(r"\d{3}", positive)
        else:
            raise ContractError("dependency-declaration-invalid")
        negatives = []
        for annotation in clauses[1:]:
            if not re.fullmatch(negative_list, annotation, re.I):
                raise ContractError("dependency-annotation-invalid")
            negatives.extend(re.findall(r"\d{3}", annotation))
        if len(set(negatives)) != len(negatives):
            raise ContractError("duplicate-dependency-annotation")
        if set(negatives) & set(dependencies):
            raise ContractError("dependency-declaration-contradicts")
        if len(set(dependencies)) != len(dependencies):
            raise ContractError("duplicate-dependency")
        result[entry_id] = {"id": entry_id, "status": match[2], "spec_dir": mapping,
                            "dependencies": dependencies, "start": match.start(), "heading_end": match.end(), "end": end}
    return result

def dependency_states(ledger: dict, selected: str) -> list[dict]:
    visiting, visited = set(), set()
    def walk(entry_id):
        if entry_id in visiting:
            raise ContractError("dependency-cycle")
        if entry_id in visited:
            return
        visiting.add(entry_id)
        for dep in ledger[entry_id]["dependencies"]:
            if dep not in ledger:
                raise ContractError("dependency-missing")
            walk(dep)
        visiting.remove(entry_id)
        visited.add(entry_id)
    walk(selected)
    return [{"entry_id": dep, "status": ledger[dep]["status"]} for dep in sorted(visited - {selected})]

def validate_delta(value: Any) -> dict:
    """Validate structure; a document never establishes caller authority."""
    if not isinstance(value, dict) or set(value) != DELTA_FIELDS:
        raise ContractError("invalid status delta fields")
    for key in ("roadmap_path", "feature_directory"):
        relative(value[key])
    if not isinstance(value["entry_id"], str) or not re.fullmatch(r"\d{3,}", value["entry_id"]):
        raise ContractError("invalid entry identity")
    for key in ("from_status", "to_status"):
        if not isinstance(value[key], str) or value[key] not in STATUSES:
            raise ContractError("invalid lifecycle status")
    if not isinstance(value["expected_roadmap_sha256"], str) or not SHA.fullmatch(value["expected_roadmap_sha256"]):
        raise ContractError("invalid preimage digest")
    authority = value["authorization_reference"]
    if (not isinstance(authority, str) or not authority.strip() or "--" in authority
            or any(ord(char) < 32 for char in authority)):
        raise ContractError("invalid authorization reference")
    evidence = value["evidence_paths"]
    if not isinstance(evidence, list) or any(not isinstance(item, str) for item in evidence):
        raise ContractError("invalid evidence paths")
    if len(evidence) != len(set(evidence)):
        raise ContractError("duplicate evidence path")
    for path in evidence:
        relative(path)
        if "--" in path:
            raise ContractError("invalid report evidence path")
    return value

def _prepare(project: Path, delta: dict, yaml: Any) -> tuple[Path, bytes, bytes, dict]:
    validate_delta(delta)
    payload = Path(__file__).resolve().parents[2]
    configuration = loader.resolve_configuration(project, payload, yaml)
    configured = Path(configuration["roadmap_path"])
    if not configured.is_absolute():
        configured = project / configured
    path = safe_path(project, delta["roadmap_path"])
    if path != configured:
        raise ContractError("delta must name the configured roadmap path")
    raw = read_bytes(project, delta["roadmap_path"])
    before = byte_digest(raw)
    if before != delta["expected_roadmap_sha256"]:
        raise ContractError("roadmap preimage changed")
    for evidence in delta["evidence_paths"]:
        read_bytes(project, evidence)
    try:
        text = raw.decode("utf-8")
    except UnicodeError as error:
        raise ContractError("roadmap must be UTF-8") from error
    ledger = entries(text)
    for entry_id in ledger:
        dependency_states(ledger, entry_id)
    item = ledger.get(delta["entry_id"])
    if item is None or item["spec_dir"] != delta["feature_directory"]:
        raise ContractError("entry identity or specification mapping mismatch")
    footers = list(FOOTER.finditer(text))
    if len(footers) != 1:
        raise ContractError("roadmap version footer invalid")
    footer = footers[0]
    for date in (footer[4], footer[0].rsplit(":", 1)[-1].strip()):
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError as error:
            raise ContractError("roadmap footer date invalid") from error
    result = {"state": "no-op", "entry_id": delta["entry_id"], "from_status": delta["from_status"],
              "to_status": delta["to_status"], "roadmap_before_sha256": before, "roadmap_after_sha256": before}
    if item["status"] == delta["to_status"]:
        return path, raw, raw, result
    if item["status"] != delta["from_status"]:
        raise ContractError("entry status preimage mismatch")
    heading = text[item["start"]:item["heading_end"]]
    replacement = heading.replace(f"[status: {delta['from_status']}]", f"[status: {delta['to_status']}]", 1)
    if replacement == heading:
        raise ContractError("status heading must use the canonical status marker")
    patched = text[:item["start"]] + replacement + text[item["heading_end"]:]
    old_version = ".".join(footer.group(i) for i in (1, 2, 3))
    new_version = f"{footer[1]}.{footer[2]}.{int(footer[3]) + 1}"
    date = datetime.now(timezone.utc).date().isoformat()
    new_footer = f"**Version**: {new_version} | **Ratified**: {footer[4]} | **Last Amended**: {date}"
    # Footer offsets follow the heading, whose status length may change.
    patched = FOOTER.sub(lambda _: new_footer, patched, count=1)
    impact = (f"<!--\nSYNC IMPACT REPORT\n==================\nVersion change: {old_version} → {new_version}\n"
              f"Bump rationale: PATCH — authorized status amendment for entry {delta['entry_id']}.\n"
              f"Status: {delta['from_status']} → {delta['to_status']}\n"
              f"Authorization: {delta['authorization_reference']}\n"
              f"Evidence paths: {json.dumps(delta['evidence_paths'], ensure_ascii=False)}\n-->\n")
    candidate = (impact + patched).encode("utf-8")
    return path, raw, candidate, {**result, "state": "ready", "roadmap_after_sha256": byte_digest(candidate),
                                  "version": new_version, "amendment_date": date}

def preview(project: Path, delta: dict, yaml: Any = None) -> dict:
    """Return a read-only exact status amendment assessment."""
    if yaml is None:
        import yaml
    return _prepare(project, delta, yaml)[3]

def _atomic(path: Path, raw: bytes, expected: bytes) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix=".roadmap-amend-", dir=path.parent)
    try:
        os.fchmod(descriptor, stat.S_IMODE(path.stat().st_mode))
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        # Revalidate containment, exact bytes and file type immediately before replacement.
        if any(parent.is_symlink() for parent in path.parents):
            raise ContractError("roadmap parent changed to a symlink")
        current = read_bytes(path.parent, path.name)
        if current != expected:
            raise ContractError("roadmap preimage changed immediately before mutation")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def apply(project: Path, delta: dict, yaml: Any = None) -> dict:
    """Apply one already-authorized amendment; callers own policy and receipts."""
    if yaml is None:
        import yaml
    validate_delta(delta)
    roadmap = safe_path(project, delta["roadmap_path"])
    lock = roadmap.with_name(roadmap.name + ".lock")
    safe_path(project, lock.relative_to(project).as_posix(), existing=False)
    descriptor = os.open(lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "r+b") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ContractError("roadmap lock must be a regular file")
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        path, before, candidate, result = _prepare(project, delta, yaml)
        if result["state"] == "no-op":
            return result
        _atomic(path, candidate, before)
        try:
            if read_bytes(project, delta["roadmap_path"]) != candidate:
                raise ContractError("readback mismatch")
        except BaseException as error:
            raise ContractError("amendment readback failed; inspect current roadmap before retry") from error
        return {**result, "state": "applied"}

def main() -> int:
    """Run through the existing isolated Specify runtime and bounded JSON boundary."""
    try:
        yaml = loader.establish_runtime(Path(__file__))
        parser = argparse.ArgumentParser()
        parser.add_argument("operation", choices=("preview", "apply"))
        parser.add_argument("--project", type=Path)
        arguments = parser.parse_args()
        discovered, _ = loader.discover_roots(Path(__file__))
        project = (arguments.project or discovered).resolve(strict=True)
        delta = strict_json(sys.stdin.read())
        result = (apply if arguments.operation == "apply" else preview)(project, delta, yaml)
        sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
        return 0
    except Exception as error:
        message = str(error) if isinstance(error, ContractError) else "unexpected amendment failure; inspect current roadmap before retry"
        sys.stderr.write("Error: " + json.dumps(message)[1:-1] + "\n")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

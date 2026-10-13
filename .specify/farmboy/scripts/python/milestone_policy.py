#!/usr/bin/env python3
"""Read-only FarmBoy policy transferred from the dirty roadmap 86b0cc7 snapshot.

FarmBoy owns phase, role, evidence and delivered-route checks. The independent
roadmap extension supplies only generic configuration and ledger amendments.
"""
from __future__ import annotations
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any

sys.dont_write_bytecode = True
class ContractError(ValueError):
    """Current workflow lifecycle evidence is invalid or unavailable."""


def roadmap_configuration(project: Path, yaml: Any) -> dict:
    """Use only the roadmap extension's generic contained configuration API."""
    project = project.resolve()
    prefix = payload_prefix(project)
    script = safe_path(project, prefix + "scripts/python/load_config.py")
    before = byte_digest(read_bytes(project, prefix + "scripts/python/load_config.py"))
    spec = importlib.util.spec_from_file_location("farmboy_generic_roadmap_configuration", script)
    if spec is None or spec.loader is None:
        raise ContractError("roadmap-configuration-unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        config = module.resolve_configuration(project, project / prefix, yaml)
    except module.ContractError as error:
        raise ContractError("roadmap-configuration-invalid") from error
    if before != byte_digest(read_bytes(project, prefix + "scripts/python/load_config.py")):
        raise ContractError("roadmap-configuration-source-changed")
    return config


def load_yaml(text: str | None, label: str, yaml: Any) -> Any:
    """Parse one YAML document while rejecting duplicate keys, aliases, and merges."""
    if text is None:
        return None

    class StrictSafeLoader(yaml.SafeLoader):
        def compose_node(self, parent: Any, index: Any) -> Any:
            if self.check_event(yaml.events.AliasEvent):
                raise ContractError(f"{label} must not contain YAML aliases")
            return super().compose_node(parent, index)

        def construct_mapping(self, node: Any, deep: bool = False) -> dict[Any, Any]:
            if not isinstance(node, yaml.nodes.MappingNode):
                raise ContractError(f"{label} contains an invalid mapping")
            mapping: dict[Any, Any] = {}
            for key_node, value_node in node.value:
                if key_node.tag == "tag:yaml.org,2002:merge" or key_node.value == "<<":
                    raise ContractError(f"{label} must not contain YAML merge keys")
                key = self.construct_object(key_node, deep=deep)
                try:
                    duplicate = key in mapping
                except TypeError as error:
                    raise ContractError(f"{label} contains an invalid mapping key") from error
                if duplicate:
                    raise ContractError(f"{label} contains duplicate key {key!r}")
                mapping[key] = self.construct_object(value_node, deep=deep)
            return mapping

    StrictSafeLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        StrictSafeLoader.construct_mapping,
    )
    try:
        documents = list(yaml.load_all(text, Loader=StrictSafeLoader))
    except ContractError:
        raise
    except yaml.YAMLError as error:
        mark = getattr(error, "problem_mark", None)
        location = f" at line {mark.line + 1}, column {mark.column + 1}" if mark else ""
        raise ContractError(f"{label} contains invalid YAML{location}") from error
    if not documents:
        return None
    if len(documents) != 1:
        raise ContractError(f"{label} must contain exactly one YAML document")
    return documents[0]


VERSION = "1.0"
POLICY_SHA256 = "09738d2d65ab12117308d586f77a2140a1cedebbad9d9bc33f0408fb822f1bd4"
SHA = re.compile(r"^[0-9a-f]{64}$")
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,95}$")
STATUSES = ("planned", "specced", "in-progress", "implemented", "verified")
PHASES = {"specify": "specced", "implement": "in-progress", "closeout": "implemented"}
OWNERS = {value: key for key, value in PHASES.items()}
CHECKS = {
    "specced": {"authoring-quality", "clarification", "independent-review", "roadmap-brief", "linkage", "dependencies", "consequential-decisions"},
    "in-progress": {"current-artifacts", "dependencies", "readiness", "eligible-scope", "native-assignments"},
    "implemented": {"full-scope-completion", "attributable-delta", "convergence", "independent-code-review", "validation", "no-buildable-defects", "future-obligations-separated"},
}
ROLES = {"specced": {"FarmBoy Reviewer", "FarmBoy Roadmap Agent"},
         "in-progress": {"FarmBoy Reviewer", "FarmBoy Readiness Checker"},
         "implemented": {"FarmBoy Code Reviewer"}}
SNAPSHOT_FIELDS = {"schema_version", "feature_directory", "entry_id", "phase", "workflow_id", "workflow_version", "run_id",
                   "current_status", "source_map", "dependency_states", "scope_sha256", "pending_future_ids"}
REQUEST_FIELDS = {"schema_version", "action", "phase", "feature_directory", "entry_id", "run_id", "workflow_id",
                  "workflow_version", "mode", "decision_reference", "milestone_evidence", "snapshot"}
PROPOSAL_FIELDS = {"schema_version", "snapshot", "milestone_evidence", "decision", "from_status", "to_status",
                   "expected_roadmap_sha256", "patch_sha256", "effect_id", "recovery"}
EVIDENCE_FIELDS = {"milestone", "owning_phase", "assessments", "required_check_ids", "satisfied_check_ids",
                   "unresolved_ids", "artifact_digests", "historical_activity", "pending_future_ids"}
ASSESSMENT_FIELDS = {"schema_version", "kind", "reviewer", "state", "feature_directory", "scope_sha256",
                     "artifact_digests", "required_check_ids", "satisfied_check_ids", "unresolved_ids"}
ENTRY = re.compile(r"^###\s+(\d+)\s+[—-]\s+.+?\s+\[status:\s*([^\]]+)\]\s*$", re.M)
FIELD = re.compile(r"^-\s+\*\*([^*]+?)(?::)?\*\*:?\s*(.*)$", re.M)
EVENT = re.compile(r"<!-- flow-roadmap-lifecycle (.+?) -->")
FOOTER = re.compile(r"\*\*Version\*\*:\s*(\d+)\.(\d+)\.(\d+)\s*\|\s*\*\*Ratified\*\*:\s*(\d{4}-\d{2}-\d{2})\s*\|\s*\*\*Last Amended\*\*:\s*\d{4}-\d{2}-\d{2}")

def digest(value: Any) -> str:
    """Hash canonical structured bytes, independently of key order."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def byte_digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()

def _reject_nulls(value: Any) -> None:
    if value is None:
        raise ContractError("null-value-invalid")
    if isinstance(value, dict):
        for item in value.values():
            _reject_nulls(item)
    elif isinstance(value, list):
        for item in value:
            _reject_nulls(item)

def exact(value: Any, fields: set[str], label: str) -> dict:
    _reject_nulls(value)
    if not isinstance(value, dict) or set(value) != fields:
        raise ContractError(f"{label}-schema-invalid")
    return value

def identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not ID.fullmatch(value) or value in {".", ".."}:
        raise ContractError(f"{label}-invalid")
    return value

def hash_value(value: Any) -> str:
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ContractError("digest-invalid")
    return value

def strings(value: Any, label: str, *, nonempty: bool = False) -> list[str]:
    if (not isinstance(value, list) or (nonempty and not value)
            or any(not isinstance(x, str) or not x.strip() for x in value) or len(set(value)) != len(value)):
        raise ContractError(f"{label}-invalid")
    return value

def strict_json(text: str) -> Any:
    """Reject duplicate keys and nonfinite values at the wire boundary."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ContractError("duplicate-json-key")
            result[key] = value
        return result
    def invalid(_):
        raise ContractError("nonfinite-json-value")
    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)
    except (ValueError, TypeError) as error:
        raise ContractError("invalid-json") from error

def relative(value: Any) -> str:
    if (not isinstance(value, str) or not value or value.startswith(("/", "~")) or "\\" in value
            or any(ord(char) < 32 for char in value) or ":" in value or any(p in {"", ".", ".."} for p in value.split("/"))):
        raise ContractError("unsafe-relative-path")
    return value

def safe_path(project: Path, value: str, *, existing: bool = True) -> Path:
    path = project / relative(value)
    cursor = project
    for part in Path(value).parts:
        cursor /= part
        if cursor.is_symlink():
            raise ContractError("symlink-path")
    if not path.resolve().is_relative_to(project.resolve()):
        raise ContractError("unsafe-relative-path")
    if existing and not path.is_file():
        raise ContractError("source-file-missing")
    return path

def read_bytes(project: Path, value: str) -> bytes:
    path = safe_path(project, value)
    with path.open("rb") as stream:
        return stream.read()

def read_json(project: Path, value: str) -> Any:
    try:
        return strict_json(read_bytes(project, value).decode("utf-8"))
    except UnicodeError as error:
        raise ContractError("source-not-utf8") from error

def source_map(project: Path, values: Any) -> dict[str, str]:
    if not isinstance(values, dict) or not values:
        raise ContractError("source-map-invalid")
    return {relative(path): byte_digest(read_bytes(project, path)) for path in values}

def validate_sources(project: Path, values: Any) -> dict[str, str]:
    observed = source_map(project, values)
    if any(hash_value(value) != observed[path] for path, value in values.items()):
        raise ContractError("stale-source-evidence")
    return observed

def evidence(project: Path, references: Any) -> list[dict]:
    if not isinstance(references, list) or not references:
        raise ContractError("evidence-missing")
    seen = set()
    for ref in references:
        exact(ref, {"path", "sha256", "kind"}, "evidence")
        path = relative(ref["path"])
        if path in seen or not isinstance(ref["kind"], str) or not ref["kind"]:
            raise ContractError("evidence-invalid")
        seen.add(path)
        if byte_digest(read_bytes(project, path)) != hash_value(ref["sha256"]):
            raise ContractError("stale-assessment-evidence")
    return references

def entries(text: str) -> dict[str, dict]:
    """Read unique entry blocks, mappings and dependency declarations."""
    found = list(ENTRY.finditer(text))
    if not found:
        raise ContractError("roadmap-ledger-missing")
    result = {}
    for number, match in enumerate(found):
        entry_id = match[1]
        if entry_id in result:
            raise ContractError("duplicate-roadmap-id")
        end = found[number + 1].start() if number + 1 < len(found) else len(text)
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
        mapping = fields.get("spec dir")
        if mapping is not None:
            mapping = mapping.strip().strip("`").rstrip("/")
            relative(mapping)
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

def payload_prefix(project: Path) -> str:
    prefix = ".specify/extensions/flow-roadmap/"
    if not (project / prefix / "extension.yml").is_file():
        raise ContractError("lifecycle-owner-contract-unavailable")
    return prefix

def pending_ids(project: Path, feature: str) -> list[str]:
    path = f"{feature}/validation/future-obligations.json"
    if not (project / path).exists():
        return []
    record = read_json(project, path)
    if (not isinstance(record, dict) or record.get("schema_version") != VERSION
            or record.get("feature_directory") != feature or not isinstance(record.get("obligations"), list)):
        raise ContractError("future-obligations-invalid")
    result = []
    for item in record["obligations"]:
        if not isinstance(item, dict) or item.get("status") != "pending":
            raise ContractError("future-obligations-invalid")
        result.append(identifier(item.get("id"), "future-obligation"))
    strings(result, "future-obligations")
    return sorted(result)

def collect_snapshot(project: Path, request: dict, yaml: Any) -> dict:
    """Collect current bytes rather than accepting the supplied snapshot as fact."""
    supplied = exact(request["snapshot"], SNAPSHOT_FIELDS, "snapshot")
    feature = relative(request["feature_directory"])
    if not feature.startswith("specs/"):
        raise ContractError("feature-directory-invalid")
    prefix = payload_prefix(project)
    payload = project / prefix
    config = roadmap_configuration(project, yaml)
    roadmap = relative(config["roadmap_path"])
    raw = read_bytes(project, roadmap)
    ledger = entries(raw.decode("utf-8"))
    selected = request["entry_id"]
    if selected not in ledger:
        raise ContractError("roadmap-entry-missing")
    selected_path = safe_path(project, feature + "/spec.md")
    selected_stat = selected_path.stat()
    mapped = []
    for item in ledger.values():
        if item["spec_dir"] is None:
            continue
        candidate_path = safe_path(project, item["spec_dir"] + "/spec.md", existing=False)
        if candidate_path.exists():
            observed = candidate_path.stat()
            if (observed.st_dev, observed.st_ino) == (selected_stat.st_dev, selected_stat.st_ino):
                mapped.append(item)
    if len(mapped) != 1 or mapped[0]["id"] != selected:
        raise ContractError("roadmap-mapping-not-unique")
    pointer = read_json(project, ".specify/feature.json")
    if not isinstance(pointer, dict) or pointer.get("feature_directory") != feature:
        raise ContractError("active-feature-mismatch")
    manifest = load_yaml(read_bytes(project, prefix + "extension.yml").decode(), "owner manifest", yaml)
    if manifest.get("extension", {}).get("id") != "flow-roadmap":
        raise ContractError("owner-identity-invalid")
    version = manifest.get("extension", {}).get("version", "")
    if (not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version)
            or tuple(map(int, version.split("."))) < (0, 4, 0)):
        raise ContractError("generic-roadmap-contract-unavailable")
    commands = {item.get("name") for item in manifest.get("provides", {}).get("commands", []) if isinstance(item, dict)}
    if not {"speckit.flow-roadmap.write", "speckit.flow-roadmap.brief"}.issubset(commands):
        raise ContractError("lifecycle-owner-contract-unavailable")
    required = {roadmap, ".specify/feature.json", ".specify/memory/constitution.md",
                f"{feature}/spec.md", request["decision_reference"], prefix + "extension.yml",
                prefix + "scripts/python/load_config.py", prefix + "scripts/python/review_contract.py",
                prefix + "scripts/python/roadmap_write.py",
                ".specify/farmboy/scripts/python/milestone_policy.py",
                ".specify/farmboy/scripts/python/phase_lifecycle.py"}
    for group in request["milestone_evidence"]:
        refs = group["assessments"]
        history = group["historical_activity"]
        evidence(project, refs)
        if history:
            evidence(project, history)
        required.update(validate_sources(project, group["artifact_digests"]))
        for ref in refs:
            record = exact(read_json(project, ref["path"]), ASSESSMENT_FIELDS, "assessment")
            required.update(validate_sources(project, record["artifact_digests"]))
        for ref in refs + history:
            required.add(relative(ref["path"]))
    if request["phase"] != "specify" or ledger[selected]["status"] in {"in-progress", "implemented", "verified"}:
        required |= {f"{feature}/plan.md", f"{feature}/tasks.md"}
    quality = f"{feature}/checklists/requirements.md"
    if (project / quality).exists():
        required.add(quality)
    for path in (".specify/extensions/flow-roadmap/roadmap-config.yml", f"{feature}/validation/future-obligations.json"):
        if (project / path).exists():
            required.add(path)
    graph = f".specify/workflows/{request['workflow_id']}/workflow.yml"
    manual = f"{feature}/validation/manual-route.json"
    if (project / graph).exists():
        required |= {graph, ".specify/farmboy/manifest.yml", ".specify/farmboy/skills-install.json", ".specify/bundle-records.json"}
        definition = load_yaml(read_bytes(project, graph).decode(), "workflow", yaml)
        graph_version = definition.get("workflow", {}).get("version")
        if graph_version != request["workflow_version"]:
            raise ContractError("workflow-version-mismatch")
        minimum = {"specify": (0, 4, 0), "implement": (0, 9, 0), "closeout": (0, 9, 0)}[request["phase"]]
        if not isinstance(graph_version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", graph_version) or tuple(map(int, graph_version.split("."))) < minimum:
            raise ContractError("lifecycle-workflow-contract-unavailable")
        controllers = load_yaml(read_bytes(project, ".specify/farmboy/manifest.yml").decode(), "controller manifest", yaml)
        controller_version = controllers.get("package", {}).get("version", "")
        if not isinstance(controller_version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", controller_version) or tuple(map(int, controller_version.split("."))) < (0, 9, 0):
            raise ContractError("lifecycle-controller-contract-unavailable")
        def has_owner_route(nodes):
            for node in nodes if isinstance(nodes, list) else []:
                if not isinstance(node, dict):
                    continue
                metadata = node.get("farmboy", {})
                if (node.get("type") == "command" and node.get("command") == "speckit.flow-roadmap.write"
                        and metadata.get("delegated") is True and metadata.get("agent") == "FarmBoy Roadmap Agent"
                        and "roadmap_delta" in node.get("input", {}).get("args", "")):
                    return True
                branches = [node.get("steps", []), node.get("default", []), *node.get("cases", {}).values()]
                if any(has_owner_route(branch) for branch in branches):
                    return True
            return False
        if not has_owner_route(definition.get("steps", [])):
            raise ContractError("lifecycle-owner-route-unavailable")
    elif (project / manual).exists():
        route = read_json(project, manual)
        exact(route, {"schema_version", "phase", "workflow_id", "workflow_version", "run_id",
                      "feature_directory", "commands", "native_assignments", "source_evidence"}, "manual-route")
        if any(route[field] != request[field] for field in ("phase", "workflow_id", "workflow_version", "run_id", "feature_directory")) or route["schema_version"] != VERSION:
            raise ContractError("manual-route-mismatch")
        strings(route["commands"], "manual-commands", nonempty=True)
        strings(route["native_assignments"], "manual-assignments", nonempty=True)
        evidence(project, route["source_evidence"])
        required.add(manual)
    else:
        raise ContractError("lifecycle-owner-contract-unavailable")
    if not isinstance(supplied["source_map"], dict) or not required.issubset(supplied["source_map"]):
        raise ContractError("required-source-coverage-missing")
    actual_map = {relative(path): byte_digest(read_bytes(project, path)) for path in set(supplied["source_map"]) | required}
    return {"schema_version": VERSION, "feature_directory": feature, "entry_id": selected,
            "phase": request["phase"], "workflow_id": request["workflow_id"], "workflow_version": request["workflow_version"],
            "run_id": request["run_id"], "current_status": ledger[selected]["status"], "source_map": actual_map,
            "dependency_states": dependency_states(ledger, selected), "scope_sha256": byte_digest(read_bytes(project, f"{feature}/spec.md")),
            "pending_future_ids": pending_ids(project, feature)}

def validate_assessment(project: Path, ref: dict, snapshot: dict, allowed_roles: set[str]) -> dict:
    record = exact(read_json(project, ref["path"]), ASSESSMENT_FIELDS, "assessment")
    if (record["schema_version"] != VERSION or record["kind"] != ref["kind"]
            or record["reviewer"] not in allowed_roles or record["state"] not in {"ready", "complete"}
            or record["feature_directory"] != snapshot["feature_directory"] or record["scope_sha256"] != snapshot["scope_sha256"]):
        raise ContractError("independent-assessment-invalid")
    required = strings(record["required_check_ids"], "assessment-checks", nonempty=True)
    satisfied = strings(record["satisfied_check_ids"], "assessment-checks", nonempty=True)
    if set(required) != set(satisfied) or strings(record["unresolved_ids"], "assessment-unresolved"):
        raise ContractError("independent-assessment-incomplete")
    artifacts = validate_sources(project, record["artifact_digests"])
    if artifacts.get(f"{snapshot['feature_directory']}/spec.md") != snapshot["scope_sha256"]:
        raise ContractError("assessment-scope-input-missing")
    return record

def occurrence(value: Any) -> str:
    if not isinstance(value, str) or "T" not in value:
        raise ContractError("occurrence-time-invalid")
    try:
        observed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ContractError("occurrence-time-invalid") from error
    if observed.tzinfo is None or observed.utcoffset() is None:
        raise ContractError("occurrence-time-invalid")
    return value

def validate_milestone(project: Path, groups: list, target: str, snapshot: dict, *, recovery: bool) -> dict:
    selected = [group for group in groups if group.get("milestone") == target]
    if len(selected) != 1:
        raise ContractError("milestone-proof-missing")
    group = exact(selected[0], EVIDENCE_FIELDS, "milestone-evidence")
    if group["owning_phase"] != OWNERS[target]:
        raise ContractError("milestone-owner-mismatch")
    required = strings(group["required_check_ids"], "milestone-checks", nonempty=True)
    satisfied = strings(group["satisfied_check_ids"], "milestone-checks", nonempty=True)
    if set(required) != CHECKS[target] or set(satisfied) != CHECKS[target] or strings(group["unresolved_ids"], "milestone-unresolved"):
        raise ContractError("milestone-proof-incomplete")
    artifacts = validate_sources(project, group["artifact_digests"])
    feature = snapshot["feature_directory"]
    must = {f"{feature}/spec.md"}
    if target != "specced":
        must |= {f"{feature}/plan.md", f"{feature}/tasks.md"}
    if not must.issubset(artifacts) or artifacts[f"{feature}/spec.md"] != snapshot["scope_sha256"]:
        raise ContractError("milestone-current-artifacts-missing")
    refs = evidence(project, group["assessments"])
    seen_roles, checks = set(), set()
    independent_inputs = {}
    for ref in refs:
        record = validate_assessment(project, ref, snapshot, ROLES[target])
        seen_roles.add(record["reviewer"])
        independent_inputs.setdefault(record["reviewer"], set()).update(record["artifact_digests"])
        checks.update(record["satisfied_check_ids"])
    if not ROLES[target].issubset(seen_roles) or not CHECKS[target].issubset(checks):
        raise ContractError("milestone-independent-coverage-incomplete")
    scope_reviewer = "FarmBoy Code Reviewer" if target == "implemented" else "FarmBoy Reviewer"
    if not must.issubset(independent_inputs.get(scope_reviewer, set())):
        raise ContractError("independent-reviewed-input-coverage-missing")

    if sorted(strings(group["pending_future_ids"], "pending-future-ids")) != snapshot["pending_future_ids"]:
        raise ContractError("future-obligations-mismatch")
    history = group["historical_activity"]
    if not isinstance(history, list):
        raise ContractError("historical-activity-invalid")
    if recovery and target == "in-progress":
        evidence(project, history)
        for ref in history:
            record = read_json(project, ref["path"])
            if (not isinstance(record, dict) or record.get("kind") != "authorized-implementation-start"
                    or record.get("scope_sha256") != snapshot["scope_sha256"]):
                raise ContractError("historical-start-unsubstantiated")
            occurrence(record.get("occurred_at"))
    elif history:
        evidence(project, history)
    return group

def validate_request(request: dict) -> None:
    action = request.get("action") if isinstance(request, dict) else None
    exact(request, REQUEST_FIELDS | ({"proposal"} if action == "revalidate" else set()), "request")
    if request["schema_version"] != VERSION or action not in {"prepare", "revalidate"}:
        raise ContractError("request-version-or-action-invalid")
    if request["phase"] not in PHASES or request["mode"] not in {"normal", "recovery"}:
        raise ContractError("phase-or-mode-invalid")
    for key in ("entry_id", "run_id", "workflow_id", "workflow_version"):
        identifier(request[key], key)
    relative(request["feature_directory"])
    relative(request["decision_reference"])
    if not isinstance(request["milestone_evidence"], list):
        raise ContractError("milestone-evidence-invalid")
    for group in request["milestone_evidence"]:
        exact(group, EVIDENCE_FIELDS, "milestone-evidence")
        if group["milestone"] not in CHECKS:
            raise ContractError("milestone-invalid")
    if len({g["milestone"] for g in request["milestone_evidence"]}) != len(request["milestone_evidence"]):
        raise ContractError("duplicate-milestone-evidence")

def blocked(reason: str, snapshot: dict | None = None) -> dict:
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", reason):
        reason = "lifecycle-source-validation-failed"
    result = {"state": "blocked", "reason_code": reason, "evidence": [], "blocking_ids": [reason],
              "resume_action": "supply-current-lifecycle-evidence"}
    if snapshot is not None:
        result["snapshot"] = snapshot
    return result

def _operations(proposal: dict) -> dict:
    operations = {key: value for key, value in proposal.items() if key != "patch_sha256"}
    operations["recovery"] = {key: value for key, value in proposal["recovery"].items() if key != "verification"}
    return operations

def evaluate(project: Path, request: dict, yaml: Any) -> dict:
    """Prepare exactly one edge or a truthful event-free assessment."""
    validate_request(request)
    try:
        snapshot = collect_snapshot(project, request, yaml)
        if snapshot != request["snapshot"]:
            raise ContractError("stale-source-snapshot")
        if any(dep["status"] != "verified" for dep in snapshot["dependency_states"]):
            raise ContractError("dependencies-not-verified")
        decision = read_json(project, request["decision_reference"])
        exact(decision, {"schema_version", "policy_sha256", "feature_directory", "phase", "scope_sha256", "kind", "reference"}, "decision")
        if (decision["schema_version"] != VERSION or decision["policy_sha256"] != POLICY_SHA256
                or any(decision[field] != snapshot[field] for field in ("feature_directory", "phase", "scope_sha256"))
                or decision["kind"] not in {"routine-invocation", "operator-resolution"}
                or not isinstance(decision["reference"], str) or not decision["reference"]):
            raise ContractError("governing-contract-mismatch")
        current = snapshot["current_status"]
        ceiling = PHASES[request["phase"]]
        if current not in STATUSES:
            return {"state": "question", "reason_code": "lifecycle-state-conflict", "snapshot": snapshot,
                    "evidence": [], "blocking_ids": ["lifecycle-state-conflict"],
                    "request": {"kind": "question", "step_id": "resolve-phase-lifecycle-conflict",
                    "question": "Resolve the current lifecycle state before an adjacent milestone effect.",
                    "options": ["Keep state and stop", "Provide an explicit reconciliation instruction"], "allow_custom_answer": True}}
        ci, ti = STATUSES.index(current), STATUSES.index(ceiling)
        if ci >= ti:
            target = current if current != "verified" else "implemented"
            group = validate_milestone(project, request["milestone_evidence"], ceiling, snapshot, recovery=False)
            if target != ceiling:
                validate_milestone(project, request["milestone_evidence"], target, snapshot, recovery=False)
            return {"state": "no-op", "reason_code": "consistent-milestone-retained", "snapshot": snapshot,
                    "evidence": group["assessments"], "blocking_ids": [], "retained_status": current}
        target = STATUSES[ci + 1]
        if request["mode"] == "normal" and target != ceiling:
            raise ContractError("adjacent-phase-recovery-required")
        group = validate_milestone(project, request["milestone_evidence"], target, snapshot,
                                   recovery=request["mode"] == "recovery" and request["phase"] != OWNERS[target])
        prefix = payload_prefix(project)
        config = roadmap_configuration(project, yaml)
        raw = read_bytes(project, config["roadmap_path"])
        proposal = {"schema_version": VERSION, "snapshot": snapshot, "milestone_evidence": request["milestone_evidence"],
                    "decision": {"reference": request["decision_reference"],
                                 "sha256": byte_digest(read_bytes(project, request["decision_reference"])),
                                 "contract_sha256": POLICY_SHA256},
                    "from_status": current, "to_status": target, "expected_roadmap_sha256": byte_digest(raw),
                    "effect_id": "lifecycle-" + digest({"snapshot": snapshot, "to_status": target})[:32],
                    "recovery": {"mode": request["mode"], "ceiling": ceiling, "roadmap_path": config["roadmap_path"],
                                 "source_preimage": raw.decode("utf-8"), "verification": []}}
        proposal["patch_sha256"] = digest(_operations(proposal))
        if request["action"] == "revalidate" and proposal != request["proposal"]:
            raise ContractError("prepared-proposal-changed")
        return {"state": "ready", "reason_code": "adjacent-milestone-substantiated", "snapshot": snapshot,
                "evidence": group["assessments"], "blocking_ids": [], "proposal": proposal}
    except ContractError as error:
        return blocked(str(error), locals().get("snapshot"))

def validate_specification_ready(project: Path, path: str, yaml: Any) -> dict:
    """Validate acyclic, current independent pre-brief authoring evidence."""
    packet = exact(read_json(project, path), {"schema_version", "feature_directory", "scope_sha256",
        "assessments", "required_check_ids", "satisfied_check_ids", "artifact_digests", "unresolved_ids"}, "authoring-ready")
    feature = relative(packet["feature_directory"])
    pointer = read_json(project, ".specify/feature.json")
    if packet["schema_version"] != VERSION or pointer.get("feature_directory") != feature:
        raise ContractError("authoring-target-mismatch")
    spec_path = feature + "/spec.md"
    quality_path = feature + "/checklists/requirements.md"
    scope = byte_digest(read_bytes(project, spec_path))
    if packet["scope_sha256"] != scope:
        raise ContractError("authoring-scope-stale")
    checks = {"authoring-quality", "clarification", "linkage", "independent-review"}
    if (set(strings(packet["required_check_ids"], "authoring-checks", nonempty=True)) != checks
            or set(strings(packet["satisfied_check_ids"], "authoring-checks", nonempty=True)) != checks
            or strings(packet["unresolved_ids"], "authoring-unresolved")):
        raise ContractError("authoring-proof-incomplete")
    artifacts = validate_sources(project, packet["artifact_digests"])
    if not {spec_path, quality_path}.issubset(artifacts):
        raise ContractError("authoring-input-coverage-missing")
    quality = read_bytes(project, quality_path).decode("utf-8")
    markers = re.findall(r"^\s*- \[([ xX])\]", quality, re.M)
    if not markers or " " in markers:
        raise ContractError("authoring-quality-incomplete")
    snapshot = {"feature_directory": feature, "scope_sha256": scope}
    covered = set()
    for ref in evidence(project, packet["assessments"]):
        if ref["kind"] != "independent-authoring-review":
            raise ContractError("authoring-review-kind-invalid")
        record = validate_assessment(project, ref, snapshot, {"FarmBoy Reviewer"})
        if not {spec_path, quality_path}.issubset(record["artifact_digests"]):
            raise ContractError("authoring-review-input-coverage-missing")
        covered.update(record["satisfied_check_ids"])
    if not checks.issubset(covered):
        raise ContractError("authoring-independent-coverage-incomplete")
    return {"specification_ready": True, "feature_directory": feature, "scope_sha256": scope,
            "artifact_digests": artifacts, "assessment_references": packet["assessments"]}

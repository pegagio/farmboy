"""Build and serve the checked-in FarmBoy catalog for bundle installation."""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import tomllib
import unicodedata
import zipfile
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from posixpath import normpath


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "bundles/farmboy/bundle.yml"
CATALOG = ROOT / "catalog"
RELEASE = CATALOG / "release.json"
CONTROLLER_SOURCE = ROOT / "controllers/farmboy"
CONTROLLER_PACKAGE_ID = "farmboy-controllers"
EXTENSION_SOURCES = {
    "flow-roadmap": "roadmap",
    "flow-wiki": "wiki",
    "farmboy-feedback": "feedback",
}
CONTROLLER_BINDINGS = (
    ("farmboy-select-feature", "FarmBoy Select Feature", "farmboy-select-feature"),
    ("farmboy-specify", "FarmBoy Specify", "farmboy-specify"),
    ("farmboy-clarify", "FarmBoy Clarify", "farmboy-clarify"),
    ("farmboy-plan", "FarmBoy Plan", "farmboy-plan"),
    ("farmboy-tasks", "FarmBoy Tasks", "farmboy-tasks"),
    ("farmboy-analyze-remediate", "FarmBoy Analyze", "farmboy-analyze-remediate"),
    ("farmboy-implement", "FarmBoy Implement", "farmboy-implement"),
    ("farmboy-converge", "FarmBoy Converge", "farmboy-converge"),
    ("farmboy-closeout", "FarmBoy Close Out", "farmboy-closeout"),
    ("farmboy-wiki-lint-update", "FarmBoy Wiki Lint Update", "farmboy-wiki-lint-update"),
)


AGENT_SOURCE = ROOT / "agents/farmboy"
AGENT_PACKAGE_ID = "farmboy-agents"


def validate_agent_manifest(manifest: object) -> dict[str, object]:
    """Validate inventory without acquiring ownership of consumer files."""
    if not isinstance(manifest, dict) or manifest.get("schema_version") != "1.0":
        fail("agent manifest schema is invalid")
    package = manifest.get("package")
    if not isinstance(package, dict) or package.get("id") != AGENT_PACKAGE_ID or not re.fullmatch(r"\d+\.\d+\.\d+", str(package.get("version", ""))):
        fail("agent package identity/version is invalid")
    entries = manifest.get("agents")
    if not isinstance(entries, list) or not entries:
        fail("agent inventory must be a nonempty list")
    seen = {key: set() for key in ("name", "file", "destination")}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != set(seen):
            fail("agent inventory entry must contain name, file and destination")
        for key in seen:
            value = entry[key]
            if not isinstance(value, str) or not value.strip() or value in seen[key]:
                fail(f"agent inventory has an empty or duplicate {key}")
            seen[key].add(value)
        for key, prefix in (("file", "agents/"), ("destination", ".codex/agents/")):
            value = entry[key]
            relative = Path(value)
            if not value.startswith(prefix) or relative.is_absolute() or ".." in relative.parts or "\\" in value or relative.as_posix() != value or len(relative.parts) != len(Path(prefix).parts) + 1 or relative.suffix != ".toml":
                fail(f"agent inventory has an unsafe {key}")
    changes = manifest.get("changes", {})
    if not isinstance(changes, dict):
        fail("agent change guidance must be an object")
    for kind in ("added", "renamed", "retired"):
        if not isinstance(changes.get(kind, []), list):
            fail("agent change guidance must contain lists")
    return manifest


def validate_agent_definition(content: bytes, name: str) -> dict[str, object]:
    """Require a parseable native definition matching the exact manifest name."""
    try:
        definition = tomllib.loads(content.decode("utf-8"))
    except (UnicodeError, tomllib.TOMLDecodeError) as error:
        fail(f"agent TOML is malformed: {type(error).__name__}")
    for key in ("name", "description", "developer_instructions", "model", "model_reasoning_effort"):
        if not isinstance(definition.get(key), str) or not definition[key].strip():
            fail(f"agent TOML lacks nonempty {key}")
    if definition["model_reasoning_effort"] not in {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}:
        fail("agent reasoning effort is invalid")
    if definition["name"] != name:
        fail("agent TOML name differs from its manifest")
    return definition


def agent_manifest(source: Path | None = None) -> dict[str, object]:
    """Read reviewed source inventory with existing YAML tooling."""
    import yaml
    try:
        return validate_agent_manifest(yaml.safe_load(((source or AGENT_SOURCE) / "manifest.yml").read_text(encoding="utf-8")))
    except yaml.YAMLError:
        fail("agent manifest YAML is malformed")


def agent_package_files(source: Path | None = None) -> dict[str, Path]:
    """Select regular reviewed source members, rejecting symlink ancestors."""
    source = source or AGENT_SOURCE
    if source.is_symlink():
        fail("agent source root is a symlink")
    if (source / "manifest.yml").is_symlink() or not (source / "manifest.yml").is_file():
        fail("agent manifest is not a regular source file")
    manifest = agent_manifest(source)
    files = {"manifest.yml": source / "manifest.yml"}
    for entry in manifest["agents"]:
        path = source / entry["file"]
        for candidate in (path, *path.parents):
            if candidate.is_symlink():
                fail("agent source or ancestor is a symlink")
            if candidate == source:
                break
        if not path.is_file():
            fail("agent source member is not a regular file")
        validate_agent_definition(path.read_bytes(), entry["name"])
        files[entry["file"]] = path
    if files["manifest.yml"].is_symlink() or not files["manifest.yml"].is_file():
        fail("agent source manifest is not a regular file")
    return files


def validate_agent_archive(archive_path: Path, expected_version: str | None = None) -> tuple[dict[str, object], dict[str, bytes]]:
    """Reject unsafe/unlisted ZIP members and inconsistent package versions."""
    import stat
    import yaml
    members = {}
    with zipfile.ZipFile(archive_path) as archive:
        for info in archive.infolist():
            path = Path(info.filename)
            mode = info.external_attr >> 16
            if info.is_dir() or info.filename in members or path.is_absolute() or ".." in path.parts or "\\" in info.filename or path.as_posix() != info.filename or (stat.S_IFMT(mode) not in (0, stat.S_IFREG)):
                fail("agent archive contains an unsafe or duplicate member")
            members[info.filename] = archive.read(info)
    if "manifest.yml" not in members:
        fail("agent archive is missing its manifest")
    try:
        manifest = validate_agent_manifest(yaml.safe_load(members["manifest.yml"].decode("utf-8")))
    except (yaml.YAMLError, UnicodeError):
        fail("agent archive manifest is malformed")
    if expected_version is not None and manifest["package"]["version"] != expected_version:
        fail("agent archive version differs from selected package")
    if set(members) != {"manifest.yml", *(entry["file"] for entry in manifest["agents"])}:
        fail("agent archive contains missing or unlisted members")
    for entry in manifest["agents"]:
        validate_agent_definition(members[entry["file"]], entry["name"])
    return manifest, members


def select_agent_targets(manifest: dict[str, object], *, agent: str | None = None, all_agents: bool = False) -> list[dict[str, str]]:
    """Select only current manifest targets, with no wildcard or alias."""
    validate_agent_manifest(manifest)
    if bool(agent) == all_agents:
        fail("reset requires exactly one exact agent name or --all")
    selected = [entry for entry in manifest["agents"] if all_agents or entry["name"] == agent]
    if not selected:
        fail("unknown current agent name")
    return selected


def package_agents(destination: Path, *, status: str = "snapshot") -> dict[str, object]:
    """Build canonical defaults deterministically, with package-only provenance."""
    files = agent_package_files()
    manifest = agent_manifest()
    destination.parent.mkdir(parents=True, exist_ok=True)
    source_hash = hashlib.sha256()
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, path in sorted(files.items()):
            data = path.read_bytes()
            if b"/Users/" in data or str(Path.home()).encode() in data:
                fail("host path in agent source")
            source_hash.update(name.encode() + b"\0" + data)
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
    return {"id": AGENT_PACKAGE_ID, "version": manifest["package"]["version"],
            "artifact": destination.name, "sha256": digest(destination),
            "source_repository": "https://github.com/pegagio/farmboy",
            "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "source_sha256": source_hash.hexdigest(), "status": status}


def _agent_path(project: Path, relative: str) -> Path:
    """Reject escaping or symlink paths without examining consumer file content."""
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != relative or "\\" in relative:
        fail("unsafe-agent-path")
    cursor = project
    for part in path.parts:
        cursor /= part
        if cursor.is_symlink():
            fail("agent-path-symlink")
    if not cursor.resolve().is_relative_to(project.resolve()):
        fail("unsafe-agent-path")
    return cursor


def _agent_identity_report(name: str) -> dict[str, object]:
    """Keep path-like and control-character identities out of portable reports."""
    portable = not any(character in name for character in ("/", "\\")) and not any(
        unicodedata.category(character) == "Cc" for character in name
    )
    return {"name": name if portable else "<redacted>", "identity_redacted": not portable}


def validate_agent_metadata(metadata: object) -> dict[str, object]:
    """Require portable package provenance, never consumer-copy tracking."""
    fields = {"id", "version", "artifact", "sha256", "source_repository", "source_commit", "source_sha256", "status"}
    if not isinstance(metadata, dict) or set(metadata) != fields:
        fail("invalid-agent-package-metadata")
    if metadata["id"] != AGENT_PACKAGE_ID or metadata["status"] not in ("snapshot", "released"):
        fail("invalid-agent-package-identity")
    for key in fields:
        if not isinstance(metadata[key], str) or not metadata[key].strip():
            fail("invalid-agent-package-field")
    if not re.fullmatch(r"\d+\.\d+\.\d+", metadata["version"]) or Path(metadata["artifact"]).name != metadata["artifact"] or "\\" in metadata["artifact"]:
        fail("invalid-agent-package-coordinate")
    if any(not re.fullmatch(r"[a-f0-9]{64}", metadata[k]) for k in ("sha256", "source_sha256")):
        fail("invalid-agent-package-digest")
    if not re.fullmatch(r"[a-f0-9]{40,64}", metadata["source_commit"]) or not re.fullmatch(r"https://github.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", metadata["source_repository"]):
        fail("invalid-agent-package-provenance")
    return metadata


def cache_agent_defaults(project: Path, archive: Path, metadata: dict[str, object]) -> None:
    """Replace a validated package cache, restoring the previous cache on failure."""
    validate_agent_metadata(metadata)
    if digest(archive) != metadata.get("sha256") or metadata.get("id") != AGENT_PACKAGE_ID:
        fail("agent-package-digest-mismatch")
    _, members = validate_agent_archive(archive, str(metadata["version"]))
    validate_agent_source_digest(members, metadata)
    target = _agent_path(project, ".specify/farmboy/agent-defaults")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not target.is_dir():
        fail("agent-cache-not-directory")
    stage = Path(tempfile.mkdtemp(prefix=".agent-defaults-", dir=target.parent))
    backup = stage.with_name(stage.name + "-previous")
    try:
        (stage / "package.zip").write_bytes(archive.read_bytes())
        (stage / "manifest.json").write_text(json.dumps(metadata, sort_keys=True) + "\n")
        if target.exists():
            os.replace(target, backup)
        try:
            os.replace(stage, target)
        except OSError:
            if backup.exists():
                os.replace(backup, target)
            raise
    finally:
        if stage.exists():
            shutil.rmtree(stage)
        if backup.exists() and target.exists():
            shutil.rmtree(backup)


def remove_agent_defaults(project: Path) -> None:
    """Remove available defaults only; copied configurations are consumer-owned."""
    target = _agent_path(project, ".specify/farmboy/agent-defaults")
    if target.exists():
        if not target.is_dir():
            fail("agent-cache-not-directory")
        shutil.rmtree(target)


def agent_operation(project: Path, operation: str, *, agent: str | None = None,
                    all_agents: bool = False) -> dict[str, object]:
    """Preflight a manifest-selected copy/reset and report bounded partial writes."""
    project = project.resolve()
    result = {"schema_version": "1.0", "operation": operation, "status": "failed",
              "inputs": {"agent": None, "all": all_agents}, "package": None,
              "targets": [], "warnings": [], "recovery": None, "conflict": None}
    targets = result["targets"]
    written = 0
    failed_index = None
    try:
        if not project.is_dir() or not _agent_path(project, ".specify").is_dir():
            fail("project-not-initialized")
        metadata_file = _agent_path(project, ".specify/farmboy/agent-defaults/manifest.json")
        archive = _agent_path(project, ".specify/farmboy/agent-defaults/package.zip")
        metadata = validate_agent_metadata(json.loads(metadata_file.read_text()))
        if metadata.get("id") != AGENT_PACKAGE_ID or digest(archive) != metadata.get("sha256"):
            fail("agent-cache-integrity-mismatch")
        result["package"] = metadata
        manifest, members = validate_agent_archive(archive, metadata["version"])
        validate_agent_source_digest(members, metadata)
        if operation == "install-missing":
            if agent or all_agents:
                fail("install-missing-does-not-accept-selectors")
            entries = manifest["agents"]
        elif operation == "reset":
            entries = select_agent_targets(manifest, agent=agent, all_agents=all_agents)
            result["inputs"]["agent"] = agent
            result["warnings"].append("Reset discards customizations in the selected current targets.")
        else:
            fail("unknown-agent-operation")
        targets.extend({"name": e["name"], "path": e["destination"], "outcome": "not-attempted"} for e in entries)
        destinations = {}
        for index, entry in enumerate(entries):
            failed_index = index
            target = _agent_path(project, entry["destination"])
            if target.exists() and not target.is_file():
                fail("agent-destination-not-regular")
            destinations[entry["name"]] = target
        failed_index = None
        inventory = _agent_path(project, ".codex/agents")
        identities = {}
        if inventory.exists():
            for path in sorted(inventory.glob("*.toml")):
                if path.is_symlink() or not path.is_file():
                    fail("agent-inventory-nonregular")
                try:
                    definition = tomllib.loads(path.read_text())
                except (UnicodeError, tomllib.TOMLDecodeError):
                    result["warnings"].append("Unparseable project agent: " + path.relative_to(project).as_posix())
                    continue
                name = definition.get("name")
                if isinstance(name, str):
                    if name in identities:
                        result["conflict"] = {
                            **_agent_identity_report(name),
                            "paths": [identities[name].relative_to(project).as_posix(), path.relative_to(project).as_posix()],
                            "recovery": "Rename or remove one definition after checking dependent assignments, then retry the operation.",
                        }
                        fail("duplicate-project-agent-identity")
                    identities[name] = path
        for index, entry in enumerate(entries):
            existing = identities.get(entry["name"])
            if existing is not None and existing != destinations[entry["name"]]:
                failed_index = index
                result["conflict"] = {
                    **_agent_identity_report(entry["name"]),
                    "paths": [existing.relative_to(project).as_posix(), entry["destination"]],
                    "recovery": "Rename or remove the competing definition after checking dependent assignments, then retry the operation.",
                }
                fail("agent-identity-destination-conflict")
        for index, entry in enumerate(entries):
            failed_index = index
            target = destinations[entry["name"]]
            try:
                # Recheck ancestry immediately before mutation; external writers are not owned.
                _agent_path(project, entry["destination"])
                if operation == "install-missing" and target.exists():
                    targets[index]["outcome"] = "preserved-existing"
                    continue
                _atomic_bytes(target, members[entry["file"]])
                targets[index]["outcome"] = "created" if operation == "install-missing" else "reset"
                written += 1
            except OSError:
                targets[index]["outcome"] = "failed"
                raise
        result["status"] = "complete"
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        result["status"] = "partial" if written else "failed"
        result["error"] = str(error) if isinstance(error, ValueError) else type(error).__name__
        if targets and not any(t["outcome"] == "failed" for t in targets):
            if failed_index is not None:
                targets[failed_index]["outcome"] = "failed"
        result["recovery"] = (result["conflict"]["recovery"] if result["conflict"] else
                               "Inspect target outcomes and retry the same explicit operation after resolving the reported failure.")
    return result


def validate_agent_source_digest(members: dict[str, bytes], metadata: dict[str, object]) -> None:
    """Verify package source provenance against the archive's actual members."""
    source_hash = hashlib.sha256()
    for name, content in sorted(members.items()):
        source_hash.update(name.encode() + b"\0" + content)
    if source_hash.hexdigest() != metadata["source_sha256"]:
        fail("agent-source-digest-mismatch")


def verify_agent_release(release: dict[str, object], catalog_dir: Path) -> None:
    """Validate package pin, artifact integrity and canonical source correspondence."""
    import yaml
    pin = yaml.safe_load(BUNDLE.read_text()).get("agent_package")
    entry = validate_agent_metadata(release.get("agent_package"))
    if not isinstance(pin, dict) or not isinstance(entry, dict) or any(entry.get(k) != pin.get(k) for k in ("id", "version")):
        fail("catalog agent package differs from bundle pin")
    artifact = catalog_dir / "packages" / str(entry.get("artifact", ""))
    if artifact.name != entry.get("artifact") or not artifact.is_file() or digest(artifact) != entry.get("sha256"):
        fail("agent package missing or mismatched")
    manifest, members = validate_agent_archive(artifact, str(entry["version"]))
    validate_agent_source_digest(members, entry)
    if manifest != agent_manifest() or members != {name: p.read_bytes() for name, p in agent_package_files().items()}:
        fail("agent package differs from canonical source")


def fail(message: str) -> None:
    raise ValueError(message)


def selected_specify(cwd: Path) -> str | None:
    """Use the project's mise-selected Specify before considering PATH."""
    mise = shutil.which("mise")
    if mise:
        result = subprocess.run([mise, "which", "specify"], cwd=cwd, text=True, capture_output=True, check=False)
        if result.returncode == 0 and result.stdout.strip():
            selected = result.stdout.strip()
            if not Path(selected).is_file() or not os.access(selected, os.X_OK):
                fail("mise-selected Specify executable is missing or not executable")
            return selected
    return shutil.which("specify")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def field(text: str, name: str, indent: int = 2) -> str:
    match = re.search(rf"^{' ' * indent}{re.escape(name)}:\s*([^\n]+)", text, re.MULTILINE)
    if match is None:
        fail(f"missing {name}")
    return match.group(1).strip().strip('"\'')


def bundle_components() -> tuple[str, dict[str, dict[str, str]]]:
    """Read the fixed, simple component lists in this repository's bundle manifest."""
    lines = BUNDLE.read_text(encoding="utf-8").splitlines()
    version = field("\n".join(lines), "version", 2)
    components: dict[str, dict[str, str]] = {"extensions": {}, "workflows": {}}
    kind: str | None = None
    component_id: str | None = None
    in_provides = False
    for line in lines:
        if line == "provides:":
            in_provides = True
        elif line and not line.startswith(" "):
            in_provides = False
            kind = None
        elif in_provides and (match := re.fullmatch(r"  ([a-z_]+):", line)):
            if match.group(1) not in components:
                fail(f"unsupported bundle component kind: {match.group(1)}")
        if line == "  extensions:":
            kind = "extensions"
        elif line == "  workflows:":
            kind = "workflows"
        elif kind and (match := re.fullmatch(r'    - id: "?([^" ]+)"?', line)):
            component_id = match.group(1)
        elif kind and component_id and (match := re.fullmatch(r'      version: "?([^" ]+)"?', line)):
            components[kind][component_id] = match.group(1)
            component_id = None
    if set(components["extensions"]) != set(EXTENSION_SOURCES) or not components["workflows"]:
        fail("bundle component list is incomplete or has changed; review the catalog builder")
    return version, components


def source_commit(source: Path, tracked_path: str = ".") -> str:
    status = subprocess.run(
        ["git", "status", "--porcelain", "--", tracked_path], cwd=source,
        text=True, capture_output=True, check=True,
    )
    if status.stdout.strip():
        fail(f"source has uncommitted changes in {tracked_path}: {source}")
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=source,
        text=True, capture_output=True, check=True,
    ).stdout.strip()


def require_local_release_sources_clean(root: Path) -> None:
    """Require committed bundle and workflow definitions for a released catalog."""
    status = subprocess.run(
        ["git", "status", "--porcelain", "--", "bundles/farmboy/bundle.yml", "workflows", "agents/farmboy"],
        cwd=root, text=True, capture_output=True, check=True,
    ).stdout.strip()
    if status:
        fail("bundle or workflow source has uncommitted changes; release builds require clean source")


def release_tag(source: Path, version: str, commit: str) -> str:
    tag = f"v{version}"
    tag_type = subprocess.run(
        ["git", "cat-file", "-t", f"refs/tags/{tag}"], cwd=source,
        text=True, capture_output=True, check=False,
    )
    if tag_type.returncode or tag_type.stdout.strip() != "tag":
        fail(f"{source} needs an annotated {tag} release tag")
    resolved = subprocess.run(
        ["git", "rev-parse", f"refs/tags/{tag}^{{commit}}"], cwd=source,
        text=True, capture_output=True, check=True,
    ).stdout.strip()
    if resolved != commit:
        fail(f"{source} HEAD differs from release tag {tag}")
    return tag


def extension_metadata(source: Path) -> dict[str, str]:
    manifest = (source / "extension.yml").read_text(encoding="utf-8")
    if "extension:\n" not in manifest:
        fail(f"extension manifest has no extension section: {source}")
    section = manifest.split("extension:\n", 1)[1].split("\nrequires:", 1)[0]
    return {name: field(section, name) for name in ("id", "name", "version", "author")}


def runtime_files(source: Path) -> list[Path]:
    files = [source / name for name in ("extension.yml", "config-template.yml", "LICENSE") if (source / name).is_file()]
    for dirname in ("commands", "scripts", "templates"):
        directory = source / dirname
        if directory.is_dir():
            files.extend(path for path in directory.rglob("*") if path.is_file() and not path.is_symlink() and "__pycache__" not in path.parts)
    return sorted(files, key=lambda path: str(path.relative_to(source)))


def controller_manifest() -> dict[str, object]:
    """Read the deliberately small, reviewed controller package manifest."""
    text = (CONTROLLER_SOURCE / "manifest.yml").read_text(encoding="utf-8")
    package_section = text.split("package:\n", 1)[1].split("\nrequires:", 1)[0]
    require_section = text.split("requires:\n", 1)[1].split("\ncontrollers:", 1)[0]
    package_id = field(package_section, "id")
    version = field(package_section, "version")
    specify_version = field(require_section, "specify_cli_version")
    controllers: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in text.splitlines():
        if line.startswith("  - skill_id:"):
            if current is not None:
                controllers.append(current)
            current = {"skill_id": line.split(":", 1)[1].strip().strip("\"'")}
        elif current is not None and line.startswith("    ") and ":" in line:
            key, value = line.strip().split(":", 1)
            current[key] = value.strip().strip("\"'")
    if current is not None:
        controllers.append(current)
    if package_id != CONTROLLER_PACKAGE_ID or not version or not specify_version:
        fail("controller package manifest identity or version is invalid")
    actual = [(item.get("skill_id"), item.get("display_name"), item.get("workflow_id")) for item in controllers]
    if actual != list(CONTROLLER_BINDINGS):
        fail("controller manifest must declare the reviewed controller inventory in order")
    if len({item["skill_id"] for item in controllers}) != len(CONTROLLER_BINDINGS) or len({item["workflow_id"] for item in controllers}) != len(CONTROLLER_BINDINGS):
        fail("controller skill and workflow bindings must be unique")
    return {
        "package_id": package_id,
        "version": version,
        "specify_cli_version": specify_version,
        "controllers": controllers,
    }


def controller_package_files() -> dict[str, Path]:
    """Map reviewed source files to their consumer installation paths."""
    manifest = controller_manifest()
    files: dict[str, Path] = {}
    shared = [CONTROLLER_SOURCE / "manifest.yml", CONTROLLER_SOURCE / "controller-protocol.md"]
    scripts = CONTROLLER_SOURCE / "scripts"
    shared.extend(
        path for path in scripts.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )
    for source in shared:
        if source.is_symlink():
            fail(f"controller package cannot contain symlinks: {source.name}")
        relative = source.relative_to(CONTROLLER_SOURCE)
        files[(Path(".specify/farmboy") / relative).as_posix()] = source
    declared_ids = {item["skill_id"] for item in manifest["controllers"]}
    skill_root = CONTROLLER_SOURCE / "skills"
    observed_ids = {path.name for path in skill_root.iterdir() if path.is_dir()}
    if observed_ids != declared_ids:
        fail("controller skill directories differ from the reviewed manifest inventory")
    for item in manifest["controllers"]:
        skill_id = item["skill_id"]
        skill_dir = skill_root / skill_id
        skill_file = skill_dir / "SKILL.md"
        metadata_file = skill_dir / "agents/openai.yaml"
        if not skill_file.is_file() or not metadata_file.is_file():
            fail(f"controller skill is incomplete: {skill_id}")
        skill_text = skill_file.read_text(encoding="utf-8")
        display_text = metadata_file.read_text(encoding="utf-8")
        name_match = re.search(r"^name:\s*[\"']?([^\"'\n]+)", skill_text, re.MULTILINE)
        display_match = re.search(r'^  display_name:\s*[\"\']([^\"\']+)', display_text, re.MULTILINE)
        if name_match is None or name_match.group(1).strip() != skill_id:
            fail(f"Codex skill name differs from manifest: {skill_id}")
        if display_match is None or display_match.group(1) != item["display_name"]:
            fail(f"Codex display name differs from manifest: {skill_id}")
        for source in sorted(skill_dir.rglob("*")):
            if source.is_file():
                if source.is_symlink():
                    fail(f"controller package cannot contain symlinks: {source.name}")
                relative = source.relative_to(skill_root)
                files[(Path(".agents/skills") / relative).as_posix()] = source
    return dict(sorted(files.items()))


def package_controller(destination: Path) -> dict[str, object]:
    """Build a deterministic direct Codex skill package without host paths."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    files = controller_package_files()
    home = str(Path.home()).encode()
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, source in files.items():
            data = source.read_bytes()
            if (home and home in data) or (b"/" + b"Users/") in data:
                fail(f"host-specific path in controller package file: {name}")
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
    manifest = controller_manifest()
    return {
        "package_id": manifest["package_id"],
        "version": manifest["version"],
        "artifact": destination.name,
        "sha256": digest(destination),
        "files": sorted(files),
        "controllers": manifest["controllers"],
    }


def _safe_package_members(archive_path: Path) -> dict[str, bytes]:
    """Validate the package archive before any consumer path is written."""
    members: dict[str, bytes] = {}
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            name = member.filename
            path = Path(name)
            if path.is_absolute() or ".." in path.parts or name.startswith(("/", "\\")):
                fail("controller package contains an unsafe path")
            if member.is_dir():
                continue
            if not (name.startswith(".specify/farmboy/") or re.match(r"^\.agents/skills/farmboy-[^/]+/", name)):
                fail(f"controller package contains an unexpected path: {name}")
            members[name] = archive.read(member)
    if not members or ".specify/farmboy/manifest.yml" not in members:
        fail("controller package is missing its manifest")
    return members


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _atomic_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def _read_ownership_record(record_path: Path) -> dict[str, object]:
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"FarmBoy skill ownership record is unreadable: {error}")
    if record.get("package") != CONTROLLER_PACKAGE_ID or not isinstance(record.get("files"), dict):
        fail("FarmBoy skill ownership record is malformed")
    if record.get("status") != "installed":
        fail(f"FarmBoy skill package is in incomplete state: {record.get('status')}")
    return record


def _owned_target(project: Path, relative: str) -> Path:
    """Confine recorded package files to the direct FarmBoy package inventory."""
    if not isinstance(relative, str) or not relative or "\\" in relative:
        fail("invalid FarmBoy ownership path")
    path = Path(relative)
    parts = path.parts
    if path.is_absolute() or path.as_posix() != relative or ".." in parts:
        fail(f"invalid FarmBoy ownership path: {relative}")
    skills = {skill_id for skill_id, _, _ in CONTROLLER_BINDINGS} | {"farmboy-start-feature"}
    skill_path = (
        len(parts) >= 4 and parts[:2] == (".agents", "skills")
        and parts[2] in skills and parts[3:] in {("SKILL.md",), ("agents", "openai.yaml")}
    )
    helper_path = (
        parts[:2] == (".specify", "farmboy")
        and (parts[2:] in {("manifest.yml",), ("controller-protocol.md",)} or
             (len(parts) >= 4 and parts[2] == "scripts"))
    )
    if not (skill_path or helper_path):
        fail(f"invalid FarmBoy ownership path: {relative}")
    target = project / path
    cursor = project
    for part in parts:
        cursor /= part
        if cursor.is_symlink():
            fail(f"FarmBoy ownership path crosses a symlink: {relative}")
    if not target.resolve(strict=False).is_relative_to(project.resolve()):
        fail(f"FarmBoy ownership path escapes consumer project: {relative}")
    return target


def install_controller_package(
    project: Path,
    archive_path: Path,
    *,
    refresh: bool,
    source_digest: str,
    catalog_status: str,
    preflight_only: bool = False,
) -> None:
    """Install or refresh the direct skill package with digest-based ownership."""
    project = Path(project).resolve()
    members = _safe_package_members(Path(archive_path))
    manifest_text = members[".specify/farmboy/manifest.yml"].decode("utf-8")
    package_version = field(manifest_text.split("package:\n", 1)[1].split("\nrequires:", 1)[0], "version")
    record_path = project / ".specify/farmboy/skills-install.json"
    record_exists = record_path.is_file()
    old_record: dict[str, object] | None = None
    old_record_bytes: bytes | None = None
    old_files: dict[str, bytes | None] = {}
    if refresh and record_exists:
        old_record_bytes = record_path.read_bytes()
        old_record = _read_ownership_record(record_path)
        old_owned = old_record["files"]
    else:
        if record_exists:
            fail("FarmBoy skills are already installed; use refresh")
        old_owned = {}
    for relative, content in members.items():
        target = _owned_target(project, relative)
        owned_before = isinstance(old_owned, dict) and relative in old_owned
        if owned_before:
            expected = old_owned[relative]
            if not target.is_file() or digest(target) != expected:
                fail(f"locally changed FarmBoy owned file blocks replacement: {relative}")
            old_files[relative] = target.read_bytes()
        elif target.exists():
            fail(f"consumer-owned path conflicts with FarmBoy skills: {relative}")
        else:
            old_files[relative] = None
    if refresh and isinstance(old_owned, dict):
        for relative, expected in old_owned.items():
            target = _owned_target(project, relative)
            if relative not in members:
                if not target.is_file() or digest(target) != expected:
                    fail(f"locally changed obsolete FarmBoy owned file blocks refresh: {relative}")
                old_files[relative] = target.read_bytes()
    manifest = json.loads(json.dumps(controller_manifest())) if CONTROLLER_SOURCE.is_dir() else {}
    current_bindings = manifest.get("controllers", [])
    files_record = {relative: _sha256_bytes(content) for relative, content in members.items()}
    provisional = {
        "schema_version": "1.0",
        "package": CONTROLLER_PACKAGE_ID,
        "version": package_version,
        "source_sha256": source_digest,
        "catalog_status": catalog_status,
        "controllers": current_bindings,
        "files": files_record,
        "status": "refreshing" if old_record is not None else "installing",
    }
    if preflight_only:
        return
    _atomic_bytes(record_path, (json.dumps(provisional, indent=2, sort_keys=True) + "\n").encode())
    try:
        for relative, content in members.items():
            _atomic_bytes(_owned_target(project, relative), content)
        observed = {relative: digest(_owned_target(project, relative)) for relative in members}
        if observed != files_record:
            fail("installed FarmBoy skill inventory differs from the package")
        if refresh and isinstance(old_owned, dict):
            for relative in old_owned:
                if relative not in members:
                    _owned_target(project, relative).unlink()
        provisional["status"] = "installed"
        _atomic_bytes(record_path, (json.dumps(provisional, indent=2, sort_keys=True) + "\n").encode())
    except Exception:
        for relative, content in old_files.items():
            target = _owned_target(project, relative)
            if content is None:
                try:
                    target.unlink()
                except FileNotFoundError:
                    pass
            else:
                _atomic_bytes(target, content)
        if old_record_bytes is None:
            record_path.unlink(missing_ok=True)
        else:
            _atomic_bytes(record_path, old_record_bytes)
        raise


def remove_controller_package(project: Path, *, preflight_only: bool = False) -> None:
    """Remove only unchanged files recorded as FarmBoy owned."""
    project = Path(project).resolve()
    record_path = project / ".specify/farmboy/skills-install.json"
    if not record_path.is_file():
        fail("FarmBoy skill ownership record is missing")
    record = _read_ownership_record(record_path)
    owned = record["files"]
    assert isinstance(owned, dict)
    for relative, expected in owned.items():
        target = _owned_target(project, relative)
        if not target.is_file() or digest(target) != expected:
            fail(f"locally changed FarmBoy owned file blocks removal: {relative}")
    if preflight_only:
        return
    record["status"] = "removing"
    _atomic_bytes(record_path, (json.dumps(record, indent=2, sort_keys=True) + "\n").encode())
    for relative in sorted(owned, key=lambda item: item.count("/"), reverse=True):
        _owned_target(project, relative).unlink()
    remaining = [relative for relative in owned if _owned_target(project, relative).exists()]
    if remaining:
        fail(f"FarmBoy skill removal incomplete: {', '.join(remaining)}")
    record_path.unlink()
    for relative in owned:
        parent = _owned_target(project, relative).parent
        while parent != project and parent.name not in {"runs", "flow-controllers", ".specify", ".agents", "skills"}:
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent


def remove(project: Path) -> None:
    """Remove the Specify bundle and unchanged FarmBoy owned Codex skills."""
    project = Path(project).resolve()
    if not project.is_dir() or ROOT in project.parents:
        fail("removal target must be an existing consumer outside the source checkout")
    if not (project / ".specify").is_dir():
        fail("removal target is not an initialized Specify consumer")
    record = project / ".specify/farmboy/skills-install.json"
    if not record.is_file():
        fail("FarmBoy skill ownership record is missing")
    remove_controller_package(project, preflight_only=True)
    expected_specify = tomllib.loads((ROOT / "mise.toml").read_text(encoding="utf-8"))["tools"]["pipx:specify-cli"]
    specify = selected_specify(project)
    if specify is None:
        fail("specify is unavailable; run mise trust and mise install in this checkout")
    version = subprocess.run([specify, "--version"], cwd=project, text=True, capture_output=True, check=True).stdout.strip()
    if version != f"specify {expected_specify}":
        fail(f"expected Specify {expected_specify}, found {version}")
    subprocess.run([specify, "bundle", "remove", "farmboy"], cwd=project, check=True)
    remove_controller_package(project)
    remove_agent_defaults(project)


def package_extension(source: Path, destination: Path, extension_id: str) -> None:
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in runtime_files(source):
            data = path.read_bytes()
            if str(Path.home()).encode() in data:
                fail(f"host-specific home path in {extension_id}/{path.relative_to(source)}")
            info = zipfile.ZipInfo(str(Path(extension_id) / path.relative_to(source)), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)


def build(roadmap: Path, wiki: Path, snapshot: bool = False) -> None:
    if not snapshot:
        require_local_release_sources_clean(ROOT)
    bundle_version, components = bundle_components()
    sources = {
        "flow-roadmap": roadmap.resolve(),
        "flow-wiki": wiki.resolve(),
        "farmboy-feedback": ROOT / "extensions/farmboy-feedback",
    }
    release: dict[str, object] = {
        "schema_version": "1.0", "bundle_version": bundle_version,
        "status": "snapshot" if snapshot else "released",
        "extensions": {}, "workflows": {},
    }
    with tempfile.TemporaryDirectory(prefix="farmboy-build-") as temporary:
        packages = Path(temporary)
        for extension_id, source in sources.items():
            metadata = extension_metadata(source)
            expected = components["extensions"][extension_id]
            if metadata["id"] != extension_id or metadata["version"] != expected:
                fail(f"{source} must declare {extension_id} version {expected}")
            tracked_path = "extensions/farmboy-feedback" if extension_id == "farmboy-feedback" else "."
            commit = source_commit(ROOT if extension_id == "farmboy-feedback" else source, tracked_path)
            tag = None if extension_id == "farmboy-feedback" or snapshot else release_tag(source, expected, commit)
            artifact = f"{extension_id}-{expected}.zip"
            package_extension(source, packages / artifact, extension_id)
            release["extensions"][extension_id] = {
                "version": expected, "name": metadata["name"], "author": metadata["author"],
                "source_repository": "https://github.com/pegagio/farmboy" if extension_id == "farmboy-feedback" else f"https://github.com/pegagio/spec-kit-flow-{EXTENSION_SOURCES[extension_id]}",
                "source_commit": commit, "source_tag": tag,
                "artifact": artifact, "sha256": digest(packages / artifact),
            }
        for workflow_id, version in components["workflows"].items():
            path = ROOT / "workflows" / workflow_id / "workflow.yml"
            source = path.read_text(encoding="utf-8")
            if field(source.split("workflow:\n", 1)[1], "id") != workflow_id or field(source.split("workflow:\n", 1)[1], "version") != version:
                fail(f"workflow source does not match bundle pin: {workflow_id} {version}")
            release["workflows"][workflow_id] = {"version": version, "sha256": digest(path)}
        controller_archive = packages / f"{CONTROLLER_PACKAGE_ID}-{controller_manifest()['version']}.zip"
        controller = package_controller(controller_archive)
        status = subprocess.run(
            ["git", "status", "--porcelain", "--", "controllers/farmboy"],
            cwd=ROOT, text=True, capture_output=True, check=True,
        ).stdout.strip()
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
        if not snapshot and status:
            fail("controller source has uncommitted changes; release builds require clean source")
        release["controller_package"] = {
            "id": controller["package_id"], "version": controller["version"],
            "artifact": controller["artifact"], "sha256": controller["sha256"],
            "source_commit": commit, "source_dirty": bool(status),
            "source_sha256": controller["sha256"], "controllers": controller["controllers"],
        }
        release["agent_package"] = package_agents(packages / f"farmboy-agents-{agent_manifest()['package']['version']}.zip", status=release["status"])
        if RELEASE.exists():
            previous = json.loads(RELEASE.read_text(encoding="utf-8"))
            if not snapshot and previous.get("status") == "released" and previous["bundle_version"] == bundle_version and previous != release:
                fail("catalog content changed without a bundle version change")
        (CATALOG / "packages").mkdir(parents=True, exist_ok=True)
        for artifact in packages.iterdir():
            shutil.copy2(artifact, CATALOG / "packages" / artifact.name)
        RELEASE.write_text(json.dumps(release, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Built catalog for FarmBoy {bundle_version} with {len(sources)} extensions and {len(components['workflows'])} workflows")


def verified_release(catalog_dir: Path | None = None, release_path: Path | None = None) -> dict[str, object]:
    catalog_dir = catalog_dir or CATALOG
    release_path = release_path or (catalog_dir / "release.json")
    release = json.loads(release_path.read_text(encoding="utf-8"))
    bundle_version, components = bundle_components()
    if release.get("status") not in ("snapshot", "released"):
        fail("catalog status must be snapshot or released")
    if release["bundle_version"] != bundle_version:
        fail("catalog bundle version differs from bundle.yml")
    if set(release["extensions"]) != set(components["extensions"]) or set(release["workflows"]) != set(components["workflows"]):
        fail("catalog components differ from bundle.yml")
    for extension_id, version in components["extensions"].items():
        entry = release["extensions"][extension_id]
        artifact = catalog_dir / "packages" / entry["artifact"]
        if entry["version"] != version or not artifact.is_file() or digest(artifact) != entry["sha256"]:
            fail(f"catalog artifact is missing or mismatched: {extension_id}")
        if release["status"] == "released" and extension_id in ("flow-roadmap", "flow-wiki") and entry.get("source_tag") != f"v{version}":
            fail(f"catalog source tag differs from bundle pin: {extension_id}")
        with zipfile.ZipFile(artifact) as archive:
            manifest_name = f"{extension_id}/extension.yml"
            if manifest_name not in archive.namelist():
                fail(f"catalog archive has no extension manifest: {extension_id}")
            manifest = archive.read(manifest_name).decode("utf-8")
            section = manifest.split("extension:\n", 1)[1].split("\nrequires:", 1)[0]
            if field(section, "id") != extension_id or field(section, "version") != version:
                fail(f"catalog archive manifest differs from bundle pin: {extension_id}")
    for workflow_id, version in components["workflows"].items():
        entry = release["workflows"][workflow_id]
        path = ROOT / "workflows" / workflow_id / "workflow.yml"
        if entry["version"] != version or digest(path) != entry["sha256"]:
            fail(f"workflow source differs from catalog release: {workflow_id}")
    controller = release.get("controller_package")
    if not isinstance(controller, dict) or controller.get("id") != CONTROLLER_PACKAGE_ID:
        fail("catalog has no FarmBoy controller package record")
    current_manifest = controller_manifest()
    if controller.get("version") != current_manifest["version"]:
        fail("catalog controller package version differs from the reviewed manifest")
    package_path = catalog_dir / "packages" / str(controller.get("artifact", ""))
    if not package_path.is_file() or digest(package_path) != controller.get("sha256"):
        fail("catalog controller package is missing or has a checksum mismatch")
    members = _safe_package_members(package_path)
    packaged_manifest = members[".specify/farmboy/manifest.yml"].decode("utf-8")
    packaged_bindings = re.findall(
        r'^  - skill_id: "([^"]+)"\n    display_name: "([^"]+)"\n    workflow_id: "([^"]+)"',
        packaged_manifest, re.MULTILINE,
    )
    if packaged_bindings != list(CONTROLLER_BINDINGS) or controller.get("controllers") != current_manifest["controllers"]:
        fail("catalog controller inventory differs from the reviewed package manifest")
    if release["status"] == "released" and controller.get("source_dirty"):
        fail("released controller package cannot have dirty source provenance")
    verify_agent_release(release, catalog_dir)
    return release


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_: object) -> None:
        pass


def build_development_snapshot(destination: Path, *, source_overrides: dict[str, Path] | None = None) -> dict[str, object]:
    """Compose a disposable snapshot catalog without changing checked-in release files."""
    destination = Path(destination)
    package_dir = destination / "packages"
    package_dir.mkdir(parents=True, exist_ok=True)
    previous = json.loads(RELEASE.read_text(encoding="utf-8"))
    bundle_version, components = bundle_components()
    extensions: dict[str, object] = {}
    source_overrides = source_overrides or {}
    for extension_id, version in components["extensions"].items():
        previous_entry = previous["extensions"].get(extension_id)
        source = source_overrides.get(extension_id)
        if extension_id == "farmboy-feedback" and source is None:
            source = ROOT / "extensions/farmboy-feedback"
        if source is not None:
            source = Path(source).resolve()
            metadata = extension_metadata(source)
            if metadata["id"] != extension_id or metadata["version"] != version:
                fail(f"development snapshot source does not match bundle pin: {extension_id}")
            artifact_name = f"{extension_id}-{version}.zip"
            artifact = package_dir / artifact_name
            package_extension(source, artifact, extension_id)
            status = subprocess.run(["git", "status", "--porcelain"], cwd=source,
                                    text=True, capture_output=True, check=True).stdout.strip()
            commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=source,
                                    text=True, capture_output=True, check=True).stdout.strip()
            extensions[extension_id] = {
                "version": version, "name": metadata["name"], "author": metadata["author"],
                "source_repository": (
                    "https://github.com/pegagio/farmboy"
                    if extension_id == "farmboy-feedback"
                    else f"https://github.com/pegagio/spec-kit-flow-{EXTENSION_SOURCES[extension_id]}"
                ),
                "source_commit": commit, "source_tag": None, "source_dirty": bool(status),
                "artifact": artifact_name, "sha256": digest(artifact),
            }
        else:
            if previous_entry is None:
                fail(f"development snapshot source required for new extension identity: {extension_id}")
            if previous_entry["version"] != version:
                fail(f"development snapshot source required for changed extension pin: {extension_id}")
            artifact = CATALOG / "packages" / previous_entry["artifact"]
            if not artifact.is_file() or digest(artifact) != previous_entry["sha256"]:
                fail(f"released extension package is missing or mismatched: {extension_id}")
            shutil.copy2(artifact, package_dir / artifact.name)
            extensions[extension_id] = previous_entry
    workflows = {}
    for workflow_id, version in components["workflows"].items():
        source = ROOT / "workflows" / workflow_id / "workflow.yml"
        metadata = source.read_text(encoding="utf-8").split("workflow:\n", 1)[1]
        if field(metadata, "id") != workflow_id or field(metadata, "version") != version:
            fail(f"workflow source does not match bundle pin: {workflow_id}")
        workflows[workflow_id] = {"version": version, "sha256": digest(source)}
    controller_path = package_dir / f"{CONTROLLER_PACKAGE_ID}-{controller_manifest()['version']}.zip"
    controller = package_controller(controller_path)
    status = subprocess.run(
        ["git", "status", "--porcelain", "--", "controllers/farmboy"],
        cwd=ROOT, text=True, capture_output=True, check=True,
    ).stdout.strip()
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
    release: dict[str, object] = {
        "schema_version": "1.0",
        "bundle_version": bundle_version,
        "status": "snapshot",
        "extensions": extensions,
        "workflows": workflows,
        "controller_package": {
            "id": controller["package_id"], "version": controller["version"],
            "artifact": controller["artifact"], "sha256": controller["sha256"],
            "source_commit": commit, "source_dirty": bool(status),
            "source_sha256": controller["sha256"], "controllers": controller["controllers"],
        },
    }
    release["agent_package"] = package_agents(package_dir / f"farmboy-agents-{agent_manifest()['package']['version']}.zip")
    release_file = destination / "release.json"
    release_file.write_text(json.dumps(release, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    verified_release(destination, release_file)
    return release


def install(project: Path, refresh: bool, development_snapshot: bool = False,
            source_overrides: dict[str, Path] | None = None) -> None:
    project = project.resolve()
    if not project.is_dir():
        fail(f"consumer project directory does not exist: {project}")
    if ROOT in project.parents:
        fail("consumer project must not be nested inside the FarmBoy source checkout")
    snapshot_directory: tempfile.TemporaryDirectory[str] | None = None
    catalog_dir = CATALOG
    release_path = RELEASE
    if development_snapshot:
        temporary_root = Path(tempfile.gettempdir()).resolve()
        if project != ROOT.resolve() and temporary_root not in project.parents:
            fail("development snapshots require the source checkout root or a disposable consumer under the system temporary directory")
        if not (project / ".specify").is_dir():
            fail("development snapshot target must already be initialized as a Specify consumer")
        snapshot_directory = tempfile.TemporaryDirectory(prefix="farmboy-snapshot-catalog-")
        catalog_dir = Path(snapshot_directory.name)
        try:
            release = build_development_snapshot(catalog_dir, source_overrides=source_overrides)
        except Exception:
            snapshot_directory.cleanup()
            raise
        release_path = catalog_dir / "release.json"
    else:
        release = verified_release(catalog_dir, release_path)
        if release["status"] != "released":
            fail("catalog is a development snapshot; use --development-snapshot with the initialized source checkout root or a disposable consumer")
    expected_specify = tomllib.loads((ROOT / "mise.toml").read_text(encoding="utf-8"))["tools"]["pipx:specify-cli"]
    specify = selected_specify(project)
    if specify is None:
        fail("specify is unavailable; run mise trust and mise install in this checkout")
    version = subprocess.run([specify, "--version"], text=True, capture_output=True, check=True).stdout.strip()
    if version != f"specify {expected_specify}":
        fail(f"expected specify {expected_specify}, found {version}")
    controller_record = release["controller_package"]
    controller_archive = catalog_dir / "packages" / controller_record["artifact"]
    install_controller_package(
        project, controller_archive, refresh=refresh,
        source_digest=controller_record["source_sha256"], catalog_status=release["status"],
        preflight_only=True,
    )
    agent_record = release["agent_package"]
    agent_archive = catalog_dir / "packages" / agent_record["artifact"]
    validate_agent_archive(agent_archive, agent_record["version"])
    with tempfile.TemporaryDirectory(prefix="farmboy-catalog-") as temporary:
        directory = Path(temporary)
        assets = directory / "assets"
        assets.mkdir()
        for entry in release["extensions"].values():
            shutil.copy2(catalog_dir / "packages" / entry["artifact"], assets / entry["artifact"])
        workflows = assets / "workflows"
        workflows.mkdir()
        for workflow_id in release["workflows"]:
            shutil.copy2(ROOT / "workflows" / workflow_id / "workflow.yml", workflows / f"{workflow_id}.yml")
        handler = functools.partial(QuietHandler, directory=str(directory))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            extensions = {
                extension_id: {
                    "name": entry["name"], "version": entry["version"],
                    "description": "FarmBoy release component", "author": entry["author"],
                    "download_url": f"{base}/assets/{entry['artifact']}", "sha256": entry["sha256"],
                }
                for extension_id, entry in release["extensions"].items()
            }
            workflow_entries = {
                workflow_id: {
                    "id": workflow_id, "name": workflow_id, "version": entry["version"],
                    "description": "FarmBoy workflow", "author": "pegagio",
                    "url": f"{base}/assets/workflows/{workflow_id}.yml", "tags": ["farmboy"],
                }
                for workflow_id, entry in release["workflows"].items()
            }
            (directory / "extensions.json").write_text(json.dumps({"schema_version": "1.0", "extensions": extensions}), encoding="utf-8")
            (directory / "workflows.json").write_text(json.dumps({"schema_version": "1.0", "workflows": workflow_entries}), encoding="utf-8")
            environment = os.environ.copy()
            environment["SPECKIT_CATALOG_URL"] = f"{base}/extensions.json"
            environment["SPECKIT_WORKFLOW_CATALOG_URL"] = f"{base}/workflows.json"
            command = [specify, "bundle", "install", str(BUNDLE)]
            if refresh:
                command.append("--refresh")
            action = "Refreshing" if refresh else "Installing"
            print(f"{action} FarmBoy {release['bundle_version']} in {project}", flush=True)
            subprocess.run(command, cwd=project, env=environment, check=True)
            install_controller_package(
                project, controller_archive, refresh=refresh,
                source_digest=controller_record["source_sha256"], catalog_status=release["status"],
            )
            cache_agent_defaults(project, agent_archive, agent_record)
            if not refresh:
                result = agent_operation(project, "install-missing")
                if result["status"] != "complete":
                    fail("agent installation incomplete: " + json.dumps(result, sort_keys=True))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            if snapshot_directory is not None:
                snapshot_directory.cleanup()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    builder = commands.add_parser("build", help="Build versioned catalog packages")
    builder.add_argument("roadmap", type=Path)
    builder.add_argument("wiki", type=Path)
    builder.add_argument("--snapshot", action="store_true", help="Build development packages that cannot be installed through catalog tasks")
    for name in ("install", "refresh"):
        consumer = commands.add_parser(name, help=f"{name} the bundle in a consumer project")
        consumer.add_argument("project", type=Path)
        consumer.add_argument("--development-snapshot", action="store_true", help="build and use an unreleased snapshot in the initialized source checkout root or a disposable consumer")
        consumer.add_argument("--roadmap-source", type=Path, help="use this reviewed flow-roadmap checkout in the disposable development snapshot")
    remover = commands.add_parser("remove", help="remove the bundle and unchanged FarmBoy owned controllers")
    remover.add_argument("project", type=Path)
    agents = commands.add_parser("agents", help="Manage consumer-owned agent copies")
    actions = agents.add_subparsers(dest="agent_command", required=True)
    for action in ("install-missing", "reset"):
        operation = actions.add_parser(action, help="Reset discards selected customizations" if action == "reset" else "Add only absent current defaults")
        operation.add_argument("project", type=Path)
        operation.add_argument("--json", action="store_true", dest="json_output")
        if action == "reset":
            selection = operation.add_mutually_exclusive_group(required=True)
            selection.add_argument("--agent")
            selection.add_argument("--all", action="store_true", dest="all_agents")
    arguments = parser.parse_args()
    try:
        if arguments.command == "agents":
            result = agent_operation(arguments.project, arguments.agent_command, agent=getattr(arguments, "agent", None), all_agents=getattr(arguments, "all_agents", False))
            if arguments.json_output:
                print(json.dumps(result, sort_keys=True))
            else:
                print(f"operation: {result['operation']} status: {result['status']}")
                package = result["package"]
                if package:
                    print(f"package: {package['id']} {package['version']} status={package['status']}")
                    print(f"artifact: {package['artifact']}")
                    print(f"package_sha256: {package['sha256']}")
                    print(f"source: {package['source_repository']}@{package['source_commit']}")
                    print(f"source_sha256: {package['source_sha256']}")
                inputs = result["inputs"]
                print(f"inputs: agent={inputs['agent'] or 'none'} all={str(inputs['all']).lower()}")
                for warning in result["warnings"]:
                    print(f"warning: {warning}")
                for target in result["targets"]:
                    print(f"target: {target['name']} {target['path']}: {target['outcome']}")
                conflict = result["conflict"]
                if conflict:
                    print(f"conflict: {conflict['name']} at {', '.join(conflict['paths'])}")
                if "error" in result:
                    print("catalog: " + result["error"], file=sys.stderr)
                if result["recovery"]:
                    print(f"recovery: {result['recovery']}")
            if result["status"] != "complete":
                if arguments.json_output:
                    print("catalog: " + result.get("error", "agent operation failed"), file=sys.stderr)
                return 1
        elif arguments.command == "build":
            build(arguments.roadmap, arguments.wiki, arguments.snapshot)
        elif arguments.command == "remove":
            remove(arguments.project)
        else:
            source_overrides = {key: value for key, value in {
                "flow-roadmap": arguments.roadmap_source,
            }.items() if value is not None}
            if source_overrides and not arguments.development_snapshot:
                fail("extension source overrides require --development-snapshot")
            install(arguments.project, arguments.command == "refresh", arguments.development_snapshot,
                    source_overrides=source_overrides)
    except (ValueError, OSError, subprocess.CalledProcessError, KeyError, zipfile.BadZipFile) as error:
        print(f"catalog: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

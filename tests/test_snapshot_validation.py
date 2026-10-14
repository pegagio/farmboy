"""Validate the development bundle snapshot with checked and explicit sources.

Roadmap source is supplied through FLOW_ROADMAP_SOURCE when the bundle pin is
newer than the checked-in release archive; wiki and feedback remain pinned.
"""

from __future__ import annotations

import hashlib
import json
import importlib
import importlib.util
import os
import pwd
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import yaml

from test_bundle_lifecycle import (
    FEEDBACK_ID,
    ROADMAP_ID,
    WIKI_ID,
    LocalCatalog,
    ROOT,
    WORKFLOW_IDS,
    archive_extension,
    extension_manifest,
    released_feedback_source,
    sha256,
)
from implementation_scope_snapshot import (
    POST_PASS_CAPTURE_FIELDS,
    _capture_post_pass_command,
    exercise_installed_scope_matrix,
)


SPECIFY_BIN = os.environ.get("SPECIFY_BIN", "specify")
RELEASE_PATH = ROOT / "catalog/release.json"
BUNDLE_PATH = ROOT / "bundles/farmboy/bundle.yml"
INDEPENDENT_WORKFLOW = ROOT / "tests/consumer-fixtures/independent-workflow.yml"


_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_PATTERN = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_REQUIREMENT_ID_PATTERN = re.compile(r"^(?:FR|SC)-\d{3}$")
_ABSOLUTE_HOST_PATH_PATTERN = re.compile(
    r"(?:^|[^A-Za-z0-9_])/(?!/)[^\s,;)}\]]+|"
    r"(?:^|[^A-Za-z0-9_])[A-Za-z]:\\[^\s,;)}\]]+|file://[^\s,;)}\]]+"
)
_EMAIL_PATTERN = re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b")
_SECRET_PATTERN = re.compile(r"\b(?:Bearer\s+\S+|(?:gh[pousr]_|sk-)[A-Za-z0-9_-]{8,})", re.IGNORECASE)
_TRANSCRIPT_KEYS = {"transcript", "raw_transcript", "stdout", "stderr", "rendered_prompt"}
_IDENTITY_KEYS = {"username", "user_name", "personal_name", "full_name", "email"}

_CONTRACT_COMPONENT_BYTES = b"synthetic controller component bytes for contract validation\n"
_CONTRACT_INVENTORY_BYTES = b"synthetic installed inventory fixture for contract validation\n"
_CONTRACT_COMPONENT_SHA256 = hashlib.sha256(_CONTRACT_COMPONENT_BYTES).hexdigest()
_CONTRACT_INVENTORY_SHA256 = hashlib.sha256(_CONTRACT_INVENTORY_BYTES).hexdigest()
_CONTRACT_COMPONENT_ID = "farmboy-controllers"
_CONTRACT_COMPONENT_VERSION = "fixture-version-1"
_CONTRACT_CLI_VERSION = "fixture-cli-version-not-executed"
_CONTRACT_RUNTIME_VERSION = sys.version.split()[0]
_CONTROLLER_SIBLING_MODULES = ("implementation_scope", "phase_lifecycle", "selection", "readiness")


def _load_controller_module_isolated(name: str, path: Path) -> object:
    """Load a source or installed controller without borrowing sibling modules from another tree."""
    previous_modules = {module_name: sys.modules.pop(module_name, None)
                        for module_name in _CONTROLLER_SIBLING_MODULES}
    previous_path = sys.path[:]
    try:
        sys.path.insert(0, str(path.parent))
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise AssertionError(f"controller cannot be loaded: {path.name}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = previous_path
        for module_name, module in previous_modules.items():
            if module is None:
                sys.modules.pop(module_name, None)
            else:
                sys.modules[module_name] = module


def _load_sibling_module_cache(module_dir: Path) -> dict[str, object]:
    """Load one runtime's siblings as a cache precondition and restore the caller's cache."""
    previous_modules = {module_name: sys.modules.pop(module_name, None)
                        for module_name in _CONTROLLER_SIBLING_MODULES}
    previous_path = sys.path[:]
    try:
        sys.path.insert(0, str(module_dir))
        loaded: dict[str, object] = {}
        for module_name in _CONTROLLER_SIBLING_MODULES:
            loaded[module_name] = importlib.import_module(module_name)
        return loaded
    finally:
        sys.path[:] = previous_path
        for module_name, module in previous_modules.items():
            if module is None:
                sys.modules.pop(module_name, None)
            else:
                sys.modules[module_name] = module


def _runtime_private_identifiers() -> set[str]:
    """Return host identity values for rejection without persisting them."""
    identifiers = {value.strip() for value in (os.environ.get("USER"), os.environ.get("LOGNAME"))
                   if value and value.strip()}
    try:
        account = pwd.getpwuid(os.getuid())
    except (KeyError, OSError):
        account = None
    if account is not None:
        if account.pw_name:
            identifiers.add(account.pw_name)
        gecos_name = account.pw_gecos.split(",", 1)[0].strip()
        if gecos_name:
            identifiers.add(gecos_name)
    return identifiers


def assert_portable_observation_contract(
        observation: dict[str, object], *, expected_provenance: dict[str, object]) -> None:
    """Reject incomplete or host-specific connected validation observations."""
    required = {
        "scenario_id", "requirement_ids", "environment_kind", "execution_mode", "provenance",
        "expected", "observed", "valid_control_id", "parity",
    }
    if not required <= observation.keys():
        raise AssertionError(f"portable observation is missing fields: {sorted(required - observation.keys())}")
    if not isinstance(observation["scenario_id"], str) or not observation["scenario_id"]:
        raise AssertionError("scenario_id must be a non-empty string")
    requirement_ids = observation["requirement_ids"]
    if (not isinstance(requirement_ids, list) or not requirement_ids
            or any(not isinstance(item, str) or not _REQUIREMENT_ID_PATTERN.fullmatch(item)
                   for item in requirement_ids)):
        raise AssertionError("requirement_ids must contain FR/SC identifiers")
    if observation["environment_kind"] != "contract-fixture":
        raise AssertionError("environment_kind must identify this as a contract fixture")
    if observation["execution_mode"] != "contract-only-synthetic-fixture":
        raise AssertionError("execution_mode must not imply workflow execution")

    provenance = observation["provenance"]
    if not isinstance(provenance, dict):
        raise AssertionError("provenance must be an object")
    if provenance.get("source_repository") != "pegagio/farmboy":
        raise AssertionError("source_repository must identify the reviewed repository")
    if provenance.get("provenance_kind") != "synthetic-contract-fixture":
        raise AssertionError("provenance_kind must identify synthetic contract data")
    if not isinstance(provenance.get("source_commit"), str) or not _COMMIT_PATTERN.fullmatch(
            provenance["source_commit"]):
        raise AssertionError("source_commit must have the required identifier form")
    if not isinstance(provenance.get("source_dirty"), bool):
        raise AssertionError("source_dirty must be a boolean")
    coordinates = provenance.get("source_coordinates")
    if (not isinstance(coordinates, list) or not coordinates
            or any(not isinstance(path, str) or not path or path.startswith("/")
                   or "\\" in path or re.match(r"^[A-Za-z]:", path)
                   or ".." in Path(path).parts for path in coordinates)):
        raise AssertionError("source_coordinates must be repository-relative paths")
    components = provenance.get("components")
    if not isinstance(components, list) or not components:
        raise AssertionError("components must identify every component used")
    for component in components:
        if not isinstance(component, dict) or not all(
                isinstance(component.get(key), str) and component[key]
                for key in ("id", "version")):
            raise AssertionError("each component requires an ID and observed version")
        if not isinstance(component.get("source_sha256"), str) or not _SHA256_PATTERN.fullmatch(
                component["source_sha256"]):
            raise AssertionError("each component requires its raw source SHA-256")
    if provenance.get("inventory_kind") != "synthetic-contract-fixture":
        raise AssertionError("inventory_kind must identify a synthetic fixture, not installed execution")
    if not isinstance(provenance.get("inventory_sha256"), str) or not _SHA256_PATTERN.fullmatch(
            provenance["inventory_sha256"]):
        raise AssertionError("inventory_sha256 must be a SHA-256 digest")
    for field in ("tested_cli_version", "python_version"):
        if not isinstance(provenance.get(field), str) or not provenance[field]:
            raise AssertionError(f"{field} must record the tested runtime")

    for field in ("expected", "observed"):
        result = observation[field]
        if not isinstance(result, dict) or not isinstance(result.get("decision"), str):
            raise AssertionError(f"{field} must record a decision")
    if observation["expected"].get("decision") not in {"continue", "blocked"}:
        raise AssertionError("expected decision must be continue or blocked")
    observed = observation["observed"]
    if not isinstance(observed.get("reason_code"), str) or not observed["reason_code"]:
        raise AssertionError("observed result must record a reason_code")
    for field in ("selected_step_ids", "prevented_step_ids"):
        if not isinstance(observed.get(field), list) or any(
                not isinstance(item, str) or not item for item in observed[field]):
            raise AssertionError(f"observed {field} must contain non-empty step ID strings")
    for field in ("effects", "dispatches"):
        if not isinstance(observed.get(field), list) or any(
                not isinstance(item, dict) for item in observed[field]):
            raise AssertionError(f"observed {field} must contain objects")
    for field in ("source_effect_count", "dispatch_count"):
        if type(observed.get(field)) is not int or observed[field] < 0:
            raise AssertionError(f"observed {field} must be a non-negative integer")
    if observed["decision"] == "blocked":
        if not isinstance(observed.get("resume_action"), str) or not observed["resume_action"]:
            raise AssertionError("blocked observations must record a resume_action")
    if not isinstance(observation["valid_control_id"], str) or not observation["valid_control_id"]:
        raise AssertionError("negative observations must retain their valid-control reference")
    parity = observation["parity"]
    if not isinstance(parity, dict) or parity.get("result") not in {"match", "mismatch"}:
        raise AssertionError("parity must record a source/installed comparison result")

    expected_components = expected_provenance.get("components")
    if not isinstance(expected_components, dict):
        raise AssertionError("independent component byte expectations are required")
    for component in components:
        expected_component = expected_components.get(component["id"])
        if not isinstance(expected_component, dict) or any(
                component.get(field) != expected_component.get(field)
                for field in ("version", "source_sha256")):
            raise AssertionError("component identity/version/raw digest differs from fixture bytes")
    if provenance.get("inventory_sha256") != expected_provenance.get("inventory_sha256"):
        raise AssertionError("inventory digest differs from independent fixture bytes")
    if provenance.get("tested_cli_version") != expected_provenance.get("tested_cli_version"):
        raise AssertionError("CLI version differs from independent fixture metadata")
    if provenance.get("python_version") != expected_provenance.get("python_version"):
        raise AssertionError("runtime version differs from independent fixture metadata")

    def visit(value: object, key: str = "") -> None:
        if key.lower() in _TRANSCRIPT_KEYS:
            raise AssertionError("portable observation must not include transcripts or raw process output")
        if key.lower() in _IDENTITY_KEYS:
            raise AssertionError("portable observation must not include personal identifiers")
        if re.search(r"secret|token|credential|password", key, re.IGNORECASE):
            raise AssertionError("portable observation must not include secret-bearing fields")
        if isinstance(value, dict):
            for child_key, child in value.items():
                visit(child, str(child_key))
        elif isinstance(value, list):
            for child in value:
                visit(child, key)
        elif isinstance(value, str):
            folded = value.casefold()
            if any(identifier.casefold() in folded for identifier in _runtime_private_identifiers()):
                raise AssertionError("portable observation contains a host personal identifier")
            if (_ABSOLUTE_HOST_PATH_PATTERN.search(value) or _EMAIL_PATTERN.search(value)
                    or _SECRET_PATTERN.search(value)):
                raise AssertionError("portable observation contains host-specific or sensitive data")

    visit(observation)


def _portable_observation_contract_fixture() -> dict[str, object]:
    """Build contract-only values; this fixture is not an executed observation."""
    return {
        "scenario_id": "contract-fixture-reviewed-task-reentry",
        "requirement_ids": ["FR-015", "FR-016", "SC-007"],
        "environment_kind": "contract-fixture",
        "execution_mode": "contract-only-synthetic-fixture",
        "provenance": {
            "source_repository": "pegagio/farmboy",
            "provenance_kind": "synthetic-contract-fixture",
            "source_commit": "a" * 40,
            "source_dirty": False,
            "source_coordinates": ["tests/test_snapshot_validation.py"],
            "components": [{
                "id": _CONTRACT_COMPONENT_ID,
                "version": _CONTRACT_COMPONENT_VERSION,
                "source_sha256": _CONTRACT_COMPONENT_SHA256,
            }],
            "inventory_kind": "synthetic-contract-fixture",
            "inventory_sha256": _CONTRACT_INVENTORY_SHA256,
            "tested_cli_version": _CONTRACT_CLI_VERSION,
            "python_version": _CONTRACT_RUNTIME_VERSION,
        },
        "expected": {"decision": "continue"},
        "observed": {
            "decision": "continue", "reason_code": "contract-fixture-only",
            "selected_step_ids": ["fixture-selected"], "prevented_step_ids": [],
            "source_effect_count": 1, "dispatch_count": 1,
            "effects": [{"step_id": "fixture-selected", "outcome": "simulated"}],
            "dispatches": [{"step_id": "fixture-selected", "mode": "deterministic"}],
        },
        "valid_control_id": "contract-fixture-positive-control",
        "parity": {"result": "match", "counterpart_environment_kind": "source"},
    }


class PortableObservationContractTests(unittest.TestCase):
    """Validate the portable observation shape independently of the future writer."""

    def test_contract_acceptsCompletePortableFixture(self) -> None:
        observation = _portable_observation_contract_fixture()
        assert_portable_observation_contract(observation, expected_provenance={
            "components": {_CONTRACT_COMPONENT_ID: {
                "version": _CONTRACT_COMPONENT_VERSION,
                "source_sha256": hashlib.sha256(_CONTRACT_COMPONENT_BYTES).hexdigest(),
            }},
            "inventory_sha256": hashlib.sha256(_CONTRACT_INVENTORY_BYTES).hexdigest(),
            "tested_cli_version": _CONTRACT_CLI_VERSION,
            "python_version": _CONTRACT_RUNTIME_VERSION,
        })

    def test_contractRejectsSingleFieldPortabilityViolations(self) -> None:
        expected_provenance = {
            "components": {_CONTRACT_COMPONENT_ID: {
                "version": _CONTRACT_COMPONENT_VERSION,
                "source_sha256": hashlib.sha256(_CONTRACT_COMPONENT_BYTES).hexdigest(),
            }},
            "inventory_sha256": hashlib.sha256(_CONTRACT_INVENTORY_BYTES).hexdigest(),
            "tested_cli_version": _CONTRACT_CLI_VERSION,
            "python_version": _CONTRACT_RUNTIME_VERSION,
        }
        mutations = (
            ("source_coordinates", "(/home/synthetic-user/project/controller.py)"),
            ("windows_source_coordinates", "(C:/synthetic-user/controller.py)"),
            ("scenario_id", ""),
            ("requirement_ids", ["not-a-requirement"]),
            ("component-source_sha256", "0" * 64),
            ("inventory_sha256", "0" * 64),
            ("tested_cli_version", "fixture-cli-version-forged"),
            ("observed-effects", [42]),
            ("observed-selected-step", [42]),
            ("boolean-source_effect_count", True),
            ("negative-dispatch_count", -1),
            ("missing-reason_code", None),
            ("blocked-without-resume_action", None),
            ("valid_control_id", ""),
            ("parity-result", "unknown"),
            ("ordinary-string-private-identifier", None),
            ("email", "synthetic.person@example.invalid"),
            ("synthetic_secret", "synthetic-secret-value"),
            ("raw-transcript", "synthetic transcript content"),
        )
        for mutation, value in mutations:
            with self.subTest(mutation=mutation):
                observation = _portable_observation_contract_fixture()
                assert_portable_observation_contract(observation, expected_provenance=expected_provenance)
                mutated = json.loads(json.dumps(observation))
                if mutation == "source_coordinates":
                    mutated["provenance"]["source_coordinates"] = [value]
                elif mutation == "windows_source_coordinates":
                    mutated["provenance"]["source_coordinates"] = [value]
                elif mutation == "component-source_sha256":
                    mutated["provenance"]["components"][0]["source_sha256"] = value
                elif mutation == "inventory_sha256":
                    mutated["provenance"]["inventory_sha256"] = value
                elif mutation == "tested_cli_version":
                    mutated["provenance"][mutation] = value
                elif mutation == "observed-effects":
                    mutated["observed"]["effects"] = value
                elif mutation == "observed-selected-step":
                    mutated["observed"]["selected_step_ids"] = value
                elif mutation == "boolean-source_effect_count":
                    mutated["observed"]["source_effect_count"] = value
                elif mutation == "negative-dispatch_count":
                    mutated["observed"]["dispatch_count"] = value
                elif mutation == "missing-reason_code":
                    mutated["observed"].pop("reason_code")
                elif mutation == "blocked-without-resume_action":
                    mutated["observed"]["decision"] = "blocked"
                    mutated["observed"]["resume_action"] = value
                elif mutation == "parity-result":
                    mutated["parity"]["result"] = value
                elif mutation == "ordinary-string-private-identifier":
                    private_identifier = next(iter(_runtime_private_identifiers()))
                    mutated["observed"]["note"] = f"synthetic note {private_identifier} retained"
                elif mutation == "synthetic_secret":
                    mutated["observed"]["synthetic_secret"] = value
                elif mutation == "email":
                    mutated["provenance"]["contact"] = value
                elif mutation == "raw-transcript":
                    mutated["observed"]["raw_transcript"] = value
                else:
                    mutated[mutation] = value
                with self.assertRaises(AssertionError):
                    assert_portable_observation_contract(mutated, expected_provenance=expected_provenance)


def extract_pinned_extension(extension_id: str, destination: Path) -> tuple[Path, dict[str, str]]:
    """Extract one checksum-verified release package into a temporary tree."""
    release = json.loads(RELEASE_PATH.read_text(encoding="utf-8"))
    entry = release["extensions"][extension_id]
    archive_path = ROOT / "catalog/packages" / entry["artifact"]
    if sha256(archive_path) != entry["sha256"]:
        raise AssertionError(f"release archive checksum differs for {extension_id}")
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            parts = Path(member.filename).parts
            if not parts or parts[0] != extension_id or ".." in parts:
                raise AssertionError(f"unsafe path in {extension_id} release archive")
            archive.extract(member, destination)
    source = destination / extension_id
    manifest = extension_manifest(source)
    if manifest.get("id") != extension_id or manifest.get("version") != entry["version"]:
        raise AssertionError(f"release metadata and manifest disagree for {extension_id}")
    return source, entry


def installed_payload_inventory(consumer: Path, agent_entries: list[dict[str, str]]) -> dict[str, object]:
    """Digest actual files owned by the installed bundle packages."""
    owned_roots = {
        "farmboy-controllers": [consumer / ".specify/farmboy"],
        "flow-roadmap": [consumer / ".specify/extensions/flow-roadmap"],
        "flow-wiki": [consumer / ".specify/extensions/flow-wiki"],
        "farmboy-feedback": [consumer / ".specify/extensions/farmboy-feedback"],
    }
    paths: dict[str, str] = {}
    components: dict[str, str] = {}
    for component_id, roots in owned_roots.items():
        for root in roots:
            if not root.is_dir():
                raise AssertionError(f"installed component payload root is missing: {root.name}")
            for path in sorted(item for item in root.rglob("*") if item.is_file()):
                relative = path.relative_to(consumer).as_posix()
                paths[relative] = sha256(path)
                components[relative] = component_id
    for workflow_id in WORKFLOW_IDS:
        root = consumer / ".specify/workflows" / workflow_id
        if not root.is_dir():
            raise AssertionError(f"installed workflow payload is missing: {workflow_id}")
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            relative = path.relative_to(consumer).as_posix()
            paths[relative] = sha256(path)
            components[relative] = workflow_id
    for entry in agent_entries:
        path = consumer / entry["destination"]
        if not path.is_file():
            raise AssertionError(f"installed agent payload is missing: {entry['destination']}")
        relative = path.relative_to(consumer).as_posix()
        paths[relative] = sha256(path)
        components[relative] = "farmboy-agents"
    for skill_id in ("farmboy-select-feature", "farmboy-specify", "farmboy-clarify",
                     "farmboy-plan", "farmboy-tasks", "farmboy-analyze-remediate",
                     "farmboy-implement", "farmboy-converge", "farmboy-closeout",
                     "farmboy-wiki-lint-update"):
        root = consumer / ".agents/skills" / skill_id
        if not root.is_dir():
            raise AssertionError(f"installed launched skill is missing: {skill_id}")
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            relative = path.relative_to(consumer).as_posix()
            paths[relative] = sha256(path)
            components[relative] = "farmboy-controllers"
    return {"owned_files": [{"path": path, "component_id": components[path], "sha256": paths[path]}
                            for path in sorted(paths)],
            "owned_file_count": len(paths), "owned_payload_sha256": paths}


class SnapshotValidationTests(unittest.TestCase):
    """Install, refresh, and remove a snapshot without damaging consumer data."""

    def test_snapshotLifecycle_preservesConsumerFilesAndRecordsProvenance(self) -> None:
        real_roadmap = ROOT / ".specify/memory/roadmap.md"
        real_roadmap_sha_before = sha256(real_roadmap)
        specify_path = shutil.which(SPECIFY_BIN)
        if specify_path is None:
            self.fail(f"required Specify CLI not found: {SPECIFY_BIN}")

        with tempfile.TemporaryDirectory(prefix="farmboy-snapshot-") as temporary:
            fixture = Path(temporary)
            consumer = fixture / "consumer"
            consumer.mkdir()
            home = fixture / "home"
            home.mkdir()

            roadmap_location = os.environ.get("FLOW_ROADMAP_SOURCE")
            if not roadmap_location:
                self.fail("FLOW_ROADMAP_SOURCE is required for installed lifecycle parity")
            roadmap_source = Path(roadmap_location).resolve()
            roadmap_manifest = extension_manifest(roadmap_source)
            bundle_manifest = yaml.safe_load(BUNDLE_PATH.read_text(encoding="utf-8"))
            roadmap_pin = next(item["version"] for item in bundle_manifest["provides"]["extensions"]
                               if item["id"] == ROADMAP_ID)
            if roadmap_manifest.get("id") != ROADMAP_ID or roadmap_manifest.get("version") != roadmap_pin:
                self.fail("explicit roadmap source does not match the reviewed bundle pin")
            wiki_source, wiki_release = extract_pinned_extension(WIKI_ID, fixture / "wiki")
            feedback_source = released_feedback_source(fixture / "feedback")
            sources = {ROADMAP_ID: roadmap_source, WIKI_ID: wiki_source, FEEDBACK_ID: feedback_source}
            with LocalCatalog(fixture / "catalog", sources) as local_catalog:
                environment = os.environ.copy()
                environment.update({
                    "HOME": str(home),
                    "SPECKIT_CATALOG_URL": local_catalog.extension_url,
                    "SPECKIT_WORKFLOW_CATALOG_URL": local_catalog.workflow_url,
                })

                def run_specify(*arguments: str) -> str:
                    completed = subprocess.run(
                        [specify_path, *arguments],
                        cwd=consumer,
                        env=environment,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        check=False,
                    )
                    self.assertEqual(0, completed.returncode, completed.stdout)
                    return completed.stdout

                def run_catalog(operation: str) -> str:
                    command = [sys.executable, str(ROOT / "tools/catalog.py"), operation, str(consumer)]
                    if operation in {"install", "refresh"}:
                        command.extend(["--dev", "--roadmap-source", str(roadmap_source)])
                    completed = subprocess.run(command, cwd=ROOT, env=environment, text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
                    self.assertEqual(0, completed.returncode, completed.stdout)
                    return completed.stdout

                cli_version = subprocess.run(
                    [specify_path, "--version"], text=True, capture_output=True, check=True
                ).stdout.strip()
                run_specify(
                    "init", "--here", "--force", "--non-interactive", "--integration", "codex",
                    "--integration-options=--skills",
                )

                consumer_files = {
                    consumer / "AGENTS.md": "# Consumer guidance\nKeep this file.\n",
                    consumer / ".codex/agents/coder.toml": 'name = "Coder"\ndescription = "Consumer-owned"\n',
                    consumer / ".codex/agents/unrelated.toml": 'name = "Unrelated consumer agent"\n',
                    consumer / "specs/local/README.md": "Consumer-owned feature data.\n",
                    consumer / "unrelated/keep.txt": "Unrelated project file.\n",
                    consumer / ".worktreeinclude": ".agents/\n.specify/workflow-feedback/\n.specify/extensions/local-extension/\n",
                    consumer / ".agents/skills/consumer-owned/SKILL.md": "# Consumer skill\nPreserve this ignored payload.\n",
                    consumer / ".specify/workflow-feedback/observations.jsonl": '{"id":"consumer-owned"}\n',
                    consumer / ".specify/extensions/local-extension/owned.txt": "Unrelated local component.\n",
                    consumer / "consumer-config.toml": 'setting = "retained"\n',
                }
                for path, contents in consumer_files.items():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(contents, encoding="utf-8")
                consumer_hashes = {path: sha256(path) for path in consumer_files}
                agent_manifest = yaml.safe_load((ROOT / "agents/farmboy/manifest.yml").read_text(encoding="utf-8"))
                agent_entries = agent_manifest["agents"]
                self.assertEqual(9, len(agent_entries))
                source_agent_files = {
                    ROOT / "agents/farmboy" / entry["file"]: sha256(ROOT / "agents/farmboy" / entry["file"])
                    for entry in agent_entries
                }
                self.assertTrue(source_agent_files, "the source checkout should preserve its FarmBoy agent package configurations")
                run_specify("workflow", "add", "--dev", str(INDEPENDENT_WORKFLOW))
                unrelated_workflow = consumer / ".specify/workflows/independent-consumer-check/workflow.yml"
                self.assertTrue(unrelated_workflow.is_file())
                unrelated_hash = sha256(unrelated_workflow)

                catalog_install_output = run_catalog("install")
                installed_record = json.loads((consumer / ".specify/bundle-records.json").read_text(encoding="utf-8"))
                installed = installed_record["bundles"][0]
                self.assertEqual("farmboy", installed["bundle_id"])
                contributions = installed["contributed_components"]
                expected_components = {
                    ("extensions", ROADMAP_ID), ("extensions", WIKI_ID), ("extensions", FEEDBACK_ID),
                    *(('workflows', workflow_id) for workflow_id in WORKFLOW_IDS),
                }
                self.assertEqual(expected_components, {(item["kind"], item["id"]) for item in contributions})
                self.assertTrue(all(item.get("version") for item in contributions))
                self.assertEqual(consumer_hashes, {path: sha256(path) for path in consumer_files})

                catalog_refresh_output = run_catalog("refresh")
                refreshed = json.loads((consumer / ".specify/bundle-records.json").read_text(encoding="utf-8"))
                refreshed_contributions = refreshed["bundles"][0]["contributed_components"]
                self.assertEqual(
                    {(item["kind"], item["id"], item["version"]) for item in contributions},
                    {(item["kind"], item["id"], item["version"]) for item in refreshed_contributions},
                )
                self.assertEqual(consumer_hashes, {path: sha256(path) for path in consumer_files})
                self.assertEqual(source_agent_files, {path: sha256(path) for path in source_agent_files})
                self.assertEqual(unrelated_hash, sha256(unrelated_workflow))
                installed_inventory = installed_payload_inventory(consumer, agent_entries)

                installed_controller_path = consumer / ".specify/farmboy/scripts/python/controller.py"
                installed_scope_path = consumer / ".specify/farmboy/scripts/python/implementation_scope.py"
                installed_implement_path = consumer / ".specify/workflows/farmboy-implement/workflow.yml"
                installed_lifecycle_paths = {
                    "controller_manifest": consumer / ".specify/farmboy/manifest.yml",
                    "controller": installed_controller_path,
                    "phase_lifecycle": consumer / ".specify/farmboy/scripts/python/phase_lifecycle.py",
                    "specify_workflow": consumer / ".specify/workflows/farmboy-specify/workflow.yml",
                    "implement_workflow": installed_implement_path,
                    "closeout_workflow": consumer / ".specify/workflows/farmboy-closeout/workflow.yml",
                }
                self.assertTrue(installed_controller_path.is_file(),
                                f"installed controller missing; found={list(consumer.rglob('controller.py'))}")
                self.assertTrue(installed_scope_path.is_file())
                self.assertTrue(installed_implement_path.is_file())
                for path in installed_lifecycle_paths.values():
                    self.assertTrue(path.is_file(), f"installed lifecycle payload missing: {path.name}")
                source_controller_path = ROOT / "controllers/farmboy/scripts/python/controller.py"
                source_modules_dir = source_controller_path.parent
                surrounding_modules = {name: sys.modules.get(name) for name in _CONTROLLER_SIBLING_MODULES}
                try:
                    source_preloaded = _load_sibling_module_cache(source_modules_dir)
                    sys.modules.update(source_preloaded)
                    source_preloaded_identities = {name: sys.modules[name] for name in _CONTROLLER_SIBLING_MODULES}
                    installed_controller = _load_controller_module_isolated(
                        "snapshot_installed_controller", installed_controller_path)
                    self.assertTrue(
                        all(sys.modules.get(name) is module
                            for name, module in source_preloaded_identities.items()),
                        "installed loading must restore the source-preloaded sibling cache identities",
                    )
                    self.assertTrue(installed_controller.workflow_lifecycle_check.__globals__["__file__"].endswith(
                        ".specify/farmboy/scripts/python/phase_lifecycle.py"))

                    installed_preloaded = _load_sibling_module_cache(installed_controller_path.parent)
                    sys.modules.update(installed_preloaded)
                    installed_preloaded_identities = {
                        name: sys.modules[name] for name in _CONTROLLER_SIBLING_MODULES}
                    source_controller = _load_controller_module_isolated(
                        "snapshot_source_controller", source_controller_path)
                    self.assertTrue(
                        all(sys.modules.get(name) is module
                            for name, module in installed_preloaded_identities.items()),
                        "source loading must restore the installed-preloaded sibling cache identities",
                    )
                    self.assertTrue(source_controller.workflow_lifecycle_check.__globals__["__file__"].endswith(
                        "controllers/farmboy/scripts/python/phase_lifecycle.py"))
                finally:
                    for name, module in surrounding_modules.items():
                        if module is None:
                            sys.modules.pop(name, None)
                        else:
                            sys.modules[name] = module
                self.assertTrue(
                    all(sys.modules.get(name) is module for name, module in surrounding_modules.items()),
                    "source/installed loading must restore the caller's original sibling cache identities",
                )
                installed_scope = installed_controller.implementation_scope_module
                source_consumer = fixture / "source-consumer"
                shutil.copytree(consumer, source_consumer)
                matrix = exercise_installed_scope_matrix(
                    consumer, installed_controller, installed_scope,
                    ROOT / "tests/consumer-fixtures/workflow-improvements/implementation-scope-cases.json",
                    installed_implement_path,
                )
                source_workflow_path = source_consumer / ".specify/workflows/farmboy-implement/workflow.yml"
                shutil.copy2(ROOT / "workflows/farmboy-implement/workflow.yml", source_workflow_path)
                scenarios = json.loads(
                    (ROOT / "tests/consumer-fixtures/workflow-improvements/implementation-scope-cases.json")
                    .read_text(encoding="utf-8"))["feature_023"]["scenarios"]
                scenario_by_id = {scenario["id"]: scenario for scenario in scenarios}

                def branch_contract(controller: object) -> dict[str, object]:
                    """Observe source or installed branch behavior through production APIs."""
                    observations: dict[str, object] = {}
                    for case_id in ("F023-ROUTE-PREPARATION-SKIP-CONTROL",
                                    "F023-ROUTE-SOURCE-SKIP-CONTROL",
                                    "F023-ROUTE-EMPTY-DEFAULT-CONTROL"):
                        scenario = scenario_by_id[case_id]
                        expected = scenario["expected_production_outcome"]
                        if case_id == "F023-ROUTE-PREPARATION-SKIP-CONTROL":
                            switch = {"id": "route", "type": "switch", "cases": {
                                "prepare": [{"id": "prepare"}], "source": [{"id": "source"}]}, "default": []}
                            choice = "source"
                        elif case_id == "F023-ROUTE-SOURCE-SKIP-CONTROL":
                            switch = {"id": "route", "type": "switch", "cases": {
                                "prepare": [{"id": "prepare"}], "source": [{"id": "source"}]}, "default": []}
                            choice = "prepare"
                        else:
                            switch = {"id": "route", "type": "switch", "cases": {
                                "run": [{"id": "child"}]}, "default": []}
                            choice = scenario["input"]["route_choice"]
                        selected = controller.select_switch_branch(switch, choice)
                        observations[case_id] = {"result": "continue",
                            "selected": [step["id"] for step in selected],
                            "prevented": [step["id"] for step in
                                          [child for branch in switch["cases"].values() for child in branch]
                                          if step not in selected],
                            "effects": [step["id"] for step in selected]}
                        self.assertEqual(expected["selected"], observations[case_id]["selected"])
                        self.assertEqual(expected["prevented"], observations[case_id]["prevented"])

                    # Exercise an explicitly selected empty case independently of
                    # the empty-default scenario above. Expected selection and
                    # effects are authored here rather than derived from routing.
                    empty_case_id = "F023-ROUTE-EMPTY-CASE-CONTROL"
                    empty_case_switch = {"id": "route", "type": "switch", "cases": {
                        "skip": [], "run": [{"id": "child"}]}, "default": []}
                    empty_case_selected = controller.select_switch_branch(empty_case_switch, "skip")
                    observations[empty_case_id] = {"result": "continue",
                        "selected": [step["id"] for step in empty_case_selected],
                        "prevented": [child["id"] for branch in empty_case_switch["cases"].values()
                                      for child in branch if child not in empty_case_selected],
                        "effects": [step["id"] for step in empty_case_selected]}
                    self.assertEqual([], observations[empty_case_id]["selected"])
                    self.assertEqual(["child"], observations[empty_case_id]["prevented"])
                    self.assertEqual([], observations[empty_case_id]["effects"])

                    unknown = scenario_by_id["F023-ROUTE-UNKNOWN-WITHOUT-FALLBACK"]
                    try:
                        controller.select_switch_branch(
                            {"id": "route", "type": "switch", "cases": {"run": [{"id": "child"}]}},
                            unknown["input"]["route_choice"])
                    except ValueError:
                        observations[unknown["id"]] = {"result": "block", "selected": [], "effects": []}
                    else:
                        self.fail("unknown route choice without fallback was accepted")

                    valid_definition = {"workflow": {"id": "fixture-branch-validation", "version": "1"},
                        "inputs": {"choice": {"required": True, "type": "string"}},
                        "steps": [{"id": "produce", "type": "command"},
                            {"id": "route", "type": "switch", "expression": "{{ inputs.choice }}",
                             "cases": {"skip": [], "consume": [{"id": "consume", "type": "prompt",
                                 "prompt": "Use {{ steps.produce.output.value }}"}]}, "default": []},
                            {"id": "later", "type": "command"}]}
                    controller.validate_workflow_definition(valid_definition)
                    definition_cases = {
                        "F023-DEF-NESTED-DEFAULT": lambda value: value["steps"][1]["cases"].update({"default": []}),
                        "F023-DEF-MALFORMED-CASES": lambda value: value["steps"][1].update({"cases": []}),
                        "F023-DEF-FORWARD-PRODUCER": lambda value: value["steps"][1]["cases"]["consume"][0].update(
                            {"prompt": "Use {{ steps.later.output.value }}"}),
                    }
                    for case_id, mutate in definition_cases.items():
                        mutated = json.loads(json.dumps(valid_definition))
                        mutate(mutated)
                        try:
                            controller.validate_workflow_definition(mutated)
                        except ValueError:
                            observations[case_id] = {"result": "reject", "effects": []}
                        else:
                            self.fail(f"{case_id}: invalid workflow definition was accepted")

                    timing_id = "F023-INPUT-PRODUCER-TIMING-CONTROL"
                    controller.validate_workflow_definition(valid_definition)
                    _, selected = controller.render_selected_switch(
                        valid_definition["steps"][1], {"choice": "consume"}, {})
                    self.assertEqual("consume", selected[0]["id"])
                    try:
                        controller.render_template(selected[0], {}, {})
                    except ValueError:
                        before_production = "blocked-at-consumption"
                    else:
                        self.fail("producer-dependent input rendered before its output existed")
                    consumed = controller.render_template(selected[0], {}, {"produce": {"value": "fresh"}})
                    observations[timing_id] = {"definition_result": "accept",
                        "before_production": before_production, "after_production": consumed["prompt"],
                        "result": "continue", "effects": ["consumer-dispatch"]}
                    self.assertEqual("accept", scenario_by_id[timing_id]["expected_production_outcome"][
                        "definition_result"])
                    return observations

                source_branch_observations = branch_contract(source_controller)
                installed_branch_observations = branch_contract(installed_controller)
                self.assertEqual(source_branch_observations, installed_branch_observations)

                # Prove both paired controllers' assertion path detects the
                # same single-condition production defect: an undeclared child
                # appears only when an explicit empty case is selected.
                for controller_name, branch_controller in (
                        ("source", source_controller), ("installed", installed_controller)):
                    original_select_switch_branch = branch_controller.select_switch_branch

                    def select_with_empty_case_mutation(switch: dict[str, object], choice: str,
                                                        original=original_select_switch_branch):
                        if choice == "skip" and switch.get("cases", {}).get("skip") == []:
                            return [{"id": "undeclared-empty-case-child"}]
                        return original(switch, choice)

                    try:
                        branch_controller.select_switch_branch = select_with_empty_case_mutation
                        with self.assertRaises(AssertionError):
                            branch_contract(branch_controller)
                    finally:
                        branch_controller.select_switch_branch = original_select_switch_branch

                source_matrix = exercise_installed_scope_matrix(
                    source_consumer, source_controller, source_controller.implementation_scope_module,
                    ROOT / "tests/consumer-fixtures/workflow-improvements/implementation-scope-cases.json",
                    source_workflow_path,
                )
                self.assertEqual(sha256(ROOT / "controllers/farmboy/scripts/python/controller.py"),
                                 sha256(installed_controller_path))
                self.assertEqual(sha256(ROOT / "controllers/farmboy/scripts/python/implementation_scope.py"),
                                 sha256(installed_scope_path))
                self.assertEqual(sha256(ROOT / "workflows/farmboy-implement/workflow.yml"),
                                 sha256(installed_implement_path))

                def trace_decisions(result: dict[str, object]) -> dict[str, object]:
                    """Project source and installed traces onto comparable controller decisions."""
                    details = result["details"]
                    return {"expected": result["expected"], "observed": result["observed"],
                            "sequence": result["sequence"],
                            "selected_steps": details["selected_steps"],
                            "prevented_steps": details["prevented_steps"],
                            "current_review_evidence_rechecked": details["current_review_evidence_rechecked"],
                            "history_counters": details["history_counters"],
                            "guarded_reentry": details["guarded_reentry"],
                            "prohibited_effect_counts": details["prohibited_effect_counts"],
                            "negative_traces": [{key: negative.get(key) for key in (
                                "id", "valid_control_id", "production_state", "blocker", "reason_code",
                                "resume_action", "production_resume_action", "fixture_safe_action",
                                "later_source_dispatches", "selected_steps", "prevented_steps",
                                "counters_before", "counters_after", "fallback", "history_reconstructed",
                                "budget_reset")}
                                for negative in details["negative_traces"]]}

                def lifecycle_readback_decisions(result: dict[str, object]) -> dict[str, object]:
                    """Assert the lifecycle readback contract supplied by the T018 disposable adapter."""
                    observation = result.get("lifecycle_receipt_readback")
                    self.assertIsInstance(observation, dict,
                                          "snapshot adapter must expose lifecycle receipt-readback evidence")
                    self.assertEqual(observation["effect_identity_before"], observation["effect_identity_after"])
                    self.assertEqual(observation["receipt_identity_before"], observation["receipt_identity_after"])
                    self.assertEqual(observation["receipt_timestamp_before"], observation["receipt_timestamp_after"])
                    self.assertTrue(observation["receipt_timestamp_after"])
                    self.assertEqual(observation["receipt_sha256_before"], observation["receipt_sha256_after"])
                    self.assertRegex(observation["receipt_sha256_after"], r"^[0-9a-f]{64}$")
                    self.assertEqual("verified", observation["reassessment_state"])
                    self.assertEqual("verified", observation["subprocess_runtime_state"])
                    self.assertEqual(1, observation["writer_invocations_before_readback"])
                    self.assertEqual(1, observation["writer_invocations_after_readback"])
                    self.assertEqual(observation["roadmap_mutation_count_before_reassessment"],
                                     observation["roadmap_mutation_count_after_reassessment"])
                    self.assertEqual("blocked", observation["non_roadmap_artifact_mutation_state"])
                    self.assertEqual("post-effect-source-changed",
                                     observation["non_roadmap_artifact_reason_code"])
                    return {key: observation[key] for key in (
                        "reassessment_state", "roadmap_mutation_count_before_reassessment",
                        "roadmap_mutation_count_after_reassessment", "writer_invocations_before_readback",
                        "writer_invocations_after_readback", "non_roadmap_artifact_mutation_state",
                        "non_roadmap_artifact_reason_code")}

                source_traces = source_matrix["connected_positive_traces"]
                installed_traces = matrix["connected_positive_traces"]
                source_lifecycle = source_matrix["lifecycle_receipt_readback"]
                installed_lifecycle = matrix["lifecycle_receipt_readback"]
                self.assertTrue(source_lifecycle["module_origin"].startswith(
                    "controllers/farmboy/scripts/python/phase_lifecycle.py"))
                self.assertTrue(installed_lifecycle["module_origin"].startswith(
                    ".specify/farmboy/scripts/python/phase_lifecycle.py"))
                self.assertTrue(source_lifecycle["controller_runtime_origin"].startswith(
                    "controllers/farmboy/scripts/python/controller.py"))
                self.assertTrue(installed_lifecycle["controller_runtime_origin"].startswith(
                    ".specify/farmboy/scripts/python/controller.py"))
                self.assertEqual(sha256(ROOT / "controllers/farmboy/scripts/python/phase_lifecycle.py"),
                                 source_lifecycle["module_sha256"])
                self.assertEqual(sha256(consumer / ".specify/farmboy/scripts/python/phase_lifecycle.py"),
                                 installed_lifecycle["module_sha256"])
                self.assertEqual(source_lifecycle["module_sha256"], installed_lifecycle["module_sha256"])
                self.assertEqual(sha256(ROOT / "controllers/farmboy/scripts/python/controller.py"),
                                 source_lifecycle["controller_runtime_sha256"])
                self.assertEqual(sha256(consumer / ".specify/farmboy/scripts/python/controller.py"),
                                 installed_lifecycle["controller_runtime_sha256"])
                evidence_path = os.environ.get("FARMBOY_T018_EVIDENCE_PATH")
                if evidence_path:
                    evidence_fields = (
                        "scenario_id", "module_origin", "module_sha256", "controller_runtime_origin",
                        "controller_runtime_sha256", "subprocess_runtime_state", "effect_identity_before",
                        "effect_identity_after", "receipt_identity_before", "receipt_identity_after",
                        "receipt_timestamp_before", "receipt_timestamp_after", "receipt_sha256_before",
                        "receipt_sha256_after", "roadmap_preimage_sha256", "retained_roadmap_sha256",
                        "roadmap_mutation_count_before_reassessment",
                        "roadmap_mutation_count_after_reassessment", "writer_invocations_before_readback",
                        "writer_invocations_after_readback", "reassessment_state",
                        "non_roadmap_artifact_mutation_state", "non_roadmap_artifact_reason_code",
                        "non_roadmap_artifact_path", "non_roadmap_sha256_before", "non_roadmap_sha256_after")
                    evidence = {"schema_version": "1.0", "scenario_id": "F023-LIFECYCLE-APPLIED-ROADMAP-READBACK",
                        "execution_mode": "deterministic-production-api-fixture",
                        "reviewer_assessments_are_fixture_inputs": True,
                        "source": {key: source_lifecycle[key] for key in evidence_fields},
                        "installed": {key: installed_lifecycle[key] for key in evidence_fields},
                        "source_controller_sha256": sha256(ROOT / "controllers/farmboy/scripts/python/controller.py"),
                        "installed_controller_sha256": sha256(installed_controller_path),
                        "source_scope_sha256": sha256(ROOT / "controllers/farmboy/scripts/python/implementation_scope.py"),
                        "installed_scope_sha256": sha256(installed_scope_path),
                        "source_workflow_sha256": sha256(ROOT / "workflows/farmboy-implement/workflow.yml"),
                        "installed_workflow_sha256": sha256(installed_implement_path)}
                    evidence_file = Path(evidence_path)
                    evidence_file.parent.mkdir(parents=True, exist_ok=True)
                    evidence_file.write_text(json.dumps(evidence, sort_keys=True, indent=2) + "\n", encoding="utf-8")
                self.assertEqual(lifecycle_readback_decisions(source_matrix),
                                 lifecycle_readback_decisions(matrix))
                self.assertEqual(real_roadmap_sha_before, sha256(real_roadmap),
                                 "disposable lifecycle parity must leave the project roadmap untouched")
                self.assertEqual(set(source_traces), set(installed_traces))
                for trace_id in sorted(source_traces):
                    with self.subTest(source_installed_trace=trace_id):
                        source_trace = source_traces[trace_id]
                        installed_trace = installed_traces[trace_id]
                        self.assertEqual("deterministic-installed-consumer", installed_trace["details"]["execution_mode"])
                        self.assertEqual(trace_decisions(source_trace), trace_decisions(installed_trace))
                        self.assertTrue(installed_trace["details"]["current_review_evidence_rechecked"])
                        self.assertEqual(0, installed_trace["details"]["prohibited_effect_counts"][
                            "workflow_or_phase_dispatch"])
                        self.assertEqual(0, installed_trace["details"]["prohibited_effect_counts"]["git_integration"])
                        self.assertEqual(0, installed_trace["details"]["prohibited_effect_counts"][
                            "real_roadmap_verification"])
                        self.assertEqual(0, installed_trace["details"]["prohibited_effect_counts"][
                            "feature_or_consumer_acceptance"])
                        fr009_ids = {
                            "F023-REENTRY-FORGED-HISTORY", "F023-REENTRY-ALTERED-HISTORY",
                            "F023-REENTRY-MISSING-HISTORY", "F023-REENTRY-UNBOUND-HISTORY",
                            "F023-REENTRY-STALE-REVIEW", "F023-REENTRY-UNAUTHORIZED-TASK-EDIT",
                            "F023-REENTRY-WRONG-BRANCH-OUTPUT", "F023-REENTRY-NO-SUBSTANTIVE-PROGRESS",
                            "F023-REENTRY-EXHAUSTED-LIMIT", "F023-REENTRY-EXHAUSTED-CODER-SESSIONS",
                        }
                        negatives = {negative["id"]: negative
                                     for negative in installed_trace["details"]["negative_traces"]}
                        if trace_id == "F023-POSITIVE-TASK-RESOLUTION-MARKER-ONLY":
                            self.assertTrue(fr009_ids <= set(negatives),
                                            f"{trace_id}: missing FR-009 observations "
                                            f"{sorted(fr009_ids - set(negatives))}")
                        for case_id in sorted(fr009_ids & set(negatives)):
                            negative = negatives[case_id]
                            scenario = scenario_by_id[case_id]
                            with self.subTest(negative_guard=case_id):
                                self.assertEqual(scenario["valid_control_id"], negative["valid_control_id"])
                                self.assertIsNotNone(scenario["mutation"])
                                self.assertEqual("blocked", negative["production_state"])
                                self.assertTrue(negative.get("blocker") or negative.get("reason_code"))
                                expected_action = scenario["expected_production_outcome"]["safe_action"]
                                self.assertEqual(expected_action, negative["fixture_safe_action"])
                                observed_action = negative.get("resume_action") or negative.get(
                                    "production_resume_action")
                                if observed_action is not None:
                                    self.assertIsInstance(observed_action, str)
                                self.assertEqual(0, negative["later_source_dispatches"])
                                self.assertEqual([], negative["selected_steps"])
                                self.assertTrue(negative["prevented_steps"])
                                self.assertEqual(negative["counters_before"], negative["counters_after"])
                                self.assertIs(negative["fallback"], False)
                                self.assertIs(negative["history_reconstructed"], False)
                                self.assertIs(negative["budget_reset"], False)
                self.assertEqual(15, len(matrix["cases"]))
                positive_fixture = json.loads(
                    (ROOT / "tests/consumer-fixtures/workflow-improvements/implementation-scope-cases.json")
                    .read_text(encoding="utf-8"))
                positive_traces = positive_fixture["connected_positive_traces"]
                self.assertEqual({"F023-POSITIVE-TASK-RESOLUTION-MARKER-ONLY",
                                  "F023-POSITIVE-REVIEWED-SOURCE-CORRECTION"},
                                 {trace["id"] for trace in positive_traces})
                positive_results = matrix.get("connected_positive_traces", {})
                self.assertEqual({trace["id"] for trace in positive_traces}, set(positive_results))
                self.assertEqual(2, len({trace["adapter_result_path"] for trace in positive_traces}))
                for trace in positive_traces:
                    with self.subTest(connected_positive_trace=trace["id"]):
                        self.assertEqual("deterministic-installed-consumer", trace["execution_mode"])
                        self.assertEqual(f"connected_positive_traces.{trace['id']}",
                                         trace["adapter_result_path"])
                        observed_trace = positive_results.get(trace["id"])
                        self.assertIsNotNone(observed_trace, trace["id"])
                        self.assertEqual(trace["adapter_result_path"], observed_trace["adapter_result_path"])
                        self.assertEqual(trace["sequence"], observed_trace["sequence"])
                        self.assertEqual(trace["expected"], observed_trace["observed"])
                for case in matrix["cases"]:
                    with self.subTest(scope_case=case["id"]):
                        self.assertEqual(case["expected_state"], case["observed_gate_state"])
                        dispatch = case["production_dispatch"]
                        self.assertEqual(dispatch["eligibility_request_sha256"],
                                         dispatch["eligibility_forwarded_payload_sha256"])
                        for call in case["generic_post_source_calls"]:
                            progress_dispatch = call["production_progress_dispatch"]
                            self.assertEqual(progress_dispatch["request_sha256"],
                                             progress_dispatch["forwarded_payload_sha256"])
                            self.assertEqual(progress_dispatch["rendered_prompt_sha256"],
                                             dispatch["rendered_route_scoped_execution_prompt_sha256"])
                question_case = next(case for case in matrix["cases"] if case["id"] == "SI004")
                self.assertEqual("needs-human", question_case["observed_gate_state"])
                self.assertEqual("continue", question_case["observed_route_state"])
                self.assertEqual("keep-requested-scope",
                                 question_case["operator_question"]["simulated_fixture_answer"]["answer"])
                self.assertEqual("installed-tasker-revision-successor-passed",
                                 matrix["task_revision_successor"]["result"])
                self.assertEqual("ready", matrix["task_revision_successor"]["scope_state"])
                self.assertEqual(["T003"], matrix["task_revision_successor"]["eligible_derived_task_ids"])
                self.assertEqual(["T003"], matrix["task_revision_successor"]["tracked_task_ids"])
                self.assertEqual("blocked", matrix["task_revision_successor"]["capture_project_argument_mutation_state"])
                capture_dispatch = matrix["task_revision_successor"]["capture_dispatch"]
                capture_request = capture_dispatch["request"]
                self.assertEqual("ready", capture_dispatch["result_state"])
                self.assertEqual(0, capture_dispatch["return_code"])
                self.assertEqual(list(POST_PASS_CAPTURE_FIELDS), capture_dispatch["request_fields"])
                self.assertEqual(["python3", ".specify/farmboy/scripts/python/controller.py",
                                  "post-pass-capture", "--project", "$PWD"],
                                 capture_dispatch["command_template"])
                self.assertTrue(capture_dispatch["project_argument_bound_to_consumer"])
                self.assertEqual(capture_dispatch["scope_sha256"], capture_dispatch["retained_scope_sha256"])
                self.assertEqual(capture_dispatch["scope_sha256"], capture_dispatch["eligibility_scope_sha256"])
                self.assertEqual(capture_dispatch["trusted_request_reference"],
                                 capture_dispatch["eligibility_trusted_request_reference"])
                self.assertEqual(capture_dispatch["retained_scope_sha256"],
                                 capture_dispatch["eligibility_retained_scope_sha256"])
                self.assertEqual("revise-task-plan",
                                 capture_request["producer_pairs"][0]["tasker_step_id"])
                self.assertEqual("validate-task-revision",
                                 capture_request["producer_pairs"][0]["validator_step_id"])
                self.assertEqual(capture_request["producer_pairs"][0]["validator_result"]["task_tracking_successor"],
                                 matrix["task_revision_successor"]["post_pass_state"]["task_tracking_successors"][0])
                self.assertFalse(capture_dispatch["completion_branch"])
                self.assertTrue(capture_dispatch["request_sha256"])
                self.assertEqual(set(POST_PASS_CAPTURE_FIELDS), set(capture_request))
                self.assertEqual(capture_dispatch["scope_sha256"], capture_request["scope"]["scope_sha256"])
                self.assertEqual(capture_dispatch["trusted_request_reference"],
                                 capture_request["trusted_request_reference"])
                self.assertEqual(capture_dispatch["entry_history_sha256"],
                                 capture_request["entry_history_sha256"])
                self.assertEqual(capture_dispatch["eligibility_request_sha256"],
                                 hashlib.sha256(json.dumps(capture_request["eligibility_request"], sort_keys=True,
                                                            separators=(",", ":"), ensure_ascii=False).encode()).hexdigest())
                installed_workflow_bytes = installed_implement_path.read_bytes()
                installed_workflow_text = installed_workflow_bytes.decode("utf-8")
                command_mutation = installed_workflow_text.replace(
                    '--project "$PWD"', "--project /nonexistent-capture-target", 1)
                self.assertNotEqual(installed_workflow_text, command_mutation,
                                    "installed production capture command should expose its project argument")
                try:
                    installed_implement_path.write_text(command_mutation, encoding="utf-8")
                    mutated_prompt = yaml.safe_load(installed_implement_path.read_text(encoding="utf-8"))

                    def find_capture_prompt(steps: list[dict[str, object]]) -> str:
                        for step in steps:
                            if step.get("id") == "capture-post-pass-state":
                                return str(step["prompt"])
                            nested = step.get("steps", [])
                            if isinstance(nested, list):
                                try:
                                    return find_capture_prompt(nested)
                                except StopIteration:
                                    pass
                            for branch in step.get("cases", {}).values():
                                if isinstance(branch, list):
                                    try:
                                        return find_capture_prompt(branch)
                                    except StopIteration:
                                        pass
                        raise StopIteration("capture-post-pass-state")

                    mutated_command = _capture_post_pass_command(find_capture_prompt(mutated_prompt["steps"]))
                    mutated_result = subprocess.run(mutated_command, cwd=consumer,
                        input=json.dumps(capture_request), text=True, capture_output=True, check=False)
                    self.assertNotEqual(0, mutated_result.returncode)
                    self.assertEqual("blocked", json.loads(mutated_result.stdout)["state"])

                    field_mutation = command_mutation.replace(
                        "Serialize exactly these fields: `scope`, `trusted_request_reference`",
                        "Serialize exactly these fields: `scope`, `trusted_request_ref`", 1)
                    installed_implement_path.write_text(field_mutation, encoding="utf-8")
                    mutated_prompt = yaml.safe_load(installed_implement_path.read_text(encoding="utf-8"))
                    with self.assertRaisesRegex(AssertionError, "request fields changed"):
                        _capture_post_pass_command(find_capture_prompt(mutated_prompt["steps"]))
                finally:
                    installed_implement_path.write_bytes(installed_workflow_bytes)
                self.assertEqual("blocked", matrix["task_revision_successor"]["unsubstantiated_completion_state"])
                self.assertEqual("blocked", matrix["task_revision_successor"]["replay_state"])
                self.assertEqual("blocked", matrix["task_revision_successor"]["stale_spec_state"])
                self.assertEqual("blocked", matrix["task_revision_successor"]["stale_pointer_state"])
                self.assertEqual("blocked", matrix["task_revision_successor"]["forged_approved_spec_state"])
                self.assertEqual("blocked", matrix["task_revision_successor"]["forged_semantic_scope_state"])
                self.assertEqual("continue", matrix["task_revision_successor"]["scoped_progress_after_tasker_successors"])
                self.assertEqual("continue", matrix["task_revision_successor"]["captured_revision_route_state"])
                self.assertEqual(["revise-task-plan", "validate-task-revision"],
                                 matrix["task_revision_successor"]["captured_revision_producer_step_ids"])
                self.assertEqual("ready", matrix["task_revision_successor"]["initial_eligibility_state"])
                self.assertEqual(["T002", "T003"], matrix["task_revision_successor"]["activation_task_ids"])
                self.assertEqual("ready", matrix["task_revision_successor"]["final_eligibility_state"])
                self.assertEqual("complete", matrix["task_revision_successor"]["final_scoped_progress_state"])
                self.assertEqual("complete",
                                 matrix["task_revision_successor"]["final_post_pass_completion_validator_state"])
                self.assertEqual({"post-pass-producer-branch-invalid": "blocked",
                                  "post-pass-validator-state-invalid": "blocked",
                                  "post-pass-successor-output-missing": "blocked",
                                  "stale-successor": "blocked"},
                                 matrix["task_revision_successor"]["completion_capture_negative_states"])
                self.assertEqual("blocked",
                                 matrix["task_revision_successor"]["stale_prior_pass_after_later_tracking_state"])
                self.assertEqual(["T002", "T003"], matrix["task_revision_successor"]["final_tasker_tracked_ids"])
                matrix["installed_payload_sha256"] = {
                    "controller.py": sha256(installed_controller_path),
                    "implementation_scope.py": sha256(installed_scope_path),
                    "workflow.yml": sha256(installed_implement_path),
                }
                installed_workflow_versions = {
                    phase: yaml.safe_load(path.read_text(encoding="utf-8"))["workflow"]["version"]
                    for phase, path in (("specify", installed_lifecycle_paths["specify_workflow"]),
                                        ("implement", installed_lifecycle_paths["implement_workflow"]),
                                        ("closeout", installed_lifecycle_paths["closeout_workflow"]))
                }
                matrix["lifecycle_delivery_payload_sha256"] = {
                    key: sha256(path) for key, path in installed_lifecycle_paths.items()
                }
                matrix["installed_owned_payload_inventory"] = installed_inventory
                matrix["lifecycle_workflow_versions"] = installed_workflow_versions
                self.assertEqual({"specify": "0.4.1", "implement": "0.9.1", "closeout": "0.9.2"},
                                 installed_workflow_versions)
                installed_controller_manifest = yaml.safe_load(
                    (consumer / ".specify/farmboy/manifest.yml").read_text(encoding="utf-8"))
                installed_roadmap_manifest = extension_manifest(consumer / ".specify/extensions/flow-roadmap")
                source_revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                    text=True, capture_output=True, check=True).stdout.strip()
                roadmap_revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=roadmap_source,
                    text=True, capture_output=True, check=True).stdout.strip()
                matrix["provenance"] = {
                    "specify_cli": cli_version,
                    "snapshot_install": "passed",
                    "snapshot_refresh": "passed",
                    "controller_package_version": installed_controller_manifest["package"]["version"],
                    "workflow_version": yaml.safe_load(installed_implement_path.read_text(encoding="utf-8"))["workflow"]["version"],
                    "bundle_version": yaml.safe_load(BUNDLE_PATH.read_text(encoding="utf-8"))["bundle"]["version"],
                    "farmboy_source": {"repository": "https://github.com/pegagio/farmboy",
                        "revision": source_revision, "dirty_state": "dirty"},
                    "roadmap_source": {"repository": "https://github.com/pegagio/spec-kit-flow-roadmap",
                        "revision": roadmap_revision, "dirty_state": "dirty",
                        "version": installed_roadmap_manifest["version"],
                        "manifest_sha256": sha256(consumer / ".specify/extensions/flow-roadmap/extension.yml"),
                        "source_manifest_sha256": sha256(roadmap_source / "extension.yml")},
                    "implementation_capture_source": {
                        "controller_sha256": sha256(ROOT / "controllers/farmboy/scripts/python/controller.py"),
                        "workflow_sha256": sha256(ROOT / "workflows/farmboy-implement/workflow.yml"),
                        "installed_controller_sha256": sha256(installed_controller_path),
                        "installed_workflow_sha256": sha256(installed_implement_path)},
                    "consumer_preservation": "project-owned files and unrelated installed workflow retained through refresh and removal",
                    "snapshot_install_output_observed": bool(catalog_install_output),
                    "snapshot_refresh_output_observed": bool(catalog_refresh_output),
                    "production_tags_or_publication": "not part of this validation",
                }
                self.assertEqual(15, len(matrix["cases"]))
                report_output = os.environ.get("FARMBOY_IMPLEMENTATION_SCOPE_REPORT")
                if report_output:
                    report_path = Path(report_output)
                    report_path.parent.mkdir(parents=True, exist_ok=True)
                    report_path.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")

                snapshot_output = os.environ.get("FARMBOY_LIFECYCLE_SNAPSHOT_REPORT")
                if snapshot_output:
                    snapshot_path = Path(snapshot_output)
                    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
                    configuration_paths = [consumer / ".specify/bundle-records.json",
                        consumer / ".specify/extensions.yml",
                        *(consumer / path for path in consumer_files if ".codex/agents/" in path.as_posix())]
                    configuration = [{"path": path.relative_to(consumer).as_posix(),
                                      "sha256": sha256(path), "owner": "consumer-or-installer-configuration"}
                                     for path in configuration_paths if path.is_file()]
                    snapshot_path.write_text(json.dumps({
                        "result": "install-refresh-remove-passed",
                        "specify_cli": cli_version,
                        "bundle_version": yaml.safe_load(BUNDLE_PATH.read_text(encoding="utf-8"))["bundle"]["version"],
                        "controller_package_version": installed_controller_manifest["package"]["version"],
                        "owner_version": installed_roadmap_manifest["version"],
                        "workflow_versions": installed_workflow_versions,
                        "install_and_refresh_output_observed": bool(catalog_install_output and catalog_refresh_output),
                        "owned_payload_inventory": installed_inventory,
                        "consumer_configuration": configuration,
                        "preserved_consumer_file_hashes": {
                            path.relative_to(consumer).as_posix(): value for path, value in consumer_hashes.items()},
                        "unrelated_workflow": {"path": unrelated_workflow.relative_to(consumer).as_posix(),
                            "sha256": unrelated_hash, "preserved_through_refresh_and_remove": True},
                        "limitations": ["Disposable supported development snapshot; no production release or publication claim.",
                                        "Linux remains deferred; live native-agent behavior is not covered."]
                    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")

                run_catalog("remove")
                self.assertEqual(consumer_hashes, {path: sha256(path) for path in consumer_files})
                self.assertEqual(source_agent_files, {path: sha256(path) for path in source_agent_files})
                self.assertEqual(unrelated_hash, sha256(unrelated_workflow))
                self.assertFalse((consumer / ".specify/workflows/farmboy-implement/workflow.yml").exists())
                self.assertFalse((consumer / ".specify/extensions/flow-roadmap").exists())
                self.assertFalse((consumer / ".specify/extensions/flow-wiki").exists())

            release = json.loads(RELEASE_PATH.read_text(encoding="utf-8"))
            bundle = yaml.safe_load(BUNDLE_PATH.read_text(encoding="utf-8"))["bundle"]
            git_head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True
            ).stdout.strip()
            provenance = {
                "specify_cli": cli_version,
                "snapshot": {
                    "bundle_id": bundle["id"],
                    "bundle_version": bundle["version"],
                    "source": str(BUNDLE_PATH.relative_to(ROOT)),
                    "source_revision": git_head,
                },
                "components": {
                    **{
                    extension_id: {
                        "version": release["extensions"][extension_id]["version"],
                        "sha256": release["extensions"][extension_id]["sha256"],
                        "source_repository": release["extensions"][extension_id]["source_repository"],
                        "source_commit": release["extensions"][extension_id]["source_commit"],
                        "source_tag": release["extensions"][extension_id]["source_tag"],
                    }
                    for extension_id in (WIKI_ID, FEEDBACK_ID)
                    },
                    ROADMAP_ID: {
                        "version": roadmap_manifest["version"],
                        "sha256": sha256(roadmap_source / "extension.yml"),
                        "source_repository": "https://github.com/pegagio/spec-kit-flow-roadmap",
                        "source_commit": subprocess.run(
                            ["git", "rev-parse", "HEAD"], cwd=roadmap_source, text=True,
                            capture_output=True, check=True).stdout.strip(),
                        "source_tag": None,
                    },
                },
                "result": "install-refresh-remove-passed; consumer files and unrelated workflow preserved",
                "limits": [
                    "Roadmap uses the explicitly selected compatible development checkout; wiki uses its checked-in checksum-pinned release package.",
                    "This validates the local bundle snapshot against declared component versions; it does not establish publication or consumer adoption.",
                ],
            }
            self.assertEqual("farmboy", provenance["snapshot"]["bundle_id"])
            self.assertTrue(all(provenance["components"][key]["source_commit"] for key in (ROADMAP_ID, WIKI_ID, FEEDBACK_ID)))
            report_output = os.environ.get("FARMBOY_SNAPSHOT_REPORT")
            if report_output:
                report_path = Path(report_output)
                report_path.parent.mkdir(parents=True, exist_ok=True)
                report_path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

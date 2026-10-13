"""Validate the development bundle snapshot with checked and explicit sources.

Roadmap source is supplied through FLOW_ROADMAP_SOURCE when the bundle pin is
newer than the checked-in release archive; wiki and feedback remain pinned.
"""

from __future__ import annotations

import hashlib
import json
import importlib.util
import os
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
        specify_path = shutil.which(SPECIFY_BIN)
        if specify_path is None:
            self.skipTest(f"Specify CLI not found: {SPECIFY_BIN}")

        with tempfile.TemporaryDirectory(prefix="farmboy-snapshot-") as temporary:
            fixture = Path(temporary)
            consumer = fixture / "consumer"
            consumer.mkdir()
            home = fixture / "home"
            home.mkdir()

            roadmap_location = os.environ.get("FLOW_ROADMAP_SOURCE")
            if not roadmap_location:
                self.skipTest("FLOW_ROADMAP_SOURCE is required for the current roadmap pin")
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
                sys.path.insert(0, str(installed_controller_path.parent))
                controller_spec = importlib.util.spec_from_file_location(
                    "snapshot_installed_controller", installed_controller_path)
                self.assertIsNotNone(controller_spec and controller_spec.loader)
                installed_controller = importlib.util.module_from_spec(controller_spec)
                sys.modules[controller_spec.name] = installed_controller
                controller_spec.loader.exec_module(installed_controller)
                installed_scope = installed_controller.implementation_scope_module
                matrix = exercise_installed_scope_matrix(
                    consumer, installed_controller, installed_scope,
                    ROOT / "tests/consumer-fixtures/workflow-improvements/implementation-scope-cases.json",
                    installed_implement_path,
                )
                self.assertEqual(15, len(matrix["cases"]))
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

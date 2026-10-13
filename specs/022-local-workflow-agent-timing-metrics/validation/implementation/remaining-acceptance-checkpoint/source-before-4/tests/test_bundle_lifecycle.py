"""End-to-end lifecycle coverage for the local FarmBoy bundle.

The test stands up an ephemeral localhost catalog. It is test infrastructure,
not a distributable catalog: it packages the declared extension prerequisites
and generic source only long enough to verify the native bundle path.
"""

from __future__ import annotations

import functools
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import unittest
import zipfile
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from tools import catalog


ROOT = Path(__file__).parents[1]
SPECIFY_BIN = Path(os.environ.get("SPECIFY_BIN", "specify"))
ROADMAP_SOURCE = os.environ.get("FARMBOY_TEST_ROADMAP_SOURCE")
WIKI_SOURCE = os.environ.get("FARMBOY_TEST_WIKI_SOURCE")
WORKFLOW_IDS = (
    "farmboy-select-feature",
    "farmboy-specify",
    "farmboy-clarify",
    "farmboy-plan",
    "farmboy-tasks",
    "farmboy-analyze-remediate",
    "farmboy-implement",
    "farmboy-converge",
    "farmboy-closeout",
    "farmboy-wiki-lint-update",
)
CONSUMER_FIXTURE = ROOT / "tests/consumer-fixtures/independent-workflow.yml"
ROADMAP_ID = "flow-roadmap"
WIKI_ID = "flow-wiki"
FEEDBACK_ID = "farmboy-feedback"


def sha256(path: Path) -> str:
    """Return the catalog-compatible SHA-256 digest for one test artifact."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def released_feedback_source(destination: Path) -> Path:
    """Extract the checksum-pinned feedback release for bundle lifecycle checks."""
    release = json.loads((ROOT / "catalog/release.json").read_text(encoding="utf-8"))
    entry = release["extensions"][FEEDBACK_ID]
    artifact = ROOT / "catalog/packages" / entry["artifact"]
    if sha256(artifact) != entry["sha256"]:
        raise AssertionError("released feedback archive checksum differs from catalog")
    with zipfile.ZipFile(artifact) as archive:
        for member in archive.infolist():
            parts = Path(member.filename).parts
            if not parts or parts[0] != FEEDBACK_ID or ".." in parts:
                raise AssertionError("released feedback archive has an unsafe path")
            archive.extract(member, destination)
    return destination / FEEDBACK_ID


def extension_manifest(source: Path) -> dict[str, str]:
    """Read the small manifest subset required by the disposable catalog."""
    values: dict[str, str] = {}
    in_extension = False
    for line in (source / "extension.yml").read_text(encoding="utf-8").splitlines():
        if line == "extension:":
            in_extension = True
            continue
        if in_extension and line and not line.startswith(" "):
            break
        if in_extension and ":" in line:
            key, value = line.strip().split(":", 1)
            values[key] = value.strip().strip('"\'')
    return values


def archive_extension(source: Path, artifacts: Path) -> tuple[Path, dict[str, str]]:
    """Create a single-root archive from the extension's runtime payload."""
    metadata = extension_manifest(source)
    artifact = artifacts / f"{metadata['id']}-{metadata['version']}.zip"
    runtime_roots = ("commands", "scripts", "templates")
    runtime_files = ("extension.yml", "config-template.yml", "README.md", "LICENSE")
    payload = [source / name for name in runtime_files if (source / name).is_file()]
    for root_name in runtime_roots:
        root = source / root_name
        if root.is_dir():
            payload.extend(
                path for path in root.rglob("*")
                if path.is_file() and "__pycache__" not in path.parts
            )
    with zipfile.ZipFile(artifact, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in payload:
            archive.write(path, Path(metadata["id"]) / path.relative_to(source))
    return artifact, metadata


class LocalCatalog:
    """Serve a disposable, checksum-pinned catalog on localhost."""

    def __init__(self, root: Path, extensions: dict[str, Path], catalog_versions: dict[str, str] | None = None) -> None:
        self.root = root
        self.assets = root / "assets"
        self.extensions = extensions
        self.catalog_versions = catalog_versions or {}
        self.server: ThreadingHTTPServer | None = None
        self.thread: threading.Thread | None = None

    def __enter__(self) -> "LocalCatalog":
        self.assets.mkdir(parents=True)
        extension_entries: dict[str, dict[str, str]] = {}
        for expected_id, source in self.extensions.items():
            artifact, metadata = archive_extension(source, self.assets)
            if metadata["id"] != expected_id:
                raise AssertionError(f"fixture source has id {metadata['id']}, expected {expected_id}")
            extension_entries[expected_id] = {
                "name": metadata["name"],
                "version": self.catalog_versions.get(expected_id, metadata["version"]),
                "description": "Disposable local lifecycle-test artifact.",
                "author": metadata.get("author", "pegagio"),
                "download_url": f"PLACEHOLDER/assets/{artifact.name}",
                "sha256": sha256(artifact),
            }

        workflows: dict[str, dict[str, str | list[str]]] = {}
        for workflow_id in WORKFLOW_IDS:
            source = ROOT / "workflows" / workflow_id / "workflow.yml"
            target = self.assets / "workflows" / workflow_id / "workflow.yml"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            workflow_version = next(
                line.split(":", 1)[1].strip().strip('"\'')
                for line in source.read_text(encoding="utf-8").splitlines()
                if line.startswith("  version:")
            )
            workflows[workflow_id] = {
                "id": workflow_id,
                "name": workflow_id,
                "version": workflow_version,
                "description": "FarmBoy lifecycle-test workflow.",
                "author": "pegagio",
                "url": f"PLACEHOLDER/assets/workflows/{workflow_id}/workflow.yml",
                "tags": ["fixture"],
            }

        handler = functools.partial(SimpleHTTPRequestHandler, directory=str(self.root))
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        base_url = f"http://127.0.0.1:{self.server.server_port}"
        for entry in extension_entries.values():
            entry["download_url"] = entry["download_url"].replace("PLACEHOLDER", base_url)
        for entry in workflows.values():
            entry["url"] = str(entry["url"]).replace("PLACEHOLDER", base_url)
        (self.root / "extensions-catalog.json").write_text(
            json.dumps({"schema_version": "1.0", "extensions": extension_entries}), encoding="utf-8"
        )
        (self.root / "workflows-catalog.json").write_text(
            json.dumps({"schema_version": "1.0", "workflows": workflows}), encoding="utf-8"
        )
        self.extension_url = f"{base_url}/extensions-catalog.json"
        self.workflow_url = f"{base_url}/workflows-catalog.json"
        return self

    def __exit__(self, *_: object) -> None:
        assert self.server is not None
        self.server.shutdown()
        self.server.server_close()
        assert self.thread is not None
        self.thread.join(timeout=5)


class BundleLifecycleTests(unittest.TestCase):
    """Exercise the generic bundle through native clean-consumer operations."""

    @classmethod
    def setUpClass(cls) -> None:
        if not SPECIFY_BIN.exists() and str(SPECIFY_BIN) != "specify":
            raise unittest.SkipTest("SPECIFY_BIN does not exist")
        if not ROADMAP_SOURCE or not WIKI_SOURCE:
            raise unittest.SkipTest(
                "set FARMBOY_TEST_ROADMAP_SOURCE and FARMBOY_TEST_WIKI_SOURCE"
            )

    def run_specify(self, consumer: Path, environment: dict[str, str], *args: str) -> str:
        """Run one native command, surfacing its complete output on failure."""
        completed = subprocess.run(
            [str(SPECIFY_BIN), *args],
            cwd=consumer,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if completed.returncode:
            self.fail(f"specify {' '.join(args)} failed:\n{completed.stdout}")
        return completed.stdout

    def test_installRejectsIncompatibleWiki_expectedNoBundleRecord_whenVersionDoesNotMatch(self):
        with tempfile.TemporaryDirectory(prefix="farmboy-version-mismatch-") as directory:
            fixture = Path(directory)
            consumer = fixture / "consumer"
            consumer.mkdir()
            home = fixture / "home"
            home.mkdir()
            extensions = {
                ROADMAP_ID: Path(ROADMAP_SOURCE),
                WIKI_ID: Path(WIKI_SOURCE),
                FEEDBACK_ID: released_feedback_source(fixture / "released-feedback"),
            }
            with LocalCatalog(fixture / "catalog", extensions, {WIKI_ID: "0.0.0"}) as catalog:
                environment = os.environ.copy()
                environment.update({
                    "HOME": str(home),
                    "SPECKIT_CATALOG_URL": catalog.extension_url,
                    "SPECKIT_WORKFLOW_CATALOG_URL": catalog.workflow_url,
                })
                self.run_specify(
                    consumer, environment, "init", "--here", "--force", "--non-interactive",
                    "--integration", "codex", "--integration-options=--skills",
                )
                install = subprocess.run(
                    [str(SPECIFY_BIN), "bundle", "install", str(ROOT / "bundles/farmboy/bundle.yml")],
                    cwd=consumer, env=environment, text=True, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, check=False,
                )
                self.assertNotEqual(0, install.returncode, install.stdout)
                self.assertIn(WIKI_ID, install.stdout.lower())
                self.assertIn("2.0.1", install.stdout)
                self.assertIn("0.0.0", install.stdout)
                record_path = consumer / ".specify/bundle-records.json"
                if record_path.exists():
                    self.assertFalse(json.loads(record_path.read_text(encoding="utf-8"))["bundles"])

    def test_installUpdateRemoveAndFeedbackExport_expectedGenericConsumer_whenCatalogIsAvailable(self):
        with tempfile.TemporaryDirectory(prefix="farmboy-lifecycle-") as directory:
            fixture = Path(directory)
            consumer = fixture / "consumer"
            consumer.mkdir()
            home = fixture / "home"
            home.mkdir()
            extensions = {
                ROADMAP_ID: Path(ROADMAP_SOURCE),
                WIKI_ID: Path(WIKI_SOURCE),
                FEEDBACK_ID: released_feedback_source(fixture / "released-feedback"),
            }
            with LocalCatalog(fixture / "catalog", extensions) as catalog:
                environment = os.environ.copy()
                environment.update(
                    {
                        "HOME": str(home),
                        "SPECKIT_CATALOG_URL": catalog.extension_url,
                        "SPECKIT_WORKFLOW_CATALOG_URL": catalog.workflow_url,
                    }
                )
                self.run_specify(
                    consumer,
                    environment,
                    "init",
                    "--here",
                    "--force",
                    "--non-interactive",
                    "--integration",
                    "codex",
                    "--integration-options=--skills",
                )
                consumer_owned = {
                    consumer / "AGENTS.md": "# Consumer instructions\nPreserve active project guidance.\n",
                    consumer / ".specify/memory/constitution.md": "# Constitution\nConsumer-owned governance.\n",
                    consumer / "specs/example/adoption-review.md": "# Adoption review\nConsumer-owned evidence.\n",
                    consumer / "unrelated/README.md": "Unrelated content.\n",
                    consumer / ".codex/agents/coder.toml": 'name = "Coder"\ninstructions = "consumer-owned coder"\n',
                    consumer / ".codex/agents/verifier.toml": 'name = "Verifier"\ninstructions = "consumer-owned verifier"\n',
                }
                for path, contents in consumer_owned.items():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(contents, encoding="utf-8")
                consumer_owned_hashes = {path: sha256(path) for path in consumer_owned}
                self.run_specify(consumer, environment, "workflow", "add", "--dev", str(CONSUMER_FIXTURE))
                independent = consumer / ".specify/workflows/independent-consumer-check/workflow.yml"
                self.assertTrue(independent.is_file())
                self.run_specify(
                    consumer,
                    environment,
                    "bundle",
                    "install",
                    str(ROOT / "bundles/farmboy/bundle.yml"),
                )
                self.assertEqual(consumer_owned_hashes, {path: sha256(path) for path in consumer_owned})
                record = json.loads((consumer / ".specify/bundle-records.json").read_text(encoding="utf-8"))
                self.assertEqual("farmboy", record["bundles"][0]["bundle_id"])
                contributions = record["bundles"][0]["contributed_components"]
                self.assertEqual(
                    {("extensions", extension_id) for extension_id in extensions}
                    | {("workflows", workflow_id) for workflow_id in WORKFLOW_IDS},
                    {(component["kind"], component["id"]) for component in contributions},
                )
                self.assertTrue(all(component.get("version") for component in contributions))
                for extension_id in extensions:
                    self.assertTrue((consumer / ".specify/extensions" / extension_id).is_dir())
                self.assertFalse((consumer / ".specify/extensions/roadmap").exists())
                self.assertFalse((consumer / ".specify/extensions/wiki").exists())
                self.assertFalse((consumer / ".specify/extensions/flow-feedback").exists())
                self.assertFalse((consumer / ".specify/extensions/speckit-flow-feedback").exists())
                feedback_manifest = (consumer / ".specify/extensions/farmboy-feedback/extension.yml").read_text(encoding="utf-8")
                self.assertIn("- name: speckit.farmboy-feedback.capture", feedback_manifest)
                self.assertIn("- name: speckit.farmboy-feedback.report", feedback_manifest)
                self.assertNotIn("speckit.flow-feedback.", feedback_manifest)
                for workflow_id in ("farmboy-select-feature", "farmboy-specify", "farmboy-closeout"):
                    workflow = (consumer / ".specify/workflows" / workflow_id / "workflow.yml").read_text(encoding="utf-8")
                    commands = re.findall(r'^\s+command: ["\']?(speckit\.flow-(?:roadmap|wiki)\.[a-z-]+)', workflow, re.MULTILINE)
                    self.assertTrue(commands, workflow_id)
                    for command in commands:
                        extension_id = command.split(".", 2)[1]
                        manifest = (consumer / ".specify/extensions" / extension_id / "extension.yml").read_text(encoding="utf-8")
                        self.assertIn(f"- name: {command}", manifest)
                for workflow_id in WORKFLOW_IDS:
                    self.assertTrue((consumer / ".specify/workflows" / workflow_id / "workflow.yml").is_file())
                self.assertFalse((consumer / ".specify/extensions/farmboy-feedback-maintainer").exists())
                self.assertFalse(any("diagram" in path.name.lower() for path in (consumer / ".specify/extensions").iterdir()))
                self.assertTrue(independent.is_file())
                self.run_specify(consumer, environment, "workflow", "resolve", "farmboy-converge")
                codex_stub = fixture / "codex-stub"
                shutil.copy2(ROOT / "tests/consumer-fixtures/codex-stub.sh", codex_stub)
                codex_stub.chmod(0o755)
                workflow_environment = dict(environment)
                workflow_environment["SPECKIT_INTEGRATION_CODEX_EXECUTABLE"] = str(codex_stub)
                feature_files_before = set((consumer / "specs").rglob("*")) if (consumer / "specs").exists() else set()
                # Inventory-driven selection needs a real human gate; a no-op child cannot supply it.
                # Direct-controller selection and activation are covered by deterministic fixtures.
                clarify_run = self.run_specify(
                    consumer, workflow_environment, "workflow", "run", "farmboy-clarify",
                    "--input", "feature_context=disposable consumer fixture",
                    "--json",
                )
                self.assertEqual("completed", json.loads(clarify_run)["status"])
                feature_files_after_clarify = set((consumer / "specs").rglob("*")) if (consumer / "specs").exists() else set()
                self.assertEqual(feature_files_before, feature_files_after_clarify)
                self.run_specify(consumer, workflow_environment, "workflow", "resolve", "farmboy-plan")
                plan_run = self.run_specify(
                    consumer, workflow_environment, "workflow", "run", "farmboy-plan",
                    "--input", "feature_context=disposable consumer fixture",
                    "--input", "plan_review_decision=defer", "--json",
                )
                self.assertEqual("completed", json.loads(plan_run)["status"])
                feature_files_after_plan = set((consumer / "specs").rglob("*")) if (consumer / "specs").exists() else set()
                self.assertEqual(feature_files_before, feature_files_after_plan)
                self.run_specify(consumer, workflow_environment, "workflow", "resolve", "farmboy-tasks")
                tasks_run = self.run_specify(
                    consumer, workflow_environment, "workflow", "run", "farmboy-tasks",
                    "--input", "feature_context=disposable consumer fixture",
                    "--input", "task_review_decision=defer", "--json",
                )
                self.assertEqual("completed", json.loads(tasks_run)["status"])
                feature_files_after_tasks = set((consumer / "specs").rglob("*")) if (consumer / "specs").exists() else set()
                self.assertEqual(feature_files_before, feature_files_after_tasks)
                self.run_specify(consumer, workflow_environment, "workflow", "resolve", "farmboy-analyze-remediate")
                analysis_run = self.run_specify(
                    consumer, workflow_environment, "workflow", "run", "farmboy-analyze-remediate",
                    "--input", "feature_context=disposable consumer fixture",
                    "--input", "analysis_disposition=clean", "--json",
                )
                self.assertEqual("completed", json.loads(analysis_run)["status"])
                feature_files_after_analysis = set((consumer / "specs").rglob("*")) if (consumer / "specs").exists() else set()
                self.assertEqual(feature_files_before, feature_files_after_analysis)
                self.run_specify(consumer, workflow_environment, "workflow", "resolve", "farmboy-implement")
                implementation_run = self.run_specify(
                    consumer, workflow_environment, "workflow", "run", "farmboy-implement",
                    "--input", "feature_context=disposable consumer fixture",
                    "--input", "implementation_result=blocked", "--json",
                )
                self.assertEqual("completed", json.loads(implementation_run)["status"])
                feature_files_after_implementation = set((consumer / "specs").rglob("*")) if (consumer / "specs").exists() else set()
                self.assertEqual(feature_files_before, feature_files_after_implementation)
                workflow_run = self.run_specify(
                    consumer, workflow_environment, "workflow", "run", "farmboy-converge",
                    "--input", "feature_context=disposable consumer fixture",
                    "--input", "convergence_result=clean", "--json",
                )
                self.assertEqual("completed", json.loads(workflow_run)["status"])

                # Closeout requires attributable debrief and verification evidence; a no-op child cannot supply it.
                # Deterministic direct-controller fixtures cover initial stops, correction, approval, and maintenance routing.


                observation = {
                    "observation_id": "converge-terminal-prompt-001",
                    "observed_at": "2026-09-21T12:00:00Z",
                    "component": {"id": "farmboy-converge", "version": "0.1.0", "digest": "sha256:" + sha256(ROOT / "workflows/farmboy-converge/workflow.yml")},
                    "integration": "codex",
                    "consumer_project_ref": "generic-clean-consumer",
                    "execution_profile": {"role": "worker", "capability": "standard"},
                    "expected_behavior": "A clean convergence result gives a clear next-step prompt.",
                    "observed_behavior": "The terminal prompt needs a clearer closeout handoff.",
                    "safety_response": "Stopped at the terminal state and retained the manual fallback.",
                    "manual_fallback_status": "used",
                    "evidence_references": ["validation/convergence-dogfood.md"],
                    "suggested_change_target": "workflow-source",
                    "reporter_disposition": "observed",
                }
                if os.environ.get("FARMBOY_TEST_OBSERVATION"):
                    observation = json.loads(Path(os.environ["FARMBOY_TEST_OBSERVATION"]).read_text(encoding="utf-8"))
                observation_file = consumer / "observation.json"
                observation_file.write_text(json.dumps(observation), encoding="utf-8")
                feedback_script = consumer / ".specify/extensions/farmboy-feedback/scripts/python/workflow_feedback.py"
                journal = consumer / ".specify/workflow-feedback/observations.jsonl"
                report_json = consumer / "feedback-report.json"
                report_markdown = consumer / "feedback-report.md"
                for arguments in (
                    ("capture", "--input", str(observation_file), "--journal", str(journal)),
                    ("report", "--journal", str(journal), "--json", str(report_json), "--markdown", str(report_markdown), "--producer", "generic-clean-consumer", "--created-at", datetime.now(timezone.utc).isoformat(), "--report-id", "feedback-report-001"),
                ):
                    completed = subprocess.run(
                        [os.environ.get("PYTHON", "python3"), str(feedback_script), *arguments],
                        cwd=consumer,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        check=False,
                    )
                    self.assertEqual(0, completed.returncode, completed.stdout)
                self.assertTrue(report_json.is_file())
                projection = report_markdown.read_text(encoding="utf-8")
                self.assertIn("converge-terminal-prompt-001", projection)
                for reference in observation["evidence_references"]:
                    self.assertIn(reference, projection)
                exported = json.loads(report_json.read_text(encoding="utf-8"))
                self.assertEqual(observation["component"], exported["observations"][0]["component"])
                self.assertEqual("generic-clean-consumer", exported["producer"])
                if os.environ.get("FARMBOY_TEST_REPORT_OUTPUT"):
                    shutil.copy2(report_json, os.environ["FARMBOY_TEST_REPORT_OUTPUT"])

                maintainer_script = ROOT / "extensions/farmboy-feedback-maintainer/scripts/python/workflow_feedback_intake.py"
                intake_root = fixture / "maintainer"
                intake_arguments = (
                    "--disposition", "workflow-source-change",
                    "--rationale", "Review the bounded terminal-prompt observation through normal flowback.",
                    "--received-at", "2026-09-22T00:00:00Z",
                    "--root", str(intake_root),
                )
                accepted = subprocess.run(
                    [os.environ.get("PYTHON", "python3"), str(maintainer_script), "--report", str(report_json), *intake_arguments],
                    text=True, capture_output=True, check=False,
                )
                self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)
                accepted_record = json.loads(accepted.stdout)
                self.assertEqual("workflow-source-change", accepted_record["proposed_disposition"])
                self.assertEqual(1, len(list((intake_root / "feedback/inbox").glob("*.json"))))
                self.assertEqual(1, len(list((intake_root / "feedback/triage").glob("*.json"))))

                malformed = dict(exported)
                malformed["producer"] = "tampered-consumer"
                malformed_file = fixture / "malformed-report.json"
                malformed_file.write_text(json.dumps(malformed), encoding="utf-8")
                rejected = subprocess.run(
                    [os.environ.get("PYTHON", "python3"), str(maintainer_script), "--report", str(malformed_file), *intake_arguments],
                    text=True, capture_output=True, check=False,
                )
                self.assertEqual(2, rejected.returncode, rejected.stdout + rejected.stderr)
                self.assertIn("report integrity digest mismatch", rejected.stdout)
                self.assertEqual(1, len(list((intake_root / "feedback/inbox").glob("*.json"))))
                self.assertEqual(1, len(list((intake_root / "feedback/triage").glob("*.json"))))

                self.run_specify(
                    consumer,
                    environment,
                    "bundle",
                    "install",
                    str(ROOT / "bundles/farmboy/bundle.yml"),
                    "--refresh",
                )
                self.assertEqual(consumer_owned_hashes, {path: sha256(path) for path in consumer_owned})
                refreshed_record = json.loads((consumer / ".specify/bundle-records.json").read_text(encoding="utf-8"))
                self.assertEqual(
                    {(component["kind"], component["id"]) for component in contributions},
                    {(component["kind"], component["id"]) for component in refreshed_record["bundles"][0]["contributed_components"]},
                )
                self.assertTrue(independent.is_file())
                self.run_specify(consumer, environment, "bundle", "remove", "farmboy")
                self.assertEqual(consumer_owned_hashes, {path: sha256(path) for path in consumer_owned})
                self.assertFalse((consumer / ".specify/extensions/farmboy-feedback").exists())
                self.assertFalse((consumer / ".specify/workflows/farmboy-converge").exists())
                self.assertTrue(independent.is_file())
                self.assertTrue(report_json.is_file())
                self.assertTrue(journal.is_file())


class FarmBoyControllerLifecycleTests(unittest.TestCase):
    """Exercise direct skill package ownership independently of Specify components."""

    def test_installRefreshRemovePreservesConsumerSkillsAndRecovery(self) -> None:
        with tempfile.TemporaryDirectory(prefix="farmboy-controller-consumer-") as temporary:
            fixture_root = Path(temporary)
            consumer = fixture_root / "consumer"
            local_metrics = fixture_root / "operator-home/.farmboy/metrics/metric-local.json"
            local_metrics.parent.mkdir(parents=True)
            local_metrics.write_text('{"invocation_id":"local"}\n', encoding="utf-8")
            unrelated_component = consumer / ".specify/extensions/consumer-owned/component.json"
            unrelated_component.parent.mkdir(parents=True)
            unrelated_component.write_text('{"owned":true}\n', encoding="utf-8")
            recovery = consumer / ".specify/flow-controllers/runs/retained/summary.json"
            recovery.parent.mkdir(parents=True)
            recovery.write_text('{"status":"stopped"}\n', encoding="utf-8")
            current_recovery = consumer / ".specify/farmboy-controllers/runs/retained/summary.json"
            current_recovery.parent.mkdir(parents=True, exist_ok=True)
            current_recovery.write_text('{"status":"stopped"}\n', encoding="utf-8")
            local_skill = consumer / ".agents/skills/consumer-review/SKILL.md"
            local_skill.parent.mkdir(parents=True)
            local_skill.write_text("consumer-owned", encoding="utf-8")
            custom_agents = {
                consumer / ".codex/agents/coder.toml": 'name = "Coder"\ninstructions = "consumer-owned coder"\n',
                consumer / ".codex/agents/verifier.toml": 'name = "Verifier"\ninstructions = "consumer-owned verifier"\n',
            }
            for path, contents in custom_agents.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(contents, encoding="utf-8")
            agent_hashes = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in custom_agents}
            archive = consumer / "controller-package.zip"
            catalog.package_controller(archive)
            catalog.install_controller_package(consumer, archive, refresh=False, source_digest=catalog.digest(archive), catalog_status="snapshot")
            self.assertTrue((consumer / ".specify/farmboy/scripts/python/metrics.py").is_file())
            self.assertFalse((consumer / ".agents/skills/farmboy-metrics-report").exists())
            self.assertFalse(any("farmboy-metrics-report" in name for name in catalog.controller_package_files()))
            self.assertEqual(10, len(catalog.controller_manifest()["controllers"]))
            catalog.install_controller_package(consumer, archive, refresh=True, source_digest=catalog.digest(archive), catalog_status="snapshot")
            self.assertEqual(agent_hashes, {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in custom_agents})
            self.assertEqual('{"invocation_id":"local"}\n', local_metrics.read_text(encoding="utf-8"))
            catalog.remove_controller_package(consumer)
            self.assertFalse((consumer / ".specify/farmboy/scripts/python/metrics.py").exists())
            self.assertFalse((consumer / ".agents/skills/farmboy-metrics-report").exists())
            self.assertEqual('{"invocation_id":"local"}\n', local_metrics.read_text(encoding="utf-8"))
            self.assertEqual('{"owned":true}\n', unrelated_component.read_text(encoding="utf-8"))
            self.assertTrue(recovery.is_file())
            self.assertTrue(current_recovery.is_file())
            self.assertEqual("consumer-owned", local_skill.read_text(encoding="utf-8"))
            self.assertEqual(agent_hashes, {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in custom_agents})
            self.assertTrue(recovery.is_file())
            self.assertFalse((consumer / ".agents/skills/farmboy-tasks/SKILL.md").exists())
            self.assertFalse((consumer / ".specify/farmboy/skills-install.json").exists())

    def test_nameConflictAndEditedOwnedFileBlockLifecycleChanges(self) -> None:
        with tempfile.TemporaryDirectory(prefix="farmboy-controller-conflict-") as temporary:
            consumer = Path(temporary)
            archive = consumer / "controller-package.zip"
            catalog.package_controller(archive)
            conflict = consumer / ".agents/skills/farmboy-clarify/SKILL.md"
            conflict.parent.mkdir(parents=True)
            conflict.write_text("consumer-owned", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "consumer-owned path conflicts"):
                catalog.install_controller_package(consumer, archive, refresh=False, source_digest=catalog.digest(archive), catalog_status="snapshot")
            self.assertEqual("consumer-owned", conflict.read_text(encoding="utf-8"))
            self.assertFalse((consumer / ".specify/farmboy/skills-install.json").exists())

            conflict.unlink()
            conflict.parent.rmdir()
            catalog.install_controller_package(consumer, archive, refresh=False, source_digest=catalog.digest(archive), catalog_status="snapshot")
            owned = consumer / ".agents/skills/farmboy-clarify/SKILL.md"
            owned.write_text(owned.read_text(encoding="utf-8") + "local edit\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "locally changed FarmBoy owned"):
                catalog.install_controller_package(consumer, archive, refresh=True, source_digest=catalog.digest(archive), catalog_status="snapshot")
            with self.assertRaisesRegex(ValueError, "locally changed FarmBoy owned"):
                catalog.remove_controller_package(consumer)
            self.assertIn("local edit", owned.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

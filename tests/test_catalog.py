"""Focused integrity checks for the checked-in consumer catalog release."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from tools import catalog


class CatalogReleaseTests(unittest.TestCase):
    def test_main_acceptsDevFlag_forInstallAndRefresh(self) -> None:
        for operation in ("install", "refresh"):
            with self.subTest(operation=operation), patch("sys.argv", ["catalog.py", operation, "/consumer", "--dev"]), patch.object(catalog, "install") as install:
                self.assertEqual(0, catalog.main())
                install.assert_called_once_with(Path("/consumer"), operation == "refresh", True, source_overrides={})

    def compatible_roadmap_source(self, directory: Path) -> Path:
        source = directory / "flow-roadmap-source"
        source.mkdir()
        version = catalog.bundle_components()[1]["extensions"]["flow-roadmap"]
        (source / "extension.yml").write_text(
            f'schema_version: "1.0"\nextension:\n  id: "flow-roadmap"\n  name: "FarmBoy Roadmap"\n  version: "{version}"\n  author: "pegagio"\nrequires:\n  specify_cli_version: ">=1.0.10"\n',
            encoding="utf-8",
        )
        subprocess.run(["git", "init", "-q"], cwd=source, check=True, capture_output=True)
        subprocess.run(["git", "add", "extension.yml"], cwd=source, check=True, capture_output=True)
        subprocess.run(["git", "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "source"], cwd=source, check=True, capture_output=True)
        return source

    def test_selectedSpecify_prefersProjectMiseSelection(self) -> None:
        with patch.object(catalog.shutil, "which", side_effect=lambda name: "/usr/bin/mise" if name == "mise" else "/path/specify"), patch.object(
            catalog.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "/mise/specify\n", "")
        ) as run:
            with patch.object(catalog.Path, "is_file", return_value=True), patch.object(catalog.os, "access", return_value=True):
                self.assertEqual("/mise/specify", catalog.selected_specify(Path("/consumer")))
        self.assertEqual(["/usr/bin/mise", "which", "specify"], run.call_args.args[0])

    def test_catalogRemove_dispatchesCompleteLifecycle(self) -> None:
        with patch.object(catalog.sys, "argv", ["catalog.py", "remove", "/consumer"]), patch.object(catalog, "remove") as remove:
            self.assertEqual(0, catalog.main())
        remove.assert_called_once_with(Path("/consumer"))

    def test_controllerManifest_hasTenStableBindingsAndDisplayNames(self) -> None:
        manifest = catalog.controller_manifest()
        self.assertEqual("farmboy-controllers", manifest["package_id"])
        self.assertEqual("1.0.10.dev0+pegagio.2", manifest["specify_cli_version"])
        self.assertEqual(10, len(manifest["controllers"]))
        self.assertEqual(
            [
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
            ],
            [(item["skill_id"], item["display_name"], item["workflow_id"]) for item in manifest["controllers"]],
        )

    def test_controllerPackage_containsSharedRuntimeAndNineCodexSkills(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "controller-package.zip"
            catalog.package_controller(archive)
            with zipfile.ZipFile(archive) as package:
                names = set(package.namelist())
                members = {name: package.read(name).decode("utf-8") for name in names}
                self.assertIn(".specify/farmboy/manifest.yml", names)
                self.assertIn(".specify/farmboy/controller-protocol.md", names)
                self.assertIn(".specify/farmboy/scripts/python/controller.py", names)
                self.assertFalse(any("farmboy-metrics-report" in name or "openpyxl" in name.lower() or "et_xmlfile" in name.lower() for name in names))
                self.assertEqual(10, sum(name.endswith("/SKILL.md") and name.startswith(".agents/skills/farmboy-") for name in names))
                self.assertEqual(10, sum(name.endswith("/agents/openai.yaml") and name.startswith(".agents/skills/farmboy-") for name in names))
                for skill_id, display_name, _ in catalog.CONTROLLER_BINDINGS:
                    metadata = members[f".agents/skills/{skill_id}/agents/openai.yaml"]
                    self.assertIn(f'display_name: "{display_name}"', metadata)
                    self.assertRegex(metadata, r"(?m)^  short_description: \"[^\"]+\"$")

    def test_controllerPackage_deliversMetricsHelperAndExcludesMaintainerReport(self) -> None:
        files = catalog.controller_package_files()
        metrics_path = ".specify/farmboy/scripts/python/metrics.py"
        self.assertIn(metrics_path, files)
        self.assertEqual(catalog.CONTROLLER_SOURCE / "scripts/python/metrics.py", files[metrics_path])
        self.assertFalse(any("farmboy-metrics-report" in path for path in files))
        self.assertFalse(any("openpyxl" in path.lower() or "et_xmlfile" in path.lower() for path in files))
        self.assertEqual(10, len(catalog.controller_manifest()["controllers"]))

    def test_namedAgentAssignments_matchReviewedWorkflowPackage(self) -> None:
        expectations = {
            "farmboy-start-feature": {},
            "farmboy-select-feature": {
                "list-roadmap-options": "FarmBoy Roadmap Agent", "prepare-feature-selection": "FarmBoy Roadmap Agent",
                "verify-feature-selection": "FarmBoy Reviewer",
            },
            "farmboy-specify": {
                "inspect-active-feature": "FarmBoy Roadmap Agent", "prepare-specification-request": "FarmBoy Specifier",
                "draft-specification": "FarmBoy Specifier", "assess-created-spec-linkage": "FarmBoy Reviewer",
                "verify-repaired-spec-linkage": "FarmBoy Reviewer", "brief-against-roadmap": "FarmBoy Roadmap Agent",
            },
            "farmboy-clarify": {
                "clarify-session": "FarmBoy Specifier", "assess-clarification-after-session": "FarmBoy Reviewer",
            },
            "farmboy-plan": {
                "create-plan": "FarmBoy Planner", "verify-plan-output": "FarmBoy Reviewer",
            },
            "farmboy-tasks": {
                "generate-tasks": "FarmBoy Tasker", "verify-task-output": "FarmBoy Reviewer",
            },
            "farmboy-analyze-remediate": {
                "remediate-specification": "FarmBoy Specifier", "remediate-plan": "FarmBoy Planner",
                "remediate-tasks": "FarmBoy Tasker", "analyze-artifacts": "FarmBoy Reviewer", "assess-analysis": "FarmBoy Reviewer",
            },
            "farmboy-implement": {
                "assess-implementation-state": "FarmBoy Reviewer", "run-scoped-preparation": "FarmBoy Coder",
                "run-scoped-source-implementation": "FarmBoy Coder",
                "assess-implementation-after-pass": "FarmBoy Code Reviewer",
            },
            "farmboy-converge": {
                "append-task-remediation": "FarmBoy Tasker", "reconcile-convergence-specification": "FarmBoy Specifier",
                "reconcile-convergence-plan": "FarmBoy Planner", "reconcile-convergence-tasks": "FarmBoy Tasker",
                "analyze-remediation-tasks": "FarmBoy Reviewer", "assess-remediation-eligibility": "FarmBoy Reviewer",
                "implement-remediation": "FarmBoy Coder", "assess-convergence": "FarmBoy Code Reviewer",
            },
            "farmboy-closeout": {
                "assess-closeout-readiness": "FarmBoy Reviewer", "mark-converged-specification-complete": "FarmBoy Specifier",
                "debrief-roadmap": "FarmBoy Reviewer", "assess-closeout-debrief": "FarmBoy Code Reviewer",
                "reconcile-closeout-specification": "FarmBoy Specifier", "reconcile-closeout-plan": "FarmBoy Planner",
                "reconcile-closeout-tasks": "FarmBoy Tasker", "analyze-closeout-artifacts": "FarmBoy Reviewer",
                "assess-closeout-task-eligibility": "FarmBoy Reviewer", "implement-closeout-eligible-tasks": "FarmBoy Coder",
                "prepare-wiki-maintenance": "FarmBoy Roadmap Agent", "ingest-curated-context": "FarmBoy Wiki Curator",
                "lint-wiki": "FarmBoy Reviewer", "assess-wiki-maintenance": "FarmBoy Reviewer", "verify-closeout-readiness": "FarmBoy Reviewer",
            },
        }
        expectations["farmboy-wiki-lint-update"] = {
            "lint-wiki": "FarmBoy Reviewer", "assess-wiki-findings": "FarmBoy Reviewer", "refresh-stale-source": "FarmBoy Wiki Curator",
        }
        expected_versions = {
            "farmboy-wiki-lint-update": "0.2.1",
            "farmboy-start-feature": "0.6.0", "farmboy-select-feature": "0.2.1", "farmboy-specify": "0.4.1", "farmboy-clarify": "0.5.1",
            "farmboy-plan": "0.5.1", "farmboy-tasks": "0.5.1",
            "farmboy-analyze-remediate": "0.6.1", "farmboy-implement": "0.9.1",
            "farmboy-converge": "0.5.1", "farmboy-closeout": "0.9.2",
        }
        step_pattern = __import__("re").compile(r"^(\s*)- id: ([A-Za-z0-9_-]+)$")
        for workflow_id, expected_steps in expectations.items():
            text = (catalog.ROOT / "workflows" / workflow_id / "workflow.yml").read_text(encoding="utf-8")
            version = __import__("re").search(r'^  version: "([^"]+)"$', text, __import__("re").MULTILINE)
            self.assertIsNotNone(version, workflow_id)
            self.assertEqual(expected_versions[workflow_id], version.group(1), workflow_id)
            lines = text.splitlines()
            actual_steps: dict[str, str] = {}
            for index, line in enumerate(lines):
                match = step_pattern.match(line)
                if not match:
                    continue
                indent, step_id = match.groups()
                depth = len(indent)
                end = len(lines)
                for following_index in range(index + 1, len(lines)):
                    following = step_pattern.match(lines[following_index])
                    if following and len(following.group(1)) <= depth:
                        end = following_index
                        break
                block = lines[index + 1:end]
                agent_key_indent = indent + "  "
                agent_value_indent = indent + "    "
                if step_id in expected_steps:
                    self.assertIn(agent_key_indent + "farmboy:", block, f"{workflow_id}:{step_id}")
                    self.assertIn(agent_value_indent + "delegated: true", block, f"{workflow_id}:{step_id}")
                    matching_agents = [line.strip().removeprefix("agent: ") for line in block if line.startswith(agent_value_indent + "agent: ")]
                    self.assertEqual([expected_steps[step_id]], matching_agents, f"{workflow_id}:{step_id}")
                    actual_steps[step_id] = matching_agents[0]
            self.assertEqual(expected_steps, actual_steps, workflow_id)
            self.assertNotRegex(text, r"(?m)^\s+model:\s")
            self.assertNotRegex(text, r"(?m)^\s+reasoning_effort:\s")

    def test_controllerInstallAndRemoval_preservesConsumerOwnedContentAndRecovery(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            (project / ".specify/flow-controllers/runs/existing").mkdir(parents=True)
            (project / ".specify/workflow-feedback").mkdir(parents=True)
            recovery = project / ".specify/flow-controllers/runs/existing/summary.json"
            recovery.write_text('{"status":"stopped"}\n', encoding="utf-8")
            current_recovery = project / ".specify/farmboy-controllers/runs/existing/summary.json"
            current_recovery.parent.mkdir(parents=True, exist_ok=True)
            current_recovery.write_text('{"status":"stopped"}\n', encoding="utf-8")
            feedback = project / ".specify/workflow-feedback/observations.jsonl"
            feedback.write_text('{"observation_id":"local"}\n', encoding="utf-8")
            local_skill = project / ".agents/skills/local-review/SKILL.md"
            local_skill.parent.mkdir(parents=True)
            local_skill.write_text("consumer-owned", encoding="utf-8")
            archive = project / "controller-package.zip"
            catalog.package_controller(archive)
            catalog.install_controller_package(project, archive, refresh=False, source_digest=catalog.digest(archive), catalog_status="snapshot")
            record = json.loads((project / ".specify/farmboy/skills-install.json").read_text(encoding="utf-8"))
            self.assertEqual("installed", record["status"])
            self.assertEqual(10, len(record["controllers"]))
            catalog.remove_controller_package(project)
            self.assertTrue(recovery.is_file())
            self.assertTrue(current_recovery.is_file())
            self.assertTrue(feedback.is_file())
            self.assertEqual("consumer-owned", local_skill.read_text(encoding="utf-8"))
            self.assertFalse((project / ".specify/farmboy/skills-install.json").exists())
            self.assertFalse((project / ".agents/skills/farmboy-tasks").exists())

    def testRefreshRetiresUnchangedDeprecatedLauncherButBlocksEditedCopy(self) -> None:
        for edited in (False, True):
            with self.subTest(edited=edited), tempfile.TemporaryDirectory() as temporary:
                project = Path(temporary)
                archive = project / "controllers.zip"
                catalog.package_controller(archive)
                catalog.install_controller_package(project, archive, refresh=False, source_digest=catalog.digest(archive), catalog_status="snapshot")
                legacy = project / ".agents/skills/farmboy-start-feature/SKILL.md"
                legacy.parent.mkdir(parents=True)
                legacy.write_text("legacy owned launcher")
                record_path = project / ".specify/farmboy/skills-install.json"
                record = json.loads(record_path.read_text())
                record["files"][legacy.relative_to(project).as_posix()] = catalog.digest(legacy)
                record_path.write_text(json.dumps(record))
                if edited:
                    legacy.write_text("consumer modified launcher")
                    with self.assertRaisesRegex(ValueError, "obsolete.*blocks refresh"):
                        catalog.install_controller_package(project, archive, refresh=True, source_digest=catalog.digest(archive), catalog_status="snapshot")
                    self.assertEqual("consumer modified launcher", legacy.read_text())
                else:
                    catalog.install_controller_package(project, archive, refresh=True, source_digest=catalog.digest(archive), catalog_status="snapshot")
                    self.assertFalse(legacy.exists())
                    self.assertTrue((project / ".agents/skills/farmboy-select-feature/SKILL.md").exists())

    def test_controllerInstall_preflightsNameCollisionBeforeWriting(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            conflict = project / ".agents/skills/farmboy-clarify/SKILL.md"
            conflict.parent.mkdir(parents=True)
            conflict.write_text("consumer-owned", encoding="utf-8")
            archive = project / "controller-package.zip"
            catalog.package_controller(archive)
            with self.assertRaisesRegex(ValueError, "consumer-owned path conflicts"):
                catalog.install_controller_package(project, archive, refresh=False, source_digest=catalog.digest(archive), catalog_status="snapshot")
            self.assertEqual("consumer-owned", conflict.read_text(encoding="utf-8"))
            self.assertFalse((project / ".specify/farmboy/skills-install.json").exists())

    def test_controllerRefresh_installsSkillsForLegacyBundleWithoutOwnershipRecord(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            archive = project / "controller-package.zip"
            catalog.package_controller(archive)
            catalog.install_controller_package(project, archive, refresh=True, source_digest=catalog.digest(archive), catalog_status="released")
            record = json.loads((project / ".specify/farmboy/skills-install.json").read_text(encoding="utf-8"))
            self.assertEqual("installed", record["status"])
            self.assertEqual(10, len(record["controllers"]))
            self.assertTrue((project / ".agents/skills/farmboy-tasks/SKILL.md").is_file())

    def test_controllerRefresh_legacyBundleRejectsConsumerSkillCollision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            conflict = project / ".agents/skills/farmboy-tasks/SKILL.md"
            conflict.parent.mkdir(parents=True)
            conflict.write_text("consumer-owned", encoding="utf-8")
            archive = project / "controller-package.zip"
            catalog.package_controller(archive)
            with self.assertRaisesRegex(ValueError, "consumer-owned path conflicts"):
                catalog.install_controller_package(project, archive, refresh=True, source_digest=catalog.digest(archive), catalog_status="released")
            self.assertEqual("consumer-owned", conflict.read_text(encoding="utf-8"))
            self.assertFalse((project / ".specify/farmboy/skills-install.json").exists())

    def test_controllerRefreshAndRemoval_preserveLocallyEditedOwnedFile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            archive = project / "controller-package.zip"
            catalog.package_controller(archive)
            catalog.install_controller_package(project, archive, refresh=False, source_digest=catalog.digest(archive), catalog_status="snapshot")
            edited = project / ".agents/skills/farmboy-tasks/SKILL.md"
            edited.write_text(edited.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "locally changed FarmBoy owned"):
                catalog.install_controller_package(project, archive, refresh=True, source_digest=catalog.digest(archive), catalog_status="snapshot")
            with self.assertRaisesRegex(ValueError, "locally changed FarmBoy owned"):
                catalog.remove_controller_package(project)
            self.assertIn("local edit", edited.read_text(encoding="utf-8"))

    def test_controllerRemoval_rejectsOwnershipPathEscape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "consumer"
            record_path = project / ".specify/farmboy/skills-install.json"
            record_path.parent.mkdir(parents=True)
            outside = root / "outside.txt"
            outside.write_text("consumer-owned", encoding="utf-8")
            record_path.write_text(json.dumps({
                "package": "farmboy-controllers", "status": "installed",
                "files": {"../outside.txt": catalog.digest(outside)},
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ownership path"):
                catalog.remove_controller_package(project, preflight_only=True)
            self.assertEqual("consumer-owned", outside.read_text(encoding="utf-8"))

    def test_controllerInstall_rejectsSymlinkedSkillParent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "consumer"
            other = root / "other-skills"
            other.mkdir()
            (project / ".agents").mkdir(parents=True)
            (project / ".agents/skills").symlink_to(other, target_is_directory=True)
            archive = root / "controller-package.zip"
            catalog.package_controller(archive)
            with self.assertRaisesRegex(ValueError, "ownership path crosses a symlink"):
                catalog.install_controller_package(project, archive, refresh=False, source_digest=catalog.digest(archive), catalog_status="snapshot")
            self.assertEqual([], list(other.iterdir()))

    def test_controllerInstall_rollsBackAfterPartialFileWrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            archive = project / "controller-package.zip"
            catalog.package_controller(archive)
            atomic_write = catalog._atomic_bytes
            calls = 0

            def fail_once(path: Path, content: bytes) -> None:
                nonlocal calls
                calls += 1
                if calls == 3:
                    raise OSError("simulated partial install failure")
                atomic_write(path, content)

            with patch.object(catalog, "_atomic_bytes", side_effect=fail_once):
                with self.assertRaisesRegex(OSError, "partial install failure"):
                    catalog.install_controller_package(project, archive, refresh=False, source_digest=catalog.digest(archive), catalog_status="snapshot")
            self.assertFalse((project / ".specify/farmboy/skills-install.json").exists())
            self.assertFalse(any((project / ".agents/skills").glob("farmboy-*/**/*")))

    def test_install_allowsSourceCheckout_butRejectsNestedTarget(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            release_path = Path(temporary) / "release.json"
            release_path.write_text(json.dumps({"status": "released"}), encoding="utf-8")
            with patch.object(catalog, "RELEASE", release_path), patch.object(catalog, "CATALOG", release_path.parent), patch.object(catalog, "verified_release", side_effect=ValueError("release checked")):
                with self.assertRaisesRegex(ValueError, "release checked"):
                    catalog.install(catalog.ROOT, False)
            with self.assertRaisesRegex(ValueError, "must not be nested"):
                catalog.install(catalog.ROOT / "workflows", False)

    def test_verifiedRelease_rejectsSnapshotRelabeledAsReleased(self) -> None:
        with tempfile.TemporaryDirectory(prefix="farmboy-catalog-status-") as temporary:
            temporary_catalog = Path(temporary)
            temporary_release = temporary_catalog / "release.json"
            release = catalog.build_development_snapshot(temporary_catalog, source_overrides={"flow-roadmap": self.compatible_roadmap_source(temporary_catalog)})
            release["status"] = "released"
            release["extensions"]["flow-roadmap"]["source_tag"] = None
            temporary_release.write_text(json.dumps(release), encoding="utf-8")
            with patch.object(catalog, "CATALOG", temporary_catalog), patch.object(catalog, "RELEASE", temporary_release):
                with self.assertRaisesRegex(ValueError, "source tag differs"):
                    catalog.verified_release(temporary_catalog, temporary_release)

    def test_developmentSnapshot_usesExplicitCompatibleExtensionSource(self) -> None:
        with tempfile.TemporaryDirectory(prefix="farmboy-extension-source-") as source_dir, tempfile.TemporaryDirectory(prefix="farmboy-source-snapshot-") as snapshot_dir:
            source = Path(source_dir)
            version = catalog.bundle_components()[1]["extensions"]["flow-roadmap"]
            (source / "extension.yml").write_text(
                f'schema_version: "1.0"\nextension:\n  id: "flow-roadmap"\n  name: "FlowKit Roadmap"\n  version: "{version}"\n  author: "pegagio"\nrequires:\n  specify_cli_version: ">=1.0.10"\n',
                encoding="utf-8",
            )
            subprocess.run(["git", "init", "-q"], cwd=source, check=True, capture_output=True)
            subprocess.run(["git", "add", "extension.yml"], cwd=source, check=True, capture_output=True)
            subprocess.run(["git", "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "source"], cwd=source, check=True, capture_output=True)
            snapshot = Path(snapshot_dir)
            release = catalog.build_development_snapshot(snapshot, source_overrides={"flow-roadmap": source})
            entry = release["extensions"]["flow-roadmap"]
            self.assertEqual(version, entry["version"])
            self.assertEqual(subprocess.run(["git", "rev-parse", "HEAD"], cwd=source, text=True, capture_output=True, check=True).stdout.strip(), entry["source_commit"])
            self.assertFalse(entry["source_dirty"])
            self.assertTrue((snapshot / "packages" / entry["artifact"]).is_file())
            feedback = release["extensions"]["farmboy-feedback"]
            self.assertEqual("https://github.com/pegagio/farmboy", feedback["source_repository"])
            self.assertEqual("farmboy-feedback-0.2.1.zip", feedback["artifact"])
            self.assertTrue(feedback["source_dirty"])
            self.assertTrue((snapshot / "packages" / feedback["artifact"]).is_file())
            self.assertEqual(release, catalog.verified_release(snapshot, snapshot / "release.json"))

    def test_developmentSnapshot_requiresSourceWhenExtensionPinChanges(self) -> None:
        with tempfile.TemporaryDirectory(prefix="farmboy-source-snapshot-") as temporary:
            previous = json.loads(catalog.RELEASE.read_text(encoding="utf-8"))
            previous["extensions"]["flow-roadmap"]["version"] = "0.2.0"
            previous_release = Path(temporary) / "previous-release.json"
            previous_release.write_text(json.dumps(previous), encoding="utf-8")
            snapshot = Path(temporary) / "snapshot"
            with patch.object(catalog, "RELEASE", previous_release):
                with self.assertRaisesRegex(ValueError, "development snapshot source required for changed extension pin"):
                    catalog.build_development_snapshot(snapshot)

    def test_verifiedRelease_rejectsControllerInventoryMismatch(self) -> None:
        with tempfile.TemporaryDirectory(prefix="farmboy-controller-inventory-") as temporary:
            temporary_catalog = Path(temporary)
            release_path = temporary_catalog / "release.json"
            release = catalog.build_development_snapshot(temporary_catalog, source_overrides={"flow-roadmap": self.compatible_roadmap_source(temporary_catalog)})
            release["controller_package"]["controllers"] = []
            release_path.write_text(json.dumps(release), encoding="utf-8")
            with patch.object(catalog, "CATALOG", temporary_catalog), patch.object(catalog, "RELEASE", release_path):
                with self.assertRaisesRegex(ValueError, "controller inventory differs"):
                    catalog.verified_release(temporary_catalog, release_path)

    def test_install_rejectsSnapshot_beforeStartingCatalog(self) -> None:
        with tempfile.TemporaryDirectory(prefix="farmboy-consumer-") as project:
            Path(project, ".specify").mkdir()
            release_path = Path(project) / "release.json"
            release_path.write_text(json.dumps({"status": "snapshot"}), encoding="utf-8")
            with patch.object(catalog, "CATALOG", Path(project)), patch.object(catalog, "verified_release") as verify, patch.object(catalog, "selected_specify") as select:
                for refresh in (False, True):
                    with self.subTest(refresh=refresh), self.assertRaisesRegex(ValueError, "use --dev with an initialized Specify consumer"):
                        catalog.install(Path(project), refresh)
                verify.assert_not_called()
                select.assert_not_called()
            with patch.object(catalog, "build_development_snapshot", side_effect=ValueError("snapshot built")):
                with self.assertRaisesRegex(ValueError, "snapshot built"):
                    catalog.install(Path(project), True, True)

    def test_snapshotInstall_allowsInitializedPersistentConsumers_butRejectsNestedTargets(self) -> None:
        with tempfile.TemporaryDirectory(prefix="farmboy-dogfood-") as temporary:
            root = Path(temporary).resolve() / "source"
            root.mkdir()
            other = Path(temporary).resolve() / "other"
            other.mkdir()
            (root / "temp").mkdir()
            with patch.object(catalog, "ROOT", root), patch.object(catalog.tempfile, "gettempdir", return_value=str(root / "temp")), patch.object(catalog, "build_development_snapshot", side_effect=ValueError("snapshot build reached")) as build:
                with self.assertRaisesRegex(ValueError, "already be initialized"):
                    catalog.install(root, True, True)
                build.assert_not_called()
                (root / ".specify").mkdir()
                with self.assertRaisesRegex(ValueError, "snapshot build reached"):
                    catalog.install(root, True, True)
                build.reset_mock()
                nested = root / "nested"
                nested.mkdir()
                (nested / ".specify").mkdir()
                with self.assertRaisesRegex(ValueError, "must not be nested"):
                    catalog.install(nested, True, True)
                build.assert_not_called()
                (other / ".specify").mkdir()
                for refresh in (False, True):
                    with self.subTest(refresh=refresh), self.assertRaisesRegex(ValueError, "snapshot build reached"):
                        catalog.install(other, refresh, True)
                disposable = root / "temp" / "consumer"
                disposable.mkdir(parents=True, exist_ok=True)
                (disposable / ".specify").mkdir()
                # Real temporary consumers are outside ROOT, not nested source trees.
                with patch.object(catalog, "ROOT", root / "checkout"):
                    with self.assertRaisesRegex(ValueError, "snapshot build reached"):
                        catalog.install(disposable, True, True)

    def test_releaseTag_requiresAnnotatedTagAtCheckedOutCommit(self) -> None:
        with tempfile.TemporaryDirectory(prefix="farmboy-release-tag-") as temporary:
            source = Path(temporary)
            for arguments in (
                ("init", "-q"),
                ("config", "user.name", "Example Maintainer"),
                ("config", "user.email", "maintainer@example.invalid"),
            ):
                subprocess.run(["git", *arguments], cwd=source, check=True, capture_output=True)
            (source / "extension.yml").write_text("version: 1.0.0\n", encoding="utf-8")
            subprocess.run(["git", "add", "extension.yml"], cwd=source, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-qm", "Initial release"], cwd=source, check=True, capture_output=True)
            commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=source, check=True, capture_output=True, text=True).stdout.strip()
            with self.assertRaisesRegex(ValueError, "annotated v1.0.0"):
                catalog.release_tag(source, "1.0.0", commit)
            subprocess.run(["git", "tag", "-a", "v1.0.0", "-m", "Release 1.0.0"], cwd=source, check=True, capture_output=True)
            self.assertEqual("v1.0.0", catalog.release_tag(source, "1.0.0", commit))
            with self.assertRaisesRegex(ValueError, "HEAD differs"):
                catalog.release_tag(source, "1.0.0", "0" * 40)

    def test_localReleaseSources_rejectDirtyWorkflowAndBundle(self) -> None:
        with tempfile.TemporaryDirectory(prefix="farmboy-release-source-") as temporary:
            root = Path(temporary)
            for arguments in (("init", "-q"), ("config", "user.name", "Example Maintainer"), ("config", "user.email", "maintainer@example.invalid")):
                subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True)
            workflow = root / "workflows/example/workflow.yml"
            bundle = root / "bundles/farmboy/bundle.yml"
            workflow.parent.mkdir(parents=True)
            bundle.parent.mkdir(parents=True)
            workflow.write_text("version: 1\n", encoding="utf-8")
            bundle.write_text("version: 1\n", encoding="utf-8")
            subprocess.run(["git", "add", "workflows", "bundles"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-qm", "Initial release"], cwd=root, check=True, capture_output=True)
            catalog.require_local_release_sources_clean(root)
            for path in (workflow, bundle):
                path.write_text("version: 2\n", encoding="utf-8")
                with self.subTest(path=path), self.assertRaisesRegex(ValueError, "uncommitted"):
                    catalog.require_local_release_sources_clean(root)
                path.write_text("version: 1\n", encoding="utf-8")

    def test_verifiedRelease_rejectsChangedPackage_whenChecksumNoLongerMatches(self) -> None:
        with tempfile.TemporaryDirectory(prefix="farmboy-catalog-integrity-") as temporary:
            temporary_catalog = Path(temporary)
            temporary_release = temporary_catalog / "release.json"
            release = catalog.build_development_snapshot(temporary_catalog, source_overrides={"flow-roadmap": self.compatible_roadmap_source(temporary_catalog)})
            package = temporary_catalog / "packages" / release["extensions"]["farmboy-feedback"]["artifact"]
            package.write_bytes(package.read_bytes() + b"changed")
            with patch.object(catalog, "CATALOG", temporary_catalog), patch.object(catalog, "RELEASE", temporary_release):
                with self.assertRaisesRegex(ValueError, "missing or mismatched: farmboy-feedback"):
                    catalog.verified_release(temporary_catalog, temporary_release)


class AgentPackageValidationTests(unittest.TestCase):
    """Agent inventories remain strict and independent of skill ownership."""

    def fixture(self, directory):
        import yaml
        manifest = catalog.agent_manifest()
        source = Path(directory)
        (source / 'agents').mkdir()
        (source / 'manifest.yml').write_text(yaml.safe_dump(manifest, sort_keys=False))
        for entry in manifest['agents']:
            (source / entry['file']).write_text(
                f'name = "{entry["name"]}"\ndescription = "Role"\ndeveloper_instructions = "Bounded work"\nmodel = "gpt-6-luna"\nmodel_reasoning_effort = "high"\n'
            )
        return source, manifest

    def test_duplicateAndEscapingInventory_rejected(self):
        import copy
        baseline = catalog.agent_manifest()
        for key in ('name', 'file', 'destination'):
            manifest = copy.deepcopy(baseline)
            manifest['agents'][1][key] = manifest['agents'][0][key]
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'duplicate'):
                catalog.validate_agent_manifest(manifest)
        for key in ('file', 'destination'):
            for path in ('/absolute.toml', '../escape.toml', 'agents/../escape.toml', 'agents/a/b.toml'):
                manifest = copy.deepcopy(baseline)
                manifest['agents'][0][key] = path
                with self.subTest(key=key, path=path), self.assertRaises(ValueError):
                    catalog.validate_agent_manifest(manifest)

    def test_malformedAndMismatchedDefinitions_rejected(self):
        for content in (b'invalid = [', b'name="Wrong"\ndescription="D"\ndeveloper_instructions="I"', b'name="FarmBoy Planner"'):
            with self.subTest(content=content), self.assertRaises(ValueError):
                catalog.validate_agent_definition(content, 'FarmBoy Planner')

    def test_regularSourcesAndArchive_allowlistAndVersion_checked(self):
        with tempfile.TemporaryDirectory() as temporary:
            source, manifest = self.fixture(temporary)
            files = catalog.agent_package_files(source)
            archive = source / 'package.zip'
            with zipfile.ZipFile(archive, 'w') as package:
                for member, path in files.items():
                    package.writestr(member, path.read_bytes())
            self.assertEqual(manifest, catalog.validate_agent_archive(archive, manifest['package']['version'])[0])
            with self.assertRaisesRegex(ValueError, 'version'):
                catalog.validate_agent_archive(archive, '9.9.9')
            with zipfile.ZipFile(archive, 'a') as package:
                package.writestr('unlisted.txt', 'unsafe extra')
            with self.assertRaisesRegex(ValueError, 'unlisted'):
                catalog.validate_agent_archive(archive)
            path = source / manifest['agents'][0]['file']
            path.unlink()
            path.symlink_to(source / manifest['agents'][1]['file'])
            with self.assertRaisesRegex(ValueError, 'symlink'):
                catalog.agent_package_files(source)

    def test_resetOnlyCurrentManifestTargets(self):
        manifest = catalog.agent_manifest()
        self.assertEqual(manifest['agents'], catalog.select_agent_targets(manifest, all_agents=True))
        self.assertEqual(1, len(catalog.select_agent_targets(manifest, agent='FarmBoy Planner')))
        for args in ({}, {'agent': '*'}, {'agent': 'Planner'}, {'agent': 'FarmBoy Planner', 'all_agents': True}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                catalog.select_agent_targets(manifest, **args)


if __name__ == "__main__":
    unittest.main()

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
        self.assertEqual("flow-kit-controllers", manifest["package_id"])
        self.assertEqual("1.0.10.dev0+pegagio.2", manifest["specify_cli_version"])
        self.assertEqual(10, len(manifest["controllers"]))
        self.assertEqual(
            [
                ("flow-kit-select-feature", "FlowKit Select Feature", "speckit-flow-select-feature"),
                ("flow-kit-specify", "FlowKit Specify", "speckit-flow-specify"),
                ("flow-kit-clarify", "FlowKit Clarify", "speckit-flow-clarify"),
                ("flow-kit-plan", "FlowKit Plan", "speckit-flow-plan"),
                ("flow-kit-tasks", "FlowKit Tasks", "speckit-flow-tasks"),
                ("flow-kit-analyze-remediate", "FlowKit Analyze", "speckit-flow-analyze-remediate"),
                ("flow-kit-implement", "FlowKit Implement", "speckit-flow-implement"),
                ("flow-kit-converge", "FlowKit Converge", "speckit-flow-converge"),
                ("flow-kit-closeout", "FlowKit Close Out", "speckit-flow-closeout"),
                ("flow-kit-wiki-lint-update", "FlowKit Wiki Lint Update", "speckit-flow-wiki-lint-update"),
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
                self.assertIn(".specify/flow-kit/manifest.yml", names)
                self.assertIn(".specify/flow-kit/controller-protocol.md", names)
                self.assertIn(".specify/flow-kit/scripts/python/controller.py", names)
                self.assertEqual(10, sum(name.endswith("/SKILL.md") and name.startswith(".agents/skills/flow-kit-") for name in names))
                self.assertEqual(10, sum(name.endswith("/agents/openai.yaml") and name.startswith(".agents/skills/flow-kit-") for name in names))
                for skill_id, display_name, _ in catalog.CONTROLLER_BINDINGS:
                    metadata = members[f".agents/skills/{skill_id}/agents/openai.yaml"]
                    self.assertIn(f'display_name: "{display_name}"', metadata)
                    self.assertRegex(metadata, r"(?m)^  short_description: \"[^\"]+\"$")

    def test_namedAgentAssignments_matchReviewedWorkflowPackage(self) -> None:
        expectations = {
            "speckit-flow-start-feature": {},
            "speckit-flow-select-feature": {
                "list-roadmap-options": "FlowKit-Roadmap Agent", "prepare-feature-selection": "FlowKit-Roadmap Agent",
                "verify-feature-selection": "FlowKit-Reviewer",
            },
            "speckit-flow-specify": {
                "inspect-active-feature": "FlowKit-Roadmap Agent", "prepare-specification-request": "FlowKit-Specifier",
                "draft-specification": "FlowKit-Specifier", "assess-created-spec-linkage": "FlowKit-Reviewer",
                "verify-repaired-spec-linkage": "FlowKit-Reviewer", "brief-against-roadmap": "FlowKit-Reviewer",
            },
            "speckit-flow-clarify": {
                "clarify-session": "FlowKit-Specifier", "assess-clarification-after-session": "FlowKit-Reviewer",
            },
            "speckit-flow-plan": {
                "create-plan": "FlowKit-Planner", "verify-plan-output": "FlowKit-Reviewer",
            },
            "speckit-flow-tasks": {
                "generate-tasks": "FlowKit-Tasker", "verify-task-output": "FlowKit-Reviewer",
            },
            "speckit-flow-analyze-remediate": {
                "remediate-specification": "FlowKit-Specifier", "remediate-plan": "FlowKit-Planner",
                "remediate-tasks": "FlowKit-Tasker", "analyze-artifacts": "FlowKit-Reviewer", "assess-analysis": "FlowKit-Reviewer",
            },
            "speckit-flow-implement": {
                "assess-implementation-state": "FlowKit-Reviewer", "implement-eligible-work": "FlowKit-Coder",
                "assess-implementation-after-pass": "FlowKit-Code Reviewer",
            },
            "speckit-flow-converge": {
                "append-task-remediation": "FlowKit-Tasker", "reconcile-convergence-specification": "FlowKit-Specifier",
                "reconcile-convergence-plan": "FlowKit-Planner", "reconcile-convergence-tasks": "FlowKit-Tasker",
                "analyze-remediation-tasks": "FlowKit-Reviewer", "assess-remediation-eligibility": "FlowKit-Reviewer",
                "implement-remediation": "FlowKit-Coder", "assess-convergence": "FlowKit-Code Reviewer",
            },
            "speckit-flow-closeout": {
                "assess-closeout-readiness": "FlowKit-Reviewer", "mark-converged-specification-complete": "FlowKit-Specifier",
                "debrief-roadmap": "FlowKit-Reviewer", "assess-closeout-debrief": "FlowKit-Code Reviewer",
                "reconcile-closeout-specification": "FlowKit-Specifier", "reconcile-closeout-plan": "FlowKit-Planner",
                "reconcile-closeout-tasks": "FlowKit-Tasker", "analyze-closeout-artifacts": "FlowKit-Reviewer",
                "assess-closeout-task-eligibility": "FlowKit-Reviewer", "implement-closeout-eligible-tasks": "FlowKit-Coder",
                "prepare-wiki-maintenance": "FlowKit-Roadmap Agent", "ingest-curated-context": "FlowKit-Wiki Curator",
                "lint-wiki": "FlowKit-Reviewer", "assess-wiki-maintenance": "FlowKit-Reviewer", "verify-closeout-readiness": "FlowKit-Reviewer",
            },
        }
        expectations["speckit-flow-wiki-lint-update"] = {
            "lint-wiki": "FlowKit-Reviewer", "assess-wiki-findings": "FlowKit-Reviewer", "refresh-stale-source": "FlowKit-Wiki Curator",
        }
        expected_versions = {
            "speckit-flow-wiki-lint-update": "0.2.0",
            "speckit-flow-start-feature": "0.6.0", "speckit-flow-select-feature": "0.2.0", "speckit-flow-specify": "0.2.0", "speckit-flow-clarify": "0.5.0",
            "speckit-flow-plan": "0.5.0", "speckit-flow-tasks": "0.5.0",
            "speckit-flow-analyze-remediate": "0.5.0", "speckit-flow-implement": "0.5.0",
            "speckit-flow-converge": "0.5.0", "speckit-flow-closeout": "0.7.0",
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
                    self.assertIn(agent_key_indent + "flow_kit:", block, f"{workflow_id}:{step_id}")
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
            feedback = project / ".specify/workflow-feedback/observations.jsonl"
            feedback.write_text('{"observation_id":"local"}\n', encoding="utf-8")
            local_skill = project / ".agents/skills/local-review/SKILL.md"
            local_skill.parent.mkdir(parents=True)
            local_skill.write_text("consumer-owned", encoding="utf-8")
            archive = project / "controller-package.zip"
            catalog.package_controller(archive)
            catalog.install_controller_package(project, archive, refresh=False, source_digest=catalog.digest(archive), catalog_status="snapshot")
            record = json.loads((project / ".specify/flow-kit/skills-install.json").read_text(encoding="utf-8"))
            self.assertEqual("installed", record["status"])
            self.assertEqual(10, len(record["controllers"]))
            catalog.remove_controller_package(project)
            self.assertTrue(recovery.is_file())
            self.assertTrue(feedback.is_file())
            self.assertEqual("consumer-owned", local_skill.read_text(encoding="utf-8"))
            self.assertFalse((project / ".specify/flow-kit/skills-install.json").exists())
            self.assertFalse((project / ".agents/skills/flow-kit-tasks").exists())

    def testRefreshRetiresUnchangedDeprecatedLauncherButBlocksEditedCopy(self) -> None:
        for edited in (False, True):
            with self.subTest(edited=edited), tempfile.TemporaryDirectory() as temporary:
                project = Path(temporary)
                archive = project / "controllers.zip"
                catalog.package_controller(archive)
                catalog.install_controller_package(project, archive, refresh=False, source_digest=catalog.digest(archive), catalog_status="snapshot")
                legacy = project / ".agents/skills/flow-kit-start-feature/SKILL.md"
                legacy.parent.mkdir(parents=True)
                legacy.write_text("legacy owned launcher")
                record_path = project / ".specify/flow-kit/skills-install.json"
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
                    self.assertTrue((project / ".agents/skills/flow-kit-select-feature/SKILL.md").exists())

    def test_controllerInstall_preflightsNameCollisionBeforeWriting(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            conflict = project / ".agents/skills/flow-kit-clarify/SKILL.md"
            conflict.parent.mkdir(parents=True)
            conflict.write_text("consumer-owned", encoding="utf-8")
            archive = project / "controller-package.zip"
            catalog.package_controller(archive)
            with self.assertRaisesRegex(ValueError, "consumer-owned path conflicts"):
                catalog.install_controller_package(project, archive, refresh=False, source_digest=catalog.digest(archive), catalog_status="snapshot")
            self.assertEqual("consumer-owned", conflict.read_text(encoding="utf-8"))
            self.assertFalse((project / ".specify/flow-kit/skills-install.json").exists())

    def test_controllerRefresh_installsSkillsForLegacyBundleWithoutOwnershipRecord(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            archive = project / "controller-package.zip"
            catalog.package_controller(archive)
            catalog.install_controller_package(project, archive, refresh=True, source_digest=catalog.digest(archive), catalog_status="released")
            record = json.loads((project / ".specify/flow-kit/skills-install.json").read_text(encoding="utf-8"))
            self.assertEqual("installed", record["status"])
            self.assertEqual(10, len(record["controllers"]))
            self.assertTrue((project / ".agents/skills/flow-kit-tasks/SKILL.md").is_file())

    def test_controllerRefresh_legacyBundleRejectsConsumerSkillCollision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            conflict = project / ".agents/skills/flow-kit-tasks/SKILL.md"
            conflict.parent.mkdir(parents=True)
            conflict.write_text("consumer-owned", encoding="utf-8")
            archive = project / "controller-package.zip"
            catalog.package_controller(archive)
            with self.assertRaisesRegex(ValueError, "consumer-owned path conflicts"):
                catalog.install_controller_package(project, archive, refresh=True, source_digest=catalog.digest(archive), catalog_status="released")
            self.assertEqual("consumer-owned", conflict.read_text(encoding="utf-8"))
            self.assertFalse((project / ".specify/flow-kit/skills-install.json").exists())

    def test_controllerRefreshAndRemoval_preserveLocallyEditedOwnedFile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            archive = project / "controller-package.zip"
            catalog.package_controller(archive)
            catalog.install_controller_package(project, archive, refresh=False, source_digest=catalog.digest(archive), catalog_status="snapshot")
            edited = project / ".agents/skills/flow-kit-tasks/SKILL.md"
            edited.write_text(edited.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "locally changed FlowKit-owned"):
                catalog.install_controller_package(project, archive, refresh=True, source_digest=catalog.digest(archive), catalog_status="snapshot")
            with self.assertRaisesRegex(ValueError, "locally changed FlowKit-owned"):
                catalog.remove_controller_package(project)
            self.assertIn("local edit", edited.read_text(encoding="utf-8"))

    def test_controllerRemoval_rejectsOwnershipPathEscape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "consumer"
            record_path = project / ".specify/flow-kit/skills-install.json"
            record_path.parent.mkdir(parents=True)
            outside = root / "outside.txt"
            outside.write_text("consumer-owned", encoding="utf-8")
            record_path.write_text(json.dumps({
                "package": "flow-kit-controllers", "status": "installed",
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
            self.assertFalse((project / ".specify/flow-kit/skills-install.json").exists())
            self.assertFalse(any((project / ".agents/skills").glob("flow-kit-*/**/*")))

    def test_install_allowsSourceCheckout_butRejectsNestedTarget(self) -> None:
        with patch.object(catalog, "verified_release", side_effect=ValueError("release checked")):
            with self.assertRaisesRegex(ValueError, "release checked"):
                catalog.install(catalog.ROOT, False)
            with self.assertRaisesRegex(ValueError, "must not be nested"):
                catalog.install(catalog.ROOT / "workflows", False)

    def test_verifiedRelease_rejectsSnapshotRelabeledAsReleased(self) -> None:
        with tempfile.TemporaryDirectory(prefix="spec-kit-flow-catalog-status-") as temporary:
            temporary_catalog = Path(temporary)
            temporary_release = temporary_catalog / "release.json"
            release = catalog.build_development_snapshot(temporary_catalog)
            release["status"] = "released"
            release["extensions"]["flow-roadmap"]["source_tag"] = None
            temporary_release.write_text(json.dumps(release), encoding="utf-8")
            with patch.object(catalog, "CATALOG", temporary_catalog), patch.object(catalog, "RELEASE", temporary_release):
                with self.assertRaisesRegex(ValueError, "source tag differs"):
                    catalog.verified_release(temporary_catalog, temporary_release)

    def test_verifiedRelease_rejectsControllerInventoryMismatch(self) -> None:
        with tempfile.TemporaryDirectory(prefix="spec-kit-flow-controller-inventory-") as temporary:
            temporary_catalog = Path(temporary)
            release_path = temporary_catalog / "release.json"
            release = catalog.build_development_snapshot(temporary_catalog)
            release["controller_package"]["controllers"] = []
            release_path.write_text(json.dumps(release), encoding="utf-8")
            with patch.object(catalog, "CATALOG", temporary_catalog), patch.object(catalog, "RELEASE", release_path):
                with self.assertRaisesRegex(ValueError, "controller inventory differs"):
                    catalog.verified_release(temporary_catalog, release_path)

    def test_install_rejectsSnapshot_beforeStartingCatalog(self) -> None:
        with tempfile.TemporaryDirectory(prefix="spec-kit-flow-consumer-") as project:
            Path(project, ".specify").mkdir()
            snapshot = {"status": "snapshot"}
            with patch.object(catalog, "verified_release", return_value=snapshot):
                with self.assertRaisesRegex(ValueError, "development snapshot"):
                    catalog.install(Path(project), False)
            with patch.object(catalog, "build_development_snapshot", side_effect=ValueError("snapshot built")):
                with self.assertRaisesRegex(ValueError, "snapshot built"):
                    catalog.install(Path(project), True, True)

    def test_snapshotDogfood_allowsOnlyInitializedRootOrTemporaryConsumers(self) -> None:
        with tempfile.TemporaryDirectory(prefix="spec-kit-flow-dogfood-") as temporary:
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
                with self.assertRaisesRegex(ValueError, "source checkout root or a disposable"):
                    catalog.install(other, True, True)
                build.assert_not_called()
                disposable = root / "temp" / "consumer"
                disposable.mkdir(parents=True, exist_ok=True)
                (disposable / ".specify").mkdir()
                # Real temporary consumers are outside ROOT, not nested source trees.
                with patch.object(catalog, "ROOT", root / "checkout"):
                    with self.assertRaisesRegex(ValueError, "snapshot build reached"):
                        catalog.install(disposable, True, True)

    def test_releaseTag_requiresAnnotatedTagAtCheckedOutCommit(self) -> None:
        with tempfile.TemporaryDirectory(prefix="spec-kit-flow-release-tag-") as temporary:
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
        with tempfile.TemporaryDirectory(prefix="spec-kit-flow-release-source-") as temporary:
            root = Path(temporary)
            for arguments in (("init", "-q"), ("config", "user.name", "Example Maintainer"), ("config", "user.email", "maintainer@example.invalid")):
                subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True)
            workflow = root / "workflows/example/workflow.yml"
            bundle = root / "bundles/spec-kit-flow/bundle.yml"
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
        with tempfile.TemporaryDirectory(prefix="spec-kit-flow-catalog-integrity-") as temporary:
            temporary_catalog = Path(temporary)
            temporary_release = temporary_catalog / "release.json"
            release = catalog.build_development_snapshot(temporary_catalog)
            package = temporary_catalog / "packages" / release["extensions"]["flow-feedback"]["artifact"]
            package.write_bytes(package.read_bytes() + b"changed")
            with patch.object(catalog, "CATALOG", temporary_catalog), patch.object(catalog, "RELEASE", temporary_release):
                with self.assertRaisesRegex(ValueError, "missing or mismatched: flow-feedback"):
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
        for content in (b'invalid = [', b'name="Wrong"\ndescription="D"\ndeveloper_instructions="I"', b'name="FlowKit-Planner"'):
            with self.subTest(content=content), self.assertRaises(ValueError):
                catalog.validate_agent_definition(content, 'FlowKit-Planner')

    def test_regularSourcesAndArchive_allowlistAndVersion_checked(self):
        with tempfile.TemporaryDirectory() as temporary:
            source, manifest = self.fixture(temporary)
            files = catalog.agent_package_files(source)
            archive = source / 'package.zip'
            with zipfile.ZipFile(archive, 'w') as package:
                for member, path in files.items():
                    package.writestr(member, path.read_bytes())
            self.assertEqual(manifest, catalog.validate_agent_archive(archive, '0.1.0')[0])
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
        self.assertEqual(1, len(catalog.select_agent_targets(manifest, agent='FlowKit-Planner')))
        for args in ({}, {'agent': '*'}, {'agent': 'Planner'}, {'agent': 'FlowKit-Planner', 'all_agents': True}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                catalog.select_agent_targets(manifest, **args)


if __name__ == "__main__":
    unittest.main()

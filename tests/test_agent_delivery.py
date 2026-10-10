"""Consumer-owned agent lifecycle, integrity and recovery checks."""
from __future__ import annotations

import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from tools import catalog


class AgentDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / "consumer"
        (self.project / ".specify").mkdir(parents=True)
        self.archive = self.root / "agents.zip"
        self.metadata = catalog.package_agents(self.archive)
        catalog.cache_agent_defaults(self.project, self.archive, self.metadata)

    def operation(self, action="install-missing", **kwargs):
        return catalog.agent_operation(self.project, action, **kwargs)

    def test_deterministicArchive_andSourceIsolation(self):
        other = self.root / "second.zip"
        second = catalog.package_agents(other)
        self.assertEqual(self.metadata["sha256"], second["sha256"])
        manifest, members = catalog.validate_agent_archive(other, "0.2.0")
        self.assertEqual(9, len(manifest["agents"]))
        self.assertEqual(10, len(members))
        self.assertNotIn(".codex/agents", " ".join(members))

    def test_packagePinMismatch_andSymlinkManifest_rejected(self):
        destination = self.root / "catalog"
        package_directory = destination / "packages"
        package_directory.mkdir(parents=True)
        shutil.copy2(self.archive, package_directory / self.metadata["artifact"])
        bundle = self.root / "bundle.yml"
        bundle.write_text(yaml.safe_dump({"agent_package": {"id": "flow-kit-agents", "version": "9.9.9"}}))
        with patch.object(catalog, "BUNDLE", bundle), self.assertRaisesRegex(ValueError, "bundle pin"):
            catalog.verify_agent_release({"agent_package": self.metadata}, destination)
        source = self.root / "symlink-source"
        shutil.copytree(catalog.AGENT_SOURCE, source)
        (source / "manifest.yml").unlink()
        (source / "manifest.yml").symlink_to(catalog.AGENT_SOURCE / "manifest.yml")
        with self.assertRaisesRegex(ValueError, "regular source"):
            catalog.agent_package_files(source)

    def test_cleanRepeatCustomizedAndOldFiles_preserved(self):
        directory = self.project / ".codex/agents"
        directory.mkdir(parents=True)
        (directory / "old.toml").write_text('name = "Coder"\n')
        (directory / "unrelated.toml").write_text('name = "Unrelated"\n')
        result = self.operation()
        self.assertEqual("complete", result["status"])
        self.assertEqual(["created"] * 9, [t["outcome"] for t in result["targets"]])
        entries = catalog.agent_manifest()["agents"]
        self.assertEqual(9, len(entries))
        self.assertEqual(9, len(list(directory.glob("flowkit-*.toml"))))
        for entry in entries:
            with self.subTest(agent=entry["name"]):
                self.assertEqual(
                    (catalog.AGENT_SOURCE / entry["file"]).read_bytes(),
                    (self.project / entry["destination"]).read_bytes(),
                )
        target = directory / "flowkit-coder.toml"
        target.write_text(target.read_text() + "# consumer customization\n")
        before = {p.name: p.read_bytes() for p in directory.iterdir()}
        self.assertEqual("complete", self.operation()["status"])
        self.assertEqual(before, {p.name: p.read_bytes() for p in directory.iterdir()})
        self.assertNotIn("consumer_hash", json.dumps(result))

    def test_explicitResetOneAndAll_andRemoval(self):
        self.operation()
        directory = self.project / ".codex/agents"
        target = directory / "flowkit-coder.toml"
        target.write_text(target.read_text() + "# custom\n")
        result = self.operation("reset", agent="FlowKit-Coder")
        self.assertEqual("complete", result["status"])
        self.assertEqual(["reset"], [t["outcome"] for t in result["targets"]])
        self.assertNotIn(b"# custom", target.read_bytes())
        self.assertEqual(9, len(self.operation("reset", all_agents=True)["targets"]))
        before = {p.name: p.read_bytes() for p in directory.iterdir()}
        catalog.remove_agent_defaults(self.project)
        self.assertEqual(before, {p.name: p.read_bytes() for p in directory.iterdir()})
        self.assertEqual("failed", self.operation()["status"])

    def test_cacheRefreshNewRoleAndRetirement_doNotTouchCopies(self):
        self.operation()
        directory = self.project / ".codex/agents"
        before = {p.name: p.read_bytes() for p in directory.iterdir()}
        source = self.root / "source"
        shutil.copytree(catalog.AGENT_SOURCE, source)
        manifest = yaml.safe_load((source / "manifest.yml").read_text())
        manifest["package"]["version"] = "0.3.0"
        manifest["agents"].append({"name": "Fixture-New Role", "file": "agents/new.toml", "destination": ".codex/agents/new.toml"})
        (source / "agents/new.toml").write_text('name = "Fixture-New Role"\ndescription = "Fixture"\ndeveloper_instructions = "No work"\nmodel="gpt-6-luna"\nmodel_reasoning_effort="high"\n')
        (source / "manifest.yml").write_text(yaml.safe_dump(manifest))
        with patch.object(catalog, "AGENT_SOURCE", source):
            metadata = catalog.package_agents(self.archive)
        catalog.cache_agent_defaults(self.project, self.archive, metadata)
        self.assertEqual(before, {p.name: p.read_bytes() for p in directory.iterdir()})
        result = self.operation()
        self.assertEqual("created", result["targets"][-1]["outcome"])
        self.assertEqual(10, len(list(directory.iterdir())))
        manifest["agents"] = manifest["agents"][-1:]
        (source / "manifest.yml").write_text(yaml.safe_dump(manifest))
        with patch.object(catalog, "AGENT_SOURCE", source):
            metadata = catalog.package_agents(self.archive)
        catalog.cache_agent_defaults(self.project, self.archive, metadata)
        self.assertEqual(1, len(self.operation("reset", all_agents=True)["targets"]))
        self.assertEqual(10, len(list(directory.iterdir())))

    def test_invalidSelectorsAndCache_failBeforeWrites(self):
        for kwargs in ({}, {"agent": "Unknown"}, {"agent": "FlowKit-Coder", "all_agents": True}):
            self.assertEqual("failed", self.operation("reset", **kwargs)["status"])
            self.assertFalse((self.project / ".codex").exists())
        cache = self.project / ".specify/flow-kit/agent-defaults"
        (cache / "package.zip").write_bytes(b"tampered")
        self.assertEqual("failed", self.operation()["status"])
        self.assertFalse((self.project / ".codex").exists())

    def test_duplicateIdentitySymlinkAndDirectory_failBeforeWrites(self):
        directory = self.project / ".codex/agents"
        directory.mkdir(parents=True)
        a = directory / "a.toml"
        b = directory / "b.toml"
        a.write_text('name="Duplicate"\n'); b.write_text(a.read_text())
        self.assertEqual("failed", self.operation()["status"])
        self.assertEqual(2, len(list(directory.iterdir())))
        a.unlink(); b.unlink()
        target = directory / "flowkit-coder.toml"
        target.symlink_to(self.archive)
        self.assertEqual("failed", self.operation()["status"])
        target.unlink(); target.mkdir()
        self.assertEqual("failed", self.operation()["status"])
        self.assertEqual(1, len(list(directory.iterdir())))

    def test_duplicateProjectIdentity_reportsRelativeCollisionAndPreservesFiles(self):
        directory = self.project / ".codex/agents"
        directory.mkdir(parents=True)
        first = directory / "first.toml"
        second = directory / "second.toml"
        content = 'name = "Duplicate Role"\ndescription = "fixture"\n'
        first.write_text(content)
        second.write_text(content)
        before = {path.name: path.read_bytes() for path in directory.iterdir()}

        result = self.operation()

        self.assertEqual("duplicate-project-agent-identity", result["error"])
        self.assertEqual({
            "name": "Duplicate Role",
            "identity_redacted": False,
            "paths": [".codex/agents/first.toml", ".codex/agents/second.toml"],
            "recovery": "Rename or remove one definition after checking dependent assignments, then retry the operation.",
        }, result["conflict"])
        self.assertEqual(["not-attempted"] * 9, [entry["outcome"] for entry in result["targets"]])
        self.assertEqual(before, {path.name: path.read_bytes() for path in directory.iterdir()})
        self.assertFalse(any(path.name.startswith("flowkit-") for path in directory.iterdir()))

    def test_duplicatePrivatePathIdentity_isRedactedInHumanAndJsonReports(self):
        directory = self.project / ".codex/agents"
        directory.mkdir(parents=True)
        first = directory / "first.toml"
        second = directory / "second.toml"
        def invoke(*arguments):
            output = io.StringIO()
            diagnostics = io.StringIO()
            with patch.object(catalog.sys, "argv", ["catalog.py", "agents", *arguments]), \
                 patch("sys.stdout", output), patch("sys.stderr", diagnostics):
                status = catalog.main()
            return status, output.getvalue(), diagnostics.getvalue()

        for private_identity in ("/host/private/agent-name", r"C:\private\agent-name", "private\nagent-name", "private\x01agent-name"):
            with self.subTest(identity=repr(private_identity)):
                content = f"name = {json.dumps(private_identity)}\ndescription = \"fixture\"\n"
                first.write_text(content)
                second.write_text(content)
                before = {path.name: path.read_bytes() for path in directory.iterdir()}

                status, human, diagnostics = invoke("install-missing", str(self.project))
                self.assertEqual(1, status)
                self.assertIn(".codex/agents/first.toml", human)
                self.assertIn(".codex/agents/second.toml", human)
                self.assertIn("conflict: <redacted>", human)
                self.assertIn("recovery:", human)
                self.assertIn("catalog: duplicate-project-agent-identity", diagnostics)
                self.assertNotIn(private_identity, human + diagnostics)

                status, serialized, diagnostics = invoke("install-missing", str(self.project), "--json")
                self.assertEqual(1, status)
                result = json.loads(serialized)
                self.assertEqual("duplicate-project-agent-identity", result["error"])
                self.assertEqual("<redacted>", result["conflict"]["name"])
                self.assertTrue(result["conflict"]["identity_redacted"])
                self.assertEqual([".codex/agents/first.toml", ".codex/agents/second.toml"], result["conflict"]["paths"])
                self.assertNotIn(private_identity, serialized + diagnostics)
                self.assertEqual(before, {path.name: path.read_bytes() for path in directory.iterdir()})
                self.assertFalse(any(path.name.startswith("flowkit-") for path in directory.iterdir()))

    def test_destinationIdentityConflict_reportsBothRelativePathsBeforeWrites(self):
        entry = catalog.agent_manifest()["agents"][0]
        destination = self.project / entry["destination"]
        destination.parent.mkdir(parents=True)
        competitor = destination.parent / "custom-copy.toml"
        competitor.write_text(f'name = "{entry["name"]}"\ndescription = "fixture"\n')
        before = competitor.read_bytes()

        result = self.operation()

        self.assertEqual("agent-identity-destination-conflict", result["error"])
        self.assertEqual({
            "name": entry["name"],
            "identity_redacted": False,
            "paths": [".codex/agents/custom-copy.toml", entry["destination"]],
            "recovery": "Rename or remove the competing definition after checking dependent assignments, then retry the operation.",
        }, result["conflict"])
        self.assertEqual(["failed"] + ["not-attempted"] * 8, [target["outcome"] for target in result["targets"]])
        self.assertEqual(before, competitor.read_bytes())
        self.assertFalse(destination.exists())

    def test_humanAgentOperation_reportsProvenanceInputsOutcomesAndRecovery(self):
        def invoke(*arguments):
            output = io.StringIO()
            diagnostics = io.StringIO()
            with patch.object(catalog.sys, "argv", ["catalog.py", "agents", *arguments]), \
                 patch("sys.stdout", output), patch("sys.stderr", diagnostics):
                status = catalog.main()
            return status, output.getvalue(), diagnostics.getvalue()

        status, output, diagnostics = invoke("install-missing", str(self.project))
        self.assertEqual(0, status)
        self.assertIn(f"package: {self.metadata['id']} {self.metadata['version']}", output)
        self.assertIn(f"artifact: {self.metadata['artifact']}", output)
        self.assertIn(f"sha256: {self.metadata['sha256']}", output)
        self.assertIn(f"source: {self.metadata['source_repository']}@{self.metadata['source_commit']}", output)
        self.assertIn(f"source_sha256: {self.metadata['source_sha256']}", output)
        self.assertIn("inputs: agent=none all=false", output)
        self.assertIn(".codex/agents/flowkit-coder.toml: created", output)
        self.assertEqual("", diagnostics)

        coder = self.project / ".codex/agents/flowkit-coder.toml"
        coder.write_text(coder.read_text() + "# custom\n")
        status, output, diagnostics = invoke("reset", str(self.project), "--agent", "FlowKit-Coder")
        self.assertEqual(0, status)
        self.assertIn("inputs: agent=FlowKit-Coder all=false", output)
        self.assertIn("warning: Reset discards customizations in the selected current targets.", output)
        self.assertIn(".codex/agents/flowkit-coder.toml: reset", output)
        self.assertEqual("", diagnostics)

        original = catalog._atomic_bytes
        calls = 0
        def fail_second(path, content):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise PermissionError("fixture partial failure")
            original(path, content)
        with patch.object(catalog, "_atomic_bytes", side_effect=fail_second):
            status, output, diagnostics = invoke("reset", str(self.project), "--all")
        self.assertEqual(1, status)
        self.assertIn("inputs: agent=none all=true", output)
        self.assertIn(".codex/agents/flowkit-roadmap-agent.toml: reset", output)
        self.assertIn(".codex/agents/flowkit-specifier.toml: failed", output)
        self.assertIn(".codex/agents/flowkit-planner.toml: not-attempted", output)
        self.assertIn("recovery: Inspect target outcomes and retry the same explicit operation after resolving the reported failure.", output)
        self.assertIn("catalog: PermissionError", diagnostics)
        self.assertNotIn(str(self.project), output + diagnostics)

        private_selector = "/host/private/not-an-agent"
        status, output, diagnostics = invoke("reset", str(self.project), "--agent", private_selector)
        self.assertEqual(1, status)
        self.assertIn("inputs: agent=none all=false", output)
        self.assertNotIn(private_selector, output + diagnostics)

    def test_partialWrite_reportAndSameOperationRetry(self):
        original = catalog._atomic_bytes
        calls = 0
        def fail_second(path, content):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise PermissionError("fixture failure")
            original(path, content)
        with patch.object(catalog, "_atomic_bytes", side_effect=fail_second):
            result = self.operation()
        self.assertEqual("partial", result["status"])
        self.assertEqual(["created", "failed"] + ["not-attempted"] * 7, [t["outcome"] for t in result["targets"]])
        self.assertNotIn(str(self.project), json.dumps(result))
        self.assertEqual("complete", self.operation()["status"])

    def test_resetFailure_preservesUnattemptedBytes_andRetriesSelectedTargets(self):
        self.operation()
        directory = self.project / ".codex/agents"
        for path in directory.glob("*.toml"):
            path.write_bytes(path.read_bytes() + b"# custom\n")
        manifest = catalog.agent_manifest()
        before = {p.name: p.read_bytes() for p in directory.glob("*.toml")}
        original = catalog._atomic_bytes
        calls = 0
        def fail_second(path, content):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise PermissionError("fixture reset failure")
            original(path, content)
        with patch.object(catalog, "_atomic_bytes", side_effect=fail_second):
            result = self.operation("reset", all_agents=True)
        self.assertEqual(["reset", "failed"] + ["not-attempted"] * 7,
                         [entry["outcome"] for entry in result["targets"]])
        for entry in manifest["agents"][1:]:
            path = self.project / entry["destination"]
            self.assertEqual(before[path.name], path.read_bytes())
        self.assertEqual("complete", self.operation("reset", all_agents=True)["status"])

    def test_unparseableUnrelatedFile_warnedAndPreserved(self):
        unrelated = self.project / ".codex/agents/unrelated.toml"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_bytes(b"invalid = [")
        result = self.operation()
        self.assertEqual("complete", result["status"])
        self.assertEqual(["Unparseable project agent: .codex/agents/unrelated.toml"], result["warnings"])
        self.assertEqual(b"invalid = [", unrelated.read_bytes())

    def test_invalidSelector_reportDoesNotEchoPrivateInput(self):
        result = self.operation("reset", agent="/host/private/not-an-agent")
        self.assertEqual("failed", result["status"])
        self.assertNotIn("/host/private", json.dumps(result))

    def test_failedCacheReplacement_keepsPreviousDefaults(self):
        target = self.project / ".specify/flow-kit/agent-defaults/package.zip"
        before = target.read_bytes()
        invalid = dict(self.metadata, sha256="0" * 64)
        with self.assertRaises(ValueError):
            catalog.cache_agent_defaults(self.project, self.archive, invalid)
        self.assertEqual(before, target.read_bytes())

    def test_wrongSourceDigest_rejectedBeforeCacheOrAgentMutation(self):
        invalid = dict(self.metadata, source_sha256="0" * 64)
        with self.assertRaises(ValueError):
            catalog.cache_agent_defaults(self.project, self.archive, invalid)
        metadata_path = self.project / ".specify/flow-kit/agent-defaults/manifest.json"
        self.assertEqual(self.metadata, json.loads(metadata_path.read_text()))
        metadata_path.write_text(json.dumps(invalid))
        result = self.operation()
        self.assertEqual("agent-source-digest-mismatch", result["error"])
        self.assertFalse((self.project / ".codex").exists())

    def test_preflightFailure_identifiesActualUnusableTarget(self):
        manifest = catalog.agent_manifest()
        target = self.project / manifest["agents"][3]["destination"]
        target.mkdir(parents=True)
        result = self.operation()
        self.assertEqual("failed", result["status"])
        self.assertEqual(["not-attempted"] * 3 + ["failed"] + ["not-attempted"] * 5,
                         [entry["outcome"] for entry in result["targets"]])
        self.assertEqual([target], list(target.parent.iterdir()))

    def test_cacheSwapFailure_restoresPreviousDirectory(self):
        before = (self.project / ".specify/flow-kit/agent-defaults/package.zip").read_bytes()
        original = catalog.os.replace
        calls = 0
        def fail_stage(source, target):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise PermissionError("fixture swap failure")
            return original(source, target)
        with patch.object(catalog.os, "replace", side_effect=fail_stage), self.assertRaises(PermissionError):
            catalog.cache_agent_defaults(self.project, self.archive, self.metadata)
        self.assertEqual(before, (self.project / ".specify/flow-kit/agent-defaults/package.zip").read_bytes())

    def test_symlinkAncestor_andNonportableMetadata_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.project / ".codex").symlink_to(outside, target_is_directory=True)
        self.assertEqual("failed", self.operation()["status"])
        self.assertEqual([], list(outside.iterdir()))
        invalid = dict(self.metadata, source_repository="https://github.com/example/repo absolute: /host/private")
        with self.assertRaises(ValueError):
            catalog.cache_agent_defaults(self.project, self.archive, invalid)

    def test_cliJson_andArgumentErrors(self):
        with patch.object(catalog.sys, "argv", ["catalog.py", "agents", "reset", str(self.project)]):
            with self.assertRaises(SystemExit) as error:
                catalog.main()
        self.assertEqual(2, error.exception.code)
        with patch.object(catalog.sys, "argv", ["catalog.py", "agents", "install-missing", str(self.project), "--json"]), patch("builtins.print") as output:
            self.assertEqual(0, catalog.main())
            self.assertEqual("complete", json.loads(output.call_args.args[0])["status"])

class NativeAgentBundleTests(unittest.TestCase):
    def test_nativeInstallRefreshResetRemove_preserveConsumerCopies(self):
        import os
        executable = os.environ.get("SPECIFY_BIN")
        if not executable or not Path(executable).is_file():
            self.skipTest("set SPECIFY_BIN to the supported installed CLI")
        with tempfile.TemporaryDirectory(prefix="flowkit-agent-native-") as directory:
            project = Path(directory)
            completed = subprocess.run([executable, "init", "--here", "--force", "--non-interactive", "--integration", "codex", "--integration-options=--skills"], cwd=project, text=True, capture_output=True)
            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            payload_files = {
                project / ".worktreeinclude": b".agents/\n.specify/workflow-feedback/\n.specify/extensions/local-extension/\n",
                project / ".agents/skills/consumer-owned/SKILL.md": b"# Consumer skill\nKeep this payload.\n",
                project / ".specify/workflow-feedback/retained.json": b'{"consumer":"retained"}\n',
                project / ".specify/extensions/local-extension/owned.txt": b"Unrelated component data.\n",
                project / "consumer-config.toml": b"setting = \"consumer-owned\"\n",
            }
            for path, content in payload_files.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            payload_before = {path: path.read_bytes() for path in payload_files}
            with patch.object(catalog, "selected_specify", return_value=executable):
                catalog.install(project, False, development_snapshot=True)
                configs = project / ".codex/agents"
                manifest_entries = catalog.agent_manifest()["agents"]
                self.assertEqual(9, len(manifest_entries))
                self.assertEqual(9, len(list(configs.glob("flowkit-*.toml"))))
                for entry in manifest_entries:
                    with self.subTest(agent=entry["name"]):
                        self.assertEqual(
                            (catalog.AGENT_SOURCE / entry["file"]).read_bytes(),
                            (project / entry["destination"]).read_bytes(),
                        )
                self.assertEqual(payload_before, {path: path.read_bytes() for path in payload_files})
                coder = configs / "flowkit-coder.toml"
                coder.write_text(coder.read_text() + "# Native consumer customization\n")
                unrelated = configs / "unrelated.toml"
                unrelated.write_text('name="Unrelated"\n')
                before = {p.name: p.read_bytes() for p in configs.glob("*.toml")}
                catalog.install(project, True, development_snapshot=True)
                self.assertEqual(before, {p.name: p.read_bytes() for p in configs.glob("*.toml")})
                self.assertEqual(payload_before, {path: path.read_bytes() for path in payload_files})
                result = catalog.agent_operation(project, "reset", agent="FlowKit-Coder")
                self.assertEqual("complete", result["status"])
                self.assertNotIn(b"# Native consumer", coder.read_bytes())
                reset_before = {p.name: p.read_bytes() for p in configs.glob("*.toml")}
                catalog.remove(project)
                self.assertEqual(reset_before, {p.name: p.read_bytes() for p in configs.glob("*.toml")})
                self.assertFalse((project / ".specify/flow-kit/agent-defaults").exists())
                self.assertEqual(payload_before, {path: path.read_bytes() for path in payload_files})

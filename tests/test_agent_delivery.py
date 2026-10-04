"""Consumer-owned agent lifecycle, integrity and recovery checks."""
from __future__ import annotations

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
        manifest, members = catalog.validate_agent_archive(other, "0.1.0")
        self.assertEqual(8, len(manifest["agents"]))
        self.assertEqual(9, len(members))
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
        self.assertEqual(["created"] * 8, [t["outcome"] for t in result["targets"]])
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
        self.assertEqual(8, len(self.operation("reset", all_agents=True)["targets"]))
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
        manifest["package"]["version"] = "0.2.0"
        manifest["agents"].append({"name": "Fixture-New Role", "file": "agents/new.toml", "destination": ".codex/agents/new.toml"})
        (source / "agents/new.toml").write_text('name = "Fixture-New Role"\ndescription = "Fixture"\ndeveloper_instructions = "No work"\nmodel="gpt-6-luna"\nmodel_reasoning_effort="high"\n')
        (source / "manifest.yml").write_text(yaml.safe_dump(manifest))
        with patch.object(catalog, "AGENT_SOURCE", source):
            metadata = catalog.package_agents(self.archive)
        catalog.cache_agent_defaults(self.project, self.archive, metadata)
        self.assertEqual(before, {p.name: p.read_bytes() for p in directory.iterdir()})
        result = self.operation()
        self.assertEqual("created", result["targets"][-1]["outcome"])
        self.assertEqual(9, len(list(directory.iterdir())))
        manifest["agents"] = manifest["agents"][-1:]
        (source / "manifest.yml").write_text(yaml.safe_dump(manifest))
        with patch.object(catalog, "AGENT_SOURCE", source):
            metadata = catalog.package_agents(self.archive)
        catalog.cache_agent_defaults(self.project, self.archive, metadata)
        self.assertEqual(1, len(self.operation("reset", all_agents=True)["targets"]))
        self.assertEqual(9, len(list(directory.iterdir())))

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
        self.assertEqual(["created", "failed"] + ["not-attempted"] * 6, [t["outcome"] for t in result["targets"]])
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
        self.assertEqual(["reset", "failed"] + ["not-attempted"] * 6,
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
        self.assertEqual(["not-attempted"] * 3 + ["failed"] + ["not-attempted"] * 4,
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
            feedback = project / ".specify/workflow-feedback/retained.json"
            feedback.parent.mkdir(parents=True, exist_ok=True)
            feedback.write_text("{}\n")
            with patch.object(catalog, "selected_specify", return_value=executable):
                catalog.install(project, False, development_snapshot=True)
                configs = project / ".codex/agents"
                self.assertEqual(8, len(list(configs.glob("*.toml"))))
                coder = configs / "flowkit-coder.toml"
                coder.write_text(coder.read_text() + "# Native consumer customization\n")
                unrelated = configs / "unrelated.toml"
                unrelated.write_text('name="Unrelated"\n')
                before = {p.name: p.read_bytes() for p in configs.glob("*.toml")}
                catalog.install(project, True, development_snapshot=True)
                self.assertEqual(before, {p.name: p.read_bytes() for p in configs.glob("*.toml")})
                result = catalog.agent_operation(project, "reset", agent="FlowKit-Coder")
                self.assertEqual("complete", result["status"])
                self.assertNotIn(b"# Native consumer", coder.read_bytes())
                reset_before = {p.name: p.read_bytes() for p in configs.glob("*.toml")}
                catalog.remove(project)
                self.assertEqual(reset_before, {p.name: p.read_bytes() for p in configs.glob("*.toml")})
                self.assertFalse((project / ".specify/flow-kit/agent-defaults").exists())
                self.assertEqual("{}\n", feedback.read_text())

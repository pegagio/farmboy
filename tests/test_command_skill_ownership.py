"""Command skill ownership checks for project-local Codex installations."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]
SOURCE_CONTROLLER = ROOT / "controllers/farmboy/scripts/python/controller.py"
COMMAND_ID = "speckit.flow-wiki.query"
SKILL_NAME = "speckit-flow-wiki-query"
EXTENSION_ID = "flow-wiki"
COMMAND_FILE = "commands/speckit.flow-wiki.query.md"


def load_controller(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load controller from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class OwnerConsumer:
    """Build a disposable consumer with a registered extension command."""

    def __init__(self, root: Path):
        self.root = root
        self.skill_path = root / f".agents/skills/{SKILL_NAME}/SKILL.md"
        self.manifest_path = root / f".specify/extensions/{EXTENSION_ID}/extension.yml"
        self.command_path = root / f".specify/extensions/{EXTENSION_ID}/{COMMAND_FILE}"
        self.registry_path = root / ".specify/extensions/.registry"
        self.core_manifest_path = root / ".specify/integrations/codex.manifest.json"
        self.version = "2.0.1"
        self.skill_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.command_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.command_path.write_text("# Query command source\n", encoding="utf-8")
        self.write_manifest()
        self.write_registry()
        self.write_skill()
        self.core_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.core_manifest_path.write_text(json.dumps({"integration": "codex", "files": {}}), encoding="utf-8")

    def write_manifest(self, *, version: str | None = None, commands: list[dict] | None = None, raw: str | None = None) -> None:
        if raw is None:
            manifest = {
                "schema_version": "1.0",
                "extension": {"id": EXTENSION_ID, "version": self.version if version is None else version},
                "provides": {"commands": commands if commands is not None else [{"name": COMMAND_ID, "file": COMMAND_FILE}]},
            }
            raw = yaml.safe_dump(manifest, sort_keys=False)
        self.manifest_path.write_text(raw, encoding="utf-8")

    def write_registry(self, *, enabled: bool = True, version: str | None = None, digest: str | None = None, records: dict | None = None) -> None:
        manifest_digest = hashlib.sha256(self.manifest_path.read_bytes()).hexdigest() if digest is None else digest
        if records is None:
            records = {
                EXTENSION_ID: {
                    "version": self.version if version is None else version,
                    "manifest_hash": f"sha256:{manifest_digest}",
                    "enabled": enabled,
                    "registered_commands": {"codex": [COMMAND_ID]},
                }
            }
        self.registry_path.write_text(json.dumps({"schema_version": "1.0", "extensions": records}), encoding="utf-8")

    def write_skill(self, *, name: str = SKILL_NAME, source: str | None = None) -> None:
        if source is None:
            source = f"{EXTENSION_ID}:{COMMAND_FILE}"
        self.skill_path.write_text(
            f"---\nname: {name}\nmetadata:\n  source: {source}\n---\n\n# Test command skill\n",
            encoding="utf-8",
        )


class CommandSkillOwnershipTests(unittest.TestCase):
    """Validate core and registered extension ownership without trusting name alone."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.controller = load_controller(SOURCE_CONTROLLER, "farmboy_owner_test_controller")

    def test_actualRegisteredWikiCommand_resolvesWithObservedOwnershipEvidence(self) -> None:
        result = self.controller.resolve_installed_skill(ROOT, "speckit.flow-wiki.query")
        self.assertEqual("registered-extension", result["provenance"])
        self.assertEqual("flow-wiki", result["owner_id"])
        self.assertEqual("2.0.1", result["owner_version"])
        self.assertEqual(".specify/extensions/flow-wiki/commands/speckit.flow-wiki.query.md", result["command_source_path"])
        self.assertEqual(hashlib.sha256((ROOT / result["command_source_path"]).read_bytes()).hexdigest(), result["command_source_sha256"])
        self.assertEqual(hashlib.sha256(Path(result["path"]).read_bytes()).hexdigest(), result["skill_sha256"])
        self.assertIn("rendered skill body equality is not verified", result["integrity_limit"])
        self.assertNotIn("rendered_skill_sha256", result)

    def test_copiedControllerLayout_acceptsRegisteredExtensionAbsentFromCoreFileMap(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            consumer = OwnerConsumer(root)
            controller_path = root / ".specify/farmboy/scripts/python/controller.py"
            controller_path.parent.mkdir(parents=True)
            shutil.copy2(SOURCE_CONTROLLER, controller_path)
            copied = load_controller(controller_path, "farmboy_owner_copied_controller")
            result = copied.resolve_installed_skill(root, COMMAND_ID)
        self.assertEqual("registered-extension", result["provenance"])
        self.assertEqual(EXTENSION_ID, result["owner_id"])

    def test_coreManifestDigestRemainsAuthoritative_andMismatchCannotUseExtensionFallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            consumer = OwnerConsumer(root)
            relative_skill = consumer.skill_path.relative_to(root).as_posix()
            consumer.core_manifest_path.write_text(
                json.dumps({"integration": "codex", "files": {relative_skill: hashlib.sha256(consumer.skill_path.read_bytes()).hexdigest()}}),
                encoding="utf-8",
            )
            result = self.controller.resolve_installed_skill(root, COMMAND_ID)
            self.assertEqual("codex.manifest.json", result["provenance"])
            consumer.skill_path.write_text(consumer.skill_path.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differs from its provenance record"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)

    def test_coreManifestOnlyCommandStillRequiresMatchingDigest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill_path = root / ".agents/skills/speckit-tasks/SKILL.md"
            skill_path.parent.mkdir(parents=True)
            skill_path.write_text("---\nname: speckit-tasks\n---\n", encoding="utf-8")
            core_manifest = root / ".specify/integrations/codex.manifest.json"
            core_manifest.parent.mkdir(parents=True)
            core_manifest.write_text(json.dumps({"files": {skill_path.relative_to(root).as_posix(): hashlib.sha256(skill_path.read_bytes()).hexdigest()}}), encoding="utf-8")
            result = self.controller.resolve_installed_skill(root, "speckit.tasks")
        self.assertEqual("codex.manifest.json", result["provenance"])

    def test_registeredExtensionOwnerRejectsDisabledAmbiguousAndUnregisteredCommands(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            consumer = OwnerConsumer(root)
            consumer.write_registry(enabled=False)
            with self.assertRaisesRegex(ValueError, "disabled"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)
            consumer.write_registry(records={
                EXTENSION_ID: json.loads(consumer.registry_path.read_text())["extensions"][EXTENSION_ID],
                "other-extension": {
                    "version": "1.0.0", "manifest_hash": "sha256:" + "0" * 64, "enabled": True,
                    "registered_commands": {"codex": [COMMAND_ID]},
                },
            })
            with self.assertRaisesRegex(ValueError, "ambiguous"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)
            consumer.write_registry(records={EXTENSION_ID: {
                "version": consumer.version,
                "manifest_hash": "sha256:" + hashlib.sha256(consumer.manifest_path.read_bytes()).hexdigest(),
                "enabled": True,
                "registered_commands": {"codex": ["speckit.flow-wiki.other"]},
            }})
            with self.assertRaisesRegex(ValueError, "no skill provenance"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)

    def test_extensionRegistryRejectsDuplicateJsonKeysBeforeOwnershipCanBeOverwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            consumer = OwnerConsumer(root)
            record = json.loads(consumer.registry_path.read_text(encoding="utf-8"))["extensions"][EXTENSION_ID]

            duplicate_enabled = json.dumps(record).replace('"enabled": true', '"enabled": false, "enabled": true')
            consumer.registry_path.write_text(
                '{"schema_version":"1.0","extensions":{"flow-wiki":' + duplicate_enabled + '}}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "registry is malformed"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)

            disabled = dict(record)
            disabled["enabled"] = False
            enabled = dict(record)
            enabled["enabled"] = True
            consumer.registry_path.write_text(
                '{"schema_version":"1.0","extensions":{"flow-wiki":'
                + json.dumps(disabled)
                + ',"flow-wiki":'
                + json.dumps(enabled)
                + '}}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "registry is malformed"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)

    def test_registeredExtensionOwnerRejectsMalformedRegistryManifestAndMissingHash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            consumer = OwnerConsumer(root)
            consumer.registry_path.write_text("{broken", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "registry is malformed"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)
            consumer.write_manifest(raw="extension: [broken\n")
            consumer.write_registry()
            with self.assertRaisesRegex(ValueError, "manifest is malformed"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)
            consumer.write_manifest()
            consumer.write_registry(digest="")
            with self.assertRaisesRegex(ValueError, "hash is missing or malformed"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)

    def test_registeredExtensionOwnerRejectsIdentityVersionAndDeclarationMismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            consumer = OwnerConsumer(root)
            consumer.write_registry(version="9.9.9")
            with self.assertRaisesRegex(ValueError, "identity or version"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)
            consumer.write_registry()
            consumer.write_registry(digest="0" * 64)
            with self.assertRaisesRegex(ValueError, "manifest hash differs"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)
            wrong_identity = {
                "schema_version": "1.0",
                "extension": {"id": "other-extension", "version": consumer.version},
                "provides": {"commands": [{"name": COMMAND_ID, "file": COMMAND_FILE}]},
            }
            consumer.write_manifest(raw=yaml.safe_dump(wrong_identity, sort_keys=False))
            consumer.write_registry()
            with self.assertRaisesRegex(ValueError, "identity or version"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)
            consumer.write_manifest()
            consumer.write_manifest(commands=[{"name": "speckit.flow-wiki.other", "file": COMMAND_FILE}])
            consumer.write_registry()
            with self.assertRaisesRegex(ValueError, "does not declare"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)

    def test_registeredExtensionOwnerRejectsUnsafeCommandPathAndSourceMetadataMismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            consumer = OwnerConsumer(root)
            consumer.write_manifest(commands=[{"name": COMMAND_ID, "file": "../../outside.md"}])
            consumer.write_registry()
            with self.assertRaisesRegex(ValueError, "path is unsafe"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)
            consumer.write_manifest()
            consumer.write_registry()
            consumer.write_skill(source="flow-wiki:commands/other.md")
            with self.assertRaisesRegex(ValueError, "source metadata differs"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)
            consumer.write_skill(source=None)
            consumer.skill_path.write_text("---\nname: speckit-flow-wiki-query\n---\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source metadata differs"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)

    def test_registeredExtensionOwnerRejectsSymlinkedManifestSourceAndSkill(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            consumer = OwnerConsumer(root)
            outside = root / "outside.md"
            outside.write_text("outside\n", encoding="utf-8")
            consumer.command_path.unlink()
            consumer.command_path.symlink_to(outside)
            consumer.write_registry()
            with self.assertRaisesRegex(ValueError, "symlink"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)
            consumer.command_path.unlink()
            consumer.command_path.write_text("# Source\n", encoding="utf-8")
            consumer.write_registry()
            consumer.skill_path.unlink()
            consumer.skill_path.symlink_to(outside)
            with self.assertRaisesRegex(ValueError, "symlink"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)

    def test_registeredExtensionOwnerRejectsSymlinkedManifestAndMissingSource(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            consumer = OwnerConsumer(root)
            outside = root / "outside.yml"
            outside.write_text(consumer.manifest_path.read_text(encoding="utf-8"), encoding="utf-8")
            consumer.manifest_path.unlink()
            consumer.manifest_path.symlink_to(outside)
            with self.assertRaisesRegex(ValueError, "symlink"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)
            consumer.manifest_path.unlink()
            consumer.write_manifest()
            consumer.write_registry()
            consumer.command_path.unlink()
            with self.assertRaisesRegex(ValueError, "missing"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)

    def test_installedSkillRejectsWrongNameDuplicatesAndCoreManifestSymlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            consumer = OwnerConsumer(root)
            consumer.write_skill(name="wrong-name")
            with self.assertRaisesRegex(ValueError, "different name"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)
            consumer.write_skill()
            duplicate = root / f".codex/skills/{SKILL_NAME}/SKILL.md"
            duplicate.parent.mkdir(parents=True)
            duplicate.write_text(consumer.skill_path.read_text(encoding="utf-8"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ambiguous installed"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            consumer = OwnerConsumer(root)
            consumer.core_manifest_path.unlink()
            consumer.core_manifest_path.symlink_to(consumer.skill_path)
            with self.assertRaisesRegex(ValueError, "manifest path is unsafe"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            consumer = OwnerConsumer(root)
            consumer.core_manifest_path.unlink()
            integrations = consumer.core_manifest_path.parent
            integrations.rmdir()
            integrations.symlink_to(root / "outside-integrations")
            with self.assertRaisesRegex(ValueError, "manifest path is unsafe"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)

    def test_missingCoreManifestRetainsLegacyPathOnlyWithoutAvailableOwner(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill_path = root / ".agents/skills/speckit-legacy/SKILL.md"
            skill_path.parent.mkdir(parents=True)
            skill_path.write_text("---\nname: speckit-legacy\n---\n", encoding="utf-8")
            result = self.controller.resolve_installed_skill(root, "speckit.legacy")
            expected_digest = hashlib.sha256(skill_path.read_bytes()).hexdigest()
        self.assertEqual("unrecorded", result["provenance"])
        self.assertEqual(expected_digest, result["skill_sha256"])

    def test_missingCoreManifestRejectsSkillThatClaimsUnregisteredExtensionOwner(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            consumer = OwnerConsumer(root)
            consumer.core_manifest_path.unlink()
            consumer.registry_path.unlink()
            with self.assertRaisesRegex(ValueError, "without an active registration"):
                self.controller.resolve_installed_skill(root, COMMAND_ID)


if __name__ == "__main__":
    unittest.main()

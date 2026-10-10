"""Tests for strict FarmBoy phase-lifecycle evidence handling."""

from __future__ import annotations

import hashlib
import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "controllers/farmboy/scripts/python/phase_lifecycle.py"
FIXTURE_PATH = ROOT / "tests/consumer-fixtures/workflow-improvements/phase-lifecycle-cases.json"


def load_module():
    spec = importlib.util.spec_from_file_location("farmboy_phase_lifecycle_under_test", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class RecoveryStartHistoryTests(unittest.TestCase):
    """The historical start proof stays tied to retained source records."""

    def setUp(self) -> None:
        self.module = load_module()
        self.feature = "specs/901-recovery-history"

    def _materialize(self, root: Path) -> dict:
        paths = {
            "source_run": ".specify/flow-controllers/runs/source-implement/summary.json",
            "baseline": ".specify/flow-controllers/runs/source-implement/baseline.json",
            "original_spec": ".specify/flow-controllers/runs/authorized-status/spec-before.md",
            "current_spec": f"{self.feature}/spec.md",
            "status_run": ".specify/flow-controllers/runs/authorized-status/summary.json",
            "status_authorization": ".specify/flow-controllers/runs/authorized-status/authorization.json",
            "status_effect": ".specify/flow-controllers/runs/authorized-status/effect.json",
            "status_validation": ".specify/flow-controllers/runs/authorized-status/bridge-validation.json",
            "feature_pointer": ".specify/feature.json",
        }
        current = b"**Status**: Complete\n# Reviewed scope\n"
        original = current.replace(b"**Status**: Complete", b"**Status**: Draft", 1)
        current_path = root / paths["current_spec"]
        current_path.parent.mkdir(parents=True, exist_ok=True)
        current_path.write_bytes(current)
        original_path = root / paths["original_spec"]
        original_path.parent.mkdir(parents=True, exist_ok=True)
        original_path.write_bytes(original)
        pointer = json.dumps({"feature_directory": self.feature}, sort_keys=True).encode()
        pointer_path = root / paths["feature_pointer"]
        pointer_path.parent.mkdir(parents=True, exist_ok=True)
        pointer_path.write_bytes(pointer)
        baseline_body = {"feature_directory": self.feature, "specification_sha256": sha(original),
                         "pointer_sha256": sha(pointer), "tasks": {"T001": {"marker": " "}}}
        baseline_digest = sha(json.dumps(baseline_body, sort_keys=True, separators=(",", ":")).encode())
        baseline = {"baseline": baseline_body, "baseline_sha256": baseline_digest,
                    "remaining_ids": ["task:T001"], "state": "captured"}
        source_run = {
            "run_id": "source-implement-run", "workflow_id": "farmboy-implement", "status": "stopped",
            "started_at": "2026-10-01T12:00:00+00:00",
            "steps": {"implement-eligible-work": {"status": "completed"},
                      "capture-implementation-baseline": {"status": "completed"}},
            "child_tasks": [{"agent": "FarmBoy Coder", "step_id": "implement-eligible-work", "child_id": "coder-child-1"}],
            "effective_assignments": [{"agent_name": "FarmBoy Coder", "step_id": "implement-eligible-work"}],
            "changed_files": [f"{self.feature}/implementation.py"],
            "baseline_evidence": {"baseline_sha256": baseline_digest, "path": paths["baseline"]},
        }
        implementation = root / source_run["changed_files"][0]
        implementation.parent.mkdir(parents=True, exist_ok=True)
        implementation.write_text("implemented evidence\n")
        status_records = {
            "baseline": baseline,
            "source_run": source_run,
            "status_run": {
                "run_id": "authorized-status-run", "workflow_id": "farmboy-closeout",
                "steps": {"mark-converged-specification-complete": {"status": "completed"}},
                "changed_files": [paths["current_spec"]],
            },
            "status_authorization": {"status_action": "run", "feature_directory": self.feature,
                "spec_before_sha256": sha(original), "authority": "explicit bounded status-only authorization"},
            "status_effect": {
                "step_id": "mark-converged-specification-complete",
                "kind": "bounded-existing-specification-status-update", "feature_directory": self.feature,
                "before_status": "Draft", "after_status": "Complete", "before_sha256": sha(original),
                "after_sha256": sha(current), "exact_diff": "**Status**: Draft -> **Status**: Complete",
                "other_specification_bytes_preserved": True,
            },
            "status_validation": {
                "state": "ready", "spec_path": paths["current_spec"], "before_sha256": sha(original),
                "after_sha256": sha(current), "allowed_change": "Status Draft to Complete only",
                "requirements_and_all_other_bytes_preserved": True, "convergence_intent_preserved": True,
                "future_manual_task_ids": ["T001"], "feature_acceptance_established": False,
            },
            "feature_pointer": json.loads(pointer),
        }
        for name, value in status_records.items():
            destination = root / paths[name]
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(value, sort_keys=True))
        references = {name: {"path": path, "sha256": sha((root / path).read_bytes())}
                      for name, path in paths.items()}
        return {
            "action": "validate-start-history",
            "schema_version": "1.0",
            "feature_directory": self.feature,
            "current_scope_sha256": references["current_spec"]["sha256"],
            "trusted_inputs": references,
        }

    def test_validateRecoveryStartHistory_preservesActualStartAndBothScopes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            packet = self._materialize(root)
            validated = self.module.validate_recovery_start_history(root, packet)
            source_summary = json.loads((root / packet["trusted_inputs"]["source_run"]["path"]).read_text())
            self.assertEqual("validated", validated["state"])
            self.assertEqual(source_summary["started_at"], validated["occurred_at"])
            self.assertEqual("farmboy-implement", validated["source_workflow_id"])
            self.assertEqual("capture-implementation-baseline", validated["completed_step_ids"][0])
            self.assertEqual(["T001"], validated["future_manual_task_ids"])
            self.assertEqual(packet["current_scope_sha256"], validated["scope_sha256"])
            self.assertNotEqual(validated["scope_sha256"], validated["original_scope_sha256"])

    def test_phaseLifecycleCli_exposesReadOnlyValidatedStartHistory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            packet = self._materialize(root)
            command = [sys.executable, str(ROOT / "controllers/farmboy/scripts/python/controller.py"),
                       "phase-lifecycle", "--project", str(root)]
            result = subprocess.run(command, input=json.dumps(packet), text=True,
                                    capture_output=True, check=False)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("validated", json.loads(result.stdout)["state"])

            packet["trusted_inputs"]["source_run"]["sha256"] = "0" * 64
            stale = subprocess.run(command, input=json.dumps(packet), text=True,
                                   capture_output=True, check=False)
            self.assertNotEqual(0, stale.returncode)
            self.assertEqual("blocked", json.loads(stale.stdout)["state"])

    def test_validateRecoveryStartHistory_rejectsStaleAndWrongTargetReferences(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            packet = self._materialize(root)
            raw = (root / packet["trusted_inputs"]["status_effect"]["path"]).read_bytes()
            (root / packet["trusted_inputs"]["status_effect"]["path"]).write_bytes(raw + b" ")
            with self.assertRaisesRegex(self.module.LifecycleError, "stale-trusted-input"):
                self.module.validate_recovery_start_history(root, packet)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            packet = self._materialize(root)
            packet["trusted_inputs"]["source_run"]["path"] = packet["trusted_inputs"]["baseline"]["path"]
            with self.assertRaisesRegex(self.module.LifecycleError, "start-history-stale-trusted-input"):
                self.module.validate_recovery_start_history(root, packet)

    def test_validateRecoveryStartHistory_requiresExactSchemaVersion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            packet = self._materialize(root)
            packet["schema_version"] = "9.9"
            with self.assertRaisesRegex(self.module.LifecycleError, "start-history-version-invalid"):
                self.module.validate_recovery_start_history(root, packet)

    def test_validateRecoveryStartHistory_acceptsNoDeferredManualTasks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            packet = self._materialize(root)
            reference = packet["trusted_inputs"]["status_validation"]
            validation_path = root / reference["path"]
            validation = json.loads(validation_path.read_text(encoding="utf-8"))
            validation["future_manual_task_ids"] = []
            validation_path.write_text(json.dumps(validation, sort_keys=True))
            reference["sha256"] = sha(validation_path.read_bytes())
            result = self.module.validate_recovery_start_history(root, packet)
            self.assertEqual([], result["future_manual_task_ids"])

    def test_validateRecoveryStartHistory_rejectsNonStatusSpecificationChanges(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            packet = self._materialize(root)
            current_ref = packet["trusted_inputs"]["current_spec"]
            current_path = root / current_ref["path"]
            current_path.write_bytes(current_path.read_bytes() + b"extra normative text\n")
            current_ref["sha256"] = sha(current_path.read_bytes())
            packet["current_scope_sha256"] = current_ref["sha256"]
            with self.assertRaisesRegex(self.module.LifecycleError, "start-history-status-(effect-invalid|bridge-unverified)"):
                self.module.validate_recovery_start_history(root, packet)

    def test_validateRecoveryStartHistory_rejectsMissingRecordedCoderEffect(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            packet = self._materialize(root)
            source_ref = packet["trusted_inputs"]["source_run"]
            source_file = root / source_ref["path"]
            summary = json.loads(source_file.read_text())
            summary["child_tasks"] = []
            source_file.write_text(json.dumps(summary, sort_keys=True))
            source_ref["sha256"] = sha(source_file.read_bytes())
            with self.assertRaisesRegex(self.module.LifecycleError, "start-history-implementation-effect-missing"):
                self.module.validate_recovery_start_history(root, packet)

    def test_validateStartAttestation_bindsNativeReviewerAndCurrentSnapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            packet = self._materialize(root)
            history = self.module.validate_recovery_start_history(root, packet)
            feature = packet["feature_directory"]
            validation_path = f"{feature}/validation/phase-lifecycle/start-history-validation.json"
            validation_bytes = json.dumps(history, sort_keys=True).encode()
            validation_file = root / validation_path
            validation_file.parent.mkdir(parents=True, exist_ok=True)
            validation_file.write_bytes(validation_bytes)
            artifact_paths = {
                f"{feature}/spec.md": packet["trusted_inputs"]["current_spec"]["sha256"],
                f"{feature}/plan.md": sha(b"plan\n"),
                f"{feature}/tasks.md": sha(b"tasks\n"),
                "controllers/farmboy/scripts/python/phase_lifecycle.py": sha(
                    (ROOT / "controllers/farmboy/scripts/python/phase_lifecycle.py").read_bytes()),
                "tests/test_phase_lifecycle.py": sha((ROOT / "tests/test_phase_lifecycle.py").read_bytes()),
            }
            for relative, digest in artifact_paths.items():
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                if relative.endswith("/spec.md"):
                    pass
                elif relative.endswith("plan.md"):
                    destination.write_bytes(b"plan\n")
                elif relative.endswith("tasks.md"):
                    destination.write_bytes(b"tasks\n")
                else:
                    destination.write_bytes((ROOT / relative).read_bytes())
                self.assertEqual(digest, sha(destination.read_bytes()))
            source_map = {reference["path"]: reference["sha256"]
                          for reference in packet["trusted_inputs"].values()}
            source_map[validation_path] = sha(validation_bytes)
            source_map.update(artifact_paths)
            snapshot = {
                "feature_directory": feature,
                "scope_sha256": packet["current_scope_sha256"],
                "workflow_id": "farmboy-closeout",
                "workflow_version": "0.8.0",
                "run_id": "closeout-current-run",
                "source_map": source_map,
            }
            dispatch_summary_path = f".specify/flow-controllers/runs/{snapshot['run_id']}/summary.json"
            dispatch_summary = {
                "run_id": snapshot["run_id"], "workflow_id": snapshot["workflow_id"],
                "workflow_version": snapshot["workflow_version"],
                "child_tasks": [{"agent": "FarmBoy Reviewer", "step_id": "attest-recovery-start",
                                 "child_id": "native-reviewer-child"}],
                "effective_assignments": [{"agent_name": "FarmBoy Reviewer", "step_id": "attest-recovery-start"}],
            }
            dispatch_file = root / dispatch_summary_path
            dispatch_file.parent.mkdir(parents=True, exist_ok=True)
            dispatch_file.write_text(json.dumps(dispatch_summary, sort_keys=True))
            capture_path = f".specify/flow-controllers/runs/{snapshot['run_id']}/dispatch-summary-at-capture.json"
            capture_file = root / capture_path
            capture_file.write_bytes(dispatch_file.read_bytes())
            source_summary_ref = {"path": capture_path, "sha256": sha(capture_file.read_bytes())}
            witness_path = f".specify/flow-controllers/runs/{snapshot['run_id']}/recovery-start-dispatch-witness.json"
            witness = {"schema_version": "1.0", "kind": "main-retained-native-dispatch-witness",
                "feature_directory": feature, "scope_sha256": packet["current_scope_sha256"],
                "workflow_id": snapshot["workflow_id"], "workflow_version": snapshot["workflow_version"],
                "run_id": snapshot["run_id"], "step_id": "attest-recovery-start",
                "agent": "FarmBoy Reviewer", "child_id": "native-reviewer-child",
                "source_summary": source_summary_ref}
            witness_file = root / witness_path
            witness_file.write_text(json.dumps(witness, sort_keys=True))
            witness_ref = {"path": witness_path, "sha256": sha(witness_file.read_bytes())}
            source_map[capture_path] = source_summary_ref["sha256"]
            source_map[witness_path] = witness_ref["sha256"]
            record = {
                "schema_version": "1.0", "kind": "authorized-implementation-start",
                "reviewer": "FarmBoy Reviewer", "state": "ready", "feature_directory": feature,
                "scope_sha256": packet["current_scope_sha256"], "workflow_id": snapshot["workflow_id"],
                "workflow_version": snapshot["workflow_version"], "run_id": snapshot["run_id"],
                "step_id": "attest-recovery-start", "child_id": "native-reviewer-child",
                "source_run_id": history["source_run_id"],
                "original_scope_sha256": history["original_scope_sha256"],
                "occurred_at": history["occurred_at"],
                "history_validation": {"path": validation_path, "sha256": sha(validation_bytes)},
                "dispatch_witness": witness_ref,
                "recorded_dispatch": {
                    "agent": "FarmBoy Reviewer", "step_id": "attest-recovery-start",
                    "workflow_id": snapshot["workflow_id"], "workflow_version": snapshot["workflow_version"],
                    "run_id": snapshot["run_id"], "child_id": "native-reviewer-child",
                },
                "required_check_ids": sorted(self.module.START_CHECKS),
                "satisfied_check_ids": sorted(self.module.START_CHECKS), "unresolved_ids": [],
                "artifact_digests": artifact_paths,
            }
            record_path = f"{feature}/validation/phase-lifecycle/authorized-implementation-start.json"
            record_bytes = json.dumps(record, sort_keys=True).encode()
            record_file = root / record_path
            record_file.parent.mkdir(parents=True, exist_ok=True)
            record_file.write_bytes(record_bytes)
            reference = {"path": record_path, "sha256": sha(record_bytes),
                         "kind": "authorized-implementation-start"}
            source_map[record_path] = reference["sha256"]
            validated = self.module._validate_start_attestation(root, reference, snapshot)
            self.assertEqual("native-reviewer-child", validated["child_id"])

            record["reviewer"] = "FarmBoy Readiness Checker"
            record_bytes = json.dumps(record, sort_keys=True).encode()
            record_file.write_bytes(record_bytes)
            reference["sha256"] = sha(record_bytes)
            source_map[record_path] = reference["sha256"]
            with self.assertRaisesRegex(self.module.LifecycleError, "start-attestation-identity-invalid"):
                self.module._validate_start_attestation(root, reference, snapshot)


class PhaseLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        feature = self.root / "specs/901-phase-lifecycle"
        feature.mkdir(parents=True)
        (feature / "spec.md").write_text("current specification\n", encoding="utf-8")
        (feature / "validation").mkdir()
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        for relative, record in fixture["materialized_files"].items():
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(record["content"], encoding="utf-8")
            self.assertEqual(record["sha256"], sha(destination.read_bytes()), relative)
        self.module = load_module()

    def request(self, *, action: str = "prepare") -> dict:
        spec_path = "specs/901-phase-lifecycle/spec.md"
        spec_hash = sha((self.root / spec_path).read_bytes())
        decision_path = "specs/901-phase-lifecycle/validation/operator-decisions.json"
        decision = {
            "schema_version": "1.0",
            "policy_sha256": "09738d2d65ab12117308d586f77a2140a1cedebbad9d9bc33f0408fb822f1bd4",
            "feature_directory": "specs/901-phase-lifecycle",
            "phase": "implement",
            "scope_sha256": spec_hash,
            "kind": "routine-invocation",
            "reference": "current-main-controller-operator-invocation",
        }
        decision_bytes = json.dumps(decision, sort_keys=True).encode()
        (self.root / decision_path).write_bytes(decision_bytes)
        snapshot = {
            "schema_version": "1.0",
            "feature_directory": "specs/901-phase-lifecycle",
            "entry_id": "901",
            "phase": "implement",
            "workflow_id": "farmboy-implement",
            "workflow_version": "0.7.0",
            "run_id": "run-implement-1",
            "current_status": "specced",
            "scope_sha256": spec_hash,
            "source_map": {
                spec_path: spec_hash,
                decision_path: sha(decision_bytes),
            },
            "dependency_states": [],
            "pending_future_ids": ["HUMAN-ACCEPT-001"],
        }
        request = {
            "schema_version": "1.0",
            "action": action,
            "phase": "implement",
            "feature_directory": snapshot["feature_directory"],
            "entry_id": "901",
            "run_id": "run-implement-1",
            "workflow_id": "farmboy-implement",
            "workflow_version": "0.7.0",
            "mode": "normal",
            "decision_reference": decision_path,
            "milestone_evidence": [],
            "snapshot": snapshot,
        }
        if action == "revalidate":
            request["proposal"] = self.proposal(snapshot)
        return request

    def _add_structured_recovery_start_proof(self, root: Path, request: dict,
                                             reviewer_report: dict,
                                             dispatch_summary: dict) -> dict:
        """Materialize retained history and execute the installed evidence CLIs."""
        feature = request["feature_directory"]
        spec_path = f"{feature}/spec.md"
        current_spec = (root / spec_path).read_bytes()
        original_spec = current_spec.replace(b"**Status**: Complete", b"**Status**: Draft", 1)
        self.assertNotEqual(current_spec, original_spec)
        references = {
            "source_run": ".specify/flow-controllers/runs/source-implement/summary.json",
            "baseline": ".specify/flow-controllers/runs/source-implement/baseline.json",
            "original_spec": ".specify/flow-controllers/runs/authorized-status/spec-before.md",
            "current_spec": spec_path,
            "status_run": ".specify/flow-controllers/runs/authorized-status/summary.json",
            "status_authorization": ".specify/flow-controllers/runs/authorized-status/authorization.json",
            "status_effect": ".specify/flow-controllers/runs/authorized-status/effect.json",
            "status_validation": ".specify/flow-controllers/runs/authorized-status/bridge-validation.json",
            "feature_pointer": ".specify/feature.json",
        }
        pointer_path = root / references["feature_pointer"]
        pointer_path.parent.mkdir(parents=True, exist_ok=True)
        pointer_path.write_text(json.dumps({"feature_directory": feature}, sort_keys=True))
        pointer_bytes = pointer_path.read_bytes()
        original_path = root / references["original_spec"]
        original_path.parent.mkdir(parents=True, exist_ok=True)
        original_path.write_bytes(original_spec)
        baseline_body = {
            "feature_directory": feature, "specification_sha256": sha(original_spec),
            "pointer_sha256": sha(pointer_bytes), "tasks": {"T001": {"marker": " "}},
        }
        baseline_digest = sha(json.dumps(baseline_body, sort_keys=True, separators=(",", ":")).encode())
        baseline = {"baseline": baseline_body, "baseline_sha256": baseline_digest,
                    "remaining_ids": ["task:T001"], "state": "captured"}
        baseline_path = root / references["baseline"]
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_path.write_text(json.dumps(baseline, sort_keys=True))
        source_run = {
            "run_id": "source-implement-run", "workflow_id": "farmboy-implement", "status": "stopped",
            "started_at": "2026-10-01T12:00:00+00:00",
            "steps": {"implement-eligible-work": {"status": "completed"},
                      "capture-implementation-baseline": {"status": "completed"}},
            "child_tasks": [{"agent": "FarmBoy Coder", "step_id": "implement-eligible-work", "child_id": "coder-child-1"}],
            "effective_assignments": [{"agent_name": "FarmBoy Coder", "step_id": "implement-eligible-work"}],
            "changed_files": [f"{feature}/implementation.py"],
            "baseline_evidence": {"baseline_sha256": baseline_digest, "path": references["baseline"]},
        }
        source_path = root / references["source_run"]
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(json.dumps(source_run, sort_keys=True))
        code_path = root / f"{feature}/implementation.py"
        code_path.write_text("implementation evidence\n")
        status_run = {
            "run_id": "authorized-status-run", "workflow_id": "farmboy-closeout",
            "steps": {"mark-converged-specification-complete": {"status": "completed"}},
            "changed_files": [spec_path],
        }
        authorization = {"status_action": "run", "feature_directory": feature,
                         "spec_before_sha256": sha(original_spec), "authority": "explicit bounded status-only authorization"}
        effect = {
            "step_id": "mark-converged-specification-complete", "kind": "bounded-existing-specification-status-update",
            "feature_directory": feature, "before_status": "Draft", "after_status": "Complete",
            "before_sha256": sha(original_spec), "after_sha256": sha(current_spec),
            "exact_diff": "**Status**: Draft -> **Status**: Complete", "other_specification_bytes_preserved": True,
        }
        validation = {
            "state": "ready", "spec_path": spec_path, "before_sha256": sha(original_spec),
            "after_sha256": sha(current_spec), "allowed_change": "Status Draft to Complete only",
            "requirements_and_all_other_bytes_preserved": True, "convergence_intent_preserved": True,
            "future_manual_task_ids": ["T001"], "feature_acceptance_established": False,
        }
        for name, value in (("status_run", status_run), ("status_authorization", authorization),
                            ("status_effect", effect), ("status_validation", validation)):
            destination = root / references[name]
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(value, sort_keys=True))
        readiness_payload = {"action": "record-review", "feature_directory": feature,
                             "reviewer_report": reviewer_report}
        readiness_command = [sys.executable,
            str(root / ".specify/farmboy/scripts/python/controller.py"),
            "readiness", "--project", str(root)]
        readiness_recorded = subprocess.run(readiness_command, input=json.dumps(readiness_payload),
            text=True, capture_output=True, check=False)
        self.assertEqual(0, readiness_recorded.returncode, readiness_recorded.stderr)
        readiness_receipt = json.loads(readiness_recorded.stdout)
        self.assertEqual("recorded", readiness_receipt.get("state"), readiness_receipt)
        readiness_assessed = subprocess.run(readiness_command,
            input=json.dumps({"action": "assess", "feature_directory": feature}),
            text=True, capture_output=True, check=False)
        self.assertEqual(0, readiness_assessed.returncode, readiness_assessed.stderr)
        readiness_result = json.loads(readiness_assessed.stdout)
        self.assertEqual("ready", readiness_result.get("state"), readiness_result)

        trusted_inputs = {name: {"path": path, "sha256": sha((root / path).read_bytes())}
                          for name, path in references.items()}
        history_packet = {
            "action": "validate-start-history", "schema_version": "1.0", "feature_directory": feature,
            "current_scope_sha256": sha(current_spec), "trusted_inputs": trusted_inputs,
        }
        history_command = [sys.executable,
            str(root / ".specify/farmboy/scripts/python/controller.py"),
            "phase-lifecycle", "--project", str(root)]
        history_result = subprocess.run(history_command, input=json.dumps(history_packet),
            text=True, capture_output=True, check=False)
        self.assertEqual(0, history_result.returncode, history_result.stderr)
        history = json.loads(history_result.stdout)
        self.assertEqual("validated", history.get("state"), history)
        validation_path = f"{feature}/validation/phase-lifecycle/start-history-validation.json"
        validation_file = root / validation_path
        validation_file.parent.mkdir(parents=True, exist_ok=True)
        validation_file.write_text(json.dumps(history, sort_keys=True))

        snapshot = request["snapshot"]
        snapshot["scope_sha256"] = sha(current_spec)
        snapshot["source_map"][spec_path] = sha(current_spec)
        decision_path = request["decision_reference"]
        decision_file = root / decision_path
        decision_record = json.loads(decision_file.read_text(encoding="utf-8"))
        decision_record["scope_sha256"] = sha(current_spec)
        decision_file.write_text(json.dumps(decision_record, sort_keys=True), encoding="utf-8")
        snapshot["source_map"][decision_path] = sha(decision_file.read_bytes())
        for reference in trusted_inputs.values():
            snapshot["source_map"][reference["path"]] = reference["sha256"]
        snapshot["source_map"][validation_path] = sha(validation_file.read_bytes())
        snapshot["source_map"][readiness_receipt["path"]] = readiness_receipt["sha256"]
        main_summary_path = f".specify/flow-controllers/runs/{snapshot['run_id']}/summary.json"
        main_summary = dispatch_summary
        main_summary_file = root / main_summary_path
        main_summary_file.parent.mkdir(parents=True, exist_ok=True)
        main_summary_file.write_text(json.dumps(main_summary, sort_keys=True))
        captured_summary_path = (
            f".specify/flow-controllers/runs/{snapshot['run_id']}/dispatch-summary-at-capture.json")
        captured_summary_file = root / captured_summary_path
        captured_summary_file.write_bytes(main_summary_file.read_bytes())
        captured_summary_ref = {"path": captured_summary_path,
                                 "sha256": sha(captured_summary_file.read_bytes())}
        witness_path = (
            f".specify/flow-controllers/runs/{snapshot['run_id']}/recovery-start-dispatch-witness.json")
        witness = {"schema_version": "1.0", "kind": "main-retained-native-dispatch-witness",
            "feature_directory": feature, "scope_sha256": sha(current_spec),
            "workflow_id": snapshot["workflow_id"], "workflow_version": snapshot["workflow_version"],
            "run_id": snapshot["run_id"], "step_id": "attest-recovery-start",
            "agent": "FarmBoy Reviewer", "child_id": "native-reviewer-child",
            "source_summary": captured_summary_ref}
        witness_file = root / witness_path
        witness_file.write_text(json.dumps(witness, sort_keys=True))
        witness_ref = {"path": witness_path, "sha256": sha(witness_file.read_bytes())}
        snapshot["source_map"][captured_summary_path] = captured_summary_ref["sha256"]
        snapshot["source_map"][witness_path] = witness_ref["sha256"]
        artifact_paths = {
            spec_path: sha(current_spec),
            f"{feature}/plan.md": sha((root / feature / "plan.md").read_bytes()),
            f"{feature}/tasks.md": sha((root / feature / "tasks.md").read_bytes()),
            "controllers/recovery-fixture-source.py": sha(b"immutable source evidence\n"),
            "tests/recovery-fixture-proof.py": sha(b"immutable test evidence\n"),
        }
        for relative, content in (("controllers/recovery-fixture-source.py", b"immutable source evidence\n"),
                                  ("tests/recovery-fixture-proof.py", b"immutable test evidence\n")):
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
        snapshot["source_map"].update(artifact_paths)
        return {"readiness_receipt": readiness_receipt,
                "readiness_assessment": readiness_result,
                "history_validation": history,
                "artifact_digests": artifact_paths,
                "history_path": validation_path,
                "history_sha256": sha(validation_file.read_bytes()),
                "trusted_inputs": trusted_inputs,
                "dispatch_witness": witness_ref,
                "dispatch_summary_path": main_summary_path}

    @staticmethod
    def proposal(snapshot: dict, *, target: str = "in-progress") -> dict:
        proposal = {
            "schema_version": "1.0",
            "snapshot": snapshot,
            "milestone_evidence": [],
            "decision": {
                "reference": "specs/901-phase-lifecycle/validation/operator-decisions.json",
                "sha256": "b" * 64,
                "contract_sha256": "09738d2d65ab12117308d586f77a2140a1cedebbad9d9bc33f0408fb822f1bd4",
            },
            "from_status": "specced",
            "to_status": target,
            "expected_roadmap_sha256": "c" * 64,
            "patch_sha256": "d" * 64,
            "effect_id": "run-implement-1-start-901",
            "recovery": {
                "mode": "normal",
                "ceiling": "in-progress",
                "roadmap_path": ".specify/memory/roadmap.md",
                "source_preimage": "roadmap bytes\n",
                "verification": [],
            },
        }
        operations = {key: value for key, value in proposal.items() if key != "patch_sha256"}
        operations["recovery"] = {key: value for key, value in proposal["recovery"].items() if key != "verification"}
        proposal["patch_sha256"] = sha(json.dumps(operations, sort_keys=True, separators=(",", ":")).encode())
        return proposal

    def test_validateRequest_acceptsCurrentMinimalSnapshot(self) -> None:
        self.assertEqual("prepare", self.module.validate_request(self.root, self.request())["action"])

    def testCanonicalFixturesDispatchThroughTheirContractValidators(self) -> None:
        """Execute canonical lifecycle fixture payloads against current validators."""
        fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["cases"]
        by_id = {case["id"]: case for case in fixtures}
        self.assertEqual(len(fixtures), len(by_id), "fixture IDs must be unique")

        self.assertEqual("prepare", self.module.validate_request(
            self.root, by_id["request-prepare-implement"]["payload"])["action"])
        self.assertEqual("recovery", self.module.validate_request(
            self.root, by_id["recovery-one-adjacent-edge"]["payload"])["mode"])
        with self.assertRaisesRegex(ValueError, "nonadjacent|adjacent"):
            self.module.validate_proposal(by_id["proposal-skips-adjacent-edge"]["payload"])
        self.assertEqual("in-progress", self.module.validate_proposal(
            by_id["proposal-one-adjacent-edge"]["payload"])["to_status"])

        evidence_request = by_id["request-prepare-implement"]["payload"]
        evidence = by_id["evidence-current-review"]["payload"]
        self.assertIs(self.module._validate_group(self.root, evidence, evidence_request["snapshot"]), evidence)
        with self.assertRaisesRegex(ValueError, "milestone-evidence-schema-invalid"):
            self.module._validate_group(self.root, by_id["evidence-unknown-field"]["payload"],
                                         evidence_request["snapshot"])
        invalid_evidence = {**evidence, "complete": True}
        with self.assertRaisesRegex(ValueError, "milestone-evidence-schema-invalid"):
            self.module._validate_group(self.root, invalid_evidence, evidence_request["snapshot"])

        noop = by_id["assessment-no-op"]["payload"]
        noop_request = {**evidence_request, "snapshot": noop["snapshot"]}
        self.assertEqual("no-op", self.module.validate_assessment(self.root, noop, noop_request)["state"])
        self.assertEqual("blocked", self.module.validate_assessment(
            self.root, by_id["assessment-blocked-missing-checker"]["payload"], evidence_request)["state"])
        self.assertEqual("question", self.module.validate_assessment(
            self.root, by_id["assessment-question-ambiguous-authority"]["payload"], evidence_request)["state"])

        with self.assertRaisesRegex(ValueError, "unsafe-relative-path"):
            self.module._validate_snapshot(by_id["snapshot-unsafe-parent-path"]["payload"])
        with self.assertRaisesRegex(ValueError, "duplicate-json-key"):
            self.module.strict_json('{"schema_version":"1.0","schema_version":"1.0"}')
        for case_id in ("request-unknown-field", "request-null-field", "request-revalidate-rejects-null-recovery"):
            with self.subTest(case_id=case_id), self.assertRaises(ValueError):
                self.module.validate_request(self.root, by_id[case_id]["payload"])
        raw_duplicate = by_id["request-duplicate-key"].get("raw_json")
        self.assertIsInstance(raw_duplicate, str)
        with self.assertRaisesRegex(ValueError, "duplicate-json-key"):
            self.module.strict_json(raw_duplicate)
        controller_path = ROOT / "controllers/farmboy/scripts/python/controller.py"
        duplicate_cli = subprocess.run(
            [sys.executable, str(controller_path), "phase-lifecycle", "--project", str(self.root)],
            input=raw_duplicate, text=True, capture_output=True, check=False,
        )
        self.assertNotEqual(0, duplicate_cli.returncode)
        self.assertIn("duplicate-json-key", duplicate_cli.stderr)

        recovery = by_id["recovery-one-adjacent-edge"]["payload"]
        self.assertEqual("recovery", self.module.validate_request(self.root, recovery)["mode"])
        skipped_recovery = by_id["recovery-skips-required-start-edge"]
        self.assertEqual("reject-unsubstantiated-or-nonadjacent-recovery", skipped_recovery["expected"])
        with self.assertRaisesRegex(ValueError, "authorized-start-attestation-required"):
            self.module.validate_request(self.root, skipped_recovery["payload"])

        receipts = [case for case in fixtures if case["area"] == "receipt" and case["id"] != "receipt-forbidden-null"]
        self.assertEqual(4, len(receipts))
        for case in receipts:
            with self.subTest(receipt=case["id"]):
                self.module.validate_receipt(case["payload"])

    def test_validateRequest_rejectsUnknownField(self) -> None:
        request = self.request()
        request["operator_is_authorized"] = True
        with self.assertRaisesRegex(ValueError, "request-schema-invalid"):
            self.module.validate_request(self.root, request)

    def test_validateRequest_rejectsNullRequiredField(self) -> None:
        request = self.request()
        request["entry_id"] = None
        with self.assertRaisesRegex(ValueError, "null-value-invalid"):
            self.module.validate_request(self.root, request)

    def test_strictJson_rejectsDuplicateKeys(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate-json-key"):
            self.module.strict_json('{"schema_version":"1.0","schema_version":"1.0"}')

    def test_validateRequest_rejectsUnsafeSnapshotPath(self) -> None:
        request = self.request()
        request["snapshot"]["source_map"] = {"../../outside.md": "a" * 64}
        with self.assertRaisesRegex(ValueError, "unsafe-relative-path"):
            self.module.validate_request(self.root, request)

    def test_validateRequest_rejectsStaleSourceDigest(self) -> None:
        request = self.request()
        request["snapshot"]["source_map"]["specs/901-phase-lifecycle/spec.md"] = "a" * 64
        request["snapshot"]["scope_sha256"] = "a" * 64
        with self.assertRaisesRegex(ValueError, "stale-source-evidence"):
            self.module.validate_request(self.root, request)

    def test_validateRequest_rejectsRepeatedMilestoneGroup(self) -> None:
        request = self.request()
        request["milestone_evidence"] = [{"milestone": "in-progress"}, {"milestone": "in-progress"}]
        with self.assertRaisesRegex(ValueError, "milestone-evidence-schema-invalid"):
            self.module.validate_request(self.root, request)

    def test_validateProposal_acceptsOneAdjacentEdge(self) -> None:
        proposal = self.proposal(self.request()["snapshot"])
        self.assertEqual("in-progress", self.module.validate_proposal(proposal)["to_status"])

    def test_validateProposal_rejectsSkippedEdge(self) -> None:
        proposal = self.proposal(self.request()["snapshot"], target="implemented")
        with self.assertRaisesRegex(ValueError, "proposal-not-adjacent"):
            self.module.validate_proposal(proposal)

    def test_validateProposal_rejectsWrongNormalPhaseTarget(self) -> None:
        proposal = self.proposal(self.request()["snapshot"], target="specced")
        proposal["from_status"] = "planned"
        with self.assertRaisesRegex(ValueError, "normal-proposal-phase-mismatch"):
            self.module.validate_proposal(proposal)

    def test_validateProposal_rejectsChangedPolicy(self) -> None:
        proposal = self.proposal(self.request()["snapshot"])
        proposal["decision"]["contract_sha256"] = "e" * 64
        with self.assertRaisesRegex(ValueError, "governing-contract-mismatch"):
            self.module.validate_proposal(proposal)

    def test_validateProposal_rejectsNullRecovery(self) -> None:
        proposal = self.proposal(self.request()["snapshot"])
        proposal["recovery"]["source_preimage"] = None
        with self.assertRaisesRegex(ValueError, "null-value-invalid"):
            self.module.validate_proposal(proposal)

    def test_validateReceipt_acceptsAllFourDiscriminatedOutcomes(self) -> None:
        fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["cases"]
        receipts = [case["payload"] for case in fixtures if case["area"] == "receipt" and case["id"] != "receipt-forbidden-null"]
        self.assertEqual({"applied", "no-op", "not-applied", "indeterminate"}, {item["effect_state"] for item in receipts})
        for receipt in receipts:
            self.assertIs(self.module.validate_receipt(receipt), receipt)

    def test_validateReceipt_rejectsForbiddenNullTransitionField(self) -> None:
        fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["cases"]
        receipt = next(case["payload"] for case in fixtures if case["id"] == "receipt-forbidden-null")
        with self.assertRaisesRegex(ValueError, "receipt-schema-invalid|null-value-invalid"):
            self.module.validate_receipt(receipt)

    def test_validateReceipt_rejectsForgedCrossPhaseEdge(self) -> None:
        fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["cases"]
        receipt = next(case["payload"] for case in fixtures if case["id"] == "receipt-applied-recorded")
        receipt["to_status"] = "implemented"
        with self.assertRaisesRegex(ValueError, "receipt-edge-invalid"):
            self.module.validate_receipt(receipt)

    def test_prepareBlocksWhenOwnerDeliveryIsNotInstalled(self) -> None:
        result = self.module.prepare(self.root, self.request())
        self.assertEqual("blocked", result["state"])
        self.assertEqual("lifecycle-owner-contract-unavailable", result["reason_code"])

    def test_revalidateRequiresOriginalProposal(self) -> None:
        result = self.module.revalidate(self.root, self.request())
        self.assertEqual("blocked", result["state"])
        self.assertEqual("revalidate-request-required", result["reason_code"])

    def test_prepareOnlyCallsWorkflowEvaluateAndDoesNotApply(self) -> None:
        request = self.request()
        proposal = self.proposal(request["snapshot"])
        owner = SimpleNamespace(evaluate=lambda project, payload, yaml: {
            "state": "ready", "reason_code": "adjacent-milestone-substantiated",
            "evidence": [{"path": "specs/901-phase-lifecycle/spec.md",
                          "sha256": request["snapshot"]["scope_sha256"], "kind": "independent-review"}],
            "blocking_ids": [], "snapshot": request["snapshot"], "proposal": proposal,
        })
        before = sorted(path.relative_to(self.root).as_posix() for path in self.root.rglob("*"))
        with patch.object(self.module, "_workflow_module", return_value=owner), patch.dict(sys.modules, {"yaml": SimpleNamespace()}):
            result = self.module.prepare(self.root, request)
        self.assertEqual("ready", result["state"])
        self.assertTrue((self.root / "specs/901-phase-lifecycle/spec.md").exists())
        after = sorted(path.relative_to(self.root).as_posix() for path in self.root.rglob("*"))
        self.assertEqual(before, after)

    def test_controllerProvidesDedicatedLifecycleCommand(self) -> None:
        controller_path = ROOT / "controllers/farmboy/scripts/python/controller.py"
        spec = importlib.util.spec_from_file_location("farmboy_controller_for_lifecycle_test", controller_path)
        assert spec is not None and spec.loader is not None
        controller = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"phase_lifecycle": self.module,
                                      "farmboy_controller_for_lifecycle_test": controller}):
            spec.loader.exec_module(controller)
        self.assertTrue(callable(controller.prepare_phase_lifecycle))
        self.assertTrue(callable(controller.validate_lifecycle_receipt))

    def test_controllerCliRunsPrepareAndReportsMissingOwnerDelivery(self) -> None:
        controller_path = ROOT / "controllers/farmboy/scripts/python/controller.py"
        result = subprocess.run(
            [sys.executable, str(controller_path), "phase-lifecycle", "--project", str(self.root)],
            input=json.dumps(self.request()), text=True, capture_output=True, check=False,
        )
        report = json.loads(result.stdout)
        self.assertEqual(2, result.returncode)
        self.assertEqual("blocked", report["state"])
        self.assertEqual("lifecycle-owner-contract-unavailable", report["reason_code"])

    def test_policyIsDeliveredByControllerRatherThanRoadmapExtension(self) -> None:
        policy = self.module._workflow_module(self.root)
        self.assertTrue(callable(policy.evaluate))
        self.assertTrue(callable(policy.validate_specification_ready))
        self.assertFalse(hasattr(policy, "apply"))

if __name__ == "__main__":
    unittest.main()

"""Tests for strict FlowKit phase-lifecycle evidence handling."""

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
MODULE_PATH = ROOT / "controllers/flow-kit/scripts/python/phase_lifecycle.py"
FIXTURE_PATH = ROOT / "tests/consumer-fixtures/workflow-improvements/phase-lifecycle-cases.json"


def load_module():
    spec = importlib.util.spec_from_file_location("flowkit_phase_lifecycle_under_test", MODULE_PATH)
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
            "run_id": "source-implement-run", "workflow_id": "speckit-flow-implement", "status": "stopped",
            "started_at": "2026-10-01T12:00:00+00:00",
            "steps": {"implement-eligible-work": {"status": "completed"},
                      "capture-implementation-baseline": {"status": "completed"}},
            "child_tasks": [{"agent": "FlowKit-Coder", "step_id": "implement-eligible-work", "child_id": "coder-child-1"}],
            "effective_assignments": [{"agent_name": "FlowKit-Coder", "step_id": "implement-eligible-work"}],
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
                "run_id": "authorized-status-run", "workflow_id": "speckit-flow-closeout",
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
            self.assertEqual("speckit-flow-implement", validated["source_workflow_id"])
            self.assertEqual("capture-implementation-baseline", validated["completed_step_ids"][0])
            self.assertEqual(["T001"], validated["future_manual_task_ids"])
            self.assertEqual(packet["current_scope_sha256"], validated["scope_sha256"])
            self.assertNotEqual(validated["scope_sha256"], validated["original_scope_sha256"])

    def test_phaseLifecycleCli_exposesReadOnlyValidatedStartHistory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            packet = self._materialize(root)
            command = [sys.executable, str(ROOT / "controllers/flow-kit/scripts/python/controller.py"),
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
                "controllers/flow-kit/scripts/python/phase_lifecycle.py": sha(
                    (ROOT / "controllers/flow-kit/scripts/python/phase_lifecycle.py").read_bytes()),
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
                "workflow_id": "speckit-flow-closeout",
                "workflow_version": "0.8.0",
                "run_id": "closeout-current-run",
                "source_map": source_map,
            }
            dispatch_summary_path = f".specify/flow-controllers/runs/{snapshot['run_id']}/summary.json"
            dispatch_summary = {
                "run_id": snapshot["run_id"], "workflow_id": snapshot["workflow_id"],
                "workflow_version": snapshot["workflow_version"],
                "child_tasks": [{"agent": "FlowKit-Reviewer", "step_id": "attest-recovery-start",
                                 "child_id": "native-reviewer-child"}],
                "effective_assignments": [{"agent_name": "FlowKit-Reviewer", "step_id": "attest-recovery-start"}],
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
                "agent": "FlowKit-Reviewer", "child_id": "native-reviewer-child",
                "source_summary": source_summary_ref}
            witness_file = root / witness_path
            witness_file.write_text(json.dumps(witness, sort_keys=True))
            witness_ref = {"path": witness_path, "sha256": sha(witness_file.read_bytes())}
            source_map[capture_path] = source_summary_ref["sha256"]
            source_map[witness_path] = witness_ref["sha256"]
            record = {
                "schema_version": "1.0", "kind": "authorized-implementation-start",
                "reviewer": "FlowKit-Reviewer", "state": "ready", "feature_directory": feature,
                "scope_sha256": packet["current_scope_sha256"], "workflow_id": snapshot["workflow_id"],
                "workflow_version": snapshot["workflow_version"], "run_id": snapshot["run_id"],
                "step_id": "attest-recovery-start", "child_id": "native-reviewer-child",
                "source_run_id": history["source_run_id"],
                "original_scope_sha256": history["original_scope_sha256"],
                "occurred_at": history["occurred_at"],
                "history_validation": {"path": validation_path, "sha256": sha(validation_bytes)},
                "dispatch_witness": witness_ref,
                "recorded_dispatch": {
                    "agent": "FlowKit-Reviewer", "step_id": "attest-recovery-start",
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

            record["reviewer"] = "FlowKit-Readiness Checker"
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
            "workflow_id": "speckit-flow-implement",
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
            "workflow_id": "speckit-flow-implement",
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
            "run_id": "source-implement-run", "workflow_id": "speckit-flow-implement", "status": "stopped",
            "started_at": "2026-10-01T12:00:00+00:00",
            "steps": {"implement-eligible-work": {"status": "completed"},
                      "capture-implementation-baseline": {"status": "completed"}},
            "child_tasks": [{"agent": "FlowKit-Coder", "step_id": "implement-eligible-work", "child_id": "coder-child-1"}],
            "effective_assignments": [{"agent_name": "FlowKit-Coder", "step_id": "implement-eligible-work"}],
            "changed_files": [f"{feature}/implementation.py"],
            "baseline_evidence": {"baseline_sha256": baseline_digest, "path": references["baseline"]},
        }
        source_path = root / references["source_run"]
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(json.dumps(source_run, sort_keys=True))
        code_path = root / f"{feature}/implementation.py"
        code_path.write_text("implementation evidence\n")
        status_run = {
            "run_id": "authorized-status-run", "workflow_id": "speckit-flow-closeout",
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
            str(root / ".specify/flow-kit/scripts/python/controller.py"),
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
            str(root / ".specify/flow-kit/scripts/python/controller.py"),
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
            "agent": "FlowKit-Reviewer", "child_id": "native-reviewer-child",
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
        controller_path = ROOT / "controllers/flow-kit/scripts/python/controller.py"
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

    def test_prepareOnlyCallsOwnerEvaluateAndDoesNotApply(self) -> None:
        request = self.request()
        proposal = self.proposal(request["snapshot"])
        owner = SimpleNamespace(evaluate=lambda project, payload, yaml: {
            "state": "ready", "reason_code": "adjacent-milestone-substantiated",
            "evidence": [{"path": "specs/901-phase-lifecycle/spec.md",
                          "sha256": request["snapshot"]["scope_sha256"], "kind": "independent-review"}],
            "blocking_ids": [], "snapshot": request["snapshot"], "proposal": proposal,
        })
        before = sorted(path.relative_to(self.root).as_posix() for path in self.root.rglob("*"))
        with patch.object(self.module, "_owner_module", return_value=owner), patch.dict(sys.modules, {"yaml": SimpleNamespace()}):
            result = self.module.prepare(self.root, request)
        self.assertEqual("ready", result["state"])
        self.assertTrue((self.root / "specs/901-phase-lifecycle/spec.md").exists())
        after = sorted(path.relative_to(self.root).as_posix() for path in self.root.rglob("*"))
        self.assertEqual(before, after)

    def test_controllerProvidesDedicatedLifecycleCommand(self) -> None:
        controller_path = ROOT / "controllers/flow-kit/scripts/python/controller.py"
        spec = importlib.util.spec_from_file_location("flowkit_controller_for_lifecycle_test", controller_path)
        assert spec is not None and spec.loader is not None
        controller = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"phase_lifecycle": self.module,
                                      "flowkit_controller_for_lifecycle_test": controller}):
            spec.loader.exec_module(controller)
        self.assertTrue(callable(controller.prepare_phase_lifecycle))
        self.assertTrue(callable(controller.validate_lifecycle_receipt))

    def test_controllerCliRunsPrepareAndReportsMissingOwnerDelivery(self) -> None:
        controller_path = ROOT / "controllers/flow-kit/scripts/python/controller.py"
        result = subprocess.run(
            [sys.executable, str(controller_path), "phase-lifecycle", "--project", str(self.root)],
            input=json.dumps(self.request()), text=True, capture_output=True, check=False,
        )
        report = json.loads(result.stdout)
        self.assertEqual(2, result.returncode)
        self.assertEqual("blocked", report["state"])
        self.assertEqual("lifecycle-owner-contract-unavailable", report["reason_code"])

    def test_lifecycleCaseMatrixUsesDisposableOwnerConsumers(self) -> None:
        """Run LC001-LC015 against the independently versioned owner in temp consumers.

        The owner source is deliberately supplied by the validation invocation, not
        vendored into FlowKit. Each mapped owner test creates and mutates only its
        own temporary consumer, then asserts actual roadmap bytes and receipts.
        """
        source = os.environ.get("FLOW_ROADMAP_SOURCE")
        if not source:
            self.skipTest("FLOW_ROADMAP_SOURCE is required for disposable owner lifecycle cases")
        owner_root = Path(source).resolve()
        owner_test = owner_root / "tests/python/test_phase_lifecycle.py"
        if not owner_test.is_file():
            self.fail("FLOW_ROADMAP_SOURCE lacks tests/python/test_phase_lifecycle.py")

        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        matrix = fixture["lifecycle_matrix"]
        expected_ids = [f"LC{number:03d}" for number in range(1, 16)]
        self.assertEqual(expected_ids, [case["id"] for case in matrix])
        sys.path.insert(0, str(owner_test.parent))
        self.addCleanup(sys.path.remove, str(owner_test.parent))
        owner_spec = importlib.util.spec_from_file_location("flowkit_external_owner_lifecycle_tests", owner_test)
        if owner_spec is None or owner_spec.loader is None:
            self.fail("could not load current owner lifecycle tests")
        owner_module = importlib.util.module_from_spec(owner_spec)
        owner_spec.loader.exec_module(owner_module)
        roadmap_tests_path = owner_root / "tests/python/test_review_contract.py"
        roadmap_spec = importlib.util.spec_from_file_location("flowkit_external_roadmap_review_tests", roadmap_tests_path)
        if roadmap_spec is None or roadmap_spec.loader is None:
            self.fail("could not load current owner brief contract tests")
        roadmap_module = importlib.util.module_from_spec(roadmap_spec)
        roadmap_spec.loader.exec_module(roadmap_module)

        skipped_recovery = next(item for item in fixture["cases"]
                                if item["id"] == "recovery-skips-required-start-edge")
        self.assertEqual("recovery", skipped_recovery["payload"]["mode"])

        # LC001/LC002 exercise the delivered authoring-ready proof checker in a
        # fresh temporary consumer, including the exact quality and independent
        # review evidence it requires.
        authoring_case = owner_module.LifecycleTests("test_three_phase_owned_adjacent_effects_preserve_unrelated_bytes")
        authoring_case.setUp()
        try:
            authoring_phase = owner_module.phase
            authoring_root = authoring_case.root
            feature = authoring_case.feature
            spec_path = f"{feature}/spec.md"
            quality_path = f"{feature}/checklists/requirements.md"
            review_path = f"{feature}/validation/authoring-review.json"
            packet_path = f"{feature}/validation/specification-ready.json"
            owner_module.write(authoring_root / quality_path, "# Requirements\n\n- [x] Current authoring quality\n")
            scope_digest = owner_module.sha(authoring_root / spec_path)
            checks = ["authoring-quality", "clarification", "linkage", "independent-review"]
            artifacts = {path: owner_module.sha(authoring_root / path) for path in (spec_path, quality_path)}
            review = {
                "schema_version": "1.0", "kind": "independent-authoring-review", "reviewer": "FlowKit-Reviewer",
                "state": "complete", "feature_directory": feature, "scope_sha256": scope_digest,
                "artifact_digests": artifacts, "required_check_ids": checks,
                "satisfied_check_ids": checks, "unresolved_ids": [],
            }
            owner_module.write(authoring_root / review_path, review)
            packet = {
                "schema_version": "1.0", "feature_directory": feature, "scope_sha256": scope_digest,
                "assessments": [{"path": review_path, "sha256": owner_module.sha(authoring_root / review_path),
                                 "kind": "independent-authoring-review"}],
                "required_check_ids": checks, "satisfied_check_ids": checks,
                "artifact_digests": artifacts, "unresolved_ids": [],
            }
            owner_module.write(authoring_root / packet_path, packet)
            self.assertTrue(authoring_phase.validate_specification_ready(
                authoring_root, packet_path, owner_module.yaml)["specification_ready"])

            owner_module.write(authoring_root / quality_path, "# Requirements\n\n- [ ] Unfinished quality item\n")
            artifacts = {path: owner_module.sha(authoring_root / path) for path in (spec_path, quality_path)}
            review["artifact_digests"] = artifacts
            owner_module.write(authoring_root / review_path, review)
            packet["artifact_digests"] = artifacts
            packet["assessments"] = [{"path": review_path, "sha256": owner_module.sha(authoring_root / review_path),
                                      "kind": "independent-authoring-review"}]
            owner_module.write(authoring_root / packet_path, packet)
            with self.assertRaisesRegex(authoring_phase.ContractError, "authoring-quality-incomplete"):
                authoring_phase.validate_specification_ready(authoring_root, packet_path, owner_module.yaml)
            owner_module.write(authoring_root / quality_path, "# Requirements\n\n- [x] Current authoring quality\n")
            artifacts = {path: owner_module.sha(authoring_root / path) for path in (spec_path, quality_path)}
            review["artifact_digests"] = artifacts
            owner_module.write(authoring_root / review_path, review)
            packet["artifact_digests"] = artifacts
            packet["assessments"] = []
            owner_module.write(authoring_root / packet_path, packet)
            with self.assertRaisesRegex(authoring_phase.ContractError, "evidence-missing"):
                authoring_phase.validate_specification_ready(authoring_root, packet_path, owner_module.yaml)
        finally:
            authoring_case.doCleanups()

        for case in matrix:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["owner_tests"], f"{case['id']} has no executable owner evidence")
                for method in case["owner_tests"]:
                    with self.subTest(owner_test=method):
                        case_result = unittest.TestResult()
                        owner_case = owner_module.LifecycleTests(method)
                        owner_case.run(case_result)
                        details = [str(item[1]) for item in case_result.errors + case_result.failures]
                        self.assertTrue(case_result.wasSuccessful(), f"{case['id']} {method} failed: {details}")
                        self.assertEqual(1, case_result.testsRun, f"{case['id']} {method} did not run")
                for owner_test in case["roadmap_owner_tests"]:
                    method = owner_test["method"]
                    with self.subTest(roadmap_owner_test=method):
                        case_result = unittest.TestResult()
                        owner_class = getattr(roadmap_module, owner_test["class"])
                        owner_case = owner_class(method)
                        owner_case.run(case_result)
                        details = [str(item[1]) for item in case_result.errors + case_result.failures]
                        self.assertTrue(case_result.wasSuccessful(), f"{case['id']} {method} failed: {details}")
                        self.assertEqual(1, case_result.testsRun, f"{case['id']} {method} did not run")

        import re
        import yaml

        controller_path = ROOT / "controllers/flow-kit/scripts/python/controller.py"
        spec = importlib.util.spec_from_file_location("flowkit_controller_for_lifecycle_graph", controller_path)
        self.assertIsNotNone(spec and spec.loader)
        controller = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"phase_lifecycle": self.module,
                                      "flowkit_controller_for_lifecycle_graph": controller}):
            spec.loader.exec_module(controller)

        def find(nodes: list[dict], wanted: str) -> dict:
            for node in nodes:
                if node.get("id") == wanted:
                    return node
                if node.get("type") == "switch":
                    for branch in node.get("cases", {}).values():
                        try:
                            return find(branch, wanted)
                        except KeyError:
                            pass
                if node.get("type") == "do-while":
                    try:
                        return find(node.get("steps", []), wanted)
                    except KeyError:
                        pass
            raise KeyError(wanted)

        workflows = {}
        for phase in ("specify", "implement", "closeout"):
            workflows[phase] = yaml.safe_load(
                (ROOT / f"workflows/speckit-flow-{phase}/workflow.yml").read_text(encoding="utf-8"))

        route_cases = {
            "LC001": ("specify", "route-specification-lifecycle-transition", "ready"),
            "LC002": ("specify", "route-specification-lifecycle-transition", "blocked"),
            "LC003": ("implement", "route-implementation-start-milestone", "ready"),
            "LC004": ("implement", "route-implementation-start-milestone", "blocked"),
            "LC005": ("closeout", "route-closeout-lifecycle-transition", "ready"),
            "LC006": ("closeout", "route-closeout-lifecycle-transition", "blocked"),
            "LC007": ("specify", "route-specification-lifecycle-transition", "no-op"),
            "LC009": ("closeout", "route-closeout-lifecycle-transition", "blocked"),
            "LC010": ("specify", "route-specification-lifecycle-transition", "question"),
            "LC011": ("implement", "route-implementation-start-milestone", "blocked"),
            "LC012": ("closeout", "route-closeout-lifecycle-transition", "question"),
            "LC013": ("closeout", "route-closeout-lifecycle-revalidation", "ready"),
            "LC014": ("closeout", "route-closeout-lifecycle-transition", "blocked"),
        }
        matrix = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["lifecycle_matrix"]
        self.assertEqual([f"LC{number:03d}" for number in range(1, 16)], [case["id"] for case in matrix])
        observations = {}
        for case_id, (phase, route_id, branch_name) in route_cases.items():
            workflow = workflows[phase]
            route = find(workflow["steps"], route_id)
            selected = controller.select_switch_branch(route, branch_name)
            self.assertIsInstance(selected, list)
            step_ids = [item["id"] for item in selected]
            if branch_name == "ready":
                self.assertTrue(step_ids, f"{case_id} ready route unexpectedly empty")
                if route_id.endswith("revalidation"):
                    effect_path = selected
                else:
                    revalidation_id = {
                        "specify": "route-specification-lifecycle-revalidation",
                        "implement": "route-implementation-start-revalidation",
                        "closeout": "route-closeout-lifecycle-revalidation",
                    }[phase]
                    revalidation = find(selected, revalidation_id)
                    effect_path = controller.select_switch_branch(revalidation, "ready")
                command = next((item for item in effect_path if item.get("type") == "command"), None)
                self.assertIsNotNone(command, f"{case_id} ready/revalidated path lacks production owner command")
                self.assertEqual("speckit.flow-roadmap.write", command["command"])
                step_ids += [item["id"] for item in effect_path]
                selected = selected + effect_path
            elif branch_name in {"blocked", "question"}:
                self.assertEqual([], selected, f"{case_id} must stop before any effect")

            # Render actual selected production prompts and command payloads;
            # fixture outputs stand in only for semantic agent/controller results.
            rendered = []
            for node in selected:
                template = node.get("prompt", node.get("input", {}).get("args"))
                if template is None:
                    continue
                text = json.dumps(template) if isinstance(template, (dict, list)) else str(template)
                outputs = {}
                for step_id, key_path in re.findall(r"\{\{\s*steps\.([A-Za-z0-9_-]+)\.output\.([A-Za-z0-9_.-]+)\s*\}\}", text):
                    target = outputs.setdefault(step_id, {})
                    keys = key_path.split(".")
                    for key in keys[:-1]:
                        target = target.setdefault(key, {})
                    target[keys[-1]] = "fixture-evidence"
                inputs = {key: value.get("default", "fixture-input")
                          for key, value in workflow.get("inputs", {}).items()}
                result = controller.render_template(template, inputs, outputs)
                rendered.append(result)
            observations[case_id] = {"workflow_id": workflow["workflow"]["id"],
                "route_node_id": route_id, "selected_branch": branch_name,
                "production_nodes": step_ids, "rendered_payload_count": len(rendered)}

        # Drive each LC fixture through an actual prepared consumer snapshot,
        # the FlowKit lifecycle adapter, and the production workflow route.
        # Only semantic agent outputs are fixtures; owner/adapter state is read
        # from the disposable project created for each case.
        def prepare_production_case(case_id: str, phase: str, current: str,
                                    mode: str = "normal", milestones: list[str] | None = None,
                                    producer_mutation: dict | None = None):
            owner_case = owner_module.LifecycleTests("test_three_phase_owned_adjacent_effects_preserve_unrelated_bytes")
            owner_case.setUp()
            # The owner test helper initializes the disposable roadmap/files only.
            # The packet sent below is built by the fixture callback from those
            # current files, the fixture's semantic inputs, and the production graph.
            scaffold = owner_case.request(current=current, owner=phase, mode=mode, milestones=milestones)
            immutable_digests = {}
            if "implemented" in (milestones or []):
                for relative, content in (("src/recovery-implementation.py", "implementation source evidence\n"),
                                          ("tests/recovery-validation.py", "current test proof\n")):
                    destination = owner_case.root / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_text(content, encoding="utf-8")
                    immutable_digests[relative] = owner_module.sha(destination)
                for group in scaffold["milestone_evidence"]:
                    if group["milestone"] != "implemented":
                        continue
                    group["artifact_digests"].update(immutable_digests)
                    for reference in group["assessments"]:
                        record_path = owner_case.root / reference["path"]
                        record = json.loads(record_path.read_text(encoding="utf-8"))
                        record["artifact_digests"].update(immutable_digests)
                        record_path.write_text(json.dumps(record, sort_keys=True), encoding="utf-8")
                        reference["sha256"] = owner_module.sha(record_path)
            workflow_path = ROOT / f"workflows/speckit-flow-{phase}/workflow.yml"
            graph_relative = f".specify/workflows/speckit-flow-{phase}/workflow.yml"
            graph = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
            scaffold["workflow_version"] = graph["workflow"]["version"]
            scaffold["snapshot"]["workflow_version"] = graph["workflow"]["version"]
            scaffold["snapshot"]["source_map"].update(immutable_digests)
            for group in scaffold["milestone_evidence"]:
                if group["milestone"] == "implemented":
                    for reference in group["assessments"]:
                        scaffold["snapshot"]["source_map"][reference["path"]] = reference["sha256"]
            for relative, source_path in ((graph_relative, workflow_path),
                                          (".specify/flow-kit/manifest.yml", ROOT / "controllers/flow-kit/manifest.yml")):
                destination = owner_case.root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source_path.read_bytes())
                scaffold["snapshot"]["source_map"][relative] = owner_module.sha(destination)
            for relative in (".specify/flow-kit/skills-install.json", ".specify/bundle-records.json"):
                destination = owner_case.root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text("{}\n", encoding="utf-8")
                scaffold["snapshot"]["source_map"][relative] = owner_module.sha(destination)
            # The fixture callback returns the documented typed producer output.
            # Its snapshot is checked against files now present in the disposable
            # consumer; owner_case.request is not the submitted request packet.
            request_nodes = {
                "specify": ("prepare-specification-lifecycle-request",
                            "prepare-specification-lifecycle-transition",
                            "prepare-specification-lifecycle-request"),
                "implement": ("assess-implementation-start-milestone",
                              "prepare-implementation-start-milestone",
                              "assess-implementation-start-milestone"),
                "closeout": ("prepare-closeout-lifecycle-request",
                             "prepare-closeout-lifecycle-transition",
                             "assess-closeout-lifecycle-edge"),
            }
            producer_id, forwarding_id, evidence_id = request_nodes[phase]
            producer = find(graph["steps"], producer_id)
            feature_directory = scaffold["snapshot"]["feature_directory"]
            request_path = f"{feature_directory}/validation/phase-lifecycle/request.json"
            snapshot = json.loads(json.dumps(scaffold["snapshot"]))
            snapshot["run_id"] = f"lc-{case_id.lower()}-{phase}"
            self.assertEqual(snapshot["workflow_id"], graph["workflow"]["id"])
            for relative, expected_digest in snapshot["source_map"].items():
                source = owner_case.root / relative
                self.assertTrue(source.is_file(), f"producer snapshot source missing: {relative}")
                self.assertEqual(expected_digest, owner_module.sha(source), relative)
            callback_packet = {
                "schema_version": "1.0", "action": "prepare", "phase": phase,
                "feature_directory": feature_directory, "entry_id": snapshot["entry_id"],
                "run_id": snapshot["run_id"], "workflow_id": graph["workflow"]["id"],
                "workflow_version": graph["workflow"]["version"], "mode": mode,
                "decision_reference": scaffold["decision_reference"],
                "milestone_evidence": json.loads(json.dumps(scaffold["milestone_evidence"])),
                "snapshot": snapshot,
            }
            if producer_mutation:
                callback_packet.update(producer_mutation)
            evidence_output = {"current_status": snapshot["current_status"],
                               "evidence": callback_packet["milestone_evidence"],
                               "request_path": request_path,
                               "request": callback_packet,
                               "assessment_path": f"{feature_directory}/validation/phase-lifecycle/callback.json",
                               "report": f"{feature_directory}/validation/phase-lifecycle/brief.json"}
            rendered_request = controller.render_template(producer["prompt"],
                {key: value.get("default", "fixture-input") for key, value in graph.get("inputs", {}).items()},
                {evidence_id: evidence_output,
                 "assess-specification-authoring-quality": evidence_output,
                 "assess-specification-milestone-evidence": evidence_output,
                 "assess-roadmap-brief-milestone": evidence_output,
                 "brief-against-roadmap": evidence_output})
            self.assertEqual(phase, callback_packet["phase"])
            self.assertIn("lifecycle request", rendered_request)
            self.assertIn("validation/phase-lifecycle/", rendered_request)
            packet_path = evidence_output["request_path"]
            forwarder = find(graph["steps"], forwarding_id)
            rendered_forwarder = controller.render_template(forwarder.get("prompt", forwarder.get("input", {}).get("args")),
                {key: value.get("default", "fixture-input") for key, value in graph.get("inputs", {}).items()},
                {producer_id: evidence_output})
            self.assertIn(packet_path, rendered_forwarder)
            packet = evidence_output["request"]
            packet_file = owner_case.root / packet_path
            packet_file.parent.mkdir(parents=True, exist_ok=True)
            packet_file.write_text(json.dumps(packet, sort_keys=True) + "\n", encoding="utf-8")
            request = json.loads(packet_file.read_text(encoding="utf-8"))
            self.assertEqual(packet, request)
            owner_case.forwarded_packet_path = packet_file
            owner_case.production_callback_output = evidence_output
            owner_case.production_forwarded_prompt = rendered_forwarder
            return owner_case, request, graph

        def parse_revalidation_bindings(rendered_prompt: str) -> tuple[str, dict, str]:
            """Read the callback's typed request/proposal only from rendered bindings."""
            match = re.search(r"```json\s*(.*?)\s*```", rendered_prompt, re.DOTALL)
            if match is None:
                raise AssertionError("rendered revalidation prompt lacks request/proposal bindings")
            try:
                arguments = json.loads(match.group(1))
                proposal = arguments["prepared_proposal"]
            except (KeyError, json.JSONDecodeError, TypeError, ValueError) as error:
                raise AssertionError("rendered prepared proposal is malformed") from error
            if (arguments.get("action") != "revalidate" or not isinstance(proposal, dict)
                    or not isinstance(arguments.get("request_path"), str) or not arguments["request_path"]):
                raise AssertionError("rendered request/proposal binding has invalid types")
            argument_sha256 = hashlib.sha256(match.group(1).encode("utf-8")).hexdigest()
            return arguments["request_path"], proposal, argument_sha256

        def execute_ready_production_route(owner_case, request: dict, graph: dict, phase: str,
                                           *, revalidation_mutation: dict | None = None,
                                           apply_packet_mutation: dict | None = None,
                                           before_revalidation=None,
                                           mutate_run_summary: bool = False) -> dict:
            """Execute the rendered ready branch from producer output through actual owner receipt."""
            digest = lambda value: hashlib.sha256(json.dumps(
                value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
            node_sets = {
                "specify": ("prepare-specification-lifecycle-request", "prepare-specification-lifecycle-transition",
                    "route-specification-lifecycle-transition", "revalidate-specification-lifecycle-transition",
                    "route-specification-lifecycle-revalidation", "apply-specification-lifecycle-transition",
                    "verify-specification-lifecycle-transition"),
                "implement": ("assess-implementation-start-milestone", "prepare-implementation-start-milestone",
                    "route-implementation-start-milestone", "revalidate-implementation-start-milestone",
                    "route-implementation-start-revalidation", "apply-implementation-start-milestone",
                    "verify-implementation-start-milestone"),
                "closeout": ("prepare-closeout-lifecycle-request", "prepare-closeout-lifecycle-transition",
                    "route-closeout-lifecycle-transition", "revalidate-closeout-lifecycle-transition",
                    "route-closeout-lifecycle-revalidation", "apply-closeout-lifecycle-transition",
                    "verify-closeout-lifecycle-transition"),
            }
            producer_id, adapter_id, route_id, revalidate_id, revalidate_route_id, apply_id, verify_id = node_sets[phase]
            producer_output = owner_case.production_callback_output
            inputs = {key: value.get("default", "fixture-input") for key, value in graph.get("inputs", {}).items()}
            source_outputs = {producer_id: producer_output}
            def advance_main_run_summary(boundary: str) -> None:
                if not mutate_run_summary:
                    return
                summary_path = owner_case.root / ".specify/flow-controllers/runs" / request["run_id"] / "summary.json"
                summary = json.loads(summary_path.read_text(encoding="utf-8"))
                summary.setdefault("steps", {})[f"test-boundary-{boundary}"] = {"status": "completed"}
                summary["updated_at"] = f"test-{boundary}"
                summary_path.write_text(json.dumps(summary, sort_keys=True), encoding="utf-8")
            adapter = self.module.prepare(owner_case.root, request)
            advance_main_run_summary("after-prepare")
            source_outputs[adapter_id] = {"lifecycle_assessment": adapter, "state": adapter.get("state"),
                "proposal": adapter.get("proposal")}
            route_node = find(graph["steps"], route_id)
            selected = controller.select_switch_branch(route_node, adapter["state"])
            self.assertEqual([revalidate_id, revalidate_route_id], [node["id"] for node in selected],
                             (request.get("run_id"), adapter))
            revalidate_node = find(selected, revalidate_id)
            rendered_revalidation = controller.render_template(revalidate_node["prompt"], inputs, source_outputs)
            self.assertIn("action `revalidate`", rendered_revalidation)
            rendered_request_path, rendered_proposal, rendered_arguments_sha256 = parse_revalidation_bindings(
                rendered_revalidation)
            original_prompt = revalidate_node["prompt"]
            revalidate_node["prompt"] = original_prompt.split("Rendered callback arguments:", 1)[0]
            try:
                mutated_render = controller.render_template(revalidate_node["prompt"], inputs, source_outputs)
                with self.assertRaisesRegex(AssertionError, "lacks request/proposal bindings"):
                    parse_revalidation_bindings(mutated_render)
            finally:
                revalidate_node["prompt"] = original_prompt
            request_path = owner_case.root / rendered_request_path
            if (not request_path.is_file()
                    or rendered_request_path != str(owner_case.forwarded_packet_path.relative_to(owner_case.root))):
                raise AssertionError("rendered revalidation request path is missing or differs from the prepared packet")
            if before_revalidation is not None:
                before_revalidation()
            prepared_request = json.loads(request_path.read_text(encoding="utf-8"))
            retry = {**prepared_request, "action": "revalidate", "proposal": rendered_proposal}
            if revalidation_mutation:
                retry.update(revalidation_mutation)
            request_path.write_text(json.dumps(retry, sort_keys=True) + "\n", encoding="utf-8")
            forwarded_retry = json.loads(request_path.read_text(encoding="utf-8"))
            self.assertEqual(retry, forwarded_retry)
            callback_input = {"request_json": forwarded_retry,
                "request_path": str(request_path.relative_to(owner_case.root)),
                "prepared_proposal": adapter["proposal"]}
            self.assertEqual(adapter["proposal"], callback_input["request_json"]["proposal"])
            revalidated = self.module.revalidate(owner_case.root, callback_input["request_json"])
            advance_main_run_summary("after-revalidate")
            source_outputs[revalidate_id] = {"lifecycle_assessment": revalidated,
                "state": revalidated.get("state"), "request_json": callback_input["request_json"],
                "proposal": revalidated.get("proposal")}
            revalidate_route = find(selected, revalidate_route_id)
            revalidated_branch = controller.select_switch_branch(revalidate_route, revalidated["state"])
            if revalidated["state"] != "ready":
                self.assertEqual([], revalidated_branch)
                self.assertEqual([], [node for node in revalidated_branch if node.get("id") == apply_id])
                return {"adapter": adapter, "revalidated": revalidated, "branch": [],
                    "owner_receipt": None, "rendered_revalidation": rendered_revalidation,
                    "forwarded_request_sha256": sha(request_path.read_bytes())}
            self.assertEqual([apply_id, verify_id], [node["id"] for node in revalidated_branch])
            apply_node = find(revalidated_branch, apply_id)
            rendered_apply = controller.render_template(apply_node.get("prompt", apply_node["input"]["args"]),
                inputs, source_outputs)
            match = re.search(r"PHASE_MILESTONE_REQUEST=([^\s]+)", rendered_apply)
            self.assertIsNotNone(match, rendered_apply)
            rendered_request_path = match.group(1)
            self.assertEqual(str(request_path.relative_to(owner_case.root)), rendered_request_path)
            apply_request_json = {**request, "action": "revalidate", "proposal": revalidated["proposal"]}
            callback_output = {**callback_input, "apply_request_json": apply_request_json,
                "current_proposal": revalidated["proposal"]}
            source_outputs[revalidate_id].update(callback_output)
            self.assertEqual(revalidated["proposal"], callback_output["apply_request_json"]["proposal"])
            request_path.write_text(json.dumps(callback_output["apply_request_json"], sort_keys=True) + "\n",
                encoding="utf-8")
            apply_request = json.loads((owner_case.root / rendered_request_path).read_text(encoding="utf-8"))
            if apply_packet_mutation:
                for key, value in apply_packet_mutation.items():
                    if key.startswith("proposal."):
                        apply_request["proposal"][key.split(".", 1)[1]] = value
                    else:
                        apply_request[key] = value
                (owner_case.root / rendered_request_path).write_text(
                    json.dumps(apply_request, sort_keys=True) + "\n", encoding="utf-8")
                apply_request = json.loads((owner_case.root / rendered_request_path).read_text(encoding="utf-8"))
            self.assertEqual("revalidate", apply_request["action"])
            try:
                receipt = owner_module.phase.apply(owner_case.root, apply_request["proposal"], owner_module.yaml)
                owner_error = None
            except Exception as error:
                receipt = None
                owner_error = str(error)
            if receipt is None:
                verify_result = {"state": "blocked", "reason_code": "owner-command-rejected-packet",
                    "owner_error": owner_error, "roadmap_sha256": owner_module.sha(owner_case.roadmap)}
                return {"adapter": adapter, "revalidated": revalidated, "branch": revalidated_branch,
                    "owner_receipt": None, "verification": verify_result,
                    "rendered_revalidation": rendered_revalidation, "rendered_apply": rendered_apply,
                    "forwarded_request_sha256": sha(request_path.read_bytes()), "apply_packet_blocked": True,
                    "owner_error": owner_error,
                    "production_callback_outputs": {"prepare_state": adapter.get("state"),
                        "prepare_request_sha256": digest(request),
                        "prepare_proposal_sha256": digest(adapter.get("proposal")),
                        "revalidation_state": revalidated.get("state"),
                        "revalidation_request_json_sha256": digest(callback_input["request_json"]),
                        "revalidation_proposal_sha256": digest(revalidated.get("proposal")),
                        "rendered_callback_arguments_sha256": rendered_arguments_sha256,
                        "rendered_request_path": rendered_request_path,
                        "rendered_proposal_sha256": digest(rendered_proposal),
                        "apply_request_json_sha256": digest(apply_request),
                        "rendered_command_argument_path": rendered_request_path,
                        "owner_receipt_sha256": None, "owner_error": owner_error}}
            self.module.validate_receipt(receipt)
            owner_module.phase.validate_receipt(receipt)
            advance_main_run_summary("after-owner-write")
            source_outputs[apply_id] = {"receipt": receipt, "state": receipt.get("effect_state")}
            verify_node = find(revalidated_branch, verify_id)
            rendered_verify = controller.render_template(verify_node["prompt"], inputs, source_outputs)
            self.assertIn(verify_id, [node["id"] for node in revalidated_branch])
            verify_result = {"state": "verified" if receipt["effect_state"] == "applied"
                and receipt.get("roadmap_after_sha256") == owner_module.sha(owner_case.roadmap)
                and revalidated["proposal"]["expected_roadmap_sha256"] == receipt["roadmap_before_sha256"] else "blocked",
                "receipt": receipt, "roadmap_sha256": owner_module.sha(owner_case.roadmap)}
            verify_result["receipt_validation"] = {"flowkit": "passed", "owner": "passed",
                "receipt_sha256": digest(receipt), "observed_roadmap_sha256": verify_result["roadmap_sha256"]}
            source_outputs[verify_id] = verify_result
            return {"adapter": adapter, "revalidated": revalidated, "branch": revalidated_branch,
                "owner_receipt": receipt, "verification": verify_result,
                "rendered_revalidation": rendered_revalidation, "rendered_apply": rendered_apply,
                "rendered_verify": rendered_verify, "forwarded_request_sha256": sha(request_path.read_bytes()),
                "apply_packet_blocked": (receipt.get("effect_state") != "applied"),
                "production_callback_outputs": {"prepare_state": adapter.get("state"),
                    "prepare_request_sha256": digest(request),
                    "prepare_proposal_sha256": digest(adapter.get("proposal")),
                    "revalidation_state": revalidated.get("state"),
                    "revalidation_request_json_sha256": digest(callback_input["request_json"]),
                    "revalidation_proposal_sha256": digest(revalidated.get("proposal")),
                    "rendered_callback_arguments_sha256": rendered_arguments_sha256,
                    "rendered_request_path": rendered_request_path,
                    "rendered_proposal_sha256": digest(rendered_proposal),
                    "apply_request_json_sha256": digest(apply_request),
                    "rendered_command_argument_path": rendered_request_path,
                    "owner_receipt_sha256": digest(receipt),
                    "owner_effect_state": receipt.get("effect_state"),
                    "receipt_validators": ["flowkit", "flow-roadmap owner"],
                    "verified_roadmap_sha256": verify_result["roadmap_sha256"]}}

        # Rebuild the canonical negative recovery request on an initialized
        # current owner consumer. Its sole invalidity is an unsubstantiated
        # historical start edge, so the exact packet traverses the real
        # rendered request-path command, FlowKit adapter, and external owner.
        canonical_case = owner_module.LifecycleTests(
            "test_three_phase_owned_adjacent_effects_preserve_unrelated_bytes")
        canonical_case.setUp()
        try:
            owner_support = canonical_case.request(current="specced", owner="closeout", mode="recovery",
                milestones=["specced", "in-progress"])
            fixture_data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
            aliases = skipped_recovery["materialization_aliases"]
            self.assertEqual("initialized-owner-feature-directory", aliases["feature_directory"])
            self.assertEqual("initialized-owner-required-source-map",
                             aliases["snapshot.source_map.additional_required_files"])
            self.assertEqual("canonical-fixture-materialized-file-sha256", aliases["source_references"])
            def materialize_path_aliases(value):
                if isinstance(value, dict):
                    return {materialize_path_aliases(key): materialize_path_aliases(item)
                            for key, item in value.items()}
                if isinstance(value, list):
                    return [materialize_path_aliases(item) for item in value]
                if isinstance(value, str):
                    return value.replace("specs/901-phase-lifecycle", canonical_case.feature)
                return value
            canonical_request = materialize_path_aliases(skipped_recovery["payload"])
            self.assertEqual(canonical_case.feature, canonical_request["feature_directory"])
            canonical_semantics = json.loads(json.dumps(canonical_request))
            materialized_hashes = {}
            for relative, record in fixture_data["materialized_files"].items():
                if relative == ".specify/memory/roadmap.md":
                    continue  # retain the initialized owner's actual ledger fixture
                content = record["content"].replace("specs/901-phase-lifecycle", canonical_case.feature)
                self.assertEqual(record["sha256"], sha(record["content"].encode()), relative)
                materialized_relative = relative.replace("specs/901-phase-lifecycle", canonical_case.feature)
                destination = canonical_case.root / materialized_relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(content, encoding="utf-8")
                materialized_hashes[materialized_relative] = owner_module.sha(destination)
            def refresh_declared_hash_aliases(value):
                if isinstance(value, dict):
                    refreshed = {key: refresh_declared_hash_aliases(item) for key, item in value.items()}
                    source_map = refreshed.get("source_map")
                    if isinstance(source_map, dict):
                        for relative in list(source_map):
                            if relative in materialized_hashes:
                                source_map[relative] = materialized_hashes[relative]
                    artifact_digests = refreshed.get("artifact_digests")
                    if isinstance(artifact_digests, dict):
                        for relative in list(artifact_digests):
                            if relative in materialized_hashes:
                                artifact_digests[relative] = materialized_hashes[relative]
                    relative = refreshed.get("path")
                    if relative in materialized_hashes and "sha256" in refreshed:
                        refreshed["sha256"] = materialized_hashes[relative]
                    return refreshed
                if isinstance(value, list):
                    return [refresh_declared_hash_aliases(item) for item in value]
                return value
            canonical_request = refresh_declared_hash_aliases(canonical_request)
            canonical_semantics = refresh_declared_hash_aliases(canonical_semantics)
            canonical_request["snapshot"]["source_map"] = {
                **owner_support["snapshot"]["source_map"],
                **canonical_request["snapshot"]["source_map"],
            }
            for relative in canonical_request["snapshot"]["source_map"]:
                source = canonical_case.root / relative
                self.assertTrue(source.is_file(), f"declared owner source alias missing: {relative}")
                canonical_request["snapshot"]["source_map"][relative] = owner_module.sha(source)
            self.assertEqual("initialized-owner-roadmap-sha256",
                             aliases["snapshot.source_map..specify/memory/roadmap.md"])
            self.assertEqual("initialized-owner-dependency-states",
                             aliases["snapshot.dependency_states"])
            self.assertEqual("initialized-owner-pending-future-ids",
                             aliases["snapshot.pending_future_ids"])
            canonical_request["snapshot"]["source_map"][".specify/memory/roadmap.md"] = owner_module.sha(
                canonical_case.roadmap)
            canonical_request["snapshot"]["dependency_states"] = owner_support["snapshot"]["dependency_states"]
            canonical_request["snapshot"]["pending_future_ids"] = owner_support["snapshot"]["pending_future_ids"]
            canonical_graph = owner_module.yaml.safe_load(
                (ROOT / "workflows/speckit-flow-closeout/workflow.yml").read_text(encoding="utf-8"))
            graph_relative = ".specify/workflows/speckit-flow-closeout/workflow.yml"
            installed_inputs = {
                graph_relative: ROOT / "workflows/speckit-flow-closeout/workflow.yml",
                ".specify/flow-kit/manifest.yml": ROOT / "controllers/flow-kit/manifest.yml",
            }
            for relative, source_path in installed_inputs.items():
                destination = canonical_case.root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source_path.read_bytes())
                canonical_request["snapshot"]["source_map"][relative] = owner_module.sha(destination)
            for relative in (".specify/flow-kit/skills-install.json", ".specify/bundle-records.json"):
                destination = canonical_case.root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text("{}\n", encoding="utf-8")
                canonical_request["snapshot"]["source_map"][relative] = owner_module.sha(destination)
            self.assertEqual(canonical_semantics["milestone_evidence"], canonical_request["milestone_evidence"])
            self.assertEqual("specced", canonical_request["snapshot"]["current_status"])
            activity = canonical_request["milestone_evidence"][1]["historical_activity"][0]
            activity_record = json.loads((canonical_case.root / activity["path"]).read_text(encoding="utf-8"))
            self.assertEqual("unsubstantiated-activity", activity_record["kind"])
            self.assertEqual(activity["sha256"], owner_module.sha(canonical_case.root / activity["path"]))
            canonical_request["request_path"] = (
                f"{canonical_request['feature_directory']}/validation/phase-lifecycle/closeout-request.json")
            request_node = find(canonical_graph["steps"], "prepare-closeout-lifecycle-transition")
            rendered_command = controller.render_template(request_node["prompt"], {}, {
                "prepare-closeout-lifecycle-request": {"request_path": canonical_request["request_path"]}})
            self.assertIn(canonical_request["request_path"], rendered_command)
            request_path = canonical_case.root / canonical_request["request_path"]
            request_path.parent.mkdir(parents=True, exist_ok=True)
            request_packet = {key: value for key, value in canonical_request.items() if key != "request_path"}
            request_path.write_text(json.dumps(request_packet, sort_keys=True) + "\n", encoding="utf-8")
            forwarded_request = json.loads(request_path.read_text(encoding="utf-8"))
            self.assertEqual(request_packet, forwarded_request,
                             "production forwarding must preserve the entire materialized canonical packet")
            self.assertEqual(set(canonical_semantics), set(forwarded_request),
                             "materialization must not drop or add canonical top-level fields")
            for key, expected_value in canonical_semantics.items():
                if key == "snapshot":
                    continue
                self.assertEqual(expected_value, forwarded_request[key],
                                 f"canonical submitted field changed during materialization: {key}")
            canonical_snapshot = canonical_semantics["snapshot"]
            forwarded_snapshot = forwarded_request["snapshot"]
            self.assertEqual(set(canonical_snapshot), set(forwarded_snapshot),
                             "materialization must not drop or add canonical snapshot fields")
            for key, expected_value in canonical_snapshot.items():
                if key in {"source_map", "dependency_states", "pending_future_ids"}:
                    continue
                self.assertEqual(expected_value, forwarded_snapshot[key],
                                 f"canonical submitted snapshot field changed: {key}")
            canonical_source_map = canonical_snapshot["source_map"]
            self.assertTrue(set(canonical_source_map).issubset(forwarded_snapshot["source_map"]))
            for relative, expected_digest in canonical_source_map.items():
                if relative == ".specify/memory/roadmap.md":
                    continue  # the one declared owner-current roadmap digest alias
                self.assertEqual(expected_digest, forwarded_snapshot["source_map"][relative], relative)
            self.assertEqual(owner_support["snapshot"]["dependency_states"],
                             forwarded_snapshot["dependency_states"])
            self.assertEqual(owner_support["snapshot"]["pending_future_ids"],
                             forwarded_snapshot["pending_future_ids"])
            self.assertEqual(canonical_semantics["milestone_evidence"], forwarded_request["milestone_evidence"])
            self.assertEqual(canonical_semantics["snapshot"]["current_status"],
                             forwarded_request["snapshot"]["current_status"])
            stale_materialized_sources = {
                relative: {"expected": expected, "observed": owner_module.sha(canonical_case.root / relative)
                           if (canonical_case.root / relative).is_file() else None}
                for relative, expected in forwarded_request["snapshot"]["source_map"].items()
                if not (canonical_case.root / relative).is_file()
                or owner_module.sha(canonical_case.root / relative) != expected
            }
            self.assertEqual({}, stale_materialized_sources, stale_materialized_sources)
            observed_snapshot = owner_module.phase.collect_snapshot(
                canonical_case.root, forwarded_request, owner_module.yaml)
            if observed_snapshot != forwarded_request["snapshot"]:
                self.fail("canonical owner snapshot alias mismatch: " + json.dumps({
                    key: {"expected": forwarded_request["snapshot"].get(key), "observed": observed_snapshot.get(key)}
                    for key in observed_snapshot
                    if observed_snapshot.get(key) != forwarded_request["snapshot"].get(key)}, sort_keys=True))
            before_roadmap = owner_module.sha(canonical_case.roadmap)
            adapter_result = self.module.prepare(canonical_case.root, forwarded_request)
            owner_result = owner_module.phase.evaluate(
                canonical_case.root, forwarded_request, owner_module.yaml)
            self.assertEqual("blocked", adapter_result.get("state"), adapter_result)
            self.assertEqual("authorized-start-attestation-required", adapter_result.get("reason_code"), adapter_result)
            self.assertEqual("historical-start-unsubstantiated", owner_result.get("reason_code"), owner_result)
            self.assertEqual(before_roadmap, owner_module.sha(canonical_case.roadmap))
            canonical_dispatch = {"case_id": skipped_recovery["id"],
                "payload_sha256": sha(request_path.read_bytes()), "adapter_reason": adapter_result["reason_code"],
                "owner_reason": owner_result["reason_code"], "roadmap_unchanged": True,
                "request_path": canonical_request["request_path"]}
        finally:
            canonical_case.doCleanups()

        actual_case_results = {}
        actual_cases = {
            "LC001": ("specify", "planned", "normal", ["specced"]),
            "LC002": ("specify", "planned", "normal", ["specced"]),
            "LC003": ("implement", "specced", "normal", ["in-progress"]),
            "LC004": ("implement", "specced", "normal", ["in-progress"]),
            "LC005": ("closeout", "in-progress", "normal", ["implemented"]),
            "LC006": ("closeout", "in-progress", "normal", ["implemented"]),
            "LC007": ("closeout", "verified", "normal", ["implemented"]),
            "LC009": ("closeout", "planned", "recovery", ["specced", "implemented"]),
            "LC010": ("specify", "deferred", "normal", ["specced"]),
            "LC011": ("implement", "specced", "normal", ["in-progress"]),
            "LC012": ("closeout", "abandoned", "normal", ["implemented"]),
            "LC013": ("closeout", "in-progress", "normal", ["implemented"]),
            "LC014": ("closeout", "in-progress", "normal", ["implemented"]),
            "LC015": ("closeout", "implemented", "normal", ["implemented"]),
        }
        lifecycle_routes = {
            "specify": "route-specification-lifecycle-transition",
            "implement": "route-implementation-start-milestone",
            "closeout": "route-closeout-lifecycle-transition",
        }
        for case_id, (phase, current, mode, milestones) in actual_cases.items():
            owner_case, request, graph = prepare_production_case(case_id, phase, current, mode, milestones)
            try:
                if case_id == "LC002":
                    request["milestone_evidence"] = []
                elif case_id == "LC004":
                    request["snapshot"]["dependency_states"] = [{"entry_id": "002", "status": "planned"}]
                elif case_id == "LC006":
                    owner_module.write(owner_case.root / owner_case.feature / "spec.md", "stale source\n")
                elif case_id == "LC011":
                    (owner_case.root / f".specify/workflows/speckit-flow-{phase}/workflow.yml").unlink()
                elif case_id == "LC014":
                    pass  # mutate only after a ready assessment below

                before_roadmap = owner_module.sha(owner_case.roadmap)
                assessment = self.module.prepare(owner_case.root, request)
                if case_id in {"LC001", "LC003", "LC005", "LC013"}:
                    result = execute_ready_production_route(owner_case, request, graph, phase)
                    assessment = result["adapter"]
                    revalidated = result["revalidated"]
                    receipt = result["owner_receipt"]
                    self.assertEqual("ready", assessment.get("state"), (case_id, assessment))
                    self.assertEqual("ready", revalidated.get("state"), (case_id, revalidated))
                    self.assertIsNotNone(receipt, case_id)
                    self.assertEqual("applied", receipt["effect_state"])
                    self.assertEqual("verified", result["verification"]["state"])
                    observed_state = "ready"
                    effect_state = receipt["effect_state"]
                    actual_case_results[case_id] = {"workflow": graph["workflow"]["id"],
                        "adapter_state": assessment["state"], "revalidated_state": revalidated["state"],
                        "rendered_request_sha256": result["forwarded_request_sha256"],
                        "production_callback_outputs": result["production_callback_outputs"],
                        "selected_node_ids": [node["id"] for node in result["branch"]],
                        "owner_effect_state": receipt["effect_state"],
                        "verification_state": result["verification"]["state"],
                        "roadmap_sha256_before": before_roadmap,
                        "roadmap_sha256_after": result["verification"]["roadmap_sha256"],
                        "rendered_node_inputs": {key: hashlib.sha256(value.encode()).hexdigest()
                            for key, value in result.items() if key.startswith("rendered_")}}
                elif case_id == "LC009":
                    assessment = self.module.prepare(owner_case.root, request)
                    self.assertEqual("ready", assessment.get("state"), assessment)
                    first_proposal = assessment["proposal"]
                    self.assertEqual(("planned", "specced"),
                                     (first_proposal["from_status"], first_proposal["to_status"]))
                    first_retry = {**request, "action": "revalidate", "proposal": first_proposal}
                    first_checked = self.module.revalidate(owner_case.root, first_retry)
                    self.assertEqual("ready", first_checked.get("state"), first_checked)
                    first_receipt = owner_module.phase.apply(owner_case.root, first_checked["proposal"], owner_module.yaml)
                    self.module.validate_receipt(first_receipt)
                    owner_module.phase.validate_receipt(first_receipt)
                    self.assertEqual("applied", first_receipt["effect_state"])
                    request["snapshot"]["current_status"] = "specced"
                    request["snapshot"]["source_map"][".specify/memory/roadmap.md"] = owner_module.sha(owner_case.roadmap)
                    assessment = self.module.prepare(owner_case.root, request)
                    self.assertEqual("blocked", assessment.get("state"), assessment)
                    self.assertEqual("specced", owner_module.phase.entries(owner_case.roadmap.read_text())['901']['status'])
                    observed_state = "blocked"
                    effect_state = "applied-first-edge;blocked-missing-main-attested-start-proof"
                elif case_id in {"LC002", "LC004", "LC006", "LC011", "LC014"}:
                    assessment = self.module.prepare(owner_case.root, request)
                    if case_id == "LC014":
                        self.assertEqual("ready", assessment.get("state"), assessment)
                        result = execute_ready_production_route(owner_case, request, graph, phase,
                            before_revalidation=lambda: owner_module.write(
                                owner_case.root / owner_case.feature / "spec.md", "concurrent change\n"))
                        assessment = result["revalidated"]
                    self.assertEqual("blocked", assessment.get("state"), (case_id, assessment))
                    self.assertEqual(before_roadmap, owner_module.sha(owner_case.roadmap), case_id)
                    observed_state = "blocked"
                    effect_state = "none"
                elif case_id in {"LC010", "LC012"}:
                    self.assertEqual("question", assessment.get("state"), (case_id, assessment))
                    self.assertEqual(before_roadmap, owner_module.sha(owner_case.roadmap), case_id)
                    observed_state = "question"
                    effect_state = "none"
                elif case_id == "LC007":
                    self.assertEqual("no-op", assessment.get("state"), assessment)
                    self.assertEqual(before_roadmap, owner_module.sha(owner_case.roadmap))
                    observed_state = "no-op"
                    effect_state = "none"
                elif case_id == "LC015":
                    self.assertIn(assessment.get("state"), {"no-op", "ready"}, assessment)
                    observed_state = "no-op" if assessment["state"] == "no-op" else "ready"
                    effect_state = "none"
                route_node = find(graph["steps"], lifecycle_routes[phase])
                branch = controller.select_switch_branch(route_node, observed_state)
                if observed_state in {"blocked", "question"}:
                    self.assertEqual([], branch, (case_id, branch))
                actual_case_results[case_id] = {**actual_case_results.get(case_id, {}),
                    "workflow": graph["workflow"]["id"],
                    "route_node_id": route_node["id"], "adapter_state": observed_state,
                    "selected_node_ids": [node["id"] for node in branch], "effect_state": effect_state,
                    "roadmap_sha256_before": before_roadmap,
                    "roadmap_sha256_after": owner_module.sha(owner_case.roadmap)}
            finally:
                owner_case.doCleanups()

        # LC007 exercises equal and advanced current statuses for each owning
        # phase, then proves that missing and contradictory evidence cannot be
        # mistaken for a no-op. All packets still traverse the production
        # request/forwarding prompts and both independent assessors.
        lc007_rows = []
        lc007_targets = {"specify": "specced", "implement": "in-progress", "closeout": "implemented"}
        lc007_scenarios = {
            "specify": [("equal", "specced", "normal", ["specced"]),
                        ("advanced", "in-progress", "recovery", ["specced", "in-progress"])],
            "implement": [("equal", "in-progress", "normal", ["in-progress"]),
                          ("advanced", "implemented", "recovery", ["in-progress", "implemented"])],
            "closeout": [("equal", "implemented", "normal", ["implemented"]),
                         ("advanced", "verified", "recovery", ["implemented"])],
        }
        for phase, scenarios in lc007_scenarios.items():
            for variant, current, mode, milestones in scenarios:
                for proof_state in ("valid", "missing", "contradictory"):
                    case_name = f"LC007-{phase}-{variant}-{proof_state}"
                    owner_case, request, graph = prepare_production_case(
                        case_name, phase, current, mode, milestones)
                    try:
                        if proof_state == "missing":
                            request["milestone_evidence"] = []
                        elif proof_state == "contradictory":
                            self.assertTrue(request["milestone_evidence"], case_name)
                            request["milestone_evidence"][-1]["satisfied_check_ids"] = []
                        if proof_state != "valid":
                            owner_case.forwarded_packet_path.write_text(
                                json.dumps(request, sort_keys=True) + "\n", encoding="utf-8")
                            request = json.loads(owner_case.forwarded_packet_path.read_text(encoding="utf-8"))
                        before_roadmap = owner_module.sha(owner_case.roadmap)
                        adapter_result = self.module.prepare(owner_case.root, request)
                        owner_result = owner_module.phase.evaluate(owner_case.root, request, owner_module.yaml)
                        expected_state = "no-op" if proof_state == "valid" else "blocked"
                        self.assertEqual(expected_state, adapter_result.get("state"),
                                         (case_name, adapter_result))
                        self.assertEqual(expected_state, owner_result.get("state"),
                                         (case_name, owner_result))
                        self.assertEqual(before_roadmap, owner_module.sha(owner_case.roadmap), case_name)
                        route = find(graph["steps"], lifecycle_routes[phase])
                        selected = controller.select_switch_branch(route, expected_state)
                        if expected_state == "blocked":
                            self.assertEqual([], selected, case_name)
                        lc007_rows.append({"case_id": "LC007", "phase": phase, "variant": variant,
                            "proof_state": proof_state, "adapter_state": adapter_result["state"],
                            "owner_state": owner_result["state"], "reason_code": adapter_result.get("reason_code"),
                            "roadmap_sha256": before_roadmap, "event_free": True,
                            "selected_node_ids": [node["id"] for node in selected]})
                    finally:
                        owner_case.doCleanups()
        self.assertEqual(18, len(lc007_rows))

        # LC008 executes every recovery edge as actual prepare, revalidate,
        # owner apply, and dual receipt validation above. LC013 additionally
        # validates every discriminated receipt outcome through both validators.
        receipt_cases = [case for case in json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["cases"]
                         if case["area"] == "receipt"]
        for receipt_case in receipt_cases:
            receipt = receipt_case["payload"]
            with self.subTest(receipt=receipt_case["id"]):
                if receipt_case["expected"].startswith("reject"):
                    with self.assertRaises(ValueError):
                        self.module.validate_receipt(receipt)
                    with self.assertRaises(owner_module.phase.ContractError):
                        owner_module.phase.validate_receipt(receipt)
                else:
                    self.module.validate_receipt(receipt)
                    owner_module.phase.validate_receipt(receipt)
        actual_case_results["LC008"] = {"workflow": "speckit-flow-closeout",
            "route_node_id": "route-closeout-lifecycle-transition", "adapter_state": "ready",
            "effect_state": "applied", "edges": ["planned→specced", "specced→in-progress", "in-progress→implemented"]}
        actual_case_results["LC013"]["receipt_fixture_vectors_additional"] = len(receipt_cases)
        actual_case_results["LC007"]["all_owner_proof_matrix"] = lc007_rows

        # Prove that a malformed typed producer field reaches both actual
        # consumers through the same rendered forwarding path. This sensitivity
        # case would have passed before when only generic prompt text was checked.
        mutation_case, mutation_packet, _ = prepare_production_case(
            "LC007-producer-field-mutation", "implement", "in-progress", "normal", ["in-progress"],
            producer_mutation={"workflow_id": "speckit-flow-specify"})
        try:
            submitted = json.loads(mutation_case.forwarded_packet_path.read_text(encoding="utf-8"))
            self.assertEqual("speckit-flow-specify", mutation_case.production_callback_output["request"]["workflow_id"])
            self.assertEqual(mutation_case.production_callback_output["request"], submitted)
            self.assertIn(str(mutation_case.forwarded_packet_path.relative_to(mutation_case.root)),
                          mutation_case.production_forwarded_prompt)
            self.assertEqual(submitted, mutation_packet)
            mutation_adapter = self.module.prepare(mutation_case.root, submitted)
            mutation_owner = owner_module.phase.evaluate(mutation_case.root, submitted, owner_module.yaml)
            self.assertEqual("blocked", mutation_adapter.get("state"), mutation_adapter)
            self.assertEqual("blocked", mutation_owner.get("state"), mutation_owner)
            self.assertTrue(mutation_adapter.get("reason_code"))
            self.assertTrue(mutation_owner.get("reason_code"))
            actual_case_results["LC007"]["producer_field_sensitivity"] = {
                "field": "workflow_id", "mutated_value": submitted["workflow_id"],
                "adapter_reason": mutation_adapter.get("reason_code"),
                "owner_reason": mutation_owner.get("reason_code"),
                "forwarded_packet_sha256": sha(mutation_case.forwarded_packet_path.read_bytes()),
            }
        finally:
            mutation_case.doCleanups()

        # A corrupted revalidation packet must be rejected by the actual adapter
        # output before the production switch can select the owner command.
        revalidation_case, revalidation_request, revalidation_graph = prepare_production_case(
            "LC007-revalidation-packet-mutation", "implement", "specced", "normal", ["in-progress"])
        try:
            before = owner_module.sha(revalidation_case.roadmap)
            result = execute_ready_production_route(revalidation_case, revalidation_request,
                revalidation_graph, "implement", revalidation_mutation={"workflow_id": "speckit-flow-specify"})
            self.assertEqual("blocked", result["revalidated"].get("state"), result["revalidated"])
            self.assertEqual([], result["branch"])
            self.assertIsNone(result["owner_receipt"])
            self.assertEqual(before, owner_module.sha(revalidation_case.roadmap))
            actual_case_results["LC007"]["revalidation_packet_sensitivity"] = {
                "mutated_field": "workflow_id", "adapter_state": result["revalidated"]["state"],
                "owner_node_selected": False, "roadmap_unchanged": True,
                "forwarded_request_sha256": result["forwarded_request_sha256"]}
        finally:
            revalidation_case.doCleanups()

        # A malformed owner input is parsed from the exact rendered command
        # path and reaches the real owner. Its stale proposal is rejected with
        # a not-applied receipt and leaves the roadmap unchanged.
        apply_case, apply_request, apply_graph = prepare_production_case(
            "LC007-owner-packet-mutation", "implement", "specced", "normal", ["in-progress"])
        try:
            before = owner_module.sha(apply_case.roadmap)
            result = execute_ready_production_route(apply_case, apply_request, apply_graph, "implement",
                apply_packet_mutation={"proposal.expected_roadmap_sha256": "0" * 64})
            self.assertEqual("ready", result["revalidated"]["state"])
            self.assertIsNone(result["owner_receipt"])
            self.assertTrue(result["owner_error"])
            self.assertEqual("blocked", result["verification"]["state"])
            self.assertTrue(result["apply_packet_blocked"])
            self.assertEqual(before, owner_module.sha(apply_case.roadmap))
            actual_case_results["LC007"]["owner_packet_sensitivity"] = {
                "mutated_field": "proposal.expected_roadmap_sha256",
                "owner_rejected_packet": True, "owner_error": result["owner_error"],
                "verification_state": result["verification"]["state"], "roadmap_unchanged": True,
                "forwarded_request_sha256": result["forwarded_request_sha256"]}
        finally:
            apply_case.doCleanups()
        write_boundary_results = {}

        def prepared_lc013(case_name: str):
            owner_case, request, graph = prepare_production_case(
                case_name, "closeout", "in-progress", "normal", ["implemented"])
            assessment = self.module.prepare(owner_case.root, request)
            self.assertEqual("ready", assessment.get("state"), assessment)
            retry = {**request, "action": "revalidate", "proposal": assessment["proposal"]}
            checked = self.module.revalidate(owner_case.root, retry)
            self.assertEqual("ready", checked.get("state"), checked)
            return owner_case, request, checked["proposal"]

        # Exercise the real owner write boundary with failures whose returned
        # receipt is checked against roadmap bytes and the appended event.
        owner_case, request, proposal = prepared_lc013("LC013-before-write")
        try:
            before = owner_module.sha(owner_case.roadmap)
            original_atomic = owner_module.phase._atomic
            def fail_before_write(path, raw, expected_sha256=None):
                if path == owner_case.roadmap:
                    raise OSError("injected pre-write failure")
                return original_atomic(path, raw, expected_sha256)
            with patch.object(owner_module.phase, "_atomic", fail_before_write):
                receipt = owner_module.phase.apply(owner_case.root, proposal, owner_module.yaml)
            self.module.validate_receipt(receipt)
            self.assertEqual(("not-applied", "recorded"), (receipt["effect_state"], receipt["record_state"]))
            self.assertEqual(before, owner_module.sha(owner_case.roadmap))
            fresh = self.module.prepare(owner_case.root, request)
            self.assertEqual("ready", fresh.get("state"), fresh)
            checked = self.module.revalidate(owner_case.root,
                {**request, "action": "revalidate", "proposal": fresh["proposal"]})
            retry_receipt = owner_module.phase.apply(owner_case.root, checked["proposal"], owner_module.yaml)
            self.module.validate_receipt(retry_receipt)
            self.assertEqual("applied", retry_receipt["effect_state"])
            event_count = owner_case.roadmap.read_text(encoding="utf-8").count("<!-- flow-roadmap-lifecycle ")
            self.assertEqual(1, event_count)
            write_boundary_results["before_write_retry"] = {
                "first_effect": receipt["effect_state"], "retry_effect": retry_receipt["effect_state"],
                "retry_occurrence_matches_owner_event": retry_receipt["occurred_at"] in owner_case.roadmap.read_text(encoding="utf-8"),
                "event_count": event_count, "roadmap_before_sha256": before,
                "roadmap_after_sha256": owner_module.sha(owner_case.roadmap)}
        finally:
            owner_case.doCleanups()

        owner_case, _, proposal = prepared_lc013("LC013-after-write")
        try:
            original_atomic = owner_module.phase._atomic
            def fail_after_write(path, raw, expected_sha256=None):
                original_atomic(path, raw, expected_sha256)
                if path == owner_case.roadmap:
                    raise OSError("injected post-write error")
            with patch.object(owner_module.phase, "_atomic", fail_after_write):
                receipt = owner_module.phase.apply(owner_case.root, proposal, owner_module.yaml)
            self.module.validate_receipt(receipt)
            event = next(json.loads(match) for match in __import__("re").findall(
                r"<!-- flow-roadmap-lifecycle (.+?) -->", owner_case.roadmap.read_text(encoding="utf-8")))
            self.assertEqual("applied", receipt["effect_state"])
            self.assertEqual(event["occurred_at"], receipt["occurred_at"])
            self.assertEqual(1, owner_case.roadmap.read_text(encoding="utf-8").count("<!-- flow-roadmap-lifecycle "))
            write_boundary_results["after_write_error"] = {
                "effect": receipt["effect_state"], "receipt_time_is_actual_event_time": receipt["occurred_at"] == event["occurred_at"],
                "event_count": 1, "roadmap_status": owner_module.phase.entries(owner_case.roadmap.read_text())["901"]["status"]}
        finally:
            owner_case.doCleanups()

        owner_case, _, proposal = prepared_lc013("LC013-receipt-failure")
        try:
            original_atomic = owner_module.phase._atomic
            def fail_receipt_record(path, raw, expected_sha256=None):
                if "lifecycle-receipts" in path.parts:
                    raise OSError("injected receipt persistence failure")
                return original_atomic(path, raw, expected_sha256)
            with patch.object(owner_module.phase, "_atomic", fail_receipt_record):
                receipt = owner_module.phase.apply(owner_case.root, proposal, owner_module.yaml)
            self.module.validate_receipt(receipt)
            self.assertEqual(("applied", "failed"), (receipt["effect_state"], receipt["record_state"]))
            self.assertEqual("implemented", owner_module.phase.entries(owner_case.roadmap.read_text())["901"]["status"])
            write_boundary_results["receipt_persistence_failure"] = {
                "effect": receipt["effect_state"], "record": receipt["record_state"],
                "roadmap_status": "implemented", "record_error": receipt["record_error"]}
        finally:
            owner_case.doCleanups()

        owner_case, _, proposal = prepared_lc013("LC013-unobservable-readback")
        try:
            original_atomic = owner_module.phase._atomic
            original_read = owner_module.phase.read_bytes
            effect_written = False
            def observe_atomic(path, raw, expected_sha256=None):
                nonlocal effect_written
                original_atomic(path, raw, expected_sha256)
                if path == owner_case.roadmap:
                    effect_written = True
            def hide_readback(project, relative):
                if effect_written and relative == ".specify/memory/roadmap.md":
                    raise OSError("injected unreadable readback")
                return original_read(project, relative)
            with patch.object(owner_module.phase, "_atomic", observe_atomic), \
                 patch.object(owner_module.phase, "read_bytes", hide_readback):
                receipt = owner_module.phase.apply(owner_case.root, proposal, owner_module.yaml)
            self.module.validate_receipt(receipt)
            actual_bytes = owner_case.roadmap.read_bytes()
            self.assertEqual("indeterminate", receipt["effect_state"])
            self.assertNotEqual(proposal["expected_roadmap_sha256"], owner_module.sha(owner_case.roadmap))
            self.assertEqual("implemented", owner_module.phase.entries(actual_bytes.decode())["901"]["status"])
            self.assertEqual(1, actual_bytes.decode().count("<!-- flow-roadmap-lifecycle "))
            write_boundary_results["unobservable_readback"] = {
                "receipt_effect": receipt["effect_state"], "record": receipt["record_state"],
                "observed_roadmap_status": "implemented", "event_count": 1,
                "no_rollback": True, "observed_roadmap_sha256": owner_module.sha(owner_case.roadmap)}
        finally:
            owner_case.doCleanups()
        actual_case_results["LC013"]["owner_write_boundary"] = write_boundary_results
        actual_case_results["LC015"]["verified_gate"] = {
            choice: [node["id"] for node in controller.select_switch_branch(
                find(workflows["closeout"]["steps"], "route-implemented-lifecycle-before-debrief"), choice)]
            for choice in ("verified", "blocked", "question")}
        self.assertEqual({f"LC{number:03d}" for number in range(1, 16)}, set(actual_case_results))
        # LC008 follows the actual bounded Close Out recovery loop and selects
        # all three adjacent-edge iterations from the declared loop body.
        recovery = find(workflows["closeout"]["steps"], "closeout-lifecycle-recovery-loop")
        self.assertEqual(3, recovery["max_iterations"])
        recovery_ids = [node["id"] for node in recovery["steps"]]
        self.assertEqual(["assess-closeout-lifecycle-edge", "route-closeout-recovery-evidence",
                          "prepare-closeout-lifecycle-request", "prepare-closeout-lifecycle-transition"],
                         recovery_ids[:4])
        recovery_route = find(recovery["steps"], "route-closeout-lifecycle-transition")
        self.assertEqual("switch", recovery_route["type"])
        recovery_evidence_route = find(recovery["steps"], "route-closeout-recovery-evidence")
        self.assertEqual(["assess-recovery-roadmap-brief", "assess-recovery-preparation",
                          "record-recovery-preparation", "assess-recovery-readiness",
                          "attest-recovery-start"],
                         [node["id"] for node in controller.select_switch_branch(
                             recovery_evidence_route, "recovery")])
        self.assertEqual([], controller.select_switch_branch(recovery_evidence_route, "normal"))
        observations["LC008"] = {"workflow_id": workflows["closeout"]["workflow"]["id"],
            "route_node_id": recovery_route["id"], "selected_branch": "continue x3",
            "production_nodes": recovery_ids, "max_iterations": recovery["max_iterations"]}

        # LC015 is the explicit verification gate after implemented; only its
        # verified choice reaches debrief, while blocked/question stop.
        final_gate = find(workflows["closeout"]["steps"], "route-implemented-lifecycle-before-debrief")
        verified = controller.select_switch_branch(final_gate, "verified")
        self.assertEqual(["closeout-debrief-loop"], [node["id"] for node in verified])
        self.assertEqual([], controller.select_switch_branch(final_gate, "blocked"))
        self.assertEqual([], controller.select_switch_branch(final_gate, "question"))
        observations["LC015"] = {"workflow_id": workflows["closeout"]["workflow"]["id"],
            "route_node_id": final_gate["id"], "selected_branch": "verified",
            "production_nodes": [node["id"] for node in verified],
            "blocked_nodes": [], "question_nodes": []}
        self.assertEqual({f"LC{number:03d}" for number in range(1, 16)}, set(observations))

        # Feed complete, current owner proof through each actual production
        # graph and the FlowKit adapter. Tiny owner graphs and direct calls to
        # owner unit-test methods remain useful contract evidence, but cannot
        # establish that the shipped Specify, Implement, and Close Out routes
        # satisfy the owner's installed-graph checks.
        for phase_name, current_status in (("specify", "planned"), ("implement", "specced"),
                                           ("closeout", "in-progress")):
            with self.subTest(production_phase=phase_name):
                graph_relative = f".specify/workflows/speckit-flow-{phase_name}/workflow.yml"
                graph_source = ROOT / f"workflows/speckit-flow-{phase_name}/workflow.yml"
                owner_case = owner_module.LifecycleTests("test_three_phase_owned_adjacent_effects_preserve_unrelated_bytes")
                owner_case.setUp()
                try:
                    request = owner_case.request(current=current_status, owner=phase_name)
                    immutable_digests = {}
                    if phase_name == "closeout":
                        for relative, content in (("src/current-implementation.py", "implementation source evidence\n"),
                                                  ("tests/current-implementation-proof.py", "current test proof\n")):
                            destination = owner_case.root / relative
                            destination.parent.mkdir(parents=True, exist_ok=True)
                            destination.write_text(content, encoding="utf-8")
                            immutable_digests[relative] = owner_module.sha(destination)
                        group = request["milestone_evidence"][0]
                        group["artifact_digests"].update(immutable_digests)
                        for reference in group["assessments"]:
                            record_path = owner_case.root / reference["path"]
                            record = json.loads(record_path.read_text(encoding="utf-8"))
                            record["artifact_digests"].update(immutable_digests)
                            record_path.write_text(json.dumps(record, sort_keys=True), encoding="utf-8")
                            reference["sha256"] = owner_module.sha(record_path)
                        request["snapshot"]["source_map"].update(immutable_digests)
                        for reference in group["assessments"]:
                            request["snapshot"]["source_map"][reference["path"]] = reference["sha256"]
                    installed_inputs = {
                        graph_relative: graph_source,
                        ".specify/flow-kit/manifest.yml": ROOT / "controllers/flow-kit/manifest.yml",
                    }
                    for relative, source_path in installed_inputs.items():
                        destination = owner_case.root / relative
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        destination.write_bytes(source_path.read_bytes())
                        request["snapshot"]["source_map"][relative] = owner_module.sha(destination)
                    for relative in (".specify/flow-kit/skills-install.json", ".specify/bundle-records.json"):
                        destination = owner_case.root / relative
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        destination.write_text("{}\n", encoding="utf-8")
                        request["snapshot"]["source_map"][relative] = owner_module.sha(destination)
                    graph = owner_module.yaml.safe_load(graph_source.read_text(encoding="utf-8"))
                    version = graph["workflow"]["version"]
                    request["workflow_version"] = version
                    request["snapshot"]["workflow_version"] = version
                    result = self.module.prepare(owner_case.root, request)
                    self.assertEqual("ready", result.get("state"), result)
                    self.assertEqual(current_status, result["snapshot"]["current_status"])
                    self.assertEqual(phase_name, result["proposal"]["snapshot"]["phase"])
                    expected_target = {"specify": "specced", "implement": "in-progress", "closeout": "implemented"}[phase_name]
                    self.assertEqual(expected_target, result["proposal"]["to_status"])
                finally:
                    owner_case.doCleanups()

        # Execute the bounded three-edge recovery through the real adapter and
        # owner on one disposable Close Out graph. Each subsequent preparation
        # uses the actual prior write/readback and receipt, with no replay.
        recovery_case, recovery_request, graph_document = prepare_production_case(
            "LC008", "closeout", "planned", mode="recovery",
            milestones=["specced", "in-progress", "implemented"])
        try:
            (recovery_case.root / recovery_case.feature / "spec.md").write_text(
                "**Status**: Complete\n# Current specification\n", encoding="utf-8")
            feature = recovery_request["feature_directory"]
            feature_path = recovery_case.root / feature
            (recovery_case.root / ".specify/feature.json").write_text(
                json.dumps({"feature_directory": feature}, sort_keys=True), encoding="utf-8")
            checklist_path = f"{feature}/checklists/recovery-preparation.md"
            checklist = recovery_case.root / checklist_path
            checklist.parent.mkdir(parents=True, exist_ok=True)
            checklist.write_text("# Recovery preparation\n\n- [x] Current recovery scope reviewed\n", encoding="utf-8")
            package = recovery_case.root / ".specify/flow-kit/scripts/python"
            package.mkdir(parents=True, exist_ok=True)
            for source in (ROOT / "controllers/flow-kit/scripts/python").glob("*.py"):
                (package / source.name).write_bytes(source.read_bytes())

            dispatch_entries = [
                ("FlowKit-Roadmap Agent", "assess-recovery-roadmap-brief", "roadmap-child"),
                ("FlowKit-Reviewer", "assess-recovery-preparation", "preparation-reviewer-child"),
                ("FlowKit-Readiness Checker", "assess-recovery-readiness", "readiness-checker-child"),
                ("FlowKit-Reviewer", "attest-recovery-start", "native-reviewer-child"),
            ]
            dispatch_summary = {
                "run_id": recovery_request["run_id"],
                "workflow_id": graph_document["workflow"]["id"],
                "workflow_version": graph_document["workflow"]["version"],
                "child_tasks": [{"agent": agent, "step_id": step_id, "child_id": child_id}
                                for agent, step_id, child_id in dispatch_entries],
                "effective_assignments": [{"agent_name": agent, "step_id": step_id}
                                           for agent, step_id, _ in dispatch_entries],
            }
            route_inputs = {"feature_context": feature, "integration": "codex",
                            "roadmap_transition_decision": ""}
            flow_outputs = {}
            brief_path = f"{feature}/validation/phase-lifecycle/recovery-roadmap-brief.json"
            source_digests = {relative: owner_module.sha(recovery_case.root / relative)
                              for relative in (f"{feature}/spec.md", f"{feature}/plan.md",
                                              f"{feature}/tasks.md", checklist_path)}
            def phase_assessment(role: str, milestone: str, artifacts: dict[str, str]) -> dict:
                required = sorted(self.module.CHECKS[milestone])
                return {"schema_version": "1.0", "kind": "independent-phase-assessment",
                    "reviewer": role, "state": "complete", "feature_directory": feature,
                    "scope_sha256": source_digests[f"{feature}/spec.md"],
                    "artifact_digests": artifacts, "required_check_ids": required,
                    "satisfied_check_ids": required, "unresolved_ids": []}

            roadmap_brief = {"reviewer": "FlowKit-Roadmap Agent", "state": "ready",
                             "feature_directory": feature,
                             "scope_sha256": source_digests[f"{feature}/spec.md"],
                             "source_digests": source_digests, "unresolved_ids": [],
                             "linkage": "current selected roadmap entry matches this feature",
                             "assessment": phase_assessment("FlowKit-Roadmap Agent", "specced",
                                {path: digest for path, digest in source_digests.items()
                                 if path.endswith(("spec.md", "plan.md", "tasks.md"))})}
            brief_file = recovery_case.root / brief_path
            brief_file.parent.mkdir(parents=True, exist_ok=True)
            brief_file.write_text(json.dumps(roadmap_brief, sort_keys=True), encoding="utf-8")
            flow_outputs["assess-recovery-roadmap-brief"] = {"report": roadmap_brief,
                "path": brief_path, "sha256": owner_module.sha(brief_file)}
            roadmap_prompt = controller.render_template(
                find(graph_document["steps"], "assess-recovery-roadmap-brief")["input"]["args"],
                route_inputs, flow_outputs)
            self.assertIn(feature, roadmap_prompt)
            self.assertIn(source_digests[f"{feature}/spec.md"], json.dumps(roadmap_brief))

            reviewer_inputs = {**source_digests}
            reviewer_report = {"reviewer": "FlowKit-Reviewer", "state": "complete", "findings": [],
                               "reviewed_inputs": reviewer_inputs,
                               "satisfied_criteria": [], "future_classifications": [],
                               "phase_assessment": phase_assessment("FlowKit-Reviewer", "specced",
                                  {path: digest for path, digest in source_digests.items()
                                   if path.endswith(("spec.md", "plan.md", "tasks.md"))})}
            prep_prompt = controller.render_template(
                find(graph_document["steps"], "assess-recovery-preparation")["prompt"],
                route_inputs, flow_outputs)
            self.assertIn("readiness.record_review", prep_prompt)
            self.assertEqual(source_digests, reviewer_report["reviewed_inputs"])
            flow_outputs["assess-recovery-preparation"] = {"reviewer_report": reviewer_report,
                "role_fixture": "FlowKit-Reviewer judgment bound to current source digests"}

            record_step = find(graph_document["steps"], "record-recovery-preparation")
            rendered_record = controller.render_template(record_step["prompt"], route_inputs, flow_outputs)
            payload_match = re.search(r"with JSON\s+`(.*)` on stdin", rendered_record, re.DOTALL)
            self.assertIsNotNone(payload_match, rendered_record)
            rendered_readiness_payload = json.loads(payload_match.group(1))
            self.assertEqual(reviewer_report, rendered_readiness_payload["reviewer_report"])

            readiness_command = [sys.executable, str(package / "controller.py"),
                                 "readiness", "--project", str(recovery_case.root)]
            for invalid_report in ({**reviewer_report, "reviewer": "FlowKit-Readiness Checker"},
                                   {**reviewer_report, "reviewed_inputs": {**reviewer_inputs,
                                     f"{feature}/spec.md": "0" * 64}}):
                rejected = subprocess.run(readiness_command,
                    input=json.dumps({**rendered_readiness_payload, "reviewer_report": invalid_report}),
                    text=True, capture_output=True, check=False)
                self.assertNotEqual(0, rejected.returncode)
                self.assertEqual("readiness-record-write-rolled-back" if not json.loads(rejected.stdout).get("state")
                                 else "readiness-review-verdict-invalid-or-stale",
                                 json.loads(rejected.stdout).get("reason_code"))

            readiness_proof = self._add_structured_recovery_start_proof(
                recovery_case.root, recovery_request, reviewer_report, dispatch_summary)
            route_inputs["main_retained_dispatch_witness"] = readiness_proof["dispatch_witness"]
            receipt = readiness_proof["readiness_receipt"]
            self.assertEqual("recorded", receipt["state"])
            self.assertTrue(receipt["path"].endswith("readiness-review.json"))
            checker_artifacts = {path: digest for path, digest in source_digests.items()
                                 if path.endswith(("spec.md", "plan.md", "tasks.md"))}
            checker_artifacts[receipt["path"]] = receipt["sha256"]
            checker_prompt = controller.render_template(
                find(graph_document["steps"], "assess-recovery-readiness")["prompt"], route_inputs,
                {**flow_outputs, "record-recovery-preparation": receipt,
                 "readiness-assessment": readiness_proof["readiness_assessment"]})
            self.assertIn(receipt["path"], checker_prompt)
            self.assertIn(receipt["path"],
                          [item["path"] for item in readiness_proof["readiness_assessment"]["source_evidence"]])
            self.assertEqual(receipt["sha256"], next(item["sha256"] for item in
                readiness_proof["readiness_assessment"]["source_evidence"] if item["path"] == receipt["path"]))
            readiness_step = find(graph_document["steps"], "assess-recovery-readiness")
            flow_outputs["assess-recovery-readiness"] = {
                "assessment": readiness_proof["readiness_assessment"],
                "phase_assessment": phase_assessment(
                    "FlowKit-Readiness Checker", "in-progress", checker_artifacts),
                "reviewer": "FlowKit-Readiness Checker", "state": "complete",
                "source_digests": source_digests, "role_fixture": "fresh exact-scope independent judgment"}
            flow_outputs["record-recovery-preparation"] = {
                "path": receipt["path"], "sha256": receipt["sha256"],
                "history_path": readiness_proof["history_path"],
                "history_sha256": readiness_proof["history_sha256"]}
            readiness_prompt = controller.render_template(readiness_step["prompt"], route_inputs, flow_outputs)
            self.assertEqual("FlowKit-Readiness Checker", readiness_step["flow_kit"]["agent"])

            history_ref = {"path": readiness_proof["history_path"],
                           "sha256": readiness_proof["history_sha256"]}
            flow_outputs["record-recovery-preparation"] = {
                "path": receipt["path"], "sha256": receipt["sha256"],
                "history_path": history_ref["path"], "history_sha256": history_ref["sha256"]}
            attestation_prompt = controller.render_template(
                find(graph_document["steps"], "attest-recovery-start")["prompt"], route_inputs, flow_outputs)
            self.assertIn(history_ref["path"], attestation_prompt)
            self.assertEqual(history_ref["sha256"], owner_module.sha(
                recovery_case.root / history_ref["path"]))
            attestation_path = f"{feature}/validation/phase-lifecycle/authorized-implementation-start.json"
            attestation = {
                "schema_version": "1.0", "kind": "authorized-implementation-start",
                "reviewer": "FlowKit-Reviewer", "state": "ready", "feature_directory": feature,
                "scope_sha256": recovery_request["snapshot"]["scope_sha256"],
                "workflow_id": recovery_request["workflow_id"],
                "workflow_version": recovery_request["workflow_version"],
                "run_id": recovery_request["run_id"], "step_id": "attest-recovery-start",
                "child_id": "native-reviewer-child",
                "source_run_id": readiness_proof["history_validation"]["source_run_id"],
                "original_scope_sha256": readiness_proof["history_validation"]["original_scope_sha256"],
                "occurred_at": readiness_proof["history_validation"]["occurred_at"],
                "history_validation": history_ref,
                "dispatch_witness": route_inputs["main_retained_dispatch_witness"],
                "recorded_dispatch": {"agent": "FlowKit-Reviewer", "step_id": "attest-recovery-start",
                    "workflow_id": recovery_request["workflow_id"],
                    "workflow_version": recovery_request["workflow_version"],
                    "run_id": recovery_request["run_id"], "child_id": "native-reviewer-child"},
                "required_check_ids": sorted(self.module.START_CHECKS),
                "satisfied_check_ids": sorted(self.module.START_CHECKS), "unresolved_ids": [],
                "artifact_digests": readiness_proof["artifact_digests"],
            }
            attestation_file = recovery_case.root / attestation_path
            attestation_file.parent.mkdir(parents=True, exist_ok=True)
            attestation_file.write_text(json.dumps(attestation, sort_keys=True), encoding="utf-8")
            attestation_ref = {"path": attestation_path, "sha256": owner_module.sha(attestation_file),
                               "kind": attestation["kind"]}
            recovery_request["snapshot"]["source_map"][attestation_path] = attestation_ref["sha256"]
            for group in recovery_request["milestone_evidence"]:
                if group["milestone"] == "in-progress":
                    group["historical_activity"] = [attestation_ref]
            flow_outputs["attest-recovery-start"] = {"attestation": attestation,
                "path": attestation_path, "sha256": attestation_ref["sha256"],
                "role_fixture": "FlowKit-Reviewer attestation bound to validated current invocation"}
            self.assertIn(attestation_ref["sha256"], json.dumps(flow_outputs["attest-recovery-start"]))

            implemented_artifacts = readiness_proof["artifact_digests"]
            implemented_assessment = phase_assessment(
                "FlowKit-Code Reviewer", "implemented", implemented_artifacts)
            flow_outputs["assess-implemented-lifecycle-milestone"] = {
                "phase_assessment": implemented_assessment,
                "role_fixture": "retained completed implementation assessment"}

            main_snapshot = copy.deepcopy(recovery_request["snapshot"])
            feature_validation_prefix = f"{feature}/validation/"
            main_snapshot["source_map"] = {path: digest for path, digest in main_snapshot["source_map"].items()
                if not path.startswith(feature_validation_prefix)
                or path == recovery_request["decision_reference"]}
            main_snapshot["source_map"][checklist_path] = owner_module.sha(checklist)
            future_obligations_path = f"{feature}/validation/future-obligations.json"
            if (recovery_case.root / future_obligations_path).is_file():
                main_snapshot["source_map"][future_obligations_path] = owner_module.sha(
                    recovery_case.root / future_obligations_path)
            main_snapshot["source_map"][".specify/feature.json"] = owner_module.sha(
                recovery_case.root / ".specify/feature.json")

            def build_final_request(mode: str, current_status: str,
                                    outputs: dict | None = None) -> dict:
                selected_outputs = flow_outputs if outputs is None else outputs
                if mode == "recovery":
                    required_outputs = {
                        "assess-recovery-roadmap-brief", "assess-recovery-preparation",
                        "record-recovery-preparation", "assess-recovery-readiness",
                        "attest-recovery-start", "assess-implemented-lifecycle-milestone"}
                    missing_outputs = required_outputs - selected_outputs.keys()
                    if missing_outputs:
                        raise ValueError(f"recovery request is missing producer outputs: {sorted(missing_outputs)}")
                    current_spec_digest = owner_module.sha(recovery_case.root / f"{feature}/spec.md")
                    reviewer = selected_outputs["assess-recovery-preparation"]["reviewer_report"]
                    roadmap_output = selected_outputs["assess-recovery-roadmap-brief"]
                    roadmap = roadmap_output["report"]
                    checker = selected_outputs["assess-recovery-readiness"]
                    recorder = selected_outputs["record-recovery-preparation"]
                    if (reviewer.get("reviewer") != "FlowKit-Reviewer"
                            or reviewer.get("reviewed_inputs") != source_digests
                            or reviewer.get("reviewed_inputs", {}).get(f"{feature}/spec.md") != current_spec_digest
                            or roadmap.get("reviewer") != "FlowKit-Roadmap Agent"
                            or roadmap.get("source_digests") != source_digests
                            or checker.get("reviewer") != "FlowKit-Readiness Checker"
                            or checker.get("source_digests") != source_digests):
                        raise ValueError("recovery producer role or current input binding is invalid")
                    brief_path_value, brief_digest_value = roadmap_output.get("path"), roadmap_output.get("sha256")
                    if (not isinstance(brief_path_value, str) or not isinstance(brief_digest_value, str)
                            or not (recovery_case.root / brief_path_value).is_file()
                            or owner_module.sha(recovery_case.root / brief_path_value) != brief_digest_value):
                        raise ValueError("roadmap brief producer output is missing or stale")
                    recorder_refs = ((recorder.get("path"), recorder.get("sha256")),
                                     (recorder.get("history_path"), recorder.get("history_sha256")))
                    if any(not isinstance(path, str) or not isinstance(digest, str)
                           or not (recovery_case.root / path).is_file()
                           or owner_module.sha(recovery_case.root / path) != digest
                           for path, digest in recorder_refs):
                        raise ValueError("recovery recorder output is missing or stale")
                snapshot = copy.deepcopy(main_snapshot)
                snapshot["current_status"] = current_status
                if mode == "recovery":
                    snapshot["scope_sha256"] = selected_outputs["assess-recovery-preparation"][
                        "reviewer_report"]["reviewed_inputs"][f"{feature}/spec.md"]
                snapshot["source_map"][f"{feature}/spec.md"] = snapshot["scope_sha256"]
                snapshot["source_map"][".specify/memory/roadmap.md"] = owner_module.sha(recovery_case.roadmap)
                if mode == "recovery":
                    recorder = selected_outputs["record-recovery-preparation"]
                    snapshot["source_map"][recorder["path"]] = recorder["sha256"]
                    snapshot["source_map"][recorder["history_path"]] = recorder["history_sha256"]
                    snapshot["source_map"][brief_path_value] = brief_digest_value
                    snapshot["source_map"][checklist_path] = owner_module.sha(checklist)
                else:
                    for reference in readiness_proof["trusted_inputs"].values():
                        if reference["path"] != ".specify/feature.json":
                            snapshot["source_map"].pop(reference["path"], None)
                    for reference in (receipt["path"], brief_path,
                                      readiness_proof["history_path"], attestation_path,
                                      readiness_proof["dispatch_witness"]["path"],
                                      readiness_proof["dispatch_summary_path"],
                                      readiness_proof["dispatch_witness"]["path"].replace(
                                          "recovery-start-dispatch-witness.json",
                                          "dispatch-summary-at-capture.json")):
                        snapshot["source_map"].pop(reference, None)
                milestone_entries = []
                def group_for(milestone: str, producer_roles: list[tuple[str, str]],
                              *, history: bool = False) -> dict:
                    assessments = []
                    artifacts = {}
                    for output_id, role in producer_roles:
                        output = selected_outputs[output_id]
                        if output_id == "assess-recovery-preparation":
                            record = output["reviewer_report"].get("phase_assessment")
                        elif output_id == "assess-recovery-roadmap-brief":
                            record = output["report"].get("assessment")
                        else:
                            record = output.get("phase_assessment") or output.get("assessment")
                        if not isinstance(record, dict) or record.get("reviewer") != role:
                            raise AssertionError(f"producer output lacks {role} {milestone} assessment")
                        if (record.get("feature_directory") != feature
                                or record.get("scope_sha256") != snapshot["scope_sha256"]
                                or record.get("kind") != "independent-phase-assessment"):
                            raise ValueError(f"producer assessment has stale scope or identity: {output_id}")
                        for artifact_path, artifact_digest in record.get("artifact_digests", {}).items():
                            artifact_file = recovery_case.root / artifact_path
                            if (not artifact_file.is_file()
                                    or owner_module.sha(artifact_file) != artifact_digest):
                                raise ValueError(f"producer assessment has stale artifact: {artifact_path}")
                            snapshot["source_map"][artifact_path] = artifact_digest
                        record_path = f"{feature}/validation/phase-lifecycle/{milestone}-{role.lower().replace(' ', '-').replace('-', '')}.json"
                        record_file = recovery_case.root / record_path
                        record_file.parent.mkdir(parents=True, exist_ok=True)
                        record_file.write_text(json.dumps(record, sort_keys=True), encoding="utf-8")
                        record_digest = owner_module.sha(record_file)
                        snapshot["source_map"][record_path] = record_digest
                        assessments.append({"path": record_path, "sha256": record_digest,
                                            "kind": record["kind"]})
                        artifacts.update(record["artifact_digests"])
                    group = {"milestone": milestone,
                        "owning_phase": self.module.OWNERS[milestone],
                        "assessments": assessments,
                        "required_check_ids": sorted(self.module.CHECKS[milestone]),
                        "satisfied_check_ids": sorted(self.module.CHECKS[milestone]),
                        "unresolved_ids": [], "artifact_digests": artifacts,
                        "historical_activity": [],
                        "pending_future_ids": snapshot["pending_future_ids"]}
                    if history:
                        attestation_output = selected_outputs["attest-recovery-start"]
                        attestation_record = attestation_output["attestation"]
                        attestation_path = attestation_output["path"]
                        attestation_file = recovery_case.root / attestation_path
                        attestation_file.write_text(json.dumps(attestation_record, sort_keys=True), encoding="utf-8")
                        attestation_digest = owner_module.sha(attestation_file)
                        snapshot["source_map"][attestation_path] = attestation_digest
                        group["historical_activity"] = [{"path": attestation_path,
                            "sha256": attestation_digest, "kind": attestation_record["kind"]}]
                    return group
                if mode == "recovery":
                    milestone_entries.append(group_for("specced", [
                        ("assess-recovery-preparation", "FlowKit-Reviewer"),
                        ("assess-recovery-roadmap-brief", "FlowKit-Roadmap Agent")]))
                    milestone_entries.append(group_for("in-progress", [
                        ("assess-recovery-preparation", "FlowKit-Reviewer"),
                        ("assess-recovery-readiness", "FlowKit-Readiness Checker")], history=True))
                milestone_entries.append(group_for("implemented", [
                    ("assess-implemented-lifecycle-milestone", "FlowKit-Code Reviewer")]))
                request_packet = {"schema_version": "1.0", "action": "prepare", "phase": "closeout",
                    "feature_directory": feature, "entry_id": snapshot["entry_id"],
                    "run_id": snapshot["run_id"], "workflow_id": snapshot["workflow_id"],
                    "workflow_version": snapshot["workflow_version"], "mode": mode,
                    "decision_reference": recovery_request["decision_reference"],
                    "milestone_evidence": milestone_entries, "snapshot": snapshot}
                return request_packet

            first_packet = build_final_request("recovery", "planned")
            flow_outputs["prepare-closeout-lifecycle-request"] = {"request": first_packet,
                "request_path": recovery_case.production_callback_output["request_path"],
                "role_fixture": "main request derived from five producer outputs and retained snapshot"}
            main_prompt = controller.render_template(
                find(graph_document["steps"], "prepare-closeout-lifecycle-request")["prompt"],
                route_inputs, flow_outputs)
            self.assertIn("assess-recovery-roadmap-brief", main_prompt)
            self.assertIn("assess-recovery-preparation", main_prompt)
            self.assertIn("record-recovery-preparation", main_prompt)
            self.assertIn("assess-recovery-readiness", main_prompt)
            self.assertIn("attest-recovery-start", main_prompt)
            recovery_request = first_packet
            recovery_case.production_callback_output["request"] = recovery_request
            request_path = recovery_case.root / recovery_case.production_callback_output["request_path"]
            request_path.write_text(json.dumps(recovery_request, sort_keys=True) + "\n", encoding="utf-8")
            prepared_packet = self.module.prepare(recovery_case.root, recovery_request)
            self.assertEqual("ready", prepared_packet.get("state"), prepared_packet)
            changed_scope = copy.deepcopy(recovery_request)
            changed_scope["snapshot"]["scope_sha256"] = "0" * 64
            self.assertEqual("blocked", self.module.prepare(recovery_case.root, changed_scope).get("state"))

            missing_outputs = copy.deepcopy(flow_outputs)
            missing_outputs.pop("assess-recovery-readiness")
            with self.assertRaisesRegex(ValueError, "missing producer outputs"):
                build_final_request("recovery", "planned", missing_outputs)

            wrong_role_outputs = copy.deepcopy(flow_outputs)
            wrong_role_outputs["assess-recovery-readiness"]["reviewer"] = "FlowKit-Reviewer"
            with self.assertRaisesRegex(ValueError, "producer role or current input binding"):
                build_final_request("recovery", "planned", wrong_role_outputs)

            changed_recorder_output = copy.deepcopy(flow_outputs)
            changed_recorder_output["record-recovery-preparation"]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "recorder output is missing or stale"):
                build_final_request("recovery", "planned", changed_recorder_output)

            stale_brief_output = copy.deepcopy(flow_outputs)
            stale_brief_output["assess-recovery-roadmap-brief"]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "roadmap brief producer output is missing or stale"):
                build_final_request("recovery", "planned", stale_brief_output)

            stale_scope_outputs = copy.deepcopy(flow_outputs)
            stale_scope_outputs["assess-recovery-preparation"]["reviewer_report"][
                "reviewed_inputs"][f"{feature}/spec.md"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "producer role or current input binding"):
                build_final_request("recovery", "planned", stale_scope_outputs)

            fabricated_outputs = copy.deepcopy(flow_outputs)
            fabricated_outputs["attest-recovery-start"]["attestation"]["child_id"] = "self-asserted-child"
            fabricated_outputs["attest-recovery-start"]["attestation"]["recorded_dispatch"][
                "child_id"] = "self-asserted-child"
            fabricated_packet = build_final_request("recovery", "planned", fabricated_outputs)
            fabricated_result = self.module.prepare(recovery_case.root, fabricated_packet)
            self.assertEqual("blocked", fabricated_result.get("state"), fabricated_result)

            expected_edges = [("planned", "specced"), ("specced", "in-progress"),
                              ("in-progress", "implemented")]
            for expected_from, expected_to in expected_edges:
                with self.subTest(recovery_edge=(expected_from, expected_to)):
                    edge_mode = "normal" if expected_from == "in-progress" else "recovery"
                    evidence_route = find(graph_document["steps"], "route-closeout-recovery-evidence")
                    selected_evidence = controller.select_switch_branch(evidence_route, edge_mode)
                    expected_evidence = [] if edge_mode == "normal" else [
                        "assess-recovery-roadmap-brief", "assess-recovery-preparation",
                        "record-recovery-preparation", "assess-recovery-readiness", "attest-recovery-start"]
                    self.assertEqual(expected_evidence, [node["id"] for node in selected_evidence])
                    self.assertEqual(edge_mode, "normal" if expected_from == "in-progress" else "recovery")
                    if expected_from == "specced":
                        missing_attestation = copy.deepcopy(recovery_request)
                        in_progress = next(group for group in missing_attestation["milestone_evidence"]
                                           if group["milestone"] == "in-progress")
                        in_progress["historical_activity"] = []
                        missing_result = self.module.prepare(recovery_case.root, missing_attestation)
                        self.assertEqual("blocked", missing_result.get("state"), missing_result)
                    recovery_request = build_final_request(edge_mode, expected_from)
                    flow_outputs["prepare-closeout-lifecycle-request"] = {
                        "request": recovery_request,
                        "request_path": recovery_case.production_callback_output["request_path"],
                        "role_fixture": "main request from current mode and returned producer outputs"}
                    route_inputs["feature_context"] = feature
                    main_prompt = controller.render_template(
                        find(graph_document["steps"], "prepare-closeout-lifecycle-request")["prompt"],
                        route_inputs, flow_outputs)
                    if edge_mode == "recovery":
                        self.assertEqual(receipt["sha256"], recovery_request["snapshot"]["source_map"][receipt["path"]])
                        self.assertEqual(history_ref["sha256"], recovery_request["snapshot"]["source_map"][history_ref["path"]])
                        self.assertEqual(readiness_proof["dispatch_witness"]["sha256"],
                            recovery_request["snapshot"]["source_map"][readiness_proof["dispatch_witness"]["path"]])
                    else:
                        self.assertEqual([], selected_evidence)
                        self.assertEqual(["implemented"], [group["milestone"] for group in
                            recovery_request["milestone_evidence"]])
                        self.assertEqual([], recovery_request["milestone_evidence"][0]["historical_activity"])
                        static_required = {".specify/memory/constitution.md", f"{feature}/spec.md",
                            f"{feature}/plan.md", f"{feature}/tasks.md", ".specify/feature.json",
                            ".specify/flow-kit/manifest.yml", ".specify/flow-kit/skills-install.json",
                            ".specify/bundle-records.json", ".specify/extensions/flow-roadmap/extension.yml",
                            ".specify/extensions/flow-roadmap/scripts/python/load_config.py",
                            ".specify/extensions/flow-roadmap/scripts/python/review_contract.py",
                            ".specify/extensions/flow-roadmap/scripts/python/phase_lifecycle.py",
                            ".specify/workflows/speckit-flow-closeout/workflow.yml",
                            ".specify/memory/roadmap.md", recovery_request["decision_reference"]}
                        self.assertTrue(static_required.issubset(recovery_request["snapshot"]["source_map"]),
                            sorted(static_required - recovery_request["snapshot"]["source_map"].keys()))
                    recovery_case.production_callback_output["request"] = recovery_request
                    request_path.write_text(json.dumps(recovery_request, sort_keys=True) + "\n", encoding="utf-8")
                    result = execute_ready_production_route(
                        recovery_case, recovery_request, graph_document, "closeout",
                        mutate_run_summary=True)
                    self.assertEqual("ready", result["adapter"].get("state"), result["adapter"])
                    self.assertEqual("ready", result["revalidated"].get("state"), result["revalidated"])
                    self.assertEqual(expected_to, result["owner_receipt"]["to_status"])
                    self.assertEqual(expected_from, result["owner_receipt"]["from_status"])
                    self.assertEqual("verified", result["verification"]["state"])
                    self.assertIn("rendered_revalidation", result)
                    self.assertIn("rendered_apply", result)
                    self.assertIn("rendered_verify", result)
                    main_snapshot["source_map"][".specify/memory/roadmap.md"] = owner_module.sha(recovery_case.roadmap)
            final_status = owner_module.phase.entries(recovery_case.roadmap.read_text(encoding="utf-8"))["901"]["status"]
            self.assertEqual("implemented", final_status)
            self.assertEqual(3, recovery_case.roadmap.read_text(encoding="utf-8").count("<!-- flow-roadmap-lifecycle "))
            # Re-enter at the achieved Close Out ceiling. The owner must return
            # an event-free no-op; the adapter must preserve the current bytes.
            before_noop = owner_module.sha(recovery_case.roadmap)
            recovery_request = build_final_request("normal", "implemented")
            no_op = self.module.prepare(recovery_case.root, recovery_request)
            self.assertEqual("no-op", no_op.get("state"), no_op)
            self.assertEqual("implemented", no_op["retained_status"])
            self.assertEqual(before_noop, owner_module.sha(recovery_case.roadmap))
            self.assertEqual(3, recovery_case.roadmap.read_text(encoding="utf-8").count("<!-- flow-roadmap-lifecycle "))
        finally:
            recovery_case.doCleanups()

        # This local production-graph case checks that implemented is followed by
        # the existing separate verified gate. It complements, rather than
        # substitutes for, owner receipt assertions above.
        if "LC015" in expected_ids:
            from tests.test_workflow_paths import WorkflowPathTests, find_step, load_workflow
            graph_test = WorkflowPathTests("testLifecycleMilestonesGateSpecifyImplementAndCloseoutEffects")
            case_result = unittest.TestResult()
            graph_test.run(case_result)
            details = [str(item[1]) for item in case_result.errors + case_result.failures]
            self.assertTrue(case_result.wasSuccessful(), f"LC015 verified-gate graph check failed: {details}")
            graph_test = WorkflowPathTests("testCloseoutSharedMaintenanceRequiresVerificationAndCleanLintBeforeReview")
            WorkflowPathTests.setUpClass()
            graph_test.setUp()
            try:
                closeout = load_workflow("speckit-flow-closeout")
                gate = find_step(closeout["steps"], "approve-roadmap-transition")
                route = find_step(closeout["steps"], "route-roadmap-transition")
                verification_cases = fixture["operator_resolution_cases"]["LC015"]
                self.assertEqual(verification_cases["gate_options"], gate["options"])
                for choice_case in verification_cases["choices"]:
                    explicit_choice = choice_case["value"]
                    selected = graph_test.controller.validate_gate_choice(gate, explicit_choice)
                    branch = graph_test.controller.select_switch_branch(route, selected)
                    self.assertEqual(choice_case["expected_step_ids"], [item["id"] for item in branch], explicit_choice)
            finally:
                graph_test.doCleanups()

        # Validate the focused question/answer boundary with explicit fixture
        # choices. This is a deterministic routing check, not an inferred answer.
        from tests.test_controller import load_module as load_controller_module
        controller_path = ROOT / "controllers/flow-kit/scripts/python/controller.py"
        controller_module = load_controller_module("flowkit_lifecycle_matrix_controller", controller_path)
        question_case = fixture["operator_resolution_cases"]["LC012"]
        question = question_case["question"]
        self.assertEqual("resolve-phase-lifecycle-conflict",
                         controller_module.validate_child_question(question, "resolve-phase-lifecycle-conflict")["step_id"])
        for answer_case in question_case["answers"]:
            resolved = controller_module.resolve_child_answer(
                question, answer_case["value"], question_case["same_child_id"], question_case["same_child_id"])
            self.assertEqual(answer_case["expected"], resolved["answer"])
        with self.assertRaisesRegex(ValueError, "same child"):
            controller_module.resolve_child_answer(question, "1", question_case["same_child_id"], "different-child")

        report_output = os.environ.get("SPEC_KIT_FLOW_LIFECYCLE_CASE_REPORT")
        if report_output:
            report_path = Path(report_output)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(json.dumps({"cases": actual_case_results,
                "canonical_recovery_dispatch": canonical_dispatch,
                "production_route_observations": observations}, indent=2, sort_keys=True) + "\n",
                encoding="utf-8")

if __name__ == "__main__":
    unittest.main()

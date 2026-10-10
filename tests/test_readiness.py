"""Tests for the deterministic, read-only FlowKit readiness report."""

from __future__ import annotations

import hashlib
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
import shutil
import subprocess
import sys
from unittest.mock import patch


ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "controllers/flow-kit/scripts/python/readiness.py"
SPEC = "specs/fixture/spec.md"
PLAN = "specs/fixture/plan.md"
TASKS = "specs/fixture/tasks.md"
CHECKLIST = "specs/fixture/checklists/requirements.md"


def load_module():
    spec = importlib.util.spec_from_file_location("flowkit_readiness_under_test", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        feature = self.root / "specs/fixture"
        (feature / "checklists").mkdir(parents=True)
        (feature / "validation").mkdir()
        (self.root / ".specify").mkdir()
        (self.root / ".specify/feature.json").write_text(json.dumps({"feature_directory": "specs/fixture"}))
        (self.root / SPEC).write_text("spec\n")
        (self.root / PLAN).write_text("plan\n")
        (self.root / TASKS).write_text("tasks\n")
        (self.root / CHECKLIST).write_text("# Checklist\n- [x] Quality criterion\n- [ ] Review criterion\n")
        self.readiness = load_module()

    def add_current_review(self) -> None:
        paths = [SPEC, PLAN, TASKS, CHECKLIST]
        record = {
            "schema_version": "1.0",
            "state": "complete",
            "reviewer": "FlowKit-Reviewer",
            "reviewer_verdict_sha256": "a" * 64,
            "reviewed_inputs": {path: digest(self.root / path) for path in paths},
        }
        target = self.root / "specs/fixture/validation/readiness-review.json"
        target.write_text(json.dumps(record, sort_keys=True))

    def test_assess_blocksUncheckedItemsAndMissingIndependentReview(self) -> None:
        report = self.readiness.assess(self.root, "specs/fixture")
        self.assertEqual("blocked", report["state"])
        self.assertIn("independent-review-missing", report["blocking_ids"])
        self.assertEqual("unchecked", report["criteria"][1]["marker"])
        self.assertEqual(report["criteria"][1]["id"], report["criteria"][1]["finding_id"])
        self.assertEqual("specifier", report["criteria"][0]["owner"])

    def test_assessScansAllChecklistFileTypesAndRejectsBareCoreMarkers(self) -> None:
        custom = self.root / "specs/fixture/checklists/custom.txt"
        custom.write_text("- [ ] Required review\n")
        report = self.readiness.assess(self.root, "specs/fixture")
        self.assertEqual("blocked", report["state"])
        self.assertIn("Required review", [item["source_item"] for item in report["criteria"]])
        custom.write_text("- [x] Required review\n")
        (self.root / CHECKLIST).write_text("- [x] Good\n- [ ]\n")
        report = self.readiness.assess(self.root, "specs/fixture")
        self.assertEqual("readiness-checklist-item-malformed", report["reason_code"])

    def test_assessBlocksEveryCoreMarkerThatCannotBeParsedAsAWholeChecklistLine(self) -> None:
        malformed_lines = ("- [ ]No separator", "prefix - [ ] Required", "text - [x] Required")
        for line in malformed_lines:
            with self.subTest(line=line):
                (self.root / CHECKLIST).write_text(f"- [x] Good\n{line}\n")
                report = self.readiness.assess(self.root, "specs/fixture")
                self.assertEqual("blocked", report["state"])
                self.assertEqual("readiness-checklist-item-malformed", report["reason_code"])

    def test_assessRejectsAdditionalCoreMarkersEvenWhenLeadingItemParses(self) -> None:
        malformed_lines = (
            "- [x] Good - [ ] hidden",
            "- [ ] Review - [x] embedded checked marker",
            "- [x] Good - [X] second checked marker",
        )
        for line in malformed_lines:
            with self.subTest(line=line):
                (self.root / CHECKLIST).write_text(f"- [x] Good\n{line}\n")
                report = self.readiness.assess(self.root, "specs/fixture")
                self.assertEqual("blocked", report["state"])
                self.assertEqual("readiness-checklist-item-malformed", report["reason_code"])

    def test_installedControllerBlocksNoSeparatorAndPrefixedCoreMarkers(self) -> None:
        package = self.root / ".specify/flow-kit/scripts/python"
        package.mkdir(parents=True)
        for filename in ("controller.py", "readiness.py", "selection.py"):
            source = ROOT / "controllers/flow-kit/scripts/python" / filename
            if source.exists():
                shutil.copy2(source, package / filename)
        command = [sys.executable, str(package / "controller.py"), "readiness", "--project", str(self.root)]
        for line in ("- [ ]No separator", "prefix - [ ] Required"):
            with self.subTest(line=line):
                (self.root / CHECKLIST).write_text(f"- [x] Good\n{line}\n")
                result = subprocess.run(command, input=json.dumps({"feature_directory": "specs/fixture"}),
                                        text=True, capture_output=True, check=False)
                self.assertEqual(0, result.returncode, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual("blocked", report["state"])
                self.assertIn("readiness-checklist-item-malformed", report["blocking_ids"])

    def test_installedControllerBlocksParsedLineWithHiddenUncheckedMarker(self) -> None:
        package = self.root / ".specify/flow-kit/scripts/python"
        package.mkdir(parents=True)
        for filename in ("controller.py", "readiness.py", "selection.py"):
            source = ROOT / "controllers/flow-kit/scripts/python" / filename
            if source.exists():
                shutil.copy2(source, package / filename)
        command = [sys.executable, str(package / "controller.py"), "readiness", "--project", str(self.root)]
        (self.root / CHECKLIST).write_text("- [x] Good - [ ] hidden\n")
        result = subprocess.run(command, input=json.dumps({"feature_directory": "specs/fixture"}),
                                text=True, capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual("blocked", report["state"])
        self.assertIn("readiness-checklist-item-malformed", report["blocking_ids"])

    def test_persistedReviewRejectsAuthorEvenWithCurrentDigestsAndCompleteState(self) -> None:
        checklist = self.root / CHECKLIST
        checklist.write_text(checklist.read_text().replace("[ ]", "[x]"))
        self.add_current_review()
        review_path = self.root / "specs/fixture/validation/readiness-review.json"
        review = json.loads(review_path.read_text())
        review["reviewer"] = "FlowKit-Specifier"
        review_path.write_text(json.dumps(review, sort_keys=True))
        report = self.readiness.assess(self.root, "specs/fixture")
        self.assertEqual("blocked", report["state"])
        self.assertIn("independent-review-missing", report["blocking_ids"])

    def test_completePreparationSidecarSurvivesCompoundReviewerRelocation(self) -> None:
        report = self.readiness.assess(self.root, "specs/fixture")
        current, future = report["criteria"]
        prep_path = self.root / "specs/fixture/validation/preparation.json"
        original_classification = {
            "id": future["id"], "category": "human-acceptance", "owner": "operator",
            "due_phase": "acceptance", "expected_evidence": "recorded operator verdict",
            "source_path": CHECKLIST, "source_item": future["source_item"],
        }
        prep_path.write_text(json.dumps({
            "schema_version": "1.0", "feature_directory": "specs/fixture",
            "criteria": [
                {"id": current["id"], "category": "preparation-quality", "owner": "reviewer"},
                original_classification,
            ],
        }, sort_keys=True))
        paths = [SPEC, PLAN, TASKS, CHECKLIST]
        verdict = {"reviewer": "FlowKit-Reviewer", "state": "complete", "findings": [],
                   "reviewed_inputs": {path: digest(self.root / path) for path in paths},
                   "future_classifications": [original_classification]}
        result = self.readiness.record_review(self.root, "specs/fixture", verdict)
        self.assertIn("specs/fixture/validation/preparation.json", result["updated_paths"])
        saved = json.loads(prep_path.read_text())
        self.assertEqual([current["id"]], [item["id"] for item in saved["criteria"]])
        self.assertEqual(future["id"], saved["relocations"][0]["classification"]["id"])
        fresh = self.readiness.assess(self.root, "specs/fixture")
        self.assertEqual("ready", fresh["state"])
        self.assertEqual([future["id"]], fresh["pending_future_ids"])
        self.assertEqual([current["id"]], [item["id"] for item in fresh["criteria"]])

    def test_duplicateTextRelocationBlocksBeforeMutationAndKeepsIdsAcrossReassessment(self) -> None:
        (self.root / CHECKLIST).write_text("# Checklist\n- [ ] Same obligation\n- [x] Same obligation\n")
        first, second = self.readiness.assess(self.root, "specs/fixture")["criteria"]
        self.assertNotEqual(first["id"], second["id"])
        before = (self.root / CHECKLIST).read_bytes()
        classification = {"id": first["id"], "source_path": CHECKLIST, "source_item": first["source_item"],
                          "category": "human-acceptance", "owner": "operator", "due_phase": "acceptance",
                          "expected_evidence": "decision"}
        paths = [SPEC, PLAN, TASKS, CHECKLIST]
        verdict = {"reviewer": "FlowKit-Reviewer", "state": "complete", "findings": [],
                   "reviewed_inputs": {path: digest(self.root / path) for path in paths},
                   "future_classifications": [classification]}
        with self.assertRaisesRegex(self.readiness.ReadinessError, "duplicate-text-ambiguous"):
            self.readiness.record_review(self.root, "specs/fixture", verdict)
        self.assertEqual(before, (self.root / CHECKLIST).read_bytes())
        self.assertFalse((self.root / "specs/fixture/validation/future-obligations.json").exists())
        again = self.readiness.assess(self.root, "specs/fixture")["criteria"]
        self.assertEqual([first["id"], second["id"]], [item["id"] for item in again])

    def test_nonregularReviewDestinationBlocksCompoundRelocationBeforeAnyWrite(self) -> None:
        checklist = self.root / CHECKLIST
        before = checklist.read_bytes()
        criterion = self.readiness.assess(self.root, "specs/fixture")["criteria"][1]
        classification = {"id": criterion["id"], "source_path": CHECKLIST, "source_item": criterion["source_item"],
                          "category": "human-acceptance", "owner": "operator", "due_phase": "acceptance",
                          "expected_evidence": "decision"}
        paths = [SPEC, PLAN, TASKS, CHECKLIST]
        verdict = {"reviewer": "FlowKit-Reviewer", "state": "complete", "findings": [],
                   "reviewed_inputs": {path: digest(self.root / path) for path in paths},
                   "future_classifications": [classification]}
        review_destination = self.root / "specs/fixture/validation/readiness-review.json"
        review_destination.mkdir()
        with self.assertRaisesRegex(self.readiness.ReadinessError, "destination-not-regular"):
            self.readiness.record_review(self.root, "specs/fixture", verdict)
        self.assertEqual(before, checklist.read_bytes())
        self.assertFalse((self.root / "specs/fixture/validation/future-obligations.json").exists())

    def test_nonregularLedgerOrClassificationDestinationBlocksBeforeAnyWrite(self) -> None:
        for relative in ("specs/fixture/validation/future-obligations.json",
                         "specs/fixture/validation/preparation.json"):
            with self.subTest(destination=relative):
                checklist = self.root / CHECKLIST
                before = checklist.read_bytes()
                criterion = self.readiness.assess(self.root, "specs/fixture")["criteria"][1]
                classification = {"id": criterion["id"], "source_path": CHECKLIST,
                                  "source_item": criterion["source_item"], "category": "human-acceptance",
                                  "owner": "operator", "due_phase": "acceptance", "expected_evidence": "decision"}
                paths = [SPEC, PLAN, TASKS, CHECKLIST]
                verdict = {"reviewer": "FlowKit-Reviewer", "state": "complete", "findings": [],
                           "reviewed_inputs": {path: digest(self.root / path) for path in paths},
                           "future_classifications": [classification]}
                target = self.root / relative
                if target.exists():
                    if target.is_dir():
                        target.rmdir()
                    else:
                        target.unlink()
                target.mkdir()
                with self.assertRaises(self.readiness.ReadinessError):
                    self.readiness.record_review(self.root, "specs/fixture", verdict)
                self.assertEqual(before, checklist.read_bytes())
                self.assertFalse((self.root / "specs/fixture/validation/readiness-review.json").exists())
                self.assertFalse((self.root / "specs/fixture/validation/future-obligations.json").is_file())
                target.rmdir()

    def test_readyReportRequiresFreshIndependentEvidenceAndPreservesFutureItems(self) -> None:
        checklist = self.root / CHECKLIST
        checklist.write_text(checklist.read_text().replace("[ ]", "[x]"))
        self.add_current_review()
        obligations = {
            "schema_version": "1.0",
            "feature_directory": "specs/fixture",
            "obligations": [{
                "id": "acceptance-1", "source_path": CHECKLIST,
                "source_item": "Future user acceptance", "source_item_sha256": "a" * 64,
                "source_file_sha256_before": "b" * 64, "source_file_sha256_after": "c" * 64,
                "owner": "operator", "due_phase": "acceptance", "expected_evidence": "recorded decision",
                "status": "pending", "recorded_by": "main-task-recorder",
            }],
        }
        path = self.root / "specs/fixture/validation/future-obligations.json"
        path.write_text(json.dumps(obligations))
        report = self.readiness.assess(self.root, "specs/fixture")
        self.assertEqual("ready", report["state"])
        self.assertEqual(["acceptance-1"], report["pending_future_ids"])
        self.assertEqual("pending", report["pending_future_obligations"][0]["status"])
        self.assertEqual(0, len(report["blocking_ids"]))

    def test_staleIndependentReviewAndIncompleteClassificationBlock(self) -> None:
        checklist = self.root / CHECKLIST
        checklist.write_text(checklist.read_text().replace("[ ]", "[x]"))
        self.add_current_review()
        checklist.write_text(checklist.read_text() + "\n")
        report = self.readiness.assess(self.root, "specs/fixture")
        self.assertEqual("blocked", report["state"])
        self.assertEqual("stale", report["independent_review"]["state"])
        self.assertIn("independent-review-missing", report["blocking_ids"])
        prep = self.root / "specs/fixture/validation/preparation.json"
        prep.write_text(json.dumps({"schema_version": "1.0", "feature_directory": "specs/fixture", "criteria": []}))
        report = self.readiness.assess(self.root, "specs/fixture")
        self.assertIn("criterion-coverage-incomplete", report["blocking_ids"])

    def test_fakeFutureCompletionAndUnknownOwnerClassBlock(self) -> None:
        checklist = self.root / CHECKLIST
        checklist.write_text(checklist.read_text().replace("[ ]", "[x]"))
        self.add_current_review()
        criteria = self.readiness.assess(self.root, "specs/fixture")["criteria"]
        prep = self.root / "specs/fixture/validation/preparation.json"
        prep.write_text(json.dumps({
            "schema_version": "1.0", "feature_directory": "specs/fixture",
            "criteria": [{"id": item["id"], "category": "human-acceptance", "owner": "operator"}
                         for item in criteria],
        }))
        report = self.readiness.assess(self.root, "specs/fixture")
        self.assertIn("future-obligation-not-relocated", report["blocking_ids"])
        data = json.loads(prep.read_text())
        data["criteria"][0]["owner"] = ""
        prep.write_text(json.dumps(data))
        report = self.readiness.assess(self.root, "specs/fixture")
        self.assertIn("readiness-classification-invalid", report["blocking_ids"])

    def test_activeIdentityAndSymlinkPathsBlockBeforeChecklistRead(self) -> None:
        report = self.readiness.assess(self.root, "specs/other")
        self.assertEqual("readiness-feature-identity-mismatch", report["reason_code"])
        neighbor = self.root / "specs/neighbor"
        (neighbor / "checklists").mkdir(parents=True)
        (neighbor / "checklists/secret.md").write_text("- [x] Neighbor\n")
        feature = self.root / "specs/fixture"
        (feature / "checklists").rename(feature / "checklists-original")
        (feature / "checklists").symlink_to(neighbor / "checklists", target_is_directory=True)
        report = self.readiness.assess(self.root, "specs/fixture")
        self.assertEqual("readiness-path-symlink", report["reason_code"])

    def test_futureLedgerRejectsCheckedStatusAndDuplicateIdentity(self) -> None:
        obligations = self.root / "specs/fixture/validation/future-obligations.json"
        entry = {
            "id": "future-1", "source_path": CHECKLIST, "source_item": "future",
            "source_item_sha256": "a" * 64, "source_file_sha256_before": "b" * 64,
            "source_file_sha256_after": "c" * 64, "owner": "operator", "due_phase": "acceptance",
            "expected_evidence": "decision", "status": "complete", "recorded_by": "main-task-recorder",
        }
        obligations.write_text(json.dumps({"schema_version": "1.0", "feature_directory": "specs/fixture", "obligations": [entry, entry]}))
        report = self.readiness.assess(self.root, "specs/fixture")
        self.assertIn("future-obligation-record-invalid", report["blocking_ids"])

    def test_recorderPersistsOnlyExactFreshReviewerVerdict(self) -> None:
        paths = [SPEC, PLAN, TASKS, CHECKLIST]
        verdict = {"reviewer": "FlowKit-Reviewer", "state": "complete", "findings": [],
                   "reviewed_inputs": {path: digest(self.root / path) for path in paths}}
        with self.assertRaisesRegex(self.readiness.ReadinessError, "invalid-or-stale"):
            self.readiness.record_review(self.root, "specs/fixture", {**verdict, "reviewer": "FlowKit-Coder"})
        self.assertFalse((self.root / "specs/fixture/validation/readiness-review.json").exists())
        self.readiness.record_review(self.root, "specs/fixture", verdict)
        report = self.readiness.assess(self.root, "specs/fixture")
        self.assertEqual("complete", report["independent_review"]["state"])
        (self.root / TASKS).write_text("changed tasks\n")
        report = self.readiness.assess(self.root, "specs/fixture")
        self.assertEqual("stale", report["independent_review"]["state"])
        self.assertIn("independent-review-missing", report["blocking_ids"])

    def test_taskStatusOnlyChangesPreserveCurrentReviewAcrossCoderAndTaskerReentry(self) -> None:
        (self.root / TASKS).write_text("# Tasks\n- [ ] T001 Implement route\n- [x] T002 Existing behavior\n")
        paths = [SPEC, PLAN, TASKS, CHECKLIST]
        verdict = {"reviewer": "FlowKit-Reviewer", "state": "complete", "findings": [],
                   "reviewed_inputs": {path: digest(self.root / path) for path in paths}}
        self.readiness.record_review(self.root, "specs/fixture", verdict)

        tasks = self.root / TASKS
        tasks.write_text(tasks.read_text().replace("[ ] T001", "[x] T001"))
        report = self.readiness.assess(self.root, "specs/fixture")
        self.assertEqual("complete", report["independent_review"]["state"])
        self.assertEqual(verdict["reviewed_inputs"][TASKS],
                         report["independent_review"]["task_status_delta"]["original_sha256"])
        self.assertEqual(digest(tasks), report["independent_review"]["task_status_delta"]["current_sha256"])
        self.assertEqual(["T001"], report["independent_review"]["task_status_delta"]["changed_task_ids"])

        # A Tasker may reopen the same task after a bounded iteration without
        # changing its reviewed wording or inventing a new readiness review.
        tasks.write_text(tasks.read_text().replace("[x] T001", "[ ] T001"))
        report = self.readiness.assess(self.root, "specs/fixture")
        self.assertEqual("complete", report["independent_review"]["state"])

    def test_taskDescriptionChangeStalesReviewEvenWhenTaskMarkerIsTheOnlyStatusDelta(self) -> None:
        (self.root / TASKS).write_text("# Tasks\n- [ ] T001 Implement route\n")
        paths = [SPEC, PLAN, TASKS, CHECKLIST]
        verdict = {"reviewer": "FlowKit-Reviewer", "state": "complete", "findings": [],
                   "reviewed_inputs": {path: digest(self.root / path) for path in paths}}
        self.readiness.record_review(self.root, "specs/fixture", verdict)
        tasks = self.root / TASKS
        tasks.write_text(tasks.read_text().replace("Implement route", "Implement different route").replace("[ ]", "[x]"))
        report = self.readiness.assess(self.root, "specs/fixture")
        self.assertEqual("stale", report["independent_review"]["state"])

    def test_recorderRelocatesOnlyReviewerClassifiedUncheckedItemAndPreservesPendingIdentity(self) -> None:
        report = self.readiness.assess(self.root, "specs/fixture")
        source_criterion = report["criteria"][1]
        classification = {
            "id": source_criterion["id"], "source_path": CHECKLIST,
            "source_item": source_criterion["source_item"],
            "category": "human-acceptance", "owner": "operator",
            "due_phase": "acceptance", "expected_evidence": "recorded operator verdict",
        }
        paths = [SPEC, PLAN, TASKS, CHECKLIST]
        verdict = {"reviewer": "FlowKit-Reviewer", "state": "complete", "findings": [],
                   "reviewed_inputs": {path: digest(self.root / path) for path in paths},
                   "future_classifications": [classification]}
        result = self.readiness.record_review(self.root, "specs/fixture", verdict)
        self.assertEqual("recorded", result["state"])
        self.assertNotIn("Review criterion", (self.root / CHECKLIST).read_text())
        ledger = json.loads((self.root / "specs/fixture/validation/future-obligations.json").read_text())
        self.assertEqual(source_criterion["id"], ledger["obligations"][0]["id"])
        self.assertEqual("Review criterion", ledger["obligations"][0]["source_item"])
        self.assertEqual("pending", ledger["obligations"][0]["status"])
        self.assertEqual("operator", ledger["obligations"][0]["owner"])
        self.assertEqual(64, len(ledger["obligations"][0]["source_file_sha256_before"]))
        self.assertEqual(64, len(ledger["obligations"][0]["source_file_sha256_after"]))
        readiness = self.readiness.assess(self.root, "specs/fixture")
        self.assertIn(source_criterion["id"], readiness["pending_future_ids"])
        self.assertEqual("ready", readiness["state"])

    def test_compoundRecordWriteFailuresRollbackEveryBoundaryAndAllowExactRetry(self) -> None:
        report = self.readiness.assess(self.root, "specs/fixture")
        current, future = report["criteria"]
        classification = {
            "id": future["id"], "source_path": CHECKLIST, "source_item": future["source_item"],
            "category": "human-acceptance", "owner": "operator", "due_phase": "acceptance",
            "expected_evidence": "recorded operator verdict",
        }
        (self.root / "specs/fixture/validation/preparation.json").write_text(json.dumps({
            "schema_version": "1.0", "feature_directory": "specs/fixture",
            "criteria": [
                {"id": current["id"], "category": "preparation-quality", "owner": "reviewer"},
                classification,
            ],
        }, sort_keys=True))
        ledger_path = self.root / "specs/fixture/validation/future-obligations.json"
        unrelated = {
            "id": "existing-pending", "source_path": CHECKLIST, "source_item": "Unrelated future work",
            "source_item_sha256": "a" * 64, "source_file_sha256_before": "b" * 64,
            "source_file_sha256_after": "c" * 64, "owner": "operator", "due_phase": "acceptance",
            "expected_evidence": "decision", "status": "pending", "recorded_by": "main-task-recorder",
        }
        ledger_path.write_text(json.dumps({"schema_version": "1.0", "feature_directory": "specs/fixture",
                                           "obligations": [unrelated]}, sort_keys=True))
        review_path = self.root / "specs/fixture/validation/readiness-review.json"
        review_path.write_text("prior review bytes\n")
        targets = [ledger_path, self.root / "specs/fixture/validation/preparation.json", review_path,
                   self.root / CHECKLIST]
        before = {path: path.read_bytes() for path in targets}
        paths = [SPEC, PLAN, TASKS, CHECKLIST]
        verdict = {"reviewer": "FlowKit-Reviewer", "state": "complete", "findings": [],
                   "reviewed_inputs": {path: digest(self.root / path) for path in paths},
                   "future_classifications": [classification]}
        original_write = self.readiness._atomic_write

        for boundary in range(1, len(targets) + 1):
            for after_effect in (False, True):
                with self.subTest(boundary=boundary, after_effect=after_effect):
                    for path, data in before.items():
                        path.write_bytes(data)
                    calls = 0

                    def fail_once(path: Path, data: bytes) -> None:
                        nonlocal calls
                        calls += 1
                        if calls == boundary:
                            if after_effect:
                                original_write(path, data)
                            raise OSError("injected compound write failure")
                        original_write(path, data)

                    with patch.object(self.readiness, "_atomic_write", side_effect=fail_once):
                        with self.assertRaisesRegex(self.readiness.ReadinessError, "write-rolled-back"):
                            self.readiness.record_review(self.root, "specs/fixture", verdict)
                    self.assertEqual(before, {path: path.read_bytes() for path in targets})
                    fresh = self.readiness.assess(self.root, "specs/fixture")
                    self.assertEqual("blocked", fresh["state"])
                    retried = self.readiness.record_review(self.root, "specs/fixture", verdict)
                    self.assertEqual("recorded", retried["state"])
                    ready = self.readiness.assess(self.root, "specs/fixture")
                    self.assertEqual("ready", ready["state"])
                    self.assertEqual(["existing-pending", future["id"]], ready["pending_future_ids"])
                    saved_ledger = json.loads(ledger_path.read_text())
                    self.assertEqual(["existing-pending", future["id"]],
                                     [item["id"] for item in saved_ledger["obligations"]])
                    # Reset to exact fixture state for the next injected boundary.
                    for path, data in before.items():
                        path.write_bytes(data)

    def test_compoundRecordRollbackPreservesConcurrentOutputAndReportsRecoveryPath(self) -> None:
        report = self.readiness.assess(self.root, "specs/fixture")
        future = report["criteria"][1]
        classification = {"id": future["id"], "source_path": CHECKLIST, "source_item": future["source_item"],
                          "category": "human-acceptance", "owner": "operator", "due_phase": "acceptance",
                          "expected_evidence": "recorded operator verdict"}
        paths = [SPEC, PLAN, TASKS, CHECKLIST]
        verdict = {"reviewer": "FlowKit-Reviewer", "state": "complete", "findings": [],
                   "reviewed_inputs": {path: digest(self.root / path) for path in paths},
                   "future_classifications": [classification]}
        ledger_path = self.root / "specs/fixture/validation/future-obligations.json"
        concurrent_bytes = b'{"operator_edit":"preserve"}\n'
        original_write = self.readiness._atomic_write
        calls = 0

        def concurrent_edit_then_fail(path: Path, data: bytes) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                ledger_path.write_bytes(concurrent_bytes)
                raise OSError("injected failure after concurrent edit")
            original_write(path, data)

        with patch.object(self.readiness, "_atomic_write", side_effect=concurrent_edit_then_fail):
            with self.assertRaisesRegex(self.readiness.ReadinessError, "recovery-required") as error:
                self.readiness.record_review(self.root, "specs/fixture", verdict)
        self.assertEqual(concurrent_bytes, ledger_path.read_bytes())
        self.assertIn("specs/fixture/validation/future-obligations.json", str(error.exception))
        self.assertFalse((self.root / "specs/fixture/validation/readiness-review.json").exists())
        self.assertEqual("blocked", self.readiness.assess(self.root, "specs/fixture")["state"])

    def test_copiedControllerReturnsRollbackBlockThenSupportsExactRetryAndFreshReadyAssessment(self) -> None:
        report = self.readiness.assess(self.root, "specs/fixture")
        future = report["criteria"][1]
        classification = {"id": future["id"], "source_path": CHECKLIST, "source_item": future["source_item"],
                          "category": "human-acceptance", "owner": "operator", "due_phase": "acceptance",
                          "expected_evidence": "recorded operator verdict"}
        paths = [SPEC, PLAN, TASKS, CHECKLIST]
        verdict = {"reviewer": "FlowKit-Reviewer", "state": "complete", "findings": [],
                   "reviewed_inputs": {path: digest(self.root / path) for path in paths},
                   "future_classifications": [classification]}
        source_before = (self.root / CHECKLIST).read_bytes()
        package = self.root / ".specify/flow-kit/scripts/python"
        package.mkdir(parents=True)
        for filename in ("controller.py", "readiness.py", "selection.py"):
            source = ROOT / "controllers/flow-kit/scripts/python" / filename
            if source.exists():
                shutil.copy2(source, package / filename)
        readiness_spec = importlib.util.spec_from_file_location("readiness", package / "readiness.py")
        self.assertIsNotNone(readiness_spec)
        copied_readiness = importlib.util.module_from_spec(readiness_spec)
        prior_readiness = sys.modules.get("readiness")
        sys.modules["readiness"] = copied_readiness
        readiness_spec.loader.exec_module(copied_readiness)
        controller_spec = importlib.util.spec_from_file_location("copied_flowkit_controller", package / "controller.py")
        self.assertIsNotNone(controller_spec)
        copied_controller = importlib.util.module_from_spec(controller_spec)
        sys.modules["copied_flowkit_controller"] = copied_controller
        controller_spec.loader.exec_module(copied_controller)
        try:
            request = {"action": "record-review", "feature_directory": "specs/fixture", "reviewer_report": verdict}
            before_io_output = io.StringIO()
            with patch.object(copied_controller, "record_readiness_review",
                              side_effect=copied_readiness.ReadinessError("readiness-review-verdict-stale")):
                with patch("sys.stdin", io.StringIO(json.dumps(request))), contextlib.redirect_stdout(before_io_output):
                    self.assertEqual(2, copied_controller.main(["readiness", "--project", str(self.root)]))
            before_io = json.loads(before_io_output.getvalue())
            self.assertEqual("blocked", before_io["state"])
            self.assertEqual("readiness-review-verdict-stale", before_io["reason_code"])
            self.assertEqual("repair-readiness-inputs-and-rerun-analysis", before_io["resume_action"])

            original_write = copied_readiness._atomic_write
            calls = 0

            def fail_second_write(path: Path, data: bytes) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected failure after future ledger write")
                original_write(path, data)

            output = io.StringIO()
            with patch.object(copied_readiness, "_atomic_write", side_effect=fail_second_write):
                with patch("sys.stdin", io.StringIO(json.dumps(request))), contextlib.redirect_stdout(output):
                    self.assertEqual(2, copied_controller.main(["readiness", "--project", str(self.root)]))
            blocked = json.loads(output.getvalue())
            self.assertEqual("blocked", blocked["state"])
            self.assertEqual("readiness-record-write-rolled-back", blocked["reason_code"])
            self.assertEqual("rerun-the-same-current-review-verdict-after-a-fresh-assessment",
                             blocked["resume_action"])
            self.assertEqual(source_before, (self.root / CHECKLIST).read_bytes())
            self.assertFalse((self.root / "specs/fixture/validation/future-obligations.json").exists())
        finally:
            sys.modules.pop("readiness", None)
            sys.modules.pop("copied_flowkit_controller", None)
            if prior_readiness is not None:
                sys.modules["readiness"] = prior_readiness

        command = [sys.executable, str(package / "controller.py"), "readiness", "--project", str(self.root)]
        blocked_assessment = subprocess.run(command, input=json.dumps({"feature_directory": "specs/fixture"}),
                                            text=True, capture_output=True, check=False)
        self.assertEqual(0, blocked_assessment.returncode, blocked_assessment.stderr)
        self.assertEqual("blocked", json.loads(blocked_assessment.stdout)["state"])
        recorded = subprocess.run(command, input=json.dumps(request), text=True, capture_output=True, check=False)
        self.assertEqual(0, recorded.returncode, recorded.stderr)
        self.assertEqual("recorded", json.loads(recorded.stdout)["state"])
        assessed = subprocess.run(command, input=json.dumps({"feature_directory": "specs/fixture"}),
                                  text=True, capture_output=True, check=False)
        self.assertEqual(0, assessed.returncode, assessed.stderr)
        fresh = json.loads(assessed.stdout)
        self.assertEqual("ready", fresh["state"])
        self.assertEqual([future["id"]], fresh["pending_future_ids"])

    def testNonObjectReviewPayloadsFailBothInstalledEntryPointsBeforeEffect(self) -> None:
        package = self.root / ".specify/flow-kit/scripts/python"
        package.mkdir(parents=True)
        for source in (ROOT / "controllers/flow-kit/scripts/python").glob("*.py"):
            shutil.copy2(source, package / source.name)
        feature = self.root / "specs/fixture"
        before = {str(p.relative_to(feature)): p.read_bytes() for p in feature.rglob("*") if p.is_file()}
        for verdict in (None, [], "not a review", False, 0):
            commands = [
                ([sys.executable, str(package / "readiness.py"), "record-review", "--project", str(self.root),
                  "--feature-directory", "specs/fixture"], verdict),
                ([sys.executable, str(package / "controller.py"), "readiness", "--project", str(self.root)],
                 {"action": "record-review", "feature_directory": "specs/fixture", "reviewer_report": verdict}),
            ]
            reports = []
            for command, payload in commands:
                with self.subTest(verdict=verdict, entrypoint=Path(command[1]).name):
                    result = subprocess.run(command, input=json.dumps(payload), text=True, capture_output=True)
                    self.assertEqual(2, result.returncode, result.stderr)
                    self.assertNotIn("Traceback", result.stderr)
                    report = json.loads(result.stdout)
                    self.assertEqual("blocked", report["state"])
                    self.assertEqual("readiness-review-payload-invalid", report["reason_code"])
                    self.assertEqual([report["reason_code"]], report["blocking_ids"])
                    self.assertEqual("provide-a-current-independent-review-object", report["resume_action"])
                    self.assertEqual("1.0", report["schema_version"])
                    self.assertEqual([], report["criteria"])
                    self.assertEqual([], report["source_evidence"])
                    reports.append(report)
                    self.assertEqual(before, {str(p.relative_to(feature)): p.read_bytes()
                                             for p in feature.rglob("*") if p.is_file()})
            self.assertEqual(reports[0], reports[1])

    def testRecorderRejectsNonObjectPayloadBeforeAccessingProject(self) -> None:
        for verdict in (None, [], "not a review", False, 0):
            with self.subTest(verdict=verdict):
                with self.assertRaisesRegex(self.readiness.ReadinessError, "readiness-review-payload-invalid"):
                    self.readiness.record_review(self.root / "absent-project", "specs/fixture", verdict)

    def testReadinessCliReturnsNonzeroStructuredRecorderFailureButZeroForBlockedAssessment(self) -> None:
        assessment_output = io.StringIO()
        with patch("sys.stdout", assessment_output):
            self.assertEqual(0, self.readiness.main(["assess", "--project", str(self.root),
                                                     "--feature-directory", "specs/fixture"]))
        self.assertEqual("blocked", json.loads(assessment_output.getvalue())["state"])

        request = {"reviewer": "FlowKit-Reviewer", "state": "complete", "findings": [],
                   "reviewed_inputs": {path: digest(self.root / path)
                                       for path in (SPEC, PLAN, TASKS, CHECKLIST)}}
        output = io.StringIO()
        with patch("sys.stdin", io.StringIO(json.dumps(request))), patch("sys.stdout", output):
            with patch.object(self.readiness, "record_review",
                              side_effect=self.readiness.ReadinessError("readiness-record-write-rolled-back")):
                self.assertEqual(2, self.readiness.main(["record-review", "--project", str(self.root),
                                                         "--feature-directory", "specs/fixture"]))
        blocked = json.loads(output.getvalue())
        self.assertEqual("blocked", blocked["state"])
        self.assertEqual("readiness-record-write-rolled-back", blocked["reason_code"])
        self.assertEqual("rerun-the-same-current-review-verdict-after-a-fresh-assessment",
                         blocked["resume_action"])

    def test_recorderRefusesRelocationWhenReviewerEvidenceIsStaleOrItemIsAlreadyChecked(self) -> None:
        report = self.readiness.assess(self.root, "specs/fixture")
        item = report["criteria"][1]
        classification = {"id": item["id"], "source_path": CHECKLIST, "source_item": item["source_item"],
                          "category": "implementation-evidence", "owner": "implementation",
                          "due_phase": "implementation", "expected_evidence": "test result"}
        paths = [SPEC, PLAN, TASKS, CHECKLIST]
        verdict = {"reviewer": "FlowKit-Reviewer", "state": "complete", "findings": [],
                   "reviewed_inputs": {path: digest(self.root / path) for path in paths},
                   "future_classifications": [classification]}
        result = self.readiness.record_review(self.root, "specs/fixture", verdict)
        self.assertEqual("recorded", result["state"])
        self.assertNotIn("Review criterion", (self.root / CHECKLIST).read_text())
        (self.root / TASKS).write_text("now stale\n")
        with self.assertRaisesRegex(self.readiness.ReadinessError, "invalid-or-stale"):
            self.readiness.record_review(self.root, "specs/fixture", verdict)
        self.assertNotIn("Review criterion", (self.root / CHECKLIST).read_text())

    def test_mainRecorderChecksOnlyCurrentReviewerSatisfiedCustomMarkerAndRetainsOriginalHashes(self) -> None:
        requirement_path = self.root / CHECKLIST
        requirement_path.write_text(requirement_path.read_text().replace("[ ]", "[x]"))
        custom_path = "specs/fixture/checklists/review.md"
        (self.root / custom_path).write_text("# Reviewer checklist\n- [ ] CHK001 Reviewed requirement\n")
        before = {path: digest(self.root / path) for path in (SPEC, PLAN, TASKS, CHECKLIST, custom_path)}
        custom_criteria, _ = self.readiness._items([(custom_path, (self.root / custom_path).read_bytes())])
        verdict = {"reviewer": "FlowKit-Reviewer", "state": "complete", "findings": [],
                   "reviewed_inputs": before, "satisfied_criteria": [custom_criteria[0]["id"]]}
        result = self.readiness.record_review(self.root, "specs/fixture", verdict)
        self.assertIn(custom_path, result["updated_paths"])
        saved = json.loads((self.root / "specs/fixture/validation/readiness-review.json").read_text())
        self.assertEqual(before, saved["reviewed_inputs"])
        self.assertEqual(before[custom_path], saved["reconciliations"][0]["source_file_sha256_before"])
        self.assertEqual("- [x] CHK001 Reviewed requirement\n", (self.root / custom_path).read_text().splitlines(keepends=True)[1])
        report = self.readiness.assess(self.root, "specs/fixture")
        self.assertEqual("ready", report["state"])
        self.assertEqual(before[custom_path], report["independent_review"]["reviewed_inputs"][custom_path])

    def test_installedConsumerControllerCommandAssessesAndRecordsExactReviewerEvidence(self) -> None:
        package = self.root / ".specify/flow-kit/scripts/python"
        package.mkdir(parents=True)
        for filename in ("controller.py", "readiness.py", "selection.py"):
            source = ROOT / "controllers/flow-kit/scripts/python" / filename
            if source.exists():
                shutil.copy2(source, package / filename)
        checklist = self.root / CHECKLIST
        checklist.write_text(checklist.read_text().replace("[ ]", "[x]"))
        report_inputs = {path: digest(self.root / path) for path in (SPEC, PLAN, TASKS, CHECKLIST)}
        reviewer_report = {"reviewer": "FlowKit-Reviewer", "state": "complete", "findings": [],
                           "reviewed_inputs": report_inputs}
        command = [sys.executable, str(package / "controller.py"), "readiness", "--project", str(self.root)]
        assessed = subprocess.run(command, input=json.dumps({"feature_directory": "specs/fixture",
                                                              "reviewer_report": reviewer_report}),
                                  text=True, capture_output=True, check=False)
        self.assertEqual(0, assessed.returncode, assessed.stderr)
        self.assertEqual("ready", json.loads(assessed.stdout)["state"])
        recorded = subprocess.run(command, input=json.dumps({"action": "record-review",
                                                              "feature_directory": "specs/fixture",
                                                              "reviewer_report": reviewer_report}),
                                  text=True, capture_output=True, check=False)
        self.assertEqual(0, recorded.returncode, recorded.stderr)
        self.assertEqual("recorded", json.loads(recorded.stdout)["state"])
        persisted = subprocess.run(command, input=json.dumps({"feature_directory": "specs/fixture"}),
                                   text=True, capture_output=True, check=False)
        self.assertEqual(0, persisted.returncode, persisted.stderr)
        self.assertEqual("ready", json.loads(persisted.stdout)["state"])
        review_path = self.root / "specs/fixture/validation/readiness-review.json"
        persisted_review = json.loads(review_path.read_text())
        persisted_review["reviewer"] = "FlowKit-Specifier"
        review_path.write_text(json.dumps(persisted_review))
        rejected = subprocess.run(command, input=json.dumps({"feature_directory": "specs/fixture"}),
                                  text=True, capture_output=True, check=False)
        self.assertEqual(0, rejected.returncode, rejected.stderr)
        self.assertEqual("blocked", json.loads(rejected.stdout)["state"])
        self.assertIn("independent-review-missing", json.loads(rejected.stdout)["blocking_ids"])


if __name__ == "__main__":
    unittest.main()

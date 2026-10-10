"""Unit tests for portable workflow-feedback capture and report export."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts/python/workflow_feedback.py"
SPEC = importlib.util.spec_from_file_location("workflow_feedback", MODULE_PATH)
workflow_feedback = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(workflow_feedback)


def observation() -> dict:
    """Return a valid non-sensitive feedback observation."""
    return {
        "observation_id": "feedback-001",
        "observed_at": "2026-09-21T12:00:00Z",
        "component": {
            "id": "farmboy-converge",
            "version": "0.1.0",
            "digest": "sha256:" + "a" * 64,
        },
        "integration": "codex",
        "consumer_project_ref": "consumer-project",
        "execution_profile": {"role": "worker", "capability": "standard"},
        "expected_behavior": "Prompt is clear.",
        "observed_behavior": "Terminal prompt needs clarification.",
        "safety_response": "Stopped and used the manual fallback.",
        "manual_fallback_status": "used",
        "evidence_references": ["validation/convergence-dogfood.md"],
        "suggested_change_target": "workflow-source",
        "reporter_disposition": "observed",
    }


class WorkflowFeedbackTests(unittest.TestCase):
    """Unit tests for workflow feedback capture and report output."""

    def test_captureAndExport_expectedPortableReport_whenObservationIsValid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "observation.json"
            journal = root / "state/observations.jsonl"
            report_json = root / "report.json"
            report_markdown = root / "report.md"
            source.write_text(json.dumps(observation()), encoding="utf-8")

            captured = workflow_feedback.capture(source, journal)
            exported = workflow_feedback.report(journal, report_json, report_markdown, "consumer-project", "2026-09-21T12:10:00Z", "report-001")

            report = json.loads(report_json.read_text(encoding="utf-8"))
            self.assertEqual("captured", captured["status"])
            self.assertEqual("exported", exported["status"])
            self.assertEqual("report-001", report["report_id"])
            self.assertEqual(exported["integrity_digest"], report["integrity_digest"])
            projection = report_markdown.read_text(encoding="utf-8")
            self.assertIn("feedback-001", projection)
            self.assertIn(report["report_id"], projection)
            self.assertIn(report["observations"][0]["component"]["digest"], projection)
            self.assertIn(report["observations"][0]["evidence_references"][0], projection)

    def test_capture_rejectsAbsolutePath_whenObservationContainsHostPath(self):
        invalid = observation()
        invalid["evidence_references"] = ["/private/report.txt"]
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "observation.json"
            source.write_text(json.dumps(invalid), encoding="utf-8")
            with self.assertRaisesRegex(workflow_feedback.FeedbackValidationError, "absolute host path"):
                workflow_feedback.capture(source, Path(directory) / "journal.jsonl")

    def test_capture_rejectsEmbeddedHostPath_withoutWritingJournal(self):
        for text in ("Location:/Users/pegagio/report.txt", "See (/private/tmp/report.txt)", "file:///private/tmp/report.txt"):
            with self.subTest(text=text), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                invalid = observation()
                invalid["observed_behavior"] = text
                source = root / "observation.json"
                journal = root / "journal.jsonl"
                source.write_text(json.dumps(invalid), encoding="utf-8")
                with self.assertRaisesRegex(workflow_feedback.FeedbackValidationError, "absolute host path"):
                    workflow_feedback.capture(source, journal)
                self.assertFalse(journal.exists())

    def test_capture_allowsRelativeReferenceAndHttpsUrl(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            valid = observation()
            valid["evidence_references"] = ["validation/convergence-dogfood.md", "https://example.org/evidence/report"]
            source = root / "observation.json"
            source.write_text(json.dumps(valid), encoding="utf-8")
            captured = workflow_feedback.capture(source, root / "journal.jsonl")
            self.assertEqual("captured", captured["status"])

    def test_capture_rejectsDuplicateId_whenJournalAlreadyContainsObservation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "observation.json"
            journal = root / "journal.jsonl"
            source.write_text(json.dumps(observation()), encoding="utf-8")
            workflow_feedback.capture(source, journal)
            with self.assertRaisesRegex(workflow_feedback.FeedbackValidationError, "duplicate observation_id"):
                workflow_feedback.capture(source, journal)


if __name__ == "__main__":
    unittest.main()

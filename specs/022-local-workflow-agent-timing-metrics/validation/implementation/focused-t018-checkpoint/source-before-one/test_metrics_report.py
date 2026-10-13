"""Contract tests for the maintainer-only FarmBoy metrics workbook report."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).parents[1]
REPORT_SCRIPT = ROOT / "skills/farmboy-metrics-report/scripts/metrics_report.py"
EXPECTED_COLUMNS = (
    "invocation_id", "run_id", "project", "skill", "workflow", "step", "invocation_kind",
    "agent", "model", "effort", "started_at", "finished_at", "duration_ms",
)


def load_report_module():
    if not REPORT_SCRIPT.is_file():
        raise AssertionError("T013 report implementation is not present yet")
    spec = importlib.util.spec_from_file_location("farmboy_metrics_report", REPORT_SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load the reviewed metrics report source")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def metric_record(*, invocation_id: str | None = None, **changes):
    record = {
        "schema_version": 1,
        "invocation_id": invocation_id or str(uuid.uuid4()),
        "run_id": "workflow-metrics-id",
        "step_id": "analyze-artifacts",
        "invocation_kind": "execution",
        "agent_name": "FarmBoy Reviewer",
        "skill_id": "farmboy-analyze-remediate",
        "workflow_id": "farmboy-analyze-remediate",
        "project_label": "farmboy",
        "started_at": "2026-10-12T18:00:00.125Z",
        "finished_at": "2026-10-12T18:00:01.625Z",
        "duration_ms": 1500,
        "model": "gpt-6.1-sol",
        "effort": "high",
    }
    record.update(changes)
    return record


class MetricsReportContractTests(unittest.TestCase):
    """Exports preserve the fixed metric contract and source records."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_report_module()

    def write_candidate(self, directory: Path, payload: dict | bytes, *, name: str | None = None) -> Path:
        candidate = directory / (name or f"metric-{uuid.uuid4()}.json")
        candidate.parent.mkdir(parents=True, exist_ok=True)
        raw = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        candidate.write_bytes(raw)
        return candidate

    def export(self, directory: Path) -> dict:
        result = self.report.export_workbook(directory=directory)
        self.assertIsInstance(result, dict)
        self.assertIn("output_path", result)
        self.assertTrue(Path(result["output_path"]).is_file())
        return result

    @staticmethod
    def summary(result: dict) -> dict:
        summary = result.get("summary", result)
        expected = {
            "candidate_count", "accepted_count", "duplicate_count", "conflicting_invocation_count",
            "conflicting_file_count", "invalid_counts", "skipped_count",
        }
        return {key: summary[key] for key in expected}

    def test_exportUsesOneSnapshotAndKeepsSourceBytesUnchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()
            record = metric_record()
            source = self.write_candidate(directory, record)
            before = source.read_bytes()

            result = self.export(directory)

            self.assertEqual(1, self.summary(result)["candidate_count"])
            self.assertEqual(before, source.read_bytes())

    def test_exportMapsTheExactThirteenColumnOrderAndLiteralCells(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()
            self.write_candidate(directory, metric_record(model="=1+1", effort=None, duration_ms=1500))

            result = self.export(directory)

            from openpyxl import load_workbook

            workbook = load_workbook(result["output_path"], data_only=False)
            self.assertEqual(["Metrics"], workbook.sheetnames)
            sheet = workbook["Metrics"]
            self.assertEqual(list(EXPECTED_COLUMNS), [sheet.cell(1, col).value for col in range(1, 14)])
            self.assertEqual("farmboy", sheet["C2"].value)
            self.assertEqual("farmboy-analyze-remediate", sheet["D2"].value)
            self.assertEqual("farmboy-analyze-remediate", sheet["E2"].value)
            self.assertEqual("analyze-artifacts", sheet["F2"].value)
            self.assertEqual("FarmBoy Reviewer", sheet["H2"].value)
            self.assertEqual("=1+1", sheet["I2"].value)
            self.assertIn(sheet["I2"].data_type, {"s", "inlineStr"})
            self.assertIsNone(sheet["J2"].value)
            self.assertEqual(1500, sheet["M2"].value)
            self.assertEqual("n", sheet["M2"].data_type)
            self.assertNotIn("schema_version", [sheet.cell(1, col).value for col in range(1, 14)])
            self.assertEqual(["FarmBoyMetrics"], list(sheet.tables))

    def test_exportZeroRowsCreatesHeaderOnlyTableWithoutFakeRecord(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()

            result = self.export(directory)

            from openpyxl import load_workbook

            workbook = load_workbook(result["output_path"], data_only=False)
            sheet = workbook["Metrics"]
            self.assertEqual(list(EXPECTED_COLUMNS), [sheet.cell(1, col).value for col in range(1, 14)])
            self.assertEqual("A1:M1", sheet.tables["FarmBoyMetrics"].ref)
            self.assertEqual(1, sheet.max_row)

    def test_exportCollapsesIdenticalProjectionAndExcludesEveryConflictingCopy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()
            identity = str(uuid.uuid4())
            original = metric_record(invocation_id=identity)
            copy_with_extra = {**original, "future_field": "ignored"}
            conflict = {**original, "duration_ms": 1600, "finished_at": "2026-10-12T18:00:01.725Z"}
            self.write_candidate(directory, original)
            self.write_candidate(directory, copy_with_extra)
            self.write_candidate(directory, conflict)

            result = self.export(directory)
            summary = self.summary(result)

            self.assertEqual(3, summary["candidate_count"])
            self.assertEqual(0, summary["accepted_count"])
            self.assertEqual(0, summary["duplicate_count"])
            self.assertEqual(1, summary["conflicting_invocation_count"])
            self.assertEqual(3, summary["conflicting_file_count"])
            self.assertEqual(3, summary["skipped_count"])

    def test_exportAcceptsIdenticalProjectedCopiesAndCountsTheExtraAsDuplicate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()
            identity = str(uuid.uuid4())
            original = metric_record(invocation_id=identity)
            copy_with_ignored_field = {**original, "future_field": "not part of the projection"}
            self.write_candidate(directory, original)
            self.write_candidate(directory, copy_with_ignored_field)

            result = self.export(directory)
            summary = self.summary(result)

            self.assertEqual(2, summary["candidate_count"])
            self.assertEqual(1, summary["accepted_count"])
            self.assertEqual(1, summary["duplicate_count"])
            self.assertEqual(0, summary["conflicting_invocation_count"])
            self.assertEqual(0, summary["conflicting_file_count"])
            self.assertEqual(0, summary["skipped_count"])
            from openpyxl import load_workbook

            sheet = load_workbook(result["output_path"], data_only=False)["Metrics"]
            self.assertEqual(identity, sheet["A2"].value)
            self.assertEqual(2, sheet.max_row)

    def test_exportPreservesZeroAndBackwardSignedDurationsAsNumericCells(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()
            zero = metric_record(
                invocation_id=str(uuid.uuid4()),
                started_at="2026-10-12T18:00:00.125Z",
                finished_at="2026-10-12T18:00:00.125Z",
                duration_ms=0,
            )
            backward = metric_record(
                invocation_id=str(uuid.uuid4()),
                started_at="2026-10-12T18:00:02.125Z",
                finished_at="2026-10-12T18:00:01.125Z",
                duration_ms=-1000,
            )
            self.write_candidate(directory, zero)
            self.write_candidate(directory, backward)

            result = self.export(directory)

            from openpyxl import load_workbook

            sheet = load_workbook(result["output_path"], data_only=False)["Metrics"]
            by_id = {sheet[f"A{row}"].value: row for row in (2, 3)}
            zero_duration = sheet[f"M{by_id[zero['invocation_id']]}"]
            backward_duration = sheet[f"M{by_id[backward['invocation_id']]}"]
            self.assertEqual(0, zero_duration.value)
            self.assertEqual("n", zero_duration.data_type)
            self.assertEqual(-1000, backward_duration.value)
            self.assertEqual("n", backward_duration.data_type)

    def test_exportAcceptsLegacyOptionalFieldsAndNormalizesThemToBlankCells(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()
            record = metric_record()
            del record["model"]
            del record["effort"]
            self.write_candidate(directory, record)

            result = self.export(directory)

            from openpyxl import load_workbook

            sheet = load_workbook(result["output_path"], data_only=False)["Metrics"]
            self.assertIsNone(sheet["I2"].value)
            self.assertIsNone(sheet["J2"].value)

    def test_exportCountsMalformedUnsupportedAndInvalidCandidatesOnceEach(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()
            self.write_candidate(directory, b"{bad json}")
            self.write_candidate(directory, metric_record(schema_version=2))
            invalid = metric_record(duration_ms=2)
            self.write_candidate(directory, invalid)
            self.write_candidate(directory, b"x" * 65_537)

            result = self.export(directory)
            summary = self.summary(result)

            self.assertEqual(4, summary["candidate_count"])
            self.assertEqual(0, summary["accepted_count"])
            self.assertEqual(4, summary["skipped_count"])
            self.assertEqual(
                {"malformed-json": 1, "unsupported-schema": 1, "invalid-contract": 1, "oversized": 1},
                summary["invalid_counts"],
            )

    def test_exportClassifiesNonUtf8AndNonObjectJsonCandidatesAsInvalidContractInputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()
            self.write_candidate(directory, b"\xff\xfe")
            self.write_candidate(directory, b"[]")

            result = self.export(directory)
            summary = self.summary(result)

            self.assertEqual(2, summary["candidate_count"])
            self.assertEqual(0, summary["accepted_count"])
            self.assertEqual({"malformed-json": 1, "invalid-contract": 1}, summary["invalid_counts"])

    def test_exportAcceptsCandidateExactlyAtJsonByteLimit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()
            record = metric_record()
            record["future_padding"] = ""
            empty_padding = json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            padding_length = 65_536 - len(empty_padding)
            self.assertGreaterEqual(padding_length, 0)
            record["future_padding"] = "x" * padding_length
            raw = json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            self.assertEqual(65_536, len(raw))
            self.write_candidate(directory, raw)

            result = self.export(directory)
            summary = self.summary(result)

            self.assertEqual(1, summary["candidate_count"])
            self.assertEqual(1, summary["accepted_count"])
            self.assertEqual({}, summary["invalid_counts"])

    def test_exportIgnoresSymlinksDirectoriesTemporaryAndUnrelatedNames(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()
            record = metric_record()
            self.write_candidate(directory, record)
            self.write_candidate(directory, record, name="notes.json")
            (directory / ".metric-pending.tmp").write_text("partial", encoding="utf-8")
            (directory / "subdirectory").mkdir()
            try:
                (directory / f"metric-{uuid.uuid4()}.json").symlink_to(directory / "notes.json")
            except OSError as error:
                self.fail(f"symlink fixture could not be created: {error}")

            result = self.export(directory)

            self.assertEqual(1, self.summary(result)["candidate_count"])
            self.assertEqual(1, self.summary(result)["accepted_count"])

    def test_repeatedReportsUseDistinctOutputsAndPreserveEarlierWorkbook(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()
            self.write_candidate(directory, metric_record())

            first = self.export(directory)
            first_bytes = Path(first["output_path"]).read_bytes()
            second = self.export(directory)

            self.assertNotEqual(first["output_path"], second["output_path"])
            self.assertEqual(first_bytes, Path(first["output_path"]).read_bytes())

    def test_invalidContractsRejectBooleansFractionsDuplicateKeysAndNonfiniteNumbers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()
            samples = [
                json.dumps(metric_record(schema_version=True)).encode(),
                json.dumps(metric_record(duration_ms=1500.5)).encode(),
                json.dumps(metric_record()).replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1').encode(),
                json.dumps(metric_record())[:-1].encode() + b',"future":NaN}',
            ]
            for raw in samples:
                self.write_candidate(directory, raw)

            result = self.export(directory)

            self.assertEqual(4, self.summary(result)["candidate_count"])
            self.assertEqual(0, self.summary(result)["accepted_count"])
            self.assertEqual(4, self.summary(result)["invalid_counts"]["invalid-contract"]
                             + self.summary(result)["invalid_counts"]["malformed-json"])

    def test_invalidContractsRejectMissingWrongTypedAndInvalidTimestampFields(self) -> None:
        invalid_records = []
        required = (
            "schema_version", "invocation_id", "run_id", "step_id", "invocation_kind",
            "agent_name", "skill_id", "workflow_id", "project_label", "started_at",
            "finished_at", "duration_ms",
        )
        for field in required:
            missing = metric_record()
            del missing[field]
            invalid_records.append(missing)
        for field in required[1:11]:
            empty = metric_record()
            empty[field] = ""
            invalid_records.append(empty)
        for field in ("duration_ms",):
            for value in (True, 1.5):
                invalid = metric_record()
                invalid[field] = value
                invalid_records.append(invalid)
        for field in required[1:11]:
            invalid = metric_record()
            invalid[field] = []
            invalid_records.append(invalid)
        invalid_records.extend((
            metric_record(invocation_kind="unknown"),
            metric_record(invocation_kind="probe"),
            metric_record(started_at="2026-10-12T18:00:00Z"),
            metric_record(started_at="2026-10-12T18:00:00.12Z"),
            metric_record(started_at="2026-02-30T18:00:00.125Z"),
            metric_record(finished_at="2026-10-12T18:00:00.1234Z"),
            metric_record(duration_ms=1499),
            metric_record(model=""),
            metric_record(model=17),
            metric_record(effort=False),
            metric_record(effort=[]),
        ))

        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()
            for invalid in invalid_records:
                self.write_candidate(directory, invalid)

            result = self.export(directory)

            summary = self.summary(result)
            self.assertEqual(len(invalid_records), summary["candidate_count"])
            self.assertEqual(0, summary["accepted_count"])
            self.assertEqual(len(invalid_records), summary["invalid_counts"]["invalid-contract"])

    def test_exportClassifiesBooleanAndFractionalSchemaVersionsAsUnsupported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()
            self.write_candidate(directory, metric_record(schema_version=True))
            self.write_candidate(directory, metric_record(schema_version=1.5))

            result = self.export(directory)
            summary = self.summary(result)

            self.assertEqual(2, summary["candidate_count"])
            self.assertEqual(0, summary["accepted_count"])
            self.assertEqual({"unsupported-schema": 2}, summary["invalid_counts"])

    def test_exportExcludesCompletedFileCreatedAfterCandidateSnapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()
            first = self.write_candidate(directory, metric_record())
            late_record = metric_record(invocation_id=str(uuid.uuid4()))
            late = directory / f"metric-{late_record['invocation_id']}.json"
            original_open = Path.open
            created_late = False

            def create_after_snapshot(path: Path, *args, **kwargs):
                nonlocal created_late
                if path == first and not created_late:
                    created_late = True
                    late.write_text(json.dumps(late_record), encoding="utf-8")
                return original_open(path, *args, **kwargs)

            with patch.object(Path, "open", create_after_snapshot):
                result = self.export(directory)

            self.assertTrue(created_late)
            self.assertTrue(late.is_file())
            self.assertEqual(1, self.summary(result)["candidate_count"])
            self.assertEqual(1, self.summary(result)["accepted_count"])

    def test_exportFailsAtInjectedAcceptedRowCapacityBeforePublication(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()
            sources = [self.write_candidate(directory, metric_record()) for _ in range(2)]
            before = {path: path.read_bytes() for path in sources}
            # Lower the production cap at its writer seam to avoid a million fixtures.
            with patch.object(self.report, "MAX_ACCEPTED_ROWS", 1, create=True):
                with self.assertRaises((OSError, ValueError, RuntimeError)):
                    self.report.export_workbook(directory=directory)

            reports = directory / "reports"
            self.assertFalse(reports.exists())
            self.assertEqual(before, {path: path.read_bytes() for path in sources})

    def test_outputWriteFailurePreservesInputsAndEarlierReports(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            reports = directory / "reports"
            reports.mkdir(parents=True)
            source = self.write_candidate(directory, metric_record())
            source_before = source.read_bytes()
            prior = reports / "farmboy-metrics-prior.xlsx"
            prior.write_bytes(b"prior workbook contents")
            prior_before = prior.read_bytes()

            with patch.object(self.report.os, "link", side_effect=PermissionError("fixture output denied")):
                with self.assertRaises((OSError, ValueError, RuntimeError)):
                    self.report.export_workbook(directory=directory)

            self.assertEqual(source_before, source.read_bytes())
            self.assertEqual(prior_before, prior.read_bytes())
            self.assertEqual([prior], list(reports.iterdir()))

    def test_outputNameCollisionFailsWithoutReplacingExistingWorkbook(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            reports = directory / "reports"
            reports.mkdir(parents=True)
            source = self.write_candidate(directory, metric_record())
            source_before = source.read_bytes()
            report_id = uuid.UUID("11111111-2222-4333-8444-555555555555")
            prior = reports / f"farmboy-metrics-{report_id}.xlsx"
            prior.write_bytes(b"preserve this workbook")
            prior_before = prior.read_bytes()

            with patch.object(self.report.uuid, "uuid4", return_value=report_id):
                with self.assertRaises((OSError, ValueError, RuntimeError)):
                    self.report.export_workbook(directory=directory)

            self.assertEqual(prior_before, prior.read_bytes())
            self.assertEqual(source_before, source.read_bytes())
            self.assertEqual([prior], list(reports.iterdir()))

    def test_projectedTextOverExcelLimitOrIllegalXmlIsRejectedWithoutRepair(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            directory.mkdir()
            too_long = metric_record(agent_name="x" * 32_768)
            illegal = metric_record(effort="bad\x00text")
            self.write_candidate(directory, too_long)
            self.write_candidate(directory, illegal)

            result = self.export(directory)

            self.assertEqual(0, self.summary(result)["accepted_count"])
            self.assertEqual(2, self.summary(result)["invalid_counts"]["invalid-contract"])

    def test_missingInputIsEmptyWhileCapacityAndOutputErrorsDoNotClaimSuccess(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            missing = Path(temporary) / "missing"
            result = self.export(missing)
            self.assertEqual(0, self.summary(result)["candidate_count"])
            self.assertEqual(0, self.summary(result)["accepted_count"])

    def copyReportFixture(self, root: Path) -> Path:
        shutil.copytree(
            ROOT / "skills/farmboy-metrics-report",
            root / "skills/farmboy-metrics-report",
        )
        controller = root / "controllers/farmboy/scripts/python"
        controller.mkdir(parents=True)
        shutil.copy2(ROOT / "controllers/farmboy/scripts/python/metrics.py", controller / "metrics.py")
        return root / "skills/farmboy-metrics-report/scripts/metrics_report.py"

    def runReportFixture(self, root: Path, script: Path, *, isolated_imports: bool = False):
        home = root / "home"
        home.mkdir()
        command = [sys.executable]
        if isolated_imports:
            command.append("-S")
        command.append(str(script))
        environment = {**os.environ, "HOME": str(home), "PYTHONPATH": ""}
        return subprocess.run(command, cwd=root, env=environment, text=True, capture_output=True)

    def testReportSourceLayoutFailurePrecedesOutputCreation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "fixture"
            root.mkdir()
            script = self.copyReportFixture(root)
            (root / "controllers/farmboy/scripts/python/metrics.py").unlink()

            result = self.runReportFixture(root, script)

            self.assertNotEqual(0, result.returncode)
            self.assertIn("layout", result.stderr.lower())
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse((root / "home/.farmboy/metrics/reports").exists())

    def testMissingReportDependencyFailsBeforeOutputWithoutInstallingAnything(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "fixture"
            root.mkdir()
            script = self.copyReportFixture(root)
            requirements = root / "skills/farmboy-metrics-report/requirements.txt"
            requirements_before = requirements.read_bytes()

            result = self.runReportFixture(root, script, isolated_imports=True)

            self.assertNotEqual(0, result.returncode)
            self.assertTrue("openpyxl" in result.stderr.lower() or "dependency" in result.stderr.lower())
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse((root / "home/.farmboy/metrics/reports").exists())
            self.assertEqual(requirements_before, requirements.read_bytes())


if __name__ == "__main__":
    unittest.main()

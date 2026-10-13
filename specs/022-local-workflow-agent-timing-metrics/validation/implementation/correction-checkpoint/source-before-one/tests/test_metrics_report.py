"""Contract tests for the maintainer-only FarmBoy metrics workbook report."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
import uuid
from pathlib import Path


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

    def testReportDependencyAndSourceLayoutFailurePrecedeOutputCreation(self) -> None:
        requirements = ROOT / "skills/farmboy-metrics-report/requirements.txt"
        skill = ROOT / "skills/farmboy-metrics-report/SKILL.md"
        if not requirements.exists() or not skill.exists():
            self.fail("T001 maintainer skill layout is not present yet")
        self.assertIn("openpyxl==3.1.5", requirements.read_text(encoding="utf-8"))
        self.assertIn("do not install", skill.read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()

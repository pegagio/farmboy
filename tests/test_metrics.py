"""Contract tests for FarmBoy's local agent timing metric records."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
CONTROLLER_SCRIPTS = ROOT / "controllers/farmboy/scripts/python"
sys.path.insert(0, str(CONTROLLER_SCRIPTS))

from metrics import parse_record_json, validate_record  # noqa: E402


class MetricRecordContractTests(unittest.TestCase):
    """The record validator accepts only the portable version-1 contract."""

    def setUp(self) -> None:
        self.record = {
            "schema_version": 1,
            "invocation_id": "turn-opaque-id",
            "run_id": "workflow-metrics-id",
            "step_id": "analyze-artifacts",
            "invocation_kind": "execution",
            "agent_name": "FarmBoy Reviewer",
            "skill_id": "farmboy-analyze-remediate",
            "workflow_id": "farmboy-analyze-remediate",
            "project_label": "example-project",
            "started_at": "2026-10-12T18:00:00.125Z",
            "finished_at": "2026-10-12T18:00:01.625Z",
            "duration_ms": 1500,
            "model": "gpt-6.1-sol",
            "effort": "high",
        }

    def test_validateRecord_returnsFourteenFieldProjectionWithoutTrimming(self) -> None:
        record = copy.deepcopy(self.record)
        record["agent_name"] = " FarmBoy Reviewer "
        record["model"] = "=1+1"
        record["unknown_future_field"] = "ignored"

        validated = validate_record(record)

        self.assertEqual(" FarmBoy Reviewer ", validated["agent_name"])
        self.assertEqual("=1+1", validated["model"])
        self.assertNotIn("unknown_future_field", validated)
        self.assertEqual(14, len(validated))

    def test_validateRecord_normalizesAbsentOptionalSettingsToNull(self) -> None:
        record = copy.deepcopy(self.record)
        del record["model"]
        del record["effort"]

        validated = validate_record(record)

        self.assertIsNone(validated["model"])
        self.assertIsNone(validated["effort"])

    def test_validateRecord_acceptsNullableOptionalSettings(self) -> None:
        record = copy.deepcopy(self.record)
        record["model"] = None
        record["effort"] = None

        validated = validate_record(record)

        self.assertIsNone(validated["model"])
        self.assertIsNone(validated["effort"])

    def test_validateRecord_rejectsUnsupportedSchemaKindsAndWrongExactTypes(self) -> None:
        cases = [
            ("schema_version", 2),
            ("schema_version", True),
            ("schema_version", 1.0),
            ("invocation_kind", "probe-ish"),
            ("duration_ms", True),
            ("duration_ms", 1500.5),
        ]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                record = copy.deepcopy(self.record)
                record[field] = value
                with self.assertRaises(ValueError):
                    validate_record(record)

    def test_validateRecord_acceptsEveryInvocationKind(self) -> None:
        for kind in ("execution", "continuation", "retry", "probe"):
            with self.subTest(kind=kind):
                record = copy.deepcopy(self.record)
                record["invocation_kind"] = kind
                if kind == "probe":
                    record["step_id"] = "preflight"
                validate_record(record)

    def test_validateRecord_rejectsMissingAndEmptyRequiredFields(self) -> None:
        required = (
            "schema_version",
            "invocation_id",
            "run_id",
            "step_id",
            "invocation_kind",
            "agent_name",
            "skill_id",
            "workflow_id",
            "project_label",
            "started_at",
            "finished_at",
            "duration_ms",
        )
        for field in required:
            with self.subTest(missing=field):
                record = copy.deepcopy(self.record)
                del record[field]
                with self.assertRaises(ValueError):
                    validate_record(record)
        for field in required[1:11]:
            with self.subTest(empty=field):
                record = copy.deepcopy(self.record)
                record[field] = ""
                with self.assertRaises(ValueError):
                    validate_record(record)

    def test_validateRecord_requiresExactStringTypesForIdentityFields(self) -> None:
        string_fields = (
            "invocation_id",
            "run_id",
            "step_id",
            "invocation_kind",
            "agent_name",
            "skill_id",
            "workflow_id",
            "project_label",
            "started_at",
            "finished_at",
        )
        for field in string_fields:
            for value in (None, False, 1, []):
                with self.subTest(field=field, value=value):
                    record = copy.deepcopy(self.record)
                    record[field] = value
                    with self.assertRaises(ValueError):
                        validate_record(record)

    def test_validateRecord_rejectsEmptyOptionalStringsAndInvalidOptionalTypes(self) -> None:
        for field, value in (("model", ""), ("effort", ""), ("model", 1), ("effort", False)):
            with self.subTest(field=field, value=value):
                record = copy.deepcopy(self.record)
                record[field] = value
                with self.assertRaises(ValueError):
                    validate_record(record)

    def test_validateRecord_acceptsEqualAndBackwardWallClockReadings(self) -> None:
        equal = copy.deepcopy(self.record)
        equal["finished_at"] = equal["started_at"]
        equal["duration_ms"] = 0
        self.assertEqual(0, validate_record(equal)["duration_ms"])

        backward = copy.deepcopy(self.record)
        backward["finished_at"] = "2026-10-12T18:00:00.000Z"
        backward["duration_ms"] = -125
        self.assertEqual(-125, validate_record(backward)["duration_ms"])

    def test_validateRecord_rejectsDurationThatDoesNotMatchTimestamps(self) -> None:
        record = copy.deepcopy(self.record)
        record["duration_ms"] = 1499
        with self.assertRaises(ValueError):
            validate_record(record)

    def test_validateRecord_requiresExactMillisecondUtcTimestamps(self) -> None:
        invalid_values = (
            "2026-10-12T18:00:00Z",
            "2026-10-12T18:00:00.12Z",
            "2026-10-12T18:00:00.1234Z",
            "2026-10-12T18:00:00.125+00:00",
            "2026-02-30T18:00:00.125Z",
        )
        for field in ("started_at", "finished_at"):
            for value in invalid_values:
                with self.subTest(field=field, value=value):
                    record = copy.deepcopy(self.record)
                    record[field] = value
                    with self.assertRaises(ValueError):
                        validate_record(record)

    def test_validateRecord_preservesStringsAtExcelCellLimitAndRejectsOverflow(self) -> None:
        record = copy.deepcopy(self.record)
        record["model"] = "x" * 32767
        self.assertEqual(32767, len(validate_record(record)["model"]))

        record["model"] += "x"
        with self.assertRaises(ValueError):
            validate_record(record)

    def test_validateRecord_rejectsIllegalXmlCharactersWithoutRepair(self) -> None:
        for value in ("bad\x00text", "bad\ud800text"):
            with self.subTest(value=repr(value)):
                record = copy.deepcopy(self.record)
                record["effort"] = value
                with self.assertRaises(ValueError):
                    validate_record(record)

    def test_validateRecord_acceptsLegalXmlWhitespaceAndUnicodeLiterally(self) -> None:
        record = copy.deepcopy(self.record)
        record["agent_name"] = "FarmBoy\tReviewer\nCafé 🌾"

        self.assertEqual(record["agent_name"], validate_record(record)["agent_name"])

    def test_parseRecordJson_acceptsMaximumSizeAndRejectsOneByteOver(self) -> None:
        base = json.dumps(self.record, separators=(",", ":")).encode("utf-8")
        prefix = base[:-1] + b',"ignored":"'
        suffix = b'"}'
        exact = prefix + b"x" * (65536 - len(prefix) - len(suffix)) + suffix
        self.assertEqual(65536, len(exact))
        self.assertEqual(self.record["invocation_id"], parse_record_json(exact)["invocation_id"])

        with self.assertRaises(ValueError):
            parse_record_json(exact + b" ")

    def test_parseRecordJson_rejectsDuplicateKeysAndNonFiniteNumbers(self) -> None:
        valid = json.dumps(self.record, separators=(",", ":"))
        duplicate = valid.replace('"schema_version":1', '"schema_version":1,"schema_version":1', 1)
        nonfinite = valid[:-1] + ',"ignored":NaN}'
        for raw in (duplicate, nonfinite):
            with self.subTest(raw=raw[-30:]):
                with self.assertRaises(ValueError):
                    parse_record_json(raw.encode("utf-8"))

    def test_parseRecordJson_requiresUtf8JsonObject(self) -> None:
        for raw in (b"\xff", b"[]", b"null", b"{bad json}"):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    parse_record_json(raw)


if __name__ == "__main__":
    unittest.main()

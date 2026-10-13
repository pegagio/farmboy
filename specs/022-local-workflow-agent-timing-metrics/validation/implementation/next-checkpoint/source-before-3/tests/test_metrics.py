"""Contract tests for FarmBoy's local agent timing metric records."""

from __future__ import annotations

import copy
from concurrent.futures import ThreadPoolExecutor
import errno
import json
import subprocess
import sys
import tempfile
import threading
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).parents[1]
CONTROLLER_SCRIPTS = ROOT / "controllers/farmboy/scripts/python"
sys.path.insert(0, str(CONTROLLER_SCRIPTS))

import metrics  # noqa: E402
from metrics import begin_invocation, finish_invocation, parse_record_json, validate_record  # noqa: E402


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

    def test_beginFinish_coversProbeExecutionContinuationAndRetryWithFreshIds(self) -> None:
        cases = (
            ("probe", "preflight"),
            ("execution", "analyze-artifacts"),
            ("continuation", "analyze-artifacts"),
            ("retry", "analyze-artifacts"),
        )
        records = []
        for index, (kind, step_id) in enumerate(cases):
            with self.subTest(kind=kind):
                metadata = {
                    "run_id": "one-workflow",
                    "step_id": step_id,
                    "invocation_kind": kind,
                    "agent_name": "FarmBoy Reviewer",
                    "skill_id": "farmboy-analyze-remediate",
                    "workflow_id": "farmboy-analyze-remediate",
                    "project_label": "farmboy",
                    "model": "gpt-6.1-sol",
                    "effort": "high",
                }
                token = begin_invocation(metadata, clock_ms=1_800_000_000_000 + index * 1000)
                record = finish_invocation(token, clock_ms=1_800_000_000_250 + index * 1000)
                records.append(record)
        self.assertEqual({"one-workflow"}, {record["run_id"] for record in records})
        self.assertEqual(4, len({record["invocation_id"] for record in records}))
        self.assertEqual([kind for kind, _ in cases], [record["invocation_kind"] for record in records])
        self.assertTrue(all(record["duration_ms"] == 250 for record in records))
        self.assertTrue(all("outcome" not in record for record in records))

    def test_questionClosesTurnAndContinuationExcludesHumanWait(self) -> None:
        metadata = {
            "run_id": "one-workflow",
            "step_id": "create-spec",
            "invocation_kind": "execution",
            "agent_name": "FarmBoy Specifier",
            "skill_id": "farmboy-specify",
            "workflow_id": "farmboy-specify",
            "project_label": "farmboy",
        }
        question_turn = begin_invocation(metadata, clock_ms=1000)
        question_record = finish_invocation(question_turn, clock_ms=1600)

        answer_turn = begin_invocation({**metadata, "invocation_kind": "continuation"}, clock_ms=3_600_000)
        answer_record = finish_invocation(answer_turn, clock_ms=3_600_300)

        self.assertEqual(600, question_record["duration_ms"])
        self.assertEqual(300, answer_record["duration_ms"])
        self.assertNotEqual(question_record["invocation_id"], answer_record["invocation_id"])
        self.assertEqual(question_record["run_id"], answer_record["run_id"])

    def test_pendingPollsKeepOneTurnOpenUntilObservedEnd(self) -> None:
        reads = iter((10_000, 12_500))
        observed_clock_reads = []

        def clock() -> int:
            value = next(reads)
            observed_clock_reads.append(value)
            return value

        metadata = {
            "run_id": "one-workflow",
            "step_id": "review",
            "invocation_kind": "execution",
            "agent_name": "FarmBoy Reviewer",
            "skill_id": "farmboy-converge",
            "workflow_id": "farmboy-converge",
            "project_label": "farmboy",
        }
        token = begin_invocation(metadata, clock_ms=clock)
        # Pending acknowledgements and polls do not sample or close the token.
        poll_observations = ("pending", "running", "pending")
        for _poll in poll_observations:
            self.assertEqual([10_000], observed_clock_reads)
            self.assertEqual(10_000, token["started_ms"])
        record = finish_invocation(token, clock_ms=clock)
        self.assertEqual([10_000, 12_500], observed_clock_reads)
        self.assertEqual(2500, record["duration_ms"])

    def test_observedDispatchRejectionStillProducesTimingWithoutResultClassification(self) -> None:
        metadata = {
            "run_id": "one-workflow",
            "step_id": "preflight",
            "invocation_kind": "probe",
            "agent_name": "FarmBoy Reviewer",
            "skill_id": "farmboy-analyze-remediate",
            "workflow_id": "farmboy-analyze-remediate",
            "project_label": "farmboy",
        }
        token = begin_invocation(metadata, clock_ms=50)
        # Rejection is the observed end of the request; result prose is not recorded.
        record = finish_invocation(token, clock_ms=75)
        self.assertEqual(25, record["duration_ms"])
        self.assertNotIn("outcome", record)
        self.assertNotIn("status", record)

    def testMissingObservedEndDoesNotInventCompletedRecord(self) -> None:
        token = begin_invocation(
            {
                "run_id": "one-workflow",
                "step_id": "review",
                "invocation_kind": "execution",
                "agent_name": "FarmBoy Reviewer",
                "skill_id": "farmboy-converge",
                "workflow_id": "farmboy-converge",
                "project_label": "farmboy",
            },
            clock_ms=10,
        )
        self.assertNotIn("finished_at", token)
        self.assertNotIn("duration_ms", token)

    def testBeginRejectsUnhashableInvocationKindsAsBoundedValueErrors(self) -> None:
        metadata = {
            "run_id": "one-workflow",
            "step_id": "review",
            "invocation_kind": "execution",
            "agent_name": "FarmBoy Reviewer",
            "skill_id": "farmboy-converge",
            "workflow_id": "farmboy-converge",
            "project_label": "farmboy",
        }
        for invalid_kind in ([], {}):
            with self.subTest(kind=invalid_kind):
                with self.assertRaisesRegex(ValueError, "invocation_kind"):
                    begin_invocation({**metadata, "invocation_kind": invalid_kind}, clock_ms=10)

    def testCliRejectsUnhashableInvocationKindsWithoutTracebackOrHostPath(self) -> None:
        metadata = {
            "run_id": "one-workflow",
            "step_id": "review",
            "invocation_kind": "execution",
            "agent_name": "FarmBoy Reviewer",
            "skill_id": "farmboy-converge",
            "workflow_id": "farmboy-converge",
            "project_label": "farmboy",
        }
        invalid_tokens = (
            ("begin", {**metadata, "invocation_kind": []}),
            ("begin", {**metadata, "invocation_kind": {}}),
            ("finish", {
                **metadata,
                "invocation_kind": [],
                "model": None,
                "effort": None,
                "invocation_id": "turn-opaque-id",
                "started_ms": 1_800_000_000_000,
            }),
        )
        for command, payload in invalid_tokens:
            with self.subTest(command=command, kind=payload["invocation_kind"]):
                result = subprocess.run(
                    [sys.executable, str(CONTROLLER_SCRIPTS / "metrics.py"), command],
                    input=json.dumps(payload), text=True, capture_output=True,
                )
                self.assertEqual(2, result.returncode)
                self.assertIn("invocation_kind", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertNotIn(str(ROOT), result.stderr + result.stdout)
                self.assertEqual("", result.stdout)

    def testBeginAndFinishPropagateUnavailableClockWithoutInventingRecords(self) -> None:
        metadata = {
            "run_id": "one-workflow",
            "step_id": "review",
            "invocation_kind": "execution",
            "agent_name": "FarmBoy Reviewer",
            "skill_id": "farmboy-converge",
            "workflow_id": "farmboy-converge",
            "project_label": "farmboy",
        }

        def unavailable_clock() -> int:
            raise OSError("clock unavailable")

        with self.assertRaisesRegex(OSError, "clock unavailable"):
            begin_invocation(metadata, clock_ms=unavailable_clock)

        token = begin_invocation(metadata, clock_ms=10)
        with self.assertRaisesRegex(OSError, "clock unavailable"):
            finish_invocation(token, clock_ms=unavailable_clock)
        self.assertNotIn("finished_at", token)
        self.assertNotIn("duration_ms", token)

    def testCliSerializesBeginTokenAndFinishedRecordAsJson(self) -> None:
        metadata = {
            "run_id": "one-workflow",
            "step_id": "inspect",
            "invocation_kind": "execution",
            "agent_name": "FarmBoy Coder",
            "skill_id": "farmboy-implement",
            "workflow_id": "farmboy-implement",
            "project_label": "farmboy",
        }
        begin = subprocess.run(
            [sys.executable, str(CONTROLLER_SCRIPTS / "metrics.py"), "begin"],
            input=json.dumps(metadata), text=True, capture_output=True, check=True,
        )
        token = json.loads(begin.stdout)
        self.assertEqual("one-workflow", token["run_id"])
        finish = subprocess.run(
            [sys.executable, str(CONTROLLER_SCRIPTS / "metrics.py"), "finish"],
            input=json.dumps(token), text=True, capture_output=True, check=True,
        )
        record = json.loads(finish.stdout)
        self.assertEqual(14, len(record))
        self.assertEqual(token["invocation_id"], record["invocation_id"])
        self.assertEqual(1, record["schema_version"])
        self.assertEqual(record, validate_record(record))

    def testReadAgentSettingsMatchesTomlNameAndReturnsOnlyExplicitSettings(self) -> None:
        read_settings = getattr(metrics, "read_agent_settings", None)
        self.assertTrue(callable(read_settings), "T007 exact-name TOML reader is not implemented yet")
        with tempfile.TemporaryDirectory() as temporary:
            agents = Path(temporary) / ".codex/agents"
            agents.mkdir(parents=True)
            (agents / "not-the-display-name.toml").write_text(
                'name = "FarmBoy Reviewer"\nmodel = "gpt-6.1-sol"\nmodel_reasoning_effort = "high"\n',
                encoding="utf-8",
            )
            (agents / "unrelated.toml").write_text(
                'name = "FarmBoy Coder"\nmodel = "wrong-agent-model"\n', encoding="utf-8"
            )
            self.assertEqual(
                {"model": "gpt-6.1-sol", "effort": "high"},
                read_settings(Path(temporary), "FarmBoy Reviewer"),
            )

    def testReadAgentSettingsReturnsNullForUnavailableMalformedOrAmbiguousFiles(self) -> None:
        read_settings = getattr(metrics, "read_agent_settings", None)
        self.assertTrue(callable(read_settings), "T007 exact-name TOML reader is not implemented yet")
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.assertEqual({"model": None, "effort": None}, read_settings(project, "Missing Agent"))
            agents = project / ".codex/agents"
            agents.mkdir(parents=True)
            (agents / "malformed.toml").write_text('name = "Broken"\nmodel = [\n', encoding="utf-8")
            self.assertEqual({"model": None, "effort": None}, read_settings(project, "Broken"))
            (agents / "first.toml").write_text('name = "Ambiguous"\nmodel = "one"\n', encoding="utf-8")
            (agents / "second.toml").write_text('name = "Ambiguous"\nmodel = "two"\n', encoding="utf-8")
            self.assertEqual({"model": None, "effort": None}, read_settings(project, "Ambiguous"))

    def testReadAgentSettingsReturnsNullForUnreadableExactNameFile(self) -> None:
        read_settings = getattr(metrics, "read_agent_settings", None)
        self.assertTrue(callable(read_settings), "T007 exact-name TOML reader is not implemented yet")
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            agents = project / ".codex/agents"
            agents.mkdir(parents=True)
            target = agents / "reviewer.toml"
            target.write_text('name = "FarmBoy Reviewer"\nmodel = "gpt-6.1-sol"\n', encoding="utf-8")
            original_open = Path.open

            def open_or_deny(path: Path, *args, **kwargs):
                if path == target:
                    raise PermissionError("fixture denies settings access")
                return original_open(path, *args, **kwargs)

            with patch.object(Path, "open", open_or_deny):
                self.assertEqual(
                    {"model": None, "effort": None},
                    read_settings(project, "FarmBoy Reviewer"),
                )

    def testReadAgentSettingsNormalizesInvalidOrEmptyExplicitSettingsIndividually(self) -> None:
        read_settings = getattr(metrics, "read_agent_settings", None)
        self.assertTrue(callable(read_settings), "T007 exact-name TOML reader is not implemented yet")
        fixtures = (
            ('name = "FarmBoy Reviewer"\nmodel = ""\nmodel_reasoning_effort = "high"\n',
             {"model": None, "effort": "high"}),
            ('name = "FarmBoy Reviewer"\nmodel = 17\nmodel_reasoning_effort = "high"\n',
             {"model": None, "effort": "high"}),
            ('name = "FarmBoy Reviewer"\nmodel = "gpt-6.1-sol"\nmodel_reasoning_effort = []\n',
             {"model": "gpt-6.1-sol", "effort": None}),
            ('name = "FarmBoy Reviewer"\nmodel = "gpt-6.1-sol"\nmodel_reasoning_effort = ""\n',
             {"model": "gpt-6.1-sol", "effort": None}),
            ('name = "FarmBoy Reviewer"\nmodel = "gpt-6.1-sol"\n',
             {"model": "gpt-6.1-sol", "effort": None}),
        )
        for contents, expected in fixtures:
            with self.subTest(contents=contents):
                with tempfile.TemporaryDirectory() as temporary:
                    project = Path(temporary)
                    agents = project / ".codex/agents"
                    agents.mkdir(parents=True)
                    (agents / "agent.toml").write_text(contents, encoding="utf-8")
                    self.assertEqual(expected, read_settings(project, "FarmBoy Reviewer"))

    def testEmitRecordPublishesCompleteUniqueFilesDuringConcurrentWrites(self) -> None:
        emit_record = getattr(metrics, "emit_record", None)
        self.assertTrue(callable(emit_record), "T010 record publication is not implemented yet")
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            records = [
                {**self.record, "invocation_id": str(uuid.uuid4()), "agent_name": f"Agent {index}"}
                for index in range(24)
            ]
            seen_invalid: list[str] = []
            finished = threading.Event()

            def observe_completed_files() -> None:
                while not finished.is_set():
                    for path in directory.glob("metric-*.json") if directory.exists() else ():
                        try:
                            metrics.parse_record_json(path.read_bytes())
                        except (OSError, ValueError):
                            seen_invalid.append(path.name)

            observer = threading.Thread(target=observe_completed_files)
            observer.start()
            try:
                with ThreadPoolExecutor(max_workers=12) as pool:
                    results = list(pool.map(lambda record: emit_record(record, directory=directory), records))
            finally:
                finished.set()
                observer.join(timeout=5)

            self.assertTrue(all(result.get("emitted") is True for result in results), results)
            files = sorted(directory.glob("metric-*.json"))
            self.assertEqual(len(records), len(files))
            self.assertEqual([], seen_invalid)
            published = [metrics.parse_record_json(path.read_bytes()) for path in files]
            self.assertEqual({record["invocation_id"] for record in records},
                             {record["invocation_id"] for record in published})

    def testEmitRecordCollisionAndUnsupportedLinkWarnWithoutReplacingOrLeakingDetails(self) -> None:
        emit_record = getattr(metrics, "emit_record", None)
        self.assertTrue(callable(emit_record), "T010 record publication is not implemented yet")
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "metrics"
            first = {**self.record, "invocation_id": str(uuid.uuid4())}
            published = emit_record(first, directory=directory)
            self.assertTrue(published.get("emitted"), published)
            destination = directory / f"metric-{first['invocation_id']}.json"
            original = destination.read_bytes()

            changed = {**first, "agent_name": "Replacement"}
            collision = emit_record(changed, directory=directory)

            self.assertFalse(collision.get("emitted"), collision)
            self.assertEqual("publication-collision", collision.get("warning_code"))
            self.assertEqual(original, destination.read_bytes())
            self.assertNotIn(temporary, json.dumps(collision))

            unsupported = Path(temporary) / "unsupported"
            with patch.object(metrics.os, "link", side_effect=OSError(errno.EOPNOTSUPP, "link unavailable")):
                result = emit_record({**self.record, "invocation_id": str(uuid.uuid4())}, directory=unsupported)

            self.assertFalse(result.get("emitted"), result)
            self.assertEqual("storage-failed", result.get("warning_code"))
            self.assertNotIn(temporary, json.dumps(result))
            self.assertFalse(list(unsupported.glob("metric-*.json")))
            self.assertFalse(list(unsupported.glob(".metric-*.tmp")))

    def testEmitRecordDestinationFailureReturnsBoundedWarningAndContinues(self) -> None:
        emit_record = getattr(metrics, "emit_record", None)
        self.assertTrue(callable(emit_record), "T010 record publication is not implemented yet")
        with tempfile.TemporaryDirectory() as temporary:
            blocked_parent = Path(temporary) / "not-a-directory"
            blocked_parent.write_text("occupied", encoding="utf-8")
            result = emit_record(self.record, directory=blocked_parent / "metrics")

            self.assertFalse(result.get("emitted"), result)
            self.assertIn(result.get("warning_code"), {
                "destination-unavailable", "storage-failed",
            })
            self.assertNotIn(temporary, json.dumps(result))


if __name__ == "__main__":
    unittest.main()

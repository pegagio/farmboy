"""Regression tests for bound Tasker history and operator-scoped budgets.

The fixture represents deterministic records; labels do not prove human or
native agent identity. The main controller supplies independently retained trust.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from test_implementation_scope import controller, scope, canonical_digest


class HistoricalTaskerEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.feature = "specs/099-controller-test"
        (self.root / self.feature).mkdir(parents=True)
        (self.root / ".specify").mkdir()
        self.tasks_path = self.feature + "/tasks.md"
        self.source_path = self.feature + "/source.py"
        (self.root / ".specify/feature.json").write_text(json.dumps({"feature_directory": self.feature}))
        (self.root / self.feature / "spec.md").write_text("Reviewed fixture\n")
        self.before = "- [ ] T001 Add source coverage\n- [ ] T002 Extend the same source\n"
        self.after = self.before.replace("[ ] T001", "[x] T001")
        (self.root / self.tasks_path).write_text(self.before)
        (self.root / self.source_path).write_text("original\n")
        snapshot = {"schema_version": "1.0", "run_id": "repair-test",
            "feature_directory": self.feature, "request_reference": "direct-fixture-request",
            "request_kind": "full-feature", "requested_task_ids": ["T001", "T002"],
            "task_records": [{"task_id": task, "marker": "unchecked", "description": description,
                              "description_sha256": hashlib.sha256(description.encode()).hexdigest()}
                             for task, description in (("T001", "Add source coverage"), ("T002", "Extend the same source"))],
            "input_digests": {p: self.evidence(p)["sha256"] for p in
                             (".specify/feature.json", self.feature + "/spec.md", self.tasks_path)}}
        snapshot["scope_sha256"] = canonical_digest(snapshot)
        witness = [self.evidence(self.source_path)]
        event = self.tracking_event(self.before, self.after, ["T001"], "0" * 64, witness, snapshot)
        self.binding = {"scope": snapshot, "trusted_request_reference": snapshot["request_reference"],
                        "retained_scope_sha256": snapshot["scope_sha256"], "task_tracking_successors": [event]}
        ready = controller.validate_implementation_scope(self.root, self.binding)
        # The first current validation occurs before either marker/source effect.
        self.assertEqual("blocked", ready["state"])
        (self.root / self.tasks_path).write_text(self.after)
        ready = controller.validate_implementation_scope(self.root, self.binding)
        self.assertEqual("ready", ready["state"])
        self.binding.update({k: ready[k] for k in ("retained_task_tracking_count", "retained_task_tracking_sha256")})
        (self.root / self.source_path).write_text("later authorized change\n")

    def evidence(self, path):
        return {"path": path, "sha256": hashlib.sha256((self.root / path).read_bytes()).hexdigest()}

    def tracking_event(self, before, after, completed, predecessor, witness, snapshot=None):
        snapshot = snapshot or self.binding["scope"]
        event = {"predecessor_event_sha256": predecessor, "scope_sha256": snapshot["scope_sha256"],
            "tasker_assignment": "FarmBoy Tasker", "tasks_before_text": before, "tasks_after_text": after,
            "tasker_result": {"state": "ready", "tasks_before_sha256": hashlib.sha256(before.encode()).hexdigest(),
                "tasks_after_sha256": hashlib.sha256(after.encode()).hexdigest(), "completed_task_ids": completed,
                "evidence": witness},
            "reviewer_result": {"reviewer": "FarmBoy Code Reviewer", "completed_task_ids": completed,
                                "evidence": witness}}
        event["sha256"] = canonical_digest(event)
        return event

    def test_bound_history_survives_later_source_change_without_rewriting(self):
        retained = copy.deepcopy(self.binding)
        self.assertEqual("ready", controller.validate_implementation_scope(self.root, self.binding)["state"])
        self.assertEqual(retained, self.binding)

    def test_unbound_stale_source_and_forged_binding_still_block(self):
        unbound = {k: v for k, v in self.binding.items() if not k.startswith("retained_task_tracking_")}
        self.assertEqual("task-tracking-evidence-stale", controller.validate_implementation_scope(self.root, unbound)["reason_code"])
        for key, value in (("retained_task_tracking_sha256", "0" * 64),
                           ("retained_task_tracking_count", 2), ("retained_task_tracking_count", True)):
            with self.subTest(key=key, value=value):
                bad = {**self.binding, key: value}
                self.assertEqual("historical-task-tracking-binding-invalid",
                                 controller.validate_implementation_scope(self.root, bad)["reason_code"])

    def test_altered_historical_successor_cannot_inherit_original_binding(self):
        bad = copy.deepcopy(self.binding)
        event = bad["task_tracking_successors"][0]
        event["tasker_result"]["evidence"][0]["sha256"] = "f" * 64
        event["sha256"] = canonical_digest({k: v for k, v in event.items() if k != "sha256"})
        self.assertEqual("historical-task-tracking-binding-invalid",
                         controller.validate_implementation_scope(self.root, bad)["reason_code"])

    def test_unicode_tracking_and_budget_bindings_use_canonical_utf8_without_ascii_escaping(self):
        unicode_path = self.feature + "/source-δ.py"
        (self.root / unicode_path).write_text("Unicode historical witness\n")
        payload = {k: copy.deepcopy(v) for k, v in self.binding.items() if not k.startswith("retained_task_tracking_")}
        event = payload["task_tracking_successors"][0]
        event["tasker_result"]["evidence"] = [self.evidence(unicode_path)]
        event["reviewer_result"]["evidence"] = [self.evidence(unicode_path)]
        event["sha256"] = canonical_digest({k: v for k, v in event.items() if k != "sha256"})
        ready = controller.validate_implementation_scope(self.root, payload)
        self.assertEqual("ready", ready["state"])
        expected = canonical_digest({"scope_sha256": payload["scope"]["scope_sha256"],
                                     "task_tracking_successors": payload["task_tracking_successors"]})
        self.assertEqual(expected, ready["retained_task_tracking_sha256"])
        payload.update({k: ready[k] for k in ("retained_task_tracking_count", "retained_task_tracking_sha256")})
        (self.root / unicode_path).write_text("Later change\n")
        self.assertEqual("ready", controller.validate_implementation_scope(self.root, payload)["state"])
        history, path = self.history()
        extension = self.extension(history)
        authority_path = self.feature + "/budget-δ.json"
        (self.root / authority_path).write_text("Explicit deterministic Unicode authority fixture\n")
        extension["budget_extension"]["authority_evidence"] = [self.evidence(authority_path)]
        extension["retained_budget_extension_sha256"] = canonical_digest(extension["budget_extension"])
        self.assertEqual("ready", controller.validate_implementation_scope(self.root, {**self.binding, **extension})["state"])

    def test_new_successor_evidence_is_current_until_its_binding_is_retained(self):
        after = self.after.replace("[ ] T002", "[x] T002")
        event = self.tracking_event(self.after, after, ["T002"], self.binding["task_tracking_successors"][-1]["sha256"],
                                    [self.evidence(self.source_path)])
        payload = {**self.binding, "task_tracking_successors": self.binding["task_tracking_successors"] + [event]}
        (self.root / self.tasks_path).write_text(after)
        result = controller.validate_implementation_scope(self.root, payload)
        self.assertEqual("ready", result["state"])
        (self.root / self.source_path).write_text("another source change\n")
        self.assertEqual("task-tracking-evidence-stale", controller.validate_implementation_scope(self.root, payload)["reason_code"])
        payload.update({k: result[k] for k in ("retained_task_tracking_count", "retained_task_tracking_sha256")})
        self.assertEqual("ready", controller.validate_implementation_scope(self.root, payload)["state"])

    def history(self):
        snapshot = self.binding["scope"]
        history = controller._empty_implementation_history(snapshot)
        for session in range(1, 6):
            for kind in ("coder-session-start", "source-attempt-start", "coder-session-outcome"):
                event = self.execution_event(history, session, kind)
                history = scope.append_execution_event(history, event, scope_sha256=snapshot["scope_sha256"],
                                                       retained_history_sha256=history["sha256"])
        path, _ = controller._implementation_history_path(self.root, snapshot)
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(history))
        return history, path

    def execution_event(self, history, session, kind):
        event = {"event_id": f"event-{len(history['events']) + 1}",
            "predecessor_sha256": history["events"][-1]["sha256"] if history["events"] else "0" * 64,
            "scope_sha256": self.binding["scope"]["scope_sha256"], "event_kind": kind,
            "declared_node_id": "implement-tasks", "occurred_at": "2026-10-13T12:00:00Z",
            "evidence": [self.evidence(self.feature + "/spec.md")], "coder_session_id": f"session-{session}",
            "coder_sessions_started": session,
            "source_attempts_started": session - 1 if kind == "coder-session-start" else session}
        if kind == "coder-session-outcome":
            event["outcome"] = "completed"
        else:
            event["execution_kind"] = "first-source-execution" if session == 1 else "corrective-source-execution"
        event["sha256"] = canonical_digest(event)
        return event

    def extension(self, history):
        authority = self.feature + "/operator-budget.json"
        (self.root / authority).write_text("Explicit deterministic operator-budget fixture\n")
        record = {"schema_version": "1.0", "run_id": self.binding["scope"]["run_id"],
            "scope_sha256": self.binding["scope"]["scope_sha256"], "history_sha256": history["sha256"],
            "coder_sessions_started": 5, "source_attempts_started": 5, "previous_limit": 5, "new_limit": 20,
            "authority_evidence": [self.evidence(authority)]}
        return {"budget_extension": record, "retained_budget_extension_sha256": canonical_digest(record)}

    def test_extension_appends_sixth_session_without_resetting_default_or_history(self):
        history, path = self.history()
        extension = self.extension(history)
        event = self.execution_event(history, 6, "coder-session-start")
        request = {**self.binding, "event": event, "retained_history_sha256": history["sha256"]}
        before = path.read_bytes()
        self.assertEqual("blocked", controller.append_implementation_execution_event(self.root, request)["state"])
        self.assertEqual(before, path.read_bytes())
        result = controller.append_implementation_execution_event(self.root, {**request, **extension})
        self.assertEqual("ready", result["state"])
        self.assertEqual(6, result["coder_sessions_started"])
        self.assertEqual(5, result["source_attempts_started"])
        self.assertEqual(history["events"], result["history"]["events"][:-1])
        self.assertEqual(5, scope.MAX_CODER_SESSIONS)

    def test_extension_rejects_changed_scope_anchor_counters_authority_and_digest(self):
        history, path = self.history()
        extension = self.extension(history)
        for field, value in (("scope_sha256", "0" * 64), ("history_sha256", "0" * 64),
                             ("coder_sessions_started", 6), ("source_attempts_started", 0), ("new_limit", True)):
            with self.subTest(field=field):
                bad = copy.deepcopy(extension)
                bad["budget_extension"][field] = value
                bad["retained_budget_extension_sha256"] = canonical_digest(bad["budget_extension"])
                self.assertEqual("blocked", controller.validate_implementation_scope(self.root, {**self.binding, **bad})["state"])
        bad = {**extension, "retained_budget_extension_sha256": "0" * 64}
        self.assertEqual("blocked", controller.validate_implementation_scope(self.root, {**self.binding, **bad})["state"])
        authority = extension["budget_extension"]["authority_evidence"][0]["path"]
        (self.root / authority).write_text("changed authority\n")
        self.assertEqual("blocked", controller.validate_implementation_scope(self.root, {**self.binding, **extension})["state"])
        self.assertEqual(history, json.loads(path.read_text()))

    def test_bound_extension_routes_after_six_attempts_without_refilling_counts(self):
        history, path = self.history()
        extension = self.extension(history)
        original_events = copy.deepcopy(history["events"])
        for kind in ("coder-session-start", "source-attempt-start", "coder-session-outcome"):
            event = self.execution_event(history, 6, kind)
            result = controller.append_implementation_execution_event(self.root, {
                **self.binding, **extension, "event": event, "retained_history_sha256": history["sha256"]})
            self.assertEqual("ready", result["state"])
            history = result["history"]
        previous = {"state": "continue", "reason_code": "recorded-source-finding",
            "evidence": [self.evidence(self.source_path)], "remaining_ids": ["task:T002", "finding:OLD"],
            "resolved_ids": [], "next_step_id": "implement-tasks"}
        assessment = {**previous, "reason_code": "reviewed-source-resolution", "remaining_ids": ["task:T002"],
                      "resolved_ids": ["finding:OLD"]}
        request = {**self.binding, **extension, "assessment": assessment, "eligible_task_ids": ["T002"],
            "declared_node_ids": ["implement-tasks", "prepare-scoped-prerequisites"],
            "retained_history_sha256": history["sha256"], "previous_assessment": previous,
            "retained_previous_assessment_sha256": canonical_digest({"scope_sha256": self.binding["scope"]["scope_sha256"],
                                                                     "assessment": previous})}
        routed = controller.route_scoped_implementation(self.root, request)
        self.assertEqual("continue", routed["state"])
        self.assertEqual(6, routed["history"]["coder_sessions_started"])
        self.assertEqual(6, routed["history"]["source_attempts_started"])
        self.assertEqual(original_events, routed["history"]["events"][:len(original_events)])
        assessment["resolved_ids"] = []
        self.assertEqual("blocked", controller.route_scoped_implementation(self.root, request)["state"])
        for key in extension:
            request.pop(key)
        self.assertEqual("blocked", controller.route_scoped_implementation(self.root, request)["state"])

    def current_eligibility(self):
        snapshot = self.binding["scope"]
        current = [self.evidence(self.tasks_path)]
        source = [self.evidence(self.source_path)]
        classifications = {record["task_id"]: {"task_id": record["task_id"],
            "task_description_sha256": record["description_sha256"], "completion_kind": "substantive-implementation",
            "requirement_ids": ["code"], "source_requirement_ids": ["code"], "scope_sha256": snapshot["scope_sha256"],
            "classification_evidence": current} for record in snapshot["task_records"]}
        proof = {"task_id": "T001", "task_description_sha256": classifications["T001"]["task_description_sha256"],
            "completion_kind": "substantive-implementation", "scope_sha256": snapshot["scope_sha256"],
            "requirements": [{"requirement_id": "code", "satisfied": True, "evidence": source}],
            "proof_evidence": source, "review_evidence": {"reviewer": "FarmBoy Code Reviewer", "verdict": "complete",
                "reference": self.source_path, "sha256": source[0]["sha256"]},
            "activation_sha256": "d" * 64, "source_delta_evidence": source, "validation_evidence": source}
        assessment = {"assessment_id": "current-proof", "scope_sha256": snapshot["scope_sha256"],
            "predecessor_sha256": "e" * 64, "input_digests": {self.tasks_path: current[0]["sha256"]},
            "task_states": [{"task_id": "T001", "state": "completed-with-proof", "dependency_ids": [],
                "evidence": current, "proof_sha256": canonical_digest(proof), "blocker": None, "resume_action": None},
                {"task_id": "T002", "state": "eligible", "dependency_ids": ["T001"], "evidence": current,
                 "proof_sha256": None, "blocker": None, "resume_action": None}],
            "eligible_task_ids": ["T002"], "pending_task_ids": [], "global_blockers": [], "iteration": 2,
            "evidence": current}
        return {**self.binding, "assessment": assessment, "proofs": {"T001": proof},
            "proof_requirements": {"T001": ["code"], "T002": ["code"]},
            "completion_classifications": classifications, "source_requirement_ids": {"T001": ["code"], "T002": ["code"]},
            "retained_predecessor_sha256": "e" * 64}

    def test_historical_binding_never_authorizes_stale_current_fulfillment(self):
        request = self.current_eligibility()
        self.assertEqual("ready", controller.validate_implementation_eligibility(self.root, request)["state"])
        (self.root / self.source_path).write_text("changed after current review\n")
        self.assertEqual("blocked", controller.validate_implementation_eligibility(self.root, request)["state"])
        self.assertEqual("ready", controller.validate_implementation_scope(self.root, self.binding)["state"])

    def test_each_current_review_requirement_and_assessment_witness_is_checked(self):
        request = self.current_eligibility()
        for field in ("requirements", "proof_evidence", "review_evidence", "source_delta_evidence", "validation_evidence",
                      "classification_evidence", "assessment_evidence", "task_state_evidence"):
            with self.subTest(field=field):
                bad = copy.deepcopy(request)
                proof = bad["proofs"]["T001"]
                if field == "requirements":
                    proof[field][0]["evidence"][0]["sha256"] = "0" * 64
                elif field == "review_evidence":
                    proof[field]["sha256"] = "0" * 64
                elif field == "classification_evidence":
                    bad["completion_classifications"]["T001"][field][0]["sha256"] = "0" * 64
                elif field == "assessment_evidence":
                    bad["assessment"]["evidence"][0]["sha256"] = "0" * 64
                elif field == "task_state_evidence":
                    bad["assessment"]["task_states"][0]["evidence"][0]["sha256"] = "0" * 64
                else:
                    proof[field][0]["sha256"] = "0" * 64
                bad["assessment"]["task_states"][0]["proof_sha256"] = canonical_digest(proof)
                self.assertEqual("blocked", controller.validate_implementation_eligibility(self.root, bad)["state"])


if __name__ == "__main__":
    unittest.main()

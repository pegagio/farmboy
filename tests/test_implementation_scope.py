"""Strict tests for the standalone Feature 020 requested-scope helper."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / "controllers/farmboy/scripts/python"
sys.path.insert(0, str(SCRIPTS))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


scope = load_module("implementation_scope_under_test", SCRIPTS / "implementation_scope.py")
controller = load_module("implementation_scope_controller", SCRIPTS / "controller.py")


def canonical_digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def evidence(path: str = "specs/020-test/spec.md") -> list[dict[str, str]]:
    return [{"path": path, "sha256": "a" * 64}]


class ImplementationScopeTests(unittest.TestCase):
    def setUp(self):
        self.description = "Add a validated source helper"
        self.current_tasks = {"T068": {"marker": "unchecked", "description": self.description},
                              "T069": {"marker": "unchecked", "description": "Implement the scope validator"}}
        self.scope = {
            "schema_version": "1.0", "run_id": "run-1", "feature_directory": "specs/020-test",
            "request_reference": "operator-request-1", "request_kind": "full-feature",
            "requested_task_ids": ["T068", "T069"],
            "task_records": [
                {"task_id": key, "marker": value["marker"], "description": value["description"],
                 "description_sha256": hashlib.sha256(value["description"].encode()).hexdigest()}
                for key, value in self.current_tasks.items()
            ],
            "input_digests": {"specs/020-test/spec.md": "b" * 64},
        }
        self.scope["scope_sha256"] = canonical_digest(self.scope)

    def validate_scope(self, value=None, retained_scope_sha256=None):
        value = self.scope if value is None else value
        return scope.validate_requested_scope(value, self.current_tasks,
            trusted_request_reference="operator-request-1",
            retained_scope_sha256=retained_scope_sha256 or value["scope_sha256"])

    def testFixtureHasEveryScenarioAndExplicitHighRiskBoundaries(self):
        fixture = json.loads((ROOT / "tests/consumer-fixtures/workflow-improvements/implementation-scope-cases.json").read_text())
        self.assertEqual("implementation-scope", fixture["contract"])
        self.assertEqual([f"SI{i:03}" for i in range(1, 16)], [case["id"] for case in fixture["cases"]])
        self.assertEqual({f"FR-{number:03}" for number in range(39, 49)}, set(fixture["case_map"]["functional_requirements"]))
        self.assertEqual({f"SC-{number:03}" for number in range(17, 23)}, set(fixture["case_map"]["success_criteria"]))
        for case in fixture["cases"]:
            for key in ("requirements", "setup", "task_proofs", "route", "history", "budget", "generic_no_progress",
                        "expected", "expected_route", "evidence", "provenance", "safe_resume"):
                self.assertIn(key, case, case["id"])
            self.assertFalse(case["provenance"]["child_assertions_grant_authority"])
        for case_id in ("SI002", "SI003", "SI007", "SI011", "SI012"):
            case = next(item for item in fixture["cases"] if item["id"] == case_id)
            if case_id in {"SI002", "SI003", "SI007"}:
                self.assertIn("administrative_prerequisite_ids", case["expected"])
            self.assertIn("maximum_coder_sessions", case["budget"])
            self.assertIn("source_attempts_started", case["history"])
            self.assertIn("entry_node", case["route"])

    def testFullScopeRetainsEveryUnfinishedTaskAndExactDigest(self):
        self.assertIs(self.scope, self.validate_scope())
        narrower = copy.deepcopy(self.scope)
        narrower["requested_task_ids"].remove("T069")
        narrower["task_records"].pop()
        narrower["scope_sha256"] = canonical_digest({k: v for k, v in narrower.items() if k != "scope_sha256"})
        with self.assertRaisesRegex(scope.ImplementationScopeError, "requested-scope-digest-mismatch"):
            self.validate_scope(narrower, self.scope["scope_sha256"])

    def testTaskTrackingSuccessorIsMarkerOnlyExactTaskerAndReviewerBounded(self):
        before = "- [ ] T068 Add a validated source helper\n- [ ] T069 Implement the scope validator\n"
        after = "- [x] T068 Add a validated source helper\n- [ ] T069 Implement the scope validator\n"
        before_sha = hashlib.sha256(before.encode()).hexdigest()
        after_sha = hashlib.sha256(after.encode()).hexdigest()
        evidence_ref = evidence()
        event = {"predecessor_event_sha256": "0" * 64, "scope_sha256": self.scope["scope_sha256"],
            "tasker_assignment": "FarmBoy Tasker", "tasks_before_text": before, "tasks_after_text": after,
            "tasker_result": {"state": "ready", "tasks_before_sha256": before_sha,
                "tasks_after_sha256": after_sha, "completed_task_ids": ["T068"], "evidence": evidence_ref},
            "reviewer_result": {"reviewer": "FarmBoy Code Reviewer", "completed_task_ids": ["T068"],
                "evidence": evidence_ref}}
        event["sha256"] = canonical_digest(event)
        tracking = [event]
        self.assertEqual({"T068"}, scope.validate_task_tracking_successors(
            tracking, initial_tasks_sha256=before_sha, current_tasks_text=after,
            scope_sha256=self.scope["scope_sha256"], requested_task_ids={"T068", "T069"}))
        with self.assertRaisesRegex(scope.ImplementationScopeError, "proof-required"):
            scope.validate_task_tracking_successors([], initial_tasks_sha256=before_sha,
                current_tasks_text=after, scope_sha256=self.scope["scope_sha256"],
                requested_task_ids={"T068", "T069"})
        reordered = "- [ ] T069 Implement the scope validator\n- [x] T068 Add a validated source helper\n"
        for bad_after, expected in ((after.replace("T069 Implement", "T070 Implement"), "inventory-changed"),
                                    (after.replace("Add a validated source helper", "Unrelated task edit"), "description-changed"),
                                    (after + "\nNew unrelated guidance.\n", "non-marker-content-changed"),
                                    (reordered, "task-inventory-changed"),
                                    (before, "preimage-invalid")):
            bad = copy.deepcopy(event)
            bad["tasks_after_text"] = bad_after
            bad["tasker_result"]["tasks_after_sha256"] = hashlib.sha256(bad_after.encode()).hexdigest()
            bad["sha256"] = canonical_digest({key: value for key, value in bad.items() if key != "sha256"})
            with self.subTest(expected=expected), self.assertRaisesRegex(scope.ImplementationScopeError, expected):
                scope.validate_task_tracking_successors([bad], initial_tasks_sha256=before_sha,
                    current_tasks_text=bad_after, scope_sha256=self.scope["scope_sha256"],
                    requested_task_ids={"T068", "T069"})

    def testEligibilityIncludesOnlyTaskerValidatedDerivedRevisionTasks(self):
        derived = {"T070": ("unchecked", "Correct F020-R001 in the reviewed scope")}
        task_states = [{"task_id": task_id, "state": "pending", "dependency_ids": [], "evidence": evidence(),
                        "blocker": "waiting-for-coder", "resume_action": "resume-implement", "proof_sha256": None}
                       for task_id in [*self.scope["requested_task_ids"], *derived]]
        assessment = {"assessment_id": "eligibility-derived-1", "scope_sha256": self.scope["scope_sha256"],
            "predecessor_sha256": "c" * 64, "input_digests": {"specs/020-test/tasks.md": "d" * 64},
            "task_states": task_states, "eligible_task_ids": [],
            "pending_task_ids": [*self.scope["requested_task_ids"], *derived], "global_blockers": [],
            "iteration": 1, "evidence": evidence()}
        checked = scope.validate_task_eligibility(self.scope, assessment, {},
            tasker_derived_task_records=derived, retained_predecessor_sha256="c" * 64)
        self.assertEqual(assessment, checked)
        incomplete = copy.deepcopy(assessment)
        incomplete["task_states"].pop()
        incomplete["pending_task_ids"].pop()
        with self.assertRaisesRegex(scope.ImplementationScopeError, "coverage-incomplete"):
            scope.validate_task_eligibility(self.scope, incomplete, {},
                tasker_derived_task_records=derived, retained_predecessor_sha256="c" * 64)

    def testScopeRejectsUnknownFieldsStaleTaskAndForgedReference(self):
        extra = copy.deepcopy(self.scope)
        extra["authorization"] = True
        with self.assertRaisesRegex(scope.ImplementationScopeError, "schema-invalid"):
            self.validate_scope(extra)
        stale = copy.deepcopy(self.scope)
        self.current_tasks["T068"]["description"] = "Changed after scope capture"
        with self.assertRaisesRegex(scope.ImplementationScopeError, "snapshot-stale"):
            self.validate_scope(stale)
        self.current_tasks["T068"]["description"] = self.description
        with self.assertRaisesRegex(scope.ImplementationScopeError, "trusted-request-binding"):
            scope.validate_requested_scope(self.scope, self.current_tasks,
                trusted_request_reference="child-assertion", retained_scope_sha256=self.scope["scope_sha256"])

    def testExplicitSubsetMustMatchTheTrustedRequestedIDsExactly(self):
        subset = copy.deepcopy(self.scope)
        subset["request_kind"] = "explicit-subset"
        subset["requested_task_ids"] = ["T068"]
        subset["task_records"] = subset["task_records"][:1]
        subset["scope_sha256"] = canonical_digest({key: value for key, value in subset.items() if key != "scope_sha256"})
        scope.validate_requested_scope(subset, self.current_tasks, trusted_request_reference="operator-request-1",
            retained_scope_sha256=subset["scope_sha256"], trusted_requested_task_ids=["T068"])
        with self.assertRaisesRegex(scope.ImplementationScopeError, "explicit-subset-request-mismatch"):
            scope.validate_requested_scope(subset, self.current_tasks, trusted_request_reference="operator-request-1",
                retained_scope_sha256=subset["scope_sha256"], trusted_requested_task_ids=["T069"])

    def testAdministrativeProofDischargesAccountingButHasNoSourceCredit(self):
        classification = {
            "task_id": "T068", "task_description_sha256": hashlib.sha256(self.description.encode()).hexdigest(),
            "completion_kind": "administrative-prerequisite", "requirement_ids": ["approval"],
            "source_requirement_ids": [], "scope_sha256": self.scope["scope_sha256"],
            "classification_evidence": evidence(),
        }
        scope.validate_task_completion_classification(classification, task_id="T068", task_description=self.description,
            required_requirement_ids=["approval"], source_requirement_ids=[], scope_sha256=self.scope["scope_sha256"])
        proof = {
            "task_id": "T068", "task_description_sha256": hashlib.sha256(self.description.encode()).hexdigest(),
            "completion_kind": "administrative-prerequisite", "scope_sha256": self.scope["scope_sha256"],
            "requirements": [{"requirement_id": "approval", "satisfied": True, "evidence": evidence()}],
            "proof_evidence": evidence("specs/020-test/receipt.json"),
            "review_evidence": {"reviewer": "FarmBoy Code Reviewer", "verdict": "complete", "reference": "review-1", "sha256": "c" * 64},
            "trusted_decision_references": ["main-task-answer-1"], "permitted_effect_route": "declared-roadmap-write",
            "administrative_state_before": {"state": {"status": "planned"}, "sha256": "d" * 64, "evidence": evidence()},
            "administrative_state_after": {"state": {"status": "planned"}, "sha256": "e" * 64, "evidence": evidence("specs/020-test/after.json")},
            "no_source_effect_evidence": True,
        }
        self.assertEqual("administrative-prerequisite", scope.validate_task_fulfillment_proof(
            proof, task_id="T068", task_description=self.description,
            required_requirement_ids=["approval"], scope_sha256=self.scope["scope_sha256"],
            expected_completion_kind="administrative-prerequisite")["completion_kind"])
        incomplete = copy.deepcopy(proof)
        incomplete["no_source_effect_evidence"] = False
        with self.assertRaisesRegex(scope.ImplementationScopeError, "administrative-source-effect"):
            scope.validate_task_fulfillment_proof(incomplete, task_id="T068", task_description=self.description,
                required_requirement_ids=["approval"], scope_sha256=self.scope["scope_sha256"],
                expected_completion_kind="administrative-prerequisite")
        classification["completion_kind"] = "administrative-prerequisite"
        classification["source_requirement_ids"] = ["approval"]
        with self.assertRaisesRegex(scope.ImplementationScopeError, "source-requirement-cannot-be-administrative"):
            scope.validate_task_completion_classification(classification, task_id="T068", task_description=self.description,
                required_requirement_ids=["approval"], source_requirement_ids=["approval"], scope_sha256=self.scope["scope_sha256"])
        missing = copy.deepcopy(proof)
        missing["requirements"] = []
        with self.assertRaisesRegex(scope.ImplementationScopeError, "fulfillment-requirement-incomplete"):
            scope.validate_task_fulfillment_proof(missing, task_id="T068", task_description=self.description,
                required_requirement_ids=["approval"], scope_sha256=self.scope["scope_sha256"],
                expected_completion_kind="administrative-prerequisite")

    def testSubstantiveProofRequiresActivationSourceDeltaValidationAndReview(self):
        proof = {
            "task_id": "T068", "task_description_sha256": hashlib.sha256(self.description.encode()).hexdigest(),
            "completion_kind": "substantive-implementation", "scope_sha256": self.scope["scope_sha256"],
            "requirements": [{"requirement_id": "code", "satisfied": True, "evidence": evidence()}],
            "proof_evidence": evidence("specs/020-test/proof.json"),
            "review_evidence": {"reviewer": "FarmBoy Code Reviewer", "verdict": "complete", "reference": "review-1", "sha256": "c" * 64},
            "activation_sha256": "d" * 64, "source_delta_evidence": evidence("src/helper.py"),
            "validation_evidence": evidence("tests/result.json"),
        }
        self.assertEqual("substantive-implementation", scope.validate_task_fulfillment_proof(
            proof, task_id="T068", task_description=self.description,
            required_requirement_ids=["code"], scope_sha256=self.scope["scope_sha256"],
            expected_completion_kind="substantive-implementation")["completion_kind"])
        proof["source_delta_evidence"] = []
        with self.assertRaisesRegex(scope.ImplementationScopeError, "source-delta-evidence-missing"):
            scope.validate_task_fulfillment_proof(proof, task_id="T068", task_description=self.description,
                required_requirement_ids=["code"], scope_sha256=self.scope["scope_sha256"],
                expected_completion_kind="substantive-implementation")

    def testEligibilityCoversWholeScopeAndSeparatesEligiblePendingCompleted(self):
        assessment = {
            "assessment_id": "eligibility-1", "scope_sha256": self.scope["scope_sha256"], "predecessor_sha256": "e" * 64,
            "input_digests": {"specs/020-test/tasks.md": "f" * 64},
            "task_states": [
                {"task_id": "T068", "state": "eligible", "dependency_ids": [], "evidence": evidence(), "proof_sha256": None, "blocker": None, "resume_action": None},
                {"task_id": "T069", "state": "blocked", "dependency_ids": ["T068"], "evidence": evidence(), "proof_sha256": None, "blocker": "dependency-incomplete", "resume_action": "complete-T068"},
            ],
            "eligible_task_ids": ["T068"], "pending_task_ids": ["T069"], "global_blockers": [], "iteration": 0, "evidence": evidence(),
        }
        classification = {
            "task_id": "T068", "task_description_sha256": hashlib.sha256(self.description.encode()).hexdigest(),
            "completion_kind": "substantive-implementation", "requirement_ids": ["fixture"],
            "source_requirement_ids": ["fixture"], "scope_sha256": self.scope["scope_sha256"],
            "classification_evidence": evidence(),
        }
        proof_requirements = {"T068": ["fixture"], "T069": ["fixture"]}
        source_requirement_ids = {"T068": ["fixture"], "T069": ["fixture"]}
        classifications = {"T068": classification, "T069": {
            "task_id": "T069", "task_description_sha256": hashlib.sha256(self.current_tasks["T069"]["description"].encode()).hexdigest(),
            "completion_kind": "substantive-implementation", "requirement_ids": ["fixture"],
            "source_requirement_ids": ["fixture"], "scope_sha256": self.scope["scope_sha256"],
            "classification_evidence": evidence(),
        }}
        scope.validate_task_eligibility(self.scope, assessment, {}, proof_requirements=proof_requirements,
            completion_classifications=classifications, source_requirement_ids=source_requirement_ids, retained_predecessor_sha256="e" * 64)
        broken = copy.deepcopy(assessment)
        broken["task_states"].pop()
        with self.assertRaisesRegex(scope.ImplementationScopeError, "task-state-coverage-incomplete"):
            scope.validate_task_eligibility(self.scope, broken, {}, proof_requirements=proof_requirements,
                completion_classifications=classifications, source_requirement_ids=source_requirement_ids, retained_predecessor_sha256="e" * 64)
        global_failure = copy.deepcopy(assessment)
        global_failure["global_blockers"] = [{"reason_code": "readiness-stale", "resume_action": "refresh-readiness", "evidence": evidence()}]
        with self.assertRaisesRegex(scope.ImplementationScopeError, "global-blocker-cannot-have-eligible"):
            scope.validate_task_eligibility(self.scope, global_failure, {}, proof_requirements=proof_requirements,
                completion_classifications=classifications, source_requirement_ids=source_requirement_ids, retained_predecessor_sha256="e" * 64)
        premature = copy.deepcopy(assessment)
        premature["task_states"][1].update(state="eligible", blocker=None, resume_action=None)
        premature["eligible_task_ids"] = ["T068", "T069"]
        premature["pending_task_ids"] = []
        with self.assertRaisesRegex(scope.ImplementationScopeError, "task-eligible-dependency-incomplete"):
            scope.validate_task_eligibility(self.scope, premature, {}, proof_requirements=proof_requirements,
                completion_classifications=classifications, source_requirement_ids=source_requirement_ids, retained_predecessor_sha256="e" * 64)

    def testActivationRequiresFreshContainedPreimageCoverageAndNoGuessedHash(self):
        activation = {
            "activation_id": "activation-1", "task_id": "T068", "scope_sha256": self.scope["scope_sha256"],
            "eligibility_sha256": "1" * 64, "predecessor_baseline_sha256": "2" * 64,
            "occurred_at": "2026-10-07T12:00:00Z", "requirements": ["add fixture"],
            "source_preimages": [{"path": "tests/new.py", "state": "absent"}],
            "route_evidence": evidence(), "readiness_evidence": evidence(), "iteration": 1,
        }
        scope.validate_task_activation(activation, scope_sha256=self.scope["scope_sha256"],
            eligibility_sha256="1" * 64, predecessor_baseline_sha256="2" * 64,
            task_id="T068", required_paths={"tests/new.py"})
        activation["source_preimages"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(scope.ImplementationScopeError, "preimage-schema-invalid"):
            scope.validate_task_activation(activation, scope_sha256=self.scope["scope_sha256"],
                eligibility_sha256="1" * 64, predecessor_baseline_sha256="2" * 64,
                task_id="T068", required_paths={"tests/new.py"})

    def testOwnerSourceRequiresObservedRouteAccessAndPortableCoordinates(self):
        owner = {
            "task_id": "T052", "component_id": "farmboy-roadmap", "source_identity": "pegagio/spec-kit-flow-roadmap",
            "source_coordinates": {"repository": "pegagio/spec-kit-flow-roadmap", "revision": "abc123", "dirty_state": "clean", "relative_paths": ["scripts/python/phase_lifecycle.py"]},
            "access_state": "read-write", "guidance_evidence": evidence("AGENTS.md"),
            "source_route": {"state": "permitted", "description": "Task-owned source changes", "evidence": evidence("constitution.md")},
            "authority_evidence": evidence("specs/020-test/tasks.md"), "state": "ready",
        }
        scope.validate_owner_source_assessment(owner)
        owner["source_coordinates"]["relative_paths"] = ["/outside/private/file"]
        with self.assertRaisesRegex(scope.ImplementationScopeError, "path-invalid"):
            scope.validate_owner_source_assessment(owner)

    def _history(self, execution_kind="first-source-execution"):
        history = {"schema_version": "1.0", "scope_sha256": self.scope["scope_sha256"], "events": [],
                   "coder_sessions_started": 0, "source_attempts_started": 0}
        history["sha256"] = canonical_digest({key: value for key, value in history.items() if key != "sha256"})
        retained = history["sha256"]
        session = {
            "event_id": "event-1", "predecessor_sha256": "0" * 64, "scope_sha256": self.scope["scope_sha256"],
            "event_kind": "coder-session-start", "declared_node_id": "implement-tasks", "occurred_at": "2026-10-07T12:00:00Z",
            "evidence": evidence("specs/020-test/dispatch.json"), "coder_session_id": "session-1",
            "coder_sessions_started": 1, "source_attempts_started": 0, "execution_kind": execution_kind,
        }
        session["sha256"] = canonical_digest({key: value for key, value in session.items() if key != "sha256"})
        history = scope.append_execution_event(history, session, scope_sha256=self.scope["scope_sha256"], retained_history_sha256=retained)
        attempt = {
            "event_id": "event-2", "predecessor_sha256": session["sha256"], "scope_sha256": self.scope["scope_sha256"],
            "event_kind": "source-attempt-start", "declared_node_id": "implement-tasks", "occurred_at": "2026-10-07T12:00:01Z",
            "evidence": evidence("specs/020-test/dispatch.json"), "coder_session_id": "session-1",
            "coder_sessions_started": 1, "source_attempts_started": 1, "execution_kind": execution_kind,
        }
        attempt["sha256"] = canonical_digest({key: value for key, value in attempt.items() if key != "sha256"})
        history = scope.append_execution_event(history, attempt, scope_sha256=self.scope["scope_sha256"], retained_history_sha256=history["sha256"])
        outcome = {
            "event_id": "event-3", "predecessor_sha256": attempt["sha256"], "scope_sha256": self.scope["scope_sha256"],
            "event_kind": "coder-session-outcome", "declared_node_id": "implement-tasks", "occurred_at": "2026-10-07T12:00:02Z",
            "evidence": evidence("specs/020-test/review.json"), "coder_session_id": "session-1",
            "coder_sessions_started": 1, "source_attempts_started": 1, "outcome": "completed",
        }
        outcome["sha256"] = canonical_digest({key: value for key, value in outcome.items() if key != "sha256"})
        return scope.append_execution_event(history, outcome, scope_sha256=self.scope["scope_sha256"], retained_history_sha256=history["sha256"])

    def _empty_history(self):
        history = {"schema_version": "1.0", "scope_sha256": self.scope["scope_sha256"], "events": [],
                   "coder_sessions_started": 0, "source_attempts_started": 0}
        history["sha256"] = canonical_digest(history)
        return history

    def testHistoryPersistsSessionAndAttemptBeforeDispatchAndRejectsRewind(self):
        history = self._history()
        self.assertEqual((1, 1), (history["coder_sessions_started"], history["source_attempts_started"]))
        scope.validate_execution_history(history, scope_sha256=self.scope["scope_sha256"], retained_history_sha256=history["sha256"])
        history["source_attempts_started"] = 0
        with self.assertRaisesRegex(scope.ImplementationScopeError, "counter-invalid"):
            scope.validate_execution_history(history, scope_sha256=self.scope["scope_sha256"], retained_history_sha256=history["sha256"])

    def testSharedCoderBudgetCountsEverySessionAndSameChildInputAddsNone(self):
        history = self._empty_history()
        for number in range(1, 6):
            prior = history["events"][-1]["sha256"] if history["events"] else "0" * 64
            session_id = f"session-{number}"
            start = {
                "event_id": f"start-{number}", "predecessor_sha256": prior, "scope_sha256": self.scope["scope_sha256"],
                "event_kind": "coder-session-start", "declared_node_id": "prepare-scoped-prerequisites",
                "occurred_at": f"2026-10-07T12:00:0{number}Z", "evidence": evidence("specs/020-test/dispatch.json"),
                "coder_session_id": session_id, "coder_sessions_started": number, "source_attempts_started": 0,
                "execution_kind": "preparation",
            }
            start["sha256"] = canonical_digest({key: value for key, value in start.items() if key != "sha256"})
            history = scope.append_execution_event(history, start, scope_sha256=self.scope["scope_sha256"], retained_history_sha256=history["sha256"])
            if number == 1:
                question = {
                    "event_id": "input-1", "predecessor_sha256": start["sha256"], "scope_sha256": self.scope["scope_sha256"],
                    "event_kind": "operator-input", "declared_node_id": "prepare-scoped-prerequisites",
                    "occurred_at": "2026-10-07T12:00:06Z", "evidence": evidence("specs/020-test/answer.json"),
                    "coder_session_id": session_id, "coder_sessions_started": 1, "source_attempts_started": 0,
                    "same_child_resume": True,
                }
                question["sha256"] = canonical_digest({key: value for key, value in question.items() if key != "sha256"})
                history = scope.append_execution_event(history, question, scope_sha256=self.scope["scope_sha256"], retained_history_sha256=history["sha256"])
            predecessor = history["events"][-1]["sha256"]
            outcome = {
                "event_id": f"outcome-{number}", "predecessor_sha256": predecessor, "scope_sha256": self.scope["scope_sha256"],
                "event_kind": "coder-session-outcome", "declared_node_id": "prepare-scoped-prerequisites",
                "occurred_at": f"2026-10-07T12:00:1{number}Z", "evidence": evidence("specs/020-test/review.json"),
                "coder_session_id": session_id, "coder_sessions_started": number, "source_attempts_started": 0,
                "outcome": "completed",
            }
            outcome["sha256"] = canonical_digest({key: value for key, value in outcome.items() if key != "sha256"})
            history = scope.append_execution_event(history, outcome, scope_sha256=self.scope["scope_sha256"], retained_history_sha256=history["sha256"])
        self.assertEqual(5, history["coder_sessions_started"])
        self.assertEqual(0, history["source_attempts_started"])
        next_start = {
            "event_id": "start-6", "predecessor_sha256": history["events"][-1]["sha256"], "scope_sha256": self.scope["scope_sha256"],
            "event_kind": "coder-session-start", "declared_node_id": "prepare-scoped-prerequisites",
            "occurred_at": "2026-10-07T12:00:16Z", "evidence": evidence("specs/020-test/dispatch.json"),
            "coder_session_id": "session-6", "coder_sessions_started": 6, "source_attempts_started": 0,
            "execution_kind": "preparation",
        }
        next_start["sha256"] = canonical_digest({key: value for key, value in next_start.items() if key != "sha256"})
        with self.assertRaisesRegex(scope.ImplementationScopeError, "counter-invalid"):
            scope.append_execution_event(history, next_start, scope_sha256=self.scope["scope_sha256"], retained_history_sha256=history["sha256"])

    def testPostAttemptRouteCallsActualGenericPredicateWithPreAttemptAssessment(self):
        history = self._history()
        previous = {"state": "continue", "next_step_id": "implement-tasks", "remaining_ids": ["finding:F001", "task:T069"], "resolved_ids": [],
                    "reason_code": "pending-work", "evidence": evidence()}
        current = {"state": "continue", "next_step_id": "implement-tasks", "remaining_ids": ["task:T069"], "resolved_ids": ["finding:F001"],
                   "reason_code": "defect-resolved", "evidence": evidence()}
        calls = []

        def generic(current_assessment, **kwargs):
            calls.append((current_assessment, kwargs.copy()))
            return controller.route_loop_assessment(current_assessment, **kwargs)

        result = scope.route_scoped_implementation_assessment(history=history, assessment=current,
            eligible_task_ids=["T069"], declared_node_ids={"implement-tasks", "prepare-scoped-prerequisites"},
            previous_assessment=previous, generic_route=generic, retained_history_sha256=history["sha256"])
        self.assertEqual("continue", result["action"])
        self.assertEqual(current, calls[0][0])
        self.assertIs(previous, calls[0][1]["previous_assessment"])
        self.assertEqual(1, calls[0][1]["iteration"])
        self.assertEqual(5, calls[0][1]["max_iterations"])
        self.assertNotIn("assessment_only_first_pass", calls[0][1])
        stalled = {"state": "continue", "next_step_id": "implement-tasks", "remaining_ids": ["finding:F001", "task:T069"], "resolved_ids": [],
                    "reason_code": "pending-work", "evidence": evidence()}
        result = scope.route_scoped_implementation_assessment(history=history, assessment=stalled,
            eligible_task_ids=["T069"], declared_node_ids={"implement-tasks"},
            previous_assessment=previous, generic_route=generic, retained_history_sha256=history["sha256"])
        self.assertEqual("no-progress", result["blocker"])
        with self.assertRaisesRegex(scope.ImplementationScopeError, "generic-post-source-predicate-required"):
            scope.route_scoped_implementation_assessment(history=history, assessment=current,
                eligible_task_ids=["T069"], declared_node_ids={"implement-tasks"}, previous_assessment=previous,
                retained_history_sha256=history["sha256"])

    def testPostAttemptContinuationWithNoEligibleTasksBlocksWithCurrentReason(self):
        history = self._history()
        previous = {"state": "continue", "next_step_id": "implement-tasks", "remaining_ids": ["finding:F001", "task:T069"],
                    "resolved_ids": [], "reason_code": "pending-work", "evidence": evidence()}
        current = {"state": "continue", "next_step_id": "implement-tasks", "remaining_ids": ["task:T069"],
                   "resolved_ids": ["finding:F001"], "reason_code": "pending-prerequisite", "evidence": evidence()}
        result = scope.route_scoped_implementation_assessment(history=history, assessment=current,
            eligible_task_ids=[], declared_node_ids={"implement-tasks"}, previous_assessment=previous,
            generic_route=controller.route_loop_assessment, retained_history_sha256=history["sha256"])
        self.assertEqual({"action": "blocked", "blocker": "scoped-work-pending",
                          "reason_code": "pending-prerequisite"}, result)

    def testPreSourceFocusedDecisionCanRouteToPreparationWithoutSourceEligibility(self):
        history = self._empty_history()
        question = {"state": "continue", "next_step_id": "prepare-scoped-prerequisites",
                    "remaining_ids": ["task:T068"], "resolved_ids": [],
                    "reason_code": "operator-decision-required", "evidence": evidence()}
        result = scope.route_scoped_implementation_assessment(history=history, assessment=question,
            eligible_task_ids=[], declared_node_ids={"implement-tasks", "prepare-scoped-prerequisites"},
            retained_history_sha256=history["sha256"])
        self.assertEqual({"action": "continue", "next_step_id": "prepare-scoped-prerequisites"}, result)
        unrelated = {**question, "reason_code": "pending-work"}
        stopped = scope.route_scoped_implementation_assessment(history=history, assessment=unrelated,
            eligible_task_ids=[], declared_node_ids={"implement-tasks", "prepare-scoped-prerequisites"},
            retained_history_sha256=history["sha256"])
        self.assertEqual("scoped-work-pending", stopped["blocker"])

    def testPostAttemptPreparationRouteIsRejectedAfterGenericProgress(self):
        history = self._history()
        previous = {"state": "continue", "next_step_id": "implement-tasks", "remaining_ids": ["finding:F001", "task:T069"],
                    "resolved_ids": [], "reason_code": "pending-work", "evidence": evidence()}
        current = {"state": "continue", "next_step_id": "prepare-scoped-prerequisites", "remaining_ids": ["task:T069"],
                   "resolved_ids": ["finding:F001"], "reason_code": "new-prerequisite", "evidence": evidence()}
        with self.assertRaisesRegex(scope.ImplementationScopeError, "scoped-post-source-route-invalid"):
            scope.route_scoped_implementation_assessment(history=history, assessment=current,
                eligible_task_ids=["T069"], declared_node_ids={"implement-tasks", "prepare-scoped-prerequisites"},
                previous_assessment=previous, generic_route=controller.route_loop_assessment,
                retained_history_sha256=history["sha256"])

    def testPreparationSessionCannotFollowAnySourceAttemptOutcome(self):
        source_history = self._history()
        for outcome in ("completed", "failed-dispatch", "question-stopped"):
            with self.subTest(outcome=outcome):
                history = self._empty_history()
                for original in source_history["events"]:
                    event = copy.deepcopy(original)
                    if event["event_kind"] == "coder-session-outcome":
                        event["outcome"] = outcome
                        event["sha256"] = canonical_digest({key: value for key, value in event.items() if key != "sha256"})
                    history = scope.append_execution_event(history, event, scope_sha256=self.scope["scope_sha256"],
                        retained_history_sha256=history["sha256"])
                if outcome == "question-stopped":
                    for kind in ("operator-input", "coder-session-outcome"):
                        event = {"event_id": f"resume-{kind}", "predecessor_sha256": history["events"][-1]["sha256"],
                            "scope_sha256": self.scope["scope_sha256"], "event_kind": kind,
                            "declared_node_id": "implement-tasks", "occurred_at": "2026-10-07T12:00:03Z",
                            "evidence": evidence(), "coder_session_id": "session-1",
                            "coder_sessions_started": 1, "source_attempts_started": 1}
                        event.update({"same_child_resume": True} if kind == "operator-input" else {"outcome": "completed"})
                        event["sha256"] = canonical_digest(event)
                        history = scope.append_execution_event(history, event, scope_sha256=self.scope["scope_sha256"],
                            retained_history_sha256=history["sha256"])
                previous = {"state": "continue", "next_step_id": "implement-tasks",
                    "remaining_ids": ["finding:F001", "task:T069"], "resolved_ids": [],
                    "reason_code": "pending-work", "evidence": evidence()}
                current = {"state": "continue", "next_step_id": "prepare-scoped-prerequisites",
                    "remaining_ids": ["task:T069"], "resolved_ids": ["finding:F001"],
                    "reason_code": "new-prerequisite", "evidence": evidence()}
                with self.assertRaisesRegex(scope.ImplementationScopeError, "scoped-post-source-route-invalid"):
                    scope.route_scoped_implementation_assessment(history=history, assessment=current,
                        eligible_task_ids=["T069"],
                        declared_node_ids={"implement-tasks", "prepare-scoped-prerequisites"},
                        previous_assessment=previous, generic_route=controller.route_loop_assessment,
                        retained_history_sha256=history["sha256"])
                prior = history["events"][-1]["sha256"]
                preparation = {"event_id": "preparation-after-source", "predecessor_sha256": prior,
                    "scope_sha256": self.scope["scope_sha256"], "event_kind": "coder-session-start",
                    "declared_node_id": "prepare-scoped-prerequisites", "occurred_at": "2026-10-07T12:00:04Z",
                    "evidence": evidence(), "coder_session_id": "session-2", "coder_sessions_started": 2,
                    "source_attempts_started": 1, "execution_kind": "preparation"}
                preparation["sha256"] = canonical_digest(preparation)
                with self.assertRaisesRegex(scope.ImplementationScopeError,
                        "execution-history-preparation-after-source-attempt"):
                    scope.append_execution_event(history, preparation, scope_sha256=self.scope["scope_sha256"],
                        retained_history_sha256=history["sha256"])

    def testPreSourceRouteUsesOnlyDeclaredPreparationOrFirstSourceNodes(self):
        history = self._empty_history()
        allowed = {"prepare-scoped-prerequisites", "implement-tasks"}
        result = scope.route_scoped_implementation_assessment(history=history,
            assessment={"state": "continue", "next_step_id": "implement-tasks", "remaining_ids": ["task:T068"],
                        "resolved_ids": [], "reason_code": "eligible-work", "evidence": evidence()}, eligible_task_ids=["T068"], declared_node_ids=allowed,
            retained_history_sha256=history["sha256"])
        self.assertEqual({"action": "continue", "next_step_id": "implement-tasks"}, result)
        with self.assertRaisesRegex(scope.ImplementationScopeError, "scoped-route-node-undeclared"):
            scope.route_scoped_implementation_assessment(history=history,
                assessment={"state": "continue", "next_step_id": "unmodeled-node", "remaining_ids": ["task:T068"],
                            "resolved_ids": [], "reason_code": "eligible-work", "evidence": evidence()}, eligible_task_ids=["T068"], declared_node_ids=allowed,
                retained_history_sha256=history["sha256"])

    def testFixtureAccountingIsAnExactDisjointPartition(self):
        fixture = json.loads((ROOT / "tests/consumer-fixtures/workflow-improvements/implementation-scope-cases.json").read_text())
        for case in fixture["cases"]:
            with self.subTest(case=case["id"]):
                expected = case["expected"]
                partitions = [expected[key] for key in ("eligible_task_ids", "pending_task_ids", "completed_task_ids")]
                for values in partitions:
                    self.assertEqual(len(values), len(set(values)))
                flattened = [task for values in partitions for task in values]
                self.assertEqual(len(flattened), len(set(flattened)))
                self.assertEqual(set(expected["requested_task_ids"]), set(flattened))
                self.assertFalse(set(flattened) & set(expected["outside_task_ids"]))
                if expected["state"] == "continue":
                    self.assertTrue(expected["eligible_task_ids"])

    def testRawPathAliasesAreRejectedAcrossEvidenceAndSourceInputs(self):
        for path in ("tests//new.py", "tests/./new.py", "tests/../new.py", "tests/new.py/", "/tests/new.py"):
            with self.subTest(path=path), self.assertRaises(scope.ImplementationScopeError):
                scope._evidence_list(evidence(path), "test")

    def testActivationRejectsMalformedRetainedDigestsAndUnzonedTimes(self):
        activation = {"activation_id": "a1", "task_id": "T068", "scope_sha256": "a" * 64,
            "eligibility_sha256": "b" * 64, "predecessor_baseline_sha256": "c" * 64,
            "occurred_at": "2026-10-07T12:00:00Z", "requirements": ["code"],
            "source_preimages": [{"path": "tests/new.py", "state": "absent"}],
            "route_evidence": evidence(), "readiness_evidence": evidence(), "iteration": 1}
        for field in ("scope_sha256", "eligibility_sha256", "predecessor_baseline_sha256"):
            for bad in (None, "", 1, True, "x" * 64):
                record = copy.deepcopy(activation)
                record[field] = bad
                retained = {key: activation[key] for key in ("scope_sha256", "eligibility_sha256", "predecessor_baseline_sha256")}
                retained[field] = bad
                with self.subTest(field=field, bad=bad), self.assertRaises(scope.ImplementationScopeError):
                    scope.validate_task_activation(record, **retained, task_id="T068", required_paths={"tests/new.py"})
        for bad in ("2026-10-07", "2026-10-07T12:00:00", None):
            activation["occurred_at"] = bad
            with self.assertRaisesRegex(scope.ImplementationScopeError, "time-invalid"):
                scope.validate_task_activation(activation, scope_sha256="a" * 64, eligibility_sha256="b" * 64,
                    predecessor_baseline_sha256="c" * 64, task_id="T068", required_paths={"tests/new.py"})

    def testBlockedOrMalformedPreSourceAssessmentCannotBePromoted(self):
        history = self._empty_history()
        blocked = {"state": "blocked", "reason_code": "readiness-stale", "resume_action": "refresh-readiness",
            "remaining_ids": ["task:T068"], "resolved_ids": [], "evidence": evidence()}
        def route(assessment, eligible=None):
            return scope.route_scoped_implementation_assessment(history=history, assessment=assessment,
                eligible_task_ids=eligible or [], declared_node_ids={"implement-tasks"}, retained_history_sha256=history["sha256"])
        self.assertEqual({"action": "blocked", "resume_action": "refresh-readiness"}, route(blocked))
        self.assertEqual("blocked", route(blocked, ["T068"])["action"])
        for malformed in ({**blocked, "next_step_id": "implement-tasks"},
                          {key: value for key, value in blocked.items() if key != "remaining_ids"},
                          {**blocked, "state": "complete"}):
            with self.assertRaises(scope.ImplementationScopeError):
                route(malformed)

    def testSourceOutcomesAndInputRequireExactlyOneAttemptAndClosedRoute(self):
        valid = self._history()
        start = valid["events"][0]
        history = self._empty_history()
        history = scope.append_execution_event(history, start, scope_sha256=self.scope["scope_sha256"],
            retained_history_sha256=history["sha256"])
        for outcome in ("completed", "failed-dispatch", "question-stopped"):
            event = copy.deepcopy(valid["events"][-1])
            event.update(predecessor_sha256=start["sha256"], source_attempts_started=0, outcome=outcome)
            event["sha256"] = canonical_digest({key: value for key, value in event.items() if key != "sha256"})
            with self.subTest(outcome=outcome), self.assertRaisesRegex(scope.ImplementationScopeError, "source-attempt-missing"):
                scope.append_execution_event(history, event, scope_sha256=self.scope["scope_sha256"],
                    retained_history_sha256=history["sha256"])
        current = {"state": "continue", "next_step_id": "implement-tasks", "remaining_ids": ["task:T068"],
            "resolved_ids": [], "reason_code": "eligible-work", "evidence": evidence()}
        with self.assertRaisesRegex(scope.ImplementationScopeError, "session-unclosed"):
            scope.route_scoped_implementation_assessment(history=history, assessment=current, eligible_task_ids=["T068"],
                declared_node_ids={"implement-tasks"}, retained_history_sha256=history["sha256"])
        attempt = valid["events"][1]
        history = scope.append_execution_event(history, attempt, scope_sha256=self.scope["scope_sha256"],
            retained_history_sha256=history["sha256"])
        repeated = copy.deepcopy(attempt)
        repeated.update(event_id="extra-attempt", predecessor_sha256=attempt["sha256"], source_attempts_started=2)
        repeated["sha256"] = canonical_digest({key: value for key, value in repeated.items() if key != "sha256"})
        with self.assertRaisesRegex(scope.ImplementationScopeError, "attempt-order-invalid"):
            scope.append_execution_event(history, repeated, scope_sha256=self.scope["scope_sha256"],
                retained_history_sha256=history["sha256"])

    def testCompletedOutsidePrerequisiteProofDoesNotExpandScope(self):
        for request_kind in ("full-feature", "explicit-subset"):
            requested = copy.deepcopy(self.scope)
            requested["request_kind"] = request_kind
            description = "Completed prerequisite source work"
            classification = {"task_id": "T051", "task_description_sha256": hashlib.sha256(description.encode()).hexdigest(),
                "completion_kind": "substantive-implementation", "requirement_ids": ["code"], "source_requirement_ids": ["code"],
                "scope_sha256": requested["scope_sha256"], "classification_evidence": evidence()}
            proof = {"task_id": "T051", "task_description_sha256": classification["task_description_sha256"],
                "completion_kind": "substantive-implementation", "scope_sha256": requested["scope_sha256"],
                "requirements": [{"requirement_id": "code", "satisfied": True, "evidence": evidence()}],
                "proof_evidence": evidence(), "review_evidence": {"reviewer": "FarmBoy Code Reviewer",
                    "verdict": "complete", "reference": "retained-review", "sha256": "c" * 64},
                "activation_sha256": "d" * 64, "source_delta_evidence": evidence(), "validation_evidence": evidence()}
            prerequisite = {"task_id": "T051", "description": description, "requirement_ids": ["code"],
                "source_requirement_ids": ["code"], "classification": classification, "proof": proof}
            assessment = {"assessment_id": "eligibility-2", "scope_sha256": requested["scope_sha256"],
                "predecessor_sha256": "e" * 64, "input_digests": {"specs/020-test/tasks.md": "f" * 64},
                "task_states": [
                    {"task_id": "T068", "state": "eligible", "dependency_ids": ["T051"], "evidence": evidence(),
                        "proof_sha256": None, "blocker": None, "resume_action": None},
                    {"task_id": "T069", "state": "pending", "dependency_ids": ["T068"], "evidence": evidence(),
                        "proof_sha256": None, "blocker": "dependency-incomplete", "resume_action": "complete-prerequisite"}],
                "eligible_task_ids": ["T068"], "pending_task_ids": ["T069"], "global_blockers": [],
                "iteration": 0, "evidence": evidence()}
            kind = {**classification, "task_id": "T068", "task_description_sha256": hashlib.sha256(self.description.encode()).hexdigest()}
            kwargs = dict(proof_requirements={"T068": ["code"]}, source_requirement_ids={"T068": ["code"]},
                completion_classifications={"T068": kind}, retained_predecessor_sha256="e" * 64,
                completed_prerequisites={"T051": prerequisite}, retained_prerequisite_sha256={"T051": canonical_digest(prerequisite)})
            result = scope.validate_task_eligibility(requested, assessment, {}, **kwargs)
            self.assertEqual(["T068"], result["eligible_task_ids"])
            self.assertNotIn("T051", requested["requested_task_ids"])
            kwargs["retained_predecessor_sha256"] = "f" * 64
            with self.assertRaisesRegex(scope.ImplementationScopeError, "eligibility-scope-mismatch"):
                scope.validate_task_eligibility(requested, assessment, {}, **kwargs)
            kwargs["retained_predecessor_sha256"] = "e" * 64
            kwargs["retained_prerequisite_sha256"]["T051"] = "f" * 64
            with self.assertRaisesRegex(scope.ImplementationScopeError, "prerequisite-proof-binding-invalid"):
                scope.validate_task_eligibility(requested, assessment, {}, **kwargs)

    def testFailedDispatchRetainsAttemptAndQuestionResumesSameSession(self):
        valid = self._history()
        for outcome in ("failed-dispatch", "question-stopped"):
            history = self._empty_history()
            for original in valid["events"]:
                event = copy.deepcopy(original)
                if event["event_kind"] == "coder-session-outcome":
                    event["outcome"] = outcome
                    event["sha256"] = canonical_digest({key: value for key, value in event.items() if key != "sha256"})
                history = scope.append_execution_event(history, event, scope_sha256=self.scope["scope_sha256"],
                    retained_history_sha256=history["sha256"])
            self.assertEqual(1, history["source_attempts_started"])
            self.assertEqual(1, history["coder_sessions_started"])
            if outcome == "question-stopped":
                for kind in ("operator-input", "coder-session-outcome"):
                    event = {"event_id": kind, "predecessor_sha256": history["events"][-1]["sha256"],
                        "scope_sha256": self.scope["scope_sha256"], "event_kind": kind,
                        "declared_node_id": "implement-tasks", "occurred_at": "2026-10-07T12:00:03Z",
                        "evidence": evidence(), "coder_session_id": "session-1",
                        "coder_sessions_started": 1, "source_attempts_started": 1}
                    event.update({"same_child_resume": True} if kind == "operator-input" else {"outcome": "completed"})
                    event["sha256"] = canonical_digest(event)
                    history = scope.append_execution_event(history, event, scope_sha256=self.scope["scope_sha256"],
                        retained_history_sha256=history["sha256"])
                self.assertEqual(1, history["coder_sessions_started"])

    def testHistoryRejectsBooleanCountersAndSubstitutedNodes(self):
        for field in ("coder_sessions_started", "source_attempts_started"):
            history = self._history()
            history[field] = True
            history["sha256"] = canonical_digest({key: value for key, value in history.items() if key != "sha256"})
            with self.assertRaisesRegex(scope.ImplementationScopeError, "counter-invalid"):
                scope.validate_execution_history(history, scope_sha256=self.scope["scope_sha256"],
                    retained_history_sha256=history["sha256"])
        history = self._history()
        history["events"][1]["declared_node_id"] = "prepare-scoped-prerequisites"
        history["events"][1]["sha256"] = canonical_digest({key: value for key, value in history["events"][1].items() if key != "sha256"})
        history["events"][2]["predecessor_sha256"] = history["events"][1]["sha256"]
        history["events"][2]["sha256"] = canonical_digest({key: value for key, value in history["events"][2].items() if key != "sha256"})
        history["sha256"] = canonical_digest({key: value for key, value in history.items() if key != "sha256"})
        with self.assertRaisesRegex(scope.ImplementationScopeError, "attempt-order-invalid"):
            scope.validate_execution_history(history, scope_sha256=self.scope["scope_sha256"], retained_history_sha256=history["sha256"])


if __name__ == "__main__":
    unittest.main()

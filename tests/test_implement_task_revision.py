"""Production-route and history checks for Tasker-owned Implement repair."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]
CONTROLLER_DIR = ROOT / "controllers/flow-kit/scripts/python"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(CONTROLLER_DIR))
from tools.catalog import controller_package_files


def load_controller():
    spec = importlib.util.spec_from_file_location("task_revision_controller", CONTROLLER_DIR / "controller.py")
    if spec is None or spec.loader is None:
        raise AssertionError("controller module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def find_step(steps, step_id):
    for step in steps:
        if step.get("id") == step_id:
            return step
        for value in step.values():
            if isinstance(value, list):
                found = find_step(value, step_id)
                if found is not None:
                    return found
            elif isinstance(value, dict):
                found = find_step([value], step_id)
                if found is not None:
                    return found
    return None


def render_switch(controller, switch, inputs, outputs):
    rendered = controller.render_template(
        {key: value for key, value in switch.items() if key not in {"cases", "default"}}, inputs, outputs
    )
    rendered["cases"] = switch.get("cases", {})
    if "default" in switch:
        rendered["default"] = switch["default"]
    return rendered


class ImplementTaskRevisionRouteTests(unittest.TestCase):
    """Rendered branches invoke only the reviewed Tasker for routine repair."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.controller = load_controller()
        cls.workflow = yaml.safe_load((ROOT / "workflows/speckit-flow-implement/workflow.yml").read_text())

    def test_openCorrectionTaskSkipsTaskerAndClosedOrMissingTaskUsesExactAssignment(self) -> None:
        loop = find_step(self.workflow["steps"], "implementation-loop")
        self.assertIsNotNone(loop)
        route = find_step(loop["steps"], "route-post-assessment")
        continue_branch = route["cases"]["continue"]
        task_revision_route = continue_branch[0]
        revision = task_revision_route["cases"]["revise"]
        preflight_route = next(item for item in revision if item.get("id") == "route-task-revision-preflight")
        preflight_block = self.controller.select_switch_branch(
            render_switch(self.controller, preflight_route, {"feature_context": "specs/031-consumer"},
                          {"preflight-task-revision-snapshot": {"state": "blocked"}}),
            "blocked",
        )
        self.assertEqual(["stop-task-revision-preflight-blocked"], [item["id"] for item in preflight_block])
        self.assertNotIn("revise-task-plan", [item["id"] for item in preflight_block])
        snapshot_route = next(item for item in preflight_route["cases"]["ready"]
                              if item.get("id") == "route-task-revision-snapshot")
        snapshot_block = self.controller.select_switch_branch(
            render_switch(self.controller, snapshot_route, {"feature_context": "specs/031-consumer"},
                          {"revalidate-task-revision-snapshot": {"state": "blocked"}}),
            "blocked",
        )
        self.assertEqual(["stop-task-revision-dispatch-blocked"], [item["id"] for item in snapshot_block])
        assignments = {item.step_id: item.agent_name for item in self.controller.collect_agent_assignments(self.workflow["steps"])}
        tasker_step = next(item for item in snapshot_route["cases"]["ready"]
                           if item.get("id") == "revise-task-plan")
        tasker_steps = revision
        self.assertEqual("FlowKit-Tasker", assignments["revise-task-plan"])
        self.assertEqual("speckit.tasks", tasker_step["command"])
        self.assertTrue(tasker_step["flow_kit"]["delegated"])
        self.assertEqual("route-task-revision", task_revision_route["id"])

        for case_id, task_revision_action, choice, expected, finding_task_id in (
            ("open correction task", "skip", "skip", [], "T008"),
            ("completed correction task", "revise", "revise", tasker_steps, "T008"),
            ("missing correction task", "revise", "revise", tasker_steps, "T046"),
        ):
            finding = {"id": "F020-R001", "task_id": finding_task_id}
            outputs = {
                "assess-implementation-after-pass": {
                    "state": "continue", "task_revision_action": task_revision_action,
                    "findings": [finding],
                    "findings_json": json.dumps([finding]),
                },
                "prepare-task-revision": {"task_snapshot_json": json.dumps({
                    "tasks_path": "specs/020-example/tasks.md", "tasks_before_sha256": "abc",
                    "scenario": case_id, "finding_task_id": finding_task_id,
                })},
                "freeze-task-revision-scope": {
                    "frozen_scope": json.dumps({"findings": [], "eligible_task_owners": {},
                                                 "permitted_added_task_owner": "FlowKit-Tasker"}),
                    "scope_sha256": "scope-digest",
                },
                "revise-task-plan": {"tasker_result_json": json.dumps({"revision_state": "updated", "finding_ids": ["F020-R001"]})},
                "review-task-revision-scope": {"semantic_review": json.dumps({"state": "approved"})},
                "validate-task-revision": {"state": "ready"},
            }
            with self.subTest(case_id=case_id):
                rendered = render_switch(self.controller, task_revision_route,
                    {"integration": "codex", "feature_context": "specs/020-example"}, outputs)
                selected = self.controller.select_switch_branch(rendered, choice)
                self.assertEqual([step["id"] for step in expected], [step["id"] for step in selected])
        rendered_outcome = render_switch(
            self.controller, route, {"integration": "codex", "feature_context": "specs/020-example"}, outputs
        )
        selected_outcome = self.controller.select_switch_branch(rendered_outcome, "continue")
        self.assertEqual([step["id"] for step in continue_branch], [step["id"] for step in selected_outcome])

    def testTaskRevisionBranchRetainsFreshReviewAndZeroProgressRequirements(self) -> None:
        loop = find_step(self.workflow["steps"], "implementation-loop")
        self.assertIsNotNone(loop)
        body_ids = {step["id"] for step in loop["steps"]}
        self.assertIn("assess-implementation-after-pass", body_ids)
        self.assertIn("implement-tasks", body_ids)
        self.assertTrue(any(step.get("id") == "assess-implementation-after-pass" for step in loop["steps"]))
        prompt = next(step for step in loop["steps"] if step.get("id") == "assess-implementation-after-pass")["prompt"]
        self.assertIn("task_revision_action", prompt)
        outcome = find_step(loop["steps"], "route-post-assessment")
        revision = outcome["cases"]["continue"][0]["cases"]["revise"]
        preflight_route = next(step for step in revision if step.get("id") == "route-task-revision-preflight")
        dispatch_route = next(step for step in preflight_route["cases"]["ready"]
                              if step.get("id") == "route-task-revision-snapshot")
        validation = next(step for step in dispatch_route["cases"]["ready"]
                          if step.get("id") == "validate-task-revision")
        self.assertIn("substantive_progress", validation["prompt"])
        self.assertIn("fresh independent", validation["prompt"])
        self.assertNotIn("assessment_before_correction", loop)
        self.assertEqual("implementation_scope", loop["controller_loop_mode"])
        self.assertEqual(5, loop["max_iterations"])

    def testRevisionPromptCarriesCurrentFindingAndSnapshotThroughProductionRenderer(self) -> None:
        loop = find_step(self.workflow["steps"], "implementation-loop")
        self.assertIsNotNone(loop)
        outcome = find_step(loop["steps"], "route-post-assessment")
        revision = outcome["cases"]["continue"][0]["cases"]["revise"]
        preflight_route = next(step for step in revision if step.get("id") == "route-task-revision-preflight")
        dispatch_route = next(step for step in preflight_route["cases"]["ready"]
                              if step.get("id") == "route-task-revision-snapshot")
        tasker = next(step for step in dispatch_route["cases"]["ready"]
                      if step.get("id") == "revise-task-plan")
        rendered = self.controller.render_template(tasker, {"feature_context": "specs/020-example", "integration": "codex"}, {
            "assess-implementation-after-pass": {
                "findings": [{"id": "F020-R001", "task_id": "T008", "exact_correction": "preserve pointer"}],
                "findings_json": '[{"id":"F020-R001","task_id":"T008","exact_correction":"preserve pointer"}]',
            },
            "prepare-task-revision": {
                "task_snapshot_json": '{"feature_directory":"specs/020-example","tasks_path":"specs/020-example/tasks.md","tasks_before_text":"- [X] T008 Correct prior issue","tasks_before_sha256":"abc","eligible_task_ids":["T008"]}',
            },
            "freeze-task-revision-scope": {
                "frozen_scope": '{"findings":[{"id":"F020-R001"}]}', "scope_sha256": "scope-digest",
            },
            "revise-task-plan": {"tasker_result_json": '{"revision_state":"updated","finding_ids":["F020-R001"]}'},
            "review-task-revision-scope": {"semantic_review": '{"state":"approved"}'},
            "validate-task-revision": {"state": "ready"},
        })
        self.assertIn("F020-R001", rendered["input"]["args"])
        self.assertIn("T008", rendered["input"]["args"])
        self.assertIn("tasks_before_sha256", rendered["input"]["args"])
        self.assertIn("task edits are not implementation progress", rendered["input"]["args"])
        semantic_step = next(step for step in dispatch_route["cases"]["ready"]
                             if step.get("id") == "review-task-revision-scope")
        self.assertIn("compare the actual before/after task text", semantic_step["prompt"])
        self.assertIn("Reject invented, omitted, substituted, wrong-owner, unrelated-scope", semantic_step["prompt"])
        self.assertNotIn("Feature 020", semantic_step["prompt"])
        rendered_semantic = self.controller.render_template(semantic_step, {"feature_context": "specs/031-consumer"}, {
            "prepare-task-revision": {"task_snapshot_json": json.dumps({
                "feature_directory": "specs/031-consumer", "specification_text": "The 031 consumer scope",
                "specification_sha256": "a" * 64,
            })},
            "freeze-task-revision-scope": {"frozen_scope": "approved-scope", "scope_sha256": "scope-31"},
            "revise-task-plan": {"tasker_result_json": "result"},
        })
        self.assertIn("specs/031-consumer", rendered_semantic["prompt"])
        self.assertIn("The 031 consumer scope", rendered_semantic["prompt"])

    def testUnavailableOrInvalidTaskerAssignmentFailsWorkflowPreflight(self) -> None:
        changed = yaml.safe_load((ROOT / "workflows/speckit-flow-implement/workflow.yml").read_text())
        loop = find_step(changed["steps"], "implementation-loop")
        self.assertIsNotNone(loop)
        outcome = find_step(loop["steps"], "route-post-assessment")
        tasker = find_step(changed["steps"], "revise-task-plan")
        tasker["flow_kit"]["agent"] = "FlowKit-Unreviewed"
        with self.assertRaisesRegex(ValueError, "unknown or invalid Codex agent"):
            self.controller.collect_agent_assignments(changed["steps"])

    def testRepeatedFindingNoProgressAndPassCapRemainExactStops(self) -> None:
        loop = find_step(self.workflow["steps"], "implementation-loop")
        self.assertIsNotNone(loop)
        self.assertEqual(5, loop["max_iterations"])
        body_ids = {step["id"] for step in loop["steps"]}
        baseline = {"state": "continue", "next_step_id": "implement-tasks",
                    "remaining_ids": ["F020-R001"], "resolved_ids": []}
        repeated = {"state": "continue", "next_step_id": "implement-tasks",
                    "remaining_ids": ["F020-R001"], "resolved_ids": []}
        no_progress = self.controller.route_loop_assessment(
            repeated, iteration=2, previous_assessment=baseline,
            max_iterations=loop["max_iterations"], loop_body_step_ids=body_ids,
            assessment_before_correction=True,
        )
        self.assertEqual({"action": "blocked", "blocker": "no-progress"}, no_progress)
        resolved = {"state": "continue", "next_step_id": "implement-tasks",
                    "remaining_ids": ["F020-R002"], "resolved_ids": ["F020-R001"]}
        capped = self.controller.route_loop_assessment(
            resolved, iteration=5, previous_assessment=baseline,
            max_iterations=loop["max_iterations"], loop_body_step_ids=body_ids,
            assessment_before_correction=True,
        )
        self.assertEqual({"action": "blocked", "blocker": "loop-cap-exhausted"}, capped)


class TaskRevisionValidationTests(unittest.TestCase):
    """Only attributable, in-scope task edits pass the controller validator."""

    def setUp(self) -> None:
        self.controller = load_controller()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.feature = "specs/020-fixture"
        feature_dir = self.project / self.feature
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text("# Approved fixture scope\n", encoding="utf-8")
        self.tasks_path = feature_dir / "tasks.md"
        self.pointer = self.project / ".specify/feature.json"
        self.pointer.parent.mkdir()
        self.pointer.write_text(json.dumps({"feature_directory": self.feature}), encoding="utf-8")
        self.before = "- [X] T001 Keep verified implementation\n- [ ] T002 Existing open work\n"
        self.tasks_path.write_text(self.before, encoding="utf-8")
        self.frozen_scope = {
            "findings": [{"id": "F020-R001", "exact_correction": "Correct the absent-pointer activation regression."}],
            "eligible_task_owners": {"T002": "FlowKit-Tasker"},
            "permitted_added_task_owner": "FlowKit-Tasker",
            "tasker_owner": "FlowKit-Tasker",
            "approved_specification_sha256": hashlib.sha256(
                (feature_dir / "spec.md").read_bytes()).hexdigest(),
        }

    def payload(self, after: str, *, changed: dict | None = None, semantic_changes: dict | None = None) -> dict:
        self.tasks_path.write_text(after, encoding="utf-8")
        changed = changed or {}
        reopened_ids = changed.get("reopened_task_ids", [])
        added_ids = changed.get("added_task_ids", ["T003"])
        mapped_ids = sorted(set(reopened_ids + added_ids))
        result = {
            "revision_state": "updated",
            "feature_directory": self.feature,
            "tasks_path": f"{self.feature}/tasks.md",
            "tasks_before_sha256": hashlib.sha256(self.before.encode()).hexdigest(),
            "tasks_after_sha256": hashlib.sha256(after.encode()).hexdigest(),
            "finding_ids": ["F020-R001"],
            "task_mappings": [{"finding_id": "F020-R001", "task_ids": mapped_ids, "owner": "FlowKit-Tasker"}],
            "reopened_task_ids": reopened_ids,
            "added_task_ids": added_ids,
            "preserved_completed_task_ids": ["T001"],
        }
        result.update(changed)
        semantic_review = {
            "reviewer": "main-controller", "state": "approved", "finding_ids": ["F020-R001"],
            "task_ids": mapped_ids,
            "scope_sha256": self.controller.task_revision_scope_digest(
                self.feature, f"{self.feature}/tasks.md", self.frozen_scope),
            "rationale": "Every revised task is necessary for the frozen correction and remains in approved scope.",
        }
        semantic_review.update(semantic_changes or {})
        return {"feature_directory": self.feature, "tasks_path": f"{self.feature}/tasks.md",
                "tasks_before_text": self.before, "frozen_scope": self.frozen_scope,
                "semantic_review": semantic_review, "tasker_result": result}

    def testMissingInScopeCorrectionTask_isAcceptedWithoutProgressCredit(self) -> None:
        after = self.before + "- [ ] T003 [US1] Correct F020-R001 absent-pointer activation in tests/test_controller.py\n"
        result = self.controller.validate_task_revision(self.project, self.payload(after))
        self.assertEqual("ready", result["state"])
        self.assertEqual(["T003"], result["eligible_task_ids"])
        self.assertFalse(result["substantive_progress"])
        self.assertEqual(["T001"], result["preserved_completed_task_ids"])

    def testValidatedTaskerRevisionExtendsImmutableScopeByAppendOnlySuccessor(self) -> None:
        before_sha = hashlib.sha256(self.before.encode()).hexdigest()
        pointer_sha = hashlib.sha256(self.pointer.read_bytes()).hexdigest()
        spec_path = self.project / self.feature / "spec.md"
        spec_sha = hashlib.sha256(spec_path.read_bytes()).hexdigest()
        scope = {
            "schema_version": "1.0", "run_id": "revision-successor-test",
            "feature_directory": self.feature, "request_reference": "operator-request-1",
            "request_kind": "full-feature", "requested_task_ids": ["T002"],
            "task_records": [{"task_id": "T002", "marker": "unchecked", "description": "Existing open work",
                "description_sha256": hashlib.sha256(b"Existing open work").hexdigest()}],
            "input_digests": {".specify/feature.json": pointer_sha, f"{self.feature}/spec.md": spec_sha,
                f"{self.feature}/tasks.md": before_sha},
        }
        scope["scope_sha256"] = self.controller.implementation_scope_module._digest(scope)
        after = self.before + "- [ ] T003 [US1] Correct F020-R001 absent-pointer activation\n"
        revision_payload = self.payload(after)
        revision_payload.update({"requested_scope": scope, "retained_scope_sha256": scope["scope_sha256"],
            "trusted_request_reference": "operator-request-1", "task_tracking_successors": []})
        result = self.controller.validate_task_revision(self.project, revision_payload)
        self.assertEqual("ready", result["state"], result)
        self.assertEqual(scope["scope_sha256"], result["task_tracking_successor"]["scope_sha256"])
        self.assertEqual(before_sha, scope["input_digests"][f"{self.feature}/tasks.md"])
        rebound = self.controller.validate_implementation_scope(self.project, {
            "scope": scope, "trusted_request_reference": "operator-request-1",
            "retained_scope_sha256": scope["scope_sha256"],
            "task_tracking_successors": [result["task_tracking_successor"]],
        })
        self.assertEqual("ready", rebound["state"], rebound)
        self.assertEqual(["T003"], rebound["tasker_derived_task_ids"])
        task_path = f"{self.feature}/tasks.md"
        task_evidence = [{"path": task_path, "sha256": hashlib.sha256(self.tasks_path.read_bytes()).hexdigest()}]
        classification = {"task_id": "T003",
            "task_description_sha256": hashlib.sha256(b"[US1] Correct F020-R001 absent-pointer activation").hexdigest(),
            "completion_kind": "substantive-implementation", "requirement_ids": ["code"],
            "source_requirement_ids": ["code"], "scope_sha256": scope["scope_sha256"],
            "classification_evidence": task_evidence}
        eligibility = self.controller.validate_implementation_eligibility(self.project, {
            "scope": scope, "trusted_request_reference": "operator-request-1",
            "retained_scope_sha256": scope["scope_sha256"],
            "task_tracking_successors": [result["task_tracking_successor"]],
            "assessment": {"assessment_id": "derived-eligibility", "scope_sha256": scope["scope_sha256"],
                "predecessor_sha256": "e" * 64,
                "input_digests": {task_path: hashlib.sha256(self.tasks_path.read_bytes()).hexdigest()},
                "task_states": [
                    {"task_id": "T002", "state": "pending", "dependency_ids": [], "evidence": task_evidence,
                     "blocker": "source-task-not-selected", "resume_action": "resume-implementation", "proof_sha256": None},
                    {"task_id": "T003", "state": "eligible", "dependency_ids": [], "evidence": task_evidence,
                     "blocker": None, "resume_action": None, "proof_sha256": None}],
                "eligible_task_ids": ["T003"], "pending_task_ids": ["T002"], "global_blockers": [],
                "iteration": 1, "evidence": task_evidence},
            "proofs": {}, "proof_requirements": {"T003": ["code"]},
            "completion_classifications": {"T003": classification},
            "source_requirement_ids": {"T003": ["code"]},
            "retained_predecessor_sha256": "e" * 64})
        self.assertEqual("ready", eligibility["state"], eligibility)
        self.assertEqual(["T003"], eligibility["eligibility"]["eligible_task_ids"])

    def testCompletedCorrectionTaskCanBeReopenedWithFindingAndHistoryPreserved(self) -> None:
        self.before = "- [X] T001 Keep verified implementation\n- [X] T002 Existing task that needs F020-R001 correction\n"
        self.tasks_path.write_text(self.before, encoding="utf-8")
        after = "- [X] T001 Keep verified implementation\n- [ ] T002 Existing task that needs F020-R001 correction\n"
        result = self.controller.validate_task_revision(self.project, self.payload(
            after, changed={"reopened_task_ids": ["T002"], "added_task_ids": [], "preserved_completed_task_ids": ["T001"]}
        ))
        self.assertEqual("ready", result["state"])
        self.assertEqual(["T002"], result["eligible_task_ids"])

    def testStaleDigestChangedIdentityDeletionAndUnrelatedEditAreBlocked(self) -> None:
        after = self.before + "- [ ] T003 [US1] Correct F020-R001 activation\n"
        payload = self.payload(after)
        payload["tasker_result"]["tasks_before_sha256"] = "0" * 64
        self.assertEqual("task-revision-digest-mismatch", self.controller.validate_task_revision(self.project, payload)["reason_code"])

        payload = self.payload(after)
        payload["tasks_path"] = "specs/021-other/tasks.md"
        self.assertEqual("task-revision-path-out-of-scope", self.controller.validate_task_revision(self.project, payload)["reason_code"])

        duplicate_task = self.before + "- [ ] T003 [US1] Correct F020-R001 activation\n- [ ] T003 [US1] Duplicate F020-R001 task\n"
        payload = self.payload(duplicate_task)
        self.assertEqual("task-revision-validation-failed", self.controller.validate_task_revision(self.project, payload)["reason_code"])

        payload = self.payload("# Changed accepted plan heading\n" + self.before + "- [ ] T003 [US1] Correct F020-R001 activation\n")
        self.assertEqual("task-revision-unrelated-document-content-changed", self.controller.validate_task_revision(self.project, payload)["reason_code"])

        payload = self.payload(after)
        self.pointer.write_text(json.dumps({"feature_directory": "specs/021-other"}), encoding="utf-8")
        self.assertEqual("task-revision-feature-identity-changed", self.controller.validate_task_revision(self.project, payload)["reason_code"])

        self.pointer.write_text(json.dumps({"feature_directory": self.feature}), encoding="utf-8")
        payload = self.payload("- [X] T001 Keep verified implementation\n- [ ] T003 [US1] Correct F020-R001 activation\n")
        self.assertEqual("task-revision-history-deleted", self.controller.validate_task_revision(self.project, payload)["reason_code"])

        payload = self.payload("- [ ] T001 altered F020-R001\n- [ ] T002 Existing open work\n- [ ] T003 [US1] Correct F020-R001 activation\n")
        self.assertEqual("task-revision-unrelated-task-changed", self.controller.validate_task_revision(self.project, payload)["reason_code"])

        payload = self.payload(self.before + "- [ ] T003 [US1] Correct F020-R001 activation\n")
        self.tasks_path.write_text("- [ ] T003 [US1] Correct F020-R001 activation\n" + self.before, encoding="utf-8")
        payload["tasker_result"]["tasks_after_sha256"] = hashlib.sha256(self.tasks_path.read_bytes()).hexdigest()
        self.assertEqual("task-revision-task-id-renumbered", self.controller.validate_task_revision(self.project, payload)["reason_code"])

    def testFrozenFindingCoverageRejectsInventedOmittedAndSubstitutedFindings(self) -> None:
        after = self.before + "- [ ] T003 [US1] Correct F020-R001 absent-pointer activation\n"
        for finding_ids, expected_reason in (
            (["F020-R999"], "task-revision-finding-snapshot-mismatch"),
            ([], "task-revision-findings-invalid"),
            (["F020-R002"], "task-revision-finding-snapshot-mismatch"),
        ):
            with self.subTest(finding_ids=finding_ids):
                payload = self.payload(after, changed={"finding_ids": finding_ids})
                self.assertEqual(expected_reason, self.controller.validate_task_revision(self.project, payload)["reason_code"])

        for mappings in (
            [{"finding_id": "F020-R999", "task_ids": ["T003"], "owner": "FlowKit-Tasker"}],
            [],
            [{"finding_id": "F020-R002", "task_ids": ["T003"], "owner": "FlowKit-Tasker"}],
        ):
            with self.subTest(task_mappings=mappings):
                payload = self.payload(after, changed={"task_mappings": mappings})
                self.assertEqual("task-revision-finding-mapping-mismatch",
                                 self.controller.validate_task_revision(self.project, payload)["reason_code"])

    def testFrozenOwnerAndIndependentSemanticReviewRejectWrongOwnerAndUnrelatedScope(self) -> None:
        after = self.before + "- [ ] T003 [US1] Correct F020-R001 absent-pointer activation\n"
        wrong_owner = self.payload(after, changed={"task_mappings": [
            {"finding_id": "F020-R001", "task_ids": ["T003"], "owner": "FlowKit-Coder"}
        ]})
        self.assertEqual("task-revision-wrong-owner", self.controller.validate_task_revision(self.project, wrong_owner)["reason_code"])

        unrelated = self.before + "- [ ] T003 [US1] F020-R001 replace unrelated governance and configuration\n"
        rejected_review = self.payload(unrelated, semantic_changes={
            "state": "rejected", "rationale": "The appended task is outside the frozen correction scope."
        })
        self.assertEqual("task-revision-semantic-review-required",
                         self.controller.validate_task_revision(self.project, rejected_review)["reason_code"])

    def testEligibleOwnerSnapshotAndSemanticScopeDigestMustRemainExact(self) -> None:
        self.before = "- [X] T001 Keep verified implementation\n- [X] T002 Existing F020-R001 correction task\n"
        self.tasks_path.write_text(self.before, encoding="utf-8")
        after = "- [X] T001 Keep verified implementation\n- [ ] T002 Existing F020-R001 correction task\n"
        payload = self.payload(after, changed={"reopened_task_ids": ["T002"], "added_task_ids": [],
                                               "preserved_completed_task_ids": ["T001"]})
        payload["frozen_scope"]["eligible_task_owners"]["T002"] = "FlowKit-Coder"
        self.assertEqual("task-revision-owner-snapshot-invalid", self.controller.validate_task_revision(self.project, payload)["reason_code"])

        self.frozen_scope["eligible_task_owners"]["T002"] = "FlowKit-Tasker"
        payload = self.payload(after, changed={"reopened_task_ids": ["T002"], "added_task_ids": [],
                                               "preserved_completed_task_ids": ["T001"]})
        payload["semantic_review"]["scope_sha256"] = "0" * 64
        self.assertEqual("task-revision-semantic-review-required", self.controller.validate_task_revision(self.project, payload)["reason_code"])

        payload = self.payload(after, changed={"reopened_task_ids": ["T002"], "added_task_ids": [],
                                               "preserved_completed_task_ids": ["T001"]})
        payload["frozen_scope"]["approved_specification_sha256"] = "b" * 64
        self.assertEqual("task-revision-semantic-review-required",
                         self.controller.validate_task_revision(self.project, payload)["reason_code"])

    def testLexicalTaskSymlinkToOtherFeatureIsRejectedBeforeResolvingAndPreservesOtherFile(self) -> None:
        after = self.before + "- [ ] T003 [US1] Correct F020-R001 activation\n"
        payload = self.payload(after)
        other_feature = self.project / "specs/021-other"
        other_feature.mkdir(parents=True)
        other_tasks = other_feature / "tasks.md"
        other_before = "- [X] T001 Other feature evidence\n"
        other_tasks.write_text(other_before, encoding="utf-8")
        self.tasks_path.unlink()
        self.tasks_path.symlink_to(other_tasks)
        pointer_before = self.pointer.read_bytes()
        result = self.controller.validate_task_revision(self.project, payload)
        self.assertEqual("task-revision-path-symlink", result["reason_code"])
        self.assertEqual(other_before, other_tasks.read_text(encoding="utf-8"))
        self.assertEqual(pointer_before, self.pointer.read_bytes())


class InstalledConsumerTaskRevisionTests(unittest.TestCase):
    """The literal workflow helper command works from the installed package path."""

    def testLiteralRenderedValidationCommandAcceptsAndRejectsConsumerRevision(self) -> None:
        controller = load_controller()
        workflow = yaml.safe_load((ROOT / "workflows/speckit-flow-implement/workflow.yml").read_text())
        loop = find_step(workflow["steps"], "implementation-loop")
        self.assertIsNotNone(loop)
        revise_steps = find_step(workflow["steps"], "route-task-revision-preflight")["cases"]["ready"]
        freeze = find_step(workflow["steps"], "freeze-task-revision-scope")
        validation = find_step(workflow["steps"], "validate-task-revision")
        preflight = find_step(workflow["steps"], "preflight-task-revision-snapshot")
        prompt = validation["prompt"]
        scope_match = re.search(r"`(python3 \.specify/flow-kit/scripts/python/controller\.py task-revision-scope)`", freeze["prompt"])
        preflight_match = re.search(r"`(python3 \.specify/flow-kit/scripts/python/controller\.py task-revision-preflight --project \"\$PWD\")`", preflight["prompt"])
        match = re.search(r"`(python3 \.specify/flow-kit/scripts/python/controller\.py validate-task-revision --project \"\$PWD\")`", prompt)
        self.assertIsNotNone(scope_match, "workflow must freeze scope with the installed helper before Tasker")
        self.assertIsNotNone(preflight_match, "workflow must run the installed preflight before reading tasks")
        self.assertIsNotNone(match, "workflow must name the literal installed helper command")
        scope_command = scope_match.group(1)
        preflight_command = preflight_match.group(1)
        command = match.group(1)

        with tempfile.TemporaryDirectory(prefix="flowkit-installed-controller-") as temporary:
            consumer = Path(temporary)
            for relative, source in controller_package_files().items():
                destination = consumer / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            installed_helper = consumer / ".specify/flow-kit/scripts/python/controller.py"
            self.assertTrue(installed_helper.is_file())
            self.assertFalse((consumer / "controllers/flow-kit/scripts/python/controller.py").exists())

            feature = consumer / "specs/020-consumer-fixture"
            feature.mkdir(parents=True)
            (feature / "spec.md").write_text("# Approved consumer fixture\n", encoding="utf-8")
            tasks_path = feature / "tasks.md"
            before = "- [X] T001 Preserved implementation\n- [ ] T002 Existing task\n"
            after = before + "- [ ] T003 [US1] Correct F020-R001 absent-pointer activation\n"
            tasks_path.write_text(after, encoding="utf-8")
            pointer = consumer / ".specify/feature.json"
            pointer.parent.mkdir(parents=True, exist_ok=True)
            pointer.write_text(json.dumps({"feature_directory": "specs/020-consumer-fixture"}), encoding="utf-8")
            preflight_payload = {"feature_directory": "specs/020-consumer-fixture",
                                 "tasks_path": "specs/020-consumer-fixture/tasks.md"}
            tasks_path.write_text(before, encoding="utf-8")
            safe_snapshot = subprocess.run(preflight_command, cwd=consumer, shell=True, text=True,
                                           input=json.dumps(preflight_payload), capture_output=True, check=False)
            self.assertEqual(0, safe_snapshot.returncode, safe_snapshot.stderr)
            snapshot_result = json.loads(safe_snapshot.stdout)
            self.assertEqual("ready", snapshot_result["state"])
            self.assertEqual(hashlib.sha256(before.encode()).hexdigest(), snapshot_result["tasks_before_sha256"])
            tasks_path.write_text(after, encoding="utf-8")
            immediate = subprocess.run(preflight_command, cwd=consumer, shell=True, text=True,
                                       input=json.dumps({**preflight_payload,
                                           "expected_tasks_sha256": snapshot_result["tasks_before_sha256"],
                                           "expected_specification_sha256": snapshot_result["specification_sha256"]}),
                                       capture_output=True, check=False)
            self.assertEqual("task-revision-digest-mismatch", json.loads(immediate.stdout)["reason_code"])
            frozen_scope = {
                "findings": [{"id": "F020-R001", "exact_correction": "Correct the absent-pointer activation regression."}],
                "eligible_task_owners": {"T002": "FlowKit-Tasker"},
                "permitted_added_task_owner": "FlowKit-Tasker", "tasker_owner": "FlowKit-Tasker",
                "approved_specification_sha256": snapshot_result["specification_sha256"],
            }
            tasks_path_relative = "specs/020-consumer-fixture/tasks.md"
            scope_result = subprocess.run(
                scope_command, cwd=consumer, shell=True, text=True,
                input=json.dumps({"feature_directory": "specs/020-consumer-fixture",
                                  "tasks_path": tasks_path_relative, "frozen_scope": frozen_scope}),
                capture_output=True, check=False,
            )
            self.assertEqual(0, scope_result.returncode, scope_result.stderr)
            scope_digest = json.loads(scope_result.stdout)["scope_sha256"]
            tasker_result = {
                "revision_state": "updated", "feature_directory": "specs/020-consumer-fixture",
                "tasks_path": tasks_path_relative,
                "tasks_before_sha256": hashlib.sha256(before.encode()).hexdigest(),
                "tasks_after_sha256": hashlib.sha256(after.encode()).hexdigest(),
                "finding_ids": ["F020-R001"],
                "task_mappings": [{"finding_id": "F020-R001", "task_ids": ["T003"], "owner": "FlowKit-Tasker"}],
                "reopened_task_ids": [], "added_task_ids": ["T003"],
                "preserved_completed_task_ids": ["T001"],
            }
            semantic_review = {
                "reviewer": "main-controller", "state": "approved", "finding_ids": ["F020-R001"],
                "task_ids": ["T003"],
                "scope_sha256": scope_digest,
                "rationale": "T003 addresses only the frozen correction.",
            }
            payload = {
                "feature_directory": "specs/020-consumer-fixture", "tasks_path": tasks_path_relative,
                "tasks_before_text": before, "frozen_scope": frozen_scope,
                "tasker_result": tasker_result, "semantic_review": semantic_review,
            }
            accepted = subprocess.run(command, cwd=consumer, shell=True, text=True, input=json.dumps(payload),
                                      capture_output=True, check=False)
            self.assertEqual(0, accepted.returncode, accepted.stderr)
            self.assertEqual("ready", json.loads(accepted.stdout)["state"])

            semantic_review["state"] = "rejected"
            rejected = subprocess.run(command, cwd=consumer, shell=True, text=True, input=json.dumps(payload),
                                      capture_output=True, check=False)
            self.assertEqual(0, rejected.returncode, rejected.stderr)
            self.assertEqual("task-revision-semantic-review-required", json.loads(rejected.stdout)["reason_code"])

            route = find_step(workflow["steps"], "route-task-revision-preflight")
            neighbor = consumer / "specs/021-neighbor"
            neighbor.mkdir(parents=True)
            neighbor_tasks = neighbor / "tasks.md"
            neighbor_spec = neighbor / "spec.md"
            neighbor_before = "- [X] T001 Neighbor evidence\\n"
            neighbor_tasks.write_text(neighbor_before, encoding="utf-8")
            neighbor_spec.write_text("# Neighbor scope\\n", encoding="utf-8")
            pointer_before = pointer.read_bytes()
            for case_name, unsafe_feature, make_alias in (
                ("task symlink", "specs/020-consumer-fixture", lambda: (tasks_path.unlink(), tasks_path.symlink_to(neighbor_tasks))),
                ("parent symlink", "specs/021-alias", lambda: (consumer / "specs/021-alias").symlink_to(neighbor, target_is_directory=True)),
            ):
                with self.subTest(case_name=case_name):
                    if unsafe_feature == "specs/021-alias":
                        pointer.write_text(json.dumps({"feature_directory": unsafe_feature}), encoding="utf-8")
                    current_pointer = pointer.read_bytes()
                    make_alias()
                    blocked = subprocess.run(preflight_command, cwd=consumer, shell=True, text=True,
                        input=json.dumps({"feature_directory": unsafe_feature, "tasks_path": f"{unsafe_feature}/tasks.md"}),
                        capture_output=True, check=False)
                    self.assertEqual(0, blocked.returncode, blocked.stderr)
                    blocked_result = json.loads(blocked.stdout)
                    self.assertEqual("task-revision-path-symlink", blocked_result["reason_code"])
                    rendered_route = render_switch(controller, route, {"feature_context": unsafe_feature}, {
                        "preflight-task-revision-snapshot": blocked_result,
                    })
                    stop_steps = controller.select_switch_branch(rendered_route, "blocked")
                    self.assertEqual(["stop-task-revision-preflight-blocked"], [item["id"] for item in stop_steps])
                    self.assertNotIn("revise-task-plan", [item["id"] for item in stop_steps])
                    self.assertEqual(neighbor_before, neighbor_tasks.read_text(encoding="utf-8"))
                    self.assertEqual(current_pointer, pointer.read_bytes())



if __name__ == "__main__":
    unittest.main()

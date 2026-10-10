"""Evidence-bound defect progress without premature parent-task completion."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / "controllers/flow-kit/scripts/python"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("progress_controller", SCRIPTS / "controller.py")
controller = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = controller
spec.loader.exec_module(controller)


class ImplementationProgressTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.feature = "specs/020-test"
        (self.root / ".specify").mkdir()
        (self.root / ".specify/feature.json").write_text(json.dumps({"feature_directory": self.feature}))
        target = self.root / self.feature
        target.mkdir(parents=True)
        (target / "spec.md").write_text("Reviewed scope\n")
        (target / "tasks.md").write_text("- [ ] T016 Implement both code corrections\n")
        (target / "helper.py").write_text("def result(): return 'bug'\n")
        self.path = f"{self.feature}/helper.py"
        self.findings = [self.finding("R001"), self.finding("R002")]
        self.capture = controller.capture_implementation_baseline(self.root, {
            "feature_directory": self.feature, "selected_task_ids": ["T016"], "findings": self.findings})
        self.assertEqual("ready", self.capture["state"])

    def evidence(self):
        return [{"path": self.path, "sha256": hashlib.sha256((self.root / self.path).read_bytes()).hexdigest()}]

    def finding(self, identifier):
        return {"id": identifier, "task_id": "T016", "artifact_location": self.path + ":1",
                "violated_requirement": "An exact recorded behavior", "observed_deficiency": identifier,
                "exact_correction": "Correct this behavior", "evidence": self.evidence()}

    def review(self, resolved=True):
        return {"reviewer": "FlowKit-Code Reviewer", "baseline_sha256": self.capture["baseline_sha256"],
                "findings": [{"id": x["id"], "task_id": "T016", "status": "resolved" if i == 0 and resolved else "unresolved",
                              "resolution_summary": "Original reproducer and regression now pass",
                              "evidence": self.evidence()} for i, x in enumerate(self.findings)],
                "new_findings": [], "completed_task_ids": []}

    def validate(self, review):
        return controller.validate_implementation_progress(self.root, {
            "baseline": self.capture["baseline"], "baseline_sha256": self.capture["baseline_sha256"], "review": review})

    def current_scope_payload(self):
        description = "Implement both code corrections"
        paths = [".specify/feature.json", f"{self.feature}/spec.md", f"{self.feature}/tasks.md"]
        scope = {"schema_version": "1.0", "run_id": "scoped-progress-test", "feature_directory": self.feature,
                 "request_reference": "trusted-test-request", "request_kind": "full-feature",
                 "requested_task_ids": ["T016"],
                 "task_records": [{"task_id": "T016", "marker": "unchecked", "description": description,
                                   "description_sha256": hashlib.sha256(description.encode()).hexdigest()}],
                 "input_digests": {path: hashlib.sha256((self.root / path).read_bytes()).hexdigest() for path in paths}}
        scope["scope_sha256"] = hashlib.sha256(
            json.dumps(scope, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        return {"scope": scope, "trusted_request_reference": "trusted-test-request",
                "retained_scope_sha256": scope["scope_sha256"]}

    def fix(self):
        (self.root / self.path).write_text("def result(): return 'one defect fixed'\n")

    def test_partialDefectClosureContinuesWithParentOpen(self):
        self.fix()
        result = self.validate(self.review())
        self.assertEqual("ready", result["state"])
        self.assertEqual(["finding:R001"], result["resolved_ids"])
        self.assertEqual(["task:T016", "finding:R002"], result["remaining_ids"])
        self.assertIn("[ ] T016", (self.root / self.feature / "tasks.md").read_text())
        current = {"state": "continue", "next_step_id": "implement-eligible-work",
                   "remaining_ids": result["remaining_ids"], "resolved_ids": result["resolved_ids"]}
        previous = {"remaining_ids": self.capture["remaining_ids"]}
        self.assertEqual("continue", controller.route_loop_assessment(
            current, iteration=2, max_iterations=5, loop_body_step_ids={"implement-eligible-work"},
            previous_assessment=previous)["action"])
        self.assertEqual("loop-cap-exhausted", controller.route_loop_assessment(
            current, iteration=5, max_iterations=5, loop_body_step_ids={"implement-eligible-work"},
            previous_assessment=previous)["blocker"])
        self.assertEqual(self.capture["baseline"]["findings"][1]["evidence"],
                         result["baseline"]["findings"][0]["evidence"])
        self.assertEqual(self.evidence(), result["baseline"]["findings"][0]["current_evidence"])

    def test_unresolvedSourceFixCanCloseAfterTestOnlyCorrection(self):
        original = copy.deepcopy(self.capture)
        self.fix()
        first = self.validate(self.review())
        self.assertEqual(["finding:R001"], first["resolved_ids"])
        frozen = copy.deepcopy(first)
        regression = self.root / self.feature / "regression.txt"
        regression.write_text("Both original reproducers now pass\n")
        evidence = self.evidence() + [{"path": regression.relative_to(self.root).as_posix(),
                                      "sha256": hashlib.sha256(regression.read_bytes()).hexdigest()}]
        following = {"reviewer": "FlowKit-Code Reviewer", "baseline_sha256": first["baseline_sha256"],
                     "findings": [{"id": "R002", "task_id": "T016", "status": "resolved",
                                   "resolution_summary": "Earlier source fix plus final regression substantiate closure",
                                   "evidence": evidence}], "new_findings": [], "completed_task_ids": []}
        second = controller.validate_implementation_progress(self.root, {
            "baseline": first["baseline"], "baseline_sha256": first["baseline_sha256"], "review": following})
        self.assertEqual("ready", second["state"])
        self.assertEqual(["finding:R002"], second["resolved_ids"])
        self.assertEqual(["task:T016"], second["remaining_ids"])
        self.assertEqual(frozen, first)
        self.assertEqual(original, self.capture)

    def test_legacyBaselineRecoveryRequiresRetainedDigestAndUnchangedFinding(self):
        origin = {key: copy.deepcopy(self.capture[key]) for key in ("baseline", "baseline_sha256")}
        self.fix()
        first = self.validate(self.review())
        legacy = copy.deepcopy(first["baseline"])
        finding = legacy["findings"][0]
        finding["evidence"] = finding.pop("current_evidence")
        digest = controller._progress_digest(legacy)
        review = {"reviewer": "FlowKit-Code Reviewer", "baseline_sha256": digest,
                  "findings": [{"id": "R002", "task_id": "T016", "status": "resolved",
                                "resolution_summary": "Original source effect and current reproducer verified",
                                "evidence": self.evidence()}], "new_findings": [], "completed_task_ids": []}
        payload = {"baseline": legacy, "baseline_sha256": digest, "review": review}
        self.assertEqual("blocked", controller.validate_implementation_progress(self.root, payload)["state"])
        payload["finding_source_baselines"] = [origin]
        result = controller.validate_implementation_progress(self.root, payload)
        self.assertEqual("ready", result["state"])
        self.assertEqual(["finding:R002"], result["resolved_ids"])
        invalid = copy.deepcopy(payload)
        invalid["finding_source_baselines"][0]["baseline_sha256"] = "0" * 64
        self.assertEqual("blocked", controller.validate_implementation_progress(self.root, invalid)["state"])
        invalid = copy.deepcopy(payload)
        historic = invalid["finding_source_baselines"][0]["baseline"]
        historic["findings"][1]["exact_correction"] = "An easier correction"
        invalid["finding_source_baselines"][0]["baseline_sha256"] = controller._progress_digest(historic)
        self.assertEqual("blocked", controller.validate_implementation_progress(self.root, invalid)["state"])
        invalid = copy.deepcopy(payload)
        historic = invalid["finding_source_baselines"][0]["baseline"]
        historic["feature_directory"] = "specs/999-other-feature"
        invalid["finding_source_baselines"][0]["baseline_sha256"] = controller._progress_digest(historic)
        self.assertEqual("blocked", controller.validate_implementation_progress(self.root, invalid)["state"])
        invalid = copy.deepcopy(payload)
        invalid["review"]["findings"][0]["evidence"][0]["sha256"] = "0" * 64
        self.assertEqual("blocked", controller.validate_implementation_progress(self.root, invalid)["state"])
        (self.root / self.path).write_text("def result(): return 'bug'\n")
        payload["review"]["findings"][0]["evidence"] = self.evidence()
        self.assertEqual("blocked", controller.validate_implementation_progress(self.root, payload)["state"])

    def test_unresolvedReviewAndTestEditsDoNotCreateSourceProgress(self):
        first = self.validate(self.review(resolved=False))
        self.assertFalse(first["substantive_progress"])
        test_path = self.root / self.feature / "new-test.txt"
        test_path.write_text("New test only\n")
        review = self.review(resolved=False)
        review["baseline_sha256"] = first["baseline_sha256"]
        for finding in review["findings"]:
            finding["status"] = "resolved"
        result = controller.validate_implementation_progress(self.root, {
            "baseline": first["baseline"], "baseline_sha256": first["baseline_sha256"], "review": review})
        self.assertEqual("blocked", result["state"])

    def testScopedProgressRejectsAdministrativeTaskResolutionAsSourceCredit(self):
        self.fix()
        review = self.review()
        review["findings"][1]["status"] = "resolved"
        review["task_completion_evidence"] = self.evidence()
        review["completed_task_ids"] = ["T016"]
        baseline = self.capture["baseline"]
        progress_payload = {"baseline": baseline, "baseline_sha256": self.capture["baseline_sha256"], "review": review}

        scope_payload = self.current_scope_payload()
        history = controller._empty_implementation_history(scope_payload["scope"])

        def append(event):
            nonlocal history
            event["scope_sha256"] = scope_payload["scope"]["scope_sha256"]
            event["predecessor_sha256"] = history["events"][-1]["sha256"] if history["events"] else "0" * 64
            event["evidence"] = self.evidence()
            event["sha256"] = hashlib.sha256(
                json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
            result = controller.append_implementation_execution_event(self.root, {
                **scope_payload, "event": event, "retained_history_sha256": history["sha256"]})
            self.assertEqual("ready", result["state"], result)
            history = result["history"]

        append({"event_id": "event-1", "event_kind": "coder-session-start",
                "declared_node_id": "implement-tasks", "occurred_at": "2026-10-08T12:00:00Z",
                "coder_session_id": "session-1", "coder_sessions_started": 1,
                "source_attempts_started": 0, "execution_kind": "first-source-execution"})
        append({"event_id": "event-2", "event_kind": "source-attempt-start",
                "declared_node_id": "implement-tasks", "occurred_at": "2026-10-08T12:00:01Z",
                "coder_session_id": "session-1", "coder_sessions_started": 1,
                "source_attempts_started": 1, "execution_kind": "first-source-execution"})
        append({"event_id": "event-3", "event_kind": "coder-session-outcome",
                "declared_node_id": "implement-tasks", "occurred_at": "2026-10-08T12:00:02Z",
                "coder_session_id": "session-1", "coder_sessions_started": 1,
                "source_attempts_started": 1, "outcome": "completed"})

        partial_payload = {"baseline": self.capture["baseline"],
                           "baseline_sha256": self.capture["baseline_sha256"], "review": self.review()}
        partial_progress = controller.validate_implementation_progress(self.root, partial_payload)
        current = {"state": "continue", "reason_code": "partial-finding-progress",
                   "evidence": self.evidence(), "remaining_ids": partial_progress["remaining_ids"],
                   "resolved_ids": partial_progress["resolved_ids"], "next_step_id": "implement-tasks"}
        spec_path = f"{self.feature}/spec.md"
        previous = {"state": "continue", "reason_code": "prior-work-remains",
                    "evidence": [{"path": spec_path, "sha256": hashlib.sha256((self.root / spec_path).read_bytes()).hexdigest()}],
                    "remaining_ids": self.capture["remaining_ids"], "resolved_ids": [],
                    "next_step_id": "implement-tasks"}
        scoped_payload = {
            "controller_loop_mode": "implementation_scope", **scope_payload, "assessment": current,
            "eligible_task_ids": ["T016"],
            "declared_node_ids": ["prepare-scoped-prerequisites", "implement-tasks"],
            "retained_history_sha256": history["sha256"], "previous_assessment": previous,
            "progress": partial_payload, "administrative_prerequisite_ids": [],
        }
        generic_route = controller.route_loop_assessment
        with patch.object(controller, "route_loop_assessment", wraps=generic_route) as predicate:
            routed = controller.validate_scoped_implementation_progress(self.root, scoped_payload)
        self.assertEqual("continue", routed["state"])
        self.assertEqual({"action": "continue", "next_step_id": "implement-tasks"}, routed["scoped_route"])
        self.assertEqual(1, predicate.call_count)
        actual = predicate.call_args.args[0]
        kwargs = predicate.call_args.kwargs
        self.assertEqual(partial_progress["resolved_ids"], actual["resolved_ids"])
        self.assertEqual(previous["remaining_ids"], kwargs["previous_assessment"]["remaining_ids"])

        progress = controller.validate_implementation_progress(self.root, progress_payload)
        self.assertEqual("ready", progress["state"])
        self.assertIn("task:T016", progress["resolved_ids"])
        self.assertEqual("blocked", controller.validate_scoped_implementation_progress(self.root, {
            "controller_loop_mode": "implementation_scope", "history": history,
            "assessment": {"resolved_ids": progress["resolved_ids"]},
            "eligible_task_ids": [], "declared_node_ids": ["prepare-scoped-prerequisites", "implement-tasks"],
            "retained_history_sha256": history["sha256"], "previous_assessment": {"resolved_ids": []},
            "progress": progress_payload, "administrative_prerequisite_ids": ["T016"],
        })["state"])
        self.assertEqual("administrative-proof-counted-as-source-progress",
                         controller.validate_scoped_implementation_progress(self.root, {
            "controller_loop_mode": "implementation_scope", **scope_payload,
            "assessment": {"resolved_ids": progress["resolved_ids"]},
            "eligible_task_ids": [], "declared_node_ids": ["prepare-scoped-prerequisites", "implement-tasks"],
            "retained_history_sha256": history["sha256"], "previous_assessment": {"resolved_ids": []},
            "progress": progress_payload, "administrative_prerequisite_ids": ["T016"],
        })["reason_code"])

    def test_unchangedSourceCannotClaimDefectClosure(self):
        self.assertEqual("blocked", self.validate(self.review())["state"])

    def test_newFindingsRemainOpenAndEarnNoRetrospectiveCredit(self):
        self.fix()
        review = self.review(False)
        review["new_findings"] = [self.finding("R003")]
        result = self.validate(review)
        self.assertFalse(result["substantive_progress"])
        self.assertIn("finding:R003", result["remaining_ids"])
        current = {"state": "continue", "next_step_id": "implement-eligible-work",
                   "remaining_ids": result["remaining_ids"], "resolved_ids": result["resolved_ids"]}
        self.assertEqual("no-progress", controller.route_loop_assessment(
            current, iteration=2, max_iterations=5, loop_body_step_ids={"implement-eligible-work"},
            previous_assessment={"remaining_ids": self.capture["remaining_ids"]})["blocker"])

    def test_omittedRenamedOwnerChangedOrInventedResolutionRejects(self):
        self.fix()
        for change in (lambda r: r["findings"].pop(),
                       lambda r: r["findings"][0].update(id="renamed"),
                       lambda r: r["findings"][0].update(task_id="T999"),
                       lambda r: r["findings"].append({"id": "new", "status": "resolved"})):
            with self.subTest(change=change):
                review = self.review()
                change(review)
                self.assertEqual("blocked", self.validate(review)["state"])

    def test_parentCompletionCannotHideRemainingDefect(self):
        self.fix()
        review = self.review()
        review["completed_task_ids"] = ["T016"]
        review["task_completion_evidence"] = self.evidence()
        self.assertEqual("blocked", self.validate(review)["state"])

    def test_wrongReviewerStaleEvidenceAndScopeMutationReject(self):
        self.fix()
        review = self.review()
        review["reviewer"] = "FlowKit-Coder"
        self.assertEqual("blocked", self.validate(review)["state"])
        review = self.review()
        (self.root / self.path).write_text("Changed after independent review\n")
        self.assertEqual("blocked", self.validate(review)["state"])
        (self.root / self.feature / "spec.md").write_text("Scope changed\n")
        self.assertEqual("blocked", self.validate(self.review())["state"])

    def test_originalBaselineCannotBeRewrittenAfterCorrection(self):
        self.fix()
        self.capture["baseline"]["findings"][0]["observed_deficiency"] = "An invented easier gap"
        self.assertEqual("blocked", self.validate(self.review())["state"])

    def test_unreviewedCheckedMarkerCannotErasePendingTaskOnNextPass(self):
        self.fix()
        (self.root / self.feature / "tasks.md").write_text("- [X] T016 Implement both code corrections\n")
        review = self.review()
        for item in review["findings"]:
            item["status"] = "resolved"
        first = self.validate(review)
        self.assertEqual(["task:T016"], first["remaining_ids"])
        following = {"reviewer": "FlowKit-Code Reviewer", "baseline_sha256": first["baseline_sha256"],
                     "findings": [], "new_findings": [], "completed_task_ids": []}
        second = controller.validate_implementation_progress(self.root, {"baseline": first["baseline"],
                   "baseline_sha256": first["baseline_sha256"], "review": following})
        self.assertEqual(["task:T016"], second["remaining_ids"])
        self.assertFalse(second["substantive_progress"])

    def test_validatedTaskerRevisionAdvancesWithoutTaskOnlyProgress(self):
        from tests.test_implement_task_revision import TaskRevisionValidationTests
        fixture = TaskRevisionValidationTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        source = fixture.project / fixture.feature / "helper.py"
        source.write_text("Recorded bug\n")
        path = f"{fixture.feature}/helper.py"
        evidence = [{"path": path, "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}]
        finding = {"id": "F020-R001", "task_id": "T001", "artifact_location": path + ":1",
                   "violated_requirement": "Correct the frozen regression", "observed_deficiency": "Bug",
                   "exact_correction": fixture.frozen_scope["findings"][0]["exact_correction"], "evidence": evidence}
        capture = controller.capture_implementation_baseline(fixture.project, {
            "feature_directory": fixture.feature, "selected_task_ids": ["T001"], "findings": [finding]})
        fixture.frozen_scope["eligible_task_owners"] = {"T001": "FlowKit-Tasker"}
        fixture.frozen_scope["approved_specification_sha256"] = capture["baseline"]["specification_sha256"]
        after = "- [ ] T001 Keep verified implementation — correct F020-R001 absent-pointer regression\n- [ ] T002 Existing open work\n"
        payload = fixture.payload(after, changed={"reopened_task_ids": ["T001"], "added_task_ids": [],
                                                "preserved_completed_task_ids": []})
        self.assertEqual("ready", controller.validate_task_revision(fixture.project, payload)["state"])
        transition = controller.advance_implementation_baseline(fixture.project, {
            "baseline": capture["baseline"], "baseline_sha256": capture["baseline_sha256"],
            "task_revision_payload": payload})
        self.assertEqual("ready", transition["state"])
        self.assertFalse(transition["substantive_progress"])
        self.assertEqual(capture["baseline"]["findings"], transition["baseline"]["findings"])
        source.write_text("Bug fixed\n")
        review = {"reviewer": "FlowKit-Code Reviewer", "baseline_sha256": transition["baseline_sha256"],
                  "findings": [{"id": "F020-R001", "task_id": "T001", "status": "resolved",
                                "resolution_summary": "Exact regression now passes", "evidence": [
                                    {"path": path, "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}]}],
                  "new_findings": [], "completed_task_ids": []}
        result = controller.validate_implementation_progress(fixture.project, {
            "baseline": transition["baseline"], "baseline_sha256": transition["baseline_sha256"], "review": review})
        self.assertEqual("ready", result["state"])
        self.assertEqual(["finding:F020-R001"], result["resolved_ids"])
        self.assertEqual(["task:T001"], result["remaining_ids"])

    def test_stableFindingIdSurvivesInstalledTaskerHandoffWithoutRenaming(self):
        from tests.test_implement_task_revision import TaskRevisionValidationTests
        from tools.catalog import controller_package_files
        import shutil

        fixture = TaskRevisionValidationTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        for relative, source in controller_package_files().items():
            destination = fixture.project / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        helper = fixture.project / ".specify/flow-kit/scripts/python/controller.py"

        def invoke(command, payload):
            args = [sys.executable, str(helper), command]
            if command != "task-revision-scope":
                args += ["--project", str(fixture.project)]
            result = subprocess.run(args, input=json.dumps(payload), text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr or result.stdout)
            return json.loads(result.stdout)

        identifier = "F020-RESUME-R002"
        source = fixture.project / fixture.feature / "helper.py"
        source.write_text("Recorded bug\n")
        path = f"{fixture.feature}/helper.py"
        finding = {"id": identifier, "task_id": "T001", "artifact_location": path + ":1",
                   "violated_requirement": "Correct the frozen regression", "observed_deficiency": "Bug",
                   "exact_correction": fixture.frozen_scope["findings"][0]["exact_correction"],
                   "evidence": [{"path": path, "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}]}
        capture = invoke("implementation-baseline", {"feature_directory": fixture.feature,
                         "selected_task_ids": ["T001"], "findings": [finding]})
        self.assertEqual("ready", capture["state"])
        fixture.frozen_scope["findings"][0]["id"] = identifier
        fixture.frozen_scope["eligible_task_owners"] = {"T001": "FlowKit-Tasker"}
        fixture.frozen_scope["approved_specification_sha256"] = capture["baseline"]["specification_sha256"]
        frozen = invoke("task-revision-scope", {"feature_directory": fixture.feature,
                        "tasks_path": f"{fixture.feature}/tasks.md", "frozen_scope": fixture.frozen_scope})
        self.assertIn("scope_sha256", frozen)
        # Reopening preserves the original description and appends the exact finding.
        after = fixture.before.replace("[X] T001 Keep verified implementation",
                                       f"[ ] T001 Keep verified implementation — correct {identifier}")
        revision = fixture.payload(after, changed={
            "finding_ids": [identifier], "task_mappings": [
                {"finding_id": identifier, "task_ids": ["T001"], "owner": "FlowKit-Tasker"}],
            "reopened_task_ids": ["T001"], "added_task_ids": [], "preserved_completed_task_ids": []},
            semantic_changes={"finding_ids": [identifier]})
        self.assertEqual("ready", invoke("validate-task-revision", revision)["state"])
        transition = invoke("implementation-baseline-transition", {
            "baseline": capture["baseline"], "baseline_sha256": capture["baseline_sha256"],
            "task_revision_payload": revision})
        self.assertEqual("ready", transition["state"])
        self.assertFalse(transition["substantive_progress"])
        self.assertEqual([finding], transition["baseline"]["findings"])
        source.write_text("Bug fixed\n")
        review = {"reviewer": "FlowKit-Code Reviewer", "baseline_sha256": transition["baseline_sha256"],
                  "findings": [{"id": identifier, "task_id": "T001", "status": "resolved",
                                "resolution_summary": "Exact regression now passes", "evidence": [
                                    {"path": path, "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}]}],
                  "new_findings": [], "completed_task_ids": []}
        result = invoke("implementation-progress", {"baseline": transition["baseline"],
                        "baseline_sha256": transition["baseline_sha256"], "review": review})
        self.assertEqual("ready", result["state"])
        self.assertEqual([f"finding:{identifier}"], result["resolved_ids"])
        self.assertEqual(["task:T001"], result["remaining_ids"])

    def test_blankOrNonStringFindingIdsAreRejectedByBothHelpers(self):
        from tests.test_implement_task_revision import TaskRevisionValidationTests
        fixture = TaskRevisionValidationTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        for identifier in (None, False, 20, "", " \t"):
            with self.subTest(identifier=identifier):
                finding = self.finding(identifier)
                capture = controller.capture_implementation_baseline(self.root, {
                    "feature_directory": self.feature, "selected_task_ids": ["T016"], "findings": [finding]})
                self.assertEqual("blocked", capture["state"])
                scope = copy.deepcopy(fixture.frozen_scope)
                scope["findings"][0]["id"] = identifier
                with self.assertRaises(ValueError):
                    controller.task_revision_scope_digest(fixture.feature, f"{fixture.feature}/tasks.md", scope)

    def test_sourceWorkflowUsesAutomaticCaptureAndValidation(self):
        import yaml
        workflow = yaml.safe_load((ROOT / "workflows/speckit-flow-implement/workflow.yml").read_text())
        controller.validate_workflow_graph(workflow["steps"])
        capture = next(x for x in workflow["steps"] if x["id"] == "capture-implementation-baseline")
        rendered = controller.render_template(capture, {"feature_context": self.feature}, {})
        self.assertIn("implementation-baseline", rendered["prompt"])
        self.assertLess([x["id"] for x in workflow["steps"]].index(capture["id"]),
                        [x["id"] for x in workflow["steps"]].index("route-readiness-before-core"))
        def find(nodes, identifier):
            for node in nodes:
                if node["id"] == identifier:
                    return node
                branches = [node.get("steps", [])] + list(node.get("cases", {}).values())
                for branch in branches:
                    match = find(branch, identifier)
                    if match:
                        return match
        assessor = find(workflow["steps"], "assess-implementation-after-pass")
        self.assertEqual("FlowKit-Code Reviewer", assessor["flow_kit"]["agent"])
        prompt = controller.render_template(assessor, {"feature_context": self.feature}, {})["prompt"]
        self.assertIn("implementation-progress", prompt)
        self.assertIn("even while its parent task remains open", prompt)
        self.assertNotIn("completed at least one previously unfinished task", prompt)

    def test_copiedControllerCLIProvesPartialClosure(self):
        import shutil
        target = self.root / ".specify/flow-kit/scripts/python"
        target.mkdir(parents=True)
        for source in SCRIPTS.glob("*.py"):
            shutil.copyfile(source, target / source.name)
        self.fix()
        result = subprocess.run([sys.executable, str(target / "controller.py"), "implementation-progress", "--project", str(self.root)],
                                input=json.dumps({"baseline": self.capture["baseline"],
                                                  "baseline_sha256": self.capture["baseline_sha256"], "review": self.review()}),
                                text=True, capture_output=True, check=True)
        self.assertEqual(["finding:R001"], json.loads(result.stdout)["resolved_ids"])


if __name__ == "__main__":
    unittest.main()

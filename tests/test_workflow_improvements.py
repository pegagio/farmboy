"""Regression tests for Feature 020 selection and activation contracts."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml


ROOT = Path(__file__).parents[1]
CONTROLLER_DIR = ROOT / "controllers/farmboy/scripts/python"
sys.path.insert(0, str(CONTROLLER_DIR))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class FeatureReferenceTests(unittest.TestCase):
    """Feature references resolve independently of menu order and generic gates."""

    def setUp(self) -> None:
        self.selection = load_module("farmboy_selection_test", CONTROLLER_DIR / "selection.py")
        self.entries = [
            {"id": "020", "title": "FarmBoy Workflow Iteration and Improvements"},
            {"id": "002", "title": "Clarify Specification"},
            {"id": "017", "title": "FarmBoy Agent Configuration"},
        ]

    def resolve(self, reference: str, kind: str = "auto", menu_order: list[str] | None = None):
        return self.selection.resolve_feature_reference(
            reference, kind, self.entries, menu_order or ["017", "020", "002"]
        ).to_dict()

    def test_stableFeatureIds_titles_andCanonicalAnswers_ignoreMenuReordering(self) -> None:
        reordered = ["017", "020", "002"]
        for reference in ("020", "20", "F020", "Feature 020", "Feature 20"):
            with self.subTest(reference=reference):
                result = self.resolve(reference, menu_order=reordered)
                self.assertEqual("selected", result["state"])
                self.assertEqual("020", result["selected_entry_id"])
                self.assertEqual("stable-id", result["match_method"])
        self.assertEqual("020", self.resolve("farmboy workflow iteration and improvements", "exact-title")["selected_entry_id"])
        self.assertEqual("020", self.resolve("020", "canonical-answer")["selected_entry_id"])

    def test_explicitMenuPositions_followPresentedOrder(self) -> None:
        reordered = ["017", "020", "002"]
        for reference in ("2", "option 2", "menu 2"):
            with self.subTest(reference=reference):
                result = self.resolve(reference, "menu-position", reordered)
                self.assertEqual("selected", result["state"])
                self.assertEqual("020", result["selected_entry_id"])
                self.assertEqual("menu-position", result["match_method"])

    def test_bareNumberWithConflictingIdAndMenuPosition_isAmbiguous(self) -> None:
        result = self.resolve("2")
        self.assertEqual("ambiguous", result["state"])
        self.assertEqual(["002", "020"], result["candidate_ids"])
        self.assertEqual("feature-reference-conflict", result["reason_code"])

    def test_duplicateTitleAndMalformedInventory_blockOrReportAmbiguity(self) -> None:
        self.entries.append({"id": "021", "title": "FarmBoy Workflow Iteration and Improvements"})
        result = self.resolve("FarmBoy Workflow Iteration and Improvements", "exact-title")
        self.assertEqual("ambiguous", result["state"])
        self.assertEqual({"020", "021"}, set(result["candidate_ids"]))
        invalid = self.selection.resolve_feature_reference("020", "stable-id", self.entries, ["unknown"])
        self.assertEqual("blocked", invalid.state)

    def test_unknownMissingAndDeferredReferences_neverSelectAnotherFeature(self) -> None:
        for reference, expected_state, expected_reason in (
            ("F999", "missing", "feature-reference-not-found"),
            ("", "missing", "feature-reference-missing"),
            ("defer", "blocked", "feature-selection-deferred"),
        ):
            with self.subTest(reference=reference):
                result = self.selection.resolve_feature_reference(reference, "auto", self.entries, ["020", "002", "017"])
                self.assertEqual(expected_state, result.state)
                self.assertEqual(expected_reason, result.reason_code)
                self.assertIsNone(result.selected_entry_id)

    def test_untrustedOrInferredRequest_isNotConvertedIntoSelectionAuthority(self) -> None:
        # Resolution is deterministic only after the main controller has established
        # the reference kind; an interest filter is deliberately not a resolver input.
        for reference in ("I am interested in workflow improvements", "maybe Feature 020"):
            result = self.resolve(reference, "exact-title")
            self.assertEqual("missing", result["state"])
            self.assertIsNone(result["selected_entry_id"])

    def test_resolveFeatureCli_returnsJsonWithoutProjectMutation(self) -> None:
        payload = json.dumps({
            "reference": "Feature 020", "reference_kind": "stable-id",
            "entries": self.entries, "menu_order": ["017", "020", "002"],
        })
        result = subprocess.run(
            [sys.executable, str(CONTROLLER_DIR / "controller.py"), "resolve-feature"],
            input=payload, text=True, capture_output=True, check=True,
        )
        self.assertEqual("020", json.loads(result.stdout)["selected_entry_id"])


class FeatureActivationTests(unittest.TestCase):
    """Activation revalidates a complete current snapshot before pointer writes."""

    def setUp(self) -> None:
        self.controller = load_module("farmboy_controller_feature_activation", CONTROLLER_DIR / "controller.py")
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name)
        metadata = self.project / ".specify/memory"
        metadata.mkdir(parents=True)
        (self.project / ".specify/feature.json").write_text('{"consumer_field":"keep"}\n', encoding="utf-8")
        self.roadmap = metadata / "roadmap.md"
        self.roadmap.write_text("roadmap snapshot\n", encoding="utf-8")
        self.spec_dir = self.project / "specs/020-farmboy-workflow-iteration-improvements"
        self.spec_dir.mkdir(parents=True)
        (self.spec_dir / "spec.md").write_bytes(b"existing spec bytes\n")
        self.entries = [
            {"id": "001", "title": "Foundation", "status": "verified", "feature_directory": "specs/001-foundation", "dependency_ids": [], "spec_sha256": None},
            {"id": "020", "title": "Workflow Improvements", "status": "planned", "feature_directory": "specs/020-farmboy-workflow-iteration-improvements", "dependency_ids": ["001"], "spec_sha256": hashlib.sha256((self.spec_dir / "spec.md").read_bytes()).hexdigest()},
        ]

    def snapshot(self) -> dict:
        pointer = self.project / ".specify/feature.json"
        exists = pointer.exists()
        return {
            "selected_entry_id": "020",
            "entries": self.entries,
            "menu_order": ["020", "001"],
            "roadmap_path": ".specify/memory/roadmap.md",
            "roadmap_sha256": hashlib.sha256(self.roadmap.read_bytes()).hexdigest(),
            "pointer_snapshot": {"state": "present" if exists else "absent",
                                 "sha256": hashlib.sha256(pointer.read_bytes()).hexdigest() if exists else None},
        }

    def test_firstAndRepeatActivation_preservePlannedStateAndExistingSpecBytes(self) -> None:
        snapshot = self.snapshot()
        first = self.controller.activate_selected_feature(self.project, snapshot)
        self.assertEqual("complete", first["state"])
        self.assertTrue(first["activation"]["changed"])
        self.assertEqual("planned", first["lifecycle_status"])
        self.assertEqual(b"existing spec bytes\n", (self.spec_dir / "spec.md").read_bytes())
        pointer = self.project / ".specify/feature.json"
        active = json.loads(pointer.read_text(encoding="utf-8"))
        self.assertEqual("keep", active["consumer_field"])
        self.assertEqual("specs/020-farmboy-workflow-iteration-improvements", active["feature_directory"])
        repeated = self.controller.activate_selected_feature(self.project, self.snapshot())
        self.assertEqual("complete", repeated["state"])
        self.assertFalse(repeated["activation"]["changed"])

    def test_firstActivationWithAbsentPointer_revalidatesAbsenceAndCreatesOnlyPointer(self) -> None:
        pointer = self.project / ".specify/feature.json"
        pointer.unlink()
        snapshot = self.snapshot()
        result = self.controller.activate_selected_feature(self.project, snapshot)
        self.assertEqual("complete", result["state"])
        self.assertEqual({"feature_directory": "specs/020-farmboy-workflow-iteration-improvements"},
                         json.loads(pointer.read_text(encoding="utf-8")))
        self.assertEqual(b"existing spec bytes\n", (self.spec_dir / "spec.md").read_bytes())

    def test_pointerAppearingAfterAbsentSnapshot_blocksWithoutOverwritingIt(self) -> None:
        pointer = self.project / ".specify/feature.json"
        pointer.unlink()
        snapshot = self.snapshot()
        pointer.write_text('{"other":"writer"}\n', encoding="utf-8")
        result = self.controller.prepare_feature_activation(self.project, snapshot)
        self.assertEqual("blocked", result["state"])
        self.assertEqual('{"other":"writer"}\n', pointer.read_text(encoding="utf-8"))

    def testStaleRoadmapPointerOrSpecificationSnapshot_blocksBeforeMutation(self) -> None:
        for stale_part in ("roadmap", "pointer", "spec"):
            with self.subTest(stale_part=stale_part):
                with tempfile.TemporaryDirectory() as temporary:
                    project = Path(temporary)
                    (project / ".specify/memory").mkdir(parents=True)
                    roadmap = project / ".specify/memory/roadmap.md"
                    roadmap.write_text("snapshot\n", encoding="utf-8")
                    (project / ".specify/feature.json").write_text("{}\n", encoding="utf-8")
                    target = project / "specs/020"
                    target.mkdir(parents=True)
                    spec = target / "spec.md"
                    spec.write_text("before\n", encoding="utf-8")
                    entries = [dict(self.entries[0]), dict(self.entries[1])]
                    entries[1].update(feature_directory="specs/020", spec_sha256=hashlib.sha256(spec.read_bytes()).hexdigest())
                    snapshot = {
                        "selected_entry_id": "020", "entries": entries, "menu_order": ["020", "001"],
                        "roadmap_path": ".specify/memory/roadmap.md", "roadmap_sha256": hashlib.sha256(roadmap.read_bytes()).hexdigest(),
                        "pointer_snapshot": {"state": "present", "sha256": hashlib.sha256((project / ".specify/feature.json").read_bytes()).hexdigest()},
                    }
                    if stale_part == "roadmap":
                        roadmap.write_text("changed\n", encoding="utf-8")
                    elif stale_part == "pointer":
                        (project / ".specify/feature.json").write_text('{"extra":true}\n', encoding="utf-8")
                    else:
                        spec.write_text("changed\n", encoding="utf-8")
                    result = self.controller.prepare_feature_activation(project, snapshot)
                    self.assertEqual("blocked", result["state"])
                    self.assertEqual("020", result["selected_entry_id"])

    def testDuplicateMappingUnmetDependencyLifecycleConflictAndUnsafePath_block(self) -> None:
        cases = []
        duplicate = self.snapshot()
        duplicate["entries"].append({"id": "021", "title": "Duplicate owner", "status": "planned", "feature_directory": self.entries[1]["feature_directory"], "dependency_ids": [], "spec_sha256": None})
        cases.append(("duplicate mapping", duplicate))
        unmet = self.snapshot()
        unmet["entries"][0]["status"] = "planned"
        cases.append(("unmet dependency", unmet))
        lifecycle = self.snapshot()
        lifecycle["entries"][1]["status"] = "abandoned"
        cases.append(("terminal lifecycle", lifecycle))
        unsafe = self.snapshot()
        unsafe["entries"][1]["feature_directory"] = "../outside"
        cases.append(("unsafe mapping", unsafe))
        for label, snapshot in cases:
            with self.subTest(case=label):
                result = self.controller.prepare_feature_activation(self.project, snapshot)
                self.assertEqual("blocked", result["state"])
                self.assertFalse((self.project / ".specify/feature.json").read_text().startswith('{"feature_directory"'))

    def test_competingSymlinkAliasToSelectedDirectory_blocksBeforeMutation(self) -> None:
        (self.project / "specs/020-alias").symlink_to(self.spec_dir, target_is_directory=True)
        snapshot = self.snapshot()
        snapshot["entries"].append({"id": "021", "title": "Alias owner", "status": "planned",
                                    "feature_directory": "specs/020-alias", "dependency_ids": [], "spec_sha256": None})
        pointer = self.project / ".specify/feature.json"
        before = pointer.read_bytes()
        result = self.controller.prepare_feature_activation(self.project, snapshot)
        self.assertEqual("blocked", result["state"])
        self.assertEqual(before, pointer.read_bytes())

    def testMalformedPointerAndPointerWriteFailure_preserveOriginalBytes(self) -> None:
        pointer = self.project / ".specify/feature.json"
        pointer.write_text("not json", encoding="utf-8")
        snapshot = self.snapshot()
        result = self.controller.prepare_feature_activation(self.project, snapshot)
        self.assertEqual("blocked", result["state"])
        self.assertEqual("not json", pointer.read_text(encoding="utf-8"))

        pointer.write_text('{"consumer_field":"keep"}\n', encoding="utf-8")
        snapshot = self.snapshot()
        with patch.object(self.controller.os, "replace", side_effect=PermissionError("fixture write failure")):
            with self.assertRaises(PermissionError):
                self.controller.activate_selected_feature(self.project, snapshot)
        self.assertEqual('{"consumer_field":"keep"}\n', pointer.read_text(encoding="utf-8"))

    def testPendingGovernanceAndInjectedAuthorizationFields_doNotChangeSnapshotAuthority(self) -> None:
        snapshot = self.snapshot()
        snapshot["authorization"] = {"trusted": True, "source": "child report"}
        result = self.controller.prepare_feature_activation(self.project, snapshot)
        self.assertEqual("ready", result["state"])
        self.assertNotIn("authorization", result)

    def testNoOpRoadmapPatchAndSameTarget_revalidationRemainNoOp(self) -> None:
        snapshot = self.snapshot()
        first = self.controller.activate_selected_feature(self.project, snapshot)
        self.assertEqual("complete", first["state"])
        pointer = self.project / ".specify/feature.json"
        before = pointer.read_bytes()
        second = self.controller.activate_selected_feature(self.project, self.snapshot())
        self.assertEqual("complete", second["state"])
        self.assertFalse(second["activation"]["changed"])
        self.assertEqual(before, pointer.read_bytes())

    def testSeparatelyRequestedPhase_isNotDispatchedByActivationHelper(self) -> None:
        result = self.controller.activate_selected_feature(self.project, self.snapshot())
        self.assertEqual("complete", result["state"])
        self.assertNotIn("next_workflow", result)

    def testAuthorizedSwitch_preservesUnrelatedPointerFieldsAndTargetBytes(self) -> None:
        entries = [dict(item) for item in self.entries]
        entries.append({
            "id": "021", "title": "Other Planned Feature", "status": "planned",
            "feature_directory": "specs/021-other", "dependency_ids": [], "spec_sha256": None,
        })
        snapshot = self.snapshot()
        snapshot.update(selected_entry_id="021", entries=entries, menu_order=["020", "021", "001"])
        activated = self.controller.activate_selected_feature(self.project, snapshot)
        self.assertEqual("complete", activated["state"])
        self.assertEqual("planned", activated["lifecycle_status"])
        pointer = json.loads((self.project / ".specify/feature.json").read_text(encoding="utf-8"))
        self.assertEqual("keep", pointer["consumer_field"])
        self.assertEqual("specs/021-other", pointer["feature_directory"])
        self.assertFalse((self.project / "specs/021-other").exists())


class FeatureWorkflowRoutingTests(unittest.TestCase):
    """The reviewed workflow keeps selection and consequential patch gates distinct."""

    def test_interestDoesNotSelect_andNoopPatchSkipsOnlyPatchApproval(self) -> None:
        workflow = yaml.safe_load((ROOT / "workflows/farmboy-select-feature/workflow.yml").read_text(encoding="utf-8"))
        self.assertIn("Do not select from interest alone", workflow["steps"][0]["prompt"])
        resolve = next(step for step in workflow["steps"] if step["id"] == "resolve-feature-request")
        self.assertIn("typed resolve-feature helper", resolve["prompt"])
        self.assertIn("without asking the operator to repeat the choice", resolve["prompt"])
        self.assertIn("ask one focused selection question", resolve["prompt"])
        intent_route = next(step for step in workflow["steps"] if step["id"] == "route-feature-intent")
        self.assertIn("selected", intent_route["cases"])
        self.assertEqual([], intent_route["cases"]["deferred"])
        route = next(step for step in intent_route["cases"]["selected"] if step.get("id") == "route-selection-readiness")["cases"]["ready"][0]
        self.assertEqual("route-required-roadmap-patch", route["id"])
        self.assertEqual(["false", "true"], list(route["cases"]))
        self.assertEqual("activate-selected-feature", route["cases"]["false"][0]["id"])
        self.assertFalse(any(step.get("type") == "gate" for step in route["cases"]["false"]))
        patch_gate = route["cases"]["true"][0]
        self.assertEqual("gate", patch_gate["type"])
        self.assertIn("exact roadmap patch", patch_gate["message"])
        patch_command = route["cases"]["true"][1]["cases"]["approve"][0]
        self.assertIn("{{ steps.prepare-feature-selection.output.proposed_patch }}", patch_command["input"]["args"])

    def testRenderedSelectionRoutes_directSkipsRepeatChoiceAndAmbiguousRequestAsksFocusedQuestion(self) -> None:
        workflow = yaml.safe_load((ROOT / "workflows/farmboy-select-feature/workflow.yml").read_text(encoding="utf-8"))
        controller = load_module("farmboy_controller_selection_routes", CONTROLLER_DIR / "controller.py")
        route = next(step for step in workflow["steps"] if step["id"] == "route-feature-intent")
        outputs = {
            "resolve-feature-request": {"state": "selected", "selected_entry_id": "020"},
            "prepare-feature-selection": {"state": "ready", "selected_entry_id": "020", "feature_brief": "brief",
                                          "proposed_patch": [], "feature_json": "{}", "patch_required": "false",
                                          "feature_directory": "specs/020-example"},
            "approve-feature-selection": {"choice": "approve"},
        }
        rendered = controller.render_template(route, {"integration": "codex", "feature_request": "Feature 020"}, outputs)
        direct = controller.select_switch_branch(rendered, "selected")
        self.assertEqual("prepare-feature-selection", direct[0]["id"])
        self.assertFalse(any(step.get("type") == "gate" for step in direct))
        self.assertEqual([], controller.select_switch_branch(rendered, "deferred"))

    def testRenderedPatchRoutes_useStringStatesThroughProductionRendererAndBranchSelector(self) -> None:
        workflow = yaml.safe_load((ROOT / "workflows/farmboy-select-feature/workflow.yml").read_text(encoding="utf-8"))
        controller = load_module("farmboy_controller_patch_routes", CONTROLLER_DIR / "controller.py")
        intent_route = next(step for step in workflow["steps"] if step["id"] == "route-feature-intent")
        readiness = next(step for step in intent_route["cases"]["selected"] if step["id"] == "route-selection-readiness")
        route = readiness["cases"]["ready"][0]
        outputs = {
            "prepare-feature-selection": {"patch_required": "false", "selected_entry_id": "020",
                                          "feature_brief": "brief", "proposed_patch": [],
                                          "feature_json": "{}", "feature_directory": "specs/020-example"},
            "approve-feature-selection": {"choice": "approve"},
        }
        rendered = controller.render_template(route, {"integration": "codex"}, outputs)
        for choice, expected_step in (("false", "activate-selected-feature"),
                                      ("true", "approve-feature-selection")):
            with self.subTest(choice=choice):
                branch = controller.select_switch_branch(rendered, choice)
                self.assertEqual(expected_step, branch[0]["id"])
                if choice == "false":
                    self.assertFalse(any(item.get("type") == "gate" for item in branch))
                else:
                    self.assertEqual("gate", branch[0]["type"])


class ReadinessEnvelopeCompatibilityTests(unittest.TestCase):
    """Readiness detail remains separate from the controller's strict outcome envelope."""

    def test_readinessPayloadIsNotAcceptedAsAnOutcomeEnvelopeField(self) -> None:
        controller = load_module("farmboy_controller_readiness_envelope", CONTROLLER_DIR / "controller.py")
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            evidence = project / "spec.md"
            evidence.write_text("current\n", encoding="utf-8")
            valid = {
                "state": "complete", "reason_code": "readiness-current",
                "evidence": [{"path": "spec.md", "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest()}],
                "remaining_ids": [], "resolved_ids": [],
            }
            self.assertEqual(valid, controller.validate_outcome_envelope(valid, project, {"assess"}))
            with self.assertRaisesRegex(ValueError, "unsupported fields"):
                controller.validate_outcome_envelope(
                    {**valid, "readiness_report": {"state": "ready"}}, project, {"assess"}
                )


class ImplementationProgressWorkflowTests(unittest.TestCase):
    """Production Implement routing permits independently verified partial progress."""

    def test_partialDefectResolutionKeepsParentOpenAndUsesGuardedReentry(self) -> None:
        controller = load_module("farmboy_controller_implementation_progress_route", CONTROLLER_DIR / "controller.py")
        workflow = yaml.safe_load((ROOT / "workflows/farmboy-implement/workflow.yml").read_text(encoding="utf-8"))

        def find_step(nodes, step_id):
            for node in nodes:
                if node.get("id") == step_id:
                    return node
                branches = [node.get("steps", []), node.get("default", [])]
                branches.extend(node.get("cases", {}).values())
                for branch in branches:
                    found = find_step(branch, step_id)
                    if found is not None:
                        return found
            return None

        loop = find_step(workflow["steps"], "implementation-loop")
        assessor = find_step(workflow["steps"], "assess-implementation-after-pass")
        outcome = find_step(workflow["steps"], "route-post-assessment")
        capture = find_step(workflow["steps"], "capture-post-pass-state")
        self.assertIsNotNone(loop)
        self.assertIsNotNone(assessor)
        self.assertIsNotNone(outcome)
        self.assertIsNotNone(capture)
        self.assertIn("Never substitute entry snapshots or read outputs from untaken branches", capture["prompt"])
        self.assertIn("task_tracking_successor", capture["prompt"])
        self.assertIn("controller.py post-pass-capture --project", capture["prompt"])
        for field in ("entry_history_sha256", "producer_pairs", "eligibility_request", "completion_branch"):
            self.assertIn(f"`{field}`", capture["prompt"])
        self.assertEqual(5, loop["max_iterations"])
        self.assertNotIn("assessment_before_correction", loop)
        self.assertEqual("implementation_scope", loop["controller_loop_mode"])
        rendered_assessor = controller.render_template(
            assessor, {"feature_context": "specs/020-example", "integration": "codex"},
            {"capture-implementation-baseline": {"baseline_json": '{"remaining_ids":["task:T016","finding:R001","finding:R002"]}',
                                                 "baseline_sha256": "a" * 64}},
        )
        self.assertIn("even while its parent task remains open", rendered_assessor["prompt"])
        self.assertIn("Return a review object", rendered_assessor["prompt"])

        partial = {
            "assess-implementation-after-pass": {
                "state": "continue", "task_revision_action": "skip",
                "remaining_ids": ["task:T016", "finding:R002"],
                "resolved_ids": ["finding:R001"],
            },
            "route-scoped-execution": {"state": "continue"},
            "gate-readiness-before-reentry": {"readiness_gate": {"state": "ready"}},
        }
        rendered_outcome = controller.render_template(
            {key: value for key, value in outcome.items() if key not in {"cases", "default"}},
            {"feature_context": "specs/020-example", "integration": "codex"}, partial,
        )
        rendered_outcome["cases"] = outcome["cases"]
        continued = controller.select_switch_branch(rendered_outcome, "continue")
        self.assertEqual("route-task-revision", continued[0]["id"])
        self.assertEqual("preflight-reviewed-task-tracking", continued[1]["id"])
        self.assertEqual("track-reviewed-task-outcomes", continued[2]["id"])
        self.assertEqual("validate-reviewed-task-tracking", continued[3]["id"])
        self.assertEqual("reassess-readiness-before-reentry", continued[4]["id"])
        revision = controller.render_template(
            {key: value for key, value in continued[0].items() if key not in {"cases", "default"}},
            {"integration": "codex"}, partial,
        )
        revision["cases"] = continued[0]["cases"]
        self.assertEqual([], controller.select_switch_branch(revision, "skip"))
        self.assertTrue(controller.evaluate_loop_condition(loop["condition"], partial))
        blocked_readiness = {**partial, "gate-readiness-before-reentry": {"readiness_gate": {"state": "blocked"}}}
        blocked_readiness["route-scoped-execution"] = {"state": "blocked"}
        self.assertFalse(controller.evaluate_loop_condition(loop["condition"], blocked_readiness))

    def test_scopedCallbackForwardsExactStateDependentReviewerEnvelope(self) -> None:
        controller = load_module("farmboy_controller_implementation_progress_envelope", CONTROLLER_DIR / "controller.py")
        workflow = yaml.safe_load((ROOT / "workflows/farmboy-implement/workflow.yml").read_text(encoding="utf-8"))
        def find_step(nodes, step_id):
            for node in nodes:
                if node.get("id") == step_id:
                    return node
                branches = [node.get("steps", []), node.get("default", [])]
                branches.extend(node.get("cases", {}).values())
                for branch in branches:
                    found = find_step(branch, step_id)
                    if found is not None:
                        return found
            return None

        execution = find_step(workflow["steps"], "route-scoped-execution")
        capture = find_step(workflow["steps"], "capture-post-pass-state")
        self.assertIsNotNone(capture)
        for envelope in (
            {"state": "continue", "next_step_id": "implement-tasks", "reason_code": "review-continue",
             "evidence": [], "remaining_ids": ["task:T001"], "resolved_ids": []},
            {"state": "blocked", "resume_action": "restore-owner-checkout", "reason_code": "owner-unavailable",
             "evidence": [], "remaining_ids": ["task:T001"], "resolved_ids": []},
            {"state": "complete", "reason_code": "all-work-complete", "evidence": [],
             "remaining_ids": [], "resolved_ids": ["task:T001"]},
        ):
            with self.subTest(state=envelope["state"]):
                rendered = controller.render_template(execution, {"feature_context": "specs/020-example", "integration": "codex"}, {
                    "route-scoped-entry": {"scope": {"scope_sha256": "a" * 64},
                        "retained_previous_assessment_sha256": "c" * 64,
                        "previous_assessment": {"state": "continue"}, "baseline": {"baseline_sha256": "b" * 64}},
                    "assess-implementation-after-pass": {"outcome_envelope": envelope, "review": {"reviewer": "FarmBoy Code Reviewer"}},
                    "gate-readiness-before-core": {"readiness_gate": {"state": "ready"}},
                    "capture-post-pass-state": {"post_pass_state": {"producer_records": []}},
                })
                rendered_packet = json.loads(rendered["prompt"].split("```json ", 1)[1].split(" ```", 1)[0])
                self.assertEqual(envelope, rendered_packet["current_assessment"])
                self.assertEqual("c" * 64, rendered_packet["retained_previous_assessment_sha256"])
                self.assertIn("Read the durable history file again", rendered["prompt"])
                self.assertIn("capture-post-pass-state.output.post_pass_state", rendered["prompt"])
                self.assertEqual({"producer_records": []}, rendered_packet["post_pass_state"])
                self.assertNotIn("route-scoped-entry.output.history", rendered["prompt"])
                self.assertNotIn("route-scoped-entry.output.task_tracking_successors", rendered["prompt"])


if __name__ == "__main__":
    unittest.main()

"""Workflow continuation, gate, and artifact-order checks across F014 stories."""

from __future__ import annotations

import argparse
import importlib.util
import hashlib
import io
import json
import sys
import tempfile
import unittest
from zipfile import ZipFile
from pathlib import Path
from typing import Any
from unittest.mock import patch

import yaml


ROOT = Path(__file__).parents[1]
WORKFLOWS = ROOT / "workflows"
CONTROLLER_PATH = ROOT / "controllers/flow-kit/scripts/python/controller.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_workflow(workflow_id: str) -> dict[str, Any]:
    return yaml.safe_load((WORKFLOWS / workflow_id / "workflow.yml").read_text(encoding="utf-8"))


def find_step(nodes: list[dict[str, Any]], step_id: str) -> dict[str, Any] | None:
    for node in nodes:
        if node.get("id") == step_id:
            return node
        for branch in node.get("cases", {}).values() if isinstance(node.get("cases"), dict) else []:
            found = find_step(branch, step_id)
            if found is not None:
                return found
        found = find_step(node.get("default", []), step_id)
        if found is not None:
            return found
        found = find_step(node.get("steps", []), step_id)
        if found is not None:
            return found
    return None


def commands(nodes: list[dict[str, Any]]) -> list[str]:
    result = []
    for node in nodes:
        if "command" in node:
            result.append(node["command"])
        elif node.get("type") == "switch":
            for branch in node.get("cases", {}).values():
                result.extend(commands(branch))
            result.extend(commands(node.get("default", [])))
        elif node.get("type") == "do-while":
            result.extend(commands(node.get("steps", [])))
    return result


def walk(nodes: list[dict[str, Any]]) -> list[tuple[dict[str, Any], str | None, str | None]]:
    result = []
    for node in nodes:
        result.append((node, None, None))
        for branch_id, branch in node.get("cases", {}).items() if isinstance(node.get("cases"), dict) else []:
            result.extend(walk(branch))
        result.extend(walk(node.get("default", [])))
        result.extend(walk(node.get("steps", [])))
    return result


class WorkflowPathTests(unittest.TestCase):
    """Corrective routes preserve ordering, re-assessment, and human authority."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.controller = load_module("flowkit_workflow_path_controller", CONTROLLER_PATH)

    def testAnalyzeUsesOneWaterfallAnalyzerAndAssessment(self) -> None:
        workflow = load_workflow("speckit-flow-analyze-remediate")
        loop, report = workflow["steps"]
        self.assertEqual("analysis-remediation-loop", loop["id"])
        self.assertTrue(loop["assessment_only_first_pass"])
        self.assertEqual(6, loop["max_iterations"])
        self.assertEqual("assess-analysis", loop["steps"][-1]["id"])
        self.assertEqual(["speckit.specify", "speckit.plan", "speckit.tasks", "speckit.analyze"], commands(workflow["steps"]))
        flags = ("spec_action", "plan_action", "task_action")
        expected = {
            "baseline": (["skip", "skip", "skip"], ["speckit.analyze"]),
            "specification": (["run", "run", "run"], ["speckit.specify", "speckit.plan", "speckit.tasks", "speckit.analyze"]),
            "plan": (["skip", "run", "run"], ["speckit.plan", "speckit.tasks", "speckit.analyze"]),
            "tasks": (["skip", "skip", "run"], ["speckit.tasks", "speckit.analyze"]),
        }
        for entry, (actions, expected_commands) in expected.items():
            with self.subTest(entry=entry):
                outputs = {"prepare-analysis-flowback": dict(zip(flags, actions))}
                observed = []
                for node in loop["steps"]:
                    if node.get("type") == "switch":
                        choice = self.controller.render_template(node["expression"], {}, outputs)
                        observed.extend(commands(self.controller.select_switch_branch(node, choice)))
                    elif "command" in node:
                        observed.append(node["command"])
                self.assertEqual(expected_commands, observed)
        assessor = loop["steps"][-1]
        self.assertIn("{{ steps.analyze-artifacts.output.report }}", assessor["prompt"])
        with self.assertRaisesRegex(ValueError, "unresolved step output reference"):
            self.controller.render_template(assessor["prompt"], {"feature_context": "014"}, {})
        self.assertNotIn("analysis_decision", workflow["inputs"])
        self.assertIn("required operator decision", report["prompt"])

    def testAssessmentOnlyFirstPassEstablishesBaselineOnce(self) -> None:
        baseline = {"state": "continue", "next_step_id": "remediate-tasks",
                    "remaining_ids": ["F001"], "resolved_ids": []}
        common = {"max_iterations": 6, "loop_body_step_ids": {"remediate-tasks"}}
        self.assertEqual("continue", self.controller.route_loop_assessment(
            baseline, iteration=1, assessment_only_first_pass=True, **common)["action"])
        for iteration, previous in ((1, baseline), (2, None), (2, baseline)):
            self.assertEqual("no-progress", self.controller.route_loop_assessment(
                baseline, iteration=iteration, previous_assessment=previous,
                assessment_only_first_pass=True, **common)["blocker"])
        self.assertEqual("no-progress", self.controller.route_loop_assessment(
            baseline, iteration=1, **common)["blocker"])
        self.assertEqual("complete", self.controller.route_loop_assessment(
            {"state": "complete"}, iteration=1, assessment_only_first_pass=True, **common)["action"])
        resolved = {"state": "continue", "next_step_id": "remediate-tasks",
                    "remaining_ids": ["F002"], "resolved_ids": ["F001"]}
        self.assertEqual("loop-cap-exhausted", self.controller.route_loop_assessment(
            resolved, iteration=6, previous_assessment=baseline,
            assessment_only_first_pass=True, **common)["blocker"])
        for node in (
            {"id": "invalid", "type": "prompt", "prompt": "x", "assessment_only_first_pass": True},
            {"id": "invalid", "type": "do-while", "assessment_only_first_pass": "true"},
        ):
            with self.assertRaisesRegex(ValueError, "assessment_only_first_pass"):
                self.controller.validate_workflow_graph([node])

    def testAssessmentOnlyBaselineCliFlag(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "tasks.md").write_text("Finding F001 remains", encoding="utf-8")
            assessment = {
                "state": "continue", "reason_code": "routine-task-gap",
                "evidence": [{"path": "tasks.md", "sha256": hashlib.sha256((project / "tasks.md").read_bytes()).hexdigest()}],
                "remaining_ids": ["F001"], "resolved_ids": [], "next_step_id": "remediate-tasks",
            }
            argv = ["route-loop", "--project", str(project), "--iteration", "1",
                    "--max-iterations", "6", "--loop-body-step", "remediate-tasks"]
            for flag, expected in (([], "blocked"), (["--assessment-only-first-pass"], "continue")):
                output = io.StringIO()
                with patch("sys.stdin", io.StringIO(json.dumps({"assessment": assessment}))), patch("sys.stdout", output):
                    self.assertEqual(0, self.controller.main(argv + flag))
                self.assertEqual(expected, json.loads(output.getvalue())["action"])

    def test_implementRepeatsExistingTasksOnlyWhileProgressIsVerified(self) -> None:
        workflow = load_workflow("speckit-flow-implement")
        steps = workflow["steps"]
        self.assertEqual(["assess-implementation-state", "implementation-continuation-loop", "report-implementation-outcome"], [step["id"] for step in steps])
        self.assertEqual("FlowKit-Reviewer", steps[0]["flow_kit"]["agent"])
        self.assertIn("progress baseline", steps[0]["prompt"])
        loop = steps[1]
        self.assertEqual("do-while", loop["type"])
        self.assertEqual(5, loop["max_iterations"])
        self.assertEqual(["implement-eligible-work", "assess-implementation-after-pass"], [step["id"] for step in loop["steps"]])
        self.assertEqual("{{ steps.assess-implementation-after-pass.output.state == 'continue' }}", loop["condition"])
        self.assertEqual(["speckit.implement"], commands(steps))
        self.assertEqual("FlowKit-Coder", loop["steps"][0]["flow_kit"]["agent"])
        self.assertEqual("FlowKit-Code Reviewer", loop["steps"][1]["flow_kit"]["agent"])
        self.assertNotIn("implementation_decision", workflow["inputs"])
        self.assertIn("all remaining eligible tasks", loop["steps"][0]["input"]["args"])
        self.assertIn("operator input is required", loop["steps"][0]["input"]["args"])
        self.assertIn("another speckit.implement session can safely proceed", loop["steps"][1]["prompt"])
        self.assertIn("Independently review the changed code", loop["steps"][1]["prompt"])
        self.assertIn("no remaining eligible task", loop["steps"][1]["prompt"])
        self.assertIn("successful command alone is not completion evidence", loop["steps"][1]["prompt"])
        self.assertIn("no-progress or five-pass safety stop", steps[2]["prompt"])

    def testLoopRoutingStopsForNoProgressAndCapButAcceptsCleanBeforeCorrectivePass(self) -> None:
        complete = {"state": "complete"}
        self.assertEqual({"action": "complete"}, self.controller.route_loop_assessment(
            complete, iteration=0, max_iterations=5, loop_body_step_ids={"correct"}
        ))
        initial = {"state": "continue", "next_step_id": "correct", "remaining_ids": ["T001"]}
        self.assertEqual({"action": "continue", "next_step_id": "correct"}, self.controller.route_loop_assessment(
            initial, iteration=0, max_iterations=5, loop_body_step_ids={"correct"}
        ))
        no_progress = {**initial, "evidence": [{"path": "tasks.md", "sha256": "f" * 64}]}
        self.assertEqual({"action": "blocked", "blocker": "no-progress"}, self.controller.route_loop_assessment(
            no_progress, iteration=1, max_iterations=5, loop_body_step_ids={"correct"}, previous_assessment=initial
        ))
        progress = {"state": "continue", "next_step_id": "correct", "remaining_ids": ["T002"], "resolved_ids": ["T001"]}
        self.assertEqual({"action": "continue", "next_step_id": "correct"}, self.controller.route_loop_assessment(
            progress, iteration=1, max_iterations=5, loop_body_step_ids={"correct"}, previous_assessment=initial
        ))
        self.assertEqual({"action": "blocked", "blocker": "loop-cap-exhausted"}, self.controller.route_loop_assessment(
            progress, iteration=5, max_iterations=5, loop_body_step_ids={"correct"}, previous_assessment=initial
        ))

    def testAnalyzeReportsConsequentialDecisionWithoutTakingAction(self) -> None:
        workflow = load_workflow("speckit-flow-analyze-remediate")
        assessment = find_step(workflow["steps"], "assess-analysis")
        self.assertIn("without taking the consequential action", assessment["prompt"])
        self.assertFalse(any(node.get("type") == "gate" for node, _, _ in walk(workflow["steps"])))
        self.assertFalse(any(command.startswith("speckit.flow-kit-") for command in commands(workflow["steps"])))

    def testManualAnalyzeAndImplementPathsMatchTheirContinuationContracts(self) -> None:
        readme = (ROOT / "workflows/README.md").read_text(encoding="utf-8")
        analyze = readme.split("## Manual analysis and remediation path", 1)[1].split("## Manual implementation path", 1)[0]
        implement = readme.split("## Manual implementation path", 1)[1].split("## Manual convergence path", 1)[0]
        for required in ("do not ask the operator to classify a routine result", "repeated findings", "no measurable progress", "five-pass safety cap", "smallest safe resumption action"):
            self.assertIn(required, analyze)
        self.assertIn("all remaining eligible tasks", implement)
        self.assertIn("required operator input", implement)
        self.assertIn("does not invoke Specify, Plan, Tasks, Analyze", implement)
        self.assertIn("If eligible tasks remain", implement)
        self.assertIn("five-pass safety cap", implement)
        self.assertIn("Leave Converge", implement)

    def testSpecificationUsesActiveTargetAndOnlyVerifiedLinksReachBrief(self) -> None:
        workflow = load_workflow("speckit-flow-specify")
        steps = workflow["steps"]
        self.assertEqual("inspect-active-feature", steps[0]["id"])
        self.assertNotIn("feature_request", workflow["inputs"])
        draft = find_step(steps, "draft-specification")["input"]["args"]
        self.assertIn("SPECIFY_FEATURE_DIRECTORY", draft)
        prepare = find_step(steps, "prepare-specification-request")["prompt"]
        self.assertIn("{{ steps.inspect-active-feature.output.actual_spec_dir }}", prepare)
        self.assertIn("{{ steps.retrieve-governing-context.output.report }}", prepare)
        linkage = find_step(steps, "route-created-spec-linkage")
        patch = find_step(steps, "route-spec-dir-patch-decision")
        outcome = find_step(steps, "route-specification-outcome")
        self.assertEqual(["apply-approved-spec-dir-patch", "verify-repaired-spec-linkage"], [n["id"] for n in patch["cases"]["approve-exact-patch"]])
        self.assertEqual({"repairable", "linked", "blocked"}, set(linkage["cases"]))
        for state in ("linked", "blocked"):
            self.assertEqual([], self.controller.select_switch_branch(linkage, state))
        self.assertTrue(self.controller.select_switch_branch(linkage, "repairable"))
        for choice in ("amend", "defer", "invalid"):
            self.assertEqual([], self.controller.select_switch_branch(patch, choice))
        self.assertEqual(["speckit.flow-roadmap.brief"], commands(outcome["cases"]["ready-for-brief"]))
        self.assertEqual([], self.controller.select_switch_branch(outcome, "blocked"))
        with self.assertRaises(ValueError):
            self.controller.select_switch_branch(outcome, "invalid")
        for step_id in ("route-active-feature", "route-specification-readiness"):
            route = find_step(steps, step_id)
            self.assertEqual([], self.controller.select_switch_branch(route, "blocked"))
            with self.assertRaises(ValueError):
                self.controller.select_switch_branch(route, "invalid")
            self.assertIn("speckit.specify", commands(self.controller.select_switch_branch(route, "ready")))
        self.assertIn("original active target", find_step(steps, "prepare-specification-outcome")["prompt"])
        self.assertFalse(any("select-roadmap-feature" == n["id"] for n, _, _ in walk(steps)))

    def testTransitionLabelsPreserveHumanChoiceRouting(self) -> None:
        for workflow_id, route_id, approval in (
            ("speckit-flow-select-feature", "route-selection-approval", "approve"),
            ("speckit-flow-specify", "route-spec-dir-patch-decision", "approve-exact-patch"),
        ):
            workflow = load_workflow(workflow_id)
            route = find_step(workflow["steps"], route_id)
            self.assertEqual({approval: "approved", "default": "not-approved"}, route["transition_labels"])
            self.assertIn("speckit.flow-roadmap.write", commands(self.controller.select_switch_branch(route, approval)))
            for choice in ("amend", "defer"):
                self.assertEqual([], self.controller.select_switch_branch(route, choice))
            self.controller.validate_workflow_graph(workflow["steps"])
            for labels in ({"missing-branch": "blocked"}, {approval: ""}, []):
                with self.subTest(labels=labels), self.assertRaises(ValueError):
                    self.controller.validate_workflow_graph([{**route, "transition_labels": labels}])

    def testStartFeatureListsCandidatesAndWaitsForExactHumanSelection(self) -> None:
        workflow = load_workflow("speckit-flow-select-feature")
        self.assertEqual("", self.controller.validate_required_inputs(workflow, {})["feature_request"])
        listing, gate, route = workflow["steps"][:3]
        outputs = {"list-roadmap-options": {
            "report": "Feature 29 -> Feature 28 -> Feature 26 (depends on). Feature 26 is ready.",
            "selection_options": ["026 — Foundation", "030 — Independent feature", "defer"]}}
        rendered = self.controller.render_template(gate, {}, outputs)
        self.assertEqual(outputs["list-roadmap-options"]["selection_options"], rendered["options"])
        self.assertIsInstance(rendered["options"], list)
        self.assertEqual("026 — Foundation", self.controller.validate_gate_choice(rendered, "1"))
        self.assertEqual("030 — Independent feature", self.controller.validate_gate_choice(rendered, "030 — Independent feature"))
        with self.assertRaises(ValueError):
            self.controller.validate_gate_choice(rendered, "029 — Blocked feature")
        with self.assertRaises(ValueError):
            self.controller.validate_gate_choice(rendered, "")
        self.assertEqual([], self.controller.select_switch_branch(route, "defer"))
        chosen = self.controller.validate_gate_choice(rendered, "2")
        selected = self.controller.select_switch_branch(route, chosen)
        self.assertEqual("prepare-feature-selection", selected[0]["id"])
        rendered_args = self.controller.render_template(selected[0]["prompt"], {},
            {"select-roadmap-feature": {"choice": chosen}})
        self.assertIn(chosen, rendered_args)
        self.assertIn("Do not substitute another candidate", selected[0]["prompt"])
        for required in ("direct_unlock_count", "downstream_dependent_count", "Deduplicate", "Missing references, cycles", "do not pick a candidate"):
            self.assertIn(required, listing["prompt"])
        no_candidates = self.controller.render_template(gate, {},
            {"list-roadmap-options": {"report": "No eligible candidates.", "selection_options": ["defer"]}})
        self.assertEqual("defer", self.controller.validate_gate_choice(no_candidates, "1"))
        for options in ([], ["duplicate", "duplicate"], [1], "not-an-array"):
            with self.subTest(options=options), self.assertRaises(ValueError):
                invalid = self.controller.render_template(gate, {},
                    {"list-roadmap-options": {"report": "Inventory", "selection_options": options}})
                self.controller.validate_gate_choice(invalid, "1")
        with self.assertRaisesRegex(ValueError, "unresolved step output reference"):
            self.controller.render_template(gate, {}, {})
        for malformed in ("invented-options", "{{ inputs.feature_request }}"):
            with self.assertRaises(ValueError):
                self.controller.validate_workflow_graph([{**gate, "options": malformed}])

    def testActivationWritesOnlyPointerAndPreservesExistingSpec(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            (project / ".specify").mkdir()
            pointer = project / ".specify/feature.json"
            pointer.write_text(json.dumps({"feature_directory": "specs/old", "consumer_field": "keep"}))
            result = self.controller.activate_feature(project, "specs/026-new")
            self.assertTrue(result["changed"])
            self.assertFalse((project / "specs").exists())
            self.assertEqual("keep", json.loads(pointer.read_text())["consumer_field"])
            target = project / "specs/026-new"
            target.mkdir(parents=True)
            spec = target / "spec.md"
            spec.write_bytes(b"Existing reviewed specification\n")
            before = spec.read_bytes()
            self.assertFalse(self.controller.activate_feature(project, "specs/026-new")["changed"])
            self.assertEqual(before, spec.read_bytes())
            self.assertEqual([], list((project / ".specify").glob(".feature-*")))
            self.assertEqual([pointer], list((project / ".specify").iterdir()))
            for unsafe in ("../escape", "/absolute", "specs/../escape", "specs//bad", ".specify/target", "specs/trailing/", ""):
                with self.subTest(unsafe=unsafe), self.assertRaises(ValueError):
                    self.controller.activate_feature(project, unsafe)
            with tempfile.TemporaryDirectory() as outside:
                (project / "escape").symlink_to(outside, target_is_directory=True)
                with self.assertRaises(ValueError):
                    self.controller.activate_feature(project, "escape/target")
            for invalid in (None, 42, ""):
                pointer.write_text(json.dumps({"feature_directory": invalid}))
                before = pointer.read_bytes()
                with self.assertRaises(ValueError):
                    self.controller.activate_feature(project, "specs/next")
                self.assertEqual(before, pointer.read_bytes())
            pointer.write_text("broken json")
            with self.assertRaises(ValueError):
                self.controller.activate_feature(project, "specs/next")
            self.assertEqual("broken json", pointer.read_text())

    def testSelectionApprovalSeparatesRoadmapAndPointerMutation(self) -> None:
        w = load_workflow("speckit-flow-select-feature")
        route = find_step(w["steps"], "route-selection-approval")
        self.assertEqual(["apply-selected-roadmap-patch", "activate-selected-feature", "verify-feature-selection"],
                         [n["id"] for n in route["cases"]["approve"]])
        for choice in ("amend", "defer", "invalid"):
            self.assertEqual([], self.controller.select_switch_branch(route, choice))
        readiness = find_step(w["steps"], "route-selection-readiness")
        self.assertEqual([], self.controller.select_switch_branch(readiness, "blocked"))
        with self.assertRaises(ValueError):
            self.controller.select_switch_branch(readiness, "invalid")
        gate = find_step(w["steps"], "approve-feature-selection")
        self.assertIn("feature_json", gate["message"])
        self.assertIn("proposed_patch", gate["message"])
        self.assertNotIn("speckit.specify", commands(w["steps"]))
        deprecated = load_workflow("speckit-flow-start-feature")
        self.assertTrue(deprecated["workflow"]["deprecated"])
        self.assertFalse(commands(deprecated["steps"]))

    def testRoadmapBriefResolverRequiresTheExplicitExactPairInDisposableFixtures(self) -> None:
        archive = ROOT / "catalog/packages/flow-roadmap-0.2.1.zip"
        with tempfile.TemporaryDirectory(prefix="flowkit-roadmap-linkage-") as temporary:
            fixture_root = Path(temporary).resolve()
            with ZipFile(archive) as bundle:
                for source in (
                    "flow-roadmap/scripts/python/load_config.py",
                    "flow-roadmap/scripts/python/review_contract.py",
                ):
                    destination = fixture_root / source
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(bundle.read(source))
            contract_path = fixture_root / "flow-roadmap/scripts/python/review_contract.py"
            contract = load_module("flowkit_linkage_review_contract", contract_path)

            target = "specs/014-flowkit-workflow-improvements/"
            selected_id = "014"
            feature_dir = fixture_root / target
            feature_dir.mkdir(parents=True)
            (feature_dir / "spec.md").write_text("# Fixture spec\n", encoding="utf-8")
            roadmap_path = fixture_root / ".specify/memory/roadmap.md"
            roadmap_path.parent.mkdir(parents=True)

            def resolve(mapping: str | None) -> dict[str, Any]:
                field = f"- **Spec dir**: `{mapping}`\n" if mapping is not None else ""
                roadmap_path.write_text(
                    "### 014 — Fixture Feature [status: in-progress]\n" + field,
                    encoding="utf-8",
                )
                arguments = argparse.Namespace(
                    roadmap_path=".specify/memory/roadmap.md",
                    spec_target=target,
                    roadmap_entry=selected_id,
                    ambient_feature=None,
                    selected_entry=None,
                )
                return contract.resolve_target(fixture_root, arguments)

            unique = resolve("specs/014-flowkit-workflow-improvements/")
            self.assertEqual("selected", unique["state"])
            self.assertEqual(selected_id, unique["entry"]["id"])
            self.assertEqual("exact-spec-dir", unique["match_method"])
            for mapping in (None, "specs/old-location/"):
                with self.subTest(mapping=mapping):
                    self.assertEqual("conflict", resolve(mapping)["state"])
                    # The fixture remains unmodified until the workflow's exact-patch gate approves.
                    approved_patch = "specs/014-flowkit-workflow-improvements/"
                    repaired = resolve(approved_patch)
                    self.assertEqual("selected", repaired["state"])
                    self.assertEqual(selected_id, repaired["entry"]["id"])

    def testClarifyRepeatsBoundedSessionsOnlyWhileFreshAmbiguityEvidenceProgresses(self) -> None:
        workflow = load_workflow("speckit-flow-clarify")
        steps = workflow["steps"]
        self.assertEqual("clarification-session-loop", steps[0]["id"])
        loop = find_step(steps, "clarification-session-loop")
        self.assertEqual(5, loop["max_iterations"])
        self.assertEqual(["clarify-session", "assess-clarification-after-session"],
                         [step["id"] for step in loop["steps"]])
        command = find_step(steps, "clarify-session")
        self.assertEqual("speckit.clarify", command["command"])
        self.assertIn("five-question cap per session", command["input"]["args"])
        self.assertIn("operator", command["input"]["args"])
        self.assertEqual(["speckit.clarify"], commands(loop["steps"]))
        self.assertEqual("clarification-outcome-stop", steps[-1]["id"])
        self.assertFalse(any(step.get("type") in {"switch", "gate"} for step in steps))
        self.assertFalse(any("speckit-flow-plan" in command for command in commands(steps)))

        initial = {"state": "continue", "next_step_id": "clarify-session", "remaining_ids": ["Q1", "Q2"]}
        progress = {"state": "continue", "next_step_id": "clarify-session", "remaining_ids": ["Q2"], "resolved_ids": ["Q1"]}
        self.assertEqual({"action": "continue", "next_step_id": "clarify-session"}, self.controller.route_loop_assessment(
            progress, iteration=1, max_iterations=5, loop_body_step_ids={"clarify-session"}
        ))
        self.assertEqual({"action": "blocked", "blocker": "no-progress"}, self.controller.route_loop_assessment(
            {**initial, "resolved_ids": []}, iteration=1, max_iterations=5, loop_body_step_ids={"clarify-session"}
        ))
        self.assertEqual({"action": "continue", "next_step_id": "clarify-session"}, self.controller.route_loop_assessment(
            {"state": "continue", "next_step_id": "clarify-session", "remaining_ids": ["Q3"], "resolved_ids": ["Q2"]},
            iteration=2, max_iterations=5, loop_body_step_ids={"clarify-session"}, previous_assessment=progress
        ))
        self.assertEqual({"action": "blocked", "blocker": "no-progress"}, self.controller.route_loop_assessment(
            {**initial, "resolved_ids": []}, iteration=1, max_iterations=5,
            loop_body_step_ids={"clarify-session"}, previous_assessment=initial
        ))
        self.assertEqual({"action": "blocked", "blocker": "loop-cap-exhausted"}, self.controller.route_loop_assessment(
            progress, iteration=5, max_iterations=5, loop_body_step_ids={"clarify-session"}, previous_assessment=initial
        ))

    def testPlanRetriesOnlyMissingOutputsWithExplicitGapFeedback(self) -> None:
        workflow = load_workflow("speckit-flow-plan")
        steps = workflow["steps"]
        self.assertEqual(["plan-output-loop", "report-plan-outcome"], [step["id"] for step in steps])
        loop = steps[0]
        self.assertEqual(5, loop["max_iterations"])
        self.assertEqual("{{ steps.verify-plan-output.output.state == 'continue' }}", loop["condition"])
        prepare, create, verify = loop["steps"]
        self.assertEqual(["prepare-plan-request", "create-plan", "verify-plan-output"],
                         [step["id"] for step in loop["steps"]])
        self.assertEqual(["speckit.plan"], commands(steps))
        self.assertEqual("FlowKit-Planner", create["flow_kit"]["agent"])
        self.assertEqual("FlowKit-Reviewer", verify["flow_kit"]["agent"])
        self.assertEqual("{{ steps.prepare-plan-request.output.args }}", create["input"]["args"])
        self.assertIn("latest verify-plan-output remaining_ids", prepare["prompt"])
        self.assertIn("{{ steps.prepare-plan-request.output.remaining_ids }}", verify["prompt"])
        self.assertIn("Independently review the planning outputs", verify["prompt"])
        initial = {"state": "continue", "next_step_id": "prepare-plan-request",
                   "remaining_ids": ["plan.md:technical-context", "research.md"], "resolved_ids": []}
        repaired = {**initial, "remaining_ids": ["research.md"], "resolved_ids": ["plan.md:technical-context"]}
        self.assertEqual("continue", self.controller.route_loop_assessment(
            repaired, iteration=1, max_iterations=5,
            loop_body_step_ids={"prepare-plan-request", "create-plan", "verify-plan-output"},
            previous_assessment=initial)["action"])
        self.assertEqual("no-progress", self.controller.route_loop_assessment(
            initial, iteration=2, max_iterations=5,
            loop_body_step_ids={"prepare-plan-request", "create-plan", "verify-plan-output"},
            previous_assessment=initial)["blocker"])
        self.assertIn("separate operator invocation", steps[1]["prompt"])

    def testTasksRetriesGenerationGapsAndPreservesTaskHistory(self) -> None:
        workflow = load_workflow("speckit-flow-tasks")
        loop, report = workflow["steps"]
        self.assertEqual("tasks-output-loop", loop["id"])
        self.assertEqual(5, loop["max_iterations"])
        self.assertEqual("{{ steps.verify-task-output.output.state == 'continue' }}", loop["condition"])
        prepare, generate, verify = loop["steps"]
        self.assertEqual(["prepare-task-request", "generate-tasks", "verify-task-output"],
                         [step["id"] for step in loop["steps"]])
        self.assertEqual(["speckit.tasks"], commands(workflow["steps"]))
        self.assertEqual("FlowKit-Tasker", generate["flow_kit"]["agent"])
        self.assertEqual("FlowKit-Reviewer", verify["flow_kit"]["agent"])
        self.assertEqual("{{ steps.prepare-task-request.output.args }}", generate["input"]["args"])
        self.assertIn("latest verify-task-output remaining_ids", prepare["prompt"])
        self.assertIn("{{ steps.prepare-task-request.output.remaining_ids }}", verify["prompt"])
        self.assertIn("{{ steps.prepare-task-request.output.task_history }}", verify["prompt"])
        self.assertIn("unchecked implementation tasks do not make task generation incomplete", verify["prompt"])
        self.assertIn("Independently review tasks.md", verify["prompt"])
        self.assertIn("lost task history", verify["prompt"])
        self.assertNotIn("task_decision", workflow["inputs"])
        self.assertIn("Analyze, and implementation require separate operator action", report["prompt"])
        initial = {"state": "continue", "next_step_id": "prepare-task-request",
                   "remaining_ids": ["tasks.md:US1", "tasks.md:dependencies"]}
        repaired = {**initial, "remaining_ids": ["tasks.md:dependencies"],
                    "resolved_ids": ["tasks.md:US1"]}
        body_ids = {step["id"] for step in loop["steps"]}
        self.assertEqual("continue", self.controller.route_loop_assessment(
            repaired, iteration=1, max_iterations=5, loop_body_step_ids=body_ids,
            previous_assessment=initial)["action"])
        self.assertEqual("no-progress", self.controller.route_loop_assessment(
            initial, iteration=1, max_iterations=5, loop_body_step_ids=body_ids,
            previous_assessment=initial)["blocker"])
        self.assertEqual("complete", self.controller.route_loop_assessment(
            {"state": "complete", "remaining_ids": []}, iteration=5, max_iterations=5,
            loop_body_step_ids=body_ids)["action"])

    def testConvergeAlwaysChecksBeforeSharedCorrectionAndReturnsAfterImplementation(self) -> None:
        workflow = load_workflow("speckit-flow-converge")
        loop, report = workflow["steps"]
        self.assertTrue(loop["assessment_before_correction"])
        self.assertNotIn("assessment_only_first_pass", loop)
        self.assertEqual(6, loop["max_iterations"])
        self.assertEqual(["append-task-remediation", "assess-convergence", "route-convergence-correction"],
                         [n["id"] for n in loop["steps"]])
        self.assertNotIn("convergence_decision", workflow["inputs"])
        flags = ("spec_action", "plan_action", "task_action")
        paths = {
            "clean": (["skip"] * 3, "complete", "complete", ["speckit.converge"]),
            "convergence-blocked": (["skip"] * 3, "blocked", "complete", ["speckit.converge"]),
            "convergence-question": (["skip"] * 3, "blocked", "complete", ["speckit.converge"]),
            "specification": (["run"] * 3, "continue", "continue", ["speckit.converge", "speckit.specify", "speckit.plan", "speckit.tasks", "speckit.analyze", "speckit.implement"]),
            "plan": (["skip", "run", "run"], "continue", "continue", ["speckit.converge", "speckit.plan", "speckit.tasks", "speckit.analyze", "speckit.implement"]),
            "tasks": (["skip", "skip", "run"], "continue", "continue", ["speckit.converge", "speckit.tasks", "speckit.analyze", "speckit.implement"]),
            "implementation-only": (["skip"] * 3, "continue", "continue", ["speckit.converge", "speckit.analyze", "speckit.implement"]),
            "no-eligible-work": (["skip"] * 3, "continue", "complete", ["speckit.converge", "speckit.analyze"]),
            "analysis-blocked": (["skip"] * 3, "continue", "blocked", ["speckit.converge", "speckit.analyze"]),
            "analysis-question": (["skip"] * 3, "continue", "blocked", ["speckit.converge", "speckit.analyze"]),
        }
        for name, (actions, convergence, eligibility, expected) in paths.items():
            with self.subTest(path=name):
                outputs = {"prepare-convergence-flowback": dict(zip(flags, actions)),
                           "assess-convergence": {"state": convergence},
                           "assess-remediation-eligibility": {"state": eligibility}}
                def selected_commands(nodes):
                    observed = []
                    for node in nodes:
                        if node.get("type") == "switch":
                            choice = self.controller.render_template(node["expression"], {}, outputs)
                            observed.extend(selected_commands(self.controller.select_switch_branch(node, choice)))
                        elif "command" in node:
                            observed.append(node["command"])
                    return observed
                self.assertEqual(expected, selected_commands(loop["steps"]))
        assessor = loop["steps"][1]
        self.assertEqual("FlowKit-Code Reviewer", assessor["flow_kit"]["agent"])
        self.assertIn("independently review implementation changes", assessor["prompt"])
        self.assertIn("otherwise return blocked", assessor["prompt"])
        with self.assertRaisesRegex(ValueError, "unresolved step output reference"):
            self.controller.render_template(assessor["prompt"], {"feature_context": "014"}, {})
        self.assertIn("fresh report", self.controller.render_template(assessor["prompt"], {"feature_context": "014"},
            {"append-task-remediation": {"report": "fresh report"}}))
        self.assertIn("Propagate any unresolved blocked", report["prompt"])
        self.assertIn("current-pass outcomes", report["prompt"])
        before = {"state": "continue", "next_step_id": "implement-remediation", "remaining_ids": ["G1", "G2"], "resolved_ids": []}
        after = {**before, "remaining_ids": ["G2"], "resolved_ids": ["G1"]}
        common = {"max_iterations": 6, "loop_body_step_ids": {"implement-remediation"}, "assessment_before_correction": True}
        self.assertEqual("continue", self.controller.route_loop_assessment(before, iteration=1, **common)["action"])
        self.assertEqual("continue", self.controller.route_loop_assessment(after, iteration=2, previous_assessment=before, **common)["action"])
        self.assertEqual("no-progress", self.controller.route_loop_assessment(before, iteration=2, previous_assessment=before, **common)["blocker"])
        self.assertEqual("loop-cap-exhausted", self.controller.route_loop_assessment(after, iteration=6, previous_assessment=before, **common)["blocker"])
        self.assertEqual("complete", self.controller.route_loop_assessment({"state": "complete"}, iteration=6, previous_assessment=before, **common)["action"])
        for state in ("blocked", "needs-human"):
            self.assertEqual(state, self.controller.route_loop_assessment(
                {"state": state, "resume_action": "resolve-finding"}, iteration=1, **common)["action"])
        with self.assertRaisesRegex(ValueError, "mutually exclusive"):
            self.controller.route_loop_assessment(before, iteration=1, assessment_only_first_pass=True, **common)


    def testUngatedLoopStatesStopForOperatorInputAndRetainLegacyGateRouting(self) -> None:
        import copy
        for purpose in ("clarify", "plan", "tasks", "implement", "analyze-remediate", "converge"):
            workflow = load_workflow("speckit-flow-" + purpose)
            self.controller.validate_workflow_graph(workflow["steps"])
            self.assertNotIn("needs-human", json.dumps(workflow))
            self.assertEqual({"action": "blocked", "resume_action": "answer-operator-question"},
                self.controller.route_loop_assessment(
                    {"state": "blocked", "resume_action": "answer-operator-question"},
                    iteration=1, max_iterations=5, loop_body_step_ids=set()))
        legacy = copy.deepcopy(load_workflow("speckit-flow-converge"))
        legacy["steps"][0]["steps"][2]["cases"]["needs-human"] = []
        self.controller.validate_workflow_graph(legacy["steps"])
        self.assertEqual({"action": "needs-human", "gate_step_id": "operator-review"},
            self.controller.route_loop_assessment(
                {"state": "needs-human", "gate_step_id": "operator-review"},
                iteration=1, max_iterations=5, loop_body_step_ids=set(),
                human_gate_step_ids={"operator-review"}))

    def testHeadAssessmentRequiresGuardedCorrectionAndCliFlag(self) -> None:
        import copy
        workflow = load_workflow("speckit-flow-converge")
        self.controller.validate_workflow_graph(workflow["steps"])
        for mutation in ("nonempty-clean", "wrong-expression", "baseline-mode", "wrong-position", "wrong-type", "boolean-condition"):
            changed = copy.deepcopy(workflow)
            loop = changed["steps"][0]
            if mutation == "nonempty-clean":
                loop["steps"][2]["cases"]["complete"] = [{"id": "unsafe", "command": "speckit.implement"}]
            elif mutation == "wrong-expression":
                loop["steps"][2]["expression"] = "{{ steps.assess-convergence.output.reason_code }}"
            elif mutation == "baseline-mode":
                loop["assessment_only_first_pass"] = True
            elif mutation == "wrong-position":
                loop["steps"].reverse()
            elif mutation == "wrong-type":
                loop["assessment_before_correction"] = "true"
            else:
                loop["condition"] = True
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.controller.validate_workflow_graph(changed["steps"])
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "tasks.md").write_text("Gap G1", encoding="utf-8")
            assessment = {"state": "continue", "reason_code": "implementation-gap",
                "evidence": [{"path": "tasks.md", "sha256": hashlib.sha256((project / "tasks.md").read_bytes()).hexdigest()}],
                "remaining_ids": ["G1"], "resolved_ids": [], "next_step_id": "implement-remediation"}
            argv = ["route-loop", "--project", str(project), "--iteration", "1", "--max-iterations", "6",
                    "--loop-body-step", "implement-remediation", "--assessment-before-correction"]
            output = io.StringIO()
            with patch("sys.stdin", io.StringIO(json.dumps({"assessment": assessment}))), patch("sys.stdout", output):
                self.assertEqual(0, self.controller.main(argv))
            self.assertEqual("continue", json.loads(output.getvalue())["action"])

    def testCloseoutUsesSharedWaterfallAndStopsBeforeCorrectionsWhenBlocked(self) -> None:
        workflow = load_workflow("speckit-flow-closeout")
        steps = workflow["steps"]
        self.controller.validate_workflow_graph(steps)
        self.assertNotIn("needs-human", json.dumps(workflow))
        loop = find_step(steps, "closeout-debrief-loop")
        self.assertTrue(loop["assessment_before_correction"])
        self.assertEqual(6, loop["max_iterations"])
        self.assertEqual(["debrief-roadmap", "assess-closeout-debrief", "route-closeout-correction"],
                         [n["id"] for n in loop["steps"]])
        self.assertEqual("FlowKit-Code Reviewer", loop["steps"][1]["flow_kit"]["agent"])
        self.assertIn("Independently review implementation changes", loop["steps"][1]["prompt"])
        self.assertIn("otherwise return blocked", loop["steps"][1]["prompt"])
        route = find_step(steps, "route-closeout-correction")
        for state in ("complete", "blocked"):
            self.assertEqual([], self.controller.select_switch_branch(route, state))
        correction = route["cases"]["continue"]
        flags = ("spec_action", "plan_action", "task_action")
        for name, actions, eligibility, expected in (
            ("spec", ["run"] * 3, "continue", ["speckit.specify", "speckit.plan", "speckit.tasks", "speckit.analyze", "speckit.implement"]),
            ("plan", ["skip", "run", "run"], "continue", ["speckit.plan", "speckit.tasks", "speckit.analyze", "speckit.implement"]),
            ("tasks", ["skip", "skip", "run"], "continue", ["speckit.tasks", "speckit.analyze", "speckit.implement"]),
            ("implementation", ["skip"] * 3, "continue", ["speckit.analyze", "speckit.implement"]),
            ("no-work", ["skip"] * 3, "complete", ["speckit.analyze"]),
            ("blocked", ["skip"] * 3, "blocked", ["speckit.analyze"]),
        ):
            outputs = {"prepare-closeout-flowback": dict(zip(flags, actions)),
                       "assess-closeout-task-eligibility": {"state": eligibility}}
            def selected(nodes):
                observed = []
                for n in nodes:
                    if "command" in n:
                        observed.append(n["command"])
                    elif n.get("type") == "switch":
                        choice = self.controller.render_template(n["expression"], {}, outputs)
                        observed.extend(selected(self.controller.select_switch_branch(n, choice)))
                return observed
            with self.subTest(path=name):
                self.assertEqual(expected, selected(correction))
        self.assertEqual(1, commands(steps).count("speckit.flow-roadmap.debrief"))
        eligibility_route = find_step(steps, "route-closeout-implementation")
        self.assertEqual([], eligibility_route["cases"]["blocked"])
        self.assertFalse(any("speckit.flow-roadmap.debrief" in commands(branch)
                             for branch in eligibility_route["cases"].values()))
        common = {"max_iterations": 6, "loop_body_step_ids": {"reconcile-closeout-tasks"},
                  "assessment_before_correction": True}
        before = {"state": "continue", "next_step_id": "reconcile-closeout-tasks", "remaining_ids": ["F1", "F2"], "resolved_ids": []}
        after = {**before, "remaining_ids": ["F2"], "resolved_ids": ["F1"]}
        self.assertEqual("continue", self.controller.route_loop_assessment(before, iteration=1, **common)["action"])
        self.assertEqual("continue", self.controller.route_loop_assessment(after, iteration=2, previous_assessment=before, **common)["action"])
        self.assertEqual("no-progress", self.controller.route_loop_assessment(before, iteration=2, previous_assessment=before, **common)["blocker"])
        self.assertEqual("loop-cap-exhausted", self.controller.route_loop_assessment(after, iteration=6, previous_assessment=before, **common)["blocker"])
        self.assertEqual("complete", self.controller.route_loop_assessment({"state": "complete"}, iteration=6, **common)["action"])
        self.assertEqual("blocked", self.controller.route_loop_assessment(
            {"state": "blocked", "resume_action": "answer-product-question"}, iteration=1, **common)["action"])

    def testCloseoutSharedMaintenanceRequiresVerificationAndCleanLintBeforeReview(self) -> None:
        steps = load_workflow("speckit-flow-closeout")["steps"]
        initial = find_step(steps, "route-initial-closeout")
        for state in ("complete", "blocked"):
            self.assertEqual([], self.controller.select_switch_branch(initial, state))
        preparation = find_step(steps, "prepare-roadmap-verification")
        self.assertNotIn("{{ steps.", preparation["prompt"])
        self.assertIn("without requiring a loop output", preparation["prompt"])
        roadmap = find_step(steps, "route-roadmap-verification")
        self.assertEqual([], roadmap["cases"]["already-verified"])
        self.assertEqual([], roadmap["cases"]["blocked"])
        patch_route = find_step(steps, "route-roadmap-transition")
        self.assertEqual(["speckit.flow-roadmap.write"], commands(patch_route["cases"]["approve-patch"]))
        for choice in ("return-to-workflow", "defer"):
            self.assertEqual([], self.controller.select_switch_branch(patch_route, choice))
        gate = find_step(steps, "approve-roadmap-transition")
        self.assertIn("proposed_patch", gate["message"])
        write = find_step(steps, "apply-approved-roadmap-verification")["input"]["args"]
        self.assertIn("SPEC_TARGET={{ inputs.feature_context }}", write)
        self.assertIn("proposed_patch", write)
        maintenance = find_step(steps, "prepare-wiki-maintenance")
        self.assertIn("already-verified", maintenance["prompt"])
        self.assertIn("freshly verified", maintenance["prompt"])
        wiki_route = find_step(steps, "route-wiki-maintenance")
        self.assertEqual([], wiki_route["cases"]["blocked"])
        self.assertEqual(["speckit.flow-wiki.ingest", "speckit.flow-wiki.lint"], commands(wiki_route["cases"]["ready"]))
        self.assertIsNone(find_step(steps, "route-commit-readiness"))
        self.assertIsNone(find_step(steps, "confirm-commit-readiness"))
        self.assertNotIn("commit_readiness_decision", load_workflow("speckit-flow-closeout")["inputs"])
        verification = find_step(steps, "verify-closeout-readiness")
        self.assertIn("ready-for-explicit-commit or blocked", verification["prompt"])
        self.assertEqual("verify-closeout-readiness", wiki_route["cases"]["ready"][-1]["id"])
        self.assertIn("latest verify-closeout-readiness result", steps[-1]["prompt"])
        self.assertIn("subsequent explicit operator request", steps[-1]["prompt"])
        self.assertEqual("report-closeout-outcome", steps[-1]["id"])
        self.assertEqual(1, sum(n.get("type") == "gate" for n, _, _ in walk(steps)))
        self.assertFalse(any(c.startswith("speckit-flow-") for c in commands(steps)))


    def testWikiRefreshRepeatsOnlyForResolvedGapsAndStopsForUntrustedEvidence(self) -> None:
        steps = load_workflow("speckit-flow-closeout")["steps"]
        self.controller.validate_workflow_graph(steps)
        loop = find_step(steps, "wiki-reconciliation-loop")
        self.assertEqual(5, loop["max_iterations"])
        self.assertEqual(["prepare-wiki-refresh", "ingest-curated-context", "lint-wiki", "assess-wiki-maintenance"],
                         [n["id"] for n in loop["steps"]])
        self.assertEqual("{{ steps.assess-wiki-maintenance.output.state == 'continue' }}", loop["condition"])
        self.assertEqual("{{ steps.prepare-wiki-refresh.output.source }}", loop["steps"][1]["input"]["args"])
        lint = loop["steps"][2]
        self.assertEqual("speckit.flow-wiki.lint", lint["command"])
        # Core lint interprets arguments as a page/check scope; empty runs every check.
        self.assertEqual("", self.controller.render_template(lint["input"]["args"], {}, {}))
        self.assertIn("already-authorized", loop["steps"][0]["prompt"])
        self.assertIn("baseline_remaining_ids", loop["steps"][-1]["prompt"])
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            evidence = project / "lint-report.md"
            evidence.write_text("G1 source coverage verified; G2 stale claim remains")
            current = {"state": "continue", "reason_code": "refresh-authorized-source",
                "evidence": [{"path": "lint-report.md", "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest()}],
                "remaining_ids": ["G2"], "resolved_ids": ["G1"], "next_step_id": "prepare-wiki-refresh"}
            body = {n["id"] for n in loop["steps"]}
            validated = self.controller.validate_outcome_envelope(current, project, body)
            common = {"max_iterations": 5, "loop_body_step_ids": body}
            self.assertEqual("continue", self.controller.route_loop_assessment(validated, iteration=1, **common)["action"])
            before = {**validated, "remaining_ids": ["G1", "G2"], "resolved_ids": []}
            self.assertEqual("continue", self.controller.route_loop_assessment(validated, iteration=2, previous_assessment=before, **common)["action"])
            self.assertEqual("no-progress", self.controller.route_loop_assessment(validated, iteration=3, previous_assessment=validated, **common)["blocker"])
            self.assertEqual("loop-cap-exhausted", self.controller.route_loop_assessment(validated, iteration=5, previous_assessment=before, **common)["blocker"])
            for reason in ("conflicting-source-authority", "age-only-stale-warning", "source-unavailable"):
                blocked = {**current, "state": "blocked", "reason_code": reason, "resume_action": "resolve-wiki-finding"}
                blocked.pop("next_step_id")
                blocked = self.controller.validate_outcome_envelope(blocked, project, body)
                self.assertEqual("blocked", self.controller.route_loop_assessment(blocked, iteration=2, **common)["action"])
            evidence.write_text("changed after assessment")
            with self.assertRaisesRegex(ValueError, "does not match"):
                self.controller.validate_outcome_envelope(current, project, body)


    def testCloseoutTracksResolvedClaimsWhileSameSourceCoverageRemains(self) -> None:
        steps = load_workflow("speckit-flow-closeout")["steps"]
        loop = find_step(steps, "wiki-reconciliation-loop")
        body = {n["id"] for n in loop["steps"]}
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            page = project / "wiki-plan.md"
            page.write_text("Plan loop limits represented; partial activation recovery missing")
            evidence = [{"path": page.name, "sha256": hashlib.sha256(page.read_bytes()).hexdigest()}]
            baseline = {
                "state": "continue", "reason_code": "plan-claims-missing", "evidence": evidence,
                "remaining_ids": ["plan-loop-limits", "plan-partial-activation", "inventory-graph-boundaries"],
                "resolved_ids": [], "next_step_id": "prepare-wiki-refresh",
            }
            partial_source = {**baseline,
                "remaining_ids": ["plan-partial-activation", "inventory-graph-boundaries"],
                "resolved_ids": ["plan-loop-limits"]}
            assessed = self.controller.validate_outcome_envelope(partial_source, project, body)
            common = {"max_iterations": loop["max_iterations"], "loop_body_step_ids": body}
            self.assertEqual("continue", self.controller.route_loop_assessment(
                assessed, iteration=3, previous_assessment=baseline, **common)["action"])
            # A date-only change cannot replace verified prior-claim resolution.
            page.write_text(page.read_text() + "\nFreshness date revalidated")
            dates_only = {**assessed, "resolved_ids": [], "evidence": [
                {"path": page.name, "sha256": hashlib.sha256(page.read_bytes()).hexdigest()}]}
            dates_only = self.controller.validate_outcome_envelope(dates_only, project, body)
            self.assertEqual("no-progress", self.controller.route_loop_assessment(
                dates_only, iteration=4, previous_assessment=partial_source, **common)["blocker"])
            self.assertEqual("loop-cap-exhausted", self.controller.route_loop_assessment(
                assessed, iteration=5, previous_assessment=baseline, **common)["blocker"])
            complete = {**dates_only, "state": "complete", "remaining_ids": [],
                        "resolved_ids": baseline["remaining_ids"]}
            complete.pop("next_step_id")
            complete = self.controller.validate_outcome_envelope(complete, project, body)
            self.assertEqual("complete", self.controller.route_loop_assessment(
                complete, iteration=5, previous_assessment=baseline, **common)["action"])

    def testCloseoutDispatchCarriesCorrectionsAndRevalidationWithoutExtraGates(self) -> None:
        steps = load_workflow("speckit-flow-closeout")["steps"]
        prepare = find_step(steps, "prepare-wiki-refresh")
        assess = find_step(steps, "assess-wiki-maintenance")
        outputs = {
            "prepare-wiki-refresh": {
                "baseline_remaining_ids": ["plan-partial-activation"],
                "refresh_findings": "plan section: report successful roadmap write and failed activation as partial state",
                "freshness_revalidations": "claims supported; source/page digests recorded; zero progress credit",
            },
            "ingest-curated-context": {"report": "partial state contract cited"},
            "lint-wiki": {"report": "six checks clean"},
        }
        rendered = self.controller.render_template(assess["prompt"], {}, outputs)
        self.assertIn(outputs["prepare-wiki-refresh"]["refresh_findings"], rendered)
        self.assertIn(outputs["prepare-wiki-refresh"]["freshness_revalidations"], rendered)
        protocol = (ROOT / "controllers/flow-kit/controller-protocol.md").read_text()
        self.assertIn("prepare-wiki-refresh.refresh_findings", protocol)
        self.assertIn("alongside the unchanged single source token", prepare["prompt"])
        self.assertIn("every affected claim and citation", prepare["prompt"])
        self.assertIn("do not ask for a freshness exception", prepare["prompt"])
        self.assertIn("earns no substantive progress credit", prepare["prompt"])
        self.assertIn("outside the frozen scope", prepare["prompt"])
        curation = find_step(steps, "prepare-wiki-maintenance")["prompt"]
        self.assertIn("readable registered local sources", curation)
        self.assertIn("do not add unrelated sources, external paths, or remote urls", curation.lower())
        self.assertEqual(["approve-roadmap-transition"],
                         [n["id"] for n, _, _ in walk(steps) if n.get("type") == "gate"])
        # Core ingestion still receives one source token, not the checklist as arguments.
        ingest = find_step(steps, "ingest-curated-context")
        self.assertEqual("specs/example/plan.md", self.controller.render_template(
            ingest["input"]["args"], {}, {"prepare-wiki-refresh": {"source": "specs/example/plan.md"}}))

    def testStandaloneWikiUpdateStartsWithLintAndRefreshesOnlySelectedSources(self) -> None:
        workflow = load_workflow("speckit-flow-wiki-lint-update")
        self.controller.validate_workflow_graph(workflow["steps"])
        inputs = self.controller.validate_required_inputs(workflow, {})
        self.assertEqual("", inputs["lint_scope"])
        self.assertEqual("", inputs["authorized_urls"])
        self.assertNotIn("feature_context", workflow["inputs"])
        loop, report = workflow["steps"]
        self.assertTrue(loop["assessment_before_correction"])
        self.assertEqual(26, loop["max_iterations"])
        lint, assess, route = loop["steps"]
        self.assertEqual("speckit.flow-wiki.lint", lint["command"])
        self.assertEqual("", self.controller.render_template(lint["input"]["args"], inputs, {}))
        self.assertEqual("report-wiki-update-outcome", report["id"])
        for state in ("complete", "blocked"):
            self.assertEqual([], self.controller.select_switch_branch(route, state))
        corrections = self.controller.select_switch_branch(route, "continue")
        self.assertEqual(["prepare-stale-source-refresh", "refresh-stale-source"], [n["id"] for n in corrections])
        self.assertEqual("docs/architecture.md", self.controller.render_template(corrections[-1]["input"]["args"], inputs,
            {"prepare-stale-source-refresh": {"source": "docs/architecture.md"}}))
        self.assertEqual(["speckit.flow-wiki.lint", "speckit.flow-wiki.ingest"], commands(workflow["steps"]))
        self.assertFalse(any(n.get("type") == "gate" for n, _, _ in walk(workflow["steps"])))
        # The declared correction contains ingestion only; it cannot rewrite feature artifacts or invoke another workflow.
        self.assertEqual(["speckit.flow-wiki.ingest"], commands(corrections))
        common = {"max_iterations": 26, "loop_body_step_ids": {"prepare-stale-source-refresh", "refresh-stale-source"},
                  "assessment_before_correction": True}
        first = {"state": "continue", "next_step_id": "prepare-stale-source-refresh",
                 "remaining_ids": ["stale:A", "stale:B", "contradiction:C"], "resolved_ids": []}
        second = {**first, "remaining_ids": ["stale:B", "contradiction:C"], "resolved_ids": ["stale:A"]}
        third = {**first, "remaining_ids": ["stale:D", "contradiction:C"], "resolved_ids": ["stale:B"]}
        self.assertEqual("continue", self.controller.route_loop_assessment(first, iteration=1, **common)["action"])
        self.assertEqual("continue", self.controller.route_loop_assessment(second, iteration=2, previous_assessment=first, **common)["action"])
        self.assertEqual("continue", self.controller.route_loop_assessment(third, iteration=3, previous_assessment=second, **common)["action"])
        blocked = {"state": "blocked", "remaining_ids": ["contradiction:C"], "resume_action": "resolve-source-authority"}
        self.assertEqual("blocked", self.controller.route_loop_assessment(blocked, iteration=4, **common)["action"])
        self.assertEqual("no-progress", self.controller.route_loop_assessment(second, iteration=3, previous_assessment=second, **common)["blocker"])
        self.assertEqual("loop-cap-exhausted", self.controller.route_loop_assessment(second, iteration=26, previous_assessment=first, **common)["blocker"])
        self.assertEqual("complete", self.controller.route_loop_assessment({"state": "complete"}, iteration=26, **common)["action"])

    def exercise_semantic_review_fixture(self, purpose: str) -> None:
        """Execute scripted independent review/author handoffs, not LLM reasoning."""
        workflow = load_workflow('speckit-flow-' + purpose)
        loop = workflow['steps'][0]
        prepare, author, review = loop['steps']
        self.assertEqual('FlowKit-Reviewer', review['flow_kit']['agent'])
        self.assertNotEqual(author['flow_kit']['agent'], review['flow_kit']['agent'])
        body = {n['id'] for n in loop['steps']}
        for required in ('findings verbatim in args', 'observed_deficiency', 'exact_correction', 'do not rename repeated findings'):
            self.assertIn(required, prepare['prompt'])
        for required in ('separate workflow-specific result', 'strict assessment envelope', 'Fresh review', 'new blocking findings', 'never infer its answer'):
            self.assertIn(required, review['prompt'])
        for fixture in sorted((ROOT / 'tests/consumer-fixtures' / (purpose + '-semantic-review')).glob('*.json')):
            case = json.loads(fixture.read_text())
            finding = case['finding']
            self.assertEqual({'id', 'artifact_location', 'violated_requirement', 'observed_deficiency', 'exact_correction'}, set(finding))
            with self.subTest(case=fixture.name), tempfile.TemporaryDirectory() as directory:
                project = Path(directory)
                artifact = project / (purpose + '.md')
                artifact.write_text(case['before'])
                def envelope(remaining, resolved, state='continue'):
                    result = {'state': state, 'reason_code': 'semantic-review',
                        'evidence': [{'path': artifact.name, 'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()}],
                        'remaining_ids': remaining, 'resolved_ids': resolved}
                    if state == 'continue':
                        result['next_step_id'] = prepare['id']
                    elif state == 'blocked':
                        result['resume_action'] = 'answer-product-question'
                    return self.controller.validate_outcome_envelope(result, project, body)
                initial = envelope([finding['id']], [])
                # Findings are a separate workflow-specific result, never envelope fields.
                with self.assertRaisesRegex(ValueError, 'unsupported fields'):
                    self.controller.validate_outcome_envelope({**initial, 'findings': [finding]}, project, body)
                scripted_review = {'assessment': initial, 'findings': [finding]}
                # Script the main-task preparer preserving the entire reviewer payload.
                request = {'remaining_ids': initial['remaining_ids'], 'args': json.dumps(scripted_review['findings'])}
                rendered = self.controller.render_template(author['input']['args'], {'feature_context': 'fixture'}, {prepare['id']: request})
                self.assertEqual([finding], json.loads(rendered))
                common = {'max_iterations': loop['max_iterations'], 'loop_body_step_ids': body,
                          'previous_assessment': initial}
                for mutation in ('digest-only', 'wording-only', 'repeated', 'renamed'):
                    artifact.write_text(case['before'] + ('\nRephrased commentary.\n' if mutation != 'repeated' else ''))
                    unchanged = envelope(['renamed-' + finding['id']] if mutation == 'renamed' else [finding['id']], [])
                    self.assertEqual('no-progress', self.controller.route_loop_assessment(unchanged, iteration=2, **common)['blocker'])
                stale = initial
                with self.assertRaisesRegex(ValueError, 'does not match'):
                    self.controller.validate_outcome_envelope(stale, project, body)
                artifact.write_text(case['after'])
                # Fresh scripted FlowKit-Reviewer confirms correction and retains a new blocker.
                self.assertIn(finding['exact_correction'], artifact.read_text())
                refreshed = envelope(['new-blocking-finding'], [finding['id']])
                self.assertEqual('continue', self.controller.route_loop_assessment(refreshed, iteration=2, **common)['action'])
                self.assertEqual('loop-cap-exhausted', self.controller.route_loop_assessment(refreshed, iteration=5, **common)['blocker'])
                question = 'Which retention period does the product require?'
                blocked_report = {'assessment': envelope(['product-question'], [], 'blocked'), 'question': question}
                self.assertEqual(question, blocked_report['question'])
                self.assertNotIn('answer', blocked_report)
                self.assertEqual('blocked', self.controller.route_loop_assessment(blocked_report['assessment'], iteration=2, **common)['action'])
                with self.assertRaisesRegex(ValueError, 'unresolved'):
                    envelope([finding['id']], [], 'complete')
                clean = envelope([], [finding['id']], 'complete')
                self.assertEqual('complete', self.controller.route_loop_assessment(clean, iteration=2, **common)['action'])
                if purpose == 'tasks':
                    for line in case['before'].splitlines():
                        if line.startswith('- ['):
                            self.assertIn(line, artifact.read_text())
        self.assertEqual(5, loop['max_iterations'])
        self.assertEqual(['speckit.' + purpose], commands(workflow['steps']))

    def test_planPopulatedSemanticDefects_preserveExactHandoffAndBoundedStops(self) -> None:
        self.exercise_semantic_review_fixture('plan')


    def test_tasksPopulatedSemanticDefects_preserveExactHandoffAndHistory(self) -> None:
        self.exercise_semantic_review_fixture('tasks')

    def test_codeReviewExactDelta_correctsEligibleTaskOrStopsWithoutAuthority(self) -> None:
        """Script distinct FlowKit-Code Reviewer/FlowKit-Coder results through declared correction paths."""
        configurations = (
            ('implement', 'assess-implementation-after-pass', 'implement-eligible-work', None),
            ('converge', 'assess-convergence', 'implement-remediation', 'prepare-convergence-flowback'),
            ('closeout', 'assess-closeout-debrief', 'implement-closeout-eligible-tasks', 'prepare-closeout-flowback'),
        )
        for purpose, review_id, author_id, prepare_id in configurations:
            workflow = load_workflow('speckit-flow-' + purpose)
            review = find_step(workflow['steps'], review_id)
            author = find_step(workflow['steps'], author_id)
            self.assertEqual('FlowKit-Code Reviewer', review['flow_kit']['agent'])
            self.assertEqual('FlowKit-Coder', author['flow_kit']['agent'])
            self.assertIn('implementation delta', review['prompt'])
            self.assertIn('separate workflow-specific result', review['prompt'])
            self.assertIn('exact review findings', author['input']['args'])
            body = {n['id'] for n, _, _ in walk(workflow['steps'])}
            loop = find_step(workflow['steps'], {'implement': 'implementation-continuation-loop',
                'converge': 'convergence-remediation-loop', 'closeout': 'closeout-debrief-loop'}[purpose])
            with self.subTest(workflow=purpose), tempfile.TemporaryDirectory() as directory:
                project = Path(directory)
                source = project / 'feature.py'
                before = 'def retain():\n    return True\n'
                deficient = 'def retain():\n    return False\n'
                source.write_text(deficient)
                finding = {'id': 'CR-001', 'task_id': 'T002', 'artifact_location': 'feature.py:2',
                    'violated_requirement': 'FR-001 retain data', 'observed_deficiency': 'returns False',
                    'exact_correction': 'Restore return True',
                    'delta': {'path': 'feature.py', 'before_sha256': hashlib.sha256(before.encode()).hexdigest(),
                              'after_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}}
                (project / 'delta.json').write_text(json.dumps({'before': before, 'after': deficient, 'finding': finding}))
                def outcome(state, remaining, resolved, reason='code-review'):
                    result = {'state': state, 'reason_code': reason,
                        'evidence': [{'path': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                                     for p in (source, project / 'delta.json')],
                        'remaining_ids': remaining, 'resolved_ids': resolved}
                    if state == 'continue': result['next_step_id'] = author_id
                    if state == 'blocked': result['resume_action'] = 'record-or-reopen-task-and-reinvoke'
                    return self.controller.validate_outcome_envelope(result, project, body)
                baseline = outcome('continue', ['T001', 'T002'], [])
                current = outcome('continue', ['T002'], ['T001'])
                common = {'max_iterations': loop['max_iterations'], 'loop_body_step_ids': body,
                    'previous_assessment': baseline,
                    'assessment_before_correction': loop.get('assessment_before_correction', False)}
                self.assertEqual('continue', self.controller.route_loop_assessment(current, iteration=2, **common)['action'])
                if prepare_id:
                    prepare = find_step(workflow['steps'], prepare_id)
                    self.assertIn('implementation_args', prepare['prompt'])
                    eligibility = 'assess-remediation-eligibility' if purpose == 'converge' else 'assess-closeout-task-eligibility'
                    args = self.controller.render_template(author['input']['args'], {'feature_context': 'fixture'},
                        {prepare_id: {'implementation_args': json.dumps([finding], indent=2)}, eligibility: {'remaining_ids': ['T002']}})
                    self.assertIn(json.dumps([finding], indent=2), args)
                else:
                    self.assertIn('latest assess-implementation-after-pass', author['input']['args'])
                # FlowKit-Coder applies only T002; a fresh scripted reviewer verifies the change.
                source.write_text(before)
                namespace = {}
                exec(source.read_text(), namespace)
                self.assertTrue(namespace['retain']())
                fresh = outcome('complete', [], ['T002'])
                self.assertEqual('complete', self.controller.route_loop_assessment(fresh, iteration=3, **common)['action'])
                with self.assertRaisesRegex(ValueError, 'unresolved'):
                    outcome('complete', ['CR-001'], ['T002'])
                blocked = outcome('blocked', ['CR-001'], [], 'no-safe-eligible-correction')
                self.assertEqual({'action': 'blocked', 'resume_action': 'record-or-reopen-task-and-reinvoke'},
                    self.controller.route_loop_assessment(blocked, iteration=2, **common))
                self.assertEqual('no-progress', self.controller.route_loop_assessment(
                    baseline, iteration=2, **common)['blocker'])
                self.assertEqual('loop-cap-exhausted', self.controller.route_loop_assessment(
                    current, iteration=loop['max_iterations'], **common)['blocker'])
                question = {'question': 'Which data retention rule is approved?', 'assessment': blocked}
                self.assertNotIn('answer', question)
                self.assertIn('never infer', review['prompt'])
                self.assertIn('no safe eligible', review['prompt'])
                self.assertIn('successful command', review['prompt'])
                self.assertNotIn('speckit.flow-kit-', ' '.join(commands(workflow['steps'])))
                # Existing Closeout roadmap approval remains outside the correction branch.
                if purpose != 'implement':
                    route = find_step(workflow['steps'], 'route-convergence-correction' if purpose == 'converge' else 'route-closeout-correction')
                    self.assertEqual([], self.controller.select_switch_branch(route, 'blocked'))
                    self.assertFalse(any('roadmap.write' in c for c in commands(route['cases']['continue'])))


if __name__ == "__main__":
    unittest.main()

"""Production-template routing for preparation readiness workflow steps."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]
CONTROLLER_PATH = ROOT / "controllers/flow-kit/scripts/python/controller.py"


def load_controller():
    spec = importlib.util.spec_from_file_location("readiness_route_controller", CONTROLLER_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {CONTROLLER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def workflow(name: str) -> dict:
    path = ROOT / "workflows" / name / "workflow.yml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def find(nodes: list[dict], step_id: str) -> dict:
    for node in nodes:
        if node.get("id") == step_id:
            return node
        for branch in node.get("cases", {}).values():
            result = find(branch, step_id)
            if result:
                return result
        result = find(node.get("default", []), step_id)
        if result:
            return result
        result = find(node.get("steps", []), step_id)
        if result:
            return result
    return {}


class ReadinessWorkflowRouteTests(unittest.TestCase):
    """Rendered routes preserve recorder authority and readiness-before-core ordering."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.controller = load_controller()

    def test_analyzeSwitchRendersExactRecorderAndSkipBranches(self) -> None:
        analyze = workflow("speckit-flow-analyze-remediate")
        route = find(analyze["steps"], "route-readiness-recording")
        for action, expected in (("run", ["record-readiness-evidence"]), ("skip", [])):
            rendered = self.controller.render_template(
                route,
                {"feature_context": "specs/020-example", "integration": "codex"},
                {"prepare-analysis-flowback": {
                    "readiness_record_action": action,
                    "readiness_record_args": '{"reviewer":"FlowKit-Reviewer"}',
                }},
            )
            selected = self.controller.select_switch_branch(rendered, action)
            self.assertEqual(expected, [step["id"] for step in selected])
            if selected:
                prompt = self.controller.render_template(
                    selected[0]["prompt"],
                    {"feature_context": "specs/020-example"},
                    {"prepare-analysis-flowback": {
                        "readiness_record_args": '{"reviewer":"FlowKit-Reviewer"}',
                    }},
                )
                self.assertIn('"reviewer":"FlowKit-Reviewer"', prompt)
                self.assertIn("action: record-review", prompt)
                self.assertIn("Never mark built-in author checklist items", prompt)
                self.assertNotIn("/Users/", prompt)

    def test_analyzeRemediationUsesFreshAnalysisCheckerAndSmallestOwner(self) -> None:
        analyze = workflow("speckit-flow-analyze-remediate")
        loop = find(analyze["steps"], "analysis-remediation-loop")
        self.assertEqual(6, loop["max_iterations"])
        self.assertTrue(loop["assessment_only_first_pass"])
        body = loop["steps"]
        analyze_step = find(body, "analyze-artifacts")
        checker = find(body, "check-readiness")
        assessor = find(body, "assess-analysis")
        self.assertEqual("FlowKit-Reviewer", analyze_step["flow_kit"]["agent"])
        self.assertEqual({"delegated": True, "agent": "FlowKit-Readiness Checker"}, checker["flow_kit"])
        self.assertEqual("FlowKit-Reviewer", assessor["flow_kit"]["agent"])
        checker_prompt = self.controller.render_template(
            checker["prompt"], {"feature_context": "specs/020-example"},
            {"assess-readiness-evidence": {"readiness_report_json": '{"state":"ready"}'},
             "analyze-artifacts": {"report": "fresh artifact findings"}},
        )
        self.assertIn("Read only the deterministic report", checker_prompt)
        self.assertIn("fresh Analyze report", checker_prompt)
        self.assertIn("Do not edit", checker_prompt)
        assessor_prompt = self.controller.render_template(
            assessor["prompt"], {"feature_context": "specs/020-example"},
            {"assess-readiness-evidence": {"readiness_report_json": '{"state":"ready"}'},
             "check-readiness": {"readiness_review": '{"state":"ready"}'},
             "analyze-artifacts": {"report": "fresh artifact findings"}},
        )
        self.assertIn("Keep artifact findings and readiness findings distinct", assessor_prompt)
        self.assertIn("After any correction, the next bounded pass must rerun fresh Analyze and Checker assessment", assessor_prompt)
        for step_id, agent in (("remediate-specification", "FlowKit-Specifier"),
                                ("remediate-plan", "FlowKit-Planner"),
                                ("remediate-tasks", "FlowKit-Tasker")):
            self.assertEqual(agent, find(body, step_id)["flow_kit"]["agent"])
        self.assertIn("smallest authorized owner", find(body, "prepare-analysis-flowback")["prompt"])

    def test_checkerMetadataAndImplementGatePrecedeCoreCommand(self) -> None:
        implement = workflow("speckit-flow-implement")
        loop = find(implement["steps"], "implementation-loop")
        body = loop["steps"]
        before_loop = implement["steps"]
        checker = next(step for step in before_loop if step["id"] == "check-readiness-before-core")
        self.assertEqual({"delegated": True, "agent": "FlowKit-Readiness Checker"}, checker["flow_kit"])
        for source_step in ("run-scoped-preparation", "run-scoped-source-implementation"):
            self.assertEqual("FlowKit-Coder", find(body, source_step)["flow_kit"]["agent"])
        self.assertLess([step["id"] for step in implement["steps"]].index(checker["id"]),
                        [step["id"] for step in implement["steps"]].index("route-readiness-before-core"))
        gate = next(step for step in before_loop if step["id"] == "gate-readiness-before-core")
        rendered = self.controller.render_template(
            gate["prompt"], {"feature_context": "specs/020-example"},
            {"assess-readiness-before-core": {"readiness_report_json": '{"state":"ready"}'},
             "check-readiness-before-core": {"readiness_review": '{"state":"ready"}'}},
        )
        self.assertIn("Immediately before entering the implementation loop, rerun the installed readiness helper", rendered)
        self.assertEqual({"assess-implementation-state", "assess-implementation-start-milestone"},
                         {step["id"] for step in before_loop
                          if step.get("flow_kit", {}).get("agent") == "FlowKit-Reviewer"})
        initial_route = next(step for step in before_loop if step["id"] == "route-readiness-before-core")
        self.assertIn("Do not dispatch core implementation", initial_route["cases"]["blocked"][0]["prompt"])
        for state, expected in (("ready", ["implementation-loop"]), ("blocked", ["stop-readiness-before-core"])):
            choice = self.controller.render_template(initial_route["expression"], {}, {
                "verify-lifecycle-and-readiness-before-coding": {"state": state},
            })
            selected = self.controller.select_switch_branch(initial_route, choice)
            self.assertEqual(expected, [step["id"] for step in selected])
            self.assertFalse(any(step.get("command") == "speckit.implement" for step in selected))
        blocked_start = self.controller.select_switch_branch(
            initial_route, self.controller.render_template(initial_route["expression"], {}, {
                "verify-lifecycle-and-readiness-before-coding": {"state": "blocked"},
            }))
        self.assertFalse(any(step.get("id") == "implementation-loop" for step in blocked_start))

        reentry_route = find(body, "route-readiness-before-reentry")
        self.assertIn("Never dispatch Reviewer routinely", find(body, "gate-readiness-before-reentry")["prompt"])
        for state, expected in (("ready", []), ("blocked", ["stop-readiness-before-reentry"])):
            choice = self.controller.render_template(reentry_route["expression"], {}, {
                "gate-readiness-before-reentry": {"readiness_gate": {"state": state}},
            })
            selected = self.controller.select_switch_branch(reentry_route, choice)
            self.assertEqual(expected, [step["id"] for step in selected])
            self.assertFalse(any(step.get("command") == "speckit.implement" for step in selected))
        blocked_route = self.controller.render_template(
            find(body, "route-scoped-execution")["prompt"], {}, {
                "route-scoped-entry": {
                    "scope": {"requested_task_ids": ["T001"], "scope_sha256": "a" * 64},
                    "eligibility": {"eligibility": {"eligible_task_ids": ["T001"]}},
                    "history": {"coder_sessions_started": 0, "source_attempts_started": 0},
                    "task_tracking_successors": [],
                    "previous_assessment": {"state": "continue", "remaining_ids": ["task:T001"],
                                            "resolved_ids": []},
                    "baseline": {"tasks": {"T001": {"marker": " "}}},
                },
                "assess-implementation-after-pass": {
                    "outcome_envelope": {
                        "state": "continue", "reason_code": "review-complete", "evidence": [],
                        "remaining_ids": ["task:T001"], "resolved_ids": [],
                    },
                    "review": {},
                },
                "gate-readiness-before-core": {"readiness_gate": {"state": "blocked"}},
                "capture-post-pass-state": {"post_pass_state": {
                    "history": {"coder_sessions_started": 0, "source_attempts_started": 0},
                    "task_tracking_successors": [],
                    "eligibility": {"eligible_task_ids": ["T001"]},
                }},
                "route-post-assessment": {"state": "continue"},
            })
        self.assertIn("a blocked readiness or post-pass capture result takes precedence", blocked_route)
        self.assertFalse(self.controller.evaluate_loop_condition(loop["condition"], {
            "route-scoped-execution": {"state": "blocked"},
        }))
        self.assertTrue(self.controller.evaluate_loop_condition(loop["condition"], {
            "route-scoped-execution": {"state": "continue"},
        }))
        self.assertIn("After the Code Reviewer continue verdict and any Tasker revision or skip",
                      find(body, "reassess-readiness-before-reentry")["prompt"])


if __name__ == "__main__":
    unittest.main()

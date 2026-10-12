"""Regression coverage for Implement's mutually exclusive entry routes."""

import unittest

from test_workflow_paths import ROOT, find_step, load_module, load_workflow


class ImplementSwitchRoutingTests(unittest.TestCase):
    def setUp(self):
        self.controller = load_module(
            "implement_switch_controller", ROOT / "controllers/farmboy/scripts/python/controller.py"
        )
        self.steps = load_workflow("farmboy-implement")["steps"]

    def selected(self, step_id, choice):
        switch = find_step(self.steps, step_id)
        rendered = self.controller.render_template(switch, {"integration": "codex", "feature_context": "selected feature"}, {
            "route-scoped-entry": {"next_step_id": choice}
        })
        return self.controller.select_switch_branch(rendered, choice)

    def test_source_execution_skips_preparation(self):
        self.assertEqual([], self.selected("prepare-scoped-prerequisites", "implement-tasks"))
        selected = self.selected("implement-tasks", "implement-tasks")
        self.assertEqual([
            "record-source-session-and-attempt", "run-scoped-source-implementation",
            "record-source-session-outcome",
        ], [node["id"] for node in selected])

    def test_preparation_skips_source_execution(self):
        self.assertEqual([], self.selected("implement-tasks", "prepare-scoped-prerequisites"))
        selected = self.selected("prepare-scoped-prerequisites", "prepare-scoped-prerequisites")
        self.assertEqual([
            "record-preparation-session-start", "run-scoped-preparation",
            "record-preparation-session-outcome",
        ], [node["id"] for node in selected])

    def test_unrecognized_guard_states_select_stop_fallbacks(self):
        for step_id, stop_id in (
            ("route-readiness-before-core", "stop-readiness-before-core-unrecognized"),
            ("route-task-revision-snapshot", "stop-task-revision-dispatch-unrecognized"),
        ):
            with self.subTest(step_id=step_id):
                switch = find_step(self.steps, step_id)
                self.assertEqual([stop_id], [node["id"] for node in
                    self.controller.select_switch_branch(switch, "unrecognized")])

    def test_all_source_switch_defaults_are_top_level(self):
        def inspect(value):
            if isinstance(value, dict):
                if value.get("type") == "switch":
                    self.assertNotIn("default", value.get("cases", {}), value["id"])
                for child in value.values():
                    inspect(child)
            elif isinstance(value, list):
                for child in value:
                    inspect(child)

        for path in (ROOT / "workflows").glob("*/workflow.yml"):
            with self.subTest(workflow=path.parent.name):
                inspect(load_workflow(path.parent.name))

"""Regression coverage for Implement's mutually exclusive entry routes."""

import unittest
import io
import json
from contextlib import redirect_stdout
from unittest.mock import patch

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

    def test_selectedEmptyCaseAndTopLevelEmptyDefaultPreserveSkip(self):
        switch = {
            "id": "route",
            "type": "switch",
            "cases": {"skip": [], "run": [{"id": "run-child", "command": "speckit.fixture"}]},
            "default": [],
        }
        self.assertEqual([], self.controller.select_switch_branch(switch, "skip"))
        self.assertEqual([], self.controller.select_switch_branch(switch, "unknown"))
        self.assertEqual([{"id": "run-child", "command": "speckit.fixture"}],
                         self.controller.select_switch_branch(switch, "run"))

    def test_unknownChoiceWithoutFallbackRaisesBeforeSelectingAChild(self):
        switch = {"id": "route", "type": "switch", "cases": {
            "run": [{"id": "run-child", "command": "speckit.fixture"}]}}
        with self.assertRaisesRegex(ValueError, "no branch for the selected choice"):
            self.controller.select_switch_branch(switch, "unknown")

    def testEmptySelectedRouteContainsNoUntakenBranchChildren(self):
        switch = {"id": "route", "type": "switch", "cases": {
            "skip": [], "run": [{"id": "untaken-command", "command": "speckit.fixture"}]}}
        selected = self.controller.select_switch_branch(switch, "skip")
        dispatched = [node["command"] for node in selected if "command" in node]
        self.assertEqual([], selected)
        self.assertEqual([], dispatched)

    def testRenderedSwitchSelectsRouteWithoutRenderingUntakenOrFutureInputs(self):
        switch = {
            "id": "route",
            "type": "switch",
            "expression": "{{ steps.assess.output.next_step_id }}",
            "transition_labels": {"skip": "skip preparation", "run": "execute source"},
            "cases": {
                "skip": [],
                "run": [{"id": "consume", "type": "prompt",
                         "prompt": "Use {{ steps.producer.output.value }}"}],
            },
            "default": [],
        }
        metadata, selected = self.controller.render_selected_switch(switch, {}, {
            "assess": {"next_step_id": "skip"},
        })
        self.assertEqual("skip", metadata["expression"])
        self.assertEqual([], selected)

        metadata, selected = self.controller.render_selected_switch(switch, {}, {
            "assess": {"next_step_id": "run"},
        })
        self.assertEqual("run", metadata["expression"])
        self.assertEqual("{{ steps.producer.output.value }}", selected[0]["prompt"].split("Use ", 1)[1])
        with self.assertRaisesRegex(ValueError, "unresolved step output reference"):
            self.controller.render_template(selected[0], {}, {})
        consumed = self.controller.render_template(selected[0], {}, {"producer": {"value": "fresh"}})
        self.assertEqual("Use fresh", consumed["prompt"])

    def testRenderedSwitchSupportsEmptyFallbackAndBooleanChoiceNormalization(self):
        empty_default = {"id": "route", "type": "switch", "expression": "{{ inputs.choice }}",
                         "cases": {"run": [{"id": "run-child", "command": "speckit.fixture"}]},
                         "default": []}
        _, selected = self.controller.render_selected_switch(empty_default, {"choice": "unknown"}, {})
        self.assertEqual([], selected)

        boolean_switch = {"id": "route", "type": "switch", "expression": "{{ steps.assess.output.enabled }}",
                          "cases": {"true": [{"id": "enabled-child", "command": "speckit.fixture"}],
                                    "false": []}}
        _, selected = self.controller.render_selected_switch(boolean_switch, {}, {"assess": {"enabled": True}})
        self.assertEqual(["enabled-child"], [step["id"] for step in selected])
        with self.assertRaisesRegex(ValueError, "no branch for the selected choice"):
            self.controller.render_selected_switch(
                {"id": "route", "type": "switch", "expression": "{{ inputs.choice }}", "cases": {"run": []}},
                {"choice": "unknown"}, {})

    def testBranchCommandRendersExpressionAndReturnsOnlySelectedRawChildren(self):
        switch = {
            "id": "route", "type": "switch",
            "expression": "{{ steps.assess.output.next_step_id }}",
            "cases": {
                "skip": [],
                "run": [{"id": "consume", "type": "prompt",
                         "prompt": "Use {{ steps.producer.output.value }}"}],
            },
            "default": [],
        }
        request = {"switch": switch, "inputs": {}, "outputs": {"assess": {"next_step_id": "skip"}}}
        output = io.StringIO()
        with patch("sys.stdin", io.StringIO(json.dumps(request))), redirect_stdout(output):
            status = self.controller.main(["branch"])
        self.assertEqual(0, status)
        self.assertEqual([], json.loads(output.getvalue())["steps"])

        request["outputs"]["assess"]["next_step_id"] = "run"
        output = io.StringIO()
        with patch("sys.stdin", io.StringIO(json.dumps(request))), redirect_stdout(output):
            status = self.controller.main(["branch"])
        self.assertEqual(0, status)
        selected = json.loads(output.getvalue())["steps"]
        self.assertEqual("{{ steps.producer.output.value }}", selected[0]["prompt"].split("Use ", 1)[1])

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

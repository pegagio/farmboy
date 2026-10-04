"""Machine-checkable branch and gate coverage for every FlowKit workflow."""

from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_step(nodes: list[dict], step_id: str) -> dict | None:
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


def commands(nodes: list[dict]) -> list[str]:
    result = []
    for node in nodes:
        if "command" in node:
            result.append(node["command"])
        for branch in node.get("cases", {}).values() if isinstance(node.get("cases"), dict) else []:
            result.extend(commands(branch))
        result.extend(commands(node.get("default", [])))
        result.extend(commands(node.get("steps", [])))
    return result


class WorkflowGraphInventoryTests(unittest.TestCase):
    """Every source workflow has a static projection of its complete graph."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.inventory = load_module("flowkit_workflow_inventory", ROOT / "tools/validate_workflows.py")

    def test_activeAndDeprecatedWorkflowsExposeStopsAndAssignmentsWithRequiredGates(self) -> None:
        projections = [self.inventory.project_workflow(item) for item in self.inventory.load_workflows()]
        expected = {
            "speckit-flow-start-feature", "speckit-flow-select-feature", "speckit-flow-specify", "speckit-flow-clarify", "speckit-flow-plan", "speckit-flow-tasks",
            "speckit-flow-analyze-remediate", "speckit-flow-implement", "speckit-flow-converge", "speckit-flow-closeout", "speckit-flow-wiki-lint-update",
        }
        self.assertEqual(expected, {item["workflow_id"] for item in projections})
        for projection in projections:
            with self.subTest(workflow=projection["workflow_id"]):
                self.assertTrue(projection["entry_step_id"])
                self.assertEqual("unverified", projection["native_agent_selection"]["status"])
                self.assertIn("does not request native Codex subagents", projection["native_agent_selection"]["reason"])
                if projection["workflow_id"] == "speckit-flow-start-feature":
                    self.assertFalse(projection["assignments"])
                    self.assertFalse(projection["branches"])
                    continue
                if projection["workflow_id"] in {"speckit-flow-clarify", "speckit-flow-implement", "speckit-flow-plan", "speckit-flow-tasks", "speckit-flow-analyze-remediate", "speckit-flow-converge", "speckit-flow-wiki-lint-update"}:
                    if projection["workflow_id"] in {"speckit-flow-analyze-remediate", "speckit-flow-converge", "speckit-flow-wiki-lint-update"}:
                        self.assertTrue(projection["branches"])
                    else:
                        self.assertFalse(projection["branches"])
                    self.assertFalse(projection["human_decisions"])
                else:
                    self.assertTrue(projection["branches"])
                    self.assertTrue(projection["human_decisions"])
                self.assertTrue(projection["assignments"])
                self.assertIn("unexplained_terminal_paths", projection)
        analyze = next(item for item in projections if item["workflow_id"] == "speckit-flow-analyze-remediate")
        implement = next(item for item in projections if item["workflow_id"] == "speckit-flow-implement")
        self.assertEqual("analysis-remediation-loop", analyze["entry_step_id"])
        self.assertTrue(analyze["continuation_edges"])
        self.assertEqual("assess-implementation-state", implement["entry_step_id"])
        self.assertTrue(implement["continuation_edges"])
        self.assertTrue(all(not item["unexplained_terminal_paths"] for item in projections))
        returned = {
            item["workflow_id"]: {path["terminal_step_id"] for path in item["bounded_stops"]
                                   if path.get("reason") == "operator-selected-return-command-ends-current-workflow"}
            for item in projections
        }
        self.assertEqual(set(), returned["speckit-flow-plan"])
        self.assertEqual(set(), returned["speckit-flow-tasks"])

    def testOnlyGatedReturnCommandsReceiveTheExplicitBoundedReturnClassification(self) -> None:
        definition = {
            "workflow": {"id": "fixture", "version": "1.0"},
            "steps": [
                {"id": "decision", "type": "gate", "options": ["return"]},
                {"id": "route", "type": "switch", "cases": {
                    "return": [{"id": "return-to-plan", "command": "speckit.plan"}],
                }},
            ],
        }
        projection = self.inventory.project_workflow(definition)
        self.assertEqual([], projection["unexplained_terminal_paths"])
        self.assertEqual("operator-selected-return-command-ends-current-workflow",
                         projection["bounded_stops"][0]["reason"])

    def test_unexplainedTerminalDetectionReportsUnclassifiedLeaf(self) -> None:
        definition = {
            "workflow": {"id": "fixture", "version": "1.0"},
            "steps": [{"id": "finish", "type": "prompt", "prompt": "Continue working."}],
        }
        projection = self.inventory.project_workflow(definition)
        self.assertEqual("finish", projection["unexplained_terminal_paths"][0]["terminal_step_id"])
        explained = {
            **definition,
            "steps": [{"id": "finish", "type": "prompt", "prompt": "Stop with the bounded blocker."}],
        }
        self.assertEqual([], self.inventory.project_workflow(explained)["unexplained_terminal_paths"])

    def testInventoryCLIListsAllWorkflows(self) -> None:
        projections = [self.inventory.project_workflow(item) for item in self.inventory.load_workflows()]
        self.assertEqual(11, len(projections))
        self.assertTrue(all("continuation_edges" in item and "bounded_stops" in item for item in projections))

    def testSelectionAndSpecificationSeparateMutationAuthority(self) -> None:
        workflows = {w["workflow"]["id"]: w for w in self.inventory.load_workflows()}
        selection = workflows["speckit-flow-select-feature"]
        authoring = workflows["speckit-flow-specify"]
        self.assertEqual(["speckit.flow-roadmap.write"], commands(selection["steps"]))
        self.assertNotIn("speckit.specify", commands(selection["steps"]))
        self.assertEqual(2, len(self.inventory.project_workflow(selection)["human_decisions"]))
        self.assertEqual(1, len(self.inventory.project_workflow(authoring)["human_decisions"]))
        self.assertEqual("inspect-active-feature", authoring["steps"][0]["id"])
        self.assertEqual(["speckit.flow-wiki.query", "speckit.specify", "speckit.flow-roadmap.write", "speckit.flow-roadmap.brief"], commands(authoring["steps"]))
        deprecated = workflows["speckit-flow-start-feature"]
        self.assertTrue(deprecated["workflow"]["deprecated"])
        self.assertEqual([], commands(deprecated["steps"]))
        self.assertEqual(1, len(deprecated["steps"]))

    def testPlanGraphLoopsThroughCorePlanningAndOutputVerification(self) -> None:
        workflow = next(item for item in self.inventory.load_workflows()
                        if item["workflow"]["id"] == "speckit-flow-plan")
        self.assertEqual(["plan-output-loop", "report-plan-outcome"],
                         [step["id"] for step in workflow["steps"]])
        self.assertEqual(["speckit.plan"], commands(workflow["steps"]))
        graph = self.inventory.project_workflow(workflow)
        self.assertFalse(graph["branches"])
        self.assertFalse(graph["human_decisions"])
        self.assertTrue(graph["continuation_edges"])
        self.assertFalse(graph["unexplained_terminal_paths"])

    def testClarifyGraphKeepsOperatorQuestionsAndNeverStartsPlan(self) -> None:
        workflow = next(item for item in self.inventory.load_workflows()
                        if item["workflow"]["id"] == "speckit-flow-clarify")
        steps = workflow["steps"]
        loop = find_step(steps, "clarification-session-loop")
        self.assertEqual(5, loop["max_iterations"])
        command_ids = {node.get("id") for node, _, _ in self.inventory._walk(steps) if "command" in node}
        self.assertEqual({"clarify-session"}, command_ids)
        self.assertEqual(["clarify-session", "assess-clarification-after-session"],
                         [node["id"] for node in loop["steps"]])
        readme = (ROOT / "workflows/README.md").read_text(encoding="utf-8")
        manual = readme.split("## Manual clarification path", 1)[1].split("## Manual planning path", 1)[0]
        self.assertIn("five-question cap applies per session", manual)
        self.assertIn("same invocation", manual)
        self.assertIn("wait for the operator's answer", manual)
        self.assertIn("without invoking Plan", manual)

    def testTasksGraphUsesOnlyCoreSkillAndOutputLoop(self) -> None:
        workflow = next(item for item in self.inventory.load_workflows()
                        if item["workflow"]["id"] == "speckit-flow-tasks")
        self.assertEqual(["tasks-output-loop", "report-task-outcome"],
                         [step["id"] for step in workflow["steps"]])
        self.assertEqual(["speckit.tasks"], commands(workflow["steps"]))
        graph = self.inventory.project_workflow(workflow)
        self.assertFalse(graph["branches"])
        self.assertFalse(graph["human_decisions"])
        self.assertTrue(graph["continuation_edges"])
        self.assertFalse(graph["unexplained_terminal_paths"])
        manual = (ROOT / "workflows/README.md").read_text().split(
            "## Manual task-generation path", 1)[1].split("## Manual analysis and remediation path", 1)[0]
        self.assertIn("without a routine pre-generation question", manual)
        self.assertIn("separately invoke Analyze", manual)
        self.assertIn("preserving task IDs, completion markers", manual)

    def testConvergeGraphOrdersRemediationAndStopsWithoutStartingCloseOut(self) -> None:
        workflow = next(item for item in self.inventory.load_workflows()
                        if item["workflow"]["id"] == "speckit-flow-converge")
        steps = workflow["steps"]
        loop, report = steps
        self.assertEqual("convergence-remediation-loop", loop["id"])
        self.assertTrue(loop["assessment_before_correction"])
        self.assertEqual(6, loop["max_iterations"])
        self.assertEqual("assess-convergence", loop["steps"][1]["id"])
        self.assertEqual("report-convergence-outcome", report["id"])
        self.assertEqual(["speckit.converge", "speckit.specify", "speckit.plan", "speckit.tasks",
                          "speckit.analyze", "speckit.implement"], commands(steps))
        eligibility = find_step(steps, "route-remediation-implementation")
        self.assertEqual({"continue", "complete", "blocked"}, set(eligibility["cases"]))
        for state in ("complete", "blocked"):
            self.assertEqual([], eligibility["cases"][state])
        self.assertFalse(any(command.startswith("speckit.flow-") for command in commands(steps)))
        self.assertFalse(any(node.get("type") == "gate" for node, _, _ in self.inventory._walk(steps)))
        manual = (ROOT / "workflows/README.md").read_text(encoding="utf-8").split(
            "## Manual convergence path", 1
        )[1].split("## Manual closeout path", 1)[0]
        self.assertIn("same invocation", manual)
        self.assertIn("Analyze changed tasks before implementation", manual)
        self.assertIn("separate operator instruction", manual)

    def testCloseoutGraphSharesCorrectionAndMaintainsVerifiedContext(self) -> None:
        workflow = next(item for item in self.inventory.load_workflows()
                        if item["workflow"]["id"] == "speckit-flow-closeout")
        steps = workflow["steps"]
        self.assertEqual("assess-closeout-readiness", steps[0]["id"])
        loop = find_step(steps, "closeout-debrief-loop")
        self.assertTrue(loop["assessment_before_correction"])
        self.assertEqual(6, loop["max_iterations"])
        self.assertEqual("debrief-roadmap", loop["steps"][0]["id"])
        self.assertEqual("assess-closeout-debrief", loop["steps"][1]["id"])
        self.assertEqual({"continue", "complete", "blocked"}, set(loop["steps"][2]["cases"]))
        self.assertEqual("report-closeout-outcome", steps[-1]["id"])
        self.assertEqual(1, commands(steps).count("speckit.flow-roadmap.debrief"))
        self.assertEqual(1, commands(steps).count("speckit.plan"))
        self.assertEqual(1, commands(steps).count("speckit.tasks"))
        self.assertEqual(1, sum(n.get("type") == "gate" for n, _, _ in self.inventory._walk(steps)))
        self.assertEqual([], self.inventory.project_workflow(workflow)["unexplained_terminal_paths"])
        manual = (ROOT / "workflows/README.md").read_text().split("## Manual closeout path", 1)[1]
        for phrase in ("in-place Draft-to-Complete", "rerun debrief", "exact roadmap verification patch", "does not commit"):
            self.assertIn(phrase, manual)



    def assert_diagram_metadata(self, workflow: dict, diagram: str) -> None:
        """Compare reviewed Mermaid declarations with actual source nodes."""
        block = diagram.split("```mermaid\n", 1)[1].split("```", 1)[0]
        declarations = {}
        aliases = {}
        shapes = {"do-while": ('{{"', '"}}'), "prompt": ('["', '"]'),
                  "gate": ('[/"', '"/]'), "command": ('(["', '"])')}
        for line in block.splitlines():
            match = re.fullmatch(r'\s*(\w+)(.*"([^"\n]+)".*)\s*', line)
            if not match:
                continue
            alias, notation, label = match.groups()
            step_id = label.split('<br/>', 1)[0]
            self.assertNotIn(step_id, declarations, "duplicate diagram step")
            declarations[step_id] = (notation.strip(), label)
            aliases[step_id] = alias
        nodes = {node['id']: node for node, _, _ in self.inventory._walk(workflow['steps'])}
        self.assertEqual(set(nodes), set(declarations), "diagram step IDs differ from source")
        delegated = set()
        for match in re.finditer(r'^\s*class ([\w,]+) delegated\s*$', block, re.MULTILINE):
            delegated.update(match.group(1).split(','))
        expected_delegated = set()
        for step_id, node in nodes.items():
            notation, label = declarations[step_id]
            assigned = node.get('flow_kit', {}).get('agent')
            agents = re.findall(r'\(([^()]*)\)', label)
            self.assertEqual([assigned] if assigned else [], agents,
                             f"{step_id}: agent label differs from source")
            self.assertEqual([node['command']] if 'command' in node else [],
                             re.findall(r'command: ([^<]+)', label),
                             f"{step_id}: command differs from source")
            kind = 'command' if 'command' in node else node['type']
            if kind == 'switch':
                self.assertRegex(notation, r'^@\{ shape: diam, label: ".*" \}$')
            else:
                opening, closing = shapes[kind]
                self.assertTrue(notation.startswith(opening) and notation.endswith(closing),
                                f"{step_id}: wrong {kind} shape")
            if node.get('flow_kit', {}).get('delegated') is True:
                expected_delegated.add(aliases[step_id])
            if kind == 'do-while':
                self.assertIn(f"max_iterations: {node['max_iterations']}", label)
                self.assertIn('condition:', label)
        self.assertEqual(expected_delegated, delegated, "delegation outlines differ from source")
        if delegated:
            self.assertRegex(block, r'classDef delegated [^\n]*stroke-dasharray:6 4')
        self.assertEqual(['start((Start))'], re.findall(r'^\s*(start\(\(Start\)\))\s*$', block, re.MULTILINE))
        entries = re.findall(r'^\s*start --> (\w+)\s*$', block, re.MULTILINE)
        self.assertEqual([aliases[workflow['steps'][0]['id']]], entries, "wrong Start edge")
        self.assertIn('style start fill:#111827,stroke:#111827,color:#ffffff', block)

    def test_diagramsMatchSourceStepMetadataIncludingUnassignedLoops(self) -> None:
        for workflow in self.inventory.load_workflows():
            workflow_id = workflow['workflow']['id']
            with self.subTest(workflow=workflow_id):
                diagram = (ROOT / 'workflows' / workflow_id / 'flowchart.md').read_text()
                self.assert_diagram_metadata(workflow, diagram)

    def test_diagramMetadataRejectsPhantomMissingAndIncorrectDeclarations(self) -> None:
        workflow = next(w for w in self.inventory.load_workflows()
                        if w['workflow']['id'] == 'speckit-flow-plan')
        original = (ROOT / 'workflows/speckit-flow-plan/flowchart.md').read_text()
        mutations = {
            'phantom-loop-agent': ('plan-output-loop<br/>condition:', 'plan-output-loop<br/>(FlowKit-Reviewer)condition:'),
            'missing-agent': ('<br/>(FlowKit-Planner)', ''),
            'wrong-agent': ('(FlowKit-Planner)', '(FlowKit-Tasker)'),
            'wrong-command': ('command: speckit.plan', 'command: speckit.tasks'),
            'wrong-id': ('prepare-plan-request', 'prepare-other-request'),
            'wrong-shape': ('prepare["prepare-plan-request"]', 'prepare(["prepare-plan-request"])'),
            'missing-outline': ('class create,verify delegated', 'class verify delegated'),
            'phantom-outline': ('class create,verify delegated', 'class loop,create,verify delegated'),
            'wrong-entry': ('start --> loop', 'start --> create'),
            'wrong-cap': ('max_iterations: 5', 'max_iterations: 6'),
        }
        for defect, (before, after) in mutations.items():
            with self.subTest(defect=defect):
                self.assertIn(before, original)
                with self.assertRaises(AssertionError):
                    self.assert_diagram_metadata(workflow, original.replace(before, after))

    def test_manualPlanAndTasksPreserveIndependentSemanticReviewContract(self) -> None:
        readme = (ROOT / 'workflows/README.md').read_text()
        for purpose, heading, following, author, review_id in (
            ('plan', 'planning', 'task-generation', 'FlowKit-Planner', 'verify-plan-output'),
            ('tasks', 'task-generation', 'analysis and remediation', 'FlowKit-Tasker', 'verify-task-output'),
        ):
            with self.subTest(workflow=purpose):
                manual = readme.split('## Manual ' + heading + ' path', 1)[1].split(
                    '## Manual ' + following + ' path', 1)[0]
                workflow = next(w for w in self.inventory.load_workflows()
                                if w['workflow']['id'] == 'speckit-flow-' + purpose)
                review = find_step(workflow['steps'], review_id)
                prepare = workflow['steps'][0]['steps'][0]
                self.assertEqual('FlowKit-Reviewer', review['flow_kit']['agent'])
                self.assertEqual(author, workflow['steps'][0]['steps'][1]['flow_kit']['agent'])
                self.assertEqual(5, workflow['steps'][0]['max_iterations'])
                for field in ('artifact_location', 'violated_requirement', 'observed_deficiency', 'exact_correction'):
                    self.assertIn(field, manual)
                    self.assertIn(field, review['prompt'])
                    self.assertIn(field, prepare['prompt'])
                for phrase in ('independent FlowKit-Reviewer', 'structural and semantic', author,
                               'verbatim', 'Fresh review', 'substantive resolution',
                               'new blocking findings', 'Wording-only or digest-only',
                               'renamed or repeated findings', 'successful commands',
                               "operator's answer", 'never infer', 'five-pass safety limit'):
                    self.assertIn(phrase, manual)
                self.assertNotIn('not design quality', manual)
                self.assertIn('required-file production alone', manual)
                self.assertIn('preserving completed design' if purpose == 'plan' else
                              'preserving task IDs, completion markers', manual)

    def test_assessmentPromptsDeclareBothIdentifierGrammars(self) -> None:
        protocol = (ROOT / "controllers/flow-kit/controller-protocol.md").read_text()
        self.assertIn("must omit `next_step_id`, `gate_step_id`, and `resume_action`", protocol)
        self.assertNotIn("exactly one route field", protocol)
        grammar = "^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$"
        assessed = set()
        for workflow in self.inventory.load_workflows():
            for node, _, _ in self.inventory._walk(workflow["steps"]):
                prompt = node.get("prompt", "")
                if node.get("type") != "prompt" or "reason_code" not in prompt:
                    continue
                with self.subTest(workflow=workflow["workflow"]["id"], step=node["id"]):
                    self.assertIn(f"Both `reason_code` and `resume_action` must match `{grammar}`", prompt)
                    self.assertIn("never use underscores or spaces", prompt)
                    self.assertIn("For `complete`, omit `next_step_id`, `gate_step_id`, and `resume_action`", prompt)
                    self.assertIn("for `continue`, include only `next_step_id` targeting a declared loop-body step", prompt)
                    self.assertIn("for `blocked`, include only a stable `resume_action`", prompt)
                    self.assertNotIn("exactly one state-appropriate route", prompt)
                    assessed.add(workflow["workflow"]["id"])
        self.assertEqual({"speckit-flow-" + purpose for purpose in (
            "analyze-remediate", "clarify", "closeout", "converge", "implement",
            "plan", "tasks", "wiki-lint-update")}, assessed)

    def test_semanticReviewChanges_preserveReviewedExactTopologyAndBounds(self) -> None:
        baseline = json.loads((ROOT / 'tests/consumer-fixtures/semantic-review-topology.json').read_text())
        def topology(nodes):
            return [{k: topology(v) if k in ('steps', 'default') else
                {b: topology(c) for b, c in v.items()} if k == 'cases' else v
                for k, v in n.items() if k in ('id', 'type', 'command', 'condition',
                    'max_iterations', 'assessment_before_correction', 'assessment_only_first_pass',
                    'expression', 'cases', 'default', 'steps', 'flow_kit')} for n in nodes]
        for purpose, expected in baseline.items():
            workflow = yaml.safe_load((ROOT / 'workflows' / ('speckit-flow-' + purpose) / 'workflow.yml').read_text())
            with self.subTest(workflow=purpose):
                self.assertEqual(expected, topology(workflow['steps']))

if __name__ == "__main__":
    unittest.main()

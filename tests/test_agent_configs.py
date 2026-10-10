"""Validate repository-local Codex agent definitions used by workflows."""

from __future__ import annotations

import tomllib
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]
EXPECTED_AGENTS = {
    "farmboy-roadmap-agent.toml": "FarmBoy Roadmap Agent",
    "farmboy-specifier.toml": "FarmBoy Specifier",
    "farmboy-planner.toml": "FarmBoy Planner",
    "farmboy-tasker.toml": "FarmBoy Tasker",
    "farmboy-reviewer.toml": "FarmBoy Reviewer",
    "farmboy-coder.toml": "FarmBoy Coder",
    "farmboy-code-reviewer.toml": "FarmBoy Code Reviewer",
    "farmboy-wiki-curator.toml": "FarmBoy Wiki Curator",
    "farmboy-readiness-checker.toml": "FarmBoy Readiness Checker",
}
def walk_steps(steps: list[dict]):
    """Yield each workflow node across switch branches and loop bodies."""
    for step in steps:
        yield step
        for branch in step.get("cases", {}).values():
            yield from walk_steps(branch)
        yield from walk_steps(step.get("default", []))
        yield from walk_steps(step.get("steps", []))


class AgentConfigTests(unittest.TestCase):
    """All workflow assignments resolve to native, role-specific TOML files."""

    def test_agentFiles_haveExpectedNamesAndRequiredInstructions(self) -> None:
        agent_dir = ROOT / "agents/farmboy/agents"
        self.assertEqual(set(EXPECTED_AGENTS), {path.name for path in agent_dir.glob("*.toml")})
        for filename, expected_name in EXPECTED_AGENTS.items():
            with self.subTest(agent=expected_name):
                data = tomllib.loads((agent_dir / filename).read_text(encoding="utf-8"))
                self.assertEqual(expected_name, data.get("name"))
                self.assertTrue(data.get("description", "").strip())
                self.assertTrue(data.get("developer_instructions", "").strip())
                self.assertEqual(expected_name, tomllib.loads((agent_dir / filename).read_text())['name'])

    def test_approvedSettingsAndOutputContracts_areExplicit(self) -> None:
        for filename in EXPECTED_AGENTS:
            data = tomllib.loads((ROOT / "agents/farmboy/agents" / filename).read_text())
            if filename in ("farmboy-coder.toml", "farmboy-tasker.toml"):
                pair = ("gpt-6-luna", "high")
            else:
                effort = "low" if filename in ("farmboy-roadmap-agent.toml", "farmboy-wiki-curator.toml") else "medium" if filename in ("farmboy-code-reviewer.toml", "farmboy-readiness-checker.toml") else "high"
                model = "gpt-6-luna" if filename == "farmboy-readiness-checker.toml" else "gpt-6.1-sol"
                pair = (model, effort)
            with self.subTest(agent=filename):
                self.assertEqual(pair, (data.get("model"), data.get("model_reasoning_effort")))
                self.assertEqual({"name", "description", "developer_instructions", "model", "model_reasoning_effort"}, set(data))
                for text in ("kind: question", "same child", "blocker", "evidence", "step_id"):
                    self.assertIn(text, data["developer_instructions"])

    def test_everyActiveWorkflowAssignment_resolvesExactlyOnce(self) -> None:
        agent_names = set(EXPECTED_AGENTS.values())
        workflow_paths = sorted((ROOT / "workflows").glob("farmboy-*/workflow.yml"))
        active = [path for path in workflow_paths if path.parent.name != "farmboy-start-feature"]
        self.assertEqual(10, len(active))
        assignments = []
        for path in active:
            definition = yaml.safe_load(path.read_text(encoding="utf-8"))
            for step in walk_steps(definition.get("steps", [])):
                farmboy = step.get("farmboy", {})
                if farmboy.get("delegated") is True:
                    name = farmboy.get("agent")
                    self.assertIn(name, agent_names, f"{path.name}:{step.get('id')}")
                    assignments.append((path, step.get("id"), name))
        expected_count = sum(1 for path in active for step in walk_steps(yaml.safe_load(path.read_text())["steps"]) if step.get("farmboy", {}).get("delegated") is True)
        self.assertEqual(expected_count, len(assignments))
        self.assertGreater(expected_count, 0)
        self.assertEqual(agent_names, {name for _, _, name in assignments})

    def test_authoringRoles_allowRequiredSelfChecksButKeepIndependentReviewSeparate(self) -> None:
        for filename in ("farmboy-specifier.toml", "farmboy-planner.toml", "farmboy-tasker.toml"):
            instructions = tomllib.loads((ROOT / "agents/farmboy/agents" / filename).read_text())["developer_instructions"]
            with self.subTest(agent=filename):
                self.assertIn("Complete command-required self-checks and quality checklists", instructions)
                self.assertIn("do not replace independent review by another assigned agent", instructions)
                self.assertIn("Do not", instructions)
                self.assertIn("act as the independent reviewer of your own", instructions)

    def test_authoringAndReviewAssignments_useDifferentRoles(self) -> None:
        def assignments(workflow_id: str) -> dict[str, str]:
            path = ROOT / "workflows" / workflow_id / "workflow.yml"
            definition = yaml.safe_load(path.read_text(encoding="utf-8"))
            return {
                step["id"]: step["farmboy"]["agent"]
                for step in walk_steps(definition.get("steps", []))
                if step.get("farmboy", {}).get("delegated") is True
            }

        plan = assignments("farmboy-plan")
        tasks = assignments("farmboy-tasks")
        implement = assignments("farmboy-implement")
        self.assertNotEqual(plan["create-plan"], plan["verify-plan-output"])
        self.assertNotEqual(tasks["generate-tasks"], tasks["verify-task-output"])
        self.assertNotEqual(implement["run-scoped-source-implementation"], implement["assess-implementation-after-pass"])
        self.assertEqual("FarmBoy Code Reviewer", implement["assess-implementation-after-pass"])


    def test_postImplementationReviewNodes_useDistinctCodeReviewerAndCoder(self) -> None:
        for purpose, review_id, coder_id in (
            ('implement', 'assess-implementation-after-pass', 'run-scoped-source-implementation'),
            ('converge', 'assess-convergence', 'implement-remediation'),
            ('closeout', 'assess-closeout-debrief', 'implement-closeout-eligible-tasks'),
        ):
            definition = yaml.safe_load((ROOT / 'workflows' / ('farmboy-' + purpose) / 'workflow.yml').read_text())
            assignments = {n['id']: n.get('farmboy', {}).get('agent') for n in walk_steps(definition['steps'])}
            with self.subTest(workflow=purpose):
                self.assertEqual('FarmBoy Code Reviewer', assignments[review_id])
                self.assertEqual('FarmBoy Coder', assignments[coder_id])
                self.assertNotEqual(assignments[review_id], assignments[coder_id])

if __name__ == "__main__":
    unittest.main()

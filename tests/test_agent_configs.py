"""Validate repository-local Codex agent definitions used by workflows."""

from __future__ import annotations

import tomllib
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]
EXPECTED_AGENTS = {
    "flowkit-roadmap-agent.toml": "FlowKit-Roadmap Agent",
    "flowkit-specifier.toml": "FlowKit-Specifier",
    "flowkit-planner.toml": "FlowKit-Planner",
    "flowkit-tasker.toml": "FlowKit-Tasker",
    "flowkit-reviewer.toml": "FlowKit-Reviewer",
    "flowkit-coder.toml": "FlowKit-Coder",
    "flowkit-code-reviewer.toml": "FlowKit-Code Reviewer",
    "flowkit-wiki-curator.toml": "FlowKit-Wiki Curator",
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
        agent_dir = ROOT / ".codex/agents"
        self.assertEqual(set(EXPECTED_AGENTS), {path.name for path in agent_dir.glob("*.toml")})
        for filename, expected_name in EXPECTED_AGENTS.items():
            with self.subTest(agent=expected_name):
                data = tomllib.loads((agent_dir / filename).read_text(encoding="utf-8"))
                self.assertEqual(expected_name, data.get("name"))
                self.assertTrue(data.get("description", "").strip())
                self.assertTrue(data.get("developer_instructions", "").strip())
                canonical = ROOT / "agents/flow-kit/agents" / filename
                self.assertEqual(canonical.read_bytes(), (agent_dir / filename).read_bytes())

    def test_approvedSettingsAndOutputContracts_areExplicit(self) -> None:
        for filename in EXPECTED_AGENTS:
            data = tomllib.loads((ROOT / "agents/flow-kit/agents" / filename).read_text())
            if filename in ("flowkit-coder.toml", "flowkit-tasker.toml"):
                pair = ("gpt-6-luna", "high")
            else:
                effort = "low" if filename in ("flowkit-roadmap-agent.toml", "flowkit-wiki-curator.toml") else "medium" if filename == "flowkit-code-reviewer.toml" else "high"
                pair = ("gpt-6.1-sol", effort)
            with self.subTest(agent=filename):
                self.assertEqual(pair, (data.get("model"), data.get("model_reasoning_effort")))
                self.assertEqual({"name", "description", "developer_instructions", "model", "model_reasoning_effort"}, set(data))
                for text in ("kind: question", "same child", "blocker", "evidence", "step_id"):
                    self.assertIn(text, data["developer_instructions"])

    def test_everyActiveWorkflowAssignment_resolvesExactlyOnce(self) -> None:
        agent_names = set(EXPECTED_AGENTS.values())
        workflow_paths = sorted((ROOT / "workflows").glob("speckit-flow-*/workflow.yml"))
        active = [path for path in workflow_paths if path.parent.name != "speckit-flow-start-feature"]
        self.assertEqual(10, len(active))
        assignments = []
        for path in active:
            definition = yaml.safe_load(path.read_text(encoding="utf-8"))
            for step in walk_steps(definition.get("steps", [])):
                flow_kit = step.get("flow_kit", {})
                if flow_kit.get("delegated") is True:
                    name = flow_kit.get("agent")
                    self.assertIn(name, agent_names, f"{path.name}:{step.get('id')}")
                    assignments.append((path, step.get("id"), name))
        expected_count = sum(1 for path in active for step in walk_steps(yaml.safe_load(path.read_text())["steps"]) if step.get("flow_kit", {}).get("delegated") is True)
        self.assertEqual(expected_count, len(assignments))
        self.assertGreater(expected_count, 0)
        self.assertEqual(agent_names, {name for _, _, name in assignments})

    def test_authoringRoles_allowRequiredSelfChecksButKeepIndependentReviewSeparate(self) -> None:
        for filename in ("flowkit-specifier.toml", "flowkit-planner.toml", "flowkit-tasker.toml"):
            instructions = tomllib.loads((ROOT / ".codex/agents" / filename).read_text())["developer_instructions"]
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
                step["id"]: step["flow_kit"]["agent"]
                for step in walk_steps(definition.get("steps", []))
                if step.get("flow_kit", {}).get("delegated") is True
            }

        plan = assignments("speckit-flow-plan")
        tasks = assignments("speckit-flow-tasks")
        implement = assignments("speckit-flow-implement")
        self.assertNotEqual(plan["create-plan"], plan["verify-plan-output"])
        self.assertNotEqual(tasks["generate-tasks"], tasks["verify-task-output"])
        self.assertNotEqual(implement["implement-eligible-work"], implement["assess-implementation-after-pass"])
        self.assertEqual("FlowKit-Code Reviewer", implement["assess-implementation-after-pass"])


    def test_postImplementationReviewNodes_useDistinctCodeReviewerAndCoder(self) -> None:
        for purpose, review_id, coder_id in (
            ('implement', 'assess-implementation-after-pass', 'implement-eligible-work'),
            ('converge', 'assess-convergence', 'implement-remediation'),
            ('closeout', 'assess-closeout-debrief', 'implement-closeout-eligible-tasks'),
        ):
            definition = yaml.safe_load((ROOT / 'workflows' / ('speckit-flow-' + purpose) / 'workflow.yml').read_text())
            assignments = {n['id']: n.get('flow_kit', {}).get('agent') for n in walk_steps(definition['steps'])}
            with self.subTest(workflow=purpose):
                self.assertEqual('FlowKit-Code Reviewer', assignments[review_id])
                self.assertEqual('FlowKit-Coder', assignments[coder_id])
                self.assertNotEqual(assignments[review_id], assignments[coder_id])

if __name__ == "__main__":
    unittest.main()

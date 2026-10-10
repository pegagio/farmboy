"""Contract checks for reusable merge-bounded active-agent guidance."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
GUIDANCE = ROOT / "docs/merge-bounded-flow-back.md"


class ConsumerAdoptionGuidanceTests(unittest.TestCase):
    def test_active_guidance_covers_all_model_rules_and_operator_control(self) -> None:
        text = GUIDANCE.read_text(encoding="utf-8").lower()
        for phrase in (
            "one mutable change set", "changes flow back", "designated integration branch",
            "new feature", "active agent guidance", "operator", "farmboy",
            "analysis/remediation", "convergence", "pre-merge", "missing checks",
            "unresolved divergence",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_agent_guidance_does_not_instruct_independent_workflow_invocation(self) -> None:
        text = GUIDANCE.read_text(encoding="utf-8").lower()
        self.assertIn("must not launch", text)
        self.assertIn("operator", text)
        self.assertIn("underlying commands", text)


if __name__ == "__main__":
    unittest.main()

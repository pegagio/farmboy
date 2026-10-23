"""Focused source/return boundaries; these do not certify model obedience."""
from pathlib import Path
import hashlib
import json
import re
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
QUESTIONS = ["Are they reasonable for the scope of the feature?", "Do they add unnecessary machinery or ceremony?", "Do they align with the feature's intent?", "Is the architecture sound?", "Can the plan and/or tasks be tightened without redesigning?", "Is the execution checklist appropriate, or is it overly elaborate?"]

class ContractTests(unittest.TestCase):
    def test_generic_body_and_portable_copy(self):
        rel = Path('.agents/skills/farmboy-review-implementation-plan/SKILL.md')
        text = (ROOT / rel).read_text()
        for question in QUESTIONS:
            self.assertEqual(text.count(question), 1)
        for phrase in ['Standalone', 'same session', 'report_reference', 'reviewed_candidate', 'reviewer_mandate', 'findings', 'disposition', 'incomplete', 'without also executing the body', 'verified current', 'No material authorship', 'optional', 'proposal bytes']:
            self.assertIn(phrase, text)
        for command in ['feature run acquire', 'feature handoff apply', 'feature run release']:
            self.assertNotIn(command, text)
        self.assertNotRegex(text, r'/Users/|/home/[^~]|schema20|Feature9')
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / rel
            p.parent.mkdir(parents=True)
            p.write_text(text)
            self.assertEqual(hashlib.sha256(p.read_bytes()).digest(), hashlib.sha256((ROOT / rel).read_bytes()).digest())

    def test_adapter_boundary_and_existing_segments(self):
        a = (ROOT / '.agents/skills/farmboy-diagram-work/SKILL.md').read_text()
        n = (ROOT / '.agents/skills/farmboy-diagram-work/references/native-protocol.md').read_text()
        for phrase in ['solely owns native acquisition/reuse', 'Invoke farmboy-review-implementation-plan', 'same session', 'invalid', 'release/readback', 'sandbox_permissions=require_escalated', 'broad reusable approval rule']:
            self.assertIn(phrase, a)
        for phrase in ['review_grant', 'review_evidence', 'plan_approved', 'plan_revision_required', 'specification_change_required', 'reviewer_owner', 'reviewer_session', 'delegate-plan-review', 'assessment.approval_id', 'context.applicable_approval']:
            self.assertIn(phrase, n)
        for entry in ['farmboy-prepare-specification', 'farmboy-prepare-implementation-plan', 'farmboy-deliver-approved-plan']:
            self.assertIn(entry, a)

    def test_conditioned_planning_guidance_and_example(self):
        text = (ROOT / '.agents/skills/farmboy-diagram-work/references/native-protocol.md').read_text()
        section = text.split('### Conditional approval applicability', 1)[1].split('\n## ', 1)[0]
        for phrase in ['assessment.conditions', 'truthful', 'exact approved artifacts', 'current requested phase',
                       'blind copying', 'placeholder', 'without conditions', 'unresolved', 'TEST ONLY',
                       'feature planning show --feature', '--request-file', 'no run', 'definitive acquire rejection',
                       'no resubmission', 'uncertain', 'absent operation']:
            self.assertIn(phrase, section)
        example = json.loads(re.search(r'<!-- planning-offer-example -->\s*```json\s*(.*?)```', section, re.S)[1])
        self.assertEqual(set(example), {'contract_version', 'expected_revision', 'expected_queue_revision',
                                      'dependencies', 'owner', 'session', 'pinned_handoff', 'approval_id', 'assessment',
                                      'expected_head', 'repository_id', 'instance_id', 'worktree_key', 'workspace_clean'})
        self.assertEqual(example['contract_version'], 9)
        self.assertEqual(example['approval_id'], example['assessment']['approval_id'])
        self.assertTrue(example['assessment']['conditions'])
        self.assertIn('TEST ONLY', example['assessment']['rationale'])
        self.assertIn('approved specification', ' '.join(example['assessment']['conditions']))
        self.assertIn('planning', ' '.join(example['assessment']['conditions']))
        self.assertNotIn('plan_approval_id', example)
        for field in ['workspace', 'branch', 'segment', 'purpose', 'discovery_selected']:
            self.assertNotIn(field, example)
            self.assertIn(field, section)
        self.assertIn('planning-handoff', section)
        self.assertIn('not a plan approval', section)

    def test_return_contract_and_no_implicit_adoption(self):
        t = (ROOT / 'docs/review-implementation-plan.md').read_text()
        for phrase in ['report_reference', 'reviewed_candidate', 'reviewer_mandate', 'findings', 'disposition', 'incomplete', 'SHA-256', 'planning-return', 'specification-escalation', 'non-blocking', 'same session', 'explicit', 'consumer refresh']:
            self.assertIn(phrase.lower(), t.lower())
        self.assertIn('missing', t)
        self.assertIn('invalid', t)
        self.assertNotIn('/Users/', t)

if __name__ == '__main__':
    unittest.main()

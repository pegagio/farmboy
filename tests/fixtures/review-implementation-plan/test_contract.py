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

    def test_delivery_reads_committed_review_before_implementation(self):
        t = (ROOT / '.agents/skills/farmboy-deliver-approved-plan/SKILL.md').read_text()
        self.assertLess(t.index('## Consume applicable committed plan-review evidence'), t.index('## Implement, verify and converge'))
        for phrase in ['read the full committed report', 'wrong-feature', 'wrong-candidate', 'working bytes', 'routine flow-back', 'do not use the task list as the failure report']:
            self.assertIn(phrase, t)
        a = (ROOT / '.agents/skills/farmboy-diagram-work/SKILL.md').read_text()
        n = (ROOT / '.agents/skills/farmboy-diagram-work/references/native-protocol.md').read_text()
        self.assertIn('authoritative review references', a)
        for phrase in ['## Delivery review-evidence lookup', 'review_evidence', 'plan_candidate', 'feature operation show', 'unavailable']:
            self.assertIn(phrase, n)

    def test_delivery_obligations_are_not_priority_or_approval_shortcuts(self):
        t = (ROOT / '.agents/skills/farmboy-deliver-approved-plan/SKILL.md').read_text()
        for phrase in ['at any priority', 'priority alone', 'explicitly non-blocking', 'resolution/supersession evidence', 'optional-obligation contradiction', 'no automatic return or re-review']:
            self.assertIn(phrase, t)

    def test_delivery_optional_decisions_and_non_diagram_applicability(self):
        t = (ROOT / '.agents/skills/farmboy-deliver-approved-plan/SKILL.md').read_text()
        for phrase in ['report/item reference', 'adopted or declined', 'concise reason', 'not applicable', 'report-bearing approval', 'neither condition', 'without duplicate notes', 'consider every optional suggestion']:
            self.assertIn(phrase, t)
        self.assertNotIn('feature handoff apply', t)
        self.assertNotIn('feature run acquire', t)

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

    def test_return_consumption_precedes_planning_setup(self):
        t = (ROOT / '.agents/skills/farmboy-prepare-implementation-plan/SKILL.md').read_text()
        self.assertLess(t.index('## Consume findings driving a planning return'), t.index('## Compose the actual core commands'))
        for phrase in ['full committed report', 'originating', 'unresolved reason is incomplete', 'at any priority', 'adopted or declined', 'report-free', 'without duplicate notes']:
            self.assertIn(phrase, t)

    def test_specification_return_uses_ordinary_clarification(self):
        t = (ROOT / '.agents/skills/farmboy-prepare-specification/SKILL.md').read_text()
        a = (ROOT / '.agents/skills/farmboy-diagram-work/SKILL.md').read_text()
        n = (ROOT / '.agents/skills/farmboy-diagram-work/references/native-protocol.md').read_text()
        for phrase in ['## Specification-return continuation', 'full committed report', 'ordinary clarification', 'not fresh drafting', 'genuine question waits', 'unresolved reason is incomplete']:
            self.assertIn(phrase, t)
        for phrase in ['## Supply return review context', 'clarify/clarification', 'known originating', 'no product answers']:
            self.assertIn(phrase, a)
        self.assertIn('## Return review-evidence lookup', n)
        self.assertIn('plan_revision_required', n)
        self.assertIn('specification_change_required', n)

    def test_return_fixture_boundaries_and_cases(self):
        fixture = (ROOT / 'tests/fixtures/review-implementation-plan/prepare_semantic_fixtures.py').read_text()
        for case in ['wrong-feature','wrong-candidate','wrong-route','altered','missing','decoy','resolved','ambiguous','changed','resume']:
            self.assertIn(case, fixture)
        native = (ROOT / 'tests/fixtures/review-implementation-plan/return_native_subject.py').read_text()
        for phrase in ['TEST ONLY', 'exec', 'resume', 'native-wait-observation.json', 'current_run', 'applicable_approval', 'test-only-return-review-handoff']:
            self.assertIn(phrase, native)
        self.assertNotIn('--dangerously-bypass-approvals-and-sandbox', native)
        self.assertNotIn('core.hooksPath', native)
        self.assertNotIn('automation', (ROOT / 'tests/fixtures/review-implementation-plan/return_native_bridge.go.txt').read_text())

    def test_return_contract_and_no_implicit_adoption(self):
        t = (ROOT / 'docs/review-implementation-plan.md').read_text()
        for phrase in ['report_reference', 'reviewed_candidate', 'reviewer_mandate', 'findings', 'disposition', 'incomplete', 'SHA-256', 'planning-return', 'specification-escalation', 'non-blocking', 'same session', 'explicit', 'consumer refresh']:
            self.assertIn(phrase.lower(), t.lower())
        self.assertIn('missing', t)
        self.assertIn('invalid', t)
        self.assertNotIn('/Users/', t)

if __name__ == '__main__':
    unittest.main()

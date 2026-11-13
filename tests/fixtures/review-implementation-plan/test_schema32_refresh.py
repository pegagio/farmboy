"""Consumer package regression checks; not model/session runtime acceptance."""
import ast
import hashlib
import json
from pathlib import Path
import re
import unittest
ROOT = Path(__file__).resolve().parents[3]
ADAPTER = ROOT / '.agents/skills/farmboy-diagram-work'
class Schema32Refresh(unittest.TestCase):
    def test_complete_matched_helpers(self):
        expected = json.loads(Path(__file__).with_name('schema32-helper-hashes.json').read_text())['helpers']
        self.assertEqual(set(expected), {'authorization_context.py', 'checkpoint_roles.py', 'prepare-authorization.py', 'prepare-handoff.py', 'prepare-plan-review.py'})
        for name, digest in expected.items():
            data = (ADAPTER / 'scripts' / name).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), digest)
            ast.parse(data)
        self.assertIn("database_version') == 32", (ADAPTER / 'scripts/prepare-plan-review.py').read_text())
    def test_human_gate_and_entry_precedence(self):
        protocol = (ADAPTER / 'references/native-protocol.md').read_text()
        for phrase in ['quality_contract:1', 'review_preparation_contract:2', 'authorize-plan-quality', 'plan_review_passed', 'awaiting_plan_approval']:
            self.assertIn(phrase, protocol)
        for entry in ['farmboy-request-plan-review', 'farmboy-review-implementation-plan']:
            text = (ROOT / '.agents/skills' / entry / 'SKILL.md').read_text()
            self.assertLess(text.index('## Matched Diagram schema32'), text.index('## Resolve'))
            for phrase in ['quality pass only', 'human', 'Standalone behavior below is unchanged', 'never create a new legacy']:
                self.assertIn(phrase, text)
    def test_operational_reference_links(self):
        for file in [ADAPTER/'SKILL.md', ADAPTER/'references/native-protocol.md']:
            for link in re.findall(r'\]\(([^)]+)\)', file.read_text()):
                if link.startswith(('https:', 'http:', '#')): continue
                self.assertTrue((file.parent/link.split('#')[0]).exists(), (file,link))
    def test_consumer_customizations_preserved(self):
        text=(ADAPTER/'SKILL.md').read_text()
        for header in ['## Supply delivery review context','## Supply return review context']: self.assertIn(header,text)
        protocol=(ADAPTER/'references/native-protocol.md').read_text()
        for header in ['### Conditional approval applicability','## Delivery review-evidence lookup','## Return review-evidence lookup']: self.assertIn(header,protocol)
if __name__ == '__main__': unittest.main()

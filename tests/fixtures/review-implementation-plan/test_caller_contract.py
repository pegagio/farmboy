"""Caller authority/routing and portable fixture contracts; not model-obedience proof."""
from pathlib import Path
import json
import os
import copy
import ast
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
CALLER = ROOT / '.agents/skills/farmboy-request-plan-review/SKILL.md'

class CallerContract(unittest.TestCase):
    def text(self):
        return CALLER.read_text()

    def test_one_operator_entry_and_nonrecursive_body(self):
        t = self.text()
        for phrase in ['one selected independent whole-plan review', 'one concise question', 'actual bounded human mandate', 'at most one reviewer', 'already dispatched', 'do not dispatch again', 'no material authorship']:
            self.assertIn(phrase, t)
        reviewer = (ROOT / '.agents/skills/farmboy-review-implementation-plan/SKILL.md').read_text()
        self.assertIn('farmboy-request-plan-review', reviewer)
        self.assertIn('before becoming the semantic reviewer', reviewer)
        self.assertIn('already dispatched independent reviewer', reviewer)

    def test_existing_authority_and_exact_manual_route(self):
        t = self.text()
        for phrase in ['feature', 'pinned_handoff', 'expected_revision', 'reviewer_owner', 'reviewer_session', 'authorization', 'delegate-plan-review', 'supplied unchanged', 'Review alone is not delegation', 'advice-only', 'no new selector', 'controls', 'separate session']:
            self.assertIn(phrase, t)
        self.assertIn('adapter alone', t)
        self.assertIn('no self-issued grant', t)
        self.assertNotIn('core.hooksPath', t)
        self.assertNotIn('--dangerously-bypass', t)

    def test_collection_resume_and_human_stop(self):
        t = self.text()
        for phrase in ['report_reference', 'reviewed_candidate', 'reviewer_mandate', 'findings', 'disposition', 'incomplete', 'SHA-256', 'accepted native terminal', 'absent owner/claim', 'known session', 'operation', 'denied', 'pending', 'uncertain', 'No automatic repair', 'implementation', 'do not dispatch again']:
            self.assertIn(phrase, t)
        self.assertIn('process exit', t)
        self.assertIn('historical replay', t)

    def test_standalone_and_no_new_framework(self):
        t = self.text()
        for phrase in ['Standalone', 'no Diagram dependency', 'no new API', 'no registry', 'no supervisor', 'Consumer refresh', 'ordinary permissions', 'normal hooks']:
            self.assertIn(phrase, t)
        self.assertNotIn('/Users/', t)

class FixtureContract(unittest.TestCase):
    def test_standalone_inputs_are_complete_and_do_not_launch(self):
        helper = ROOT / 'tests/fixtures/review-implementation-plan/prepare_caller_fixtures.py'
        with tempfile.TemporaryDirectory() as d:
            destination = Path(d) / 'cases'
            subprocess.run([sys.executable, '-B', str(helper), str(destination)], check=True, capture_output=True)
            for mode in ['clean', 'planning', 'product-question']:
                repo = destination / mode
                self.assertTrue((repo / '.agents/skills/farmboy-request-plan-review/SKILL.md').is_file())
                self.assertTrue((repo / 'specs/001-fixture/architecture.md').is_file())
                self.assertEqual(subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True), '')
            self.assertTrue((destination / 'source-manifest.json').is_file())
            requests = json.loads((destination / 'caller-requests.json').read_text())
            self.assertIn('No delegated approval role',requests['missing-mandate'])
            self.assertIn('CONTROLLED',requests['uncertain-resume'])

class CheckpointFixture(unittest.TestCase):
    def test_generated_refusal_hook_preserves_normal_failure(self):
        tree = ast.parse((ROOT / 'tests/fixtures/review-implementation-plan/prepare_caller_fixtures.py').read_text())
        bridge = next(ast.literal_eval(n.args[0]) for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == 'bridge' and n.func.attr == 'write_text')
        body = re.search(r'os.WriteFile\(h,\[\]byte\(`(.*?)`\),0700\)', bridge, re.S).group(1)
        self.assertTrue(body.startswith('#!/bin/sh\n'))
        self.assertNotIn('--no-verify', body)
        self.assertEqual(subprocess.run(['sh','-n'],input=body,text=True,capture_output=True).returncode,0)
        result = subprocess.run(['sh'],input=body,text=True,capture_output=True)
        self.assertEqual(result.returncode,1)
        self.assertIn('TEST ONLY controlled checkpoint refusal',result.stderr)

@unittest.skipUnless(os.environ.get('FARM29_CALLER_FIXTURE'), 'Explicit private native fixture required; source tests are not native proof')
class NativeTransport(unittest.TestCase):
    def test_missing_wrong_stale_and_nonindependent_grants_refuse(self):
        folder = Path(os.environ['FARM29_CALLER_FIXTURE']).resolve()
        fixture = json.loads((folder / 'fixture.json').read_text())
        cli = folder / 'diagram'
        env = os.environ.copy(); env['DIAGRAM_CONFIG'] = fixture['config']
        def invoke(args, wanted=0):
            p = subprocess.run([str(cli),*args,'--file',fixture['store'],'--json'],cwd=fixture['repo'],env=env,capture_output=True,text=True)
            self.assertEqual(p.returncode,wanted,p.stdout+p.stderr)
            return json.loads(p.stdout)
        before = invoke(['feature','show','--feature',fixture['feature']])
        c = before['context']
        request = {'contract_version':9,'expected_revision':c['revision'],'expected_queue_revision':before['queue_revision'],'dependencies':before['dependencies'],
                   'owner':'test-only-caller-reviewer','session':'test-only-caller-reviewer-session','pinned_handoff':c['latest_handoff'],
                   'workspace':c['workspace'],'branch':c['branch'],'expected_head':subprocess.check_output(['git','-C',fixture['repo'],'rev-parse','HEAD'],text=True).strip(),
                   'repository_id':c['repository_id'],'instance_id':c['instance_id'],'worktree_key':c['worktree_key'],'workspace_clean':True,
                   'segment':'review-plan','purpose':'plan-review','approval_id':c['applicable_approval'],
                   'assessment':{'actor':'TEST ONLY evaluator','rationale':'Isolated native grant refusal, not a model or production approval.','evidence':['actual private Git/native input inspected'],'approval_id':c['applicable_approval']}}
        grant = {'feature':fixture['feature'],'pinned_handoff':c['latest_handoff'],'expected_revision':c['revision'],
                 'reviewer_owner':request['owner'],'reviewer_session':request['session'],
                 'authorization':{'actor':'TEST ONLY fixture human','provenance':'Explicit bounded fixture validation under authorized FARM29 delivery; not approval of real work.','decision':'delegate-plan-review','outcome':'Review this disposable candidate only.','approach':'Preserve local count intent and human gates.','conditions':['No implementation, real project or next workflow.']}}
        results = []
        for mode in ['missing','wrong-feature','stale','same-author']:
            r=copy.deepcopy(request);g=copy.deepcopy(grant)
            if mode=='wrong-feature':g['feature']='F29-999'
            if mode=='stale':g['expected_revision']-=1
            if mode=='same-author':r['owner']='different-external-planner';g['reviewer_owner']=r['owner']
            if mode!='missing':r['review_grant']=g
            path=folder/('negative-'+mode+'.json');path.write_text(json.dumps(r))
            out=invoke(['feature','run','acquire','--feature',fixture['feature'],'--operation','test-only-farm29-negative-'+mode,'--request-file',str(path)],1)
            self.assertIn(out['error']['code'],['approval_required','authority_conflict'])
            after=invoke(['feature','show','--feature',fixture['feature']])
            self.assertEqual(after['context']['revision'],before['context']['revision'])
            self.assertFalse(after.get('current_run'));self.assertFalse(after.get('current_claim'))
            results.append({'case':mode,'native_error':out['error']['code'],'revision_unchanged':True,'owner_absent':True})
        (folder/'negative-results.json').write_text(json.dumps(results,indent=2)+'\n')

if __name__ == '__main__':
    unittest.main()

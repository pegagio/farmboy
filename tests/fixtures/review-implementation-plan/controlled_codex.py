#!/usr/bin/env python3
"""TEST ONLY deterministic composition driver, NOT an LLM/Markdown interpreter.

Parent runs a case table through actual launcher. Child models the candidate
adapter/body sequence, reads their actual source and emits real native effects
only in the private fixture. Source checks + this plumbing cannot prove judgment.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
SOURCE=Path(os.environ['FB025_SOURCE'])
CLI=os.environ['FB025_TEST_CLI']

def git(repo,*args):
    return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()

def commit(repo,paths):
    subprocess.run(['git','-C',str(repo),'add','--',*paths],check=True)
    subprocess.run(['git','-C',str(repo),'-c','user.name=Pegagio','-c','user.email=pegagio@example.invalid','-c','commit.gpgsign=false','commit','-qm','TEST ONLY candidate/evidence'],check=True)

def native(repo,store,cfg,*args,request=None,ok=True):
    cmd=[CLI,*args,'--file',str(store),'--json']
    if request is not None:
        p=Path(cfg).parent/'request.json'; p.write_text(json.dumps(request)); cmd+=['--request-file',str(p)]
    env=os.environ.copy(); env['DIAGRAM_CONFIG']=str(cfg)
    p=subprocess.run(cmd,cwd=repo,env=env,text=True,capture_output=True)
    if ok and p.returncode: raise AssertionError((cmd,p.returncode,p.stdout,p.stderr))
    return json.loads(p.stdout) if ok else p

def identity(v,repo):
    c=v['context']
    return dict(repository_id=c['repository_id'],instance_id=c['instance_id'],worktree_key=c['worktree_key'],expected_head=git(repo,'rev-parse','HEAD'),workspace_clean=not git(repo,'status','--porcelain'))

def assessment(v,owner):
    return dict(actor=owner,rationale='TEST ONLY private actual candidate and authority inspection',evidence=['TEST ONLY fixture'],approval_id=v['context']['applicable_approval'])

def child():
    prompt=sys.stdin.read(); first=prompt.index('{'); selection,end=json.JSONDecoder().raw_decode(prompt[first:])
    item=selection['candidate']; grant=selection['review_grant']; repo=Path(selection['directory']); store=selection['store']; cfg=selection['config']; label=selection['operation_prefix']; owner=selection['owner']; session=selection['session']; feature=item['feature']; mode=os.environ['FB025_CASE']
    out=Path(cfg).parent
    trace=[]
    body=(SOURCE/'.agents/skills/farmboy-review-implementation-plan/SKILL.md').read_text(); adapter=(SOURCE/'.agents/skills/farmboy-diagram-work/SKILL.md').read_text()
    assert 'reviewer_mandate' in body and 'solely owns native acquisition/reuse' in adapter
    assert grant==json.loads((out/'grant.json').read_text()); assert owner==grant['reviewer_owner'] and session==grant['reviewer_session']
    current=native(repo,store,cfg,'feature','show','--feature',feature); c=current['context']; original=current['handoff']; spec=original['accepted_spec']; proposal=original['plan_candidate']; original_approval=current['historical_approval']['id']
    trace.append('adapter:verify-grant-and-candidate')
    req=dict(contract_version=9,expected_revision=c['revision'],expected_queue_revision=current['queue_revision'],dependencies=current['dependencies'],owner=owner,session=session,pinned_handoff=c['latest_handoff'],segment='review-plan',purpose='plan-review',workspace=c['workspace'],branch=c['branch'],approval_id=c['applicable_approval'],review_grant=grant,discovery_selected=True,assessment=assessment(current,owner),**identity(current,repo))
    admitted=native(repo,store,cfg,'feature','run','acquire','--feature',feature,'--operation',label+'-acquire',request=req)
    run=admitted['current_run']; trace.append('adapter:acquire')
    # Verify reuse at inner seam without a second native acquisition.
    checked=native(repo,store,cfg,'feature','show','--feature',feature)
    assert checked['current_run']['id']==run['id'] and run['owner']==owner and run['session']==session and run['epoch']>0
    trace.append('body:verified-current-reuse')
    refs=[*spec['artifacts'],*proposal['artifacts']]
    before={a['path']:hashlib.sha256((repo/a['path']).read_bytes()).hexdigest() for a in refs}
    report=Path(spec['artifacts'][0]['path']).parent/'validation/plan-review.md'
    (repo/report).parent.mkdir(parents=True,exist_ok=True)
    questions=['Are they reasonable for the scope of the feature?','Do they add unnecessary machinery or ceremony?',"Do they align with the feature's intent?",'Is the architecture sound?','Can the plan and/or tasks be tightened without redesigning?','Is the execution checklist appropriate, or is it overly elaborate?']
    disposition={'approve':'approve','planning':'planning-return','specification':'specification-escalation'}.get(mode)
    text='# TEST ONLY controlled semantic report\n\n'+''.join(f'{i}. {q}\nTEST ONLY controlled answer; plumbing evidence, no model judgment.\n\n' for i,q in enumerate(questions,1))
    text+=f'Candidate: {json.dumps(proposal,sort_keys=True)}\nReviewer/mandate: {owner}; {json.dumps(grant,sort_keys=True)}\nDisposition: {disposition or "incomplete"}\n'
    if mode=='approve': text+='Optional non-blocking suggestion: shorten an example; no obligation or approval condition.\n'
    (repo/report).write_text(text)
    returned=dict(report_reference=dict(path=str(report),sha256=hashlib.sha256((repo/report).read_bytes()).hexdigest()),reviewed_candidate=dict(feature=feature,spec=spec,proposal=proposal),reviewer_mandate=grant,findings=[],disposition=disposition)
    if mode=='invalid': returned['report_reference']['sha256']='0'*64
    if mode=='missing': returned={}
    if mode=='incomplete': returned['incomplete']='TEST ONLY missing architecture evidence'
    trace.append('body:return-once')
    valid=bool(returned.get('disposition')) and returned.get('reviewed_candidate',{}).get('proposal')==proposal and returned.get('reviewer_mandate')==grant and returned.get('report_reference',{}).get('sha256')==hashlib.sha256((repo/report).read_bytes()).hexdigest()
    assert all(hashlib.sha256((repo/a).read_bytes()).hexdigest()==h for a,h in before.items())
    # Adapter handles persistence; body above never changes authority.
    commit(repo,[str(report)])
    cur=native(repo,store,cfg,'feature','show','--feature',feature)
    base=dict(contract_version=9,expected_revision=cur['context']['revision'],expected_queue_revision=cur['queue_revision'],dependencies=cur['dependencies'],run_id=run['id'],epoch=run['epoch'],owner=owner,pinned_handoff=run['input_handoff'])
    if not valid:
        release={**base,'reason':'TEST ONLY incomplete/invalid body output; no substantive decision'}
        native(repo,store,cfg,'feature','run','release','--feature',feature,'--operation',label+'-release',request=release)
        trace.append('adapter:incomplete-release')
    else:
        mapping={'approve':('plan_approved','approve'),'planning-return':('plan_revision_required','revision-required'),'specification-escalation':('specification_change_required','specification-change-required')}
        outcome,decision=mapping[returned['disposition']]
        review=dict(actor=owner,provenance='TEST ONLY explicit bounded human grant',decision=decision,outcome='TEST ONLY controlled candidate disposition',approach='TEST ONLY native plumbing, not semantic evaluation')
        if decision!='approve': review['requests']=['TEST ONLY spec.md product question' if decision=='specification-change-required' else 'TEST ONLY tasks.md: remove duplicated fixture work within intent']
        final={**base,**identity(cur,repo),'approval_id':c['applicable_approval'],'checkpoint':spec,'plan_candidate':proposal,'review_evidence':dict(commit=git(repo,'rev-parse','HEAD'),artifacts=[dict(path=str(report),sha256=hashlib.sha256((repo/report).read_bytes()).hexdigest())]),'outcome':outcome,'classification':'material' if mode=='specification' else 'routine','questions':['TEST ONLY change product intent?'] if mode=='specification' else [],'review':review,'assessment':assessment(cur,owner)}
        final['assessment'].update(checks_complete=True,closeout_clear=True,resources_assessed=True)
        native(repo,store,cfg,'feature','handoff','apply','--feature',feature,'--operation',label+'-handoff',request=final)
        trace.append('adapter:finalize-once')
    result=native(repo,store,cfg,'feature','show','--feature',feature)
    assert not result.get('current_run') and result['historical_approval']['id']==original_approval
    assert all(hashlib.sha256((repo/a).read_bytes()).hexdigest()==h for a,h in before.items())
    (out/'trace.json').write_text(json.dumps(trace)); (out/'after.json').write_text(json.dumps(result)); (out/'returned.json').write_text(json.dumps(returned))
    print(json.dumps({'type':'turn.completed'}))

def parent(manifest):
    f=json.loads(Path(manifest).read_text()); repo=Path(f['repo']); feature=f['feature']
    # Explicit TEST ONLY private adoption, not a live consumer refresh.
    paths=['.agents/skills/farmboy-review-implementation-plan/SKILL.md','.agents/skills/farmboy-diagram-work/SKILL.md','.agents/skills/farmboy-diagram-work/references/native-protocol.md','docs/review-implementation-plan.md']
    for p in paths:
        dest=repo/p; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(SOURCE/p,dest)
    real=os.environ.get('FB025_MODE')=='real'
    if real:
        route=repo/'AGENTS.md'; route.write_text('# TEST ONLY native review consumer\nExplicit Diagram-enabled review route using the exact candidate executable, private store/config and supplied grant from launcher context. Read actual farmboy-diagram-work then its generic review body. Pegagio explicitly authorized isolated real-session evaluation under Sentinel_ed01a0edd9a081919407404a0e369b2a. TEST ONLY human labels represent this bounded fixture mandate, not production approvals. No material proposal authorship by this reviewer. Preserve approved intent, proposal bytes, and all existing human gates. No real queued work, installation, controls outside fixture, next phase or external repository access. Native transport request files belong beside the supplied private config, outside Git. Follow the adapter on invalid/missing evidence and release truthfully; do not force approval.\n')
        paths.append('AGENTS.md')
    commit(repo,paths)
    modes=['real'] if real else ['approve','planning','specification','incomplete','missing','invalid','missing-grant','wrong-grant','revoked']
    for mode in modes:
        with tempfile.TemporaryDirectory(prefix='fb025-case-') as d:
            root=Path(d); root.chmod(0o700); store=root/'private.db'; cfg=root/'config.yml'
            # Supported consistent SQLite backup, PRIVATE fixture only.
            src=sqlite3.connect('file:'+f['store']+'?mode=ro',uri=True); dest=sqlite3.connect(store); src.backup(dest); dest.close(); src.close(); store.chmod(0o600)
            cfg.write_text('version: 1\ndatastore: '+str(store)+'\n'); cfg.chmod(0o600)
            native(repo,store,cfg,'automation','set','--project','FBTEST','--enabled','true')
            native(repo,store,cfg,'automation','set','--workflow','review-plan','--enabled','true')
            v=native(repo,store,cfg,'feature','show','--feature',feature); c=v['context']
            grant=dict(feature=feature,pinned_handoff=c['latest_handoff'],expected_revision=c['revision'],reviewer_owner='TEST ONLY independent reviewer',reviewer_session='fb025-'+mode,authorization=dict(actor='TEST ONLY human',provenance='TEST ONLY isolated evaluation authority',decision='delegate-plan-review',outcome='TEST ONLY whole-plan review',approach='Preserve TEST ONLY approved intent/UX',conditions=['TEST ONLY no later workflow or live state']))
            if mode=='wrong-grant': grant['feature']='FBTEST-999'
            g=root/'grant.json'; g.write_text(json.dumps(grant)); g.chmod(0o600)
            if mode=='revoked':
                req=dict(contract_version=9,expected_revision=c['revision'],expected_queue_revision=v['queue_revision'],dependencies=v['dependencies'],pinned_handoff=c['latest_handoff'],decision_kind='plan',review_grant=grant,review=dict(actor='TEST ONLY human',provenance='TEST ONLY explicit revoke',decision='revoke-plan-review'),assessment=assessment(v,grant['reviewer_owner']),**identity(v,repo))
                native(repo,store,cfg,'feature','review','record','--feature',feature,'--operation','test-only-revoke',request=req)
            executable=root/'codex'; executable.write_text('#!/bin/sh\nexec '+shlex_quote(sys.executable)+' '+shlex_quote(str(Path(__file__).resolve()))+' --child "$@"\n'); executable.chmod(0o700)
            if real: executable=Path(os.environ['FB025_REAL_CODEX'])
            env=os.environ.copy(); env.update(DIAGRAM_CONFIG=str(cfg),FB025_CASE=mode)
            cmd=[os.environ['FB025_TEST_LAUNCHER'],'--file',str(store),'--diagram',CLI,'--codex',str(executable)]
            if mode!='missing-grant': cmd+=['--review-grant-file',str(g)]
            launch=subprocess.run(cmd,cwd=repo,env=env,text=True,capture_output=True)
            print('TEST ONLY CASE',mode,'exit',launch.returncode,flush=True)
            if real:
                evidence=Path(os.environ['FB025_REAL_EVIDENCE']); evidence.mkdir(parents=True,exist_ok=True)
                (evidence/'launcher-stdout.txt').write_text(launch.stdout); (evidence/'launcher-stderr.txt').write_text(launch.stderr)
                after=native(repo,store,cfg,'feature','show','--feature',feature)
                (evidence/'native-after.json').write_text(json.dumps(after,indent=2))
                import re
                prefixes=re.findall(r'operation prefix (launch-[0-9a-f]+)',launch.stdout+launch.stderr)
                if prefixes:
                    op=native(repo,store,cfg,'feature','operation','show','--feature',feature,'--operation',prefixes[0]+'-acquire')
                    (evidence/'admission-operation.json').write_text(json.dumps(op,indent=2))
                    assert op.get('outcome')!='absent', 'actual review adapter did not acquire'
                assert not after.get('current_run'), 'real reviewer retained native owner'
                reports=list(repo.glob('specs/**/validation/plan-review.md'))
                assert reports, 'actual semantic body did not save report'
                for report in reports: shutil.copyfile(report,evidence/'plan-review.md')
                print('REAL candidate skill observation',after.get('plan_state'),after.get('handoff',{}).get('outcome'),'launcher exit',launch.returncode,flush=True)
                assert after.get('handoff',{}).get('outcome') in ['plan_approved','plan_revision_required','specification_change_required'], 'Real native finalization incomplete; retained observation is not complete-chain acceptance'
                assert launch.returncode==0, 'Real launcher did not confirm completed native disposition'
                continue
            if launch.returncode and mode in ['approve','planning','specification']:
                raise AssertionError((mode,launch.stdout,launch.stderr))
            if mode in ['missing-grant','wrong-grant','revoked']:
                assert launch.returncode!=0 and not (root/'trace.json').exists(),(mode,launch.stdout,launch.stderr)
            else:
                assert (root/'trace.json').exists(),(mode,launch.stdout,launch.stderr)
                trace=json.loads((root/'trace.json').read_text()); assert trace.count('adapter:acquire')==1 and trace.count('body:return-once')==1
                after=json.loads((root/'after.json').read_text()); assert not after.get('current_run')
                expected={'approve':'plan_approved','planning':'plan_revision_required','specification':'specification_change_required'}.get(mode)
                if expected: assert after['handoff']['outcome']==expected and trace.count('adapter:finalize-once')==1
                else: assert launch.returncode!=0 and 'adapter:finalize-once' not in trace and after['plan_state']=='awaiting_plan_review'
                print('TEST ONLY TRACE',mode,trace,flush=True)
    print('TEST ONLY controlled plumbing passed; no model judgment certified.',flush=True)

def shlex_quote(s):
    import shlex
    return shlex.quote(s)

if __name__=='__main__':
    if '--child' in sys.argv: child()
    elif '--fixture' in sys.argv: parent(sys.argv[sys.argv.index('--fixture')+1])
    else: raise SystemExit('TEST ONLY --fixture or --child required')

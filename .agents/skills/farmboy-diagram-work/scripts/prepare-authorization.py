#!/usr/bin/env python3
"""Read-only consumer preflight. Reported scope is not host/operator authentication."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import time
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import authorization_context as a
import checkpoint_roles as roles
_spec=importlib.util.spec_from_file_location('authorization_transport',Path(__file__).with_name('prepare-plan-review.py'))
transport=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(transport)


def regular_bytes(path, limit=a.LIMIT):
    path=Path(path);a.require(path.is_absolute() and not path.is_symlink(),'unsafe_source')
    try:
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        with os.fdopen(fd,'rb') as f:
            before=os.fstat(f.fileno());a.require(stat.S_ISREG(before.st_mode) and before.st_size<=limit,'source_limit')
            raw=f.read(limit+1);after=os.fstat(f.fileno())
        a.require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns) and len(raw)<=limit,'source_changed')
        current=path.stat(follow_symlinks=False)
        a.require((current.st_dev,current.st_ino,current.st_mtime_ns,current.st_size)==(before.st_dev,before.st_ino,before.st_mtime_ns,before.st_size),'source_changed')
        return raw
    except OSError:raise a.Refusal('source_unavailable') from None


def read_source(path, expected=None):
    raw=regular_bytes(path);digest=hashlib.sha256(raw).hexdigest()
    a.require(expected is None or digest==expected,'source_changed')
    return {'value':a.validate(a.decode(raw)),'sha256':digest}


def command(argv, cwd, deadline=None):
    try:
        remaining=30 if deadline is None else min(30,deadline-time.monotonic());a.require(remaining>0,'consumer_timeout')
        code,out,_=transport.run(argv,str(cwd),remaining);a.require(code==0,'consumer_read_failed');return out
    except transport.Failure:raise a.Refusal('consumer_read_unavailable') from None


def native(diagram, store, workspace, *args, deadline=None):
    raw=command([diagram,*args,'--file',store,'--json'],workspace,deadline)
    try:d=a.decode(raw)
    except a.Refusal:raise a.Refusal('invalid_native_response') from None
    a.require(isinstance(d,dict) and not d.get('error'),'native_read_refused');return d


def verify_policy(workspace, policy, deadline=None):
    workspace=Path(workspace)
    def git(*args):return command(['git',*args],workspace,deadline)
    a.require(Path(git('rev-parse','--show-toplevel').decode().strip()).resolve()==workspace.resolve(),'workspace_identity_mismatch')
    def blob(commit,path):
        raw=git('ls-tree','-z',commit,'--',path).split(b'\0')
        a.require(len(raw)==2 and raw[-1]==b'' and b'\t' in raw[0],'unsafe_policy_artifact')
        meta,name=raw[0].split(b'\t',1);a.require(meta.split()[0] in [b'100644',b'100755'] and name.decode()==path,'unsafe_policy_artifact')
        return git('show',commit+':'+path)
    def working(path):
        p=workspace/path
        a.require(p.resolve().is_relative_to(workspace.resolve()),'unsafe_policy_artifact')
        for part in [p,*p.parents]:
            if part==workspace:break
            a.require(not part.is_symlink(),'unsafe_policy_artifact')
        return regular_bytes(p)
    try:
        roles.verify_checkpoint(policy['historical'],blob)
        roles.verify_checkpoint(policy['current'],blob,working)
    except roles.RoleError:raise a.Refusal('policy_stale') from None
    paths={x['path'] for x in policy['current']['artifacts']}
    for required in ['AGENTS.md','.specify/memory/constitution.md','.agents/skills/farmboy-diagram-work/SKILL.md']:
        if (workspace/required).exists():a.require(required in paths,'adoption_evidence_required')
    # Meaning/adoption remains the declared, attributable consumer assessment.
    return len(paths)


def verify_instance(workspace, expected, deadline):
    common=Path(command(['git','rev-parse','--git-common-dir'],workspace,deadline).decode().strip())
    if not common.is_absolute():common=Path(workspace)/common
    actual='instance/'+hashlib.sha256(os.fsencode(str(common.resolve()))).hexdigest()
    a.require(isinstance(expected,str) and expected==actual,'instance_binding_mismatch')


def current_candidate(d, segment):
    run=d.get('current_run')
    claim=d.get('current_claim')
    if claim:return (claim.get('input',{}).get('checkpoint') or {}).get('commit','')
    if run:
        inp=run.get('original_input',{})
        cp=inp.get('references',{}).get('plan_candidate') if segment in ['deliver','review-plan'] else inp.get('checkpoint')
    else:
        h=d.get('handoff') or {}
        cp=h.get('plan_candidate') if segment in ['deliver','review-plan'] else (h.get('accepted_spec') or (d.get('context') or {}).get('enrollment'))
    if segment=='integrate':
        cp=((run or {}).get('original_input',{}).get('references',{}).get('delivery_result') or (d.get('latest_delivery') or {}).get('delivery_result') or {}).get('checkpoint')
    return (cp or {}).get('commit','')


def prepared_recovery(d, selection, workspace, deadline):
    a.require(selection['mode']=='released-continuation','preparation_claim_required')
    entries=(((d.get('context') or {}).get('continuation') or {}).get('entries') or [])
    matching=[x for x in entries if x.get('segment')=='setup' and x.get('purpose')=='draft' and x.get('mode','') in ['', 'execution']]
    a.require(len(matching)==1 and not matching[0].get('hold'),'prepared_recovery_binding_required')
    stop=matching[0].get('stop') or {};ready=stop.get('readiness') or {}
    a.require(stop.get('disposition')=='recoverable' and bool(stop.get('claim_id')) and (ready.get('recovery') or {}).get('former_writer_stopped') is True,'prepared_recovery_binding_required')
    a.require(isinstance(ready.get('workspace'),str) and Path(ready['workspace']).resolve()==Path(workspace).resolve(),'prepared_recovery_workspace_mismatch')
    branch=command(['git','symbolic-ref','HEAD'],workspace,deadline).decode().strip();head=command(['git','rev-parse','HEAD'],workspace,deadline).decode().strip()
    a.require(branch==ready.get('branch') and head==ready.get('expected_head'),'prepared_state_changed')
    if ready.get('workspace_clean') is True:a.require(not command(['git','status','--porcelain'],workspace,deadline).strip(),'prepared_state_changed')
    # Native readiness/OS-writer death remains reported evidence, not independent
    # proof. Existing successor admission/allowance and caller inspection control it.


def inspect_quality_scope(d, selection, pins, run, auth):
    a.require(not selection.get('review_grant') and auth.get('contract_version') == 2
              and auth.get('kind') == 'quality-sequence' and auth.get('state') == 'active', 'quality_scope_required')
    seq=auth.get('sequence')
    try:
        digest=transport.sequence_digest(seq)
    except (transport.Failure,KeyError,TypeError):
        raise a.Refusal('invalid_quality_scope') from None
    a.require(digest == auth.get('sequence_sha256') and seq.get('feature') == selection['feature']
              and seq.get('spec_approval_id') == (d.get('context') or {}).get('applicable_approval')
              and seq.get('authorization',{}).get('decision') == 'authorize-plan-quality', 'quality_scope_mismatch')
    if run:
        original=(run.get('original_input') or {}).get('quality_admission') or {}
        a.require(original.get('publication') == auth.get('publication_operation')
                  and original.get('sequence_sha256') == digest
                  and original.get('reviewer_owner') == selection['owner']
                  and original.get('reviewer_session') == selection['session']
                  and original.get('candidate',{}).get('commit') == selection['candidate'], 'quality_admission_mismatch')
    else:
        a.require(d.get('review_authority_applicable') is True
                  and (d.get('handoff') or {}).get('plan_candidate',{}).get('commit') == selection['candidate'], 'quality_not_applicable')


def inspect(source, selection, workspace, diagram, store, effects, expected=None, deadline=None):
    deadline=time.monotonic()+30 if deadline is None else deadline
    origin=read_source(source,expected);v=origin['value'];a.require(isinstance(selection,dict),'invalid_selection')
    a.shape({k:x for k,x in selection.items() if k!='review_grant'},'project feature segment purpose candidate revision owner session setup_required mode')
    if 'review_grant' in selection:a.require(isinstance(selection['review_grant'],dict) and selection['segment']=='review-plan' and selection['mode']!='finalization','invalid_explicit_review_grant')
    a.require(selection['mode'] in ['', 'revision','finalization','released-continuation','released-delivery'],'unsupported_entry_mode')
    a.require(selection['project']==v['project'],'scope_project_mismatch');a.integer(selection['revision'])
    a.require(type(selection['setup_required']) is bool,'invalid_selection');a.text(selection['owner'],128,True);a.text(selection['session'],128,True)
    if selection['segment']!='dispatcher':a.require(bool(selection['owner'].strip()) and bool(selection['session'].strip()),'recipient_required')
    scope=a.select(v,selection['feature'],selection['segment'],selection['purpose'],selection['candidate'],effects)
    version=native(diagram,store,workspace,'database','version',deadline=deadline)
    a.require(version.get('contract_version')==2 and version.get('database_version')==32 and version.get('supported') is True,'unsupported_database')
    p=native(diagram,store,workspace,'project','show','--key',selection['project'],deadline=deadline)
    a.require(p.get('contract_version')==4 and p.get('project',{}).get('key')==selection['project'] and p['project'].get('status')=='active','project_mismatch')
    workspace=Path(workspace);a.require(workspace.is_absolute() and workspace.is_dir(),'workspace_unavailable')
    revision=selection['revision'];context_present=False
    if selection['segment']=='dispatcher':
        a.require(Path(p['project']['repository']).resolve()==workspace.resolve(),'project_root_mismatch')
        verify_instance(workspace,p['project'].get('instance_id'),deadline)
    else:
        d=native(diagram,store,workspace,'feature','show','--feature',selection['feature'],deadline=deadline);c=d.get('context') or {};run=d.get('current_run')
        context_present=isinstance(d.get('context'),dict)
        observed_revision=c.get('revision') if context_present else (0 if selection['setup_required'] and not d.get('current_run') and not d.get('current_claim') and not d.get('workspace_linked') else None)
        a.integer(observed_revision)
        a.require(d.get('contract_version')==9 and d.get('feature')==selection['feature'] and observed_revision==revision,'stale_native_selection')
        a.require(d.get('issue_state')=='open' and d.get('project_status')=='active','terminal_or_inactive_feature')
        observed_candidate=current_candidate(d,selection['segment'])
        if selection['setup_required'] and not d.get('idea') and not d.get('current_claim'):
            q=native(diagram,store,workspace,'feature','queue','show','--project',selection['project'],deadline=deadline)
            entries=(q.get('queue') or {}).get('entries',[])
            matches=[x for x in entries if x.get('feature')==selection['feature']]
            a.require(q.get('contract_version')==9 and (q.get('queue') or {}).get('project')==selection['project'] and len(matches)==1,'queued_input_required')
            observed_candidate=(matches[0].get('request') or {}).get('commit','')
        captured=(selection['candidate']=='' and selection['segment'] in ['setup','specify'] and selection['purpose']=='draft' and bool(scope['native']['idea_sha256']) and scope['native']['idea_sha256']==(d.get('idea') or {}).get('input_sha256','') and not d.get('historical_approval'))
        a.require(captured or observed_candidate==selection['candidate'],'candidate_mismatch')
        claim=d.get('current_claim')
        if claim:
            a.require(claim.get('owner')==selection['owner'] and claim.get('session')==selection['session'] and isinstance(claim.get('claim_id'),str) and bool(claim['claim_id']) and type(claim.get('epoch')) is int and claim['epoch']>0 and selection['setup_required'],'claim_binding_mismatch')
            a.require('draft' not in effects,'link_before_drafting')
        pins=scope['native']
        a.require(pins['spec_approval']==c.get('applicable_approval','') and pins['plan_approval']==c.get('plan_approval_id',''),'approval_binding_mismatch')
        if run:
            a.require(run.get('owner')==selection['owner'] and run.get('session')==selection['session'] and run.get('segment')==selection['segment'] and run.get('purpose')==selection['purpose'] and run.get('status')=='active','owner_binding_mismatch')
            a.require(revision>=pins['revision'] and run.get('input_handoff','')==pins['handoff'],'native_binding_mismatch')
        else:a.require((revision>=pins['revision'] if claim else revision==pins['revision']) and c.get('latest_handoff','')==pins['handoff'],'native_binding_mismatch')
        if selection['setup_required']:
            verify_instance(workspace,p['project'].get('instance_id'),deadline)
            a.require(not c.get('workspace') and ((bool(selection['candidate']) and not pins['idea_sha256']) or (bool(pins['idea_sha256']) and pins['idea_sha256']==(d.get('idea') or {}).get('input_sha256',''))),'unlinked_binding_mismatch')
            if claim and pins['idea_sha256']:a.require((claim.get('input') or {}).get('idea_sha256')==pins['idea_sha256'],'claim_input_mismatch')
            if Path(p['project']['repository']).resolve()!=workspace.resolve():
                a.require('prepare_workspace' in scope['effects'],'scope_missing')
                if claim is None:prepared_recovery(d,selection,workspace,deadline)
                # The actual same-Git-family preparation worktree is consumer inspected,
                # not yet a native linked association. Existing caller exclusivity/link
                # reports still govern its creation; semantic drafting stays forbidden.
        else:
            a.require(Path(c.get('workspace','')).resolve()==workspace.resolve(),'workspace_binding_mismatch')
            verify_instance(workspace,c.get('instance_id'),deadline)
            branch=command(['git','symbolic-ref','HEAD'],workspace,deadline).decode().strip()
            a.require(branch==c.get('branch'),'branch_binding_mismatch')
            pointer=a.decode(regular_bytes(workspace/'.specify/feature.json'));a.require(isinstance(pointer,dict) and isinstance(pointer.get('feature_directory'),str),'feature_pointer_required')
            directory=workspace/pointer['feature_directory'];a.require(directory.resolve().is_relative_to(workspace.resolve()) and directory.is_dir(),'feature_pointer_mismatch')
            enrolled=(c.get('enrollment') or {}).get('artifacts',[])
            a.require(any((workspace/x['path']).parent.resolve()==directory.resolve() for x in enrolled),'feature_pointer_mismatch')
        if selection['mode']=='finalization':
            entries=((c.get('continuation') or {}).get('entries') or [])
            matching=[x for x in entries if x.get('mode')=='finalization' and x.get('segment')==selection['segment'] and x.get('purpose')==selection['purpose']]
            a.require(len(matching)==1 and not matching[0].get('hold') and ((matching[0].get('stop') or {}).get('readiness') or {}).get('finalization'),'finalization_binding_required')
        if selection['segment']=='review-plan' and selection['mode']!='finalization':
            inspect_quality_scope(d,selection,scope['native'],run,c.get('review_authority') or {})
    count=verify_policy(workspace,scope['policy'],deadline)
    # Detect a changed/replaced/withdrawn carrier during consumer inspection.
    read_source(source,origin['sha256'])
    return {'contract_version':1,'status':'ready','source_sha256':origin['sha256'],'source_id':v['id'],'project':selection['project'],'feature':selection['feature'],'segment':selection['segment'],'purpose':selection['purpose'],'candidate':selection['candidate'],'workspace':str(workspace.resolve()),'native_context_present':context_present,'revision':revision,'owner':selection['owner'],'session':selection['session'],'mode':selection['mode'],'effects':effects,'policy_artifacts':count,'assurance':'consumer_reported','host':a.host_capabilities(),'limitations':['Reference integrity does not authenticate permission or semantic applicability.','Unseen denial history and out-of-band changes are not independently observed.','Consumer ordering is not a filesystem interlock; native and actual host guards remain required.']}


def check_action(args, effect, segment=None, purpose=None, candidate=None):
    """Called before an existing guarded action; never performs that action."""
    deadline=time.monotonic()+30
    source=getattr(args,'authorization_file',None);expected=getattr(args,'authorization_sha256',None)
    a.require((source is None)==(expected is None),'verified_source_and_digest_required')
    if source is None:return None
    a.require(bool(source) and isinstance(expected,str) and len(expected)==64,'verified_source_and_digest_required')
    d=native(args.diagram,args.store,args.workspace,'feature','show','--feature',args.feature,deadline=deadline);c=d.get('context') or {};run=d.get('current_run')
    stage=segment or (run or {}).get('segment');why=purpose or (run or {}).get('purpose')
    a.require(stage in a.STAGES,'selection_required')
    chosen=candidate if candidate is not None else current_candidate(d,stage)
    if stage in ['setup','specify'] and why=='draft' and not d.get('historical_approval'):
        data=read_source(source,expected)['value']
        if any(s['feature']==args.feature and s['segment']==stage and s['purpose']==why and s['candidate']=='' and s['native']['idea_sha256']==(d.get('idea') or {}).get('input_sha256') for s in data['scopes']):chosen=''
    sel={'project':args.feature.rsplit('-',1)[0],'feature':args.feature,'segment':stage,'purpose':why,'candidate':chosen,'revision':c.get('revision'),'owner':args.owner,'session':args.session,'setup_required':not bool(c.get('workspace')),'mode':'finalization' if ((run or {}).get('original_input') or {}).get('finalization_origin') else ''}
    return inspect(source,sel,args.workspace,args.diagram,args.store,effect if isinstance(effect,list) else [effect],expected,deadline)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['source','selection-file','workspace','diagram','store']:p.add_argument('--'+k,required=True)
    p.add_argument('--expected-sha256');p.add_argument('--effect',action='append',required=True);args=p.parse_args()
    try:
        for x in [args.source,args.selection_file,args.workspace,args.diagram,args.store]:a.require(Path(x).is_absolute(),'absolute_paths_required')
        sel=a.decode(regular_bytes(args.selection_file));result=inspect(args.source,sel,args.workspace,args.diagram,args.store,args.effect,args.expected_sha256)
        raw=json.dumps(result,sort_keys=True);a.require(len(raw.encode())<=512<<10,'response_limit');print(raw);return 0
    except (a.Refusal,OSError,ValueError,KeyError,TypeError) as e:
        code=str(e) if isinstance(e,a.Refusal) else 'invalid_consumer_input'
        print(json.dumps({'contract_version':1,'status':'refused','reason':code,'effects':'none'}));return 1

if __name__=='__main__':raise SystemExit(main())

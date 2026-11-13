#!/usr/bin/env python3
"""Prepare one existing ordinary terminal; never acquire, decide, retry or finalize."""
import argparse
import copy
import importlib.util
import json
import os
from pathlib import Path
import re
import tempfile

# Reuse the maintained bounded transport, preserving injectable local wrappers for tests.
try:
    _spec = importlib.util.spec_from_file_location('diagram_review_transport', Path(__file__).with_name('prepare-plan-review.py'))
    _transport = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_transport)
except (ImportError, OSError):
    print(json.dumps(dict(status='failed', reason='incomplete_client_package', effects='no native calls')))
    raise SystemExit(1) from None
Failure, require, run, roles = _transport.Failure, _transport.require, _transport.run, _transport.roles


def native(args, command):
    code, out, _ = run([args.diagram, *command, '--file', args.store, '--json'], args.workspace)
    try:
        value = json.loads(out)
    except (ValueError, UnicodeError):
        raise Failure('invalid_native_response', 'uncertain') from None
    require(isinstance(value, dict), 'invalid_native_envelope')
    if value.get('error'):
        error = value['error']
        reason = error.get('code', 'native_error') if isinstance(error, dict) else 'native_error'
        raise Failure(reason, 'uncertain' if reason == 'outcome_ambiguous' else 'refused')
    require(code == 0, 'native_process_failed')
    return value


def git(args, *command):
    code, out, _ = run(['git', *command], args.workspace)
    require(code == 0, 'git_verification_failed')
    return out


def blob(args, commit, path):
    entry = git(args, 'ls-tree', '-z', commit, '--', path).split(b'\0')
    require(len(entry) == 2 and entry[-1] == b'' and b'\t' in entry[0], 'invalid_artifact_type')
    metadata, name = entry[0].split(b'\t', 1)
    require(metadata.split()[0] in [b'100644', b'100755'] and name.decode() == path, 'invalid_artifact_type')
    return git(args, 'show', commit + ':' + path)


def working(args, path):
    p = Path(args.workspace) / path
    require(p.resolve().is_relative_to(Path(args.workspace).resolve()) and p.is_file()
            and not p.is_symlink(), 'artifact_path_escape_or_missing')
    return p.read_bytes()


def verify(args, cp, current=False):
    return roles.verify_checkpoint(cp, lambda c,p: blob(args,c,p),
                                   (lambda p: working(args,p)) if current else None)


def output(args, declaration, head):
    require(isinstance(declaration, dict) and set(declaration) == {'artifacts'}, 'artifact_only_output_required')
    cp = dict(commit=head, artifacts=declaration['artifacts'])
    verify(args, cp, True)
    return cp


def text_list(value, required=False):
    return isinstance(value, list) and (bool(value) or not required) and all(isinstance(x, str) and x.strip() for x in value)


def prepare(args):
    prior = native(args, ['feature', 'operation', 'show', '--feature', args.feature, '--operation', args.operation])
    require(prior.get('contract_version') == 9 and prior.get('operation_id') == args.operation, 'invalid_operation_response')
    if prior.get('outcome') != 'absent':
        return None, None
    version = native(args, ['database', 'version'])
    require(version.get('contract_version') == 2 and version.get('database_version') == 32
            and version.get('supported') is True, 'unsupported_database')
    v = native(args, ['feature', 'show', '--feature', args.feature])
    require(v.get('contract_version') == 9 and v.get('feature') == args.feature, 'invalid_feature_response')
    n, c = v.get('current_run'), v.get('context')
    require(isinstance(n, dict) and isinstance(c, dict) and not v.get('current_claim'), 'active_ordinary_owner_required')
    require(c.get('revision') == args.revision and type(c.get('revision')) is int, 'stale_selection')
    require(all(n.get(k) == x for k,x in [('id', args.run), ('epoch', args.epoch), ('owner', args.owner),
            ('session', args.session), ('feature', args.feature), ('status', 'active')]), 'owner_binding_mismatch')
    original = n.get('original_input')
    require(isinstance(original, dict) and not original.get('finalization_origin'), 'use_existing_finalization_route')
    root = Path(git(args, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
    require(root == Path(args.workspace).resolve() and n.get('workspace') == args.workspace, 'workspace_mismatch')
    common = Path(git(args, 'rev-parse', '--git-common-dir').decode().strip())
    if not common.is_absolute():
        common = root / common
    import hashlib
    instance = 'instance/' + hashlib.sha256(os.fsencode(str(common.resolve()))).hexdigest()
    require(n.get('instance_id') == instance and n.get('repository_id') == args.repository
            and re.fullmatch(r'repository/(?:[0-9a-f]{32}|[0-9a-f]{64})', args.repository)
            and n.get('worktree_key') == args.worktree and re.fullmatch(r'worktree/[0-9a-f]{32}', args.worktree), 'identity_mismatch')
    branch = git(args, 'symbolic-ref', 'HEAD').decode().strip()
    head = git(args, 'rev-parse', 'HEAD').decode().strip()
    require(branch == n.get('branch') and not git(args, 'status', '--porcelain'), 'branch_or_cleanliness_mismatch')
    # Read at most the existing transport bound; never consume unbounded caller JSON.
    declaration_path = Path(args.output_file)
    require(declaration_path.is_file() and not declaration_path.is_symlink(), 'invalid_output_declaration_file')
    with declaration_path.open('rb') as src:
        raw = src.read((1 << 20) + 1)
    require(len(raw) <= 1 << 20, 'output_declaration_limit')
    def unique(pairs):
        value = {}
        for k,x in pairs:
            require(k not in value, 'duplicate_json_member')
            value[k] = x
        return value
    body = json.loads(raw, object_pairs_hook=unique)
    require(isinstance(body, dict), 'invalid_output_declaration')
    stage, purpose = n.get('segment'), n.get('purpose')
    selected = roles.stage_roles(stage, purpose, body.get('outcome'))
    allowed = {'outcome', 'classification', 'questions', 'assessment', *selected}
    if stage == 'review-plan': allowed.add('review')
    if stage == 'deliver' and body.get('outcome') == 'review_required': allowed.add('review_needed')
    require(set(body) == allowed, 'stage_output_fields_mismatch')
    require(body['classification'] in ['routine', 'material'] and text_list(body['questions']), 'invalid_outcome_evidence')
    a = body['assessment']
    require(isinstance(a, dict) and set(a) <= {'actor','rationale','evidence','conditions','checks_complete','closeout_clear','resources_assessed'}
            and a.get('actor') == args.owner and isinstance(a.get('rationale'),str) and a['rationale'].strip()
            and text_list(a.get('evidence'),True) and text_list(a.get('conditions'),True), 'missing_assessment')
    for key in ['checks_complete','closeout_clear','resources_assessed']:
        if key in a: require(type(a[key]) is bool, 'invalid_assessment')
    a = copy.deepcopy(a)
    for key in ['spec_approval_id','plan_approval_id','result_review_id']:
        if original.get(key): a[{'spec_approval_id':'approval_id'}.get(key,key)] = original[key]
    r = dict(contract_version=9, expected_revision=args.revision, expected_queue_revision=v.get('queue_revision'),
             dependencies=v.get('dependencies'), run_id=args.run, epoch=args.epoch, owner=args.owner,
             pinned_handoff=n.get('input_handoff',''), expected_head=head, repository_id=args.repository,
             instance_id=instance, worktree_key=args.worktree, workspace_clean=True, outcome=body['outcome'],
             questions=body['questions'], classification=body['classification'], assessment=a)
    require(type(r['expected_queue_revision']) is int and isinstance(r['dependencies'],list), 'missing_queue_facts')
    # Verify immutable original inputs at their own commits. Never require an old input's
    # tasks/report working bytes to equal newly completed output, or repin those references.
    verify(args, original['checkpoint'])
    refs = original.get('references', {})
    for key in ['accepted_spec','plan_candidate']:
        if refs.get(key): verify(args, refs[key])
    historical = v.get('historical_approval')
    if historical: verify(args, historical['checkpoint'])
    if stage in ['review-plan', 'deliver']:
        require(isinstance(refs.get('accepted_spec'),dict) and isinstance(refs.get('plan_candidate'),dict), 'missing_original_roles')
        r.update(checkpoint=refs['accepted_spec'], plan_candidate=refs['plan_candidate'])
    for key in selected:
        if key == 'delivery_result':
            d = body[key]
            require(isinstance(d,dict) and set(d)=={'checkpoint','required_checks','convergence','closeout'}, 'invalid_delivery_output')
            d = copy.deepcopy(d);d['checkpoint']=output(args,d['checkpoint'],head)
            artifacts=d['checkpoint']['artifacts'];require(d['convergence'] in artifacts and d['closeout'] in artifacts,'missing_delivery_member')
            require(isinstance(d['required_checks'],list) and d['required_checks'], 'missing_required_checks')
            names=set()
            for check in d['required_checks']:
                require(isinstance(check,dict) and set(check)=={'name','reported_outcome','artifact'}
                        and isinstance(check['name'],str) and check['name'].strip() and check['name'] not in names
                        and check['reported_outcome']=='passed' and check['artifact'] in artifacts,'invalid_required_check')
                names.add(check['name'])
            require(all(a.get(k) is True for k in ['checks_complete','closeout_clear','resources_assessed']), 'incomplete_delivery_assessment')
            r[key]=d
        else:
            r[key]=output(args,body[key],head)
    if stage in ['specify','clarify','plan']:
        names=[Path(x['path']).name for x in r['checkpoint']['artifacts']]
        require('spec.md' in names and not any(x in ['plan.md','tasks.md'] or 'analysis' in x for x in names), 'invalid_accepted_spec_role')
        if historical:
            pair=historical['id']+'@'+historical['checkpoint']['commit']+'..'+r['checkpoint']['commit']
            inspection=dict(pair=pair if pair in args.inspected_role_pair else None,applicability=args.approval_applicability,evidence=args.role_evidence,conditions=args.role_condition)
            evidence=roles.verify_roles(historical['checkpoint'],r['checkpoint'],r.get('plan_candidate'),
                                       lambda c,p:blob(args,c,p),lambda p:working(args,p),inspection,historical['id'])
            a['evidence'] += evidence
            if evidence:a['conditions'] += args.role_condition
    if stage == 'review-plan':
        # The admitted proposal and accepted input are current review INPUTS, not
        # historical output that a report can supersede. Report membership grants
        # no exception to their exact committed/working verification.
        require(isinstance(historical,dict) and historical.get('id') == original.get('spec_approval_id'),
                'missing_original_spec_approval')
        pair=historical['id']+'@'+historical['checkpoint']['commit']+'..'+refs['accepted_spec']['commit']
        inspection=dict(pair=pair if pair in args.inspected_role_pair else None,
                        applicability=args.approval_applicability,evidence=args.role_evidence,conditions=args.role_condition)
        evidence=roles.verify_roles(historical['checkpoint'],refs['accepted_spec'],refs['plan_candidate'],
                                   lambda c,p:blob(args,c,p),lambda p:working(args,p),inspection,historical['id'])
        a['evidence'] += evidence
        if evidence:a['conditions'] += args.role_condition
    elif stage == 'deliver' and body['outcome'] != 'review_required':
        require(isinstance(original.get('plan_approval_id'),str) and original['plan_approval_id'].strip(),
                'missing_original_plan_approval')
        # Frozen semantics are verified at their historical commits; any working evolution
        # must be explicitly covered by verified current output and inspected under its
        # own approval pair. Completed task markers are not silently copied into the old plan.
        current = r.get('review_evidence') or r['delivery_result']['checkpoint']
        for key, approval_key in [('accepted_spec','spec_approval_id'),('plan_candidate','plan_approval_id')]:
            old = refs[key]
            pair=original.get(approval_key,'')+'@'+old['commit']+'..'+current['commit']
            inspection=dict(pair=pair if pair in args.inspected_role_pair else None,
                            applicability=args.approval_applicability,evidence=args.role_evidence,conditions=args.role_condition)
            evidence=roles.verify_roles(old,current,None,lambda c,p:blob(args,c,p),lambda p:working(args,p),inspection,original.get(approval_key,''))
            a['evidence'] += evidence
            if evidence:a['conditions'] += args.role_condition
        # Earlier specification approval may precede the exact admitted accepted input.
        # Validate that relation separately; its current accepted bytes were just checked.
        if historical:
            pair=historical['id']+'@'+historical['checkpoint']['commit']+'..'+refs['accepted_spec']['commit']
            inspection=dict(pair=pair if pair in args.inspected_role_pair else None,
                            applicability=args.approval_applicability,evidence=args.role_evidence,conditions=args.role_condition)
            evidence=roles.verify_roles(historical['checkpoint'],refs['accepted_spec'],None,
                                       lambda c,p:blob(args,c,p),lambda p:working(args,p),inspection,historical['id'])
            a['evidence'] += evidence
            if evidence:a['conditions'] += args.role_condition
    if stage=='plan':
        if body['outcome']=='awaiting_plan_review':
            names=[Path(x['path']).name for x in r['plan_candidate']['artifacts']]
            require('plan.md' in names and 'tasks.md' in names and any('analysis' in x for x in names)
                    and body['classification']=='routine' and not body['questions'], 'incomplete_plan_output')
        else: require(body['classification']=='material', 'material_planning_return_required')
    if body['outcome']=='needs_clarification': require(bool(body['questions']), 'missing_clarification_questions')
    if stage=='review-plan':
        review=body['review'];grant=original.get('quality_admission')
        scope=c.get('review_authority',{})
        require(v.get('quality_contract') == 1 and scope.get('kind') == 'quality-sequence'
                and scope.get('state') == 'active' and isinstance(grant,dict)
                and grant.get('publication') == scope.get('publication_operation')
                and grant.get('sequence_sha256') == scope.get('sequence_sha256')
                and grant.get('candidate') == refs.get('plan_candidate'), 'quality_scope_changed')
        require(isinstance(grant,dict) and grant.get('reviewer_owner')==args.owner and grant.get('reviewer_session')==args.session,
                'missing_original_quality_scope')
        require(isinstance(review,dict) and set(review)<=set(['actor','provenance','decision','outcome','approach','conditions','requests'])
                and all(isinstance(review.get(k),str) and review[k].strip() for k in ['actor','provenance','decision','outcome','approach'])
                and review['actor']==args.owner and text_list(review.get('conditions')) and text_list(review.get('requests',[])), 'invalid_review_output')
        expect={'plan_review_passed':'pass','plan_revision_required':'revision-required','specification_change_required':'specification-change-required'}
        require(review['decision']==expect[body['outcome']], 'review_outcome_mismatch')
        require((body['outcome']=='plan_review_passed' and not review.get('requests') and not body['questions'] and body['classification']=='routine')
                or (body['outcome']=='plan_revision_required' and review.get('requests') and not body['questions'] and body['classification']=='routine')
                or (body['outcome']=='specification_change_required' and review.get('requests') and body['questions'] and body['classification']=='material'), 'invalid_review_disposition')
        r['review']=review
    if stage=='deliver' and body['outcome']=='review_required':
        require(body['classification']=='material' and body['review_needed'] in ['spec','plan']
                and (body['review_needed']=='spec' or not body['questions']), 'invalid_delivery_return')
        r['review_needed']=body['review_needed']
    if stage=='deliver' and body['outcome']=='awaiting_result_review':
        require(body['classification']=='routine' and not body['questions'], 'invalid_delivery_disposition')
    return r, v


def completion(value, args, request, reason):
    """Observe the exact canonical terminal; this grants no retry or new authority."""
    require(isinstance(value,dict) and type(value.get('contract_version')) is int
            and value['contract_version']==9 and value.get('feature')==args.feature, reason)
    context, handoff = value.get('context'), value.get('handoff')
    require(isinstance(context,dict) and type(context.get('revision')) is int
            and context['revision']==args.revision+1 and isinstance(handoff,dict), reason)
    identity=handoff.get('id')
    require(isinstance(identity,str) and identity.startswith('handoff/') and identity[len('handoff/'):].strip()
            and context.get('latest_handoff')==identity and handoff.get('run_id')==args.run
            and type(handoff.get('epoch')) is int and handoff['epoch']==args.epoch
            and handoff.get('outcome')==request['outcome']
            and value.get('current_run') is None and value.get('current_claim') is None, reason)
    require(handoff.get('accepted_spec')==request['checkpoint'], reason)
    for key in ['plan_candidate','review_evidence','delivery_result']:
        if key in request:
            require(handoff.get(key)==request[key], reason)
    if 'review' in request:
        require(handoff.get('quality_review') == request['review'] and not value.get('plan_approval'), reason)
        if request['outcome'] == 'plan_review_passed':
            require(value.get('plan_state') == 'awaiting_plan_approval', reason)
    return handoff


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['diagram','store','workspace','feature','operation','run','owner','session','repository','worktree','output-file']:
        p.add_argument('--'+key,required=True)
    p.add_argument('--authorization-file');p.add_argument('--authorization-sha256')
    p.add_argument('--revision',type=int,required=True);p.add_argument('--epoch',type=int,required=True)
    p.add_argument('--inspected-role-pair',action='append',default=[]);p.add_argument('--approval-applicability',choices=['unchanged','material','unknown'])
    p.add_argument('--role-evidence',action='append',default=[]);p.add_argument('--role-condition',action='append',default=[])
    args=p.parse_args(argv);phase='preparation'
    try:
        require(all(Path(x).is_absolute() for x in [args.diagram,args.store,args.workspace,args.output_file]), 'absolute_paths_required')
        request,before=prepare(args)
        if request is None:
            result=dict(status='historical',reason='inspect_existing_operation_and_current_authority',effects='no terminal attempted');code=2
        else:
            request['assessment']['evidence']+=_transport.verified_authorization(args,['native_handoff'])
            with tempfile.TemporaryDirectory(prefix='diagram-handoff-') as tmp:
                path=Path(tmp)/'request.json'
                with path.open('x') as out:
                    os.chmod(path,0o600);json.dump(request,out)
                current=native(args,['feature','show','--feature',args.feature])
                require(current.get('context',{}).get('revision')==args.revision and current.get('current_run')==before['current_run']
                        and current.get('queue_revision')==before['queue_revision'] and current.get('dependencies')==before['dependencies'], 'native_state_changed_during_preparation')
                require(git(args,'rev-parse','HEAD').decode().strip()==request['expected_head']
                        and git(args,'symbolic-ref','HEAD').decode().strip()==before['current_run']['branch']
                        and not git(args,'status','--porcelain'),'workspace_changed_during_preparation')
                _transport.verified_authorization(args,['native_handoff'])
                phase='submission'
                value=native(args,['feature','handoff','apply','--feature',args.feature,'--operation',args.operation,'--request-file',str(path)])
                returned=completion(value,args,request,'invalid_terminal_response')
                observed=native(args,['feature','show','--feature',args.feature])
                current=completion(observed,args,request,'terminal_readback_mismatch')
                require(current==returned, 'terminal_readback_mismatch')
                result=dict(status='success',reason='ordinary_handoff_recorded',effects='native handoff and released ownership verified',handoff=value['handoff'].get('id'));code=0
    except (Failure, roles.RoleError) as e:
        reason=e.reason if isinstance(e,Failure) else str(e)
        status=e.status if isinstance(e,Failure) else 'refused'
        if phase=='submission' and reason in ['invalid_terminal_response','terminal_readback_mismatch','invalid_native_response','native_process_failed']:
            status='uncertain'
        elif phase=='preparation' and status=='uncertain':status='failed'
        result=dict(status=status,reason=reason,effects='no terminal attempted' if phase=='preparation' else 'inspect operation/current authority; no retry');code=1
    except (OSError,ValueError,KeyError,TypeError,UnicodeError):
        result=dict(status='failed' if phase=='preparation' else 'uncertain',reason='preparation_or_transport_failed',effects='no terminal attempted' if phase=='preparation' else 'inspect operation/current authority; no retry');code=1
    print(json.dumps(dict(phase=phase,action='prepare ordinary handoff',target=args.feature,operation=args.operation,**result)))
    return code

if __name__=='__main__':raise SystemExit(main())

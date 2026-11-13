#!/usr/bin/env python3
"""Consumer-owned published-review preparation; native acquire remains authoritative."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
import selectors
import subprocess
import tempfile
import time
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import checkpoint_roles as roles
except ImportError:
    print(json.dumps(dict(phase="preparation", status="failed", reason="incomplete_client_package", effects="no native calls")))
    raise SystemExit(1) from None


class Failure(Exception):
    def __init__(self, reason, status='refused'):
        self.reason, self.status = reason, status


def require(ok, reason):
    if not ok:
        raise Failure(reason)


def run(argv, cwd, timeout=30):
    """Fixed argv, bounded capture/time; no shell or retry. Caller knows mutation phase."""
    require(0 < timeout <= 30, 'process_timeout')
    with subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        with selectors.DefaultSelector() as sel:
            sel.register(proc.stdout, selectors.EVENT_READ, 0)
            sel.register(proc.stderr, selectors.EVENT_READ, 1)
            output = [bytearray(), bytearray()]
            deadline = time.monotonic() + timeout
            while sel.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    proc.kill()
                    raise Failure('process_timeout', 'uncertain')
                for key, _ in sel.select(remaining):
                    data = os.read(key.fd, 65536)
                    if not data:
                        sel.unregister(key.fileobj)
                    else:
                        output[key.data].extend(data)
                        if len(output[key.data]) > 1024 * 1024:
                            proc.kill()
                            raise Failure('output_limit', 'uncertain')
            return proc.wait(), bytes(output[0]), bytes(output[1])


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
        raise Failure(reason, 'uncertain' if reason == 'outcome_ambiguous' else ('denied' if 'denied' in reason else 'refused'))
    if code != 0:
        raise Failure('native_process_failed', 'uncertain')
    return value


def git(args, *command):
    code, out, _ = run(['git', *command], args.workspace)
    require(code == 0, 'git_verification_failed')
    return out


def read_blob(args, commit, name):
    entry = git(args, 'ls-tree', '-z', commit, '--', name).split(b'\0')
    require(len(entry) == 2 and entry[-1] == b'' and b'\t' in entry[0], 'invalid_artifact_type')
    metadata, path = entry[0].split(b'\t', 1)
    require(metadata.split()[0] in [b'100644', b'100755'] and path.decode() == name, 'invalid_artifact_type')
    return git(args, 'show', commit + ':' + name)


def read_working(args, name):
    path = Path(args.workspace) / name
    require(path.resolve().is_relative_to(Path(args.workspace).resolve())
            and path.is_file() and not path.is_symlink(), 'artifact_path_escape_or_missing')
    return path.read_bytes()


def checkpoint(args, cp, working=False):
    try:
        return roles.verify_checkpoint(cp, lambda c,p: read_blob(args,c,p),
                                       (lambda p: read_working(args,p)) if working else None)
    except roles.RoleError as e:
        raise Failure(str(e)) from None


def role_inspection(args):
    return dict(pair=args.inspected_role_pair, applicability=args.approval_applicability,
                evidence=args.role_evidence, conditions=args.role_condition)


def sequence_digest(sequence):
    # Fixed native QualitySequence/Checkpoint/Artifact/Review field order.
    keys = ['feature', 'spec_approval_id', 'accepted_spec', 'initial_handoff', 'authorization']
    auth_keys = ['actor', 'provenance', 'decision', 'outcome', 'approach', 'conditions']
    require(set(sequence) == set(keys) and set(sequence['authorization']) == set(auth_keys), 'invalid_quality_scope_shape')
    cp = sequence['accepted_spec']
    require(set(cp) == {'commit', 'artifacts'} and isinstance(cp['artifacts'], list), 'invalid_quality_scope_spec')
    for art in cp['artifacts']:
        require(set(art) == {'path', 'sha256'}, 'invalid_quality_scope_spec')
    canonical = {k: sequence[k] for k in keys}
    canonical['accepted_spec'] = dict(commit=cp['commit'], artifacts=[dict(path=a['path'], sha256=a['sha256']) for a in cp['artifacts']])
    canonical['authorization'] = {k: sequence['authorization'][k] for k in auth_keys}
    encoded = json.dumps(canonical, ensure_ascii=False, separators=(',', ':'))
    for literal, escaped in [('<', r'\u003c'), ('>', r'\u003e'), ('&', r'\u0026'), ('\u2028', r'\u2028'), ('\u2029', r'\u2029')]:
        encoded = encoded.replace(literal, escaped)
    return hashlib.sha256(encoded.encode()).hexdigest()


def prepare(args):
    prior = native(args, ['feature', 'operation', 'show', '--feature', args.feature,
                          '--operation', args.operation])
    require(prior.get('contract_version') == 9 and prior.get('operation_id') == args.operation,
            'invalid_operation_response')
    if prior.get('outcome') != 'absent':
        # Historical success is not current ownership. No reconstruction or body replay.
        return None
    version = native(args, ['database', 'version'])
    require(version.get('contract_version') == 2 and version.get('database_version') == 32
            and version.get('supported') is True, 'unsupported_database')
    v = native(args, ['feature', 'review-authority', 'show', '--feature', args.feature])
    require(v.get('contract_version') == 9 and v.get('feature') == args.feature, 'invalid_feature_response')
    require(type(v.get('review_preparation_contract')) is int and v['review_preparation_contract'] == 2 and v.get('quality_contract') == 1,
            'unsupported_review_preparation')
    c = v.get('context')
    require(isinstance(c, dict) and 'current_run' not in c and 'current_claim' not in c,
            'invalid_context_shape')
    # Optional empty owner properties are omitted by the native contract; nested contexts are not.
    require('context' not in c and not v.get('current_run') and not v.get('current_claim'), 'ownership_conflict')
    require(type(c.get('revision')) is int and c.get('revision') == args.revision and c.get('latest_handoff') == args.handoff,
            'stale_selection')
    require(v.get('plan_state') == 'awaiting_plan_review' and v.get('review_authority_applicable') is True,
            'review_not_applicable')
    a = c.get('review_authority')
    require(isinstance(a, dict) and a.get('contract_version') == 2 and a.get('kind') == 'quality-sequence'
            and a.get('state') == 'active' and not a.get('grant') and not a.get('consumed_run_id')
            and a.get('publication_operation') == args.publication and a.get('sequence_sha256') == args.digest,
            'publication_mismatch')
    g = a.get('sequence')
    require(isinstance(g, dict) and g.get('feature') == args.feature
            and g.get('spec_approval_id') == c.get('applicable_approval'), 'quality_scope_mismatch')
    auth = g.get('authorization')
    require(isinstance(auth, dict) and auth.get('decision') == 'authorize-plan-quality'
            and all(isinstance(auth.get(k), str) and auth[k].strip() for k in ['actor', 'provenance', 'outcome', 'approach'])
            and isinstance(auth.get('conditions'), list) and auth['conditions']
            and all(isinstance(x, str) and x.strip() for x in auth['conditions']), 'invalid_quality_scope')
    require(sequence_digest(g) == args.digest, 'sequence_digest_mismatch')
    require(all(s.strip() for s in [args.rationale, *args.evidence, *args.condition]), 'missing_assessment')
    require(args.evidence and args.condition, 'missing_assessment')
    root = Path(git(args, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
    require(isinstance(c.get('workspace'), str) and args.workspace == c['workspace']
            and root == Path(args.workspace).resolve(), 'workspace_mismatch')
    common = Path(git(args, 'rev-parse', '--git-common-dir').decode().strip())
    if not common.is_absolute():
        common = root / common
    instance = 'instance/' + hashlib.sha256(os.fsencode(str(common.resolve()))).hexdigest()
    require(instance == c.get('instance_id'), 'instance_mismatch')
    for key, expected in [('repository_id', args.repository), ('worktree_key', args.worktree)]:
        pattern = r'repository/(?:[0-9a-f]{32}|[0-9a-f]{64})' if key == 'repository_id' else r'worktree/[0-9a-f]{32}'
        require(expected == c.get(key) and re.fullmatch(pattern, expected), 'identity_mismatch')
    require(git(args, 'symbolic-ref', 'HEAD').decode().strip() == c.get('branch'), 'branch_mismatch')
    head = git(args, 'rev-parse', 'HEAD').decode().strip()
    require(not git(args, 'status', '--porcelain'), 'unclean_workspace')
    advancement = []
    if head != args.candidate:
        require(args.inspected_head == head and args.advancement_evidence
                and all(s.strip() for s in args.advancement_evidence), 'advancement_inspection_required')
        code, _, _ = run(['git', 'merge-base', '--is-ancestor', args.candidate, head], args.workspace)
        require(code == 0, 'workspace_not_descendant' if code == 1 else 'git_verification_failed')
        # Caller judges the actual diff's scope/authority implications. Retain the immutable
        # inspected pair and exact diff digest, not a filename-based semantic classifier.
        diff = git(args, 'diff', '--no-ext-diff', '--no-textconv', '--binary', args.candidate, head)
        advancement = [f'Consumer inspected advancement {args.candidate} -> {head}; '
                       f'diff SHA256 {hashlib.sha256(diff).hexdigest()}', *args.advancement_evidence]
    elif args.inspected_head or args.advancement_evidence:
        require(args.inspected_head == head and all(s.strip() for s in args.advancement_evidence),
                'advancement_inspection_mismatch')
    handoff = v.get('handoff')
    require(isinstance(handoff, dict) and handoff.get('id') == args.handoff, 'invalid_handoff')
    proposal = handoff.get('plan_candidate')
    require(isinstance(proposal, dict) and proposal.get('commit') == args.candidate, 'candidate_mismatch')
    approval = v.get('historical_approval')
    require(isinstance(approval, dict) and approval.get('id') == c.get('applicable_approval')
            and isinstance(approval.get('review'), dict) and approval.get('checkpoint') == g['accepted_spec'], 'missing_spec_approval')
    try:
        role_evidence = roles.verify_roles(approval.get('checkpoint'), handoff.get('accepted_spec'), proposal,
                                           lambda c,p: read_blob(args,c,p), lambda p: read_working(args,p),
                                           role_inspection(args), approval['id'])
    except roles.RoleError as e:
        raise Failure(str(e)) from None
    require(type(v.get('queue_revision')) is int and isinstance(v.get('dependencies'), list), 'missing_queue_facts')
    require(v['queue_revision'] == args.queue_revision and v['dependencies'] == json.loads(args.dependencies), 'stale_queue_selection')
    return dict(contract_version=9, expected_revision=args.revision,
                expected_queue_revision=v['queue_revision'], dependencies=v['dependencies'],
                owner=args.owner, session=args.session, pinned_handoff=args.handoff,
                approval_id=approval['id'], segment='review-plan', purpose='plan-review',
                quality_admission=dict(publication=args.publication, sequence_sha256=args.digest,
                    expected_revision=args.revision, pinned_handoff=args.handoff, candidate=proposal,
                    reviewer_owner=args.owner, reviewer_session=args.session),
                transition='plan-quality-review', discovery_selected=args.discovery_selected,
                workspace=args.workspace, branch=c['branch'], expected_head=head, workspace_clean=True,
                repository_id=args.repository, instance_id=instance, worktree_key=args.worktree,
                assessment=dict(actor=args.owner, approval_id=approval['id'], rationale=args.rationale,
                                evidence=[*args.evidence, *advancement, *role_evidence],
                                conditions=[*args.condition, *(args.role_condition if role_evidence else [])]))


def verified_authorization(args, effects, segment=None, purpose=None, candidate=None):
    source=getattr(args,'authorization_file',None);digest=getattr(args,'authorization_sha256',None)
    require((source is None)==(digest is None),'verified_source_and_digest_required')
    if source is None:return []
    require(bool(source) and isinstance(digest,str) and re.fullmatch('[0-9a-f]{64}',digest),'verified_source_and_digest_required')
    import importlib.util
    sys.dont_write_bytecode=True
    spec=importlib.util.spec_from_file_location('action_authorization',Path(__file__).with_name('prepare-authorization.py'))
    try:
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        observed=module.check_action(args,effects,segment,purpose,candidate)
    except (OSError,ImportError,ValueError):raise Failure('unsupported_consumer_capability') from None
    except Exception as e:
        # Only bounded codes cross this boundary; no raw source/native payload.
        if e.__class__.__name__=='Refusal':raise Failure('authorization:'+str(e)) from None
        raise Failure('authorization_preflight_failed') from None
    return ['Consumer authorization source SHA256 '+observed['source_sha256']+'; policy/current selection mechanically checked; semantic scope remains consumer_reported; CLI host approval import unsupported.']


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['diagram', 'store', 'workspace', 'feature', 'operation', 'handoff', 'candidate',
                 'publication', 'digest', 'dependencies', 'owner', 'session', 'repository', 'worktree', 'rationale']:
        p.add_argument('--' + name, required=True)
    p.add_argument('--authorization-file');p.add_argument('--authorization-sha256')
    p.add_argument('--revision', required=True, type=int)
    p.add_argument('--queue-revision', required=True, type=int)
    p.add_argument('--evidence', required=True, action='append')
    p.add_argument('--condition', required=True, action='append')
    p.add_argument('--discovery-selected', action='store_true')
    p.add_argument('--inspected-role-pair')
    p.add_argument('--approval-applicability', choices=['unchanged', 'material', 'unknown'])
    p.add_argument('--role-evidence', action='append', default=[])
    p.add_argument('--role-condition', action='append', default=[])
    p.add_argument('--inspected-head', help='actual full HEAD explicitly inspected for unchanged-input advancement')
    p.add_argument('--advancement-evidence', action='append', default=[],
                   help='actual intervening-diff inspection and continuing authority applicability; repeatable')
    args = p.parse_args(argv)
    phase = 'preparation'
    try:
        require(Path(args.diagram).is_absolute() and Path(args.store).is_absolute()
                and Path(args.workspace).is_absolute(), 'absolute_paths_required')
        request = prepare(args)
        if request is None:
            result = dict(status='historical', reason='inspect_existing_operation_and_current_authority',
                          effects='no acquisition attempted; no review body authorized')
            code = 2
        else:
            request['assessment']['evidence']+=verified_authorization(args,['native_admission','independent_review'],'review-plan','plan-review',args.candidate)
            # Serialization and private file creation complete before phase switches or any acquisition call.
            with tempfile.TemporaryDirectory(prefix='diagram-review-') as tmp:
                path = Path(tmp) / 'request.json'
                with path.open('x', encoding='utf-8') as out:
                    os.chmod(path, 0o600)
                    json.dump(request, out)
                require(git(args, 'rev-parse', 'HEAD').decode().strip() == request['expected_head']
                        and git(args, 'symbolic-ref', 'HEAD').decode().strip() == request['branch']
                        and not git(args, 'status', '--porcelain'), 'workspace_changed_during_preparation')
                verified_authorization(args,['native_admission','independent_review'],'review-plan','plan-review',args.candidate)
                phase = 'admission'
                acquired = native(args, ['feature', 'run', 'acquire', '--feature', args.feature,
                                         '--operation', args.operation, '--request-file', str(path)])
                if acquired.get('review_admission_replayed') is True:
                    print(json.dumps(dict(phase=phase, action='acquire published plan review', target=args.feature,
                                          operation=args.operation, status='historical',
                                          reason='native_exact_replay', effects='no new review body authorized')))
                    return 2
                require(acquired.get('review_admission_replayed') is False, 'invalid_admission_response')
                current = acquired.get('current_run')
                require(isinstance(current, dict) and current.get('owner') == args.owner
                        and current.get('session') == args.session and current.get('segment') == 'review-plan'
                        and current.get('input_handoff') == args.handoff
                        and current.get('original_input',{}).get('quality_admission') == request['quality_admission'], 'invalid_admission_response')
                result = dict(status='success', run_id=current['id'], epoch=current['epoch'],
                              effects='native run acquired; verify current context before semantic review')
                code = 0
    except Failure as e:
        status = 'uncertain' if phase == 'admission' and e.reason == 'invalid_admission_response' else e.status
        if phase == 'preparation' and status == 'uncertain':
            status = 'failed'  # All preparation subprocesses are reads; no acquire has been attempted.
        result = dict(status=status, reason=e.reason,
                      effects='no acquisition attempted' if phase == 'preparation' else 'inspect operation/current authority before dependent work')
        code = 1
    except (OSError, ValueError, KeyError, TypeError, UnicodeError):
        result = dict(status='failed' if phase == 'preparation' else 'uncertain', reason='preparation_or_transport_failed',
                      effects='no acquisition attempted' if phase == 'preparation' else 'inspect operation/current authority')
        code = 1
    print(json.dumps(dict(phase=phase, action='prepare/acquire published plan review',
                          target=args.feature, operation=args.operation, **result)))
    return code


if __name__ == '__main__':
    raise SystemExit(main())

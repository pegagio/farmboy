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


class Failure(Exception):
    def __init__(self, reason, status='refused'):
        self.reason, self.status = reason, status


def require(ok, reason):
    if not ok:
        raise Failure(reason)


def run(argv, cwd):
    """Fixed argv, bounded capture/time; no shell or retry. Caller knows mutation phase."""
    with subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        with selectors.DefaultSelector() as sel:
            sel.register(proc.stdout, selectors.EVENT_READ, 0)
            sel.register(proc.stderr, selectors.EVENT_READ, 1)
            output = [bytearray(), bytearray()]
            deadline = time.monotonic() + 30
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


def checkpoint(args, cp, working=False):
    require(isinstance(cp, dict) and isinstance(cp.get('commit'), str)
            and re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', cp['commit'])
            and isinstance(cp.get('artifacts'), list) and cp['artifacts'], 'invalid_checkpoint')
    for artifact in cp['artifacts']:
        require(isinstance(artifact, dict), 'invalid_artifact')
        name = artifact.get('path')
        require(isinstance(name, str) and name and not PurePosixPath(name).is_absolute()
                and '..' not in PurePosixPath(name).parts and str(PurePosixPath(name)) == name
                and '\\' not in name and '\x00' not in name, 'invalid_artifact_path')
        blob = git(args, 'show', cp['commit'] + ':' + name)
        require(hashlib.sha256(blob).hexdigest() == artifact.get('sha256'), 'artifact_mismatch')
        if working:
            path = Path(args.workspace) / name
            require(path.resolve().is_relative_to(Path(args.workspace).resolve()), 'artifact_path_escape')
            require(path.read_bytes() == blob, 'working_artifact_mismatch')



def grant_digest(grant):
    # Match existing native ReviewGrant.Digest's fixed struct order and Go JSON string escaping.
    # Published native responses omit all optional gate-role fields; reject any instead of normalizing authority.
    auth_keys = ['actor', 'provenance', 'decision', 'outcome', 'approach', 'conditions']
    grant_keys = ['feature', 'pinned_handoff', 'expected_revision', 'reviewer_owner', 'reviewer_session', 'authorization']
    require(set(grant) == set(grant_keys) and set(grant['authorization']) == set(auth_keys), 'invalid_grant_shape')
    canonical = {k: grant[k] for k in grant_keys}
    canonical['authorization'] = {k: grant['authorization'][k] for k in auth_keys}
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
    require(version.get('contract_version') == 2 and version.get('database_version') == 28
            and version.get('supported') is True, 'unsupported_database')
    v = native(args, ['feature', 'review-authority', 'show', '--feature', args.feature])
    require(v.get('contract_version') == 9 and v.get('feature') == args.feature, 'invalid_feature_response')
    require(type(v.get('review_preparation_contract')) is int and v['review_preparation_contract'] == 1,
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
    require(isinstance(a, dict) and type(a.get('contract_version')) is int and a.get('contract_version') == 1 and a.get('state') == 'published'
            and not a.get('consumed_run_id') and a.get('publication_operation') == args.publication
            and a.get('grant_sha256') == args.digest, 'publication_mismatch')
    g = a.get('grant')
    require(isinstance(g, dict) and g.get('feature') == args.feature
            and type(g.get('expected_revision')) is int and g.get('expected_revision') == args.revision and g.get('pinned_handoff') == args.handoff
            and g.get('reviewer_owner') == args.owner and g.get('reviewer_session') == args.session,
            'grant_mismatch')
    auth = g.get('authorization')
    require(isinstance(auth, dict) and auth.get('decision') == 'delegate-plan-review'
            and all(isinstance(auth.get(k), str) and auth[k].strip() for k in
                    ['actor', 'provenance', 'outcome', 'approach'])
            and isinstance(auth.get('conditions'), list) and auth['conditions']
            and all(isinstance(s, str) and s.strip() for s in auth['conditions'])
            and not any(auth.get(k) for k in ['requests', 'integration_permission', 'instruction_change',
                                            'authorization_sha256', 'specification_advancement']), 'invalid_grant')
    require(grant_digest(g) == args.digest, 'grant_digest_mismatch')
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
    checkpoint(args, proposal, True)
    checkpoint(args, handoff.get('accepted_spec'), True)
    approval = v.get('historical_approval')
    require(isinstance(approval, dict) and approval.get('id') == c.get('applicable_approval')
            and isinstance(approval.get('review'), dict), 'missing_spec_approval')
    checkpoint(args, approval.get('checkpoint'), True)
    require(type(v.get('queue_revision')) is int and isinstance(v.get('dependencies'), list), 'missing_queue_facts')
    require(v['queue_revision'] == args.queue_revision and v['dependencies'] == json.loads(args.dependencies), 'stale_queue_selection')
    return dict(contract_version=9, expected_revision=args.revision,
                expected_queue_revision=v['queue_revision'], dependencies=v['dependencies'],
                owner=args.owner, session=args.session, pinned_handoff=args.handoff,
                approval_id=approval['id'], segment='review-plan', purpose='plan-review',
                review_grant=g, discovery_selected=args.discovery_selected,
                workspace=args.workspace, branch=c['branch'], expected_head=head, workspace_clean=True,
                repository_id=args.repository, instance_id=instance, worktree_key=args.worktree,
                assessment=dict(actor=args.owner, approval_id=approval['id'], rationale=args.rationale,
                                evidence=[*args.evidence, *advancement], conditions=args.condition))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['diagram', 'store', 'workspace', 'feature', 'operation', 'handoff', 'candidate',
                 'publication', 'digest', 'dependencies', 'owner', 'session', 'repository', 'worktree', 'rationale']:
        p.add_argument('--' + name, required=True)
    p.add_argument('--revision', required=True, type=int)
    p.add_argument('--queue-revision', required=True, type=int)
    p.add_argument('--evidence', required=True, action='append')
    p.add_argument('--condition', required=True, action='append')
    p.add_argument('--discovery-selected', action='store_true')
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
            # Serialization and private file creation complete before phase switches or any acquisition call.
            with tempfile.TemporaryDirectory(prefix='diagram-review-') as tmp:
                path = Path(tmp) / 'request.json'
                with path.open('x', encoding='utf-8') as out:
                    os.chmod(path, 0o600)
                    json.dump(request, out)
                require(git(args, 'rev-parse', 'HEAD').decode().strip() == request['expected_head']
                        and git(args, 'symbolic-ref', 'HEAD').decode().strip() == request['branch']
                        and not git(args, 'status', '--porcelain'), 'workspace_changed_during_preparation')
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
                        and current.get('input_handoff') == args.handoff, 'invalid_admission_response')
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

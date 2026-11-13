"""Pure checkpoint role policy; callers supply bounded repository observations."""
import hashlib
import re
from pathlib import PurePosixPath


class RoleError(Exception):
    pass


def check(ok, reason):
    if not ok:
        raise RoleError(reason)


def members(artifacts):
    check(isinstance(artifacts, list) and bool(artifacts), 'invalid_artifacts')
    seen = set()
    for a in artifacts:
        check(isinstance(a, dict) and set(a) == {'path', 'sha256'}, 'invalid_artifact')
        p, digest = a['path'], a['sha256']
        check(isinstance(p, str) and p and not PurePosixPath(p).is_absolute()
              and '..' not in PurePosixPath(p).parts and str(PurePosixPath(p)) == p
              and '\\' not in p and '\x00' not in p, 'invalid_artifact_path')
        check(p not in seen, 'duplicate_artifact')
        check(isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest), 'invalid_artifact_digest')
        seen.add(p)
    return artifacts


def verify_checkpoint(cp, read_blob, read_working=None):
    check(isinstance(cp, dict) and set(cp) == {'commit', 'artifacts'}
          and isinstance(cp['commit'], str) and re.fullmatch('(?:[0-9a-f]{40}|[0-9a-f]{64})', cp['commit']),
          'invalid_checkpoint')
    observed = {}
    for a in members(cp['artifacts']):
        try:
            blob = read_blob(cp['commit'], a['path'])
            check(isinstance(blob, bytes) and hashlib.sha256(blob).hexdigest() == a['sha256'],
                  'artifact_mismatch')
            if read_working is not None:
                check(read_working(a['path']) == blob, 'working_artifact_mismatch')
        except (OSError, KeyError):
            raise RoleError('missing_artifact') from None
        observed[a['path']] = blob
    return observed


def verify_roles(historical, current, proposal, read_blob, read_working, inspection=None, approval_id=''):
    def verify_named(name, cp, working=None):
        try:
            return verify_checkpoint(cp, read_blob, working)
        except RoleError as e:
            raise RoleError(name + ':' + str(e)) from None
    old = verify_named('historical', historical)
    accepted = verify_named('current', current, read_working)
    if proposal is not None:
        verify_named('proposal', proposal, read_working)
    differences = []
    for p, blob in old.items():
        try:
            actual = read_working(p)
        except (OSError, KeyError):
            raise RoleError('missing_historical_working_artifact') from None
        if actual != blob:
            check(p in accepted and accepted[p] == actual, 'uncovered_historical_working_mismatch')
            differences.append((p, blob, actual))
    if not differences:
        return []
    pair = approval_id + '@' + historical['commit'] + '..' + current['commit']
    check(isinstance(inspection, dict) and inspection.get('pair') == pair,
          'role_inspection_required')
    check(inspection.get('applicability') == 'unchanged', 'affected_approval_review_required')
    for key in ['evidence', 'conditions']:
        check(isinstance(inspection.get(key), list) and inspection[key]
              and all(isinstance(x, str) and x.strip() for x in inspection[key]), 'role_inspection_required')
    evidence = []
    for path, before, after in differences:
        # Length-delimited bytes prevent ambiguity; this identifies the exact pair, not its meaning.
        digest = hashlib.sha256(len(before).to_bytes(8, 'big') + before + after).hexdigest()
        evidence.append(f'Consumer role inspection {pair}; path {path}; '
                        f'historical SHA256 {hashlib.sha256(before).hexdigest()}; '
                        f'current SHA256 {hashlib.sha256(after).hexdigest()}; diff SHA256 {digest}')
    return evidence + inspection['evidence']


def stage_roles(segment, purpose, outcome):
    if (segment, purpose) in [('specify', 'draft'), ('specify', 'flowback'), ('clarify', 'clarification')]:
        check(outcome in ['needs_clarification', 'awaiting_spec_review'], 'stage_outcome_mismatch')
        return ('checkpoint',)
    if (segment, purpose) == ('plan', 'planning-handoff'):
        check(outcome in ['awaiting_plan_review', 'needs_clarification', 'awaiting_spec_review'], 'stage_outcome_mismatch')
        return ('checkpoint', 'plan_candidate') if outcome == 'awaiting_plan_review' else ('checkpoint',)
    if (segment, purpose) == ('review-plan', 'plan-review'):
        check(outcome in ['plan_review_passed', 'plan_revision_required', 'specification_change_required'], 'stage_outcome_mismatch')
        return ('review_evidence',)
    if (segment, purpose) == ('deliver', 'delivery'):
        check(outcome in ['awaiting_result_review', 'review_required'], 'stage_outcome_mismatch')
        return ('delivery_result',) if outcome == 'awaiting_result_review' else ()
    raise RoleError('unsupported_ordinary_stage_use_existing_route')

"""Bounded reported authorization values. No native effects or consent authority.

All source/policy/host IO is owned by the explicit consumer. Matching/digests prove
structure and identity, never truth, unseen history or actual operator permission.
"""
import json
import re
from pathlib import PurePosixPath

CAPABILITY = 1
LIMIT = 1 << 20
EFFECTS = frozenset('prepare_workspace draft clarify plan native_admission local_commit review_grant independent_review record_review delivery native_handoff dispatcher_start dispatcher_stop dispatcher_restart credential_access external_request integration installation publication'.split())
STAGES = {'setup': ['draft'], 'specify': ['draft','flowback'], 'clarify': ['clarification'], 'plan': ['planning-handoff'], 'review-plan': ['plan-review'], 'deliver': ['delivery'], 'integrate': ['integration'], 'dispatcher': ['start','restart','stop']}

class Refusal(Exception):
    pass

def require(ok, code):
    if not ok:
        raise Refusal(code)

def shape(v, keys):
    require(isinstance(v,dict) and set(v)==set(keys.split()), 'invalid_members')

def text(v, limit=2048, empty=False):
    require(isinstance(v,str) and len(v)<=limit and '\x00' not in v and (empty or bool(v.strip())), 'invalid_text')
    return v

def texts(v, maximum=32, required=False):
    require(isinstance(v,list) and len(v)<=maximum and (not required or bool(v)), 'invalid_list')
    for x in v:text(x)

def integer(v, maximum=(1<<63)-1):
    require(type(v) is int and 0<=v<=maximum, 'invalid_integer')

def relative(v):
    text(v,1024)
    p=PurePosixPath(v)
    require(not p.is_absolute() and str(p)==v and '..' not in p.parts and '\\' not in v, 'unsafe_path')

def checkpoint(v):
    shape(v,'commit artifacts');require(isinstance(v['commit'],str) and re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})',v['commit']), 'invalid_commit')
    require(isinstance(v['artifacts'],list) and 0<len(v['artifacts'])<=16,'policy_artifact_limit')
    seen=set()
    for a in v['artifacts']:
        shape(a,'path sha256');relative(a['path']);require(a['path'] not in seen,'duplicate_artifact');seen.add(a['path'])
        require(isinstance(a['sha256'],str) and re.fullmatch('[0-9a-f]{64}',a['sha256']),'invalid_digest')

def assessment(v):
    shape(v,'actor rationale evidence conditions');text(v['actor'],256);text(v['rationale']);texts(v['evidence'],64,True);texts(v['conditions'],32,True)

def unique(pairs):
    result={}
    for k,v in pairs:
        require(k not in result,'duplicate_member');result[k]=v
    return result

def decode(raw):
    require(isinstance(raw,bytes) and len(raw)<=LIMIT,'source_limit')
    try:return json.loads(raw,object_pairs_hook=unique,parse_constant=lambda _:require(False,'nonfinite_number'))
    except (ValueError,UnicodeError):raise Refusal('invalid_json') from None

def validate(v):
    shape(v,'contract_version id project state mandate dispatcher_effect conditions evidence scopes')
    require(type(v['contract_version']) is int and v['contract_version']==CAPABILITY,'unsupported_authorization_capability')
    text(v['id'],128);require(isinstance(v['project'],str) and re.fullmatch('[A-Z][A-Z0-9]{1,9}',v['project']),'invalid_project')
    require(v['state']=='active','source_withdrawn');shape(v['mandate'],'actor provenance reference')
    text(v['mandate']['actor'],256);text(v['mandate']['provenance']);text(v['mandate']['reference'])
    require(v['dispatcher_effect'] in ['dispatcher_start','dispatcher_restart'],'invalid_dispatcher_effect')
    texts(v['conditions'],32,True);texts(v['evidence'],64,True)
    require(isinstance(v['scopes'],list) and 0<len(v['scopes'])<=64,'scope_limit');seen=set()
    for s in v['scopes']:
        shape(s,'feature segment purpose candidate effects policy assessment native budgets history')
        require(isinstance(s['segment'],str) and s['segment'] in STAGES and s['purpose'] in STAGES[s['segment']],'invalid_stage')
        if s['segment']=='dispatcher':require(s['feature']=='' and s['candidate']=='','invalid_dispatcher_scope')
        else:
            text(s['feature'],128)
            require(isinstance(s['feature'],str) and re.fullmatch(re.escape(v['project'])+r'-[1-9][0-9]*',s['feature']),'scope_project_mismatch')
            require(s['candidate']=='' or (isinstance(s['candidate'],str) and re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})',s['candidate'])),'invalid_candidate')
        key=(s['feature'],s['segment'],s['purpose'],s['candidate']);require(key not in seen,'duplicate_scope');seen.add(key)
        texts(s['effects'],len(EFFECTS),True);require(len(set(s['effects']))==len(s['effects']) and set(s['effects'])<=EFFECTS,'unknown_effect')
        shape(s['policy'],'historical current adoption');checkpoint(s['policy']['historical']);checkpoint(s['policy']['current']);assessment(s['policy']['adoption']);assessment(s['assessment'])
        shape(s['native'],'revision handoff spec_approval plan_approval idea_sha256');integer(s['native']['revision'])
        for k in ['handoff','spec_approval','plan_approval','idea_sha256']:text(s['native'][k],128,True)
        shape(s['budgets'],'external_requests credential_uses')
        for x in s['budgets'].values():integer(x)
        require(isinstance(s['history'],list) and len(s['history'])<=64,'history_limit')
        for h in s['history']:
            shape(h,'reference action target state effect_state new_permission confirmed_nonexecution')
            for k in ['reference','target']:text(h[k])
            require(isinstance(h['action'],str) and h['action'] in EFFECTS and h['state'] in ['pending','denied','uncertain','completed'],'invalid_history')
            require(h['effect_state'] in ['none','unknown','applied'] and type(h['confirmed_nonexecution']) is bool,'invalid_history')
            text(h['new_permission'],2048,True)
    return v

def select(v, feature, segment, purpose, candidate, effects):
    validate(v);require(bool(effects) and set(effects)<=EFFECTS,'unknown_effect')
    scopes=[s for s in v['scopes'] if (s['feature'],s['segment'],s['purpose'],s['candidate'])==(feature,segment,purpose,candidate)]
    require(len(scopes)==1,'scope_mismatch');s=scopes[0];require(set(effects)<=set(s['effects']),'scope_missing')
    for effect,budget in [('external_request','external_requests'),('credential_access','credential_uses')]:
        if effect in effects:require(s['budgets'][budget]>0,'external_budget_exhausted')
    for h in s['history']:
        if h['action'] not in effects:continue
        require(h['state']=='denied' and h['effect_state']=='none' and h['confirmed_nonexecution'] and bool(h['new_permission'].strip()),'denied_or_uncertain_effect')
    return s

def host_capabilities():
    return {'route':'codex_exec','parent_approval_import':'unsupported','human_response':'unsupported','approval_observations':'consumer_reported','limitations':'No authenticated host decision channel is supplied by a carrier or prompt.'}

def host_observation(state, association):
    require(state in ['pending','approved','denied','unsupported','uncertain'],'invalid_host_state')
    require(isinstance(association,dict) and set(association)<=set(['request','session','action','target']),'invalid_host_association')
    for v in association.values():text(v)
    return {'state':state,'association':association,'assurance':'consumer_reported','authorizes_action':False,'no_request_observed':not bool(association)}

def match_host_response(request, response):
    """TEST/adapter association check only. Caller cannot promote it to host consent."""
    shape(request,'request session action target');shape(response,'request session action target decision')
    require(all(isinstance(v,str) and v.strip() for v in request.values()),'invalid_host_request')
    require(all(response[k]==v for k,v in request.items()),'foreign_host_response')
    require(response['decision'] in ['accept','acceptForSession','decline','cancel'],'invalid_host_response')
    return {'decision':response['decision'],'association_matched':True,'authorizes_action':False,'assurance':'controlled_or_consumer_reported'}

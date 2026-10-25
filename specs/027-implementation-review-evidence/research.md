# Research: Consume the review before delivery

This research resolves placement and evidence use from current repository sources at approved spec checkpoint `f040dd9123cb8ae4e9b677774a39129eb33f4039`. No external repository/service research or unresolved technical choice requires product input.

## Workflow placement

**Decision**: Add assessment in `.agents/skills/farmboy-deliver-approved-plan/SKILL.md` after identity/approval resolution and before implementation, extending its existing resume/closeout instructions.

**Rationale**: That file owns the actual implementation call, setup boundary, standalone/external execution and ordinary notes. It already prohibits relabeling required gaps optional. The approved boundary leaves core `speckit-implement` unchanged.

**Alternatives considered**: A core patch broadens authority and bare-command behavior; a new wrapper duplicates routing; a guide-only reminder does not establish the required pre-effect step.

## Native evidence and semantic ownership

**Decision**: Extend optional adapter/reference instructions to trace current plan approval/handoff to existing committed `review_evidence` and `plan_candidate` references through supported inspection. Supply ordinary same-session context, without another acquisition/body invocation.

**Rationale**: The current native protocol documents these separate checkpoint roles. `docs/review-implementation-plan.md` assigns semantic judgment to Farmboy. Consumer verification still checks physical Git bytes and applicability; native acceptance alone cannot prove them.

**Alternatives considered**: New native fields/private SQL or a registry are unnecessary/out of scope. Newest-file selection loses authority. Guessing unavailable fields is unsafe; unavailable supported evidence stops precisely. No upstream source access is required by the plan.

## Findings and history

**Decision**: Interpret obligation/status separately from priority. Any current unresolved requirement/blocker stops. Optional advice means no defect or unmet obligation; priority alone cannot compel it. Resolution/supersession needs evidence applicable to current approved meaning.

**Rationale**: Approved FR-003/005 and existing delivery/review rules state this boundary. Approval text alone cannot settle contradictory findings.

**Alternatives considered**: Blocking all high-priority advice removes optionality. Assuming approval resolves everything conceals inconsistency. Per-finding machine state adds an unwanted tracker.

## Notes and standalone applicability

**Decision**: Use existing delivery notes for report/item reference, adopted/declined and reason, or none/not applicable. Reuse valid decisions on resume and reassess relevant changes while retaining history. Standalone applicability follows report-bearing approval or governing requirement only.

**Rationale**: Existing notes already retain actual decisions and historical/current distinctions. No report requirement should be invented for another consumer.

**Alternatives considered**: A fixed ledger/new template adds ceremony. Mandatory review everywhere broadens scope. Filename discovery silently creates obligations from stray reports.

## Verification

**Decision**: Extend existing `test_contract.py` and delivery/adapter recipes, then require separately evaluated actual Codex execution during later authorized delivery.

**Rationale**: Existing contracts test source boundaries without added dependencies; existing fixture practice distinguishes assertions from real behavior. Constitution III requires actual skill observation before acceptance.

**Alternatives considered**: An invented semantic classifier tests itself. Historical private native builders require external source/compiler access and must not be implicitly refreshed. Missing runtime capability is incomplete acceptance, not installation authority.

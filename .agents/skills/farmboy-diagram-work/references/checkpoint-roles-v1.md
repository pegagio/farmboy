# Checkpoint roles v1 — source client contract

This is a Diagram-owned consumer-client contract over existing Feature9/schema31 operations. It adds no native schema, table, capability, approval role, migration or scheduler. Source completion does not install or adopt a client.

## Distinct roles

Preserve original run input, historical approval, applicable accepted input, exact proposal and actual completed output separately. Verify historical blobs against their own full commit/digests. Verify current roles against their own committed/working bytes. Historical working differences require explicit current-role path coverage and attributable exact-pair inspection of actual differences and continued approval conditions. Proposal membership does not cover historical-spec drift in review preparation. No filename, ancestry, hash equality or routine label proves semantics.

`checkpoint_roles.py` is pure policy with injected repository observations. Both clients retain bounded fixed-argv transport, private request files and one consequential call at most. They never edit/commit content, acquire new authority behind the caller, issue grants, renew allowances or retry.

## Independent review preparation

Existing `prepare-plan-review.py` flags remain. Ordinary unchanged inputs use the existing invocation. For historical/current accepted-spec overlap append:

```text
--inspected-role-pair APPROVAL_ID@HISTORICAL_COMMIT..ACCEPTED_COMMIT
--approval-applicability unchanged
--role-evidence "Actual inspected difference and why protected meaning/conditions remain applicable"
--role-condition "Relevant continuing approval condition"
```

Evidence/condition flags repeat. Explicit material/unknown applicability stops for affected review. Missing/stale pair or uncovered drift refuses before acquire. The helper records both commits, path, old/current blob hashes and a deterministic length-delimited diff digest in existing Assessment evidence. It cannot authenticate natural-language assertions or prove semantic equivalence. Accountable consumer inspection and independent semantic review remain necessary. Descendant-head inspection is separate; existing candidate/publication/grant pins remain unchanged.

## Ordinary handoff preparation

Use `python3 .agents/skills/farmboy-diagram-work/scripts/prepare-handoff.py --help` for the complete maintained interface. Required selection flags are `--diagram --store --workspace --feature --operation --revision --run --epoch --owner --session --repository --worktree --output-file`. Paths are absolute; selected owner/session/run/epoch/revision must match actual current ordinary native ownership. No discovery selection, acquire or control change is performed by this terminal entry.

The bounded output JSON uses existing outcome/classification/questions/assessment fields and stage-specific artifact-only output declarations. A prepared artifact set is `{artifacts:[{path,sha256}]}`; any commit override, unknown field, duplicate JSON/member, unsafe/nonregular path or mismatched bytes refuses. Actual clean HEAD supplies new Checkpoint.commit. Assessment actor must be actual owner; rationale, evidence and conditions are substantive caller reports, never fabricated by the helper.

| Stage/outcome | Current output fields | Frozen semantic fields |
| --- | --- | --- |
| specify draft/flowback, clarify | checkpoint with spec.md, actual questions/classification | original run input/approval/lineage |
| planning success | checkpoint accepted-spec and complete plan_candidate with plan/tasks/analysis | original input and spec approval |
| planning return | checkpoint; material classification/questions as applicable | original input and approval history |
| independent plan review | review_evidence plus actual review verdict/requests/conditions | admitted accepted-spec/proposal/grant/publication |
| delivery success | delivery_result.checkpoint plus member passed-check/convergence/closeout evidence | admitted accepted-spec and approved plan |
| delivery review_required | no successful output; material classification and review_needed spec/plan | admitted accepted-spec and approved plan |

All existing native stage/outcome guards remain. The helper copies frozen review/delivery inputs from the admitted run, not caller fields. Completed tasks may differ from their original approved-plan bytes only as explicitly declared verified current output under an exact plan-approval/output inspection pair; uncovered clean input drift refuses. Historical specification/accepted-input evolution is checked separately. Producer `--inspected-role-pair` may repeat for independently inspected spec and plan pairs; evidence/conditions remain attributable and bound to each derived difference. The review entry needs only its single applicable historical/current spec pair. Material returns do not claim successful delivery or approve altered meaning.

Read existing operation first. Verify current native ownership/capabilities and clean canonical Git identity, original committed inputs, current output and applicability; recheck native revision/run/queue/dependencies and physical HEAD/branch/cleanliness immediately before the single handoff apply. Native validates its existing atomic ownership/revision/grant/revocation/state rules. Success requires released handoff readback. Existing/conflicting operation, timeout/lost/malformed response or race stops for operation/current-state inspection without retry or new pins. Git and native are not one atomic transaction; single-writer discipline and final rechecks remain explicit limits.

Integration and finalization-origin runs refuse this ordinary entry and retain their existing routes. No released semantic review recovery, finalization allowance, live budget, acceptance or deployment authority is created.

## Matched source adoption

When separately authorized, preserve consumer customizations and adopt the adapter SKILL.md, references/native-protocol.md, scripts/prepare-plan-review.py, scripts/prepare-handoff.py and scripts/checkpoint_roles.py together, plus this root `docs/architecture/contracts/checkpoint-roles-v1.md` document at its linked path. Missing adjacent files fail before native effects. Older copied helpers retain previous behavior; schema number alone does not copy client code. No external consumer is refreshed by this Feature's source tests.

Private contract fixtures, exported-copy tests and a real disposable producer→native→consumer test validate roles and effect counts independently. Full qualification evidence is in specs/057-checkpoint-role-boundaries/evidence/qualification.md. No credential, real Feature/store or installed executable is a fixture.


Independent technical result review repairs: review terminal input verification is strict for the admitted current accepted-spec and proposal, regardless of report membership or any prior plan ID. Delivery-only completion evolution remains separate. Terminal success requires a nonempty matching handoff identity, exact Feature/contract/run/epoch/outcome/revision/current-handoff facts and declared roles, followed by consistent released readback. Contradictory, partial or foreign observation is uncertain and grants no retry.

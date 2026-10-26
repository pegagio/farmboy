# Native Diagram protocol for the optional Farmboy adapter

Use existing native interfaces, not a new adapter packet/store/validator. Baseline: accepted028 closeout `8c938d7273b7e5f648ff2c9b88871f7bd88691ff`, implementation `975094763a0e8021e49c68565d9f58c239855e6e`, Feature9/schema23 is the current installed target after the explicitly authorized preserving DIAG-17 deployment from integrated Diagram a9233abfc82e328d521e3555ede073f3b6e10675; the prior DIAG-7 schema19/Feature8 target is historical. Project4/Repository2, Issue-query6/publication3, independent capture-request2/capture-result1/title1, failure1, backupreceipt2 and databaseversion2 remain separate. The cited accepted028 commits below are historical Feature6 inputs, not a current version pin. Initial enroll is removed. The caller must have an actual compatible binary and explicitly selected store/config; source availability alone proves neither. No migration, reset, legacy fallback, installer or upstream patch. No Diagram core consumer filesystem/Git access.

## Approval delegation

References to human approval permit a delegate only where current project governance and an explicit human mandate authorize that role and scope. Preserve truthful delegate/mandate attribution and all remaining checkpoints; never infer delegation or execution permission.

## Transport and current-context verification

Use the explicitly supplied binary path, existing native `--json --file STORE` and the selected existing configuration. For isolated authorized tests the existing `DIAGRAM_CONFIG` selects a private regular mode0600 YAML file (`version: 1`, `datastore: ABSOLUTE_STORE`); database parent is mode0700. Never replace a user's configuration or repurpose HOME. No automatic database creation outside explicit test/setup authority. Use help/read-only inspection to establish capability before mutations.

Each mutation sends one strict native JSON object through `--request-file FILE`, at most1MiB, with only that action's fields, `contract_version:9` for Feature operations, stable operation identity and explicit `--feature`. Serialize JSON using an existing tool/runtime rather than shell interpolation. Unknown fields, trailing objects or incompatible versions reject; do not bypass rejection. Evidence/consumer paths are data and never permission for core to fetch them. Temporary native request files are transport, not a journal. Preserve original request/operation identity in ordinary existing notes/session evidence when uncertainty requires it; do not overwrite a request then retry its old operation ID with changed facts.

Before an inner entry continues, read current `project show --key PROJECT`, `feature queue show --project PROJECT`, `feature show --feature FEATURE` using explicit store. Resolve their real envelopes rather than guessing fields. Verify selected canonical identity, current owner/session/run/epoch and original/current input/dependency/approval applicability, linked workspace/branch/checkpoint and whole outer objective against the actual invocation and local observations. A stale receipt or wrapper flag cannot pass this check. If already current, do not claim/link/acquire again. Missing or foreign context stops. All three Farmboy entry seams delegate native details to this check.

## Consumer verification and checkpoint discipline

Inspect actual Git top-level/common-dir/worktree topology, full symbolic `refs/heads/` branch, current HEAD/index/worktree, project/portable declarations and canonical native repository/instance/worktree identity under the consumer's rules. Verify declared artifact containment and actual blob/path SHA-256 at each referenced commit; detect a mismatched physical identity/HEAD or stale digest before reporting. Do not conflate an absolute locator with existence or report acceptance with verification. No guessing declaration IDs. Native recorded binding must agree with actual consumer declarations/identity. Historical spec/plan commits may differ from current result HEAD; keep correct roles.

Canonical local identity is concrete: resolve the absolute Git common directory, SHA-256 its canonical path string, and use `instance/<64 lowercase hex>` plus unadopted `repository/<same64hex>`. Resolve the actual absolute worktree root, SHA-256 its canonical path string and truncate to the first16 bytes (32 lowercase hex) for `worktree/<32hex>`; a full64hex worktree digest is invalid. An adopted portable repository uses its actual consumer-owned `repository/<32hex>` declaration/native binding instead. Verify declarations and recorded identity agree; do not guess aliases. This is existing native identity policy, not adapter-owned identity storage.

Before core helpers inspect their actual persistence convention: explicit selected identity, contained directory, standard `.specify/feature.json` and effective `SPECIFY_FEATURE_DIRECTORY` agree; the would-be literal persisted value must already equal the pointer. Prepare caller association conventionally before execution. No equivalent-alias rewrite, temporary pointer swap/restore, branch retarget or helper patch.

Disclose at explicit segment launch that necessary feature-scoped checkpoint commits use normal hooks and are authorized subject to user restrictions/safe isolation; selecting/viewing alone authorizes none. Inspect actual index/worktree before staging; reconcile feature artifacts; enumerate exact selected paths/hunks. Never `git add .`/`-A`, silently include unrelated index entries, unstage/reset/stash unrelated work, or falsify cleanliness. If unrelated index entries or inseparable shared edits prevent safe commit, preserve them and save precise required input. Even safely isolated commits do not imply the remaining workspace is clean; a clean-required native action must be true or stop. Normal rejecting hooks/commit failure stay technical blockers. Verify the resulting actual commit/tree and blobs before reporting. No merge/push or receipt-only tail commit.

## Initial claim and link

Read queue/current Feature first. A queue/offer grants nothing. Claim before feature workspace preparation using:

```text
diagram feature claim --feature FEATURE --operation OP --request-file FILE --json --file STORE
```

Exact claim object fields: `contract_version`, `expected_revision` (0 only when context absent), `expected_queue_revision`, `dependencies`, `owner`, `session`, `assessment`. Claim forbids workspace/branch/repository identity/checkpoint/expected_head/clean/run/claim/phase/decision/result fields. It captures original queued input/dependency/source/Project-binding facts and grants exclusive setup only, no current run. Assessment has actual actor, rationale and nonempty evidence; not an approval.

After current claim, externally prepare/verify the consumer workspace then:

```text
diagram feature link --feature FEATURE --operation OP --request-file FILE --json --file STORE
```

Exact link object fields: `contract_version`, `claim_id`, `epoch`, `owner`, `session`, `expected_revision`, `expected_queue_revision`, `dependencies`, `repository_id`, `instance_id`, `worktree_key`, `workspace`, `branch`, `expected_head`, `checkpoint`, optional source-less `idea_sha256`, `assessment`, `workspace_clean`. Version9; true cleanliness required. Checkpoint is the native `{commit, artifacts:[{path,sha256}]}` at the original/current queued commit; all identity fields explicit, full branch ref, actual absolute workspace. No supplied run/phase/decision/result/approval/intent fields. Copy current dependency pins exactly from native records, not invented ones.

Link verifies original/current queued checkpoint/artifact-set, dependency/evidence/source-binding and Project binding identities under current revision guards. Pure report consistency is not physical verification. Real drift requires inspected explicit release/reclaim preserving files, never silent repin. Success consumes claim and atomically admits one same-owner/session full specify/draft run with new epoch; inspect actual returned/current run. No extra initial acquire. Failure leaves claim/files intact and publishes no partial association.

## Later acquisition, human reviews and result roles

Use existing `feature run acquire` only for a later current segment with expected Feature/queue revisions, dependencies, explicit identity/workspace/full branch/HEAD/clean assessment, owner/session, current pinned_handoff, segment/purpose and applicable approval IDs. Exact existing action allowlists remain authoritative; omit unrelated zero-valued fields. Native pairs are specify/draft for initial link, specify/flowback for explicitly selected revision of an already-linked current specification when native state permits (never a new initial claim), clarify/clarification for ordinary questions, plan/planning-handoff for planning and deliver/delivery for delivery. `feature planning show` and `feature delivery show` are read-only offers, not runs.

### Conditional approval applicability

Before the first acquire, inspect the actual applicable approval and its review conditions. When that approval's review has conditions, **assessment.conditions is required**: a nonempty array of truthful applicability explanations for the exact approved artifacts and current requested phase. The top-level approval_id and assessment.approval_id both identify that verified historical specification decision, not a plan approval. An approval ID or a successful offer alone supplies neither applicability evidence nor permission.

Verify the checkpoint/artifact digests, original decision scope and actual current authorization. Explain which limits still apply and, when relevant, why a historical invocation-only restriction differs from separately authorized later work. For example, an earlier “specification only” instruction does not itself authorize planning; a later explicit planning selection can, subject to the unchanged gates. Stop affected work if applicability or permission is unresolved. Avoid blind copying of review conditions, a generic placeholder such as “conditions satisfied,” or invented permission. An approval without conditions requires no synthetic conditions entry; the ordinary assessment and identity requirements still apply. This is existing native enforcement, not a new approval or per-condition ledger.

This minimal **TEST ONLY** example assumes fixture revision4/queue1, no dependencies, the displayed spec handoff and approval, and approved specification commit consisting of forty3s with actually matching artifacts, unadopted repository/instance identity consisting of sixty-four4s and worktree identity consisting of thirty-two5s. The fixture operator separately authorized planning. These illustrative values and explanations are not verified production facts: a real caller must inspect and supply its actual current values and own assessment. Copying this example never grants authority.

<!-- planning-offer-example -->
```json
{
  "contract_version": 9,
  "expected_revision": 4,
  "expected_queue_revision": 1,
  "dependencies": [],
  "owner": "test-only-planner",
  "session": "test-only-preflight",
  "pinned_handoff": "handoff/11111111111111111111111111111111",
  "approval_id": "approval/22222222222222222222222222222222",
  "assessment": {
    "actor": "test-only-planner",
    "rationale": "TEST ONLY: verified the fixture specification and current planning authorization.",
    "evidence": [
      "TEST ONLY fixture spec checkpoint: 3333333333333333333333333333333333333333",
      "TEST ONLY whole-spec decision and separately selected planning request"
    ],
    "approval_id": "approval/22222222222222222222222222222222",
    "conditions": [
      "I compared the current fixture artifacts with the approved specification at 3333333333333333333333333333333333333333; their recorded digests agree.",
      "The prior specification-only restriction concerned the earlier invocation. The TEST ONLY operator separately selected planning now; implementation, integration and publication remain outside this request."
    ]
  },
  "expected_head": "3333333333333333333333333333333333333333",
  "repository_id": "repository/4444444444444444444444444444444444444444444444444444444444444444",
  "instance_id": "instance/4444444444444444444444444444444444444444444444444444444444444444",
  "worktree_key": "worktree/55555555555555555555555555555555",
  "workspace_clean": true
}
```

Serialize that offer to a request file using an ordinary JSON tool, then inspect:

```text
diagram feature planning show --feature TEST-1 --request-file offer.json --json --file PRIVATE_STORE
```

For a linked repository, supply its required verified identity/HEAD/cleanliness reports as shown; omitting identity rejects before conditions validation. Use only planning-offer fields: contract_version, expected_revision, expected_queue_revision, dependencies, owner, session, pinned_handoff, approval_id and assessment; expected_head/repository_id/instance_id/worktree_key/workspace_clean report actually verified physical context. Do not add acquire-only workspace, branch, segment, purpose or discovery_selected to the offer. Inspect its actual response before the first acquire. An accepted offer grants no run or ownership. Offer-input mistakes can be corrected within actual authorization before acquisition.

For the separate acquire request, retain current applicable offer facts and add actual workspace, full refs/heads/ branch, segment: plan and purpose: planning-handoff, plus verified HEAD/repository/instance/worktree/cleanliness. Set discovery_selected: true only when genuinely discovery-selected and authorized; otherwise omit it. Re-read current pins if they changed; do not fabricate current facts. Native acceptance is still required before work.

A launcher-driven definitive acquire rejection means stop immediately: no feature work and no resubmission within that invocation, even if inspection confirms an absent operation. An uncertain outcome must first be inspected through operation/current-state readback; it is never assumed authority or permission to retry. This guidance does not change the launcher's abort rule or add a recovery loop.

Ordinary clarification separately acquires before edits and retains the run between genuine questions; release at saved review. Whole-spec approval gates planning; whole-plan approval gates delivery. `feature review record` is invoked only when explicitly asked to record an actual applicable human decision. Review.actor/provenance/decision/outcome/approach/conditions identify that real decision; fixture decisions must say TEST ONLY. No check/assessment/Goal is a human decision. Result acceptance does not supply integration_permission. Material changed meaning returns to affected spec/plan review; historical approval remains historical.

Use `feature handoff apply --feature FEATURE --operation OP --request-file FILE --json --file STORE` under current run. Current v9 handoff allows expected_revision/expected_queue_revision/dependencies, run_id/epoch/owner/pinned_handoff, checkpoint/outcome/questions/classification/assessment, plan_candidate/delivery_result/review_needed/integration_result/integration_review and applicable approval_id/plan_approval_id/result_review_id, plus action-appropriate expected_head/repository_id/instance_id/worktree_key/workspace_clean. This adapter never selects integration fields/operations. Do not submit session/workspace/branch to handoff merely because they are in acquire. Use actual native required action/segment fields and errors; no new permissive validator.

| Local outcome | Native return boundary |
| --- | --- |
| Draft with material product questions | `needs_clarification`, actual checkpoint/questions and current authority; no answers invented |
| Settled draft / resolved genuine questions | `awaiting_spec_review`; explicit whole-spec approval still required |
| Complete coherent planning pass | `awaiting_plan_review`; accepted_spec/checkpoint distinct from plan_candidate containing actual plan/tasks/fresh-analysis refs, routine classification and applicability assessment |
| Verified committed delivery | `awaiting_result_review`; actual typed delivery_result and applicable spec/plan IDs, routine classification and complete actual evidence |
| Material change | Supported review-required/current spec-review outcome with affected review_needed/classification and actual refs; never pretend a successful delivery |
| Incomplete/input/technical failure | Do not invent a success outcome; save actual local work/required input/attempts/technical limitation and use supported release, inspect its outcome |

DeliveryResult has `checkpoint`, `required_checks:[{name,reported_outcome,artifact:{path,sha256}}]`, `convergence:{path,sha256}`, `closeout:{path,sha256}`. All must be actual candidate artifacts; assessment's checks_complete/closeout_clear/resources_assessed and applicable approval IDs/conditions must be true/accurate, never inferred from filenames. Only report checks actually passed. Planning must not use plan_candidate as accepted_spec. Actual native operation acceptance is separate from local skill success. Successful handoff atomically releases; inspect operation/current Feature and absent current run/claim before human waiting.

## Delivery review-evidence lookup

For a selected delivery inspect current Feature/approval/handoff facts using supported `feature show` and, for a known recorded review operation, `feature operation show --feature FEATURE --operation OP --json --file STORE`. Trace the applicable `plan_review` decision and exact approved proposal to the corresponding accepted plan-review handoff/operation's `review_evidence` and `plan_candidate` checkpoints. The report checkpoint is separate from the approved proposal and accepted specification; do not substitute latest HEAD for any role. Use current authoritative records and retained exact operation references, not a guessed operation name, newest report or private SQL. If the supported inspection cannot locate/verify the applicable evidence, stop and report that unavailable capability/reference; do not install, patch tools or invent response fields.

Before supplying context verify the current approval identity/scope, original reviewed feature/candidate, recorded report path/commit/supplied SHA-256, actual committed blob digest and relevant current applicability/resolution evidence. Current supported Feature/operation envelopes determine which references are available; an accepted record does not prove file truth. Carry the applicable report set and existing references to the generic delivery body in this same session, preserving one run/body and native recording/release ownership. Report/approval contradictions remain a Farmboy semantic assessment and precise stop, not a Diagram approval rewrite. Preserve historical reviewed checkpoints separately from current routine flow-back; changed commit alone is not a blanket re-review rule. No new native field, report format or evidence registry is introduced.

## Return review-evidence lookup

For a selected next planning/clarification segment inspect actual current `feature show` handoff, `plan_review`, `original_input.references` and known originating `feature operation show` results. Match the accepted nonapproval disposition to the reviewed proposal and report checkpoint: `plan_revision_required` carries actionable planning requests and retains applicable spec approval; `specification_change_required` carries actual product questions, Needs clarification and no current spec approval. Source contract uses existing `review_evidence`, `plan_candidate`, accepted-spec and original-input roles; use their real response envelopes. Keep report, reviewed proposal and revised current HEAD separate.

Resolve only the applicable report set and existing resolution/supersession refs. Verify committed blobs and working bytes through consumer Git inspection. If later handoffs obscure direct report references, use the exact originating accepted operation/handoff and report/candidate refs retained in ordinary feature notes, then supported operation inspection; do not scan private SQL, invent an operation, choose newest reports or build a history service. Unknown/unavailable reference or contradictory route/candidate is a precise stop with existing release/uncertainty behavior.

Before reporting a successful return, the ordinary consumer records each required finding's correction/current resolution or precise unresolved input in existing affected artifacts. Unresolved reason is incomplete, never a successful required-finding resolution. Retain origin/report/candidate references for later review/resume; no new native fields/ledger. The adapter transports these ordinary references/context once, while the executing generic body owns semantic assessment and actual product answers.

Use existing plan/planning-handoff for planning return after applicable spec approval and current pins. Use clarify/clarification for actual specification escalation, acquiring before edits and holding authority between genuine questions; save awaiting_spec_review only after real questions resolve. Human whole-spec approval remains required before later planning. Do not reacquire initial claim/link, invoke fresh preparation, auto-record retain-approved or alter schema/controls. Already-authorized state-eligible specify/flowback remains distinct. The reviewer never launches or repairs its returned workflow.

## Release, recovery, uncertainty and stale input

Use `feature run release` with explicit current authority and reason; release must not depend on renewed dependency/physical eligibility. Preparation exact fields: `contract_version`, `claim_id`, `epoch`, `owner`, `session`, `expected_revision`, `reason`. Preparation recovery exact fields: `contract_version`, `claim_id`, `epoch`, `owner`, `session`, `expected_revision`, `recovery`, `assessment`. Select exactly one claim_id or run_id. After link, preparation selector rejects; use current execution run, never consumed claim. Execution release retains expected context/queue revisions/dependencies, run_id/epoch/owner/pinned_handoff/reason; execution recovery retains the native current-input/HEAD/session/recovery/report rules.

The existing native `recovery` object has `action` (`resume` or `replace`), `inspection` (nonempty array of actual inspection references), `former_writer_stopped` (boolean), and nonblank `committed`, `dirty`, `untracked` preservation descriptions. Replacement requires actual stopped-writer confirmation before submitting true; an owner label, timeout or synthetic request is insufficient. Full-run recovery uses exactly `contract_version`, `expected_revision`, `expected_queue_revision`, `dependencies`, `run_id`, `epoch`, `owner`, `session`, `pinned_handoff`, `expected_head`, `repository_id`, `instance_id`, `worktree_key`, `assessment`, `workspace_clean`, `recovery`. It preserves the predecessor's original input, approval, segment and purpose; replacement creates a new epoch and fences the old run. Do not add workspace/branch or claim fields to that execution request. A released/completed predecessor cannot be recovered.

Native dependency pins are `{feature, revision, checkpoint, assessment_sha256}`; checkpoint is the existing commit/artifacts object. Copy current native pins, including their actual assessment digest. Existing `feature dependency add` / `assess` requests use `contract_version`, `expected_queue_revision`, `prerequisite`, `dependency_assessment`; remove omits the assessment. The assessment object is `{checkpoint, target_revision, verification, applicability}`. Verification uses actual attributable Review fields `actor`, `provenance`, `decision: verified`, `outcome`, `approach`, `conditions`; applicability uses the existing assessment actor/rationale/nonempty evidence. This records an actual inspected verification decision, never creates one by declaration. The checkpoint must equal the prerequisite's current accepted input (or queued input before a handoff), with a valid inspected revision. A changed accepted input requires fresh inspection/applicability through supported dependency assessment; refreshing a revision or copying new pins cannot silently reconcile an old claim/run. Save refusal, preservation, release and explicit reassessment before new dependent effects. Wrong field/type rejection establishes request validation only. Current request shapes follow Feature9 `model.go`, `queue.go`, `recovery.go` and CLI allowlists at clean integrated a9233ab; the accepted028 Feature6 shapes remain historical; they add no adapter schema or service.

Before replacement, actual external inspection/preservation includes committed/dirty/untracked work and explicit stopped former writer. Same-session resume and deliberate replacement use existing native recovery, original input preserved, stale authority fenced. Prelink unknown location is unknown, not proof no external files exist. No process killing, timeout takeover, deletion, search service or new recovery framework.

After lost response inspect `feature operation show --feature FEATURE --operation OP --json --file STORE`. Exact historical accepted replay does not reacquire or repeat external effects. Inspect current Feature before new writes. Conflicting reuse rejects; absent response permits only actual supported retry, unreadable/corrupt lookup remains ambiguous. Reconcile changed accepted input/binding/dependency/approval before dependent effects. Do not treat refreshed revisions as semantic independence or add a blanket upstream-integrated gate. Preserve intact pending human handoffs and actual answers.

Integration is outside this adapter. Separate actual project policy and explicit authorization govern a later external executor and destination-instruction review; Diagram owns serialization/receipts without receipt-only Git commits. No implicit push.

## Feature9 cutover compatibility boundaries

Before each new segment require the selected CLI's database version response to identify schema23 with supported:true and current native Feature responses to identify contract9. A schema16/17/18/19/20/21/22 store or Feature6/7/8 caller is incompatible: stop, never automatically migrate, retry with a guessed version or select another store. The selected basename may still be diagram-v16.db after an expressly authorized in-place migration; inspect its native schema rather than infer it from the filename.

Normal manually selected Farmboy work omits discovery_selected (or reports false). Automation controls remain OFF and do not disable manual admission. Never set discovery_selected:true to bypass permission/eligibility, enable a workflow or launch automatically. No extra launcher or discovery packet is added.

Historical operation receipts retain their recorded contract versions. Inspect the actual historical record separately from current Feature9 authority; do not rewrite it or mistake replay of an old accepted operation for current ownership. Existing released-predecessor successor data/actions do not authorize automatic recovery; use only separately requested supported recovery after actual stop/preservation verification.

Captured source-less ideas are real unqueued Features, not approval or execution authority. Capture uses the independent capture1 schema; explicit queue enrollment is separate. Existing source-backed preparation continues its usual checkpoint rules. For an explicitly queued captured idea, claim pins its immutable idea hash rather than a fabricated source checkpoint; link verifies that same idea_sha256 and the actual new request checkpoint before binding source. Read current native required fields/error contracts. Do not convert an idea into queued/spec work without explicit selection.

Packaged Spec Kit helpers select their own extension-local checksum-verified darwin-arm64 executable, not PATH. Replacing ~/.local/bin/diagram does not upgrade that bundle. Keep release/binary/checksum/helper compatibility together; stage/test a matched source bundle privately and require separately authorized documented installation before using it. No upstream patch or installed bundle refresh follows from this protocol update.


## Independent plan-review composition

This new segment requires matched Diagram Feature9/schema23 support. Pin the existing reference to Diagram source `a9233abfc82e328d521e3555ede073f3b6e10675` (`modules/diagram-cli/internal/feature/plan_review.go` and `model.go`, launcher `launcher.go`/`entry.go`). Historical schema19/Feature8 and schema20/21/22 Feature9 clients are retained only for their matching old stores/receipts; all current operational segments on schema23 use Feature9. No dual operational client mode is implied. Missing capability stops this review route; never install/migrate, guess a version, fall back to standalone or alter consumer routing as an entry effect.

The caller supplies the existing `review_grant` object: feature, pinned_handoff, expected_revision, reviewer_owner, reviewer_session and authorization. Authorization uses existing Review fields with actual human actor/provenance, decision `delegate-plan-review`, whole-plan outcome, protected-intent approach and explicit nonblank conditions. It cannot include integration permission or a different approval role. Match actual current feature/candidate/revision and labels, and inspect actual mandate, reviewer independence, holds and revocation; structural native acceptance is not authentication or semantic proof.

For actual launcher `--review-grant-file` invocation, the launcher passes that supplied object unchanged in the child prompt and uses its reviewer_owner/reviewer_session. Consume it unchanged on adapter-owned `review-plan`/`plan-review` admission; never invent/repin a grant, replace labels or infer authorization from discovery. Discovery-selected admission uses existing controls and fresh backend eligibility; a manually authorized invocation retains the normal manual path. Do not add a generic grant schema or production transport helper.

Before report writes acquire current native review authority through existing feature run acquire with actual expected revisions/dependencies, identity/workspace/HEAD/clean assessment, approved-spec ID and matching review_grant. If already current, inspect the native Project/queue/Feature, actual association and admitted owner/session/run/epoch/original-current pins/grant; reuse only an exact applicable match. Never use the author's ownership. Generic body verifies this current context through this reference but performs no native mutations.

Native role-specific assessment is required as well as the top-level approval reference: for review admission and finalization put the actual applicable historical spec decision ID from `context.applicable_approval` in both Request `approval_id` and `assessment.approval_id`. Assessment must also have actual actor, rationale and nonempty evidence; merely naming the decision in prose or only at top level is insufficient. Verify the decision and artifact applicability before reporting that ID. Do not invent a plan approval for a plan still under review. Review admission uses `contract_version:9`, expected Feature/queue revisions, copied actual dependencies, owner/session, `pinned_handoff`, `segment:review-plan`, `purpose:plan-review`, unchanged `review_grant`, actual workspace/branch/HEAD/repository/instance/worktree and true cleanliness. Handoff uses the admitted run_id/epoch/owner/input_handoff and role-correct report/spec/proposal references, not session/workspace/branch fields forbidden by that action. This details existing matched native requirements, not a new schema or relaxed gate.

The semantic body returns the ordinary fields in its [return guide](../../../../docs/review-implementation-plan.md#return-content). Read actual report bytes and compare path/SHA-256, reviewed_candidate, reviewer_mandate, findings and disposition with admitted proposal and current grant/authority. Missing, unreadable, invalid, stale or contradictory output cannot approve. Checkpoint only actual authorized report evidence, retaining admitted proposal/spec references and a separate `review_evidence` checkpoint at the report commit. No receipt-only tail commit.

Map approve → handoff `plan_approved` / Review decision `approve`, without blocking requests/questions. Map planning-return → `plan_revision_required` / `revision-required` with actionable requests. Map specification-escalation → `specification_change_required` / `specification-change-required`, material classification and actual product questions; preserve historical specification approval, never supply revised-spec approval. Use actual existing strict Request fields from the matched contract, not inferred permissive payloads.

For final review output, use the existing Request `review` object with actual actor, provenance, decision, outcome and approach; non-approval decisions additionally carry nonblank `requests`. Review approval has no blocking requests/questions. Request `questions` is empty for approve/planning return and contains the actual product questions for specification escalation; classification is routine/routine/material respectively. Report `review_evidence` is the existing `{commit, artifacts:[{path,sha256}]}` of the actual report checkpoint. Preserve exact original-input `references.accepted_spec` as Request `checkpoint` and `references.plan_candidate` as Request `plan_candidate`, even when the report commit is later. Include actual expected HEAD/repository/instance/worktree/cleanliness and current role-correct assessment. Do not infer these native field shapes from model output or reverse-engineer a binary when required contract evidence is unavailable; report the specific missing interface information instead. This is the current native action contract summarized for consumer use, not a separate transport protocol.

After one native finalization inspect accepted operation/current Feature and absent current run/claim. For incomplete/invalid body return, preserve report/work and use supported explicit release with current authority, not a manufactured decision. On uncertain finalization first inspect its operation/current state; never release/retry on an assumed outcome or continue under historical accepted ownership. Report rejected/uncertain recording or unresolved ownership precisely. Stop after disposition/release readback: no implementation, repair/re-review, extra child or subsequent workflow. Revocation is an authority control, not a process kill or automatic release.


## Current registration-retirement compatibility

The DIAG-12 deployment established schema22. The explicitly authorized DIAG-17 compatibility refresh supersedes that current pin with schema23 from integrated Diagram `a9233abfc82e328d521e3555ede073f3b6e10675`, retaining Project4, Issue-query6, Feature9 request grammar and Repository2/discovery1/capture2 families. Historical deployment records retain their recorded versions. Current reads expose project_status/retirement context; historical receipts retain their recorded versions. Verify active status before new work and never route a retired historical root to new work. Native transactional mutation guards remain authoritative, including manual paths and stale callers. Registration retirement preserves identities/history and immutable ID authority while releasing active repository-path exclusion; it does not onboard a replacement or delegate an approval role.

Inspect retirement through project retirement show before an explicitly authorized project retire request. Preserve the exact inspection fingerprint, stable operation and attributable Assessment; inspect the stored receipt/current state before retrying an uncertain outcome. No retirement, registration, import/cutover, enablement, migration or client refresh follows from ordinary workflow invocation or client availability. Historical worktrees require deliberate compatibility revalidation before use. Farmboy remains standalone and flow-roadmap authoritative until a separately reviewed workflow-authority cutover.

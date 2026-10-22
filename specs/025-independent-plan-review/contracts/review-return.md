# Reviewer-to-caller return contract

This is a small agent-readable contract, not a new API, JSON schema, subprocess protocol or persisted packet. Both coordinated layers run in the same independent reviewer session. A standalone caller receives the same semantic information without native context. The adapter resumes after the body returns once and reads the saved report itself.

## Minimum named content

| Content | Required meaning and validation |
|---|---|
| Report reference | Contained selected-feature-relative `validation/plan-review.md`, actual SHA-256 of saved bytes; missing/unreadable/different bytes means incomplete. Adapter may subsequently checkpoint those exact bytes under authorized scope. |
| Reviewed candidate | Same selected feature, exact approved specification and whole proposal/checklist/design/fresh-analysis/architecture references supplied and verified at entry; actual committed or uncommitted status explicit. No silent repin. |
| Reviewer and mandate | Actual reviewer identity, separate-session/non-authorship basis, actual bounded human mandate and applicable constraints/required independent evidence. No fabricated human provenance or Diagram identity authentication claim. |
| Six answers and findings | All six rubric answers with evidence in the report; actionable blockers name artifact/problem/reason/expected correction. Optional suggestions explicitly non-blocking and no unmet obligation. Return identifies findings and references their report sections rather than inventing another store. |
| Disposition | Exactly approve, planning-return or specification-escalation for complete semantic review; their meanings match spec FR-005. Approve cannot include blocking requests/questions/unmet obligations. Escalation carries actual product questions, not a revised spec. |
| Incomplete/error | On failure, no substantive disposition; precise failed/missing/uncertain input, evidence already saved, known effects, remaining work and next ordinary action. A partial report may be preserved but cannot be mistaken for approval. |

The receiving adapter compares return against saved report and current admitted candidate/grant/owner/session/run/epoch. Contradictions, a missing field/report, invalid digest/disposition, candidate mismatch, unverified authorization or revoked grant stop substantive finalization. Do not reinterpret free prose, infer approve from exit0, repair/rewrite reviewer conclusions or launch another review. Preserve evidence; release with current authority using supported native procedure if possible, otherwise report exact uncertain ownership and inspect before retrying.

## Adapter-only native mapping

- approve → handoff outcome plan_approved and review decision approve, no blockers; optional-only findings stay non-blocking.
- planning-return → plan_revision_required / revision-required, actual actionable requests.
- specification-escalation → specification_change_required / specification-change-required, material questions; historical spec approval preserved, no new spec approval.
- incomplete/error/invalid → no decision; explicit supported release/inspection and truthful incomplete handoff to caller.

Use actual admitted spec/proposal pins plus separate review_evidence report checkpoint; retain actual owner/session/run/epoch and native operation identities. Validate exact native fields against existing matched contracts. Accepted finalization and released authority are independently read back; a local return or checkpoint alone is not a native decision. Then stop, with no auto-implementation or new child.

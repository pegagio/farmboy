# FARM-28 existing information and state roles

No new persisted model, schema or report format is proposed. The following are semantic roles carried by existing Git artifacts and optional native records.

| Role | Existing content and validation | Relationship |
|---|---|---|
| Applicable return | Feature, originating accepted review handoff/known operation, `planning-return` or `specification-escalation`, committed report path/commit/SHA-256 | Must refer to the exact reviewed candidate and selected current return; newest report or equal bytes alone do not establish route authority |
| Reviewed candidate | Existing accepted-spec and proposal checkpoints, including plan/tasks/design/analysis references | Remains distinct from report checkpoint and revised current artifacts |
| Finding disposition | Existing report/item reference plus correction and artifact section/evidence, applicable resolution/supersession, voluntary advice reason or unresolved input | Every required finding driving the return must have a truthful disposition before a complete handoff; unresolved reason is incomplete, not resolution |
| Clarification answer | Actual operator answer in existing spec Clarifications section, with corresponding current requirements/scenarios/checklist changes | No fabricated answer; answer is not whole-spec approval |
| Approval and current run | Existing native decision/handoff/owner/session/run/epoch and revision pins, or standalone governance context | Evidence access supplies no execution authority; retain historical decisions separately |

## Existing transition boundaries

- Planning-return: accepted reviewer `plan_revision_required` with actionable requests, no product questions and routine classification; current state stays Ready for planning, spec approval retained, plan approval absent. Separately selected plan/planning-handoff admits corrections; fresh analysis precedes awaiting_plan_review and release.
- Specification-return: accepted reviewer `specification_change_required` with actual questions and material classification; state Needs clarification and applicable spec approval cleared. Separately selected clarify/clarification reads the report and asks/integrates answers. Retain its authority during genuine waits; successful resolution yields awaiting_spec_review and release, never planning eligibility by itself.
- A separately authorized revision already in a state permitting specify/flowback may use that existing route. It cannot replace clarification admission from Needs clarification, allocate a fresh feature or invoke initial draft setup.
- Missing evidence/ambiguous resolution/failed permission or technical prerequisite: preserve artifacts and exact issue, use existing supported incomplete/release/uncertainty handling, and verify outcomes. Do not invent a successful handoff or automatic next workflow.
- A human can explicitly resolve an unchanged specification through native existing governance; the consuming workflow cannot manufacture retain-approved or use historical approval to bypass changed-meaning review.

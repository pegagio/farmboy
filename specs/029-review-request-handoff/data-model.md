# FARM-29 existing data and responsibility model

No runtime schema, database table, dispatch registry or new persisted packet is introduced.

| Existing concept | Facts and constraints | Owner |
| --- | --- | --- |
| Selection | One actual project/Feature, immutable spec/proposal references and native candidate handoff/revision. Unknown or ambiguous selection stops before dispatch. | Selecting caller verifies Git/native facts. |
| Human mandate | Actual actor/provenance, explicit whole-plan approval role, protected intent/UX/constraints and applicable reviewer scope. Review alone is not delegation; no standing authority. | Human supplies authority; caller transports; reviewer independently verifies. |
| ReviewGrant | Existing Feature, pinned_handoff, expected_revision, reviewer_owner, reviewer_session, authorization Review. Values must refer to this candidate and selected independent reviewer. | Caller builds existing object from actual evidence; native validates consistency; adapter passes unchanged. |
| Reviewer session/run | Separate session without material authorship; one continuous reviewer invocation; at most one matching child per selected request. Native acquire/reuse and owner/epoch guards remain unchanged. | Existing host tools dispatch/inspect; adapter owns native run. |
| Saved result | Existing report_reference, reviewed_candidate, reviewer_mandate, findings, disposition or incomplete; actual immutable report checkpoint distinct from original proposal. | Reviewer judges; adapter checkpoints/finalizes/releases; caller verifies/collects. |
| Resume evidence | Known session/operation/Feature/candidate references in existing conversation/feature notes. No result or lost context means unknown, not finished. | Caller inspects existing native operation/current state before effects. |

Existing native states remain authoritative: awaiting_plan_review → plan_approved, plan_revision_required or specification_change_required after a valid independent terminal. The first permits separately selected delivery; the second permits separately selected planning return; the third holds work for separately selected clarification/spec review. No local caller state can create approval, completion or release. Incomplete is an observation of missing/failing work, not a new native lifecycle.

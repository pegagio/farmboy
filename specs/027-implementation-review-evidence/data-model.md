# Existing evidence relationships

These concepts already exist in approvals, Git artifacts and notes. This document adds no schema, classes, runtime object, packet or store.

| Concept | Existing information consumed | Validation/relationship |
|---|---|---|
| Approval | Selected feature, approved meaning/candidate, actual decision/provenance/conditions | Applicable explicit spec/full-plan approval remains necessary; tests/process output never create it. |
| Committed review | Report path, commit and supplied SHA-256 integrity reference | Verify actual Git blob/full content, supplied digest and contained feature association; uncommitted evidence cannot replace required evidence. |
| Reviewed candidate | Existing spec/proposal references and applicability evidence | Supports current approved meaning; report commit need not equal proposal/current commit. Routine flow-back needs evidence; material changes return to review. |
| Finding | Existing item reference/text, required/blocking versus optional meaning, priority and resolution/supersession evidence | Priority alone never establishes blocking. Unsettled status/contradictions stop. No new mandatory fields or machine enum. |
| Optional decision | Report/item, adopted or declined, concise reason in ordinary notes | Consider before related effects; record by closeout. Adoption identifies actual approved coverage/work; decline cannot waive obligations. |
| Prior assessment | Existing notes identifying considered evidence, applicability and decisions | Reuse only while valid; reassess relevant changes without duplicate work or overwriting history. |

For Diagram, trace current approval through supported native handoff/review references and verify actual consumer bytes. For non-Diagram consumers, approval/governance establishes report applicability. Without either condition record not applicable and retain ordinary behavior without Diagram lookup.

Evidence resolution, full reading, consistency assessment, optional decisions and ordinary implementation/closeout are instruction steps, not new lifecycle states. A gap/current blocker stops dependent effects under existing incomplete/ownership rules; it grants no automatic return or re-review.

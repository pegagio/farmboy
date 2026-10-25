# Return workflows consume plan-review findings

Native identity: FARM-28; captured idea SHA-256 `2231ce692fdb5e0a59dc325718bd206007bee73e6d74b5aa25bf609d0e976b07`. This request binds the existing item; it creates no new roadmap identity.

## Authoritative captured intent

Close the plan-review feedback loop on non-approval routes. When review routes work back to planning/tasking/analysis or to specification review, the next separately invoked workflow must locate and read the applicable current committed report and explicitly address the findings driving that route, recording traceable disposition in existing artifacts. Avoid stale report/candidate/route associations, distinguish resolved historical findings from current required action, and preserve required human specification review/approval gates. The reviewer must stop after its disposition, not rerun the next workflow itself. Whether one feature should cover both planning-return and specification-return branches is a focused open question for later specification. Complementary to FARM-27 (Implementation consumes current plan-review evidence): together, applicable review output is consumed whichever branch is selected, including successful approval. This descriptive link does not assert an execution dependency. Farmboy owns workflow semantics; the optional adapter locates authoritative Diagram evidence references, and Diagram owns state/approval authority. Reuse existing artifacts without new tracking infrastructure or assumed Diagram runtime behavior.

Captured example: A reviewer saves a planning-return report and stops. When the operator separately invokes planning/tasking/analysis, that workflow reads the correct report, addresses the findings that caused the return, and records disposition in the existing plan/tasks/analysis artifacts. A report identifying a specification issue routes to the separately selected specification workflow and human specification gate; neither the reviewer nor the next workflow silently approves it or consumes an unrelated/stale report.

## Current invocation

Pegagio selected initial FARM-28 specification preparation on 2026-10-25, including supported queue/link, an isolated worktree from current develop and normal scoped artifact checkpoints. Stop at clarification or human specification review. Do not infer approval or start planning/implementation. No installation, push, merge, schema or automation-control changes. BGG remains paused and is not accessed or resumed. The original capture was roadmap-only; this later explicit selection authorizes preparation only.

Source baseline: integrated FARM-27 at `20bbd66a941706c28d5afa959c8348031c405494`. Preserve its historical artifacts and all unrelated primary changes/untracked files. Reuse existing review evidence/notes and keep the change proportionate.

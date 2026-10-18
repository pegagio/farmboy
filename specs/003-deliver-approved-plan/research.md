# Research: Deliver approved plan through closeout

Research uses the installed repository contracts and ordinary Git behavior. No external repository, agent delegation, tool installation or runtime workflow experiment was used. The operator's no-delegation constraint overrides the core planning command's research-agent suggestion. These are design decisions for full-plan review, not implemented behavior.

## Table of Contents

The decisions below resolve technical context without adding product scope.

- [Composition](#composition)
- [Status and commit order](#status-and-commit-order)
- [Evidence and failure handling](#evidence-and-failure-handling)
- [Native boundaries and verification](#native-boundaries-and-verification)

## Composition

**Decision**: Add one Markdown skill, `.agents/skills/farmboy-deliver-approved-plan/SKILL.md`, with a guide, fixture cases and ordinary feature acceptance evidence. Compose installed speckit-implement, applicable project checks, speckit-converge, separate routine repair, roadmap-debrief, wiki-ingest and wiki-lint. Do not change the installed core skills.

**Rationale**: Existing 001/002 use this pattern; implementation and convergence have distinct write boundaries. Converge can append new tasks only after implement has run; it cannot repair spec/plan/code. It must leave tasks byte-identical on a clean result. Separate delivery-authorized repair handles coherent flow-back, then implement/verification/convergence reassess current behavior.

**Alternatives**: Manual command chaining is smaller in source but repeats the operator's coordination toil. A controller, new state format, automatic recovery or delegated executor is unjustified and prohibited. Recommend the single skill.

**Sources**: Installed speckit-implement and speckit-converge skills; existing farmboy-prepare-specification and farmboy-prepare-implementation-plan; FR-003–008/014.

## Status and commit order

**Decision from actual review feedback**: Finish implementation, required verification, clean convergence, coherent artifacts and documentation/debrief/wiki closeout. Include the implemented roadmap update with all scoped delivery artifacts, then make the final scoped local commit. Only after actual commit success report implemented/Awaiting result review. Preserve unrelated work.

**Rationale**: The human requested “It feels like we should end with a commit” and explicitly directed that ordinary Git errors need no special handling. If Git actually errors, report that ordinary error honestly without a delivery-success claim. No new failure procedure, state protocol, bookkeeping or reversal authority is justified.

**Alternatives and recommendation**: Manual chaining is simpler in source size but repeats coordination toil. Recommend the existing thin skill composition with a final scoped commit. Additional failure-handling machinery would add complexity without a current need and is not proposed. The latest explicit clarification resolves status wording; it does not approve the whole implementation proposal.

**Acceptance boundary**: Delivery never writes verified. Later explicit applicable human result acceptance separately authorizes implemented→verified. Neither acceptance recording nor delivery implies integration, merge or push.

**Sources**: FR-009–012, actual plan-review feedback and latest direct human closeout clarification recorded in spec.md.

## Evidence and failure handling

**Decision**: Use existing feature spec/plan/tasks and concise delivery notes/evidence only. Inspect normal current Git/roadmap state on entry/resume. Stop for an unavailable check, ambiguous identity/approval, an untrustworthy debrief delta, unclear commit scope or a material decision. Do not invent a pass, baseline or answer. Preserve actual partial effects and explain missing work.

**Rationale**: Debrief requires an attributable implementation delta; its default dirty-tree scope includes the complete actual delta, including unexpected paths. Do not silently filter unrelated paths or infer a clean-tree delta. Use a supported explicit range only when actual existing evidence establishes it; otherwise stop for the missing boundary. Debrief recommends and never writes lifecycle state. Ingest accepts one authorized contained source at a time; repeated ingest/lint may correct in-scope knowledge issues, not authorize product/governance changes.

**Ordinary errors**: Required checks or missing authoritative context stop dependent work under the existing command contracts. Report actual command/Git errors honestly without claiming successful delivery. No special commit-failure mechanism or additional persistence is proposed.

**Alternatives**: A persistent attempt registry or snapshots used by the workflow duplicate Git/roadmap and add maintenance risk. Recommend ordinary inspection and an honest stop. Test evaluator observations are evidence, not a runtime subsystem.

## Native boundaries and verification

**Decision**: Reuse the 001/002 bounded saved-handoff pattern. The delivery skill never creates/reactivates a Goal. For an explicitly selected matching objective, read actual controls; save the endpoint, complete it and verify native complete before requesting input or review. A bounded required-input endpoint saves INCOMPLETE delivery, exact input, artifact links, actual work/remaining issues and ordinary next action. Only an actual answer plus separately selected ordinary continuation resumes artifacts outside that completed Goal.

**Rationale**: This preserves FR-013 without claiming automatic waiting works. Unknown failures, unavailable controls and unmet delivery-only objectives are not successful input handoffs.

**Verification approach**: Define fixture expectations before implementation, then independently observe the actual final skill in a real Codex subject separate from the evaluator, including Farmboy and a disposable Spec Kit project. Test approvals/commits/status effects are fixture-scoped. Full local lifecycle observation includes actual clarification, explicit spec and full-plan approvals, delivery repair, closeout, result review and interruption/resume. Do not infer acceptance from simulations or static checks. This planning session performs none of those experiments. Subject/evaluator separation is a later verification arrangement, not delegation by the delivered skill.

**Alternative**: A new continuation engine cannot solve the need within this scope and is prohibited. Recommend supported exposed controls and existing artifacts only, preserving unverified native limitations honestly.

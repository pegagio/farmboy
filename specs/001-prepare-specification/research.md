# Research and design rationale — revision 2026-10-17

## Historical evidence retained

The earlier one-skill combined design successfully exercised ordinary single/multi-round clarification and human-review stops in an independent subject. Native Goals instead continued twice after an unanswered question and reached `Goal stalled`; the 2026-10-17 user-operated reproduction did the same. The final turn’s claim that it marked the Goal blocked was prose following a file read, not a native state receipt. These failures remain in [acceptance history](validation/acceptance.md), not reclassified passes.

Official Goals guidance separates model start/completion from user/system pause/resume. Client app-server Goal/input APIs are not automatically tools available to the skill-executing agent. No supported automatic suspend/resume contract was established for the tested mode. Do not build a controller or write host databases to compensate.

## Approved and implemented boundary

End the automated objective at a useful saved draft/handoff. This retains automation’s value while making completion observable before human interaction. Use existing Spec Kit clarification ordinarily afterward, preserving genuine waits and supported rounds; no new Farmboy clarification skill is necessary. Clarification completion remains distinct from explicit spec approval before planning, with review depth chosen by the human.

Use resolved Spec Kit templates and existing setup helpers for the automated drafting step. The full specify command may ask questions before it completes; bypassing that requirement after invoking it would be dishonest. The existing Farmboy skill can own bounded drafting/handoff without reproducing clarification. Missing helper support is an execution blocker, not permission to install or invent a framework.

## Alternatives and machinery

Keeping a live Goal across questions failed twice. Pretending native completion means approval would remove a human decision and is rejected. A separate clarification skill duplicates existing capability without necessity. A custom controller, persistence layer, database repair, forced mode switch or modified core command is unnecessary and unapproved. The one existing skill plus ordinary clarify is the delivered minimum.

## Verification requirement and observed result

Independently observe actual native Goal completion at ambiguous and settled handoffs; ordinary question wait/answer incorporation outside that Goal; preserved resume/portability; and no planning without explicit approval. Earlier ordinary success is useful historical evidence, not proof of revised runtime behavior. No new runtime test ran during this design revision.


The revised independent observations are now recorded under T025–T028 in [acceptance evidence](validation/acceptance.md): both handoffs, actual ordinary question/answer/review stop, operator-observed native completion with session corroboration, and explicit test-only approval recognition without planning. The API does not expose a native Goal-state receipt. The settled case revalidates an existing draft; earlier tests cover creation/selection. Final reconciliation and closeout checks are recorded separately rather than treating these source notes as proof.

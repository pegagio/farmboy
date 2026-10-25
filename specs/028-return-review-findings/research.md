# FARM-28 research decisions

Source inspected: Farmboy approved specification `efccb744ff69f73115c337a24fa2258a31b52149` and existing workflow sources at the same tree; read-only matched Diagram source `6cc924aca52e51318be10e08f63554fbcb62d56b` supplies native contract context. Installed schema22 supported and Feature9 verified. No external package, installation or product unknown remains. Research was performed in the same planning session as prescribed by the composite; no runtime steps were delegated.

## R1 — Share evidence semantics, retain separate execution paths

Decision: reuse FARM-27 full-report/integrity/applicability and required-versus-optional semantics, extending the existing planning entry and ordinary clarification context. Planning return repairs plan/tasks/design and performs fresh read-only analysis. Specification return carries actual product questions through existing clarification/revision, preserves genuine waits, and returns to human specification review. The reviewer stops after disposition.

Rationale: `.agents/skills/farmboy-prepare-implementation-plan/SKILL.md` already supports in-scope revision without resetting artifacts/tasks; `farmboy-prepare-specification` already points to separately invoked ordinary clarification. `speckit-clarify` takes user input, reads the current specification, integrates actual answers and reassesses the checklist. It needs applicable return context, not a replacement command. Keep all core `speckit-*` bodies/helpers unchanged.

Alternatives: a unified return executor or new clarification skill would duplicate authority and wait behavior; fresh preparation on escalation would conflict with current native Needs clarification admission and risk dropping accepted answers. Rejected.

## R2 — Native evidence is available without a schema change

Decision: use `feature show` current handoff/plan_review/original_input and known `feature operation show` records to locate the accepted return's `review_evidence`, `plan_candidate` and disposition. Verify actual committed Git bytes separately. Never query private SQL or pick the newest report. Retain the originating operation/report/candidate references in ordinary affected plan/spec notes before a later handoff would otherwise obscure them.

Rationale: current native `model.go` exposes Handoff.review_evidence and original_input; `plan_review.go` stores report/candidate/spec roles separately for both nonapproval dispositions. A planning return is Ready for planning with revision_required and historical spec approval retained; specification escalation is Needs clarification with current approval cleared. Existing `run.go` admits plan/planning-handoff versus clarify/clarification accordingly. Source inspection proves interface availability, not actual future model obedience.

Alternatives: changing native persistence, creating an evidence ledger, scanning arbitrary historical operations or treating current HEAD as reviewed candidate are unnecessary and outside scope. If supported records plus retained known references cannot establish association, stop precisely rather than guess.

## R3 — Generic clarification receives context, not a new lifecycle

Decision: document one human-readable generic return-consumption rule in `docs/workflow-handoffs.md` and the existing specification continuation guidance; pass the applicable full report/reference, candidate, disposition and real product question as ordinary context to the existing `speckit-clarify` invocation. The optional adapter supplies authoritative references and current native authority, not product answers or semantic approval. The ordinary executing model reads/interprets findings and integrates answers under that selected clarification workflow. Standalone callers supply equivalent explicit current return evidence without Diagram.

Rationale: avoids editing core Spec Kit or making a guide a new runtime loader, fixed packet or transport API. The existing Farmboy specification entry only directs already-returned work to the established continuation; it does not redraft, answer questions or execute clarification from a completed preparation invocation. Genuine clarification holds the selected clarification authority until saved review or explicit incomplete/early-stop release. Specify/flowback remains limited to already-permitted current states; never reacquire an initial claim for a linked return.

Alternatives: modifying core clarify to depend on Diagram, wrapping it in an autonomous controller, or doing semantic correction in Diagram are rejected. No report-bearing return is interpreted as approval.

## R4 — Dispositions remain ordinary artifact content

Decision: record each finding by report/item reference with changed artifact/section and evidence, applicable existing resolution/supersession, optional adopted/declined reason, or precise unresolved input. Use plan/tasks/analysis notes for planning and spec Clarifications/notes plus requirements checklist for specification. Do not use checkboxes as the sole failure report. Required findings remain obligations at every priority; only actual product answers resolve product questions.

Rationale: meets traceability without counters, scores, tables with lifecycle ownership, new file formats or external storage. Existing resolutions can be reused when still applicable; revision inequality alone neither erases nor reopens findings.

## R5 — Proportionate verification uses existing fixtures

Decision: extend maintained review contract tests and existing planning/specification/adapter case recipes, reusing existing semantic-fixture and actual Codex observation patterns. Add narrowly scoped return-fixture inputs/bridge files only where the existing fixture lacks the two return dispositions; no new general test runner. Later delivery must show real executing sessions separately evaluated, including both generic and matched private native paths. No live FARM/BGG store used as a test fixture.

Rationale: static checks prove instruction placement/unchanged boundaries; actual full-report reads, repair, question waits, native handoff and absent-owner readback require observation. Historical schema20 native builder is not current proof: use only a private matched schema22 source snapshot/compatible existing helpers with explicit delivery-time test authorization. Missing access/capability remains unpassed, never installation or permission bypass.

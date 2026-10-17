# Conceptual artifacts: Prepare implementation plan

This model describes information already present in conversation and Git artifacts. It is not a new schema, database, runtime approval register, state file or entity implementation. No classes, typed payloads or persistence layer are proposed.

## Existing information and validation

The following named concepts let the skill inspect current work without hiding authority in ambiguous prose. Existing artifacts remain canonical.

| Concept | Existing location and information | Validation constraint | Relationship |
|---|---|---|---|
| Selected feature | Explicit operator target and .specify/feature.json; contained feature path and current artifacts | “One selected feature; explicit and ambient identity must agree before effects.” | Owns the current spec, plan and tasks |
| Approved specification | Available conversation OR an applicable existing review note identifying approved content | “Explicit approval of current meaning is required; material changes require affected human review.” | Governs the proposal; no new register |
| Implementation proposal | plan.md, required supporting design artifacts and tasks.md; dependency order and task completion evidence | “Preserve current artifacts, accepted decisions and existing task identities on resume.” | Implements only approved specification intent |
| Analysis finding | Ordinary current read-only analysis report: location, issue, severity and suggested correction | “A pass requires zero actionable inconsistencies and zero unmet requirements, regardless of severity.” | Separate authorized repair may edit affected artifacts; analysis does not |
| Optional suggestion | Ordinary report prose identifying a non-required improvement | “No actionable inconsistency or unmet requirement may be relabeled optional.” | May accompany review; does not prolong polishing |
| Handoff | Concise existing feature notes and available conversation; actual result, attempts/issues when incomplete, next human action | “Edits alone prove neither progress nor passing; no numeric limits, counters, scores or new persistence.” | Awaiting full-plan review only after fresh pass; INCOMPLETE otherwise |

## Readable stages and authority

These are explanatory labels, not new roadmap lifecycle values or machine state transitions. Approved spec plus separately selected planning authorizes preparation; completed current proposal plus qualifying fresh analysis leads to Awaiting full-plan review. New decisions, scope/material changes, genuine blockage or repeated unsuccessful approaches lead to an INCOMPLETE input handoff. Human review may request authorized revision, which reconciles artifacts and repeats fresh analysis. Plan approval is a separate explicit decision; even approval does not make this skill implement anything. Existing approved-review handoffs are presented rather than reactivated.

## Out of scope

There are no data-volume, field-length, migration, retention or concurrent-writer controls to implement. Runtime is one session/feature. Do not turn these conceptual rows into JSON packets, an approval service, a findings ledger or a progress monitor. Future independent verification may record ordinary human-readable observations and source references; those are evidence, not runtime ownership/state machinery.

## Bounded automation handoff distinction

Existing plan/spec notes retain INCOMPLETE planning outcome, exact human input, artifact references, attempts/issues and next ordinary action. A separately selected Goal may successfully finish that saved-human-input handoff objective before interaction; this is distinct from analysis passing and plan approval. After a real answer ordinary continuation preserves the completed Goal and existing artifacts. No new entity, schema, store or controller is added; technical failures and unmet clean-proposal objectives remain outside this endpoint.

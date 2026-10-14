---
title: Codex workflow controller design
type: concept
sources: [S033, S036, S039]
updated: 2026-10-14
---

# Codex workflow controller design

The canonical `controllers/farmboy/controller-protocol.md` is shared by ten active direct Codex skills. Installed workflows own prompts, commands, branches and gates; the main controller executes that graph without copying decisions into skills or invoking the native workflow runner. Historical FlowKit catalog/controller contracts and earlier concrete-model topology remain in [controller history](./codex-controller-history.md); they are not current FarmBoy identity or live-dispatch proof. (S033)

## Native dispatch and interaction

Each delegated executable step declares `farmboy.delegated: true` and an exact reviewed `farmboy.agent`. Names alone create no delegation. Main validates all branches and probes each distinct exact native `agent_type` before creating workflow state. Missing, invalid or unavailable assignments stop without a substitute; probes perform no work and are not execution children. Configuration belongs to Codex and the consumer, with no per-run agent, model or effort override. A title or matching model does not prove native selection. (S033)

Each modeled delegated step receives a fresh bounded child; accepted human answers return to the same interactive child. Main retains gates, switches, orchestration and consequential choices. Definition, availability, native dispatch and observed model/effort are separate evidence; protocol text does not establish any live FarmBoy launch. (S033)

## Installation and recovery boundaries

Bootstrap uses `.specify/farmboy/scripts/bootstrap.sh`, the installed manifest/skill records and read-only composed graph. Main captures workflow digest and installation fingerprints and rechecks them at step boundaries. Refresh lets an active node finish, then stops further work. New recovery summaries live beneath `.specify/farmboy-controllers/`; existing installed packages or historic records gain no refreshed identity merely because source names changed. (S033)

A successful command grants no Git integration, roadmap verification, publication or acceptance. Completion cannot launch another workflow phase. Failed or interrupted work preserves partial edits and records an exact blocker and safe resumption boundary; no automatic rollback or blind retry follows. (S033)

## Metrics turn contract

The shared protocol retains one metrics correlation UUID across probes, working turns, continuations and retries, separately from recovery identity. Exact assignment context, safe logical project identity and passive exact-name project TOML settings are prepared before timing; unavailable settings are null and never control dispatch or establish runtime settings. (S033)

Begin immediately before native spawn or same-child continuation. Keep the token in main context through pending acknowledgements and polls; finish only after an observed end, including question, rejection, failure or interruption. Finish a question turn before human waiting; a resumed turn gets a new token. Unobserved endings produce no completed record. Tokens never enter child prompts or results. (S033)

Clock, metadata, helper and storage failures warn while preserving original dispatch, results, routing and human gates. Failed begin creates no invented record; finish reads the clock before persistence. Failed publication is not retried or replaced. These are normative protocol requirements, not live instrumentation proof; the [local timing design](./local-agent-timing-metrics.md) defines the record and workbook contract. (S033, S036)

## Feature 023 validation contract

The [validation boundaries](./workflow-validation-boundaries.md) distinguish whole-definition validity, selected-route input availability at consumption, and required source/installed parity. Feature 023 specifies these contracts and deterministic evidence limits; its requirements alone establish no measured live result. (S039)

## Related pages

- [Assessment contract](./controller-assessment-contract.md)
- [Graph responsibilities](./workflow-graph-responsibility-boundaries.md)
- [Named agents](./agent-roles-and-inheritance.md)

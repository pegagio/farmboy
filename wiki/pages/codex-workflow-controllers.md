---
title: Codex workflow controller design
type: concept
sources: [S033]
updated: 2026-10-11
---

# Codex workflow controller design

The canonical `controllers/farmboy/controller-protocol.md` is shared by ten active direct Codex skills. Installed workflows own prompts, commands, branches and gates; the main controller executes that graph without copying decisions into skills or invoking the native workflow runner. Historical FlowKit catalog/controller contracts and earlier concrete-model topology remain in [controller history](./codex-controller-history.md); they are not current FarmBoy identity or live-dispatch proof. (S033)

## Native dispatch and interaction

Each delegated executable step declares `farmboy.delegated: true` and an exact reviewed `farmboy.agent`. Names alone create no delegation. Main validates all branches and probes each distinct exact native `agent_type` before creating workflow state. Missing, invalid or unavailable assignments stop without a substitute; probes perform no work and are not execution children. Configuration belongs to Codex and the consumer, with no per-run agent, model or effort override. A title or matching model does not prove native selection. (S033)

Each modeled delegated step receives a fresh bounded child; accepted human answers return to the same interactive child. Main retains gates, switches, orchestration and consequential choices. Definition, availability, native dispatch and observed model/effort are separate evidence; protocol text does not establish any live FarmBoy launch. (S033)

## Installation and recovery boundaries

Bootstrap uses `.specify/farmboy/scripts/bootstrap.sh`, the installed manifest/skill records and read-only composed graph. Main captures workflow digest and installation fingerprints and rechecks them at step boundaries. Refresh lets an active node finish, then stops further work. New recovery summaries live beneath `.specify/farmboy-controllers/`; existing installed packages or historic records gain no refreshed identity merely because source names changed. (S033)

A successful command grants no Git integration, roadmap verification, publication or acceptance. Completion cannot launch another workflow phase. Failed or interrupted work preserves partial edits and records an exact blocker and safe resumption boundary; no automatic rollback or blind retry follows. (S033)

## Related pages

- [Assessment contract](./controller-assessment-contract.md)
- [Graph responsibilities](./workflow-graph-responsibility-boundaries.md)
- [Named agents](./agent-roles-and-inheritance.md)

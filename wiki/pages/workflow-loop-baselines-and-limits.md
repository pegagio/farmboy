---
title: Workflow loop baselines and limits
type: reference
sources: [S033]
updated: 2026-10-14
---

# Workflow loop baselines and limits

Earlier Feature 014 capacities and retained FlowKit recovery contracts remain in [loop history](./workflow-loop-history.md). The canonical FarmBoy protocol preserves finite progress checks: substantive independent resolution of prior findings or eligible tasks is required; hashes, command success, questions and markers alone earn no progress. Gates and consequential human answers remain in main. (S033)

## Current Implement scope

Requested scope is immutable and distinct from current eligibility. The seven-node `implementation_scope` carrier is specific to `farmboy-implement`, with an exact five-pass limit. Main stores append-only session/source-attempt events in `.specify/farmboy-controllers/implementation-history/<run-id>.json`, validating predecessor and evidence before atomic write. Session start precedes new Coder dispatch; failed dispatches and question-stopped sessions count. Same-child answers append evidence without another session. Preparation, eligibility refresh or Tasker updates never refill either budget. (S033)

After source work, independently evidenced prior-finding or scoped-task resolution, current readiness and validated history govern continuation. FarmBoy Tasker revisions do not resolve findings; FarmBoy Code Reviewer completion requires whole-task proof and no unresolved owned finding. No progress, stale history, unavailable authority, unanswered consequential questions and exhausted applicable budgets stop safely. Read-only source-preimage recovery itself grants no additional pass, counter reset or continuation of a capped run; the explicit bound run-budget exception below requires separate operator authority. (S033)

An explicit operator instruction may extend only this scoped run’s ceiling to a larger finite integer. Main verifies actual human authority and retains `budget_extension` with an independently held `retained_budget_extension_sha256` before re-entry, forwarding both through scope, eligibility, activation, history, capture and route callbacks. The receipt binds schema version 1.0, run ID, original scope digest, existing history-prefix digest, actual consumed Coder-session/source-attempt counts, previous/new limits and nonempty current authority evidence; the initial previous limit is five. Labels and self-authored receipts establish no authority. Missing, changed, cross-scope or unbound receipts, altered authority evidence and mismatched history prefixes block. Original scope, consumed counters, failed attempts and the generic no-progress predicate remain unchanged; answers, markers, receipts and extensions never reset history. Other workflows retain declared caps. Routine execution cannot invent an extension, and this exception grants no roadmap, Git, acceptance or other-phase authority. Retained prefix/budget fields pass unchanged until a current validator returns a newly validated tracking prefix; returned hashes grant no permission. (S033)

## Close Out wiki scope

Wiki maintenance is a sibling five-pass loop after roadmap verification. Each pass ingests one source from the frozen authorized set with exact source-backed stable claim findings, then performs full lint and independent assessment. Claim-level correction can earn progress while other claims from that source remain unresolved; source coverage is a grouping. Findings cannot be renamed to manufacture progress. Later lint cannot expand the frozen set. (S033)

Main may revalidate date-only warnings against all current cited claims and authorized sources. Only supported conflict-free claims permit an actual-date freshness update with claim/source and before/after proof; timestamps earn zero substantive progress. Missing access, unsupported or conflicting claims, no progress and cap exhaustion remain blockers. Commit readiness requires the latest complete assessment with no unresolved coverage or lint findings, rather than successful ingestion alone. (S033)

## Related pages

- [Assessment contract](./controller-assessment-contract.md)
- [Graph responsibilities](./workflow-graph-responsibility-boundaries.md)

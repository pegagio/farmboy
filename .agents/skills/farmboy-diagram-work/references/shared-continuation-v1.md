# Shared bounded continuation (schema26 / Feature9)

DIAG-24 replaces separate mutable planning/delivery policy storage with one optional `feature_contexts.continuation_json` envelope (`entries`, unique fixed stage/purpose slots). Existing claim/run/operation receipts supply lineage and consumption; no ledger, scheduler, generic handler framework or background resolver. Source availability does not install clients, migrate a live store, enable controls or authorize a Feature continuation.

## Actual operations and roles

`feature continuation show --feature ID` reads policies/status and history-derived consumed/remaining allowance. `feature continuation record --feature ID --operation OP --request-file FILE` records a strict Feature9 request containing expected Feature/queue revisions, exact dependencies/current handoff, actual input checkpoint/approval pins, Assessment and `continuation_policy`. The policy record has `segment`, `purpose`, `decision`, optional `previous_allowance`, `mandate`, `stop`. No decision can carry unrelated run/approval/integration fields.

Decisions: authorize, renew, hold, clear-hold, assess-stop. Authorize/renew requires actual human Review decision `authorize-bounded-continuation` with actor/provenance/outcome/approach/conditions. Renew names the exact prior allowance. Hold/clear-hold use `hold-continuation` / `clear-continuation-hold`; clearing a hold grants no mandate or readiness. Existing paused/denied disposition cannot be cleared by coordinator diagnosis or renewal. Legacy planning/delivery commands retain their exact old authority labels and role restrictions as translations into this same engine, with immutable old operation digests/replay receipts.

Stop identifies exactly `claim_id` or `run_id`, epoch, disposition recoverable/paused/denied/unknown, and an attributable Assessment. Optional complete readiness is allowed only for recoverable: expected_head, workspace_clean, existing stopped-writer/preservation Recovery, failed/changed/evidence/explicit unverified resolution and coordinator Review `continue-bounded-continuation`. Setup adds verified workspace/branch/repository/instance/worktree/checkpoint reports. Required unknown facts remain blocked; metadata does not prove physical truth or semantic resolution.

`feature run recover` with `recovery.action=successor` accepts exactly one released predecessor selector (`claim_id` for setup; `run_id` for execution) and `continuation` {segment,purpose,allowance_operation,resolution}, exact current revision/queue/dependency/input/identity/HEAD/preservation/decision reports and selected owner/session. Native admission revalidates before ownership in its transaction, preserves original inputs/history, consumes one allowance and records explicit predecessor origin. No fresh acquire fallback, terminal reactivation or epoch reset. Setup returns preparation authority only; ordinary request-only link carries its origin into the same-owner drafting run.

## Supported stage checks and stops

| Slot | Additional boundary |
| --- | --- |
| setup/draft | Actual latest released unlinked setup claim/nonzero epoch and unchanged captured/queued input/Project/source/dependencies. Consumer verifies existing scaffold; first captured link identifies exactly one specs/<directory>/request.md, even when a blank spec template is committed. Existing clean-link and identity validation remain intact. |
| specify/draft, specify/flowback | Actual original drafting or expressly authorized revision purpose, associated workspace/input and current purpose/state/approval applicability. Normal committed specification handoff; never manufacture approval. |
| plan/planning-handoff | Applicable specification approval and exact accepted planning input; normal whole-plan review. |
| deliver/delivery | Applicable specification/whole-plan approvals/candidate, partial implementation/task/evidence preservation and remaining external budgets; normal result review. |

Released independent review/integration continuation is deliberately unsupported. Normal review requires exact caller grant, independence and revocation checks; DIAG-25 availability is separate. Integration partial/uncertain Git effects require deliberate target reconciliation. Clarification answers/result acceptance remain human decisions, not recoverable waiting. Active-owner resume/replace remains separate and preserves any existing continuation origin/consumption.

One admitted successor consumes its allowance even if setup link or later work fails. Replay, competing caller, another operation/coordinator, host restart, changed input or stage alone grants no new attempt. Explicit applicable operator renewal preserves prior history and grants/reset no other right. Paused/held, denied, unresolved, possibly live, unknown, scope-mismatched or exhausted work stays stopped. Inspect uncertain operation/current state before retrying. Consumers verify Git/files/processes and resolution; native core validates recorded consistency and attribution only.

## Discovery and observation

Ordinary discovery uses current project/workflow toggles, dependencies and exact readiness/allowance. New work uses `recovery_mode: released-continuation` with actual segment/purpose; setup additionally reports setup_required. Existing legacy delivery transport remains accepted for its original wrapper scope. Linked drafting continuation is distinct from pristine initial setup. Current normal ordering and one awaited child/same-store guard remain unchanged; disabled toggles block new admission, not cancel an owned child.

The launcher transports stored readiness unchanged; selected child verifies actual facts and recovers first, reuses authority once, completes only missing/affected work with normal hooks and stage checks, then commits/finalizes its human handoff. Observation requires actual child exit, exact attributable admitted origin/original input and committed handoff/released ownership. Zero exit or claim release alone is not success. Failure/uncertainty stops the poller visibly; no automatic retry/host restart, guard clearing or bypass.

## Explicit preserving25→26 migration

`database upgrade --file STORE --from-version 25 --to-version 26` requires separately authorized cutover, exact schema identity/shape and zero active claims/runs. It converts old planning/delivery policies through the matched pure policy decoder, removes their mutable columns, preserves all other context values/revisions, every run/handoff/approval/operation receipt and controls, checks recovery history, foreign keys/integrity and schema in one transaction. Malformed/ambiguous/unknown authority or injected failure rolls back. Already-current revalidates26; older clients refuse the new version. Snapshot/restore remains separately explicit.

Existing allowance IDs, mandate/input scope, holds/dispositions and consumed origins remain authoritative. Legacy null stays opted out; incomplete old planning readiness stays non-discoverable until fresh applicable evidence is recorded. Conversion never authorizes a retry or repins a predecessor. Historical command replay returns its original receipt unchanged and restores no ownership. Normal admission never migrates a store. Private fixture evidence proves declared composition, not real model/platform obedience or live BGG behavior.

# Workflow contract: completed-checkpoint workflow revision v1

This source contract is not installed until an explicitly authorized cutover. Existing Feature9/contract9 payloads remain accepted with optional additions; capability advertisement and schema28 checks gate new use.

## Operator entry

Provide `feature revision request`, `feature revision show`, `feature revision withdraw` and an explicit replacement option on request. Request/withdraw are normal native operations with stable operation IDs, expected Feature/queue revisions and selected store. Request accepts explicit flags for exact feature/handoff/checkpoint, authorized segment, repeated concrete changes, actual actor/provenance/conditions and optional source decision/replaced ID. For spec requests, include complete authority/changes in the accepted envelope and original operation result receipt; request_sha256 alone cannot retain provenance because original request bodies are not stored. The maintained CLI constructs and validates the typed payload; an agent does not extract nested JSON to manufacture it. Reject duplicates/unknown flags, blank provenance/changes, unsupported pairs, incomplete artifact bundle or inconsistent current pins. Full checkpoint is resolved from the named native handoff and compared to the supplied commit; never inspect consumer files in core.

For plan/result sources, use existing review commands/decisions as canonical publication. A management request may reference an existing exact return to withdraw/replace its dispatch intent, but cannot erase rejection, supply missing human authority or duplicate its approval. Existing returned plans need no registration. Preserve currentPlanDecision linkage: original candidate/source decision handoff and current reviewer-disposition handoff may differ and must both remain exact. Source decision scope and applicable execution mandate are checked; an approval to request changes alone is not silently broadened into unbounded execution.

Show returns one normalized typed revision view: source/target, requested changes and provenance, segment/purpose, pending/admitted/withdrawn/blocked/stale, reason, source/creation operation and admitted run when applicable. Missing intent is explicit; malformed/error responses are never interpreted as no request or authority. Withdrawal reports already_admitted with the existing run if acquisition won, rather than pretending success. Replacement requires naming old source and actual fresh request authority. Reissuing consumed/withdrawn intent under another ID without new human authority refuses.

## Selection and maintained admission

Extend EligibleWork with optional revision reference and preserve actual purpose. One common selector returns typed selection for forward work, completed revision or existing continuation; explicit stage switches remain small. Existing ordering and controls remain. Pending/blocked same-feature intent is authoritative over superseded forward work even with its workflow OFF. Unrelated features remain eligible under existing ordering. Never parse allowed_actions prose to reconstruct routing.

Expose a maintained revision-admission CLI entry used by launcher/adapter. The launcher renders exact native source/target pins and child owner/session; the consumer inspects actual mandate and reports actual branch/workspace/HEAD, canonical identities and clean/preserved-artifact assessment using existing stage reporting. The command resolves current native envelope, validates required reports, constructs the existing acquire request deterministically with discovery_selected and revision reference, then calls the same Store acquire path. No separate owner, preview acquisition or hand-built request file is needed. Preparation/flag/report failure creates no run or consumption; uncertainties inspect operation/current state before any retry. This is a narrow new route, not a redesign of all native actions or a claim to authenticate semantic human consent.

Inside the acquire transaction recheck selected source/target/current revisions, workflow/project controls/dependencies, owner/stopped prior writer and current applicable approvals/conditions. Validate stage pair: specify/flowback on linked complete spec; plan/planning-handoff on current return; deliver/delivery on current repair. Native physical reports remain consumer claims. Record revision origin with one run, consume atomically and preserve operation replay. No new run/segment/status enums. Manual normal admission must not bypass a pending revision or reconsume a failed one under different labels.

## Stage-specific handoff

- Specification: preserve existing routine/material applicability assessment; unapproved draft returns to review/real clarification; material changes clear affected current decisions under existing rules while historical approvals remain.
- Planning: coherent plan/tasks/fresh analysis; latest candidate needs appropriate exact caller review grant and independent reviewer. No reuse/repin of old grants.
- Delivery: repair within applicable approved scope, fresh evidence/convergence; result acceptance and integration permission must apply to the new result.
- Review verdicts, human answers/acceptance, integration/replay and Done/cancelled history are not revision execution targets.
- Active ownership and DIAG24 released-incomplete continuation remain separate, with preserved revision origin and budgets. No request renewal disguises failed execution as fresh forward work.

## Compatibility and refusal

Nullable intent preserves prior records; schema28 requires an explicitly approved preserving upgrade and matching tools at deployment. New conditional capability prevents consumers from assuming support from binary presence. Tests cover missing/wrong capability, stale/withdrawn/conflicting intent, off controls, new-ID replay, permission denial/uncertain effects, failed preparation and two-writer races. No production store migration, grant publication or workflow activation is authorized by this document.

## Implemented command flags

`feature revision show --feature ID --file STORE --json` returns the typed Feature9 revision view. For request/withdraw supply `--operation`, `--revision`, `--queue-revision`, `--handoff`, `--candidate` (current execution checkpoint commit), and attributable `--actor`/`--provenance`. Request additionally requires `--outcome`, `--approach`, repeated nonblank `--change`/`--condition`, and optional exact `--replaces`. Withdraw requires exact `--source`. No request-file/envelope extraction is needed.

`feature revision acquire` requires those exact current revision/queue/handoff pins, `--candidate` (the revision target bundle commit), `--source`, and actual inspected `--owner`, `--session`, `--workspace`, `--branch`, `--head`, `--repository`, `--instance`, `--worktree`, `--workspace-clean`, `--rationale`, repeated `--evidence`/`--condition`. Ordinary poller entry includes `--discovery-selected`; manual authority does not. It deterministically builds the existing acquire input. Any uncertain or historical invocation must be inspected through existing `feature operation show`, never automatically repeated. Preparation errors do not consume a request. CLI/metadata acceptance is not independent authentication of human consent or physical Git facts.

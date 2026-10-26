# FARM-29 research decisions

## Caller entry placement

**Decision**: Add `farmboy-request-plan-review` as the operator-facing selecting caller; preserve the independent semantic body and add only a small route seam for a direct user request versus an already dispatched reviewer.

**Rationale**: Existing source accepts supplied grants but has no owner for producing and dispatching them from human intent. A plan-author session may coordinate but must never make the independent decision. Current generic review body forbids launching another workflow; it must route a caller request before becoming the reviewer, not recursively create reviewers from inside semantic execution.

**Alternatives considered**: Have the reviewer generate its own grant (violates actual caller authority); add dispatch to every planning entry (duplicates responsibility); add a generic drive engine (larger unapproved scope). A single portable skill is the smallest explicit entry and can later be composed without adding authority.

## Native and host mechanism

**Decision**: Reuse Diagram's existing per-invocation ReviewGrant and independent-session entry/result facilities. Pin private native acceptance source to integrated `f6494a1e390d29e6657e95a6b6f6c28bebe09ac0`, schema23/Feature9. Production scope changes no Diagram source.

**Rationale**: `internal/feature/plan_review.go` already binds Feature, handoff/revision and reviewer owner/session, rejects same recorded candidate author and uses human Review fields; launcher transports a supplied `--review-grant-file`. It is not an explicit arbitrary review selector: use an already supported exact manual independent-session route when discovery cannot select this candidate. Source pin is fixture compatibility, not authority to migrate/install/enable production.

**Alternatives considered**: New launcher selector or discovery ordering; native grant service; dispatch store. None is needed. Host tools differ, so capability-based start/read/wait instructions use whichever existing route actually supports the required isolation and result inspection. Missing capabilities stop before dispatch, without “fallback” admission to an uncoordinated route.

## Mandate and recovery limits

**Decision**: Already explicit bounded delegation is reused; ambiguous review-only/advice-only requests stop for the missing substantive role. Caller retains child/operation locators in ordinary session evidence and inspects before any resumed effect.

**Rationale**: Removing operator-authored JSON does not remove human mandate. Native records protect authority; they do not authenticate human prose or prove process death. Unknown dispatch cannot safely become a second reviewer.

**Alternatives considered**: Automatically delegate on “review”; infer absence from missing result; add restart/lease/monitor registry. All exceed the approved boundaries.

## Acceptance strategy

**Decision**: Reuse current source-contract and disposable Git/native test conventions, add focused caller fixtures, and require independently evaluated actual caller-to-reviewer execution.

**Rationale**: Constitution III and FR-014 require actual changed-skill behavior, not only transport fixtures. Shared refusal variants and one real complete journey plus real negative dispositions/failure boundaries provide proportional coverage. No massive host matrix or real Fusion retry is required.

**Alternatives considered**: Only check prose; only test semantic reviewer; manufacture native receipts in a fake model. These do not prove the missing dispatch/collection behavior.

All planning unknowns are resolved from current source, approved scope and existing runtime contracts. No research agent, new dependency installation or external browsing was needed or invoked.

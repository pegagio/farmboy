# Implementation Plan: Reusable independent plan review

**Branch**: `025-independent-plan-review` | **Date**: 2026-10-22 | **Spec**: [spec.md](spec.md)

**Status**: Whole plan approved by Pegagio Sentinel_ed01a0edd9a081919407404a0e369b2a; selected for bounded implementation and isolated real-session evaluation. Human result acceptance remains pending.

**Input and approval**: Pegagio's Sentinel_544eb7cc99508191ba0dac1c79e64f3a approves the complete specification and planning. The exact approved spec SHA-256 is `486a4c5240b5d3e9e5b7a4ffe876717ad67e115c59cd75858046c7bdc4fbfcfe`, uncommitted at base `e5f8bbf76f74da9898518e820aca936c54e2dcae`. Approval is recorded against025 in the canonical flow-roadmap ledger, now specced. The approved file remains byte-identical, including its historical drafting header. This plan clarifies its return contract without changing product scope.

## Summary

Add one generic Markdown review skill and guide, and extend the existing optional Diagram adapter/reference for that review entry. An independent authorized session answers the exact six questions, saves one report and returns a small ordinary result to its caller. Same-session skill composition means the executing agent follows the adapter, enters the semantic body, saves the report, then resumes the adapter instructions; it is not a subprocess return ABI or new API. The launcher may start this reviewer session, but the adapter and body share that one session.

The body decides semantic approve/planning-return/specification-escalation, or incomplete. Only the adapter acquires/reuses native authority, transports the actual supplied grant, checkpoints authorized report evidence, maps native terminals, finalizes once and verifies release/readback. Proposal artifacts stay unchanged. No new lifecycle owner, runtime library, scheduler, evaluator service, schema, installer or automatic next phase.

## Technical Context

**Language/Version**: Markdown skills/guides and existing Git/JSON tools; focused Python3.11 standard-library unittest fixtures match this repository's toolchain. No production Python wrapper.
**Primary dependencies**: Existing Farmboy standalone/external seams and optional adapter; explicitly authorized Diagram reference source `d29c0809f722985bf2fd2a7fd5cfd8a2e4ce573e`. Native review requires matched Feature9/schema20 CLI and launcher only in disposable tests. Selected live store remains schema19 and must never be opened by the schema20 fixture binary.
**Storage**: Existing feature Git artifacts and ordinary report `validation/plan-review.md`; native Diagram records remain authoritative when enabled. No new database, registry, persistent transport or generic grant store.
**Testing**: Source-boundary assertions plus one reusable private Git/SQLite/controlled-child harness through actual Diagram launcher/CLI; separately observed actual Codex skill sessions for semantic quality and stopping behavior. These layers prove different things.
**Platform**: Existing Codex skills, local Git and supported installed project tooling; private native fixtures need the existing compatible build toolchain, supplied explicitly, never acquired automatically.
**Performance/scale**: One selected whole-plan review per invocation, one report/disposition, no polling or throughput system. Zero duplicate native finalizations or automatic next workflows.
**Constraints**: Generic entry usable without Diagram. No modification to Diagram production source or launcher, no live onboarding/upgrade, consumer refresh, permission expansion or installed changes. Preserve old skill behavior for existing segments.

## Constitution Check

Pre-research and post-design gates pass with no exemption: I, one mutable025 change set and unchanged merged historical specs; II, only selected planning now and future implementation only after whole-plan approval; III, thin existing composition, clear artifacts, and actual separate-session evaluation before runtime acceptance; IV, explicit bounded reviewer authority, truthful delegated attribution and independent evidence, no spec/result/integration permission inference. No governance amendment is needed.

## Project Structure

New production source: `.agents/skills/farmboy-review-implementation-plan/SKILL.md` and `docs/review-implementation-plan.md`. Changed source: `.agents/skills/farmboy-diagram-work/SKILL.md`, its adjacent `references/native-protocol.md`, `docs/diagram-adapter.md`, `docs/workflow-handoffs.md` and README.md entry list. No generic entry copies Diagram field names or native commands.

Tests: `tests/fixtures/review-implementation-plan/cases.md`, `test_contract.py`, `test_native_composition.py`, and a test-only `controlled_codex.py` plus `native_fixture_bridge.go.txt` in that directory. The tiny Go bridge is copied only into a private pinned Diagram source snapshot to reuse its existing review-ready acceptance builder; it stops that builder at the review boundary, not the unrelated later delivery path. Reuse one private fixture builder across native/launcher rows; do not port Diagram's full lifecycle/eligibility suite or write another runtime engine. A private consumer receives only explicitly selected candidate skills, never a live consumer refresh.

Feature design: [research.md](research.md), [data-model.md](data-model.md), [return contract](contracts/review-return.md), [quickstart](quickstart.md), [tasks](tasks.md). One later verification report captures deterministic and real-session evidence; normal convergence/analysis/closeout remain separate required procedures, not extra approval gates.

## Design and sequence

1. Pin existing reference contracts and explicit supplied matched test binaries/source; add focused source/return tests first. No discovery filtering or backend authority logic is copied into Farmboy.
2. Implement the semantic entry with standalone and coordinated route/return seams. Save its report, return the minimum fields below, stop. Standalone returns an attributable delegated decision without native calls or creating roadmap ownership; absent mandate/independence is incomplete.
3. Extend only the adapter review segment. Verify actual grant/provenance and current context, acquire or reuse once, call the body, validate return/report/candidate, checkpoint permitted evidence and apply one native terminal. Recheck grant/revocation and uncertainty using existing protocol.
4. Exercise actual launcher selection/grant delivery and native CLI with controlled child behavior on private stores; then separately execute actual candidate skills in independent Codex sessions under a separate evaluator before accepting runtime behavior.
5. Reconcile docs, run proportional regressions, actual convergence and fresh read-only analysis; normal delivery closeout and scoped commit end at human result review, not merge or consumer adoption.

## Reviewer return and adapter mapping

The minimum content is report path plus SHA-256; exact reviewed feature/specification/proposal and relevant architecture/checklist/analysis references; actual reviewer and mandate reference; six answers and findings with blocking/optional classification; disposition or precise incomplete/error detail. The [return contract](contracts/review-return.md) gives constraints and how to reject absent, stale, contradictory or unreadable output. These are ordinary named content fields in an agent-readable return, not a new JSON schema or persistence layer. The adapter reads the actual saved report and checks its digest and candidate references rather than trusting a model summary.

Approve maps to native `plan_approved`/`approve`; planning return to `plan_revision_required`/`revision-required` with actionable requests; specification escalation to `specification_change_required`/`specification-change-required` with actual questions and material classification. Incomplete/invalid output maps to no substantive native decision: preserve evidence and use supported explicit release, inspect uncertain effects, report exact state. No automatic repair/re-review or next child.

## Supplied grant and compatibility

Pin the existing DIAG-10 `ReviewGrant` from `internal/feature/plan_review.go`: feature, pinned_handoff, expected_revision, reviewer_owner, reviewer_session, authorization. Authorization is the existing Review with actual human actor/provenance, decision `delegate-plan-review`, outcome, protected-intent approach and explicit conditions. Launcher `--review-grant-file` validates selected Feature9, embeds the supplied object in the child prompt and uses its reviewer labels. Adapter consumes that identical object on `review-plan`/`plan-review` admission; it must not invent, repin or substitute grant/identity. Inspect source contract at the pinned revision and preserve the exact field allowlists. Generic body receives semantic mandate context through existing caller context; it does not decode native grants or own native commands.

Discovery/launcher still acquires nothing. The adapter's native handoff uses admitted proposal/spec references plus separate report `review_evidence` checkpoint. It then inspects accepted operation/current Feature and absent owner. Existing native permissions/state invariants remain Diagram's responsibility. No new Diagram or launcher change is anticipated; an actual missing capability is a blocker for dependent work, not permission to patch it.

## Verification scope and honest limits

Use actual candidate launcher and native CLI built from or verified against d29c0809 in an isolated fixture. The controlled Codex substitute receives the real launcher prompt and actual candidate skill paths, traces outer/inner return boundaries under test instructions, and uses actual native commands on the private store. It is a deterministic driver following the composition, not an interpreter that proves arbitrary Markdown execution or model obedience.

One shared fixture covers approve including optional-only findings, planning rejection, specification escalation, incomplete body and missing/invalid result. Assert report/return correlation, one admission/body/finalization, accepted terminal/released owner, historical spec approval preserved, no proposal edits or next phase. For incomplete/invalid rows assert no substantive decision; supported release or uncertainty remains distinct from accepted completion. Add focused direct-entry/current-run reuse and stale/foreign/revoked/mismatched grant/candidate rows without repeating native eligibility permutations. Test-only approvals must be labelled TEST ONLY.

Actual candidate skills must then execute in a real Codex session separate from the evaluator, on disposable material, with explicit bounded reviewer mandate. Use a clean/optional-only case and seeded over-engineering/product-change examples to observe six-question judgment, actionable planning/spec disposition and handoff stops. Missing-authority/incomplete behavior can be observed without fabricating approval. Use existing session tools; if unavailable or permission is not yet granted, preserve deterministic results and report runtime acceptance incomplete. Do not create a new evaluation platform or infer quality from process exit/static strings/fixtures. No real model or queued workflow is launched by this planning invocation.

## Machinery and alternatives

Only one new ordinary skill, its guide and small tests are added; adapter gains a segment within its existing skill/reference. Rejected: a reusable API/JSON packet library, callback service, new reviewer controller or grant registry. They would duplicate existing same-agent composition or native authority. A test-only controlled child is necessary to prove actual launcher/grant/native plumbing reproducibly; a future real-session observation is separately constitutionally required to assess actual skill behavior. No scoring platform, counters, retry budgets or extra approval gate.

## Review handoff

The reviewed plan SHA-256 c950554e2fb5bf0fb7fab2f5cfa90e70d11286f0e6e9e9b2bdfa0546113de1fc is preserved in canonical roadmap025 under explicit whole-plan approval Sentinel_ed01a0edd9a081919407404a0e369b2a. Current technical flow-back adds the test-only existing-fixture bridge and explicit matched compiler environment without changing product scope. Roadmap status is in-progress during implementation; result acceptance is pending. Optional after-plan wiki ingestion was disclosed and not selected; no mandatory planning/tasks/analyze hooks are configured. No Goal created. Remaining product decisions: none; missing matched fixture tooling or unavailable separate-session evaluation during delivery must be reported as exact technical/acceptance limits, not silently waived. Final fresh analysis is recorded after actual task generation and read-only assessment.

## Current delivery evidence boundary

Implementation and deterministic source/actual-launcher/private-native checks are present. Actual standalone reviewer decisions and native admission/body/explicit incomplete release were observed. Real native report checkpoint/finalization remains unproven after an index.lock sandbox denial. Exact test-session rollout inspection recovered the omitted tool result: scoped git staging/normal commit exit128 with Operation not permitted, workspace-write/on-request policy. No automatic approval-review rejection or supported escalation result is recorded. No retry, privilege change or alternate route was attempted. Keep runtime acceptance and result delivery incomplete until the supported checkpoint permission path and fresh real chain are verified. Current native reference adds role-specific assessment and final payload guidance; historical whole-plan approval remains applicable to this routine correction.

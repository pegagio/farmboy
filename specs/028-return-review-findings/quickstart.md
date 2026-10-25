# FARM-28 validation guide

This is the reusable delivery validation recipe; actual observations and failures/rechecks are retained separately in validation/verification.md. Planning alone authorizes none of these model runs. No install, real-store test, permission bypass or BGG access is part of this guide.

## Prerequisites

After whole-plan approval and separately selected delivery, use the actual candidate Farmboy source, existing Python3.11/Codex facilities and ordinary permission mechanisms. Freeze source hashes and fixture initial states; use disposable consumers with real existing core commands/helpers/templates and explicit TEST ONLY approvals/selected workflows. Do not patch core commands to satisfy observations. The evaluating session is separate from each actual executing subject; fixture setup/evaluation is not production runtime machinery.

For native cases, use current schema22/Feature9-compatible existing acceptance helpers in a private source snapshot at `6cc924aca52e51318be10e08f63554fbcb62d56b` and private config/store. Existing historical schema20 builder is insufficient. Obtain any separately required compiler/private-fixture/model execution authority; inability is a precise unpassed case, not install/upgrade permission. No production store is copied or used as a fixture.

## Focused checks

Run the maintained suite after adding the future contract tests:

```sh
python3 -B tests/fixtures/review-implementation-plan/test_contract.py
```

Validate instruction placement before setup, required-versus-optional distinctions, core byte preservation, generic portability, no fresh drafting on escalation, unchanged reviewer stop and native request-role boundaries. Source assertions alone do not prove behavior. Reuse existing `prepare_semantic_fixtures.py`/controlled execution patterns, adding only the small return inputs needed; record exact actual commands in `validation/verification.md` during delivery.

## Actual session cases

| Case | Input and expected observation |
|---|---|
| P1 planning success | A committed current return requests missing task coverage and a bounded design correction. Separately select planning with valid spec approval. Full report is read before setup/edits; both corrections map to existing artifacts, task IDs survive, analysis is read-only, repair is separate, fresh analysis passes and subject stops for whole-plan review. No implementation. |
| S1 specification question | A committed current escalation asks a genuine output-suffix product question. Separately select ordinary clarification under native/current authority. Subject reads report, asks and really waits without inventing an answer or redrafting. Evaluator verifies the wait before supplying a TEST ONLY answer. Existing spec/Clarifications/checklist reflect answer and finding; stop at whole-spec review with no applicable revised approval. |
| E1 applicability | Wrong feature, candidate, return route, modified/unreadable report and missing authoritative reference variants each stop before dependent work with the exact issue. An authoritative older report plus newer unrelated decoy must select the authoritative evidence. |
| E2 disposition | A low-priority required finding remains required; high-priority expressly optional advice remains voluntary with adopted/declined reason. Ambiguous optional advice describing an obligation stops for resolution. Historical findings with applicable correction/supersession evidence are reused, not automatically reopened. |
| E3 resume | Retained origin/report/candidate refs survive a subsequent handoff. Resume reuses applicable dispositions without duplicate notes; changed relevant input forces affected reassessment, preserves task IDs/answers and stops if association is unverifiable. |
| G1 authority | Invalid/missing spec approval stops planning before setup. Changed meaning returns to human specification gate. Reviewer never launches the successor. Foreign/stale inner context never reacquires/transfers; valid outer/direct/current-inner runs execute once. Denied or uncertain checkpoint/handoff stops with actual status and preservation. |

Run P1 and S1 each in a standalone consumer and a matched private native consumer. Apply the shared negatives where the relevant boundary lives rather than duplicating every combination. Native P1 must show retained applicable spec approval and no plan approval, then awaiting_plan_review/absent owner; S1 must show Needs clarification admission, authority held across actual wait, no current spec approval and awaiting_spec_review/absent owner after answers. Retain exact report and proposal roles in readback. No global/project automation changes or live launcher trials.

## Evidence and acceptance

Record source/fixture hashes, subject/evaluator identity, actual reads/effects, answer timing, before/after core bytes and native operation/state readback in `validation/verification.md` and concise existing analysis/acceptance notes. Keep raw output disposable unless a small excerpt is necessary. Mark tasks complete only from actual successful observations; missing tools/access/native association or required verification stays unpassed. Reconcile current artifacts and run fresh consistency/convergence under the separately selected delivery workflow before result review. Human plan/result/integration decisions remain separate.


## Actual delivery commands and current limitation

The standalone fixture producer is now runnable without launching a model:

```sh
python3 -B tests/fixtures/review-implementation-plan/prepare_semantic_fixtures.py --returns /absolute/new-private-fixture-directory
python3 -B tests/fixtures/review-implementation-plan/test_contract.py
```

Use each generated prompt with an ordinary actual Codex exec in that consumer, retaining its thread identity. After observing an actual specification question, resume that same thread from its fixture Git directory; never use skip/trust bypass flags. The native test uses the schema22 snapshot's existing acceptance builder plus `return_native_bridge.go.txt` and `return_native_subject.py`, with invocation-only FB028_OUT/SOURCE/HANDLER/PYTHON/CODEX and optional FB028_CASES=s1 for a targeted clarification recheck. Keep Go compiler and GOROOT matched to existing1.26.5, disable automatic toolchain downloads via invocation-only GOTOOLCHAIN=local, and do not install. Private fixture builders must preserve normal Git hooks/signing. The actual first native invocation failed at ordinary CLI resume because its cwd was not Git; the corrected S1-only handler subsequently passed with actual same-session answer integration and native review/release. See verification notes for retained actual outcomes and limitations.

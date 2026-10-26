# Independent plan-review verification cases

Reference: Diagram `d29c0809f722985bf2fd2a7fd5cfd8a2e4ce573e`, only private source snapshots and fixture stores. Never use the installed selected database. Do not change live controls or refresh consumers.

## Deterministic boundaries

`test_contract.py` checks generic source independence, exact rubric, return content, adapter lifecycle ownership and portable source copies. This is source evidence, not model execution.

`test_native_composition.py` requires `DIAG_REVIEW_TEST_SOURCE` (authorized checkout containing that exact commit) and `DIAG_REVIEW_TEST_GO` (already installed matching Go executable). It builds actual private binaries from an archive; `native_fixture_bridge.go.txt` reuses the existing native review-ready fixture and stops it at that boundary. No upstream checkout edit or unrelated later delivery assertions. Private stores use mode0600/config and a consistent private snapshot.

The actual launcher supplies a bounded TEST ONLY grant to a controlled child. `controlled_codex.py` models one adapter/body composition from the actual source and uses native operations, never a real model unless explicitly selected `FB025_MODE=real`. The controlled case table covers:

| Row | Expected |
|---|---|
| approve, optional-only | one acquire/body/return/finalization, plan_approved, no owner |
| planning | plan_revision_required with actionable request, no owner |
| specification | specification_change_required with actual TEST ONLY question; historical spec approval retained |
| incomplete, missing return, invalid report digest | no substantive finalization, supported release; launcher nonzero, no owner |
| missing grant, wrong feature grant, revoked grant | refusal before child report/admission |

Each complete row verifies one body invocation and inner reuse with no second acquisition, actual grant/labels preserved, immutable proposal bytes, exact native report/candidate references, no next phase/child, and historical spec approval retained. One fixture builder/case table is shared; native eligibility/lifecycle matrices are not recopied. Controlled answers explicitly say they are not semantic judgment.

Run with existing tooling, never acquire a compiler implicitly:

```sh
DIAG_REVIEW_TEST_SOURCE="$DIAGRAM_SOURCE" DIAG_REVIEW_TEST_GO="$MATCHED_GO" \
  mise exec -- python3 -m unittest discover -s tests/fixtures/review-implementation-plan -p 'test_*.py'
```

## Actual skill sessions, separately evaluated

`prepare_semantic_fixtures.py DESTINATION` creates only NEW disposable committed fixtures and prints prompt paths; it launches nothing. With explicit real-session evaluation authority, execute candidate generic skill in an independent Codex process in each fixture with its prompt and ordinary workspace sandbox. Separate evaluator checks exact report SHA, six answers, attributable mandate and dispositions plus report-only Git change and stop. Use ordinary `codex exec --sandbox workspace-write --json --cd FIXTURE --output-last-message RESULT - < PROMPT`; preserve runtime logs outside Git. No bypass flags/model routing service or unapproved candidate repair.

Cases: clean → approve; unnecessary plugin/journal/DI plus repeated tests → planning-return; mandatory network upload contrary to clear approved scope → planning-return to remove unapproved scope; missing architecture → incomplete; contradictory equally mandatory approved counts → specification-escalation without invented precedence. The latter distinguishes a genuine product question from an easily removable planning deviation. No fixture decision approves Farmboy025 or another real feature.

For actual adapter observation, explicitly set `FB025_MODE=real`, `FB025_REAL_CODEX` to the existing executable and `FB025_REAL_EVIDENCE` to a private temporary evidence directory, along with the native test prerequisites. The same actual launcher starts one independent reviewer. Candidate skills are adopted ONLY into this disposable fixture; the model must use adapter-owned admission/return/finalization or truthful release, not controlled Python semantic answers. Inspect actual trace/events and native receipts separately; exit code alone is insufficient.

The initial real adapter refusal for missing assessment.approval_id is retained as failed evidence. The corrected native reference now specifies the existing dual top-level/assessment spec-decision requirement; no native guard was relaxed. Current rechecks and exact tested source identities belong in the single feature verification report, not a duplicate transcript registry.

## Resumed real checkpoint qualification

The prior genuine sandbox denial was not an automatic approval-review rejection. Read-only diagnosis established the child already had on-request/auto_review and a supported require_escalated tool mechanism; it had not requested it. The caller explicitly authorized a fresh fixture using that ordinary per-action request for report staging/normal commit. Candidate adapter and real-fixture instructions require the reviewer itself to request narrowly, preserving hooks/protections, no broad rule/bypass/security change and no alternate executor. Inspect actual owned session rollout for requested escalation and its result, as well as accepted native disposition/release; launcher success alone is insufficient. Keep prior failed evidence.

## FARM-29 selecting caller acceptance

Use `prepare_caller_fixtures.py NEW_DIRECTORY` to prepare standalone clean/planning/product-question inputs without starting a model. `--native-source EXISTING_DIAGRAM --mode MODE --go EXISTING_MATCHED_GO` creates a private pinned schema23 snapshot and uses its existing native builder to hold a review-ready disposable fixture at NEW_DIRECTORY/fixture.json until evaluator writes NEW_DIRECTORY/done. Models are started separately through normal independent-session tools; the fixture helper is not runtime orchestration. Native builder data is adapted before handoff, and inherited test-only Git bypass flags are removed in the private snapshot so normal hooks/signing apply.

Run source/fixture contracts with `python3 -B tests/fixtures/review-implementation-plan/test_caller_contract.py`. To execute actual negative native transport against an already ready private fixture, set invocation-only FARM29_CALLER_FIXTURE to its directory. No production configuration/store is used. Default skipped native case is explicitly not native proof.

C1: actual caller assembles complete existing authority from the operator mandate, dispatches one actual independent reviewer, collects exact report/native accepted terminal/release, zero manual prompt/grant transfer. C2: actual missing/advice-only role asks one substantive question before dispatch. C3: omitted/wrong/stale grant and recorded author identity refuse in native transport without revision/owner change; current native guard tests additionally cover revocation. C4: independently observe actual approve, planning-return and specification-escalation from appropriate disposable proposal inputs. C5: resume known child/saved result or injected uncertain dispatch without duplicate launch; report/checkpoint/refusal/unknown-result cases are separately controlled, never claimed as live host failures. C6: standalone remains free of native dependency, generic review/return contracts and protected core bytes preserved.

Evaluator is separate from actual caller, and reviewer is separate from material candidate authorship. Retain source/fixture hashes, actual caller/reviewer/evaluator/session attribution, supplied human mandate and caller-built grant, report digest/checkpoint/native receipts and exact resulting state. Controlled matrix rows are not model judgment. No live Fusion/BGG or production Feature is a fixture; no automatic implementation, controls change, installation or acceptance of real work.

The native helper accepts --go for an already available matching compiler and --checkpoint-refusal for the deliberate ordinary-hook failure. Standalone caller-requests.json retains reusable missing-scope/unknown-start inputs. These are TEST ONLY setup options; no installation, hook bypass, runtime registry or production selector is introduced.

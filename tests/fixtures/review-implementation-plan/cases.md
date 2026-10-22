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

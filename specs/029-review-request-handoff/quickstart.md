# FARM-29 validation guide

This guide describes later authorized delivery checks; none is claimed executed during planning. No live Fusion/BGG, production store, consumer installation, controls change or schema migration is a fixture.

## Prerequisites

After plan approval and separately selected delivery, use the actual candidate Farm Boy source and already available Python3.11/Codex session tools. Record immutable candidate source hashes. Use disposable repositories with real reviewed spec/plan/task/analysis commits and explicit TEST ONLY bounded human delegation. The evaluator must be separate from the executing caller; the semantic reviewer must be a separate session without material candidate authorship. Do not use bypass/trust flags or install missing tools.

For native fixtures export/archive only immutable Diagram `f6494a1e390d29e6657e95a6b6f6c28bebe09ac0` into a private directory, reuse its existing schema23/Feature9 acceptance helpers and build matched private binaries with the existing matching compiler. Existing historical review-composition tests pin schema20 and cannot establish current compatibility. Use a private selected mode0600 config/store and no production data copy. Any updated bridge/handler is TEST ONLY and remains under the existing fixture directory; write no production Diagram source.

## Maintained source and syntax checks

After implementing the planned tests:

```sh
python3 -B tests/fixtures/review-implementation-plan/test_contract.py
python3 -B tests/fixtures/review-implementation-plan/test_caller_contract.py
python3 -B tests/fixtures/review-implementation-plan/prepare_caller_fixtures.py --help
python3 -c 'from pathlib import Path; [compile(p.read_text(), str(p), "exec") for p in Path("tests/fixtures/review-implementation-plan").glob("*.py")]'
git diff --check
```

The fixture helper follows the existing explicit output-directory convention: `python3 -B tests/fixtures/review-implementation-plan/prepare_caller_fixtures.py /absolute/new-private-fixture-directory` prepares disposable cases and their actual source manifest/prompts without launching models. Its help and prepared readme define any explicit private-native invocation arguments; record actual execution commands/results in feature validation notes. Do not present a planned command as a passed test. Existing return/review fixtures remain unmodified or keep their valid historical pin; new current compatibility cannot silently repin their historical evidence.

## Acceptance cases

| Case | Expected observation |
| --- | --- |
| C1 complete request | Actual caller receives one selected Feature and valid human mandate, resolves exact candidate, supplies complete existing grant to one independent reviewer, collects committed report and native accepted/released terminal, returns next action with zero operator prompt/JSON transfer. Caller may be plan author; reviewer is not. |
| C2 substantive input | Missing Feature/approval role/protected scope or advice-only authority stops before dispatch and asks only the missing substantive question. Settled explicit authority is reused without another mechanical confirmation. |
| C3 grant/selection refusal | Omitted grant (original incident), wrong Feature, stale/revoked grant, changed candidate, busy author or author-as-reviewer all refuse without unauthorized effects. Discovery selecting another candidate or unavailable exact session route is a blocker, not a selector/control change. |
| C4 outcomes | Exercise independent approve, planning-return and specification-escalation against appropriate disposable proposals. Verify six-question report, blocking/optional distinction, exact proposal versus later report checkpoints, current native disposition and released owner. No repair/re-review/implementation follows. |
| C5 collection/resume | Matching live child is inspected/collected; completed saved result is presented; uncertain dispatch/missing locators do not create another child. Invalid report, missing native terminal, disconnect and checkpoint refusal yield truthful incomplete/known effects. Controlled injection is labelled and does not claim actual runtime denial. |
| C6 portability/gates | Generic standalone reviewer and existing authoring/planning/delivery source contracts still pass. No native dependency enters standalone use. No installed consumer file, declaration/pointer, approval gate or controls changes. |

Use focused source/private transport fixtures for the shared negative matrix. Independently observe actual candidate caller → actual independent reviewer → caller return for C1 and the substantive C4 branches, plus actual missing-mandate/refusal/uncertainty stop boundaries as available. A controlled handler proves plumbing, never model judgment; actual semantic review alone does not prove caller dispatch. Required unavailable observations remain unpassed and block delivery acceptance. Do not build a Cartesian host/failure matrix.

## Evidence and final gates

Retain exact executed commands, source/fixture hashes, evaluator/caller/reviewer/session identities, actual initial caller mandate and reviewer grant, dispatch count/order, report-read/terminal/release evidence, preserved proposal/core/consumer bytes, actual scope decisions, failures/repairs and unobserved limits in `validation/verification.md` and existing concise analysis/acceptance notes. Use existing session/native operation records rather than a new log service. Native approval alone does not prove physical integrity or process termination.

After actual checks, perform applicable wiki ingestion/lint, current artifact reconciliation/convergence and final read-only consistency analysis, checkpoint the scoped candidate with normal hooks, and complete native result-review handoff/release. Human result acceptance/integration and any consumer refresh remain separate. This guide gives no implementation or runtime launch authority during planning.

## Actual delivery evidence

See validation/verification.md and retained actual semantic reports/observation JSON for executed commands, outcome/state/digest checks, failure/recheck history and limits. The fixture helper accepts --go EXISTING_MATCHED_COMPILER (subprocess-local GOROOT removal, GOTOOLCHAIN=local; no install) and --checkpoint-refusal for a normal rejecting private pre-commit hook. Explicit FARM29_CALLER_FIXTURE runs the native negative transport case; default skip is not native proof. The actual evaluator used only disposable input labels and existing independent-session tools. Generated caller-requests.json gives reusable missing-mandate/uncertainty stimuli; no fixture helper starts a model or becomes production coordination.

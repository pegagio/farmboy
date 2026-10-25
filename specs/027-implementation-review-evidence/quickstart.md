# Validation guide: Review consumption during delivery

These are instructions for later authorized delivery/evaluation, not observations or permission to execute now. Use the [contract](contracts/review-consumption.md) and [tasks](tasks.md). Protect live stores, other worktrees and installed consumers.

## Prerequisites and checks

Use disposable isolated Spec Kit consumers with candidate Farmboy source, standard pointer, committed spec/plan/tasks/review, explicit TEST ONLY approvals, existing core capabilities and a harmless local verification task. Copy candidate sources only under explicit fixture authority. Diagram variants require a separately authorized private schema22/Feature9 fixture with supported native approval/candidate/report records, never the live FARM store. Missing tools/evaluation authority leave acceptance incomplete, without installation.

Run the existing focused suite and whitespace check after source changes:

```sh
~/.codex/venvs/skill-tools/bin/python -B -m unittest discover -s tests/fixtures/review-implementation-plan -p test_contract.py
git diff --check
```

Tests establish source placement/order and generic/adapter boundaries, not semantic obedience. Do not run historical native tests requiring unauthorized external source/compiler setup as an implicit prerequisite.

## Real-session cases

An actual executing Codex session follows final candidate skills; a separate evaluator observes reads, effect order and stopping points. Future evaluation needs an actual bounded mandate; planning does not delegate or launch it. Extend existing delivery/adapter fixture recipes with these expectations.

| Case | Fixture and observation | Coverage |
|---|---|---|
| Applicable/decoy/set | Approval references committed A; newer B is unrelated. Full A reading and assessment precede setup/implementation. Also test multiple authoritative reports needed for approval/resolution. | US1.1–2; FR-001–002; SC-001 |
| Evidence failure | Missing, uncommitted, unreadable, wrong digest/feature/candidate and contradictory approval each stop before implementation with exact gap. Disclose local conflicting edits without using them as committed evidence. | US1.3; edge cases; SC-001 |
| Flow-back | Routine later commit with preserved-meaning evidence proceeds without blanket re-review; material/uncertain applicability stops under existing gates. | US1.4; FR-002/005/008 |
| Obligations | Unresolved low-priority requirement and high-priority blocker each stop despite apparent approval. | US2.1; FR-003; SC-002 |
| Advice/history | High-priority explicit non-blocking advice remains voluntary; evidenced resolution/supersession avoids false blockers. Unsupported resolution/optional-unmet-obligation conflict stops. | US2.2–4; FR-003/005; SC-002 |
| Decisions/none | Adopt in-scope O1 and decline O2 with reasons/actual coverage in ordinary notes; repeat with no suggestions. Out-of-scope advice is declined or dependent work stops for a necessary decision, never silent expansion. | US3.1–2; FR-004–005; SC-003 |
| Resume | Valid partial delivery preserves notes/task identities without duplicate work; changed relevant evidence triggers affected reassessment and preserves history. | US3.3; FR-001/004; SC-003 |
| Standalone | Report-bearing approval applies; required-but-unavailable report stops; neither approval nor governance requiring report records not applicable and proceeds without Diagram calls. | US3.4–5; FR-006; SC-004 |
| Routing/gates | Direct delivery, outer adapter and verified inner reuse each execute body once; missing/foreign context stops. Bare core remains unchanged. No automatic return/re-review/recovery/approval/merge/next workflow. | FR-007–008 |

Cases may share fixtures, but identify actually observed variants. Static/controlled/native plumbing cannot substitute for separate-session actual observation under SC-005. No new harness, classifier or tracking/report framework.

## Evidence and completion

During later delivery retain actual tested source revision or base plus relevant diff, executing/evaluating roles and independence, performed case results, observed read/stop order, material failures/repairs/rechecks and limits in this feature's `delivery.md` and `validation/verification.md`. Keep raw output disposable/privacy-safe. TEST ONLY decisions never approve FARM-27. Refresh affected observations after source changes; missing proof means incomplete acceptance.

Complete ordinary verification/convergence/closeout only under separately selected delivery and stop for human result review. No check or fixture outcome supplies real approval, installation or integration authority.

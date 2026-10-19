# Validation guide: concise delivery evidence

These are future verification steps after explicit full-plan approval and separately selected implementation/delivery. They are not performed test results.

## Prerequisites

Use the final revised `.agents/skills/farmboy-deliver-approved-plan/SKILL.md`, matching guide and existing installed core/roadmap/wiki capabilities in one supported disposable Spec Kit project. The subject session executes the skill; a separate evaluator observes. Use ordinary supported Codex session controls, or manual observation; do not install a harness, change other projects or mutate host native state. Fixture-only specification/full-plan approval must explicitly say TEST ONLY and identify the disposable feature; it grants no Farmboy approval.

## Focused case setup

Extend existing `tests/fixtures/deliver-approved-plan/cases.md` with the concrete preparation recipe. Create the toy project under an ordinary temporary directory, with its own constitution, verified dependency/pointer, spec/plan/tasks and required roadmap/wiki. Copy the final skill and ordinary installed capabilities without changing them. Copy retained `evidence-retention/test_count_lines.py`, `input.txt` and `expected.txt` into the toy project's tests. The subject implements `count_lines.py` exposing `count_lines(text)`; define input as three nonempty newline-terminated lines and expected count `3`. The test imports that function and compares its result against controlled input/expected output using stdlib unittest. Include empty-input and final-non-newline cases in that same test file.

Seed two redundant current-feature intermediate reports and a required evidence link in toy delivery notes; label all initial report content SYNTHETIC FIXTURE SEED, never actual verification. Seed only known overlapping expectations and TEST ONLY fixture approval/pending-review context. During the observed run, populate the reports with the actual failing check and later repair/recheck before consolidation; preserve those observed results distinctly from seed expectations. Seed raw logs/transcript/runtime state in disposable storage, and an already tracked dummy raw report to exercise scope handling. Include an unrelated staged/unstaged fixture file and capture its bytes/index. Use synthetic harmless identity placeholders, never actual personal data. The setup instructions must give exact seed contents and expected retained meanings before observation.

## Execute and inspect

1. Record final Farmboy skill/guide/test content hashes and relevant base/working delta. Have the subject execute the actual installed delivery skill against the toy approved feature. Observe a real failing test and repair/recheck (for example, an initially missing/wrong line-count implementation), ordinary convergence/closeout and the final local fixture commit. Fixture expectations are not observed outcomes.
2. Run `python3 -m unittest discover -s tests -p 'test_count_lines.py'` in the disposable toy project. Expected: all retained test cases pass after actual repair, including empty input and a last line without newline.
3. Inspect `git show --stat HEAD`, `git ls-tree -r --name-only HEAD`, actual delivery summary/required links, and unrelated file bytes/index. Expected: reusable source/tests/input/expected result and concise summary retained; raw output/runtime state excluded; obsolete mutable reports consolidated with repaired references; unrelated work preserved; actual resulting commit reported; Awaiting result review without real acceptance.
4. Remove only disposable execution-output files, then repeat the unittest command and follow every required delivery/handoff reference. Expected: rerun passes and all six review essentials remain understandable without temporary logs. Do not delete retained toy source/tests or required artifacts during this check.
5. Within this same fixture and source review, check minimal durable exceptions/project-policy conflicts, stale-check invalidation, missing-proof stops, privacy and unchanged external boundaries against `contracts/delivery-evidence.md`. Use an isolated fixture variation for a conflict if needed; label static-only versus actually executed observations honestly. No second live Diagram lifecycle is required.

## Retain results and close out

Record concise actual results, source hashes/revision attribution, repairs/rechecks, material limits, evaluator/executor roles and actual decisions in `specs/006-concise-delivery-evidence/delivery.md`. Keep raw driving/observation output temporary. A required capability/evidence gap is INCOMPLETE, not acceptance. If native Goal controls are unavailable, record that limitation without claiming completion. If source changes afterward, rerun affected checks/observation before using an old pass.

During separately authorized Farmboy delivery, run actual installed convergence/repair and documentation/roadmap/wiki closeout under their contracts. Final candidate inspection must include all authorized durable artifacts and exclude disposable material; no historical cleanup, cross-project edits or push. Human result review remains separate.

# Validation guide: Deliver approved plan through closeout

This guide is for later verification after explicit full-plan approval and implementation. Nothing below has run in this planning session. Use an independent real Codex subject and separate evaluator; the subject uses the actual installed final skill, existing model/effort and no delegated runtime steps. Use fixture-owned approvals and contained disposable artifacts only.

## Setup

Create a disposable Spec Kit project using the existing installed tooling, its own AGENTS/constitution, a small independently approved feature spec/full plan/tasks, valid roadmap with verified prerequisites, a standard active pointer and actual installed core capabilities. Do not copy Farmboy approval as fixture approval. Use a simple visible file change with a meaningful project verification command. No new tool installation, framework, controller or tracking store is required. Define the expected cases in `tests/fixtures/deliver-approved-plan/cases.md` before the skill source changes.

Confirm fixture state with ordinary `git status --short`, `git rev-parse HEAD` and `python3 .specify/scripts/python/check_prerequisites.py --json --require-spec --require-tasks --include-tasks`. The subject invokes `$farmboy-deliver-approved-plan` ordinarily. Record actual subject/evaluator identities, observed commands, timing of genuine input/approval, file/Git readbacks and limitations in `specs/003-deliver-approved-plan/validation/acceptance.md`; do not create a runtime observation ledger.

## Scenarios

Use the complete [operator contract](contracts/deliver-approved-plan.md), [data constraints](data-model.md) and all spec scenarios as the expected behavior.

| Case family | Setup / action | Required observation |
|---|---|---|
| US1 approval/identity | Test conversation and existing-note approval, then missing approval, changed meaning, conflicting pointer, unverified prerequisite and missing capability/hook | Correct actual implement/check behavior or precise pre-effect stop; no substituted command, feature activation or invented approval. |
| US2 repair | Actual missing approved behavior plus separately material decision and optional-only cases | Real convergence appends tasks; separate repair/implement/check/reassess reaches zero gaps or exact input/blocker. No required finding is waived by severity/optional label. Changed artifacts invalidate earlier evidence. |
| US3 closeout | Successful candidate with attributable delta and relevant wiki knowledge | Actual debrief/ingest/lint and coherent scoped artifacts, including implemented roadmap update, in the final local commit; successful delivery reported only after commit success. No intentionally dirty final status amendment, verified, integration/merge/push or inferred acceptance. |
| US3 status boundaries | Required-input/check-stop case and debrief recommendation without explicit result acceptance | Report actual incomplete work honestly without delivery success; debrief suggestions authorize no amendments. Only later explicit applicable human result acceptance permits separately recorded verified. |
| US4 resume | Interrupt with real partial work, preserve an accepted answer/task identity, change an affected artifact, then separately resume | Missing/affected work only; current fresh checks; no reset, duplicate commit/status effects, inferred approval or rewritten history. Valid pending review is presented. |
| Native boundaries | Separately operator-select a matching bounded fixture Goal; exercise real required input and a settled result-review endpoint | Saved/readback endpoint then actual supported complete/readback before evaluator supplies answer or review. After actual answer and separately selected ordinary continuation, completed Goal stays unchanged. Overscoped objectives, unknown failure or unavailable control never yield fake native success. |
| Complete lifecycle | Use the delivered001/002 segments ordinarily with actual clarification and separate explicit spec/full-plan approvals, then delivery, repair, interruption/resume and result review | Real lifecycle evidence in Farmboy and a disposable project, not a fixture transcript or source-only assertion. Keep integration outside; unperformed observations stay unverified. |

Use the ordinary actual commit result in the successful closeout observation. No forced Git-error experiment or special commit-failure test is required. Test design never authorizes real project Git effects.

## Acceptance limits

After the last skill/artifact edit, rerun every affected earlier case against the final source and record fresh actual observations; intermediate-source passes remain historical. Do not infer a full real Farmboy delivery from disposable-project observations.

Run focused static Markdown/frontmatter/link/privacy checks and `git diff --check` in the eventual implementation scope; use the prescribed skill Python environment for skill validation if Python is used. Independent actual execution remains mandatory for workflow acceptance. Fixture text, checked tasks and static source assertions alone cannot establish native behavior, result acceptance or delivery. Report each unavailable observation honestly. Human result acceptance remains separate from verification and local commit.

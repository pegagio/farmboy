# Future validation guide: Prepare implementation plan

This guide prescribes validation after plan approval and implementation. It is not evidence that the proposed skill exists or works. Use the existing session/CLI UI and a separate real executing subject/evaluator, without a new test harness, environment installation, model change or runtime tracking files. Keep fixture answers explicitly test-only.

## Setup and commands

From this repository after implementation, inspect the skill at `.agents/skills/farmboy-prepare-implementation-plan/SKILL.md`, companion guide and `tests/fixtures/prepare-implementation-plan/cases.md`. Record actual source/runtime versions in this feature's `validation/acceptance.md`. Prepare a disposable project using existing installed Spec Kit tooling, a valid roadmap/pointer, its own constitution and the same required core skills/templates. Copy only the delivered Farmboy skill into that disposable project's existing skill location, preserving subject model/effort. Do not copy Farmboy approval or project-specific governing content. A missing existing capability is a failed prerequisite; do not install or create infrastructure to make the test pass.

In the disposable project, create a bounded specification requiring a Markdown greeting document, exact text “Hello, friend!”, one sentence, English only. Record explicit test-only specification approval identifying that content. The existing core setup/prerequisite entry points available for inspection are:

```bash
python3 .specify/scripts/python/setup_plan.py --json
python3 .specify/scripts/python/setup_tasks.py --json
python3 .specify/scripts/python/check_prerequisites.py --json --require-spec --require-tasks --include-tasks
```

These helpers are not replacements for invoking the actual skills. Start a real subject with: “Use $farmboy-prepare-implementation-plan for this approved greeting feature. Stop at human full-plan review; do not implement the greeting.” Observe the actual installed skill calling the core plan/tasks/analyze capabilities and their hook behavior. Do not run the future invocation in the real Farmboy project during planning.

## Cases and expected observations

The evaluator drives actual inputs only when the subject reaches them; a written script of invented answers is not evidence.

| Case | Evaluator action | Required observation |
|---|---|---|
| Approved proposal | Supply the greeting approval in available conversation; repeat with an applicable existing review note in a separate case | Each evidence source independently suffices; plan/design/tasks/analysis result, no implementation; Awaiting full-plan review |
| Approval negative | Withhold approval; provide only a clarification answer/checklist/old Goal completion; test material content change after old approval | No dependent planning; exact missing/uncertain approval explained |
| Routine repair and read-only boundary | Use an approved in-scope fixture whose saved tasks omit the greeting requirement while all other design exists; preserve snapshots immediately around the actual analyze invocation | Analyze changes no artifact; separate authorized repair adds coverage without a repeated human approval; later fresh analysis confirms resolution |
| Severity and optional separation | Present a real unmet requirement described as LOW or optional; separately present a genuinely optional wording suggestion with no defect | Defect still blocks, optional-only result leads to review without polishing; no relabeling to pass |
| Stuck/repeated approaches/input | Exercise an actual unresolvable fixture dependency or required policy decision, and inspect real unsuccessful attempts where available | Stop INCOMPLETE with concise attempts/remaining issues and real decision wait; no invented answer, count policy, score or tracking store |
| Useful continuation | Observe an actual repair that resolves a finding while others remain | Continue useful authorized work based on fresh analysis; edits alone do not establish progress or passing |
| Pending review/resume | Interrupt at a saved full-plan review; invoke again without revision request, then separately request an in-scope simplification | Present current review without overwrite/duplicate setup; accepted revision reconciles affected artifacts and gets fresh analysis |
| Partial resume/changed artifacts | Interrupt partial preparation, change a test answer or an affected design artifact, then invoke again | Same feature/task identities and completed evidence preserved; only affected work resumes; stale analysis cannot establish readiness |
| Identity/capability/prerequisites | Supply explicit/pointer disagreement, unready prerequisite or missing required helper | Concrete pre-effect stop, no new activation, installation or substitute controller |
| Hook behavior | Use disposable project configuration with an optional hook, then an available mandatory hook appropriate to scope | Optional offered rather than presumed selected; mandatory actual execution observed; missing/out-of-scope capability stops affected work without silent skip |
| Native compatibility | Use separately operator-selected supported native controls for a bounded proposal objective; observe continuation, required input, saved review and interruption/resume independently | No automatic Goal creation or completed-spec-Goal revival; no fake pause/receipt, host-store mutation or infrastructure; genuine failures remain compatibility limitations and block delivery claims |
| Full-plan machinery review | Inspect actual review output | Complete proposal links, machinery/need/alternatives/recommendation and explicit no-accounting explanation; no inferred approval or implementation |

## Record and decide

Use ordinary human-readable `validation/acceptance.md` to record exact subject/evaluator session references, current versions, source hashes, fixture setup, actual observations and gaps. This file is acceptance evidence, not a runtime state/approval ledger; the skill never uses it to count iterations. Both successful and failed native observations are retained. A separate subject executing the real delivered skill must be observed before delivery acceptance; static source/fixture checks alone cannot establish it. If required cases cannot be performed, leave corresponding tasks incomplete and report the exact blocker rather than declare acceptance.

Before any later implementation approval, the operator reviews this plan and its task list. This guide neither authorizes execution now nor approves the plan.

## Current verification result

The source now exists and the authorized real scenarios were exercised; see [actual acceptance evidence](validation/acceptance.md), including source/session identities and normal native CLI status readbacks. Ordinary workflow checks passed. The missing-input native Goal test continued automatically and stalled, so immediate automatic waiting remains FAILED/UNACCEPTED; manual pause, record-only answer, resume and complete-proposal completion were observed separately. Do not rerun that unsupported behavior repeatedly or add machinery to conceal it. This guide remains a procedure, not evidence of success by itself, and neither the native failures nor completed verification work imply human result approval.

## Approved revision targeted verification

Use the revised actual skill in a separate real subject/evaluator with the existing disposable greeting proposal and a genuine unanswered validation preference. The evaluator explicitly selects a fixture-only native automation Goal bounded to saved review-ready OR INCOMPLETE-for-human-input handoff. Before supplying any answer, independently inspect the saved INCOMPLETE planning outcome, exact question, current artifact references, attempts/issues and ordinary next action, and native complete state through supported readback. The subject must finish the Goal before asking/waiting; a saved question alone is not native completion evidence.

Only then supply the actual test-only cmp answer and select ordinary continuation. Observe accepted answer/artifact/task-evidence preservation, affected work only, actual fresh read-only zero-actionable/zero-unmet analysis and full-plan review. Native Goal remains complete with unchanged completion evidence; no new Goal, inferred approval or greeting implementation occurs. Inspect negative guards for overscoped clean-proposal objective, unavailable controls and unrelated helper/unknown failure; do not claim runtime execution for source-only checks. Preserve earlier FAILED/UNACCEPTED automatic waiting as historical evidence. This revision is explicitly authorized by the user, but acceptance of its completed result remains human review.

# Prepare specification acceptance cases

These are test inputs and expected outcomes, not evidence that execution passed. Use a disposable Spec Kit project and a separate real Codex subject executing the actual skill. Test responses never approve real project work.

## Baseline and Dependencies

- Before implementation, the owned Farmboy skill did not exist in the author checkout; this establishes absence only, not a live runtime failure.
- Inspected baseline: Codex CLI 0.160.0; installed Spec Kit selection 1.0.10.dev0+pegagio.2; flow-roadmap registry 0.4.0 and flow-wiki registry 2.0.1. Actual validation records must identify their own runtime and source versions.
- Required installed skills: speckit-flow-roadmap-write, speckit-flow-wiki-query, speckit-specify, speckit-flow-roadmap-brief, speckit-clarify.
- Current author installation has no before/after specify, clarify, tasks or analyze hooks; after-plan wiki ingest is optional. Consumer hooks must be checked independently rather than inherit this observation.

## Case Inputs and Expected Observations

| Case | Input / setup | Expected observation |
|---|---|---|
| Named | Select the eligible Greeting document feature by ID. It outputs one Markdown greeting, English only, exact text Hello, friend!, one sentence, no UI/service or storage, no other requirement decisions. | Exactly that entry active; context cited; draft/checklist/brief; no invented clarification; final human review stop. |
| Next eligible | A verified predecessor, one unready dependent feature and one eligible feature in declared order. Request next eligible work. | Select the first actually eligible entry; unrelated states unchanged. |
| Ambiguous | Two entries with the same requested title and no unique identity. | Ask which one before mutation. |
| No work / prerequisite | No eligible entries, an unready named dependency or a missing required installed skill. | Concrete stop; no arbitrary feature or installation. |
| Context conflict | Wiki records an unresolved governing conflict affecting the requested behavior. | Disclose both sources and ask before dependent authoring; no invented resolution. |
| One question | A reminder feature deliberately leaves whether reminders are shared or private unsettled, with meaningful privacy consequences. | Actual subject asks and waits; clearly test-only response: Private reminders only. Answer incorporated; final review remains separate. |
| Multiple rounds | A deliberately underspecified shared reservation feature leaves ownership, visibility, conflicting reservations, cancellation authority, expiration, audit visibility and notification recipients unsettled. Do not pre-answer those choices. | Real questions and waits; supported additional rounds without restart request when material questions remain. Driver supplies one test-only choice per actual question, not a bulk invented transcript. |
| Pending question resume | Interrupt after an actual unanswered question. | Restore same target/question after current-artifact check; no answer by silence or duplicate spec. |
| Pending review resume | Interrupt at final review before approval. | Restore pending review; no implicit planning or approval. |
| Changed artifact/answer | While paused, change an appropriate test artifact or supersede a test answer explicitly. | Revalidate and reconcile current intent; ask about consequential conflict; do not restore stale content. |
| Goals | Use actual supported native Goal controls with the subject skill. | Observe activation, genuine input/review stops and interruption/resume. Platform/no-progress/budget stops remain incomplete. No fixture-only compatibility claim. |

Record actual observations and any unavailable case in the feature’s validation/acceptance.md. Do not edit installed component behavior, global configuration or model/effort to make a case pass. Mechanical comparisons support but do not replace actual observations.

## Exact-version repeated-use evidence and fixture requirements

For installed Specify 1.0.10.dev0+pegagio.2, source revision `e367aae92d6ff254a0608848e41c1b67e656db32`, `docs/reference/agentic-sdd.md:64` explicitly permits repeated focused clarify uses before planning. Supply this as version-attributed evidence alongside the unchanged installed command; do not assert that a host limit resets or force an unresolved instruction conflict. The actual subject accepted distinct bounded command interactions after assessing both sources.

Every synthetic roadmap entry, including negative-selection fixtures, must retain required description, outcome and Scope (in) fields. Missing fields in driver-created 005/006 caused a real helper failure; adding those fields restored lifecycle evaluation without changing the helper.

## Revised boundary cases — 2026-10-17

Earlier case descriptions/evidence concern the former combined behavior. The active revised tests below supersede its live-Goal-wait expectation; old failures remain failures.

| Case | Setup and evaluator action | Required subject observation |
|---|---|---|
| Ambiguous draft/Goal | Select test feature 007 with visibility explicitly unsettled, or an equivalent one-choice fixture. Set the preparation Goal only through saved draft/handoff. Supply no answer during automation. | Actual revised skill saves usable draft/findings, Needs clarification and ordinary clarify entry point; native Goal is complete, not stalled; no idle continuation or fabricated answer. |
| Settled draft/Goal | Use fixed greeting requirements. | Native Goal completes at Awaiting spec review, with no invented question, approval or later phase. |
| Ordinary clarification | After verified Goal completion, evaluator explicitly invokes existing clarify ordinarily; wait for the subject’s actual question before giving a test-only creator-private answer. | Actual question wait and answer incorporation; supported rounds/limits; completed preparation Goal stays completed; human review remains separate. |
| Approval prerequisite | Before explicit approval, evaluator asks whether planning may proceed. Clarification answer/Goal completion are not approval. Later supply explicit test-only spec approval solely to inspect prerequisite recognition. | No plan/tasks command or later-phase artifact before approval; after approval, report readiness for separately selected planning without executing it during this test. |
| Resume/negative paths | Proportionately re-exercise target identity, pending handoff/input/review and changed artifacts. | No duplicate activation/feature, fabricated approval or revival of completed Goal to await answers; blockers reported honestly. |

Keep the previous subject/Goal untouched unless the operator explicitly readies it for this test. Do not work around runtime access denials, alter native databases, change model/effort or create a controller to make a test pass. Existing documentation/reference supports repeated ordinary clarify uses; it does not provide native Goal suspension.

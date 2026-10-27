# Independent implementation-plan review

Explicitly select one feature and authorize an independent reviewer under the project's bounded delegation rules. The reviewer must be a separate session with no material candidate authorship, inspecting the approved specification, complete proposal/checklist/design/fresh analysis and relevant architecture. This entry neither creates a mandate nor approves execution by being available.

For an operator-facing request to arrange review, use `$farmboy-request-plan-review` in the selecting session. An already dispatched independent reviewer uses `$farmboy-review-implementation-plan`; its standalone route has no Diagram dependencies. In deliberately Diagram-enabled projects that reviewer entry invokes `$farmboy-diagram-work` once. Adapter and semantic body compose in the same session inside the independent reviewer: adapter establishes/verifies authority, body reviews and returns, adapter validates/records/releases. The selecting caller then collects the actual outcome. This is not a new API or coordination framework.

## Return content

The body saves selected-feature `validation/plan-review.md` with the six exact answers/rationale, candidate references, actual reviewer/human mandate/independence evidence, findings and one decision. It returns:

| Named content | Caller verification |
|---|---|
| report_reference | contained selected feature path and SHA-256 of saved report bytes |
| reviewed_candidate | exact feature, approved specification, plan/tasks/checklist/design/analysis/architecture references and committed or base-plus-dirty state |
| reviewer_mandate | actual reviewer, human provenance/bounds and independence evidence |
| findings | actionable blocking requests versus explicitly non-blocking optional suggestions, tied to report sections |
| disposition | approve, planning-return or specification-escalation on complete review |
| incomplete | no substantive disposition; precise technical/missing/uncertain input, saved evidence/known effects and next action |

Approval permits optional-only suggestions, never an unresolved blocker or unmet obligation. Planning-return asks for correction within approved specification meaning. Specification-escalation asks actual product questions, not a rewritten or approved spec. Technical failure, missing or invalid/contradictory output is incomplete, not an implicit approval.

The receiving adapter reads the actual report, checks its digest/candidate/mandate and current native authority, checkpoints only authorized evidence and maps the existing native disposition once. It alone owns acquisition/reuse, grant transport, finalization and released readback; the semantic body owns judgment. Standalone returns the attributable report/decision to its caller without creating a native lifecycle. No proposal repair, automatic re-review or next workflow follows. Approval is distinct from implementation permission.

## Optional Diagram use and adoption

The native review segment requires matched Feature9/schema24 capabilities. The current deployed source reference is Diagram `da6569ce57b6aa0a4b151d38bde8a5c55061a1da`; current Project4/Issue-query6 projections must be matched. Historical schema19/20/21/22/23 clients/stores require their matching historical tools. The adapter's adjacent native reference owns exact fields, grant validation and terminal mapping; generic skill has no version or command coupling. Availability grants no approval authority or workflow launch.

A caller's existing `--review-grant-file` flows unchanged from launcher prompt to adapter admission, with its exact reviewer labels and actual bounded human mandate. Neither launcher selection nor an enabled automation switch delegates approval. Unavailable capability, refused permissions, stale grant or uncertain state stops dependent effects, without upgrade or authority fabrication.

Consumer refresh is explicit later work. Delivery here updates Farmboy source only: do not copy into a live project's skills/configuration, change its enabled route, install tools, migrate a live store or enable automation by inference. Disposable authorized fixtures can adopt selected source copies for tests without live adoption. Controlled launcher/native tests prove plumbing; actual independent real-session observations are separately needed for skill behavior/judgment before runtime acceptance. No evaluation platform is required.

## Report checkpoint approval boundary

The generic body does not commit. When the coordinated adapter needs its already-authorized report checkpoint and the runtime protects Git metadata, it may request the existing per-action approval for narrowly scoped staging and normal commit. This is an approval request, not permission expansion or a sandbox bypass. Preserve hooks, add no broad reusable rule, and never substitute another executor for the reviewer's checkpoint. An actual approval-review denial stops that action; uncertain results require inspection. Do not ask the human to repeat already established checkpoint authority merely because the technical approval mechanism must still be used. Missing mechanism/capability remains an exact incomplete boundary.


## Consume findings during Farmboy delivery

Before core implementation/setup, delivery reads the full applicable committed review supporting the current approved candidate. Current unresolved required corrections/blockers or unmet obligations stop at any priority; approval alone cannot resolve a contradiction. Priority alone does not turn expressly non-blocking advice into a requirement. For example, high-priority optional advice with no defect remains voluntary; a low-priority required correction still blocks. Historical findings need applicable resolution/supersession evidence rather than deletion or inferred resolution. Ambiguous status or advice that describes an unmet obligation requires the precise evidence/decision, without automatic return, repair, re-review or approval invalidation. Farmboy owns this semantic assessment; review production and native approval authority are unchanged.

## Consume findings on separately selected return

After the reviewer stops, the separately selected planning or ordinary clarification/revision session reads the applicable full committed report and verifies feature, reviewed candidate, disposition, integrity and existing resolution evidence before affected setup/edits. Record required finding corrections/resolutions or precise unresolved reasons in existing plan/tasks/analysis or spec Clarifications/notes/checklist. Unresolved reason is incomplete, not a successful resolution. Required findings remain obligations at any priority; genuine optional advice is voluntary with adopted/declined reasons. Preserve known originating accepted operation/report/candidate refs for later handoffs and reuse applicable dispositions without duplicate notes.

Planning return preserves approved specification meaning, task IDs and completed evidence, performs separate repair/fresh read-only analysis, then stops for full-plan review. Material product change stops for separately selected specification work. Specification escalation uses existing ordinary clarification/revision on the same feature, holds current clarification authority through genuine question waits, integrates actual answers and returns to explicit human whole-spec review; no fresh drafting or inferred approval. Core commands remain unchanged. Standalone callers supply equivalent explicit current return context; no report requirement is added to ordinary report-free work. Missing/wrong/stale/ambiguous evidence stops precisely rather than selecting the newest report or adding a tracker.

## Selecting-caller handoff

“Arrange independent review of this saved plan” selects the thin caller. The caller may be the author, but the semantic reviewer must be a separate session without material authorship. Verify the exact candidate, actual human mandate and applicable role before dispatch. Review alone is not delegation; ask one concise question for missing substantive scope, never for operator-authored grant JSON. A known applicable explicit mandate is reused without redundant confirmation.

On a Diagram route the caller assembles the existing ReviewGrant and supplies it unchanged in the initial independent-session prompt/context, including Feature/handoff/revision, reviewer labels, actual human provenance and constraints. It uses the host's exposed exact-target independent-session/read/wait facilities. The reviewer never issues its own missing grant. Native admission, normal report checkpoint/hooks, finalization and release remain solely in the existing adapter; the caller does none of those on its behalf.

The existing launcher transports `--review-grant-file` only when discovery selects that exact candidate. It is not an arbitrary manual review selector. Controls-OFF manual review uses the supported explicit independent-session entry when available; missing targeting/capability/permission stops rather than installing, enabling controls or adding a selector. An already dispatched reviewer never routes back to caller dispatch.

Caller collection verifies actual report SHA-256/candidate/mandate and native accepted terminal plus released owner, preserving original proposal versus report checkpoints. A process exit or prose alone is insufficient. Resume inspects the known child/operation/current state before effects; missing or uncertain context never justifies another reviewer. Every denial/failure returns its exact action, target, reason and known effects; no alternate-executor workaround.

Return six conclusions, required/optional findings and actual disposition/release with the next ordinary decision. There is no automatic repair/re-review/implementation. This source feature installs nothing in consumers. Existing project-local selective directory-copy adoption remains explicitly authorized later work, with preserved customizations and compatibility verification.

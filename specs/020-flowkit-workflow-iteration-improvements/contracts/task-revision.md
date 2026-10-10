# Implement Task Revision Contract

This prospective contract implements the operator's 2026-10-05 addition to Feature 020 (FR-023/SC-009). It does not authorize another FlowKit workflow, unrelated scope, external source changes, Git integration or acceptance.

## Trigger and Ownership

Independent code assessment identifies a concrete defect within the selected feature for which the task plan needs a reopened or newly recorded correction task. Before reading task bytes, the installed controller helper verifies the active pointer, lexical task and parent paths, and physical containment within the selected feature. It then freezes the exact task text and digest plus the selected feature's specification text and digest. Immediately before Tasker dispatch, it repeats the identity and path checks and requires both digests to match. The main controller then freezes the exact finding IDs and corrections, eligible existing task IDs and owners, and the `FlowKit-Tasker` owner permitted to append a new task. The deterministic scope digest includes the approved selected-feature specification digest. It delegates the bounded `speckit.tasks` revision to exact `FlowKit-Tasker` through declared workflow metadata. Naming the agent in prose or using a generic child is insufficient. Routine in-scope revision requires no extra reopening approval.

Tasker owns task-plan revision. After Tasker returns, the main controller performs a separate semantic comparison of the actual diff with the frozen findings, exact corrections, owner map and approved feature scope. The deterministic validator requires this affirmative review to name the same frozen finding and task IDs and scope digest; Tasker cannot supply or replace that review. Coder implements eligible tasks; independent Code Reviewer evaluates implementation. Neither a Coder completion claim nor Tasker's task edit resolves a code finding. The main controller retains consequential gates and validates the resulting task diff before coding resumes.

## Allowed Task Changes

Tasker may reopen only an existing ID allowed by the frozen owner map and attach the exact stable finding. Where no eligible existing task owns necessary in-scope work, Tasker may append a new unique ID with concrete paths and dependencies under the frozen `FlowKit-Tasker` append owner. It preserves unrelated completed IDs, markers, completed descriptions and accepted decisions. It does not renumber tasks, delete completed work, claim future evidence, modify governing artifacts, or expand product scope. New scope or unsafe ambiguity stops for operator resolution. Preflight rejects task-file and parent-directory symlinks before reading the selected task snapshot or dispatching Tasker; it also requires physical containment within the selected feature. A cross-feature symlink alias is blocked before another feature's task file can be read or changed.

## Revision Result

Return a structured revision result with selected feature identity, finding references, before/after task digests, reopened and added IDs, and preserved completed IDs. Evidence paths are repository-relative; values below illustrate the shape and are not current completion evidence:

```json
{
  "revision_state": "updated",
  "feature_directory": "specs/020-flowkit-workflow-iteration-improvements",
  "tasks_path": "specs/020-flowkit-workflow-iteration-improvements/tasks.md",
  "finding_ids": ["F020-R001"],
  "task_mappings": [{"finding_id": "F020-R001", "task_ids": ["T008"], "owner": "FlowKit-Tasker"}],
  "reopened_task_ids": ["T008"],
  "added_task_ids": [],
  "preserved_completed_task_ids": ["T001", "T002"]
}
```

The runtime result also includes observed `tasks_before_sha256` and `tasks_after_sha256`, and an exact blocker when revision cannot proceed. The validator compares Tasker finding and task mappings against the frozen pre-Tasker snapshot, enforces the owner map, checks the separate main-controller semantic review and scope digest, and validates identity, current digests, lexical and physical path containment, task uniqueness, and permitted history changes. A missing or invalid result is not implicit success.

## Bounds and Stops

Keep the existing Implement correction bound and no-progress/repeated-finding checks. Reopening or appending tasks earns zero substantive implementation progress; only fresh independent code evidence resolves findings. Preserve stable finding IDs across passes. Missing or unavailable exact Tasker assignment, stale evidence, unsafe task diff, unmet prerequisite, scope/authority/product decision or ambiguous recovery stops without fallback. Task revision never invokes FlowKit Tasks, Analyze, Converge or an undeclared later phase.

## Required Validation

Execute production rendering and branch routing for open-task correction, closed-task reopening, and missing in-scope task cases. Execute the literal rendered validation command through the installed `.specify/flow-kit/scripts/python/controller.py` package layout in a disposable consumer for both a valid revision and a rejected revision. Verify exact Tasker metadata and native availability separately from no-op fixtures. Demonstrate preserved history, bounded return to Coder, fresh independent assessment, and focused stops for invented/omitted/substituted findings, wrong owners, unrelated scope, and cross-feature symlink aliases. Synchronize source charts and manual guidance; local tests do not prove consumer delivery or feature acceptance.


## Defect Progress and Parent Task Completion

The operator's 2026-10-06 addition FR-025/SC-011 allows continuation on an independently resolved prior code defect while its parent task remains unfinished. It removes the whole-task-completion prerequisite for another otherwise safe authorized Implement pass; it does not relax task completion or acceptance evidence.

Freeze a read-only pre-correction baseline of selected unfinished task IDs and known unresolved finding IDs, with each finding's exact requirement, observed deficiency, existing eligible owner and current source digests. Code Reviewer supplies fresh resolution evidence, not Tasker or Coder claims. The strict outcome envelope remains unchanged: `remaining_ids` may contain unfinished task and unresolved finding references, and `resolved_ids` may contain completed prior tasks or resolved prior findings. Keep namespaces distinguishable and preserve task mappings in the workflow-specific result. Actual prior recorded IDs drive the existing progress intersection; do not overwrite history or manufacture a baseline after correction.

A resolved defect must satisfy its recorded requirement and observable deficiency with fresh code/validation evidence. Another instance of the same violation keeps that finding open; a genuinely distinct newly discovered violation is separately recorded and remains unresolved. Discovery alone earns no credit. Task revision, checkbox edits, successful commands, source-byte churn, renamed findings, omitted findings or report updates cannot resolve a defect. Core readiness and current correction eligibility are independent continuation prerequisites.

Continuation needs a prior task or finding resolution, safe remaining selected work and available iteration budget. Completing the whole task is unnecessary for progress, but its checkbox stays open until its full requirement is independently substantiated. Preserve existing no-progress, cap, unavailable-agent, stale/readiness, authority and unsafe-recovery stops. Do not ask for fresh routine authorization solely because a parent task remains unfinished, invoke another workflow, hot-refresh an active installation or infer feature acceptance.

## Requested Scope Compatibility

The 2026-10-07 Story 7 [implementation scope contract](implementation-scope.md) supplies the missing distinction between trusted requested work and current correction eligibility. The existing frozen Tasker revision scope remains specific to reviewed findings; it is not the full Implement authorization. Original request and all initially blocked scoped task identities must be retained before correction, independently from the unresolved-work projection in a successor progress baseline. No eligible list can narrow that request.

Ordinary evidence-supported tracking is owned by exact FlowKit-Tasker and changes only validated completion markers; it does not require a defect revision finding or grant code-progress credit. Reopening/adding defect tasks retains the existing preflight, exact finding mapping, separate semantic review and bounded baseline-transition validation. Preserve original scope and defect source before bytes; append a new derivative/baseline/history record rather than retroactively adding task IDs to the original comparison. Material added product scope requires the actual focused operator decision before effect.

Before later activation, fresh task-specific source preimages and current eligibility/readiness/owner route proof are required. Newly found defects enter the next recorded correction history with zero discovery-pass credit. Completed prerequisites or a real same-child answer trigger reassessment, not a fabricated defect resolution, new task approval or reset of the existing five-pass budget. Initial source execution after a decision remains distinct from corrective re-entry; no-progress source correction still stops. Full request/subset accounting and exact partial/blocker receipts follow the scope contract. This clarification is prospective artifact design, not a claim that old baseline transitions already support these new records.

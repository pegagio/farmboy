# Converge stops before recording a reviewed correction task

This report captures an unnecessary operator restart during Feature 023 convergence. The existing Implement correction-accounting report covers a related symptom; this Converge task-recording failure needs its own regression and future correction task.

## Evidence and reproduction

The installed `farmboy-converge` 0.5.1 definition has normalized digest `b6543f8a0372c20910e1a0e1e49af75ca14664bebef12b4f45ab39a4e8a3cd30`. Run `04f6e328-6aac-4247-a029-f1c50fe94165` completed its first append-only convergence command with no reported gaps, then its independent Code Reviewer found `F023-CONVERGE-DIAGNOSTIC-CONTEXT` against FR-002. All existing tasks were checked, including the finding's original owner T005. The actual controller returned `blocked` with `record-or-reopen-diagnostic-correction-task-and-revalidate-eligibility`, before the workflow could record new correction work.

The [independent review](../../specs/023-workflow-branch-validation-controller-integration/validation/convergence-review-pass1.json) preserves the finding and valid-control reproductions. The original stop report is preserved in the retained run's `resume-original-session.json`; later recovery reports must not replace the historical assessment. The operator had already invoked Converge, whose purpose includes bounded task recording, analysis, implementation and reassessment. No product, constitutional, authority, material-scope, Git, roadmap or acceptance decision was required for this diagnostic correction.

## Defect and expected behavior

The core convergence command precedes independent code review. A defect discovered only by that reviewer can therefore lack an unfinished task. The installed assessment requires an eligible recorded task before continuing, but its correction branch cannot run until that assessment continues. This creates a circular prerequisite and requires renewed operator authorization for routine in-scope work.

The future correction should allow bounded recording of a reviewed in-scope finding as new append-only work, preserve completed task markers and the original finding identity, and require fresh artifact analysis and eligibility before implementation. Recording tasks earns zero substantive progress. Keep finite correction limits, retained counters, native assignments, current evidence checks and real consequential decision gates. Do not silently reopen completed history or infer permission for another workflow.

## Relationship and future task

The [Implement first-defect correction stop](2026-10-13-implement-first-defect-correction-stop.md) and planned Feature 024 / WR-04 cover related continuation accounting. Feature 024's current roadmap scope names Implement, so this report does not claim that its approved scope already includes Converge. The existing Feature 014 convergence-loop intent is relevant prior authority, not evidence that this path works. No roadmap amendment or existing completed feature task has been changed.

- [ ] FB-CONVERGE-001 Fix the reviewed-finding/task-recording prerequisite cycle in the reusable Converge workflow and shared protocol. Add deterministic source/disposable-consumer tests in which the initial command is clean, independent review discovers a bounded in-scope defect owned by a completed task, new correction work is recorded without changing prior markers, fresh analysis and eligibility precede correction, and a later independent assessment proves closure. Verify stable finding identity, retained finite counters, zero progress for administrative recording, strict stale-evidence rejection and stops for genuine consequential decisions. Reconcile this task into the selected future feature's approved spec/plan/tasks before implementation; related record: Feature 024 / WR-04.

## Current recovery boundary

The operator explicitly authorized task recording, diagnostic correction and retained Converge resumption on 2026-10-14. That instruction unblocks this run only. Feature 023 fixes the contextual diagnostics finding; it does not implement FB-CONVERGE-001 or silently change the reusable continuation policy. Preserve the original roadmap effect, receipt, staged index, Implement counters and Converge assessment history.

The first correction was followed by a second assessment that independently closed the original cases and found `F023-CONVERGE-NESTED-GRAPH-LOCATION`, another exact-location violation of FR-002. The core convergence command had recorded its separate template-form finding as T024, but the reviewer-only nested-location finding again lacked an unfinished task. The [pass 2 review](../../specs/023-workflow-branch-validation-controller-integration/validation/convergence-review-pass2.json) reproduced the same prerequisite cycle. The retained operator instruction already authorizes bounded diagnostic task recording and correction, so the controller records the additional task and reassesses eligibility without asking for another confirmation. This run-specific recovery is additional regression evidence for FB-CONVERGE-001; it does not change the installed workflow's default policy or reset either counter.

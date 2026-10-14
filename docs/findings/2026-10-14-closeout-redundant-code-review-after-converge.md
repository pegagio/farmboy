# Redundant Closeout code reviews after successful Converge

The operator reported this workflow defect during Feature 023 Closeout on 2026-10-14 and requested recording it for a later fix. This report does not change the installed workflow or expand Feature 023.

## Observed defect

Installed `farmboy-closeout` 0.9.2 requires fresh native Code Reviewer dispatches for both `assess-implemented-lifecycle-milestone` and `assess-closeout-debrief` after a successful Converge gate. Feature 023 had already passed independent Converge review with all 25 tasks complete and current source-bound validation. Closeout changed only the specification status and roadmap lifecycle; implementation source and tests remained unchanged. Nevertheless, both steps repeated substantive code review alongside evidence revalidation, adding time and operator confusion without a new implementation delta.

## Evidence

Converge's clean independent review is retained in `specs/023-workflow-branch-validation-controller-integration/validation/convergence-review-pass3.json` and completion in `validation/convergence-resume-outcome.json` under that feature. Closeout's repeated assessments are `validation/phase-lifecycle/closeout-implemented-assessment.json`, `closeout-implemented-review-report.json`, and `closeout-debrief-assessment.json`. Its status-only bridge is `closeout-status-before-spec.md` plus `closeout-status-owner-effect.json` in the same directory. The fresh debrief is `specs/023-workflow-branch-validation-controller-integration/roadmap-reviews/debrief-20261014T160531Z.md`.

The active definitions are `workflows/farmboy-closeout/workflow.yml`; lifecycle proof checks are in `controllers/farmboy/scripts/python/milestone_policy.py` and `phase_lifecycle.py`; execution guidance is `controllers/farmboy/controller-protocol.md`. Both installed and source `farmboy-closeout` workflow definitions have SHA-256 `f7fc526dc6feb2f8eed03bc633d024ca12d67a744de8c9db9d82b117d3453ad8` and corroborate the two required Code Reviewer steps. These coordinates identify the defect; a later implementation must revalidate their current content.

## Proposed correction and acceptance

Reuse attributable, independent, successful Converge review and validation when the selected feature, reviewed scope, code/test inputs, and proof bindings remain current. Closeout should verify those bindings and review its roadmap outcome, verification amendment, and wiki upkeep. Review substantive changes since the trusted Converge boundary when they exist. Missing, stale, untrusted, cross-feature, or incomplete Converge evidence must retain a safe fresh review or explicit recovery route; task markers and labels alone remain insufficient.

Regression coverage should demonstrate no duplicate whole-code review for unchanged code after clean Converge; exact status-only specification bridging; bounded review of subsequent substantive changes; rejection or fresh review for stale/missing/cross-feature proof; preserved roadmap verification approval, validation strictness, bounded corrections, and separate Git/acceptance authority. Reusing evidence must not manufacture native identity or overwrite historical assessments.

## Deferred correction task

This is a separately authorized future workflow fix, distinct from the existing Closeout continuation/accounting defect and Feature 023's completed buildable scope.

- [ ] **FB-CLOSEOUT-REVIEW-001**: Reconcile this defect through the owning workflow's specification, plan, and task artifacts, then implement and independently validate Converge evidence reuse and delta-only Closeout code review with the acceptance cases above. Preserve consequential gates and current evidence validation. Do not reopen Feature 023 or amend the roadmap solely from this record.

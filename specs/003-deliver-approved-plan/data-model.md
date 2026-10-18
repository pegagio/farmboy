# Data model: Existing delivery artifacts

This is a conceptual model of existing files and review evidence, not a new schema or persistence layer. All references are contained project-relative paths in authored artifacts; illustrative accounts use pegagio.

## Selected feature and approvals

The selected feature is identified by its authoritative roadmap entry and `.specify/feature.json` directory. **Constraint**: “Explicit selected identity and ambient active-feature identity must agree before effects.” Dependencies must be verified. Specification and full-plan approval are actual conversation evidence or an applicable content-identifying existing note; historical approval does not approve changed meaning. No approval register is introduced.

## Candidate and evidence

A delivery candidate consists of current implementation, coherent spec/plan/tasks, actual verification/convergence results, documentation/debrief/wiki outcomes and the actual local commit. Existing task identities, checked evidence and accepted answers survive resume. **Constraint**: “Zero actionable gaps and zero unmet obligations are required for clean delivery.” Findings of any severity remain required if they identify a defect/unmet requirement. Optional suggestions are distinct.

Use ordinary existing artifact notes for a concise handoff: actual outcome, candidate/artifact references, evidence/limitations, remaining work or exact required input, and next ordinary action. These are report content, not a serialized execution packet or runtime ledger. Actual Git identity may be reported in conversation/notes after commit; it does not require another commit.

## Status and handoff meanings

Only existing roadmap lifecycle values are used. **Constraint**: “Successful local delivery records implemented and hands off Awaiting result review; only subsequent explicit applicable human result acceptance separately authorizes verified.” Incomplete attempts must not falsely advance either status. Technical verification is distinct from the ledger label verified. Awaiting result review and INCOMPLETE are readable handoff labels, not new ledger values.

The implemented update and all scoped delivery artifacts belong in the final local commit after checks/documents. Successful delivery means that actual commit succeeded; ordinary Git errors do not justify a success claim. This uses existing artifacts and command results, without an additional status protocol or failure model.

## Native automation boundary

A native objective is inspected only if separately operator-selected. **Constraint**: “Save the complete matching endpoint and verify supported native complete readback before requesting or waiting for human input.” A bounded input endpoint includes INCOMPLETE delivery outcome, exact question, artifacts, actual work/attempts and remaining issues, next ordinary action. After an actual answer, only separately selected ordinary interaction continues artifacts outside the completed Goal. No new Goal, event store, ownership record or recovery model is introduced.

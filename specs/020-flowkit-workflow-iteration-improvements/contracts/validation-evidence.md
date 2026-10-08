# Contract: Feedback Reassessment and Validation Evidence

FR-001/FR-021/FR-022 require attributable present results linked to unchanged historical observations. Portable feature validation artifacts establish evidence, not runtime authority, publication or feature acceptance.

## Required Records

Future `validation/observations.json` contains one current assessment for each of the five immutable IDs from the consolidated report. Fields are observation_id, historical_component, current_component, disposition, requirement_ids, test_case_ids, evidence and gap. Disposition is reproduced/not-reproduced/not-tested; not-tested requires a specific missing context/command/evidence gap. Original records and report bytes stay intact.

Future `validation/cases.json` contains per-area, native-context and combined case results. Each has case_id, area, requirements, context_id, expected, observed, result, component_provenance, evidence and limitations. Source provenance includes component ID/version, source repository/ref/commit, package/source digest, tested CLI version, observed client version/context or unavailable, preparation and actual result. Paths are normalized repository-relative; all persisted source evidence includes SHA-256.

Native definition provenance uses package/source identities and consumer configuration/version-control state; no consumer-copy ownership hash ledger is added. Avoid secrets, credentials, raw transcripts, personal host paths or unsupported settings claims. Sanitized exact native errors may be kept only as bounded summaries.

## Combined Sequence

In a disposable prepared project, retain the same uniquely mapped feature across explicit activation, separately requested authoring/preparation, Analyze readiness and separately requested Implement startup. Record each operator invocation boundary, current identity/evidence, prompt decisions and result. Starting Implement proves startup only; it does not complete implementation or accept the feature. Required pending future obligations remain pending.

A blocked variant uses an unresolved consequential authority decision or unavailable exact assignment, with no unsafe mutation/fallback. Retain earlier successful results, current blocker and safe resumption. A ready saved report never overrides changed current state. Include readiness loop cases for each declared correction owner, exact native Checker availability, stable findings, semantic resolution, no-progress/cap/authority stops and immediate Implement handoff revalidation. Preserve unchanged core files and pending future obligations as explicit compatibility evidence. The Checker consumes required independent verdicts; it cannot replace them.

## Success Accounting

Require each per-area outcome, both combined variants and all native-context cases individually. All five observations remain traceable even when one is not reproduced or cannot be tested; truthful not-tested accounting satisfies traceability, not the missing behavioral target. Automated fixtures/no-op transport may establish local contract/dispatch behavior but cannot pass live native or effective settings cases. Capacity feedback may stay unresolved under the narrowed scope.

Independent reviewers check semantic results and provenance. Release/adoption/stock compatibility/Git integration/The Diagram and feature acceptance require their own evidence and explicit decisions; no state field here grants them.

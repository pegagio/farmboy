# Close Out routine continuation defect

FarmBoy Close Out should complete authorized, source-supported maintenance without repeatedly requiring a new invocation. Feature 022 exposed a mismatch between that intent and the installed wiki loop's progress and pass accounting. This finding records the defect and the operator-directed recovery; it does not claim a controller implementation fix.

## Observed failures

The first Close Out invocation finished roadmap verification and all six substantive wiki content corrections, then exhausted its five wiki passes with one date-only installation-history warning. A subsequent invocation revalidated the historical page and cleared the warning. Independent review then found a supported citation attribution correction in the same historical paragraph. Because the metadata-only repair earned zero substantive progress credit, the generic loop rejected a second pass as `no-progress`, despite a concrete safe correction within the frozen source set.

The controller asked the operator to authorize yet another invocation. The operator identified this as a FarmBoy defect: ordinary Close Out repair and reassessment should continue under the existing workflow authorization. The current run continues from its fully recorded pass-one boundary under that direction, preserving the original stop, actual pass accounting, source scope, named assignments, and consequential gates.

A second provenance issue appeared while preparing the citation correction: the existing S026 identity is a directory, whereas the selected frozen source is its `follow-up.md` file. Exact file ingestion must receive its own stable registry identity. Treating the directory S-id as the file's dedup identity was incorrect. Preparation was corrected before effects; no directory access expansion was authorized.

## Source leads and evidence

Inspect `workflows/farmboy-closeout/workflow.yml`, `controllers/farmboy/controller-protocol.md`, and `controllers/farmboy/scripts/python/controller.py`, especially `route_loop_assessment`. The wiki loop starts with preparation and ingestion, then lint and independent assessment. Without a preceding assessment, first-pass continuation requires a substantive resolved ID; date-only revalidation explicitly earns no such credit. Newly discovered safe work therefore can be blocked before its first corrective pass. A fixed five-pass allowance also mixes content ingestion with administrative freshness maintenance.

Feature evidence is under `specs/022-local-workflow-agent-timing-metrics/validation/closeout/`. The earlier `outcome-46aadf4e.json` records cap exhaustion after verification. `fresh-879906e8/wiki-assessment.json` identifies `historical-pyyaml-source-attribution`; `outcome.json` and `summary-before-operator-continuation.json` retain the later no-progress stop. `operator-continuation.json` records the operator-directed continuation. The two citation repair proposals preserve the file-versus-directory identity correction before effects.

## Desired correction and verification

Keep this change within FarmBoy. No Spec Kit, Codex, Excel, or dependency changes are required. Reuse existing controller primitives where practical.

Establish current findings before correction, distinguish substantive claim repair from administrative freshness work, and allow an actionable newly discovered in-scope finding to receive its first authorized correction. Do not require a new invocation merely because a metadata-only pass correctly earns zero substantive progress credit. Preserve honest no-progress detection for repeated ineffective corrections and protect against unbounded churn without prematurely stopping a finite, progressing maintenance queue.

Test at least the observed sequence: existing verified feature, date-only warning, supported metadata revalidation, newly discovered citation gap, automatic source ingestion correction, fresh full lint, independent complete assessment, and final readiness. Also test substantive corrections followed by administrative cleanup; unchanged findings after an ineffective correction; changed source identity or hashes; and genuine consequential decisions. Source selection must distinguish normalized file identities from directory grouping IDs.

Success means routine supported corrections reach evidenced Close Out completion under the original authorization, with retained histories and current validation. A required authority, product, constitutional, material scope, or Git decision must still stop at its explicit human gate. Readiness never grants permission to commit, merge, publish, or accept a feature.

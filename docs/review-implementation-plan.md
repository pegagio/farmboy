# Independent implementation-plan review

Explicitly select one feature and authorize an independent reviewer under the project's bounded delegation rules. The reviewer must be a separate session with no material candidate authorship, inspecting the approved specification, complete proposal/checklist/design/fresh analysis and relevant architecture. This entry neither creates a mandate nor approves execution by being available.

Use `$farmboy-review-implementation-plan` on a standalone route without Diagram dependencies. In deliberately Diagram-enabled projects the ordinary entry invokes `$farmboy-diagram-work` once. The adapter and semantic body then compose in the same session: adapter establishes/verifies authority, body reviews and returns, adapter validates/records/releases. This is not an API, subprocess return or new coordination framework.

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

The new native review segment needs matched Feature9/schema21 capabilities. The current deployed source reference is Diagram `9fc12923e1399d5c88a1c1a2193474869564ddda`; source availability does not install that support. Historical schema19/20 clients/stores require their matching historical tools; current operations require schema21. The adapter's adjacent native reference owns exact fields, grant validation and terminal mapping; generic skill has no version or command coupling.

A caller's existing `--review-grant-file` flows unchanged from launcher prompt to adapter admission, with its exact reviewer labels and actual bounded human mandate. Neither launcher selection nor an enabled automation switch delegates approval. Unavailable capability, refused permissions, stale grant or uncertain state stops dependent effects, without upgrade or authority fabrication.

Consumer refresh is explicit later work. Delivery here updates Farmboy source only: do not copy into a live project's skills/configuration, change its enabled route, install tools, migrate a live store or enable automation by inference. Disposable authorized fixtures can adopt selected source copies for tests without live adoption. Controlled launcher/native tests prove plumbing; actual independent real-session observations are separately needed for skill behavior/judgment before runtime acceptance. No evaluation platform is required.

## Report checkpoint approval boundary

The generic body does not commit. When the coordinated adapter needs its already-authorized report checkpoint and the runtime protects Git metadata, it may request the existing per-action approval for narrowly scoped staging and normal commit. This is an approval request, not permission expansion or a sandbox bypass. Preserve hooks, add no broad reusable rule, and never substitute another executor for the reviewer's checkpoint. An actual approval-review denial stops that action; uncertain results require inspection. Do not ask the human to repeat already established checkpoint authority merely because the technical approval mechanism must still be used. Missing mechanism/capability remains an exact incomplete boundary.

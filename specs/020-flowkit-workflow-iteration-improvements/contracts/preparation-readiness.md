# Contract: FlowKit Preparation Readiness and Correction

FR-010–FR-014 and FR-024 define one current readiness meaning at FlowKit Analyze and Implement boundaries. The operator approved this FlowKit-owned replacement on 2026-10-06; the original core-evaluator proposal is superseded. This is a prospective source contract, not evidence of implemented readiness or permission to bypass installed gates.

## Table of Contents

- [Source and Agent Ownership](#source-and-agent-ownership)
- [Preparation and Future Obligations](#preparation-and-future-obligations)
- [Readiness Result and Findings](#readiness-result-and-findings)
- [Analyze Correction and Reassessment](#analyze-correction-and-reassessment)
- [Implement Handoff](#implement-handoff)
- [Compatibility and Validation](#compatibility-and-validation)

## Source and Agent Ownership

The readiness helper belongs to `controllers/flow-kit/scripts/python/readiness.py`, delivered through the normal controller package. It validates active identity, safe normalized feature-contained paths, checklist coverage, stable item locators, counts and current source/evidence digests. It reads only the selected feature and makes no mutation during assessment. It must reject lexical symlink escapes and unsafe paths before reading or recording artifacts.

A new reviewed native `FlowKit-Readiness Checker` definition belongs to `agents/flow-kit/agents/flowkit-readiness-checker.toml` and its source manifest, using `gpt-6-luna` with `model_reasoning_effort = "medium"`. The exact agent is explicitly assigned in the changed workflow definitions and receives no per-run model/effort override. Definition presence is not native dispatch or effective-setting proof. Unavailable exact Checker stops the invocation without fallback; installation, reload or another phase is not automatic recovery.

Checker is read-only and bounded to interpreting mechanical helper results, established obligation classifications and existing evidence/verdict records. It cannot author corrections, judge work it authored, replace required independent requirements review, grant authority or mark achieved outcomes. Existing FlowKit-Reviewer remains responsible for substantive independent review and artifact findings; its model/effort is unchanged. Missing review is a finding requiring the proper reviewer, not an opportunity for Checker to invent an approval.

## Preparation and Future Obligations

Known built-in `checklists/requirements.md` assesses specification quality under Specify/Clarify author ownership. Custom standard checklists are reviewer-owned requirements-quality artifacts. Every checklist item remains a preparation blocker until current evidence and its authorized owner establish satisfaction. All source items require coverage; unchecked items cannot be exempted by filename, future-sounding text or a sidecar flag.

Implementation tests and human acceptance obligations live outside `checklists/`, normally in an existing feature-local `validation/` artifact. They remain pending with stable identity, original text, owner, due phase and expected evidence. Future obligations cannot be marked checked or discarded to make core Implement proceed.

For a mixed/legacy checklist, explicit authorized classification must establish which obligations are preparation and which are genuinely future work. An optional feature-local `preparation.json` may record item locators, category, owner, input/evidence digests and relocation provenance. Unknown/mixed purpose, unowned criteria, duplicate locators, incomplete coverage, unsupported claims or changed evidence block until the proper owner reconciles them. A stale record never suppresses current source content.

A declared main-task recorder may relocate a reviewed future obligation only within the selected feature, preserving pending status, identity/text, source/destination linkage and before/after digests. This is visible reconciliation, not an invisible deletion or fake completion. Revalidate source, destination, classification and authorization immediately before effect. Conflicting destination, changed source, missing owner or consequential reclassification stops without mutation. Do not change task history or unrelated files as a side effect.

## Readiness Result and Findings

FlowKit readiness result schema version 1.0 contains `feature_directory`, `state`, `reason_code`, `blocking_ids`, `pending_future_ids`, `criteria`, `source_evidence`, and a stable `resume_action` when blocked. `state` is `ready` or `blocked`; helper errors are bounded nonzero failures rather than empty success reports. Real criteria/evidence arrays cover every actual assessed obligation. Persisted paths are repository-relative. No raw transcripts, secrets or absolute host paths enter evidence.

Each criterion records category (`preparation-quality`, `preparation-review`, `implementation-evidence`, `human-acceptance`, or `unresolved`), owner, due phase, source/item locator and digest, status, expected evidence and evidence references. An item without an existing ID uses exact item text plus occurrence index; ambiguous locators block. Independent-review evidence must identify the reviewer and current reviewed inputs; author self-checks are insufficient where independent review is required.

A readiness finding has stable `id`, `source_path`, `source_item`, `missing_evidence`, `owner`, `correction_kind`, `authority_state`, `due_phase`, and `evidence`. Preserve IDs across corrections, stale records and repeated reports; do not rename a gap to manufacture progress. Ready requires no unresolved preparation findings, current supporting evidence, and zero unchecked items in the unchanged core checklist scan. Future IDs remain pending outside that scan.

Core artifact-analysis findings and Checker readiness findings are separate authoritative sources. The controller combines them for routing without hiding one behind the other's success. The existing strict workflow outcome envelope remains unchanged; readiness detail is a separate workflow output, not undocumented fields injected into that envelope.

## Analyze Correction and Reassessment

Analyze and Remediate must close repairable readiness gaps rather than merely append them to a final report. The first pass is read-only and establishes both artifact and readiness baselines. Subsequent passes use exact current findings and the smallest declared authorized correction route:

| Gap | Correction owner and boundary |
|---|---|
| Built-in specification-quality defect | FlowKit-Specifier; reconcile affected plan/tasks when necessary |
| Plan defect | FlowKit-Planner; reconcile affected tasks |
| Task defect | FlowKit-Tasker; preserve IDs and completed history |
| Missing substantive independent verdict | FlowKit-Reviewer; read-only assessment, never invented by Checker |
| Supported verdict/marker recording | Declared main-task recorder; persist exact current authorized evidence only |
| Reviewed pending future obligation in mixed checklist | Declared main-task recorder; preserve identity, status and relocation provenance |
| Unknown purpose/owner, product/scope/authority decision or unsafe effect | Stop for exact owner/operator resolution; no speculative correction |

Every new delegated step has an exact reviewed assignment. Every mutating step is explicit in the workflow graph. The Checker and artifact assessors do not mutate; recorders cannot invent positive verdicts. Invoke only declared bounded core commands, never another FlowKit workflow. If required owner/recorder authority or native assignment is unavailable, block before effect and name the exact finding and resumption action.

After each correction, rerun fresh core artifact analysis and Checker readiness assessment against current inputs. The controller routes another correction only for safe in-scope work and evidenced resolution of at least one prior gap. A genuinely corrected artifact or a newly supplied required independent verdict can resolve a gap; report writes, checkbox flips, timestamp changes and obligation relocation alone earn zero progress. Retain all unresolved and newly discovered findings.

Keep the existing six assessments: one initial baseline and at most five correction passes. Repeated unresolved findings without substantive progress, failed commands, stale/unsafe evidence, unresolved consequential decisions, unavailable owners or cap exhaustion stop with precise evidence and safe resumption. A clean final assessment may complete; cap exhaustion is not readiness. Analyze is complete for preparation only when artifact analysis is clean, readiness is ready and core's actual checklist gate would pass. It never claims implementation, acceptance or the next workflow invocation.

## Implement Handoff

Separately requested FlowKit Implement runs the same current helper/Checker policy immediately before core `speckit.implement`. Validate active identity and input/evidence freshness; the saved Analyze ready report is evidence, not authority. Changed inputs require fresh assessment. Revalidate the accepted snapshot adjacent to Coder dispatch; mismatched identity, digests, missing review or any unchecked preparation item blocks before core startup.

Ready preparation allows ordinary core Implement to see all preparation checklist items checked and continue through its existing gate. Pending future obligations stay visible outside `checklists/`. Never overwrite core source, templates, installed skills/helpers or checklist semantics; do not use a generic override answer or a prompt instruction to bypass core's gate. Standalone core commands retain current behavior.

A readiness gap found at Implement startup reports its exact blocker and safe Analyze resumption. Implement does not automatically invoke Analyze or inherit its correction authority. This contract changes readiness inside FlowKit; it does not require the superseded `check_prerequisites.py --readiness` capability or a core-owner delivery/pin change.

## Compatibility and Validation

Source definitions, helper logic and production-rendered paths must be tested in disposable consumers before packaging claims. Native launch evidence is separate and retains the original eight-role matrix plus the new Checker in the same three contexts. Current installed workflows and old recovery checkpoints are not hot-upgraded.

| Case | Required outcome |
|---|---|
| Clean artifact analysis and checked preparation with current evidence | Ready; no implementation/acceptance claim |
| Safe author/plan/task gap | Declared smallest-owner correction, then fresh analysis and readiness |
| Required independent review missing | Correct Reviewer route; exact verdict recorded by authorized recorder, then reassess |
| Existing verdict has stale inputs | Block or authorized fresh review; saved ready is invalid |
| Reviewed future obligation mixed into checklist | Authorized traceable relocation; remains pending outside core scan |
| Unknown or ambiguous obligation classification | Exact blocked owner/operator resolution, no blanket exclusion |
| Recorder changes a marker without real evidence | Reject and retain readiness finding |
| Unrelated or unauthorized correction | Stop before mutation; preserve source/destination and unrelated bytes |
| No progress, repeated finding or final continue at cap | Bounded stop, never clean readiness |
| Checker unavailable | Exact native assignment/step blocker, no generic agent or per-run override |
| Artifact changes between Analyze and Implement | Fresh readiness and adjacent digest revalidation before Coder |
| Core startup | Existing unchecked-item gate unchanged; no fake checked future items or `--readiness` flag |

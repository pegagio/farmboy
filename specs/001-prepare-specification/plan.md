# Revised Implementation Plan: Prepare specification

**Branch**: `reboot/2026-10-16/prompt-first` | **Revision**: 2026-10-17 | **Spec**: [spec.md](spec.md)

**Status**: Revised specification and plan explicitly approved by Pegagio for implementation on 2026-10-17. Implementation/independent verification and the authorized local closeout sequence may proceed within scope; remote push is not authorized. Prior evidence remains historical; revised runtime observations and targeted checks are recorded in validation/acceptance.md. Final closeout and human result review remain distinct.

## Outcome and boundary

Keep the one existing Farmboy-owned skill, but narrow its automated responsibility to feature selection, context discovery, draft preparation and an explicit saved handoff. A native Goal succeeds at that handoff. Material questions lead to ordinary `$speckit-clarify`; a settled draft leads directly to human specification review. The completed Goal does not wait for answers, resume around clarification, or stand for human approval. Planning requires explicit specification approval at the review depth the operator chooses.

## Existing capabilities and execution

1. Revalidate project guidance, constitution, roadmap/pointer identity, eligibility and current artifacts. Preserve existing named/eligible selection and negative stops. Interrupted drafting may resume; a completed handoff is not reactivated.
2. Activate only the selected entry/linkage and query bounded cited wiki context through existing capabilities.
3. Resolve current Spec Kit spec/checklist templates and existing feature setup helpers; author the draft and record unresolved choices and quality findings. The full specify command can require interactive answers before it finishes. Do not invoke it and then ignore its instructions or claim it completed. Use the existing supported template/helper drafting path; if necessary capability is absent, report a blocker rather than install or recreate it.
4. Use the installed roadmap-brief capability. An unresolved product choice may be disclosed in a successful draft/handoff; a governing conflict, unsupported draft path or unusable artifact remains a blocker. Passing a complete-spec checklist is not required merely to acknowledge a draft containing explicit questions; report its actual incomplete criteria honestly.
5. Save a concise handoff in existing spec metadata/notes: artifact paths, unresolved topics/limitations and next stage. For a usable ambiguous draft, finish the Goal at clarification handoff; for a settled draft, finish at human review handoff. Verify native completion rather than assert it in prose. If it cannot be confirmed, report incomplete compatibility and stop.
6. Outside the completed Goal, the operator invokes existing clarify ordinarily. Its actual answers flow back into the spec and affected findings/brief through existing commands. Supported focused rounds and early termination remain governed by the installed command/reference. No new Farmboy clarification skill is justified.
7. Clarification completion leads to human spec review, not approval. No plan/tasks command starts until explicit approval. The operator may review deeply or briefly; the agent does not add another approval gate.

## Technical context and machinery assessment

Runtime delivery remains one tracked Markdown skill using the current session/model/effort. Reuse project-local templates, standard feature identity, roadmap/wiki/brief helpers and core clarify. Pending input/handoff stays in existing feature artifacts and conversation. No new controller, database, persistence schema, harness, scheduler, configuration feature, mode switch, per-step delegation or second skill is proposed. Direct draft authoring is a bounded responsibility inside the existing skill, not a copied implementation of clarification. The actual helper interfaces and resolved template were validated during implementation; missing capability remains a stop rather than permission to invent commands.

Changed delivery files after review: `.agents/skills/farmboy-prepare-specification/SKILL.md`, `docs/prepare-specification.md`, and `tests/fixtures/prepare-specification/cases.md`. The existing skill and documentation are revised under the explicit implementation approval. Runtime acceptance still requires the new evidence; source changes alone are not acceptance.

## Verification to perform after review and implementation

Use a real subject separate from the evaluator in a disposable project, with the actual revised skill. Prefer existing app/CLI observation; manual native controls are acceptable. No new infrastructure.

- Ambiguous draft: one invocation selects/authors and saves a clarification handoff. Observe native Goal completion before any answer, with preserved unresolved choices and no further automatic turns; do not mistake a stall for completion.
- Settled draft: observe native Goal completion at human-review handoff without manufactured questions.
- Ordinary clarification: after the completed Goal, invoke existing clarify separately; observe a real saved question and actual wait, supply a clearly test-only answer, inspect incorporation and human-review handoff. The preparation Goal must stay completed.
- Approval boundary: before explicit spec approval, a request to proceed cannot start planning. Clarification completion, Goal completion, silence and test answers are not approval. After explicit test-only approval in the fixture, the planning prerequisite may be recognized; do not actually implement later workflows in this feature’s test.
- Resume/negative checks: preserve existing target, context, changed-artifact and portability protections with proportionate affected-path checks. Any unsupported command/Goal operation is a concrete blocker, not an invented success.

Retain all earlier successful ordinary tests and failed native waiting tests as historical evidence. They do not prove the revised behavior. T014/T022 are superseded, unpassed obligations; new tasks identify the changed implementation and evidence.

## Diagram alignment to review

Diagram planned 022/023 already distinguish clarification/review waits from spec approval and planning handoff. They should distinguish successful automated draft/handoff, ordinary clarification needing human input, and human spec approval. A completed draft Goal cannot authorize planning or release Feature/workspace ownership as if the approved-spec checkpoint existed. The adopted future Diagram ownership boundary releases the drafting owner only after a durable needs-clarification/review-ready handoff; ordinary clarification explicitly acquires ownership before edits and retains it while active between questions. Diagram constitution 6.0.0/roadmap 2.2.0 now give explicit Specifying → Needs clarification/Awaiting spec review, clarification resolved → review, review → Ready for planning only on approval, and review → Needs clarification boundaries. Their future 022/023 storage decisions do not add local state machinery here. Preserve exact reviewed versus accepted-handoff references. Four macro phases, repository-canonical artifacts and later integration authority remain unchanged. Diagram files are read-only in this pass; see [impact assessment](diagram-alignment.md).

## Constitution and review gate

The design preserves mutable premerge flow-back, selected authority, genuine human decisions, simplicity and independent real execution. No constitutional amendment is proposed. The revised review gate has been explicitly satisfied. Execute only approved tasks; independent native evidence is still required before acceptance/closeout, and no push is authorized.

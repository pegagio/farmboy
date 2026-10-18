# Optional Farmboy–Diagram adapter: requirements draft

**Status:** Draft for review, linked from planned Farmboy roadmap entry005. This is not a numbered specification, implementation plan, packaging decision or authorization to build/run the adapter.

## Purpose and readiness

Reduce manual coordination between Diagram-selected work and Farmboy's existing specification, planning and delivery skills. Standalone Farmboy remains independent of the adapter and Diagram.

Local prerequisite004 is verified. Cross-project prerequisites are Diagram029's corrected consumer-repository boundary and reporting interfaces, followed by028's revised claim/start/link contracts.029's whole specification is approved for planning; its report interfaces are not designed yet.028 is paused pending029 and renewed review. This draft can capture requirements now, but it does not claim those interfaces or runtime capabilities exist. End-to-end acceptance requires their actual supported implementations. Diagram029 planning remains separate. [F1, D1–D3]

## Responsibility boundary

The consuming agent/adapter inspects and verifies repositories, canonical identities, workspaces, branches, Git state, artifacts and applicable project rules. Diagram owns claims, recorded execution authority, approvals, transitions and consistency of submitted reports. Diagram core must not inspect or modify consuming repositories, including through registration, read-only inspection, helpers, handoff or integration paths.

References are locators, not permission to retrieve their contents. Diagram's acceptance of a report establishes what it recorded and authorized; it does not independently prove physical files, isolation, current availability or merge effects. No helper or adapter name may move consumer inspection back into Diagram core. [D1, D2]

## Required behavior

These are proposed requirements for later specification and review.

1. **Optional, bounded invocation.** The adapter MUST act only within explicitly selected feature/segment or selection scope. It MUST consume Diagram's current selection and eligibility decisions, not create a competing queue, dispatch fleet or expand into another workflow. Existing standalone Farmboy journeys MUST require no adapter configuration or service. Carry authorized routine controls without making the human orchestrate claim/link internals or repeat settled decisions.

2. **Ownership before preparation.** Once028 is revised and delivered, initial work MUST follow metadata claim → external workspace preparation → association/link → eligible content execution. A preparation claim authorizes setup, not specification/code writes. The adapter MUST verify the actual workspace under project rules and report it; intended paths are not proof. Content work requires accepted association and current executing authority. One owner per feature is mandatory; independent features may run in isolated workspaces. [D1–D3]

3. **Consumer-side verification.** The agent/adapter MUST verify the relevant repository/workspace/branch/input/artifact facts itself, preserve unrelated committed, staged, dirty and untracked work, and supply attributable observations through the eventually approved Diagram interfaces. Unknown observations MUST remain unknown. Diagram validates reported canonical facts and current records; incorrect reported identities are not proof of physical isolation. No certificate, attestation service or parallel report ledger is required.

4. **Use existing Farmboy external entries.** The adapter MUST supply selected identity, intent, segment, accessible authoritative Git context, artifact references and applicable authority/approval evidence. Farmboy MUST execute the requested existing skill without repeating roadmap selection/activation. The adapter MUST establish the conventional workspace/pointer association before helpers; existing helper persistence must not silently retarget or rewrite it. No fixed context packet, new fit brief or provenance register is required. [F1, F2]

5. **Respect current meaning and human decisions.** Existing Git constitution, direction and feature artifacts remain authoritative for project rules/context. Material missing, conflicting or stale input MUST produce a specific question before dependent work. Unchanged applicable approval MUST remain usable without repeated approval. Changed meaning requires affected human review. Diagram-recorded approval and its applicability to actual artifact contents are distinct checks; neither supplied references nor successful execution creates approval.

6. **Preserve segment handoffs.** Each run MUST return actual work, feature/request/segment association, artifacts/evidence, checkpoint or current working state, remaining input/blockers and next permitted action. Uncommitted bytes MUST identify their base/state rather than masquerade as a committed checkpoint. Historical reviewed checkpoints, latest accepted handoff and current artifacts MUST remain distinguishable.

7. **Release at human boundaries.** After a durable handoff awaiting a later human step, the adapter MUST apply the supported handoff/release transition before idling, confirming Diagram's recorded outcome. It MUST NOT leave a preparatory claim as an extra retained lock. Later clarification/continuation requires separately established current authority; an active interactive clarification retains authority as the coordination contract prescribes. Farmboy returning notes alone does not acquire, release or transfer ownership. A blocked dependency must not prevent an otherwise authorized truthful release. [F1, D1–D4]

8. **Truthful Goal and feature outcomes.** A native Goal MAY complete only through exposed supported controls at its entire explicitly bounded, durably saved endpoint, with actual completion readback before a human wait. A permitted INCOMPLETE-for-input handoff can complete automation while delivery stays incomplete. Answers/continuation occur ordinarily outside that completed Goal. Unknown technical failures, unavailable controls and unmet delivery-only objectives MUST NOT become successful handoffs. Goal completion never implies Diagram result acceptance, approval, delivery, verification or integration.

9. **Revalidate changed authority and input.** Before dependent work and result submission, the adapter MUST inspect current Diagram authority/input/dependency/approval conditions and verify relevant local facts. Stale or superseded authority MUST NOT be reused. Changed upstream accepted input requires responsible reassessment and affected flow-back; routine applicability is not automatic semantic independence. Preserve otherwise permitted asynchronous specification/planning without inventing an upstream-integrated gate. [D1, D3, D4]

10. **Report and resume without duplicate effects.** Submit only actually observed outcomes through supported Diagram operations, retaining applicable ownership/revision/operation guards. Distinguish local execution from accepted coordination recording. An uncertain response MUST remain uncertain until supported inspection resolves it; exact accepted retries must not repeat Farmboy or Git effects. Resume only missing/affected work and present an intact pending review rather than replaying it. Ownership replacement remains explicit, with preservation, stopped-writer confirmation and stale-owner fencing; no timeout takeover, process control, cleanup or recovery framework. [D1–D4]

11. **Keep integration separate.** Delivery MUST retain verification/convergence, coherent documentation and the scoped local commit, then stop for human result/UAT review. Integration requires explicit applicable human permission, current project branch/target/check/instruction policy and a separately authorized external executor. Missing/conflicting policy stops dependent integration. Honor required explicit review of destination instruction/policy changes before effect; never silently replace governing instruction sources. The adapter MUST NOT infer merge/push authority, select executor placement or perform integration merely because delivery or review succeeded. Diagram serializes reported repository/target keys and records authorized outcomes; integration receipts stay in its database, referencing actual Git checkpoints, without receipt-only project commits. Only integration merge freezes feature meaning. [F1, D1, D4]

## Use cases and review boundaries

| Selected work | Farmboy endpoint | Required next boundary |
|---|---|---|
| Prepare a specification | Saved draft/checklist; Needs clarification or Awaiting spec review | Release the completed preparation run; separately authorize ordinary clarification or human spec review |
| Clarify or revise | Genuine answers/current artifacts; Awaiting spec review | Explicit applicable whole-spec approval before planning |
| Prepare implementation plan | Complete proposal/tasks and fresh passing analysis, or truthful input/blocker handoff | Human full-plan review before delivery |
| Deliver approved work | Verified/converged local candidate, scoped commit and actual evidence; Awaiting result review | Explicit human result acceptance; integration permission remains a distinct explicit decision |
| Resume after input or changed upstream work | Preserved answers/work, current authority and affected reassessment | Return to the affected review when meaning changed; no duplicate selection or replay |

These are behavior boundaries, not proposed command names, report fields or lifecycle/schema designs.

## Acceptance requirements

- Independently observe an actual adapter/agent invoking the installed Farmboy skills with the supported corrected Diagram interfaces and disposable real repositories/Git/coordination state. The executing session MUST be separate from its evaluator; simulations alone cannot establish end-to-end acceptance.
- Demonstrate the full selected-work lifecycle through genuine clarification, explicit spec/plan/result decisions, required repair, local delivery commit and human handoffs. Label test-driver answers and fixture approvals TEST ONLY; they authorize no real project work.
- Exercise external entry for all three skills, standalone regression for all three, no competing ownership, permitted independent-feature isolation, stale authority/input, missing context, changed approvals, interruption/resume and no duplicate effects. Observe ownership release at saved human waits and separately authorized continuation.
- Prove the consumer agent performs relevant repository verification while Diagram operates without consumer repository/Git access. Distinguish actual repository observations from Diagram's report-consistency checks and recorded decisions.
- Verify actual committed delivery after the commit exists; never require a future closing commit to prove its own preconditions. Report observed, simulated, excluded and unobserved cases separately. No production reset, live integration or push is implied by test authorization.

## Open decisions and dependencies

- **Diagram029:** approved report/assessment interfaces, supported native interactions and representation/version changes remain design work in029. Do not invent exact commands, JSON fields or persistent structures here.
- **Diagram028:** revise and review claim/link/run contracts against029 before relying on their admission, release or retry behavior. Earlier direct-inspection planning details are not a current implementation contract.
- **Adapter packaging and invocation:** skill, command, helper or other placement is undecided; no service, scheduler, fleet or installation dependency is selected.
- **Native mapping:** map each Farmboy outcome/human wait to the reviewed Diagram operations once available; do not introduce a parallel state model.
- **Integration executor and project policy:** executor placement is separate; actual projects supply their own target/branch/check policy and explicit permission. This adapter requirement does not choose an executor.

No numbered specification, implementation plan, runtime implementation, automatic authorization, new store/attestation/ledger/accounting/recovery framework, merge or push follows from this draft.

## Sources and scope of inspection

Reviewed working documentation on2026-10-18; Diagram source status does not imply runtime compliance. Current029 supersedes consumer-inspection obligations in older coordination contracts; those contracts supply retained coordination semantics only.

- **F1:** [Farmboy004 workflow contract](../specs/004-align-diagram-handoffs/contracts/workflow-handoffs.md), especially external entry, outcomes, ownership and helper no-write clarification.
- **F2:** [Farmboy workflow handoff guide](workflow-handoffs.md) and [004 specification](../specs/004-align-diagram-handoffs/spec.md).
- **D1:** `~/Documents/Codex/2026-10-16/task-8/diagram-029/specs/029-consumer-repository-boundary/spec.md` (approved for planning; report interfaces remain undesigned).
- **D2:** `~/Documents/Codex/2026-10-16/task-8/diagram-029/docs/architecture/consumer-repository-boundary.md`.
- **D3:** `~/Documents/Codex/2026-10-16/task-8/diagram-028/specs/028-feature-start-enrollment/spec.md`, its pause notice and `clarifications.md`; prior plan/tasks are paused, not adopted here.
- **D4:** `~/Documents/Codex/2026-10-16/task-8/diagram-029/docs/architecture/contracts/`: `feature-queue-segments-v2.md`, `feature-delivery-v3.md`, `feature-integration-v4.md`, read subject to029's boundary correction.

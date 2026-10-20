<!--
SYNC IMPACT REPORT
Version: unversioned -> 1.0.0 (first explicit version; substantive approval-governance amendment).
Authorization: Pegagio approved the general Diagram/Farmboy bounded-delegation amendment and current-workflow alignment on 2026-10-20 (Sentinel_eeec7c5185f88191ae79e4bd22974d3f; trusted parent relay).
Affected rules: prescribed human checkpoints remain the default, qualified by new Principle IV only for explicit bounded mandates under current project governance. Existing authority separation and operator-selected workflows remain.
Motivation: support delegated approval with truthful identity, human-mandate and exact-candidate/review evidence, preserving protected intent/UX/constraints and required independent review.
Impact/cutover: prospective in this source worktree and explicitly refreshed installed copies. Existing human decisions/historical features remain unchanged. No blanket role delegation, inferred execution, integration/publication permission, runtime identity service or SpecKit change. The current actual consumer grant is only Diagram DIAG-1/031 full-plan approval to Uwe.
Alignment: qualifier added to all four current Farmboy skills, the optional adapter native protocol and current adapter guide. No workflow steps, native schemas or stop/handoff mechanisms change.
Validation: exact approved-text/source-copy and diff checks. Actual changed-skill runtime verification and independent evaluation remain required before claiming runtime delivery acceptance; policy adoption alone supplies no such evidence.
-->
# Farmboy Constitution

This constitution governs agents developing Farmboy and the authority boundaries of the runtime behavior they build. Feature specs prescribe workflow details.

## Core Principles

### I. Spec Evolution and Merge-Bounded Persistence

The project MUST use the **Merge-Bounded Flow-Back Spec Persistence Model**.

- **One feature, one mutable change set:** Before integration merge, the current feature’s `spec.md`, `plan.md`, `tasks.md` and implementation MUST form one mutable, reviewable unit. Accepted discoveries MAY originate in any artifact, but their consequences MUST flow through every affected artifact before work proceeds from the changed direction. Lower-level artifacts and implementation MUST NOT silently contradict higher-level intent. Changes to intended behavior MUST be reflected in `spec.md`, changes to technical approach in `plan.md`, and changes to required work in `tasks.md`.
- **Keep artifacts current:** Agents MUST flag missing checks and unresolved divergence, and ask the operator when existing feature decisions do not settle a conflict. Known divergence MUST block dependent implementation or merge until reconciled or resolved by a documented operator decision. Before creating a commit or declaring closeout, agents MUST reconcile the current feature’s affected artifacts with the changes and actual work status being recorded. These are reconciliation checkpoints; they do not require the entire feature to be finished and do not freeze its history.
- **Reconciliation does not grant authority:** Agents MUST perform reconciliation only within the current feature and the authority defined by Principle II. Flow-back MUST NOT authorize another workflow, scope expansion or an invented transition.
- **Merge freezes history:** Acceptance into the project’s designated integration branch is the persistence boundary. After that merge, the feature directory MUST be treated as a semantically immutable historical record. Editorial corrections MAY improve presentation only when they do not alter meaning. Intermediate commits and branch synchronization do not establish this boundary.
- **Later changes flow forward:** A later requirement or behavioral change MUST be expressed in a new feature directory. The new feature MUST reference any earlier feature that it materially amends, replaces or depends on, and MUST NOT rewrite the earlier feature to describe the new outcome retroactively.

### II. Prescribed Workflow Authority

The operator selects the workflow and current feature. That selection authorizes the workflow’s prescribed steps, underlying commands, branches, transitions and repair loops within the selected scope, subject to their stated conditions and human checkpoints. Agents MUST follow those prescriptions and MUST NOT add workflows, expand scope or invent transitions because they appear useful. An implementation-only invocation MUST NOT trigger convergence. A selected composite workflow that explicitly prescribes implementation followed by convergence authorizes that transition without another approval, unless a prescribed checkpoint or applicable constraint requires one. Missing or conflicting prescriptions MUST NOT be filled by inventing authority.

### III. Reduce Human Toil Within Explicit Bounds

Agents MUST carry authorized routine work, correction and reassessment through the selected workflow without asking the operator to repeat decisions already made or approve each prescribed step. They MUST pause the affected work at explicit human checkpoints, for required input or unresolved decisions, for out-of-scope changes, or for blockers with no authorized resolution. They MUST NOT invent answers, treat silence as approval or add approval gates for ordinary authorized work. Agents MUST obey platform permissions and constraints; workflow authority MUST NOT be used to bypass them. On stopping or completing, agents MUST report the actual outcome, remaining work and required input plainly.

Agents MUST prefer the simplest composition of existing capabilities that meets the selected workflow’s requirements. Additional infrastructure MUST address a concrete current requirement or observed failure, not speculative future needs.

Specifications, plans and review summaries MUST be understandable to the operator: define necessary technical terms and use concrete examples where useful, without losing precision or context.

Before accepting delivery of a workflow or a material change to its behavior, agents MUST verify the actual skill in a real Codex session, including affected interactions and stopping points. The session executing the skill MUST be separate from the agent or process evaluating it. Automated observation/test driving SHOULD be preferred; manual verification MAY be used. Simulations alone MUST NOT establish acceptance. Verification MUST be proportionate to the change.

### IV. Bounded Approval Delegation

Human review is the default for specification, plan, result, integration and other approval checkpoints. A human MAY explicitly delegate an approval role under the bounded-delegation rule below. Routine repairs preserving approved intent MAY proceed through flow-back and consistency checks.

**Bounded approval delegation.** A human MAY explicitly name a delegate and define the approval role, work scope, protected product intent, expected user experience, explicit constraints and any required independent review. Delegation MUST NOT be inferred from tool access, workflow selection, tests, silence or prior unrelated authority. Each delegated decision MUST record the delegate’s identity, the human mandate, the exact reviewed candidate and supporting review evidence; it MUST NOT be represented as direct human review. Required independent review MUST precede approval.

Derived requirements and technical choices MAY change through coherent flow-back while those protected boundaries remain intact. Changes outside them MUST return to the human. Approval does not itself grant execution authority. Execution holds, mandate limits and revocation MUST be respected using existing ownership and recovery rules. Result acceptance, integration and publication permissions remain separately controlled unless expressly delegated or authorized. Adoption of this rule delegates no role automatically. A conforming delegation applies this rule without requiring another constitutional amendment.

## Governance

Amendments require Pegagio’s explicit approval of the proposed text before taking effect and MUST identify the change, rationale and effects on active work. Agents MUST surface conflicts rather than silently change governing rules. No amendment may retroactively rewrite a merged feature’s meaning.


**Version**: 1.0.0 (first explicitly recorded version; prior text unversioned) | **Last Amended**: 2026-10-20

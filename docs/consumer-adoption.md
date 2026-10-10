# Consumer Adoption Review

Use this runbook after installing or refreshing FarmBoy when a project wants to assess the Merge-Bounded Flow-Back Spec Persistence Model. Installation and refresh make reusable components available; neither changes project-owned governance nor establishes adoption.

The runbook is an operator-directed manual procedure. An agent may inspect files and draft a proposal when the operator explicitly asks, but it must leave constitutional decisions, material conflict resolution, and workflow invocation with the operator.

## Inputs and scope

Choose one consumer project and one feature-work scope. Record the project's actual designated integration branch, the governance files that establish project rules, and the active agent guidance files that apply to the work. Include nested instructions and overrides. Do not assume `main`, `develop`, a root `AGENTS.md`, or a README is authoritative without evidence.

Copy [the adoption review worksheet](templates/adoption-review.md) into a project-owned review location. Use project-relative paths and headings or line references. Keep expected fixture results separate from observations. The reusable [model proposal text](merge-bounded-flow-back.md) is a starting point; preserve equivalent or stricter project wording when it satisfies the complete rule.

## Review each model rule

For M1–M5, record separate evidence in governance and active agent guidance. Use `compatible`, `missing`, `conflicting`, or `uncertain`; cite the applicable text and explain why it satisfies, fails, or may not govern the selected scope. README text can give context but cannot establish active agent guidance.

| Rule | Required meaning |
| --- | --- |
| M1 | Before integration, `spec.md`, `plan.md`, `tasks.md`, and implementation form one mutable change set. |
| M2 | Accepted discoveries flow to the affected artifacts and are reconciled across the set before work continues from the changed direction. |
| M3 | Agents flag missing checks and unresolved divergence, recommend relevant operator-invoked checks, and do not invoke workflows or underlying commands independently. Known divergence blocks implementation or merge until reconciled or explicitly resolved. |
| M4 | Acceptance into the project's designated integration branch freezes feature meaning; editorial corrections cannot change semantics. |
| M5 | Later behavioral changes use a new feature directory and refer to earlier features they materially amend, replace, or depend on. |

An equivalent or stricter rule counts only when its evidence satisfies the entire required meaning. Cite all passages when the rule is distributed across files. If the branch, authority chain, semantics, or guidance applicability is unknown, investigate inspectable project evidence or ask the operator; retain `uncertain` until resolved.

## Propose, decide, and apply

If any required evidence is missing or conflicting, prepare a minimal exact patch. Show the before and after text, target paths, affected rule IDs, rationale, and baseline digests. Explain conflicts without treating the consumer's existing rule as invalid. Follow the project's own constitution-amendment procedure, including any required version or date updates.

The proposal does not authorize itself. Record the operator's `accept`, `decline`, or `defer` decision, the reviewed patch digest or exact subset, and any decision conditions. Apply only the accepted patch after confirming that each target still matches the reviewed baseline. If a baseline changed, discard the stale patch, reinspect, and present a revised proposal for review. A decline or deferral makes no governance or guidance change. Do not create a missing constitution without explicit approval.

After accepted edits, reread each affected file, recompute final digests, and rebuild the M1–M5 matrix. Preserve unrelated project rules and local edits. Record the result and remaining operator decisions in the worksheet.

## Outcomes

- **confirmed**: Every rule has compatible evidence in both governance and active agent guidance, the integration boundary and guidance applicability are established, and required decisions for applied edits are recorded.
- **partial**: Required evidence is absent or incomplete, with no unresolved material conflict or uncertainty. A deferred proposal for missing rules is partial.
- **declined**: The operator explicitly declined the proposal. Report observed evidence and retain conflicts in the matrix without claiming adoption.
- **unresolved**: A material conflict, uncertain compatibility, ambiguous authority or integration boundary, or changed proposal baseline remains unsettled.

An explicit decline takes precedence; otherwise unresolved evidence takes precedence over partial evidence. Only complete compatible evidence permits confirmed. `defer` is a decision, not an outcome: missing evidence is partial, while a conflict or uncertainty is unresolved.

## New installation, refresh, and removal

After a new install or refresh, begin a fresh inspection of current consumer files. Refresh does not overwrite project-owned guidance and an old confirmed worksheet cannot be carried forward as current evidence. Record the installed component identities, versions, and digests separately from the runbook/template source revision or digest. Test these operations only in a disposable initialized consumer; do not remove FarmBoy from a real project as part of validation.

Removal affects installed FarmBoy components according to the installation guide. It does not authorize deleting the consumer's constitution, active guidance, merged feature history, or adoption review. Check hashes before and after install, refresh, and removal to demonstrate preservation.

## Manual agent prompt

An operator may copy this prompt into a selected consumer task:

> Review this project's adoption of the Merge-Bounded Flow-Back model using the reviewed consumer-adoption runbook and worksheet. Inspect active agent guidance, applicable governance, and the project's designated integration boundary. Map M1–M5 to evidence in both guidance and governance, preserving equivalent or stricter project wording when each complete rule is satisfied. Prepare minimal exact patches for missing rules and show all proposed changes, affected paths, rationale, and baseline digests before asking for decisions. Do not apply constitutional amendments or resolve material conflicts without the operator's explicit decision on the exact patch. Recheck baselines before applying accepted changes, then reinspect and report confirmed, partial, declined, or unresolved with final evidence and limitations. Flag missing checks and recommend a relevant FarmBoy workflow for separate operator invocation; do not invoke a workflow or its underlying command.

## Evidence limits

Structural tests and synthetic cases verify document contracts and expected classifications. They do not prove semantic equivalence, a live agent's behavior, adoption outside the tested consumer, publication, or compatibility with stock Spec Kit. Record manual and live-agent observations separately, including actual decisions, source coordinates and digests, tested CLI version, component provenance, outcomes, deviations, and limitations. Do not describe expected fixture results as observed adoption.

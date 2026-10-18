# Optional adapter entry contract

This proposed agent-readable interface defines one optional skill, not a new CLI/API or serialized authority packet. Exact native fields and operations are in [native mapping](native-mapping.md). All design remains subject to full-plan review.

## Ordinary intent and established project routing

The operator can say “start feature12,” “clarify this feature,” “plan this feature” or “deliver this feature.” The agent resolves one feature and one selected segment from ordinary intent plus explicit project instructions. It must not require an adapter skill name, a “use Diagram” phrase or confirmation of an already unambiguous route. Product questions and prescribed human review/input stops still apply.

On a deliberately Diagram-enabled route, the agent invokes the optional `$farmboy-diagram-work` internally with the resolved project/feature/segment, selected existing store/config and authorized consumer context. Initial preparation claims/verifies/links before content; later clarification/planning/delivery acquires current applicable authority and uses existing external skills. Applicable spec/full-plan decisions remain required. Neither the routing declaration nor an example grants ownership or starts a later segment.

An established standalone route uses the existing standalone Farmboy entry. Tool/skill presence alone never enables Diagram. Missing/ambiguous routing or selection asks for targeted input before effects. Missing capability on an enabled route is a precise limitation, never a silent fallback, install, upstream patch, migration or rebind.

## Farmboy entry checks and inner return

All three Farmboy-owned entries check project routing before effects, including direct invocation. Established standalone continues without Diagram; missing/ambiguous routing asks targeted input; unavailable enabled routing stops without fallback. Enabled direct entry without a current adapter invocation hands the selected segment to the adapter once and propagates its return, never subsequently executing the body again.

For an already-current inner adapter invocation, use the adapter/reference's current native verification: selected project/feature/segment, owner/session/run/epoch, applicable input/approvals and consumer association must match. Only then run the existing external body. A flag, foreign context or historical receipt is insufficient; stale/unverified context stops dependent effects, not automatic reacquisition. No recursive wrapper, duplicate claim/report or new context envelope/store is permitted.

Inner Farmboy returns local outcome/artifacts without releasing Diagram authority or completing the wider Goal. One adapter invocation owns the whole saved endpoint, accepted recording/release and supported native completion/readback. Standalone behavior is retained after route selection. Actual ordinary/direct-entry tests establish agent adherence; no absolute interception guarantee is implied. Diagram-specific fields/protocol remain here and in the adjacent native mapping, rather than copied into three workflow bodies.

## Deliberate project opt-in and scope

The exact proposed enabling action is in [plan](../plan.md#project-routing-and-deliberate-opt-in): the operator adds a bounded routing paragraph to the specifically identified consumer project's existing `AGENTS.md`, or separately authorizes an agent to make that exact edit. This feature supplies the example in Farmboy's own guide; it neither edits arbitrary consumers nor adds a configuration framework. The skill must already be available through existing supported project/host mechanisms; absence is input, not permission to patch another software project.

005 implementation must remain within Farmboy's optional adapter, minimal routing checks in its three own entries, its own documentation/guidance and focused acceptance fixtures. It must use existing external APIs/skills without changing Spec Kit, Diagram or any other external software project's source, skills, hooks, configuration or implementation. A required external software patch is an exact compatibility blocker, not scope to repair elsewhere. Deliberate consumer-project opt-in guidance is separate from external software implementation: it may be applied only to the specifically identified consumer instruction file with explicit authorization; availability, route selection or this plan alone grants no external edit permission. No external enablement/edit is performed by this planning task. Opt-in does not launch a segment, approve an artifact, grant a native Goal, or override explicit restrictions.

## Segment-launch checkpoint authority

Explicitly launching one adapter segment includes disclosed authorization for necessary feature-scoped checkpoint commits with normal project hooks. Merely selecting or viewing a feature grants no commit authority. Explicit user restrictions/overrides remain controlling; this authority grants no merge or push. Stage only the selected feature changes: preserve unrelated staged, unstaged and untracked work, never sweep the entire workspace, and stop for targeted input if safe isolation cannot be established. Reconcile affected artifacts, verify the exact staged scope and inspect the resulting committed checkpoint. Never disturb unrelated index entries to make a commit or native cleanliness check pass. Normal hooks remain enabled; their failure or a failed commit is incomplete work. This rule applies to each explicitly launched segment, including ordinary clarification, and does not automatically launch any later segment.

## Responsibilities and boundaries

The skill inspects current Diagram records, prepares native request transport from actual consumer observations and invokes exactly the selected existing skill in the same model/effort/session. It neither delegates runtime steps nor installs its dependencies. The consuming agent follows actual project rules for repository/workspace/artifact checks. The standard pointer must be prepared before core helpers, with lexical persistence equality verified. A caller must not use a temporary pointer overwrite or patch helpers to force compatibility.

Farmboy returns a local artifact endpoint. The adapter then handles actual native report acceptance/release using current guards; it does not claim that Farmboy mutated coordination. Ordinary human decisions are separately explicit and applicable to exact content. When a native review record is explicitly requested with an actual human decision, use existing review-record semantics; never synthesize approval from task completion, test-driver claims or a planning invocation.

## Return and failure examples

A successful draft return identifies feature/segment, actual spec/checklist paths, accepted native handoff and released run, unresolved topics or none, checkpoint/base state and next ordinary clarification or human review. A planning return adds all design/tasks/fresh analysis and Awaiting full-plan review. A delivery return adds actual commit/verification/convergence/closeout evidence and Awaiting result review.

A saved draft whose required checkpoint is prevented by an explicit restriction or unsafe isolation returns INCOMPLETE coordination recording: actual local paths/base/dirty state, exact restriction or isolation input needed, actual release outcome and separately selected ordinary next action. A failed hook/commit is reported as the actual blocker. It never fabricates a checkpoint, sweeps unrelated work, or undoes/deletes the draft. Later authorized continuation rechecks current authority/input and reuses intact work; ordinary authorized checkpoint commits need no repeated permission request.

A lost response returns uncertainty until supported operation inspection establishes accepted/absent/conflicting outcome. Exact accepted replay skips external work and never reacquires a historical run. Native failure or incompatible Goal objective stays a technical limitation, never a fabricated successful input handoff.

Every human boundary saves/readbacks actual current artifacts and actual coordination outcome; if the entire separately selected native Goal matches and is satisfied, complete/read it through exposed supported tools before waiting. No automatic Goal activation or restarted preparation, no next segment and no plan approval follow this return.

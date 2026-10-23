# Existing planning guidance contract

This documents how to present the existing interface, not a new API.

- State when assessment.conditions is required and what it means. Tie request/assessment approval IDs to the actual historical spec decision and verify artifact/phase applicability; actual authorization must support claims. Do not copy conditions blindly, insert a generic placeholder or infer an unrelated approval.
- A condition-free approval does not require a synthetic conditions array. Existing identity/actor/rationale/evidence requirements still apply.
- The worked example uses one declared TEST ONLY context and parseable JSON. Illustrative IDs, commits and prose are not reusable authority. No unfilled token may be represented as a valid real request.
- The planning offer uses --request-file and only its allowed fields: contract/revisions/dependencies, owner/session, pinned_handoff, approval_id, assessment, and required verified expected_head/repository_id/instance_id/worktree_key/workspace_clean for the linked repository. Do not include workspace, branch, segment, purpose or discovery_selected in that offer.
- For acquire, supply actual workspace/branch, segment plan and purpose planning-handoff; discovery_selected is true only for a real discovery route and is otherwise omitted. Preserve all other current guards. The example may show this delta without duplicating a large request.
- An accepted offer remains read-only and creates no claim/run. Correcting offer input before first acquire is distinct from retrying a rejected acquire. The latter stays prohibited within a launcher invocation; uncertainty is inspected before effects.

Focused regression prevents loss of the conditional rule, meaningful-assessment warning, action-specific example shape, preflight and abort boundary. Real-session observation covers the changed preflight instructions only; the native guard, generic planning body and launcher controller are unchanged and must not be patched or reimplemented.

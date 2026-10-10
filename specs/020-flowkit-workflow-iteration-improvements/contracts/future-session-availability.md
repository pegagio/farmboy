# Contract: Prepared Projects, Future Chats and Native Availability

This contract covers FR-015–FR-019 and the agent portion of FR-022. It preserves Feature 017 consumer ownership, excludes capacity/cleanup remedies, and records startup limitations without guaranteeing lifecycle control.

## Table of Contents

- [Preparation and Propagation](#preparation-and-propagation)
- [Native Matrix](#native-matrix)
- [Failure and Recovery](#failure-and-recovery)
- [Evidence Boundaries](#evidence-boundaries)

## Preparation and Propagation

Supported preparation uses the existing documented CLI/PyYAML prerequisites, current catalog install/install-missing and tracked definitions. Refresh updates cached defaults while preserving consumer copies. Explicit reset remains the only supported selected-copy replacement operation; this feature does not request a reset. All eight source-checkout `.codex/agents/` definitions are tracked. Ignored `.agents` skills, component payload and ownership records propagate through reviewed `.worktreeinclude` entries in local Codex-managed worktrees.

Do not add an entire `.codex/` copy rule or a setup script without evidence of a specific gap. A consumer's native files/config/settings/unrelated agents remain theirs. Needed supported project-config changes require exact visible patch and explicit operator approval. Plain Git worktrees, remote contexts and fresh clones retain their documented separate preparation needs; no universal acquisition promise is inferred.

Preparation inventory validates current package/default source metadata, readable identities, installed skill/controller records, workflow/extension payload and declared assignments. Existing package/source digests establish provenance. Consumer definitions may differ by customization; presence/preservation does not imply equality or effective runtime settings. This contract adds no content ownership hashes or merge algorithm for those copies.

Feature 020 may validate this preparation using the existing supported development-snapshot path in the source checkout or a disposable initialized consumer. Record its unreleased status and actual source/package digests; propagate that prepared payload through the existing supported worktree mechanism. Production release packaging follows feature Closeout as a separately requested activity and is not a prerequisite for the native matrix. Neither delivery mode substitutes for the required exact native launch evidence.

## Native Matrix

Required context kinds are prepared-checkout-future-chat, prepared-worktree-future-chat and new-worktree-first-chat. Each requires all exact names:

| Role | Native requested agent_type |
|---|---|
| Roadmap | FlowKit-Roadmap Agent |
| Specification | FlowKit-Specifier |
| Planning | FlowKit-Planner |
| Tasking | FlowKit-Tasker |
| Artifact review | FlowKit-Reviewer |
| Implementation | FlowKit-Coder |
| Code review | FlowKit-Code Reviewer |
| Wiki | FlowKit-Wiki Curator |
| Additive readiness assessment (approved 2026-10-06; source delivery pending) | FlowKit-Readiness Checker |

Each role receives a bounded read-only probe request that acknowledges exact identity and scope; it must perform no workflow work. The controller records actual exact native request and returned response/error. A friendly task name/label is insufficient. Preserve the original eight-role cases and add the new Checker in each context after its reviewed source delivery, sequentially as available, never substituting generic agents. The original 24 cases plus three additive Checker cases are validation work explicitly authorized by the operator, not a replacement centralized preflight framework for Feature 016.

Example failed case:

```json
{
  "case_id": "first-worktree-chat-reviewer",
  "context_id": "new-worktree-first-chat",
  "requested_agent_type": "FlowKit-Reviewer",
  "state": "failed",
  "evidence": [],
  "error_summary": "Definition present; exact agent_type unavailable in exposed native interface",
  "resume_action": "open-fresh-chat-in-prepared-worktree",
  "effective_settings": "unavailable"
}
```

A real case records source evidence and separately establishes whether that resumption was tested/supported. The example does not assert that fresh chat always repairs discovery.

## Failure and Recovery

| Condition | Report and allowed next action |
|---|---|
| Payload absent before chat | Name missing payload/current installation state; supported project preparation may be separately authorized |
| Present files, exact interface unavailable | Record interface limitation and affected name/context; stop workflow preflight; do not infer missing installation |
| First chat starts before preparation | Retain observed ordering and failed/not-tested cases; causal loading behavior remains hypothesis |
| Later fresh chat succeeds | Record separate success and tested resumption; retain first-chat failure and unmet first-chat outcome |
| Duplicate/invalid identity or unsafe file path | Preserve current files; owner resolves specific identity/config conflict before retry |
| Native thread-limit error | Record exact sanitized failure/partial matrix; no capacity increase or child cleanup; later retry requires operator-directed supported context |
| Client identity/effective settings unavailable | Mark unavailable/unverified; do not invent version or infer settings from TOML |

Only established supported recovery belongs in user guidance. No current-chat reload, per-chat install, automatic fallback or guaranteed first-chat startup order is introduced. Manual workflow fallback remains distinct from passing native preflight and does not transform a failed exact launch into success.

## Evidence Boundaries

Prepared inventory, delivery tests, no-op transport, exact native response and effective settings are different evidence levels. Context records must describe whether files were demonstrably present before chat initialization or timing was unknown. Runtime timestamps may be sanitized into ordering observations without exporting host paths/transcripts. Original historical capacity feedback remains independently unresolved; future availability success cannot claim its cause fixed. SC-005 retains all 24 original-role successes and now requires three additional exact Checker successes; failures/not-tested stay unmet rather than being averaged away.

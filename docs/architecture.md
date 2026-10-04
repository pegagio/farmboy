# Boundary and Adapter Model

Spec Kit Flow is the generic source authority for reusable workflows, accepted presets, portable feedback capture/report, and maintainer-only feedback intake. The generic source contains no Diagram executable, database, registration command, canonical-state mutation, or runtime service dependency.

The Diagram may consume a pinned Spec Kit Flow release through a separately versioned adapter. That adapter is not part of this repository's generic bundle, and adapter-specific feedback needs its own future authority decision.

Workflow source packages remain manually reviewable and independently adoptable. The generic feedback protocol provides evidence and a proposed next action only; an accepted refinement re-enters the ordinary Spec Kit Flow specification, planning, task, and implementation flow.


## Reviewed Agent Defaults

Canonical `agents/flow-kit/` definitions form the separately versioned `flow-kit-agents` package pinned by the bundle. The catalog stages validated package provenance and defaults in `.specify/flow-kit/agent-defaults/`, independently of controller-skill ownership. Bundle install adds missing copies, refresh changes only the available package, explicit reset replaces manifest-selected targets, and removal preserves consumer copies. Native TOML alone owns model/effort; workflow/controller metadata owns exact role assignments. [Installation guidance](installation.md#agent-configuration-and-consumer-copies) lists settings and lifecycle commands. Package checks, supported values, exact native selection and observed effective settings are separate validation evidence.

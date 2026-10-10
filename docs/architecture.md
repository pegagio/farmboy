# Boundary and Adapter Model

FarmBoy is the generic source authority for reusable workflows, accepted presets, portable feedback capture/report, and maintainer-only feedback intake. The generic source contains no Diagram executable, database, registration command, canonical-state mutation, or runtime service dependency.

The Diagram may consume a pinned FarmBoy release through a separately versioned adapter. That adapter is not part of this repository's generic bundle, and adapter-specific feedback needs its own future authority decision.

Workflow source packages remain manually reviewable and independently adoptable. The generic feedback protocol provides evidence and a proposed next action only; an accepted refinement re-enters the ordinary FarmBoy specification, planning, task, and implementation flow.


## Reviewed Agent Defaults

Canonical `agents/farmboy/` definitions form the separately versioned `farmboy-agents` package pinned by the bundle. The catalog stages validated package provenance and defaults in `.specify/farmboy/agent-defaults/`, independently of controller-skill ownership. Bundle install adds missing copies, refresh changes only the available package, explicit reset replaces manifest-selected targets, and removal preserves consumer copies. Native TOML alone owns model/effort; workflow/controller metadata owns exact role assignments. [Installation guidance](installation.md#agent-configuration-and-consumer-copies) lists settings and lifecycle commands. Package checks, supported values, exact native selection and observed effective settings are separate validation evidence.

Each delegated role is limited to its named artifact or eligible task scope and its existing correction route. Authors complete command-required self-checks and quality checklists; these do not replace a separate assigned reviewer, who assesses the named evidence independently. A child needing operator input returns one structured question to the main task, which presents it to the operator and relays the answer to that same child. A blocked child reports the exact blocker and safe resumption action. Children do not expand authority, dispatch another workflow or undeclared phase, make consequential decisions, integrate Git, or claim acceptance; the controller retains gates and phase dispatch. See the [canonical agent definitions](../agents/farmboy/manifest.yml), [agent package contract](../specs/017-farmboy-agent-configuration/contracts/agent-package.md), and [delivery command contract](../specs/017-farmboy-agent-configuration/contracts/agent-delivery-cli.md).

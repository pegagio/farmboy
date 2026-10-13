---
title: Diagram adapter boundary
type: decision
sources: [S001, S003, S034]
updated: 2026-10-12
---

# Diagram adapter boundary

## Current FarmBoy boundary

FarmBoy owns generic reusable workflows and portable feedback; the Diagram may consume a pinned release through a separately versioned adapter outside the generic bundle. Generic source excludes Diagram executables, databases, registration, canonical-state mutation and runtime services. Adapter feedback still needs a future authority decision. (S034)

Current installation names are `farmboy-<purpose>` workflows. Native TOML owns model/effort, while workflow/controller metadata assigns exact roles; delegated children retain their named scope and cannot integrate Git, expand authority or claim acceptance. Configuration, supported values, exact native selection and effective settings remain separate evidence. (S034)

## Earlier identity and provenance

The following observations retain the preceding source identity; current guide naming supersedes it without making old names aliases. (S034)

The Diagram is a consumer of Spec Kit Flow, not a runtime prerequisite for the generic bundle. Diagram registration, canonical work, projections, adapter feedback, and future orchestration belong to a separately versioned adapter and its own authority decisions. (S001, S003)

Generic Spec Kit Flow source excludes Diagram executables, databases, registration commands, canonical-state mutation, and runtime service dependencies. Adapter-specific feedback requires a future authority decision. (S001, S003)

The original design rationale and dogfood evidence came from The Diagram's `specs/027-workflow-prompt-hardening/`; that provenance does not make the Diagram checkout a required source of current generic behavior. (S001)

Generic workflows retain `speckit-flow-<purpose>` IDs, independently versioned extensions retain their reviewed manifest IDs, and the bundle composes those versioned components. Diagram-specific registration, state projections, and orchestration remain outside these generic source contracts. (S001)

## Related pages

- [Project authority and review gates](./project-authority-and-review-gates.md)
- [Bundle and workflow model](./bundle-and-workflow-model.md)

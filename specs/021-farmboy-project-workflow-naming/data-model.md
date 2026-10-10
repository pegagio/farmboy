# Data Model: Existing Identity Schemas

This rename introduces **no new data model, persistence, journal or state machine**. The core planning deliverable is explicitly limited to existing identities and their schema-preservation rules.

## Naming Inventory

The [naming contract](contracts/naming.md) is a reviewable documentation table, not a new runtime inventory format. Existing fields for bundle/package IDs, workflow/skill IDs, exact agent names and owned paths receive the approved values.

Existing manifest, installation record, agent-default, native registry and controller evidence schemas remain unchanged apart from applicable identity/path values and the delegation-container key spelling. The one approved field-name change is the existing delegation container `flow_kit` → `farmboy`; nested `delegated` / `agent` types, dispatch rules, lifecycle vocabulary and evidence semantics remain unchanged. Both feedback extension and command identities change; existing journal/report fields and data remain intact without conversion.

## Validation Rules

Each active purpose maps to one canonical skill/workflow; each existing role maps to one exact agent name. Manifests, role declarations, validators and references must agree. The ten active purposes, nine roles and standalone renderer remain distinct inventories.

Old invocation aliases are absent. Retained independent IDs, actual URLs, unrelated grammar and immutable historical values are not naming defects. Existing ownership/conflict behavior is preserved; no new classification or consumer discovery record is introduced.

## Inapplicable Models

There is no migration observation record, adoption state machine, legacy conversion schema, checkpoint transfer or new recovery transition. Existing installations are outside cutover upgrade scope. The operator-controlled absence of paused old-name runs adds no runtime guard.

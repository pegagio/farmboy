# Data model: Workflow handoff concepts

This describes semantic concepts expressed in ordinary requests and existing Git notes. It defines no serialized schema, mandatory field packet, database, register, new file format or runtime validator. References must stay within authorized access; lack of accessible required input is a specific question, not a fetch permission.

## Execution request and artifact association

One request associates selected feature identity, intent, requested segment and existing artifacts/context. “Identity must identify one contained feature and agree with any existing workspace pointer before effects.” Core commands use their existing caller-established workspace association; a missing required association is surfaced to the caller, never repaired by queue activation or silent retargeting. “Context references must be accessible under current authority; identify revision or current working state when needed.” There are no length, numeric quota, volume or persistence requirements.

## Outcome and checkpoint references

An execution outcome refers to that feature/request/segment, actual work, artifacts/evidence, remaining work/input/blockers and next review/action. “A committed checkpoint reference must identify an actual Git revision; uncommitted artifacts must disclose base revision and current working state.” Reviewed checkpoint, latest accepted handoff checkpoint and current artifacts are distinct concepts, not competing writable copies. Invalid/stale identity or references require the specific missing input before dependent effects. No outcome automatically accepts itself or grants ownership.

## Approval and owner relationships

Approval identifies the reviewed meaning/checkpoint, and may remain applicable after routine in-scope flow-back. “Material changes require the affected review; unchanged applicable work is not reapproved.” Diagram owns selection, eligibility, dependency, approval, active-owner and accepted-handoff decisions. Farmboy uses supplied applicable authority and reports uncertainty; it neither acquires/releases ownership nor implements a local one-owner lock. Sequential owners require coordinator-authorized handoff. Independent features require isolation rather than shared-workspace execution.

## Human-facing stage meanings

Standalone state remains in existing artifacts/roadmap. Externally coordinated readable outcomes do not become local lifecycle storage: draft → Needs clarification or Awaiting spec review; ordinary clarification → review; explicit spec approval → eligible separately selected planning; reconciled plan/tasks → Awaiting full-plan review; approved plan plus selected delivery → Awaiting result review after actual local candidate commit. Required input/failure/interruption is truthfully distinguished. No automatic next workflow follows.

## Integration outcome

Human final-result/UAT review authorizes later integration only explicitly. Project policy governs branch/target/checks; Diagram serializes repository/target integration and owns its database receipt. Farmboy returns Git references only, without implementing the executor, selecting placement, writing receipt commits or granting push. Integration merge freezes feature meaning; later material changes use a new linked feature.

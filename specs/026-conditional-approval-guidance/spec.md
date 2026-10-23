# Feature Specification: Fix conditional approval assessment guidance

**Feature Branch**: `026-conditional-approval-guidance`
**Created**: 2026-10-23
**Native identity**: FARM-26
**Status**: Awaiting whole-spec review
**Input**: Correct a demonstrated omission in the optional Diagram adapter's planning-admission guidance, using the existing native contract and human gates.

## Problem and scope

A real WITB-8 launcher child verified its approved specification but submitted an acquire request without `assessment.conditions`. Diagram rejected it with `assessment_required`: “record explicit conditions-applicability evidence.” No run or planning work resulted. The consumer reference and current Farm Boy source both omit this explicit conditional field rule for later acquisition. Diagram's existing check predates the attempt and works correctly.

An **applicability assessment** is the executing agent's truthful explanation of how an existing approval and its constraints apply to the exact artifacts and requested phase now. It is not a new approval, a copied list of old restrictions or a generic success assertion. This correction amends guidance from merged FARM-5/FARM-25 through a new small change set; their historical specifications remain intact.

## User Scenarios & Testing

### User Story 1 - Prepare a valid conditioned planning request (Priority: P1)

An authorized planner can follow the source adapter reference to assess current approval conditions and construct a valid native planning request before claiming execution authority.

**Independent Test**: Review the example against a controlled conditioned-approval fixture and check that the request includes the correct approval reference and meaningful applicability assessment. No production feature or real retry is needed to check the documented contract.

**Acceptance Scenarios**:

1. **Given** an applicable whole-spec approval with conditions, **When** a planner follows the guidance, **Then** the request includes `assessment.conditions` explaining applicability to verified approved artifacts and the current phase, not a placeholder or unexamined copy.
2. **Given** the historical restriction applied to a specification-preparation invocation and later planning has separate actual authorization, **When** the planner assesses applicability, **Then** it distinguishes the two scopes truthfully and preserves all remaining gates. If permission or meaning is unresolved, it stops for clarification rather than inventing authority.
3. **Given** a prepared typed request, **When** the planner uses the existing read-only planning offer before acquisition, **Then** it supplies the offer's allowed fields and required request file, verifies the response, and treats the offer as inspection rather than ownership.

### User Story 2 - Preserve safe rejection and unchanged optional behavior (Priority: P1)

**Independent Test**: Compare the correction with the existing native conditional-field guard and launcher failure contract.

1. **Given** an approval without conditions, **When** constructing the assessment, **Then** guidance does not invent a universal condition or placeholder requirement.
2. **Given** a definitive acquire rejection, **When** the child is launcher-driven, **Then** it aborts that invocation without feature work or resubmission. An absent operation does not override the launcher's no-retry rule; uncertainty is inspected without assumed authority.

### Edge Cases

- A valid approval ID alone does not supply applicability evidence. The minimal example must distinguish request-level and assessment-level approval references.
- An approval condition's relevance can depend on the original invocation and later explicit permission. Never infer that permission from flags, selection, a previous unrelated decision or a successful offer.
- Read-only offer validation can be corrected before the first acquire within actual authorization. A rejected acquire remains a stop; this correction adds no retry loop or recovery permission.
- Native field optionality depends on context: omission is allowed when no approval conditions apply, but is invalid for a conditioned approval. An example must not conceal that distinction.

## Requirements

### Functional Requirements

- **FR-001**: Correct `.agents/skills/farmboy-diagram-work/references/native-protocol.md` to state the existing rule explicitly: if the applicable approval's review has conditions, `assessment.conditions` is required. Explain its meaning as truthful current applicability evidence in the existing text array; do not add a per-condition ledger, fixed wording or new approval record.
- **FR-002**: Explain how the agent verifies exact approved artifacts/current requested phase and assesses relevant limits, including separately authorized later work. Forbid blind copying, synthetic placeholders and inferred permission; unresolved applicability must stop affected work.
- **FR-003**: Include one minimal valid planning example with the required native request/assessment approval references and meaningful conditions assessment. Clearly distinguish illustrative fixture values from verified values a real caller must supply. It must remain consistent with current Feature9 request shapes; do not invent a plan approval or use real approvals to authorize fixture work.
- **FR-004**: Describe typed `feature planning show --request-file` preflight using its actual allowed fields before first acquisition. An offer grants no run. Preserve strict action-specific fields, current-state inspection and the launcher's immediate abort/no-retry behavior after definitive acquire rejection; do not weaken native validation.
- **FR-005**: Add a focused regression/contract check in the existing test infrastructure covering the example and conditioned/condition-free distinction, truthful-assessment guidance, read-only preflight and rejection stop. Keep it a small adapter documentation correction, not a native report-builder or generalized schema framework.
- **FR-006**: Keep native Diagram validation, launcher code/behavior, generic planning skill, historical specs and unrelated work unchanged. Source changes precede any separately authorized consumer refresh. This feature grants no live WITB retry, controls, permissions/profile changes, merge or push.

### Existing concepts

Applicable approval, current assessment, planning offer and execution run are existing native concepts. No new persisted entity, approval role, workflow, allocator or lifecycle is introduced.

## Success Criteria

- **SC-001**: A reader can find the conditional field rule, explain why the failed request is incomplete, and produce the documented valid planning request from verified context without consulting Diagram implementation source.
- **SC-002**: Focused checks distinguish a conditioned approval requiring applicability evidence from a condition-free approval and guard against removing the preflight or acquire-rejection stop guidance.
- **SC-003**: Review confirms source scope is confined to the adapter reference and its focused regression support; no new runtime machinery, authority, permission or implicit next workflow appears.
- **SC-004**: Delivery evidence distinguishes document/contract verification from actual skill-runtime observations. Before accepting changed workflow behavior, meet the constitution's proportionate separate real-Codex-session requirement; simulations alone and this specification do not prove it. A live WITB retry or consumer refresh requires its own later authorization.

## Assumptions and review notes

The requested fix has no unresolved product choice. Native admission stays authoritative and unchanged. FARM's acknowledged Diagram cutover is active; its queue contains this single correction after imported completed history. No installed bug-fix entry or native Bug execution-run path is available, so the existing small Feature specification/plan/result gates are used without a second tracking item or new lifecycle.

This draft is specification only. Whole-spec approval is required before planning; whole-plan approval is required before implementation. No source patch or test implementation is represented as complete.

**Quality note for whole-spec review**: The standard checklist's two literal “no APIs/implementation details” criteria are disclosed exceptions because the exact native field and command names are the requested documentation subject. The remaining 14 criteria are satisfied. This does not authorize source implementation or waive native admission; review this retained interface scope with the whole specification.

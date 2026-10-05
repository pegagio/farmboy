# Workflow Feedback Report

- **Report ID**: `select-feature-explicit-intent-20261005`
- **Created**: 2026-10-05T16:25:44Z
- **Producer**: spec-kit-flow
- **Integrity**: `sha256:d61b37462f4702a0f85a13494d55b54b032bbab7ecdf9ea3d026f904fd8defa1`

## select-feature-explicit-intent-redundant-gates-20261005

- **Component**: `speckit-flow-select-feature` 0.2.0 (`sha256:8dd56f81973a4994ef3505e8a2a879bc49cfc031fabc799b9a3d89812feef2ae`)
- **Integration**: codex
- **Expected**: A direct user instruction to add DEP017-01 to the roadmap, activate that same item, and write its specification should authorize those explicitly requested operations in that order. After the new item resolves uniquely to Feature 019, carry that intent forward without another selection question. Accept unambiguous feature references such as F019 or 019 while distinguishing stable feature IDs from menu positions. A clearly requested roadmap modification should not require approval of exact patch bytes solely because the controller derived routine wording, numbering or linkage within the requested scope. Ask only when authorization, target identity, consequential scope or recovery remains genuinely unresolved.
- **Observed**: The user reported four prompts to express an intent already clear in the initial instruction. The roadmap amendment was separately reviewed and applied. Select Feature then required a fresh menu choice rather than carrying the explicit target forward. The installed gate rejected F019 and subsequently 019; menu position 2 succeeded. A second gate required approval of the exact active-pointer payload even though activation was explicitly requested and the prepared roadmap patch was empty. Menu position 1 approved that gate. Activation and specification subsequently completed. The supplied interaction excerpt compresses the identifier retries; session tool results establish both rejected forms. This report summarizes the interaction without reproducing dialogue.
- **Safety response**: Existing controls prevented writes before their literal gates were satisfied. No unauthorized roadmap or pointer change resulted, but the controls imposed redundant prompts. This capture/export records requested future behavior only; it does not amend the constitution, roadmap authority, installed/source workflows or current feature scope. Existing Feature 019 PyYAML work remains independent.
- **Manual fallback**: The user worked around the gate by answering menu positions 2 and 1. No source fix or authorization-aware alternative was implemented.
- **Suggested target**: Prospective coordinated authorization contract across reviewed Select Feature workflow/controller gate handling, Roadmap Write and governing constitution language. Distinguish direct human authorization from inferred proposals and untrusted evidence. Reuse explicit selected-target intent across separately requested phases; normalize uniquely resolving stable IDs and natural answers without choosing ambiguous targets. Do not require exact-patch reconfirmation for a clearly requested, bounded roadmap modification or empty-patch activation. Still ask for ambiguous identifiers, conflicting mappings, unclear dependency readiness, unsupported inferred changes, material scope/authority changes outside the explicit request, or ambiguous recovery. Preserve source provenance, validation, reporting and separate Git/publication/acceptance authorization. Regression cases should include the reported multi-phase request, F019/019/exact title/menu choices, ambiguous number-versus-index cases, inferred unrequested deltas, and external evidence that cannot authorize changes. A reviewed follow-up should reconcile governance and workflow behavior rather than silently bypass existing rules or fold this into the PyYAML feature.
- **Reporter disposition**: observed
- **Evidence references**:
  - `.specify/flow-controllers/runs/30c57106-29eb-4bce-8129-b051b3797684/summary.json`
  - `.specify/workflows/speckit-flow-select-feature/workflow.yml`
  - `.specify/flow-kit/controller-protocol.md`
  - `.specify/flow-kit/scripts/python/controller.py`
  - `.agents/skills/speckit-flow-roadmap-write/SKILL.md`
  - `.specify/extensions/flow-roadmap/commands/speckit.flow-roadmap.write.md`
  - `.specify/memory/constitution.md`
  - `specs/019-catalog-python-runtime-prerequisites/spec.md`


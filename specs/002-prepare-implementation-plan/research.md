# Research: Prepare implementation plan

All decisions below come from the current approved spec and inspected installed sources in this checkout. This document resolves design choices; it does not claim native runtime behavior has been verified. No research agent, external repository or new tool installation was used, consistent with the approved single-session constraints.

## Composition and authorization

**Decision**: Compose installed `speckit-plan` → `speckit-tasks` → read-only `speckit-analyze`; perform routine repair as a separate authorized step, then fresh analysis. **Rationale**: These commands already own templates, prerequisites, phase-specific artifacts and hooks. The direct operator decision and constitution II–III authorize routine current-scope repairs without repeated approvals. **Alternatives considered**: Copy core command logic (drift/maintenance burden); change analyzer to write fixes (breaks read-only contract); always ask for batch approval (contradicts the approved Q1 answer). Do not change core skills.

Sources: `.agents/skills/speckit-plan/SKILL.md`, `.agents/skills/speckit-tasks/SKILL.md`, `.agents/skills/speckit-analyze/SKILL.md`, `.specify/memory/constitution.md`, current spec Clarifications/FR-005.

## Templates, identity and existing artifacts

**Decision**: Use the installed command entry points and helpers with current feature pointer; respect explicit target constraints before effects. **Rationale**: `setup_plan.py --json` resolves the plan template and skips copying when plan.md exists; `setup_tasks.py --json` returns the effective tasks template/content after checking plan prerequisites. `check_prerequisites.py --json --require-spec --require-tasks --include-tasks` resolves analysis inputs. In `common.py`, `get_current_branch()` reads SPECIFY_FEATURE and falls back to the feature-directory name, not Git: report actual branch separately. **Alternatives considered**: Guess paths/branch or reset templates on resume (could overwrite current work); create a manifest/controller (unnecessary and prohibited). Existing task IDs and actual completion evidence must survive revision.

Sources: `.specify/scripts/python/setup_plan.py`, `setup_tasks.py`, `check_prerequisites.py`, `common.py`, `.specify/feature.json`.

## Approval and passing rule

**Decision**: Accept explicit approval from available conversation OR an applicable existing content-identifying review note. Treat material-change uncertainty as required input. A fresh pass means no actionable inconsistency and no unmet requirement, regardless of severity; optional suggestions remain separate. **Rationale**: These are the four clarified operator policies, not new defaults. **Alternatives considered**: Add an approval registry (unnecessary machinery); infer approval from checklist/Goal completion (forbidden); permit LOW/MEDIUM defects or relabel them optional (violates approved intent).

Source: current spec FR-002/004/010 and clarification answers 1–3. The approved content digest and metadata distinction are in spec.md and plan.md; future metadata changes do not retroactively approve changed meaning.

## Stopping and resuming without accounting

**Decision**: Continue useful authorized repairs based on existing analysis/spec/plan/tasks evidence. Stop INCOMPLETE when genuinely stuck, repeating unsuccessful approaches or needing a human decision; explain attempts and remaining issues concisely. **Rationale**: Latest Q4 explicitly replaces the earlier numeric rule. Edits alone do not prove progress; actual fresh analysis determines readiness. **Alternatives considered**: Numeric limits, counters/reset semantics, scores, state files, controllers, databases/event ledgers/metrics or renamed tracking frameworks are prohibited, rather than deferred design options. A repeated invocation inspects real artifacts and pending stage instead of reading a new resume store.

Sources: current spec replacement Q4, FR-007/009, SC-007; existing `.agents/skills/farmboy-prepare-specification/SKILL.md` for the artifact-based handoff pattern.

## Goals and independent acceptance

**Decision**: Do not create a Goal automatically or reactivate the completed specification Goal. Use only supported exposed native controls if a separately operator-selected bounded Goal exists; verify actual compatibility later in a separate real subject. Ordinary manual invocation is the baseline. **Rationale**: Existing Feature 001 evidence distinguishes actual completion at saved handoff from failed live-Goal human waits. Current exposed tool names alone prove neither future suspension nor planning compatibility. **Alternatives considered**: Assume live waiting works, fake a completion receipt or add continuation infrastructure (unsupported and outside scope).

Sources: `specs/001-prepare-specification/plan.md`, `quickstart.md`, `.agents/skills/farmboy-prepare-specification/SKILL.md`, current spec FR-012/013. Runtime compatibility is a required delivery verification item, not an unresolved product question or a pre-planning execution gate.

## Packaging and verification effort

**Decision**: Add one Markdown skill, one guide and Markdown fixture cases, with observations later in this feature's ordinary validation/acceptance.md. **Rationale**: Feature 001 already uses that shape. There is no server/CLI/API, extra library, new harness or serialized entity model to implement. **Alternatives considered**: A new Python controller or a generic testing/accounting package adds no necessary capability. Existing native session/CLI observation and small ad hoc source checks are sufficient; independent real execution remains mandatory.

Sources: existing `docs/prepare-specification.md`, `tests/fixtures/prepare-specification/cases.md`, `mise.toml`, current spec FR-011/013/014. No new framework, dependency, environment mutation or cross-repository access is requested.

## Implementation setup revalidation

T001 revalidated the installed plan/tasks/analyze helpers and effective templates, current pointer, 16/16 requirements checklist, constitution and selected scope on 2026-10-17. CLI availability probe reports Codex 0.163.0; this alone is not workflow evidence or proof of native Goal behavior. Independent subjects must retain the inherited current model/effort. Optional before-implement brief and after-implement debrief/wiki hooks are not selected; no mandatory implement/converge hook exists. Core skills and global settings are unchanged. Approved plan digest before metadata is `ee6e13687370b5def1ad2a310b24aa2dd79aefff144b4226c68f93c27f4facc1`.

## Approved human-input endpoint correction

**Decision**: For a separately operator-selected automation Goal whose actual entire objective is a saved review-ready OR INCOMPLETE-for-human-input handoff, durably save the INCOMPLETE planning outcome, exact required input, current artifact references, attempted work/remaining issues and next ordinary action in existing spec/plan notes; inspect that saved handoff, then complete the matching automation Goal through actually exposed supported controls and verify native readback BEFORE waiting for a person. This is successful handoff-objective completion only: it is neither passing analysis, a review-ready plan, plan approval nor implementation authority. After an actual answer, continue by separately operator-started ordinary interaction outside the completed Goal; never create or reactivate a Goal automatically. An overscoped unmet clean-proposal objective, unavailable native controls, arbitrary helper failure or unknown technical failure does not qualify for this human-input endpoint. Preserve the exact limitation without fabricating success, answers or controls. **Rationale**: The prior real native input-wait observation stalled; the user explicitly approved Feature001-style completion at a durable bounded human-input handoff instead. **Alternatives**: Live automatic waiting remains FAILED/UNACCEPTED; a controller or new persistence is prohibited; ordinary interaction after completed automation is the simplest supported approach. The user authorizes the material change and verification, not result acceptance. Earlier research/approval digests remain historical.

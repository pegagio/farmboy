# Implementation Plan: Agent Python Environment

**Actual Git branch**: `specs/017-flowkit-agent-configuration` | **Date**: 2026-10-05 | **Spec**: [spec.md](spec.md)

This plan replaces the superseded Specify/FlowKit runtime-integration design. The feature directory stays `specs/019-catalog-python-runtime-prerequisites`; the setup helper's `019-catalog-python-runtime-prerequisites` branch value is synthetic feature metadata, not the observed Git branch.

## Summary

Prepare one repository-local `.venv` from the existing mise Python pin, install the required PyYAML package with existing uv, and tell the agent to use `mise exec -- python` for ordinary repository Python work, including between skill invocations. Mise activates that existing environment through its standard `_.python.venv` configuration. No interpreter locator, custom launcher, component profile or runtime integration is needed.

FlowKit will provide a self-contained, copyable setup guide for explicitly adopting this same pattern in other projects. The guide carries the small configuration, requirements and agent-instruction snippets; no bundle installer or source-checkout runtime dependency is added.

Keep the current Python `3.11.16`, uv `0.12.5` and Specify tool declarations. Add `requirements-agent.txt` containing `PyYAML==6.0.3`, a preparation task and a small read-only check task in `mise.toml`, plus concise agent/setup guidance. PyYAML is already required by the approved spec; [research.md](research.md) assesses other utilities and selects none. This plan creates no implementation tasks or environment.

## Contents

- [Technical context](#technical-context)
- [Constitution check](#constitution-check)
- [Project structure](#project-structure)
- [Preparation and usage](#preparation-and-usage)
- [Validation strategy](#validation-strategy)
- [Risks and planning limits](#risks-and-planning-limits)

## Technical Context

- **Language/version**: Existing CPython 3.11.16 project pin; initial validation on the observed macOS arm64 environment.
- **Primary dependencies**: Required PyYAML 6.0.3; existing mise and uv. No Specify imports or new tooling dependencies.
- **Storage**: One committed requirements file and ignored local `.venv`; no database, ownership ledger or runtime schema.
- **Testing**: Direct Python import and safe YAML round-trip, disposable preparation and subprocess checks using existing stdlib unittest when automation is appropriate.
- **Target platform**: Current macOS repository context. Other operating systems have no new support claim until tested.
- **Project type**: Repository development environment and agent guidance.
- **Performance goals**: No interpreter guessing or undocumented package installation; no arbitrary startup-time target.
- **Constraints**: FR-001–FR-009 and SC-001–SC-005; retain skill-tools exception, user-owned environment protection and Feature 017 evidence.
- **Scale/scope**: One environment per adopting project, one required package, two small mise tasks and one reusable guide. Adoption is opt-in; no consumer migration or workflow changes.

## Constitution Check

Pre-research and post-design checks pass within this planning scope. Independent review is a separate assigned step; no acceptance is claimed.

| Principle | Design result |
|---|---|
| I — Persistence | Current spec governs; replace superseded design artifacts without altering Feature 017 history or drafting tasks. |
| II — Authority | Remain inside this delegated Plan step; no workflow chaining, roadmap mutation, Git integration or environment changes. |
| III — Boundaries | Agent environment and portable adoption instructions only; no installed controller, extension or external repository edits. |
| IV — Simplicity and approval | Reuse existing mise/uv and already-required PyYAML; no extra package, tool or framework adopted. |
| V — Evidence | Validate the actual agent invocation and preserve failures separately from successful retries; no native-dispatch or compatibility claims. |

No constitutional exception is needed. The current requirement checklist remains a spec artifact; this command does not refresh its wording or assert a fresh checklist review.

## Project Structure

The following are proposed implementation paths, not files implemented by this planning command:

```text
requirements-agent.txt                 # PyYAML==6.0.3
mise.toml                              # existing pins, existing-venv activation, python:prepare/check
AGENTS.md                              # ordinary Python convention and skill-tools exception
README.md                              # short preparation/use pointer
docs/installation.md                  # short pointer, distinct from bundle setup
docs/agent-python-environment.md       # self-contained adoption recipe, copyable inputs and verification
tests/                                # focused preparation/invocation regression coverage
.venv/                                 # local, already ignored; never committed or copied
```

Feature design artifacts are this plan, [research.md](research.md), [data-model.md](data-model.md), [quickstart.md](quickstart.md), and the two concise documents under `contracts/`. Existing filenames are retained for reviewability; their previous protocol contents are replaced. Task generation remains a separate operator-invoked phase.

## Preparation and Usage

Use `[env] _.python.venv = ".venv"` to activate an existing environment without enabling creation during ordinary execution. From the repository root, document `mise install python uv` followed by `mise run python:prepare`; the existing `run_auto_install = false` remains in force. No Specify installation is a prerequisite of these two steps.

The preparation task creates `.venv` only when the path is absent, using uv with the exact installed mise Python path and `--no-python-downloads`, then installs the requirements into `.venv/bin/python` explicitly. A shell existence guard must include symlinks, and preparation must stop for an existing path rather than letting `uv venv` replace it. A ready existing environment produces a read-only successful result. An incomplete or incompatible existing environment remains unchanged, with instructions to inspect it; after explicit authorization to repair that local environment, the documented targeted `uv pip install --python .venv/bin/python -r requirements-agent.txt` is sufficient when its Python is compatible. Replacing an incompatible environment requires a separate operator decision. Failed installs retain their failed outcome and may leave an incomplete newly created environment; they never report readiness.

The `python:check` task performs a small read-only check: expected `.venv` exists and is not an external symlink, its Python runs, Python matches the current pin, `sys.prefix` is the project environment, PyYAML matches the declared version, and safe YAML serialization/parsing round-trips a mapping with a list, scalar and boolean. Print the actual interpreter, Python/PyYAML versions and success or a concise failure/recovery message. This is a human-readable diagnostic, not a new reporting protocol. Do not silently check a base or unrelated Python if activation fails.

Project guidance directs ordinary commands to `mise exec -- python <args>` and a readiness check at session start or after preparation changes. Activated interactive shells may use `python`; shims or a version match alone are insufficient evidence. A failed invocation must not lead the agent to guess other interpreters or install packages ad hoc. Scripts belonging to or validating Codex skills continue to use the prescribed skill-tools interpreter, and report its missing packages before changing that environment. No arbitrary agent command is intercepted.

Document setup in each new checkout/worktree; `.venv` is already ignored and must not be added to `.worktreeinclude`. Existing catalog tasks naturally receive mise's configured environment, without changes to catalog behavior or claiming full catalog lifecycle validation.

## Repeatable Project Adoption

Deliver `docs/agent-python-environment.md` as the reusable FlowKit setup material. It must contain the complete `requirements-agent.txt`, minimal Python/uv pins and existing-venv activation snippet, complete portable definitions for the same two preparation/check tasks, the ordinary agent-invocation paragraph with skill-tools exception, `.venv/` ignore guidance and all preparation/verification commands. Inline task bodies or copyable project-local files must travel with the recipe; none may import this checkout, require `.specify`, run Specify, locate a personal interpreter or download an unreviewed remote script. The two tasks retain the preparation/check boundaries above. This is documented setup material, not a new component, installer or runtime framework.

For a clean target project, copy the documented inputs into that project, explicitly trust its mise configuration, provision Python/uv, prepare, then verify the same invocation. Each target has its own generated `.venv`; never copy an environment or add it to worktree propagation. The initial tested recipe uses this project's retained pins and macOS context; it does not promise other-platform support without observations.

For an existing project, inspect `mise.toml`, dependency declarations, agent guidance, ignore rules and `.venv` before adding anything. Merge only missing configuration and preserve unrelated sections. Never append duplicate TOML tables or task names. Existing compatible pins may be retained only after the direct checks pass; do not silently rewrite differing pins, requirements, `_.python.venv` values or colliding preparation/check tasks. Treat unresolved compatibility or conflicts as a concrete operator decision before adoption; selecting a different environment path or tool version is outside the baseline recipe until deliberately reconciled. Existing environments remain unchanged under the earlier preparation rule. No automatic edits to consumer projects occur.

## Validation Strategy

The direct scenarios in [quickstart.md](quickstart.md) cover all requirements:

| Requirement | Evidence to collect during implementation |
|---|---|
| FR-001, FR-003 / SC-001 | Clean disposable checkout: only documented prerequisites and preparation, then required package use. |
| FR-002 / SC-001 | Actual documented Python safely round-trips representative YAML. |
| FR-004 / SC-002 | New non-activated shell uses `mise exec -- python`; confirm interpreter/prefix and version. Guidance preserves skill-tools rule. |
| FR-005 / SC-004 | Missing environment/package, failed install and incompatible/pre-existing environment fail clearly without substitution or silent modification. |
| FR-006 / SC-003 | Research utility assessment records purposes, alternatives, costs and exclusions; no optional additions adopted. |
| FR-007 | Review diff for agent preparation/guidance and opt-in reuse only; no runtime launchers, framework or component edits. |
| FR-008 | Record source revision, actual paths locally, Python/PyYAML/tool versions, setup performed and outcomes; portable records normalize host paths. Protect Feature 017 bytes. |
| FR-009 / SC-005 | Second clean disposable project uses only the delivered recipe; same YAML checks pass. Existing-config/environment fixture preserves unrelated state and surfaces conflicts before changes. |

Use a disposable writable fixture for preparation and negative cases; never damage the operator's active environment to demonstrate failures. A small focused automated subprocess test should establish fresh preparation, explicit invocation and preservation on existing-path failure; do not build a general runtime matrix. Record unavailable network/package acquisition truthfully. Broader native agent, bundle lifecycle, stock Specify, automatic consumer migration and Linux/Windows checks are outside these acceptance scenarios. The second-project recipe check proves observed repeatability only, not general consumer adoption.

## Risks and Planning Limits

The explicit invocation depends on agents following project guidance; it cannot alter a global agent default. Exact PyYAML pinning makes the small environment predictable but requires deliberate future updates. Existing `.venv` and target-project configuration conflicts need inspection rather than automatic replacement. A self-contained recipe may drift from source tasks; the second-project check must exercise the delivered snippets rather than hand-transcribed alternatives. Acquiring tools/packages needs network or populated caches; installation failure is an unresolved preparation result.

Planning inspected existing pins/imports, source guidance, ignored/worktree paths, setup helper and official mise/uv documentation. No packages were installed, no `.venv` was created and no fresh preparation or runtime check was claimed. Feature 017's failed mise preparation, separate equipped-interpreter retry, accepted model evidence, unverified effective settings and native Specify transport limitation remain historical evidence. Earlier roadmap briefs and reviews concern superseded designs; they are preserved and do not prove this design implemented.

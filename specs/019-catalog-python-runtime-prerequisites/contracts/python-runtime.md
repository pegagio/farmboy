# Usage Convention: Agent Python Environment

These are proposed project preparation and usage interfaces, not installed commands. They replace the superseded selected-Specify launcher contract; no external API or component runtime protocol is added.

| Interface | Result and boundary |
|---|---|
| `mise install python uv` | Explicitly provision the existing pinned prerequisites; does not require installing Specify. |
| `mise run python:prepare` | Create an absent `.venv` using installed mise Python, install pinned requirements there, and check it. Ready existing state succeeds without mutation; conflicting/incomplete existing state stops unchanged for inspection. |
| `mise run python:check` | Read-only local-environment, interpreter, version and safe YAML check. Report the actual result and recovery on failure; never install or choose another environment. |
| `mise exec -- python <args>` | Execute ordinary repository Python using mise's existing-venv activation. Agent guidance requires preparation/check success; matching version or shims alone are insufficient. |

Failure output identifies the missing tool/environment/package or failed installation and its documented recovery. A missing environment points to preparation; existing state requires inspection before repair/replacement. Package acquisition failure remains failure, even if a partial `.venv` exists. The targeted repair command in the quickstart is run only after approval to modify that environment.

Preserve `~/.codex/venvs/skill-tools/bin/python` for scripts belonging to or validating Codex skills. This feature does not prepare that interpreter, change global PATH, rewrite installed skills or automatically intercept arbitrary agent commands. [Quickstart](../quickstart.md) supplies the validation guide.

## Portable Setup Material

The proposed `docs/agent-python-environment.md` must carry the complete copyable requirements (`PyYAML==6.0.3`), tool pins (`python = "3.11.16"`, `uv = "0.12.5"` under `[tools]`), activation (`_.python.venv = ".venv"` under `[env]`), the two complete task definitions, ignore rule and agent guidance. These inputs are configuration/documentation examples; the task implementation is not authored during planning. For a target with existing tables, merge keys into those tables rather than duplicating table headers.

The copyable guidance says: use `mise exec -- python <args>` for ordinary project Python, including between skill invocations; first follow preparation/check instructions; do not guess alternate interpreters or install packages ad hoc. Preserve any applicable higher-priority skill-tools rule and report its gaps before changes. The guide includes explicit project configuration trust, installation, preparation, direct YAML verification and incomplete-environment recovery steps without requiring a FlowKit/Specify runtime installation.

Opt-in adoption preserves target configuration and environment ownership. A conflict in tool pins, requirements, activation paths or task names stops merging for an operator decision; unrelated settings and files remain unchanged. The recipe cannot require this source checkout, global edits, personal paths or copying `.venv`. Its initial platform/version evidence and unsupported alternatives are stated plainly. Repeatability is validated by the second-project scenario, not inferred from first-project success.

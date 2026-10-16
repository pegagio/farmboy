# Farmboy agent guidance

## Repository and worktree boundary

- Identify the owner only as `pegagio` (`Pegagio` in prose) across source, docs, examples and generated artifacts. Never record the owner’s personal name or local username; use `~` or `$HOME` for home paths and `pegagio` for illustrative accounts.
- Confine task work to this repository and the current worktree. Do not inspect or modify other repositories, worktrees or unrelated files unless explicitly directed.
- If the task needs access beyond these bounds, explain the target and reason and ask before crossing, unless that access is already explicitly authorized. Permission for one external location does not grant access to others. These repository instructions do not change platform permissions or global Codex settings.

## Direction and scope

- Consult [project direction](docs/direction.md) only when the task needs project direction, goals, scope or roadmap context; do not load it routinely. Keep its agreed decisions separate from its recommendations and open questions; do not duplicate its decision text here.
- The `flow-roadmap` extension records known features planned for implementation in `.specify/memory/roadmap.md`; consult it when the task needs planned-work context.
- The `flow-wiki` extension maintains the project’s LLM wiki in `wiki/`; use `$speckit-flow-wiki-query` when the task needs project context.
- Preserve the Farmboy name and generic execution/Diagram adapter boundary. Diagram retains canonical coordination authority in its own project.

The [Farmboy Constitution](.specify/memory/constitution.md) governs development.

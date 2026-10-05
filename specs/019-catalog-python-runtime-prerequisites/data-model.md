# Data Model: Agent Python Environment

No application domain model, database, runtime inventory or reporting schema is needed. The only committed dependency data is the proposed `requirements-agent.txt`, containing `PyYAML==6.0.3`; the existing Python and uv pins remain in `mise.toml`.

The ignored `.venv` is local generated state, not a tracked artifact or transferable worktree asset. It is absent, usable, or incomplete for preparation purposes; these are ordinary diagnostic outcomes, not persisted lifecycle records. Existing environment paths are inspected and preserved rather than claimed or replaced.

Validation checks the actual Python interpreter/prefix, pinned versions and safe YAML behavior as described in [plan.md](plan.md). A human-readable result and a concise recovery instruction are sufficient. Additional utility dispositions remain in [research.md](research.md), not a machine-readable capability API. No unresolved entity or transition design remains.

The portable delivery uses the same requirements/configuration/guidance as copyable text in `docs/agent-python-environment.md`; no template registry or consumer state model is introduced. Each explicitly adopting project owns its configuration and generated environment. Existing pins, task names, activation settings and environment paths are inspected for conflicts rather than overwritten. The second-project and preservation scenarios in [quickstart.md](quickstart.md) validate these boundaries.

---
name: farmboy-analyze-remediate
description: Analyze and remediate feature artifacts. Run the installed farmboy-analyze-remediate workflow in this Codex task.
---

# FarmBoy Analyze

Run only the installed `farmboy-analyze-remediate` workflow in the selected consumer project and current Codex task. Follow `.specify/farmboy/controller-protocol.md` exactly. The installed workflow owns its prompts, commands, branch logic, and gates; do not duplicate them here or call `specify workflow run`. Start by validating the installed controller inventory and invoking `bash .specify/farmboy/scripts/bootstrap.sh "$PWD" farmboy-analyze-remediate farmboy-analyze-remediate` from the consumer project. Translate supplied workflow inputs to repeated `--input name=value` arguments. Review the returned `agent_assignments`, follow the named-agent dispatch procedure in the shared protocol, and stop before workflow work if a required agent cannot be confirmed. Do not launch another workflow phase.

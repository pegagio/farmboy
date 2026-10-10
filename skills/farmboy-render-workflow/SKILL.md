---
name: farmboy-render-workflow
description: Create or refresh a Mermaid flowchart for a user-selected FarmBoy workflow.yml, with exact step IDs, agent and command labels, type shapes, and delegated outlines.
---

# FarmBoy Render Workflow

Create a Markdown Mermaid flowchart from the selected source `workflow.yml`. This skill documents a workflow; it does not invoke that workflow or its commands.

## Select the source and destination

Resolve the user's workflow ID, name, or path to exactly one `workflows/farmboy-*/workflow.yml` in the current project. Ask for the choice only if several source definitions match. Read the selected YAML and nearby repository guidance. Treat the YAML as authoritative; an existing diagram is a style reference, not an alternate graph. Save or update `flowchart.md` beside the selected YAML unless the user specifies another project path. Preserve unrelated content in an existing file.

## Draw the graph

Walk `steps` in declaration order, including each switch `cases` branch, `default`, and `do-while` body. Add one presentation-only entry node, `start((Start))`, styled as a dark circle with white text, and connect it to the first YAML step. The Start marker is not a workflow step or part of the step-ID coverage check. Give every YAML step exactly one Mermaid node whose visible first line is its exact `id`. Connect sequential steps, selected switch branches, branch joins, and loop entry, repetition, and exit according to the YAML. Label switch edges with their exact case keys unless the switch declares a `transition_labels` mapping. That optional mapping supplies presentation labels for case keys or `default`; it does not change branch selection or the recorded output. Use only declared labels and verify each mapped key names an existing case or default branch. Show a loop's condition and `max_iterations`; distinguish its unconditional first pass from later passes. An empty branch rejoins at the next declared step. Do not invent other workflow steps, approvals, or transitions. If the YAML lacks enough information to determine an edge, label the uncertainty in prose instead of silently choosing a path.

Use these Clarify diagram conventions:

| YAML step | Mermaid rendering |
| --- | --- |
| `prompt` | Rectangle |
| `switch` | Diamond, using `@{ shape: diam }` |
| `do-while` | Hexagon |
| `gate` | Parallelogram |
| Command step | Rounded node |

Use a dashed outline only for `farmboy.delegated: true`; leave other outlines solid. In particular, do not style a switch as delegated. Put the assigned agent on a new line as `(AgentName)` when present. Put a nonblank command on a new line as `command: command.name`. Do not print `id:`, `agent:`, `type:`, `delegated`, or placeholders for absent values. Use short edge labels and Mermaid-safe node aliases while keeping YAML IDs verbatim in visible labels. If the renderer makes a switch outline appear dashed, explicitly set that switch's `stroke-dasharray:0`.

Write a short title and legend above the Mermaid block, including the Start marker, and a concise note below it for behavior the edges cannot show clearly. Link to the neighboring `workflow.yml`. Match the project's Markdown conventions. The Clarify `flowchart.md`, when present, is the local rendering example.

## Verify and deliver

Compare the complete set of YAML step IDs with the diagram's visible node labels, excluding the single Start marker. Check that Start has exactly one outgoing edge to the first declared step, and that each branch and loop path reaches its declared continuation or stop. Check node shapes and delegation marks against the YAML. Run available Markdown or graph validation and `git diff --check`; report any rendering limitation plainly. Return a link to the saved diagram and summarize the source workflow and validation. Do not commit unless asked.

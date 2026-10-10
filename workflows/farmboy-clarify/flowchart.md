# Clarify workflow flowchart

This diagram maps the step IDs in [workflow.yml](./workflow.yml) to their execution paths. Each node shows its step ID and, when assigned, the agent name in parentheses or a command. Steps without an agent assignment remain in the main task.

The dark Start circle marks workflow entry. Rectangles are `prompt` steps, the hexagon is the `do-while` step's end-of-body condition, and the rounded node is the command step. A dashed outline marks `farmboy.delegated: true`. The five-question limit applies to each `speckit.clarify` session; the `do-while` step allows at most five sessions in one invocation.

```mermaid
flowchart TD
    start((Start))
    sessionLoop{{"clarification-session-loop<br/>condition: after-session state == continue<br/>max_iterations: 5"}}
    clarify(["clarify-session<br/>(FarmBoy Specifier)<br/>command: speckit.clarify"])
    after["assess-clarification-after-session<br/>(FarmBoy Reviewer)"]

    outcome["clarification-outcome-stop"]

    start --> sessionLoop
    sessionLoop -- first session or continue within limit --> clarify
    clarify -- session complete --> after
    after --> sessionLoop
    sessionLoop -- complete, blocked, or limit reached --> outcome

    classDef delegated stroke:#4b5563,stroke-width:2px,stroke-dasharray:6 4
    class clarify,after delegated
    style start fill:#111827,stroke:#111827,color:#ffffff
```

The command session checks for significant ambiguity, asks substantive questions in the main task when needed, relays each operator answer to the same active child, and incorporates accepted answers incrementally. The post-session assessment controls whether another session starts. The first `continue` result requires evidence that the session resolved an ambiguity; later results must resolve a prior remaining ID. All terminal states use one outcome step, which reports the reason for stopping and preserves unresolved questions. Clarification does not invoke Plan or approve planning readiness.

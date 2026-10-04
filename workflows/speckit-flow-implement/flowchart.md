# Implement workflow flowchart

This diagram maps every step ID in [workflow.yml](./workflow.yml) to its execution path. Each node shows its step ID, its assigned agent in parentheses when present, and its command when present.

The dark Start circle marks workflow entry. The hexagon is a `do-while` step, the rounded node is a command step, and rectangles are `prompt` steps. A dashed outline marks `flow_kit.delegated: true`.

```mermaid
flowchart TD
    start((Start))
    initial["assess-implementation-state<br/>(FlowKit-Reviewer)"]
    loop{{"implementation-continuation-loop<br/>condition: assess-implementation-after-pass state == continue<br/>max_iterations: 5"}}
    implement(["implement-eligible-work<br/>(FlowKit-Coder)<br/>command: speckit.implement"])
    assess["assess-implementation-after-pass<br/>(FlowKit-Code Reviewer)"]
    report["report-implementation-outcome"]

    start --> initial
    initial -- eligible tasks remain --> loop
    initial -- complete or blocked --> report
    loop -- first pass or continued progress --> implement
    implement --> assess --> loop
    loop -- complete, blocked, no progress, or cap --> report

    classDef delegated stroke:#4b5563,stroke-width:2px,stroke-dasharray:6 4
    class initial,implement,assess delegated
    style start fill:#111827,stroke:#111827,color:#ffffff
```

The initial assessment records unfinished tasks before any implementation session. Each pass runs the existing implementation skill and checks current task and validation evidence against that baseline. Another pass starts only when eligible tasks remain and progress is verified. The workflow stops for completion, operator input, a concrete blocker, no progress, or the five-pass safety cap; Converge remains a separate operator invocation.

FlowKit-Code Reviewer uses an attributable implementation delta and returns exact review findings separately from the strict envelope. FlowKit-Coder receives those findings through eligible existing task correction. Fresh review confirms resolution; absent a safe eligible route, the workflow reports a specific blocked recovery. Product questions retain operator ownership.

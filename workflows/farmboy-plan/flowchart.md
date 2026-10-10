# Plan workflow flowchart

This diagram maps every step ID in [workflow.yml](./workflow.yml) to its execution path. Each node shows its exact step ID, its assigned agent in parentheses when present, and its command when present.

The dark Start circle marks workflow entry. The hexagon is a `do-while` step, rectangles are `prompt` steps, and the rounded node is a command step. A dashed outline marks `farmboy.delegated: true`.

```mermaid
flowchart TD
    start((Start))
    loop{{"plan-output-loop<br/>condition: verify-plan-output state == continue<br/>max_iterations: 5"}}
    prepare["prepare-plan-request"]
    create(["create-plan<br/>(FarmBoy Planner)<br/>command: speckit.plan"])
    verify["verify-plan-output<br/>(FarmBoy Reviewer)"]
    report["report-plan-outcome"]

    start --> loop
    loop -- first pass or retry with progress --> prepare
    prepare -- exact structural and semantic findings --> create
    create --> verify --> loop
    loop -- complete, blocked, no progress, or cap --> report

    classDef delegated stroke:#4b5563,stroke-width:2px,stroke-dasharray:6 4
    class create,verify delegated
    style start fill:#111827,stroke:#111827,color:#ffffff
```

The first request records missing outputs as a progress baseline. Each retry feeds the exact missing files or placeholder sections from the latest verification into the planning skill while preserving completed design. FarmBoy Reviewer checks plan content against the approved specification, including tradeoffs, risks, and validation. Exact findings return through the existing planning loop. Another pass requires verified gap resolution. Operator input, blockers, no progress, or the five-pass safety limit stop the loop; Tasks remains a separate invocation.

# Analyze and Remediate workflow flowchart

This diagram maps every step ID in [workflow.yml](./workflow.yml) to its execution path. Each node shows its exact step ID, its assigned agent in parentheses when present, and its command when present.

The dark Start circle marks workflow entry. Rectangles are `prompt` steps, diamonds are `switch` steps, the hexagon is the `do-while` step, and rounded nodes are command steps. A dashed outline marks `farmboy.delegated: true`.

```mermaid
flowchart TD
    start((Start))
    loop{{"analysis-remediation-loop<br/>condition: assess-analysis state == continue<br/>max_iterations: 6"}}
    prepare["prepare-analysis-flowback"]
    specRoute@{ shape: diam, label: "route-specification-remediation" }
    spec(["remediate-specification<br/>(FarmBoy Specifier)<br/>command: speckit.specify"])
    planRoute@{ shape: diam, label: "route-plan-remediation" }
    plan(["remediate-plan<br/>(FarmBoy Planner)<br/>command: speckit.plan"])
    tasksRoute@{ shape: diam, label: "route-task-remediation" }
    tasks(["remediate-tasks<br/>(FarmBoy Tasker)<br/>command: speckit.tasks"])
    readinessRoute@{ shape: diam, label: "route-readiness-recording" }
    record["record-readiness-evidence<br/>main-task recorder; verified Reviewer evidence"]
    analyze(["analyze-artifacts<br/>(FarmBoy Reviewer)<br/>command: speckit.analyze"])
    readiness["assess-readiness-evidence<br/>deterministic installed helper"]
    checker["check-readiness<br/>(FarmBoy Readiness Checker)"]
    assess["assess-analysis<br/>(FarmBoy Reviewer)"]
    report["report-analysis-outcome"]

    start --> loop
    loop -- first baseline or continued progress --> prepare --> specRoute
    specRoute -- run --> spec --> planRoute
    specRoute -- skip --> planRoute
    planRoute -- run --> plan --> tasksRoute
    planRoute -- skip --> tasksRoute
    tasksRoute -- run --> tasks --> readinessRoute
    tasksRoute -- skip --> readinessRoute
    readinessRoute -- run --> record --> analyze
    readinessRoute -- skip --> analyze
    analyze --> readiness --> checker --> assess --> loop
    loop -- complete, blocked, no progress, or cap --> report

    classDef delegated stroke:#4b5563,stroke-width:2px,stroke-dasharray:6 4
    class spec,plan,tasks,analyze,checker,assess delegated
    style specRoute stroke-dasharray:0
    style planRoute stroke-dasharray:0
    style tasksRoute stroke-dasharray:0
    style start fill:#111827,stroke:#111827,color:#ffffff
```

The first pass skips all correction stages and establishes a fresh analysis baseline. Later passes enter the shared waterfall at the highest affected artifact: specification → plan → tasks, plan → tasks, or tasks only. Every path reaches the same analyzer and assessment. The first baseline may continue without resolved findings; every correction pass requires verified resolution of a prior finding. Six total passes allow one baseline and at most five corrections. Missing evidence, invalid stage actions, failed commands, blockers, or required operator decisions stop before further mutation and are reported in the main task. Implementation remains separately invoked.

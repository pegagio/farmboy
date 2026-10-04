# Select Active Feature flowchart

This diagram maps every step ID in [workflow.yml](./workflow.yml) to its execution path. The dark Start circle marks entry; rectangles are prompts, diamonds are switches, parallelograms are human gates, and rounded nodes are commands. Dashed outlines indicate delegated steps.

```mermaid
flowchart TD
    start((Start))
    n01["list-roadmap-options<br/>(FlowKit-Roadmap Agent)"]
    n02[/"select-roadmap-feature"/]
    n03@{ shape: diam, label: "route-feature-selection" }
    n04["prepare-feature-selection<br/>(FlowKit-Roadmap Agent)"]
    n05@{ shape: diam, label: "route-selection-readiness" }
    n06[/"approve-feature-selection"/]
    n07@{ shape: diam, label: "route-selection-approval" }
    n08(["apply-selected-roadmap-patch<br/>command: speckit.flow-roadmap.write"])
    n09["activate-selected-feature"]
    n10["verify-feature-selection<br/>(FlowKit-Reviewer)"]
    n11["report-feature-selection"]

    start --> n01
    n01 --> n02
    n02 --> n03
    n03 -- selected --> n04
    n04 --> n05
    n05 -- ready --> n06
    n06 --> n07
    n07 -- approved --> n08
    n08 --> n09
    n09 --> n10
    n03 -- defer --> n11
    n10 --> n11
    n07 -- not-approved --> n11
    n05 -- blocked --> n11

    classDef delegated stroke:#4b5563,stroke-width:2px,stroke-dasharray:6 4
    class n01,n04,n10 delegated
    style n03 stroke-dasharray:0
    style n05 stroke-dasharray:0
    style n07 stroke-dasharray:0
    style start fill:#111827,stroke:#111827,color:#ffffff
```

Readiness uses ready or blocked, with required human input recorded as a blocker. Only approval takes the mutation branch; amendment and deferral share the not-approved exit and remain visible in the outcome. Dependency questions keep the selection gate pending until an explicit choice or defer. Only the approved roadmap/pointer proposal reaches mutation. Activation updates only .specify/feature.json; the target may not exist, and existing spec content is preserved. The final verification checks pointer and roadmap agreement. No specification, directory, or branch is created; Specify requires separate invocation. Failures after a roadmap write preserve and report the partial state.

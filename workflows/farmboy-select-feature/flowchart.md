# Select Active Feature flowchart

This diagram maps every step ID in [workflow.yml](./workflow.yml) to its execution path. The dark Start circle marks entry; rectangles are prompts, diamonds are switches, parallelograms are human gates, and rounded nodes are commands. Dashed outlines indicate delegated steps.

```mermaid
flowchart TD
    start((Start))
    n01["list-roadmap-options<br/>(FarmBoy Roadmap Agent)"]
    n02["resolve-feature-request"]
    n03@{ shape: diam, label: "route-feature-intent" }
    n04["prepare-feature-selection<br/>(FarmBoy Roadmap Agent)"]
    n05@{ shape: diam, label: "route-selection-readiness" }
    n06@{ shape: diam, label: "route-required-roadmap-patch<br/>false/true string states" }
    n07["activate-selected-feature"]
    n08[/"approve-feature-selection"/]
    n09@{ shape: diam, label: "route-selection-approval" }
    n10(["apply-selected-roadmap-patch<br/>command: speckit.flow-roadmap.write"])
    n11["activate-selected-feature-after-roadmap-write"]
    n12["verify-feature-selection<br/>(FarmBoy Reviewer)"]
    n13["report-feature-selection"]

    start --> n01
    n01 --> n02 --> n03
    n03 -- selected --> n04 --> n05
    n03 -- deferred --> n13
    n05 -- ready --> n06
    n05 -- blocked --> n13
    n06 -- no-patch --> n07 --> n12 --> n13
    n06 -- patch-required --> n08 --> n09
    n09 -- approved --> n10 --> n11 --> n12
    n09 -- not-approved --> n12

    classDef delegated stroke:#4b5563,stroke-width:2px,stroke-dasharray:6 4
    class n01,n04,n12 delegated
    style start fill:#111827,stroke:#111827,color:#ffffff
```

The main task uses the typed resolver on a direct, unambiguous operator target without asking for a repeated choice. Missing or ambiguous intent prompts one focused selection question; dependency questions remain separate. A no-patch route proceeds to pointer activation, while any nonempty patch retains explicit approval. Pointer snapshots distinguish absent from present and carry a digest for revalidation. Activation preserves lifecycle and existing specification bytes and creates no feature directory or spec. Specify remains a separate operator invocation.

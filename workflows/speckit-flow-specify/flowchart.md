# Author Active Specification flowchart

This diagram maps every step ID in [workflow.yml](./workflow.yml) to its execution path. The dark Start circle marks entry; rectangles are prompts, diamonds are switches, parallelograms are human gates, and rounded nodes are commands. Dashed outlines indicate delegated steps.

```mermaid
flowchart TD
    start((Start))
    n01["inspect-active-feature<br/>(FlowKit-Roadmap Agent)"]
    n02@{ shape: diam, label: "route-active-feature" }
    n03(["retrieve-governing-context<br/>command: speckit.flow-wiki.query"])
    n04["prepare-specification-request<br/>(FlowKit-Specifier)"]
    n05@{ shape: diam, label: "route-specification-readiness" }
    n06(["draft-specification<br/>(FlowKit-Specifier)<br/>command: speckit.specify"])
    n07["assess-created-spec-linkage<br/>(FlowKit-Reviewer)"]
    n08@{ shape: diam, label: "route-created-spec-linkage" }
    n09[/"review-spec-dir-patch"/]
    n10@{ shape: diam, label: "route-spec-dir-patch-decision" }
    n11(["apply-approved-spec-dir-patch<br/>command: speckit.flow-roadmap.write"])
    n12["verify-repaired-spec-linkage<br/>(FlowKit-Reviewer)"]
    n13["prepare-specification-outcome"]
    n14@{ shape: diam, label: "route-specification-outcome" }
    lc1["assess-specification-authoring-quality<br/>(FlowKit-Reviewer)"]
    lc2@{ shape: diam, label: "route-specification-authoring-quality" }
    n15(["brief-against-roadmap<br/>(FlowKit-Roadmap Agent)<br/>command: speckit.flow-roadmap.brief"])
    lc3["assess-specification-milestone-evidence<br/>(FlowKit-Reviewer)"]
    lc4["assess-roadmap-brief-milestone<br/>(FlowKit-Roadmap Agent)"]
    lc5["prepare-specification-lifecycle-request<br/>(FlowKit-Reviewer)"]
    lc6["prepare-specification-lifecycle-transition"]
    lc7@{ shape: diam, label: "route-specification-lifecycle-transition" }
    lc8["revalidate-specification-lifecycle-transition"]
    lc9@{ shape: diam, label: "route-specification-lifecycle-revalidation" }
    lc10(["apply-specification-lifecycle-transition<br/>(FlowKit-Roadmap Agent)<br/>command: speckit.flow-roadmap.write"])
    lc11["verify-specification-lifecycle-transition<br/>(FlowKit-Reviewer)"]
    lc12["verify-existing-specification-lifecycle-state-after-revalidation<br/>(FlowKit-Reviewer)"]
    lc13["verify-existing-specification-lifecycle-state<br/>(FlowKit-Reviewer)"]
    n16["report-specification-outcome"]

    start --> n01
    n01 --> n02
    n02 -- ready --> n03
    n03 --> n04
    n04 --> n05
    n05 -- ready --> n06
    n06 --> n07
    n07 --> n08
    n08 -- repairable --> n09
    n09 --> n10
    n10 -- approved --> n11
    n11 --> n12
    n12 --> n13
    n10 -- not-approved --> n13
    n08 -- linked --> n13
    n08 -- blocked --> n13
    n05 -- blocked --> n13
    n02 -- blocked --> n13
    n13 --> n14
    n14 -- ready-for-brief --> lc1
    lc1 --> lc2
    lc2 -- ready --> n15
    lc2 -- blocked --> n16
    n15 --> lc3 --> lc4 --> lc5 --> lc6 --> lc7
    lc7 -- ready --> lc8 --> lc9
    lc9 -- ready --> lc10 --> lc11 --> n16
    lc9 -- no-op --> lc12 --> n16
    lc9 -- blocked / question --> n16
    lc7 -- no-op --> lc13 --> n16
    lc7 -- blocked / question --> n16
    n14 -- blocked --> n16

    classDef delegated stroke:#4b5563,stroke-width:2px,stroke-dasharray:6 4
    class n01,n04,n06,n07,n12,lc1,n15,lc3,lc4,lc5,lc10,lc11,lc12,lc13 delegated
    style n02 stroke-dasharray:0
    style n05 stroke-dasharray:0
    style n08 stroke-dasharray:0
    style n10 stroke-dasharray:0
    style n14 stroke-dasharray:0
    style lc2 stroke-dasharray:0
    style lc7 stroke-dasharray:0
    style lc9 stroke-dasharray:0
    style start fill:#111827,stroke:#111827,color:#ffffff
```

In route-created-spec-linkage, linked and blocked reach the same outcome step but retain different evidence: only linked or a freshly verified approved repair can permit the brief. Conflicts, ambiguity, and required human input are blocked reasons. This workflow consumes the active .specify/feature.json pointer and unique roadmap mapping; it does not select a feature. A reserved target can be absent until authoring. The core command receives explicit SPECIFY_FEATURE_DIRECTORY and must preserve that identity. Verified initial linkage or an exactly approved repair with fresh verification reaches one brief. Missing context, ambiguity, target drift, deferred repair, or failed commands skip the brief or stop before further mutation. Clarify and Plan remain separately invoked.

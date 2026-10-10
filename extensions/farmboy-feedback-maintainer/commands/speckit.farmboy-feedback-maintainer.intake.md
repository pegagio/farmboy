---
description: "Validate a transferred feedback report and record a bounded proposal"
---

# Intake Workflow Feedback

This maintainer-only command accepts a transferred report through the public syntax:

```text
speckit.farmboy-feedback-maintainer.intake --report <REPORT_JSON> --disposition <DISPOSITION> --rationale <TEXT>
```

Accepted dispositions are `workflow-source-change`, `preset-investigation`, `agent-policy-investigation`, `reproduction-requested`, `deferred`, and `rejected`. Intake validates report shape, integrity, component provenance, redaction, and duplicates before writing an inbox copy and an explicit triage record under the source repository's `feedback/` directory.

Intake is evidence and proposal creation only. It must not edit a workflow source package, preset, bundle, roadmap, Git state, installed component, or agent policy. A non-duplicate accepted proposal must re-enter the ordinary FarmBoy specification, planning, task, and implementation flow before any source change occurs.

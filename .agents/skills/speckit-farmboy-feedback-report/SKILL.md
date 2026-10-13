---
name: speckit-farmboy-feedback-report
description: Export a portable workflow-feedback JSON report and Markdown projection
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: pegagio
  source: farmboy-feedback:commands/speckit.farmboy-feedback.report.md
---

# Export Workflow Feedback Report

Export consumer-local observations through this public syntax:

```text
speckit.farmboy-feedback.report --journal <JOURNAL_JSONL> --json <REPORT_JSON> --markdown <REPORT_MD> --producer <PRODUCER_REF> --created-at <RFC3339> --report-id <REPORT_ID>
```

The command validates every observation again, creates a self-contained report with a deterministic integrity digest, and writes a Markdown projection from that same report. It is offline and never uploads, submits, installs, changes, or triages anything. Transfer the two generated files through an explicit human-approved handoff to the FarmBoy maintainer intake.
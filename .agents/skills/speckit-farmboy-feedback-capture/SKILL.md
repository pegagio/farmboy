---
name: speckit-farmboy-feedback-capture
description: Validate and append one sanitized workflow-feedback observation
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: pegagio
  source: farmboy-feedback:commands/speckit.farmboy-feedback.capture.md
---

# Capture Workflow Feedback

Capture one observation in consumer-local operational state. The public syntax is:

```text
speckit.farmboy-feedback.capture --input <OBSERVATION_JSON> [--journal <JOURNAL_JSONL>]
```

Pass the observation as a JSON file, never as a transcript or free-form command argument. The command validates required provenance, a component digest, lifecycle status, and the redaction boundary before appending a canonical JSON record to `.specify/workflow-feedback/observations.jsonl` by default.

Reject raw agent transcripts, secrets, credentials, private keys, absolute host paths, malformed data, and duplicate observation IDs. Capture records evidence only: it does not contact FarmBoy, change an installed component, modify workflow source, select an agent, mutate a roadmap, or modify project authority.
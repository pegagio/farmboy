# FarmBoy Feedback Maintainer Intake

This component is installed only in the FarmBoy maintainer environment. Consumer projects receive `farmboy-feedback` capture/report only and must transfer reports through a human-approved handoff.

Intake validates a report's schema version, report integrity digest, complete consumer observation shape, component ID/version/digest, required redaction boundary, and duplicate relationship. Component digests may use either the consumer's bare or `sha256:`-prefixed form; the report integrity digest remains prefixed. A valid unique report is copied into `feedback/inbox/` and receives a reviewable triage record in `feedback/triage/`. A duplicate keeps the prior record relationship rather than creating a second proposed source change.

The `feedback/` directory is local maintainer evidence and is ignored by Git. Promote accepted findings into a reviewed specification or approved roadmap amendment with enough provenance and disposition to stand alone in a fresh checkout. Do not treat an intake record as approval for a source change.

Version `0.1.1` rejects absolute host paths embedded in report prose or `file://` URLs, even when the report digest is valid. It also checks the maintainer's rationale and receipt-time text for sensitive values before writing either record.

Each triage record records the report ID and digest, component coordinates, disposition, rationale, status, and next action. A disposition is never an implementation: the next action for a source refinement is an ordinary FarmBoy specification, planning, task, and implementation proposal.

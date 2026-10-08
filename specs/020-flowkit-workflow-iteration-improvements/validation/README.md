# Feature 020 Validation Evidence

This directory holds portable evidence for Feature 020. Evidence records observations and validation outcomes; it does not authorize source changes, installation, publication, roadmap verification, or feature acceptance.

Use repository-relative paths only. Record source component ID and version, repository/ref/commit when observed, package or source SHA-256, tested Specify CLI version, and the exact command or case that produced the result. Do not include host paths, credentials, private data, or raw agent transcripts. Keep errors to bounded sanitized summaries that preserve the actionable reason.

Keep evidence claims separate. A passing implementation test establishes only the behavior exercised by that test. A native launch requires the exact requested native agent type and its actual response or error. Effective settings require direct observation of the settings in force. Human acceptance is recorded only when the authorized human explicitly accepts the result. File presence, package provenance, simulated transport, and successful commands do not establish any of those other claims.

Historical observations in `tests/consumer-fixtures/workflow-improvements/observations.json` are immutable evidence copied from the consolidated feedback report. Preserve that report's bytes and component provenance. Current assessments belong in `validation/observations.json`; do not rewrite the historical fixture to reflect later behavior.

For each validation case, record the expected behavior, observed behavior, result, source provenance, evidence references, and limitations. Use `not-tested` with the exact missing context or capability when evidence cannot be collected. Never report an unavailable or unobserved result as a pass. Keep preparation evidence distinct from implementation evidence, native availability, effective settings, and acceptance.

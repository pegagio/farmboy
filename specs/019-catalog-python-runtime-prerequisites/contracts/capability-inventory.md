# Utility Dispositions: Agent Python Environment

The superseded capability-inventory protocol is replaced by a small human-reviewed dependency decision. No inventory JSON, component profiles, reconciliation command or capability-report schema is implemented.

The required third-party package is PyYAML 6.0.3. JSON/TOML/path/process support comes from the existing Python 3.11 stdlib. pytest, requests/httpx, rich and jsonschema are excluded because no demonstrated gap justifies them; the evidence, alternatives and maintenance tradeoffs are recorded in [research.md](../research.md).

For any later proposed addition, document the actual task or failure, expected benefit, existing alternative and maintenance cost. Obtain explicit approval before adoption. Absence of an excluded package is not incomplete preparation; an agent uses the documented alternative or reports the task-specific limitation.

The portable recipe carries this same PyYAML-only baseline; reuse does not justify adding speculative packages. Other projects may assess their own recurring-task needs and approve additions explicitly without changing the generic baseline or silently inheriting this project's installed packages.

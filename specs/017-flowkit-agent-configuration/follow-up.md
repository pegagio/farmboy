# Follow-up: Catalog Python Runtime Prerequisites

**Tracking ID**: DEP017-01. **Disposition**: Operator-directed deferral to a follow-up feature on 2026-10-04. **Roadmap entry/specification**: Not yet created; no feature number or implementation approach is selected.

This record tracks a confirmed catalog setup defect discovered during Feature 017 Close Out. The operator directed that it be fixed in a follow-up feature and documented now. It remains unresolved; deferral does not make the failed command successful or grant Feature 017 acceptance.

## Observed gap

Feature 017 agent-package handling imports PyYAML (`yaml`) in `tools/catalog.py`; its plan already lists PyYAML as a dependency. The catalog tasks in `mise.toml` execute `python3`, while the advertised checkout preparation provisions mise tools without declaring or provisioning that Python package.

The documented command `mise run catalog:refresh . --development-snapshot` failed with `ModuleNotFoundError: No module named 'yaml'`. Mise-selected Python `3.11.16` had no importable `yaml` module. A retry using the existing skill-tools interpreter with PyYAML `6.0.3` succeeded. That alternate environment establishes the observed refresh result there, not success of the documented mise preparation path. No dependencies or environments were changed during this investigation.

Affected surfaces are `tools/catalog.py`, the five `catalog:*` tasks in `mise.toml`, checkout preparation and lifecycle instructions in `docs/installation.md`, and actual-entry-point validation. Current tests remain evidence for their recorded prepared interpreter.

## Approved disposition

The operator stated: "yes, let's actually fix this in a follow-up feature and document it now". Feature 017 retains its agent identity, settings, instruction, package and lifecycle requirements. Its current completion coverage is explicitly qualified: delivery behavior and predictable file dispositions were demonstrated in the dependency-equipped tested environment; reliable preparation of the advertised mise runtime and complete provisioning guidance are deferred here. This qualifies FR-008, FR-011 and SC-003 without claiming their original unconditional usability target passed.

The defect is deferred rather than technically resolved. No Feature 017 implementation task becomes eligible for this repair. Existing task IDs and completion markers, accepted native field/value evidence, unverified effective settings and the inherited native Specify transport limitation remain intact. Roadmap verification and feature acceptance retain their separate human gates.

## Required follow-up outcome

The future feature must establish reproducible Python dependencies for the supported catalog execution path, reconcile tooling and setup instructions, and validate the documented install, refresh and agent operations after the documented preparation. It must make missing prerequisites actionable rather than rely on a personal interpreter that happens to contain them.

The follow-up may assess shared Specify/Codex tooling environment patterns, but changes outside this repository need their own authority and scope. Choosing dependency metadata, lockfiles, uv usage, virtual environments or installation policy belongs to that feature's reviewed planning; none is selected by this record. No new framework, package installation, environment mutation or implementation is authorized now.

## Future validation

Validate the actual supported entry points in a fresh disposable initialized consumer using only the documented setup. Exercise the full agent-delivery lifecycle while preserving consumer files, and add regression coverage for missing or unavailable declared dependencies. Record runtime/package versions, source coordinates and observed results. Keep the original failed mise attempt and alternate-interpreter retry distinguishable; do not rewrite them as a passing setup check.

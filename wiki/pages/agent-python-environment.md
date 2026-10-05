---
title: Agent Python environment
type: decision
sources: [S018, S027, S028]
updated: 2026-10-05
---

# Agent Python environment

Feature 019 addresses ordinary agent Python work: PyYAML must be available in the interpreter actually used, including between skill invocations. It excludes Specify/FlowKit runtime unification and a general runtime-management framework. (S027)

## Preparation and use

The reviewed design uses an ignored project-local `.venv`, existing mise Python 3.11.16 and uv 0.12.5, and the single pinned requirement `PyYAML==6.0.3`. Mise activates the existing environment; ordinary agent work uses `mise exec -- python`. Preparation and read-only checking are `mise run python:prepare` and `mise run python:check`; no custom interpreter locator or component launcher is needed. (S028)

Preparation creates only an absent environment. An already-ready environment succeeds without replacement; an incomplete or conflicting existing path stops unchanged for inspection and authorized repair. Failed acquisition remains failed preparation, even if it leaves a partial environment. Checking reports actual interpreter/prefix, pinned versions and safe YAML behavior without installing packages. (S028)

Python version equality does not prove package availability; shims alone do not activate this environment. Scripts belonging to or validating Codex skills retain the higher-priority `~/.codex/venvs/skill-tools/bin/python` exception; this feature does not prepare that interpreter or modify global Python. (S027, S028)

## Utility choices and repeatability

The utility assessment selects no additions beyond required PyYAML. pytest, HTTP clients, rich and jsonschema lack a demonstrated gap here; stdlib unittest, HTTP, JSON, TOML, path and process facilities cover the identified alternatives. Later additions require concrete need, benefit/cost assessment and approval, rather than assumed availability. (S028)

FlowKit provides a self-contained copyable guide carrying requirements, mise preparation/check configuration and agent instructions. Adoption is explicit and project-local, without Specify installation, automatic consumer migration or shared runtime coupling. Existing pins, task names, activation settings and environments are inspected and preserved; conflicting choices need an operator decision. The unchanged recipe/check supports Python 3.11.16; differing pins remain untouched and are not claimed validated. (S028)

## Evidence and chronology

Validation records successful source preparation and explicit Python/YAML checks, two focused regression tests, ready-repeat and negative preservation scenarios, failed offline acquisition and a separately authorized successful retry. A second disposable project copied the guide without installed FlowKit/Specify state; a conflicting existing-project fixture preserved configuration hashes and an environment sentinel. These observations are bounded to macOS arm64 and retained versions, not other platforms, real external adoption, publication or full catalog lifecycle. (S028)

> ⚠ conflict: S018/S027 preserve the earlier “mechanism undecided/revised planning required” stage; S028 records subsequent reviewed local-environment choices, delivery and validation. This is explicit chronological supersession, not an unresolved design choice. Earlier catalog/shared-Specify briefs remain superseded history; the debrief proposes verification but is not ledger authority. (S018, S027, S028)

DEP017-01's original missing-PyYAML failure and alternate skill-tools success remain historical. Feature 017's accepted model-support evidence, unverified effective settings, native Specify limitations and separately failed catalog test remain preserved; later environment success does not rewrite them. (S027, S028)

## Related pages

- [Bundle and workflow model](./bundle-and-workflow-model.md)
- [FlowKit agent configuration and consumer delivery](./flowkit-agent-configuration-and-delivery.md)

# Implementation Plan: Reliable Workflow Agent Capacity

**Branch**: `feedback` (actual Git branch; setup helper reports feature identity `018-reliable-workflow-agent-capacity`) | **Date**: 2026-10-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature 018, its two accepted clarifications, and the operator’s agent-owned validation constraint (FR-017/SC-007). Planning ends at design; no task generation, implementation, workflow execution, consumer configuration edit, or release is performed.

## Contents

The plan preserves the core template sections and adds the design and validation boundaries needed for tasking.

- [Summary](#summary)
- [Technical Context](#technical-context)
- [Constitution Check](#constitution-check)
- [Project Structure](#project-structure)
- [Design and Delivery](#design-and-delivery)
- [Validation and Completion](#validation-and-completion)
- [Complexity Tracking](#complexity-tracking)

## Summary

Add a small standard-library capacity helper to validate and persist parent-chat-scoped child lifecycle evidence. The main-task controller retains native dispatch and release authority. It registers probes before any successful workflow run exists, preserves results and validated interaction completion, releases eligible children immediately, and sweeps earlier verified FlowKit children in the same chat at entry. A positively identified capacity launch failure permits one cleanup sweep and one exact-name retry, never command replay. Catalog install/refresh prints setup guidance; consumer configuration is never a managed package file.

The investigation found prior restoration by native reversible archival and a current documented capacity setting, but did not reproduce the October 3 failure or establish the desktop's effective configured value. The design selects capability-checked native release and a candidate four-child configuration, with consumer recommendation publication gated on measured live evidence. [Research](research.md) records decisions and limits rather than claiming tests already passed.

## Technical Context

The existing architecture remains in place.

**Language/Version**: Python 3.11.16, Markdown controller instructions, existing YAML manifests; Python standard library including json, pathlib, hashlib, tempfile, and tomllib.

**Primary Dependencies**: Existing Specify fork `1.0.10.dev0+pegagio.2`, existing PyYAML for repository configuration tooling, native Codex exact-agent launch/read/release tools. No added dependency. Local CLI inspection reports `codex-cli 0.157.1`; this does not identify the running desktop build or its effective configuration.

**Storage**: Consumer-local atomic JSON under `.specify/flow-controllers/agent-sessions/<parent-chat-id>/`; separate from workflow `runs/`. No external service, database, raw transcript, or global config storage.

**Testing**: Existing unittest suites, proposed capacity unit/contract suite, disposable consumer install/refresh/remove, and actual native live sequential workflow execution. Use `~/.codex/venvs/skill-tools/bin/python` for skill validation; no environment changes.

**Target Platform**: Initially supported local Codex desktop with native exact named dispatch. Lifecycle adapter capability is checked at invocation; unavailable controls yield a specific bounded stop. Unix contributor tooling remains unchanged.

**Project Type**: Existing reusable workflow/controller package and catalog CLI.

**Performance Goals**: At least three separately invoked workflows and more than twelve terminal children with two necessary release cycles. One active work child at a time under current controller sequencing. No waiting or polling loop to conceal exhaustion.

**Constraints**: Preserve same-child question relay; immutable retained results before release; same-parent ownership; one recovery retry per failed launch; no workflow summary before successful preflight; no replay or role substitution; no consumer config mutation. Native side effects remain outside Python; inspectable structured helper decisions replace prompt-only eligibility rules.

**Scale/Scope**: Ten active controller skills share one protocol; probes remain unchanged in number and purpose. Ledger grows with this chat's actual children, not unrelated app chats. Four open child slots is the initial validation candidate, not a claim that four is today's desktop limit. Validate candidate four and a documented constrained available budget before final consumer advice. The agent configures one disposable project once and may constrain availability using verified driver-owned protected occupancy children; measured available slots are distinct from an introspected effective setting. Do not require separately configured manual chats for two and four.

## Constitution Check

Pre-research and post-design gates use Constitution 6.0.0. No constitutional amendment or exception is required by this design.

| Gate | Before research | After design | Evidence and implication |
|---|---|---|---|
| I: coherent mutable feature, prospective changes | Pass | Pass | Spec and clarifications govern these artifacts; later tasks must cover design and tests; no verified feature history is edited. |
| II: operator authority and exact dispatch | Pass | Pass | User approved same-chat earlier-child cleanup and immediate release; native agent and question gates remain exact; retry is restricted to an unstarted failed launch. |
| III: generic source and component ownership | Pass | Pass | Capacity helper belongs to controller source; catalog composes it; no Diagram runtime and no consumer agent/config ownership change. |
| IV: source authority and manual fallback | Pass | Pass | Change source protocol/helper/docs; retain installed graph and manual path; introduce no framework or dependency. |
| V: bounded evidence and feedback | Pass | Pass | Record compact provenance, no raw transcripts; historical archival is not current live proof; actual sequential/recovery tests gate delivery. |
| Consumer preservation | Pass | Pass | Install/refresh/remove never own or write `.codex/config.toml`; notice describes an unapplied recommendation. |
| Feature boundaries | Pass | Pass | Features 016/017 and Select Feature approval routing remain excluded. |

Preflight lifecycle diagnostics are new local evidence, not workflow execution state. Preserve `recovery.create_summary(preflight_passed=True)` unchanged in its semantic gate. A record may describe completed probes without a `run_id`; neither a probe nor cleanup counts as workflow progress.

## Project Structure

The feature documentation follows the existing specification layout.

### Documentation (this feature)

```text
specs/018-reliable-workflow-agent-capacity/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── child-lifecycle.md
│   └── consumer-capacity-guidance.md
├── checklists/requirements.md
└── roadmap-reviews/
```

`tasks.md` is generated only by a later explicitly invoked tasking command.

### Source Code (repository root)

```text
controllers/flow-kit/
├── controller-protocol.md
├── manifest.yml
└── scripts/python/
    ├── capacity.py             # proposed new helper
    ├── controller.py
    └── recovery.py
tools/catalog.py
docs/installation.md
tests/
├── consumer-fixtures/agent-capacity/scenarios.json # proposed bounded synthetic test inputs
├── test_capacity.py            # proposed new suite
├── test_controller.py
├── test_catalog.py
├── test_bundle_lifecycle.py
└── test_snapshot_validation.py
```

**Structure Decision**: Use a separate composable `capacity.py` rather than extending `controller.py` into a native process orchestrator. Existing package enumeration already includes controller scripts. Centralize lifecycle instructions in the shared protocol; do not duplicate them across workflow prompts or change graph topology. Small protocol-version/manifest updates follow source changes; release archives and catalog metadata are only regenerated through the reviewed packaging path when authorized.

## Design and Delivery

The [lifecycle contract](contracts/child-lifecycle.md) and [consumer guidance contract](contracts/consumer-capacity-guidance.md) define exact payloads and observable behavior.

1. Register each actual native probe/work child with typed parent/child identity and immutable invocation/step association. Do not invent IDs from activity labels. If runtime identity cannot be proven, report an ownership/capability limitation and exclude that child from cleanup.
2. Preserve compact usable results and digests before marking interaction complete. Pending question or continuation keeps the original child protected. A completed turn or idle display alone is insufficient.
3. At entry and after each child finishes, inspect eligible same-chat records, re-observe native terminal state immediately before release, validate revision/digest/ownership, then use the supported native close control if exposed; otherwise use native reversible archival only on clients for which restoration has been validated. Do not use interrupt as a release substitute.
4. Record operation acceptance separately from capacity restoration. A subsequent successful exact named launch establishes observed restoration; lack of a subsequent launch remains unconfirmed. Failed/unavailable release is explicitly reported and yields a safe stop when the next required release cannot be satisfied.
5. For recognized capacity exhaustion, do one eligible sweep and at most one fresh exact-name launch. Failed or no eligible release, uncertain ownership, unknown errors, or repeated exhaustion stop. A running-child failure follows existing recovery without capacity-driven command retry.
6. Link lifecycle evidence into run summaries only after successful preflight. Add stable capacity stop codes without putting raw native error text into portable records. Preserve historical summaries and tolerate absence of new fields on older runs.
7. Print one recommendation/setup reference from the shared catalog install/refresh success path. Print a qualified partial-update notice on failures after mutation without claiming a successful installation or applied config. No duplicate notice inside low-level package installation. Ship a reviewed setup guide in the shared controller package so the reference remains available after checkout/catalog shutdown.
8. Inspect only the target project's bounded config for an advisory state when needed; never infer effective runtime settings from it or read global secrets/config to make a recommendation. Preserve config bytes and exclude the file from ownership records. Default to generic advice if inspection is unavailable; it must not invalidate otherwise successful component installation.
9. Make validation agent-owned using `tests/consumer-fixtures/agent-capacity/scenarios.json` and a native driver procedure in this feature's `validation/native-runbook.md`. The main-task test driver separately invokes each installed workflow in the authorized disposable-test scope; production workflows do not chain other workflows. Python prepares fixtures and validates evidence, never calls native dispatch/release. The agent prepares the project/config, supplies only predetermined synthetic test-actor inputs, performs native actions, and captures results. Genuine product questions, consequential decisions, and acceptance retain human gates. Unsupported automation is a blocker rather than manual scenario work; human environment labor is limited to one initial Codex project setup when required. Reuse the same configured project and persistent test chat for the sequence; validate supported automated context/reload handling before proposing any additional test context.

Proposed consumer example is `[agents] max_concurrent_threads_per_session = 4`, merged by the operator. The candidate is deliberately modest and fits sequential execution with protected-child headroom. Final recommendation requires live tests at that value; a failed test returns to this feature's artifacts for reconciliation before source delivery. Different existing valid values are not automatically labeled wrong. Both legacy/new keys together require manual reconciliation, not silent precedence assumptions.

## Validation and Completion

The quickstart separates runnable baseline checks from commands requiring implementation. Planning performs documentation/link/schema consistency checks only; unit tests of unchanged code do not prove a capacity fix.

| Requirements | Design surface | Required proof |
|---|---|---|
| FR-001/002 | Research + client capability capture | Current controls/default uncertainty, exact runtime observations, historical boundary. |
| FR-003–005 | Lifecycle ledger + protocol | Durable result, strict parent/step ownership, immediate release, prior invocation handling, protected children and stale revision rejection. |
| FR-006–008 | Recovery envelope + protocol | One retry, failed launch only, positive capacity classification, no replay, preflight vs run state, specific stops. |
| FR-009–012 | Catalog notice + packaged guide | Install/refresh visibility, operator merge, alias/trust/reload guidance, unchanged config bytes. |
| FR-013/014 | Deterministic + disposable + native live suites | All configuration states and partial failures, at least three real workflows, >12 children, repeated release, failure boundaries, provenance. |
| FR-015/016 | Full graph/controller regression | Same-child relay, assignments, gates, manual path, no graph or unrelated feature changes. |
| FR-017 / SC-007 | Agent-owned native driver + synthetic fixture | Agent executes setup/configuration, all scenario commands and inputs, assertions, and evidence; zero manual test cases, at most one human project setup, preserved genuine decision gates. |

Native verification is an implementation milestone, not completed planning research. Missing safe native ownership/release evidence or required actual sequential/recovery results is a completion blocker. Unavailable effective-setting introspection alone is a recorded limitation: keep the effective value explicitly unknown, validate documented setting support, trust/override and reload handling, and establish the required native behavioral results without claiming an introspected value. A configured candidate alone does not establish an effective constrained budget or validation-backed recommendation; record supported runtime budget evidence or measured constraints for the sequence and the limits of attributing results to the candidate. A simulated ledger/slot model cannot replace live positive recovery evidence. After tasking, recommend Analyze and Remediate before implementation; do not launch it automatically.

## Complexity Tracking

There are no justified constitutional violations. The new ledger is necessary because workflow run summaries intentionally do not exist before successful preflight; overloading them would falsely imply execution. No scheduler, long-lived daemon, global agent pool, automatic config writer, new dependency, or workflow redesign is introduced.

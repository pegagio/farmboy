# Research: Reliable Workflow Agent Capacity

Research on 2026-10-03 resolves design choices without claiming the future implementation or live acceptance tests have run.

## Contents

Use the decisions below to distinguish observed facts, chosen design, and delivery evidence still required.

- [Evidence Baseline](#evidence-baseline)
- [Capacity Setting and Recommendation](#capacity-setting-and-recommendation)
- [Child Lifecycle and Release](#child-lifecycle-and-release)
- [Persistence and Recovery Bound](#persistence-and-recovery-bound)
- [Consumer Installation and Upgrade](#consumer-installation-and-upgrade)
- [Rejected Alternatives and Validation Limits](#rejected-alternatives-and-validation-limits)
- [Source Coordinates](#source-coordinates)

## Evidence Baseline

The current source controller manifest is `flow-kit-controllers` 0.5.3. Installed observation coordinates are Clarify 0.4.5, composed digest `sha256:a23a117e134aa2fefb5bb4aeb9f0c518b3e87ccf5ade57299b26a327dd9e7862`, controller 0.5.3. The observation reports a successful Specifier probe followed by Reviewer `agent thread limit reached` before workflow work. The count of twelve is operator-reported; it does not establish a limit. [Local journal](../../.specify/workflow-feedback/observations.jsonl), observation `clarify-agent-thread-limit-preflight-20261003`.

Repository evidence already demonstrates one earlier native restoration after verifying and reversibly archiving a completed test child. It also records no exposed close/retire API and no capacity restoration from interrupting an idle child in that test client. [Historical capacity recovery](../014-flowkit-workflow-improvements/validation/live-workflows/capacity-recovery.json), [runbook](../014-flowkit-workflow-improvements/validation/live-workflows/runbook.md).

Current CLI inspections returned `codex-cli 0.157.1` and `specify 1.0.10.dev0+pegagio.2`. Neither identifies the desktop build or proves its effective capacity. This planning session declares four concurrency slots and successfully launched one read-only research agent; that is limited planning-tool evidence, not a FlowKit recovery test. The October 3 root cause and configured value remain unconfirmed facts, not unresolved design choices.

## Capacity Setting and Recommendation

**Decision**: Use the documented `agents.max_concurrent_threads_per_session` spelling in consumer guidance, with four as the initial live-validation candidate. Do not publish it as a tested recommendation until actual implementation scenarios pass. If measurements reject it, reconcile the candidate in the feature artifacts before delivery.

**Rationale**: The documented setting controls concurrently open spawned children, excluding the primary, and the documentation retains `agents.max_threads` as a legacy alias. Four matches this planning session's declared slots and provides headroom for sequential controller work. There is no evidence supporting a large blanket increase. [Official subagent settings](https://learn.chatgpt.com/docs/agent-configuration/subagents#global-settings).

Project-level overrides require trust; higher-priority runtime overrides may defeat a project value. Therefore distinguish file parsing from an effective runtime observation. [Official configuration precedence](https://learn.chatgpt.com/docs/config-file/config-basic#configuration-precedence).

**Alternatives considered**: Keeping an implicit default hides consumer expectations. Raising capacity to accommodate accumulated historical children postpones failure. Guessing a particular old limit or claiming a file proves effective runtime capacity is unsupported. Setting both alias and canonical key creates avoidable ambiguity. CLI acceptance is not desktop validation.

**Verification decision**: Record documented field support plus trusted project configuration, any exposed effective-setting metadata, and constrained actual spawn/release observations in a disposable consumer. If the desktop cannot expose its effective value, report it unknown; behavioral test results may still demonstrate the tested sequence, but must not be mislabeled configuration introspection. Consumer setup uses a fresh chat as the conservative reload procedure unless the tested client proves supported in-place reload. Starting fresh once to apply configuration is distinct from restarting repeatedly to evade exhaustion.

## Child Lifecycle and Release

**Decision**: Main-task native tools perform release; Python validates evidence and eligibility. Prefer a supported close/retire operation if present. Otherwise use reversible native archival only when the tested client demonstrates restoration and retention. Never fall back to filesystem/database edits, guessed thread IDs, interrupt, or generic agent substitution.

**Rationale**: Official documentation describes closing completed agent threads but does not establish this desktop's exact release API or restoration semantics. The existing repo supplies bounded archival evidence. Preserve capability checks and require fresh live validation of the selected adapter. [Official thread controls](https://learn.chatgpt.com/docs/agent-configuration/subagents#managing-subagents), historical record above.

**Eligibility decision**: A typed native identity and stored FlowKit invocation association establish parent/child ownership. Confirm terminal execution, preserved usable result, no unanswered question, and no continuation. Re-observe immediately before mutation; stale identity/state/revision fails closed. Earlier same-chat FlowKit children are eligible under the operator's answer; labels and idle state alone are not proof. A legacy child absent from the ledger is skipped unless typed native evidence and its retained outcome can be validated and registered without guessing.

**Alternatives considered**: Automatic cleanup by matching labels risks unrelated chats. Reusing one child for many steps weakens fresh-role review. Only releasing at boundaries or after failure conflicts with the accepted immediate-release clarification. Blanket archival risks pending answers and continuation.

## Persistence and Recovery Bound

**Decision**: Add `capacity.py` with atomic, revision-checked session JSON and compact immutable result files under `agent-sessions/<parent-chat-id>/`. Keep it separate from run summaries; probes use an invocation ID and null run ID. The protocol calls it before/after native tool operations. No native API or shell dispatch is embedded in the helper.

**Rationale**: `recovery.create_summary()` refuses unsuccessful preflight. Run summaries describe executed workflow state; the new ledger describes resource lifecycle. Cross-invocation cleanup requires durable ownership and results even for probes before a run exists. Existing recovery redaction and atomic-write patterns are reusable at the module level where appropriate, not by weakening summary gates.

**Recovery decision**: For one positively classified capacity launch failure, allow one eligible cleanup sweep and one fresh launch of the same exact agent. Total launch attempts for that step instance are at most two, including the original. Failed cleanup, no eligible child, unknown failure, or repeat exhaustion produces a stable stop. Native executing-child failures retain the existing no-automatic-retry contract. Capacity recovery never replays commands.

**Re-analysis decision**: Missing safe ownership/release proof or actual required native sequence/recovery results blocks completion. Unavailable effective-setting introspection alone remains a disclosed limitation, consistent with FR-001/010 and SC-005. Validate supported setting/trust/reload behavior and actual native outcomes; keep unknown values unknown and distinguish measured constraints from a configured candidate. Implement `inspect-session` explicitly as a read-only compact ledger lookup, including an absent-session result without creating files; CLI scaffolding is insufficient to deliver this operation.

**Validation ownership decision**: The implementation agent owns the native driver, fixture preparation, disposable configuration, separately dispatched workflow sequence, synthetic test-actor inputs, assertions, and evidence collection. One initial Codex project setup may require the operator; a manual test matrix is not an acceptable fallback. Genuine consequential decisions remain gated. Configure candidate four once and, where native capability supports it, use verified driver-owned protected children to constrain observed available slots in the same persistent test chat; never describe occupancy as effective-setting introspection. This replaces the earlier two-setting test candidate procedure without relaxing required sequential, protected-child, recovery, or recommendation proof. A driver instruction/fixture is sufficient; reject a new scheduler, native API in Python, automated product-phase chaining, and repeated manual dispatch requests.

**Alternatives considered**: Unlimited retries obscure failures; sleep/retry without changed evidence wastes time; putting probes in a workflow run violates the preflight boundary; storing raw native messages/transcripts undermines portability.

## Consumer Installation and Upgrade

**Decision**: Emit one notice from `tools/catalog.py:install()` for both success routes, after controller package installation. Include operation state, unapplied recommendation, supported key/candidate once validated, preserved ownership, and the consumer-local packaged guide path. On partial failure distinguish updates from successful completion. Ship the guide with the shared controller package so users retain it without a source checkout or active localhost catalog.

**Rationale**: Both install and refresh already pass through that function; low-level package calls also run preflight and would duplicate notices. `controller_package_files()` owns only controller payload and skill files. `.codex/config.toml` stays outside ownership, rollback, and removal. Target-file parsing may classify only local advisory state; it never reads global config or certifies effective values.

**Alternatives considered**: Documentation-only advice is easy to miss during upgrade. Automatic writes conflict with consumer ownership. A localhost link expires with the catalog command. Reading and printing global configuration may reveal unrelated data. A malformed consumer config should yield guidance, not falsely change the component operation outcome.

## Rejected Alternatives and Validation Limits

All planning choices above are resolved. The effective historic limit, current root cause, desktop build, measured recommendation, and sustained live behavior are facts to capture in implementation validation, not claims produced by design documents. Acceptance remains gated on the spec's real sequential workflow tests; static tests, a research-agent launch, and historical recovery do not satisfy them. No consumer configuration, runtime, source behavior, package archive, or installed component was changed during planning.

## Source Coordinates

This planning baseline identifies exact inspected source bytes. No source behavior changed during planning.

| Path | SHA-256 |
|---|---|
| `controllers/flow-kit/manifest.yml` | `8aea597f3983f8730907a60fc0ee5a45038e2ffb3f96f8c5c43bf9c1630eb671` |
| `controllers/flow-kit/controller-protocol.md` | `bb470c22252016ca3195d0a1f2b55b69a398455126e324d2987b5acad269825f` |
| `controllers/flow-kit/scripts/python/recovery.py` | `2028995b9a8298a7dfc65e529f98e1025ef776ed0a9d2a7175992a4fb0afad77` |
| `controllers/flow-kit/scripts/python/controller.py` | `a7e3145b54df71176fdf53e7de6b2bd6550ce7ecfd3a16531fd9aac59fb8e058` |
| `tools/catalog.py` | `50707fa36344fd389d5958f7d9d5a43ea54baa5d746dcdccf60c5ed376d4b58d` |
| `workflows/speckit-flow-clarify/workflow.yml` | `3d14ce6389c4c441e1b9fafbfa2a61660dc89729999f1765ec2e2f8143b9148a` |

**Captured HEAD**: `b69e001c5852938482a6699d0619dc46b4280ac7`. The approved roadmap and Feature 018 artifacts are uncommitted; the baseline is not a release or acceptance claim.

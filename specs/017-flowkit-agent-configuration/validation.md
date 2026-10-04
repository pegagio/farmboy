# Feature 017 Implementation Validation

This record separates observed source/client evidence from unfinished checks. It grants no publication, roadmap verification or acceptance.


## Table of Contents

This record retains earlier attempts as provenance; use the resumed implementation and convergence sections for current status.

- [Baseline](#baseline)
- [Evidence Boundaries](#evidence-boundaries)
- [Identity Migration and Foundation](#identity-migration-and-foundation)
- [T012 Support Gate: Prior Desktop Evidence Recovered](#t012-support-gate-prior-desktop-evidence-recovered)
- [Core Convergence and Implementation Attempt: 2026-10-04](#core-convergence-and-implementation-attempt-2026-10-04)
- [Recovery of Accepted Desktop Evidence: 2026-10-04](#recovery-of-accepted-desktop-evidence-2026-10-04)
- [T012 Support Check Completed: 2026-10-04](#t012-support-check-completed-2026-10-04)
- [Resumed Implementation and Final Evidence: 2026-10-04](#resumed-implementation-and-final-evidence-2026-10-04)
- [Resumed Core Convergence Outcome](#resumed-core-convergence-outcome)

## Baseline

- Source revision: `ced0e9e67e49d1ff757e41e313445d5b504a8f9f`.
- Codex CLI: `0.157.1`; Specify: `1.0.10.dev0+pegagio.2`; Python source pin: `3.11.16`.
- Source bundle `0.13.8`, source controller `0.5.3`; checked-in catalog bundle `0.13.7`, controller `0.5.2`.
- Catalog controller artifact SHA-256: `1de97fc94a5e4a8d9ef0bd1534b8962d437bf7a5d71984988380c925bb8a3778`.
- Operator-approved settings: [research](research.md#approved-model-and-effort-decisions); package/CLI authority: [contracts](contracts/agent-delivery-cli.md).

| Existing role | Local source | SHA-256 | Settings |
|---|---|---|---|
| Roadmap Agent | `.codex/agents/roadmap-agent.toml` | `2b025a5aa76aaa4b89f82721756cf99b968fbfaa5b65ae44b8d23061812e231d` | model/effort absent |
| Specifier | `.codex/agents/specifier.toml` | `4f09e54c5066125a7adef2425a72e5b817f8e25a8876d31c583c7e697daf1858` | model/effort absent |
| Planner | `.codex/agents/planner.toml` | `041b0b09800a7c201b15e3d6e4d1a3b08c3ae91ff152360de5a4a9c807a51441` | model/effort absent |
| Tasker | `.codex/agents/tasker.toml` | `8f434d69c3c9ea1c1c4c30e156ad23b3f6baeeb9cc40ab467de280739ee774de` | model/effort absent |
| Reviewer | `.codex/agents/reviewer.toml` | `07f711cb97c7d258277d4b0088186cc102abaedc6ed79fa2a404c5773597b790` | model/effort absent |
| Coder | `.codex/agents/coder.toml` | `3692abc7bcd75b7140baa439cf3876591989bf9d59f4088517f7f484935de033` | model/effort absent |
| Code Reviewer | `.codex/agents/code-reviewer.toml` | `f7ba175fcfbeb30a7aa8329abcf2f6c6e92977302eb131ce1826172e35775ca4` | model/effort absent |
| Wiki Curator | `.codex/agents/wiki-curator.toml` | `0def82ab62e5d7458ca6054c28c270e91286e0fb315fb734a002ed3b1b9aed76` | model/effort absent |


## Evidence Boundaries

Native field/value support, settings application, consumer lifecycle, exact live dispatch and effective child settings remain unfinished. Host model metadata alone does not satisfy the support gate. Installed running-controller inventory will remain unchanged; disposable consumers validate source packages.

## Identity Migration and Foundation

- T001–T003: portable baseline, lifecycle scenario fixtures and eight-role package manifest recorded.
- T004: strict manifest, regular source, TOML, archive allowlist/version and current reset-target validators; four focused package validation tests passed within the 26-test catalog suite. No consumer-copy ownership fields added.
- T005–T010: eight exact `FlowKit-` names and `flowkit-*.toml` local/canonical copies migrated; original descriptions/instructions remain byte-identical after removing only the name prefix. Model and effort remain unapplied pending T012.
- T011: recursive coverage observed **49 delegated assignments** across ten active workflows; all YAML objects equal the attributable preimplementation baseline after reversing only the identity prefix. Step IDs, delegation flags, transitions, human gates, loop bounds and probe timing are unchanged. Deprecated Start Feature is byte-identical.
- Source `.gitignore` already contains Python environments/build artifacts, caches and temporary-file patterns; no setup changes required.

### Commands and outcomes

All commands use the existing skill-tools interpreter (PyYAML is absent from mise-selected Python; no environment changed):

```text
python -m unittest discover -s tests -p test_agent_configs.py  # 5 passed
python -m unittest discover -s tests -p test_controller.py     # 51 passed
python -m unittest discover -s tests -p test_workflow_graph.py # 15 passed
python -m unittest discover -s tests -p test_workflow_paths.py # 28 passed
python -m unittest discover -s tests -p test_catalog.py        # 26 passed
python tools/validate_workflows.py --fail-on-unexplained       # zero unexplained terminals
```

### Retained unprefixed source references

- `controllers/flow-kit/controller-protocol.md:14` — Feature 015 desktop experiment, historical settings/selection evidence.

## T012 Support Gate: Prior Desktop Evidence Recovered

Approved settings remain unapplied. The original CLI-only investigation below overlooked accepted desktop evidence. The recovery section supersedes its claim that native field loading and every approved pair lack evidence; current-role dispatch and effective settings remain separate checks.

| Exact role | Requested model | Requested effort | Native agent-file field/value support | Live exact dispatch | Effective settings |
|---|---|---|---|---|---|
| FlowKit-Roadmap Agent | `gpt-6.1-sol` | `low` | unverified | not run | unverified |
| FlowKit-Specifier | `gpt-6.1-sol` | `high` | unverified | not run | unverified |
| FlowKit-Planner | `gpt-6.1-sol` | `high` | unverified | not run | unverified |
| FlowKit-Tasker | `gpt-6-luna` | `high` | unverified | not run | unverified |
| FlowKit-Reviewer | `gpt-6.1-sol` | `high` | unverified | not run | unverified |
| FlowKit-Coder | `gpt-6-luna` | `high` | unverified | not run | unverified |
| FlowKit-Code Reviewer | `gpt-6.1-sol` | `medium` | unverified | not run | unverified |
| FlowKit-Wiki Curator | `gpt-6.1-sol` | `low` | unverified | not run | unverified |

### Tested methods

Codex CLI `0.157.1` was tested with eight disposable standalone `.codex/agents/*.toml` candidates containing approved pairs, without applying them to source or consumer copies:

- `codex debug models --bundled` exposes model catalog metadata. This is advertised support only.
- `codex --no-daemon -C <disposable-project> -c features.multi_agent=true debug prompt-input <bounded-inspection-prompt>` succeeds but returns model-visible messages without custom-agent settings or names. It supplies no agent-file parsing evidence.
- Native stdio app-server `initialize`, `config/read` for the disposable project and ephemeral `thread/start` succeed without a model turn. The returned effective main-thread config/settings do not expose the standalone custom-agent definitions or prove their parsing. Main-thread initialization is not custom-agent dispatch.
- Native read-only introspection required approved sandbox escalation after the restricted command returned an OS permission failure. No model turns, delegated child agents, account mutations or running installed-controller refresh occurred.

### Exact blocker and resumption

T012 requires attributable tested-client parsing/value support before T014/T015 apply settings. The bounded native introspection available here does not supply that evidence, so T012 is unfinished and T013–T035 remain unexecuted under the sequential task plan. This is an evidence gap, not a demonstrated rejection of either model.

Resume by obtaining native custom-agent parsing/value evidence for these eight disposable candidates on a supported client, preserving the required separation from live dispatch and effective-setting proof. Any changed evidence requirement or alternate support decision belongs to the operator. The source migration is incomplete as a deliverable: no new agent catalog artifact, bundle pin, cache/copy/reset implementation, coordinated versions or released package is claimed. Existing installed components remain unchanged.


## Core Convergence and Implementation Attempt: 2026-10-04

The operator invoked the core Converge/Implement loop. A present-state assessment found missing approved settings, partial instruction refinements, missing consumer package/lifecycle operations, incomplete coordinated version/migration delivery, and unfinished consumer/live/final validation. Converge appended T036–T040 without changing any prior task content. These tasks reference, rather than replace or waive, T012–T035.

Core Implement prerequisites and both readiness checklists pass (planning 14 checked, requirements 16 checked, no unchecked items). The tested CLI still reports `0.157.1`. T036 requires the attributable native custom-agent field/value evidence already required by T012; the previously tested read-only methods document an unresolved evidence gap. No new support proof is available from this invocation. Under the existing sequential dependencies, T037–T040 cannot proceed before this gate. No approved model settings were applied or task completion claimed.

The existing focused suites were rerun with the configured skill-tools Python interpreter: 125 tests passed across agent configs, catalog, controller, workflow graph and workflow paths. Workflow validation reports zero unexplained terminals. A preliminary run under the default Python failed because PyYAML was absent; rerunning in the existing configured environment resolved that environment issue without dependency changes. These checks validate the implemented foundation/identity work, not the missing delivery or native setting support.

No before/after Converge hooks are registered. Core Implement's optional roadmap brief remains uninvoked; no mandatory implementation hooks are registered. Recovery requires supported-client evidence for all eight approved candidate pairs, or an explicit operator decision changing the support gate with reconciled artifacts. The convergence goal remains incomplete, with T012–T040 unfinished.


### Support-gate revalidation: protocol surface

A follow-up check still observes Codex CLI `0.157.1`. Its supported `app-server generate-json-schema --experimental` command generated the current protocol schema in temporary storage. Inspection of generated request and configuration schemas found no custom-agent parsing/selection request or response field exposing a candidate role's resolved configuration. Ordinary configuration and model-list surfaces are present, but do not establish candidate-file parsing or exact-role dispatch. This adds protocol-surface evidence to the prior bounded runtime inspection; it does not prove the CLI rejects the candidates.

Official [Subagents documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents), fetched 2026-10-04, continues to document standalone agent files and explicit `model`/`model_reasoning_effort` precedence. Documentation and protocol generation do not discharge the tested-client support gate. T012/T036 remain unfinished; no model settings, completion markers or approved evidence requirements changed.


## Recovery of Accepted Desktop Evidence: 2026-10-04

The operator recalled inspecting the launched children in the desktop UI. The existing [Feature 015 validation record](../015-agent-roles-assignment-inheritance/validation.md#named-agent-dispatch-gate) already records the accepted screenshots: project `Coder` returned its unique instruction marker with inherited Sol/medium settings, then returned its updated marker with explicit `model = "gpt-6-luna"` and `model_reasoning_effort = "high"`, displayed as GPT-6 Luna · High. The record identifies source revision `8522d05e0328741c40dee17e04a05543b7cbfa81`, Specify `1.0.10.dev0+pegagio.2` and CLI `0.157.1`; the desktop app version and exact UI action were not captured. Those limits were explicitly accepted. Later Consumer B desktop observations corroborate explicit Luna/high on Architect and GPT-6 Sol/high on Verifier.

This evidence establishes standalone custom-agent field loading, inheritance and the explicit Luna/high pair on the observed desktop path. CLI introspection limitations do not invalidate it. GPT-6 Sol is not GPT-6.1 Sol; the older Sol observations cannot establish the newer exact model's support.

| Approved roles | Requested pair | Reusable support evidence | Remaining check |
|---|---|---|---|
| FlowKit-Coder, FlowKit-Tasker | `gpt-6-luna` / `high` | Accepted Feature 015 explicit desktop setting observation | Current prefixed-role dispatch/effective-setting checks remain T033; no repeated field-mechanism test required |
| FlowKit-Roadmap Agent, FlowKit-Wiki Curator | `gpt-6.1-sol` / `low` | Field mechanism established; exact pair not observed in recovered record | One native desktop support check for this distinct pair |
| FlowKit-Code Reviewer | `gpt-6.1-sol` / `medium` | Field mechanism established; exact pair not observed in recovered record | One native desktop support check for this distinct pair |
| FlowKit-Specifier, FlowKit-Planner, FlowKit-Reviewer | `gpt-6.1-sol` / `high` | Field mechanism established; exact pair not observed in recovered record | One native desktop support check for this distinct pair |

Under the operator's instruction to recover and narrow verification, T012/T036 now reuse this accepted evidence and require only three outstanding distinct-pair desktop support checks. Mapping shared pair evidence to multiple roles establishes setting support, not successful dispatch of every renamed role. T033 retains current exact-role dispatch and effective-setting results or explicit gaps. No evidence requirement was silently waived, no backend execution was inferred from a UI label, and no task was marked complete solely from this recovery. The remaining native checks require a surface that can launch the disposable configured candidates; the CLI paths previously tested did not establish that capability.


## T012 Support Check Completed: 2026-10-04

Following the operator's instruction to proceed with the narrowed checks, three native child launches explicitly requested `gpt-6.1-sol` with `low`, `medium` and `high` respectively. All launches succeeded and the children returned their expected no-work readiness responses. The activity names were `sol_low_availability_probe`, `sol_medium_availability_probe` and `sol_high_availability_probe`; each used the native default agent type with an explicit model/effort request and performed no project work. These are bounded value-availability probes, not substitute FlowKit workflow children or proof of custom-role selection.

T012 is satisfied by combined evidence: accepted Feature 015 desktop configuration observations establish native field loading and explicit Luna/high support; the three current native launches establish availability of the remaining Sol pairs. This is support evidence assembled from distinct observations, not a claim that all eight current files have been dispatched or their effective settings observed. T012's wording now records that method; its per-role mapping is the approved shared-pair table in the recovery section. T036 remains unfinished because it also requires T013/T014 configuration validation and application.

A separate current native-selection check requested `FlowKit-Reviewer` and was rejected with `unknown agent_type` before any child launched. No temporary agent files were written. Current renamed-role selection is therefore unresolved in this chat, and the installed unprefixed workflow assignments still need coordinated delivery. T033 retains those exact-role and effective-setting checks; successful generic availability launches do not discharge them.

The support check no longer blocks T013/T014. Approved settings remain unapplied at the end of this bounded verification request; no effective-setting claim, consumer-delivery result or completion of T013–T040 is inferred.


### Operator UI Confirmation of Sol Probe Settings

On 2026-10-04 the operator confirmed in the Codex desktop child panes that the three launched probes displayed Sol with high, medium and low effort respectively. This corroborates the explicit `gpt-6.1-sol` requests for `sol_high_availability_probe`, `sol_medium_availability_probe` and `sol_low_availability_probe` with observed UI model/effort indicators, rather than inferring effective settings from readiness responses. The confirmation is operator-observed desktop evidence; it does not independently measure backend execution or establish dispatch of the eight current prefixed custom roles. No additional screenshots, repeated pair probes or CLI parsing checks are required for these three supported pairs. T033 still records current prefixed-role dispatch and setting observations or explicit gaps separately.


## Resumed Implementation and Final Evidence: 2026-10-04

This section supersedes earlier statements that settings and delivery are unapplied. Support gate T012 is complete using the accepted desktop evidence and operator-confirmed Sol probes above. Implementation now includes all eight approved native settings, structured question/blocker contracts, deterministic packaging, validated available-default cache, consumer-owned install-missing/reset, coordinated versions and installation guidance. Independent review and current exact-role native dispatch remain unresolved. Neither support evidence nor passing source tests waives those obligations.

### Source and package coordinates

The implementation is an uncommitted snapshot based on source revision `ced0e9e67e49d1ff757e41e313445d5b504a8f9f`. Tested Specify is `1.0.10.dev0+pegagio.2` on Python `3.11.16`; Codex CLI is `0.157.1`. Desktop app version remains unavailable. Agent instructions and settings are content-addressed by the package source digest, independently of the base commit. No package was published and no Git integration occurred.

| Component | Current snapshot version | Observed integrity |
|---|---|---|
| `spec-kit-flow` bundle | `0.14.0` | Pins controller, agent package and ten active workflows |
| `flow-kit-controllers` | `0.6.0` | Artifact SHA-256 `bc96a2236230ed4248f4bb5fd066c21dcde671f4d0260f937529ec5e601e122e` |
| `flow-kit-agents` | `0.1.0` | Artifact SHA-256 `410266fc9dc79a78ed267c58a96e745a7e1980db6f9bd1c9a444b15402bb7f0f` |
| Agent canonical source | `0.1.0` | Source SHA-256 `40e0ee5b2862ff7e701fcc744fb8a75965fe73b4751d0f7980622e557dc1cf5c` |
| Select Feature, Specify, Wiki Lint/Update | `0.2.0` each | Source SHA-256 recorded and verified in `catalog/release.json` |
| Clarify, Plan, Tasks, Analyze/Remediate, Implement, Converge | `0.5.0` each | Source SHA-256 recorded and verified in `catalog/release.json` |
| Closeout | `0.7.0` | Source SHA-256 recorded and verified in `catalog/release.json` |
| Deprecated Start Feature | `0.6.0` | Unchanged stop-only source; excluded from active bundle |

Independent extension coordinates remain unchanged: `flow-roadmap` `0.2.1` at `86b0cc70054b7eca4d715fbccd6448165a85fc1f`, `flow-wiki` `2.0.1` at `0292ff66758e36849cee4e0f6bcbdac51629e1d0`, and `flow-feedback` `0.2.1` at `6b4c680d0b284f08e149cd0464e4c1f752b5cb7c`; their original artifact digests/source repositories remain in `catalog/release.json`. Snapshot generation reused pinned independent artifacts, and `verified_release()` verified current package pins, source correspondence and artifact digests. New controller/agent artifacts were generated at new coordinates; previous archives were retained.

### Instruction and authority self-review

Compared with the baseline native role files, each description and original responsibility/exclusion instruction is preserved. Every role receives the exact name prefix, approved native model/effort fields and the same appended output contract: relative evidence, facts distinguished from inference, structured questions containing `kind`, `step_id`, `question`, `options`, `allow_custom_answer`, main-task relay to the same child, and exact blockers/resumption actions. No tool, sandbox or other permission fields were added. Canonical and local copies match. This is an author inspection, not independent review.

| Role | Approved pair | Preserved mutation/output boundary |
|---|---|---|
| FlowKit-Roadmap Agent | `gpt-6.1-sol` / `low` | Scoped ledger evidence and smallest patch; apply only already-approved exact patches; never self-approve |
| FlowKit-Specifier | `gpt-6.1-sol` / `high` | Selected spec/checklists and command-required self-check; no plan/tasks/code/roadmap/pointer changes |
| FlowKit-Planner | `gpt-6.1-sol` / `high` | Selected planning outputs and command-required self-check; no task generation/code/scope changes |
| FlowKit-Tasker | `gpt-6-luna` / `high` | Selected task derivation with preserved IDs/completion and self-check; no upstream/code mutation |
| FlowKit-Reviewer | `gpt-6.1-sol` / `high` | Read-only selected artifact assessment; no edits, self-review or acceptance |
| FlowKit-Coder | `gpt-6-luna` / `high` | Selected eligible implementation tasks and relevant checks; no re-specification/planning/tasking or consequential decisions |
| FlowKit-Code Reviewer | `gpt-6.1-sol` / `medium` | Read-only selected implementation/test inspection; no own-work review, edits or invented tasks |
| FlowKit-Wiki Curator | `gpt-6.1-sol` / `low` | Authorized registered sources and cited wiki updates; no feature/roadmap edits or unauthorized ingestion |

All roles preserve workflow/Git/acceptance prohibitions. Suitability rationale is documented in `docs/installation.md` and approved research; no benchmark or savings claim is made. Author self-checks remain distinct from independent review.

### Disposable consumer matrix

`tests/test_agent_delivery.py` exercises the approved scenario inventory from `tests/consumer-fixtures/agent-delivery/scenarios.json`, with focused package cases in `tests/test_catalog.py`. Lifecycle tests are colocated in the dedicated delivery module rather than expanding the existing controller-only lifecycle class. Byte comparisons are disposable test assertions, never a runtime ownership ledger.

| Input/operation | Expected and observed result |
|---|---|
| Clean bundle/catalog installation | Native Specify initialized disposable consumer; eight defaults copied after component/controller install |
| Repeat install with consumer model/instruction edits | Existing prefixed files byte-identical; reported `preserved-existing`; no customization classification |
| Existing unprefixed/unrelated definitions | Old `Coder` and unrelated files preserved; missing current names copied |
| Ordinary refresh | Defaults cache updated; every copied file byte-identical |
| Fixture package `0.2.0` with new role | Refresh leaves new role absent; explicit install-missing copies only absent entry |
| Fixture retirement | Reset-all selects current manifest only; obsolete/unrelated files retained |
| Reset-one | Only selected current target restored; warning explicitly states discarded customizations |
| Reset-all | Exactly current manifest targets restored; other files preserved |
| Bundle removal | Cache removed; all consumer agent copies, unrelated files and feedback retained |
| Invalid selectors/cache/digests/version/inventory | Failure before agent writes; no echo of an unknown private selector; previous cache retained |
| Duplicate identities, directory/symlink targets or ancestors | Zero agent writes; actual unsafe selected target identified; no readiness claim |
| Unparseable unrelated TOML | File retained with portable warning; full native readiness remains unverified |
| Injected second-file install/reset failure | First atomic write complete, second failed, remainder not attempted; unaffected bytes retained; same explicit retry completes |
| Injected cache swap failure | Previous directory restored; prior defaults retained |
| Package construction | Deterministic canonical-only archive; symlink manifest/unlisted members rejected; source/artifact digests and bundle pin verified |

Native install/refresh/reset/remove ran against the actual pinned Specify CLI and a localhost catalog in disposable consumers. Tests do not establish live custom-role dispatch. Updated installation documentation includes acquisition, direct customization, cache-only refresh followed by install-missing, selected reset, retirement/mixed-version recovery and removal.

### Checks and exact limitations

Checks used the existing skill-tools Python environment; no dependency or environment change was made. The final focused command (`PYTHONPATH=tests python -m unittest test_agent_delivery.AgentDeliveryTests test_catalog test_agent_configs test_bundle_lifecycle.FlowKitControllerLifecycleTests`) passed 51 tests. The final discovery run with `SPECIFY_BIN` set passed 154 tests with one skipped environment-dependent class. This includes the native agent-bundle lifecycle test and source/controller/snapshot suites. `tools/validate_workflows.py --fail-on-unexplained` reports zero unexplained terminals and 49 active delegated assignments. `git diff --check` passes.

The skipped legacy `BundleLifecycleTests` class was separately enabled using the pinned roadmap/wiki artifacts as source fixtures. That expanded run executed 153 tests and had one failure: `test_installUpdateRemoveAndFeedbackExport_expectedGenericConsumer_whenCatalogIsAvailable` reaches `assess-clarification-after-session`, then native Specify reports `Cannot dispatch prompt: integration None CLI not found or not installed.` Explicit `integration=codex` input did not fix it and was removed. The source prompt omits `integration` both at the base revision and now. This is an observed inherited native-CLI limitation, not a passing check. The fixture failure is retained; no unrelated workflow integration/probe redesign was applied to force a green result. Installation loader success is not native named-agent dispatch proof, as documented in the installation guide.

Graph/path/controller tests preserve delegation, main-task human gates, probe/capacity semantics, manual fallback, deprecated Start Feature and generic Diagram boundaries. Feature 016/018 behavior was not introduced or changed. Current reference reconciliation corrected an obsolete installation paragraph that excluded agent delivery; historical records and wiki provenance were retained.

### Native evidence and remaining review

For all eight roles, configuration presence, exact approved pair and canonical/local consistency pass. Native field/value support is satisfied by the previously accepted evidence and current operator-confirmed Sol pair observations. Exact live dispatch of the eight renamed roles remains unverified; their effective settings remain unverified. The current session rejected `FlowKit-Reviewer` and, on this resumed pass, `FlowKit-Code Reviewer` with `unknown agent_type` before a child launched. No default or old-name agent was substituted. The other six names have not been claimed tested successfully; this chat exposes the previous unprefixed role registry. No further pair/field probes are required.

Independent review could not launch, so T017/T037 remain open. T033/T040 remain open pending all-eight exact native checks from a session that loads the renamed project definitions. Resume those checks and independent review after opening the project in a fresh Codex chat; if any exact name remains unavailable, preserve the exact blocker and resolve the client/project configuration rather than substituting another role. Current installed source-checkout controllers still carry the older unprefixed inventory; use coordinated catalog installation/refresh, not manual installed-copy edits, before an installed workflow dispatch check.

| Requirement group | Present evidence | Residual gap |
|---|---|---|
| FR-001–002, SC-001 | Eight source identities, recursive assignments, package pins, current reference audit | Current native role inventory not reloaded |
| FR-003–006, SC-002 | Approved pairs, support evidence, authority-preserving contract diff and self-check | Assigned independent instruction/settings assessment |
| FR-007 | Exact-name validation and unavailable-name stop without fallback | Current all-eight native selection results |
| FR-008–011, SC-003–004 | Deterministic package, consumer lifecycle matrix, byte preservation, portable reports and docs | None in tested delivery scope |
| FR-012–014, SC-005–006 | Versions/digests and distinct evidence categories above | Live renamed roles/settings unverified; inherited native CLI fixture fails |
| FR-015–016, Constitution I–V | Unchanged topology/probes/capacity/manual authority and generic component boundaries | Independent final review outstanding |

Optional core Implement roadmap brief/debrief and wiki-ingest hooks were identified in `.specify/extensions.yml` and left for operator invocation (`$speckit-flow-roadmap-brief`, `$speckit-flow-roadmap-debrief`, `$speckit-flow-wiki-ingest`). No mandatory implementation hook or Converge hook is registered. No roadmap, wiki, feature acceptance, publication, commit, push or merge is inferred.


## Resumed Core Convergence Outcome

Outcome: `tasks_appended`, not `converged`. Findings F6/F7 are the two high-severity partial gaps described above; no new missing/contradictory/unrequested buildable behavior was found in the bounded Feature 017 source inventory. Core Converge appended T041/T042 under Phase 8 without changing earlier tasks. Thirty-six of the original 40 tasks have completion evidence; T017/T033/T037/T040 and the two new resumption tasks remain open. The current chat cannot launch the required renamed review role. Core Implement cannot complete those evidence tasks by substituting another role, repeating already accepted model-pair probes, or treating automated checks as live evidence. Resume with a client session that loads the migrated definitions and then rerun core convergence after the independently reviewed/native checks complete.

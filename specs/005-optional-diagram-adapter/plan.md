# Implementation Plan: Coordinate Diagram work through an optional Farmboy adapter

**Branch**: `reboot/2026-10-16/prompt-first` | **Prepared**: 2026-10-18 | **Spec**: [spec.md](spec.md)

**Input**: Approved005 specification including FR-021 direct-entry checks and the isolated-seam review consideration;21 requirements,8 success criteria and21 scenarios. FR-020 external-software prohibition and the settled checkpoint rule remain controlling. Spec approval is not full-plan approval.

**Status**: Approved full plan — Selected for implementation through the installed Farmboy delivery composite. No merge, push, integration, result acceptance or real consumer instruction edit is authorized.

## Summary

Implement one optional skill, `$farmboy-diagram-work`, with an adjacent native-protocol reference. Ordinary operator intent follows explicitly established project routing; the agent uses this skill transparently only on a deliberately enabled Diagram route. Standalone routing remains standalone, and tool availability alone enables nothing. The same agent composes the existing Diagram CLI and Farmboy's three external entries, plus ordinary clarification, for exactly one selected segment. It verifies consumer Git/workspace/artifacts itself, reports attributable native facts and records/releases at the prescribed human handoff. Diagram retains coordination authority and validates report consistency; it never gains consumer filesystem/Git access. Each of the three Farmboy-owned entries receives one small routing seam before effects and a coordinated-return rule; established standalone behavior remains independent of Diagram.

The proposal deliberately uses agent-readable composition rather than a Python wrapper, service or new command framework. It specifies invocation/transport, disclosed segment-launch checkpoint authority, restriction/isolation stops, uncertain native outcomes, current-authority continuation and compatible native Goal completion. All new machinery is enumerated below for the full-plan decision.

## Table of Contents

The proposal includes design decisions, source scope, future verification and the saved review boundary.

- [Technical Context](#technical-context)
- [Constitution Check](#constitution-check)
- [Project Structure](#project-structure)
- [Project routing and deliberate opt-in](#project-routing-and-deliberate-opt-in)
- [Direct-entry seam and current adapter context](#direct-entry-seam-and-current-adapter-context)
- [Design and execution sequence](#design-and-execution-sequence)
- [Machinery and alternatives](#machinery-and-alternatives)
- [Verification and delivery ordering](#verification-and-delivery-ordering)
- [Complexity Tracking](#complexity-tracking)
- [Saved review handoff](#saved-review-handoff)

## Technical Context

**Language/Version**: Markdown agent skill/reference; no new executable implementation language or package. Existing consumer Git/JSON tooling; skill-validation scripts, if needed, use `~/.codex/venvs/skill-tools/bin/python` per project instructions.

**Primary Dependencies**: Existing installed Farmboy three external entries and ordinary Spec Kit clarify; supported Diagram CLI Feature6/schema16, Project2/Issue3 report boundary; existing native Goal tools only when explicitly selected/available. The adapter is optional; no dependency is added to standalone Farmboy. No install or new library is proposed.

**Storage**: Existing canonical Git artifacts and normal feature notes; native Diagram selected store owns coordination and receipts. Ephemeral native JSON request files only; no adapter database, manifest, cache, lock, event log or approval register.

**Testing**: Focused case specification in `tests/fixtures/diagram-adapter/cases.md`; independent real native executing/evaluating sessions over disposable repositories/stores, existing fixtures for three standalone regressions. Static source/link/privacy/coverage checks complement, never replace runtime acceptance.

**Target Platform**: Current Codex agent skill environment with authorized local Git and a supported Diagram CLI. No new cross-platform launcher or remote service.

**Project Type**: Optional agent workflow composition in the existing repository skill layout.

**Performance Goals**: No service throughput/SLA required. One selected segment per invocation; zero duplicate accepted external effects and zero invented authority. Reuse native reads/receipts and complete bounded work before human handoff rather than add polling, repair counters or background work.

**Constraints**: 005 implementation MUST remain within Farmboy's optional adapter, minimal routing checks in its three own entries, its own documentation/guidance and focused acceptance fixtures. It MUST use existing external APIs/skills without changing Spec Kit, Diagram or any other external software project's source, skills, hooks, configuration or implementation. A required external software patch is an exact compatibility blocker, not scope to repair elsewhere. Deliberate consumer-project opt-in guidance is separate from external software implementation: it may be applied only to the specifically identified consumer instruction file with explicit authorization; availability, route selection or this plan alone grants no external edit permission. Same model/effort; no per-step delegation, new controller, automatic phase expansion, store migration/reset, legacy fallback, Spec Kit/core-tool or constitution edits, merge/push or integration executor. Actual physical verification belongs to consumer. Explicit human gates and project policy survive every path.

**Scale/Scope**: Four explicit segment choices serving one feature per invocation; one active owner per feature; independent features only in isolated branches/worktrees, without a fleet/scheduler.

## Constitution Check

Pre-research and post-design checks both pass as a proposal, with no constitutional exception. These checks do not constitute runtime acceptance.

| Principle | Design response | Gate |
| --- | --- | --- |
| I — Flow-back/history | Current005 artifacts remain one coherent change set; material meaning changes return to review. Preserve historical001–004 and old005 brief as historical snapshots. Only integration merge freezes history. | PASS |
| II — Prescribed authority | One explicitly selected segment; existing skills own their prescribed loops and actual hooks. Separate analysis and repair; disclosed segment-launch authority covers only necessary scoped checkpoints with normal hooks and user overrides, never an automatic later workflow, decision or integration. | PASS |
| III — Toil and explicit bounds | One optional composition removes native bookkeeping burden; ordinary genuine answers/reviews remain separate. No controller/store/counters; saved artifact/current-operation inspection supports resume. | PASS |
| III — Independent actual verification | Future tasks require separate native executor/evaluator, installed skill, real disposable Git/coordination, actual human stops and all standalone regressions. No simulation-only acceptance. | REQUIRED BEFORE DELIVERY ACCEPTANCE |

Local roadmap004 is verified;005 remains selected/in-progress. No lifecycle/status amendment is part of this planning run. Current028 accepted committed interfaces support the design now: closeout HEAD `8c938d7273b7e5f648ff2c9b88871f7bd88691ff`, implementation `975094763a0e8021e49c68565d9f58c239855e6e`, verified31/31. Acceptance and commit are established, with no merge/release/deployment claim. Before later dependent implementation, recheck actual source/binary/store compatibility and inspect drift, not a new product-review gate.

## Project Structure

The following is exact proposed scope; source paths do not yet exist merely because they appear here.

### Documentation (this feature)

Standard planning outputs remain canonical design material, not runtime state.

```text
specs/005-optional-diagram-adapter/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── adapter-entry.md
│   └── native-mapping.md
├── tasks.md
├── checklists/requirements.md
├── roadmap-reviews/brief-20261018T212232Z.md  # historical preparation snapshot
└── validation/                            # ordinary evidence, when produced
```

### Source Code (repository root)

The recommended implementation adds one optional entry/reference, one guide and a focused case document. It modifies only a small routing seam and coordinated-return behavior in the three Farmboy-owned entries; all Diagram protocol details stay in the adapter/reference. Spec Kit and other external software remain unchanged.

```text
.agents/skills/farmboy-diagram-work/
├── SKILL.md
└── references/native-protocol.md
docs/diagram-adapter.md
README.md                                 # optional routing/guide link only
.agents/skills/farmboy-prepare-specification/SKILL.md      # minimal entry/return seam
.agents/skills/farmboy-prepare-implementation-plan/SKILL.md # minimal entry/return seam
.agents/skills/farmboy-deliver-approved-plan/SKILL.md       # minimal entry/return seam
tests/fixtures/diagram-adapter/cases.md
```

**Structure Decision**: Follow current thin Markdown skill/fixture architecture. No Python application, new module tree, installer, new Spec Kit extension, packaging metadata or tool dependency. The reference documents existing action-specific native fields/commands; it is not a schema validator or alternate authority register. Existing guides/fixtures are read/reused as appropriate rather than rewritten wholesale.

## Project routing and deliberate opt-in

Add an ordinary-intent routing example to Farmboy's own `docs/diagram-adapter.md`, with a README discovery link. Add the small route check to each of the three Farmboy-owned entries; no Spec Kit command/extension/hook changes. The exact consumer enabling action is a bounded addition to that consumer project's existing `AGENTS.md`, made by the operator or by an agent separately authorized to edit that named file. The operator supplies actual existing Diagram project/store references and makes the optional Farmboy skill available through already supported host/project mechanisms. Missing availability stops setup;005 provides no installer, software patch or new configuration framework. This plan does not authorize or perform any real consumer guidance edit.

Proposed copyable paragraph, with illustrative values replaced during deliberately authorized setup:

> For this consumer project, use Farmboy for ordinary feature requests. Diagram coordination is deliberately enabled for project PROJECT using the existing selected Diagram configuration/store STORE. Resolve the feature and exactly one segment from the request and current context: “start feature12” selects specification preparation; “clarify this feature,” “plan this feature” and “deliver this feature” select only that segment. Internally use the optional farmboy-diagram-work skill with the resolved context; the operator need not name it. Ask for missing/ambiguous routing or selection only; preserve genuine product questions and required reviews. Obtain current Diagram authority before effects. Missing enabled-route capability is a blocker, not permission to install, patch software or fall back. Disclose that explicit segment launch includes necessary feature-scoped checkpoint commits with normal hooks, subject to explicit restrictions and safe feature-only staging; no merge or push. Existing human gates and the whole-adapter Goal endpoint remain mandatory.

The standalone alternative is a deliberate project instruction to use existing standalone Farmboy entries for the same ordinary intent, without Diagram. Absent/conflicting routing asks targeted input; merely finding a Diagram binary or skill never enables it. An unambiguous established route is not repeatedly reconfirmed. Opt-in only establishes routing: it grants no segment launch, approval, ownership, Goal activation, arbitrary consumer edit or external software modification.

Consumer instruction configuration is distinct from implementation in Spec Kit/Diagram/dependencies. Those software projects remain untouched, including their skills/hooks/configuration. If existing APIs/skills cannot satisfy this design, report the exact incompatibility and stop dependent work; do not broaden scope. Disposable test-consumer guidance changes require explicit fixture authorization and never alter real consumers or external software repositories.

## Direct-entry seam and current adapter context

Each Farmboy entry checks the explicit project route before mutations, native Goal changes or selected segment effects. Reads needed to establish routing/context are allowed. The same seam covers ordinary-intent dispatch and direct named-skill invocation:

| Observed route/context | Entry action |
| --- | --- |
| Established standalone | Continue existing standalone body; no adapter/Diagram lookup or dependency |
| Missing/ambiguous route or selection | Ask only targeted unresolved input before effects |
| Deliberately enabled Diagram, unavailable adapter/capability | Save precise limitation and stop; no fallback/install |
| Enabled Diagram, no current adapter invocation | Hand the same explicitly selected segment to the optional adapter once; propagate its return and do not then run the original body again |
| Enabled Diagram, already-current adapter context | Verify selected project/feature/segment, current owner/session/run/epoch, applicable input/approvals, workspace association and whole outer endpoint using the adapter/reference's existing native checks; continue only the selected existing external body |
| Claimed context is stale, foreign or unverified | Stop dependent effects for current verification; no new claim, automatic reacquire or recursive wrapper |

The adapter establishes and readbacks existing native authority before invoking an inner entry. Existing context is ordinary invocation/session evidence plus current native facts, not a new packet/token, persisted wrapper marker, callback API or ownership store. A Boolean “inside adapter” flag or historical receipt is insufficient. Reuse the existing external-entry inputs; add no mandatory serialized context schema. The adapter/reference owns native verification details so the three entry seams do not copy claim/link/report field logic.

When the core is executing inside the verified adapter invocation, it returns local artifacts/outcome to that invocation and does not release Diagram ownership or complete the wider Goal. The adapter alone verifies/records/releases the full endpoint and completes/readbacks a separately selected matching Goal. Direct outer entry propagates that result without a second execution/report. Standalone Goal behavior remains prescribed; no automatic Goal or restart is introduced. Ordinary clarification remains the separately selected existing Spec Kit command under adapter-held authority; no fourth Farmboy skill is added.

This is one concrete Diagram routing branch per entry, with protocol confined to the adapter/reference. It honors the small-seam consideration without extracting a plugin API, registry, discovery mechanism, hook catalog, Jira support, multi-adapter framework, service or ledger. Compared with AGENTS-only routing, the seam covers direct named entry use. Per-Spec-Kit command hooks miss preparation and bracket inner/repeated commands rather than the full segment; none are added. Agent compliance must be independently observed in actual runs; no absolute interception guarantee is claimed.

## Design and execution sequence

The [research](research.md), [data model](data-model.md), [entry contract](contracts/adapter-entry.md) and [native mapping](contracts/native-mapping.md) supply the detailed proposal. User-story increments share only the optional skill and its adjacent reference.

1. **Read current authority before effects**: Resolve ordinary intent through explicit project routing. Deliberately enabled Diagram uses the adapter internally; standalone uses existing standalone entries. Ask only for missing/ambiguous routing/selection, never infer enablement from availability or silently fall back from unavailable enabled routing. Disclose the segment-launch checkpoint authority and honor explicit restrictions/overrides; selecting/viewing a feature alone grants none. Select explicit store/project/feature/segment, inspect current queue/Feature/approval facts and consumer instructions. Resolve ambiguity/missing capability with an exact stop. Never silently enroll/register/rebind, migrate a store or start another feature. For initial work use native claim first; for later work use current allowed acquire with required decisions/input pins.
2. **Prepare and verify externally**: After claim, create/select the actual consumer workspace under its rules. Inspect Git identity/topology/full branch/HEAD/cleanliness/declarations/checkpoint blobs/digests. Establish contained directory and pointer; compare lexical helper persistence before calls. Report link using native Feature6 fields; success consumes claim and admits initial draft run without an extra acquire. Diagram only checks report consistency.
3. **Execute selected capability**: Each Farmboy-owned entry applies the route seam above before effects; a verified current adapter call continues without recursive wrapping/claim/report, while a direct outer call enters the adapter once and only propagates its result. Same session/model/effort invokes one existing external Farmboy skill, or separately authorized ordinary clarify (`clarify/clarification` native authority). No competing roadmap, auto-selected optional hooks or automatic Goal/phase. Existing selected skills govern analysis/repair and delivery closeout.
4. **Record actual endpoint**: Verify current authority/input and local evidence again. Submit native handoff with correct checkpoint roles and accepted-spec versus plan-candidate separation; successful handoff completes/releases the run. Read back actual operation/current owner state. A local saved result is not accepted coordination. Dirty artifacts require honest base/current state. Explicitly launching one adapter segment includes disclosed authorization for necessary feature-scoped checkpoint commits with normal project hooks. Merely selecting or viewing a feature grants no commit authority. Explicit user restrictions/overrides remain controlling; this authority grants no merge or push. Stage only the selected feature changes: preserve unrelated staged, unstaged and untracked work, never sweep the entire workspace, and stop for targeted input if safe isolation cannot be established. Reconcile affected artifacts, verify staged scope and resulting commit; restriction/isolation stops or failed hooks/commits preserve work and remain incomplete. Explicit release preserves saved work if recording fails or needs input.
5. **End matching native automation**: One selected adapter objective includes its entire local/coordination/handoff endpoint; no nested Goal. Core skills return their segment result without completing a wider unmatched objective. Supported native completion/readback happens only after the complete matching endpoint is saved/read, before human waiting. Technical/Goal mismatch stays a limitation. No automatic Goal restart after answers.
6. **Continue only after separate selection**: Ordinary clarification acquires current authority and retains it while active between questions; saved review releases. Explicit whole-spec approval gates planning and explicit full-plan approval gates delivery. Human result acceptance and integration permission are separate. Material changes return to affected review; unchanged applicable approvals persist.
7. **Resume and uncertainty**: Inspect artifacts/current native authority/operation first. Accepted replay does not rerun Farmboy/Git or grant authority. Changed upstream/binding/input gets responsible reassessment and supported explicit release/reclaim when necessary, no semantic guess or upstream-integrated blanket gate. Existing recovery requires stopped-writer confirmation and preservation; no timeout takeover or cleanup.

## Machinery and alternatives

Every addition is proposed for full-plan review, not silently authorized by specification approval.

| Item | Responsibility and concrete need | Simpler alternatives / tradeoffs | Recommendation |
| --- | --- | --- | --- |
| One optional `farmboy-diagram-work` skill | Coordinate native authority, consumer verification, external invocation and result/release; removes manual orchestration | Documentation-only leaves the toil; separate adapter per segment duplicates guards; executable wrapper adds a second lifecycle | Add one skill; keep protocol there and minimal routing/return seams in all three Farmboy-owned entries |
| Small routing/return seam in each of three Farmboy-owned entries | Cover direct invocation before effects and preserve outer ownership/Goal endpoint | AGENTS-only discovery misses direct entry; per-command hooks have wrong boundaries; runtime interception/framework exceeds scope | Minimal route decision plus verified current context, no protocol duplication or new store |
| Existing project instruction paragraph in Farmboy guide | Route ordinary requests transparently after deliberate consumer opt-in | Mandatory skill names burden the operator; external hooks/patches violate scope; new config framework adds machinery | Operator-applied or separately authorized bounded consumer AGENTS.md edit; no actual external edit here |
| One adjacent native-protocol reference | Keep exact native operations/field roles reviewable without bloating entry text | Inline everything avoids another file but makes review/resume harder; copied schema validator drifts | One reference, native contract remains authoritative |
| Existing native request-file JSON | Carry action-specific facts to supported CLI with standard strict validation | Network transport adds service/auth/deployment; adapter packet/store duplicates authority | Native local JSON transport only; no new protocol |
| Consumer verification procedure | Establish actual workspace/Git/artifact truth that core cannot inspect | Trusting reports alone cannot establish physical truth; moving verifier into core violates029 | Explicit agent checks using existing tools, no verifier service/helper |
| Disclosed segment-launch checkpoint authority | Produce genuine committed evidence without repeated permission prompts | Feature selection alone or workspace-wide commits exceed authority; asking again for every prescribed checkpoint adds toil | Necessary feature-scoped commits with normal hooks and user overrides; preserve unrelated staged/unstaged/untracked work, stop on unsafe isolation, no merge/push |
| Standard design/evidence docs and focused fixture cases | Make design, coverage and actual independent observations reviewable | New receipt manifest/tracker duplicates files and native store | Existing feature notes/validation only; no runtime schema/store |
| Native whole-objective completion/readback | End at saved human boundary without confusing inner result with full adapter endpoint | Nested/live waiting Goals and custom continuation machinery conflict with existing skills | Existing supported controls only, no auto-creation/restart |
| Existing Diagram CLI and consumer Git | Optional adapter capability dependency | New library/transport installer expands scope; absence must be explicit | No installation/dependency changes; precise missing capability stop |

No scheduler, ownership service, daemon, ledger, attestation, accounting, polling/counter/reset/score, generic retry/recovery framework, integration executor or new persistent structure is proposed. Continuation uses current artifacts plus existing native operation inspection; repairs are useful in-scope work until fresh pass or exact input, not a newly programmed loop engine.

## Verification and delivery ordering

All runtime work below is future work, contingent on explicit005 plan approval and separately selected implementation. Nothing in this planning run demonstrates005 runtime compliance.

- Build the focused case document before source so acceptance names actual observed behaviors and failures. First useful increment is initial draft/handoff (US1); it is not full005 acceptance without US2–US4.
- Independently execute installed optional skill over one small disposable real feature through genuine clarification, applicable explicit TEST ONLY spec/full-plan/result decisions, repair and committed local delivery. Fixture decisions approve only fixture work. Separate executor and evaluator observe actual current authority, local files, native operations, release/readback and later selection.
- Independently observe ordinary-intent and direct invocation of all three modified entries, first adapter entry versus verified already-current context, stale/foreign/flag-only context refusal, no recursive execution/double claim/report and no early release/whole-Goal completion.
- Observe ordinary-intent routing with deliberate enabled/standalone project guidance, absent/conflicting routing, available-but-not-enabled tools, enabled-but-unavailable capability, no redundant routing confirmation and no external software patches or unauthorized consumer guidance edits.
- Cover the three external entries and ordinary clarification, all three standalone entries with no Diagram dependency, missing context/pointer lexical mismatch, stale input/authority/decisions, changed meaning/flow-back, lost responses/replay, pre/postlink interruption, blocked-dependency release, explicit recovery, same-feature conflict and two isolated independent features.
- Verify physical reports externally while Diagram has no consumer repo/Git access. Include a structurally consistent false report to demonstrate core's trust limit; do not call core acceptance physical proof. No integration/push/production reset is part of tests. Use existing native disposable coordination preparation only under future explicit test authority.
- Use scoped source/link/privacy/whitespace checks and fresh read-only analysis after final artifact changes. Delivery/convergence uses the separately selected existing composite; this plan does not activate it.
- Before future final005 commit, reconcile completed source/tasks/artifacts/evidence and report any still-unavailable post-commit observation as pending because it cannot yet exist. After the actual commit succeeds, the independent evaluator verifies the commit/tree/scoped artifact references before human result acceptance. Keep that post-commit observation in the review conversation/external evaluator evidence; no receipt-only tail commit or self-precondition.

## Complexity Tracking

No constitution violation or complexity exception is proposed. The machinery table explains every addition and alternative; the operator can approve or simplify it at full-plan review.

## Saved review handoff

**Awaiting full human plan review.** The direct-entry revision is explicitly approved and this proposal reconciles its21 requirements/8 criteria/21 scenarios. Three minimal Farmboy-owned entry/return seams replace the previous unchanged-core choice, with protocol confined to one optional adapter/reference. The external-software condition, checkpoint consent, feature-only staging and human gates remain intact. Prior analysis is historical; the fresh direct-entry analysis assesses current source. Full-plan approval and implementation remain pending. Current accepted committed028 Feature6/schema16 interfaces are reconciled against `validation/farmboy005-contract-baseline.json` in the authorized upstream worktree, closeout HEAD `8c938d7273b7e5f648ff2c9b88871f7bd88691ff`, implementation `975094763a0e8021e49c68565d9f58c239855e6e`, clean status, verified31/31. Committed contract/schema hashes match inspected source bytes; no merge/release/deployment is asserted. Earlier accepted-uncommitted observations remain historical in research/spec notes. Later compatibility recheck concerns actual current interfaces/capability/drift, with no new human review or commit gate.

Artifacts: [specification](spec.md), [research](research.md), [data model](data-model.md), [entry contract](contracts/adapter-entry.md), [native mapping](contracts/native-mapping.md), [validation guide](quickstart.md), [ordered tasks](tasks.md). The [fresh direct-entry analysis](validation/analysis-direct-entry.md) records current source coverage/freshness; [preceding routing/scope analysis](validation/analysis-routing-scope.md) retains its pre-delta source hashes and coverage; [checkpoint-authority analysis](validation/analysis-checkpoint-authority.md) retains the preceding source snapshot; [committed-baseline analysis](validation/analysis-committed-baseline.md) retains the preceding source snapshot; [preceding planning pass](validation/analysis-planning.md) is now a historical source snapshot; [initial analysis](validation/analysis-planning-initial.md) preserves the separate checklist-stage finding and authorized repair history. Any later affected edit invalidates that pass.

Checkpoint:005 standalone planning on actual branch `reboot/2026-10-16/prompt-first`, base `7e0f9e1a2b5a3c6fba62b49c599b72f7fba81876`, uncommitted approved spec metadata and planning artifacts. Setup returned feature label `005-optional-diagram-adapter`, not a changed Git branch. Requirements-file bytes, pointer, roadmap and all unrelated feature history remain preserved. The direct-entry spec delta is approved and reconciled, with the external-software condition preserved; full human plan review is pending. Prior native completion and analysis approve nothing. Explicit full-plan approval and separately selected work are required before implementation. Optional after-plan wiki ingest is unselected; no mandatory plan/tasks/analyze hooks are configured.

**Full-plan approval and selected delivery**: The operator explicitly approved this revised full plan and implementation. Reviewed plan SHA-256: `69042439944a48184607e0f7cb95ad8ed2d55581bc7ad8ae352204d6fa7c7d01`; reviewed36-task proposal SHA-256: `5f9ddbf444ba7ea3febe2c4f8467e572d1d5fd6862d697fa5a209c6e7267af6b`. Execute the installed `farmboy-deliver-approved-plan` composition through implementation, verification/convergence/flow-back, documentation and its scoped local delivery commit, then stop for human result review. FR-020, deliberate fixture-only test authority, no real consumer instruction edit, checkpoint consent and unrelated staging preservation remain controlling. Passing tests or native Goal completion do not accept the result or authorize merge/push/integration. No approval date is invented. Earlier pending-plan statements are historical and superseded by this explicit selection.


**Current delivery applicability**: The approved minimal optional skill/reference, three isolated entry seams and own guide/fixtures are implemented without new runtime machinery or external software changes. Final-source separate-session observations and independent evaluation are reconciled in [acceptance evidence](validation/acceptance.md), including one genuine-question-through-committed-result FBT-3 lifecycle and all three standalone ordinary/direct entries. Earlier future-work/pending-review prose describes the saved proposal; the explicit approval above and selected delivery supersede it for current execution. Reviewed product/design meaning and historical hashes remain unchanged. Required root analysis/convergence/closeout are recorded separately, T036 remains postcommit-only, and Farmboy005 result acceptance remains pending. Packaging/native JSON transport choices remain exactly those reviewed; no automatic integration or new Goal follows.

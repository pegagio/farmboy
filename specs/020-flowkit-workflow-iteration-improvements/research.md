# Research: FlowKit Workflow Iteration and Improvements

This research resolves technical design choices through current reviewed source and owner boundaries. It does not amend authority, prove all reported defects reproduced, or establish Codex runtime startup causation.

## Table of Contents

- [Observed Baseline](#observed-baseline)
- [Decisions and Alternatives](#decisions-and-alternatives)
- [Proposed Governing Reconciliation](#proposed-governing-reconciliation)
- [Owner Handoffs and Open Evidence](#owner-handoffs-and-open-evidence)

- [Lifecycle Amendment Research](#lifecycle-amendment-research)

- [Requested Scope Research](#requested-scope-research)

## Observed Baseline

The inspected source checkout HEAD is `8a90c078035da998447c362ff37dd314c0cb053f`; the current feature and roadmap are mutable working artifacts. The installed and source behavior examined is baseline evidence, not a live replay of historical observations.

| Surface | Observed contract | Source |
|---|---|---|
| Selection 0.2.0 | Interest cannot select; fresh choice and exact approval are mandatory; unclear lifecycle requires input | `workflows/speckit-flow-select-feature/workflow.yml` |
| Controller 0.6.0 | Generic gate parser treats a bare valid number as menu ordinal; `activate_feature` preserves extra fields, atomic write and same-target no-op | `controllers/flow-kit/scripts/python/controller.py` |
| Analyze/Implement 0.5.0 | Current analysis completeness concerns analyzer findings; implementation assessment does not establish shared checklist readiness | Corresponding source `workflow.yml` files |
| Core Implement | Every unchecked item blocks and asks a generic override; core Analyze is read-only; built-in quality and custom reviewer ownership differ | `pegagio/spec-kit`, `templates/commands/implement.md`, `analyze.md`, `checklist.md` and template/script layer; inspected core HEAD `e367aae92d6ff254a0608848e41c1b67e656db32` |
| Roadmap 0.2.1 | Interactive inferred creation/amendment requires explicit confirmation; brief lifecycle advancement is distinct from activation | `pegagio/spec-kit-flow-roadmap`, `commands/speckit.flow-roadmap.write.md`, `scripts/python/review_contract.py`; HEAD `86b0cc70054b7eca4d715fbccd6448165a85fc1f` |
| Agent 0.1.0 | Install-missing preserves existing files; refresh updates cached defaults; reset is explicit | `agents/flow-kit/manifest.yml`, `tools/catalog.py`, `docs/installation.md` |
| Worktree preparation | All eight `.codex/agents/` definitions are tracked; `.worktreeinclude` lists ignored controller/skill/extension/workflow state | Git inventory and `.worktreeinclude` |
| Bundle 0.14.0 | Catalog status snapshot; controller 0.6.0, roadmap 0.2.1, wiki 2.0.1, feedback 0.2.1 | `catalog/release.json`, `bundles/spec-kit-flow/bundle.yml` |

Direct selected executable reported `specify 1.0.10.dev0+pegagio.2`. A separate `mise exec` check failed creating a trusted-config symlink because this delegated sandbox cannot write that state directory; it does not establish the CLI is missing. No environment change was made. Skill-tools Python 3.11.16 and PyYAML 6.0.3 are available. Native desktop version/effective role settings were not independently established by this planning command.

## Decisions and Alternatives

Each decision separates deterministic validation from judgment and authority.

### D1: Dedicated feature-reference normalization

**Decision**: Add a small source controller module for typed stable-ID/title/menu resolution. Keep general gate behavior unchanged for non-feature gates. Main controller canonicalizes an unambiguous natural answer before deterministic resolution; competing interpretations return ambiguity.

**Rationale**: The existing generic numeric gate parser is appropriate for an ordinary menu but cannot distinguish stable feature IDs from positions. Avoid changing every approval menu's meaning.

**Alternatives considered**: Prompt-only parsing hides testable ambiguity rules; global parser changes couple unrelated gates; accepting `trusted: true` from input files falsely manufactures authorization. Typed resolution plus direct-user context is the smallest bounded change.

### D2: Activation preserves lifecycle

**Decision**: Selection changes active identity only. Planned without authored spec stays planned; existing consistent state and bytes remain. Status advancement remains separate documented authoring/implementation authority. Empty roadmap delta skips roadmap write. Fresh fingerprint/ownership/dependency/pointer validation precedes activation.

**Rationale**: Existing pointer helper already supplies atomic/no-op/preservation behavior. No new lifecycle state is needed. A pending documented transition is not automatically a contradiction.

**Alternatives considered**: Marking every activation in-progress conflates selection with work; creating empty directories/specs gives misleading evidence; inventing active status adds governance/migration cost; treating existing planned+spec as automatically inconsistent forces unnecessary repair.

### D3: Source-owned shared readiness evaluation

**Decision**: Propose core Python readiness evaluation and additive `check_prerequisites.py --readiness --json`. Core Analyze/Implement and FlowKit consume the same versioned report. FlowKit validates current report/evidence and retains its strict outcome envelopes; classification metadata belongs to the mutable selected feature.

**Rationale**: Core owns its generic checklist gate; changing only FlowKit prose cannot remove the current core override. One evaluator avoids divergent definitions and new runtime dependencies. This requires separately authorized core source delivery; unsupported capability blocks clean startup.

**Alternatives considered**: Duplicate parser implementations invite drift; a custom preset is not approved; editing installed templates breaks source authority/provenance; removing future items or checking their boxes is false evidence; a universal override discards preparation protection. A new service/database is unnecessary.

### D4: Preserve author/reviewer/recorder separation

**Decision**: Known quality checks retain existing owners; explicit metadata classifies mixed/legacy future proof and names evidence/due phase. Reviewer evaluates independently and returns read-only outcomes. A declared authorized recorder persists exact review results; markers may change only under authorized owner authority. Unavailable ownership blocks.

**Rationale**: Current Reviewer instructions prohibit artifact edits. Recording a verdict is different from producing it; author self-check is still valuable without replacing independent review. There is no safe automatic inference from an unchecked mixed item.

**Alternatives considered**: Giving Reviewer blanket write authority weakens separation; making the Coder check custom review markers violates ownership; treating every nonrequirements filename as future proof silently bypasses legacy obligations.

### D5: Validate existing delivery before fixing configuration

**Decision**: Use tracked native definitions plus `.worktreeinclude` propagation, with install-missing/refresh ownership unchanged. Only a reproduced supported gap may lead to an explicit consumer configuration proposal.

**Rationale**: Inspected source already has the intended inventory and propagation paths. First-chat availability is a live client test, not a package-missing inference.

**Alternatives considered**: New setup scripts duplicate supported app mechanisms; adding `.codex/` broadly could overwrite consumer configuration; per-chat installs increase risk without proving native interface availability; consumer-copy hashing contradicts Feature 017 ownership rules.

### D6: Separate native matrices and causal claims

**Decision**: Test eight exact native roles in each of three contexts with per-case provenance and actual outcomes. Preserve first-chat failure and later success as distinct cases. Report capacity/interface limits without recovery mutation or generic fallback.

**Rationale**: File existence, model labels and no-op calls are insufficient. Timing may support a hypothesis but cannot establish undocumented Codex loading rules. The capacity observation has no promised remedy here.

**Alternatives considered**: Inferring root cause from a successful fresh chat overclaims; raising capacity/archiving children revives excluded scope; shrinking the required matrix silently changes SC-005.

### D7: Versioned source handoffs

**Decision**: Reconcile governing contract first, then independently owned roadmap/core source; consume their tested revisions through existing pins/catalog. Wiki source has no assumed behavior change; optional ingestion is a separate authorization.

**Rationale**: Separate source owners cannot be bypassed with a local bundle archive patch. A clean plan is not authority for cross-repository implementation or release.

**Alternatives considered**: Vendoring extension commands here creates a second authority; editing packaged ZIPs hides provenance; pretending current versions support new semantics creates false compatibility.

## Proposed Governing Reconciliation

The following wording is a concrete proposal only. Human approval must precede authority-dependent implementation. Constitution 6.0.0 remains operative; proposed incompatible authority changes imply a MAJOR constitutional revision if approved. The operator decides the exact amendment/version through its explicit governance process.

Proposed replacement for the roadmap-patch decision sentence in Principle II, preserving its surrounding assignment/separate-invocation rules:

> A direct trusted operator instruction that unambiguously authorizes a bounded roadmap modification or activation is the explicit human decision for that operation. Routine wording, numbering and linkage derived wholly within that instruction do not require a second approval solely for their exact patch bytes. The controller must make the resulting changes and their authorization inspectable and revalidate the current target, dependencies and governing state before effect. An inferred or unrequested roadmap change, constitutional amendment, authority change, material scope change, substantive product decision or ambiguous recovery must pass a focused explicit human decision gate before mutation. Selection changes active identity only and does not establish authoring, implementation, verification or acceptance. Separately requested phases may retain settled same-target intent after revalidation; completion does not invoke another workflow.

Affected contracts: `.specify/memory/constitution.md` Principle II/governance; `AGENTS.md`; source controller protocol and selected workflow routing; independently owned roadmap Write's interactive/noninteractive authority rules; active installation/adoption/manual guidance. Current wiki exact-patch/selection pages are historical synthesis, not amendment authority. After approved source changes, ingest the prospective contract with citations/supersession rather than semantically rewriting merged features.

Migration: retain installed exact gates until approved compatible source is installed. Preserve active recovery and pending questions. A separately requested resume revalidates target/authority and uses the new rule without pretending old gates passed. Direct user intent is not retroactive approval of a distinct material scope or governing amendment.

## Owner Handoffs and Open Evidence

Technical approach is resolved. These substantive delivery/evidence gates remain prospective and must be recorded honestly:

| Gate | Owner and exact requirement | Safe action while pending |
|---|---|---|
| Governing authority | Operator explicitly approves current proposed reconciliation | Continue planning/review; preserve operative authority; no changed-authority effect |
| Roadmap direct-amendment semantics | Independent roadmap source receives authorized change/test/version delivery | Prepare contract handoff; current command keeps gates; no local extension-copy edit |
| Readiness capability | Spec Kit owner authorizes/evidences shared evaluator/core templates and compatible CLI | Prepare shared fixture handoff; unsupported core report blocks readiness claim |
| Native first/future chats | Operator supplies actual prepared Codex contexts and exact launches | Retain not-tested gaps; do not claim startup guarantee or install per chat |
| Propagation alteration | Only if specific supported gap reproduced, operator approves exact project config patch | Record current inventory and preserve consumer files |

No new product ambiguity, model pair or dependency decision is introduced. First-chat causation, effective settings and capacity cause remain unknown external evidence rather than blockers to documenting this bounded design. Implementation/acceptance claims require the corresponding gates and tests.


## Operator-Approved Readiness Revision — 2026-10-06

This decision supersedes D3's core-evaluator implementation proposal and the core-delivery gate in the original research; the original observations and proposals above remain historical evidence. The operator selected a FlowKit-only approach, a dedicated `FlowKit-Readiness Checker` using Luna/Medium, and an Analyze correction/reassessment loop for its findings. It requires no Spec Kit core changes. Existing core Implement's unchecked-item gate remains operative.

FlowKit will assess all actual preparation obligations, obtain missing independent review from its proper owner, and record only authorized evidence-backed marker changes. Reviewed future obligations may move outside `checklists/` without losing identity, pending status or provenance. The new Checker is read-only; deterministic helpers handle mechanics and it consumes existing review verdicts rather than inventing them. Every safe in-scope readiness gap feeds the declared smallest-owner correction route and fresh artifact/readiness reassessment. Unknown ownership, unsafe changes, unavailable exact roles, consequential decisions, no progress and the existing cap stop explicitly. FlowKit Implement revalidates current preparation before core startup; no saved ready flag or prompt overrides the core gate.

Roadmap extension verification is deferred by the operator. Its current command already supports explicitly authorized deltas, so targeted compatibility validation must precede any claim that an extension rewrite is required. This deferral and design amendment do not establish verification, native availability, source delivery or feature acceptance.

## Lifecycle Amendment Research

These 2026-10-07 decisions add prospective lifecycle design while preserving D1–D7 and dated readiness decisions. The authoritative requested behavior is spec FR-026–FR-038; source inspection supplies compatibility facts, not approval. Current source and installed three-phase graphs have matching hashes. Roadmap extension 0.2.1 is independently owned at `https://github.com/pegagio/spec-kit-flow-roadmap`; installed `review_contract.py`, Write/Brief/Debrief skills and manifest provide the observed interface. No external research, dependency addition or implementation was needed to resolve these local integration questions.

### D8: Milestones belong to explicit phase nodes

**Decision**: Specify records specced after current independent authoring review and brief; Implement records in-progress after readiness/eligibility before Coder; Close Out records implemented after full current completion review before debrief. Roadmap Agent owns each extension Write, separate Reviewer/Code Reviewer supplies substantiation.

**Rationale**: All three current graphs omit the writes; Close Out reaches debrief with stale planned state. A final-report status assertion cannot make a missing effect inspectable or enforce coding/debrief order.

**Alternatives considered**: Selection-based advancement conflates identity with work; inferring implemented from checkboxes/Complete loses evidence; implicit after-command hooks lack declared gates and recovery. Explicit reviewed nodes fit current controller routing and manual fallback without a new framework.

### D9: Separate authoring readiness from Complete

**Decision**: Add owner-reviewed `specification_ready` evidence mode to brief/lifecycle evaluation, retaining legacy `--spec-complete` semantics for old callers. Draft can be authoring-ready when author quality, required clarification, independent review and linkage/brief are satisfied; Close Out keeps Complete as its own final header action.

**Rationale**: Current brief evaluates planned→specced only with its spec-complete boolean, but Close Out alone completes the header after implementation. Feeding that header back into Specify would create a circular completion prerequisite. New mode consumes current review references and required-check coverage, not an unsupported boolean declaration.

**Alternatives considered**: Mark Complete during Specify changes existing completion meaning and recreates label-only proof; passing spec-complete=true for Draft silently changes existing API semantics; editing core changes an unnecessary owner. Additive extension contract avoids each problem.

### D10: Adjacent recovery with present effect dates

**Decision**: Each phase declares a finite recovery ceiling; Close Out may recover up to three ordered missing milestones without invoking other workflows or repeating substantiated code. Each missing milestone has distinct current proof, original owning phase and actual executing workflow recorded. Start recovery can consume earlier attributable implementation activity plus current review of prerequisite compatibility; ordinary startup still needs eligible current work.

**Rationale**: Feature 020 remains planned; single planned→implemented repair violates extension preservation and invents skipped history. Old full-scope convergence is now stale for the lifecycle amendment, so its 49 completed tasks cannot authorize new completion.

**Alternatives considered**: Re-run every phase/coding duplicates adequately evidenced work; skip directly using latest label has no missing-edge proof; auto-rollback after later failure discards true effects. Adjacent recovery is bounded and resumable but requires more explicit evidence and owner compatibility tests.

### D11: Guarded owner write with independent trust

**Decision**: FlowKit prepares/validates snapshots and routes; the extension’s versioned Write mode alone mutates roadmap bytes using its path/config validators, cooperative lock, exact preimage comparison, atomic replacement and truthful receipt handling. Main controller establishes trusted operator invocation and exact native assignments; JSON role/authorization fields never grant trust.

**Rationale**: Current Write accepts direct bounded authorized deltas but lacks structured evidence/current-state binding. New effect contracts need entry/pointer/governance/dependency/source maps, per-edge idempotence and separate later-failure status.

**Alternatives considered**: Direct FlowKit writes split owner policy; trusting serialized approval lets reports grant authority; a database transaction adds needless infrastructure and cannot cover arbitrary user edits. Supported writers cooperate under one lock; unsynchronized external file edits remain an explicitly tested detection limitation.

### D12: Approve and deliver the runtime policy without invented governance gates

**Decision**: Current constitution 7.0.0 supports planning and direct bounded amendments. No amendment is required for this design action. Explicit approval/reconciliation of the new runtime milestone and stale-recovery contract, owner source/command delivery, roadmap outcome/scope alignment and downstream task/readiness updates must precede reliance. If owner review finds additional authority conflict, report the exact necessary amendment rather than guessing a constitutional patch now.

**Rationale**: The specification explicitly makes routine milestone invocation authority prospective. The latest brief identifies a durable scope mismatch while acknowledging settled trusted intent. Design can resolve technical work without either bypassing current rules or blocking planning on future delivery.

**Alternatives considered**: Treating Plan invocation as current lifecycle authorization expands scope; refusing planning until code/policy exists is circular; blanket amendment/approval adds unnecessary gates. Preserve existing governance until specific reviewed delivery is authorized.

### D13: Additive versioned delivery and separate evidence

**Decision**: Coordinate owner extension, changed three workflows, controller and bundle versions/pins; preserve unchanged roles/components, core source and original validation history. Development snapshot supports new validation before production release. New cases require their own source/provenance/results; source settings and mock traces do not prove live effective settings.

**Rationale**: Current checked-in catalog release metadata describes older snapshot components while current unreleased source/installation are newer. Testing the old archive or manually editing installedcopies would miss the correction.

**Alternatives considered**: Production tags before closeout recreate the previously removed release loop; versionless changes make compatibility opaque; a new native role/model is unnecessary. Use existing supported development snapshot and retain post-closeout production release.

### Resolved unknowns and remaining delivery evidence

The authoring/Complete ambiguity, missing implemented evaluator, extension write ownership, recovery mode/limits, stale-evidence handling and packaging path are resolved in this design. Remaining gaps are prospective delivery/review/validation, not unresolved product choices: owner source 0.3.0-compatible behavior, exact delivered versions/hashes, explicit runtime-contract approval, durable roadmap alignment, Tasker updates, fresh readiness/convergence and lifecycle cases. None is marked complete by this research pass.

## Requested Scope Research

This 2026-10-07 addition resolves Story 7 design from current source inspection and the operator's approved amendment. Current pre-Tasker evidence is 51/67 completed with 16 open lifecycle tasks; [lifecycle-governance.json](validation/lifecycle-governance.json) records T050 scope alignment and T051 exact-policy approval. The approved phase-lifecycle contract is unchanged; its older approval/delivery prose is historical. Owner capability and Story 7 implementation remain prospective. No new authority question or constitutional amendment is identified for planning.

### D14: Request identity survives eligibility changes

**Decision**: Main controller records all requested existing unfinished task identities before assessment, including blocked dependencies, or exactly the trusted explicit subset. Reviewer assesses eligibility separately; deterministic checks enforce identity, safe paths, membership and current digests. The original request never shrinks with completed/eligible projection; no restricted request automatically expands to its prerequisites.

**Rationale**: Current `capture_implementation_baseline` accepts any existing unique selected IDs without testing eligibility. Its generated `selected_task_ids` source in the workflow, rather than the helper's allowance, caused the observed orchestration error. Explicit request establishment makes that distinction enforceable and reviewable.

**Alternatives considered**: Re-asking the operator for an already-requested task recreates the inefficiency; a generated eligibility list as authorization loses blocked scope; rewriting a stopped baseline after completion falsifies before evidence. Preserve stopped historical runs and implement the future routing correction instead.

### D15: First execution and correction progress have separate prerequisites

**Decision**: Use discriminated independent per-task administrative versus substantive fulfillment proof. A real same-child answer or fulfilled administrative prerequisite triggers fresh eligibility/readiness assessment and discharges only that task's requested accounting at zero code credit. Deliver a new `implementation-route` adapter and reviewed Implement-only loop mode: while the independently retained source-attempt history is empty, ordinary strict route membership permits bounded preparation or first source execution under all common guards. Persist session/attempt-start events before dispatch. After any source attempt, including failed/no-effect/question-stopped dispatch, call the unchanged generic prior-remaining/resolved predicate against the actual pre-attempt substantive assessment with no first-pass exemption. Retain one monotonic global five-session budget across preparation/coding; same-child question resumption reuses its session. Exact graph/API/counter ordering and abuse checks are defined in [the scope contract](contracts/implementation-scope.md#declared-routing-and-budget-integration).

**Rationale**: A decision can unlock coding without proving a code change. Current generic `controller.py:504` does not distinguish administrative preparation from source correction and would reject the legitimate administrative-to-first-source path. A narrow explicit adapter/graph mode supplies the missing boundary; the generic source predicate remains operative after a source attempt, and independent task proof reconciles administrative task completion with zero implementation credit. This uses existing recovery/dispatch structures, not a general scheduling engine.

**Alternatives considered**: Counting every marker/report as progress bypasses the guard; requiring a resolved defect before any source execution is circular; renewing the budget on each dependency defeats bounded correction. A vague first-pass exemption or changing the generic predicate for every workflow creates an abuse path. A separate preparation budget allows more than five actual Coder sessions. Choose an explicit mode validated against actual graph/history and one common budget; its cost is a small supported adapter/schema change covered by T069/T070 and graph integration T071.

### D16: Immutable comparison history plus fresh activation evidence

**Decision**: Add versioned requested-scope and per-task eligibility/activation records in existing run storage. Preserve original known-defect source digests and every predecessor baseline. Later activated tasks get task-specific preimages immediately before their own execution. Bind completion proofs to individual requirements/source deltas and native independent reviewer provenance. New findings enter a new successor and earn no credit for the discovery pass.

**Rationale**: Current successor baseline drops completed tasks and has only finding-specific source evidence; it cannot itself represent full authorization or evidence for a never-executed later task. Additive scope validation and task-specific proof binding are actual helper/API changes beyond the simple full-ID capture clarification.

**Alternatives considered**: Undifferentiated recapture can delete defects or invent before proof; a second authoritative task ledger causes drift; replacing version 1.0 silently harms consumers. Add a small module/contract and pinned new graph while preserving old-caller semantics.

### D17: External source work and installed consumption differ

**Decision**: Validate actual external checkout/access/guidance/permitted source-work route/task authority before dispatch. Missing runtime capability alone cannot block source work tasked to deliver it; downstream effects still need compatible installed owner support. An unavailable source or unsettled owner rule yields its actual blocker/resumption, without assuming access or overriding permissions.

**Rationale**: T052 is authorized owner-source delivery, not a call to an already-installed capability. Packaging ownership is separate from native delegation; exact existing Coder/Reviewer roles and owner rules remain binding.

**Alternatives considered**: Excluding all external tasks mistakes ownership for scope; treating task authority as universal write permission overreaches; editing installed payloads splits behavior ownership.

### D18: Separate attributable validation and delivery

**Decision**: SI001–SI015 cover all Story 7 scenarios using existing unittest/production renderer/disposable development snapshot, plus exact live/manual boundaries when separately authorized. Integrate existing lifecycle delivery/pins without a new package or production-release prerequisite. Current old convergence and 51/67 state remain historical only.

**Rationale**: Source tests, trusted invocation, native dispatch and actual consumer behavior are distinct claims. The [scope contract](contracts/implementation-scope.md) and [quickstart](quickstart.md#requested-scope-validation) specify exact outcomes, coverage and gaps.

**Alternatives considered**: Reusing LC cases without scope assertions leaves new requirements unproved; string-only checks miss routing; silent zero discovery/owner absence fabricates coverage. Require actual nonzero run counts and preserve not-tested gaps.

No technical unknown or product choice remains for this planning reconciliation. Actual external source availability, permitted access, future source changes, version allocation, new snapshot delivery, independent review/readiness and case execution remain unperformed evidence obligations.

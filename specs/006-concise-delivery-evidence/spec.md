# Feature Specification: Retain concise delivery evidence and keep run output disposable

**Feature Branch**: `006-concise-delivery-evidence`

**Created**: 2026-10-19

**Status**: Specification approved; delivered candidate accepted on 2026-10-19. See delivery.md for the actual decision and disclosed limits.

**Input**: Direct operator request to activate Feature 006 and prepare its specification. Keep reproducible test code, fixtures and expected outputs in Git; normally keep raw run logs, transcripts, workflow state and intermediate reports disposable. Retain a concise feature-level verification summary with relevant source revision, checks/results, material limitations and actual human approval decisions. Avoid repository bloat, private identity capture and new evidence infrastructure.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review verification after temporary output disappears (Priority: P1)

Pegagio reviews a delivered feature using a concise durable summary, without opening a session transcript or depending on temporary files.

**Why this priority**: Verification must remain meaningful even when execution output is discarded.

**Independent Test**: Complete one small delivery fixture, remove its disposable output, and have a separate evaluator establish tested source, checks/results, repairs, remaining limits and actual decision status using committed feature artifacts alone.

**Acceptance Scenarios**:

1. **Given** a feature with performed checks, a repaired failure and a pending human result review, **When** delivery is prepared, **Then** its durable summary identifies the source revision or base revision plus relevant working changes, checks and outcomes, repair and recheck, limitations and pending review; it does not report human acceptance.
2. **Given** temporary raw output has disappeared, **When** a reviewer follows required evidence references, **Then** each reference resolves to retained evidence sufficient to understand the claimed result; optional temporary diagnostic locations are explicitly disposable and never the sole support for a required claim.
3. **Given** a material edit after a check or review, **When** delivery resumes, **Then** the summary identifies affected stale results and the necessary recheck or affected human review before relying on them.

### User Story 2 - Keep rerunnable assets without committing run debris (Priority: P1)

An executor retains the small reusable inputs and expected results needed to repeat verification while leaving run-specific noise outside the scoped commit.

**Why this priority**: Reproducibility requires test assets, not an archive of every execution.

**Independent Test**: Inspect the delivery candidate and repeat its fixture checks using retained test code, fixtures, expected outputs and instructions after discarding execution output.

**Acceptance Scenarios**:

1. **Given** test code, deterministic fixtures and expected outputs alongside raw stdout, a transcript, workflow state and an intermediate report, **When** the final scope is inspected, **Then** reusable assets and the concise summary are included, while temporary execution material is excluded or ignored and unstaged.
2. **Given** a failed check, **When** the executor summarizes it, **Then** the failure and its impact survive concisely; unsuccessful or unperformed checks are never converted to passes merely because raw output is excluded.
3. **Given** local paths or personal identities in raw output, **When** durable artifacts are authored, **Then** they use Pegagio/pegagio and portable paths such as `~/Development/github/pegagio/farmboy`, without copying private names, local usernames or session content.

### User Story 3 - Consolidate evidence without losing meaning or authority (Priority: P2)

A maintainer replaces redundant current-scope reports with a concise account and repairs references, while preserving historical meaning and review boundaries.

**Why this priority**: Consolidation should make review easier without weakening evidence or silently rewriting history.

**Independent Test**: Consolidate obsolete reports in an authorized mutable fixture, then verify every affected reference, distinct finding and decision against the retained summary.

**Acceptance Scenarios**:

1. **Given** overlapping mutable reports in the authorized scope, **When** they are consolidated, **Then** the summary retains distinct material findings, repairs, unresolved limits and actual decisions, and all affected required references resolve.
2. **Given** a project-specific evidence rule requiring a particular durable item, **When** preparing delivery, **Then** that rule is honored; a genuine conflict is surfaced before dependent closeout rather than silently discarded.
3. **Given** an externally selected delivery, **When** returning evidence, **Then** existing caller-owned coordination and handoff semantics are preserved, with required references pointing to retained evidence; no new queue, approval register or evidence service appears.

### Edge Cases

- A check runs against uncommitted changes: a base revision alone cannot claim those changes were tested; record the relevant working delta and invalidate affected checks after further material edits.
- A final commit does not yet exist: do not fabricate its hash or create a later receipt-only commit merely to include its own hash. Report the actual resulting checkpoint in the ordinary handoff.
- Temporary output is lost before a trustworthy result is established: record the evidence gap and repeat the affected verification when required; absence is never a pass.
- A fixture contains a test-only approval: label it as such; it cannot approve the real feature. Silence and passing checks are not approval.
- A report is already tracked: ignoring it does not remove it from the candidate. Inspect the actual staged scope and preserve unrelated work.
- An old report belongs to merged history or another feature/project: this feature grants no broad deletion or semantic rewrite authority. Preserve it unless a separately authorized change can respect the constitutional history boundary.
- An expected output is large or contains unstable personal details: retain only the reusable, portable expectation needed for the check; do not reclassify an entire transcript as a fixture to justify committing it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The delivery skill and operator guide MUST distinguish durable feature evidence, reusable verification assets and disposable execution material before the scoped local commit. Their existing “ALL scoped delivery artifacts” wording MUST mean authorized durable deliverables, not every file produced during a run.
- **FR-002**: Delivery MUST retain a concise feature-level account of relevant tested source revision/working state, checks actually performed, results, material failures and repairs with rechecks, unresolved limitations, and actual human decisions or pending decisions relevant to the candidate. Existing feature documentation MAY hold this account; no additional evidence store is required.
- **FR-003**: Each verification claim MUST remain attributable to the source and execution actually observed. Checklists, expectations, simulations and static checks MUST be distinguished from observed real-session behavior. No future commit, unrun check or unobserved native completion may be reported as verified.
- **FR-004**: Reproducible test code, reusable fixtures, expected outputs and the instructions needed to repeat their checks MUST remain durable Git assets within authorized scope. Disposable run output MUST NOT be their only definition or sole evidence for a required outcome.
- **FR-005**: Raw stdout, run logs, full session transcripts, workflow/runtime state and superseded intermediate reports MUST normally remain in temporary disposable storage or ignored local locations, excluded from the final scoped commit. Durable exceptions MUST be justified by an applicable project evidence requirement or a concrete essential verification need, kept minimal and free of private identities; convenience alone is insufficient.
- **FR-006**: Required delivery and returned handoff evidence references MUST resolve to retained artifacts sufficient to support their claims after temporary output disappears. Optional diagnostic references MUST be labeled disposable and nonessential.
- **FR-007**: Consolidation MUST preserve distinct material results, limitations, truthful source attribution and actual decisions; repair affected references; and respect selected scope, unrelated work and merge-bounded history. It MUST NOT invent approval or rewrite a merged feature's meaning.
- **FR-008**: Durable artifacts MUST use Pegagio/pegagio and portable home-relative or repository-relative paths. They MUST omit private personal names, local usernames, incidental session identifiers and copied transcript content that is unnecessary to establish the result. Decision attribution MUST preserve who acted in the relevant role and what was decided without private identity capture.
- **FR-009**: Existing project-specific evidence requirements MUST be consumed before discarding or consolidating evidence. An unresolved material conflict or missing required proof MUST stop dependent closeout with the precise gap and remaining action.
- **FR-010**: The change MUST preserve Feature 003's verification/convergence, actual local commit and Awaiting result review endpoint; explicit specification/full-plan/result approvals; affected review after material changes; and Feature 004/005 external handoff/optional-adapter boundaries. Summarization MUST NOT weaken independent real-session acceptance or imply acceptance, integration or push.
- **FR-011**: Acceptance of this workflow change MUST include a separate evaluator observing the actual installed skill in a real Codex session using one small delivery fixture. The observation MUST demonstrate retained reusable assets and concise required evidence, excluded temporary output, truthful decision attribution and review stopping behavior. Simulations alone MUST NOT establish acceptance; test-only approvals remain fixture-local.
- **FR-012**: The solution MUST use the existing workflow/artifact mechanisms. A new evidence database, registry, accounting system, generic framework, automatic cleanup/retention service, broad history rewrite, upstream runtime change or cross-project implementation is outside scope.

### Key Entities

- **Durable feature summary**: The concise retained account of source, checks/results, repairs, limitations and applicable decisions that supports the feature's delivery review.
- **Reusable verification asset**: Test code, controlled fixture, expected output or repeat instructions needed for rerunnable verification.
- **Disposable execution output**: Run-specific diagnostic or intermediate material whose disappearance does not invalidate required retained evidence.
- **Human decision**: An actual applicable instruction/approval and its content or checkpoint, conditions and limits, distinct from pending review and test-only decisions; this is existing documentation, not a new register.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After disposable output is removed from the small delivery fixture, a separate reviewer can identify all six review essentials from retained artifacts: tested source, performed checks, outcomes, repairs/rechecks, material limits and actual decision status.
- **SC-002**: All required evidence references in that candidate remain resolvable without temporary storage; there are zero required references supported solely by discarded output.
- **SC-003**: The fixture's final candidate contains its reusable tests, fixtures, expected outputs and concise feature summary, with zero raw transcripts, run logs or runtime state accidentally included. Its prescribed checks can be repeated from retained assets.
- **SC-004**: Every claim sampled in the fixture agrees with the actual observed result and decision; zero fixture approvals are attributed to real feature acceptance, and pending or failed checks remain visible.
- **SC-005**: The observed workflow stops for human result review with its existing authority boundaries intact, and no private names or local usernames appear in the new durable artifacts.

## Assumptions

- Dependency 003 is verified in the configured roadmap. This feature materially amends its current delivery skill/guide behavior rather than changing historical Feature 003 meaning. Features 004/005 define boundaries to preserve, not new work to activate.
- Default evidence policy is concise durable summaries plus reusable assets and disposable raw output. Applicable project-specific requirements can justify minimal durable exceptions; conflicts require a stop rather than an invented retention policy.
- No arbitrary size quota, retention timer, extra database or standalone cleanup automation is needed. “Concise” means retaining the review essentials once, without repeated logs or duplicate report narratives.
- Consolidation is limited to authorized mutable current-scope artifacts and references. Broad cleanup of Farmboy historical evidence or other projects is excluded; planning must identify any concrete eligible consolidation before proposing edits.
- No material product question remains under the supplied intent and these bounded defaults. Human specification review may request a revision or ordinary clarification.

## Historical context and preparation handoff

- Selected workflow: installed `farmboy-prepare-specification`, standalone named-feature activation and saved draft handoff. Core specify's template/quality criteria were reused; the full interactive command was not invoked.
- Baseline: clean `develop` at `e1183047592c9f8cfc8d434c48e0e428fb4779ad`. Draft, checklist and roadmap activation are uncommitted changes on this base; there is no Feature 006 delivery checkpoint or approval.
- Sources: [constitution](../../.specify/memory/constitution.md), [roadmap entry 006](../../.specify/memory/roadmap.md), [direction](../../docs/direction.md), [current delivery skill](../../.agents/skills/farmboy-deliver-approved-plan/SKILL.md), [operator guide](../../docs/deliver-approved-plan.md), and the direct operator request. Existing ALL-scoped-artifacts wording motivates FR-001; this draft does not change executable delivery behavior.
- Wiki query: “Which delivery evidence, historical persistence and approval boundaries must 006 preserve?” [Delivery direction and evidence](../../wiki/pages/delivery-direction.md) (S002/S006), [Approved local delivery](../../wiki/pages/local-delivery.md) (S009/S010), [Feature artifacts and merge history](../../wiki/pages/feature-history.md) (S001/S002), and [Prescribed workflow authority](../../wiki/pages/workflow-authority.md) (S001/S002) support retained verification, commit/review boundaries, mutable premerge artifacts and independent actual-skill observation. IDs were checked against the source registry. **Partial**: wiki does not describe the new 006 storage distinction or exact consolidation candidates; the direct request/roadmap supply intent, and later authorized implementation can ingest its actual delivery source through ordinary wiki maintenance.
- Quality: [requirements checklist](checklists/requirements.md) passes draft-authoring criteria; this assesses specification completeness, not implementation success or human approval. Roadmap fit is assessed separately through installed roadmap-brief.
- Native Goals: no supported activation/completion/readback control is exposed in this execution environment. No Goal was created and no native completion is claimed. Saved draft preparation can end ordinarily; native Goal compatibility remains unverified here.
- **Historical preparation handoff: Awaiting spec review.** No material clarification question remains. Pegagio must explicitly approve this specification before any separately selected planning workflow. Do not approve, plan, task, implement, commit or push from this preparation invocation.

Current authority and performed delivery results are recorded in [delivery.md](delivery.md). Pegagio subsequently approved this specification and full plan and selected execution; the preparation notes above retain their earlier checkpoint meaning. This metadata reconciliation changes no approved requirement.

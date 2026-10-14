---
title: Closeout and verification boundary
type: decision
sources: [S013, S021, S029, S018]
updated: '2026-10-14'
---

# Closeout and verification boundary

## Earlier feature contracts

The following cited contracts preserve earlier feature intent; Feature 014's prospective refinements are distinguished below. (S021)

Closeout starts from an operator-identified converged feature, but convergence does not itself complete the feature. A separately approved feature-completion operation must be available; if it is missing, closeout stops before roadmap or wiki changes and does not substitute specification drafting. (S013)

After that operation, roadmap debrief precedes a proposed verification patch. The operator reviews the debrief and exact patch before roadmap write applies only the approved change; return, deferral, or an invalid choice stops the write. (S013)

After an approved roadmap patch, the operator selects durable sources for wiki ingestion and runs wiki lint before commit-readiness review. Unresolved lint findings or blockers stop or return to the affected workflow. A ready-for-explicit-commit disposition does not commit, integrate Git, or accept project work. (S013)

## Feature 014 completion and maintenance

Close Out assesses selected-feature convergence and completion evidence. A clearly converged existing Draft specification may be changed in place to Complete and debriefed without a redundant operation-availability or status-edit gate; ambiguous evidence or authority blocks. Routine debrief corrections flow through affected artifact layers and fresh reassessment until an exact patch is supported or a bounded stop occurs. (S021)

The exact roadmap verification patch still needs explicit approval. Newly approved and currently trusted already verified entries both receive curated single-source ingestion, lint, and coverage checks before automatic commit-readiness reporting. Initial curation includes feature-relevant registered local supporting sources within operator-issued project scope without another confirmation; unavailable or unauthorized sources and scope expansion remain blockers. (S021)

The wiki loop permits five single-source ingestion, lint, and assessment passes. Baseline findings identify independently verifiable missing contracts or stale claims before correction. Source coverage groups findings; each fully corrected prior claim earns substantive progress even when other claims remain. Assessments retain remaining and newly found claims rather than requiring whole-source completion for progress. Conflicts, required authority decisions, unsupported repairs, stale evidence, no progress, and cap exhaustion block. (S021)

Close Out may clear date-only warnings by revalidating claims and citations against current authorized sources, recording source and page before/after digests, and setting freshness metadata to the actual validation date. This requires no separate freshness exception and earns no substantive progress credit; unverified date-only warnings remain blockers. The separately invoked Wiki Lint Update retains its FR-025 policy: age-only timestamp changes remain reported for resolution. (S021)

One final report preserves completed evidence, questions, original gate choices, and partial changes. Readiness does not commit, integrate Git, or accept the feature. (S021)

**Accepted supersession**: S013 requires a separately approved completion operation and a human commit-readiness decision; S021 authorizes evidence-backed in-place completion and automated readiness reporting while retaining exact roadmap approval and separate Git/acceptance authority. S013 remains historical feature evidence. (S013, S021)

[Feature 020 contract](./feature020-closeout-and-verification-boundary.md). (S029)

## Feature 023 qualified verification

The roadmap records Feature 023 as verified for its full reviewed buildable scope, with deterministic validation bounded separately from live-agent behavior, release and acceptance. [Feature 023 qualified verification](./feature023-verification-qualification.md) retains the counts, tested coordinates and pending evidence. (S018)

## Related pages

- [Workflow lifecycle](./workflow-lifecycle.md)
- [Controller assessment contract](./controller-assessment-contract.md)

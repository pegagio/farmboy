---
title: Prescribed workflow authority
type: decision
sources: [S001, S002, S003]
updated: 2026-10-16
---

# Prescribed workflow authority

The operator selects the workflow and current feature. Its prescribed steps, commands, branches, transitions and repair loops are authorized only within that scope and subject to stated conditions and human checkpoints. An implementation-only invocation does not authorize convergence; a selected composite explicitly prescribing that transition can authorize it. Missing prescriptions do not create authority. (S001)

Routine authorized work proceeds without repeated approval. Explicit checkpoints, required input, unresolved decisions, out-of-scope changes and blockers without an authorized resolution pause affected work. Agents cannot invent answers or bypass platform constraints, and report actual outcomes and remaining work plainly. Amendments require Pegagio’s explicit approval. (S001)

[Feature artifacts and merge history](./feature-history.md) explains reconciliation and the historical boundary; neither flow-back nor command success grants additional workflow authority. (S001)

The [delivery direction](./delivery-direction.md) describes the intended lifecycle and its human reviews; executable transitions remain subject to the selected workflow. (S002)

[Project context pointers](./project-context.md) identifies the task-driven direction, roadmap and wiki references without expanding repository access. (S003)

Prefer the simplest existing-capability composition meeting the selected workflow. Extra infrastructure needs a concrete current requirement or observed failure; speculative needs are insufficient. Specifications, plans and review summaries define necessary terms and use concrete examples where useful while retaining precision and context. (S001)

Acceptance of a delivered workflow or material behavior change requires observing the actual skill in a real Codex session, including affected interactions and stops. The executing session must be separate from the evaluating agent or process. Prefer automated observation/test driving; manual verification is acceptable. Simulations alone are insufficient. Keep verification proportionate to the change. (S001)

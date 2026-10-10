# FarmBoy Rename Checkpoint

Checkpoint requested by the operator on 2026-10-10. Feature 021 implementation is paused; its partial changes are preserved for later resumption after a separately developed roadmap-boundary correction.

## Recorded State

The pre-rename source baseline is commit `b6dcae9de22147f867717e322c7bb2cb8a240715`, which merges completed Feature 020 from develop. Constitution 8.0.0 approves the FarmBoy identity cutover. Feature 021 remains the selected work in this checkout, and the rename has not been accepted, independently code-reviewed, published or integrated into develop.

T001–T009 are marked complete by the implementation child; T010–T012 remain unchecked. Source changes include workflow/controller/agent/renderer/bundle/feedback names, the owned delegation metadata key, packaging, current documentation and regression expectations. Installed consumer components remain under their prior identities and were not refreshed by this work.

## Validation and Blockers

The implementation child reported passing focused controller, agent, catalog, ownership, implementation-scope/progress/readiness, workflow graph/path, snapshot and feedback checks. The structural validator reported zero unexplained terminal paths. A disposable consumer using Specify CLI `1.0.10.dev0+pegagio.2` installed the FarmBoy 0.18.0 development snapshot with all ten active workflows, round-tripped Plan metadata, rejected old bundle/workflow IDs and installed maintainer intake separately. These results do not establish live-agent behavior or release compatibility.

Two validation failures remain:

- **Phase lifecycle**: 30 tests reported two errors because the independent roadmap lifecycle contract expects FlowKit role names, paths, package IDs and metadata while this source emits FarmBoy identities.
- **Bundle lifecycle**: Four tests reported one failure with `Cannot dispatch prompt: integration None CLI not found or not installed.` This separate failure requires investigation without assuming the rename caused it.

The roadmap snapshot used `flow-roadmap` 0.3.0 source at commit `86b0cc70054b7eca4d715fbccd6448165a85fc1f` with existing uncommitted changes and no matching release tag. Wiki 2.0.1 source was clean at `0292ff66758e36849cee4e0f6bcbdac51629e1d0`. No external source was modified by this implementation. The Python environment repair was explicitly approved; Python 3.11.16 and PyYAML 6.0.3 passed the project checks.

## Agreed Next Step

Preserve this rename checkpoint and develop the roadmap-boundary correction separately from the pre-rename baseline, retaining existing FlowKit identities there. The approved boundary places milestone decisions, evidence checks and independent readback in the workbench workflows; the roadmap extension performs generic, explicitly authorized ledger edits. Each repository records its own changes. The extension ID and generic commands remain unchanged.

Before resuming the rename, integrate the separately reviewed correction under explicit Git authorization, reconcile Feature 021's affected artifacts and obtain fresh implementation assessment. Preserve current task IDs and completed work; do not infer completion from task markers or this checkpoint. No commits beyond this requested checkpoint, push, publication or feature acceptance are authorized by this note.

# Farmboy archive and recovery

## What was preserved

The clean reboot was approved on 16 October 2026. Before the active checkout changed, all thirteen registered Farmboy worktrees and Git administration were copied into a restricted local preservation directory. File bytes, symlink targets, modes, mtimes, original indexes and separate staged/unstaged binary patches were verified against their sources. Original linked worktrees were retained in place.

Dated local archive branches preserve every original worktree HEAD and screened source snapshot. `-head` suffix branches identify the exact original HEAD. Where staged changes existed, a separate `-index` branch preserves that staged tree before the working-state snapshot. Snapshot commits are evidence checkpoints, not acceptance or release claims.

| Archive branch | Snapshot commit |
| --- | --- |
| `archive/2026-10-16/primary` | `41edab98e0b9fe935866aa7907b54714c9664f08` |
| `archive/2026-10-16/1ceb` | `637d7c40ed7ecabca9658ce89dec66bbeec6ca3e` |
| `archive/2026-10-16/1ed1` | `04edf278eb20d52cad83a333d409c847503d1e66` |
| `archive/2026-10-16/4a9d` | `7966bedf4814fd41681d77150db46611e0d24027` |
| `archive/2026-10-16/b73a` | `d99ec66c06bf4097ca49a7e028d35215fbdf3e59` |
| `archive/2026-10-16/d2ac` | `7966bedf4814fd41681d77150db46611e0d24027` |
| `archive/2026-10-16/d7bc` | `4d3275cab954706617b7261085d0a7e56d43b38c` |
| `archive/2026-10-16/d9ea` | `ecb1dde3d676ad4e9c0a2d0b71f83fbfcdf3888c` |
| `archive/2026-10-16/e023` | `10704cc937f4e793fbccfc789c365fae1896a960` |
| `archive/2026-10-16/f713` | `7966bedf4814fd41681d77150db46611e0d24027` |
| `archive/2026-10-16/farmboy-environment-test` | `e3a309e4aa6def43f535dbf87982c4fe1eb706ec` |
| `archive/2026-10-16/farmboy-spec-kit-flow` | `f8b81d8026639b29a5f5ef27aa6fe7a68027cdeb` |
| `archive/2026-10-16/roadmap-boundary-correction-spec-kit-flow` | `f8b81d8026639b29a5f5ef27aa6fe7a68027cdeb` |

Feature 024's staged tree is `archive/2026-10-16/1ed1-index` at `36f895f3d8dfeb1ce8cb7f3702fe162efc8ac8b1`. Its working-state snapshot is a child of that staged snapshot. The original feature branch and dirty worktree were not changed or resumed.

The restricted local preservation root is:

`~/Documents/Codex/2026-10-16/task-2/farmboy-preservation-2026-10-16/`

It contains `preservation.json`, `archive-results.json`, `preservation-verified.json`, a verified `farmboy-all-refs.bundle`, an independent pre-migration `git-administration/` copy, and per-worktree `files/`, `manifest.json`, `index.original`, staged/unstaged patches, and NUL-delimited inventories. `primary-retired-local/` holds ignored/local material moved out of the active checkout after the branch switch; its independent verified copies also remain under `worktrees/primary/files/`.

Backups beyond Git are necessary. Ignored run/implementation histories, local notes/feedback, editor state, virtual environments and generated caches were not blindly committed. Eleven unsuitable untracked files in one historical worktree were kept only in the restricted backup: ten local/editor items and one generated binary/archive. The credential-pattern scan found no flagged credentials among the admitted changed source. That scan is conservative screening, not a guarantee about the contents of historical commits.

## Inspect or recover safely

- Inspect a file without changing a checkout: `git show archive/2026-10-16/1ed1:path/to/file`.
- For an independent historical view, use `git worktree add --detach <new-empty-path> archive/2026-10-16/1ed1`. Choose a new destination; do not overwrite an existing worktree.
- To recover exact uncommitted/index distinctions, use the corresponding restricted per-worktree snapshot and original index in a disposable recovery checkout rooted at its recorded original HEAD. Compare recovered staged and unstaged diffs with the saved patches. The original worktree remains the easiest intact reference.
- If repository administration is lost, the verified Git bundle can seed a separate recovery repository. The pre-migration administration copy also retains original refs, reflogs, staged objects and per-worktree metadata. Do not copy that administration over a live repository or overwrite its other worktrees.
- Do not delete backups or archive branches until a separately authorized retention decision. Never put local-only or sensitive backup contents into Git or Library without a new review.

## Active-tree boundary

Old specifications, constitution, roadmap, wiki, workflows, controllers, packages, tests, runtime setup and assigned-agent configuration are historical, not active requirements on the reboot branch. The reboot commit removes them through normal history-preserving tree changes; it does not rewrite their old commits. New requirements need forward-going reviewed artifacts. Restoring a file for inspection does not reactivate its policy.

No workflow was resumed or implemented. `develop`, `master`, remote refs and remote defaults were left unchanged. The primary checkout now uses the separately named reboot branch so its former active machinery is absent without rewriting the integration line.

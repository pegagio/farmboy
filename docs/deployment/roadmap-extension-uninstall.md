# Retired roadmap extension removal

Pegagio explicitly requested uninstalling the roadmap extension after FARM onboarding and, after an approval-review refusal, directly confirmed removal of the identified installed FlowKit Roadmap 0.4.0 extension, ID flow-roadmap. Initial requests were denied before execution and left live bytes unchanged. The supported specify extension remove flow-roadmap --force action subsequently succeeded under the new confirmation; no manual removal or alternate executor bypass was used.

The uninstaller removed the four managed write/brief/debrief/sync commands, extension-owned scripts/templates/config/manifest and the three optional roadmap hooks. Registry and installed-list entries are removed; Flow Wiki 2.0.1 and its two optional hooks remain unchanged. The supported default procedure backed up roadmap-config.yml under .specify/extensions/.backup/flow-roadmap/. A complete pre-removal recovery copy and checksummed preservation baseline are also retained outside the checkout. The preexisting untracked roadmap-write Python cache was restored byte-for-byte from that copy; the remaining cache-only directory has no extension manifest, command or hook and is not an installed extension. Other preexisting deletions, lock and cache files remain unchanged.

## Executed verification

- Installed list contains only Flow Wiki; flow-roadmap is absent from the registry, installed list and hook configuration, and all four managed roadmap command skill files are absent.
- specify integration status --json reports status ok, findings empty and zero missing/modified managed files. Native event refresh completed without a reported failure.
- Generic independent-plan-review source-contract checks passed (three tests); git diff --check passes.
- Before/after SHA-256 comparison confirms every tracked byte outside the 19 uninstall-owned path changes is unchanged. The historical .specify/memory/roadmap.md, every spec/evidence file, Wiki extension/content, generic/Diagram workflow skills, active pointer, constitution, FARM authority guidance and portable declarations are preserved. All unrelated untracked bytes are also preserved.
- Native FARM cutover farm-workflow-tracking-cutover-20261023 remains accepted, pinning authority checkpoint 880521d3cd6335e4d1d2a03777bb8064283699e9. Its authority artifacts still match actual committed/working bytes, and current binding binding/207ba8fb0730299852734a599ebe1040 agrees. Diagram FARM remains the sole operational tracker; this removal changes no native history or authority record.
- Automation remains OFF, with no active Feature run or launched workflow. No push, unrelated cleanup, old-history deletion or global installation change.

Only the 19 uninstaller-owned tracked changes and this operational record are checkpointed with normal hooks and explicit staging. The generated configuration backup and preexisting unrelated dirt remain outside that commit; no arbitrary cleanup or backup-content commit is included.

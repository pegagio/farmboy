# FARM-28 delivery verification

Baseline: approved proposal037476797d625bcee650f076837866e85735eed8; report-only current HEAD363bb24d26515bd4d88fdb0e7173d2b4ef6b9df1. Delivery run `run/621b6077d87e199e45da159b9a60c25c`, epoch6, native revision11. Actual source implementation and runtime outcomes are recorded below as they occur; future cases are not passes.

## Review consumption and authority

Before core setup, read full applicable report `validation/plan-review.md` at363bb24, SHA25656afa90022e282457e982dd53ed932ac209f103e327ea1c57fd664891766609c, through accepted operation `launch-cb1370a437da00c2473a41729b7dcae3-handoff`. Exact approved candidate0374767 and human spec checkpoint efccb74 matched working/committed digests. Required findings: none. Optional suggestions: none. Native spec/plan approval IDs and inherited review constraints were assessed for current separately selected delivery; no broader permission inferred.

## Initial checks

- Standard implementation prerequisite helper passed; existing literal feature pointer unchanged.
- Requirements-quality checklist:16/16 PASS, read-only gate; no custom incomplete checklist.
- Isolated worktree clean at entry. Existing Python ignore patterns cover generated fixture/cache files; no ignore changes needed. Primary unrelated dirt remains untouched.
- Core skill/helper/template baseline hashes retained in the table below; no core edits permitted.
- No mandatory pre/post implementation/convergence hooks configured. Optional post-implementation wiki ingestion is not automatically selected; prescribed closeout maintenance still runs once.

## Core baseline

- `.agents/skills/speckit-analyze/SKILL.md`: `1b1233a3a92cba277cc3f80533b3999a3194f2566b569e1deefad304fad3530a`
- `.agents/skills/speckit-checklist/SKILL.md`: `cf754e4fdb350bac26b0955b0af06bf4ac8f8ff0907e6db696e8f93b06844273`
- `.agents/skills/speckit-clarify/SKILL.md`: `569c830d56f4d7b6a0ee6f6c6741820472724a8d1f6021912b44cd55888a8fcd`
- `.agents/skills/speckit-constitution/SKILL.md`: `06bf15100066a86df4c5edfac35b16ecfe216751bdbc68db2d98357e9e751508`
- `.agents/skills/speckit-converge/SKILL.md`: `dc28f28b48f7c74f3828404f0832504358da358d631b12d7dab06266546504a0`
- `.agents/skills/speckit-flow-wiki-ingest/SKILL.md`: `12e27b5f9c7c45ddde07eda9e10a401f5e06fc8fb463a99c79d4073330a52261`
- `.agents/skills/speckit-flow-wiki-init/SKILL.md`: `ed3cc6070455a1d20d0986d78886a7b6afe4df40d59cbce080380abad13e678c`
- `.agents/skills/speckit-flow-wiki-lint/SKILL.md`: `99ac94bd27864f0813a7cbc209fbfaa97a3e01868d1df89de0f9879db48e3284`
- `.agents/skills/speckit-flow-wiki-query/SKILL.md`: `fcea99785fe767118e0d9485262881340b61a54ac8af07867019b6be883afa88`
- `.agents/skills/speckit-flow-wiki-status/SKILL.md`: `e299097b5c08c214c729c4d6d5300691e8fcc234334ef8539cb25002a7b996ab`
- `.agents/skills/speckit-implement/SKILL.md`: `ca79e1f816ede6230466e04249be8d3a1f396a9ea2f4c8e8ffc4af3ca5afda8e`
- `.agents/skills/speckit-plan/SKILL.md`: `dffe72852101b265bd93461691caec528b3e0d06459fc7f8d543191cdabe714e`
- `.agents/skills/speckit-specify/SKILL.md`: `a505028de7f6489878696d6656c7d057f3a66119ebb8c0cc82d69fabb7b344ff`
- `.agents/skills/speckit-tasks/SKILL.md`: `50612808eaee6c5fe32c64329661ba4d833d03fcbf9d7d318ea158e89eb30712`
- `.agents/skills/speckit-taskstoissues/SKILL.md`: `a409552af49641be404750b358de7a4d3936a79c336013bfd4c7cfa9d8b79f04`
- `.specify/scripts/bash/check-prerequisites.sh`: `13be175548848bd84e96a90cf9be87665c2e68603b2eaa3e19187e7ca8b4fcb0`
- `.specify/scripts/bash/common.sh`: `69a154ea1e5a622598e25eac939a0d8c30ed68e2d9f0da5e8204e468e4d8b64e`
- `.specify/scripts/bash/create-new-feature.sh`: `f4244c6cf95025e5726669938e9152d4a557cc7c1e8b027a43cb4de72677da16`
- `.specify/scripts/bash/resolve-template.sh`: `829e227096abc8bf0889889ec9f792f503ca5d395b7836a8a7eb739ee75214e7`
- `.specify/scripts/bash/setup-plan.sh`: `d0bd298c026446f3c63167130d65e49e4aa4485de6bef18bcdfd57b19aa0de96`
- `.specify/scripts/bash/setup-tasks.sh`: `0350b2def158c4dc333cd888fc5a3b10785b3d5c2cf936f93e910242ea9d507d`
- `.specify/scripts/python/check_prerequisites.py`: `368e364d1e08e67ae7c19b46b4e41a35596d6a9468ca7cb391c23e7bf0ae1b88`
- `.specify/scripts/python/common.py`: `fa8c8726ef1b805b68a21c993d5cf934b36230fe752a1734f4578629204aac93`
- `.specify/scripts/python/create_new_feature.py`: `c348aa02883188308de637f96b51d9861fa0379dbafcb5c0ed1d4c098b3e34ec`
- `.specify/scripts/python/resolve_template.py`: `2e80e872519609b21480e16f1b1ad7620e4469b4faf88af1ecefa8f778c768a0`
- `.specify/scripts/python/setup_plan.py`: `4371353b509ff352da27846e6e68d495fce2f9eeda87c28a39f8dc9d5354e438`
- `.specify/scripts/python/setup_tasks.py`: `9133333ba0971723d165d5575493404b43ec8d227e96ddbd3a9f63ad2cf174fe`
- `.specify/templates/checklist-template.md`: `70bbc48e884fab372ffb09e83e78ff983e28b69caebf8cd9964a02b6836683ac`
- `.specify/templates/constitution-template.md`: `ce7549540fa45543cca797a150201d868e64495fdff39dc38246fb17bd4024b3`
- `.specify/templates/plan-template.md`: `a828ad6206526574ab3fc99be6d0154588cb1c9774c5919d71b81ab5b2dbffa0`
- `.specify/templates/spec-template.md`: `3945437fc35cd30a5b2bf7beea680337c3516826d3efa5a6b92c4a7eca1ba28e`
- `.specify/templates/tasks-template.md`: `b0f527d41e546af0c31903e04f9b20965b6b497b573792198f663a64ce128863`

## Red contract check

Existing suite extended with two return-boundary checks; initial run failed on missing planning consumption section and specification-return continuation, as expected before source changes. Existing unrelated tests were retained.

## Standalone P1 actual observation — PASS

Executing session `01a17452-ebc7-7c10-bdc1-5673311b1983` was separate from this delivery evaluator. Current candidate copies were run using normal `codex exec --json` in a disposable standalone consumer. Full committed report was read/verified in command event1 before plan setup event4; actual core plan/tasks prerequisites ran, proposal corrections removed daemon approach and added input-preservation verification, and existing T001/T002 survived. Subject recorded R1/R2 correction and voluntary high-priority O1 adoption in existing plan notes, performed fresh read-only analysis and stopped Awaiting full-plan review. Input/spec/pointer/source copies unchanged; no greeting implementation or commit. Relevant output artifacts SHA256:
- `plan.md`: `d2ebc170a55989de1e692bf5db26a642623463693842a6ab50ee2d42d55b398b`
- `tasks.md`: `5bd8dbc6c869a3caee0eb9dc76bd9a134e90aa7a4a8ccc0f7cb9c48c0416c0e0`
- `research.md`: `0e2f9d8240a33b21a3a6efb9d399cb6d585f6f36cd13681fcc365293b464ef7d`
- `data-model.md`: `a9fcda82d099beae05b7bcb59305e32a14fce96c44f5a4e29a53622be3747032`
- `quickstart.md`: `9393dbee0b6dae152ad3cb7d4c4e8e60220e29286e77afac14ede1d814bff51b`

Retained factual observation above is sufficient after disposable logs/consumer disappear; raw `/tmp/farm28-p1.jsonl` is optional nonessential diagnostic output. No native claim is made for this standalone case.

## Standalone S1 genuine wait observed

Actual separate subject `01a17454-ee87-7db2-afab-4cb434bd619c` read the committed report and ran the ordinary clarification path-only helper. It asked R1 whether greeting.md includes the literal suffix Welcome, offered exact-byte options and ended waiting. Evaluator inspected this real question and unchanged tracked fixture artifacts before supplying any answer. This is an actual wait, not a supplied transcript. Continuation outcome is recorded below after execution.

## Standalone S1 continuation — PASS

After the observed real wait, evaluator supplied actual TEST ONLY answer B (include Welcome) into the same session. The subject integrated it into existing specification/Clarifications and related acceptance wording, reassessed the existing checklist, recorded the required finding disposition and stopped Awaiting spec review with no approval or planning. No greeting artifact was implemented. Final spec SHA256 `0ace3cb1a0de13cf97a54a194bc8f6586691436fa0bd8fb9c13f4fc1bd6b48ca`. Raw temporary output is disposable; retained question/answer/session/changed-artifact facts support this observation.

## Shared standalone evidence/obligation/resume matrix — PASS

Actual independent executing subject `01a17457-ec3b-7b00-acd1-5295815f4442` processed10 disposable consumers; this delivery evaluator checked actual resulting artifacts, unchanged input/HEADs, preserved task identities and no greeting implementation. Decoy selected authoritative older report; resolved reused R1 evidence; resume kept task bytes and existing resolutions. Seven invalid/ambiguous/material-change cases stopped with exact existing plan notes, tasks unchanged. No Diagram calls/commits/installs or source repairs.

| Case | Observed result | Saved plan-note SHA256 |
|---|---|---|
| wrong-feature | PASS precise stop | `b4de180682011c6975ca9ea4bf4588397fe3966715291256affa4c6d200ad579` |
| wrong-candidate | PASS precise stop | `dd8038149ee80b211c2d1f29ed83ab0dcbc4e968c3ef895d7be93fe2b6cc39eb` |
| wrong-route | PASS precise stop | `9a5088f6b4484d57a670f6ccd6911385ee53eb4581ec73dd1f71ad78304beca8` |
| altered | PASS precise stop | `367c7456e03cd2e0fb790255f04af56687d9a61d76a9d2d992cf44793dd33480` |
| missing | PASS precise stop | `1db44e1ee81237ef9bcfcf2dbf250ecdda4aa24e12f72bea2113bb03fc488556` |
| decoy | PASS review-ready | `84704ccc3683b0846266e85aa08537182fd0296b295c9950259c127951aa94fc` |
| resolved | PASS review-ready | `19436c97159b5b578d4cf4658f319ffb2f330af8447d4512beeaec5cccc50e78` |
| ambiguous | PASS precise stop | `ba5c33388308b394ff27fb81dd4218a5431387fcf8cdf993f2dd0561c5db3902` |
| changed | PASS precise stop | `5bea75310e3b2d117865af1a4c1e5ed40ab0c19f5a8325ec050afe12bb2161fc` |
| resume | PASS review-ready | `121c018237635eacae5ff7edabc89e56e7371d82b7c037bf1e22fe150e3ada85` |

The three valid consumers performed real helper work and fresh read-only analysis before full-plan review. Raw temporary transcript is optional nonessential diagnostics; retained session, per-case outcome/digests and preservation facts above remain evidence.

## Matched native first-run evidence — partial

Actual native planning subject completed outer P1 and exact-inner planning with accepted awaiting_plan_review and absent owner, preserved applicable spec approval and existing T001, added concrete exact-byte validation and fresh analysis. Exact-inner reused the existing run. Foreign/stale stopped without transfer, missing-origin and wrong-candidate stopped before dependent effects. Parent inspected these states/artifacts before disposable test cleanup. No effect.txt implementation existed.

| Case | Native revision | Outcome | Owner at observation |
|---|---|---|---|
| p1 | 14 | awaiting_plan_review | None |
| inner | 14 | awaiting_plan_review | None |
| foreign | 13 | plan_revision_required | TEST ONLY foreign owner |
| stale | 13 | plan_revision_required | TEST ONLY return subject |
| missing-reference | 11 | awaiting_plan_review | None |
| wrong-candidate | 12 | plan_revision_required | None |
| s1 | 13 | specification_change_required | TEST ONLY return subject |

Native S1 session01a1745b-2b14-7043-b60c-9d90c34cbac8 read full report/candidate/origin, acquired clarify run42bf629be780d1e19b6dbbd77f9189f6 epoch7/revision13 with no spec approval, and asked/waited for a suffix answer. Its CLI resume failed before execution: “Not inside a trusted directory and --skip-git-repo-check was not specified.” Handler inherited non-Git source-snapshot cwd. Overall first native suite FAILED, not a pass. Go cleaned only its own disposable fixture tree; original store paths are no longer current authority.

Interim app message returned active-writer (no answer sent); Computer Use getApp(Codex) was denied before any UI interaction for safety reasons. No UI retry/bypass. The independently existing ordinary CLI resume now uses its actual fixture Git cwd, without a skip/trust/permission flag. A recheck was requested for S1, but the initial edit failed because its cwd was the private snapshot; the command continued with the already-compiled prior fixture bridge. Required answer/handoff remains unpassed until the corrected source actually executes. Mixed diagnostic/JSON parsing is scalar-safe. An initial relative-path edit failed before changing files; the absolute-path correction/filter was applied after the active recheck handler had already loaded the prior code. That recheck therefore repeats the private planning cases; it cannot establish the corrected resume behavior. This is a harness scheduling mistake, not an additional product finding. The corrected source must be exercised by a subsequent isolated S1 invocation only after the active recheck exits.

Private binary was compiled from pinned local Diagram6cc924 using matching installed Go1.26.5 after an initial inherited-GOROOT1.23.6 mismatch; invocation env only changed. Private builder hook/signing bypass arguments were removed before execution to retain normal hooks. No installation or live source/schema/control change. Builder inputs are explicitly simulated TEST ONLY; actual consumer subjects are separate model executions evaluated by this delivery session.

## Changed source identity

The following current maintained source bytes are the candidate exercised by actual generic/native consumer sessions (test harness fixes are listed separately above). Documentation/wiki-only changes do not stand in for runtime proof.

- `.agents/skills/farmboy-prepare-implementation-plan/SKILL.md`: `e39cd744252971d84ddcce7b6ba3b250eeb5c3b3b487eb7a38b832bdfa8cc436`
- `.agents/skills/farmboy-prepare-specification/SKILL.md`: `f31e527baa651970278030a1156f67cbd29e2f95e0f3d8f0312f1dfc9ea75254`
- `.agents/skills/farmboy-diagram-work/SKILL.md`: `1710a2b46061151fc74713621c0335449929803bbcec65648bb24518d20edcee`
- `.agents/skills/farmboy-diagram-work/references/native-protocol.md`: `60d5a64c4230e1f6e4024249969057e8036ed1b173004bbd2d31589e912482d6`
- `docs/workflow-handoffs.md`: `fe407a28ab444f8f88f00cdf6feddfe74b0fed97ec30f24492807b3421275bab`
- `docs/diagram-adapter.md`: `16338ece81a0f010d77aa76ddff6016ee5e14b2370f61a3329e959b7272abf76`
- `docs/review-implementation-plan.md`: `521f1a7042fb9f2b535b3b58ce9b0feb1ce524e8aae546e0f720258f0755dcf8`

## Additional native planning readback retained

The scheduling recheck repeated the private planning cases before targeted filtering was loaded. Those were additional observations, not needed to replace the initial successes. Parent independently read actual current native state before cleanup:

- `p1`: actual subject `01a17461-2686-7993-91da-2168763f7efc`, result proposal `f823451f6e1fad8e5c14b029bde911c12b902238`, handoff `handoff/7bd40653040038d19cb00dbbfee89bb8`, native revision14, retained spec approval `approval/a96fbce382afc22aa58a714a6b1b57e0`, absent owner. Artifact roles/digests: `specs/001-fixture/plan.md` SHA256 `4a2cc0536e8c8428132e6173f4fd2f9901bfcdb0009cfcdbc008e3f59a79c7ab`; `specs/001-fixture/tasks.md` SHA256 `c143bfcafaaf85e619a9763a2380489b087354c0f94f39c989c956f304cade70`; `specs/001-fixture/analysis-fresh.md` SHA256 `5c04190ae169b5ed1cde5baff38787ca15bfb580b7c568b21eea08a7cfb915bb`; `specs/001-fixture/research.md` SHA256 `692acb57e1153fa937232fd8d93a21e0c474fa3a3389c94b8c87395ea51e71c5`; `specs/001-fixture/data-model.md` SHA256 `ccc9ee0bd24306f3a3bbb689a0c13a945a2057bdb6225eb50dfad6657a3fbb0b`; `specs/001-fixture/quickstart.md` SHA256 `ecbb27fe6259d6cf54b925f9cde657d71aa24b5aaa9b8bed55637ce8257c5cb9`
- `inner`: actual subject `01a17461-2686-7993-91da-2168763f7efc`, result proposal `5646afb6d1c45fa3e03b080c58acdaeefea96760`, handoff `handoff/92222ce0d9a2fe392380e99e5147c96c`, native revision14, retained spec approval `approval/5bba6625ab24e337a6c61de0a9761737`, absent owner. Artifact roles/digests: `specs/001-fixture/plan.md` SHA256 `2e1c7bb3154916f129d4725a0b6cb0d7ef5798ffa380a592991d4861180f113d`; `specs/001-fixture/tasks.md` SHA256 `c143bfcafaaf85e619a9763a2380489b087354c0f94f39c989c956f304cade70`; `specs/001-fixture/analysis-fresh.md` SHA256 `8fa5d96a9d6b5e8abbab0f4752a9d092a06cf4e4d18f12e8b17096e30f284548`; `specs/001-fixture/research.md` SHA256 `692acb57e1153fa937232fd8d93a21e0c474fa3a3389c94b8c87395ea51e71c5`; `specs/001-fixture/data-model.md` SHA256 `ccc9ee0bd24306f3a3bbb689a0c13a945a2057bdb6225eb50dfad6657a3fbb0b`; `specs/001-fixture/quickstart.md` SHA256 `ecbb27fe6259d6cf54b925f9cde657d71aa24b5aaa9b8bed55637ce8257c5cb9`

The same actual subject stopped foreign/stale owner/revision mismatches, absent-origin and wrong-candidate cases before dependent effects; these remain explicit negative observations, not native approval. Full source implementation remains the same recorded hashes.

## Targeted native S1 continuation — PASS

The corrected one-case invocation executed only S1 after the prior invocation had exited (no active duplicate). Actual same-session subject `01a17469-3a76-7c22-bbe3-0d03307190b6` read full committed report/candidate/origin, acquired clarify run `run/733e364851946d9028ee0262d90c5fac` epoch7, asked the genuine suffix question and yielded while retaining ownership with no applicable spec approval. The evaluator observed/retained that wait before supplying TEST ONLY A (include Welcome). Ordinary `codex exec resume` used the actual fixture Git cwd with no skip/trust/permission bypass.

The same subject integrated actual answer/finding R1 into the existing specification/Clarifications, made a normal feature-only checkpoint and recorded accepted `awaiting_spec_review` at revision14, handoff `handoff/8f58e57a3e664919c7b95e0dd8b45777`, with no current owner/claim and no applicable revised-spec approval. Worktree was clean; no effect.txt implementation or planning followed. Spec SHA256 `9bec84f200eb83fe360a49c754da7ddb42600dba3c7a34e5226cdbaa3cab85bb`. Native accepted-spec checkpoint `0b457c02ca53d959e4bb65c7249f80c85fbe9960` retains its actual artifact digest. Existing native fixture had no additional requirements checklist; standalone S1 separately observed the existing-checklist reassessment.

Go targeted test `TestFarmboy028NativeReturns` exited0/PASS using current matched schema22/Feature9 and actual model execution. Parent independently verified the retained native state and resulting artifact content; it did not infer success solely from exit0. This supplies the previously unpassed T017 answer/handoff/release observation. Earlier harness failures remain recorded above; no prior failed run is relabeled passed, no UI denial retried, and no broader authority was inferred. Together with initial native outer/current-inner and refusal observations, required native return coverage is complete. Raw temporary output remains disposable nonessential diagnostics; session/run/handoff/checkpoint/digest facts here are retained proof.

## Final independent checks and closeout preparation

Ten focused contracts, Python syntax, unchanged core baseline, contained artifact links/portable prose and whitespace checks PASS. Wiki S011/S012 upkeep and12-page lint PASS. Fresh current consistency and convergence found zero actionable gaps or unmet obligations; convergence changed no task bytes. All source/verification tasks and T019 are complete (19/20); T020 remains the actual outer commit/result handoff endpoint. No future commit or accepted result is asserted by this preparation note.

## Observed checkpoint and final reconciliation

Normal Git hooks passed at actual source/evidence checkpoint `004712786f48f8ded996faf36803641cf3584cd5`; exact committed source bytes match the retained tested hashes, and worktree was clean. Final task/closeout metadata reconciles the completed checkpoint and prepares the outer native result. No unperformed final commit or handoff/release is represented as observed here; actual final references are returned only after success.

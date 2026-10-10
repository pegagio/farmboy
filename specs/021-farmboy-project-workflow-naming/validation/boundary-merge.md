# Roadmap Boundary Merge Validation

On 2026-10-10 the operator explicitly authorized merging `codex/roadmap-boundary-correction` into `farmboy`, resolving rename conflicts and running relevant validation. Pushing, existing-consumer refresh and resuming implementation were excluded.

## Integrated Source

The merge combines FarmBoy checkpoint `87227a111496a02d7e4fc297b5479bb885fefe2b` and reviewed correction `7a43bb37398baec7a757feb04cbb83dcb901fac4`, sharing baseline `b6dcae9de22147f867717e322c7bb2cb8a240715`. Reviewed policy moved into `controllers/farmboy/scripts/python/milestone_policy.py`; the controller, phase adapter, Specify/Implement/Close Out workflows, documentation, source guards and tests retain FarmBoy names and use generic roadmap writes.

Source pins are controllers 0.9.0, Specify 0.4.0, Implement/Close Out 0.9.0 and independent flow-roadmap 0.4.0. The roadmap source is clean at `34483aa212e5cb3302615c0fad043d1eb908edc9`; its runtime payload matches cleanup `7eec0b73b49d4d242d491530da5011de62b4d211`. Independent extension IDs, generic commands, actual repository URLs and neutral schema/function names remain unchanged.

Rename reconciliation included canonical synthetic reviewer names, their bound assessment/proposal digests, snapshot version expectations and supplying the compatible roadmap source to the native-delivery fixture. The replaced extension-owner case matrix is covered by the correction's workflow-owned boundary suite and retained local phase tests. Validators were not weakened to accept stale identities or hashes.

## Observed Validation

Python 3.11.16, PyYAML 6.0.3 and Specify CLI `1.0.10.dev0+pegagio.2` were observed on macOS arm64.

| Check | Result |
|---|---|
| Source unittest discovery with native-delivery, snapshot and generic roadmap inputs | 356 tests; successful, one bundle-lifecycle prerequisite skip |
| Local phase lifecycle | 30 tests; passed |
| Workflow-owned boundary, including delivered generic configuration | 23 tests; passed in source discovery |
| Snapshot validation with compatible sources | One test; passed |
| Native agent delivery in a disposable consumer | 22 tests; passed |
| Fresh installed joint boundary | One joint test covering Specify, Implement and Close Out; passed |
| Feedback capture/report and maintainer intake | Five and eight tests; passed |
| Workflow structural validation | Zero unexplained terminal paths |
| Whitespace/conflict markers | Passed |

The joint check used the roadmap repository's reviewed joint test in a temporary runner, substituting only the renamed bundle/controller paths and reviewer name. The roadmap repository was not edited. Actual generic writes, authoring proof rejection and independent effect readback ran in disposable consumers. Assessments were synthetic; this does not establish live installed phase-workflow or named-agent dispatch.

The separately enabled bundle lifecycle suite ran four tests and reported one failure: `Cannot dispatch prompt: integration None CLI not found or not installed.` This previously recorded native prompt-dispatch issue remains unresolved and is not treated as passing validation or fixed by the merge. Linux was not tested.

## Preserved Pause

Constitution, roadmap ledger, active feature pointer, task IDs/markers, Feature 020 history and existing consumer installations remain unchanged. Feature 022 artifacts and review/provenance were carried byte-for-byte from the reviewed correction. T010–T012 remain open; this merge validation does not resume or complete those tasks or establish feature acceptance.

Packaging for the installed joint check was generated only in disposable source/consumer copies with the existing builder. Checked-in catalog snapshots and archives were not regenerated or published. Mutable Feature 021 artifact reconciliation, a fresh implementation assessment, any consumer refresh and further implementation remain operator-selected follow-up work.

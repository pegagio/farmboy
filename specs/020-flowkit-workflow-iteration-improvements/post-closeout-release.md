# Post-closeout production release handoff

**Status**: Pending. This release work is separate from Feature 020 implementation, convergence, and closeout. It must not block those activities.

## Why the release moved

The original T037 combined two different deliveries: a development snapshot needed to validate and use current Feature 020 source, and a production catalog release that requires committed, reviewed source and release tags. The first can happen before closeout; the second depends on the Git state produced by implementation review and closeout. T037 now covers only development-snapshot installation and validation. This file carries the production-release work forward as a pending handoff.

The previous T037 release obligation is preserved here as historical wording:

> After T036 and availability of clean reviewed source checkouts at metadata-matching tags, use the existing `mise run catalog:build` to regenerate `catalog/release.json` and affected `catalog/packages/` archives so package bytes/digests match reviewed FlowKit sources and pins; leave artifacts unchanged if a required source delivery or Git prerequisite is unavailable. Validate digests and install the reviewed snapshot into disposable consumers before T022–T024 launch the additive Checker, recording exact commands/results and gaps in `specs/020-flowkit-workflow-iteration-improvements/validation/summary.md`.

## When to resume

Resume only after Feature 020 has separately completed its requested Converge and Closeout workflows. Production release work requires a separate explicit release invocation. Git integration, creation of tags, and production catalog generation each require explicit authorization; completion of Feature 020 or its closeout does not silently authorize those operations. The release handoff does not invoke publication or push changes.

## Release procedure

Before building, review the exact source revisions and reconcile every package version with `bundles/spec-kit-flow/bundle.yml` and the corresponding manifests. Inspect `tools/catalog.py` as the executable source of release checks. Its current `build` path requires:

- Clean local source paths for `bundles/spec-kit-flow/bundle.yml`, `workflows/`, and `agents/flow-kit/`, plus clean `controllers/flow-kit` and `extensions/flow-feedback` source used by the catalog.
- Clean complete checkouts of the independently versioned roadmap and wiki extension sources. Each checkout must have an annotated `v<version>` tag for the version pinned in the bundle, and that tag must resolve to the checkout's `HEAD`.
- Manifest versions, workflow versions, agent package version, and bundle pins that agree. FlowKit itself does not need a release tag for this builder; the `v<version>` tag check applies to the roadmap and wiki source checkouts only.

After the authorized source and Git prerequisites are met, build with the existing task:

```sh
mise run catalog:build /path/to/spec-kit-flow-roadmap /path/to/spec-kit-flow-wiki
```

Review the generated `catalog/release.json` and each affected `catalog/packages/` archive against its source version, source revision, and SHA-256 digest. Install the catalog into a disposable initialized consumer and record the exact command, installed package digests, readiness and compatibility results, preservation checks, and any gap. Keep source acceptance, runtime agent availability, and effective agent settings as separate claims. The build and validation do not publish or push the catalog.

## Sequencing amendment record

On 2026-10-06, T037 was narrowed to pre-closeout development-snapshot package validation and disposable-consumer installation. T022–T025 and T027–T031 retain their pending validation requirements against that snapshot. The production release obligation above moved to this post-closeout handoff; it has no Feature 020 task checkbox and is not a blocker for implementation, convergence, or closeout. This note changes sequencing only; it does not claim the snapshot installation, production build, verification matrix, or release has occurred.

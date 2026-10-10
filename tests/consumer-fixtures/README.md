# Consumer Fixtures

`missing-required-components.sh` demonstrates the current local-development failure mode: a clean consumer with no configured component source cannot install the bundle offline, and Spec Kit records no partial bundle provenance.

`../test_bundle_lifecycle.py` creates a private, disposable localhost catalog to exercise successful clean-consumer installation, refresh, removal, and feedback export. `independent-workflow.yml` is an unrelated consumer component that must survive bundle removal. The test receives `flow-roadmap` and `flow-wiki` source directories through `FARMBOY_TEST_ROADMAP_SOURCE` and `FARMBOY_TEST_WIKI_SOURCE`. They are test inputs only, not a runtime dependency of the generic bundle or a substitute for its future published catalog coordinates.

`start-feature-linkage.json` supplies unique, missing, stale, conflicting, ambiguous, approved, declined, and post-write mapping cases for Start Feature's exact `Spec dir` link and brief routing checks.

`diagram-converge-observation.json` is a sanitized retrospective observation from the Diagram dogfood run. Set `FARMBOY_TEST_OBSERVATION` to this fixture and `FARMBOY_TEST_REPORT_OUTPUT` to a temporary output path to export a portable report from the installed feedback extension. The test also checks that maintainer intake accepts the valid report and rejects a tampered copy without creating another record. Both intake checks use a disposable maintainer root; transferring an accepted report into the FarmBoy source repository is a separate, explicit operation.

The lifecycle test also advertises `flow-wiki` version `0.0.0` from its private catalog against the bundle's pinned `2.0.1`. Native installation must report both versions and leave no compatible bundle record. This complements the missing-component fixture without contacting a public catalog.

Run the lifecycle test with a compatible Spec Kit executable and vetted source directories for the two required extension prerequisites. The test publishes nothing, starts no persistent service, and removes only its fresh temporary fixture directory.

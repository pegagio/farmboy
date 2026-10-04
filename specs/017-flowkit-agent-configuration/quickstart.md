# Quickstart Validation: FlowKit Agent Configuration and Consumer Delivery

This guide validates the future implementation. Proposed agent CLI commands are not available in the current baseline; do not execute this guide as evidence of implemented behavior until that phase completes. Run only in disposable initialized consumers and keep results portable.

## Table of Contents

- [Prerequisites and Source Checks](#prerequisites-and-source-checks)
- [Disposable Consumer Lifecycle](#disposable-consumer-lifecycle)
- [Negative and Migration Cases](#negative-and-migration-cases)
- [Live Named-Agent Evidence](#live-named-agent-evidence)

## Prerequisites and Source Checks

Use existing project tooling and installed dependencies. The source pins Python 3.11.16 and Specify `1.0.10.dev0+pegagio.2`; observed CLI during planning was `0.157.1`. Record actual versions at validation time, source commit, package/workflow/controller versions, artifact/source digests and snapshot/released status. Confirm operator-approved settings and source contract before creating fixtures.

Run focused checks, then source graph validation using the existing tooling environment:

```bash
mise exec -- python3 -m unittest discover -s tests -p 'test_agent_configs.py'
mise exec -- python3 -m unittest discover -s tests -p 'test_catalog.py'
mise exec -- python3 -m unittest discover -s tests -p 'test_bundle_lifecycle.py'
mise exec -- python3 tools/validate_workflows.py --fail-on-unexplained
```

After focused checks pass, run the full existing suite once. Skill-specific Python checks use the configured skill-tools interpreter. Expected source outcomes: eight exact prefixed files/roles, explicit approved pairs, canonical-source/local-config equality, every nested active assignment resolving once, author/reviewer separation, unchanged graph/probe behavior, valid package integrity and no undocumented current name drift.

## Disposable Consumer Lifecycle

Initialize a temporary consumer with the supported Specify CLI using the project's existing lifecycle fixture pattern. The following installation command uses the existing supported snapshot path; set `consumer_project` to that initialized disposable directory:

```bash
mise run catalog:install -- "$consumer_project" --development-snapshot
```

Expected: installed components/default cache plus eight absent copies acquired. This creates no consumer-copy ownership ledger. Keep a fixture with local model/instruction edits and unrelated/unprefixed/retired files; capture bytes in the test harness for preservation assertions (test comparisons are not runtime ownership tracking).

Exercise the prospective interface from [delivery contract](contracts/agent-delivery-cli.md):

```bash
mise run catalog:agents -- install-missing "$consumer_project" --json
mise run catalog:refresh -- "$consumer_project" --development-snapshot
mise run catalog:agents -- reset "$consumer_project" --agent "FlowKit-Planner" --json
mise run catalog:agents -- reset "$consumer_project" --all --json
mise run catalog:remove -- "$consumer_project"
```

Use separate fixtures to prove each transition rather than letting a preceding reset erase preservation evidence.

| Scenario | Expected result |
|---|---|
| Clean bundle install | Eight copied defaults; valid native inventory |
| Repeat install-missing | All existing files byte-identical, reported preserved |
| Existing customized prefixed file | Install-missing preserves it and does not classify edits |
| Ordinary refresh to changed/new defaults | Cache advances; all consumer copies byte-identical; new role remains absent until install-missing |
| Install-missing after refresh | New missing entries copied; existing configurations preserved |
| Reset-one customized Planner | Only Planner target equals selected default; discarded customization explicit |
| Reset-all | Current manifest-listed targets equal defaults; unrelated/unprefixed/obsolete preserved |
| Bundle removal | Copies and consumer-owned feedback survive; defaults cache/components removed by their existing contracts |

The future-version/new-role case is a packaging/lifecycle fixture, not authorization to add a ninth production role. Capture package versions/digests for both fixture inventories.

## Negative and Migration Cases

Exercise unknown reset name, both/neither target selector, missing/invalid defaults, wrong digest, duplicate identities, malformed TOML, unlisted archive member, path traversal, symlink destination/ancestor, destination directory and permission/write failure. Preflight failures yield no writes; induced mid-write failure reports exact completed/failed/not-attempted targets and bounded retry. Verify unchanged content for every out-of-scope file and no silently accepted usable inventory.

Create an old-only unprefixed consumer and mixed-version assignments. Install new defaults without deleting old files. Confirm missing/ambiguous exact identity stops supported dispatch with no alias or substitute. Follow documented customization/reset migration and confirm resolution. Renamed/retired fixture definitions survive refresh/removal and appear in update guidance.

## Live Named-Agent Evidence

After static/lifecycle checks and operator settings approval, validate all eight exact names using the installed controller's existing dispatch/probe procedure in a fresh disposable project/session as needed. Do not launch another FlowKit phase or change probe timing to obtain evidence. Each invocation stays narrow and authorized; the parent handles questions/gates and author/reviewer separation. A no-op executable records dispatch transport only.

Record separately: configuration consistency, supported field/value validation, live exact-name selection and observed effective model/effort. Use native reported settings only if available; otherwise mark effective settings unverified even when dispatch succeeds. Record affected role/requested pair, client identity/version, source/package provenance, scenario and outcome for unavailable fields/values; never choose a fallback. Account/client support failures require operator resolution before applying unsupported choices. Reports contain no secrets, raw transcripts or host paths. Local validation establishes no publication, consumer adoption, roadmap verification or acceptance.
